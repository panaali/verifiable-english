"""The kb-10b shadow (`usecases/safetyfw_shadow.py`): it records Python's answers unchanged and compares them
with Lean's `soft-selected`, not with Python's own.

Fixture: kb-10a's three-rule document (tests/test_soft_selected.py), whose Lean answers are known. A planted
difference (a Python answer edited after the call) must be listed as a mismatch with both answers; agreeing
answers list none; the installed wrappers return Python's answer and record it with the harness's context.
"""
from __future__ import annotations

import importlib.util
import types
from pathlib import Path

import pytest

from tests.test_soft_selected import MODEL, QUERIES, document, lean  # noqa: F401  (the fixture)
from ve.model import FiniteModel
from ve.softnorms import SoftenedNormDocument, SoftNormDocument

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("kb10_shadow_under_test", ROOT / "usecases" / "safetyfw_shadow.py")
shadow_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(shadow_module)


def model_of(doc):
    return FiniteModel.from_dict(doc.elaborated.base_environment(), MODEL)


def harness(doc, model):
    """A stand-in run.py: a document builder, an item, a `completed` evaluated by Python."""
    module = types.SimpleNamespace(MUTANT=None)
    module.document = lambda default: doc
    module.completed = lambda d, predicate, values: {"a": False, "b": True, "c": True, "e": False}[values[0]]

    def answer(item):
        d = module.document("deny")
        return ([r.name for r in d.elaborated.selected_rules("x_required", model, (item,))],
                module.completed(d, "x_required", (item,)))
    module.answer = answer
    return module


SPEC = {"completed": lambda h, doc, predicate, values: (doc, MODEL, predicate, values),
        "contexts": {"answer": lambda h, item: f"item {item}"}}


def run(doc, items="abce"):
    shadow = shadow_module.Shadow()
    model = model_of(doc)
    module = harness(doc, model)
    with shadow_module.installed(shadow, module, SPEC):
        answers = {item: module.answer(item) for item in items}
    return shadow, answers


@pytest.fixture
def doc_under_shadow():
    """A three-rule document elaborated while the wrappers are installed (so it knows its soft source)."""
    shadow = shadow_module.Shadow()
    with shadow_module.installed(shadow, harness(None, None), {**SPEC, "contexts": {}}):
        doc = document("deny")
    return doc


def test_agreeing_answers_list_no_mismatch(lean, doc_under_shadow):  # noqa: F811
    shadow, answers = run(doc_under_shadow)
    assert answers == {"a": (["o"], False), "b": (["h"], True), "c": (["d"], True), "e": ([], False)}
    report = shadow.compare()
    assert report["calls_compared"] == {"completed": 4, "selected": 4}
    assert report["python_answers"] == {"completed false": 2, "completed true": 2,
                                        "selected empty": 1, "selected non-empty": 3}
    assert report["calls_by_family"] == {"item": 8}
    assert (report["lean_calls"], report["distinct_queries"]) == (1, 4)
    assert report["mismatches"] == [] and report["refusals"] == [] and report["background_false"] == []
    assert report["document_choices"] == {next(iter(shadow.documents)): ["'deny'"]}


def test_a_planted_difference_is_listed_with_python_and_lean_answers(lean, doc_under_shadow):  # noqa: F811
    shadow, _ = run(doc_under_shadow)
    planted = []
    for index, call in enumerate(shadow.calls):
        kind, *rest, python, context = call
        if rest[3] == ("b",):  # Python's answer at b, edited after the call: Lean's stays h / true
            python = ["d"] if kind == "selected" else False
            shadow.calls[index] = (kind, *rest, python, context)
            planted.append(kind)
    assert sorted(planted) == ["completed", "selected"]
    report = shadow.compare()
    assert report["mismatch_calls"] == 2
    assert [(m["kind"], m["case"], m["tuple"], m["python"], m["lean"], m["background"]) for m in report["mismatches"]] \
        == [("completed", "item b", ["b"], "false", "true", True), ("selected", "item b", ["b"], '["d"]', '["h"]', True)]


def test_a_model_outside_the_soft_premises_is_counted_with_background_false(lean, doc_under_shadow):  # noqa: F811
    shadow = shadow_module.Shadow()
    bad = {**MODEL, "relations": {**MODEL["relations"], "soft__excepted__d": [["e"]]}}
    shadow.record("selected", doc_under_shadow, bad, "x_required", ("a",), ["d"])
    report = shadow.compare()
    assert report["mismatches"] == [] and report["background_false_calls"] == 1
    assert report["background_false"][0]["tuple"] == ["a"]


