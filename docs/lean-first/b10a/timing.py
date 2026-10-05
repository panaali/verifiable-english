"""Paired base/head timings for lean-first batch 10a (docs/LEAN-FIRST-PLAN.md 5.1 item 4).

Three measurements, base and head alternating, each run's child CPU (user + system) read
from `os.wait4` around it:

* `ve_norm_defaults_route` on the same input file: the cases the norm-defaults conformance
  harnesses send (the three-way fixtures and spec 8's 1,000 generated trees), captured once
  from this checkout. The new kinds are not in it: they have no base to compare with, and
  their cost is the `report` row below (head only).
* `tools/lean_first_diff.py record --corpus readings` (the readings route's executable
  changed bytes: it imports the edited norm-defaults modules) and `--corpus probe
  --authority lean` (the service's executable changed bytes too), from each checkout.

Usage: python3 docs/lean-first/b10a/timing.py BASE_ROOT [--runs N] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def capture_cases():
    """The cases the norm-defaults harnesses send, in order."""
    from ve.backends import lean as transport
    from conformance import norm_defaults_differential, norm_defaults_three_way
    captured = []
    real = transport.run_norm_defaults_cases

    def recording(executable, cases, **kwargs):
        captured.extend(cases)
        return real(executable, cases, **kwargs)
    transport.run_norm_defaults_cases = recording
    import ve.norm_defaults_route as route
    route.run_norm_defaults_cases = recording
    try:
        norm_defaults_three_way.run()
        norm_defaults_differential.run()
    finally:
        transport.run_norm_defaults_cases = real
        route.run_norm_defaults_cases = real
    return captured


def timed(command, *, cwd, stdin=None, env=None):
    """Wall seconds and child CPU seconds of one command, its output discarded."""
    with open(os.devnull, "wb") as sink:
        start = time.monotonic()
        process = subprocess.Popen(command, cwd=cwd, stdin=stdin or subprocess.DEVNULL, stdout=sink,
                                   stderr=sink, env=env)
        _, status, usage = os.wait4(process.pid, 0)
        wall = time.monotonic() - start
    process.returncode = os.waitstatus_to_exitcode(status)
    return {"wall": round(wall, 2), "cpu": round(usage.ru_utime + usage.ru_stime, 2), "exit": process.returncode}


def load():
    return round(os.getloadavg()[0], 1)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--out", type=Path, default=ROOT / "docs/lean-first/b10a/evidence/timing.json")
    parser.add_argument("--route-only", action="store_true", help="only the ve_norm_defaults_route rows")
    args = parser.parse_args(argv)
    roots = {"base": args.base.resolve(), "head": ROOT}
    env = dict(os.environ, VE_NATIVE_PREBUILT="1", VE_LEAN_PREBUILT="1",
               PATH=str(Path.home() / ".elan/bin") + os.pathsep + os.environ["PATH"])
    cases = capture_cases()
    with tempfile.TemporaryDirectory() as tmp:
        # in the harnesses' chunks of 1,000 cases: the route reads at most 16 MiB of input
        chunks = []
        for start in range(0, len(cases), 1000):
            chunk = Path(tmp) / f"cases-{start}.json"
            chunk.write_text(json.dumps(cases[start:start + 1000], ensure_ascii=False))
            chunks.append(chunk)
        result = {"cases": len(cases), "chunks": len(chunks), "runs": []}
        for run in range(args.runs):
            for side in ("base", "head") if run % 2 == 0 else ("head", "base"):
                binary = roots[side] / "lean/.lake/build/bin/ve_norm_defaults_route"
                row = {"run": run + 1, "side": side, "what": "ve_norm_defaults_route", "load": load(),
                       "wall": 0.0, "cpu": 0.0, "exit": 0}
                for chunk in chunks:
                    one = timed([str(binary), str(chunk)], cwd=tmp)
                    row["wall"] = round(row["wall"] + one["wall"], 2)
                    row["cpu"] = round(row["cpu"] + one["cpu"], 2)
                    row["exit"] = max(row["exit"], one["exit"])
                result["runs"].append(row)
        if args.route_only:
            args.out.write_text(json.dumps(result, indent=1) + "\n")
            print(json.dumps(result, indent=1))
            return
        for corpus, extra in (("readings", []), ("probe", ["--authority", "lean"])):
            for run in range(min(args.runs, 2)):
                for side in ("base", "head") if run % 2 == 0 else ("head", "base"):
                    out = Path(tmp) / f"{side}-{corpus}-{run}.jsonl"
                    row = {"run": run + 1, "side": side, "what": f"record {corpus}", "load": load()}
                    row.update(timed(["uv", "run", "--frozen", "python", "tools/lean_first_diff.py", "record",
                                      "--root", str(roots[side]), "--out", str(out), "--corpus", corpus,
                                      *extra, "--workers", "8"], cwd=ROOT, env=env))
                    result["runs"].append(row)
    args.out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
