"""Plant each seeded fault of premise-scale, prove its named test fails, then restore the source
(evidence/mutants.json), one fault at a time.

- "cargo": the Rust test target runs on the planted source.
- "release": the Rust release binary is built from the planted source, and the Python test runs
  against it, trusting that build's hash for this run only (VE_RUST_SHA256).
- "python": the Python test runs on the planted source and the binaries built from the restored
  sources (the Rust release binary is rebuilt first, so no prior Rust fault's build is used).
- "lean": `ve_service` is built from the planted source (the build must pass: a fault the proofs
  catch is the next kind), its hash is added to `lean/checkers.lock` for the run only, and the
  Python test runs against it.
- "lean-proof": the build of the planted module must fail at the named theorem (`Module:theorem`;
  build checklist item 10: the statement says what the code does).

After the last fault the sources are restored, the release binary and `ve_service` are rebuilt,
and each must be one its lock pins."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from tools import nested_pytest  # noqa: E402  (the one builder of a nested pytest command)
import rust_build  # noqa: E402

LOCK = ROOT / "lean/checkers.lock"
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
LAKE = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}:{os.environ['PATH']}"}
SCALE = "tests/test_premise_scale.py::"
ANSWER = "tests/test_search_budget_answer.py::"
RUST_TESTS = "premise_scale"  # rust/ve-core/tests/premise_scale.rs
SEARCH, GROUND = "rust/ve-profile/src/search.rs", "rust/ve-profile/src/ground.rs"
RUN, BUDGET = "lean/VE/SearchBudget/Run.lean", "lean/VE/SearchBudget/Budget.lean"
# (bug, file, before, after, how the test runs, test)
CASES = [
    ("a raised sort is searched at the shared bound (Rust ignores the per-sort maximum)", SEARCH,
     ".map(|s| sort_bounds.get(s).map_or(maximum, |(_, most)| *most))",
     ".map(|_| maximum)",
     "cargo", "a_raised_sort_is_searched_at_its_size"),
    ("the same fault, seen through the premise check", SEARCH,
     ".map(|s| sort_bounds.get(s).map_or(maximum, |(_, most)| *most))",
     ".map(|_| maximum)",
     "release", SCALE + "test_exactly_three_principal_types_has_a_lean_checked_model_at_size_three"),
    ("the ground-fact candidate leaves out the stated unary facts", GROUND,
     'Some(("unary" | "binary", a)) if a.len() >= 3',
     'Some(("binary", a)) if a.len() >= 3',
     "cargo", "the_ground_route_tries_the_stated_facts_alone"),
    ("the ground-fact candidate is reported without being checked against the premises", SEARCH,
     '        if status == "Valid" {\n',
     '        if status == "Valid" || ground_only {\n',
     "cargo", "a_ground_candidate_the_premises_reject_is_no_witness"),
    ("the budget row's entries are not bound one per requested sort", "ve/search.py",
     'if type(entries) is not list or len(entries) != len(case["sorts"]):',
     'if type(entries) is not list:',
     "python", ANSWER + "test_one_fault_mutants_are_refused_or_change_nothing"),
    ("the premise check skips the ground-fact route", "ve/vacuity.py",
     "for ground_only in (False, True):",
     "for ground_only in (False,):",
     "python", SCALE + "test_stated_quantities_give_their_own_model"),
    ("a Rust timeout in the premise check's search is a failure, not 'no witness'", "ve/vacuity.py",
     "    except RustTimeout:\n        return None\n",
     "    except ZeroDivisionError:\n        return None\n",
     "python", SCALE + "test_a_rust_timeout_is_no_witness"),
    ("the readings route's scaled search takes Lean's budget over the route's", "ve/readings_verdicts.py",
     'options = {"max_domain_size": BUDGET["max_domain_size"], "max_models": BUDGET["max_models"],\n'
     '               "max_evaluations": BUDGET["max_evaluations"],',
     'options = {"max_domain_size": lean.max_domain_size, "max_models": lean.max_models,\n'
     '               "max_evaluations": lean.max_evaluations,',
     "python", "tests/test_readings_budget_zero.py::test_budget_zero_every_verdict_op_is_unknown"),
    ("the Rust limit ignores the case line's size", "ve/backends/rust_jsonl.py",
     "base + per_byte * size + square * n * n",
     "base + 0 * size + square * n * n",
     "python", SCALE + "test_the_default_limit_grows_with_the_case"),
    ("Lean's row states a shared domain bound one above its budget", RUN,
     '("max_domain_size", toJson b.domainSize)',
     '("max_domain_size", toJson (b.domainSize + 1))',
     "lean", SCALE + "test_lean_raises_only_the_sort_the_premises_force"),
    ("Lean raises a sort past the per-sort cap", BUDGET,
     "def sortCap : Nat := 8",
     "def sortCap : Nat := 9",
     "lean", SCALE + "test_no_sort_is_raised_within_the_shared_bound_or_past_the_cap"),
    ("a raised sort's most is one above its demand", BUDGET,
     "if b.domainSize < d ∧ d ≤ sortCap then some (s, d, d) else none",
     "if b.domainSize < d ∧ d ≤ sortCap then some (s, d, d + 1) else none",
     "lean-proof", "VE.SearchBudget.Budget:sortBounds_spec"),
]


def lake(*targets: str) -> subprocess.CompletedProcess:
    return subprocess.run(["lake", "build", *targets], cwd=ROOT / "lean", env=LAKE, capture_output=True,
                          text=True, check=False)


def release() -> str:
    subprocess.run([sys.executable, str(ROOT / "tools/rust_build.py")], cwd=ROOT, check=True, capture_output=True)
    return rust_build.digest(rust_build.RELEASE_BINARY)


def pytest(test: str, **settings: str) -> subprocess.CompletedProcess:
    return subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", test]), cwd=ROOT,
                          env=nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1", **settings),
                          capture_output=True, text=True, check=False)


def run(how: str, test: str) -> tuple[subprocess.CompletedProcess, bool]:
    """The test's run and whether it failed for the planted fault."""
    if how == "cargo":
        done = subprocess.run([sys.executable, str(ROOT / "tools/rust_build.py"), "test", "--locked",
                               "--manifest-path", str(ROOT / "rust/Cargo.toml"), "-p", "ve-core",
                               "--test", RUST_TESTS, "--", test], cwd=ROOT, capture_output=True, text=True,
                              check=False)
        return done, "test result: FAILED" in done.stdout + done.stderr
    if how == "release":
        done = pytest(test, VE_RUST_SHA256=release())
        return done, "1 failed" in done.stdout
    if how == "python":
        # The binary built from the restored Rust source: never a prior Rust fault's build.
        done = pytest(test, VE_RUST_SHA256=release())
        return done, " failed" in done.stdout
    if how == "lean-proof":
        module, theorem = test.split(":")  # the module whose build must fail, inside this theorem
        source = ROOT / "lean" / (module.replace(".", "/") + ".lean")
        lines = source.read_text().splitlines()
        start = next(i for i, line in enumerate(lines, 1) if line.startswith(f"theorem {theorem} "))
        end = next((i for i, line in enumerate(lines, 1) if i > start and line.startswith("theorem ")), len(lines))
        done = lake(module)
        prefix = f"error: {source.relative_to(ROOT / 'lean')}:"
        errors = [int(line[len(prefix):].split(":")[0]) for line in (done.stdout + done.stderr).splitlines()
                  if line.startswith(prefix)]
        return done, done.returncode != 0 and bool(errors) and all(start <= n < end for n in errors)
    built = lake("ve_service")
    if built.returncode != 0:
        raise RuntimeError(f"the Lean mutant did not build: {built.stdout[-1500:]}")
    original = LOCK.read_text()
    lock = json.loads(original)
    lock["ve_service"] = [*lock["ve_service"], rust_build.digest(SERVICE)]
    try:
        LOCK.write_text(json.dumps(lock, indent=2) + "\n")
        done = pytest(test, VE_RUST_SHA256=release())
    finally:
        LOCK.write_text(original)
    return done, " failed" in done.stdout


