"""Paired batch-12 latency of the UDHR document and eligibility harness.

    python docs/lean-first/b12/latency.py BASE_ROOT DOCUMENT OUT_JSON

Three UDHR runs alternate base and head. The eligibility harness runs once per
side, as in batch 9's same-host measurement. The document is a historical UDHR
pilot blob extracted to a temporary file before this script is called. A prior
eligibility measurement can be carried forward when correcting the UDHR blob.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import time

HEAD = Path(__file__).resolve().parents[3]


def check(root: Path, operation: str, document: Path) -> dict:
    command = ([sys.executable, "-m", "ve", "document", "check", str(document)] if operation == "udhr"
               else [sys.executable, "usecases/eligibility/run.py", "--no-write"])
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    done = subprocess.run(command, cwd=root, env={**os.environ, "PYTHONPATH": str(root)},
                          capture_output=True, check=False)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
    return {"wall_s": wall, "cpu_s": cpu, "exit": done.returncode,
            "stdout_sha256": hashlib.sha256(done.stdout).hexdigest(),
            "stdout_bytes": len(done.stdout), "stderr": done.stderr.decode("utf-8", "replace")[-500:]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("base", type=Path)
    parser.add_argument("document", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--reuse-eligibility", type=Path)
    args = parser.parse_args()
    roots = {"base": args.base.resolve(), "head": HEAD}
    if roots["base"] == HEAD or not args.document.is_file():
        parser.error("a distinct base checkout and an existing UDHR document are required")
    rows = (json.loads(args.reuse_eligibility.read_text()) if args.reuse_eligibility else {})
    for operation in ("udhr", "eligibility"):
        if operation == "eligibility" and args.reuse_eligibility:
            if not rows[operation]["same_output"] or not rows[operation]["within_budget"]:
                parser.error("reused eligibility measurement did not pass")
            continue
        runs = {"base": [], "head": []}
        for _ in range(3 if operation == "udhr" else 1):
            for side, root in roots.items():
                runs[side].append(check(root, operation, args.document.resolve()))
        output = {(row["exit"], row["stdout_sha256"], row["stdout_bytes"])
                  for side in runs for row in runs[side]}
        medians = {side: {"wall_s": statistics.median(row["wall_s"] for row in runs[side]),
                          "cpu_s": statistics.median(row["cpu_s"] for row in runs[side])}
                   for side in runs}
        ratio = medians["head"]["wall_s"] / medians["base"]["wall_s"]
        cpu_ratio = medians["head"]["cpu_s"] / medians["base"]["cpu_s"]
        rows[operation] = {"runs": runs, "median": medians, "wall_ratio": ratio,
                           "child_cpu_ratio": cpu_ratio,
                           **({"document_sha256": hashlib.sha256(args.document.read_bytes()).hexdigest()}
                              if operation == "udhr" else {}),
                           "same_output": len(output) == 1 and next(iter(output))[0] == 0
                           and next(iter(output))[2] > 0,
                           "within_budget": ratio <= 1.25 and
                           (operation != "udhr" or medians["head"]["wall_s"] <= 120)}
    args.out.write_text(json.dumps(rows, indent=1) + "\n")
    print(json.dumps({op: {key: value for key, value in row.items() if key != "runs"}
                      for op, row in rows.items()}, indent=1))
    return 0 if all(row["same_output"] and row["within_budget"] for row in rows.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
