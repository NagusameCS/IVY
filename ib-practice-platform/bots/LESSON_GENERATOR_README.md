# IvyStudy Lesson Generator

Automated lesson generation system using Ollama + LLM (locally on your machine).

## Quick Start

### 1. Install Ollama
Download and install from https://ollama.ai (it runs a local API server)

### 2. Pull the Model
```bash
ollama pull mistral
```
(This downloads the Mistral 7B model - fast and good for educational content. ~4GB)

### 3. Start Ollama
```bash
ollama serve
```
Keep this running in the background. It listens on `http://localhost:11434`

### 4. Queue Lessons
```bash
cd ib-practice-platform\bots
python lesson_generator.py --queue
```

This reads all `plan_*.json` files and queues them for generation.

### 5. Generate Lessons
```bash
python lesson_generator.py --generate 5
```
This generates 5 pending lessons. Use `--all` to generate everything.

### 6. Check Status
```bash
python lesson_generator.py --status
```

## Commands

| Command | Effect |
|---------|--------|
| `--queue` | Queue all lessons from plan files |
| `--queue --subject biology` | Queue only biology lessons |
| `--generate N` | Generate N pending lessons (default: 5) |
| `--generate --subject math_aa` | Generate 5 math_aa lessons |
| `--all` | Generate ALL pending lessons |
| `--status` | Show current generation status |
| No args | Show status (same as `--status`) |

## System Architecture

### Files Created

1. **lesson_generator.py** (450+ lines)
   - Main script for queuing and generating lessons
   - Uses Ollama HTTP API at `http://localhost:11434/api/generate`
   - Stores metadata in SQLite: `bots/queue.db`
   - Saves lessons as markdown: `data/lessons/{subject}/{code}_{title}.md`

2. **start_lesson_generator.bat**
   - Simple batch file to run commands from Windows

### Database Schema

Lessons stored in `queue.db` with fields:
- `id`: Auto-increment primary key
- `subject`: Subject name (biology, math_aa, etc.)
- `curriculum_code`: IB code (e.g., "A.1", "B.2.3")
- `lesson_title`: Human-readable title
- `topic_name`: Topic context
- `status`: pending | completed | failed
- `content`: First 5000 chars of generated markdown
- `error_message`: Error details if failed
- `retry_count`: Number of generation attempts
- `created_at`: When queued
- `generated_at`: When completed

Indexes on: `status`, `subject`

### Generation Process

1. **Check Ollama**: Verify server is running and model is available
2. **Queue**: Read `plan_*.json` files, insert into `lessons` table (pending)
3. **Generate**: For each pending lesson:
   - Build prompt with curriculum context
   - Call Ollama API with system prompt (contains markdown rules)
   - Receive generated markdown
   - Validate length (>200 chars)
   - Save to file with YAML frontmatter
   - Update database status to "completed"
4. **Handle Failures**: Retry up to 3 times, then mark as failed

### Output Structure

Lessons saved to `data/lessons/{subject}/{code}_{title}.md`:

```
data/
├── lessons/
│   ├── biology/
│   │   ├── A.1_water.md
│   │   ├── A.2_nucleic_acids.md
│   │   └── ...
│   ├── math_aa/
│   │   ├── A.1.1_complex_numbers.md
│   │   └── ...
│   └── ...
```

Each file starts with YAML frontmatter:
```yaml
---
subject: biology
curriculum_code: A.1
title: Water
generated_at: 2024-01-15T10:23:45.123456
---

[Markdown lesson content here...]
```

## Markdown Syntax Rules

### Structure
- **Overview**: 1-2 sentence intro
- **Key Concepts**: ## heading with main points
- **Sections**: ### subheadings for detailed content
- **Summary**: ## Summary with 3-4 sentence recap

### Formatting
- **Bold terms**: `**term**`
- *Italic emphasis*: `*emphasis*`
- Code: ` ```formula``` ` or ` ```python``` `
- Math: `$inline$` or `$$display$$`
- Lists: `- bullet` or `1. numbered`

### Callout Boxes
Using blockquotes:
```markdown
> **Important:** key concept
> **Note:** additional info
> **Example:** worked example
> **Exam Tip:** exam reference
```

### Examples
- Include 2-3 worked examples per lesson
- Use actual IB problem formats
- Show step-by-step solutions

### Length Guidelines
- 1500-2500 words total
- 5-7 main concept sections
- 2-3 worked examples

## Configuration

Edit `lesson_generator.py` top section to customize:

```python
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"  # Change to: llama2, neural-chat, dolphin-mixtral, etc.
TIMEOUT = 300  # 5 minutes per lesson
MAX_RETRIES = 3
```

## Alternative Models

Other good models for educational content:

| Model | Size | Good For | Install |
|-------|------|----------|---------|
| mistral | 7B | **Fast, balanced** | `ollama pull mistral` |
| llama2 | 7B-70B | **Accurate** | `ollama pull llama2` |
| neural-chat | 7B | **Conversational** | `ollama pull neural-chat` |
| dolphin-mixtral | 46B | **Most capable** | `ollama pull dolphin-mixtral` |

(Larger models = slower but higher quality. Sizes shown are base; RAM needed is 2-3x size)

## Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check it's listening: `curl http://localhost:11434/api/tags`

### "Model not found"
- Pull the model: `ollama pull mistral`
- Or change model in lesson_generator.py

### "Generation timeout"
- Lesson took >300 seconds
- Either: increase `TIMEOUT` value, or use faster model (mistral instead of llama2)

### "Content too short"
- LLM generated <200 chars (too weak prompt/model)
- Try: different model, or adjust validation in code (line ~250)

### Database locked
- Close other processes using `queue.db`
- Or delete `.db-wal` and `.db-shm` files (they're temporary)

## Performance Tips

1. **Generate in batches**: `--generate 5` then check results, rather than `--all` at once
2. **Monitor Ollama**: Watch RAM usage if getting slower
3. **Faster generation**: Use mistral instead of llama2 or dolphin-mixtral
4. **Quality vs Speed**: Increase `TIMEOUT` and use larger model if quality issues

## Integration with IvyStudy

Once lessons are generated in `data/lessons/`, you can:

1. **Index for search**: Update practice platform search index
2. **Link from practice**: Add lesson links to related practice problems
3. **Publish to main site**: Deploy markdown lessons to public_html
4. **Create lesson pages**: Add Tailwind-styled lesson viewer to site

## Database Queries

Check status of specific subject:
```sql
SELECT COUNT(*), status FROM lessons 
WHERE subject='biology' 
GROUP BY status;
```

Find failed lessons:
```sql
SELECT curriculum_code, lesson_title, error_message 
FROM lessons 
WHERE status='failed';
```

## Advanced Usage

### Generate one subject at a time
```bash
python lesson_generator.py --queue --subject biology
python lesson_generator.py --generate --subject biology --all
```

### Check what would be generated
```bash
python lesson_generator.py --status
```

### Restart failed lessons
```sql
UPDATE lessons SET status='pending', retry_count=0 WHERE status='failed';
```
Then run: `python lesson_generator.py --all`

### Export lessons as JSON
After generation, create a simple script to read `data/lessons/` and convert to JSON for API.

---

**Started**: Q1 2024  
**Status**: Active generation  
**Lessons**: Dynamically generated via Ollama  
**Format**: Markdown with custom IB syntax  
**Storage**: `data/lessons/{subject}/` + SQLite metadata
