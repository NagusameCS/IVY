#!/usr/bin/env python3
"""
Quality and accuracy verifier for generated IB lessons.

Checks all generated lesson markdown files against plan_*.json and reports:
- Coverage (missing/extra lessons)
- Structure compliance (headings, summary, examples)
- Curriculum signal checks (code/title/topic/tag mentions)
- Subject-specific sanity checks

Outputs:
- ib-practice-platform/data/lesson_quality_report.json
- ib-practice-platform/data/lesson_quality_report.md
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
BOTS_DIR = ROOT / "bots"
LESSONS_DIR = ROOT / "data" / "lessons"
REPORT_JSON = ROOT / "data" / "lesson_quality_report.json"
REPORT_MD = ROOT / "data" / "lesson_quality_report.md"

CORE_SUBJECTS = [
    "biology",
    "business",
    "chemistry",
    "computer_science",
    "economics",
    "math_aa",
    "math_ai",
    "physics",
]

SUBJECT_EXPECTED_TERMS = {
    "biology": ["cell", "enzyme", "dna", "organism", "homeostasis"],
    "business": ["market", "revenue", "profit", "stakeholder", "strategy"],
    "chemistry": ["mole", "bond", "reaction", "equilibrium", "concentration"],
    "computer_science": ["algorithm", "data", "complexity", "program", "system"],
    "economics": ["demand", "supply", "market", "price", "elasticity"],
    "math_aa": ["function", "equation", "derivative", "graph", "proof"],
    "math_ai": ["model", "data", "probability", "statistics", "graph"],
    "physics": ["force", "energy", "motion", "field", "velocity"],
}

SUBJECT_MATH_HEAVY = {"math_aa", "math_ai", "physics", "chemistry", "economics"}


@dataclass
class LessonCheck:
    subject: str
    curriculum_code: str
    lesson_title: str
    file_exists: bool
    file_path: str
    word_count: int
    has_key_concepts: bool
    has_summary: bool
    has_examples: bool
    has_exam_tip: bool
    has_curriculum_code_signal: bool
    foreign_code_hits: int
    has_title_signal: bool
    tag_hits: int
    expected_tag_count: int
    subject_term_hits: int
    has_math_signal_if_expected: bool
    score: float
    status: str
    issues: List[str]


def load_plans() -> Dict[str, List[dict]]:
    plans: Dict[str, List[dict]] = {}
    for subject in CORE_SUBJECTS:
        plan_path = BOTS_DIR / f"plan_{subject}.json"
        if not plan_path.exists():
            plans[subject] = []
            continue
        plans[subject] = json.loads(plan_path.read_text(encoding="utf-8"))
    return plans


def expected_file_path(subject: str, curriculum_code: str, title: str) -> Path:
    safe_title = title.lower().replace(" ", "_").replace("/", "_")
    safe_title = re.sub(r"[^a-z0-9._-]", "", safe_title)
    safe_title = safe_title.strip("._-") or "untitled"
    return LESSONS_DIR / subject / f"{curriculum_code}_{safe_title}.md"


def tokenize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def score_lesson(check: LessonCheck) -> float:
    points = 0.0
    points += 10 if check.file_exists else 0
    points += 10 if check.word_count >= 700 else 0
    points += 10 if check.word_count >= 1200 else 0
    points += 10 if check.has_key_concepts else 0
    points += 10 if check.has_summary else 0
    points += 10 if check.has_examples else 0
    points += 10 if check.has_exam_tip else 0
    points += 10 if check.has_curriculum_code_signal else 0
    points += 10 if check.has_title_signal else 0
    if check.expected_tag_count > 0:
        points += 5 if check.tag_hits >= max(1, check.expected_tag_count // 3) else 0
        points += 5 if check.tag_hits >= max(2, check.expected_tag_count // 2) else 0
    else:
        points += 10
    points += 5 if check.subject_term_hits >= 2 else 0
    points += 5 if check.has_math_signal_if_expected else 0
    return min(100.0, points)


def evaluate_lesson(subject: str, lesson: dict, all_codes: List[str]) -> LessonCheck:
    topic = lesson.get("topic", "")
    subtopic = lesson.get("subtopic", "")
    curriculum_code = f"{topic}.{subtopic}"
    title = lesson.get("lesson_title", "Untitled")
    tags = lesson.get("tags", [])

    path = expected_file_path(subject, curriculum_code, title)
    issues: List[str] = []

    if not path.exists():
        return LessonCheck(
            subject=subject,
            curriculum_code=curriculum_code,
            lesson_title=title,
            file_exists=False,
            file_path=str(path.relative_to(ROOT)),
            word_count=0,
            has_key_concepts=False,
            has_summary=False,
            has_examples=False,
            has_exam_tip=False,
            has_curriculum_code_signal=False,
            foreign_code_hits=0,
            has_title_signal=False,
            tag_hits=0,
            expected_tag_count=len(tags),
            subject_term_hits=0,
            has_math_signal_if_expected=(subject not in SUBJECT_MATH_HEAVY),
            score=0.0,
            status="missing",
            issues=["missing_file"],
        )

    content = path.read_text(encoding="utf-8", errors="replace")
    text = tokenize(content)
    words = len(re.findall(r"\b[\w-]+\b", content))

    has_key_concepts = "## key concepts" in text
    has_summary = "## summary" in text
    has_examples = "**example:**" in text or "example:" in text
    has_exam_tip = "**exam tip:**" in text or "exam tip:" in text

    code_signal = curriculum_code.lower() in text
    this_code = curriculum_code.lower()
    foreign_code_hits = 0
    for code in all_codes:
        if code == this_code:
            continue
        if code in text:
            foreign_code_hits += 1

    # Detect references that look like curriculum codes, even if absent from plan files.
    code_like_refs = re.findall(
        r"\b(?:[A-Z]\.[A-Z]\.\d+|[A-Z]\.\d+\.\d+|[A-Z]\d\.[A-Z]\d\.\d+|\d+\.\d+\.\d+)\b",
        content,
    )
    for ref in code_like_refs:
        if ref.lower() != this_code:
            foreign_code_hits += 1
    title_signal = tokenize(title) in text

    tag_hits = 0
    for tag in tags:
        token = tag.replace("-", " ").lower()
        if token in text:
            tag_hits += 1

    subject_hits = 0
    for term in SUBJECT_EXPECTED_TERMS.get(subject, []):
        if term in text:
            subject_hits += 1

    if subject in SUBJECT_MATH_HEAVY:
        has_math_signal = bool(re.search(r"\$[^$]+\$|\$\$[^$]+\$\$|\\frac|\\sum|\\int", content))
    else:
        has_math_signal = True

    if words < 700:
        issues.append("low_word_count")
    if not has_key_concepts:
        issues.append("missing_key_concepts_section")
    if not has_summary:
        issues.append("missing_summary_section")
    if not code_signal:
        issues.append("missing_curriculum_code_signal")
    if foreign_code_hits > 0:
        issues.append("foreign_curriculum_reference")
    if tag_hits < max(1, len(tags) // 3) if tags else False:
        issues.append("low_tag_coverage")
    if subject_hits < 2:
        issues.append("low_subject_term_hits")
    if not has_math_signal and subject in SUBJECT_MATH_HEAVY:
        issues.append("missing_math_signal")

    check = LessonCheck(
        subject=subject,
        curriculum_code=curriculum_code,
        lesson_title=title,
        file_exists=True,
        file_path=str(path.relative_to(ROOT)),
        word_count=words,
        has_key_concepts=has_key_concepts,
        has_summary=has_summary,
        has_examples=has_examples,
        has_exam_tip=has_exam_tip,
        has_curriculum_code_signal=code_signal,
        foreign_code_hits=foreign_code_hits,
        has_title_signal=title_signal,
        tag_hits=tag_hits,
        expected_tag_count=len(tags),
        subject_term_hits=subject_hits,
        has_math_signal_if_expected=has_math_signal,
        score=0.0,
        status="ok",
        issues=issues,
    )
    check.score = score_lesson(check)

    if (
        check.score < 65
        or "missing_curriculum_code_signal" in issues
        or "missing_summary_section" in issues
        or "foreign_curriculum_reference" in issues
    ):
        check.status = "needs_review"
    elif issues:
        check.status = "warning"

    return check


def summarize(results: List[LessonCheck]) -> Dict[str, object]:
    total = len(results)
    completed = sum(1 for r in results if r.file_exists)
    missing = sum(1 for r in results if not r.file_exists)
    needs_review = sum(1 for r in results if r.status == "needs_review")
    warnings = sum(1 for r in results if r.status == "warning")
    avg_score = round(sum(r.score for r in results) / total, 2) if total else 0.0

    by_subject: Dict[str, Dict[str, object]] = {}
    for subject in CORE_SUBJECTS:
        rows = [r for r in results if r.subject == subject]
        if not rows:
            continue
        by_subject[subject] = {
            "total": len(rows),
            "completed": sum(1 for r in rows if r.file_exists),
            "missing": sum(1 for r in rows if not r.file_exists),
            "needs_review": sum(1 for r in rows if r.status == "needs_review"),
            "warnings": sum(1 for r in rows if r.status == "warning"),
            "average_score": round(sum(r.score for r in rows) / len(rows), 2),
        }

    return {
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "overall": {
            "total_lessons": total,
            "completed": completed,
            "missing": missing,
            "needs_review": needs_review,
            "warnings": warnings,
            "average_score": avg_score,
        },
        "by_subject": by_subject,
    }


def write_reports(summary: Dict[str, object], results: List[LessonCheck]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": summary,
        "results": [asdict(r) for r in results],
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Lesson Quality Report")
    lines.append("")
    overall = summary["overall"]
    lines.append(f"- Total lessons in plans: {overall['total_lessons']}")
    lines.append(f"- Completed files: {overall['completed']}")
    lines.append(f"- Missing files: {overall['missing']}")
    lines.append(f"- Needs review: {overall['needs_review']}")
    lines.append(f"- Warnings: {overall['warnings']}")
    lines.append(f"- Average score: {overall['average_score']}")
    lines.append("")

    lines.append("## By Subject")
    for subject, data in summary["by_subject"].items():
        lines.append(
            f"- {subject}: {data['completed']}/{data['total']} complete, "
            f"score {data['average_score']}, reviews {data['needs_review']}, warnings {data['warnings']}"
        )
    lines.append("")

    lines.append("## Critical Items (Needs Review)")
    critical = [r for r in results if r.status == "needs_review"]
    if not critical:
        lines.append("- None")
    else:
        for r in critical[:100]:
            lines.append(
                f"- {r.subject} {r.curriculum_code} {r.lesson_title}: "
                f"score {r.score}, issues={', '.join(r.issues)}"
            )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_quality_check() -> int:
    plans = load_plans()
    all_codes: List[str] = []
    for lessons in plans.values():
        for lesson in lessons:
            all_codes.append(f"{lesson.get('topic', '')}.{lesson.get('subtopic', '')}".lower())

    checks: List[LessonCheck] = []
    for subject, lessons in plans.items():
        for lesson in lessons:
            checks.append(evaluate_lesson(subject, lesson, all_codes))

    summary = summarize(checks)
    write_reports(summary, checks)

    overall = summary["overall"]
    print("Lesson quality check complete")
    print(
        f"Total={overall['total_lessons']} Completed={overall['completed']} "
        f"Missing={overall['missing']} NeedsReview={overall['needs_review']} "
        f"Warnings={overall['warnings']} AvgScore={overall['average_score']}"
    )
    print(f"JSON: {REPORT_JSON}")
    print(f"MD:   {REPORT_MD}")

    return 0


if __name__ == "__main__":
    raise SystemExit(run_quality_check())
