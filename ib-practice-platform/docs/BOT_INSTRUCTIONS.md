# Bot Instructions — Generating Questions for IB Practice Platform

## Goal

You are generating a `questions.json` file that the IB Practice Platform (`index.html`) will load and render. The platform handles all UI, navigation, scoring, and rendering — you just need to produce well-formed question data.

## Output Format

Your output must be a single JSON file:

```json
{
  "version": "1.0",
  "generated_at": "2026-03-26T00:00:00Z",
  "generator": "your-bot-name",
  "question_count": 100,
  "questions": [ ... ]
}
```

## Question Object Schema

Every question MUST have these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | YES | Unique ID. Format: `{subject}_{subtopic}_{type}_{n}` e.g. `math_aa_1.1_mcq_001` |
| `subject` | string | YES | Must match a key in curriculum.json: `math_aa`, `math_ai`, `physics`, `chemistry`, `biology`, `economics`, `business`, `computer_science` |
| `topic` | string | YES | Topic code: `"1"`, `"A"`, `"S1"`, etc. |
| `subtopic` | string | YES | Subtopic code: `"1.1"`, `"A.1"`, `"S1.1"`, etc. |
| `type` | string | YES | One of: `mcq`, `multi_select`, `worked`, `numerical`, `ordering`, `matching`, `graph_sketch`, `chem_structure`, `truth_table`, `calculation` |
| `difficulty` | string | YES | One of: `core`, `challenge`, `extension` |
| `tags` | string[] | YES | Array of topic tags for filtering |
| `title` | string | YES | Short descriptive title |
| `stem` | string | YES | Question text. KaTeX supported: `\\(inline\\)` and `\\[display\\]` |
| `content` | object | YES | Type-specific content (see below) |
| `mark_scheme` | string | YES | Full worked solution. KaTeX supported. |
| `hints` | string[] | NO | Progressive hints |
| `marks` | number | NO | Total marks for the question |
| `time_estimate` | number | NO | Estimated minutes to solve |

## Content Objects by Type

### mcq
```json
{
  "options": [
    {"label": "A", "text": "\\(32\\)", "correct": true},
    {"label": "B", "text": "\\(30\\)", "correct": false},
    {"label": "C", "text": "\\(35\\)", "correct": false},
    {"label": "D", "text": "\\(27\\)", "correct": false}
  ],
  "shuffle": true
}
```
- Exactly ONE option must have `"correct": true`
- Labels should be A, B, C, D
- `shuffle: true` means the platform may reorder options

### multi_select
```json
{
  "options": [
    {"text": "Option 1", "correct": true},
    {"text": "Option 2", "correct": false},
    {"text": "Option 3", "correct": true}
  ]
}
```
- Multiple options can be correct

### worked
```json
{
  "instruction": "Work this problem by hand, then check the mark scheme.",
  "parts": [
    {"label": "(a)", "text": "Find the first derivative.", "marks": 3},
    {"label": "(b)", "text": "Find the stationary points.", "marks": 4}
  ]
}
```
- `parts` is optional. If absent, the question is a single part.
- `instruction` is optional. Default: "Solve by hand and check your answer."

### numerical
```json
{
  "answer": 9.6,
  "tolerance": 0.01,
  "unit": "cm",
  "sf": 3
}
```
- `tolerance`: absolute tolerance for comparison. Default: 0.01
- `unit`: display unit. Optional.
- `sf`: significant figures expected. Optional.

### ordering
```json
{
  "items": ["Prophase", "Metaphase", "Anaphase", "Telophase"],
  "correct_order": [0, 1, 2, 3]
}
```
- `items`: array of strings (displayed shuffled)
- `correct_order`: indices into items array giving the correct sequence

### matching
```json
{
  "left": ["-OH", "-COOH", "-NH2", "-CHO"],
  "right": ["Hydroxyl", "Carboxyl", "Amine", "Aldehyde"],
  "correct_pairs": [[0,0], [1,1], [2,2], [3,3]]
}
```
- `correct_pairs`: array of [left_index, right_index] pairs

### graph_sketch
```json
{
  "options": [
    {"label": "A", "graph": {"type": "function", "expr": "2*Math.sin(3*x)", "xmin": 0, "xmax": 6.28, "ymin": -3, "ymax": 3}, "correct": true},
    {"label": "B", "graph": {"type": "function", "expr": "3*Math.sin(2*x)", "xmin": 0, "xmax": 6.28, "ymin": -4, "ymax": 4}, "correct": false}
  ]
}
```
- `expr`: JavaScript math expression. Use `Math.sin`, `Math.cos`, `Math.exp`, etc.
- The platform renders each as a small canvas plot

### chem_structure
```json
{
  "options": [
    {"label": "A", "smiles": "CCO", "name": "Ethanol", "correct": true},
    {"label": "B", "smiles": "CC=O", "name": "Acetaldehyde", "correct": false}
  ],
  "render_mode": "2d"
}
```
- `smiles`: SMILES notation for the molecule
- Platform uses SmilesDrawer to render 2D structures

