"""AR-20 evidence (not a test): re-record pilot documents base and head, as `tools/lean_first_diff.py record
--corpus pilots` records them (`pilot_documents`, `write_pilot`, `pilot_check`, the same environment), for the
records whose A/B outcome was the recorder's time-out on both sides (PIPELINE-LIMITS L75). AR-16a's
`pilot_rerun.py`, with every (case, side) check run at once instead of one after the other. `--timeout`
replaces the recorder's 600 s wall-clock limit for this re-run only; each side's outcome is written as the
recorder writes it, and the two are compared as JSON.

    python docs/arch/AR-20/pilot_rerun.py --base-root DIR --head-root DIR --case NAME ... [--timeout S] --out FILE
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import lean_first_diff as diff  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--head-root", type=Path, required=True)
    parser.add_argument("--case", nargs="+", required=True)
    parser.add_argument("--timeout", type=int, default=diff.PILOT_TIMEOUT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    diff.PILOT_TIMEOUT = args.timeout
    documents = {name: (blob, text) for name, blob, text in diff.pilot_documents(ROOT)}
    roots = {"base": args.base_root.resolve(), "head": args.head_root.resolve()}
    with tempfile.TemporaryDirectory(prefix="ar20-pilot-rerun-") as scratch:
        def check(task):
            index, name, side = task
            blob, text = documents[name]
            folder = Path(scratch) / f"{side}-{index}"
            folder.mkdir()
            env = {**os.environ, "PYTHONPATH": str(roots[side]),
                   "VE_SHADOW_LOG": str(folder / "english-shadow.jsonl")}
            env.pop("VE_AUTHORITY", None)
            path = diff.write_pilot(ROOT, folder, name, blob, text)
            start = time.monotonic()
            outcome = diff.pilot_check(roots[side], path, env)
            return task, outcome, round(time.monotonic() - start)

        tasks = [(i, name, side) for i, name in enumerate(args.case) for side in ("base", "head")]
        with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
            results = list(pool.map(check, tasks))
    rows = []
    for i, name in enumerate(args.case):
        row = {"case": name, "source_sha256": documents[name][0], "timeout": args.timeout}
        for (index, _, side), outcome, seconds in results:
            if index == i:
                row[side], row[f"{side}_seconds"] = outcome, seconds
        row["same"] = row["base"] == row["head"]
        row["answered"] = "timeout" not in row["base"] and "timeout" not in row["head"]
        rows.append(row)
        print(json.dumps({k: v for k, v in row.items() if k not in ("base", "head")}), flush=True)
    args.out.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
    return 0 if all(row["same"] and row["answered"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
