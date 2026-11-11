#!/usr/bin/env python3
"""ap-5 statement gate: each item of spec section 8's Lean block (each `structure`, `def`, `theorem` and docstring) is
in lean/VE/Acts/Specialise.lean unchanged after whitespace normalisation. Run from the repository root; exit 1 on a
difference. `python3 docs/act-phrases/ap-5/check_statements.py`"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = (ROOT / "docs/spec/act-phrases.md").read_text()
block = spec.split("## 8. AP-5: Lean statements", 1)[1].split("```lean", 1)[1].split("```", 1)[0]
norm = lambda s: " ".join(s.split())
src = norm((ROOT / "lean/VE/Acts/Specialise.lean").read_text())
items = [i.strip() for i in re.split(r"\n(?=structure |def |theorem |/--)", "\n" + block) if i.strip()]
bad = [i for i in items if norm(i) not in src]
for i in items:
    print("DIFF" if i in bad else "OK  ", norm(i)[:100])
print(f"{len(items) - len(bad)} of {len(items)} items verbatim")
sys.exit(1 if bad or not items else 0)
