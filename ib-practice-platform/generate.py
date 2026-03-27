#!/usr/bin/env python3
"""
IB Practice Platform — Question Generator
==========================================
Reads template JSON files from data/templates/ and produces a questions.json
file that the platform loads automatically.

Usage:
  python generate.py                          # Generate from all templates, 3 instances each
  python generate.py --count 5                # 5 instances per template
  python generate.py --subject math_aa        # Only Math AA
  python generate.py --subject physics --topic A  # Only Physics topic A
  python generate.py --difficulty core         # Only core difficulty
  python generate.py --seed 42                # Reproducible randomization
  python generate.py --output my_questions.json
"""

import json
import os
import sys
import random
import math
import ast
import argparse
import operator
from datetime import datetime, UTC
from pathlib import Path

# ─── Helpers ───────────────────────────────────────────────────────────

def load_templates(template_dir):
    """Load all template JSON files from the given directory."""
    templates = []
    for f in sorted(Path(template_dir).glob("*.json")):
        try:
            data = None
            load_error = None
            for enc in ("utf-8", "utf-8-sig", "cp1252"):
                try:
                    with open(f, "r", encoding=enc) as fh:
                        data = json.load(fh)
                    break
                except Exception as e:
                    load_error = e

            if data is None:
                raise load_error

            if isinstance(data, list):
                templates.extend(data)
            elif isinstance(data, dict) and "templates" in data:
                templates.extend(data["templates"])
            else:
                templates.append(data)
        except Exception as e:
            print(f"WARNING: Failed to load {f}: {e}", file=sys.stderr)
    return templates


def sample_param(spec):
    """Sample a random value for a parameter specification."""
    ptype = spec.get("type", "int")

    if ptype == "int":
        lo, hi = spec.get("min", 1), spec.get("max", 10)
        exclude = set(spec.get("exclude", []))
        candidates = [x for x in range(lo, hi + 1) if x not in exclude]
        if not candidates:
            return lo
        return random.choice(candidates)

    elif ptype == "float":
        lo, hi = spec.get("min", 0.0), spec.get("max", 1.0)
        dp = spec.get("dp", 2)
        val = random.uniform(lo, hi)
        return round(val, dp)

    elif ptype == "choice":
        values = spec.get("values", [0])
        return random.choice(values)

    elif ptype == "bool":
        return random.choice([True, False])

    else:
        return spec.get("default", 0)


