"""Compare the implemented RD-9 declarations against the approved Lean blocks of docs/spec/rd-9-soft-chain.md 6.

Each section of 6 is one batch's block (SC-1's 6.3 to 6.5, SC-2's 6.6, SC-3's 6.7, SC-4's 6.8, SC-5's 6.9, SC-6's
6.10), compared with the files 6.1 places it in by `check_readings_defaults_statements.compare`: every declaration
of the block, a theorem up to its proof's `:=`, a definition stated without a body up to its signature.

A section's last field names approved declarations that are not built yet. They are reported as not built ("SC-1
unbuilt: ..." for SC-1, whose acceptance probe greps for the word), and a marker whose declaration exists fails the
check, so the list can only shrink. Every SC-1 declaration is built, so SC-1 names none.
"""

from pathlib import Path
import re

from check_readings_defaults_statements import compare, declarations, lean_of


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/rd-9-soft-chain.md"
LEAN = ROOT / "lean/VE"
SECTIONS = (
    ("SC-1 entailment", "### 6.3", "### 6.4", [LEAN / "NormDefaults/LayeredEntail.lean"],
     {"theorem": 9, "def": 5, "structure": 0}, set()),
    ("SC-1 documents", "### 6.4", "### 6.5", [LEAN / "Readings/SoftDefaults.lean"],
     {"theorem": 4, "def": 9, "structure": 0}, set()),
    ("SC-1 fold", "### 6.5", "### 6.6", [LEAN / "Readings/Verdicts.lean"],
     {"theorem": 14, "def": 7, "structure": 1}, set()),
    ("SC-2 separation", "### 6.6", "### 6.7", [LEAN / "Readings/SoftSeparate.lean"],
     {"theorem": 6, "def": 6, "structure": 0}, set()),
    ("SC-6 layered kinds", "### 6.10", "### 6.11",
     [LEAN / "NormDefaults/LayeredAdmission.lean", LEAN / "NormDefaults/Admission.lean", LEAN / "NormDefaults/Run.lean"],
     {"theorem": 6, "def": 18, "structure": 2}, set()),
)


def approved_block(start: str, stop: str) -> dict:
    section = SPEC.read_text().split(start, 1)[1].split(stop, 1)[0]
    code = section.split("```lean", 1)[1].split("```", 1)[0]
    # Line comments (`-- proved in the stub`) are dropped; a docstring's `/--` is kept, so it still ends the
    # declaration before it.
    return declarations(re.sub(r"(?<![/-])--[^\n]*", "", code), statements_only=True)


def main(sections=SECTIONS) -> int:
    errors = []
    for title, start, stop, sources, expected, later in sections:
        approved = approved_block(start, stop)
        lean = lean_of(sources)
        for name in sorted(later):
            keys = [key for key in approved if key[1] == name]
            if not keys or any(key in lean for key in keys):
                errors.append(f"{name}: not-built marker is stale")
            for key in keys:
                approved.pop(key)
        counted = dict(expected)
        for kind in counted:
            counted[kind] -= sum(1 for name in later for key in [(kind, name)] if key in approved_block(start, stop))
        e, _ = compare(title, approved, sources, counted, {}, set())
        errors.extend(e)
        if later:
            word = "unbuilt" if title.startswith("SC-1") else "not built yet"
            print(f"{title.split()[0]} {word}: {', '.join(sorted(later))}")
    if errors:
        print("\n".join(errors))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
