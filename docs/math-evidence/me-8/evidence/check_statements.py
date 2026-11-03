"""me-8 statement gate: each declaration of spec 8.1's Lean block appears in Interval.lean or Consistency.lean,
whitespace and comments normalised (an opaque definition: its signature, followed by its body).

Run from the checkout root: `python3 docs/math-evidence/me-8/evidence/check_statements.py`; exit 1 on any difference.
"""
import re
import sys

spec = open("docs/spec/math-evidence.md").read()
section = spec[spec.index("### 8.1 Consistency"):spec.index("### 8.2 Identities")]
start = section.index("```lean") + len("```lean")
block = section[start:section.index("```", start)]


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"--[^\n]*", "", text)).strip()


lean = norm(open("lean/VE/Calc/Interval.lean").read() + open("lean/VE/Calc/Consistency.lean").read())
parts = [norm(re.sub(r"/--.*?-/\s*", "", p, flags=re.S))
         for p in re.split(r"\n(?=(?:/--|def |theorem |instance |inductive ))", block.strip())]
parts = [p for p in parts if p]
missing = [p for p in parts if p not in lean]
for p in missing:
    print("DIFF:", p[:160])
print(f"{len(parts) - len(missing)} of {len(parts)} spec 8.1 declarations appear verbatim (whitespace and comments "
      "normalised) in Interval.lean and Consistency.lean")
sys.exit(1 if missing else 0)
