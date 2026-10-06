"""Compare the twelve added E2 theorem statements with the approved section 5.5 text.

Whitespace is ignored; every binder, hypothesis and conclusion is compared. The
Lean compiler checks elaboration, and lean/audit.py checks proof dependencies.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/english-lean-e2.md"
SOURCE = ROOT / "lean/VE/EnglishGrammar"


def normal(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    section = SPEC.read_text().split("### 5.5 The statements", 1)[1].split("### 5.6", 1)[0]
    block = section.split("```lean", 1)[1].split("```", 1)[0]
    starts = list(re.finditer(r"^theorem (\w+)\b", block, re.M))
    if len(starts) != 12:
        print(f"expected twelve approved E2 statements, found {len(starts)}")
        return 1
    sources = {path: path.read_text() for path in SOURCE.rglob("*.lean")}
    errors = []
    for index, start in enumerate(starts):
        name = start[1]
        end = starts[index + 1].start() if index + 1 < len(starts) else len(block)
        approved = normal(block[start.start():end])
        pattern = re.compile(rf"\btheorem {re.escape(name)}\b[\s\S]*?:=\s*by\b")
        found = [(path, match) for path, content in sources.items() for match in pattern.finditer(content)]
        if len(found) != 1:
            errors.append(f"{name}: expected one Lean declaration, found {len(found)}")
            continue
        actual = normal(re.split(r":=\s*by\b", found[0][1].group(), maxsplit=1)[0])
        if actual != approved:
            errors.append(f"{name}: statement differs\n  approved: {approved}\n  Lean:     {actual}")
    print(f"checked {len(starts)} approved E2 statements")
    if errors:
        print("\n".join(errors))
        return 1
    print("PASS: exact statement text after whitespace normalization")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