def safe_eval(expr, params):
    """Safely evaluate a math expression using AST parsing (no eval)."""
    SAFE_FUNCS = {
        "abs": abs, "round": round, "int": int, "float": float,
        "pi": math.pi, "e": math.e,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "exp": math.exp, "pow": pow, "floor": math.floor, "ceil": math.ceil,
        "factorial": math.factorial, "comb": math.comb, "perm": math.perm,
        "gcd": math.gcd,
    }
    ns = {**SAFE_FUNCS, **{k: v for k, v in params.items()}}

    _OPS = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
        ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos,
    }

    def _eval_node(node):
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant: {node.value!r}")
        if isinstance(node, ast.Name):
            if node.id in ns:
                return ns[node.id]
            raise ValueError(f"Unknown name: {node.id}")
        if isinstance(node, ast.BinOp):
            op = _OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(_eval_node(node.left), _eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            op = _OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported unary: {type(node.op).__name__}")
            return op(_eval_node(node.operand))
        if isinstance(node, ast.Call):
            func = _eval_node(node.func)
            if not callable(func):
                raise ValueError(f"Not callable: {func}")
            args = [_eval_node(a) for a in node.args]
            return func(*args)
        if isinstance(node, ast.Attribute):
            # Allow math.X lookups
            val = _eval_node(node.value)
            if val is math:
                return getattr(math, node.attr)
            raise ValueError(f"Unsupported attribute access")
        raise ValueError(f"Unsupported node: {type(node).__name__}")

    try:
        tree = ast.parse(str(expr), mode='eval')
        result = _eval_node(tree)
        if isinstance(result, float):
            if abs(result) > 0.01:
                result = round(result, 4)
            else:
                result = round(result, 8)
        return result
    except Exception:
        return str(expr)


def substitute(template_str, params):
    """Replace {{param}} placeholders with actual values."""
    if not isinstance(template_str, str):
        return template_str
    result = template_str
    for key, val in params.items():
        result = result.replace("{{" + key + "}}", str(val))
    return result


def format_number(val):
    """Format a number nicely for display."""
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return f"{val:.4g}"
    return str(val)


# ─── Question Generation ──────────────────────────────────────────────

def generate_question(template, instance_num, params=None):
    """Generate one question instance from a template."""

    # Sample parameters
    if params is None:
        params = {}
        for pname, pspec in template.get("params", {}).items():
            params[pname] = sample_param(pspec)

    # Handle computed params (second pass)
    for pname, pspec in template.get("params", {}).items():
        if pspec.get("type") == "computed" and "formula" in pspec:
            params[pname] = safe_eval(pspec["formula"], params)

    # Compute answer
    answer_raw = None
    answer_template = template.get("answer_template", "")
    if answer_template:
        answer_raw = safe_eval(substitute(answer_template, params), params)

    params["answer"] = answer_raw if answer_raw is not None else ""

    # Generate distractors for MCQ
    distractors = []
    for dt in template.get("distractor_templates", []):
        d = safe_eval(substitute(dt, params), params)
        distractors.append(d)

    # Build the question object
    qid = f"{template['id']}_{instance_num:03d}"
    stem = substitute(template.get("stem_template", ""), params)
    mark_scheme = substitute(template.get("mark_scheme_template", ""), params)
    hints = [substitute(h, params) for h in template.get("hints", [])]

    q = {
        "id": qid,
        "subject": template.get("subject", ""),
        "topic": str(template.get("topic", "")),
        "subtopic": str(template.get("subtopic", "")),
        "type": template.get("type", "worked"),
        "difficulty": template.get("difficulty", "core"),
        "tags": template.get("tags", []),
        "title": substitute(template.get("title", ""), params),
        "stem": stem,
        "content": {},
        "mark_scheme": mark_scheme,
        "hints": hints,
        "marks": template.get("marks", 4),
    }

    # Build type-specific content
    qtype = template.get("type", "worked")

    if qtype == "mcq":
        # Build options from template or generate
        if "options_template" in template:
            options = []
            for opt in template["options_template"]:
                options.append({
                    "label": opt.get("label", ""),
                    "text": substitute(str(opt.get("text", "")), params),
                    "correct": opt.get("correct", False),
                })
            q["content"] = {"options": options, "shuffle": True}
        elif answer_raw is not None and distractors:
            options = [
                {"label": "A", "text": format_number(answer_raw), "correct": True}
            ]
            labels = ["B", "C", "D"]
            for i, d in enumerate(distractors[:3]):
                options.append({
                    "label": labels[i],
                    "text": format_number(d),
                    "correct": False,
                })
            # Pad if needed
            while len(options) < 4:
                fudge = answer_raw * random.choice([0.8, 1.2, 0.5, 1.5]) if isinstance(answer_raw, (int, float)) else "N/A"
                options.append({
                    "label": chr(65 + len(options)),
                    "text": format_number(fudge),
                    "correct": False,
                })
            q["content"] = {"options": options, "shuffle": True}

    elif qtype == "multi_select":
        if "options_template" in template:
            options = []
            for opt in template["options_template"]:
                options.append({
                    "text": substitute(str(opt.get("text", "")), params),
                    "correct": opt.get("correct", False),
                })
            q["content"] = {"options": options}

    elif qtype == "numerical":
        q["content"] = {
            "answer": answer_raw if answer_raw is not None else 0,
            "tolerance": template.get("tolerance", 0.01),
            "unit": substitute(template.get("unit", ""), params),
            "sf": template.get("sf", 3),
        }

    elif qtype == "worked":
        parts = template.get("parts_template", template.get("parts", []))
        if parts:
            q["content"] = {
                "instruction": "Solve by hand and check the mark scheme.",
                "parts": [
                    {
                        "label": substitute(p.get("label", ""), params),
                        "text": substitute(p.get("text", ""), params),
                        "marks": p.get("marks", 2),
                    }
                    for p in parts
                ],
            }
        else:
            q["content"] = {
                "instruction": "Solve by hand and check the mark scheme.",
            }

    elif qtype == "matching":
        q["content"] = {
            "left": [substitute(x, params) for x in template.get("left", [])],
            "right": [substitute(x, params) for x in template.get("right", [])],
            "correct_pairs": template.get("correct_pairs", []),
        }

    elif qtype == "ordering":
        q["content"] = {
            "items": [substitute(x, params) for x in template.get("items", [])],
            "correct_order": template.get("correct_order", []),
        }

    elif qtype == "calculation":
        steps = []
        for s in template.get("steps_template", template.get("steps", [])):
            step = {
                "label": substitute(s.get("label", ""), params),
                "content": substitute(s.get("content", ""), params),
                "type": s.get("type", "info"),
            }
            if s.get("type") == "input":
                step["answer"] = safe_eval(substitute(s.get("answer", "0"), params), params)
                step["tolerance"] = s.get("tolerance", 0.01)
                step["unit"] = s.get("unit", "")
            steps.append(step)
        q["content"] = {"steps": steps}

    elif qtype == "truth_table":
        q["content"] = template.get("truth_table_content", {})

    elif qtype == "chem_structure":
        if "options_template" in template:
            options = []
            for opt in template["options_template"]:
                options.append({
                    "label": opt.get("label", ""),
                    "smiles": substitute(opt.get("smiles", ""), params),
                    "name": substitute(opt.get("name", ""), params),
                    "correct": opt.get("correct", False),
                })
            q["content"] = {"options": options, "render_mode": "2d"}

    elif qtype == "graph_sketch":
        if "options_template" in template:
            options = []
            for opt in template["options_template"]:
                options.append({
                    "label": opt.get("label", ""),
                    "graph": opt.get("graph", {}),
                    "correct": opt.get("correct", False),
                })
            q["content"] = {"options": options}

    return q


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate IB practice questions from templates")
    parser.add_argument("--count", type=int, default=3, help="Instances per template (default: 3)")
    parser.add_argument("--subject", type=str, default=None, help="Filter by subject key")
    parser.add_argument("--topic", type=str, default=None, help="Filter by topic")
    parser.add_argument("--subtopic", type=str, default=None, help="Filter by subtopic")
    parser.add_argument("--difficulty", type=str, default=None, help="Filter by difficulty")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--output", type=str, default="questions.json", help="Output file path")
    parser.add_argument("--templates-dir", type=str, default=None, help="Templates directory")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # Find templates directory
    script_dir = Path(__file__).parent
    templates_dir = Path(args.templates_dir) if args.templates_dir else script_dir / "data" / "templates"

    if not templates_dir.exists():
        print(f"ERROR: Templates directory not found: {templates_dir}", file=sys.stderr)
        sys.exit(1)

    # Load templates
    templates = load_templates(templates_dir)
    print(f"Loaded {len(templates)} templates from {templates_dir}")

    # Filter
    if args.subject:
        templates = [t for t in templates if t.get("subject") == args.subject]
    if args.topic:
        templates = [t for t in templates if str(t.get("topic")) == args.topic]
    if args.subtopic:
        templates = [t for t in templates if str(t.get("subtopic")) == args.subtopic]
    if args.difficulty:
        templates = [t for t in templates if t.get("difficulty") == args.difficulty]

    print(f"Generating from {len(templates)} templates ({args.count} instances each)...")

    # Generate questions
    questions = []
    for tmpl in templates:
        for i in range(1, args.count + 1):
            try:
                q = generate_question(tmpl, i)
                questions.append(q)
            except Exception as e:
                print(f"WARNING: Failed to generate from {tmpl.get('id', '?')}: {e}", file=sys.stderr)

    # Shuffle
    random.shuffle(questions)

    # Output
    output = {
        "version": "1.0",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "generator": "ib-practice-generator",
        "template_count": len(templates),
        "question_count": len(questions),
        "questions": questions,
    }

    output_path = script_dir / args.output if not os.path.isabs(args.output) else Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(questions)} questions -> {output_path}")

    # Stats
    by_subject = {}
    by_type = {}
    for q in questions:
        subj = q.get("subject", "?")
        by_subject[subj] = by_subject.get(subj, 0) + 1
        qtype = q.get("type", "?")
        by_type[qtype] = by_type.get(qtype, 0) + 1

    print("\nBy subject:")
    for s, c in sorted(by_subject.items()):
        print(f"  {s}: {c}")
    print("\nBy type:")
    for t, c in sorted(by_type.items()):
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
