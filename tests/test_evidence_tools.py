"""Evidence tools pass only on evidence (lf-1 review B, the class of route_parity.py's empty pass).

Each tool whose exit status a batch cites refuses inputs that cannot show anything (the same file
or directory twice, nothing recorded, an operation or corpus that yields no case) and fails a run
whose own result says it compared nothing or found a difference.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from tools import lean_service_latency, lean_service_parity, rust_output_diff, stage2_parity

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("b1_latency", ROOT / "docs/lean-first/b1/latency.py")
b1_latency = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b1_latency)


@pytest.fixture
def isolated_probe(monkeypatch):
    """stage2_parity.main patches the probe matrix and the dispatch observers; undo it."""
    monkeypatch.setattr(stage2_parity.dispatch, "observers", list(stage2_parity.dispatch.observers))
    for name in ("outcome", "graph_baselines", "boundary_baselines", "feature_baselines", "OPERATIONS"):
        monkeypatch.setattr(stage2_parity.probe, name, getattr(stage2_parity.probe, name))


def test_stage2_parity_refuses_an_operation_it_does_not_probe(isolated_probe, capsys):
    """`--show NO_SUCH_OPERATION` filtered the matrix to nothing, compared nothing and exited 0."""
    assert stage2_parity.main(["--show", "no_such_operation"]) == 2
    assert "no operation" in capsys.readouterr().err


def test_stage2_parity_fails_a_run_that_compared_no_cell(isolated_probe, monkeypatch, capsys):
    monkeypatch.setattr(stage2_parity, "_generate", lambda authority: {"cells": [], "authority": authority})
    monkeypatch.setattr(stage2_parity, "compare", lambda *a, **k: {"authority": "lean", "cells": [], "probes": []})
    assert stage2_parity.main(["--authority", "lean"]) == 2
    assert "no probe cell" in capsys.readouterr().err


@pytest.mark.parametrize("cells, probes, status", [
    (["same, adapter", "baseline drift"], ["same, python"], 0),
    (["same, adapter", "regression"], [], 1),
    (["same, python"], ["different"], 1),
])
def test_stage2_parity_exit_status_is_its_result(cells, probes, status):
    """It exited 0 even with regressions; its report was the only gate."""
    result = {"cells": [{"class": c} for c in cells], "probes": [{"class": c} for c in probes]}
    assert stage2_parity.exit_status(result) == status


def _checkout(path: Path) -> Path:
    (path / "ve").mkdir(parents=True)
    (path / "ve" / "__init__.py").write_text("")
    return path


@pytest.fixture
def two_checkouts(tmp_path):
    document = tmp_path / "d.ve.md"
    document.write_text("x")
    return _checkout(tmp_path / "base"), _checkout(tmp_path / "head"), document


def test_b1_latency_refuses_inputs_that_compare_nothing(two_checkouts, tmp_path):
    """Two equal failures (a bad root, a missing document) were `same_output` and exit 0."""
    base, head, document = two_checkouts
    assert b1_latency.main([str(base), str(base), str(document)]) == 2
    assert b1_latency.main([str(tmp_path), str(head), str(document)]) == 2
    assert b1_latency.main([str(base), str(head), str(tmp_path / "missing.ve.md")]) == 2
    assert b1_latency.main([str(base), str(head), str(document), "--runs", "0"]) == 2


@pytest.mark.parametrize("outputs, status", [
    ({"base": (0, "ok\n"), "head": (0, "ok\n")}, 0),
    ({"base": (0, "ok\n"), "head": (0, "other\n")}, 1),
    ({"base": (1, ""), "head": (1, "")}, 1),
])
def test_b1_latency_fails_unless_every_output_matches(two_checkouts, monkeypatch, outputs, status):
    base, head, document = two_checkouts
    side = {base: "base", head: "head"}
    monkeypatch.setattr(b1_latency, "check", lambda root, doc: (0.1, 0.1, *outputs[side[root]]))
    assert b1_latency.main([str(base), str(head), str(document), "--runs", "2"]) == status


def test_b1_latency_compares_every_run_not_the_last():
    assert not b1_latency.same_output({"base": {(0, "a"), (0, "b")}, "head": {(0, "a"), (0, "b")}})
    assert b1_latency.same_output({"base": {(0, "a")}, "head": {(0, "a")}})


def test_lean_service_latency_refuses_a_bench_without_workloads(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(lean_service_latency, "workloads", lambda root, quick: [])
    assert lean_service_latency.main(["--out", str(tmp_path / "out"), "--bench-root", str(tmp_path)]) == 2
    assert "no workload" in capsys.readouterr().err


def _parity(*corpora):
    rows = [{"mode": "route", "corpus": name, "cases": cases, "identical": same} for name, cases, same in corpora]
    return {"corpora": rows, "total": {"cases": sum(r["cases"] for r in rows),
                                       "identical": sum(r["identical"] for r in rows)}}


def test_lean_service_parity_fails_an_empty_corpus(capsys):
    """A corpus whose glob matched nothing added 0/0 and the gate passed."""
    assert lean_service_parity.gate_status(_parity(("a", 3, 3), ("b", 2, 2))) == 0
    assert lean_service_parity.gate_status(_parity(("a", 3, 3), ("queries", 0, 0))) == 1
    assert "EMPTY corpus route: queries" in capsys.readouterr().err
    assert lean_service_parity.gate_status(_parity(("a", 3, 2))) == 1
    assert lean_service_parity.gate_status(_parity()) == 1


def test_rust_output_diff_refuses_the_baseline_as_the_new_build(tmp_path, capsys):
    baseline = tmp_path / "ve-baseline"
    baseline.write_bytes(b"binary")
    assert rust_output_diff.compare(baseline, baseline) == 2
    assert "baseline itself" in capsys.readouterr().err
