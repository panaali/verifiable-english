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
    ("SC-4 wire", "### 6.8", "### 6.9",
     [LEAN / "Readings/UnspecifiedWire.lean", LEAN / "Readings/SoftWire.lean"],
     {"theorem": 7, "def": 13, "structure": 3}, set()),
    ("SC-5 verdicts", "### 6.9", "### 6.10",
     [LEAN / "Readings/VerdictsWire.lean", LEAN / "Readings/SoftVerdicts.lean"],
     {"theorem": 13, "def": 11, "structure": 3}, set()),
    ("SC-6 layered kinds", "### 6.10", "### 6.11",
     [LEAN / "NormDefaults/LayeredAdmission.lean", LEAN / "NormDefaults/Admission.lean", LEAN / "NormDefaults/Run.lean"],
     {"theorem": 6, "def": 18, "structure": 2}, set()),
)


# Declarations whose build differs from the approved text by one exact edit the DRI signed after the bounded statement
# re-check (spec 11 item 11, plan SC-0; B4 of manage-agents/reviews/dri-signatures-qa-q2-rd-9.md, re-check PASS in
# manage-agents/reviews/rd-9-b4-recheck.md, signed in manage-agents/reviews/rd-9-dri-signatures-20261015.md item 3).
# The approved text with the edit applied must equal the Lean text exactly; any other difference fails.
B4 = "SIGNED by DRI 2026-10-15 (B4, bounded statement re-check PASS)"
SIGNED = {
    # Gains `(hN : N.D = b.D)`: the soft case types its situation vocabulary by `primeModel_valid`, which needs the
    # choice's `E` to be the request's, and `Environment` holds functions, so the signature `(b) (N)` cannot check it
    # at run time; every caller has the fact (`AdmittedSD.hN`, `AdmittedND.hN`), and no approved theorem states
    # `choiceLayeredG` (spec 12.24).
    "choiceLayeredG": (B4, ("(wfc : VE.NormDefaults.WellFormedU (choiceU N c) = true) :",
                            "(wfc : VE.NormDefaults.WellFormedU (choiceU N c) = true) (hN : N.D = b.D) :")),
    # Builds `free N.D` once (`let freeDoc`), as the route builds one document per request
    # (tests/test_readings_lean_sharing.py); the approved body builds it twice, through `decisionCount` and `freeU N`,
    # which is `asU N (free N.D).1` by definition, so the value is the same (spec 12.25).
    "ndTextWith": (B4, (":= ((reservedUnsaid N).map (s!\"InvalidInput: reserved name {·}\")).or <| "
                        "(ndDocTextG re (decisionCount (free N.D).1) (freeU N)).or",
                        ":= let freeDoc := free N.D ((reservedUnsaid N).map (s!\"InvalidInput: reserved name {·}\")).or "
                        "<| (ndDocTextG re (decisionCount freeDoc.1) (asU N freeDoc.1)).or")),
}


def signed_edits(approved: dict) -> tuple[list[str], list[str]]:
    """Apply each signed edit to its approved declaration in place. Returns the report lines and the errors: an edit
    that does not apply (its text is not in the approved declaration) is an error, so the list can only shrink."""
    lines, errors = [], []
    for name, (ruling, (before, after)) in SIGNED.items():
        for key in [key for key in approved if key[1] == name]:
            texts = approved[key]
            edited = [text.replace(before, after, 1) for text in texts]
            if len(texts) != 1 or edited == texts:
                errors.append(f"{name}: the signed edit does not apply to the approved text")
                continue
            approved[key] = edited
            lines.append(f"{name}: {ruling}: approved text with its one signed edit")
    return lines, errors


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
        signed, e = signed_edits(approved)
        errors.extend(e)
        e, _ = compare(title, approved, sources, counted, {}, set())
        errors.extend(e)
        for line in signed:
            print(line)
        if later:
            word = "unbuilt" if title.startswith("SC-1") else "not built yet"
            print(f"{title.split()[0]} {word}: {', '.join(sorted(later))}")
    if errors:
        print("\n".join(errors))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
