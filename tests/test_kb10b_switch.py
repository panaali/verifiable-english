"""kb-10b steps (2)-(4): a soft document's selected rules and completed outcomes are Lean's `soft-selected` answers.

`SoftenedNormDocument.selected_rules` and `SoftenedNormDocument.outcome_at` read Lean's bound answer
(`ve.softnorms.selected_at`, which `ve.soft_route.selected_at` relays through its own runner) for a document
built by `SoftNormDocument`. One call per (document, model) sends every query the pair can be asked; the answers are kept per document request and model. Over Lean's
query limit the pair is asked per predicate, then per query. A hand-built document without its soft source
keeps Python's path. The three safety-framework harnesses' `completed` read `outcome_at`.

The fixture is kb-10a's three-rule document (tests/test_soft_selected.py): per tuple of `x_required`, the
rules Lean selects and the completed outcome under the deny and allow defaults.
"""
from __future__ import annotations

import copy
import sys
import types
from pathlib import Path

import pytest

from tests.test_soft_selected import EXPECTED, MODEL, document, lean  # noqa: F401  (`lean` is a fixture)
from tests.usecase_scope import load_script, sibling_names, usecase_scope
from ve import soft_route, softnorms
from ve.errors import CheckerUnavailable, ResourceLimit, VEError
from ve.model import FiniteModel
from ve.softnorms import SoftenedNormDocument

ROOT = Path(__file__).resolve().parents[1]
TUPLES = sorted(EXPECTED)


@pytest.fixture
def calls(monkeypatch):
    """Every `selected_at` call (its query list), answered by Lean; and an empty answer cache."""
    monkeypatch.setattr(softnorms, "_SELECTIONS", type(softnorms._SELECTIONS)())
    sent = []
    genuine = softnorms.selected_at

    def recording(doc, model, queries):
        sent.append([(q[0], tuple(q[1])) for q in queries])
        return genuine(doc, model, queries)
    monkeypatch.setattr(softnorms, "selected_at", recording)
    return sent


def model_of(doc, data=MODEL):
    return FiniteModel.from_dict(doc.elaborated.base_environment(), data)


@pytest.mark.parametrize("default", ["deny", "allow"])
def test_selected_rules_and_outcomes_are_leans_answers_at_each_tuple(lean, calls, default):
    """Each tuple gets its own row: the rules selected there and the outcome there, not a neighbour's."""
    doc = document(default)
    model = model_of(doc)
    for t in TUPLES:
        selected, deny, allow = EXPECTED[t]
        assert [r.name for r in doc.elaborated.selected_rules("x_required", model, (t,))] == selected, t
        assert doc.elaborated.outcome_at("x_required", model, (t,)) is (deny if default == "deny" else allow), t
    # x_permitted has no rule: nothing selected, its own default (allow) decides.
    assert doc.elaborated.selected_rules("x_permitted", model, ("a",)) == ()
    assert doc.elaborated.outcome_at("x_permitted", model, ("a",)) is True
    assert len(calls) == 1


def test_selected_rules_returns_the_documents_rule_objects_in_rule_order(lean, calls):
    doc = document()
    model = model_of(doc)
    [rule] = doc.elaborated.selected_rules("x_required", model, ("c",))
    assert rule is doc.elaborated.by_name["d"] and rule.sign is True


def test_the_outcome_is_not_the_truth_of_the_selection(lean, calls):
    """At `a` a rule is selected (`o`, the negative default) and the deny outcome is false; at `e` nothing is
    selected and the allow outcome is true. An outcome read from the selection gets both wrong."""
    deny, allow = document("deny"), document("allow")
    assert deny.elaborated.selected_rules("x_required", model_of(deny), ("a",))
    assert deny.elaborated.outcome_at("x_required", model_of(deny), ("a",)) is False
    assert not allow.elaborated.selected_rules("x_required", model_of(allow), ("e",))
    assert allow.elaborated.outcome_at("x_required", model_of(allow), ("e",)) is True


