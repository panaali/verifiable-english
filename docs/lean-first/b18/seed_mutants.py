"""Prove the batch 18 regressions fail on seeded bugs, one per behaviour the batch claims.

    uv run python docs/lean-first/b18/seed_mutants.py OUT_JSON [--lean LEAN_JSON]

Each Python mutant edits one changed file, runs the test that must catch it, restores the file (even if
pytest fails to start) and runs the test again, which must pass. `--lean` merges the Lean mutants, which need
a rebuild and a temporary pin and were run by hand (their record says how). Run from the repository root
with the native builds of this checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]

# (name, file, text, mutant text, test)
MUTANTS = (
    ("model_encoding_keyed_by_claim", "ve/backends/lean_runner.py",
     "    entry = _MODELS.get(id(model))\n    if entry is not None and entry[0] is model:\n",
     "    entry = _MODELS.get(id(model)) or next((e for e in _MODELS.values() if e[0].model_id == model.model_id), None)\n"
     "    if entry is not None:\n",
     "tests/test_stage2_evaluation.py::test_a_cached_model_encoding_never_stands_for_another_model"),
    ("duplicate_error_class", "ve/errors.py",
     "class ResourceLimit(VEError):",
     "class CheckerUnavailable(VEError):\n    code = \"CheckerUnavailable\"\n\n\nclass ResourceLimit(VEError):",
     "tests/test_relay.py::test_each_code_has_exactly_one_class_in_ve_errors"),
    ("python_authority_returns", "ve/evaluate.py",
     "    return owned(\"evaluate\", lambda: _evaluate_lean(env, case))",
     "    if __import__(\"os\").environ.get(\"VE_AUTHORITY\") == \"python\":\n"
     "        return _evaluate_validated(formulas, model, max_evaluations=max_evaluations,\n"
     "                                   max_trace_nodes=max_trace_nodes, trace=trace)\n"
     "    return owned(\"evaluate\", lambda: _evaluate_lean(env, case))",
     "tests/test_stage2_dispatch.py::test_no_setting_selects_an_authority"),
    ("limit_read_under_another_name", "ve/limits.py",
     "MAX_DEPTH = _STATED[\"max_depth\"]", "MAX_DEPTH = _STATED[\"max_nodes\"]",
     "tests/test_lean_service.py::test_handshake"),
    ("explanation_rows_outside_the_tree", "ve/evaluate.py",
     "    if position != len(rows):\n", "    if False:\n",
     "tests/test_metered_lean.py::test_explanation_rows_must_be_exactly_one_tree"),
    ("metered_answer_kind_unbound", "ve/backends/lean_runner.py",
     "    if row[\"status\"] == \"ok\" and set(row) != METERED_FIELDS[case[\"kind\"]]:\n",
     "    if False:\n",
     "tests/test_metered_lean.py::test_a_metered_answer_of_the_other_kind_is_no_answer"),
    ("countermodel_route_reads_display_blocks", "ve/search.py",
     "request = {\"id\": \"countermodel\", \"environment\": background_environment(env), **soft_case(env),",
     "request = {\"id\": \"countermodel\", \"environment\": env.to_dict(), **soft_case(env),",
     "tests/test_model_environment.py::test_search_status_and_comparison_answer_as_the_base_did"),
)


def run_test(test: str) -> dict:
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", test],
                          cwd=ROOT, env={**os.environ, "VE_NATIVE_PREBUILT": "1"},
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return {"exit_code": proc.returncode, "failed": "FAILED" in proc.stdout or " failed" in proc.stdout,
            "output_tail": proc.stdout[-1500:]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--lean", type=Path, help="the hand-run Lean mutants' record to merge")
    args = parser.parse_args()
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
        assert hashlib.sha256(path.read_bytes()).hexdigest() == before, name
        restored = run_test(test)
        entries.append({"name": name, "language": "Python", "file": relative, "test": test,
                        "source_sha256": before, "mutant": mutant, "restored": restored})
        assert mutant["exit_code"] != 0 and mutant["failed"], (name, mutant["output_tail"])
        assert restored["exit_code"] == 0, (name, restored["output_tail"])
        print(name, "failed as expected; restored test passed", flush=True)
    if args.lean:
        entries += json.loads(args.lean.read_text())["mutants"]
    args.out.write_text(json.dumps({"mutants": entries}, indent=1) + "\n")


if __name__ == "__main__":
    main()
