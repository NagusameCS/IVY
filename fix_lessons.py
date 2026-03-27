#!/usr/bin/env python3
"""
Fix lesson structure issues and prepare for regeneration
"""

import os
import json
import re

LESSONS_DIR = "ib-practice-platform/data/lessons"
QUALITY_REPORT = "ib-practice-platform/data/lesson_quality_report.json"

# Lessons that should be regenerated (score < 50)
REGENERATE_THRESHOLDS = {
    "math_aa": 60,      # Regenerate math lessons with score < 60
    "physics": 100,     # Regenerate ALL physics lessons
    "general": 70       # Regenerate others with score < 70
}

def fix_lesson_structure(filepath, content):
    """Fix common structural issues in lessons"""
    original = content
    
    # Fix: Convert "**Overview:**" to "## Overview"
    content = re.sub(
        r'^\*\*Overview:\*\*\s*',
        '## Overview\n\n',
        content,
        flags=re.MULTILINE
    )
    
    # Fix: Fix UTF-8 corruption
    corruptions = {
        'â€™': "'",      # curly apostrophe
        'â€œ': '"',      # left curly quote
        'â€\u009d': '"', # right curly quote
        'Â': '',         # stray byte marker
        'Weâ€™': "We'",
        'donâ€™t': "don't",
        'canâ€™t': "can't",
        'itâ€™s': "it's",
        "I'â€™m": "I'm",
    }
    
    for corrupted, fixed in corruptions.items():
        if corrupted in content:
            content = content.replace(corrupted, fixed)
    
    # Fix: Replace HTML subscripts/superscripts with LaTeX
    content = re.sub(r'<sub>([^<]+)</sub>', r'~\1~', content)
    content = re.sub(r'<sup>([^<]+)</sup>', r'^{\1}', content)
    
    # Fix: Ensure proper spacing after markdown headers
    content = re.sub(r'(^#+)\s*([^\s])', r'\1 \2', content, flags=re.MULTILINE)
    
    return content if content != original else original

def analyze_quality_report():
    """Parse quality report to find lessons to regenerate"""
    with open(QUALITY_REPORT, 'r') as f:
        report = json.load(f)
    
    to_regenerate = {}
    
    for item in report['results']:
        subject = item['subject']
        score = item['score']
        filename = item.get('file_path', '')
        
        # Determine if this lesson should be regenerated
        threshold = REGENERATE_THRESHOLDS.get(subject, REGENERATE_THRESHOLDS['general'])
        
        if score < threshold:
            if subject not in to_regenerate:
                to_regenerate[subject] = []
            
            to_regenerate[subject].append({
                'code': item['curriculum_code'],
                'title': item['lesson_title'],
                'score': score,
                'issues': item.get('issues', []),
                'filename': os.path.basename(filename) if filename else None
            })
    
    return to_regenerate, report

def apply_fixes():
    """Apply structural fixes to all lessons"""
    fixed_count = 0
    
    for subject_dir in os.listdir(LESSONS_DIR):
        subject_path = os.path.join(LESSONS_DIR, subject_dir)
        if not os.path.isdir(subject_path):
            continue
        
        for lesson_file in sorted(os.listdir(subject_path)):
            if not lesson_file.endswith('.md'):
                continue
            
            filepath = os.path.join(subject_path, lesson_file)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                fixed_content = fix_lesson_structure(filepath, content)
                
                if fixed_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    fixed_count += 1
                    print(f"✓ Fixed: {subject_dir}/{lesson_file}")
            
            except Exception as e:
                print(f"✗ Error fixing {filepath}: {e}")
    
    return fixed_count

def main():
    print("Step 1: Analyzing quality report...")
    to_regenerate, report = analyze_quality_report()
    
    print(f"\nLessons to regenerate (below quality threshold):")
    for subject, lessons in sorted(to_regenerate.items()):
        print(f"\n{subject}: {len(lessons)} lessons")
        for lesson in sorted(lessons, key=lambda x: x['score'])[:5]:  # Show worst 5
            print(f"  - {lesson['code']}: {lesson['title']} (score: {lesson['score']})")
        if len(lessons) > 5:
            print(f"  ... and {len(lessons) - 5} more")
    
    print("\n" + "="*60)
    print("Step 2: Applying structural fixes to all lessons...")
    fixed_count = apply_fixes()
    print(f"\n✓ Fixed {fixed_count} lessons")
    
    # Save regeneration queue
    queue_data = {
        'total_to_regenerate': sum(len(v) for v in to_regenerate.values()),
        'by_subject': {k: len(v) for k, v in to_regenerate.items()},
        'lessons_by_subject': to_regenerate
    }
    
    with open('regeneration_queue.json', 'w') as f:
        json.dump(queue_data, f, indent=2)
    
    print("\nRegeneration queue saved to regeneration_queue.json")
    print(f"Total lessons to regenerate: {queue_data['total_to_regenerate']}")

if __name__ == "__main__":
    main()
