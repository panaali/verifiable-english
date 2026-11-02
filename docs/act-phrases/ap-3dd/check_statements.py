"""ap-3dd statement gate: `readAs`, `IntendedActs` and the two theorems equal the specification's text.

    python3 docs/act-phrases/ap-3dd/check_statements.py

Compares section 6.6 of docs/spec/act-phrases.md with lean/VE/Acts/Faithful.lean, whitespace normalised: a definition
up to the next docstring or blank line, a theorem up to its `:=` in Lean and the next item in the spec. Exit 1 on any
difference or a name missing on either side.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NAMES = ["def readAs", "def IntendedActs", "theorem elaborate_faithful", "theorem Decode.decodeElaboratedU_faithful"]


def statement(text, name, ends):
    i = text.index(f"{name} ")
    return " ".join(text[i:min(k for k in (text.find(e, i + 1) for e in ends) if k > 0)].split())


def main():
    spec = (ROOT / "docs/spec/act-phrases.md").read_text()
    spec = spec[spec.index("### 6.6"):spec.index("\n### 6.7")]
    lean = (ROOT / "lean/VE/Acts/Faithful.lean").read_text()
    bad = []
    for name in NAMES:
        ends = ["\n/--", "\n\n"] if name.startswith("def") else [" :=", "\n:="]
        want = statement(spec, name, ["\ntheorem", "\n/--", "\ndef ", "\n\n", "\n```"])
        have = statement(lean, name, ends)
        print(("EQUAL " if want == have else "DIFF  ") + name)
        if want != have:
            print("  spec:", want, "\n  lean:", have)
            bad.append(name)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
