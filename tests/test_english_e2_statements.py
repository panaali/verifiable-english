"""The twelve E2 statements of spec 5.5 are checked by Lean, not by reading Lean source as text (review, checklist 11)."""

import re

from tools import check_english_e2_statements as statements


# Each mutant changes one approved statement: a flipped value, a dropped conjunct, a changed conclusion.
MUTANTS = {
    "policy_iff_no_failure": ("L.policyOk E O = true ↔", "L.policyOk E O = false ↔"),
    "admitRequest_ok": ("obs = obligations rs ∧ ", ""),
    "codeClasses_total": ("isSome = true", "isSome = false"),
    "decode_encode": ("= some A", "= none"),
}


def test_lean_proves_every_approved_statement_and_refuses_each_mutant():
    approved = statements.approved()
    assert [name for name, _ in approved] == [
        "policy_iff_no_failure", "policy_selection", "admitRequest_ok", "admitRequest_exact", "admitRequest_policy",
        "translateRequest_policy", "grammarFault_none", "overlayCheck_constants", "checkRequest_some",
        "sensesRequest_policy", "codeClasses_total", "decode_encode"]
    mutated = []
    for name, text in approved:
        if name in MUTANTS:
            old, new = MUTANTS[name]
            assert old in text, name
            text = text.replace(old, new, 1)
        mutated.append((name, text))
    # One Lean run for both: the mutants are renamed so that the file holds the approved text and its mutants.
    source = statements.lean_file(approved + [(f"{name}_mutant", text) for name, text in mutated
                                              if name in MUTANTS])
    source = re.sub(r"@(\w+)_mutant\b", r"@\1", source)
    lines = source.splitlines()
    starts = sorted((i, line.split()[1].removeprefix("approved_")) for i, line in enumerate(lines, 1)
                    if line.startswith("theorem approved_"))
    errors = statements.lean_errors_of(source)
    failed = {int(m[1]) for m in re.finditer(r"\.lean:(\d+):\d+: error", errors)}
    # Each error is charged to the theorem whose text it falls in.
    failing = {next(name for start, name in reversed(starts) if start <= line) for line in failed}
    assert failing == {f"{n}_mutant" for n in MUTANTS}, errors[-4000:]
