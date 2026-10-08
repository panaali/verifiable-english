"""Prove the batch 17 ownership regressions fail on four seeded bugs.

Each source edit is restored before the next run, even if pytest fails to start.
Run from the repository root with the prebuilt native binaries.
"""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
PYTEST = Path(os.environ.get("VE_B17_PYTEST", "/tmp/ve-lf17-venv/bin/pytest"))
EVIDENCE = Path(os.environ.get("VE_B17_MUTANTS", "/tmp/ve-lf17-mutants.json"))

MUTANTS = (
    ("assist_found_without_replay", "ve/assist/session.py",
     'if proof is not None and self._lean_replays(proof, premises, conclusion):',
     'if proof is not None and proof.status == "Found":',
     "test_assist_decide_replays_found_in_lean"),
    ("entails_found_without_replay", "ve/assist/session.py",
     'return self._lean_replays(proof, premises, conclusion)',
     'return proof.status == "Found"',
     "test_assist_positive_entailment_requires_lean_replay"),
    ("assist_no_without_lean_witness", "ve/assist/session.py",
     'if self._lean_refutes(premises, conclusion, model):',
     'if model is not None:',
     "test_assist_negative_decision_requires_lean_countermodel"),
    ("cedar_python_verdict", "ve/adapters/cedar.py",
     'with pinned("lean"):', 'with pinned("python"):',
     "test_cedar_evaluates_each_request_under_lean"),
)


def run_test(test):
    proc = subprocess.run(
        [str(PYTEST), "-q", f"tests/test_b17_owner.py::{test}", "-x"],
        cwd=ROOT, env={**os.environ, "VE_NATIVE_PREBUILT": "1"},
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        timeout=120,
    )
    return {"exit_code": proc.returncode, "failed_test": f"FAILED tests/test_b17_owner.py::{test}" in proc.stdout,
            "output_tail": proc.stdout[-4000:]}


def main():
    entries = []
    for name, relative, old, new, test in MUTANTS:
        path = ROOT / relative
        original = path.read_bytes()
        before = hashlib.sha256(original).hexdigest()
        assert original.count(old.encode()) == 1, name
        try:
            path.write_bytes(original.replace(old.encode(), new.encode(), 1))
            mutant = run_test(test)
        finally:
            path.write_bytes(original)
        after = hashlib.sha256(path.read_bytes()).hexdigest()
        assert before == after, name
        restored = run_test(test)
        entries.append({"name": name, "file": relative, "test": test,
                        "source_sha256": before, "mutant": mutant, "restored": restored})
        assert mutant["exit_code"] != 0 and mutant["failed_test"], name
        assert restored["exit_code"] == 0, name
        print(name, "failed as expected; restored test passed", flush=True)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps({"mutants": entries}, indent=2) + "\n")


if __name__ == "__main__":
    main()
