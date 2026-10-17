"""fu-rd9-checks: the two relay bindings rd-9's rechecks left open (rd-9-c141730 looprecheck1, FOLLOW-UP).

1. Binding-audit row 38: the rights report shows a rights-conflict answer's status line. Its Lean shape
   (`rights.json#/$defs/packages`) makes an UNKNOWN answer's line the UNKNOWN line, its `detail` a certificate failure
   and its `conditional_on` empty, and a CONFLICT-FREE answer's line the CONFLICT-FREE line. The relay binds the target
   an UNKNOWN line names to the request's targets, and the line to its detail (R8 (b)).
2. The `report_id` of a soft-norms or rights admission answer is the identity of its report over the environment and
   the document sent (`admission.report_identity`, which `bound_admission` checks on the core route).
"""
from __future__ import annotations

import copy

import pytest

from ve import rights_route, soft_route
from ve.backends.service_schema import Invalid, check_row
from ve.errors import CheckerUnavailable

ROW_38 = "CONFLICT-FREE among rules on the same act, conditional on 9 coherence premises and 0 limitation premises"
CONFLICT_UNBOUND = "CheckerUnavailable: Lean rights conflict is not bound to the request: unbound conflict status text"


@pytest.fixture(scope="module", autouse=True)
def _service():
    from tests.test_soft_norms_lean import SERVICE
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def _gamma():
    from tests.test_relay_binding_inventory import _rights_sources
    from ve.rights import RightsEnvironment
    raw, units = _rights_sources()["gamma"]
    return RightsEnvironment(raw), units


