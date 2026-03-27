#!/usr/bin/env python3
"""
Comprehensive Lesson Improvement Tool

Analyzes all lessons for:
1. Markdown syntax errors
2. Encoding issues
3. Missing sections
4. Curriculum gaps
5. Content completeness
"""

import os
import json
import re
from collections import defaultdict

LESSONS_DIR = "ib-practice-platform/data/lessons"
QUALITY_REPORT = "ib-practice-platform/data/lesson_quality_report.json"

# Expected sections for a complete lesson
REQUIRED_SECTIONS = {
    "overview": r"##\s+Overview|^(Overview|OVERVIEW)",
    "key_concepts": r"##\s+Key Concepts",
    "examples": r"##\s+Examples?|##\s+Worked Examples?",
    "summary": r"##\s+Summary|##\s+Key Takeaways",
    "exam_tip": r"##\s+Exam Tip|##\s+IB Exam Tips?",
    "practice": r"##\s+Practice|##\s+Practice Problems?",
}

class LessonAnalyzer:
    def __init__(self):
        self.issues = defaultdict(list)
        self.encoding_errors = []
        self.missing_sections = defaultdict(list)
        self.syntax_errors = []
        self.low_quality = []
        
    def check_encoding(self, filepath):
        """Check for UTF-8 encoding issues"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for encoding corruption signs
            corrupted_patterns = [
                (r'â€™', "'"),  # curly quote issues
                (r'â€œ', '"'),
                (r'â€\u009d', '"'),
                (r'Â', ''),  # stray byte markers
            ]
            
            has_corruption = False
            for pattern, replacement in corrupted_patterns:
                if pattern in content:
                    has_corruption = True
                    break
            
            return content, has_corruption
        except UnicodeDecodeError as e:
            self.encoding_errors.append(f"{filepath}: {str(e)}")
            return None, True
    
    def check_markdown_syntax(self, filepath, content):
        """Check for markdown syntax errors"""
        errors = []
        
        # Check for unclosed code blocks
        backtick_count = content.count('```')
        if backtick_count % 2 != 0:
            errors.append("Unclosed code block (odd number of ```)")
        
        # Check for unmatched brackets
        bracket_pairs = [
            (r'\[', r'\]'),
            (r'\{', r'\}'),
            (r'\(', r'\)'),
        ]
        
        for open_br, close_br in bracket_pairs:
            open_count = len(re.findall(open_br, content))
            close_count = len(re.findall(close_br, content))
            if open_count != close_count:
                errors.append(f"Unmatched brackets: {open_count} {open_br} vs {close_count} {close_br}")
        
        # Check for improper LaTeX
        math_blocks = re.findall(r'\$[^$]+\$', content)
        for block in math_blocks:
            if block.count('{') != block.count('}'):
                errors.append(f"Unmatched braces in LaTeX: {block[:50]}")
        
        return errors
    
    def check_sections(self, filepath, content, subject):
        """Check for required sections"""
        missing = []
        
        # All lessons should have overview and key concepts
        required_for_all = ["overview", "key_concepts"]
        
        for section in required_for_all:
            pattern = REQUIRED_SECTIONS[section]
            if not re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                missing.append(section)
        
        return missing
    
    def check_word_count(self, content):
        """Check if content is substantial enough"""
        # Remove frontmatter
        content = re.sub(r'^---.*?^---', '', content, flags=re.MULTILINE | re.DOTALL)
        # Remove markdown symbols
        words = len(re.findall(r'\b\w+\b', content))
        return words
    
    def check_curriculum_coverage(self):
        """Verify curriculum code coverage"""
        # Load curriculum from struct.json
        struct_file = "ib-practice-platform/data/struct.json"
        if not os.path.exists(struct_file):
            return None
        
        try:
            with open(struct_file, 'r') as f:
                struct = json.load(f)
            return struct
        except:
            return None
    
    def analyze_all_lessons(self):
        """Analyze all lessons in the directory"""
        results = {}
        
        for subject_dir in os.listdir(LESSONS_DIR):
            subject_path = os.path.join(LESSONS_DIR, subject_dir)
            if not os.path.isdir(subject_path):
                continue
            
            results[subject_dir] = []
            
            for lesson_file in sorted(os.listdir(subject_path)):
                if not lesson_file.endswith('.md'):
                    continue
                
                filepath = os.path.join(subject_path, lesson_file)
                content, has_corruption = self.check_encoding(filepath)
                
                if content is None:
                    continue
                
                lesson_info = {
                    "file": lesson_file,
                    "path": filepath,
                    "issues": [],
                    "word_count": 0,
                }
                
                # Check encoding
                if has_corruption:
                    lesson_info["issues"].append("ENCODING_CORRUPTION")
                
                # Check syntax
                syntax_errors = self.check_markdown_syntax(filepath, content)
                if syntax_errors:
                    lesson_info["issues"].extend(syntax_errors)
                
                # Check sections
                missing_sections = self.check_sections(filepath, content, subject_dir)
                if missing_sections:
                    lesson_info["issues"].append(f"MISSING_SECTIONS: {','.join(missing_sections)}")
                
                # Check word count
                word_count = self.check_word_count(content)
                lesson_info["word_count"] = word_count
                if word_count < 500:
                    lesson_info["issues"].append(f"LOW_WORD_COUNT: {word_count} (< 500)")
                
                results[subject_dir].append(lesson_info)
        
        return results
    
    def print_summary(self, results):
        """Print analysis summary"""
        print("\n" + "="*80)
        print("LESSON ANALYSIS SUMMARY")
        print("="*80)
        
        total_lessons = 0
        total_issues = 0
        encoding_issues = 0
        low_word_count = 0
        missing_sections = 0
        syntax_errors = 0
        
        for subject, lessons in sorted(results.items()):
            print(f"\n{subject.upper()} ({len(lessons)} lessons)")
            print("-" * 60)
            
            subject_issues = 0
            for lesson in lessons:
                total_lessons += 1
                if lesson["issues"]:
                    subject_issues += 1
                    total_issues += 1
                    
                    # Count issue types
                    for issue in lesson["issues"]:
                        if "ENCODING" in issue:
                            encoding_issues += 1
                        elif "WORD_COUNT" in issue:
                            low_word_count += 1
                        elif "MISSING_SECTIONS" in issue:
                            missing_sections += 1
                        elif "Unclosed" in issue or "Unmatched" in issue:
                            syntax_errors += 1
                    
                    print(f"  ⚠️  {lesson['file']} ({lesson['word_count']} words)")
                    for issue in lesson["issues"]:
                        print(f"       └─ {issue}")
            
            if subject_issues == 0:
                print(f"  ✅ All {len(lessons)} lessons OK")
        
        print("\n" + "="*80)
        print("STATISTICS")
        print("="*80)
        print(f"Total lessons analyzed: {total_lessons}")
        print(f"Lessons with issues: {total_issues}")
        print(f"Encoding corruption issues: {encoding_issues}")
        print(f"Low word count issues: {low_word_count}")
        print(f"Missing sections: {missing_sections}")
        print(f"Syntax errors: {syntax_errors}")
        
        print("\nIssues by subject:")
        for subject, lessons in sorted(results.items()):
            issue_count = sum(1 for l in lessons if l["issues"])
            print(f"  {subject}: {issue_count}/{len(lessons)}")

def main():
    analyzer = LessonAnalyzer()
    results = analyzer.analyze_all_lessons()
    analyzer.print_summary(results)
    
    # Save detailed results
    with open("lesson_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nDetailed results saved to lesson_analysis_results.json")

if __name__ == "__main__":
    main()
