"""ap-3db statement gate: the theorems of spec 6.4 this item reaches keep the specification's text.

    python3 docs/act-phrases/ap-3db/check_statements.py

Compares section 6.4 of docs/spec/act-phrases.md with their Lean files, whitespace normalised, a theorem up to its `:=`.
Lean writes `readings_lexical_only` inside its namespace with `VE.Acts.Lexical.check`, so both sides drop the prefixes
`VE.Readings.Wire.` and `VE.Acts.` before they are compared. Exit 1 on any difference or a name missing on either side.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NAMES = {"decodeElaboratedU_source": "Acts/Decode.lean", "decodeElaboratedU_wellFormed": "Acts/Decode.lean",
         "decodeElaboratedU_lexical": "Acts/Decode.lean", "readings_lexical_only": "Readings/Wire.lean",
         "checkAct_lexical": "Acts/Wire.lean", "checkAct_joined": "Acts/Wire.lean"}


def statement(text, name, ends):
    i = text.index(f"{name} ")
    body = " ".join(text[i:min(k for k in (text.find(e, i + 1) for e in ends) if k > 0)].split())
    return body.replace("VE.Readings.Wire.", "").replace("VE.Acts.Wire.", "").replace("VE.Acts.", "")


def main():
    spec = (ROOT / "docs/spec/act-phrases.md").read_text()
    spec = spec[spec.index("### 6.4"):spec.index("\n### 6.5")]
    bad = []
    for name, path in NAMES.items():
        lean = (ROOT / "lean/VE" / path).read_text()
        want = statement(spec.replace("theorem VE.Readings.Wire.", "theorem ").replace("theorem VE.Acts.Wire.", "theorem "),
                         name, ["\ntheorem", "\n/--", "\n```", "\nend "])
        have = statement(lean, name, [" :=\n", " := by"])
        print(("EQUAL " if want == have else "DIFF  ") + name)
        if want != have:
            print("  spec:", want, "\n  lean:", have)
            bad.append(name)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
