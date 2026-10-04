"""`ve document check` wall and CPU time at two checkouts (lean-first batch 1, gate item 4).

    python docs/lean-first/b1/latency.py BASE_ROOT HEAD_ROOT DOCUMENT... [--runs N]

Each document is checked N times by each checkout's `ve` (`python -m ve document check`, the checkout's own
sources and builds), alternating the two; the CPU time is the process tree's (`ve`, its Lean and Rust
children), read from RUSAGE_CHILDREN.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import time


def check(root, document):
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.perf_counter()
    done = subprocess.run([sys.executable, "-m", "ve", "document", "check", str(document)], cwd=root,
                          env={**os.environ, "PYTHONPATH": str(root)}, capture_output=True, text=True)
    wall = time.perf_counter() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = after.ru_utime + after.ru_stime - usage.ru_utime - usage.ru_stime
    return wall, cpu, done.returncode, done.stdout


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("base", type=Path)
    parser.add_argument("head", type=Path)
    parser.add_argument("documents", nargs="+", type=Path)
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args(argv)
    report = {}
    for document in args.documents:
        runs = {"base": [], "head": []}
        outputs = {}
        for _ in range(args.runs):
            for side in ("base", "head"):
                wall, cpu, code, stdout = check(getattr(args, side), document.resolve())
                runs[side].append((wall, cpu))
                outputs[side] = (code, stdout)
        report[document.name] = {side: {"wall_median": round(statistics.median(w for w, _ in r), 3),
                                        "cpu_median": round(statistics.median(c for _, c in r), 3)}
                                 for side, r in runs.items()}
        report[document.name]["same_output"] = outputs["base"] == outputs["head"]
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
