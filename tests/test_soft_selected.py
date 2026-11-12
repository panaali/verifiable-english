"""The soft route's `soft-selected` kind (kb-10a) and its relay `ve.soft_route.selected_at`.

One three-rule document over act X (`x_required`, one sort): a strict rule `h` (guard `v`), a default
rule `d` whose exception (sufficient condition `s`) holds at some tuples, and a default rule `o` of the
other sign (guard `w`) that `d` overrides. Lean answers, per query, the rules whose base-expanded
selection formula holds (`selectedAt`) and the completed outcome (`outcomeAt`), under the predicate's
default deny and allow; a model that violates the exception premise is answered with `background: false`
(SPEC 4.2); an unknown predicate, a mistyped tuple and an empty `queries` are refused. The relay keeps
only answers bound to the request (`bind_selected`); every bound field is fuzzed below and in
tests/test_relay_binding_inventory.py.
"""
from __future__ import annotations

import copy

import pytest

from tests import lean_routes
from tests.test_soft_norms_lean import SERVICE, env, norm, should
from ve import soft_route
from ve.errors import CheckerUnavailable, VEError
from ve.softnorms import SoftEnvironment, SoftNormDocument

EXTRA = {name: {"arguments": ["assistant"], "description": name} for name in ("v", "w", "s")}
EXCEPTION = {"decided_by": "assistant", "sufficient": [["unary", "s", ["var", 0]]], "necessary": [], "factors": []}
RULES = [norm("h", "x_required", True, guard=("unary", "v", ["var", 0])),
         should("d", "x_required", True, over=["o"], exception=EXCEPTION),
         should("o", "x_required", False, guard=("unary", "w", ["var", 0]))]
# a: d's exception holds (s, excepted) and o's guard: o selected, nothing overrides it.
# b: the strict rule's guard: h selected, both defaults blocked by it.
# c: o's guard, d not excepted: d selected and o overridden by it.
# e: d excepted, no guard: nothing selected, the predicate's default decides.
MODEL = {"complete": True, "domains": {"assistant": ["a", "b", "c", "e"], "user": []}, "constants": {},
         "relations": {"v": [["b"]], "w": [["a"], ["c"]], "s": [["a"], ["e"]],
                       "soft__excepted__d": [["a"], ["e"]], "soft__excepted__o": []}}
QUERIES = [{"predicate": "x_required", "tuple": [t]} for t in "abce"] + [{"predicate": "x_permitted", "tuple": ["a"]}]
EXPECTED = {  # tuple -> (selected, outcome under deny, outcome under allow)
    "a": (["o"], False, False), "b": (["h"], True, True), "c": (["d"], True, True), "e": ([], False, True)}


@pytest.fixture(scope="module")
def lean():
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def case(default="deny", *, model=MODEL, queries=QUERIES, case_id="selected"):
    return {"id": case_id, "kind": "soft-selected", "environment": env(req=default, extra=EXTRA),
            "norms": RULES, "model": model, "queries": queries}


def rows(cases):
    status, out, stderr = lean_routes.run("soft-norms", cases)
    assert status in (0, 1), stderr
    assert len(out) == len(cases)
    return out


def document(default="deny"):
    return SoftNormDocument(SoftEnvironment(env(req=default, extra=EXTRA)), RULES)


@pytest.mark.parametrize("default", ["deny", "allow"])
def test_selected_rules_and_outcomes_of_the_three_rule_document(lean, default):
    answer = soft_route.selected_at(document(default), MODEL, QUERIES)
    assert answer["background"] is True
    got = {r["tuple"][0]: (r["selected"], r["outcome"]) for r in answer["results"] if r["predicate"] == "x_required"}
    assert got == {t: (sel, deny if default == "deny" else allow) for t, (sel, deny, allow) in EXPECTED.items()}
    # x_permitted has no rule: nothing selected, its own default (allow) decides.
    assert answer["results"][-1] == {"predicate": "x_permitted", "tuple": ["a"], "selected": [], "outcome": True}
    assert [(r["predicate"], r["tuple"]) for r in answer["results"]] == [(q["predicate"], q["tuple"]) for q in QUERIES]


def test_the_raw_row_is_the_relay_answer(lean):
    [row] = rows([case()])
    assert row["status"] == "ok" and row["id"] == "selected"
    assert soft_route.bind_selected(row, case()) == {
        "background": row["background"], "results": row["results"]}


def test_a_model_violating_an_exception_premise_is_answered_with_background_false(lean):
    """s(a) holds but d's decision predicate is false at a: the soft background fails; Lean answers
    (now d selects at a and overrides o) and reports it, it does not refuse (SPEC 4.2)."""
    bad = copy.deepcopy(MODEL)
    bad["relations"]["soft__excepted__d"] = [["e"]]
    answer = soft_route.selected_at(document(), bad, QUERIES[:1])
    assert answer == {"background": False,
                      "results": [{"predicate": "x_required", "tuple": ["a"], "selected": ["d"], "outcome": True}]}


