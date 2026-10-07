"""Verify batch 10b's evidence and print the numbers `DELTA.md` reports.

`evidence()` reads only committed files (A/B comparisons, fourteen-seed fuzzer
evidence, timing) and the Git diff against the base; the report test calls it.
`--gate` adds the full-suite gate JSON, which is written outside the checkout
because it names the commit it ran on.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).with_name("evidence")
BASE = "7345e3ed"
CORPORA = {"core": 58482, "norm": 2020, "profiles": 35713, "pilots": 294}


def _json(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text())


def lines() -> dict:
    """Python lines deleted under `ve/` and Lean lines added under `lean/`, against the base."""
    out = subprocess.check_output(["git", "diff", "--numstat", f"{BASE}..HEAD"], cwd=ROOT, text=True)
    totals = {"python_deleted": 0, "python_added": 0, "lean_added": 0, "lean_deleted": 0}
    for row in out.splitlines():
        added, deleted, path = row.split("\t")
        if path.startswith("ve/") and path.endswith(".py"):
            totals["python_deleted"] += int(deleted)
            totals["python_added"] += int(added)
        if path.startswith("lean/") and path.endswith(".lean"):
            totals["lean_added"] += int(added)
            totals["lean_deleted"] += int(deleted)
    return totals


def evidence() -> dict:
    recordings = _json("ab-recordings.json")["recordings_sha256"]
    ab = {}
    for name, expected in CORPORA.items():
        row = _json(f"ab-{name}-compare.json")
        assert sum(row["records"].values()) == row["totals"]["same"] == expected and set(row["totals"]) == {"same"}
        assert row["unavailable_both"] == {} and row["unlisted"] == 0 and row["differences"] == []
        assert recordings[name]["base"] == recordings[name]["head"]
        ab[name] = expected
    fuzz = _json("fuzzer-seeds.json")
    assert fuzz["base_commit"].startswith(BASE) and len(fuzz["seeds"]) == 14
    assert all(not seed["unexplained"] for seed in fuzz["seeds"])
    kinds: dict[str, int] = {}
    for seed in fuzz["seeds"]:
        for row in seed["explained"]:
            kind = row.get("kind") or ("unmasked" if "unmasked" in row else "retired replay")
            kinds[kind] = kinds.get(kind, 0) + 1
    timing = _json("timing.json")["runs"]
    assert all(run["exit"] == 0 for run in timing)
    mean = {side: {key: round(sum(r[key] for r in timing if r["side"] == side) / 2, 2) for key in ("wall", "user")}
            for side in ("base", "head")}
    return {"ab_same": ab, "date_seeds": len(fuzz["seeds"]), "fuzzer_explained": dict(sorted(kinds.items())),
            "head_only_findings": sum(seed["head_new"] - seed["base_new"] + seed["base_only_new"]
                                      for seed in fuzz["seeds"]),
            "timing_mean": mean, "lines": lines()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", type=Path)
    args = parser.parse_args()
    report = evidence()
    if args.gate:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        gate = json.loads(args.gate.read_text())
        assert gate["status"] == "passed" and gate["commit_sha"] == head and not gate["dirty"]
        assert gate["counts"].get("failed", 0) == 0
        report["gate"] = {"commit": head, "status": gate["status"], "counts": gate["counts"]}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
