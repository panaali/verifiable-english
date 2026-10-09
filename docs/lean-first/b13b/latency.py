"""Paired batch-13b latency of the UDHR document, the eligibility harness and the agent-policy harness.

    python docs/lean-first/b13b/latency.py BASE_ROOT DOCUMENT OUT_JSON

Three UDHR runs and three agent-policy runs (`check.py base`, the part whose typing, Background and
admission calls 13b moves to Lean; its own timings are normalised before the outputs are compared) alternate
base and head; the eligibility harness (`--no-write`) runs once per side, as in batch 9's same-host
measurement. Section 4's budget: each at most 1.25x the base wall, the UDHR document at most 120 s. The document is a historical UDHR
pilot blob extracted to a temporary file before this script is called. A prior
eligibility measurement can be carried forward when correcting the UDHR blob.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import time

HEAD = Path(__file__).resolve().parents[3]


def check(root: Path, operation: str, document: Path) -> dict:
    command = {"udhr": [sys.executable, "-m", "ve", "document", "check", str(document)],
               "eligibility": [sys.executable, "usecases/eligibility/run.py", "--no-write"],
               "agent-policy": [sys.executable, "usecases/agent-policy/check.py", "base"]}[operation]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    done = subprocess.run(command, cwd=root, env={**os.environ, "PYTHONPATH": str(root),
                                                  "VE_RUST_BINARY": str(root / "rust/target/release/ve")},
                          capture_output=True, check=False)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
    # The agent-policy report ends with its own timings; every decimal in it is one (normalised before hashing).
    stdout = re.sub(rb"[0-9]+\.[0-9]+", b"<s>", done.stdout) if operation == "agent-policy" else done.stdout
    return {"wall_s": wall, "cpu_s": cpu, "exit": done.returncode,
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stdout_bytes": len(stdout), "stderr": done.stderr.decode("utf-8", "replace")[-500:]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("base", type=Path)
    parser.add_argument("document", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--reuse-eligibility", type=Path)
    parser.add_argument("--reuse", type=Path, help="keep these operations' rows from a previous run's JSON")
    parser.add_argument("--keep", nargs="*", default=(), help="the operations kept from --reuse")
    args = parser.parse_args()
    roots = {"base": args.base.resolve(), "head": HEAD}
    if roots["base"] == HEAD or not args.document.is_file():
        parser.error("a distinct base checkout and an existing UDHR document are required")
    rows = (json.loads(args.reuse_eligibility.read_text()) if args.reuse_eligibility else {})
    if args.reuse:
        previous = json.loads(args.reuse.read_text())
        rows.update({operation: previous[operation] for operation in args.keep})
    for operation in ("udhr", "eligibility", "agent-policy"):
        if operation in args.keep:
            continue
        if operation == "eligibility" and args.reuse_eligibility:
            if not rows[operation]["same_output"] or not rows[operation]["within_budget"]:
                parser.error("reused eligibility measurement did not pass")
            continue
        runs = {"base": [], "head": []}
        for _ in range(1 if operation == "eligibility" else 3):
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
