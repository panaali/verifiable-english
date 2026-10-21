#!/usr/bin/env python3
"""Check the stopped efficiency replay; fail on every unmeasured corpus verdict."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main() -> int:
    data = json.loads((HERE / "evidence.json").read_text())
    lean = json.loads((HERE / "lean-only.json").read_text())
    attempt = json.loads((HERE / "pytest-attempt.json").read_text())
    stop = data["stop_rule"]
    bad = []
    if (lean["seconds"], attempt["seconds"], stop["lean_only_seconds"],
            stop["pytest_attempt_seconds"]) != (265, 862, 265, 862):
        bad.append("sweep times disagree")
    if stop["three_times_seconds"] != 3 * lean["seconds"] or attempt["seconds"] <= stop["three_times_seconds"]:
        bad.append("the 3x stop condition does not hold")
    if lean["counts"]["SURVIVOR"] != 30 or attempt["counts"]["KILLED-BY-PYTEST"] != 0:
        bad.append("sweep verdict counts disagree")
    if sum(lean["counts"].values()) != sum(attempt["counts"].values()) or len(data["corpus"]) != 34:
        bad.append("a row is absent")
    for row in data["corpus"]:
        source = subprocess.run(["git", "show", f"{row['reviewed_head']}:{row['file']}"], cwd=ROOT,
                                capture_output=True, text=True, check=False)
        if source.returncode or row["before"] not in source.stdout:
            bad.append(f"{row['item']}/{row['id']}: reviewed source text missing")
        if row["legacy_verdict"] == "UNMEASURED" or row["fixed_verdict"] == "UNMEASURED":
            bad.append(f"{row['item']}/{row['id']}: replay skipped by stop rule")
    for issue in bad:
        print(issue)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
