"""Statement gate of ap-1d: each theorem it proves equals docs/spec/act-phrases.md 4.3, whitespace normalised.

    python3 docs/act-phrases/ap-1d/statements.py

A theorem's statement runs from `theorem <name>` to the `:=` that ends it (the spec's have no `:=`, so theirs ends
at the next declaration, `end` or code fence); `Accepts` is compared whole, to its blank line. Exit 1 when one
differs.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
NAMES = ["Accepts", "check_spec", "check_no_clause", "fixedOk_unique"]
HEAD = r"(?:theorem|def) {}\b"


def spec_statement(text: str, name: str) -> str:
    block = text[text.index("### 4.3 Theorems"):text.index("### 4.4")]
    start = re.search(HEAD.format(name), block).start()
    if block.startswith("def", start):
        return " ".join(block[start:block.index("\n\n", start)].split())
    end = re.compile(r"\n(?:theorem |def |end |/-[-!]|```)").search(block, start + 1).start()
    return " ".join(block[start:end].split())


def lean_statement(text: str, name: str) -> str:
    start = re.search(HEAD.format(name), text).start()
    if text.startswith("def", start):
        return " ".join(text[start:text.index("\n\n", start)].split())
    end = re.compile(r" :=(?: by)?\n").search(text, start).start()
    return " ".join(text[start:end].split())


def main() -> None:
    spec = (ROOT / "docs/spec/act-phrases.md").read_text()
    lean = (ROOT / "lean/VE/Acts/LexicalProofs.lean").read_text()
    bad = [n for n in NAMES if spec_statement(spec, n) != lean_statement(lean, n)]
    for n in NAMES:
        print("DIFFERS" if n in bad else "EQUAL  ", n)
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
