"""Reading-set verdicts on the Lean authority: Lean's `readings` mode checks the evidence."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ve.backends import dispatch, relay
from ve.environment import Environment
from ve.errors import CheckerUnavailable, VEError
from ve.readings import check_readings
from tests import probe_matrix as pm

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "lean/.lake/build/bin/ve_service").exists(),
                                reason="Lean service has not been built")

ATOM = ["unary", "base", ["const", "x"]]
NEGATED = ["not", ATOM]
ALTERNATIVES = [{"id": "s", "version": 2, "readings": [
    {"kind": "asserted", "content": ATOM}, {"kind": "asserted", "content": NEGATED}]}]
QUERIES = {
    "ALL": (ALTERNATIVES, ["or", ATOM, NEGATED], [["top"]]),
    "SOME": (ALTERNATIVES, ["bottom"], [NEGATED]),
    "NONE": ([{"id": "s", "version": 2, "readings": [
        {"kind": "asserted", "content": ATOM}, {"kind": "asserted", "content": ["top"]}]}],
        ["bottom"], [ATOM]),
}


def env():
    return Environment(pm.raw_environment(()))


def cases(monkeypatch):
    calls = []
    real = relay.decide

    def spy(mode, batch, **kw):
        rows = real(mode, batch, **kw)
        if mode == "readings":
            calls.extend(zip(batch, rows))
        return rows

    monkeypatch.setattr(relay, "decide", spy)
    return calls


@pytest.mark.parametrize("verdict", list(QUERIES))
def test_readings_verdicts_match_python_and_are_lean_checked(monkeypatch, verdict):
    sets, conclusion, fixed = QUERIES[verdict]
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = check_readings(env(), sets, conclusion, fixed=fixed)
    assert expected["verdict"] == verdict
    seen = []
    monkeypatch.setattr(dispatch, "observers", [lambda op, auth: seen.append((op, auth))])
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    calls = cases(monkeypatch)
    assert check_readings(env(), sets, conclusion, fixed=fixed) == expected
    assert ("readings", "lean") in seen
    [(case, row)] = calls
    assert case["verdict"] == row["verdict"] == verdict


def submitted(monkeypatch, verdict):
    sets, conclusion, fixed = QUERIES[verdict]
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    calls = cases(monkeypatch)
    check_readings(env(), sets, conclusion, fixed=fixed)
    return copy.deepcopy(calls[0][0])


@pytest.mark.parametrize("verdict,change,message", [
    ("ALL", lambda case: case["fixed"].append(["top"]), "stale"),
    ("ALL", lambda case: case.update(conclusion=["unary", "base", ["const", "x"]]), "stale"),
    ("NONE", lambda case: case["evidence"]["model"]["relations"].update(base=[]), "does not check"),
    ("NONE", lambda case: case.update(verdict="ALL"), "certificate"),
    ("SOME", lambda case: case["evidence"]["countermodel"].update(
        choice=case["evidence"]["proof"]["choice"]), "does not check"),
    ("SOME", lambda case: case["evidence"]["proof"].update(choice=[5]), "one reading of each set"),
])
def test_lean_rebuilds_premises_and_checks_evidence(monkeypatch, verdict, change, message):
    case = submitted(monkeypatch, verdict)
    assert relay.decide("readings", [case])[0]["verdict"] == verdict
    change(case)
    with pytest.raises(VEError, match=message):
        relay.decide("readings", [case])


def test_a_verdict_lean_does_not_confirm_is_unavailable(monkeypatch):
    from ve.backends.diagnostics import checker_error
    sets, conclusion, fixed = QUERIES["ALL"]
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    real = relay.decide

    def refuse(mode, batch, **kw):
        if mode == "readings":
            raise checker_error("the ALL evidence does not check")
        return real(mode, batch, **kw)

    monkeypatch.setattr(relay, "decide", refuse)
    with pytest.raises(CheckerUnavailable, match="does not check"):
        check_readings(env(), sets, conclusion, fixed=fixed)

    def other(mode, batch, **kw):
        rows = real(mode, batch, **kw)
        return [{**row, "verdict": "NONE"} for row in rows] if mode == "readings" else rows

    monkeypatch.setattr(relay, "decide", other)
    with pytest.raises(CheckerUnavailable):
        check_readings(env(), sets, conclusion, fixed=fixed)


@pytest.mark.parametrize("verdict", list(QUERIES))
def test_readings_over_a_norms_environment(monkeypatch, verdict):
    raw = pm.raw_environment(("norms@0",))
    norms_env = Environment(raw)
    sets, conclusion, fixed = QUERIES[verdict]
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = check_readings(norms_env, sets, conclusion, fixed=fixed)
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    calls = cases(monkeypatch)
    assert check_readings(norms_env, sets, conclusion, fixed=fixed) == expected
    assert [row["verdict"] for _, row in calls] == [verdict]


@pytest.mark.parametrize("family", [("closure@0",), ("closure@0", "nary@0"), ("order@0",),
                                    ("closure@0", "definitions@0"), ("closure@0", "nary@0", "data@0"),
                                    ("order@0", "norms@0")])
@pytest.mark.parametrize("verdict", list(QUERIES))
def test_readings_on_the_closure_core_and_order_families(monkeypatch, family, verdict):
    """Lean's readings mode checks verdicts over every family (VE/Service/Family.lean)."""
    family_env = Environment(pm.raw_environment(family))
    sets, conclusion, fixed = QUERIES[verdict]
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = check_readings(family_env, sets, conclusion, fixed=fixed)
    assert expected["verdict"] == verdict
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    calls = cases(monkeypatch)
    assert check_readings(family_env, sets, conclusion, fixed=fixed) == expected
    [(case, row)] = calls
    assert row["verdict"] == verdict
    if verdict == "NONE":
        case = copy.deepcopy(case)
        case["evidence"]["model"]["relations"]["base"] = []
        with pytest.raises(VEError, match="does not check"):
            relay.decide("readings", [case])


@pytest.mark.parametrize("kind", ["v0", "closure", "order"])
@pytest.mark.parametrize("verdict", list(QUERIES))
def test_readings_on_the_frozen_envelopes(monkeypatch, kind, verdict):
    from tests.test_stage2_graph import legacy_environment
    legacy = legacy_environment(kind)
    sets, conclusion, fixed = QUERIES[verdict]
    monkeypatch.setenv("VE_AUTHORITY", "python")
    expected = check_readings(legacy, sets, conclusion, fixed=fixed)
    assert expected["verdict"] == verdict
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    calls = cases(monkeypatch)
    assert check_readings(legacy, sets, conclusion, fixed=fixed) == expected
    assert [row["verdict"] for _, row in calls] == [verdict]
