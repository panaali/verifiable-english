#!/usr/bin/env python3
"""Compare every declaration of spec 7.2 (docs/spec/defeasible.md) with lean/VE/Defaults/Wire.lean, token for token
after whitespace normalisation, with comments, docstrings and proofs removed. A spec declaration with no body (a
`def` or `theorem` the batch writes) must be a prefix of the built one up to its `:=`. Usage, from the repository
root, with another file as the optional argument (the model kind is on wip/df-1ad-model):

    python3 docs/defeasible/df-1ac/evidence/compare_statements.py [lean/VE/Defaults/Wire.lean]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HEAD = re.compile(r"^(theorem|def|structure|inductive) (\S+)")


def decls(text: str) -> dict[str, str]:
    text = re.sub(r"/-.*?-/", "", text, flags=re.S)
    out, name, buf = {}, None, []
    for line in text.splitlines() + [""]:
        line = re.sub(r"\s--.*$|^--.*$", "", line)
        m = HEAD.match(line)
        if m or not line.strip() or (line[:1].isalpha() and not line.startswith(("theorem", "def"))):
            if name:
                out[name] = " ".join(" ".join(buf).split())
            name, buf = (m.group(2), [line]) if m else (None, [])
        elif name:
            buf.append(line)
    return out


def statement(d: str) -> str:
    return d.split(" := by")[0].split(" := ⟨")[0] if d.startswith("theorem") else d


def main() -> int:
    spec = (ROOT / "docs/spec/defeasible.md").read_text()
    block = spec.split("### 7.2")[1].split("### 7.3")[0].split("```lean")[1].split("```")[0]
    want = decls(block)
    have = decls((ROOT / (sys.argv[1] if len(sys.argv) > 1 else "lean/VE/Defaults/Wire.lean")).read_text())
    bad = 0
    for name, s in want.items():
        h = have.get(name)
        ok = h is not None and (statement(h) == statement(s) or (":=" not in s and h.startswith(s + " :=")))
        bad += not ok
        print(("OK      " if ok else ("MISSING " if h is None else "DIFF    ")) + name)
    print(f"{len(want) - bad} OK, {bad} not OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
