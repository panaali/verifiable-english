"""Compare the RD-1 declarations with the approved text of docs/spec/readings-defaults.md 6.2.

Every declaration of the spec's 6.2 block is compared, not only the theorems (review B2): the structure, every
definition with its body (`AchievesU`, `fillDoc`, `fillNamesFree`, `normsShaped`, `WellFormedND`, ...), and every
theorem from `theorem <name>` to the proof's `:=`. The list is read from the spec block itself, so a declaration
added to the spec is compared without editing this file. Whitespace and doc comments are ignored. The Lean
compiler checks elaboration, and lean/audit.py checks proof dependencies. A declaration that differs from the
approved text must be listed in PENDING with the reason, and is reported as pending the statement re-review; an
unlisted difference, a missing or repeated declaration, or a PENDING entry that no longer differs fails.
"""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/readings-defaults.md"
SOURCE = ROOT / "lean/VE/Readings/Unspecified.lean"
# The approved 6.2 block's declarations by kind; a change in the spec's count is a change to review.
EXPECTED = {"theorem": 10, "def": 20, "structure": 1}
# Declarations changed in the build, each awaiting the targeted statement re-review (PLAN-EXPAND2 rule 10). Empty:
# `attached_fillDoc`'s added `singlyAttached` hypothesis was approved by the DRI on 2026-10-07 and is in 6.2.
PENDING: dict[str, str] = {}
KINDS = ("theorem", "def", "structure")
START = re.compile(rf"^({'|'.join(KINDS)}) (\w+)\b", re.M)
# A line that ends a declaration: a blank line, or a line at column 0 that starts another command or a comment.
STOP = re.compile(r"^(?:\s*$|(?:theorem|lemma|def|structure|abbrev|instance|end|namespace|section|open|universe|"
                  r"variable|private|protected|noncomputable|@\[|/--|/-!|--|#))", re.M)


def normal(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def declarations(text: str, statements_only: bool) -> dict[tuple[str, str], list[str]]:
    """Every `theorem`, `def` or `structure` at column 0 of `text`: (kind, name) → its normalized texts. A theorem
    is cut at its proof's `:=` when `statements_only`."""
    out: dict[tuple[str, str], list[str]] = {}
    for start in START.finditer(text):
        line_end = text.find("\n", start.end())
        stop = STOP.search(text, len(text) if line_end < 0 else line_end + 1)
        body = text[start.start():stop.start() if stop else len(text)]
        if statements_only and start[1] == "theorem":
            body = body.split(":=", 1)[0]
        out.setdefault((start[1], start[2]), []).append(normal(body))
    return out


def approved() -> dict[tuple[str, str], list[str]]:
    section = SPEC.read_text().split("### 6.2 RD-1", 1)[1].split("### 6.3", 1)[0]
    block = section.split("```lean", 1)[1].split("```", 1)[0]
    return declarations(block, statements_only=True)


def main() -> int:
    spec = approved()
    lean = declarations(SOURCE.read_text(), statements_only=True)
    errors, pending = [], []
    counts = {kind: sum(1 for k, _ in spec if k == kind) for kind in KINDS}
    if counts != EXPECTED:
        errors.append(f"expected {EXPECTED} approved RD-1 declarations, found {counts}")
    names = {name for _, name in spec}
    for name in sorted(set(PENDING) - names):
        errors.append(f"{name}: listed as pending but not an approved declaration")
    for (kind, name), texts in sorted(spec.items()):
        if len(texts) != 1:
            errors.append(f"{name}: the spec block states it {len(texts)} times")
            continue
        found = lean.get((kind, name), [])
        if len(found) != 1:
            errors.append(f"{name}: expected one Lean {kind}, found {len(found)}")
            continue
        if found[0] == texts[0]:
            if name in PENDING:
                errors.append(f"{name}: listed as pending but matches the approved text")
        elif name in PENDING:
            pending.append(f"{name}: PENDING re-review: {PENDING[name]}\n  approved: {texts[0]}\n  Lean:     {found[0]}")
        else:
            errors.append(f"{name}: {kind} differs\n  approved: {texts[0]}\n  Lean:     {found[0]}")
    print(f"checked {len(spec)} approved RD-1 declarations ({counts['theorem']} theorems)")
    for line in pending:
        print(line)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"PASS: {len(spec) - len(pending)} exact after whitespace normalization; "
          f"{len(pending)} pending the statement re-review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
