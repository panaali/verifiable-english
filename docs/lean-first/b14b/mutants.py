"""Plant and restore batch 14b faults, recording the tests that detect them.

Run only when other tests and corpus recorders are idle:

    python docs/lean-first/b14b/mutants.py --out docs/lean-first/b14b/evidence/mutants.json

Each replacement is made in a changed product file, its named test must fail,
and the unchanged test must pass after restoration. The Lean mutation rebuilds
its module before either guard; the final service rebuild restores the binary.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import nested_pytest  # noqa: E402

PYTHON = ROOT / ".venv/bin/python"
ENV = {**os.environ, "PATH": str(Path.home() / ".elan/bin") + ":" + os.environ.get("PATH", ""),
       "XDG_CACHE_HOME": "/tmp/lf14b-cache", "UV_NO_CACHE": "1", "VE_NATIVE_PREBUILT": "1"}
GUARD = Path("/tmp/lf14b-family-route-guard.lean")


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] = ENV) -> dict:
    done = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    return {"exit": done.returncode, "tail": (done.stdout + done.stderr).splitlines()[-12:]}


def mutation(name: str, file: str, old: str, new: str, test: str, *, lean: bool = False) -> dict:
    path = ROOT / file
    original = path.read_text()
    if original.count(old) != 1:
        raise RuntimeError(f"{name}: replacement is not unique in {file}")
    command = (["lake", "env", "lean", str(GUARD)] if lean else
               nested_pytest.command(["-q", "--tb=short", test], python=[str(PYTHON)]))
    test_env = ENV if lean else nested_pytest.environment(ENV)
    build = ["lake", "build", "VE.Norms.Family"]
    cwd = ROOT / "lean" if lean else ROOT
    try:
        path.write_text(original.replace(old, new))
        compiled = run(build, cwd=cwd) if lean else {"exit": 0}
        planted = run(command, cwd=cwd, env=test_env) if compiled["exit"] == 0 else {"exit": None, "tail": []}
    finally:
        path.write_text(original)
    restored_build = run(build, cwd=cwd) if lean else {"exit": 0}
    restored = run(command, cwd=cwd, env=test_env) if restored_build["exit"] == 0 else {"exit": None, "tail": []}
    row = {"name": name, "file": file, "test": test, "compiled": compiled,
           "planted": planted, "restored_build": restored_build, "restored": restored}
    if compiled["exit"] != 0 or planted["exit"] in (None, 0) or restored_build["exit"] != 0 or restored["exit"] != 0:
        raise RuntimeError(f"{name}: mutant was not caught and restored: {row}")
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    GUARD.write_text('import VE.Norms.Family\nopen Lean\n'
                     '#guard VE.Norms.Family.firstOrderFormula false '
                     '((Json.parse "[\\"reach\\",\\"star\\",[\\"named\\",\\"before\\"],'
                     '[\\"var\\",0],[\\"var\\",0]]").toOption.getD Json.null) == false\n')
    rows = [
        mutation("family_route", "ve/norms.py", "return family_in_scope(env)", "return False",
                 "tests/test_stage2_norms.py::test_non_first_order_norms_are_dispatched_and_match_python"),
        mutation("target_binding", "ve/norms.py",
                 'if len(row["targets"]) != len(expected) or set(row["targets"]) != expected:',
                 "if False:", "tests/test_stage2_norms.py::test_non_first_order_conflict_refuses_extra_target"),
        mutation("certificate_layer_binding", "ve/norms.py",
                 'if row["layers"] != sum(d.regulated is not None for d in document.env.predicates.values()):',
                 "if False:", "tests/test_stage2_norms.py::test_non_first_order_certificate_refuses_unbound_layer_count"),
        mutation("refused_witness", "ve/norms.py",
                 'if row["verdict"] != "CONFLICT" or row.get("target") != target:',
                 'if row.get("target") != target:',
                 "tests/test_stage2_norms.py::test_non_first_order_conflict_refused_witness_is_unavailable"),
        mutation("zero_budget_unknown", "ve/norms.py",
                 '                return _conflict_report(document, target, sorts, model, values, lean=True)\n'
                 '        except _Exhausted:\n'
                 '            return ConflictReport("UNKNOWN", detail="MAX_EVALUATIONS")',
                 '                return _conflict_report(document, target, sorts, model, values, lean=True)\n'
                 '        except _Exhausted:\n'
                 '            return ConflictReport("CONFLICT")',
                 "tests/test_stage2_norms.py::test_non_first_order_conflict_zero_model_budget_is_unknown"),
        mutation("nary_substitution", "ve/norms.py",
                 "    if isinstance(formula, Atom) and nary_atoms:\n",
                 "    if isinstance(formula, Atom):\n",
                 "tests/test_stage2_norms.py::test_retained_python_route_keeps_the_base_nary_expansion"),
        mutation("search_admission_substituted", "ve/norms.py",
                 "_Checker(env).formula(admitted, tuple(reversed(sorts)))",
                 "_Checker(env).formula(formula, tuple(reversed(sorts)))",
                 "tests/test_stage2_norms.py::test_retained_python_route_keeps_the_base_nary_expansion"),
        mutation("prove_admission_substituted", "ve/norms.py",
                 "_validate_inputs(env, (), _bind(Not(admitted), sorts))",
                 "_validate_inputs(env, (), _bind(Not(formula), sorts))",
                 "tests/test_stage2_norms.py::test_retained_python_route_keeps_the_base_nary_expansion"),
        mutation("lean_generators_base_expansion", "ve/norms.py",
                 "searched = document.conflict_targets(nary_atoms=True) if lean else base",
                 "searched = base",
                 "tests/test_stage2_norms.py::test_lean_route_f5_witness_is_unknown_not_checker_unavailable"),
        mutation("lean_situation_base_expansion", "ve/norms.py",
                 "document.selected_rules(target, model, values, nary_atoms=lean)",
                 "document.selected_rules(target, model, values)",
                 "tests/test_stage2_norms.py::test_lean_route_situation_names_the_rules_selected_by_leans_targets"),
        mutation("lean_route_answer_drift", "ve/norms.py",
                 'return ConflictReport("UNKNOWN", detail=row["detail"])',
                 'return ConflictReport("UNKNOWN", detail="tableau budget or search bound")',
                 "tests/test_stage2_norms.py::test_lean_family_route_answers_as_the_retained_python_route"),
        mutation("lean_non_fol_selector", "lean/VE/Norms/Family.lean",
                 '| .ok a => (VE.Core.erase a).isSome', '| .ok _ => true', str(GUARD), lean=True),
    ]
    service = run(["lake", "build", "ve_service", "ve_response_decode"], cwd=ROOT / "lean")
    if service["exit"] != 0:
        raise RuntimeError(f"service rebuild after mutants failed: {service}")
    result = {"mutants": rows, "service_restored": service}
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(rows)} planted faults caught; restored tests and service build pass")


if __name__ == "__main__":
    main()
