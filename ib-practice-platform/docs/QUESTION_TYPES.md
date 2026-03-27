# Question Types — Detailed Specifications

## Type Matrix by Subject

This table shows which question types are most appropriate for each subject area.

| Type | Math AA/AI | Physics | Chemistry | Biology | Economics | Business | CS |
|------|-----------|---------|-----------|---------|-----------|----------|-----|
| mcq | *** | *** | *** | *** | *** | *** | *** |
| multi_select | ** | ** | ** | *** | ** | ** | ** |
| worked | *** | *** | ** | * | ** | ** | ** |
| numerical | *** | *** | *** | * | ** | *** | * |
| ordering | * | * | ** | *** | * | * | ** |
| matching | * | ** | *** | *** | ** | ** | ** |
| graph_sketch | *** | ** | * | * | *** | * | - |
| chem_structure | - | - | *** | * | - | - | - |
| truth_table | * | - | - | - | - | - | *** |
| calculation | ** | *** | *** | - | ** | *** | * |

`***` = Primary type, `**` = Common, `*` = Occasional, `-` = Not applicable

## Detailed Specifications per Type

### MCQ — Tips for Each Subject

**Mathematics**: Most useful for quick-check problems. Test formula recall, quick calculations, graph identification. Distractors should reflect common calculation errors.

**Physics**: Good for conceptual understanding. "In which direction does the force act?" with diagram descriptions. Numerical answers with unit traps.

**Chemistry**: Electron configuration identification, balancing equations (is this balanced?), identify the functional group, predict products.

**Biology**: Classification, identification of organelles, matching processes to locations, recall of facts.

**Economics**: Definition matching, identifying which curve shifts, predicting effects of policy changes.

**Business**: Identifying the correct management theory, financial term definitions, strategy identification.

**Computer Science**: Algorithm output prediction, identifying data structures, logic gate outputs.

### Worked Problems — Part Structure

For multi-part problems, structure the `parts` array carefully:

```json
{
  "parts": [
    {
      "label": "(a)",
      "text": "Show that...",
      "marks": 2,
      "command_term": "show"
    },
    {
      "label": "(b)",
      "text": "Hence find...",
      "marks": 4,
      "command_term": "find",
      "depends_on": "(a)"
    },
    {
      "label": "(c)",
      "text": "Justify why...",
      "marks": 2,
      "command_term": "justify"
    }
  ]
}
```

IB Command Terms to use:
- **show**: Display working leading to a given result
- **find**: Obtain an answer (working expected)
- **calculate**: Obtain a numerical answer
- **determine**: Obtain answer using given info
- **prove**: Rigorous mathematical argument
- **sketch**: Draw approximate graph showing key features
- **explain**: Give a detailed account of reasons
- **describe**: Give a detailed account of features
- **compare**: Give an account of similarities and differences
- **justify**: Support with evidence/reasoning
- **suggest**: Propose a solution/hypothesis
- **evaluate**: Make an appraisal with evidence
- **discuss**: Consider different perspectives
- **state**: Give a specific name/value without explanation
- **define**: Give the precise meaning

### Graph Sketch — Function Expression Reference

For `graph_sketch` type, expressions use JavaScript Math:

```javascript
// Basic functions
"x"               // linear
"x*x"             // quadratic
"x*x*x"           // cubic
"1/x"             // reciprocal
"Math.sqrt(x)"    // square root
"Math.abs(x)"     // absolute value

// Trigonometric
"Math.sin(x)"
"Math.cos(x)"
"Math.tan(x)"

// Exponential/Logarithmic
"Math.exp(x)"
"Math.log(x)"     // natural log
"Math.pow(2, x)"  // 2^x

// Combined
"2*Math.sin(3*x) + 1"
"Math.exp(-x*x)"  // Gaussian
"x*Math.exp(-x)"  // xe^(-x)
```

For graph options, always provide `xmin`, `xmax`, `ymin`, `ymax` to ensure consistent scales.

### Chemical Structure — SMILES Reference

Common SMILES patterns for IB Chemistry:

```
Methane:        C
Ethane:         CC
Ethene:         C=C
Ethyne:         C#C
Methanol:       CO
Ethanol:        CCO
Methanal:       C=O
Ethanal:        CC=O
Methanoic acid: OC=O
Ethanoic acid:  CC(=O)O
Propan-1-ol:    CCCO
Propan-2-ol:    CC(O)C
Butane:         CCCC
2-methylpropane: CC(C)C
Chloromethane:  CCl
Bromoethane:    CCBr
Benzene:        c1ccccc1
Phenol:         c1ccc(O)cc1
Toluene:        Cc1ccccc1
Amine (ethyl):  CCN
Ester:          CC(=O)OC
Amide:          CC(=O)N
```

The platform uses SmilesDrawer to render these. Always test that your SMILES strings render correctly.

### Truth Table — Logic Operators

For `truth_table` type:

| Symbol | Meaning | KaTeX |
|--------|---------|-------|
| AND | Conjunction | `\\land` |
| OR | Disjunction | `\\lor` |
| NOT | Negation | `\\lnot` |
| XOR | Exclusive or | `\\oplus` |
| IMPLIES | Implication | `\\Rightarrow` |
| IFF | Biconditional | `\\Leftrightarrow` |

Example expressions:
- `"P AND Q"` → \\(P \\land Q\\)
- `"NOT P OR Q"` → \\(\\lnot P \\lor Q\\)
- `"(P AND Q) OR (NOT R)"` → \\((P \\land Q) \\lor (\\lnot R)\\)

### Calculation — Step Types

Each step in a `calculation` question can be:

| Step Type | Description | Has Input? |
|-----------|-------------|------------|
| `info` | Display information/formula | No |
| `input` | Student enters a value | Yes |
| `reveal` | Hidden content revealed on click | No |

## Difficulty Guidelines

### Core (Easy)
- Direct application of a single formula/concept
- Numerical answers are "clean" (integers or simple fractions)
- 1-2 steps to solve
- Corresponds to IB marks 1-3

### Challenge (Medium)
- Requires combining 2-3 concepts
- May involve multi-step reasoning
- Answers may not be "clean" — rounding needed
- Corresponds to IB marks 3-6

### Extension (Hard)
- HL-only or requires deep understanding
- Multi-step problems with connections between topics
- May require proof, optimization, or abstract reasoning
- Corresponds to IB marks 6-10+

## ID Naming Convention

```
{subject}_{subtopic}_{type}_{difficulty_code}_{sequence}
```

Examples:
- `math_aa_1.1_mcq_c_001` — Math AA, subtopic 1.1, MCQ, core, #1
- `physics_A.1_numerical_ch_003` — Physics, subtopic A.1, numerical, challenge, #3
- `chemistry_S2.2_chem_structure_c_001` — Chemistry VSEPR structure question

Difficulty codes: `c` = core, `ch` = challenge, `e` = extension
