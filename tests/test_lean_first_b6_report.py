"""Lean-first batch 6: the latency table of `docs/lean-first/b6/DELTA.md` is rendered from the evidence files
(build checklist 20), every paired UDHR run gave identical reports within the plan's CPU and wall allowances, and
the report's comparison and fuzzer figures are the saved evidence's (`check_evidence.py`)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B6 = ROOT / "docs/lean-first/b6"


def _module(name):
    spec = importlib.util.spec_from_file_location(f"lean_first_b6_{name}", B6 / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_latency_table_is_generated_from_the_evidence():
    report = _module("report")
    text = (B6 / "DELTA.md").read_text()
    assert report.BEGIN in text and report.END in text
    assert text.split(report.BEGIN, 1)[1].split(report.END, 1)[0] == report.render()


def test_every_udhr_run_is_identical_and_within_the_allowances():
    report = _module("report")
    runs = report.timing()["runs"]
    assert any("20261003T0600Z" in r["document"] for r in runs)
    assert runs and all(r["output_equal"] and r["base"]["exit"] == r["head"]["exit"] == 0 for r in runs)
    summary = report.summary()
    assert summary["max_ratio"] <= report.CPU_RATIO_LIMIT
    assert summary["max_head_wall"] < report.PILOT_WALL_LIMIT


def test_the_report_states_the_saved_evidence():
    _module("check_evidence").main()
