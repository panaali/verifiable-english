"""Lean latency measurements for docs/LEAN-FIRST-PLAN.md.

Run from the repository root with the call profiler loaded:

    export PATH=$HOME/.elan/bin:$PATH VE_LEANFIRST_LOG=/tmp/lf.jsonl PYTHONPATH=docs/lean-first/hook
    uv run --frozen python docs/lean-first/measure.py startup --repeats 20
    VE_LEANFIRST_TAG=doc:udhr uv run --frozen python docs/lean-first/measure.py document load PATH
    uv run --frozen python docs/lean-first/measure.py report /tmp/lf.jsonl [--by-caller | --by-op]

`startup` times every Lean executable on an empty batch (process start to answer) and the
service's spawn-to-handshake. `document` times one public document step (load, check, render)
and logs it as an `op` line beside the profiler's calls. `report` aggregates a log by tag.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
BIN = ROOT / "lean/.lake/build/bin"
# Executable -> argv tail for an empty batch on stdin.
EMPTY_ARGS = {"ve_conformance": [], "ve_service": None, "ve_english_run": None, "ve_response_decode": None}


def _log(record: dict) -> None:
    path = os.environ.get("VE_LEANFIRST_LOG")
    if path:
        record.update(tag=os.environ.get("VE_LEANFIRST_TAG", ""), pid=os.getpid())
        with open(path, "a") as handle:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def _children_cpu() -> float:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def _load() -> float:
    return float(Path("/proc/loadavg").read_text().split()[0])


def pct(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    index = min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))
    return ordered[index]


def startup(repeats: int) -> None:
    from ve.backends.lean_service import LeanService
    rows = []
    for exe in sorted(BIN.iterdir()):
        if not os.access(exe, os.X_OK) or EMPTY_ARGS.get(exe.name, []) is None:
            continue
        argv = [str(exe), *EMPTY_ARGS.get(exe.name, ["-"])]
        times, cpus, codes = [], [], set()
        for _ in range(repeats):
            cpu = _children_cpu()
            started = time.perf_counter()
            proc = subprocess.run(argv, input=b"[]", capture_output=True, timeout=120)
            times.append(time.perf_counter() - started)
            cpus.append(_children_cpu() - cpu)
            codes.add(proc.returncode)
        rows.append({"exe": exe.name, "size_mib": round(exe.stat().st_size / 2**20, 1),
                     "p50_ms": round(pct(times, .5) * 1000, 1), "p95_ms": round(pct(times, .95) * 1000, 1),
                     "cpu_p50_ms": round(pct(cpus, .5) * 1000, 1), "exit": sorted(codes)})
    cold = []
    for _ in range(repeats):
        service = LeanService()
        started = time.perf_counter()
        service.start()
        cold.append(time.perf_counter() - started)
        service.close()
    rows.append({"exe": "ve_service (spawn to handshake, build hash cached)",
                 "p50_ms": round(pct(cold, .5) * 1000, 1), "p95_ms": round(pct(cold, .95) * 1000, 1)})
    _log({"kind": "startup", "rows": rows, "load": _load()})
    print(json.dumps(rows, indent=1))


CORPORA = [("conformance/evaluation.json", "evaluate"), ("conformance/countermodels.json", "evaluate"),
           ("conformance/closure.json", "evaluate")]


def _service_cpu(service) -> float:
    try:
        return int(Path(f"/proc/{service.pid}/schedstat").read_text().split()[0]) / 1e9
    except (OSError, ValueError, IndexError):
        return 0.0


def corpus() -> None:
    """Each conformance file three ways: one `ve_conformance` process for the whole file, one service request
    per case, and the service's batched `run` (256 cases per request)."""
    from ve.backends.lean_service import LeanService
    rows = []
    with LeanService(timeout=600) as service:
        for name, mode in CORPORA:
            path = ROOT / name
            cases = json.loads(path.read_text())
            cpu = _children_cpu()
            started = time.perf_counter()
            proc = subprocess.run([str(BIN / "ve_conformance"), str(path)], capture_output=True, timeout=600)
            one_shot = (time.perf_counter() - started, _children_cpu() - cpu, proc.returncode)
            per_case, per_case_cpu = [], []
            for case in cases:
                cpu = _service_cpu(service)
                started = time.perf_counter()
                service.run(mode, [case])
                per_case.append(time.perf_counter() - started)
                per_case_cpu.append(_service_cpu(service) - cpu)
            cpu = _service_cpu(service)
            started = time.perf_counter()
            results = service.run(mode, cases)
            batched = (time.perf_counter() - started, _service_cpu(service) - cpu)
            rows.append({"corpus": name, "cases": len(cases), "bytes": path.stat().st_size,
                         "one_shot_s": round(one_shot[0], 3), "one_shot_cpu_s": round(one_shot[1], 3),
                         "one_shot_exit": one_shot[2],
                         "per_case_sum_s": round(sum(per_case), 3), "per_case_p50_ms": round(pct(per_case, .5) * 1000, 2),
                         "per_case_p95_ms": round(pct(per_case, .95) * 1000, 2),
                         "per_case_max_ms": round(max(per_case) * 1000, 2),
                         "per_case_cpu_p50_ms": round(pct(per_case_cpu, .5) * 1000, 2),
                         "batched_s": round(batched[0], 3), "batched_cpu_s": round(batched[1], 3),
                         "batched_errors": sum(1 for r in results if isinstance(r, dict) and r.get("status") == "error")})
    _log({"kind": "corpus", "rows": rows, "load": _load()})
    print(json.dumps(rows, indent=1))


