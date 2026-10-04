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
        # `row_code` is a code the runner's own row carries (the soft-norms@0 contract's).
        return [{"index": i, "digest": "0" * 64,
                 "result": {**{k: v for k, v in row.items() if k not in ("code", "generator", "row_code")},
                            **({"code": row["row_code"]} if "row_code" in row else {})},
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


def test_route_rows_keep_rejections_as_rows(monkeypatch):
    """`rows` (batch 1) returns every row, rejections included, for a caller that reads them itself."""
    rows = [{"id": "a", "status": "ok", "value": 1},
            {"id": "b", "status": "error", "error": "UnsupportedProfile: x", "code": "UnsupportedProfile"}]
    pool = _Pool(rows)
    monkeypatch.setattr(relay, "_pool", pool)
    assert relay.rows("rights", [{"id": "a"}, {"id": "b"}], timeout=3.0) == [
        {"id": "a", "status": "ok", "value": 1}, {"id": "b", "status": "error", "error": "UnsupportedProfile: x"}]
    assert pool.calls == [("rights", [{"id": "a"}, {"id": "b"}], 3.0)]


def test_a_route_rows_own_contract_code_is_the_errors_code(monkeypatch):
    """A soft route rejection carries the soft-norms@0 contract code in its row; the relayed error keeps it
    as its code (as the one-shot transport did), its class from the service's public code, its text Lean's."""
    text = "UnsupportedProfile: Unsupported profile norm-defaults@0"
    monkeypatch.setattr(relay, "_pool", _Pool([{"id": "s", "status": "error", "error": text,
                                                 "code": "UnsupportedProfile",
                                                 "row_code": "SOFT_UNSUPPORTED_PROFILE"}]))
    with pytest.raises(UnsupportedProfile) as caught:
        relay.decide("soft-norms", [{"id": "s"}])
    assert caught.value.code == "SOFT_UNSUPPORTED_PROFILE" and caught.value.message == text


ROUTE_MODES = ("soft-norms", "rights", "speech-acts", "reports", "alternatives", "risk", "risk-eval",
               "quantity", "norm-defaults", "discourse", "readings-route", "diagnose")


@needs_service
@pytest.mark.parametrize("mode", ROUTE_MODES)
def test_every_route_mode_answers_through_the_service(mode):
    """Each one-shot route is a service mode (batch 1): a case it cannot read is a rejection row of the
    mode's schema, bound to the case, never an operational failure."""
    [row] = relay.rows(mode, [{"id": "x", "kind": "no-such-kind", "unit": "soft-norms@0"}])
    assert row["status"] == "error" and type(row["error"]) is str, row


@needs_service
def test_risk_eval_reads_its_cases_with_leans_own_json_parser():
    """`risk-eval` reads its batch as `ve_risk_eval` did, with Lean.Json.parse: a null the restricted wire
    decoder refuses (the whole batch, for every other mode) is that case's rejection row here."""
    [row] = relay.rows("risk-eval", [{"environment": None, "quantities": [], "conditions": []}])
    assert row["status"] == "error", row
    with pytest.raises(VEError, match="restricted JSON"):
        relay.rows("risk", [{"id": "x", "kind": "risk-elaborate", "environment": None}])


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
