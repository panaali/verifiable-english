"""Lean's `readings-verdicts` answer over a document's components, as untrusted output (docs/spec/readings-defaults.md
4.5; plan RD-4b; build checklist 4).

The product answer (`Readings.Run.runProduct`) is typed by its generated, proved schema (`verdicts_components`) and
bound to its request by `Components.check_product`: its cases are exactly the split's, each case's own answer is bound
as RD-3 binds an answer (rows exactly the case's compatible choices, every piece the request's), and every
component, choice, unit and line it names exists in the request. The fuzz below takes genuine answers of every form
and retypes, drops, empties, duplicates and rebinds each field; each mutant must be refused. What the product
concludes from its rows (the verdict, the decided units, which lines are said) is Lean's, by theorem
(`readings_wire_product_*`), and is listed in `LEAN_OWNED` with the theorem or encoder that owns it.
"""
from __future__ import annotations

import copy
import json

import pytest

from tests import lean_routes
from tests.test_readings_companions_lean import MAIN_UNIT, env_b, lower, set_a, with_companion
from tests.test_readings_s1_lean import entry, norm, reading, reading_set, situation_id
from ve.errors import CheckerUnavailable

ND_ROUTE = "ve_readings_route"


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def absurd_b():
    """F-C15's second companion set: reading 0 F-C1's `every`, reading 1 asserting ⊥ (no situation holds it)."""
    from ve.ast import formula_from_data
    from ve.environment import Environment
    from ve.identity import meaning_id
    raw = env_b()
    companion = lower(raw)
    sigma = entry({"domains": {"agent": ["a"], "user": ["u"]}, "constants": {},
                   "relations": {"calls": [], "unsaid__warn_permitted": [["a", "u"]], "unsaid__warn_required": []}},
                  "every", "holds", True)
    sid = situation_id(raw, sigma)
    every = with_companion(reading("every", norm("must-warn", "warn_required", True), {"absurd": sid}), companion)
    absurd = reading("absurd", ["bottom"], {"every": sid}, kind="asserted")
    absurd["companion"] = {"environment": companion, "open_terms": []}
    env = Environment(companion)
    absurd["meaning_id"] = meaning_id(env, formula_from_data(env, ["bottom"]))
    return reading_set("rs_b", "u_b", [every, absurd], {sid: sigma})


# ---------------------------------------------------------------------------------------------------------------
# Genuine answers of every form, with the request each answers

@pytest.fixture(scope="module")
def genuine(tmp_path_factory):
    """(name, route, row, case) for the conflict, premises and query forms, the query's ALL, NONE, UNKNOWN by
    another component's conflict status and UNKNOWN by another component's consistency."""
    from tests.test_readings_components_document import HELP_PERMITTED, NO_AGENT, fc1, fc17, write, env_main
    from ve.document import load_document
    from ve.readings_components import context
    out = []
    tmp = tmp_path_factory.mktemp("rd4b")
    route = context(load_document(fc1(tmp)))
    for question in ("conflict", "premises"):
        row = route.conflict_answer() if question == "conflict" else route.premises_answer()
        out.append((question, route, row, route.requests[id(row)]))
    row = route.query_answer(HELP_PERMITTED)
    out.append(("ALL", route, row, route.requests[id(row)]))
    row = route.query_answer(NO_AGENT, sentence="u_a")
    out.append(("NONE", route, row, route.requests[id(row)]))
    route17 = context(load_document(fc17(tmp)))
    row = route17.query_answer(HELP_PERMITTED, sentence="u_a")
    out.append(("UNKNOWN conflict status", route17, row, route17.requests[id(row)]))
    a, _, _ = set_a()
    document = {"units": [MAIN_UNIT, {"id": "u_a"}, {"id": "u_b"}], "reading_sets": [a, absurd_b()]}
    route15 = context(load_document(write(tmp, env_main(), document, name="absurd")))
    row = route15.query_answer(NO_AGENT, sentence="u_a")
    out.append(("UNKNOWN not consistent", route15, row, route15.requests[id(row)]))
    return out


