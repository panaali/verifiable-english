"""`ve.soft_route.decide_soft_conflict` (kb-10c): `check_conflict` on a soft document decided by Lean's soft route.

Python's witness search and prover only propose; the soft route's `witness` and `packages` cases decide CONFLICT and
CONFLICT-FREE, and their answers are bound to the request (the witness's target, the UNKNOWN detail's target) or the
call is CheckerUnavailable. Fixtures: the two-rule soft document of tests/test_soft_norms_lean.py (`a` requires `x`,
`b` forbids permitting it; CONFLICT-FREE conditional on `soft:coherence:a,b`) and kb-3's strict pair `h`/`k`
(tests/test_slot_premises.py), which conflict at an assistant with both `v` and `w`.
"""
from __future__ import annotations

import pytest

from tests.test_slot_premises import EXCLUDED, FACTS_MODEL, document as strict_document
from tests.test_soft_norms_lean import env, should
from ve import soft_route
from ve.errors import CheckerUnavailable
from ve.norms import check_conflict
from ve.softnorms import SoftEnvironment, SoftNormDocument


def delta_document():
    return SoftNormDocument(SoftEnvironment(env()), [should("a", "x_required", True), should("b", "x_permitted", False)])


@pytest.fixture(autouse=True)
def fresh_answers(monkeypatch):
    """Each test starts with no kept Lean answers, so an earlier test's answer cannot stand in for a call."""
    monkeypatch.setattr(soft_route, "_CONFLICTS", {})


@pytest.fixture
def sent(monkeypatch):
    """The cases the soft route is sent, with Lean's real answers."""
    cases, real = [], soft_route.check_soft_conflict

    def recording(soft_document, **case):
        cases.append(case)
        return real(soft_document, **case)
    monkeypatch.setattr(soft_route, "check_soft_conflict", recording)
    return cases


def answering(monkeypatch, change):
    """Lean's real answer, edited by `change` before the caller reads it."""
    real = soft_route.check_soft_conflict
    monkeypatch.setattr(soft_route, "check_soft_conflict", lambda doc, **case: change(real(doc, **case), case))


def test_conflict_free_is_lean_s_and_names_its_condition(sent):
    doc = delta_document()
    report = soft_route.decide_soft_conflict(doc, prove=True)
    assert report.status == check_conflict(doc.elaborated, prove=True).status == "CONFLICT-FREE"
    assert "among rules on the same act, conditional on 1 coherence premises" in report.detail
    [case] = sent
    # Python's certificates, one per target, re-bound to the soft source's identity.
    assert {p["environment_id"] for p in case["packages"].values()} == {doc.env.environment_id}
    assert {p["document_hash"] for p in case["packages"].values()} == {doc.document_hash}
    assert sorted(case["packages"]) == sorted(name for name, *_ in doc.elaborated.conflict_targets())


def test_a_witness_python_finds_is_confirmed_by_lean_with_python_s_situation(sent):
    doc = strict_document()
    report = soft_route.decide_soft_conflict(doc, model=EXCLUDED, prove=True)
    python = check_conflict(doc.elaborated, model=EXCLUDED, prove=True)
    assert (report.status, report.target, report.tuple) == ("CONFLICT", "x_required", ("a",))
    assert (report.status, report.target, report.tuple, report.situation) == \
        (python.status, python.target, python.tuple, python.situation)
    assert "rule h requires" in report.situation and "rule k" in report.situation
    assert [set(case) for case in sent] == [{"witness"}]
    assert sent[0]["witness"]["target"] == "x_required" and sent[0]["witness"]["tuple"] == ["a"]


def test_no_witness_and_no_proof_is_unknown_without_asking_lean(sent):
    doc = strict_document()
    assert soft_route.decide_soft_conflict(doc, model=FACTS_MODEL, prove=True).status == "UNKNOWN"
    assert soft_route.decide_soft_conflict(delta_document()).detail == "tableau budget or search bound"
    assert sent == []


def test_a_zero_budget_is_unknown_never_a_verdict(sent):
    assert soft_route.decide_soft_conflict(strict_document(), model=EXCLUDED, max_evaluations=0).detail == \
        "MAX_EVALUATIONS"
    report = soft_route.decide_soft_conflict(delta_document(), prove=True, tableau_steps=0)
    assert report.status == "UNKNOWN" and report.detail.startswith("tableau budget or open branch")
    assert sent == []


