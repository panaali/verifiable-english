"""CPU-time benchmarks of the work the suite once bounded by speed (see conftest.py).

Each was an assertion in a correctness test: the pre-commit hook's cost on a large
staged change, the soft validators' refusal of exponential unfoldings, and the CPU
each kernel-bounded Lean and Rust batch of the W6a limit tests spends.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time

import pytest

from conformance.soft_norms import soft4_reproducers
from subprocesses import HANG_TIMEOUT, ChildCPU
from tools import nested_pytest
from ve.errors import VEError
from ve.soft_route import _run
from ve.softnorms import load_soft_document

ROOT = Path(__file__).resolve().parents[2]


def test_precommit_large_staged_change(record, tmp_path):
    """The hook's own work on an edit of every Python and hand-written Lean source plus
    1500 new files. `lean --deps` is left out: its share is bounded by its wall-clock
    budget (`lean_header_imports`), not by its work."""
    from test_precommit_hook import Staging, stage_large_change, without_lean
    staging = Staging(tmp_path)
    stage_large_change(staging)
    with ChildCPU() as cpu:
        result = staging.run("--timings", PATH=without_lean(tmp_path))
    assert result.returncode == 0, result.stderr
    record("hook", cpu.seconds)


@pytest.mark.parametrize("name, raw, rules, code", list(soft4_reproducers()),
                         ids=[row[0] for row in soft4_reproducers()])
def test_soft_exponential_unfoldings_are_refused_cheaply(record, name, raw, rules, code):
    """Each unfolding is beyond 2 ** 24 nodes; both validators size it from their per-rule
    tables, so a build of it would multiply these costs."""
    started = time.process_time()
    with pytest.raises(VEError) as python_error:
        load_soft_document(raw, rules)
    record("python", time.process_time() - started)
    with ChildCPU() as lean, pytest.raises(VEError) as lean_error:
        _run({"id": name, "kind": "soft-elaborate", "environment": raw, "norms": rules})
    record("lean", lean.seconds)
    assert python_error.value.code == lean_error.value.code == code


# Suite tests whose Lean and Rust batches run under a kernel CPU limit
# (tests/subprocesses.py: run_cpu_bounded): the CPU each batch spends, summed per test.
BOUNDED = {
    "w6a-generator": "tests/test_w6a_limit_generator.py::test_every_backend_reports_resource_limit_in_bounded_time",
    "w6a-route-limits": "tests/test_w6a_route_limits.py",
}


@pytest.mark.parametrize("target", BOUNDED.values(), ids=BOUNDED.keys())
def test_kernel_bounded_batches(record, tmp_path, target):
    log = tmp_path / "cpu.jsonl"
    env = nested_pytest.environment(os.environ, VE_BENCH_CPU_LOG=str(log), VE_NATIVE_PREBUILT="1",
                                    VE_LEAN_PREBUILT="1")
    result = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", target]),
                            cwd=ROOT, env=env, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stdout[-4000:]
    totals = {}
    for line in log.read_text().splitlines():
        row = json.loads(line)
        key = f"{row['test'].split('::', 1)[1]}:{row['command']}"
        totals[key] = totals.get(key, 0.0) + row["cpu"]
    for key, seconds in sorted(totals.items()):
        record(key, seconds)


@pytest.mark.parametrize("ident", ["U3", "A1"])
def test_ask_lean_cpu(record, ident):
    """Question answering Q2.6's `ask` budget (plan: Lean CPU at most 2 s per request), measured on the recorded
    U3 (the UDHR readings route, six choices) and A1 (an agent-policy document) on a warm service. The qa-q2 review
    found 2.67 s on U3: every reader of a row's key replayed its certificate's citations; the answer now builds them
    once (`VE.Ask.memoTable`)."""
    import importlib.util
    from ve.backends.lean_service import DEFAULT_EXECUTABLE, LeanService
    spec = importlib.util.spec_from_file_location("question_answering_measure",
                                                  ROOT / "tools/question_answering_measure.py")
    measure = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(measure)
    _, _, ask = measure.service_case(ident)
    with LeanService(DEFAULT_EXECUTABLE) as service:
        found = measure.measure_service(service, "ask", ask)
    if found["cpu_s"] is None:
        pytest.skip("the platform does not report the service's CPU time")
    record("lean", found["cpu_s"])
    assert found["cpu_s"] <= 2.0, found  # the plan's registered budget, beside the stored baseline


def test_gate_source_identity(record, tmp_path):
    """The gate's worktree check, run at its start and at its end (tools/gate.py: source_identity), on a clean
    checkout: its second status, against a fresh index read from HEAD, hashes every tracked file. `repository
    index` is its first status alone, which trusts the repository index's stat data (fix-fsmonitor-gate)."""
    from tools import gate
    env = gate.gate_environment(tmp_path / "scratch")
    with ChildCPU() as fresh:
        _, dirty = gate.source_identity(env)
    assert dirty is False, "a dirty checkout stops at the first status: measure on a clean one"
    record("fresh index", fresh.seconds)
    git = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false"]
    with ChildCPU() as stat:
        subprocess.run([*git, "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, env=env,
                       capture_output=True, check=True, timeout=HANG_TIMEOUT)
    record("repository index", stat.seconds)
