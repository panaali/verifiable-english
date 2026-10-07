"""Lean-first batch 6: the latency table of `docs/lean-first/b6/DELTA.md` is rendered from the evidence files
(build checklist 20), every paired UDHR run gave identical reports, and the report's comparison, fuzzer and
latency figures are the saved evidence's (`check_evidence.py`)."""
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


def test_every_udhr_run_gave_identical_reports():
    runs = _module("report").timing()["runs"]
    assert any("20261003T0600Z" in r["document"] for r in runs)
    assert runs and all(r["output_equal"] and r["base"]["exit"] == r["head"]["exit"] == 0 for r in runs)


def test_every_udhr_document_is_checked_and_rendered():
    """Recheck finding B (lf-6c): the latency evidence measured `check` only, while the UDHR pilot also renders
    (`finish.py` calls `render_document`). Every document is timed under both commands."""
    runs = _module("report").timing()["runs"]
    documents = {r["document"] for r in runs}
    assert {(d, c) for d in documents for c in ("check", "render")} == {(r["document"], r["command"]) for r in runs}
    large = [r["command"] for r in runs if "20261003T0600Z" in r["document"]]
    assert large.count("check") == large.count("render") == 3


def test_the_report_states_the_saved_evidence():
    """The recorded figures, the allowances they are read against included (`check_evidence.main`)."""
    _module("check_evidence").main()
