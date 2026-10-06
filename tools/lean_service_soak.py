"""Gate 1 soak: 20,000 mixed-mode requests on one `ve_service` process.

Usage (repository root, after `cd lean && lake build`):

    PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-uv-cache uv run --frozen \
        python tools/lean_service_soak.py --out experiments/lean-service/soak

Recycling is off, so the run shows the process's own memory behaviour. Each request
takes 1-8 cases of one mode, drawn with a fixed seed from per-mode pools (the ve-bench
workloads, including the 2,047-node certificate; conformance fixtures; route, norms,
order and English cases; adversarial inputs). Every result must equal the one-shot
executable's result for that case. RSS is sampled every 1,000 requests; the gate is
growth under 10% from request 1,000 to the end, with no restart.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.lean_service_common import (DEFAULT_BENCH, MODES, machine, one_shot, one_shot_results, summary,
                                       workloads)  # noqa: E402
from tools.lean_service_parity import adversarial, load  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402
from ve.backends.service_schema import same_json  # noqa: E402

IMPL = {mode: impl for impl, (mode, _) in MODES.items()}


def pools(bench_root):
    pool = {mode: [] for mode in IMPL}
    for name, impl, case, _ in workloads(bench_root, quick=False):
        pool[MODES[impl][0]].append(case)
    rng = random.Random(7)
    pool["evaluate"] += rng.sample(load("conformance/evaluation.json"), 60)
    pool["evaluate"] += rng.sample(load("conformance/countermodels.json"), 60)
    pool["evaluate"] += rng.sample(load("conformance/parser.json"), 40)
    pool["check-certificate"] += [r["case"] for r in rng.sample(load("conformance/v0-replay-baseline.json")["rows"], 80)]
    route = load("lean/VE/Route/examples/route-cases.json")
    pool["route"] += rng.sample(route, 80)
    pool["norms"] += rng.sample(route, 20)
    sys.path.insert(0, str(ROOT / "tests"))
    from tests.test_norms_three_way import corpus, lean_case
    pool["norms"] += [lean_case(i, d) for i, d in enumerate(corpus(80))]
    from conformance import order
    cases = order.evaluation_cases(60)
    pool["order"] += [c for c, _ in cases] if cases and isinstance(cases[0], tuple) else cases
    for mode in pool:
        pool[mode] += adversarial(mode)
    return pool


def references(pool):
    """One-shot result per pool case; None where the English runner exits 2."""
    ref = {}
    for mode, cases in pool.items():
        impl = IMPL[mode]
        if impl == "lean_english":
            ref[mode] = []
            for case in cases:
                out, code = one_shot(impl, json.dumps(case).encode())
                ref[mode].append(json.loads(out) if code == 0 else None)
        else:
            ref[mode] = one_shot_results(impl, json.dumps(cases).encode())
    return ref


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bench-root", type=Path, default=DEFAULT_BENCH)
    parser.add_argument("--requests", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20260927)
    args = parser.parse_args(argv)
    machine_info = machine()
    pool = pools(args.bench_root)
    ref = references(pool)
    rng = random.Random(args.seed)
    modes = sorted(pool)
    try:
        service = LeanService(timeout=60, max_requests=10**9, max_rss=None)
        service.start()
        latencies, rss, mismatches = [], [], []
        per_mode = {mode: 0 for mode in modes}
        started_all = time.perf_counter()
        for i in range(args.requests):
            mode = rng.choice(modes)
            picks = [rng.randrange(len(pool[mode])) for _ in range(rng.randint(1, 8))]
            started = time.perf_counter()
            results = service.run(mode, [pool[mode][k] for k in picks])
            latencies.append(time.perf_counter() - started)
            per_mode[mode] += 1
            for position, (k, got) in enumerate(zip(picks, results, strict=True)):
                want = ref[mode][k]
                if isinstance(want, dict) and "case_index" in want:  # a batch position, as one-shot
                    want = {**want, "case_index": position}
                if want is None:  # English one-shot failure: exit 2, the service's error record
                    if got.get("status") != "error":
                        mismatches.append((i, mode, k))
                elif not same_json(got, want):
                    mismatches.append((i, mode, k))
            if (i + 1) % 1000 == 0:
                rss.append({"request": i + 1, "rss_bytes": service.rss()})
                print(f"{i + 1} requests, rss {rss[-1]['rss_bytes'] / 1e6:.1f} MB, "
                      f"mismatches {len(mismatches)}, restarts {service.stats['restarts']}", flush=True)
        elapsed = time.perf_counter() - started_all
        stats = dict(service.stats)
    finally:
        service.close()
    warm = rss[0]["rss_bytes"]
    final = rss[-1]["rss_bytes"]
    growth = (final - warm) / warm
    machine_info["loadavg_after"] = list(os.getloadavg())
    data = {"machine": machine_info, "seed": args.seed, "requests": args.requests,
            "elapsed_s": round(elapsed, 1),
            "per_mode": per_mode, "pool_sizes": {m: len(c) for m, c in pool.items()},
            "mismatches": len(mismatches), "mismatch_examples": mismatches[:10], "service_stats": stats,
            "rss": rss, "rss_growth_from_1000": round(growth, 4),
            "peak_rss_bytes": max(r["rss_bytes"] for r in rss),
            "latency_first_100": summary(latencies[:100]), "latency_after_100": summary(latencies[100:])}
    passed = not mismatches and stats["restarts"] == 0 and growth < 0.10
    data["gate"] = "PASS" if passed else "FAIL"
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "soak.json").write_text(json.dumps(data, indent=2) + "\n")
    lat = data["latency_after_100"]
    md = ["# Lean service soak (stage 1, gate 1)", "",
          f"Commit `{data['machine']['commit']}`; {data['machine']['cpu']}; load average "
          f"{data['machine']['loadavg']} at start and {data['machine']['loadavg_after']} after.", "",
          f"- {args.requests} requests (seed {args.seed}; 1-8 cases each, mixed modes {per_mode}) "
          f"in {data['elapsed_s']} s on one process.",
          f"- Result mismatches against the one-shot executables: {len(mismatches)}.",
          f"- Restarts: {stats['restarts']}; recycling disabled.",
          f"- RSS at request 1,000: {warm / 1e6:.1f} MB; at the end: {final / 1e6:.1f} MB; growth "
          f"{growth * 100:.2f}% (gate < 10%); peak {data['peak_rss_bytes'] / 1e6:.1f} MB.",
          f"- Per-request latency at the client boundary after the first 100: p50 {lat['p50_ms']} ms "
          f"{lat['p50_ci_ms']}, p95 {lat['p95_ms']} ms {lat['p95_ci_ms']}, p99 {lat['p99_ms']} ms "
          f"{lat['p99_ci_ms']}, "
          f"max {lat['max_ms']} ms. First 100: p50 {data['latency_first_100']['p50_ms']} ms, "
          f"p95 {data['latency_first_100']['p95_ms']} ms.",
          f"- Gate: **{data['gate']}**.", "", "RSS samples (MB): " +
          ", ".join(f"{r['request']}: {r['rss_bytes'] / 1e6:.1f}" for r in rss)]
    (args.out / "SOAK.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
