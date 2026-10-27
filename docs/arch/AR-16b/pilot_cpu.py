"""AR-16b evidence (not a test): the CPU time of pilot documents through `ve document check`, base and head in
turn, as `tools/lean_first_diff.py record --corpus pilots` checks them (`pilot_documents`, `write_pilot`,
`pilot_check`, the same environment). Each check is one child process tree; its CPU time (user + system, from
`resource.getrusage(RUSAGE_CHILDREN)`, which counts the Lean service and Rust children it waited for) is recorded
with its wall time, and the two sides' outputs are compared as JSON. Rounds alternate base and head, so a change of
the machine's load falls on both sides.

    python docs/arch/AR-16b/pilot_cpu.py --base-root DIR --head-root DIR --case NAME ... [--rounds N] --out FILE
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import lean_first_diff as diff  # noqa: E402


def cpu() -> float:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--head-root", type=Path, required=True)
    parser.add_argument("--case", nargs="+", required=True)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    documents = {name: (blob, text) for name, blob, text in diff.pilot_documents(ROOT)}
    rows = []
    with tempfile.TemporaryDirectory(prefix="ar16b-pilot-cpu-") as scratch:
        for name in args.case:
            blob, text = documents[name]
            row = {"case": name, "source_sha256": blob, "base_cpu": [], "head_cpu": [], "base_wall": [],
                   "head_wall": []}
            outputs = {}
            for k in range(args.rounds):
                for side, root in (("base", args.base_root.resolve()), ("head", args.head_root.resolve())):
                    env = {**os.environ, "PYTHONPATH": str(root),
                           "VE_SHADOW_LOG": str(Path(scratch) / f"{side}-english-shadow.jsonl")}
                    env.pop("VE_AUTHORITY", None)
                    (Path(scratch) / f"{side}{k}").mkdir(exist_ok=True)
                    path = diff.write_pilot(ROOT, Path(scratch) / f"{side}{k}", name, blob, text)
                    before, start = cpu(), time.monotonic()
                    outputs.setdefault(side, []).append(diff.pilot_check(root, path, env))
                    row[f"{side}_cpu"].append(round(cpu() - before, 2))
                    row[f"{side}_wall"].append(round(time.monotonic() - start, 2))
            row["same"] = all(output == outputs["base"][0] for side in outputs for output in outputs[side])
            row["answered"] = all("timeout" not in output for side in outputs for output in outputs[side])
            row["cpu_ratio_of_minimums"] = round(min(row["head_cpu"]) / min(row["base_cpu"]), 3)
            rows.append(row)
            print(json.dumps(row), flush=True)
    args.out.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
    return 0 if all(row["same"] and row["answered"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
