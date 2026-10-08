"""Seeded bugs of lean-first batch 15b, one per behaviour the batch claims (build checklist 13).

Each seed is planted alone in the working tree, the named focused tests run, and the file is restored;
the record (`evidence/mutants.txt`) keeps each run's exit status and its FAILED lines. A Lean seed is
built into `ve_metered` and the clean build is restored afterwards. Run from a clean checkout:

    uv run --frozen python docs/lean-first/b15b/mutants.py
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import nested_pytest  # noqa: E402
OUT = Path(__file__).with_name("evidence") / "mutants.txt"
LAKE = str(Path.home() / ".elan/bin/lake")

# (name, file, original text, seeded text, focused tests)
SEEDS = (
    ("python-search-branch", "ve/search.py",
     '    return owned("countermodel_search", rust)',
     '    return owned("countermodel_search", lambda: CountermodelResult('
     '"NotFound", None, 0, 0, max_domain_size, max_models))',
     ["tests/test_assurance_manifest.py::test_search_reports_found_only_through_the_countermodel_check"]),
    ("lean-nonvacuity-ignores-semantic", "ve/search.py",
     '"semantic_nonvacuity": semantic})',
     '"semantic_nonvacuity": False})',
     ["tests/test_search_options.py::test_semantic_clause_guard_is_joint_per_occurrence_and_checks_hidden_branches"]),
    ("lean-evaluation-count", "ve/evaluate.py",
     "    return EvaluationResult(status, value, None if explanation is None else _explanation(explanation), work)",
     "    return EvaluationResult(status, value, None if explanation is None else _explanation(explanation), work + 1)",
     ["tests/test_stage2_evaluation.py"]),
    # Review A1/B1: Rust's search and Lean's metered cases read the model environment.
    ("model-environment-keeps-display", "ve/profiles.py",
     '                  "constants": ("verbalisation",)}',
     '                  "constants": ()}',
     ["tests/test_model_environment.py"]),
    ("model-environment-keeps-unspecified", "ve/profiles.py",
     '    "norm-defaults@0": ModelReduction(unspecified="deny"),',
     '    "norm-defaults@0": ModelReduction(),',
     ["tests/test_model_environment.py"]),
    ("metered-reads-the-route-environment", "ve/backends/lean_runner.py",
     "    return model_environment(env.to_dict())\n",
     "    return route_environment(env)\n",
     ["tests/test_model_environment.py"]),
    # Review B3: under the Lean authority the countermodel check reports Lean's values and counts.
    ("lean-countermodel-check-reports-rust", "ve/search.py",
     "        result = checked(lambda formula, budget: _evaluate_lean(env, {",
     "        result = rust() if True else checked(lambda formula, budget: _evaluate_lean(env, {",
     ["tests/test_lean_authority_values.py"]),
    # Review B2: no differential compares Rust's search with itself.
    ("execute-shadows-one-implementation", "ve/backends/dispatch.py",
     "    if op in SINGLE_OWNER or python is lean or python is rust:",
     "    if False:",
     ["tests/test_single_owner.py"]),
    ("difffuzz-compares-search-with-itself", "tools/difffuzz.py",
     '        return not (engine == "python" and python_owner(seed.meta["kind"]) in seed.engines)',
     "        return True",
     ["tests/test_single_owner.py"]),
    ("metered-exit-status", "lean/VE/Route/MeteredRun.lean",
     '    return if results.any (·.getObjValD "status" == .str "error") then 1 else 0',
     "    return 0",
     ["tests/test_metered_lean.py::test_bad_budget_types_are_bounded_errors"]),
    ("rule3-summary-ignores-deadline", "docs/lean-first/b15b/rule3.py",
     '               "passes": not any(failing.values())}',
     '               "passes": not any(ids for p, ids in failing.items() if p != "deadline")}',
     ["tests/test_b15b_evidence.py::test_rule3_rows_are_recomputed_from_the_saved_records"]),
    # Review B4: the certificate rows cover the whole cohorts and measure order.
    ("rule3-certificate-sample", "docs/lean-first/b15b/rule3.py",
     '        mine = [r for r in records if r["operation"] == operation and "passes" in r]',
     '        mine = [r for r in records if r["operation"] == operation and "passes" in r][:40]',
     ["tests/test_b15b_evidence.py::test_rule3_rows_are_recomputed_from_the_saved_records"]),
    ("rule3-certificate-order-constant", "docs/lean-first/b15b/rule3.py",
     '            "passes": {"order": _prover(head_prover) == _prover(prover),',
     '            "passes": {"order": True,',
     ["tests/test_b15b_evidence.py::test_rule3_certificate_order_is_measured_not_assumed"]),
)


def pytest(tests: list[str]) -> tuple[int, str]:
    env = {**nested_pytest.environment(os.environ), "VE_NATIVE_PREBUILT": "1", "VE_LEAN_PREBUILT": "1",
           "VE_RUST_PREBUILT": "1", "VE_RUST_BINARY": str(ROOT / "rust/target/release/ve")}
    proc = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *tests], workers=4),
                          cwd=ROOT, env=env, capture_output=True, text=True)
    lines = [line for line in proc.stdout.splitlines()
             if line.startswith("FAILED") or line.endswith(("passed", "failed")) or " passed" in line]
    return proc.returncode, "\n".join(lines)


def build(path: str) -> int:
    if not path.endswith(".lean"):
        return 0
    return subprocess.run([LAKE, "build", "ve_metered"], cwd=ROOT / "lean", capture_output=True).returncode


def main() -> None:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "ve", "lean", "tests", "docs", "tools"],
                                    cwd=ROOT, text=True).strip()
    out = [f"source commit: {head}; clean: {not dirty}"]
    for name, path, original, seeded, tests in SEEDS:
        file = ROOT / path
        text = file.read_text()
        assert text.count(original) == 1, (name, path)
        try:
            file.write_text(text.replace(original, seeded))
            built = build(path)
            code, lines = pytest(tests)
        finally:
            file.write_text(text)
        out += [f"## {name}", f"{path}: {seeded.strip()}", f"build exit: {built}; focused pytest exit: {code}",
                lines]
    built = max(build(path) for _, path, *_ in SEEDS)
    code, lines = pytest(sorted({test for *_, tests in SEEDS for test in tests}))
    out += ["## restored", f"clean build exit: {built}; focused pytest exit: {code}", lines]
    OUT.write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
