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
spec = importlib.util.spec_from_file_location("lean_first_b12_signoff", HERE / "signoff.py")
signoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(signoff)


def test_dri_signoff_requires_exactly_the_listed_changes():
    delta = report.load("delta.json")
    block, records = signoff.required(delta)
    assert block is not None and len(records) == 48
    signature = lambda identifier: {"sha256": identifier, "signed_by": "DRI",
                                    "date": "2026-10-07", "decision": "approved",
                                    "source": "explicit DRI decision"}
    approved = {"format": "lean-first-b12-signoff@1", "wording_order": signature(block),
                "verdicts": [signature(record) for record in sorted(records)]}
    assert signoff.problems(delta, approved) == []
    assert signoff.problems(delta, None) == ["DRI signoff is absent"]
    assert any("unsigned" in problem for problem in signoff.problems(
        delta, {**approved, "verdicts": approved["verdicts"][:-1]}))
    changed = json.loads(json.dumps(delta))
    changed["verdict"][0]["head"]["raised"]["message"] += " changed"
    assert any("unsigned" in problem for problem in signoff.problems(changed, approved))
    assert any("digest differs" in problem for problem in signoff.problems(
        delta, {**approved, "wording_order": signature("0" * 64)}))
    assert any("duplicate" in problem for problem in signoff.problems(
        delta, {**approved, "verdicts": approved["verdicts"] + approved["verdicts"][:1]}))
    assert any("no DRI approval" in problem for problem in signoff.problems(
        delta, {**approved, "verdicts": [{**approved["verdicts"][0], "signed_by": "agent"},
                                         *approved["verdicts"][1:]]}))
    assert any("invalid digest" in problem for problem in signoff.problems(
        delta, {**approved, "verdicts": [{"sha256": []}, *approved["verdicts"]]}))


def test_dri_signed_every_batch_12_delta_record():
    assert signoff.check() == []


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
    measurement = cpu_report.render()
    assert measurement == report.load("lean-cpu.json")
    assert measurement["same_output"] and measurement["within_budget"]
    for name in ("mutant-environment", "mutant-model-id", "mutant-probe-record",
                 "mutant-rights-null-review", "mutant-soft-profile-review",
                 "mutant-norm-defaults-review"):
        assert "1 failed" in (report.EVIDENCE / f"{name}.log").read_text()
    assert "3 passed" in (report.EVIDENCE / "mutants-restored.log").read_text()
    assert "6 passed" in (report.EVIDENCE / "mutants-restored-review.log").read_text()
    if (report.EVIDENCE / "gate.json").exists():
        assert report.load("gate.json")["status"] == "passed"
