"""Every public verdict op of the readings routes under a zero budget (build checklist 6; rd-2b review B1).

With the prover, the model search and the evaluator all at budget 0 nothing can be certified or found, so every
answer that rests on evidence is UNKNOWN: never CONFLICT-FREE, CONFLICT, model, INCONSISTENT, ALL, SOME, NONE or NOT
ALL, and never a certificate or a model. The sweep runs on both routes and on every enumerated kind of choice
document: the completion's filled documents (F-ND1, F-ND2), the norms chain (M9) and the soft chain (M8), and the
superposed route (M6); and through `ve document check` and `readings --conclusion` on the completion. Which ops are
swept is checked against the classes themselves: a new public op must be listed here as swept or as not budgeted.
"""
from __future__ import annotations

import json

import pytest

from tests import lean_routes
from tests.test_readings_nd_document import QUERY, fnd1, fnd2
from tests.test_readings_s2_document import _m6, _m8, _m9
from ve import readings_verdicts
from ve.document import check_document, load_document, main
from ve.readings_verdicts import Enumerated, Superposed, _ChoiceDocument, _FilledChoiceDocument, context

# The ops whose answers rest on a certificate, a model or a witness (each swept below), and the rest with why not.
SWEPT = {
    Superposed: {"conflict", "model", "certificate", "premises", "candidate_premises", "dead_readings", "entailment",
                 "report_fields", "conflict_answer", "premises_answer", "query_answer", "answer_for"},
    Enumerated: {"conflict", "premises", "dead_readings", "entailment", "report_fields", "conflict_answer",
                 "premises_answer", "query_answer"},
    # RD-3: a choice's document only generates evidence; Lean checks and folds it (`readings-verdicts`).
    _ChoiceDocument: {"conflict_case", "witness_case", "certificate_case", "model_case"},
    _FilledChoiceDocument: {"conflict_case", "witness_case", "certificate_case", "model_case"},
}
NOT_BUDGETED = {
    "lean": "the relay to Lean's service, no search",
    "choice_json": "a choice's JSON form", "choice_text": "a choice's text", "untaken_text": "a diagnostic's text",
    "candidates": "the candidates of the sets", "dropped": "the narrowing in force, read from the document",
    "restrictions": "the couplings and narrowings in force, read from the document",
    "taken": "whether a compatible choice takes the candidates: the enumeration itself",
    "over_budget": "the constant answer past 64 choices", "base": "the base environment",
    "check_answer": "Lean's answer checked against its request, no search",
    "frame": "the request's document decoded for that check, no search",
}
X_REQUIRED = ["forall", "act", ["unary", "x_required", ["var", 0]]]  # F-ND2's query (the gated one)
FIXTURES = {"F-ND1": (fnd1, QUERY), "F-ND1 enumerated oracle": (fnd1, QUERY),
            "F-ND2": (fnd2, X_REQUIRED), "M9": (_m9, None), "M8": (_m8, None),
            "M6": (_m6, None)}


def fixture_route(name, tmp_path):
    """Keep RD-3's filled choice checker covered after RD-6b makes F-ND1's public route superposed; F-ND1's filled
    choice document is also swept directly on the superposed route."""
    make, _ = FIXTURES[name]
    doc = load_document(make(tmp_path))
    if name == "F-ND1 enumerated oracle":
        row = doc["readings_s2"]
        row["route"] = "enumerated"
        row["finding"] = {"text": "ReadingsNotSuperposable: rs_1", "cause": "the unspecified completion"}
    return context(doc)


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


@pytest.fixture
def zero(monkeypatch):
    for key in readings_verdicts.BUDGET:
        monkeypatch.setitem(readings_verdicts.BUDGET, key, 0)


def unknown(answer, key):
    assert answer[key] == "UNKNOWN", answer
    return answer


def public(cls):
    """The public methods and properties of `cls` and its bases (constants such as `chain` are not ops)."""
    return {name for klass in cls.__mro__ if klass is not object for name, value in vars(klass).items()
            if not name.startswith("_") and (callable(value) or isinstance(value, property))}


