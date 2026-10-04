"""`ve/backends/relay.py`, the one Python entry to Lean's decisions (docs/LEAN-FIRST-PLAN.md,
rule 2, batch 0): Lean's code chooses the exception class and Lean's text is raised verbatim;
only operational failures are Python's own (`CheckerUnavailable`)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.probe_matrix import raw_environment
from ve import Environment
from ve.admission import AdmissionError
from ve.ast import Const, Unary, formula_to_data
from ve.backends import relay
from ve.backends.service_schema import DIRECTORY as SCHEMAS
from ve.errors import (CheckerUnavailable, InvalidModel, ResourceLimit, UnknownSymbol, UnsupportedProfile,
                       VEError)

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
needs_service = pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
HANDSHAKE_CODES = json.loads((SCHEMAS / "envelope.json").read_text())["handshake"]["properties"]["codes"]["const"]
ROW_CODES = json.loads((SCHEMAS / "common.json").read_text())["$defs"]["code"]["enum"]


def test_one_class_per_code_of_the_service():
    """The class table, the handshake the client requires and the rows' code domain are one list."""
    assert list(relay.CLASSES) == HANDSHAKE_CODES == ROW_CODES


@needs_service
def test_the_service_states_the_code_list_the_client_requires():
    from ve.backends.lean_service import LeanService
    with LeanService(SERVICE) as service:
        assert service.handshake["codes"] == HANDSHAKE_CODES


class _Pool:
    """A pool whose service answers `rows`, each bound with the code beside it (`coding`)."""

    def __init__(self, rows):
        self.rows, self.calls = rows, []

    def run_bound(self, mode, cases, *, timeout=None):
        self.calls.append((mode, cases, timeout))
        return [{"index": i, "digest": "0" * 64,
                 "result": {k: v for k, v in row.items() if k not in ("code", "generator")},
                 **{k: row[k] for k in ("code", "generator") if k in row}} for i, row in enumerate(self.rows)]

    def close(self):
        pass


@pytest.mark.parametrize("code, cls", [(code, cls) for code, cls in relay.CLASSES.items()
                                       if code != "CheckerUnavailable"])
def test_each_code_raises_its_class_with_the_text_verbatim(monkeypatch, code, cls):
    text = f"{code}: Lean's own words, kept: as sent"
    monkeypatch.setattr(relay, "_pool", _Pool([{"id": "a", "status": "ok"},
                                               {"id": "b", "status": "error", "error": text, "code": code}]))
    with pytest.raises(VEError) as caught:
        relay.decide("check", [{"id": "a"}, {"id": "b"}])
    expected = cls or AdmissionError
    assert type(caught.value) is expected and caught.value.code == expected.code
    assert caught.value.message == text and str(caught.value) == text
    assert caught.value.backend_rejection is True


def test_a_rejection_does_not_lose_its_generator(monkeypatch):
    row = {"id": "a", "status": "error", "error": "InvalidModel(literals): x", "code": "InvalidModel",
           "generator": "literals"}
    monkeypatch.setattr(relay, "_pool", _Pool([row]))
    with pytest.raises(InvalidModel) as caught:
        relay.decide("route", [{"id": "a"}])
    assert caught.value.to_dict() == {"code": "InvalidModel", "message": "InvalidModel(literals): x",
                                      "generator": "literals"}


@pytest.mark.parametrize("code", ["DependencyCycle", "", "unknownsymbol", "InvalidInput "])
def test_an_unknown_code_is_operational(monkeypatch, code):
    monkeypatch.setattr(relay, "_pool", _Pool([{"id": "a", "status": "error", "error": "x", "code": code}]))
    with pytest.raises(CheckerUnavailable, match="unknown code"):
        relay.decide("check", [{"id": "a"}])


def test_lean_checker_unavailable_is_operational(monkeypatch):
    row = {"id": "a", "status": "error", "error": "CheckerUnavailable: x", "code": "CheckerUnavailable"}
    monkeypatch.setattr(relay, "_pool", _Pool([row]))
    with pytest.raises(CheckerUnavailable, match="^CheckerUnavailable: x$"):
        relay.decide("check", [{"id": "a"}])


def test_rows_are_returned_in_order_and_unchanged(monkeypatch):
    rows = [{"id": str(i), "status": "ok", "value": i} for i in range(3)]
    pool = _Pool(rows)
    monkeypatch.setattr(relay, "_pool", pool)
    assert relay.decide("evaluate", [{"id": "0"}], timeout=7.0) == rows
    assert pool.calls == [("evaluate", [{"id": "0"}], 7.0)]


@needs_service
def test_genuine_typing_rejection_is_leans(monkeypatch):
    """Lean's code and text, unstripped: `UnknownSymbol: ...` (wording list W1 of DELTA.md)."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    env = Environment(raw_environment(()))
    ast = json.loads(json.dumps(formula_to_data(env, Unary("base", Const("x")))).replace('"base"', '"missing"'))
    case = {"id": "c", "environment": env.to_dict(), "ast": ast}
    with pytest.raises(UnknownSymbol) as caught:
        relay.decide("check", [case])
    assert caught.value.message.startswith("UnknownSymbol: ")


@needs_service
def test_genuine_request_error_carries_leans_code():
    from ve.backends.lean_service import LeanService
    with LeanService(SERVICE) as service:
        _, response = service.exchange("evaluate", "[{},{}]", 2, budget={"cases": 1, "bytes": 1 << 20})
    assert response["status"] == "error" and response["code"] == "ResourceLimit"
    error = relay.rejection(response["code"], response["error"])
    assert type(error) is ResourceLimit and error.message == "ResourceLimit: batch has 2 cases; budget is 1"


@needs_service
def test_genuine_profile_rejection_is_leans(monkeypatch):
    raw = raw_environment(())
    raw["profiles"] = 7
    with pytest.raises(UnsupportedProfile, match="^UnsupportedProfile: "):
        relay.decide("environment", [{"id": "e", "environment": raw}])
