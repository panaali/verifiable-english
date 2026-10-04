"""CPU-time benchmarks against stored baselines: the speed checks kept out of the test suite.

Correctness tests never accept on speed (tests/test_hang_guards.py). What the code
costs is measured here, in CPU seconds, which machine load stretches far less than
elapsed time, and compared with `baselines.json`: a measurement fails when it exceeds
its baseline by more than the stored tolerance. Run nightly and on demand, after the
native builds (`cd lean && lake build`, and the Rust release build), never in the suite:

    PATH="$HOME/.elan/bin:$PATH" uv run --frozen python -m pytest tools/bench/test_perf.py \
        --bench-report /tmp/ve-bench.json

`--update-baselines` rewrites the baselines of the benchmarks that ran from this run
(review the diff: a baseline is a claim about the code's cost).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASELINES = Path(__file__).with_name("baselines.json")
sys.path.insert(0, str(ROOT / "tests"))  # as pytest's suite run imports its helpers
sys.path.insert(0, str(ROOT))

from subprocesses import HANG_TIMEOUT  # noqa: E402
from tools.bench import baseline  # noqa: E402

# The checker clients' wall-clock waits are hang guards (tests/conftest.py); a benchmark
# under load must not stop at a production default either.
CHECKER_TIMEOUTS = ("VE_RUST_TIMEOUT", "VE_LEAN_SERVICE_TIMEOUT", "VE_LEAN_SERVICE_STARTUP_TIMEOUT",
                    "VE_LEAN_TIMEOUT", "VE_CONFORMANCE_HANG_TIMEOUT", "VE_PRECOMMIT_TIMEOUT")
MEASURED = {}


def pytest_addoption(parser):
    parser.addoption("--update-baselines", action="store_true",
                     help="rewrite the baselines of the benchmarks that ran from this run")
    parser.addoption("--bench-report", type=Path, help="write every measurement and the machine load here")


def pytest_configure(config):
    for variable in CHECKER_TIMEOUTS:
        os.environ[variable] = str(HANG_TIMEOUT)


@pytest.fixture
def record(request):
    """record(measure, cpu_seconds): one measurement of this benchmark, checked at its end."""
    name = request.node.nodeid.split("::", 1)[1]
    seen = {}

    def add(measure, seconds):
        seen[f"{name}::{measure}"] = round(seconds, 3)
    yield add
    MEASURED.update(seen)
    if request.config.getoption("--update-baselines"):
        return
    assert seen, "a benchmark recorded no measurement"
    problems = baseline.over(seen, json.loads(BASELINES.read_text()))
    assert problems == [], "\n".join(problems)


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    if config.getoption("--update-baselines") and MEASURED:
        stored = baseline.updated(json.loads(BASELINES.read_text()), MEASURED)
        BASELINES.write_text(json.dumps(stored, indent=2) + "\n")
    report = config.getoption("--bench-report")
    if report:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True, timeout=HANG_TIMEOUT).stdout.strip()
        report.write_text(json.dumps({"commit": commit, "cpus": os.cpu_count(),
                                      "load_at_end": os.getloadavg(), "measurements": MEASURED},
                                     indent=2, sort_keys=True) + "\n")