@pytest.mark.parametrize("cls", list(SWEPT), ids=lambda cls: cls.__name__)
def test_every_public_op_is_swept_or_named_unbudgeted(cls):
    assert public(cls) - set(NOT_BUDGETED) == SWEPT[cls]


def sweep_choice(document, conclusion):
    """A choice's own document generates nothing at budget 0: no conflict package, witness, certificate or model."""
    assert document.conflict_case()["packages"] == {}
    assert document.witness_case() is None
    assert document.certificate_case(conclusion) is None and document.certificate_case(None) is None
    assert document.model_case(conclusion) is None and document.model_case(None) is None


def sweep_enumerated(route, conclusion):
    conflict = unknown(route.conflict(), "status")
    assert [c["status"] for c in conflict["choices"]] == ["UNKNOWN"] * len(route.choices)
    assert not conflict["witnesses"]
    premises = unknown(route.premises(), "status")
    assert {c["status"] for c in premises["choices"]} == {"UNKNOWN"} and "model" not in premises
    assert {c["status"] for c in premises["candidates"]} <= {"UNKNOWN", "narrowed"}
    unknown(route.entailment(conclusion), "verdict")
    for candidate in route.candidates():
        unknown(route.entailment(conclusion, assumed=[candidate]), "verdict")
    for choice in route.choices:
        sweep_choice(route._choice(choice), conclusion)
    return route.report_fields()


def sweep_superposed(route, conclusion):
    unknown(route.conflict(), "status")
    unknown(route.conflict_answer()["result"], "status")
    assert route.model() is None and route.model(conclusion=conclusion) is None
    assert route.certificate() is None and route.certificate(conclusion=conclusion) is None
    premises = unknown(route.premises(), "status")
    unknown(route.premises_answer()["result"], "status")
    assert "model" not in premises
    assert {c["status"] for c in route.candidate_premises()} <= {"UNKNOWN", "narrowed"}
    result = unknown(route.entailment(conclusion), "verdict")
    answer = route.query_answer(conclusion)
    unknown(answer["result"], "verdict")
    assert route.answer_for(result, conclusion) is answer
    for candidate in route.candidates():
        unknown(route.conflict([candidate]), "status")
        assert route.model([candidate]) is None and route.certificate([candidate]) is None
        unknown(route.entailment(conclusion, assumed=[candidate]), "verdict")
    return route.report_fields()


@pytest.mark.parametrize("name", list(FIXTURES))
def test_budget_zero_every_verdict_op_is_unknown(name, tmp_path, zero):
    make, conclusion = FIXTURES[name]
    route = fixture_route(name, tmp_path)
    if isinstance(route, Enumerated):
        kind = _FilledChoiceDocument if route.completion else _ChoiceDocument
        assert all(type(route._choice(c)) is kind for c in route.choices)
        report = sweep_enumerated(route, conclusion)
    else:
        assert isinstance(route, Superposed)
        report = sweep_superposed(route, conclusion)
        if name == "F-ND1":
            sweep_choice(_FilledChoiceDocument(route, route.choices[0]), conclusion)
    assert report["status"].startswith("UNKNOWN") and report["conflict"]["status"] == "UNKNOWN"
    # Every candidate of these fixtures is taken by a compatible choice: none is dead whatever the budget.
    assert report["dead_readings"] in (None, []) and route.dead_readings() in (None, [])


