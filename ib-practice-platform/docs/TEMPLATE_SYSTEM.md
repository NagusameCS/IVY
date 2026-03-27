# IB Practice Platform — Template System Documentation

## Overview

This platform uses a **template-based question generation system**. Templates define the *structure* of a question (with parameter placeholders), and a local bot fills in those parameters to create randomized instances. Each time a student practices, they get different numbers but the same *type* of problem.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Template JSON   │────>│  Question Bot    │────>│  questions.json  │
│  (schema/specs)  │     │  (your local LLM)│     │  (generated Qs)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                                                         v
                                                  ┌─────────────────┐
                                                  │  index.html      │
                                                  │  (renders & runs)│
                                                  └─────────────────┘
```

## Question JSON Schema

Every question in `questions.json` must conform to this schema:

```json
{
  "questions": [
    {
      "id": "string (unique identifier)",
      "subject": "string (subject key from curriculum.json)",
      "topic": "string (topic number/letter)",
      "subtopic": "string (subtopic code, e.g. '1.1')",
      "type": "string (question type — see below)",
      "difficulty": "core | challenge | extension",
      "tags": ["array", "of", "string", "tags"],
      "title": "Short title for the question",
      "stem": "The question text. Supports KaTeX: \\(inline\\) and \\[display\\]",
      "content": { ... },
      "mark_scheme": "Full worked solution with KaTeX support",
      "hints": ["Optional array of progressive hints"],
      "marks": 4,
      "source": "Optional: exam paper reference"
    }
  ]
}
```

## Question Types

### 1. `mcq` — Multiple Choice Question

The most common type. Student selects one correct answer from 4 options.

```json
{
  "type": "mcq",
  "stem": "An arithmetic sequence has \\(a_1 = 5\\) and \\(d = 3\\). Find \\(a_{10}\\).",
  "content": {
    "options": [
      {"label": "A", "text": "\\(32\\)", "correct": true},
      {"label": "B", "text": "\\(30\\)", "correct": false},
      {"label": "C", "text": "\\(35\\)", "correct": false},
      {"label": "D", "text": "\\(27\\)", "correct": false}
    ],
    "shuffle": true
  }
}
```

**Rendering**: Radio buttons. Options can contain KaTeX math. Set `shuffle: true` to randomize option order (the platform will track which is correct regardless).

**Distractor generation tips**: For arithmetic, use common errors like off-by-one (forgetting -1 in formula), wrong operation, or misplacing the sign.

### 2. `multi_select` — Multiple Correct Answers

Student selects all correct answers from a list.

```json
{
  "type": "multi_select",
  "stem": "Which of the following are properties of a group?",
  "content": {
    "options": [
      {"text": "Closure", "correct": true},
      {"text": "Associativity", "correct": true},
      {"text": "Commutativity", "correct": false},
      {"text": "Identity element exists", "correct": true},
      {"text": "Every element has an inverse", "correct": true}
    ],
    "min_select": 1,
    "max_select": 5
  }
}
```

**Rendering**: Checkboxes. "Check Answer" button reveals which are correct.

### 3. `worked` — Do-By-Hand with Mark Scheme

The student works the problem on paper and reveals the mark scheme to self-assess. No input field.

```json
{
  "type": "worked",
  "stem": "Prove by mathematical induction that \\(\\sum_{r=1}^{n} r = \\frac{n(n+1)}{2}\\) for all \\(n \\in \\mathbb{Z}^+\\).",
  "content": {
    "instruction": "Write your proof on paper, then check against the mark scheme.",
    "parts": [
      {"label": "(a)", "text": "Show the base case \\(n=1\\) holds.", "marks": 2},
      {"label": "(b)", "text": "Assume true for \\(n=k\\) and prove for \\(n=k+1\\).", "marks": 4},
      {"label": "(c)", "text": "Write the conclusion.", "marks": 1}
    ]
  },
  "mark_scheme": "**Base case**: \\(n=1\\): LHS = 1, RHS = 1(2)/2 = 1. True.\n\n**Inductive step**: Assume \\(\\sum_{r=1}^{k} r = \\frac{k(k+1)}{2}\\).\n\nThen \\(\\sum_{r=1}^{k+1} r = \\frac{k(k+1)}{2} + (k+1) = \\frac{(k+1)(k+2)}{2}\\).\n\n**Conclusion**: By PMI, true for all \\(n \\in \\mathbb{Z}^+\\)."
}
```

**Rendering**: Question text with a prominent "Show Mark Scheme" button. Parts listed with mark allocations.

### 4. `numerical` — Numeric Answer

Student enters a number, checked against the correct answer with optional tolerance.

```json
{
  "type": "numerical",
  "stem": "A sector has radius 8 cm and angle 1.2 radians. Find the arc length.",
  "content": {
    "answer": 9.6,
    "tolerance": 0.01,
    "unit": "cm",
    "sf": 3
  }
}
```

**Rendering**: Number input field with unit label. "Check" button compares with tolerance.

### 5. `ordering` — Arrange in Order

Student arranges items in the correct sequence.

```json
{
  "type": "ordering",
  "stem": "Arrange the following steps of mitosis in order:",
  "content": {
    "items": ["Prophase", "Metaphase", "Anaphase", "Telophase"],
    "correct_order": [0, 1, 2, 3]
  }
}
```

**Rendering**: Draggable list items or up/down buttons.

### 6. `matching` — Match Two Columns

Student matches items from column A to column B.

```json
{
  "type": "matching",
  "stem": "Match each functional group with its name:",
  "content": {
    "left": ["-OH", "-COOH", "-NH2", "-CHO"],
    "right": ["Hydroxyl", "Carboxyl", "Amine", "Aldehyde"],
    "correct_pairs": [[0,0], [1,1], [2,2], [3,3]]
  }
}
```

**Rendering**: Two columns with dropdowns or drag-to-match.

### 7. `graph_sketch` — Graph-based MCQ

Student selects which graph/sketch matches the description.

```json
{
  "type": "graph_sketch",
  "stem": "Which graph shows \\(y = 2\\sin(3x)\\) for \\(0 \\leq x \\leq 2\\pi\\)?",
  "content": {
    "options": [
      {"label": "A", "graph": {"type": "function", "expr": "2*sin(3*x)", "xmin": 0, "xmax": 6.28}, "correct": true},
      {"label": "B", "graph": {"type": "function", "expr": "3*sin(2*x)", "xmin": 0, "xmax": 6.28}, "correct": false},
      {"label": "C", "graph": {"type": "function", "expr": "2*cos(3*x)", "xmin": 0, "xmax": 6.28}, "correct": false},
      {"label": "D", "graph": {"type": "function", "expr": "sin(3*x)", "xmin": 0, "xmax": 6.28}, "correct": false}
    ]
  }
}
```

**Rendering**: Uses Chart.js or canvas to render small function plots for each option.

### 8. `chem_structure` — Chemistry Structure Question

For organic chemistry: identify or select a molecular structure.

```json
{
  "type": "chem_structure",
  "stem": "Which structure represents ethanol?",
  "content": {
    "options": [
      {"label": "A", "smiles": "CCO", "correct": true},
      {"label": "B", "smiles": "CC=O", "correct": false},
      {"label": "C", "smiles": "CC(=O)O", "correct": false},
      {"label": "D", "smiles": "CCN", "correct": false}
    ],
    "render_mode": "2d"
  }
}
```

**Rendering**: Converts SMILES to 2D structure drawings using SmilesDrawer library.

### 9. `truth_table` — Logic/CS Truth Table

```json
{
  "type": "truth_table",
  "stem": "Complete the truth table for \\(P \\land (Q \\lor R)\\):",
  "content": {
    "variables": ["P", "Q", "R"],
    "expression": "P AND (Q OR R)",
    "given_columns": ["P", "Q", "R"],
    "solve_columns": ["Q OR R", "P AND (Q OR R)"]
  }
}
```

**Rendering**: Interactive table where some cells are filled, others need student input.

### 10. `calculation` — Multi-step Calculation

```json
{
  "type": "calculation",
  "stem": "A gas occupies 2.5 dm^3 at 300 K and 100 kPa. Find the number of moles.",
  "content": {
    "steps": [
      {"label": "Write the ideal gas law", "content": "\\(PV = nRT\\)"},
      {"label": "Substitute values", "content": "\\(n = \\frac{PV}{RT}\\)"},
      {"label": "Calculate", "answer": 0.1003, "tolerance": 0.001, "unit": "mol"}
    ]
  }
}
```

**Rendering**: Steps revealed progressively. Final answer checked numerically.

## Template Parameters (for Bot Generation)

When creating templates for your bot, define parameters that get randomized:

```json
{
  "template_id": "math_aa_1.1_geometric_sum",
  "params": {
    "a1": {"type": "int", "min": 2, "max": 10},
    "r": {"type": "choice", "values": [0.5, 2, 3, -2]},
    "n": {"type": "int", "min": 4, "max": 12}
  },
  "stem_template": "A geometric series has first term {{a1}} and common ratio {{r}}. Find S_{{n}}.",
  "answer_formula": "a1 * (1 - r^n) / (1 - r)",
  "distractor_formulas": [
    "a1 * (r^n - 1) / (r - 1) + a1",
    "a1 * r^(n-1)",
    "a1 * (1 - r^(n+1)) / (1 - r)"
  ]
}
```

Your bot should:
1. Read the template
2. Sample random parameter values
3. Compute the answer from the formula
4. Generate distractors
5. Format into the standard question JSON
6. Output to `questions.json`

## File Structure

```
ib-practice-platform/
├── index.html              ← Main app (everything in one file)
├── questions.json           ← Generated by your bot (not included)
├── data/
│   ├── curriculum.json      ← Complete IB curriculum structure
│   ├── elements/
│   │   └── periodic-table.json  ← All 118 elements
│   └── templates/           ← Template files for each subject (optional)
│       ├── math_aa.json
│       ├── physics.json
│       └── ...
└── docs/
    ├── TEMPLATE_SYSTEM.md   ← This file
    ├── QUESTION_TYPES.md    ← Detailed type specs
    └── BOT_INSTRUCTIONS.md  ← Instructions for your local bot
