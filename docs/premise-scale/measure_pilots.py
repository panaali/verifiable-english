"""Measure the premise check on the premise-scale pilots (time, memory, premise status).

Each pilot runs `check_document` in a fresh process under the pilots' address-space cap
(`prlimit --as=6442450944`), and the row records the wall time, the peak resident memory of
the Python process and of its largest checker child, and the premise status. The "before"
side runs the same Python with the binary of the merge base (`--rust` and `--rust-sha256`).

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
print(json.dumps({"premises": premises, "error": error, "check_seconds": round(wall, 2),
                  "python_peak_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024}))
"""


def measure(path: Path, env: dict, cap: int) -> dict:
    start = time.monotonic()
    proc = subprocess.run(["prlimit", f"--as={cap}", sys.executable, "-c", INNER, str(path)],
                          capture_output=True, text=True, env=env, cwd=ROOT)
    wall = time.monotonic() - start
    import resource
    row = {"pilot": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
           "bytes": path.stat().st_size, "exit": proc.returncode, "wall_seconds": round(wall, 2),
           "children_peak_mb": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss // 1024}
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
    parser.add_argument("pilots", nargs="+", type=lambda p: Path(p).resolve())
    args = parser.parse_args()
    env = {k: v for k, v in os.environ.items() if k not in ("VE_RUST_TIMEOUT", "VE_RUST_JSONL", "VE_RUST_SHA256")}
    if args.rust:
        env["VE_RUST_JSONL"], env["VE_RUST_SHA256"] = args.rust, args.rust_sha256
    if args.rust_timeout:
        env["VE_RUST_TIMEOUT"] = args.rust_timeout
    rows = []
    for path in args.pilots:
        # One wrapper process per pilot, so its children's peak memory is that pilot's alone.
        single = subprocess.run([sys.executable, __file__, "--single", str(args.cap), str(path)],
                                capture_output=True, text=True, env=env, check=True)
        row = json.loads(single.stdout)
        row["label"] = args.label
        row["rust_timeout"] = args.rust_timeout or "default"
        print(json.dumps({k: row[k] for k in ("pilot", "status", "wall_seconds", "children_peak_mb", "error")
                          if k in row}), flush=True)
        rows.append(row)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--single"]:
        print(json.dumps(measure(Path(sys.argv[3]), dict(os.environ), int(sys.argv[2]))))
    else:
        main()
