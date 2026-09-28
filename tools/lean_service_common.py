"""Shared helpers for the stage-1 Lean service tools (latency, soak).

The workloads are the ve-bench harness's (`~/code/ve-bench/bench/run.py`, `corpus()`),
imported unchanged; each bench implementation maps to one service mode and one
one-shot command. Our `ve` is imported first, so the bench only contributes `bench`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
DEFAULT_BENCH = Path.home() / "code/ve-bench"

# bench implementation -> (service mode, one-shot command)
MODES = {
    "lean": ("evaluate", [BIN / "ve_conformance"]),
    "lean_cert": ("check-certificate", [BIN / "ve_conformance", "check-certificate"]),
    "lean_order": ("order", [BIN / "ve_conformance", "order"]),
    "lean_route": ("route", [BIN / "ve_conformance", "route"]),
    "lean_norms": ("norms", [BIN / "ve_norms_route"]),
    "lean_english": ("english", [BIN / "ve_english_run"]),
}


def bench_module(bench_root: Path = DEFAULT_BENCH):
    import ve.backends.lean_service  # noqa: F401  (ours, before the bench path)
    if str(bench_root) not in sys.path:
        sys.path.append(str(bench_root))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from bench import run
    return run


def workloads(bench_root: Path = DEFAULT_BENCH, quick: bool = False):
    """[(name, implementation, service_case, one_shot_input_bytes)] for every Lean row."""
    run = bench_module(bench_root)
    rows = []
    for name, (case, impls) in run.corpus(quick).items():
        for impl in impls:
            if impl not in MODES:
                continue
            if impl == "lean_english":
                service_case = {"environment": case["lean_environment"], "lexicon": case["lexicon"],
                                "cases": [run.wire(case, impl)]}
                one_shot = json.dumps(service_case, separators=(",", ":")).encode()
            else:
                service_case = run.wire(case, impl)
                one_shot = json.dumps([service_case], separators=(",", ":")).encode()
            rows.append((name, impl, service_case, one_shot))
    return rows


def one_shot(impl: str, payload: bytes, timeout: float = 120) -> tuple[bytes, int]:
    proc = subprocess.run([str(x) for x in MODES[impl][1]], input=payload, capture_output=True,
                          timeout=timeout)
    return proc.stdout, proc.returncode


def one_shot_results(impl: str, payload: bytes) -> list:
    out, code = one_shot(impl, payload)
    assert code in (0, 1), (impl, code, out[:300])
    value = json.loads(out)
    return [value] if impl == "lean_english" else value


def percentile(xs, q):
    values = sorted(xs)
    k = (len(values) - 1) * q
    lo = int(k)
    return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (k - lo)


def summary(xs_seconds, rng=None, resamples=1000):
    """Median, p95, p99 in ms, with 95% bootstrap intervals for p50 and p95."""
    rng = rng or random.Random(0)
    ms = [x * 1000 for x in xs_seconds]
    def interval(q):
        boots = sorted(percentile([rng.choice(ms) for _ in ms], q) for _ in range(resamples))
        return [round(boots[int(0.025 * resamples)], 3), round(boots[int(0.975 * resamples) - 1], 3)]
    return {"n": len(ms), "p50_ms": round(statistics.median(ms), 3), "p50_ci_ms": interval(0.5),
            "p95_ms": round(percentile(ms, 0.95), 3), "p95_ci_ms": interval(0.95),
            "p99_ms": round(percentile(ms, 0.99), 3), "p99_ci_ms": interval(0.99),
            "max_ms": round(max(ms), 3)}


def machine():
    cpu = "unknown"
    try:
        cpu = next(line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                   if line.startswith("model name"))
    except (OSError, StopIteration):
        pass
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()
    return {"cpu": cpu, "logical_cpus": os.cpu_count(), "loadavg": list(os.getloadavg()),
            "python": sys.version.split()[0], "commit": commit}
