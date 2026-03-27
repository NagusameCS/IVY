#!/usr/bin/env python3
"""
Improved Lesson Generator for High-Quality IB Study Guides

Generates comprehensive, structured lessons with:
- Complete curriculum coverage
- Multiple worked examples
- Exam tips and practice
- Proper mathematical notation
- Visual descriptions for diagrams
"""

import os
import json
import subprocess
import sys
import re
from datetime import datetime

SUBJECTS_MAPPING = {
    'math_aa': 'IB Mathematics: Analysis and Approaches (AA)',
    'physics': 'IB Physics',
}

# Improved prompt templates for better quality
LESSON_PROMPT_TEMPLATE = """You are creating a comprehensive IB {subject} study guide for {grade_level} students.

TOPIC: {curriculum_code} - {topic_title}

Create a detailed, well-structured lesson guide for this topic. The guide MUST include ALL of the following sections:

## Structure (MUST INCLUDE ALL):
1. ## Overview - Clear description of the topic and its importance in IB {subject}
2. ## Learning Objectives - What students should be able to do after this lesson
3. ## Key Concepts - Bulleted list of main ideas (at least 5 key concepts)
4. ## Detailed Explanations - In-depth coverage of each concept with theory
5. ## Worked Examples - At least 3 worked examples with step-by-step solutions
6. ## Common Misconceptions - Address 3-4 common mistakes students make
7. ## Real-World Applications - Show how this topic applies outside the classroom
8. ## Practice Problems - 5-10 practice questions for students to attempt
9. ## Summary - Key takeaways and connections
10. ## Exam Tips - Specific IB exam strategy for this topic

## Quality Requirements:
- Use proper mathematical notation ($$notation$$ for inline, $$
notation$$ for blocks)
- Include descriptive text about diagrams/visuals (describe as "[DIAGRAM: description]")
- Write in clear, precise language appropriate for IB students
- Ensure all content is accurate and comprehensive
- Use bullet points for lists
- Bold key terminology
- Include references to IB exam patterns when relevant

## Topic-Specific Context:
{context}

## Important: 
- Minimum 2000 words for comprehensive coverage
- All formulas should use proper LaTeX notation
- Ensure consistent mathematical rigor
- Make connections to other IB topics when relevant

Generate the complete study guide now:"""

def load_regeneration_queue():
    """Load list of lessons to regenerate"""
    with open('regeneration_queue.json', 'r') as f:
        queue = json.load(f)
    return queue

def load_curriculum_info():
    """Load curriculum structure to understand context"""
    structures = {}
    for subject in SUBJECTS_MAPPING.keys():
        struct_file = f"ib-practice-platform/data/struct_{subject}.json"
        if os.path.exists(struct_file):
            try:
                with open(struct_file, 'r') as f:
                    structures[subject] = json.load(f)
            except:
                pass
    return structures

def get_curriculum_context(subject, curriculum_code, topic_title):
    """Build context information for the lesson"""
    contexts = {
        'math_aa': {
            'prob_dist': 'This is part of probability and statistics. Cover definitions, parameters, and applications.',
            'calculus': 'This covers differential and integral calculus. Include both theoretical foundations and practical applications.',
            'vectors': 'Cover vector algebra, operations, and 3D geometry with detailed examples.',
            'probability': 'Cover foundational probability concepts with clear definitions and examples.',
            'statistics': 'Cover statistical methods, hypothesis testing, and inference.',
            'series': 'Cover arithmetic and geometric series, limits, and convergence.',
            'functions': 'Cover various function families, transformations, and applications.',
            'logic': 'Cover set theory, logic, and proof methods.',
        },
        'physics': {
            'thermal': 'Cover thermal energy transfer, heat capacity, and thermodynamics.',
            'mechanics': 'Cover forces, motion, energy, power, and rotational mechanics.',
            'waves': 'Cover wave properties, interference, diffraction, and sound.',
            'electricity': 'Cover electric fields, circuits, magnetism, and electromagnetic induction.',
            'nuclear': 'Cover atomic structure, radioactivity, and nuclear reactions.',
            'quantum': 'Cover photon energies, the photoelectric effect, and quantum phenomena.',
        }
    }
    
    # Map to appropriate context
    context_keys = contexts.get(subject, {})
    for key, context_text in context_keys.items():
        if key.lower() in str(topic_title).lower():
            return context_text
    
    return f"This is a comprehensive topic in IB {SUBJECTS_MAPPING.get(subject, subject)}. Provide thorough, detailed coverage appropriate for the IB curriculum."

