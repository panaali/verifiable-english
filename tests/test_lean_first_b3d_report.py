"""Lean-first batch 3d: the tables of `docs/lean-first/b3d/DELTA.md` are rendered from the evidence files
(build checklist 20), every paired run they report gave identical answers, and the corpus A/B left nothing
unlisted."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B3D = ROOT / "docs/lean-first/b3d"


def _report():
    spec = importlib.util.spec_from_file_location("lean_first_b3d_report", B3D / "report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_delta_tables_are_generated_from_the_evidence():
    report = _report()
    text = (B3D / "DELTA.md").read_text()
    assert report.BEGIN in text and report.END in text
    assert text.split(report.BEGIN, 1)[1].split(report.END, 1)[0] == report.render()


def test_every_paired_route_run_gave_identical_answers():
    report = _report()
    runs = [run for name in report.UDHR_RUNS for run in json.loads((B3D / "evidence" / name).read_text())["runs"]]
    assert runs and all(run["identical"] and run["base"]["exit"] == run["head"]["exit"] for run in runs)
    corpus = json.loads((B3D / "evidence/corpus-timing.json").read_text())["runs"]
    assert corpus and all(all(run["base"][k] == run["head"][k] for k in ("ok", "rejected", "unavailable"))
                          for run in corpus)


def test_the_ab_lists_every_difference_and_the_delta_lists_only_the_udhr_translation():
    summary = json.loads((B3D / "evidence/ab-summary.json").read_text())
    assert summary["unlisted"] == 0 and set(summary["totals"]) <= {"same", "availability"}
    delta = json.loads((B3D / "delta.json").read_text())
    assert set(delta) == {"availability"} and len(delta["availability"]) == summary["totals"]["availability"] == 1
    [record] = delta["availability"]
    assert record["case"].startswith("pilot/udhr-20261003T0600Z:") and record["case"].endswith("/translation.ve.md")
    assert record["base"]["stdout"]["status"] == "CheckerUnavailable" and record["head"]["exit"] == 0