def test_a_witness_lean_does_not_confirm_is_checker_unavailable(monkeypatch):
    answering(monkeypatch, lambda row, case: {**row, "verdict": "UNKNOWN"})
    with pytest.raises(CheckerUnavailable, match="does not confirm"):
        soft_route.decide_soft_conflict(strict_document(), model=EXCLUDED)


def test_a_witness_confirmed_for_another_target_is_checker_unavailable(monkeypatch):
    answering(monkeypatch, lambda row, case: {**row, "target": "x_permitted"})
    with pytest.raises(CheckerUnavailable, match="does not confirm"):
        soft_route.decide_soft_conflict(strict_document(), model=EXCLUDED)


def test_lean_s_unknown_is_kept_when_its_detail_names_a_sent_target(monkeypatch):
    def unknown(row, case):
        return {**row, "verdict": "UNKNOWN", "detail": f"invalid certificate for {row['targets'][0]}"}
    answering(monkeypatch, unknown)
    report = soft_route.decide_soft_conflict(delta_document(), prove=True)
    assert report.status == "UNKNOWN" and report.detail.startswith("invalid certificate for ")


@pytest.mark.parametrize("change", [
    {"verdict": "UNKNOWN", "detail": "invalid certificate for absent"},
    {"verdict": "UNKNOWN", "detail": "no reason"},
    {"verdict": "UNKNOWN", "detail": 7},
    {"verdict": "UNKNOWN"},
    {"verdict": "CONFLICT"},
], ids=["unsent-target", "free-text", "typed-int", "no-detail", "conflict-on-packages"])
def test_an_unbound_packages_answer_is_checker_unavailable(monkeypatch, change):
    def edited(row, case):
        out = {key: value for key, value in row.items() if key != "detail"}
        return {**out, **change}
    answering(monkeypatch, edited)
    with pytest.raises(CheckerUnavailable, match="not bound to the request"):
        soft_route.decide_soft_conflict(delta_document(), prove=True)


def test_a_repeated_request_is_answered_once_and_a_different_one_is_asked(sent):
    """The kept answers are keyed by the whole request: the same document, model and certificates are sent once;
    another document, or another model, is sent again (and keeps its own answer)."""
    delta, strict = delta_document(), strict_document()
    first = soft_route.decide_soft_conflict(delta, prove=True)
    again = soft_route.decide_soft_conflict(delta_document(), prove=True)
    assert (first.status, again.status, len(sent)) == ("CONFLICT-FREE", "CONFLICT-FREE", 1)
    witnessed = soft_route.decide_soft_conflict(strict, model=EXCLUDED)
    assert witnessed.status == "CONFLICT" and len(sent) == 2
    assert soft_route.decide_soft_conflict(strict, model=EXCLUDED).status == "CONFLICT" and len(sent) == 2
    other = {**EXCLUDED, "domains": {"assistant": ["a", "b"], "user": []},
             "relations": {"v": [["a"]], "w": [["a"]]}}
    assert soft_route.decide_soft_conflict(strict, model=other).status == "CONFLICT" and len(sent) == 3
    assert [set(case) for case in sent] == [{"packages"}, {"witness"}, {"witness"}]


def test_kept_answer_includes_the_rules_with_the_same_environment_and_case(sent):
    """A certificate accepted for one soft source cannot supply another source's kept answer."""
    first = delta_document()
    second = SoftNormDocument(SoftEnvironment(env()), [should("a", "x_required", True)])
    assert first.env.to_dict() == second.env.to_dict()
    assert first.document_hash != second.document_hash
    assert soft_route.decide_soft_conflict(first, prove=True).status == "CONFLICT-FREE"
    [case] = sent
    assert set(case) == {"packages"}
    assert soft_route._kept_conflict(first, **case)["verdict"] == "CONFLICT-FREE"
    assert len(sent) == 1
    other = soft_route._kept_conflict(second, **case)
    assert other["verdict"] == "UNKNOWN"
    assert other["detail"].startswith("missing certificate for ")
    assert len(sent) == 2
