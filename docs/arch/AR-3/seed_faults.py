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
    ("the diff's deletion of a function authorises its removal without a trailer", RULE,
     "        removal = next((removal for removal in removals if removal.covers(nodeid)), None)\n",
     "        removal = next((removal for removal in removals if removal.covers(nodeid)), None) or (\n"
     "            Removal(nodeid, label, '') if label != UNLABELLED else None)\n",
     TESTS + "test_a_dropped_test_fails_without_a_trailer_and_passes_with_one[deleted test function]"),
    ("a trailer covers any ID that starts with its target", RULE,
     '        return nodeid == self.target or nodeid.startswith((self.target + "::", self.target + "["))\n',
     "        return nodeid.startswith(self.target)\n",
     TESTS + "test_what_a_trailer_covers[tests/a.py::test_f]"),
    ("a trailer naming a test the head still collects is not stale", RULE,
     "        if still is not None:\n",
     "        if False:\n",
     TESTS + "test_a_trailer_naming_a_collected_test_is_stale[its file]"),
    ("a trailer without a reason records a removal", RULE,
     "    if not separator or not target.strip() or target != target.strip() or not reason.strip():\n",
     "    if not separator or not target.strip() or target != target.strip():\n",
     TESTS + "test_a_trailer_is_a_target_and_a_reason[no reason]"),
    ("trailers before the base count", RULE,
     '               f"{base}..{head}", "--"], cwd=root, env=env).stdout.decode()\n',
     '               head, "--"], cwd=root, env=env).stdout.decode()\n',
     TESTS + "test_git_reads_the_trailers_of_base_to_head_only"),
    ("a deleted test function is not labelled", RULE,
     "        if len(after) < len(before):\n",
     "        if False:\n",
     TESTS + "test_a_dropped_test_fails_without_a_trailer_and_passes_with_one[deleted test function]"),
    ("the parametrisation leaves out the module-level names its decorators use", RULE,
     "    pending = _names([*roots, *included.values()])\n",
     "    pending = set()\n",
     TESTS + "test_a_dropped_test_fails_without_a_trailer_and_passes_with_one[shrunk module list]"),
    ("a record copied to another commit is used", RULE,
     '    if (record["format"], record["commit_sha"], record["tree_sha"]) != (FORMAT, commit, tree) \\\n',
     '    if record["format"] != FORMAT \\\n',
     TESTS + "test_a_record_retyped_or_rebound_is_ignored[commit other]"),
    ("the gate passes a base ID no trailer names", GATE,
     "    if verdict.failed():\n        result[\"failures\"].append({\"stage\": \"coverage\",\n",
     "    if False:\n        result[\"failures\"].append({\"stage\": \"coverage\",\n",
     TESTS + "test_the_gate_fails_on_every_missing_id_no_trailer_names_and_lists_the_recorded"),
    ("the gate passes a stale trailer", GATE,
     "    if verdict.failed():\n        result[\"failures\"].append({\"stage\": \"coverage\",\n",
     "    if verdict.refused:\n        result[\"failures\"].append({\"stage\": \"coverage\",\n",
     TESTS + "test_a_stale_or_malformed_trailer_fails_the_gate[stale]"),
    ("the gate collects the base even when it has a record", GATE,
     "    if found is not None:\n        collection[\"base_source\"]",
     "    if False:\n        collection[\"base_source\"]",
     TESTS + "test_the_gate_takes_the_base_record_and_collects_only_without_one"),
    ("a merge stops on a conflict over the retired baseline", "tools/regen_generated.py",
     "    retired = [path for path in unmerged if path in RETIRED]\n",
     "    retired = []\n",
     "tests/test_regen_generated.py::test_resolve_takes_the_deletion_of_a_retired_file"),
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
