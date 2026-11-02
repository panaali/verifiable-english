"""me-7 statement gate: each declaration of spec 7's Lean block appears in Stats.lean, whitespace and comments normalised.

Run from the checkout root: `python3 docs/math-evidence/me-7/evidence/check_statements.py`; exit 1 on any difference.
"""
import re
import sys

spec = open("docs/spec/math-evidence.md").read()
section = spec[spec.index("## 7. Statistics (ME-7)"):spec.index("## 8. Consistency")]
start = section.index("```lean") + len("```lean")
block = section[start:section.index("```", start)]


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"--[^\n]*", "", text)).strip()


lean = norm(open("lean/VE/Calc/Stats.lean").read())
parts = [norm(re.sub(r"/--.*?-/\s*", "", p, flags=re.S))
         for p in re.split(r"\n(?=(?:/--|def |theorem |instance |inductive ))", block.strip())]
parts = [p for p in parts if p]
missing = [p for p in parts if p not in lean]
for p in missing:
    print("DIFF:", p[:160])
print(f"{len(parts) - len(missing)} of {len(parts)} spec 7 declarations appear verbatim (whitespace and comments "
      "normalised) in Stats.lean")
sys.exit(1 if missing else 0)