def test_one_call_per_document_and_model_sends_every_query_of_the_pair(lean, calls):
    """The first question sends every regulated predicate (rule order first) times every tuple over the model's
    domains, in product order; later questions of the pair, and of a rebuilt copy of the document, send none."""
    doc = document()
    model = model_of(doc)
    doc.elaborated.outcome_at("x_required", model, ("e",))
    every = [("x_required", (t,)) for t in "abce"] + [("x_permitted", (t,)) for t in "abce"]
    assert calls == [every]
    for t in TUPLES:
        doc.elaborated.selected_rules("x_required", model, (t,))
    again = document()
    again.elaborated.selected_rules("x_permitted", model_of(again), ("b",))
    assert len(calls) == 1


def test_another_model_or_another_document_is_another_call(lean, calls):
    doc = document()
    other = copy.deepcopy(MODEL)
    other["relations"]["v"] = [["c"]]
    assert [r.name for r in doc.elaborated.selected_rules("x_required", model_of(doc), ("b",))] == ["h"]
    assert [r.name for r in doc.elaborated.selected_rules("x_required", model_of(doc, other), ("b",))] == ["d"]
    allow = document("allow")
    allow.elaborated.outcome_at("x_required", model_of(allow), ("e",))
    assert len(calls) == 3


def test_a_wire_dictionary_model_is_the_same_pair_as_its_finite_model(lean, calls):
    doc = document()
    assert doc.elaborated.outcome_at("x_required", model_of(doc), ("b",)) is True
    assert doc.elaborated.outcome_at("x_required", model_of(doc).to_dict(), ("c",)) is True
    assert len(calls) == 1


def test_kept_answers_are_bounded_least_recently_used_first_out(lean, calls, monkeypatch):
    monkeypatch.setattr(softnorms, "SELECTION_DOCUMENTS", 1)
    deny, allow = document("deny"), document("allow")
    deny.elaborated.outcome_at("x_required", model_of(deny), ("b",))
    allow.elaborated.outcome_at("x_required", model_of(allow), ("b",))
    allow.elaborated.outcome_at("x_required", model_of(allow), ("e",))
    assert len(calls) == 2
    deny.elaborated.outcome_at("x_required", model_of(deny), ("e",))
    assert len(calls) == 3


def limited(monkeypatch, limit):
    """A relay that refuses a query list longer than `limit` as the relay raises Lean's limit (the class
    `ResourceLimit`, Lean's wire code), and asks Lean otherwise."""
    monkeypatch.setattr(softnorms, "_SELECTIONS", type(softnorms._SELECTIONS)())
    sent = []
    genuine = softnorms.selected_at

    def relay(doc, model, queries):
        sent.append([(q[0], tuple(q[1])) for q in queries])
        if len(queries) > limit:
            error = ResourceLimit(f"ResourceLimit: soft-selected queries over {limit}")
            error.code = "SOFT_RESOURCE_LIMIT"
            raise error
        return genuine(doc, model, queries)
    monkeypatch.setattr(softnorms, "selected_at", relay)
    return sent


def test_over_the_query_limit_the_pair_is_asked_per_predicate(lean, monkeypatch):
    sent = limited(monkeypatch, 4)
    doc = document()
    model = model_of(doc)
    for t in TUPLES:
        assert [r.name for r in doc.elaborated.selected_rules("x_required", model, (t,))] == EXPECTED[t][0]
    assert doc.elaborated.outcome_at("x_permitted", model, ("c",)) is True
    by_predicate = [[(p, (t,)) for t in "abce"] for p in ("x_required", "x_permitted")]
    assert sent == [[*by_predicate[0], *by_predicate[1]], by_predicate[0], by_predicate[1]]


def test_over_the_limit_for_one_predicate_each_query_is_asked_alone_never_truncated(lean, monkeypatch):
    sent = limited(monkeypatch, 1)
    doc = document()
    model = model_of(doc)
    assert doc.elaborated.outcome_at("x_required", model, ("b",)) is True
    assert doc.elaborated.outcome_at("x_required", model, ("e",)) is False
    assert [len(s) for s in sent] == [8, 4, 1, 1]
    assert sent[2:] == [[("x_required", ("b",))], [("x_required", ("e",))]]