def _conflict(monkeypatch, mutation):
    """The rights report with Lean's package answer to `rights-conflict` mutated; returns the mutant and its case."""
    real, seen = rights_route.decide_once, {}

    def forged(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case["kind"] == "rights-conflict" and "witness" not in case:
            mutation(row)
            seen.update(row=row, case=case)
        return row

    monkeypatch.setattr(rights_route, "decide_once", forged)
    environment, units = _gamma()
    return lambda: rights_route.report_rights(environment, units), seen


def test_the_genuine_conflict_answer_is_unknown_and_shown():
    """The forgeries below start from this answer: no package is sent, so the one target's certificate is missing."""
    environment, units = _gamma()
    conflict = rights_route.report_rights(environment, units)["conflict"]
    assert conflict == {"verdict": "UNKNOWN", "targets": ["arrest_permitted"], "conditional_on": [],
                        "status_text": "UNKNOWN: missing certificate for arrest_permitted, budget 10000"}


def _set(**fields):
    def mutation(row):
        row.update(fields)
    return mutation


def _drop_detail(**fields):
    def mutation(row):
        row.pop("detail")
        row.update(fields)
    return mutation


@pytest.mark.parametrize("mutation", [
    # Row 38 as the audit wrote it: a CONFLICT-FREE line, with its counts, on an UNKNOWN verdict.
    pytest.param(_set(status_text=ROW_38, conditional_on=[]), id="row 38"),
    pytest.param(_set(status_text="ghost"), id="UNKNOWN line renamed"),
    pytest.param(_set(detail="ghost", status_text="UNKNOWN: ghost, budget 10000"), id="detail not a certificate"),
    pytest.param(_set(conditional_on=["soft:coherence:a,b"]), id="UNKNOWN conditional on a premise"),
    pytest.param(_drop_detail(verdict="CONFLICT-FREE"), id="CONFLICT-FREE with the UNKNOWN line"),
])
def test_a_status_line_of_the_wrong_verdict_does_not_fit_the_lean_shape(monkeypatch, mutation):
    call, seen = _conflict(monkeypatch, lambda row: None)
    call()
    check_row("rights", seen["row"], seen["case"], 0)
    forged = copy.deepcopy(seen["row"])
    mutation(forged)
    with pytest.raises(Invalid):
        check_row("rights", forged, seen["case"], 0)


@pytest.mark.parametrize("mutation", [
    pytest.param(_set(status_text="UNKNOWN: missing certificate for ghost, budget 10000"), id="line names ghost"),
    pytest.param(_set(detail="missing certificate for ghost",
                      status_text="UNKNOWN: missing certificate for ghost, budget 10000"), id="detail names ghost"),
    pytest.param(_set(status_text="UNKNOWN: invalid certificate for arrest_permitted, budget 10000"),
                 id="line and detail differ"),
    pytest.param(_set(status_text="UNKNOWN: missing certificate for arrest_permitted, budget 9999"),
                 id="budget shifted"),
    pytest.param(_set(detail="missing certificate for ", status_text="UNKNOWN: missing certificate for , budget 10000"),
                 id="no target"),
])
def test_an_unknown_line_naming_what_the_request_lacks_is_unavailable(monkeypatch, mutation):
    """Each forgery fits the shape, so only the relay's binding can refuse it."""
    call, seen = _conflict(monkeypatch, mutation)
    with pytest.raises(CheckerUnavailable) as raised:
        call()
    assert str(raised.value) == CONFLICT_UNBOUND
    check_row("rights", seen["row"], seen["case"], 0)


# ---------------------------------------------------------------------------------------------------
# report_id

SOURCES = {"rights": ("gamma", "carve-out"), "soft": ("open pair", "holistic")}


def _admission(family, name):
    """The admission call of one source of the binding inventory, and the module function it asks Lean through."""
    from tests import test_relay_binding_inventory as inventory
    if family == "rights":
        from ve.rights import RightsEnvironment
        raw, units = inventory._rights_sources()[name]
        environment = RightsEnvironment(raw)
        return inventory._rights_calls(name, environment, units)["rights-admission"], (rights_route, "decide")
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    raw, norms = inventory._soft_sources()[name]
    document = SoftNormDocument(SoftEnvironment(raw), norms)
    return inventory._soft_calls(name, document, raw, norms)["soft-admission"], (soft_route, "_run")


def _forge_admission(monkeypatch, family, mutation, name=None):
    call, (module, attr) = _admission(family, name or SOURCES[family][0])
    real, seen = getattr(module, attr), {}

    def forged(*args):
        rows = real(*args)
        listed = type(rows) is list
        cases = args[1] if listed else [args[-1]]
        out = []
        for case, row in zip(cases, rows if listed else [rows]):
            row = copy.deepcopy(row)
            if case["kind"] == "admission":
                seen["genuine"] = copy.deepcopy(row)
                mutation(row)
                check_row(family if family == "rights" else "soft-norms", row, case, 0)
            out.append(row)
        return out if listed else out[0]

    monkeypatch.setattr(module, attr, forged)
    return call, seen


@pytest.mark.parametrize("family", ["soft", "rights"])
def test_the_genuine_report_id_is_relayed(monkeypatch, family):
    call, seen = _forge_admission(monkeypatch, family, lambda row: None)
    assert call()["report_id"] == seen["genuine"]["report_id"]


def _other_sources_id(family):
    """The genuine report id of another source's admission: a well-formed id this request did not get."""
    with pytest.MonkeyPatch.context() as patch:
        call, seen = _forge_admission(patch, family, lambda row: None, SOURCES[family][1])
        call()
    return seen["genuine"]["report_id"]


@pytest.mark.parametrize("family", ["soft", "rights"])
@pytest.mark.parametrize("forged", ["zero hash", "reversed", "another source's"])
def test_a_report_id_of_another_report_is_unavailable(monkeypatch, family, forged):
    other = _other_sources_id(family) if forged == "another source's" else None

    def mutation(row):
        row["report_id"] = {"zero hash": "0" * 64, "reversed": row["report_id"][::-1]}.get(forged, other)
        assert row["report_id"] != seen["genuine"]["report_id"]

    call, seen = _forge_admission(monkeypatch, family, mutation)
    with pytest.raises(CheckerUnavailable) as raised:
        call()
    assert str(raised.value) == (f"CheckerUnavailable: Lean {family} admission is not bound to the request: "
                                 f"unbound {family} admission report id")
