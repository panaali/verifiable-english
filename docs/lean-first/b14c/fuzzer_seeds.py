"""Run the fourteen dated CI differential samples on this batch's final code.

Usage: uv run python docs/lean-first/b14c/fuzzer_seeds.py OUT_DIRECTORY SUMMARY_JSON
Each child completes before the summary is written. The same reviewed baseline
is checked on every seed; new signatures are passed to date_seed_replay.py for
the base/head comparison. A missing report or baseline change fails collection.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
SEEDS = tuple(range(20260921, 20260931)) + tuple(range(20261001, 20261005))


def one(seed: int, scratch: Path) -> dict:
    report = scratch / f"{seed}.json"
    log = scratch / f"{seed}.log"
    if report.is_file():
        data = json.loads(report.read_text())
        if data.get("seed") == seed and type(data.get("passed")) is bool:
            return {"seed": seed, "exit_code": 0 if data["passed"] else 1,
                    "passed": data["passed"],
                    "new": len(data["new"]), "baseline_entries": data["baseline"]["entries"],
                    "sampled": data["mutants"]}
    with log.open("w") as output:
        done = subprocess.run([sys.executable, "tools/difffuzz.py", "--ci", "--seed", str(seed),
                               "--report", str(report), "--minimise-limit", "0"], cwd=ROOT, stdout=output,
                              stderr=subprocess.STDOUT, check=False)
    if not report.is_file():
        return {"seed": seed, "exit_code": done.returncode, "passed": False,
                "error": log.read_text(errors="replace")[-500:]}
    data = json.loads(report.read_text())
    return {"seed": seed, "exit_code": done.returncode, "passed": data["passed"],
            "new": len(data["new"]), "baseline_entries": data["baseline"]["entries"],
            "sampled": data["mutants"]}


def main() -> int:
    scratch, summary = map(Path, sys.argv[1:])
    scratch.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = sorted(pool.map(lambda seed: one(seed, scratch), SEEDS), key=lambda row: row["seed"])
    good = len(rows) == len(SEEDS) and all(row["exit_code"] in (0, 1) and
                                             row.get("baseline_entries") == 250 for row in rows)
    summary.write_text(json.dumps({"complete": good, "seeds": rows}, indent=2, sort_keys=True) + "\n")
    print(f"{len(rows)}/{len(SEEDS)} date seeds recorded; "
          f"{sum(row.get('new', 0) for row in rows)} signatures require base replay")
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
