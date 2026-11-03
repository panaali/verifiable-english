#!/usr/bin/env python3
"""df-5ab's four declarations in lean/VE/Defaults/Zone.lean against spec 7.5 (docs/spec/defeasible.md), word for word
after whitespace normalisation (`forcedAll_sound` at its DRI-signed wording, already in 7.5). Run from the repository
root: python3 docs/defeasible/df-5ab/evidence/check_statements.py > docs/defeasible/df-5ab/evidence/statements.out"""
from pathlib import Path

spec = Path("docs/spec/defeasible.md").read_text()
zone = Path("lean/VE/Defaults/Zone.lean").read_text()


def header(kind: str, name: str, src: str) -> str:
    """The declaration up to its body, whitespace-normalised."""
    i = src.index(f"{kind} {name} ")
    text = src[i:src.index("\n\n", i)]
    return " ".join(text.split(":= by")[0].split(" :=\n")[0].split())


bad = 0
for kind, name in [("def", "forcedAllOf"), ("theorem", "forcedAll_sound"), ("theorem", "defaultCompletion_below"),
                   ("theorem", "forced_everywhere")]:
    s, z = header(kind, name, spec), header(kind, name, zone)
    ok = s == z
    bad += not ok
    print(f"{name}: {'OK' if ok else 'DIFFERS'}")
print("ALL OK" if not bad else f"{bad} DIFFER")
