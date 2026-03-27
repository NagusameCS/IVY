# IB Practice Platform

A Khan Academy-style practice system for IB subjects. Runs 100% locally as a single HTML file — no server needed.

## Quick Start

1. Open `index.html` in any browser
2. Select a subject, check subtopics you want to practice
3. Configure session (question count, difficulty, timer)
4. Start practicing

## Generating Questions

The platform ships with ~10 demo questions. To get full coverage, generate questions using your local bot.

1. Read `docs/BOT_INSTRUCTIONS.md` for the complete question JSON schema
2. Read `docs/QUESTION_TYPES.md` for type-specific details
3. Read `docs/TEMPLATE_SYSTEM.md` for the template architecture overview
4. Generate a `questions.json` file and place it next to `index.html`
5. Refresh — questions load automatically

## Subjects Covered

All topics and subtopics from the IB curriculum:

| Subject | Topics | Subtopics |
|---------|--------|-----------|
| Mathematics AA | 10 | 81 |
| Mathematics AI | 10 | 81 (shared with AA) |
| Physics | 5 | 24 |
| Chemistry | 6 | 23 |
| Biology | 4 | 16 |
| Economics | 4 | 23 |
| Business Management | 5 | 28 |
| Computer Science | 5 | 11 |

## Question Types

| Type | Description | Input Method |
|------|-------------|-------------|
| `mcq` | Multiple choice (A-D) | Radio buttons |
| `multi_select` | Multiple correct answers | Checkboxes |
| `worked` | Do by hand, check mark scheme | Reveal button |
| `numerical` | Enter a number | Number input |
| `ordering` | Arrange items in order | Drag or buttons |
| `matching` | Match two columns | Dropdowns |
| `graph_sketch` | Select matching graph | MCQ with plots |
| `chem_structure` | Identify molecular structure | MCQ with SMILES |
| `truth_table` | Complete logic table | Cell inputs |
| `calculation` | Multi-step with intermediate answers | Step inputs |

## Built-in Tools

- **Periodic Table**: Full 118 elements, color-coded, clickable for details
- **Graphing Calculator**: Desmos integration
- **Scientific Calculator**: TI-84 style functions
- **Formula Sheets**: Math, Physics, Chemistry, Economics, Business

## File Structure

```
ib-practice-platform/
├── index.html           ← Main app (self-contained)
├── questions.json       ← Your generated questions (create this)
├── README.md            ← This file
├── data/
│   ├── curriculum.json  ← Complete IB curriculum structure
│   └── elements/
│       └── periodic-table.json  ← All 118 elements
└── docs/
    ├── TEMPLATE_SYSTEM.md    ← Architecture overview
    ├── BOT_INSTRUCTIONS.md   ← How to generate questions
    └── QUESTION_TYPES.md     ← Detailed type specs
```

## Tech Stack

- Single HTML file, inline CSS/JS
- KaTeX for math rendering
- Chart.js for graph rendering
- SmilesDrawer for chemical structures
- Desmos API for graphing calculator
- Google Material Icons
- Inter + JetBrains Mono fonts

## Design

SAT Bluebook aesthetic — white background, flat design, blue accent (#0d47a1), no gradients, no emojis. Responsive layout.
