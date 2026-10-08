"""Batch 12's reported numbers come from its gate evidence."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
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
    # Exercise record-level signatures even when the production delta has no
    # verdict changes after paths and diagnostic classes are restored.
    delta["verdict"].append({"corpus": "synthetic", "authority": "lean",
                             "case": "signature-test", "op": "model",
                             "base": {"raised": {"code": "InvalidModel", "message": "old"}},
                             "head": {"raised": {"code": "InvalidInput", "message": "new"}}})
    block, records = signoff.required(delta)
    assert block is not None and len(records) == len(delta["verdict"]) + len(delta["availability"])
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


def test_delta_retains_frozen_paths_and_quoted_names():
    """The DRI signed wording only where the old diagnostic's information survives."""
    delta = report.load("delta.json")
    quoted = lambda text: re.findall(r"'[^']+'", text)
    for row in delta["wording"]:
        for name in quoted(row["base"]):
            assert name in row["head"], row
    for row in [*delta["verdict"], *delta["order"]]:
        base = row["base"].get("raised", {})
        head = row["head"].get("raised", {})
        if "path" in base:
            assert head.get("path") == base["path"], row
        for name in quoted(base.get("message", "")):
            assert name in head.get("message", ""), row


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


def test_branch_trust_allowance_counts_only_batch_12_changes():
    from tools import trust_map

    baseline = json.loads((ROOT / "docs/trust-baseline.json").read_text())
    main_baseline = json.loads(subprocess.check_output(
        ["git", "show", "main:docs/trust-baseline.json"], cwd=ROOT))
    assert baseline["history"][-1]["rebaselined_from"] == trust_map.budget(main_baseline["totals"])
    current, problems = trust_map.measure(ROOT, ROOT / "tools/trust-classes.json",
                                          ROOT / "lean/statements.txt")
    parent, parent_problems, _ = trust_map.measure_rev(report.BASE)
    assert not problems and not parent_problems
    assert baseline["totals"] == trust_map.totals(current)
    assert baseline["files"] == current
    now = trust_map.budget(trust_map.totals(current))
    before = trust_map.budget(trust_map.totals(parent))
    growth = {key: now[key] - before[key] for key in ("K", "S", "V")}
    assert baseline["signed"][-1]["allow"] == growth
    text = (HERE / "DELTA.md").read_text()
    assert f"**{sum(growth.values())} trusted Lean\nlines added**" in text
    changes = report.line_changes()["production Python"]
    assert f"**{changes[1]} production Python lines**" in text
