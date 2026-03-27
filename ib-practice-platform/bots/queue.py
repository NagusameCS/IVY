#!/usr/bin/env python3
import argparse
import json
import math
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "bots" / "queue.db"
GENERATE_SCRIPT = ROOT / "generate.py"
OUTPUT_PATH = ROOT / "questions.json"
TEMPLATES_DIR = ROOT / "data" / "templates"
WEB_STRUCT_URL = "https://raw.githubusercontent.com/NagusameCS/IVY/main/struct.json"
WEB_STRUCT_CACHE_PATH = ROOT / "bots" / "web_struct_cache.json"

SUBJECTS = [
    "math_aa",
    "math_ai",
    "physics",
    "chemistry",
    "biology",
    "economics",
    "business",
    "computer_science",
]

LESSON_SUBJECTS = [
    "math_aa",
    "math_ai",
    "physics",
    "chemistry",
    "biology",
    "economics",
    "business",
    "computer_science",
]

VERIFY_CHECKS = [
    "schema_validation",
    "duplicate_detection",
    "difficulty_distribution",
    "topic_coverage",
    "latex_syntax",
]

# If a job remains "running" longer than this, assume a crashed worker and requeue.
STALE_RUNNING_SECONDS = 15 * 60

SUBJECT_WEB_MAP = {
    "math_aa": {
        "subjects": {"math"},
        "categories": {"math aa"},
    },
    "math_ai": {
        "subjects": {"math"},
        "categories": {"math ai"},
    },
    "physics": {
        "subjects": {"physics"},
        "categories": {"physics"},
    },
    "chemistry": {
        "subjects": {"chem", "chemistry"},
        "categories": {"chemistry"},
    },
    "biology": {
        "subjects": {"bio", "biology"},
        "categories": {"biology"},
    },
    "economics": {
        "subjects": {"econ", "economics"},
        "categories": {"economics"},
    },
    "business": {
        "subjects": {"business"},
        "categories": {"business"},
    },
    "computer_science": {
        "subjects": {"compsci", "computer science"},
        "categories": {"computer science"},
    },
}


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    # Improve concurrent read/write behavior and reduce fsync pressure.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'queued',
            retries INTEGER NOT NULL DEFAULT 0,
            max_retries INTEGER NOT NULL DEFAULT 3,
            created_at INTEGER NOT NULL,
            started_at INTEGER,
            finished_at INTEGER,
            error TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_id ON jobs(status, id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_started ON jobs(status, started_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_kind_status ON jobs(kind, status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at)")
    conn.commit()
    return conn


def enqueue(conn, kind, payload, max_retries=3):
    conn.execute(
        "INSERT INTO jobs (kind, payload, status, max_retries, created_at) VALUES (?, ?, 'queued', ?, ?)",
        (kind, json.dumps(payload), max_retries, int(time.time())),
    )
    conn.commit()


def enqueue_default_queue(conn, total_questions=80000):
    per_subject = total_questions // len(SUBJECTS)

    for subject in SUBJECTS:
        enqueue(
            conn,
            "practice_generation",
            {
                "subject": subject,
                "target_questions": per_subject,
                "difficulty": "all",
            },
            max_retries=5,
        )

    for subject in LESSON_SUBJECTS:
        enqueue(
            conn,
            "lesson_planning",
            {
                "subject": subject,
                "curriculum_source": "data/curriculum.json",
            },
            max_retries=3,
        )

    for subject in LESSON_SUBJECTS:
        enqueue(
            conn,
            "missing_lesson_generation",
            {
                "subject": subject,
                "web_struct_url": WEB_STRUCT_URL,
                "curriculum_source": "data/curriculum.json",
            },
            max_retries=3,
        )

    for check in VERIFY_CHECKS:
        enqueue(
            conn,
            "verification",
            {
                "check": check,
                "target": "questions.json",
            },
            max_retries=4,
        )


def next_job(conn):
    row = conn.execute(
        "SELECT id, kind, payload, retries, max_retries FROM jobs WHERE status='queued' ORDER BY id LIMIT 1"
    ).fetchone()
    return row


def mark_started(conn, job_id):
    conn.execute(
        "UPDATE jobs SET status='running', started_at=? WHERE id=?",
        (int(time.time()), job_id),
    )
    conn.commit()


def mark_done(conn, job_id):
    conn.execute(
        "UPDATE jobs SET status='done', finished_at=?, error=NULL WHERE id=?",
        (int(time.time()), job_id),
    )
    conn.commit()


def mark_failed(conn, job_id, retries, max_retries, err):
    if retries + 1 >= max_retries:
        conn.execute(
            "UPDATE jobs SET status='failed', retries=?, finished_at=?, error=? WHERE id=?",
            (retries + 1, int(time.time()), str(err)[:2000], job_id),
        )
    else:
        conn.execute(
            "UPDATE jobs SET status='queued', retries=?, error=? WHERE id=?",
            (retries + 1, str(err)[:2000], job_id),
        )
    conn.commit()


def recover_stale_running_jobs(conn, stale_seconds=STALE_RUNNING_SECONDS):
    """Requeue jobs left in running state by dead/crashed workers."""
    now_ts = int(time.time())
    cutoff = now_ts - stale_seconds

    rows = conn.execute(
        "SELECT id, retries, max_retries FROM jobs WHERE status='running' AND started_at IS NOT NULL AND started_at < ?",
        (cutoff,),
    ).fetchall()

    recovered = 0
    failed = 0
    for job_id, retries, max_retries in rows:
        if retries + 1 >= max_retries:
            conn.execute(
                "UPDATE jobs SET status='failed', retries=?, finished_at=?, error=? WHERE id=?",
                (retries + 1, now_ts, "Recovered stale running job exceeded max retries", job_id),
            )
            failed += 1
        else:
            conn.execute(
                "UPDATE jobs SET status='queued', retries=?, started_at=NULL, error=? WHERE id=?",
                (retries + 1, "Recovered stale running job", job_id),
            )
            recovered += 1

    if recovered or failed:
        conn.commit()

    return recovered, failed


def run_practice_generation(payload):
    subject = payload["subject"]
    target_questions = int(payload.get("target_questions", 10000))

    template_count = count_subject_templates(subject)
    if template_count <= 0:
        raise RuntimeError(f"No templates found for subject '{subject}'")

    # Scale per-template instances to approach the subject target.
    count = max(1, math.ceil(target_questions / template_count))

    tmp_output = ROOT / "bots" / f"generated_{subject}.json"

    cmd = [
        sys.executable,
        str(GENERATE_SCRIPT),
        "--subject",
        subject,
        "--count",
        str(count),
        "--output",
        str(tmp_output),
    ]
    subprocess.run(cmd, cwd=str(ROOT), check=True)

    if not tmp_output.exists():
        raise RuntimeError(f"Generator output missing for {subject}: {tmp_output}")

    generated_raw = json.loads(tmp_output.read_text(encoding="utf-8"))
    if isinstance(generated_raw, dict):
        generated_questions = generated_raw.get("questions", [])
    elif isinstance(generated_raw, list):
        generated_questions = generated_raw
    else:
        raise RuntimeError(f"Unsupported generated output format for {subject}")

    if OUTPUT_PATH.exists():
        current_raw = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        if isinstance(current_raw, dict):
            current_questions = current_raw.get("questions", [])
        elif isinstance(current_raw, list):
            current_questions = current_raw
        else:
            current_questions = []
    else:
        current_questions = []

    merged = {}
    for q in current_questions + generated_questions:
        qid = q.get("id") if isinstance(q, dict) else None
        if qid:
            merged[qid] = q

    merged_questions = list(merged.values())
    merged_output = {
        "version": "1.0",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "generator": "ib-practice-queue-merge",
        "template_count": None,
        "question_count": len(merged_questions),
        "questions": merged_questions,
    }

    OUTPUT_PATH.write_text(json.dumps(merged_output, indent=2, ensure_ascii=False), encoding="utf-8")

    # Auto-deploy: push updated questions.json to cPanel (incremental, only if changed)
    deploy_script = ROOT.parents[0] / "deploy.py"
    if deploy_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(deploy_script), "deploy", "--target", "questions"],
                cwd=str(ROOT.parents[0]),
                capture_output=True, text=True, timeout=600,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            if result.returncode == 0:
                print(f"[queue] auto-deploy succeeded for {subject}")
            else:
                print(f"[queue] auto-deploy warning for {subject}: {result.stderr[:300]}")
        except Exception as e:
            print(f"[queue] auto-deploy skipped: {e}")


def count_subject_templates(subject):
    total = 0
    for f in sorted(TEMPLATES_DIR.glob("*.json")):
        data = None
        for enc in ("utf-8", "utf-8-sig", "cp1252"):
            try:
                data = json.loads(f.read_text(encoding=enc))
                break
            except Exception:
                continue
        if data is None:
            continue

        if isinstance(data, dict) and "templates" in data:
            templates = data["templates"]
        elif isinstance(data, list):
            templates = data
        else:
            templates = [data]

        for item in templates:
            if isinstance(item, dict) and item.get("subject") == subject:
                total += 1
    return total


def run_lesson_planning(payload):
    subject = payload["subject"]
    out = ROOT / "bots" / f"plan_{subject}.json"
    curriculum = json.loads((ROOT / "data" / "curriculum.json").read_text(encoding="utf-8"))
    subject_data = curriculum.get("subjects", {}).get(subject, {})
    if not subject_data:
        raise RuntimeError(f"No curriculum data for {subject}")

    lessons = []
    for topic_key, topic in subject_data.get("topics", {}).items():
        for subtopic_key, subtopic in topic.get("subtopics", {}).items():
            lessons.append(
                {
                    "subject": subject,
                    "topic": topic_key,
                    "topic_name": topic.get("name"),
                    "subtopic": subtopic_key,
                    "lesson_title": subtopic.get("name"),
                    "level": subtopic.get("level", "SL/HL"),
                    "tags": subtopic.get("tags", []),
                    "practice_integration": True,
                }
            )

    out.write_text(json.dumps(lessons, indent=2), encoding="utf-8")


def normalize_key(value):
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def load_web_struct(url=None):
    """Load web struct from multiple fallback sources
    Priority: local file → cache → network → error
    """
    url = url or WEB_STRUCT_URL
    
    # Priority 1: Local data directory
    local_path = ROOT / "data" / "struct.json"
    if local_path.exists():
        try:
            payload = local_path.read_text(encoding="utf-8")
            return json.loads(payload)
        except Exception as e:
            print(f"⚠️ Error reading local struct: {e}")
    
    # Priority 2: Cached copy
    if WEB_STRUCT_CACHE_PATH.exists():
        try:
            payload = WEB_STRUCT_CACHE_PATH.read_text(encoding="utf-8")
            return json.loads(payload)
        except Exception as e:
            print(f"⚠️ Error reading cached struct: {e}")
    
    # Priority 3: Network fetch
    try:
        print(f"Fetching struct from network: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "IVY-Queue/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = resp.read().decode("utf-8")
        
        # Validate
        data = json.loads(payload)
        
        # Cache for next time
        WEB_STRUCT_CACHE_PATH.write_text(payload, encoding="utf-8")
        print(f"✓ Cached struct for future use")
        return data
    except Exception as e:
        print(f"❌ Failed to fetch struct: {e}")
        raise RuntimeError(f"Cannot load web struct from {url}: {e}")


def extract_web_lessons_for_subject(web_struct, subject_key):
    cfg = SUBJECT_WEB_MAP.get(subject_key)
    if not cfg:
        return []

    lessons = []
    target_subjects = {normalize_key(x) for x in cfg.get("subjects", set())}
    target_categories = {normalize_key(x) for x in cfg.get("categories", set())}

    for subject in web_struct:
        if not isinstance(subject, dict):
            continue
        subject_name = normalize_key(subject.get("subject", ""))
        sections = subject.get("sections", [])
        for section in sections:
            if not isinstance(section, dict):
                continue
            for lesson in section.get("lessons", []):
                if not isinstance(lesson, dict):
                    continue
                categories = lesson.get("categories", [])
                categories_norm = {normalize_key(x) for x in categories if isinstance(x, str)}
                match_subject = subject_name in target_subjects
                match_category = bool(categories_norm & target_categories)
                if not (match_subject or match_category):
                    continue
                lessons.append(
                    {
                        "subject": subject.get("subject"),
                        "section": section.get("title"),
                        "section_path": section.get("path"),
                        "title": lesson.get("title"),
                        "file": lesson.get("file"),
                        "topic": lesson.get("topic"),
                        "time_estimate": lesson.get("time_estimate"),
                        "level": lesson.get("level"),
                        "tags": lesson.get("tags", []),
                    }
                )
    return lessons


def run_missing_lesson_generation(payload):
    subject = payload["subject"]
    web_url = payload.get("web_struct_url", WEB_STRUCT_URL)

    plan_path = ROOT / "bots" / f"plan_{subject}.json"
    if not plan_path.exists():
        raise RuntimeError(f"Lesson plan file missing for {subject}: {plan_path}")

    planned = json.loads(plan_path.read_text(encoding="utf-8"))
    planned_keys = {normalize_key(item.get("lesson_title", "")) for item in planned if isinstance(item, dict)}

    web_struct = load_web_struct(web_url)
    web_lessons = extract_web_lessons_for_subject(web_struct, subject)

    missing = []
    for lesson in web_lessons:
        title = lesson.get("title", "")
        if not title:
            continue
        key = normalize_key(title)
        if key in planned_keys:
            continue

        missing.append(
            {
                "subject_key": subject,
                "source_subject": lesson.get("subject"),
                "source_section": lesson.get("section"),
                "source_section_path": lesson.get("section_path"),
                "topic_code": lesson.get("topic"),
                "lesson_title": title,
                "lesson_file": lesson.get("file"),
                "level": lesson.get("level", "SL/HL"),
                "time_estimate": lesson.get("time_estimate", 20),
                "tags": lesson.get("tags", []),
                "integration": {
                    "practice": True,
                    "exemplars": True,
                    "timer": True,
                },
                "draft_markdown": (
                    f"# {title}\\n\\n"
                    f"Topic: {lesson.get('topic', 'TBD')}\\n\\n"
                    "## Objectives\\n- Define the key concept.\\n- Solve standard IB-style problems.\\n"
                    "## Guided Explanation\\nAdd curriculum-aligned explanation here.\\n"
                    "## Worked Examples\\nAdd SL and HL examples here.\\n"
                    "## Common Mistakes\\nAdd error patterns and fixes here.\\n"
                    "## Practice Bridge\\nLink this lesson into practice filters.\\n"
                ),
            }
        )

    out = ROOT / "bots" / f"plan_missing_{subject}.json"
    out.write_text(json.dumps(missing, indent=2), encoding="utf-8")


def run_verification(payload):
    check = payload["check"]
    target = ROOT / payload.get("target", "questions.json")

    if not target.exists():
        raise RuntimeError(f"Target file missing: {target}")

    raw = json.loads(target.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "questions" in raw:
        data = raw["questions"]
    elif isinstance(raw, list):
        data = raw
    else:
        raise RuntimeError("Unsupported questions.json format; expected list or {questions:[...]} object")

    if check == "schema_validation":
        required = {"id", "subject", "topic", "subtopic", "type", "difficulty", "title", "stem", "mark_scheme"}
        for i, item in enumerate(data):
            missing = required - set(item.keys())
            if missing:
                raise RuntimeError(f"Schema error at index {i}: missing {sorted(missing)}")

    elif check == "duplicate_detection":
        ids = [x.get("id") for x in data]
        if len(ids) != len(set(ids)):
            raise RuntimeError("Duplicate question IDs detected")

    elif check == "difficulty_distribution":
        diffs = [x.get("difficulty") for x in data]
        if not any(d == "core" for d in diffs):
            raise RuntimeError("No core questions found")

    elif check == "topic_coverage":
        topics = {(x.get("subject"), x.get("topic")) for x in data if x.get("subject") and x.get("topic")}
        subjects = {x.get("subject") for x in data if x.get("subject")}
        min_topics = max(8, len(subjects) * 4)
        if len(topics) < min_topics:
            raise RuntimeError(
                f"Topic coverage too low: found {len(topics)} topics across {len(subjects)} subjects, expected at least {min_topics}"
            )

    elif check == "latex_syntax":
        bad = [x.get("id") for x in data if "$$" in x.get("stem", "") and x.get("stem", "").count("$$") % 2 != 0]
        if bad:
            raise RuntimeError(f"Invalid LaTeX delimiters in {len(bad)} questions")


def run_job(kind, payload):
    if kind == "practice_generation":
        run_practice_generation(payload)
    elif kind == "lesson_planning":
        run_lesson_planning(payload)
    elif kind == "missing_lesson_generation":
        run_missing_lesson_generation(payload)
    elif kind == "verification":
        run_verification(payload)
    else:
        raise RuntimeError(f"Unknown job kind: {kind}")


def worker_loop(conn, poll_seconds=2):
    print("[queue] worker started")
    last_recovery_check = 0
    while True:
        now_ts = int(time.time())
        if now_ts - last_recovery_check >= poll_seconds:
            recovered, failed = recover_stale_running_jobs(conn)
            if recovered or failed:
                print(f"[queue] recovered stale jobs: queued={recovered}, failed={failed}")
            last_recovery_check = now_ts

        job = next_job(conn)
        if not job:
            time.sleep(poll_seconds)
            continue

        job_id, kind, payload_json, retries, max_retries = job
        payload = json.loads(payload_json)

        try:
            mark_started(conn, job_id)
            run_job(kind, payload)
            mark_done(conn, job_id)
            print(f"[queue] job #{job_id} done: {kind}")
        except Exception as exc:
            mark_failed(conn, job_id, retries, max_retries, exc)
            print(f"[queue] job #{job_id} failed: {kind} -> {exc}")


def show_status(conn):
    rows = conn.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status ORDER BY status").fetchall()
    if not rows:
        print("No jobs in queue.")
        return
    for status, count in rows:
        print(f"{status}: {count}")

    running_rows = conn.execute("SELECT started_at FROM jobs WHERE status='running' AND started_at IS NOT NULL").fetchall()
    if running_rows:
        now_ts = int(time.time())
        ages = [max(0, now_ts - int(started_at)) for (started_at,) in running_rows]
        oldest = max(ages)
        newest = min(ages)
        stale = sum(1 for a in ages if a >= STALE_RUNNING_SECONDS)
        print(f"running_age_oldest_sec: {oldest}")
        print(f"running_age_newest_sec: {newest}")
        print(f"running_stale_candidates: {stale}")

    practice_rows = conn.execute("SELECT payload, status FROM jobs WHERE kind='practice_generation'").fetchall()
    if practice_rows:
        target_total = 0
        done_jobs = 0
        for payload_json, status in practice_rows:
            try:
                payload = json.loads(payload_json)
                target_total += int(payload.get("target_questions", 0))
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
            if status == "done":
                done_jobs += 1

        question_count = 0
        if OUTPUT_PATH.exists():
            try:
                raw = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    question_count = len(raw.get("questions", []))
                elif isinstance(raw, list):
                    question_count = len(raw)
            except Exception:
                question_count = 0

        pct = (question_count / target_total * 100.0) if target_total else 0.0
        print(f"practice_jobs_done: {done_jobs}/{len(practice_rows)}")
        print(f"question_progress: {question_count}/{target_total} ({pct:.1f}%)")

    latest_created = conn.execute("SELECT MAX(created_at) FROM jobs").fetchone()[0]
    if latest_created is not None:
        batch_rows = conn.execute(
            "SELECT kind, status, payload FROM jobs WHERE created_at=?",
            (latest_created,),
        ).fetchall()
        if batch_rows:
            print(f"latest_batch_jobs: {len(batch_rows)}")
            status_counts = {}
            for _, status, _ in batch_rows:
                status_counts[status] = status_counts.get(status, 0) + 1
            for status in sorted(status_counts):
                print(f"latest_batch_{status}: {status_counts[status]}")

            batch_practice = [r for r in batch_rows if r[0] == "practice_generation"]
            if batch_practice:
                batch_target = 0
                batch_done = 0
                for _, status, payload_json in batch_practice:
                    try:
                        payload = json.loads(payload_json)
                        batch_target += int(payload.get("target_questions", 0))
                    except (json.JSONDecodeError, ValueError, TypeError):
                        pass
                    if status == "done":
                        batch_done += 1
                print(f"latest_batch_practice_jobs_done: {batch_done}/{len(batch_practice)}")
                print(f"latest_batch_practice_target: {batch_target}")


def main():
    parser = argparse.ArgumentParser(description="IB Practice Platform bot queue")
    parser.add_argument("command", choices=["seed", "worker", "status"], help="Queue command")
    parser.add_argument("--target", type=int, default=80000, help="Target total practice question count for seed")
    parser.add_argument("--poll", type=int, default=2, help="Worker poll seconds")
    args = parser.parse_args()

    conn = connect_db()

    if args.command == "seed":
        enqueue_default_queue(conn, total_questions=args.target)
        print(f"Seeded queue for target={args.target} questions")
    elif args.command == "worker":
        worker_loop(conn, poll_seconds=args.poll)
    elif args.command == "status":
        show_status(conn)


if __name__ == "__main__":
    main()
