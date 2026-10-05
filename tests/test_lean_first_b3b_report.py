"""Lean-first batch 3b: the timing tables of `docs/lean-first/b3b/DELTA.md` are rendered from the evidence files
(build checklist 20), and the paired UDHR runs they report gave identical answers."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B3B = ROOT / "docs/lean-first/b3b"


def _report():
    spec = importlib.util.spec_from_file_location("lean_first_b3b_report", B3B / "report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_delta_tables_are_generated_from_the_evidence():
    report = _report()
    text = (B3B / "DELTA.md").read_text()
    assert report.BEGIN in text and report.END in text
    assert text.split(report.BEGIN, 1)[1].split(report.END, 1)[0] == report.render()


def test_every_paired_udhr_run_gave_identical_answers():
    runs = [run for name in ("udhr-1-set.json", "udhr-10-sets.json", "udhr-whole.json")
            for run in json.loads((B3B / "evidence" / name).read_text())["runs"]]
    assert runs and all(run["identical"] and run["base"]["exit"] == run["head"]["exit"] == 0 for run in runs)


def test_every_review_round_gave_identical_answers():
    for name, _ in _report().REVIEW:
        data = json.loads((B3B / "evidence" / name).read_text())
        assert data["identical"] and set(data["runs"]) == {"base", "before", "head"}, name
        assert all(len(runs) == data["rounds"] for runs in data["runs"].values()), name
        assert len({run["exit"] for runs in data["runs"].values() for run in runs}) == 1, name
