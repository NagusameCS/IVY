# 🚀 Quick Start - Lesson Generation

## In 3 Steps

### Step 1: Install Ollama
Download from https://ollama.ai and install

### Step 2: Start Ollama & Pull Model
```bash
ollama serve
# In another terminal:
ollama pull mistral
```
(Mistral is fast. ~4GB download, ~8GB RAM needed)

### Step 3: Generate Lessons
Double-click: `start_lesson_generator.bat`

Or from command prompt:
```bash
cd ivystudy
start_lesson_generator.bat --all
```

## What It Does
- Reads `ib-practice-platform/bots/plan_*.json` (206 lessons queued)
- Uses Ollama to generate IB-standard markdown lessons locally
- Saves to `ib-practice-platform/data/lessons/{subject}/{code}_{title}.md`
- Stores metadata in `queue.db`

## Time Estimate
- **5 lessons**: 15-20 minutes
- **All 206 lessons**: 4-6 hours (runs continuously)

## Status Check
```bash
start_lesson_generator.bat --status
```

Shows:
- Total: 206
- Pending: (how many left)
- Completed: (how many done)
- Failed: (any errors)

## Files
- `start_lesson_generator.bat` — Windows launcher
- `lesson_generator.py` — Main script
- `LESSON_GENERATOR_README.md` — Full documentation
- `SESSION_COMPLETION_REPORT.md` — Complete session summary

## Example Output
```
✓ Loaded biology: 16 lessons
✓ Loaded math_aa: 81 lessons
...
✓ Queued 206 lesson(s)

📊 Generation Status:
   Total:     206
   Pending:   206
   Completed: 0
```

## Troubleshooting

**Can't find Ollama?**
→ Make sure it's running: `ollama serve`

**Model not found?**
→ Pull it: `ollama pull mistral`

**Want a different model?**
→ Edit `OLLAMA_MODEL` in `lesson_generator.py`
→ Larger models = better quality but slower

## Commands Reference

| Command | What It Does |
|---------|-------------|
| `--queue` | Queue all lessons (once per session) |
| `--generate 5` | Generate 5 lessons |
| `--generate 50` | Generate 50 lessons |
| `--all` | Generate all 206 lessons |
| `--status` | Show progress |
| `--subject biology` | Queue/generate only one subject |

## Advanced

**Generated lessons contain:**
- YAML metadata (subject, curriculum code, timestamp)
- IB-formatted markdown
- Math equations (LaTeX)
- Code examples
- Worked problems with solutions
- Callout boxes (Important, Note, Exam Tip)

**Output example (file):**
```
data/lessons/biology/A.1_water.md
```

**Output example (content):**
```md
---
subject: biology
curriculum_code: A.1
title: Water
generated_at: 2024-01-15T10:23:45.123456
---

# Water

## Overview
Water is the universal solvent...

## Key Concepts
- Polarity and hydrogen bonding
- Thermal properties
- Solvent capabilities

### Hydrogen Bonding
Oxygen's high electronegativity creates...

> **Important:** Hydrogen bonds are crucial for all life.

## Summary
[3-4 sentence recap]
```

---

That's it! The system is ready to go.

Generated: January 2024
Status: 206 lessons queued, ready for generation
Estimated completion: 4-6 hours (all lessons)
