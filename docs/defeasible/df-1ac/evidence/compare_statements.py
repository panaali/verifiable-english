#!/usr/bin/env python3
"""Spec 7.2's declarations (docs/spec/defeasible.md) against a Lean file (default lean/VE/Defaults/Wire.lean), token for
token after whitespace normalisation, comments, docstrings and proofs removed; a spec declaration with no body must be
the built one up to its `:=`. Usage from the repository root: compare_statements.py [file]."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def decls(text: str) -> dict[str, str]:
    out, name, buf = {}, None, []
    for line in re.sub(r"/-.*?-/", "", text, flags=re.S).splitlines() + [""]:
        line = re.sub(r"(^|\s)--.*$", "", line)
        m = re.match(r"^(theorem|def|structure|inductive) (\S+)", line)
        if m or not line.strip() or (line[:1].isalpha() and not line.startswith(("theorem", "def"))):
            if name:
                out[name] = " ".join(" ".join(buf).split())
            name, buf = (m.group(2), [line]) if m else (None, [])
        elif name:
            buf.append(line)
    return out


cut = lambda d: d.split(" := by")[0].split(" := ⟨")[0] if d.startswith("theorem") else d
spec = (ROOT / "docs/spec/defeasible.md").read_text().split("### 7.2")[1].split("### 7.3")[0]
want = decls(spec.split("```lean")[1].split("```")[0])
have = decls((ROOT / (sys.argv[1] if len(sys.argv) > 1 else "lean/VE/Defaults/Wire.lean")).read_text())
bad = 0
for name, s in want.items():
    h = have.get(name)
    ok = h is not None and (cut(h) == cut(s) or (":=" not in s and h.startswith(s + " :=")))
    bad += not ok
    print(("OK      " if ok else "MISSING " if h is None else "DIFF    ") + name)
print(f"{len(want) - bad} OK, {bad} not OK")
