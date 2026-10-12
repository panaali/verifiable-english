"""Plant each fault in the picked readings-route relay fix, prove its named tests fail, then restore.

    PATH=~/.elan/bin:$PATH VE_NATIVE_PREBUILT=1 uv run python docs/arch/AR-9/seed_relay_faults.py \
        > docs/arch/AR-9/evidence/relay-mutants.json

The fix is `c88e4012` from `infra/oom-rootcause`, cherry-picked unchanged so the pre-review relay
mutation gate passes (REPORT.md, "Relay gate"). One fault per thing it refuses, in each language it
changes: Lean's response shape (the decoder `ve_response_decode` and the schema it renders) and the
Python schema compiler that reads the rendered `x-unique-strings`. The Lean tests rebuild the two
executables themselves (`lean_build`); after restoring, `lake build` puts the pinned build back.
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

SHAPE = "tests/test_lean_service_schema.py::test_readings_route_shape_agrees_with_lean_on_empty_names_and_repeated_over"
GATE = "tests/test_relay_mutation_gate.py::test_readings_route_refuses_empty_labels_targets_and_repeated_over_names"
ROUTE = "lean/ResponseShape/Schemas/ReadingsRoute.lean"
CASES = [
    ("Lean accepts an empty fill label", "empty label", "lean",
     [(ROUTE, 'closed [("label", n [str, .minLength 1]),', 'closed [("label", str),')],
     [SHAPE]),
    ("Lean accepts repeated over names", "repeated over", "lean",
     [(ROUTE, '("over", n [ref "common.json#/$defs/strings", .uniqueStrings])',
       '("over", ref "common.json#/$defs/strings")')],
     [SHAPE]),
    ("Python's x-unique-strings check accepts repeated names", "repeated over", "python",
     [("ve/backends/service_schema.py", "                    len(value) != len(set(value)):",
       "                    False:")],
     ["tests/test_lean_service_schema.py::test_unique_string_lists_refuse_duplicate_rule_names", GATE]),
]


def run(test: str) -> dict:
    done = subprocess.run(nested_pytest.command(["-q", "-x", "-p", "no:cacheprovider", test]), cwd=ROOT,
                          env=nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1"),
                          capture_output=True, text=True)
    return {"test": test, "exit_code": done.returncode, "failure_excerpt": done.stdout[-1500:]}


def main() -> int:
    records = []
    for bug, claim, language, edits, tests in CASES:
        originals = {path: (ROOT / path).read_text() for path, _, _ in edits}
        try:
            for path, before, after in edits:
                text = (ROOT / path).read_text()
                if text.count(before) != 1:
                    raise RuntimeError(f"expected one mutation site for {bug} in {path}")
                (ROOT / path).write_text(text.replace(before, after, 1))
            records.append({"bug": bug, "claim": claim, "language": language, "file": edits[0][0],
                            "test": tests[0], "files": sorted(originals),
                            "runs": [run(test) for test in tests]})
        finally:
            for path, text in originals.items():
                (ROOT / path).write_text(text)
    subprocess.run(["lake", "build"], cwd=ROOT / "lean", check=True, capture_output=True)
    restored = [run(test) for _, _, _, _, tests in CASES for test in tests]
    print(json.dumps({"mutants": records, "restored": [{"test": r["test"], "exit_code": r["exit_code"]}
                                                      for r in restored]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
