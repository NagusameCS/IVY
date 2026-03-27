#!/usr/bin/env python3
"""
Lesson Generator for IvyStudy
Generates IB curriculum lessons using Ollama + LLM with custom markdown syntax.
Queues generation jobs and executes them locally.

Usage:
    python lesson_generator.py --queue                      # Queue all lessons
    python lesson_generator.py --generate 5                 # Generate 5 lessons
    python lesson_generator.py --all                        # Generate everything
    python lesson_generator.py --status                     # Show status
"""

from __future__ import annotations
import json
import os
import re
import sys
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Put parent dir in path to avoid queue.py conflict
sys.path.insert(0, str(Path(__file__).parent))

try:
    import requests
except ImportError as e:
    print("Error: 'requests' module not found. Install with: pip install requests")
    sys.exit(1)

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL_DEFAULT = "mistral"  # Preferred default when installed
LESSONS_DIR = Path(__file__).parent / "data" / "lessons"
BOTS_DIR = Path(__file__).parent / "bots"
DB_PATH = BOTS_DIR / "queue.db"
MAX_RETRIES = 3
TIMEOUT = 300  # 5 minutes per lesson


def sanitize_title_for_filename(title: str) -> str:
    safe_title = title.lower().replace(" ", "_").replace("/", "_")
    safe_title = re.sub(r"[^a-z0-9._-]", "", safe_title)
    return safe_title.strip("._-") or "untitled"


def lesson_output_path(subject: str, curriculum_code: str, lesson_title: str) -> Path:
    subject_dir = LESSONS_DIR / subject
    filename = f"{curriculum_code}_{sanitize_title_for_filename(lesson_title)}.md"
    return subject_dir / filename

# Custom Markdown Syntax Rules for IB Lessons
MARKDOWN_RULES = """
Use the following markdown syntax for all lessons:

**Structure:**
1. Start with brief 1-2 line overview
2. Use ## Key Concepts (main learning points)
3. Use ### Subtopic headers for detailed sections
4. End with ## Summary (3-4 sentences recap)

**Formatting:**
- Bold key terms: **term name**
- Italic for emphasis: *emphasis*
- Code blocks for formulas/examples: ```formula``` or ```python``` blocks
- Math: Use $equation$ for inline, $$equation$$ for display mode
- Lists: - bullet or 1. numbered

**Callout Boxes (use blockquotes):**
- > **Important:** key concept
- > **Note:** additional info
- > **Example:** worked example
- > **Exam Tip:** exam-relevant info

**Examples:**
- Include 2-3 worked examples per lesson
- Use actual IB-style problem formats
- Show step-by-step solutions

**Length:**
- 1500-2500 words total
- 5-7 main concept sections
- 2-3 worked examples

**IB Integration:**
- Reference the curriculum code (e.g., "A.1.1 Water")
- Note SL/HL extensions if applicable
- Include exam command words (describe, explain, evaluate, etc.)
"""

SYSTEM_PROMPT = f"""You are an expert IB Curriculum educator creating detailed, engaging lessons.
{MARKDOWN_RULES}

Generate lessons that are:
1. Scientifically/academically accurate
2. Appropriate for 16-18 year olds
3. Following IB syllabus specifications exactly
4. Engaging with clear explanations
5. Including practical examples and applications

Do NOT include any HTML, only markdown.
Do NOT include lesson metadata or titles (they are added separately).
Start directly with the content."""


def init_lessons_db():
    """Initialize lessons database table if needed."""
    os.makedirs(LESSONS_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if lessons table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='lessons'
    """)
    
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                curriculum_code TEXT NOT NULL,
                lesson_title TEXT NOT NULL,
                topic_name TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                content TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                generated_at TIMESTAMP,
                retry_count INTEGER DEFAULT 0,
                UNIQUE(subject, curriculum_code)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_lessons_status 
            ON lessons(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_lessons_subject 
            ON lessons(subject)
        """)
    
    conn.commit()
    conn.close()


def load_plan_files() -> Dict[str, List[dict]]:
    """Load all plan_*.json files and organize by subject."""
    plans = {}
    
    for plan_file in BOTS_DIR.glob("plan_*.json"):
        subject = plan_file.stem.replace("plan_", "")
        
        # Skip missing plans
        if "missing" in subject:
            continue
        
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                plans[subject] = json.load(f)
            print(f"✓ Loaded {subject}: {len(plans[subject])} lessons")
        except Exception as e:
            print(f"✗ Error loading {plan_file}: {e}")
    
    return plans