@pytest.mark.parametrize("name", list(FIXTURES))
def test_budget_zero_after_the_conflict_status_is_certified(name, tmp_path, monkeypatch):
    """The ops past the conflict gate: each conflict status is certified at the full budget first (and kept, as the
    routes keep it), then the prover and the model search get none. Under a CONFLICT-FREE reading the entailment and
    premise searches reach their own fallbacks, which must be UNKNOWN too."""
    make, conclusion = FIXTURES[name]
    route = fixture_route(name, tmp_path)
    if isinstance(route, Enumerated):
        documents = [route._choice(c) for c in route.choices]
        free = [e["conflict"] == "CONFLICT-FREE" for e in route.conflict_answer()["per_choice"]]
    else:
        free = [route.conflict(A)["status"] == "CONFLICT-FREE" for A in [()] + [[c] for c in route.candidates()]]
    assert any(free), name
    for key in readings_verdicts.BUDGET:
        monkeypatch.setitem(readings_verdicts.BUDGET, key, 0)
    unknown(route.entailment(conclusion), "verdict")
    for candidate in route.candidates():
        unknown(route.entailment(conclusion, assumed=[candidate]), "verdict")
    unknown(route.premises(), "status")
    if isinstance(route, Enumerated):
        for document in documents:
            assert document.certificate_case(conclusion) is None and document.model_case(conclusion) is None
            assert document.certificate_case(None) is None and document.model_case(None) is None
        # Lean's rows past the gate: a CONFLICT-FREE reading's query and premise rows have no result.
        rows = route.query_answer(conclusion)["per_choice"]
        assert rows and {e["query"] for e in rows} == {"UNKNOWN"}
        assert {e["premises"] for e in route.premises_answer()["per_choice"]} == {"UNKNOWN"}
    else:
        for A in [()] + [[c] for c in route.candidates()]:
            assert route.certificate(A, conclusion=conclusion) is None and route.model(A, conclusion=conclusion) is None
        assert {c["status"] for c in route.candidate_premises()} <= {"UNKNOWN", "narrowed"}


def test_budget_zero_fixtures_cover_every_choice_document_kind(tmp_path):
    kinds = set()
    for name, (make, _) in FIXTURES.items():
        (tmp_path / name).mkdir()
        route = fixture_route(name, tmp_path / name)
        kinds.add(type(route) if not isinstance(route, Enumerated) else
                  _FilledChoiceDocument if route.completion else _ChoiceDocument)
        if name == "F-ND1":
            kinds.add(type(_FilledChoiceDocument(route, route.choices[0])))
    assert kinds == {Superposed, _ChoiceDocument, _FilledChoiceDocument}


# ---------------------------------------------------------------------------------------------------------------
# The finding's case through `ve document`: F-ND2 has a real conflict under rs_2:0, F-ND1 none; at budget 0 neither
# is certified either way, and no English line says the rules do not contradict each other.

@pytest.mark.parametrize("make", [fnd1, fnd2], ids=["F-ND1", "F-ND2"])
def test_budget_zero_check_says_unknown_for_every_choice(make, tmp_path, zero):
    report = check_document(make(tmp_path))
    readings = report["readings"]
    assert readings["conflict"]["status"] == "UNKNOWN"
    assert readings["status"].startswith("UNKNOWN: tableau budget or open branch:")
    # RD-3's per-choice conflict statuses, kept on the superposed route (review B3 of rd-6b); the premise status is
    # given per reading there (docs/readings-defaults/rd6b/DELTA.md).
    assert {c["status"] for c in readings["conflict"]["choices"]} == {"UNKNOWN"}
    assert report["premises"]["status"] == "UNKNOWN"
    assert report["premises"].get("choices") is None
    assert {c["status"] for c in report["premises"]["candidates"]} == {"UNKNOWN"}
    # Only the route line: no conflict-free sentence, no conflict witness.
    assert readings["english"] == []


@pytest.mark.parametrize("name", ["F-ND1", "F-ND2"])
def test_budget_zero_query_is_unknown_under_every_reading(name, tmp_path, capsys, zero):
    make, query = FIXTURES[name]
    path = make(tmp_path)
    conclusion = tmp_path / "conclusion.json"
    conclusion.write_text(json.dumps(query))
    route = context(load_document(path))
    for under in [[]] + [["--under", f"{s}:{i}"] for s, i in route.candidates()]:
        assert main(["readings", str(path), "--conclusion", str(conclusion), *under]) == 0
        data = json.loads(capsys.readouterr().out)
        assert data["verdict"] == "UNKNOWN", (under, data)
        assert data.get("conflict_status", "UNKNOWN") == "UNKNOWN", (under, data)
