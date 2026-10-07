"""Compare the RD-1 and RD-6a declarations with the approved text of docs/spec/readings-defaults.md 6.2 and 6.7.

Every declaration of the spec's 6.2 block is compared, not only the theorems (review B2): the structure, every
definition with its body (`AchievesU`, `fillDoc`, `fillNamesFree`, `normsShaped`, `WellFormedND`, ...), and every
theorem from `theorem <name>` to the proof's `:=`. The list is read from the spec block itself, so a declaration
added to the spec is compared without editing this file. Whitespace and doc comments are ignored. The Lean
compiler checks elaboration, and lean/audit.py checks proof dependencies. A declaration that differs from the
approved text must be listed in PENDING with the reason, and is reported as pending the statement re-review; an
unlisted difference, a missing or repeated declaration, or a PENDING entry that no longer differs fails.

RD-6a is checked the same way against 6.7 in `SupExtra.lean`. 6.7 also states RD-6b's declarations (LATER_6A); each
is compared once it is in the file and listed as not built before.
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
SOURCE_6A = ROOT / "lean/VE/Readings/SupExtra.lean"
# 6.7's declarations by kind, RD-6b's included.
EXPECTED_6A = {"theorem": 7, "def": 3, "structure": 0}
PENDING_6A: dict[str, str] = {
    "superpose_all_extra": "added hypothesis (hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) Q); the approved "
                           "form is false (fixture X1 of lean/VE/Readings/SupExtraExamples.lean)",
}
# The one edit each RD-6a pending declaration makes to the approved text: (approved fragment, Lean fragment). Any other
# difference fails, so a pending declaration cannot drift further unnoticed.
EDITS_6A: dict[str, tuple[str, str]] = {
    "superpose_all_extra": ("(hq : Transfers.{u} D Q Q') (hcf :",
                            "(hq : Transfers.{u} D Q Q') (hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) Q) (hcf :"),
}
# 6.7's RD-6b declarations, built by RD-6b in the same file.
LATER_6A = {"fill_transfers", "nd_superpose_conflict_free", "nd_superpose_all"}
KINDS = ("theorem", "def", "structure")
# A Lean name runs to the first space or bracket, so `x'` or `A.x` is not read as `x` or `A`.
START = re.compile(rf"^({'|'.join(KINDS)}) ([\w'!?.]+)", re.M)
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


def block(start: str, stop: str) -> dict[tuple[str, str], list[str]]:
    section = SPEC.read_text().split(start, 1)[1].split(stop, 1)[0]
    return declarations(section.split("```lean", 1)[1].split("```", 1)[0], statements_only=True)


def approved() -> dict[tuple[str, str], list[str]]:
    return block("### 6.2 RD-1", "### 6.3")


def approved_6a() -> dict[tuple[str, str], list[str]]:
    return block("### 6.7 RD-6a", "## 7.")


def compare(batch: str, spec: dict, source: Path, expected: dict, pending_ok: dict[str, str],
            later: set[str], edits: dict[str, tuple[str, str]] | None = None) -> tuple[list[str], int]:
    """Print the batch's report; return its errors and its number of exact declarations."""
    lean = declarations(source.read_text(), statements_only=True)
    errors, pending, waiting = [], [], []
    counts = {kind: sum(1 for k, _ in spec if k == kind) for kind in KINDS}
    if counts != expected:
        errors.append(f"expected {expected} approved {batch} declarations, found {counts}")
    names = {name for _, name in spec}
    for name in sorted((set(pending_ok) | later) - names):
        errors.append(f"{name}: listed as pending or later but not an approved declaration")
    for (kind, name), texts in sorted(spec.items()):
        if len(texts) != 1:
            errors.append(f"{name}: the spec block states it {len(texts)} times")
            continue
        found = lean.get((kind, name), [])
        if not found and name in later:
            waiting.append(name)
            continue
        if len(found) != 1:
            errors.append(f"{name}: expected one Lean {kind}, found {len(found)}")
            continue
        if found[0] == texts[0]:
            if name in pending_ok:
                errors.append(f"{name}: listed as pending but matches the approved text")
        elif name in pending_ok and name in (edits or {}) and \
                found[0] != texts[0].replace(edits[name][0], edits[name][1], 1):
            errors.append(f"{name}: differs from the approved text by more than its pending edit\n"
                          f"  approved: {texts[0]}\n  Lean:     {found[0]}")
        elif name in pending_ok:
            pending.append(f"{name}: PENDING re-review: {pending_ok[name]}\n  approved: {texts[0]}\n  Lean:     {found[0]}")
        else:
            errors.append(f"{name}: {kind} differs\n  approved: {texts[0]}\n  Lean:     {found[0]}")
    theorems = sum(1 for k, name in spec if k == "theorem" and name not in waiting)
    print(f"checked {len(spec) - len(waiting)} approved {batch} declarations ({theorems} theorems)")
    for line in pending:
        print(line)
    if waiting:
        print(f"not built yet (a later batch): {', '.join(sorted(waiting))}")
    exact = len(spec) - len(pending) - len(waiting)
    if not errors:
        print(f"{batch} PASS: {exact} exact after whitespace normalization; {len(pending)} pending the statement "
              "re-review")
    return errors, exact


def main() -> int:
    errors, _ = compare("RD-1", approved(), SOURCE, EXPECTED, PENDING, set())
    errors_6a, _ = compare("RD-6a", approved_6a(), SOURCE_6A, EXPECTED_6A, PENDING_6A, LATER_6A, EDITS_6A)
    errors += errors_6a
    if errors:
        print("\n".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
