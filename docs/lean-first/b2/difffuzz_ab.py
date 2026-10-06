"""The differential fuzzer at the base and the head of lean-first batch 2 (gate item 2: its baseline must
not grow).

    uv run --frozen python docs/lean-first/b2/difffuzz_ab.py --base ../ve-lf-2-base --out difffuzz.json

Runs `tools/difffuzz.py --ci` and `--deep 1 --seed D` for the 14 date seeds of `SEEDS` in each checkout
(its own `ve`, Lean and Rust builds), `--jobs` runs at a time, and compares each pair of reports: the
findings by signature, the new signatures and the baseline entries seen and not reproduced. The run
fails unless every pair is equal and the head has no new signature the base lacks.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import tempfile

HEAD = Path(__file__).resolve().parents[3]
SEEDS = [f"202609{day}" for day in range(23, 31)] + [f"202610{day:02d}" for day in range(1, 7)]


def _run(root: Path, args: list[str], report: Path) -> dict:
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    proc = subprocess.run(["uv", "run", "--frozen", "python", "tools/difffuzz.py", *args, "--report", str(report)],
                          cwd=root, env=env, capture_output=True, text=True)
    if not report.exists():
        raise SystemExit(f"{root} {args}: no report (exit {proc.returncode})\n{proc.stdout[-2000:]}{proc.stderr[-2000:]}")
    return json.loads(report.read_text())


def _summary(report: dict) -> dict:
    baseline = report["baseline"]
    return {"findings": report["findings"], "new": report["new"],
            "baseline_seen": baseline.get("seen_in_sample"), "not_reproduced": baseline.get("not_reproduced"),
            "unreviewed": baseline.get("unreviewed")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=6)
    args = parser.parse_args()
    runs = [["--ci"]] + [["--deep", "1", "--seed", seed] for seed in SEEDS]
    scratch = Path(tempfile.mkdtemp(prefix="difffuzz-ab-"))
    jobs = [(side, root, run) for run in runs for side, root in (("base", args.base.resolve()), ("head", HEAD))]
    with ThreadPoolExecutor(args.jobs) as pool:
        reports = list(pool.map(lambda job: _run(job[1], job[2], scratch / f"{job[0]}-{'-'.join(job[2])}.json"),
                                jobs))
    rows, ok = [], True
    for index, run in enumerate(runs):
        base, head = _summary(reports[2 * index]), _summary(reports[2 * index + 1])
        new_base, new_head = json.dumps(base["new"], sort_keys=True), json.dumps(head["new"], sort_keys=True)
        row = {"run": " ".join(run), "findings_equal": base["findings"] == head["findings"],
               "same_new": new_base == new_head,
               "new": [base["new"] if isinstance(base["new"], int) else len(base["new"]),
                       head["new"] if isinstance(head["new"], int) else len(head["new"])],
               "baseline_seen": [base["baseline_seen"], head["baseline_seen"]],
               "not_reproduced": [len(base["not_reproduced"] or []), len(head["not_reproduced"] or [])],
               "unreviewed": [len(base["unreviewed"] or []), len(head["unreviewed"] or [])],
               "cpu_seconds": [reports[2 * index]["cpu_seconds"], reports[2 * index + 1]["cpu_seconds"]]}
        row["equal"] = (row["findings_equal"] and row["same_new"] and row["baseline_seen"][0] == row["baseline_seen"][1]
                        and base["not_reproduced"] == head["not_reproduced"] and base["unreviewed"] == head["unreviewed"])
        ok &= row["equal"]
        rows.append(row)
    args.out.write_text(json.dumps({"base": str(args.base), "head": str(HEAD), "runs": rows, "all_equal": ok},
                                   indent=1) + "\n")
    print(json.dumps({"all_equal": ok, "runs": [(r["run"], r["equal"], r["new"], r["baseline_seen"]) for r in rows]},
                     indent=1))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