def test_the_genuine_answers_cover_every_result_form(genuine):
    forms = {(row["question"], row["result"].get("verdict"), tuple(sorted(row["result"]))) for _, _, row, _ in genuine}
    assert {q for q, _, _ in forms} == {"conflict", "premises", "query"}
    verdicts = {name: row["result"].get("verdict") for name, _, row, _ in genuine}
    assert verdicts["ALL"] == "ALL" and verdicts["NONE"] == "NONE"
    assert "choice_component" in dict(genuine_by(genuine, "UNKNOWN conflict status")["result"])
    assert genuine_by(genuine, "UNKNOWN not consistent")["result"]["reason"] == (
        "another sentence's readings are not all consistent")
    for _, route, row, case in genuine:
        route.check_product(row, case)


def genuine_by(genuine, name):
    return next(row for n, _, row, _ in genuine if n == name)


# ---------------------------------------------------------------------------------------------------------------
# The fuzz: every field retyped, dropped, emptied, duplicated, rebound

def _paths(value, path=()):
    yield path, value
    if type(value) is dict:
        for key, item in value.items():
            yield from _paths(item, path + (key,))
    elif type(value) is list:
        for i, item in enumerate(value):
            yield from _paths(item, path + (i,))


def _set(root, path, new):
    root = copy.deepcopy(root)
    holder = root
    for key in path[:-1]:
        holder = holder[key]
    if new is _DROP:
        if type(holder) is dict:
            del holder[path[-1]]
        else:
            del holder[path[-1]]
    else:
        holder[path[-1]] = new
    return root


_DROP = object()
OTHER_TYPES = (7, True, None, "x", [], {})


def _type(value):
    return {bool: "bool", int: "int", float: "int", str: "str", list: "list", dict: "dict", type(None): "null"}[
        type(value)]


def _refused(route, row, case):
    try:
        route.check_product(row, case)
    except CheckerUnavailable:
        return True
    return False


def _mutants(row):
    for path, value in _paths(row):
        if not path:
            continue
        for other in OTHER_TYPES:
            if _type(other) != _type(value):
                yield "retype", path, other
        if type(path[-1]) is str:
            yield "drop", path, _DROP
        if type(value) is list and value:
            yield "empty", path, []
            yield "duplicate", path, value + [copy.deepcopy(value[0])]
            yield "drop first", path, value[1:]


def test_every_retyped_or_dropped_field_is_refused(genuine):
    survived = []
    for name, route, row, case in genuine:
        for how, path, new in _mutants(row):
            if how in ("empty", "duplicate", "drop first"):
                continue
            # The presence and contents of a gap map are Lean's computed cone, rather than an echoed request row.
            if how == "drop" and "gaps" in path and len(path) > path.index("gaps") + 1:
                continue
            mutant = _set(row, path, new)
            if mutant != row and not _refused(route, mutant, case):
                survived.append((name, how, path, new))
    assert survived == [], survived


# Lists whose length Lean owns: which lines the plan says (`productPlan`, `verdictsPlan_cites`) and what a row's
# notes and gaps hold beside the pieces (a duplicated note is the same note). Every other list restates rows,
# components, units or the request, and an empty, extra or missing entry is refused.
LEAN_OWNED = {
    "english": "Readings.Run.productPlan / verdictsPlan (plan_cites_conditions, plan_conditions_only)",
    "gaps": "Readings.Run.perChoiceJson (the filled gaps a shown model's result depends on, Lean's coneOf)",
    "decided_units": "Readings.Run.productDecided (1.10's rule on the case's own rows); a missing unit is Lean's",
    "labels": "Readings.Run.labelsOf (verdicts_conditions_*)",
    "conditional_on": "Readings.Run.conditionsOf (mem_conditionsOf)",
    "restrictions": "Readings.restrictionsFor (restrictionsFor_spec)",
    "reading_premises_used": "Readings.restrictionsFor (restrictionsFor_spec)",
    "finding_sets": "bound to the case's finding: an empty list is refused, an extra one too",
    "readings": "a plan line's readings (Readings.PlanItem.line)",
    "unchecked": "the sets the main case leaves on W2 (Readings.Run.admitPart): each one written is bound",
    "witnesses": "bound to the rows in conflict",
    "dead": "bound to the dead certificates sent",
    "untaken": "Readings.Run.untakenOf: bound to candidates no row takes",
    "candidates": "bound to the document's candidates",
    "units": "bound to the case's units",
}