def test_a_refused_query_is_listed_not_dropped(lean, doc_under_shadow):  # noqa: F811
    shadow = shadow_module.Shadow()
    shadow.record("selected", doc_under_shadow, MODEL, "x_required", ("a",), ["o"])
    shadow.record("selected", doc_under_shadow, MODEL, "no_such_predicate", ("a",), [])
    report = shadow.compare()
    assert report["calls_compared"] == {"selected": 2} and report["mismatches"] == []
    assert [(r["predicate"], r["calls"]) for r in report["refusals"]] == [("no_such_predicate", 1)]


def test_one_lean_call_per_document_and_model(lean, doc_under_shadow):  # noqa: F811
    shadow, _ = run(doc_under_shadow, items="abcebb")
    sent = []

    def ask(doc, model, queries):
        sent.append(queries)
        from ve.soft_route import selected_at
        return selected_at(doc, model, queries)
    report = shadow.compare(ask=ask)
    assert len(sent) == 1 and [q["tuple"] for q in sent[0]] == [["a"], ["b"], ["c"], ["e"]]
    assert report["calls_compared"] == {"completed": 6, "selected": 6} and report["mismatch_calls"] == 0


def test_the_wrappers_are_removed_and_a_document_without_its_soft_source_is_counted(lean):  # noqa: F811
    saved = SoftNormDocument._init_soft, SoftenedNormDocument.selected_rules
    doc = document("deny")  # built with no wrapper installed: no recorded soft source
    shadow, answers = run(doc, items="a")
    assert answers == {"a": (["o"], False)}
    assert (SoftNormDocument._init_soft, SoftenedNormDocument.selected_rules) == saved
    assert shadow.unsourced == {"item a": 1}
    assert [c[0] for c in shadow.calls] == ["completed"]


@pytest.mark.parametrize("name,item,expected", [
    ("openai-preparedness", {"id": "N2", "case": None, "item": ""}, "N2"),
    ("anthropic-rsp", {"id": "G1", "case": None, "item": ""}, "G1"),
])
def test_query_only_probe_mismatch_keeps_its_actual_choice_and_case(name, item, expected):
    """The review's N2 probe and RSP's sibling direct constructor have no document() call."""
    harness = shadow_module.load(name)
    shadow = shadow_module.Shadow()
    with shadow_module.installed(shadow, harness, shadow_module.HARNESSES[name]):
        harness.answer(item)
    assert shadow.calls
    shadow.calls = [(*call[:5], ["planted"], call[6]) for call in shadow.calls]

    def ask(_doc, _model, queries):
        return {"background": True, "results": [{**q, "selected": [], "outcome": False} for q in queries]}

    report = shadow.compare(ask=ask)
    assert report["mismatch_calls"] == len(shadow.calls)
    assert all(row["choice"] in report["document_choices"][row["document"]]
               and "RS" in row["choice"] and expected in row["case"] and row["model"] in shadow.models
               for row in report["mismatches"])
    if name == "openai-preparedness":
        assert len({row["choice"] for row in report["mismatches"]}) > 1


def test_reused_document_keeps_choice_case_and_model_in_every_report_row(doc_under_shadow):
    shadow = shadow_module.Shadow()
    module = types.SimpleNamespace(__file__=__file__)
    module.document = lambda choice: doc_under_shadow
    module.completed = lambda *_: False
    with shadow_module.installed(shadow, module, {"completed": lambda h, *a: a,
                                                "contexts": {}}):
        def exercise(choice, case, model, block=None, situation=None):
            doc = module.document(choice)
            shadow.record("selected", doc, model, "x_required", ("a",), ["planted"])
            shadow.record("selected", doc, model, "refused", ("a",), [])

        exercise({"RS1": "one"}, {"id": "case-1"}, MODEL)
        exercise({"RS1": "two"}, {"id": "case-1"}, MODEL)
        exercise({"RS1": "one"}, {"id": "case-2"}, {**MODEL, "complete": False},
                 types.SimpleNamespace(id="F11"), {"id": "witness-1"})

    def ask(_doc, _model, queries):
        if any(q["predicate"] == "refused" for q in queries):
            raise ValueError("refused")
        return {"background": False, "results": [{**q, "selected": [], "outcome": False} for q in queries]}

    report = shadow.compare(ask=ask)
    assert report["mismatch_calls"] == report["refused_calls"] == report["background_false_calls"] == 3
    for key in ("mismatches", "refusals", "background_false"):
        rows = report[key]
        assert len(rows) == 3
        assert len({(row["choice"], row["case"], row["model"]) for row in rows}) == 3
        assert all(row["choice"] in report["document_choices"][row["document"]] for row in rows)
        assert any("rule F11" in row["case"] and "witness-1" in row["case"] for row in rows)
