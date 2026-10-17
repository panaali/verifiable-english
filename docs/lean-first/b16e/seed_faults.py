"""Temporarily plant each batch 16e fault, run the test meant to catch it, and save every result, caught or not.

    python docs/lean-first/b16e/seed_faults.py

A Lean fault is built into `ve_service` and pinned for the run; the source, the lock and the build are restored
after each fault. `evidence/mutants.json` keeps the file, the test, its exit code and a failure excerpt.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
LOCK = ROOT / "lean/checkers.lock"
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
TESTS = "tests/test_b16e_rights_document.py"
LEAN = "lean/VE/Service/Document.lean"
CASES = [
    # Lean: the document mode's rights composition.
    ("rights statuses not read from the rights route", LEAN,
     '    if u.status == "CHECKED" && (R.bind fun R => R.opens.lookup u.id) == some true then {',
     '    if false then {',
     "test_rights_corpus_sample_is_lean_decided_with_the_prior_outcome"),
    ("norm meaning ids bound to the rights environment instead of E'''", LEAN,
     '    ← VE.Route.Wire.environmentId extendedProfiles extended, rules⟩',
     '    E.envId, rules⟩',
     "test_rights_corpus_sample_is_lean_decided_with_the_prior_outcome"),
    ("rights block accepted under a norm unit", LEAN,
     '    unless kind matches .rights _ do throw "UnsupportedProfile: rights@0 is required"\n',
     '',
     "test_a_norm_unit_holding_a_rights_block_is_refused_by_lean"),
    ("claim graph of a rights document decided without the rights admission", LEAN,
     'def RightsDoc.unowned : List String := ["reading_sets", "couplings", "graph"]',
     'def RightsDoc.unowned : List String := ["reading_sets", "couplings"]',
     "test_the_unowned_parts_of_a_rights_document_keep_the_retained_path[graph]"),
    ("nulls in rights content refused", LEAN,
     '  !(rights && k == "content") && hasNull 257 v',
     '  hasNull 257 v',
     "test_rights_corpus_sample_is_lean_decided_with_the_prior_outcome"),
    ("soft-norms owned without rights", LEAN,
     'def ownedBeneath (listed : List String) (p : String) : Bool := p == "soft-norms@0" && listed.contains "rights@0"',
     'def ownedBeneath (listed : List String) (p : String) : Bool := p == "soft-norms@0"',
     "test_soft_norms_is_owned_only_beneath_rights"),
    # Python: binding, construction and the retained path's containers.
    ("rights block content not bound to the request", "ve/document.py",
     '            require(rights and same(unit["content"], authored["content"]))',
     '            require(rights)  # seeded fault',
     "test_a_forged_but_typed_field_is_refused_by_the_binding[right]"),
    ("soft norm content not bound to the request", "ve/document.py",
     '    if type(answer) is not dict or type(authored) is not dict or set(answer) != set(authored):\n        return False',
     '    return True  # seeded fault',
     "test_a_forged_but_typed_field_is_refused_by_the_binding[norm]"),
    ("meaning ids bound to one environment for every kind", "ve/document.py",
     '    return env if "rights@0" in env.profiles and type(kind) is str and kind in _RIGHTS_KINDS else formula_env',
     '    return env  # seeded fault',
     "test_rights_corpus_sample_is_lean_decided_with_the_prior_outcome"),
    ("composed profile lines dropped on the Lean path", "ve/document.py",
     '        answer.update(_profile_lines(doc, answer["residual"], rights_report))',
     '        pass  # seeded fault',
     "test_rights_corpus_sample_is_lean_decided_with_the_prior_outcome"),
    ("measurement counts a rejected valid case as decided", "docs/lean-first/b16e/measure.py",
     '        if "raised" not in old or unavailable(old):\n            raise RuntimeError(f"Lean rejected',
     '        if False:\n            raise RuntimeError(f"Lean rejected',
     "test_f2_probe_a_seeded_rejection_of_a_valid_case_fails_the_measurement"),
    ("measurement accepts a report that differs from the prior path", "docs/lean-first/b16e/measure.py",
     '        if old != new:\n            raise RuntimeError(f"Lean\'s accepted report',
     '        if False:\n            raise RuntimeError(f"Lean\'s accepted report',
     "test_f2_a_forged_accepted_report_fails_the_measurement"),
    ("retained path crashes on a non-string unit id", "ve/document.py",
     '    return (type(unit.get("content")) is dict and not (type(uid) is str and uid in exclude) and',
     '    return (type(unit.get("content")) is dict and uid not in exclude and',
     "test_a_non_string_unit_id_is_the_unit_checks_diagnostic_on_both_paths"),
    ("retained path's soft rule fails on a null alterable", "ve/softnorms.py",
     "tuple(raw.get('alterable') or ())",
     "tuple(raw.get('alterable', ()))",
     "test_a_null_alterable_party_list_is_read_as_absent_on_both_paths"),
    ("retained path's rights container needs a holder guard", "ve/rights.py",
     '                        ["top"] if guard is None else guard)}',
     '                        body["guard"])}',
     "test_a_right_without_a_holder_guard_is_built_on_both_paths"),
]


def build() -> None:
    built = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", capture_output=True, text=True,
                           check=False)
    if built.returncode:
        raise RuntimeError((built.stdout + built.stderr)[-1500:])


def main() -> None:
    records = []
    for bug, relative, before, after, test in CASES:
        source = ROOT / relative
        original = source.read_text()
        lock = LOCK.read_text()
        lean = relative.endswith(".lean")
        assert original.count(before) == 1, bug
        try:
            source.write_text(original.replace(before, after, 1))
            if lean:
                build()
                pinned = json.loads(LOCK.read_text())
                pinned["ve_service"] = sorted(set(pinned["ve_service"]) |
                                              {hashlib.sha256(SERVICE.read_bytes()).hexdigest()})
                LOCK.write_text(json.dumps(pinned, indent=2) + "\n")
            env = {**os.environ, "VE_NATIVE_PREBUILT": "1"}
            done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:xdist", "-p", "no:cacheprovider",
                                   f"{TESTS}::{test}"], cwd=ROOT, env=env, capture_output=True, text=True,
                                  check=False)
        finally:
            source.write_text(original)
            LOCK.write_text(lock)
            if lean:
                build()
        output = done.stdout + done.stderr
        caught = done.returncode == 1 and " failed" in output
        records.append({"bug": bug, "file": relative, "test": f"{TESTS}::{test}", "exit_code": done.returncode,
                        "caught": caught, "failure_excerpt": output[-1500:]})
        print(f"{bug}: {test} {'failed as expected' if caught else 'PASSED: the fault survived'}", flush=True)
    path = Path(__file__).resolve().parent / "evidence/mutants.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    main()
