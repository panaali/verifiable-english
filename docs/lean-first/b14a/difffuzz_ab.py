"""The differential fuzzer at the base and the head of lean-first batch 14a (gate item 2: its baseline must
not grow).

    python docs/lean-first/b14a/difffuzz_ab.py --base /tmp/lf14a-base --out docs/lean-first/b14a/evidence/difffuzz-ab.json

Runs `tools/difffuzz.py --ci` and `--deep 1 --seed D` for the 14 date seeds of `SEEDS` in each checkout (its
own `ve`, baseline, Lean and Rust builds, `VE_NATIVE_PREBUILT=1`, `VE_RUST_BINARY`), `--jobs` runs at a time. For every run it
records the findings by surface and profile, the new signatures of each side and the
**head-only** new signatures with their answers. A base-reviewed signature is
not head-only when its minimized entry was removed from the smaller head baseline.
The run fails when the head has a head-only signature, a
baseline entry it does not reproduce, or an unreviewed entry.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HEAD = Path(__file__).resolve().parents[3]
SEEDS = [f"202609{day}" for day in range(29, 31)] + [f"202610{day:02d}" for day in range(1, 13)]


def _run(root: Path, args: list[str], report: Path) -> dict:
    env = {**os.environ, "VE_NATIVE_PREBUILT": "1", "PYTHONPATH": str(root),
           "VE_RUST_BINARY": str(root / "rust/target/release/ve"),
           "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}
    proc = subprocess.run([sys.executable, "tools/difffuzz.py", *args, "--minimise-limit", "0",
                           "--report", str(report)], cwd=root, env=env, capture_output=True, text=True)
    if not report.exists():
        raise SystemExit(f"{root} {args}: no report (exit {proc.returncode})\n{proc.stdout[-2000:]}{proc.stderr[-2000:]}")
    return json.loads(report.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--reuse-base", type=Path,
                        help="reuse the base reports of a previous run with the same checkout and seeds")
    parser.add_argument("--reuse-head", type=Path,
                        help="reuse the head reports of a previous run with the same checkout and seeds")
    args = parser.parse_args()
    base_known = {entry["signature"] for entry in json.loads(
        (args.base / "conformance/difffuzz-baseline.json").read_text())["entries"]}
    runs = [["--ci"]] + [["--deep", "1", "--seed", seed] for seed in SEEDS]
    scratch = Path(tempfile.mkdtemp(prefix="difffuzz-ab-b14a-"))
    jobs = [(side, root, run) for run in runs for side, root in (("base", args.base.resolve()), ("head", HEAD))]
    def run_job(job):
        side, root, run = job
        name = f"{side}-{'-'.join(run)}.json"
        if side == "base" and args.reuse_base is not None:
            return json.loads((args.reuse_base / name).read_text())
        if side == "head" and args.reuse_head is not None:
            return json.loads((args.reuse_head / name).read_text())
        return _run(root, run, scratch / name)
    with ThreadPoolExecutor(args.jobs) as pool:
        reports = list(pool.map(run_job, jobs))
    rows, ok = [], True
    for index, run in enumerate(runs):
        base, head = reports[2 * index], reports[2 * index + 1]
        base_new = {entry["signature"] for entry in base["new"]}
        head_only = [{"signature": entry["signature"], "surface": entry["surface"], "profile": entry["profile"],
                      "seed": entry["seed"], "classes": entry["classes"], "answers": entry["answers"],
                      "input": entry["input"]}
                     for entry in head["new"] if entry["signature"] not in base_new | base_known]
        row = {"run": " ".join(run),
               "findings": [base["findings"], head["findings"]],
               "new": [len(base["new"]), len(head["new"])],
               "base_only_new": sorted(base_new - {entry["signature"] for entry in head["new"]}),
               "head_only_new": head_only,
               "baseline": [{k: (len(v) if isinstance(v, list) else v) for k, v in side["baseline"].items()}
                            for side in (base, head)],
               "head_not_reproduced": head["baseline"]["not_reproduced"],
               "cpu_seconds": [base["cpu_seconds"], head["cpu_seconds"]]}
        row["ok"] = not head_only and not head["baseline"]["not_reproduced"] and not head["baseline"]["unreviewed"]
        ok &= row["ok"]
        rows.append(row)
    args.out.write_text(json.dumps({"base": str(args.base), "head": str(HEAD), "runs": rows, "ok": ok},
                                   indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": ok, "runs": [(r["run"], r["ok"], r["new"], len(r["head_only_new"]),
                                          r["baseline"][0]["entries"], r["baseline"][1]["entries"]) for r in rows]},
                     indent=1))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
