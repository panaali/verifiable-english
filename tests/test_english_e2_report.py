"""The integration report's gate and three-way figures come from committed results."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_report_counts_follow_gate_json():
    gate = json.loads((ROOT / "conformance/english-lean/e2-gate-result.json").read_text())
    comparison = json.loads((ROOT / "conformance/english-lean/s3-fixture-comparison.json").read_text())
    report = (ROOT / "docs/spec/english-lean-e2-integration-report.md").read_text()

    assert gate["status"] == "passed" and gate["dirty"] is False and not gate["failures"]
    counts = gate["counts"]
    assert counts["selected"] == counts["passed"] + counts["skipped"] + counts["failed"]
    assert (f"The clean gate on `{gate['commit_sha'][:8]}` passed: "
            f"**{counts['passed']:,} Python tests passed, {counts['skipped']} allowed skips, "
            f"{counts['failed']} failures; {counts['rust_passed']} Rust tests passed**") in report

    rows = comparison["rows"]
    cases = len(rows)
    agreements = sum(not row["record"]["classes"] for row in rows)
    differences = cases - agreements
    unexplained = sum(bool(row["record"]["classes"]) and row["disposition"] is None for row in rows)
    assert (comparison["cases"], comparison["agreement"], comparison["differences"],
            comparison["unexplained"]) == (cases, agreements, differences, unexplained)
    assert (f"**{cases} cases, {agreements} agreements, {differences} disposed differences, "
            f"{unexplained} unexplained differences**") in report
