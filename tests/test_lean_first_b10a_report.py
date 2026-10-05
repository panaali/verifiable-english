"""Lean-first batch 10a: the tables of `docs/lean-first/b10a/DELTA.md` are rendered from the evidence files
(build checklist 20), the corpus A/B found no difference, every paired run exited cleanly, and every seeded bug
was caught (build checklist 13)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B10A = ROOT / "docs/lean-first/b10a"


def _report():
    spec = importlib.util.spec_from_file_location("lean_first_b10a_report", B10A / "report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _evidence(name):
    return json.loads((B10A / "evidence" / name).read_text())


def test_delta_tables_are_generated_from_the_evidence():
    report = _report()
    text = (B10A / "DELTA.md").read_text()
    assert report.BEGIN in text and report.END in text
    assert text.split(report.BEGIN, 1)[1].split(report.END, 1)[0] == report.render()


def test_the_ab_found_no_difference_over_every_corpus():
    compare, records = _evidence("ab-compare.json"), _evidence("ab-records.json")
    assert compare["differences"] == [] and compare["unlisted"] == 0
    assert set(compare["totals"]) == {"same"} and compare["totals"]["same"] == sum(compare["records"].values())
    assert {name.split("/")[0] for name in compare["records"]} == {"conformance", "discourse", "pilots", "probe",
                                                                  "readings"}
    assert records["base"]["by_corpus"] == records["head"]["by_corpus"] == compare["records"]


def test_every_timed_run_exited_cleanly_on_both_sides():
    runs = _evidence("timing-route.json")["runs"] + _evidence("timing.json")["runs"]
    assert runs and all(run["exit"] == 0 for run in runs)
    for what in {run["what"] for run in runs}:
        assert {run["side"] for run in runs if run["what"] == what} == {"base", "head"}


def test_every_seeded_bug_was_caught():
    bugs = _evidence("seeded-bugs.json")
    assert len(bugs) >= 3
    for name, result in bugs.items():
        assert result.get("build") == "failed" or (result["returncode"] == 1 and result["failed"]), name
