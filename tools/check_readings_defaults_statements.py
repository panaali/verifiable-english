"""Compare the RD-1 and RD-2a declarations with the approved text of docs/spec/readings-defaults.md 6.2 and 6.3.

Every declaration of the spec's 6.2 block is compared, not only the theorems (review B2): the structure, every
definition with its body (`AchievesU`, `fillDoc`, `fillNamesFree`, `normsShaped`, `WellFormedND`, ...), and every
theorem from `theorem <name>` to the proof's `:=`. The list is read from the spec block itself, so a declaration
added to the spec is compared without editing this file. Whitespace and doc comments are ignored. The Lean
compiler checks elaboration, and lean/audit.py checks proof dependencies. A declaration that differs from the
approved text must be listed in PENDING with the reason, and is reported as pending the statement re-review; an
unlisted difference, a missing or repeated declaration, or a PENDING entry that no longer differs fails.

RD-2a's block (6.3) states some wire functions without a body (`ndText`, `admitND`, the replays: specified by their
docstrings and sections 3 to 5 of the spec); such a definition is compared up to its Lean body's `:=`. Its
declarations are found in the three files 6.1 places them in.
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


# RD-2a: spec 6.3, placed by 6.1 in the NormDefaults files (the UDoc lemmas) and `UnspecifiedWire.lean`.
SECTION_RD2A = ("### 6.3 RD-2a", "### 6.4")
SOURCES_RD2A = [ROOT / "lean/VE/NormDefaults/Wire.lean", ROOT / "lean/VE/NormDefaults/Report.lean",
                ROOT / "lean/VE/Readings/UnspecifiedWire.lean"]
EXPECTED_RD2A = {"theorem": 5, "def": 8, "structure": 3}
PENDING_RD2A: dict[str, str] = {}


def block_of(start: str, end: str) -> str:
    section = SPEC.read_text().split(start, 1)[1].split(end, 1)[0]
    return section.split("```lean", 1)[1].split("```", 1)[0]


def approved() -> dict[tuple[str, str], list[str]]:
    return declarations(block_of("### 6.2 RD-1", "### 6.3"), statements_only=True)


def approved_rd2a() -> dict[tuple[str, str], list[str]]:
    return declarations(block_of(*SECTION_RD2A), statements_only=True)


def lean_of(sources) -> dict[tuple[str, str], list[str]]:
    out: dict[tuple[str, str], list[str]] = {}
    for source in sources:
        for key, texts in declarations(Path(source).read_text(), statements_only=True).items():
            out.setdefault(key, []).extend(texts)
    return out


def compare(batch, spec, lean, expected, pending_table) -> tuple[list[str], list[str]]:
    """The errors and pending notes of one batch's approved declarations against the Lean ones."""
    errors, pending = [], []
    counts = {kind: sum(1 for k, _ in spec if k == kind) for kind in KINDS}
    if counts != expected:
        errors.append(f"expected {expected} approved {batch} declarations, found {counts}")
    names = {name for _, name in spec}
    for name in sorted(set(pending_table) - names):
        errors.append(f"{name}: listed as pending but not an approved declaration")
    for (kind, name), texts in sorted(spec.items()):
        if len(texts) != 1:
            errors.append(f"{name}: the spec block states it {len(texts)} times")
            continue
        found = lean.get((kind, name), [])
        if len(found) != 1:
            errors.append(f"{name}: expected one Lean {kind}, found {len(found)}")
            continue
        lean_text = found[0]
        if kind == "def" and ":=" not in texts[0]:  # stated without a body: the signature is compared
            lean_text = lean_text.split(" :=", 1)[0]
        if lean_text == texts[0]:
            if name in pending_table:
                errors.append(f"{name}: listed as pending but matches the approved text")
        elif name in pending_table:
            pending.append(f"{name}: PENDING re-review: {pending_table[name]}\n  approved: {texts[0]}\n  Lean:     {lean_text}")
        else:
            errors.append(f"{name}: {kind} differs\n  approved: {texts[0]}\n  Lean:     {lean_text}")
    return errors, pending


def main_rd2a() -> int:
    spec = approved_rd2a()
    errors, pending = compare("RD-2a", spec, lean_of(SOURCES_RD2A), EXPECTED_RD2A, PENDING_RD2A)
    counts = {kind: sum(1 for k, _ in spec if k == kind) for kind in KINDS}
    print(f"checked {len(spec)} approved RD-2a declarations ({counts['theorem']} theorems)")
    for line in pending:
        print(line)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"PASS: RD-2a {len(spec) - len(pending)} exact after whitespace normalization; "
          f"{len(pending)} pending the statement re-review")
    return 0


def main() -> int:
    spec = approved()
    errors, pending = compare("RD-1", spec, declarations(SOURCE.read_text(), statements_only=True), EXPECTED, PENDING)
    counts = {kind: sum(1 for k, _ in spec if k == kind) for kind in KINDS}
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
    sys.exit(max(main(), main_rd2a()))