```

## Subject-Specific Notes

### Mathematics (AA and AI)
- All math expressions must use KaTeX notation
- Vectors: use `\\begin{pmatrix}...\\end{pmatrix}`
- Complex numbers: use `a + bi` format
- Graph questions: provide function expressions for Chart.js rendering
- Proofs: use `worked` type with parts

### Chemistry
- Use SMILES notation for organic structures
- Electron configurations: use notation like `[Ar] 3d6 4s2`
- Equations: balance with KaTeX `\\ce{}` if available, or plain text
- Enthalpy diagrams: use `graph_sketch` type

### Physics
- Always include units in numerical answers
- Free body diagrams: use `worked` type (student draws)
- Circuit problems: describe circuit verbally or with simple ASCII art
- Use `numerical` type for calculations with tolerance

### Biology
- Focus on `mcq`, `matching`, `ordering`, and `worked` types
- Genetics: use Punnett square descriptions in `worked` type
- Classification: use `matching` and `ordering`

### Economics
- Diagram questions: use `worked` type (student draws curves)
- Calculation questions (elasticity, multiplier): use `numerical`
- Definition/explanation: use `worked` type

### Business Management
- Ratio calculations: use `numerical` type
- Break-even: use `calculation` type with steps
- Theory questions: use `mcq` or `worked`

### Computer Science
- Logic: use `truth_table` type
- Algorithms: use `ordering` type for step sequences
- Pseudocode: use `worked` type
- Binary/hex: use `numerical` type

## Generating Questions

### Quick Start

1. Open `index.html` in a browser
2. If no `questions.json` exists, you'll see demo content
3. Use your local bot to generate questions:

```bash
# Example: generate 50 questions for Math AA Topic 1
python generate.py --subject math_aa --topic 1 --count 50 --output questions.json
```

4. Place `questions.json` in the same folder as `index.html`
5. Refresh the page — questions load automatically

### Bot Prompt Template

Here's a prompt you can give your local LLM:

```
You are a question generator for IB exams. Generate questions in JSON format.

Subject: {subject}
Subtopic: {subtopic}
Difficulty: {difficulty}
Type: {type}

Requirements:
- Use KaTeX notation for all math: \\(inline\\) and \\[display\\]
- Generate plausible distractors for MCQ
- Include full worked mark scheme
- Ensure numerical answers are correct
- Tag with relevant curriculum tags

Output format: {see schema above}
```

## Complete Topic Coverage Checklist

The curriculum.json file contains the complete topic structure. Your bot should generate AT MINIMUM:
- 5 Core questions per subtopic
- 3 Challenge questions per subtopic  
- 2 Extension questions per HL subtopic

This gives approximately:
- Math AA: ~70 subtopics × 10 = 700 questions minimum
- Physics: ~20 subtopics × 10 = 200 questions
- Chemistry: ~20 subtopics × 10 = 200 questions
- Biology: ~16 subtopics × 10 = 160 questions
- Economics: ~20 subtopics × 10 = 200 questions
- Business: ~20 subtopics × 10 = 200 questions
- CS: ~10 subtopics × 10 = 100 questions

**Total minimum: ~1,760 questions**

For thorough coverage, aim for 20+ per subtopic = 3,500+ questions.
