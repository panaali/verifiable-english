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


def test_e2_report_section_is_the_rendering_of_the_evidence():
    from conformance import english_lean_e2_report as e2

    text = e2.REPORT.read_text()
    section = text.split(e2.BEGIN, 1)[1].split(e2.END, 1)[0]
    assert section == e2.render()


def test_e2_evidence_keeps_lean_authority():
    """The DRI's condition on review A2: every difference dispositioned, no port or overlay mismatch, no formula
    changed by a lexicon mutant, and every budget of GE2 item 9 met."""
    from conformance import english_lean_e2_report as e2

    evidence = json.loads(e2.EVIDENCE.read_text())
    parts = evidence["parts"]
    assert set(parts) == {"g3", "reverse", "mutation", "parity", "overlay", "latency"}
    _, undispositioned = e2.differences_section(parts["g3"], parts["reverse"])
    assert undispositioned == 0
    g3 = parts["g3"]
    assert g3["texts"] > 0 and not g3["roundtrip_failures"] and not g3.get("generator_stalled")
    assert g3["empty"] == [] and all(g3["by_config"].values())
    assert len(g3["fresh_seeds"]) == 14
    assert not parts["reverse"]["lean_accepts_python_differs"]
    assert not [k for k, v in parts["reverse"]["counts"].items() if k.endswith(":lean-unavailable") and v]
    assert parts["mutation"]["counts"].get("texts:changed", 0) == 0
    parity = parts["parity"]["counts"]
    assert parity.get("corpus:symbols-mismatched", 0) == parity.get("mutant:symbols-mismatched", 0) == 0
    assert not [f for f in parts["parity"]["findings"] if f.get("status") == "v6"]
    overlay = parts["overlay"]["counts"]
    assert overlay.get("corpus:compared", 0) == overlay.get("corpus:agree", 0)
    assert overlay.get("mutant:differ", 0) == 0
    assert "**missed**" not in "\n".join(e2.latency_section(parts["latency"]))
