"""ap-3d statement gate: each theorem this item proves equals the specification's text, whitespace normalised.

    python3 docs/act-phrases/ap-3d/check_statements.py

Reads the theorem from docs/spec/act-phrases.md (section 6.3, 6.4 or 6.6; up to the next theorem, docstring, `def`,
`end` or fence; the spec's namespace prefix dropped from the name) and from its Lean file (up to its `:=`). Exit 1 on
any difference or a theorem missing on either side.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
# (theorem, spec section, the spec's namespace prefix, Lean file)
THEOREMS = [
    ("checkAuthorN_split", "### 6.3", "VE.NormDefaults.Wire.", "lean/VE/NormDefaults/Wire.lean"),
    ("checkAct_lexical", "### 6.4", "VE.Acts.Wire.", "lean/VE/Acts/Wire.lean"),
    ("checkAct_joined", "### 6.4", "VE.Acts.Wire.", "lean/VE/Acts/Wire.lean"),
    ("decodeElaboratedU_source", "### 6.4", "", "lean/VE/Acts/Decode.lean"),
    ("decodeElaboratedU_wellFormed", "### 6.4", "", "lean/VE/Acts/Decode.lean"),
    ("decodeElaboratedU_lexical", "### 6.4", "", "lean/VE/Acts/Decode.lean"),
    ("elaborate_identity", "### 6.6", "", "lean/VE/Acts/Elaborate.lean"),
]


def statement(text, name, ends):
    i = text.index(f"theorem {name} ")
    j = min(k for k in (text.find(e, i + 1) for e in ends) if k > 0)
    return " ".join(text[i:j].split())


def main():
    spec = (ROOT / "docs/spec/act-phrases.md").read_text()
    bad = []
    for name, section, prefix, path in THEOREMS:
        i = spec.index(section)
        part = spec[i:spec.index("\n### ", i + 1)].replace(f"theorem {prefix}{name} ", f"theorem {name} ")
        want = statement(part, name, ["\ntheorem", "\n/--", "\ndef ", "\nend ", "\n```"])
        have = statement((ROOT / path).read_text(), name, [" :=", "\n:="])
        print(("EQUAL " if want == have else "DIFF  ") + name)
        if want != have:
            print("  spec:", want, "\n  lean:", have)
            bad.append(name)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
