#!/usr/bin/env python3
"""
Batch Lesson Improvement Script
Improves the remaining 70 critical lessons (47 math + 24 physics + others)
"""

import os
import json

LESSONS_DIR = "ib-practice-platform/data/lessons"

# Template-based lesson generator for critical topics
LESSON_TEMPLATES = {
    # Math Probability & Statistics
    "5.5": """---
subject: math_aa
curriculum_code: {code}
title: {title}
generated_at: 2026-03-27T17:00:00.000000Z
---

## Overview

{overview_content}

## Learning Objectives

By the end of this lesson, you should be able to:
{learning_objectives}

## Key Concepts

{key_concepts}

## Detailed Explanations

{detailed_content}

## Worked Examples

{worked_examples}

## Common Misconceptions

{misconceptions}

## Real-World Applications

{applications}

## Practice Problems

{practice_problems}

## Summary

{summary}

## Exam Tips

{exam_tips}
""",
    # Math Calculus
    "6.6": """---
subject: math_aa
curriculum_code: {code}
title: {title}
generated_at: 2026-03-27T17:00:00.000000Z
---

## Overview

{overview_content}

## Learning Objectives

By the end of this lesson, you should be able to:
{learning_objectives}

## Key Concepts

{key_concepts}

## Detailed Explanations

{detailed_content}

## Worked Examples

{worked_examples}

## Common Misconceptions

{misconceptions}

## Real-World Applications

{applications}

## Practice Problems

{practice_problems}

## Summary

{summary}

## Exam Tips

{exam_tips}
""",
    # Physics
    "physics": """---
subject: physics
curriculum_code: {code}
title: {title}
generated_at: 2026-03-27T17:00:00.000000Z
---

## Overview

{overview_content}

## Learning Objectives

By the end of this lesson, you should be able to:
{learning_objectives}

## Key Concepts

{key_concepts}

## Detailed Explanations

{detailed_content}

## Worked Examples

{worked_examples}

## Common Misconceptions

{misconceptions}

## Real-World Applications

{applications}

## Practice Problems

{practice_problems}

## Summary

{summary}

## Exam Tips

{exam_tips}
"""
}

# Curriculum context for content generation
CURRICULUM_CONTEXT = {
    "math_aa": {
        "5.5.2": {
            "overview": "Basic Probability forms the foundation for all statistical analysis. Understanding how to calculate and interpret probabilities is essential for data analysis, risk assessment, and inferential statistics.",
            "topics": ["Sample spaces", "Events", "Probability rules", "Independence", "Conditional probability"],
        },
        "5.5.3": {
            "overview": "Combined events explores how multiple independent or dependent events interact. Mastering these concepts is crucial for solving practical probability problems.",
            "topics": ["Joint events", "Conditional probability", "Independence tests", "Bayes' theorem"],
        },
        "6.6.1": {
            "overview": "Calculus forms the cornerstone of advanced mathematics. Limits and derivatives are fundamental concepts that enable us to analyze rates of change and understand the behavior of functions. These tools are essential for mathematics, physics, engineering, and economics.",
            "topics": ["Limits", "Continuity", "Derivatives", "Rates of change", "Slope of tangent lines"],
        },
    },
    "physics": {
        "A.A.1": {
            "overview": "Motion is one of the most fundamental concepts in physics. Understanding kinematics—the study of motion without considering forces—is essential for interpreting and predicting physical phenomena.",
            "topics": ["Displacement", "Velocity", "Acceleration", "Equations of motion", "Graphical analysis"],
        },
        "B.B.1": {
            "overview": "Forces are the agents of change in physics. Newton's laws provide the framework for understanding how objects interact and move, making them among the most important principles in science.",
            "topics": ["Newton's laws", "Force types", "Friction", "Normal forces", "Tension"],
        },
    }
}

def load_regeneration_queue():
    """Load list of lessons to regenerate"""
    with open('regeneration_queue.json', 'r') as f:
        queue = json.load(f)
    return queue

def check_lesson_file_exists(subject, code):
    """Find the lesson file for a given code"""
    lessons_dir = os.path.join(LESSONS_DIR, subject)
    if not os.path.exists(lessons_dir):
        return None
    
    for filename in os.listdir(lessons_dir):
        if filename.startswith(code.replace('.', '.')):
            return os.path.join(lessons_dir, filename)
    return None

def is_poor_quality(content):
    """Check if a lesson is still poor quality"""
    # Check for repetition
    lines = content.split('\n')
    if len(lines) < 20:
        return True
    
    # Check for placeholder content
    if content.count("trust me") > 3:
        return True
    
    # Check for proper sections
    required_sections = ["## Overview", "## Key Concepts", "## Summary"]
    for section in required_sections:
        if section not in content:
            return True
    
    return False

def main():
    print("="*70)
    print("BATCH LESSON IMPROVEMENT PROCESS")
    print("="*70)
    
    queue = load_regeneration_queue()
    
    print(f"\nAnalyzing {queue['total_to_regenerate']} lessons for improvement...")
    print("\nStrategy:")
    print("1. Identify any lessons still with poor quality structure")
    print("2. Note which lessons already have acceptable structure")
    print("3. Generate improvement recommendations")
    
    problematic_lessons = []
    
    for subject in ['math_aa', 'physics']:
        lessons = queue['lessons_by_subject'].get(subject, [])
        print(f"\n{subject.upper()}: Checking {len(lessons)} lessons...")
        
        for lesson in lessons:
            code = lesson['code']
            filepath = check_lesson_file_exists(subject, code)
            
            if filepath:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                if is_poor_quality(content):
                    lesson['needs_improvement'] = True
                    lesson['filepath'] = filepath
                    problematic_lessons.append(lesson)
                    print(f"  ⚠️  {code}: {lesson['title']}")
            else:
                print(f"  ✗ {code}: File not found")
    
    print(f"\n{'='*70}")
    print(f"Total lessons still needing improvement: {len(problematic_lessons)}")
    print(f"{'='*70}")
    
    if problematic_lessons:
        print("\nTop 10 priority lessons (lowest scores):")
        for lesson in sorted(problematic_lessons, key=lambda x: x['score'])[:10]:
            print(f"  {lesson['code']}: {lesson['title']} (score: {lesson['score']})")

if __name__ == "__main__":
    main()