def main() -> None:
    pinned = rust_build.digest(rust_build.RELEASE_BINARY)
    records = []
    try:
        for name, relative, before, after, how, test in CASES:
            path = ROOT / relative
            original = path.read_text()
            if original.count(before) != 1:
                raise RuntimeError(f"expected one mutation site for {name}")
            try:
                path.write_text(original.replace(before, after, 1))
                done, failed = run(how, test)
            finally:
                path.write_text(original)
            output = done.stdout + done.stderr
            if any(refusal in output for refusal in ("hash mismatch", "unlisted build", "invalid build lock")):
                raise RuntimeError(f"{name}: the test failed at a hash or lock check, not at the fault")
            if done.returncode == 0 or not failed:
                raise RuntimeError(f"{name}: expected a test failure, got {done.returncode}: {output[-1500:]}")
            language = {"ve": "Python", "rust": "Rust", "lean": "Lean"}[relative.split("/")[0]]
            records.append({"bug": name, "file": relative, "language": language, "how": how, "test": test,
                            "exit_code": done.returncode, "failure_excerpt": output[-1200:]})
            print(f"caught: {name}", flush=True)
    finally:
        restored = release()
        rebuilt = lake("ve_service")
    if restored != pinned:
        raise RuntimeError(f"the restored release binary {restored} is not the one before the run {pinned}")
    if rebuilt.returncode != 0 or rust_build.digest(SERVICE) not in json.loads(LOCK.read_text())["ve_service"]:
        raise RuntimeError("the restored ve_service is not pinned")
    evidence = ROOT / "docs/premise-scale/evidence/mutants.json"
    evidence.write_text(json.dumps(records, indent=2) + "\n")
    print(f"{len(records)} seeded faults caught")


if __name__ == "__main__":
    main()
