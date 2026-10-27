"""eff-20261027-1 evidence check: recompute every row of evidence.json from the saved runs (runs/*.json).

    python3 docs/infra/eff-20261027-1/check.py

Exits nonzero when a row is missing, not `pass`, or disagrees with the runs it cites: the medians, the peak RSS
sums, the stop rule (the median cold dump at least 60 s faster, the parts' RSS within lean/audit.py's, every
output equal on the three trees) and the cold-dump budget. Reads saved evidence only (no git, no Lean).
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import median
import sys

HERE = Path(__file__).resolve().parent
ROWS = ("M1", "M2", "M3", "E1", "E2", "E3", "S1", "S2", "S3", "S4")


def main() -> int:
    evidence = json.loads((HERE / "evidence.json").read_text())
    runs = {path.stem: json.loads(path.read_text()) for path in sorted((HERE / "runs").glob("*.json"))}
    rows = {row["id"]: row for row in evidence["rows"]}
    problems = []

    def need(condition: bool, row: str, message: str) -> None:
        if not condition:
            problems.append(f"{row}: {message}")

    for name in ROWS:
        need(name in rows, name, "missing")
        need(rows.get(name, {}).get("status") == "pass", name, f"status {rows.get(name, {}).get('status')!r}")
    if problems:
        return report(problems)
    for row in rows.values():
        for run in row.get("runs", ()):
            need(run in runs, row["id"], f"run {run} not saved")
    if problems:
        return report(problems)

    serial = [runs[r] for r in rows["M1"]["runs"]]
    split = [runs[r] for r in rows["M3"]["runs"]]
    need(len(serial) == 3 and all(r["mode"] == "serial" for r in serial), "M1", "not 3 serial runs")
    need(len(split) == 3 and all(r["mode"] == "split" and r["parts"] == 8 for r in split), "M3", "not 3 split runs")
    trees = evidence["trees"]
    need(all(r["head"] == trees["main"]["commit"] for r in serial + split), "M1", "a run is not of main")
    need(all("load_before" in r and "load_after" in r for r in runs.values()), "M1", "a run has no load")
    for row, group in (("M1", serial), ("M3", split)):
        need(median(r["total_seconds"] for r in group) == rows[row]["median_total_seconds"], row, "median total")
        need(median(r["statements_seconds"] for r in group) == rows[row]["median_statements_seconds"], row,
             "median Statements")
    need(max(r["statements_peak_rss_kb_max"] for r in serial) == rows["M1"]["statements_peak_rss_kb_max"], "M1",
         "serial peak RSS")
    need(max(r["statements_peak_rss_kb_sum"] for r in split) == rows["M3"]["statements_peak_rss_kb_sum_max"], "M3",
         "split peak RSS")
    audit = runs["main-audit"]
    need(audit["parts"] == rows["M2"]["parts"] and audit["parts_peak_rss_kb_sum"] == rows["M2"]["parts_peak_rss_kb_sum"],
         "M2", "audit parts or RSS")

    files = evidence["output_sha256"]
    for name in ("E1", "E2", "E3"):
        row = rows[name]
        tree = trees[row["tree"]]["commit"]
        for run in row["runs"]:
            need(runs[run]["head"] == tree, name, f"{run} is not of {tree}")
            need(runs[run]["matches_committed"] == [True, True, True], name, f"{run} differs from the committed texts")
        modes = {runs[run]["mode"] for run in row["runs"]}
        need(modes == {"serial", "split"}, name, f"modes {sorted(modes)}")
        first, second = row["hashes"]
        need(files[first] == files[second] == evidence["committed_sha256"][row["tree"]], name,
             f"{first} and {second} differ")
    need(len({trees[t]["commit"] for t in trees}) == 3, "E1", "the three trees are not distinct")

    saved = round(median(r["total_seconds"] for r in serial) - median(r["total_seconds"] for r in split), 1)
    need(saved == rows["S1"]["saved_seconds"], "S1", f"saved {saved} s")
    need(saved >= rows["S1"]["threshold_seconds"] == 60, "S1", f"saved {saved} s < 60 s")
    # Comparable load: the split runs started at a median load at least 0.8 times that of the serial ones.
    need(median(r["load_before"][0] for r in split) >= median(r["load_before"][0] for r in serial) * 0.8, "S1",
         "the split runs ran at a much lower load")
    split_kb = max(runs[r]["statements_peak_rss_kb_sum"] for r in runs if runs[r].get("mode") == "split")
    need(split_kb == rows["S2"]["split_kb"] and split_kb <= rows["S2"]["audit_kb"] == audit["parts_peak_rss_kb_sum"],
         "S2", f"split {split_kb} KB against the audit's {audit['parts_peak_rss_kb_sum']} KB")
    need(all(r["matches_committed"] == [True, True, True] for r in runs.values() if "matches_committed" in r), "S3",
         "an output differs")
    dumps = sum(1 for r in runs.values() if "mode" in r)
    need(dumps == rows["S4"]["cold_dumps"] <= evidence["cold_dump_budget"], "S4", f"{dumps} cold dumps")
    return report(problems)


def report(problems: list[str]) -> int:
    for problem in problems:
        print(f"FAIL {problem}")
    if not problems:
        print(f"PASS: {len(ROWS)} rows")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