### truth_table
```json
{
  "variables": ["P", "Q"],
  "expression_label": "P \\land Q",
  "rows": [
    {"inputs": [true, true], "output": true},
    {"inputs": [true, false], "output": false},
    {"inputs": [false, true], "output": false},
    {"inputs": [false, false], "output": false}
  ],
  "hidden_rows": [1, 3]
}
```
- `hidden_rows`: indices of rows where student must fill in the output

### calculation
```json
{
  "steps": [
    {"label": "Step 1", "content": "Write the formula: \\(PV = nRT\\)", "type": "info"},
    {"label": "Step 2", "content": "Rearrange for n", "type": "info"},
    {"label": "Step 3", "content": "Calculate n", "answer": 0.1003, "tolerance": 0.001, "unit": "mol", "type": "input"}
  ]
}
```
- Steps with `"type": "info"` are displayed
- Steps with `"type": "input"` have a number field

## KaTeX Math Notation Guide

The platform renders math using KaTeX. Use these delimiters:

- Inline math: `\\(x^2 + 1\\)`
- Display math: `\\[\\int_0^1 x^2 \\, dx = \\frac{1}{3}\\]`

Common patterns:
- Fractions: `\\frac{a}{b}`
- Subscripts: `a_1`, `a_{10}`
- Superscripts: `x^2`, `x^{n+1}`
- Square root: `\\sqrt{x}`, `\\sqrt[3]{x}`
- Greek: `\\alpha`, `\\beta`, `\\theta`, `\\pi`, `\\sigma`, `\\mu`
- Operators: `\\sin`, `\\cos`, `\\tan`, `\\ln`, `\\log`
- Sum: `\\sum_{k=1}^{n}`
- Integral: `\\int_a^b`
- Vectors: `\\begin{pmatrix} 1 \\\\ 2 \\\\ 3 \\end{pmatrix}`
- Set notation: `\\in`, `\\mathbb{R}`, `\\mathbb{Z}^+`
- Chemistry: Write reactions as plain text with subscripts: `H\\(_2\\)O`

## Distractor Generation Rules

For MCQ questions, distractors (wrong answers) should be **plausible**:

### Mathematics
- Off-by-one errors (e.g., using `n` instead of `n-1`)
- Sign errors (forgetting a negative)
- Common formula mix-ups (arithmetic vs geometric)
- Partial answers (computing part but not all)
- Correct method, arithmetic slip

### Sciences
- Correct formula, wrong unit conversion
- Forgetting to account for a factor (e.g., 2 in 2H2O)
- Common misconceptions
- Correct magnitude, wrong sign

### Humanities (Econ/Business)
- Similar-sounding but different concepts
- Correct term but wrong definition
- Plausible but incorrect applications

## Recommended Coverage Per Subtopic

| Difficulty | MCQ | Worked | Numerical | Other | Total |
|-----------|-----|--------|-----------|-------|-------|
| Core | 3 | 2 | 2 | 1 | 8 |
| Challenge | 2 | 2 | 1 | 1 | 6 |
| Extension | 1 | 2 | 1 | 0 | 4 |

This gives ~18 questions per subtopic. With ~170 subtopics across all subjects, that's ~3,000 questions for full coverage.

## Validation

Before loading, validate your `questions.json`:

1. Every question has a valid `id` (unique)
2. Every `subject` matches a key in curriculum.json
3. Every `subtopic` exists in the curriculum
4. Every `type` is one of the 10 supported types
5. Every MCQ has exactly one `correct: true` option
6. Every numerical answer has a valid number
7. KaTeX renders without errors
8. No empty strings for `stem` or `mark_scheme`

## Example: Full Question

```json
{
  "id": "math_aa_1.1_mcq_001",
  "subject": "math_aa",
  "topic": "1",
  "subtopic": "1.1",
  "type": "mcq",
  "difficulty": "core",
  "tags": ["arithmetic-sequences", "nth-term"],
  "title": "Find the nth term of an arithmetic sequence",
  "stem": "An arithmetic sequence has first term \\(a_1 = 5\\) and common difference \\(d = 3\\). Find \\(a_{10}\\).",
  "content": {
    "options": [
      {"label": "A", "text": "\\(32\\)", "correct": true},
      {"label": "B", "text": "\\(30\\)", "correct": false},
      {"label": "C", "text": "\\(35\\)", "correct": false},
      {"label": "D", "text": "\\(27\\)", "correct": false}
    ],
    "shuffle": true
  },
  "mark_scheme": "Using \\(a_n = a_1 + (n-1)d\\):\n\n\\[a_{10} = 5 + (10-1)(3) = 5 + 27 = 32\\]",
  "hints": [
    "Recall the formula for the nth term of an arithmetic sequence",
    "Be careful: it's (n-1)d, not nd"
  ],
  "marks": 2,
  "time_estimate": 1
}
```