@pytest.mark.parametrize("queries, message", [
    ([{"predicate": "nope", "tuple": ["a"]}], "InvalidInput: query 0: nope is not a regulated predicate of the source"),
    ([QUERIES[0], {"predicate": "x_required", "tuple": ["zz"]}],
     "InvalidInput: query 1: tuple has the wrong length or sort for x_required"),
    ([{"predicate": "x_required", "tuple": ["a", "b"]}],
     "InvalidInput: query 0: tuple has the wrong length or sort for x_required"),
    ([{"predicate": "v", "tuple": ["a"]}], "InvalidInput: query 0: v is not a regulated predicate of the source"),
    ([], "InvalidInput: soft-selected needs at least one query"),
])
def test_refused_queries_name_their_diagnostic(lean, queries, message):
    [row] = rows([case(queries=queries)])
    assert row == {"id": "selected", "status": "error", "code": "SOFT_INVALID_INPUT", "error": message}
    with pytest.raises(VEError, match=message):
        soft_route.selected_at(document(), MODEL, queries)


def test_a_case_without_queries_is_refused(lean):
    raw = case()
    del raw["queries"]
    [row] = rows([raw])
    assert row["status"] == "error" and row["error"] == "InvalidInput: soft-selected needs a queries array"


# ---------------------------------------------------------------------------------------------------
# Binding: a forged answer is CheckerUnavailable at the relay (the relay mutation gate, R8).

GENUINE = {"id": "soft-selected", "status": "ok", "background": True, "results": [
    {"predicate": "x_required", "tuple": ["a"], "selected": ["o"], "outcome": False},
    {"predicate": "x_required", "tuple": ["c"], "selected": ["d"], "outcome": True},
    {"predicate": "x_permitted", "tuple": ["a"], "selected": [], "outcome": True}]}
SENT = [{"predicate": r["predicate"], "tuple": r["tuple"]} for r in GENUINE["results"]]


def forge(edit):
    row = copy.deepcopy(GENUINE)
    edit(row)
    return row


def _set(path, value):
    def edit(row):
        node = row
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
    return edit


FORGERIES = {
    "a tuple not sent": _set(("results", 0, "tuple"), ["b"]),
    "a tuple of another query": _set(("results", 0, "tuple"), ["c"]),
    "a longer tuple": _set(("results", 0, "tuple"), ["a", "a"]),
    "a predicate not sent": _set(("results", 2, "predicate"), "x_required"),
    "a retyped predicate": _set(("results", 0, "predicate"), ["x_required"]),
    "a retyped tuple item": _set(("results", 0, "tuple"), [1]),
    "a result dropped": lambda row: row["results"].pop(),
    "a result added": lambda row: row["results"].append(copy.deepcopy(row["results"][0])),
    "results reordered": lambda row: row["results"].reverse(),
    "no results": _set(("results",), []),
    "a name that is no rule": _set(("results", 0, "selected"), ["zz"]),
    "a rule of another predicate": _set(("results", 2, "selected"), ["o"]),
    "a rule twice": _set(("results", 0, "selected"), ["o", "o"]),
    "rules out of the document's order": _set(("results", 1, "selected"), ["o", "d"]),
    "a retyped selected list": _set(("results", 0, "selected"), "o"),
    "a retyped outcome": _set(("results", 0, "outcome"), 0),
    "a null outcome": _set(("results", 0, "outcome"), None),
    "a retyped background": _set(("background",), "true"),
    "a missing background": lambda row: row.pop("background"),
    "an extra result field": _set(("results", 0, "why"), "x"),
    "an extra row field": _set(("verdict",), "CHECKED"),
    "another id": _set(("id",), "other"),
}


@pytest.mark.parametrize("name", sorted(FORGERIES))
def test_a_forged_answer_is_unavailable(monkeypatch, name):
    monkeypatch.setattr(soft_route, "_run", lambda request: forge(FORGERIES[name]))
    doc = type("Doc", (), {"rules": [type("R", (), {"to_dict": lambda self, n=n: n})() for n in RULES],
                           "env": SoftEnvironment(env(extra=EXTRA))})()
    with pytest.raises(CheckerUnavailable, match="not bound to the request"):
        soft_route.selected_at(doc, MODEL, SENT)


def test_the_genuine_answer_is_bound(monkeypatch):
    sent = []
    monkeypatch.setattr(soft_route, "_run", lambda request: sent.append(request) or copy.deepcopy(GENUINE))
    doc = type("Doc", (), {"rules": [type("R", (), {"to_dict": lambda self, n=n: n})() for n in RULES],
                           "env": SoftEnvironment(env(extra=EXTRA))})()
    answer = soft_route.selected_at(doc, MODEL, [(q["predicate"], q["tuple"]) for q in SENT])
    assert answer == {"background": True, "results": GENUINE["results"]}
    assert sent[0]["queries"] == SENT and sent[0]["kind"] == "soft-selected" and sent[0]["model"] == MODEL
