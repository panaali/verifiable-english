"""Plant each AR-3 fault, prove its named test fails, then restore the source (evidence/mutants.json).

Run from the checkout after `(cd lean && lake build)`: uv run python docs/arch/AR-3/seed_faults.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import nested_pytest  # noqa: E402  (the one builder of a nested pytest command)

RULE = "tools/gate_collection.py"
GATE = "tools/gate.py"
TESTS = "tests/test_gate_collection.py::"
CASES = [
    ("a deleted test file does not explain its tests", RULE,
     '        if status == "D":\n            return "its file is deleted"\n',
     '        if False:\n            return "its file is deleted"\n',
     TESTS + "test_the_diff_explains_a_deleted_or_reparametrised_test[deleted test file]"),
    ("a deleted test function does not explain its tests", RULE,
     "        if len(after) < len(before):\n",
     "        if False:\n",
     TESTS + "test_the_diff_explains_a_deleted_or_reparametrised_test[deleted test function]"),
    ("the parametrisation leaves out the module-level names its decorators use", RULE,
     "    pending = _names([*roots, *included.values()])\n",
     "    pending = set()\n",
     TESTS + "test_the_diff_explains_a_deleted_or_reparametrised_test[shrunk module list]"),
    ("a change anywhere in the test file explains a dropped test", RULE,
     '        if parametrisation(base, before) != parametrisation(head, after):\n',
     '        if True:\n',
     TESTS + "test_a_module_dropped_at_collection_fails_twice[import error]"),
    ("a record copied to another commit is used", RULE,
     '    if (record["format"], record["commit_sha"], record["tree_sha"]) != (FORMAT, commit, tree) \\\n',
     '    if record["format"] != FORMAT \\\n',
     TESTS + "test_a_record_retyped_or_rebound_is_ignored[commit other]"),
    ("the gate passes a base ID nothing explains", GATE,
     "    if refused:\n        result[\"failures\"].append({\"stage\": \"coverage\",\n",
     "    if False:\n        result[\"failures\"].append({\"stage\": \"coverage\",\n",
     TESTS + "test_the_gate_fails_on_every_unexplained_missing_id_and_lists_the_explained"),
    ("the gate collects the base even when it has a record", GATE,
     "    if found is not None:\n        collection[\"base_source\"]",
     "    if False:\n        collection[\"base_source\"]",
     TESTS + "test_the_gate_takes_the_base_record_and_collects_only_without_one"),
    ("a full gate does not record its collection", GATE,
     "                head_ids = collection[\"collected\"]\n",
     "                head_ids = None\n",
     "tests/test_gate_rerun.py::test_a_full_gate_records_its_tree_and_mode"),
]


def main() -> None:
    records = []
    for name, relative, before, after, test in CASES:
        path = ROOT / relative
        original = path.read_text()
        if original.count(before) != 1:
            raise RuntimeError(f"expected one mutation site for {name}")
        try:
            path.write_text(original.replace(before, after, 1))
            run = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", test]), cwd=ROOT,
                                 env=nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1"),
                                 capture_output=True, text=True, check=False)
        finally:
            path.write_text(original)
        output = run.stdout + run.stderr
        if run.returncode == 0 or "1 failed" not in output:
            raise RuntimeError(f"{name}: expected a test failure, got {run.returncode}: {output[-1000:]}")
        records.append({"bug": name, "file": relative, "test": test,
                        "exit_code": run.returncode, "failure_excerpt": output[-1200:]})
    evidence = ROOT / "docs/arch/AR-3/evidence/mutants.json"
    evidence.write_text(json.dumps(records, indent=2) + "\n")
    print(f"{len(records)} seeded faults caught")


if __name__ == "__main__":
    main()