def test_within_the_limit_the_pair_is_one_call(lean, monkeypatch):
    sent = limited(monkeypatch, 8)
    doc = document()
    doc.elaborated.outcome_at("x_required", model_of(doc), ("b",))
    doc.elaborated.outcome_at("x_permitted", model_of(doc), ("b",))
    assert [len(s) for s in sent] == [8]


def test_a_refusal_other_than_the_limit_is_raised_not_answered(lean, monkeypatch):
    monkeypatch.setattr(softnorms, "_SELECTIONS", type(softnorms._SELECTIONS)())
    monkeypatch.setattr(softnorms, "selected_at",
                        lambda *a: (_ for _ in ()).throw(VEError("InvalidInput: query 0: refused")))
    doc = document()
    with pytest.raises(VEError, match="query 0: refused"):
        doc.elaborated.selected_rules("x_required", model_of(doc), ("b",))
    monkeypatch.setattr(softnorms, "selected_at",
                        lambda *a: (_ for _ in ()).throw(CheckerUnavailable("CheckerUnavailable: not bound")))
    with pytest.raises(CheckerUnavailable):
        doc.elaborated.outcome_at("x_required", model_of(doc), ("b",))


def test_an_unbound_answer_is_unavailable_through_the_document(lean, monkeypatch):
    """The relay's binding stands between Lean and the document: a row for a tuple that was not sent at its
    position is CheckerUnavailable, not an answer."""
    monkeypatch.setattr(softnorms, "_SELECTIONS", type(softnorms._SELECTIONS)())
    real = softnorms._relay_run

    def shifted(case):
        row = real(case)
        row["results"] = row["results"][1:] + row["results"][:1]
        return row
    monkeypatch.setattr(softnorms, "_relay_run", shifted)
    doc = document()
    with pytest.raises(CheckerUnavailable, match="not bound to the request"):
        doc.elaborated.selected_rules("x_required", model_of(doc), ("b",))


def test_the_public_relay_sends_the_same_request_and_binds_the_same_answer(lean, monkeypatch):
    """`ve.soft_route.selected_at` is `ve.softnorms.selected_at` through the route's runner (`soft_route._run`)."""
    sent = []
    monkeypatch.setattr(soft_route, "_run", lambda case: sent.append(case) or softnorms._relay_run(case))
    doc = document()
    queries = [("x_required", ["c"]), ("x_permitted", ["a"])]
    assert soft_route.selected_at(doc, MODEL, queries) == softnorms.selected_at(doc, MODEL, queries)
    assert sent[0]["queries"] == [{"predicate": p, "tuple": t} for p, t in queries]


@pytest.mark.parametrize("predicate, values, message", [
    ("x_required", ("a", "b"), "InvalidModel: witness tuple has wrong length or sort"),
    ("x_required", ("zz",), "InvalidModel: witness tuple has wrong length or sort"),
    ("v", ("a",), "UnknownSymbol: regulated predicate v"),
])
def test_a_query_outside_the_document_is_refused_as_before_without_a_call(lean, calls, predicate, values, message):
    doc = document()
    model = model_of(doc)
    for ask in (doc.elaborated.selected_rules, doc.elaborated.outcome_at):
        with pytest.raises(VEError, match=message):
            ask(predicate, model, values)
    assert calls == []


def test_a_document_without_its_soft_source_keeps_pythons_path(lean, calls):
    """A hand-built SoftenedNormDocument has no soft source: Python's selection and outcome answer, no Lean call;
    they agree with Lean's on the fixture (the shadow's evidence, kb-10b step (1))."""
    for default in ("deny", "allow"):
        doc = document(default)
        bare = SoftenedNormDocument(doc.extended_env, list(doc.elaborated.rules))
        model = model_of(doc)
        for t in TUPLES:
            selected, deny, allow = EXPECTED[t]
            assert [r.name for r in bare.selected_rules("x_required", model, (t,))] == selected
            assert bare.outcome_at("x_required", model, (t,)) is (deny if default == "deny" else allow)
    assert calls == []


