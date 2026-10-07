"""Batch 13a: Lean parse diagnostics, order text and replay ownership."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from conformance.order import environment as order_environment
from test_lean_service import service_executable  # noqa: F401
from ve import Environment
from ve.ast import document_to_data
from ve.backends.relay import rows
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.errors import VEError
from ve.parser import _parse_python
from ve.ast import Top


ROOT = Path(__file__).resolve().parents[1]


def _case(environment, source, case_id="p"):
    return {"id": case_id, "environment": environment, "source": source}


def test_lean_parse_diagnostics_match_frozen_corpus(service_executable):
    corpus = json.loads((ROOT / "conformance/parser.json").read_text())
    actual = rows("parse", [_case(c["environment"], c["source"], c["id"]) for c in corpus],
                  executable=service_executable)
    assert len(actual) == len(corpus)
    for case, row in zip(corpus, actual, strict=True):
        env = Environment.from_dict(case["environment"])
        try:
            document = _parse_python(env, case["source"])
        except VEError as error:
            expected = error.message if error.message.startswith(error.code + ": ") else \
                error.code + ": " + error.message
            assert row["status"] == "error" and row["error"] == expected, case["id"]
            if error.span is not None:
                assert row["span"] == error.to_dict()["span"], case["id"]
        else:
            assert row["status"] == "ok", case["id"]
            assert row["ast"] == document_to_data(env, document.document), case["id"]


def test_parse_lexical_edges_share_first_fault_and_span(service_executable):
    raw = order_environment().to_dict()
    sources = ["true\u00a0.\n", "true  .\n", "true\t.\n", "true.\r\n",
               "\u201ctrue\u201d.\n", "\u212a.\n", "\u0130.\n", "true\x00.\n"]
    actual = rows("parse", [_case(raw, s, str(i)) for i, s in enumerate(sources)],
                  executable=service_executable)
    for source, row in zip(sources, actual, strict=True):
        with pytest.raises(VEError) as raised:
            _parse_python(order_environment(), source)
        error = raised.value
        expected = error.message if error.message.startswith(error.code + ": ") else \
            error.code + ": " + error.message
        assert row["status"] == "error" and row["error"] == expected
        assert row["span"] == error.to_dict()["span"]


def test_public_lean_parse_uses_lean_rejection(monkeypatch, service_executable):
    from ve import parser
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    monkeypatch.setattr(parser, "_parse_python", lambda *_: pytest.fail("Python parser decided a Lean rejection"))
    with pytest.raises(VEError) as raised:
        parser.parse_with_metadata(order_environment(), "true  .\n")
    assert raised.value.code == "SyntaxError"
    assert raised.value.span is not None


def test_shadowed_binder_keeps_its_diagnostic_code(monkeypatch, service_executable):
    from ve import parser
    case = next(c for c in json.loads((ROOT / "conformance/parser.json").read_text())
                if c["id"] == "parser_edge_019")
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    with pytest.raises(VEError) as raised:
        parser.parse_with_metadata(Environment.from_dict(case["environment"]), case["source"])
    assert raised.value.code == "ShadowedVariable"
    assert raised.value.span is not None


def test_order_parse_returns_canonical_text(service_executable):
    raw = order_environment().to_dict()
    sources = ["[@n - 1] < -5.\n", "-@n <= [3 * @m].\n",
               "for every item x7, (x7 value 0).\n"]
    actual = rows("parse", [_case(raw, s, str(i)) for i, s in enumerate(sources)],
                  executable=service_executable)
    for source, row in zip(sources, actual, strict=True):
        assert row["status"] == "ok"
        assert row["canonical"] == source.replace("x7", "x0")


def test_lean_certificate_owns_binding_and_replay_budget(service_executable):
    environment = Environment.from_dict(json.loads((ROOT / "conformance/evaluation.json").read_text())[0]
                                        ["environment"])
    found = prove_entailment(environment, [Top()], Top())
    assert found.certificate is not None
    from ve.ast import formula_to_data
    base = {"id": "cert", "environment": environment.to_dict(),
            "premises": [formula_to_data(environment, Top())],
            "conclusion": formula_to_data(environment, Top()),
            "certificate": found.certificate}
    accepted = rows("check-certificate", [base], executable=service_executable)[0]
    assert accepted["valid"] is True and accepted["steps"] > 0
    zero = rows("check-certificate", [{**base, "max_steps": 0}], executable=service_executable)[0]
    assert zero["status"] == "error" and zero["error"].startswith("ResourceLimit: certificate replay")
    stale = rows("check-certificate", [{**base, "certificate":
        {**found.certificate, "environment_id": "0" * 64}}], executable=service_executable)[0]
    assert stale["status"] == "error" and "bound to different inputs" in stale["error"]


def test_public_certificate_budget_is_sent_to_lean(monkeypatch, service_executable):
    environment = Environment.from_dict(json.loads((ROOT / "conformance/evaluation.json").read_text())[0]
                                        ["environment"])
    monkeypatch.setenv("VE_AUTHORITY", "python")
    found = prove_entailment(environment, [Top()], Top())
    assert found.certificate is not None
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    result = check_entailment_certificate(environment, [Top()], Top(), found.certificate, max_steps=0)
    assert result.status == "ResourceLimit" and result.steps == 0
