#!/usr/bin/env python3
"""
Strategic Lesson Improvement - Focus on worst performers
Targets: Probability & Statistics (5.5, 7.7), Calculus (6.6), Physics (all)
"""

LESSONS_TO_IMPROVE = {
    "math_aa": [
        {
            "code": "5.5.3",
            "title": "Combined Events",
            "focus": "Joint probability, independence, contingency"
        },
        {
            "code": "5.5.4",
            "title": "Conditional Probability & Bayes",
            "focus": "Bayes' theorem, conditional independence, updating probabilities"
        },
        {
            "code": "5.5.5",
            "title": "Random Variables & Distributions",
            "focus": "Distribution functions, expected value, variance, probability distributions"
        },
        {
            "code": "6.6.1",
            "title": "Limits & Derivative Basics",
            "focus": "Limits, continuity, definition of derivative, tangent lines"
        },
        {
            "code": "6.6.3",
            "title": "Extrema & Graph Behaviour",
            "focus": "Critical points, local/global maxima/minima, concavity, inflection points"
        },
    ],
    "physics": [
        {
            "code": "A.A.1",
            "title": "Kinematics",
            "focus": "Displacement, velocity, acceleration, equations of motion"
        },
        {
            "code": "B.B.1",
            "title": "Thermal Energy Transfers",
            "focus": "Heat, temperature, thermal equilibrium, specific heat capacity"
        },
        {
            "code": "C.C.1",
            "title": "Simple Harmonic Motion",
            "focus": "Periodic motion, SHM equations, energy in SHM, graphical analysis"
        },
        {
            "code": "E.E.1",
            "title": "Structure of the Atom",
            "focus": "Atomic structure, electron shells, spectra, quantization"
        },
    ]
}

def check_improvements_needed():
    """Check status of key lessons"""
    print("="*70)
    print("CRITICAL LESSON IMPROVEMENT PRIORITY CHECK")
    print("="*70)
    
    improvements = {}
    for subject, lessons in LESSONS_TO_IMPROVE.items():
        print(f"\n{subject.upper()} - {len(lessons)} critical lessons to review:")
        
        improvements[subject] = []
        for lesson in lessons:
            code = lesson['code']
            filepath = f"ib-practice-platform/data/lessons/{subject}/"
            filepath = filepath.replace('math_aa/', 'math_aa/')
            
            # Check if file exists
            search_pattern = code.replace('.', '\\.')
            import subprocess
            try:
                # Find the file
                result = subprocess.run(
                    f'dir "ib-practice-platform\\data\\lessons\\{subject}" /b | find "{code}"',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    filename = result.stdout.strip()
                    full_path = f"ib-practice-platform/data/lessons/{subject}/{filename}"
                    improvements[subject].append({
                        'code': code,
                        'title': lesson['title'],
                        'focus': lesson['focus'],
                        'filepath': full_path,
                        'exists': True
                    })
                    print(f"  ✓ {code}: {lesson['title']}")
                    print(f"    Focus: {lesson['focus']}")
            except:
                pass
    
    return improvements

def main():
    print("\n" + "="*70)
    print("LESSON DEPLOYMENT STATUS")
    print("="*70)
    
    # Check key lessons
    improvements = check_improvements_needed()
    
    total_critical = sum(len(v) for v in improvements.values())
    
    print(f"\n{'='*70}")
    print(f"Summary: {total_critical} critical lessons identified")
    print(f"{'='*70}")
    
    print("\nRECOMMENDED NEXT STEPS:")
    print("1. ✅ COMPLETED: Fixed structural issues (95 lessons)")
    print("2. ✅ COMPLETED: Updated basic probability (5.5.2) with comprehensive content")
    print("3. 🔄 IN PROGRESS: Identify remaining critical lessons")
    print("4. 📋 TODO: Batch regenerate remaining {0} lessons".format(71 - 1))
    print("5. 📋 TODO: Validate curriculum coverage")
    print("6. 📋 TODO: Deploy to production (cPanel + OpenCS)")
    
    print("\nDEPLOYMENT COMMAND (when ready):")
    print("  python deploy.py deploy --target all")
    print("  python deploy.py deploy --target practice")
    
    print("\nQUALITY CHECK COMMAND:")
    print("  python ib-practice-platform/lesson_quality_check.py")

if __name__ == "__main__":
    main()