def test_every_emptied_or_duplicated_row_list_is_refused(genuine):
    survived = []
    for name, route, row, case in genuine:
        for how, path, new in _mutants(row):
            if how not in ("empty", "duplicate", "drop first"):
                continue
            key = next((p for p in reversed(path) if type(p) is str), None)
            if ("gaps" in path or key in LEAN_OWNED) and key not in ("components", "per_choice", "choices", "units"):
                continue
            mutant = _set(row, path, new)
            if mutant != row and not _refused(route, mutant, case):
                survived.append((name, how, path))
    assert survived == [], survived


def _rebinds(row):
    """Every identity the answer names, replaced by one the request does not have."""
    yield ("component",), "zz"
    for i, entry in enumerate(row["components"]):
        yield ("components", i, "component"), "zz"
        for j, _ in enumerate(entry["units"]):
            yield ("components", i, "units", j), "u9"
        for j, choice_row in enumerate(entry["answer"]["per_choice"]):
            for k, _ in enumerate(choice_row["choice"]):
                yield ("components", i, "answer", "per_choice", j, "choice", k, 0), "zz"
                yield ("components", i, "answer", "per_choice", j, "choice", k, 1), 99
        yield ("components", i, "answer", "id"), "zz"
        yield ("components", i, "answer", "question"), "query" if entry["answer"]["question"] != "query" else "premises"
    for j, _ in enumerate(row["decided_units"]):
        yield ("decided_units", j), "u9"
    for j, line in enumerate(row["english"]):
        if line["component"] is not None:
            yield ("english", j, "component"), "zz"
        for k, _ in enumerate(line["line"]["readings"]):
            yield ("english", j, "line", "readings", k, 0), "zz"
    result = row["result"]
    if "components" in result:
        for j, _ in enumerate(result["components"]):
            yield ("result", "components", j, "component"), "zz"
    for name in ("component", "choice_component"):
        if name in result:
            yield ("result", name), "zz"
    if "choice" in result:
        for k, _ in enumerate(result["choice"]):
            yield ("result", "choice", k, 1), 99
    yield ("id",), "zz"
    yield ("question",), "premises" if row["question"] != "premises" else "conflict"


def test_every_rebound_identity_is_refused(genuine):
    survived = []
    for name, route, row, case in genuine:
        for path, new in _rebinds(row):
            if name != "ALL" and path == ("component",) and row["component"] is None:
                continue
            mutant = _set(row, path, new)
            if mutant != row and not _refused(route, mutant, case):
                survived.append((name, path, new))
    assert survived == [], survived


def test_a_component_s_status_that_is_not_its_own_is_refused(genuine):
    """A result restating each component's own fold restates it (no other word)."""
    for name, route, row, case in genuine:
        if "components" not in row["result"]:
            continue
        for j, item in enumerate(row["result"]["components"]):
            for word in ("CONFLICT-FREE", "CONFLICT", "UNKNOWN", "model", "INCONSISTENT"):
                if word != item["status"]:
                    assert _refused(route, _set(row, ("result", "components", j, "status"), word), case), (name, j)


def test_the_sentence_is_the_request_s(genuine):
    name, route, row, case = next(g for g in genuine if g[0] == "NONE")
    assert row["sentence"] == "u_a"
    assert _refused(route, _set(row, ("sentence",), "u_b"), case)
    assert _refused(route, _set(row, ("sentence",), None), case)
