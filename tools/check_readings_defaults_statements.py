"""Compare the RD-1 theorem statements with the approved text of docs/spec/readings-defaults.md 6.2.

Whitespace is ignored; every binder, hypothesis and conclusion is compared, from `theorem <name>` to the
proof's `:=`. The Lean compiler checks elaboration, and lean/audit.py checks proof dependencies. A statement
that differs from the approved text must be listed in PENDING with the reason, and is reported as pending
the statement re-review; an unlisted difference, a missing theorem, or a PENDING entry that no longer differs
fails.
"""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/readings-defaults.md"
SOURCE = ROOT / "lean/VE/Readings/Unspecified.lean"
EXPECTED = 10
# Statements changed in the build, each awaiting the targeted statement re-review (PLAN-EXPAND2 rule 10).
PENDING = {
    "attached_fillDoc": "adds (hs : singlyAttached N.D = true): without it the lists can differ in order "
                        "(fixture F-ND11 in lean/VE/Readings/UnspecifiedExamples.lean)",
}
# A line that starts the next declaration of the spec block.
NEXT = re.compile(r"^(?:(?:theorem|def|structure|end)\b|/--)", re.M)


def normal(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def approved_statements() -> dict[str, str]:
    section = SPEC.read_text().split("### 6.2 RD-1", 1)[1].split("### 6.3", 1)[0]
    block = section.split("```lean", 1)[1].split("```", 1)[0]
    out = {}
    for start in re.finditer(r"^theorem (\w+)\b", block, re.M):
        nxt = NEXT.search(block, start.end())
        out[start[1]] = normal(block[start.start():nxt.start() if nxt else len(block)])
    return out


def lean_statement(source: str, name: str) -> list[str]:
    found = re.finditer(rf"^theorem {re.escape(name)}\b([\s\S]*?):=", source, re.M)
    return [normal(f"theorem {name}{m[1]}") for m in found]


def main() -> int:
    approved = approved_statements()
    source = SOURCE.read_text()
    errors, pending = [], []
    if len(approved) != EXPECTED:
        errors.append(f"expected {EXPECTED} approved RD-1 statements, found {len(approved)}")
    for name in sorted(set(PENDING) - set(approved)):
        errors.append(f"{name}: listed as pending but not an approved statement")
    for name, text in approved.items():
        found = lean_statement(source, name)
        if len(found) != 1:
            errors.append(f"{name}: expected one Lean declaration, found {len(found)}")
            continue
        if found[0] == text:
            if name in PENDING:
                errors.append(f"{name}: listed as pending but matches the approved text")
        elif name in PENDING:
            pending.append(f"{name}: PENDING re-review: {PENDING[name]}\n  approved: {text}\n  Lean:     {found[0]}")
        else:
            errors.append(f"{name}: statement differs\n  approved: {text}\n  Lean:     {found[0]}")
    print(f"checked {len(approved)} approved RD-1 statements")
    for line in pending:
        print(line)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"PASS: {len(approved) - len(pending)} exact after whitespace normalization; "
          f"{len(pending)} pending the statement re-review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