def queue_lesson_jobs(plans: Dict[str, List[dict]]) -> int:
    """Queue all lessons from plan files into the database."""
    init_lessons_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total_queued = 0
    
    for subject, lessons in plans.items():
        for lesson in lessons:
            curriculum_code = f"{lesson['topic']}.{lesson['subtopic']}"
            lesson_title = lesson.get('lesson_title', 'Untitled')
            topic_name = lesson.get('topic_name', '')
            
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO lessons 
                    (subject, curriculum_code, lesson_title, topic_name, status)
                    VALUES (?, ?, ?, ?, 'pending')
                """, (subject, curriculum_code, lesson_title, topic_name))
                
                if cursor.rowcount > 0:
                    total_queued += 1
            except sqlite3.IntegrityError:
                # Already queued
                pass
    
    conn.commit()
    conn.close()
    
    return total_queued


def generate_lesson_with_ollama(
    subject: str,
    curriculum_code: str,
    lesson_title: str,
    topic_name: str,
    model_name: str,
    retry: int = 0
) -> Optional[str]:
    """Generate a single lesson using Ollama API."""
    
    prompt = f"""Generate an IB {subject.upper()} lesson for:

Title: {lesson_title}
Curriculum: {curriculum_code} - {topic_name}
Subject: {subject}

Create a comprehensive, engaging lesson following the markdown syntax rules provided in your system instructions.

Begin the lesson content directly (no title, no metadata):"""

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model_name,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9
            },
            timeout=TIMEOUT
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "response" in result:
            return result["response"].strip()
        else:
            return None
            
    except requests.exceptions.ConnectionError:
        if retry < MAX_RETRIES:
            print(f"⚠ Connection failed, retry {retry + 1}/{MAX_RETRIES}...")
            time.sleep(5)
            return generate_lesson_with_ollama(subject, curriculum_code, lesson_title, topic_name, model_name, retry + 1)
        else:
            raise Exception(f"Failed to connect to Ollama after {MAX_RETRIES} retries. Is it running?")
    except requests.exceptions.Timeout:
        if retry < MAX_RETRIES:
            print(f"⚠ Timeout, retry {retry + 1}/{MAX_RETRIES}...")
            time.sleep(5)
            return generate_lesson_with_ollama(subject, curriculum_code, lesson_title, topic_name, model_name, retry + 1)
        else:
            raise Exception(f"Generation timeout after {MAX_RETRIES} retries")
    except Exception as e:
        raise Exception(f"Ollama generation error: {str(e)}")


def save_lesson_file(
    subject: str,
    curriculum_code: str,
    lesson_title: str,
    content: str
) -> Path:
    """Save generated lesson to markdown file."""
    filepath = lesson_output_path(subject, curriculum_code, lesson_title)
    os.makedirs(filepath.parent, exist_ok=True)
    
    # Prepend lesson metadata as YAML frontmatter
    full_content = f"""---
subject: {subject}
curriculum_code: {curriculum_code}
title: {lesson_title}
generated_at: {datetime.now().isoformat()}
---

{content}
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return filepath


def process_pending_lessons(model_name: str, limit: Optional[int] = None) -> Dict[str, int]:
    """Process pending lessons in the database."""
    init_lessons_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get pending lessons
    query = "SELECT id, subject, curriculum_code, lesson_title, topic_name FROM lessons WHERE status = 'pending'"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    pending = cursor.fetchall()
    
    stats = {
        "total": len(pending),
        "generated": 0,
        "failed": 0,
        "skipped": 0
    }
    
    for lesson_id, subject, curriculum_code, lesson_title, topic_name in pending:
        try:
            print(f"\n📚 Generating: {subject.upper()} - {curriculum_code} ({lesson_title})")
            print(f"   Prompt: {lesson_title} (IB {subject} - {topic_name})")

            existing_path = lesson_output_path(subject, curriculum_code, lesson_title)
            if existing_path.exists() and existing_path.stat().st_size > 1200:
                existing_preview = existing_path.read_text(encoding="utf-8", errors="replace")[:5000]
                cursor.execute(
                    """
                    UPDATE lessons
                    SET status = 'completed', content = ?, generated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (existing_preview, lesson_id),
                )
                print(f"   ↷ Skipped (already exists): {existing_path.relative_to(LESSONS_DIR.parent)}")
                stats["generated"] += 1
                conn.commit()
                continue
            
            # Generate content
            content = generate_lesson_with_ollama(subject, curriculum_code, lesson_title, topic_name, model_name)
            
            if content and len(content) > 200:  # Minimum length check
                # Save to file
                filepath = save_lesson_file(subject, curriculum_code, lesson_title, content)
                
                # Update database
                cursor.execute("""
                    UPDATE lessons 
                    SET status = 'completed', content = ?, generated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (content[:5000], lesson_id))  # Store first 5000 chars in DB
                
                print(f"   ✓ Saved to {filepath.relative_to(LESSONS_DIR.parent)}")
                stats["generated"] += 1
                conn.commit()
            else:
                raise Exception("Generated content too short or empty")
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ✗ Error: {error_msg}")
            
            # Update retry count
            cursor.execute("SELECT retry_count FROM lessons WHERE id = ?", (lesson_id,))
            result = cursor.fetchone()
            if result:
                retry_count = result[0] + 1
            else:
                retry_count = 1
            
            if retry_count >= MAX_RETRIES:
                status = "failed"
                stats["failed"] += 1
            else:
                status = "pending"
                stats["skipped"] += 1
            
            cursor.execute("""
                UPDATE lessons 
                SET status = ?, error_message = ?, retry_count = ?
                WHERE id = ?
            """, (status, error_msg, retry_count, lesson_id))
            conn.commit()
    
    conn.commit()
    conn.close()
    
    return stats