def document(step: str, path: Path, lean_timeout: float | None = None, profile: Path | None = None) -> None:
    from ve.document import check_document, load_document, render_document
    import ve.backends.lean as lean
    if lean_timeout is not None:
        # As the UDHR pilot's verify_step.py: the readings call's fixed 120 s limit, raised here only.
        lean.run_readings_cases.__kwdefaults__["timeout"] = lean_timeout
    action = {"load": load_document, "check": check_document, "render": render_document}[step]
    if profile is not None:
        import cProfile
        profiler = cProfile.Profile()
        plain = action

        def action(p):
            profiler.enable()
            try:
                return plain(p)
            finally:
                profiler.disable()
                profiler.dump_stats(str(profile))
    load = _load()
    python_cpu, children_cpu = time.process_time(), _children_cpu()
    started = time.perf_counter()
    status = "ok"
    try:
        result = action(path)
    except Exception as exc:  # a refusal is a measured outcome too
        status = f"{type(exc).__name__}: {str(exc)[:200]}"
        result = None
    wall = time.perf_counter() - started
    python_cpu, children_cpu = time.process_time() - python_cpu, _children_cpu() - children_cpu
    summary = None
    if step == "check" and isinstance(result, dict):
        summary = result.get("premises")
    _log({"kind": "op", "op": f"document.{step}", "path": str(path), "bytes": path.stat().st_size,
          "wall": wall, "python_cpu": python_cpu, "children_cpu": children_cpu,
          "load": [load, _load()], "status": status, "summary": summary})
    print(json.dumps({"step": step, "path": str(path), "wall_s": round(wall, 3),
                      "python_cpu_s": round(python_cpu, 3), "children_cpu_s": round(children_cpu, 3),
                      "status": status, "summary": summary}, default=str))


def _stats(values: list[float], cpus: list[float]) -> dict:
    return {"n": len(values), "sum_s": round(sum(values), 3),
            "p50_ms": round(pct(values, .5) * 1000, 2), "p95_ms": round(pct(values, .95) * 1000, 2),
            "max_ms": round(max(values) * 1000, 2) if values else None,
            "cpu_sum_s": round(sum(cpus), 3), "cpu_p50_ms": round(pct(cpus, .5) * 1000, 2),
            "cpu_p95_ms": round(pct(cpus, .95) * 1000, 2),
            "cpu_max_ms": round(max(cpus) * 1000, 2) if cpus else None}


