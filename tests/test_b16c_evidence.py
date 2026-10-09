"""The 16c progress report is a view of saved evidence, independent of live git HEAD."""
from __future__ import annotations

from collections import Counter
import gzip
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/lean-first/b16c"
EVIDENCE = HERE / "evidence"
SPEC = importlib.util.spec_from_file_location("b16c_report", HERE / "report.py")
assert SPEC is not None and SPEC.loader is not None
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def test_report_is_generated_from_saved_evidence():
    delta = (HERE / "DELTA.md").read_text()
    generated = delta.split("<!-- BEGIN GENERATED B16C METRICS -->\n", 1)[1].split(
        "\n<!-- END GENERATED B16C METRICS -->", 1)[0]
    assert generated == REPORT.metrics()


def test_every_residue_has_a_saved_cause_and_count():
    share = json.loads((EVIDENCE / "share.json").read_text())
    rows = json.loads(gzip.decompress((EVIDENCE / "residues.json.gz").read_bytes()))
    assert len({(r["corpus"], r["case"]) for r in rows}) == len(rows)
    assert all(set(r) == {"corpus", "case", "cause", "source_sha256"} and
               len(r["source_sha256"]) == 64 and r["cause"] != "lean" for r in rows)
    for name, saved in share.items():
        reasons = Counter(r["cause"] for r in rows if r["corpus"] == name)
        assert dict(reasons) == saved["other"]
        assert sum(reasons.values()) + saved["lean"] == saved["documents"]


def test_scope_and_mutants_are_saved_and_named():
    scope = json.loads((EVIDENCE / "scope.json").read_text())
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())
    assert len(scope["base"]) == len(scope["head"]) == 40
    assert scope["base"] != scope["head"]
    assert scope["commits"] and scope["commits"][0]["hash"] == scope["head"]
    assert scope["changes"]
    assert len(mutants) >= 3
    assert len({m["bug"] for m in mutants}) == len(mutants)
    assert all(m["exit_code"] != 0 and "1 failed" in m["failure_excerpt"] for m in mutants)


def test_gate_numbers_are_read_from_saved_result():
    scope = json.loads((EVIDENCE / "scope.json").read_text())
    gate = json.loads((EVIDENCE / "gate.json").read_text())
    counts = gate["counts"]
    assert gate["commit_sha"] == scope["head"] and gate["dirty"] is False
    assert gate["status"] == "passed" and gate["failures"] == []
    assert counts["passed"] + counts["skipped"] + counts["failed"] == counts["selected"]
    assert counts["selected"] + counts["deselected"] == counts["collected"]
    assert {"lean_build", "lean_audit", "cargo_test", "pytest"} <= set(gate["stages"])
