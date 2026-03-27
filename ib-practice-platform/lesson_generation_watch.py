#!/usr/bin/env python3
"""Watch lesson generation progress and run quality verification when complete."""

import sqlite3
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "bots" / "queue.db"


def get_status() -> tuple[int, int, int, int]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM lessons")
    total = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM lessons WHERE status='pending'")
    pending = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM lessons WHERE status='completed'")
    completed = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM lessons WHERE status='failed'")
    failed = cur.fetchone()[0] or 0
    conn.close()
    return total, pending, completed, failed


def main() -> int:
    print("Watching lesson generation status...")
    while True:
        total, pending, completed, failed = get_status()
        print(f"Status: total={total} pending={pending} completed={completed} failed={failed}")
        if pending == 0:
            break
        time.sleep(120)

    print("Generation finished. Running quality verification...")
    rc = subprocess.call(["python", "lesson_quality_check.py"], cwd=str(ROOT))
    if rc != 0:
        print("Quality verification failed.")
        return rc

    print("Quality verification complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
