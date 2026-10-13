"""Temporarily plant each batch 16d bug, run the test meant to catch it, and save every result, caught or not."""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
LOCK = ROOT / "lean/checkers.lock"
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
CASES = [
    ("forged norm content accepted", "ve/document.py",
     '            require(same(unit["content"], authored["content"]))',
     '            pass  # seeded fault: norm content is not request-bound',
     "test_norm_content_is_bound_to_the_authored_node"),
    ("English fence lexicon omitted", "ve/document.py",
     '                case["lexicon"] = export(EnglishVocabulary(Environment(meta["environment"])))',
     '                pass  # seeded fault: no lexicon reaches the Lean English reader',
     "test_norm_defaults_readings_and_english_fence_are_decided_by_lean"),
    ("norm-defaults coverage omitted", "ve/document.py",
     '            answer["norm_defaults"] = {"gaps": gaps["gaps"], "findings": lines["findings"]}',
     '            pass  # seeded fault: the Lean report is dropped',
     "test_norm_defaults_coverage_uses_lean_report"),
    ("pending reading metadata skipped", "lean/VE/Service/Document.lean",
     '  let w2 ← Loader.compileSets E.rv E.profiles E.envId (units.map (·.id))\n'
     '    (Json.arr w2Sets.toArray) (python := true) (formula := formulaCheck E)\n'
     '    (modelRefused := some (unavailable "a distinguishing model the Lean model decoder refuses"))',
     '  let w2 : List (FrontSet × List Bool) := []  -- seeded fault: pending models are unchecked',
     "test_pending_reading_metadata_is_checked_by_lean"),
    ("coupled reading plan erased", "ve/document.py",
     '_reading_plan(active, meta.get("couplings", []))',
     '_reading_plan(active, [])  # seeded fault: coupling choices erased',
     "test_coupled_pilot_reading_plan_matches_prior_path"),
    ("pending labels refused", "lean/VE/Discourse/Loader.lean",
     '  let optional := if profiles.contains "readings@1" then ["labels"] else []',
     '  let optional : List String := []  -- seeded fault: pending labels refused',
     "test_labeled_pending_pilot_is_lean_decided"),
    # Review B1 and B2 (the norm unit roles, tests/test_b16d_norm_roles.py).
    ("quoted norm refused by the role table", "lean/VE/Norms/Admission.lean",
     '  else if kind.quoted then pure (.quoted content)\n',
     '',
     "test_b16d_norm_roles.py::test_quoted_norm_units_are_accepted_and_left_out_of_the_free_document"
     "[u0165.s01-attributed]"),
    ("Lean free document keeps a unit under an active set", "lean/VE/Service/Document.lean",
     'if setUnits.contains u.id || attached.contains u.id then none else some c',
     'if attached.contains u.id then none else some c',
     "test_b16d_norm_roles.py::test_norm_content_under_an_open_set_is_not_a_rule"),
    ("Lean free document keeps an attached unit", "lean/VE/Service/Document.lean",
     'if setUnits.contains u.id || attached.contains u.id then none else some c',
     'if setUnits.contains u.id then none else some c',
     "test_b16d_norm_roles.py::test_attached_norm_unit_is_left_out_of_the_free_document"),
    ("Python free document keeps a unit under an active set", "ve/document.py",
     'and "norm" in u["content"] and u["id"] not in held and u["id"] not in attached]',
     'and "norm" in u["content"] and u["id"] not in attached]',
     "test_b16d_norm_roles.py::test_norm_content_under_an_open_set_claims_no_coverage"),
    ("Python free document keeps an attached unit", "ve/document.py",
     'and "norm" in u["content"] and u["id"] not in held and u["id"] not in attached]',
     'and "norm" in u["content"] and u["id"] not in held]',
     "test_b16d_norm_roles.py::test_attached_norm_unit_is_left_out_of_the_free_document"),
]


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
                built = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean",
                                       capture_output=True, text=True, check=False)
                if built.returncode:
                    raise RuntimeError((built.stdout + built.stderr)[-1500:])
                pinned = json.loads(LOCK.read_text())
                pinned["ve_service"] = sorted(set(pinned["ve_service"]) |
                                              {hashlib.sha256(SERVICE.read_bytes()).hexdigest()})
                LOCK.write_text(json.dumps(pinned, indent=2) + "\n")
            env = {**os.environ, "VE_NATIVE_PREBUILT": "1", "UV_CACHE_DIR": "/tmp/uv-b16d-cache"}
            target = f"tests/{test}" if "::" in test else f"tests/test_b16d_document.py::{test}"
            done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:xdist", target], cwd=ROOT,
                                  env=env, capture_output=True, text=True, check=False)
        finally:
            source.write_text(original)
            LOCK.write_text(lock)
            if lean:
                built = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean",
                                       capture_output=True, text=True, check=False)
                if built.returncode:
                    raise RuntimeError((built.stdout + built.stderr)[-1500:])
        output = done.stdout + done.stderr
        caught = done.returncode != 0 and "1 failed" in output
        records.append({"bug": bug, "test": test, "exit_code": done.returncode, "caught": caught,
                        "failure_excerpt": output[-1800:]})
        print(f"{bug}: {test} {'failed as expected' if caught else 'PASSED: the fault survived'}", flush=True)
    path = Path(__file__).resolve().parent / "evidence/mutants.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    main()
