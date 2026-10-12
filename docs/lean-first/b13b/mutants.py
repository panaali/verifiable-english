"""Seeded faults for 13b: one per behaviour the switch claims. Each is applied alone in the checkout `--root` (a
scratch worktree of the head), its test is run and must fail, the source is restored and the same test must pass
again; a Lean fault is built and its build pinned for its run, then the original source is rebuilt and its hash
checked against the one before. Writes `evidence/mutants.json` of this checkout.

    python docs/lean-first/b13b/mutants.py --root /path/to/scratch-worktree-of-head
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent

MUTANTS = [
    ("python_selection_wins", "a Lean-owned operation is Lean's under every selection", "ve/backends/dispatch.py",
     '    if SINGLE_OWNER[op] == "lean":\n        authority = "lean"\n', "",
     ["tests/test_single_owner.py::test_a_lean_owned_operation_is_lean_s_under_every_selection",
      "tests/test_lean_first_b13b.py::test_the_switched_relay_asks_lean_under_every_selection"]),
    ("admission_report_unbound", "a Lean admission row is bound to the request (report identity)", "ve/admission.py",
     ' or row["report_id"] != expected):', "):",
     ["tests/test_lean_first_b13b.py::test_every_structural_mutant_of_a_relayed_row_is_refused"]),
    ("definitions_row_unpaired", "a Lean definitions row whose premises and generators do not pair is refused",
     "ve/definitions.py",
     '    if len(row["premises"]) != len(row["generators"]):\n', '    if False:\n',
     ["tests/test_stage2_validation.py::test_definitions_are_leans_answer_and_python_does_not_arbitrate"]),
    ("fill_premises_dropped", "norm-defaults fill premises reach Lean's replay", "ve/entailment.py",
     '                                          *getattr(env, "fill_premises", ()))]',
     '                                          )]',
     ["tests/test_norm_defaults.py::test_u5a_unspecified_obligation_beside_deny_permission_is_conflict_free"]),
    ("background_route_view", "Lean answers Background over the model projection", "ve/background.py",
     '{**case, "environment": background_environment(env)}',
     '{**case, "environment": __import__("ve.backends.lean_runner", fromlist=["x"]).cached_route_environment(env)}',
     ["tests/test_model_environment.py"]),
    ("sugar_rejection_to_lean", "a rejection inside a definitions@0 sugar production stays the retained reader's",
     "ve/parser.py",
     '            if getattr(exc, "definitions_sugar", False):\n                raise',
     '            if False:\n                raise',
     ["tests/test_definitions.py::test_definition_statement_sugar_is_input_only"]),
    ("lean_typing_refuses_readings", "Lean types formulas over readings@1 environments (Lean)",
     "lean/VE/Service/Standalone.lean",
     '  if profiles.contains "readings@1" then env ← VE.Readings.Wire.stripReadings env\n', "",
     ["tests/test_readings_s2_document.py::test_m5_narrowing_premise_and_no_dead_reading"]),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "tools"))
    import nested_pytest
    service, lock = root / "lean/.lake/build/bin/ve_service", root / "lean/checkers.lock"
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}", "VE_NATIVE_PREBUILT": "1",
           "VE_LEAN_PREBUILT": "1", "VE_RUST_PREBUILT": "1", "VE_RUST_BINARY": str(root / "rust/target/release/ve")}

    def build():
        subprocess.run(["lake", "build", "ve_service"], cwd=root / "lean", env=env, check=True, capture_output=True)

    def run(tests):
        done = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *tests]), cwd=root,
                              env=nested_pytest.environment(env), capture_output=True, text=True)
        return done.returncode, [line.split(" ")[1] for line in done.stdout.splitlines() if line.startswith("FAILED ")]

    rows = []
    original_build, lock_text = sha(service), lock.read_text()
    for name, behaviour, file, old, new, tests in MUTANTS:
        path = root / file
        source = path.read_text()
        assert source.count(old) == 1, name
        try:
            path.write_text(source.replace(old, new))
            if file.endswith(".lean"):
                build()
                pinned = json.loads(lock_text)
                pinned["ve_service"].append(sha(service))
                lock.write_text(json.dumps(pinned, indent=2) + "\n")
            mutated, failed = run(tests)
        finally:
            path.write_text(source)
            lock.write_text(lock_text)
            if file.endswith(".lean"):
                build()
        restored, still_failing = run(tests)
        rows.append({"mutant": name, "behaviour": behaviour, "file": file, "tests": tests,
                     "mutated_exit": mutated, "failed": failed, "restored_exit": restored,
                     "caught": mutated == 1 and bool(failed) and restored == 0 and not still_failing})
        print(name, mutated, failed, restored, flush=True)
    restored_build = sha(service) == original_build
    (HERE / "evidence/mutants.json").write_text(json.dumps(
        {"head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip(),
         "mutants": rows, "service_build_restored": restored_build, "service_build": original_build},
        indent=1) + "\n")
    return 0 if restored_build and all(row["caught"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
