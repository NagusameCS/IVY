"""Generate struct.json for the IVY Study homepage from curriculum.json and lesson files."""
import json, os, re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
LESSONS_DIR = ROOT / "ib-practice-platform" / "data" / "lessons"
CURRICULUM_FILE = ROOT / "ib-practice-platform" / "data" / "curriculum.json"
OUTPUT_FILE = ROOT / "struct.json"

# Map subject directory names to display names and short keys
SUBJECT_DISPLAY = {
    "math_aa": {"name": "Math AA", "tooltip": "Mathematics: Analysis and Approaches"},
    "physics": {"name": "Physics", "tooltip": "IB Physics"},
    "chemistry": {"name": "Chemistry", "tooltip": "IB Chemistry"},
    "biology": {"name": "Biology", "tooltip": "IB Biology"},
    "economics": {"name": "Economics", "tooltip": "IB Economics"},
    "business": {"name": "Business", "tooltip": "IB Business Management"},
    "computer_science": {"name": "Computer Science", "tooltip": "IB Computer Science"},
}

def parse_frontmatter(filepath):
    """Extract YAML frontmatter from a lesson markdown file."""
    text = filepath.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip()
    return fm

def estimate_read_time(filepath):
    """Estimate reading time in minutes based on word count."""
    text = filepath.read_text(encoding="utf-8", errors="replace")
    # Strip frontmatter
    text = re.sub(r"^---.*?---", "", text, count=1, flags=re.DOTALL)
    words = len(text.split())
    minutes = max(5, round(words / 200))  # ~200 wpm reading speed, minimum 5 min
    return minutes

def main():
    curriculum = json.loads(CURRICULUM_FILE.read_text(encoding="utf-8"))
    subjects_data = curriculum["subjects"]
    
    result = []
    
    for subj_dir, display_info in SUBJECT_DISPLAY.items():
        subj_path = LESSONS_DIR / subj_dir
        if not subj_path.exists():
            print(f"  Skipping {subj_dir}: no lesson directory")
            continue
        
        lesson_files = sorted(subj_path.glob("*.md"))
        if not lesson_files:
            print(f"  Skipping {subj_dir}: no lesson files")
            continue
        
        # Get curriculum data for this subject
        curriculum_subj = subjects_data.get(subj_dir, {})
        topics_data = curriculum_subj.get("topics", {})
        
        # Build a lookup: subtopic_code -> {name, level, tags, topic_name}
        subtopic_lookup = {}
        topic_name_lookup = {}  # topic_key -> topic_name
        for topic_key, topic_info in topics_data.items():
            topic_name = topic_info["name"]
            topic_name_lookup[topic_key] = topic_name
            for st_key, st_info in topic_info.get("subtopics", {}).items():
                subtopic_lookup[st_key] = {
                    "name": st_info["name"],
                    "level": st_info.get("level", "SL/HL"),
                    "tags": st_info.get("tags", []),
                    "topic_name": topic_name,
                    "topic_key": topic_key,
                }
        
        # Group lessons by topic/section
        sections = {}  # topic_key -> {title, path, lessons[]}
        
        for lf in lesson_files:
            fm = parse_frontmatter(lf)
            curriculum_code = fm.get("curriculum_code", "")
            title = fm.get("title", lf.stem.replace("_", " ").title())
            generated_at = fm.get("generated_at", "2026-03-27T00:00:00")
            
            # Determine which topic this belongs to
            # Curriculum code pattern: {topic}.{topic_repeated}.{subtopic_num}
            # e.g. "1.1.2" -> topic "1", subtopic key "1.2"
            #      "A.A.3" -> topic "A", subtopic key "A.3"
            #      "R1.R1.2" -> topic "R1", subtopic key "R1.2"
            matched_subtopic = None
            matched_topic_key = None
            
            parts = curriculum_code.split(".")
            
            if len(parts) >= 3:
                # Standard format: first part is topic, last part is subtopic num
                topic_key = parts[0]
                subtopic_key = f"{parts[0]}.{parts[-1]}"
                if subtopic_key in subtopic_lookup:
                    matched_subtopic = subtopic_lookup[subtopic_key]
                    matched_topic_key = matched_subtopic["topic_key"]
                elif topic_key in topic_name_lookup:
                    matched_topic_key = topic_key
            elif len(parts) == 2:
                # Try as subtopic key directly
                if curriculum_code in subtopic_lookup:
                    matched_subtopic = subtopic_lookup[curriculum_code]
                    matched_topic_key = matched_subtopic["topic_key"]
                elif parts[0] in topic_name_lookup:
                    matched_topic_key = parts[0]
            elif len(parts) == 1 and parts[0] in topic_name_lookup:
                matched_topic_key = parts[0]
            
            # Build section key and info
            if matched_topic_key:
                section_title = topic_name_lookup.get(matched_topic_key, f"Topic {matched_topic_key}")
                section_path = matched_topic_key
            else:
                # Fallback: use first part of curriculum code
                section_path = parts[0] if parts else "misc"
                section_title = f"Topic {section_path}"
            
            if section_path not in sections:
                sections[section_path] = {
                    "title": section_title,
                    "path": section_path,
                    "lessons": []
                }
            
            # Get metadata from curriculum or generate defaults
            level = "SL/HL"
            tags = []
            topic_name = sections[section_path]["title"]
            subsection = None
            
            if matched_subtopic:
                level = matched_subtopic.get("level", "SL/HL")
                tags = matched_subtopic.get("tags", [])
                topic_name = matched_subtopic.get("topic_name", topic_name)
                subsection = matched_subtopic.get("name", None)
            
            time_est = estimate_read_time(lf)
            
            lesson_entry = {
                "file": lf.name,
                "title": title,
                "topic": topic_name,
                "level": level,
                "tags": tags,
                "time_estimate": time_est,
                "timestamp": generated_at,
            }
            if subsection:
                lesson_entry["subsection"] = subsection
            
            sections[section_path]["lessons"].append(lesson_entry)
        
        # Sort sections by their key
        sorted_sections = sorted(sections.values(), key=lambda s: s["path"])
        
        subject_entry = {
            "subject": display_info["name"],
            "tooltip": display_info["tooltip"],
            "basePath": f"ib-practice-platform/data/lessons/{subj_dir}",
            "sections": sorted_sections,
        }
        
        total_lessons = sum(len(s["lessons"]) for s in sorted_sections)
        print(f"  {display_info['name']}: {total_lessons} lessons in {len(sorted_sections)} sections")
        result.append(subject_entry)
    
    OUTPUT_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGenerated {OUTPUT_FILE} with {len(result)} subjects, {sum(sum(len(s['lessons']) for s in subj['sections']) for subj in result)} total lessons")

if __name__ == "__main__":
    main()
