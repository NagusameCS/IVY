#!/usr/bin/env python3
"""Adds new multi_select, calculation, and ordering question templates to each subject file."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
TMPL_DIR = ROOT / "data" / "templates"

# ─── New templates per subject ─────────────────────────────────────────

NEW_TEMPLATES = {

"math_aa_core.json": [
  {
    "id": "math_aa_1_1_ms_001",
    "subject": "math_aa",
    "topic": "1",
    "subtopic": "1.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Arithmetic Sequence Properties",
    "tags": ["sequences", "arithmetic", "properties"],
    "stem_template": "Which of the following statements about arithmetic sequences are TRUE? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Consecutive terms differ by a constant value", "correct": True},
      {"text": "Consecutive terms have a constant ratio", "correct": False},
      {"text": "The \\(n\\)th term is given by \\(u_n = a + (n-1)d\\)", "correct": True},
      {"text": "An arithmetic sequence must be increasing", "correct": False},
      {"text": "A constant sequence \\((d=0)\\) is technically arithmetic", "correct": True}
    ],
    "mark_scheme_template": "TRUE: consecutive difference d; nth term u_n=a+(n-1)d; d=0 is valid (constant). FALSE: constant ratio is geometric; arithmetic sequences can decrease when d<0.",
    "hints": ["Recall the definition: arithmetic means constant difference.", "Compare with geometric sequences."],
    "marks": 2
  },
  {
    "id": "math_aa_2_2_ms_001",
    "subject": "math_aa",
    "topic": "2",
    "subtopic": "2.2",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Quadratic Function Properties",
    "tags": ["quadratics", "functions", "parabola"],
    "stem_template": "A quadratic function \\(f(x) = ax^2 + bx + c\\) with \\(a > 0\\) has a positive discriminant. Which statements are TRUE? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "The parabola opens upward", "correct": True},
      {"text": "The function has exactly two distinct real roots", "correct": True},
      {"text": "The vertex is the maximum point", "correct": False},
      {"text": "The axis of symmetry is \\(x = -\\dfrac{b}{2a}\\)", "correct": True},
      {"text": "The function has no real roots", "correct": False}
    ],
    "mark_scheme_template": "a>0 means opens upward (min vertex, not max). Positive discriminant \\(b^2-4ac>0\\) means two distinct real roots. Axis of symmetry: x=-b/(2a). FALSE: vertex is minimum; roots exist.",
    "hints": ["Recall: a>0 → opens up → vertex is minimum.", "Discriminant > 0 → two real roots."],
    "marks": 2
  },
  {
    "id": "math_aa_1_2_ms_001",
    "subject": "math_aa",
    "topic": "1",
    "subtopic": "1.2",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Geometric Sequence Properties",
    "tags": ["sequences", "geometric", "properties"],
    "stem_template": "Which of the following are TRUE about a geometric sequence with common ratio \\(r\\)? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Consecutive terms have a constant ratio", "correct": True},
      {"text": "The \\(n\\)th term is \\(u_n = u_1 \\cdot r^{n-1}\\)", "correct": True},
      {"text": "The sum to infinity exists if \\(|r| < 1\\)", "correct": True},
      {"text": "The sequence must have positive terms", "correct": False},
      {"text": "\\(r = 0\\) is a valid common ratio", "correct": False}
    ],
    "mark_scheme_template": "TRUE: constant ratio r; nth term u1*r^(n-1); sum to infinity S=u1/(1-r) exists when |r|<1. FALSE: negative r allows negative terms; r=0 would make all terms 0 (not valid geometric).",
    "hints": ["Focus on the constant ratio property.", "Sum to infinity: needs |r| < 1."],
    "marks": 2
  },
  {
    "id": "math_aa_2_3_ms_001",
    "subject": "math_aa",
    "topic": "2",
    "subtopic": "2.3",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Logarithm Laws",
    "tags": ["logarithms", "laws", "algebra"],
    "stem_template": "Which of the following logarithm identities are CORRECT? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "\\(\\log(ab) = \\log a + \\log b\\)", "correct": True},
      {"text": "\\(\\log\\left(\\dfrac{a}{b}\\right) = \\log a - \\log b\\)", "correct": True},
      {"text": "\\(\\log(a + b) = \\log a \\cdot \\log b\\)", "correct": False},
      {"text": "\\(\\log(a^n) = n \\log a\\)", "correct": True},
      {"text": "\\(\\log_a a = 1\\) for any valid base \\(a\\)", "correct": True}
    ],
    "mark_scheme_template": "Correct log laws: log(ab)=log a+log b; log(a/b)=log a-log b; log(a^n)=n log a; log_a(a)=1. INCORRECT: log(a+b) has no simplification.",
    "hints": ["Recall the three main log laws: product, quotient, power.", "log_a(a) = 1 by definition."],
    "marks": 2
  },
  {
    "id": "math_aa_1_1_calc_001",
    "subject": "math_aa",
    "topic": "1",
    "subtopic": "1.1",
    "type": "calculation",
    "difficulty": "core",
    "title": "Arithmetic Series Sum Step-by-Step",
    "tags": ["sequences", "series", "arithmetic", "calculation"],
    "stem_template": "An arithmetic sequence has first term \\(a = {{a}}\\), common difference \\(d = {{d}}\\), and \\(n = {{n}}\\) terms. Find the sum of all \\(n\\) terms.",
    "params": {
      "a": {"type": "int", "min": 1, "max": 15},
      "d": {"type": "int", "min": 1, "max": 6},
      "n": {"type": "int", "min": 5, "max": 20}
    },
    "answer_template": "{{n}} / 2 * (2 * {{a}} + ({{n}} - 1) * {{d}})",
    "steps_template": [
      {
        "label": "Step 1",
        "content": "Identify: \\(a = {{a}}\\), \\(d = {{d}}\\), \\(n = {{n}}\\). Use: \\(S_n = \\dfrac{n}{2}(2a + (n-1)d)\\)",
        "type": "info"
      },
      {
        "label": "Step 2",
        "content": "Substitute values: \\(S_{{n}} = \\dfrac{{{n}}}{2}(2({{a}}) + ({{n}}-1)({{d}}))\\). What is the answer?",
        "type": "input",
        "answer": "{{n}} / 2 * (2 * {{a}} + ({{n}} - 1) * {{d}})",
        "tolerance": 0.5,
        "unit": ""
      }
    ],
    "mark_scheme_template": "\\(S_n = \\dfrac{n}{2}(2a + (n-1)d) = \\dfrac{{{n}}}{2}({{2*a}} + {{n-1}} \\times {{d}}) = {{answer}}\\)",
    "hints": ["Formula: S_n = n/2 × (2a + (n-1)d)", "Substitute a={{a}}, d={{d}}, n={{n}}"],
    "marks": 3
  },
  {
    "id": "math_aa_2_2_calc_001",
    "subject": "math_aa",
    "topic": "2",
    "subtopic": "2.2",
    "type": "calculation",
    "difficulty": "core",
    "title": "Quadratic Roots via Quadratic Formula",
    "tags": ["quadratics", "formula", "roots", "calculation"],
    "stem_template": "Find the larger root of \\({{a}}x^2 + {{b}}x + {{c}} = 0\\) using the quadratic formula.",
    "params": {
      "a": {"type": "int", "min": 1, "max": 3},
      "b": {"type": "int", "min": -10, "max": -2},
      "c": {"type": "int", "min": 1, "max": 6}
    },
    "answer_template": "(-{{b}} + math.sqrt({{b}}**2 - 4*{{a}}*{{c}})) / (2*{{a}})",
    "steps_template": [
      {
        "label": "Step 1",
        "content": "Identify \\(a={{a}}, b={{b}}, c={{c}}\\). Compute discriminant \\(\\Delta = b^2 - 4ac\\).",
        "type": "info"
      },
      {
        "label": "Step 2",
        "content": "\\(\\Delta = ({{b}})^2 - 4({{a}})({{c}}) = {{b**2}} - {{4*a*c}}\\). What is \\(\\Delta\\)?",
        "type": "input",
        "answer": "{{b}}**2 - 4*{{a}}*{{c}}",
        "tolerance": 0.1,
        "unit": ""
      },
      {
        "label": "Step 3",
        "content": "Larger root: \\(x = \\dfrac{-b + \\sqrt{\\Delta}}{2a}\\). Give answer to 3 s.f.",
        "type": "input",
        "answer": "(-{{b}} + math.sqrt({{b}}**2 - 4*{{a}}*{{c}})) / (2*{{a}})",
        "tolerance": 0.01,
        "unit": ""
      }
    ],
    "mark_scheme_template": "\\(\\Delta = {{b**2 - 4*a*c}}\\); larger root \\(x = \\dfrac{{{-b}} + \\sqrt{{{b**2 - 4*a*c}}}}{{{2*a}}} \\approx {{answer}}\\)",
    "hints": ["Quadratic formula: x = (-b ± √(b²-4ac)) / 2a", "Larger root uses the + sign."],
    "marks": 4
  },
  {
    "id": "math_aa_2_2_ord_001",
    "subject": "math_aa",
    "topic": "2",
    "subtopic": "2.2",
    "type": "ordering",
    "difficulty": "core",
    "title": "Completing the Square — Step Order",
    "tags": ["quadratics", "completing-the-square", "method"],
    "stem_template": "Put the following steps for completing the square on \\(x^2 + bx + c\\) in the CORRECT ORDER.",
    "params": {},
    "items": [
      "Write \\(x^2 + bx = (x + b/2)^2 - (b/2)^2\\)",
      "Add the constant \\(c\\) back to both sides",
      "Identify the coefficient of \\(x\\), divide by 2, and square it",
      "Rewrite in the form \\((x+p)^2 + q\\)"
    ],
    "correct_order": [2, 0, 1, 3],
    "mark_scheme_template": "Correct order: (1) identify b/2 and square it; (2) write as (x+b/2)²-(b/2)²; (3) add c back; (4) express as (x+p)²+q.",
    "hints": ["Start by finding (b/2)².", "Complete the square before adding the constant."],
    "marks": 2
  }
],

"math_aa_hl.json": [
  {
    "id": "math_aa_hl_3_1_ms_001",
    "subject": "math_aa",
    "topic": "3",
    "subtopic": "3.1",
    "type": "multi_select",
    "difficulty": "hl",
    "title": "Complex Number Properties",
    "tags": ["complex numbers", "properties", "hl"],
    "stem_template": "Let \\(z = a + bi\\). Which of the following statements are TRUE? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "The modulus of \\(z\\) is \\(|z| = \\sqrt{a^2 + b^2}\\)", "correct": True},
      {"text": "The conjugate of \\(z\\) is \\(\\bar{z} = a - bi\\)", "correct": True},
      {"text": "\\(z \\cdot \\bar{z} = a^2 + b^2\\)", "correct": True},
      {"text": "\\(z + \\bar{z} = 2bi\\)", "correct": False},
      {"text": "\\(i^4 = 1\\)", "correct": True}
    ],
    "mark_scheme_template": "TRUE: |z|=√(a²+b²); conjugate ā=a-bi; z·ā=a²+b²; i⁴=1. FALSE: z+ā=2a (real part × 2), not 2bi.",
    "hints": ["Conjugate: change sign of imaginary part.", "z × z̄ is always real."],
    "marks": 2
  },
  {
    "id": "math_aa_hl_5_2_ms_001",
    "subject": "math_aa",
    "topic": "5",
    "subtopic": "5.2",
    "type": "multi_select",
    "difficulty": "hl",
    "title": "Integration Techniques",
    "tags": ["integration", "calculus", "hl"],
    "stem_template": "Which of the following integrals can be solved directly using the substitution method \\(u = g(x)\\)? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "\\(\\displaystyle\\int 2x \\cdot e^{x^2} \\, dx\\)", "correct": True},
      {"text": "\\(\\displaystyle\\int \\cos(3x) \\, dx\\)", "correct": True},
      {"text": "\\(\\displaystyle\\int x^2 e^x \\, dx\\)", "correct": False},
      {"text": "\\(\\displaystyle\\int \\dfrac{2x}{x^2+1} \\, dx\\)", "correct": True},
      {"text": "\\(\\displaystyle\\int x \\ln x \\, dx\\)", "correct": False}
    ],
    "mark_scheme_template": "Substitution works when the integrand contains a function and its derivative: 2x·e^(x²) (u=x²); cos(3x) (u=3x); 2x/(x²+1) (u=x²+1). Integration by parts needed for x²eˣ and x ln x.",
    "hints": ["Look for f'(x)·f(g(x)) patterns.", "x²eˣ and x ln x require integration by parts."],
    "marks": 2
  },
  {
    "id": "math_aa_hl_4_1_ms_001",
    "subject": "math_aa",
    "topic": "4",
    "subtopic": "4.1",
    "type": "multi_select",
    "difficulty": "hl",
    "title": "Probability Concepts",
    "tags": ["probability", "statistics", "hl"],
    "stem_template": "Two events \\(A\\) and \\(B\\) are mutually exclusive. Which statements MUST be true? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "\\(P(A \\cap B) = 0\\)", "correct": True},
      {"text": "\\(P(A \\cup B) = P(A) + P(B)\\)", "correct": True},
      {"text": "\\(A\\) and \\(B\\) are independent", "correct": False},
      {"text": "\\(P(A|B) = 0\\)", "correct": True},
      {"text": "\\(P(A) + P(B) \\leq 1\\)", "correct": True}
    ],
    "mark_scheme_template": "Mutually exclusive: P(A∩B)=0; P(A∪B)=P(A)+P(B); P(A|B)=0; P(A)+P(B)≤1. NOT independent (mutual exclusivity implies dependence unless one has P=0).",
    "hints": ["Mutually exclusive → cannot occur together.", "Independence requires P(A∩B)=P(A)·P(B)."],
    "marks": 2
  },
  {
    "id": "math_aa_hl_5_3_calc_001",
    "subject": "math_aa",
    "topic": "5",
    "subtopic": "5.3",
    "type": "calculation",
    "difficulty": "hl",
    "title": "Integration by Parts",
    "tags": ["integration", "by-parts", "calculus", "hl"],
    "stem_template": "Evaluate \\(\\displaystyle\\int x \\cdot e^{{{k}}x} \\, dx\\) using integration by parts.",
    "params": {
      "k": {"type": "int", "min": 1, "max": 5}
    },
    "answer_template": "None",
    "steps_template": [
      {
        "label": "Identify u and dv",
        "content": "Let \\(u = x\\) and \\(dv = e^{{{k}}x} \\, dx\\), so \\(du = dx\\) and \\(v = \\dfrac{1}{{{k}}}e^{{{k}}x}\\).",
        "type": "info"
      },
      {
        "label": "Apply formula",
        "content": "Integration by parts: \\(\\int u \\, dv = uv - \\int v \\, du\\). Write out \\(\\dfrac{x}{{{k}}}e^{{{k}}x} - \\int \\dfrac{1}{{{k}}}e^{{{k}}x} \\, dx\\).",
        "type": "info"
      },
      {
        "label": "What is the coefficient of \\(e^{{{k}}x}\\) in the final answer?",
        "content": "The final answer is \\(\\dfrac{x}{{{k}}}e^{{{k}}x} - \\dfrac{1}{{{k}}^2}e^{{{k}}x} + C\\). What is the coefficient of the second term \\(e^{{{k}}x}\\)?",
        "type": "input",
        "answer": "-1 / ({{k}} ** 2)",
        "tolerance": 0.001,
        "unit": ""
      }
    ],
    "mark_scheme_template": "\\(\\int x e^{{{k}}x} \\, dx = \\dfrac{x}{{{k}}}e^{{{k}}x} - \\dfrac{1}{{{k}}^2}e^{{{k}}x} + C\\)",
    "hints": ["Let u=x (easy to differentiate).", "The integral of e^(kx) is (1/k)e^(kx)."],
    "marks": 5
  }
],

"math_ai.json": [
  {
    "id": "math_ai_4_1_ms_001",
    "subject": "math_ai",
    "topic": "4",
    "subtopic": "4.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Normal Distribution Properties",
    "tags": ["statistics", "normal distribution", "properties"],
    "stem_template": "Which of the following are properties of the Normal distribution \\(X \\sim N(\\mu, \\sigma^2)\\)? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "The distribution is symmetric about the mean \\(\\mu\\)", "correct": True},
      {"text": "Mean = Median = Mode", "correct": True},
      {"text": "About 68% of data lies within \\(\\pm 1\\sigma\\) of the mean", "correct": True},
      {"text": "The distribution has a finite range", "correct": False},
      {"text": "The total area under the curve equals 1", "correct": True}
    ],
    "mark_scheme_template": "Normal distribution: symmetric; mean=median=mode; 68% within 1σ; total area=1. FALSE: Normal distribution extends from −∞ to +∞ (infinite range).",
    "hints": ["Think about the bell curve shape.", "Area under PDF = 1 for any probability distribution."],
    "marks": 2
  },
  {
    "id": "math_ai_2_1_ms_001",
    "subject": "math_ai",
    "topic": "2",
    "subtopic": "2.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Regression and Correlation",
    "tags": ["statistics", "regression", "correlation"],
    "stem_template": "Which statements about the correlation coefficient \\(r\\) are TRUE? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "\\(-1 \\leq r \\leq 1\\)", "correct": True},
      {"text": "\\(r = 0\\) means the variables are independent", "correct": False},
      {"text": "|r| close to 1 indicates a strong linear relationship", "correct": True},
      {"text": "\\(r\\) measures the strength and direction of linear association", "correct": True},
      {"text": "\\(r = -0.9\\) indicates a weaker relationship than \\(r = 0.6\\)", "correct": False}
    ],
    "mark_scheme_template": "-1≤r≤1; |r| close to 1 = strong linear; r measures strength AND direction. FALSE: r=0 means no LINEAR relationship, not necessarily independent; |−0.9|>|0.6| so stronger.",
    "hints": ["r is always between -1 and 1.", "Strength is measured by |r|, not sign."],
    "marks": 2
  },
  {
    "id": "math_ai_1_4_ms_001",
    "subject": "math_ai",
    "topic": "1",
    "subtopic": "1.4",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Financial Mathematics Concepts",
    "tags": ["finance", "compound interest", "annuity"],
    "stem_template": "Which of the following statements about compound interest are TRUE? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Compound interest earns interest on previously earned interest", "correct": True},
      {"text": "More frequent compounding always results in less interest earned", "correct": False},
      {"text": "The effective annual rate increases as compounding frequency increases", "correct": True},
      {"text": "\\(A = P\\left(1 + \\dfrac{r}{n}\\right)^{nt}\\) gives the amount after \\(t\\) years", "correct": True},
      {"text": "Simple and compound interest give the same result over 1 year", "correct": True}
    ],
    "mark_scheme_template": "TRUE: compound earns interest on interest; EAR increases with frequency; formula A=P(1+r/n)^(nt); at exactly 1 year, simple=compound for same annual rate. FALSE: more compounding = MORE interest.",
    "hints": ["Compare A=P(1+r)^t (compound) vs A=P(1+rt) (simple).", "EAR = (1 + r/n)^n - 1."],
    "marks": 2
  },
  {
    "id": "math_ai_1_4_calc_001",
    "subject": "math_ai",
    "topic": "1",
    "subtopic": "1.4",
    "type": "calculation",
    "difficulty": "core",
    "title": "Compound Interest Calculation",
    "tags": ["finance", "compound interest", "calculation"],
    "stem_template": "\\${{P}} is invested at {{r}}% per annum, compounded {{n}} times per year for {{t}} years. Find the final amount.",
    "params": {
      "P": {"type": "int", "min": 1000, "max": 10000},
      "r": {"type": "int", "min": 2, "max": 8},
      "n": {"type": "choice", "values": [1, 2, 4, 12]},
      "t": {"type": "int", "min": 2, "max": 10}
    },
    "answer_template": "{{P}} * (1 + {{r}} / 100 / {{n}}) ** ({{n}} * {{t}})",
    "steps_template": [
      {
        "label": "Step 1",
        "content": "Identify: \\(P = {{P}}\\), \\(r = {{r}}\\%\\), \\(n = {{n}}\\), \\(t = {{t}}\\). Formula: \\(A = P\\left(1 + \\dfrac{r}{100n}\\right)^{nt}\\)",
        "type": "info"
      },
      {
        "label": "Step 2",
        "content": "Substitute: \\(A = {{P}}\\left(1 + \\dfrac{{{r}}}{100 \\times {{n}}}\\right)^{{{n}} \\times {{t}}}\\). Calculate \\(A\\) (to 2 decimal places).",
        "type": "input",
        "answer": "{{P}} * (1 + {{r}} / 100 / {{n}}) ** ({{n}} * {{t}})",
        "tolerance": 0.5,
        "unit": "$"
      }
    ],
    "mark_scheme_template": "\\(A = {{P}}\\left(1 + \\dfrac{{{r}}}{100 \\times {{n}}}\\right)^{{{n}} \\times {{t}}} \\approx \\${{answer:.2f}}\\)",
    "hints": ["Use A = P(1 + r/(100n))^(nt).", "Convert % to decimal by dividing by 100."],
    "marks": 3
  }
],

"biology.json": [
  {
    "id": "bio_1_1_ms_001",
    "subject": "biology",
    "topic": "1",
    "subtopic": "1.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Cell Organelle Functions",
    "tags": ["cell biology", "organelles", "functions"],
    "stem_template": "Which of the following organelles are found in BOTH plant AND animal cells? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Mitochondria", "correct": True},
      {"text": "Cell wall", "correct": False},
      {"text": "Ribosomes", "correct": True},
      {"text": "Chloroplasts", "correct": False},
      {"text": "Endoplasmic reticulum", "correct": True},
      {"text": "Nucleus", "correct": True}
    ],
    "mark_scheme_template": "BOTH: mitochondria, ribosomes, endoplasmic reticulum, nucleus (and Golgi, vacuoles, cell membrane). PLANT ONLY: cell wall, chloroplasts, large central vacuole.",
    "hints": ["Animal cells lack: cell wall and chloroplasts.", "Both cell types need mitochondria for respiration."],
    "marks": 2
  },
  {
    "id": "bio_3_1_ms_001",
    "subject": "biology",
    "topic": "3",
    "subtopic": "3.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Mendelian Genetics",
    "tags": ["genetics", "alleles", "inheritance"],
    "stem_template": "Which of the following statements about dominant and recessive alleles are TRUE? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "A dominant allele is expressed when at least one copy is present", "correct": True},
      {"text": "Recessive traits can only appear in individuals with two recessive alleles", "correct": True},
      {"text": "Dominant alleles are always more common in a population", "correct": False},
      {"text": "A heterozygous individual carries two different alleles", "correct": True},
      {"text": "Recessive alleles disappear in subsequent generations", "correct": False}
    ],
    "mark_scheme_template": "TRUE: dominant expressed with 1 copy; recessive shown only in aa; heterozygous = two different alleles. FALSE: dominant ≠ more common (e.g. Huntington's is rare but dominant); recessive alleles persist in carriers.",
    "hints": ["Dominant: one copy is enough. Recessive: needs two copies.", "Heterozygous = Aa, homozygous = AA or aa."],
    "marks": 2
  },
  {
    "id": "bio_4_1_ms_001",
    "subject": "biology",
    "topic": "4",
    "subtopic": "4.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Ecological Concepts",
    "tags": ["ecology", "ecosystems", "energy flow"],
    "stem_template": "Which of the following statements about energy flow in ecosystems are TRUE? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Energy flows in one direction through a food chain", "correct": True},
      {"text": "Approximately 10% of energy is transferred between trophic levels", "correct": True},
      {"text": "Producers are heterotrophs", "correct": False},
      {"text": "Decomposers recycle nutrients but not energy", "correct": True},
      {"text": "A food web shows more complex relationships than a food chain", "correct": True}
    ],
    "mark_scheme_template": "TRUE: one-directional energy flow; ~10% transfer efficiency; decomposers recycle matter; food webs more complex. FALSE: producers are autotrophs (make own food via photosynthesis).",
    "hints": ["Producers = autotrophs (make energy from sun).", "Energy is lost as heat at each trophic level."],
    "marks": 2
  }
],

"chemistry.json": [
  {
    "id": "chem_1_1_ms_001",
    "subject": "chemistry",
    "topic": "1",
    "subtopic": "1.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Periodic Table Trends",
    "tags": ["periodic table", "trends", "atomic radius"],
    "stem_template": "Which of the following trends across Period 3 (left to right) are CORRECT? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Atomic radius decreases", "correct": True},
      {"text": "First ionisation energy generally increases", "correct": True},
      {"text": "Electronegativity decreases", "correct": False},
      {"text": "The number of protons increases by 1 each element", "correct": True},
      {"text": "Metallic character increases", "correct": False}
    ],
    "mark_scheme_template": "Left→right across Period 3: atomic radius decreases (more protons attract electrons closer); IE generally increases; proton number increases by 1. FALSE: electronegativity increases; metallic character decreases.",
    "hints": ["More protons = stronger nuclear attraction = smaller radius.", "Metallic character decreases left to right."],
    "marks": 2
  },
  {
    "id": "chem_10_1_ms_001",
    "subject": "chemistry",
    "topic": "10",
    "subtopic": "10.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Organic Functional Groups",
    "tags": ["organic chemistry", "functional groups", "identification"],
    "stem_template": "Which of the following functional groups are present in an amino acid? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Amino group (\\(\\text{—NH}_2\\))", "correct": True},
      {"text": "Carboxyl group (\\(\\text{—COOH}\\))", "correct": True},
      {"text": "Hydroxyl group (\\(\\text{—OH}\\))", "correct": False},
      {"text": "\\(\\alpha\\)-carbon bonded to both groups", "correct": True},
      {"text": "Carbonyl group (\\(\\text{C=O}\\)) in an aldehyde", "correct": False}
    ],
    "mark_scheme_template": "Amino acids contain: —NH₂ (amino), —COOH (carboxyl), and an α-carbon. The —OH in COOH is part of the carboxyl, not a separate hydroxyl. No aldehyde group in standard amino acids.",
    "hints": ["General amino acid structure: H₂N—CH(R)—COOH.", "The α-carbon is bonded to both —NH₂ and —COOH."],
    "marks": 2
  },
  {
    "id": "chem_7_1_ms_001",
    "subject": "chemistry",
    "topic": "7",
    "subtopic": "7.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Equilibrium Principles",
    "tags": ["equilibrium", "Le Chatelier", "reversible reactions"],
    "stem_template": "For an exothermic reversible reaction in equilibrium, which changes will shift the equilibrium to the RIGHT? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Decreasing temperature", "correct": True},
      {"text": "Increasing pressure (if gases are present and products side has fewer moles of gas)", "correct": True},
      {"text": "Adding a catalyst", "correct": False},
      {"text": "Increasing concentration of reactants", "correct": True},
      {"text": "Removing products", "correct": True}
    ],
    "mark_scheme_template": "Shifts RIGHT: lower T (exothermic favoured); higher P when products have fewer gas moles; adding reactants; removing products. Catalyst: speeds equilibrium, doesn't shift position.",
    "hints": ["Le Chatelier: system opposes the change.", "Catalyst: equal effect on forward and reverse."],
    "marks": 2
  },
  {
    "id": "chem_1_2_ord_001",
    "subject": "chemistry",
    "topic": "1",
    "subtopic": "1.2",
    "type": "ordering",
    "difficulty": "core",
    "title": "Empirical Formula Determination Steps",
    "tags": ["stoichiometry", "empirical formula", "method"],
    "stem_template": "Arrange the following steps for finding an empirical formula from percentage composition in the CORRECT ORDER.",
    "params": {},
    "items": [
      "Divide each mole value by the smallest mole value",
      "Write the empirical formula using the resulting ratios",
      "Assume 100 g sample; convert % to mass in grams",
      "Divide each mass by the element's molar mass to get moles"
    ],
    "correct_order": [2, 3, 0, 1],
    "mark_scheme_template": "Correct order: (1) assume 100g sample; (2) convert mass to moles (÷ molar mass); (3) divide by smallest mole value; (4) write empirical formula.",
    "hints": ["Start with 100g so % = grams directly.", "The final ratio gives the subscripts."],
    "marks": 2
  }
],

"physics.json": [
  {
    "id": "phys_2_1_ms_001",
    "subject": "physics",
    "topic": "2",
    "subtopic": "2.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Newton's Laws of Motion",
    "tags": ["mechanics", "Newton's laws", "forces"],
    "stem_template": "Which of the following statements correctly apply Newton's Second Law (\\(F = ma\\))? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "A larger force on the same mass produces greater acceleration", "correct": True},
      {"text": "An object at rest has no forces acting on it", "correct": False},
      {"text": "If net force is zero, acceleration is zero", "correct": True},
      {"text": "Mass and weight are the same quantity", "correct": False},
      {"text": "The unit of force (Newton) equals kg·m·s⁻²", "correct": True}
    ],
    "mark_scheme_template": "TRUE: F∝a for constant m; net F=0 → a=0; N=kg·m·s⁻². FALSE: object at rest has balanced forces (e.g. gravity + normal); weight=mg≠m.",
    "hints": ["F=ma: net force determines acceleration.", "Objects at rest still have gravity balanced by normal force."],
    "marks": 2
  },
  {
    "id": "phys_4_1_ms_001",
    "subject": "physics",
    "topic": "4",
    "subtopic": "4.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Wave Properties",
    "tags": ["waves", "properties", "SHM"],
    "stem_template": "Which of the following correctly describe properties of transverse waves? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Particle displacement is perpendicular to wave propagation direction", "correct": True},
      {"text": "Sound waves are transverse", "correct": False},
      {"text": "Light is an example of a transverse wave", "correct": True},
      {"text": "Transverse waves require a medium to travel through", "correct": False},
      {"text": "Amplitude affects the energy carried by the wave", "correct": True}
    ],
    "mark_scheme_template": "Transverse: perpendicular displacement; EM waves (light) are transverse; higher amplitude = more energy. FALSE: sound is longitudinal; EM waves (light) travel through vacuum — no medium needed.",
    "hints": ["Transverse: displacement ⊥ propagation.", "Light is EM wave — it can travel through vacuum."],
    "marks": 2
  },
  {
    "id": "phys_5_1_ms_001",
    "subject": "physics",
    "topic": "5",
    "subtopic": "5.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Electrical Circuit Concepts",
    "tags": ["electricity", "circuits", "Ohm's law"],
    "stem_template": "Which of the following are TRUE about components connected in SERIES in a circuit? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "The same current flows through all components", "correct": True},
      {"text": "The voltage is the same across all components", "correct": False},
      {"text": "Total resistance = sum of individual resistances", "correct": True},
      {"text": "If one component fails (open circuit), all components stop", "correct": True},
      {"text": "Total voltage = sum of individual voltages across each component", "correct": True}
    ],
    "mark_scheme_template": "Series: same current everywhere; total R=R₁+R₂+...; total V=V₁+V₂+...; one break stops all. FALSE: voltage DIVIDES (not equal) across components in series.",
    "hints": ["Series: one path for current → same current everywhere.", "Compare with parallel circuits where voltage is shared equally."],
    "marks": 2
  },
  {
    "id": "phys_2_1_calc_001",
    "subject": "physics",
    "topic": "2",
    "subtopic": "2.1",
    "type": "calculation",
    "difficulty": "core",
    "title": "Projectile Motion Step-by-Step",
    "tags": ["kinematics", "projectile", "SUVAT", "calculation"],
    "stem_template": "A ball is launched horizontally at \\({{v}}\\) m/s from a height of \\({{h}}\\) m. Find the time to reach the ground and the horizontal range.",
    "params": {
      "v": {"type": "int", "min": 5, "max": 25},
      "h": {"type": "int", "min": 5, "max": 40}
    },
    "answer_template": "{{v}} * math.sqrt(2 * {{h}} / 9.81)",
    "steps_template": [
      {
        "label": "Step 1: Time to fall",
        "content": "Vertical: \\(h = \\frac{1}{2}gt^2\\). Rearrange: \\(t = \\sqrt{\\dfrac{2h}{g}}\\).",
        "type": "info"
      },
      {
        "label": "Calculate time (s)",
        "content": "\\(t = \\sqrt{\\dfrac{2 \\times {{h}}}{9.81}}\\). Give answer to 3 s.f.",
        "type": "input",
        "answer": "math.sqrt(2 * {{h}} / 9.81)",
        "tolerance": 0.05,
        "unit": "s"
      },
      {
        "label": "Calculate horizontal range (m)",
        "content": "Horizontal: \\(R = v \\times t = {{v}} \\times t\\). Give answer to 3 s.f.",
        "type": "input",
        "answer": "{{v}} * math.sqrt(2 * {{h}} / 9.81)",
        "tolerance": 0.5,
        "unit": "m"
      }
    ],
    "mark_scheme_template": "\\(t = \\sqrt{2h/g} = \\sqrt{2 \\times {{h}} / 9.81} \\approx {{round(math.sqrt(2*h/9.81),2)}}\\) s; Range \\(= {{v}} \\times t \\approx {{round(answer,1)}}\\) m",
    "hints": ["Horizontal and vertical motion are independent.", "Use g = 9.81 m/s²."],
    "marks": 4
  },
  {
    "id": "phys_2_1_ord_001",
    "subject": "physics",
    "topic": "2",
    "subtopic": "2.1",
    "type": "ordering",
    "difficulty": "core",
    "title": "SUVAT Problem-Solving Order",
    "tags": ["kinematics", "SUVAT", "method"],
    "stem_template": "Arrange the following steps for solving a SUVAT kinematics problem in the CORRECT ORDER.",
    "params": {},
    "items": [
      "Identify which SUVAT equation to use (contains the required variable and the known ones)",
      "List all known quantities: s, u, v, a, t",
      "Substitute values and calculate the unknown",
      "Read the problem and define positive direction"
    ],
    "correct_order": [3, 1, 0, 2],
    "mark_scheme_template": "Correct order: (1) read + define direction; (2) list knowns; (3) select equation; (4) substitute and solve.",
    "hints": ["Always define positive direction first.", "You need 3 knowns to find the 2 unknowns using one equation."],
    "marks": 2
  }
],

"economics.json": [
  {
    "id": "econ_1_1_ms_001",
    "subject": "economics",
    "topic": "1",
    "subtopic": "1.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Demand Curve Shifters",
    "tags": ["demand", "shifts", "non-price factors"],
    "stem_template": "Which of the following will cause the DEMAND CURVE to shift to the RIGHT (increase in demand)? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "An increase in consumer income (normal good)", "correct": True},
      {"text": "A fall in the price of the good", "correct": False},
      {"text": "An increase in the price of a substitute good", "correct": True},
      {"text": "A positive change in consumer tastes towards the good", "correct": True},
      {"text": "Expectations of future price increases", "correct": True}
    ],
    "mark_scheme_template": "Right shift (increase): higher income (normal good); price ↑ of substitute; positive taste change; expected higher future price. WRONG: lower price causes movement ALONG the curve, not a shift.",
    "hints": ["Price changes = movement along curve, not a shift.", "Non-price factors = shift of the demand curve."],
    "marks": 2
  },
  {
    "id": "econ_3_1_ms_001",
    "subject": "economics",
    "topic": "3",
    "subtopic": "3.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Market Structure Characteristics",
    "tags": ["market structures", "perfect competition", "monopoly"],
    "stem_template": "Which of the following are characteristics of PERFECT COMPETITION? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Many buyers and sellers", "correct": True},
      {"text": "Firms are price makers", "correct": False},
      {"text": "Homogeneous (identical) products", "correct": True},
      {"text": "Free entry and exit in the long run", "correct": True},
      {"text": "Firms earn supernormal profits in the long run", "correct": False}
    ],
    "mark_scheme_template": "Perfect competition: many buyers/sellers; homogeneous products; free entry/exit; price TAKERS. FALSE: firms are price takers (not makers); LR economic profit = 0 due to free entry.",
    "hints": ["Perfect competition: firms accept market price.", "SR supernormal profit attracts entry → LR normal profit only."],
    "marks": 2
  },
  {
    "id": "econ_4_1_ms_001",
    "subject": "economics",
    "topic": "4",
    "subtopic": "4.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Monetary vs Fiscal Policy",
    "tags": ["macroeconomics", "monetary policy", "fiscal policy"],
    "stem_template": "Which of the following are examples of EXPANSIONARY monetary policy? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Reducing interest rates", "correct": True},
      {"text": "Increasing government spending", "correct": False},
      {"text": "Buying government bonds (open market operations)", "correct": True},
      {"text": "Reducing the required reserve ratio for banks", "correct": True},
      {"text": "Reducing income tax rates", "correct": False}
    ],
    "mark_scheme_template": "Expansionary monetary: lower rates; buy bonds (inject money); lower reserve ratio (more lending). NOT monetary: increased government spending and lower taxes are FISCAL policy.",
    "hints": ["Monetary policy: controlled by central bank, affects money supply/interest rates.", "Fiscal policy: government taxation and spending."],
    "marks": 2
  },
  {
    "id": "econ_1_2_calc_001",
    "subject": "economics",
    "topic": "1",
    "subtopic": "1.2",
    "type": "calculation",
    "difficulty": "core",
    "title": "Price Elasticity of Demand",
    "tags": ["elasticity", "PED", "calculation"],
    "stem_template": "When price rises from \\${{P1}} to \\${{P2}}, quantity demanded falls from {{Q1}} to {{Q2}} units. Calculate the Price Elasticity of Demand (PED).",
    "params": {
      "P1": {"type": "int", "min": 5, "max": 20},
      "P2": {"type": "int", "min": 21, "max": 40},
      "Q1": {"type": "int", "min": 100, "max": 500},
      "Q2": {"type": "int", "min": 50, "max": 99}
    },
    "answer_template": "abs(({{Q2}} - {{Q1}}) / {{Q1}}) / abs(({{P2}} - {{P1}}) / {{P1}})",
    "steps_template": [
      {
        "label": "Step 1",
        "content": "Formula: \\(\\text{PED} = \\dfrac{\\% \\Delta Q_D}{\\% \\Delta P}\\). Calculate \\(\\% \\Delta Q_D = \\dfrac{{{Q2}}-{{Q1}}}{{{Q1}}} \\times 100\\).",
        "type": "info"
      },
      {
        "label": "% change in Qd",
        "content": "\\(\\% \\Delta Q_D = \\dfrac{{{Q2}}-{{Q1}}}{{{Q1}}} \\times 100\\)%. Enter as a decimal (e.g. −0.2 for −20%).",
        "type": "input",
        "answer": "({{Q2}} - {{Q1}}) / {{Q1}}",
        "tolerance": 0.005,
        "unit": ""
      },
      {
        "label": "|PED|",
        "content": "\\(|\\text{PED}| = \\left|\\dfrac{\\%\\Delta Q_D}{\\%\\Delta P}\\right|\\). Enter the absolute value.",
        "type": "input",
        "answer": "abs(({{Q2}} - {{Q1}}) / {{Q1}}) / abs(({{P2}} - {{P1}}) / {{P1}})",
        "tolerance": 0.05,
        "unit": ""
      }
    ],
    "mark_scheme_template": "\\(\\%\\Delta Q = \\dfrac{{{Q2-Q1}}}{{{Q1}}} \\approx {{round((Q2-Q1)/Q1*100,1)}}\\%\\); \\(\\%\\Delta P = \\dfrac{{{P2-P1}}}{{{P1}}} \\approx {{round((P2-P1)/P1*100,1)}}\\%\\); \\(|\\text{PED}| \\approx {{round(answer,2)}}\\)",
    "hints": ["PED = (%ΔQd) ÷ (%ΔP)", "PED is usually negative for normal goods — take absolute value."],
    "marks": 4
  },
  {
    "id": "econ_2_2_ord_001",
    "subject": "economics",
    "topic": "2",
    "subtopic": "2.2",
    "type": "ordering",
    "difficulty": "core",
    "title": "AD-AS Analysis Steps",
    "tags": ["macroeconomics", "AD-AS", "analysis method"],
    "stem_template": "Arrange the following steps for analysing the effect of a demand-side shock using the AD-AS model in the CORRECT ORDER.",
    "params": {},
    "items": [
      "Identify the new equilibrium (price level and real output)",
      "Determine if the shock shifts AD, AS, or both",
      "Describe the economic context and the shock",
      "Show the shift on a labelled AD-AS diagram"
    ],
    "correct_order": [2, 1, 3, 0],
    "mark_scheme_template": "Correct order: (1) describe context/shock; (2) identify what shifts; (3) show shift on diagram; (4) identify new equilibrium.",
    "hints": ["Always start by identifying what is happening in the economy.", "Draw the diagram before reading off the new equilibrium."],
    "marks": 2
  }
],

"business.json": [
  {
    "id": "biz_4_1_ms_001",
    "subject": "business",
    "topic": "4",
    "subtopic": "4.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Marketing Mix (4Ps)",
    "tags": ["marketing", "4Ps", "marketing mix"],
    "stem_template": "Which of the following are elements of the Marketing Mix (4Ps)? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Product", "correct": True},
      {"text": "People", "correct": False},
      {"text": "Price", "correct": True},
      {"text": "Place (distribution)", "correct": True},
      {"text": "Promotion", "correct": True},
      {"text": "Process", "correct": False}
    ],
    "mark_scheme_template": "4Ps: Product, Price, Place, Promotion. People and Process are part of the extended 7Ps (services marketing) but not the core 4Ps.",
    "hints": ["4Ps = Product, Price, Place, Promotion.", "7Ps adds People, Process, Physical evidence."],
    "marks": 2
  },
  {
    "id": "biz_3_1_ms_001",
    "subject": "business",
    "topic": "3",
    "subtopic": "3.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Break-Even Analysis",
    "tags": ["finance", "break-even", "fixed costs", "variable costs"],
    "stem_template": "Which of the following statements about break-even analysis are TRUE? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "At break-even, total revenue equals total costs", "correct": True},
      {"text": "Above break-even output, the firm makes a loss", "correct": False},
      {"text": "Fixed costs do not change with output level", "correct": True},
      {"text": "Break-even output = Fixed Costs ÷ Contribution per unit", "correct": True},
      {"text": "A lower selling price always reduces the break-even quantity", "correct": False}
    ],
    "mark_scheme_template": "TRUE: TR=TC at break-even; FC constant; BEQ=FC÷(P-VC). FALSE: above BEQ = profit (not loss); lower price reduces contribution per unit → INCREASES BEQ.",
    "hints": ["Break-even: no profit, no loss.", "Contribution per unit = Selling price - Variable cost per unit."],
    "marks": 2
  },
  {
    "id": "biz_2_1_ms_001",
    "subject": "business",
    "topic": "2",
    "subtopic": "2.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Organisational Structures",
    "tags": ["HR", "organisational structure", "hierarchy"],
    "stem_template": "Which of the following are TRUE about a TALL organisational structure? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "There are many levels of hierarchy", "correct": True},
      {"text": "Each manager has a wide span of control", "correct": False},
      {"text": "Communication from top to bottom may be slower", "correct": True},
      {"text": "It tends to be more bureaucratic", "correct": True},
      {"text": "It is better suited to creative, innovative firms", "correct": False}
    ],
    "mark_scheme_template": "Tall = many levels; NARROW span of control; slower vertical communication; more bureaucratic. FALSE: narrow (not wide) span; flat structures suit creative/innovative environments.",
    "hints": ["Tall = more levels, narrow span.", "Flat = fewer levels, wide span."],
    "marks": 2
  },
  {
    "id": "biz_3_3_ord_001",
    "subject": "business",
    "topic": "3",
    "subtopic": "3.3",
    "type": "ordering",
    "difficulty": "core",
    "title": "Investment Appraisal — Payback Period Steps",
    "tags": ["finance", "investment appraisal", "payback period"],
    "stem_template": "Arrange the following steps for calculating the PAYBACK PERIOD of an investment in the CORRECT ORDER.",
    "params": {},
    "items": [
      "Calculate cumulative cash flows year by year",
      "Identify the year when cumulative cash flow turns positive",
      "Identify the initial investment cost",
      "Calculate the exact payback month within the final year"
    ],
    "correct_order": [2, 0, 1, 3],
    "mark_scheme_template": "Correct order: (1) identify initial cost; (2) calculate cumulative CF; (3) find when CF turns positive; (4) calculate exact month within that year.",
    "hints": ["Start with initial cost (year 0).", "Payback month = remaining cost ÷ that year's CF × 12."],
    "marks": 2
  }
],

"computer_science.json": [
  {
    "id": "cs_4_1_ms_001",
    "subject": "computer_science",
    "topic": "4",
    "subtopic": "4.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Data Structure Properties",
    "tags": ["data structures", "arrays", "stacks", "queues"],
    "stem_template": "Which of the following are TRUE about a STACK data structure? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "Elements are added and removed from the same end", "correct": True},
      {"text": "It follows Last In, First Out (LIFO) ordering", "correct": True},
      {"text": "It is used in breadth-first search (BFS)", "correct": False},
      {"text": "The main operations are push and pop", "correct": True},
      {"text": "It follows First In, First Out (FIFO) ordering", "correct": False}
    ],
    "mark_scheme_template": "Stack: LIFO; push/pop from same end (top). NOT FIFO (that's a queue); NOT used in BFS (BFS uses a queue; DFS uses a stack).",
    "hints": ["Stack = LIFO (like a stack of plates).", "Queue = FIFO; Stack = LIFO."],
    "marks": 2
  },
  {
    "id": "cs_5_1_ms_001",
    "subject": "computer_science",
    "topic": "5",
    "subtopic": "5.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Algorithm Complexity",
    "tags": ["algorithms", "Big-O", "complexity"],
    "stem_template": "Which of the following statements about algorithm time complexity are TRUE? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "O(1) means constant time regardless of input size", "correct": True},
      {"text": "A bubble sort has worst-case complexity O(n²)", "correct": True},
      {"text": "O(log n) is slower than O(n) for large inputs", "correct": False},
      {"text": "Binary search has O(log n) time complexity", "correct": True},
      {"text": "O(n!) algorithms scale well to large inputs", "correct": False}
    ],
    "mark_scheme_template": "TRUE: O(1) constant; bubble sort O(n²); binary search O(log n). FALSE: O(log n) is FASTER than O(n); O(n!) is extremely slow (factorial growth — terrible for large n).",
    "hints": ["Order: O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2^n) < O(n!)", "Faster = fewer operations for large n."],
    "marks": 2
  },
  {
    "id": "cs_3_1_ms_001",
    "subject": "computer_science",
    "topic": "3",
    "subtopic": "3.1",
    "type": "multi_select",
    "difficulty": "core",
    "title": "Network Protocols",
    "tags": ["networks", "protocols", "TCP/IP", "HTTP"],
    "stem_template": "Which of the following are TRUE about the TCP/IP model? Select ALL that apply.",
    "params": {},
    "options_template": [
      {"text": "TCP provides reliable, ordered data delivery", "correct": True},
      {"text": "UDP is more reliable than TCP", "correct": False},
      {"text": "IP is responsible for addressing and routing packets", "correct": True},
      {"text": "HTTP operates at the application layer", "correct": True},
      {"text": "TCP performs handshaking before data transfer", "correct": True}
    ],
    "mark_scheme_template": "TCP: reliable, ordered, handshaked (3-way handshake). IP: addressing/routing. HTTP: application layer. FALSE: UDP is faster but LESS reliable (no error checking/retransmission).",
    "hints": ["TCP = reliable, slow; UDP = fast, unreliable.", "IP handles routing, TCP handles data integrity."],
    "marks": 2
  },
  {
    "id": "cs_2_1_match_001",
    "subject": "computer_science",
    "topic": "2",
    "subtopic": "2.1",
    "type": "matching",
    "difficulty": "core",
    "title": "Data Structures to Use Cases",
    "tags": ["data structures", "use cases", "matching"],
    "stem_template": "Match each data structure to its most appropriate use case.",
    "params": {},
    "left": [
      "Stack",
      "Queue",
      "Hash Table",
      "Binary Tree"
    ],
    "right": [
      "Printer job management (first come, first served)",
      "Undo/redo functionality in editors",
      "Hierarchical data (file system, expression parsing)",
      "Fast key-value lookup (O(1) average)"
    ],
    "correct_pairs": [[0, 1], [1, 0], [2, 3], [3, 2]],
    "mark_scheme_template": "Stack → Undo/redo; Queue → Printer jobs (FIFO); Hash Table → fast lookup; Binary Tree → hierarchical structure.",
    "hints": ["Stack: LIFO = undo/redo.", "Queue: FIFO = first in, first served."],
    "marks": 4
  },
  {
    "id": "cs_1_1_calc_001",
    "subject": "computer_science",
    "topic": "1",
    "subtopic": "1.1",
    "type": "calculation",
    "difficulty": "core",
    "title": "Binary to Decimal Conversion",
    "tags": ["binary", "number systems", "conversion"],
    "stem_template": "Convert the 8-bit binary number \\({{b7}}{{b6}}{{b5}}{{b4}}{{b3}}{{b2}}{{b1}}{{b0}}\\) to its decimal value.",
    "params": {
      "b7": {"type": "choice", "values": [0, 1]},
      "b6": {"type": "choice", "values": [0, 1]},
      "b5": {"type": "choice", "values": [0, 1]},
      "b4": {"type": "choice", "values": [0, 1]},
      "b3": {"type": "choice", "values": [0, 1]},
      "b2": {"type": "choice", "values": [0, 1]},
      "b1": {"type": "choice", "values": [0, 1]},
      "b0": {"type": "choice", "values": [0, 1]}
    },
    "answer_template": "{{b7}}*128 + {{b6}}*64 + {{b5}}*32 + {{b4}}*16 + {{b3}}*8 + {{b2}}*4 + {{b1}}*2 + {{b0}}*1",
    "steps_template": [
      {
        "label": "Identify place values",
        "content": "Binary positional values (right to left): 1, 2, 4, 8, 16, 32, 64, 128. Multiply each bit by its place value.",
        "type": "info"
      },
      {
        "label": "Calculate decimal value",
        "content": "\\({{b7}} \\times 128 + {{b6}} \\times 64 + {{b5}} \\times 32 + {{b4}} \\times 16 + {{b3}} \\times 8 + {{b2}} \\times 4 + {{b1}} \\times 2 + {{b0}} \\times 1 = ?\\)",
        "type": "input",
        "answer": "{{b7}}*128 + {{b6}}*64 + {{b5}}*32 + {{b4}}*16 + {{b3}}*8 + {{b2}}*4 + {{b1}}*2 + {{b0}}*1",
        "tolerance": 0,
        "unit": ""
      }
    ],
    "mark_scheme_template": "Decimal value = \\({{b7}} \\times 128 + {{b6}} \\times 64 + {{b5}} \\times 32 + {{b4}} \\times 16 + {{b3}} \\times 8 + {{b2}} \\times 4 + {{b1}} \\times 2 + {{b0}} \\times 1 = {{answer}}\\)",
    "hints": ["Work from left to right: bit 7 = 128, bit 0 = 1.", "Only add place values where the bit is 1."],
    "marks": 2
  }
],

}  # END NEW_TEMPLATES


def append_templates(filename, new_items):
    path = TMPL_DIR / filename
    if not path.exists():
        print(f"SKIP: {filename} not found")
        return 0

    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR loading {filename}: {e}")
        return 0

    if not isinstance(existing, list):
        print(f"SKIP: {filename} is not a JSON array")
        return 0

    existing_ids = {item.get("id") for item in existing if isinstance(item, dict)}
    added = 0
    for item in new_items:
        if item.get("id") not in existing_ids:
            existing.append(item)
            added += 1
        else:
            print(f"  SKIP duplicate id: {item.get('id')}")

    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  {filename}: added {added} templates (total: {len(existing)})")
    return added


if __name__ == "__main__":
    total_added = 0
    for fname, items in NEW_TEMPLATES.items():
        print(f"\nProcessing {fname}...")
        total_added += append_templates(fname, items)
    print(f"\n✓ Done. Total new templates added: {total_added}")