def by_op(log: Path) -> None:
    """One line per `document` step: its Python CPU and the Lean and Rust calls made since the previous step of
    the same process (the profiler's lines are written in call order)."""
    pending: dict = {}
    for line in log.read_text().splitlines():
        r = json.loads(line)
        bucket = pending.setdefault((r.get("tag", ""), r["pid"]), [])
        if r["kind"] != "op":
            bucket.append(r)
            continue
        lean = [c for c in bucket if c["kind"] in ("oneshot", "service", "spawn")]
        rust = [c for c in bucket if c["kind"] == "rust"]
        print(json.dumps({"tag": r.get("tag", ""), "path": r["path"], "bytes": r["bytes"],
                          "wall_s": round(r["wall"], 3), "python_cpu_s": round(r["python_cpu"], 3),
                          "lean_calls": len(lean), "lean_wall_s": round(sum(c["wall"] for c in lean), 3),
                          "lean_cpu_s": round(sum(c.get("cpu", 0.0) for c in lean), 3),
                          "oneshot": sorted({c["exe"] for c in lean if c["kind"] == "oneshot"}),
                          "rust_calls": len(rust), "rust_cpu_s": round(sum(c["cpu"] for c in rust), 3),
                          "status": r["status"][:80]}))
        bucket.clear()


def report(log: Path, by_caller: bool) -> None:
    records = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
    tags = sorted({r.get("tag", "") for r in records})
    out = {}
    for tag in tags:
        rows = [r for r in records if r.get("tag", "") == tag]
        entry: dict = {"ops": [{k: r[k] for k in ("op", "path", "wall", "python_cpu", "children_cpu",
                                                   "load", "status") if k in r}
                               for r in rows if r["kind"] == "op"]}
        groups: dict = {}
        for r in rows:
            if r["kind"] == "oneshot":
                key = f"oneshot {r['exe']} {' '.join(r['args'])}".strip()
            elif r["kind"] == "service":
                key = f"service {r['mode']}"
            elif r["kind"] in ("spawn", "rust"):
                key = r["kind"]
            else:
                continue
            if by_caller:
                key += f" <- {r.get('caller')}"
            groups.setdefault(key, []).append(r)
        entry["calls"] = {}
        for key, items in sorted(groups.items()):
            stats = _stats([r["wall"] for r in items], [r.get("cpu", 0.0) for r in items])
            cases = [r["cases"] for r in items if r.get("cases") is not None]
            if cases:
                stats["cases"] = sum(cases)
                stats["max_cases"] = max(cases)
            sizes = [r["bytes"] for r in items if r.get("bytes") is not None]
            if sizes:
                stats["max_bytes"] = max(sizes)
            if items[0]["kind"] == "service":
                stats["ipc_sum_s"] = round(sum(r["ipc"] for r in items), 3)
            entry["calls"][key] = stats
        lean = sum(r["wall"] for r in rows if r["kind"] in ("oneshot", "service", "spawn"))
        lean_cpu = sum(r.get("cpu", 0.0) for r in rows if r["kind"] in ("oneshot", "service"))
        rust = sum(r["wall"] for r in rows if r["kind"] == "rust")
        total = sum(r["wall"] for r in rows if r["kind"] == "op")
        entry.update(lean_wall_s=round(lean, 3), lean_cpu_s=round(lean_cpu, 3), rust_wall_s=round(rust, 3),
                     op_wall_s=round(total, 3))
        out[tag] = entry
    print(json.dumps(out, indent=1))


def main(argv=None) -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("startup")
    s.add_argument("--repeats", type=int, default=20)
    sub.add_parser("corpus")
    d = sub.add_parser("document")
    d.add_argument("step", choices=["load", "check", "render"])
    d.add_argument("paths", type=Path, nargs="+")
    d.add_argument("--lean-timeout", type=float)
    d.add_argument("--profile", type=Path, help="cProfile output (one path only)")
    r = sub.add_parser("report")
    r.add_argument("log", type=Path)
    r.add_argument("--by-caller", action="store_true")
    r.add_argument("--by-op", action="store_true", help="one line per document step")
    args = parser.parse_args(argv)
    if args.command == "startup":
        startup(args.repeats)
    elif args.command == "corpus":
        corpus()
    elif args.command == "document":
        for path in args.paths:
            document(args.step, path, args.lean_timeout, args.profile)
    elif args.by_op:
        by_op(args.log)
    else:
        report(args.log, args.by_caller)


if __name__ == "__main__":
    main()
