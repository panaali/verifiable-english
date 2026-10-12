"""Reading-set verdicts on the Lean authority: Lean's `readings` mode checks the evidence."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ve.backends import dispatch, relay
from ve.backends.service_schema import Invalid, check_row
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


def _complete_choice_case(monkeypatch, *, joint=False):
    """Capture the genuine proposal that the Python search sends to Lean."""
    sets = [{"id": name, "version": 1, "unit": name, "status": "open",
             "readings": [
                 {"id": f"{name}-strict", "kind": "asserted", "content": formula,
                  "labels": {"force": "strict"}},
                 {"id": f"{name}-default", "kind": "asserted", "content": ["top"],
                  "labels": {"force": "default"}}]}
            for name, formula in (("a", ATOM), ("b", NEGATED))]
    coupling = {"id": "same-force", "axis": "force", "sets": [
        {"set": name, "version": 1} for name in ("a", "b")],
        "by": "translator", "reason_spans": ["a"]}
    joint_choices = {"status": "complete", "choices": [
        {"a@1": 0, "b@1": 0}, {"a@1": 1, "b@1": 1}]}
    captured = []
    real = relay.decide

    def spy(mode, batch, **kw):
        if mode == "readings-choices":
            captured.extend(copy.deepcopy(case) for case in batch if "choice_evidence" in case)
        return real(mode, batch, **kw)

    monkeypatch.setattr(relay, "decide", spy)
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    result = check_readings(env(), sets, ["bottom"],
                            **({"joint_choices": joint_choices} if joint else
                               {"couplings": [coupling]}))
    assert result["verdict"] == "SOME"
    assert len(captured) == 1
    return captured[0]


@pytest.mark.parametrize("joint", [False, True])
def test_complete_choice_verdict_is_lean_checked(monkeypatch, joint):
    case = _complete_choice_case(monkeypatch, joint=joint)
    assert relay.decide("readings-choices", [case])[0]["verdict"] == "SOME"
    assert {"certificate", "model"} <= {key for row in case["choice_evidence"] for key in row}


@pytest.mark.parametrize("mutation", [
    lambda c: c["choice_evidence"].pop(),
    lambda c: c["choice_evidence"].append(copy.deepcopy(c["choice_evidence"][0])),
    lambda c: c["choice_evidence"][0].update(choice=[True, 0]),
    lambda c: c["choice_evidence"][0].update(choice=[2, 0]),
    lambda c: c["choice_evidence"][0].update(certificate={}),
    lambda c: c["set_meta"][1]["readings"][0]["labels"].update(force="default"),
])
def test_coupled_choice_mutations_cannot_claim_a_verdict(monkeypatch, mutation):
    case = _complete_choice_case(monkeypatch)
    mutation(case)
    with pytest.raises(VEError):
        relay.decide("readings-choices", [case])


@pytest.mark.parametrize("mutation", [
    lambda c: c["choice_evidence"].pop(),
    lambda c: c["joint_choices"].append([0, 0]),
    lambda c: c["choice_evidence"][0].update(choice=[False, 0]),
])
def test_joint_choice_mutations_cannot_claim_a_verdict(monkeypatch, mutation):
    case = _complete_choice_case(monkeypatch, joint=True)
    mutation(case)
    with pytest.raises(VEError):
        relay.decide("readings-choices", [case])


def _coupled_plan_case(limit=64):
    return {"id": "plan", "kind": "plan", "limit": limit,
            "set_meta": [{"id": name, "version": 1, "unit": name,
                          "readings": [{"labels": {"force": value}}
                                       for value in ("strict", "default")]}
                         for name in ("a", "b")],
            "couplings": [{"id": "same-force", "axis": "force", "sets": [
                {"set": name, "version": 1} for name in ("a", "b")]}]}


@pytest.mark.parametrize("mutation", [
    lambda row: row["choices"][0].__setitem__(0, True),
    lambda row: row["choices"][0].__setitem__(0, 2),
    lambda row: row["choices"].append(row["choices"][0].copy()),
    lambda row: row.update(choices=[]),
    lambda row: row["conditional_on"].append("coupling:absent"),
    lambda row: row.pop("choices"),
    lambda row: row.update(extra=1),
])
def test_coupled_plan_response_is_typed_and_bound(mutation):
    case = _coupled_plan_case()
    row = relay.decide("readings-choices", [case])[0]
    assert row["choices"] == [[0, 0], [1, 1]]
    mutation(row)
    with pytest.raises(Invalid):
        check_row("readings-choices", row, case, 0)


@pytest.mark.parametrize("field,bad", [
    ("id", "other"), ("status", "UNKNOWN"), ("route", "UNKNOWN"),
    ("choices", True), ("conditional_on", ["coupling:absent"]),
])
def test_coupled_plan_every_field_is_typed_and_bound(field, bad):
    case = _coupled_plan_case()
    row = relay.decide("readings-choices", [case])[0]
    row[field] = bad
    with pytest.raises(Invalid):
        check_row("readings-choices", row, case, 0)


@pytest.mark.parametrize("mutation", [
    lambda row: row["units"].append("absent"),
    lambda row: row.update(choice_count=True),
    lambda row: row.update(choice_count=5),
    lambda row: row["budget"].update(max_choices=2),
])
def test_coupled_over_budget_response_is_typed_and_bound(mutation):
    case = _coupled_plan_case(limit=1)
    row = relay.decide("readings-choices", [case])[0]
    assert row["route"] == "UNKNOWN" and row["choice_count"] == 2
    mutation(row)
    with pytest.raises(Invalid):
        check_row("readings-choices", row, case, 0)


@pytest.mark.parametrize("field,bad", [
    ("id", "other"), ("status", "UNKNOWN"), ("route", "enumerate"),
    ("budget", {"max_choices": True}), ("choice_count", True), ("units", ["absent"]),
])
def test_coupled_unknown_every_field_is_typed_and_bound(field, bad):
    case = _coupled_plan_case(limit=1)
    row = relay.decide("readings-choices", [case])[0]
    row[field] = bad
    with pytest.raises(Invalid):
        check_row("readings-choices", row, case, 0)


@pytest.mark.parametrize("field,bad", [
    ("id", "other"), ("status", True), ("verdict", "YES"),
])
def test_coupled_verdict_every_field_is_typed_and_bound(monkeypatch, field, bad):
    case = _complete_choice_case(monkeypatch)
    row = relay.decide("readings-choices", [case])[0]
    row[field] = bad
    with pytest.raises(Invalid):
        check_row("readings-choices", row, case, 0)


def test_coupled_plan_refuses_unresolved_set():
    case = _coupled_plan_case()
    case["couplings"][0]["sets"][1]["set"] = "absent"
    with pytest.raises(VEError, match="invalid coupling set"):
        relay.decide("readings-choices", [case])


def test_coupled_plan_refuses_duplicate_set_version():
    case = _coupled_plan_case()
    case["set_meta"][1]["id"] = "a"
    with pytest.raises(VEError, match="duplicate reading set version"):
        relay.decide("readings-choices", [case])


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
