"""Measure the premise check on the premise-scale pilots (time, memory, premise status).

Each pilot runs `check_document` in a fresh process under the pilots' address-space cap
(`prlimit --as=6442450944`), and the row records the wall time, the premise status and its
answer, the CPU time of the check and every process it waited for (the Lean service included:
it is closed and waited at exit), and peak resident memory: the Python process (`python_peak_mb`), the largest process
that ended and was waited for, a Rust or one-shot Lean checker (`children_peak_mb`), and the
processes still running at the end, the persistent Lean service and Rust checkers (their
VmHWM: `live_children_peak_mb`, the largest, and `live_children_peak_sum_mb`). The "before"
side runs a checkout of this branch before its change (`--root`, with its own Lean and Rust
builds).

    uv run python docs/premise-scale/measure_pilots.py --label after --out evidence/after.json PILOT...
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INNER = r"""
import json, resource, sys, time
from ve.document import check_document
start = time.monotonic()
try:
    premises = check_document(sys.argv[1]).get("premises")
    error = None
except Exception as exc:  # the row records the failure; the measurement goes on
    premises, error = None, f"{type(exc).__name__}: {str(exc)[:300]}"
wall = time.monotonic() - start


def descendants(pid):
    import os
    out = []
    for tid in os.listdir(f"/proc/{pid}/task"):
        try:
            children = open(f"/proc/{pid}/task/{tid}/children").read().split()
        except OSError:
            continue
        for child in map(int, children):
            out += [child, *descendants(child)]
    return out


def peak_mb(pid):
    try:
        for line in open(f"/proc/{pid}/status"):
            if line.startswith("VmHWM:"):
                return int(line.split()[1]) // 1024
    except OSError:
        pass
    return 0


import os
live = descendants(os.getpid())  # the persistent Lean service and Rust processes, still running
print(json.dumps({"premises": premises, "error": error, "check_seconds": round(wall, 2),
                  "python_peak_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
                  "live_children_peak_mb": max(map(peak_mb, live), default=0),
                  "live_children_peak_sum_mb": sum(map(peak_mb, live))}))
"""


def measure(path: Path, env: dict, cap: int, root: Path) -> dict:
    start = time.monotonic()
    proc = subprocess.run(["prlimit", f"--as={cap}", sys.executable, "-c", INNER, str(path)],
                          capture_output=True, text=True, env=env, cwd=root)
    wall = time.monotonic() - start
    import resource
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    row = {"pilot": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
           "bytes": path.stat().st_size, "exit": proc.returncode, "wall_seconds": round(wall, 2),
           "cpu_seconds": round(children.ru_utime + children.ru_stime, 2),
           "children_peak_mb": children.ru_maxrss // 1024}
    lines = proc.stdout.strip().splitlines()
    try:
        row.update(json.loads(lines[-1]))
    except (IndexError, ValueError):
        row["error"] = (proc.stderr or proc.stdout)[-400:]
    premises = row.get("premises")
    row["status"] = premises.get("status") if isinstance(premises, dict) else None
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--rust", help="the Rust binary to run (VE_RUST_JSONL)")
    parser.add_argument("--rust-sha256", help="its SHA-256 (VE_RUST_SHA256)")
    parser.add_argument("--rust-timeout", help="VE_RUST_TIMEOUT for this run (default: unset)")
    parser.add_argument("--cap", type=int, default=6442450944)
    parser.add_argument("--repeat", type=int, default=1, help="runs of each pilot, one row each")
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="the checkout whose `ve` runs (the before side: a worktree at the merge base)")
    parser.add_argument("--record", help="a directory: each pilot's Rust case lines go to <pilot>.cases.jsonl")
    parser.add_argument("pilots", nargs="+", type=lambda p: Path(p).resolve())
    args = parser.parse_args()
    env = {k: v for k, v in os.environ.items() if k not in ("VE_RUST_TIMEOUT", "VE_RUST_JSONL", "VE_RUST_SHA256")}
    if args.rust:
        env["VE_RUST_JSONL"], env["VE_RUST_SHA256"] = args.rust, args.rust_sha256
    if args.rust_timeout:
        env["VE_RUST_TIMEOUT"] = args.rust_timeout
    root = args.root.resolve()
    binary = Path(env.get("VE_RUST_JSONL") or root / "rust/target/release/ve").resolve()
    rows = []
    for path in [p for p in args.pilots for _ in range(args.repeat)]:
        if args.record:
            # A pass-through wrapper: the case lines are copied to the record, the binary answers them.
            record = Path(args.record).resolve() / f"{path.name}.cases.jsonl"
            record.parent.mkdir(parents=True, exist_ok=True)
            record.write_text("")
            wrapper = record.with_suffix(".sh")
            wrapper.write_text(f"#!/bin/sh\nexec tee -a '{record}' | '{binary}' \"$@\"\n")
            wrapper.chmod(0o755)
            env["VE_RUST_JSONL"] = str(wrapper)
            env["VE_RUST_SHA256"] = hashlib.sha256(wrapper.read_bytes()).hexdigest()
        # One wrapper process per pilot, so its children's peak memory is that pilot's alone.
        single = subprocess.run([sys.executable, __file__, "--single", str(args.cap), str(root), str(path)],
                                capture_output=True, text=True, env=env, check=True)
        row = json.loads(single.stdout)
        row["label"] = args.label
        row["rust_timeout"] = args.rust_timeout or "default"
        row["root"] = str(root)
        print(json.dumps({k: row[k] for k in ("pilot", "status", "wall_seconds", "cpu_seconds", "children_peak_mb", "error")
                          if k in row}), flush=True)
        rows.append(row)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--single"]:
        print(json.dumps(measure(Path(sys.argv[4]), dict(os.environ), int(sys.argv[2]), Path(sys.argv[3]))))
    else:
        main()