def test_a_document_from_its_soft_source_never_runs_pythons_selection(lean, calls, monkeypatch):
    """No `NormDocument.selection`, `outcome` or `_Evaluator` runs in `selected_rules` and `outcome_at` (the model
    is built first: `FiniteModel.from_dict` checks the soft background in Python, a separate path)."""
    import importlib
    evaluate, norms = importlib.import_module("ve.evaluate"), importlib.import_module("ve.norms")
    doc = document()
    model = model_of(doc)

    def forbidden(*args, **kwargs):
        raise AssertionError("Python selection or evaluation ran")
    monkeypatch.setattr(norms.NormDocument, "selection", forbidden)
    monkeypatch.setattr(norms.NormDocument, "outcome", forbidden)
    monkeypatch.setattr(evaluate, "_Evaluator", forbidden)
    assert [r.name for r in doc.elaborated.selected_rules("x_required", model, ("b",))] == ["h"]
    assert doc.elaborated.outcome_at("x_required", model, ("e",)) is False


# -- the harnesses' `completed` -------------------------------------------------------------------

HARNESSES = ("anthropic-rsp", "safety-framework", "openai-preparedness")


def harness(name):
    """The harness's `run.py`, loaded with its own sibling modules (tests/usecase_scope.py): another use case's
    `translation`, `run` or `reference` already in `sys.modules` is not used, and the harness leaves none behind."""
    return load_script(ROOT / "usecases" / name / "run.py", f"kb10b_switch_{name.replace('-', '_')}")


class _Elaborated:
    order = ("act",)

    def __init__(self, answer):
        self.answer, self.asked = answer, []

    def outcome_at(self, predicate, model, values):
        self.asked.append((predicate, model, values))
        return self.answer


@pytest.mark.parametrize("answer", [True, False])
def test_the_harnesses_completed_is_outcome_at(monkeypatch, answer):
    """Each harness's `completed` returns `outcome_at`'s answer for its case model, predicate and tuple (RSP: the
    case's model; FSF: the model it is given; Preparedness: the case model at the predicate's subject)."""
    for name, args, expected in (
            ("anthropic-rsp", ("case", "act", ["s", "t"]), ("act", "M", ("s", "t"))),
            ("safety-framework", ("M", "act", ["p"]), ("act", "M", ("p",))),
            ("openai-preparedness", ("found", "act"), ("act", "M", ("k",)))):
        with usecase_scope(ROOT / "usecases" / name):  # a sibling `completed` imports late is the harness's own
            module = harness(name)
            monkeypatch.setattr(module, "model", lambda *a: "M", raising=False)
            monkeypatch.setattr(module, "subject", lambda predicate: ("capability", "k"), raising=False)
            doc = type("Doc", (), {"elaborated": _Elaborated(answer)})()
            assert module.completed(doc, *args) is answer and doc.elaborated.asked == [expected], name


def test_a_harness_loads_its_own_siblings_and_leaves_none_behind(monkeypatch):
    """Review F1 (kb-10b-switch): with another use case's module standing in `sys.modules` under each sibling
    name of every harness (as `tests/test_eligibility_wfp.py` leaves eligibility's `translation`), each harness
    still loads its own siblings; afterwards `sys.modules` and `sys.path` are exactly as before."""
    names = set().union(*(sibling_names(ROOT / "usecases" / name) for name in HARNESSES))
    assert {"translation", "run", "reference", "stage0"} <= names
    decoys = {name: types.ModuleType(name) for name in names}
    for name, decoy in decoys.items():
        monkeypatch.setitem(sys.modules, name, decoy)
    path_before = list(sys.path)
    for name in HARNESSES:
        directory = ROOT / "usecases" / name
        module = harness(name)
        for value in (module.T, module.V):
            assert Path(value.__file__).resolve().parent == directory.resolve(), (name, value)
        assert sys.path == path_before, name
        assert all(sys.modules[n] is decoys[n] for n in names), name
