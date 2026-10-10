"""AR-8's report agrees with its SAVED evidence (fixed base and head commits, never the live tree)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs/architecture/ar-8"
spec = importlib.util.spec_from_file_location("ar8_measure", FOLDER / "measure.py")
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)
EVIDENCE = json.loads((FOLDER / "evidence.json").read_text())


def test_report_table_is_rendered_from_the_saved_evidence():
    report = (FOLDER / "REPORT.md").read_text()
    assert measure.splice(report, measure.render(EVIDENCE)) == report


def test_saved_numbers_are_consistent():
    numstat = EVIDENCE["numstat"]
    assert EVIDENCE["totals"] == {"added": sum(a for a, _ in numstat.values()),
                                  "deleted": sum(d for _, d in numstat.values())}
    for path, count in EVIDENCE["lines"].items():
        added, deleted = numstat[path]
        assert count["base"] - deleted + added == count["head"], path
    assert EVIDENCE["lines"]["tools/rust-module-exceptions.json"]["head"] == 0  # deleted
    commits = EVIDENCE["commits"]
    assert commits and all(re.fullmatch(r"[0-9a-f]{40}", row["sha"]) for row in commits)
    assert commits[-1]["sha"] == EVIDENCE["head"] and EVIDENCE["base"] not in {row["sha"] for row in commits}


def test_every_seeded_bug_failed_a_test():
    mutants = EVIDENCE["mutants"]
    assert len(mutants) >= 3
    for row in mutants:
        assert row["exit"] == 1 and re.search(r"\b[1-9]\d* failed\b", row["summary"]), row
