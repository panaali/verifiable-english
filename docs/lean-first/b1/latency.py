"""`ve document check` wall and CPU time at two checkouts (lean-first batch 1, gate item 4).

    python docs/lean-first/b1/latency.py BASE_ROOT HEAD_ROOT DOCUMENT... [--runs N]

Each document is checked N times by each checkout's `ve` (`python -m ve document check`, the checkout's own
sources and builds), alternating the two; the CPU time is the process tree's (`ve`, its Lean and Rust
children), read from RUSAGE_CHILDREN.

The report is one row per document argument, in order, named by the path as given: two documents with the
same file name in different directories are two rows, never one in place of the other. Exit 0 only when
every document's output (exit status and standard output) is the same at both checkouts on every run and is
not empty; 1 otherwise. Exit 2, before anything runs, when BASE_ROOT and HEAD_ROOT are the
same directory, either is not a checkout of `ve`, a document is missing or --runs is below 1.
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
    problem = unusable(args)
    if problem:
        print(f"latency: {problem}", file=sys.stderr)
        return 2
    report = []
    for document in args.documents:
        runs = {"base": [], "head": []}
        outputs = {"base": set(), "head": set()}
        for _ in range(args.runs):
            for side in ("base", "head"):
                wall, cpu, code, stdout = check(getattr(args, side), document.resolve())
                runs[side].append((wall, cpu))
                outputs[side].add((code, stdout))
        report.append({"document": str(document),
                       **{side: {"wall_median": round(statistics.median(w for w, _ in r), 3),
                                 "cpu_median": round(statistics.median(c for _, c in r), 3)}
                          for side, r in runs.items()},
                       "same_output": same_output(outputs)})
    print(json.dumps(report, indent=2))
    return 0 if all(row["same_output"] for row in report) else 1


def unusable(args) -> str | None:
    """Why the inputs cannot show a latency comparison, or None."""
    if args.runs < 1:
        return "--runs must be at least 1"
    if args.base.resolve() == args.head.resolve():
        return f"BASE_ROOT and HEAD_ROOT are the same directory {args.base}"
    for root in (args.base, args.head):
        if not (root / "ve" / "__init__.py").is_file():
            return f"{root} is not a checkout of ve"
    missing = [str(d) for d in args.documents if not d.is_file()]
    return f"no document {', '.join(missing)}" if missing else None


def same_output(outputs) -> bool:
    """Every run of both checkouts gave one and the same nonempty output."""
    return len(outputs["base"]) == 1 and outputs["base"] == outputs["head"] and bool(next(iter(outputs["base"]))[1])


if __name__ == "__main__":
    sys.exit(main())
