"""Stage-1 latency: persistent `ve_service` versus the one-shot Lean executables.

Usage (repository root, after `cd lean && lake build`):

    PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-uv-cache uv run --frozen \
        python tools/lean_service_latency.py --out experiments/lean-service/latency

Workloads are the ve-bench harness's Lean rows (`bench.run.corpus`, full size unless
`--quick`). A persistent call is timed at the Python client boundary
(`LeanService.run(mode, [case])`: JSON encoding, IPC, supervision and decoding
included) on one warm process; a one-shot call is one process per case, as the
bench measured Lean. Samples of the two alternate. Every service result must equal
the one-shot result before timing. Batch rows time the plan's section-4 batch gates.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.lean_service_common import (DEFAULT_BENCH, MODES, machine, one_shot, one_shot_results,  # noqa: E402
                                       summary, workloads)
from ve.backends.lean_service import LeanService  # noqa: E402

BATCHES = {"W3/definitions": 2048, "W3/bundle": 256, "W1/conflict-check": 256,
           "certificate/tableau-large": 8}
GATES = {"W3/definitions": 1.0, "W3/bundle": 0.25, "W1/conflict-check": 0.5,
         "certificate/tableau-large": 0.3}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bench-root", type=Path, default=DEFAULT_BENCH)
    parser.add_argument("--samples", type=int, default=400, help="persistent calls per workload")
    parser.add_argument("--one-shot-samples", type=int, default=40)
    parser.add_argument("--batch-repeats", type=int, default=10)
    parser.add_argument("--cold-starts", type=int, default=20)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    rows = workloads(args.bench_root, args.quick)
    data = {"machine": machine(), "quick": args.quick, "cold_start": None, "calls": [], "batches": []}

    cold = []
    for _ in range(args.cold_starts):
        cold_service = LeanService(max_rss=None)
        try:
            started = time.perf_counter()
            cold_service.start()
            cold.append(time.perf_counter() - started)
        finally:
            cold_service.close()
    data["cold_start"] = summary(cold)

    service = LeanService(timeout=120, max_requests=10**9, max_rss=None)
    service.start()
    for name, impl, case, payload in rows:
        mode = MODES[impl][0]
        reference = one_shot_results(impl, payload)
        assert service.run(mode, [case]) == reference, name
        persistent, oneshot = [], []
        for i in range(max(args.samples, args.one_shot_samples)):
            if i < args.one_shot_samples:
                started = time.perf_counter()
                out, code = one_shot(impl, payload)
                oneshot.append(time.perf_counter() - started)
                assert code in (0, 1) and out, name
            if i < args.samples:
                started = time.perf_counter()
                service.run(mode, [case])
                persistent.append(time.perf_counter() - started)
        row = {"workload": name, "mode": mode, "input_bytes": len(payload),
               "persistent": summary(persistent), "one_shot": summary(oneshot)}
        row["speedup_p50"] = round(row["one_shot"]["p50_ms"] / row["persistent"]["p50_ms"], 1)
        data["calls"].append(row)
        print(f"{name:28} {mode:18} persistent p50 {row['persistent']['p50_ms']:8.3f} "
              f"p95 {row['persistent']['p95_ms']:8.3f} | one-shot p50 {row['one_shot']['p50_ms']:8.3f} "
              f"p95 {row['one_shot']['p95_ms']:8.3f}", flush=True)
        if name in BATCHES:
            n = BATCHES[name]
            cases = [case] * n
            batch_payload = (json.dumps({**case, "cases": case["cases"] * n}).encode() if impl == "lean_english"
                             else json.dumps(cases, separators=(",", ":")).encode())
            persistent, oneshot = [], []
            for _ in range(args.batch_repeats):
                started = time.perf_counter()
                results = service.run(mode, cases, timeout=120)
                persistent.append(time.perf_counter() - started)
                assert results == reference * n, name
                started = time.perf_counter()
                one_shot(impl, batch_payload)
                oneshot.append(time.perf_counter() - started)
            data["batches"].append({"workload": name, "mode": mode, "cases": n, "gate_s": GATES[name],
                                    "persistent": summary(persistent), "one_shot": summary(oneshot)})
    data["service_stats"] = service.stats
    service.close()
    data["machine"]["loadavg_after"] = list(os.getloadavg())
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "latency.json").write_text(json.dumps(data, indent=2) + "\n")
    (args.out / "LATENCY.md").write_text(report(data))
    print(report(data))


def report(data):
    m = data["machine"]
    c = data["cold_start"]
    lines = ["# Lean service latency (stage 1)", "",
             f"Commit `{m['commit']}`; {m['cpu']}, {m['logical_cpus']} logical CPUs; load average "
             f"{m['loadavg']} before, {m.get('loadavg_after')} after; Python {m['python']}; "
             f"{'quick' if data['quick'] else 'full'} bench corpus.", "",
             "Persistent: `LeanService.run(mode, [case])` on one warm `ve_service` process, timed at "
             "the Python boundary (JSON, IPC, supervision included). One-shot: one executable "
             "process per case, as ve-bench measured Lean. Bracketed values are 95% bootstrap "
             "intervals.", "",
             f"Cold start (spawn to handshake, n={c['n']}): p50 {c['p50_ms']} ms, p95 {c['p95_ms']} ms.", "",
             "| Workload | Mode | Persistent p50 ms | Persistent p95 ms | One-shot p50 ms | One-shot p95 ms | p50 speedup |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for r in data["calls"]:
        p, o = r["persistent"], r["one_shot"]
        lines.append(f"| {r['workload']} | {r['mode']} | {p['p50_ms']} {p['p50_ci_ms']} | {p['p95_ms']} "
                     f"{p['p95_ci_ms']} | {o['p50_ms']} | {o['p95_ms']} | {r['speedup_p50']}x |")
    lines += ["", "Batches (section 4 gates; the client splits at 256 cases per request):", "",
              "| Workload | Cases | Gate s | Persistent median s | Persistent p95 s | One-shot median s |",
              "|---|---:|---:|---:|---:|---:|"]
    for b in data["batches"]:
        lines.append(f"| {b['workload']} | {b['cases']} | {b['gate_s']} | "
                     f"{b['persistent']['p50_ms'] / 1000:.3f} | {b['persistent']['p95_ms'] / 1000:.3f} | "
                     f"{b['one_shot']['p50_ms'] / 1000:.3f} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