def get_status() -> Dict:
    """Get generation status from database."""
    if not DB_PATH.exists():
        return {
            "total": 0,
            "pending": 0,
            "completed": 0,
            "failed": 0
        }
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM lessons")
    total = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM lessons WHERE status = 'pending'")
    pending = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM lessons WHERE status = 'completed'")
    completed = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM lessons WHERE status = 'failed'")
    failed = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total": total,
        "pending": pending,
        "completed": completed,
        "failed": failed
    }


def resolve_ollama_model(requested_model: Optional[str] = None) -> Optional[str]:
    """Check Ollama availability and return a usable model name."""
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        models = response.json().get("models", [])
        model_names = [m.get("name", "") for m in models]

        if not model_names:
            print("✗ Ollama is running but no models are installed.")
            return None

        def pick_match(name: str) -> Optional[str]:
            if name in model_names:
                return name
            for installed in model_names:
                if installed.startswith(f"{name}:"):
                    return installed
            return None

        if requested_model:
            selected = pick_match(requested_model)
            if selected:
                return selected
            print(f"⚠ Requested model '{requested_model}' not found.")

        selected = pick_match(OLLAMA_MODEL_DEFAULT)
        if selected:
            return selected

        preferred_fallbacks = [
            "gemma3:4b",
            "gemma3:12b",
            "glm-4.7-flash:latest",
            "phi35test:latest",
            "smollm2:135m",
        ]
        for candidate in preferred_fallbacks:
            if candidate in model_names:
                print(f"⚠ Default model '{OLLAMA_MODEL_DEFAULT}' not found; using '{candidate}'.")
                return candidate

        print(f"⚠ Default model '{OLLAMA_MODEL_DEFAULT}' not found; using first available model '{model_names[0]}'.")
        return model_names[0]
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print(f"  Make sure Ollama is running at {OLLAMA_API_URL}")
        return None


def main():
    """Main entry point for lesson generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate IB curriculum lessons using Ollama")
    parser.add_argument("--queue", action="store_true", help="Queue lessons from plan files")
    parser.add_argument("--generate", type=int, nargs="?", const=5, metavar="N",
                        help="Generate N pending lessons (default: 5)")
    parser.add_argument("--status", action="store_true", help="Show generation status")
    parser.add_argument("--subject", type=str, help="Queue/generate only specific subject")
    parser.add_argument("--all", action="store_true", help="Generate all pending lessons")
    parser.add_argument("--model", type=str, help="Ollama model name override")
    
    args = parser.parse_args()
    
    # Show banner
    print("\n" + "="*60)
    print("  IvyStudy Lesson Generator (Ollama + LLM)")
    print("="*60)

    selected_model: Optional[str] = None
    
    # Check Ollama first (only if generating, not if just queuing)
    if args.generate or args.all:
        selected_model = resolve_ollama_model(args.model)
        if not selected_model:
            print("\n✗ Cannot proceed without Ollama. Exiting.")
            sys.exit(1)
    
    # Queue lessons
    if args.queue:
        print("\n📋 Queueing lessons from plan files...")
        plans = load_plan_files()
        
        if args.subject:
            plans = {k: v for k, v in plans.items() if k == args.subject}
        
        total_queued = queue_lesson_jobs(plans)
        print(f"\n✓ Queued {total_queued} lesson(s)")
    
    # Show status
    if args.status or not args.generate and not args.queue and not args.all:
        status = get_status()
        print(f"\n📊 Generation Status:")
        print(f"   Total:     {status['total']}")
        print(f"   Pending:   {status['pending']}")
        print(f"   Completed: {status['completed']}")
        print(f"   Failed:    {status['failed']}")
        
        if status['completed'] > 0:
            print(f"   Output:    {LESSONS_DIR.relative_to(LESSONS_DIR.parent.parent)}/")
    
    # Generate lessons
    if args.generate or args.all:
        limit = None if args.all else args.generate
        print(f"\n🚀 Starting lesson generation (limit: {limit or 'none'})...")
        print(f"   Model: {selected_model}")
        print(f"   Timeout: {TIMEOUT}s per lesson\n")
        
        try:
            stats = process_pending_lessons(model_name=selected_model, limit=limit)
            
            print(f"\n✓ Generation Complete!")
            print(f"   Generated: {stats['generated']}")
            print(f"   Failed:    {stats['failed']}")
            print(f"   Skipped:   {stats['skipped']}")
            
            # Show new status
            status = get_status()
            print(f"\n📊 Updated Status:")
            print(f"   Pending:   {status['pending']}")
            print(f"   Completed: {status['completed']}")
            
        except KeyboardInterrupt:
            print("\n\n⚠ Generation interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
