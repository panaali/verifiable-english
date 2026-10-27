#!/usr/bin/env python3
"""A spec section's declarations (docs/spec/defeasible.md; default 7.2) against a Lean file (default
lean/VE/Defaults/Wire.lean), token for token after whitespace normalisation, comments, docstrings and proofs removed; a
spec declaration with no body must be the built one up to its `:=`. Usage from the repository root:
compare_statements.py [file [section]], e.g. compare_statements.py lean/VE/Defaults/Meaning.lean 7.3 (df-2)."""
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
section = sys.argv[2] if len(sys.argv) > 2 else "7.2"
spec = (ROOT / "docs/spec/defeasible.md").read_text().split("### " + section + " ")[1].split("\n### ")[0]
want = decls(spec.split("```lean")[1].split("```")[0])
have = decls((ROOT / (sys.argv[1] if len(sys.argv) > 1 else "lean/VE/Defaults/Wire.lean")).read_text())
bad = 0
for name, s in want.items():
    h = have.get(name)
    ok = h is not None and (cut(h) == cut(s) or (":=" not in s and h.startswith(s + " :=")))
    bad += not ok
    print(("OK      " if ok else "MISSING " if h is None else "DIFF    ") + name)
print(f"{len(want) - bad} OK, {bad} not OK")