def generate_lesson(subject, curriculum_code, topic_title):
    """Generate a lesson using improved prompt"""
    
    # Determine grade level
    grade_level = "SL/HL"
    if subject == 'math_aa':
        grade_level = "HL"
    
    context = get_curriculum_context(subject, curriculum_code, topic_title)
    
    prompt = LESSON_PROMPT_TEMPLATE.format(
        subject=SUBJECTS_MAPPING.get(subject, subject),
        grade_level=grade_level,
        curriculum_code=curriculum_code,
        topic_title=topic_title,
        context=context
    )
    
    try:
        # Try to use ollama with improved model
        result = subprocess.run(
            ['ollama', 'run', 'smollm2:135m', '--verbose'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except Exception as e:
        print(f"Error calling ollama: {e}", file=sys.stderr)
        return None

def format_lesson(subject, curriculum_code, topic_title, content):
    """Format lesson with frontmatter and structure"""
    
    lesson = f"""---
subject: {subject}
curriculum_code: {curriculum_code}
title: {topic_title}
generated_at: {datetime.utcnow().isoformat()}Z
grade_level: {'HL' if subject == 'math_aa' else 'SL/HL'}
---

{content}
"""
    return lesson

def save_lesson(subject, curriculum_code, topic_title, content):
    """Save lesson to file"""
    # Create filename from curriculum code and title
    safe_title = re.sub(r'[^\w\s&]', '_', topic_title.lower())
    safe_title = re.sub(r'\s+', '_', safe_title.strip()).rstrip('_')
    filename = f"{curriculum_code}_{safe_title}.md"
    
    # Ensure directory exists
    lessons_dir = f"ib-practice-platform/data/lessons/{subject}"
    os.makedirs(lessons_dir, exist_ok=True)
    
    filepath = os.path.join(lessons_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def main():
    print("="*70)
    print("IB LESSON REGENERATION ENGINE")
    print("="*70)
    
    queue = load_regeneration_queue()
    print(f"\nTotal lessons to regenerate: {queue['total_to_regenerate']}")
    print(f"By subject: {queue['by_subject']}")
    
    # Process each subject
    total_generated = 0
    failed = []
    
    for subject in ['math_aa', 'physics']:
        lessons = queue['lessons_by_subject'].get(subject, [])
        if not lessons:
            continue
        
        print(f"\n{'='*70}")
        print(f"{subject.upper()}: Generating {len(lessons)} lessons")
        print(f"{'='*70}")
        
        for i, lesson_info in enumerate(sorted(lessons, key=lambda x: x['score']), 1):
            
            code = lesson_info['code']
            title = lesson_info['title']
            score = lesson_info['score']
            
            print(f"\n[{i}/{len(lessons)}] {code}: {title} (current score: {score})")
            print(f"  Issues: {', '.join(lesson_info['issues'][:3])}")
            
            # Generate lesson
            print(f"  Generating...", end='', flush=True)
            content = generate_lesson(subject, code, title)
            
            if not content:
                print(" FAILED")
                failed.append(f"{subject}/{code}")
                continue
            
            # Format and save
            formatted = format_lesson(subject, code, title, content)
            filepath = save_lesson(subject, code, title, formatted)
            
            print(f" OK ({len(content)} chars)")
            print(f"  Saved: {filepath}")
            
            total_generated += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Successfully generated: {total_generated}/{queue['total_to_regenerate']}")
    if failed:
        print(f"Failed: {len(failed)}")
        for f in failed[:5]:
            print(f"  - {f}")
        if len(failed) > 5:
            print(f"  ... and {len(failed)-5} more")
    
    print(f"\nNext steps:")
    print(f"1. Run quality check: python ib-practice-platform/lesson_quality_check.py")
    print(f"2. Review regenerated lessons for accuracy")
    print(f"3. Deploy to cPanel: python deploy.py deploy --target practice")

if __name__ == "__main__":
    main()
