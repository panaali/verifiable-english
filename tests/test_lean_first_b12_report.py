"""Batch 12's reported numbers come from its gate evidence."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/lean-first/b12"
spec = importlib.util.spec_from_file_location("lean_first_b12_report", HERE / "report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def test_delta_numbers_are_regenerated_from_evidence():
    text = (HERE / "DELTA.md").read_text()
    assert text.split(report.BEGIN, 1)[1].split(report.END, 1)[0] == report.render()
    comparisons = [report.load(f"{name}-compare.json") for name in report.COMPARES]
    assert all(item["unlisted"] == 0 for item in comparisons)
    recordings = report.load("recordings.json")
    for name, comparison in zip(report.COMPARES, comparisons, strict=True):
        count = sum(comparison["records"].values())
        assert recordings[name]["base"]["records"] == recordings[name]["head"]["records"] == count
    delta = report.load("delta.json")
    for klass in ("order", "verdict", "availability"):
        assert len(delta[klass]) == sum(item["totals"].get(klass, 0) for item in comparisons)
    assert f"{len(delta['wording'])} text pairs" in text
    for klass in ("wording", "order"):
        assert f"{sum(item['totals'].get(klass, 0) for item in comparisons)} {klass} records" in text
    fuzz = report.load("difffuzz-ab.json")
    assert len(fuzz["runs"]) == 15
    assert fuzz["ok"]
    first = report.load("difffuzz-first-pass.json")
    reviewed = {entry["signature"] for row in first["runs"] for entry in row["head_only_new"]}
    baseline = json.loads((ROOT / "conformance/difffuzz-baseline.json").read_text())
    assert reviewed
    base = json.loads(subprocess.check_output(
        ["git", "show", f"{report.BASE}:conformance/difffuzz-baseline.json"], cwd=ROOT))
    assert len(baseline["entries"]) < len(base["entries"])
    assert all(entry["follow_up"] != "TODO" for entry in baseline["entries"])
    assert all(not row["head_only_new"] and not row["head_not_reproduced"] for row in fuzz["runs"])
    for row in report.load("latency.json").values():
        assert row["same_output"] and row["within_budget"]
    source = HERE / "cpu_report.py"
    spec = importlib.util.spec_from_file_location("lean_first_b12_cpu_report", source)
    cpu_report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cpu_report)
    cpu = cpu_report.render()
    assert cpu == report.load("lean-cpu.json")
    assert cpu["same_output"] and cpu["lean_cpu_ratio"] <= 1.20 and cpu["wall_ratio"] <= 1.25
    for name in ("mutant-environment", "mutant-model-id", "mutant-probe-record",
                 "mutant-rights-null-review", "mutant-soft-profile-review",
                 "mutant-norm-defaults-review"):
        assert "1 failed" in (report.EVIDENCE / f"{name}.log").read_text()
    assert "3 passed" in (report.EVIDENCE / "mutants-restored.log").read_text()
    assert "6 passed" in (report.EVIDENCE / "mutants-restored-review.log").read_text()
    if (report.EVIDENCE / "gate.json").exists():
        assert report.load("gate.json")["status"] == "passed"
