"""ap-3c statement gate: each 6.6 theorem Elaborate.lean proves equals draft 2's text, whitespace normalised.

    python3 docs/act-phrases/ap-3c/check_statements.py

Reads the theorem's text from docs/spec/act-phrases.md section 6.6 (up to the next theorem, docstring or fence) and
from lean/VE/Acts/Elaborate.lean (up to its `:=`). Exit 1 on any difference or a theorem missing on either side.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
THEOREMS = ["elaborateMap_fst", "elaborate_wellFormed", "elaborate_one_reading", "elaborate_unspec"]


def statement(text, name, ends):
    i = text.index(f"theorem {name} ")
    j = min(k for k in (text.find(e, i + 1) for e in ends) if k > 0)
    return " ".join(text[i:j].split())


def main():
    spec = (ROOT / "docs/spec/act-phrases.md").read_text()
    spec = spec[spec.index("### 6.6 Theorems"):spec.index("### 6.7")]
    src = (ROOT / "lean/VE/Acts/Elaborate.lean").read_text()
    bad = []
    for name in THEOREMS:
        want = statement(spec, name, ["\ntheorem", "\n/--", "\n```"])
        have = statement(src, name, [" :=", "\n:="])
        print(("EQUAL " if want == have else "DIFF  ") + name)
        if want != have:
            bad.append(name)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
