"""`readings-verdicts` through the service (docs/spec/readings-defaults.md 3, 4.4, 2.4 and 8.2; plan RD-3).

Lean folds every verdict of the enumerated route: the conflict status, the premise statuses with the dead readings,
and ALL, SOME or NONE, from evidence it checks on each choice's regenerated document, with the gate of 14.8, the
restrictions computed locally, the labels an answer uses, and the English plan. The fixtures are spec 8.2's service
table; the evidence is genuine (Python's generators on the loaded document) or mutated from it, and each verdict is
read from Lean's answer.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tests import lean_routes
from tests.test_readings_nd_document import ASKS as ASKS_SENTENCE, EVERY as EVERY_SENTENCE, QUERY, fnd1, fnd2
from tests.test_readings_nd_lean import case, doc1, env1, run
from ve.document import load_document
from ve.errors import CheckerUnavailable, VEError
from ve.readings_s2_wording import query_english, report_english
from ve.readings_verdicts import context

LEAN = "ve_readings_route"
ROOT = Path(__file__).resolve().parents[1]
IMPLIES = ["forall", "agent", ["forall", "user", ["implies", ["binary", "help_required", ["var", 1], ["var", 0]],
                                                  ["binary", "help_permitted", ["var", 1], ["var", 0]]]]]
PAIR = "unsaid:pair:help_required,help_permitted"
C0, C1 = [["rs_1", 0]], [["rs_1", 1]]


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def loaded(tmp_path, make=fnd1):
    doc = load_document(make(tmp_path))
    return doc, context(doc)


def ask(route, question, evidence, **fields):
    """Lean's raw answer to a `readings-verdicts` case on the route's document with `evidence` as given."""
    [row] = run(LEAN, [case("readings-verdicts", route.environment, route.document, question=question,
                            evidence=evidence, **fields)])
    return row


def genuine(route):
    """Each choice's conflict packages from Python's generators: {choice key: {"conflict": inner case}}."""
    return {route._key(c): {"conflict": route._choice(c).conflict_case()} for c in route.choices}


def evidence_of(route, pieces):
    return [{"choice": route.choice_json(c), **pieces[route._key(c)]} for c in route.choices if route._key(c) in pieces]


def frames(answer):
    return [(line["frame"], line["result"]) for line in answer["english"]]


# ---------------------------------------------------------------------------------------------------------------
# F-ND1 (spec 8.2's service table)

def test_fnd1_conflict_free_under_every_reading_conditional_on_the_pair_premise(tmp_path):
    doc, route = loaded(tmp_path)
    answer = ask(route, "conflict", evidence_of(route, genuine(route)))
    assert answer["status"] == "ok", answer
    result = answer["result"]
    assert result["status"] == "CONFLICT-FREE" and result["conditional_on"] == [PAIR]
    assert [e["conflict"] for e in answer["per_choice"]] == ["CONFLICT-FREE", "CONFLICT-FREE"]
    # E29 (the route), E26 with R1, E3 with the pair sentence, E13 (no restriction names the set)
    assert frames(answer) == [("E29", None), ("E26", "R1"), ("E3", None), ("P1", None), ("E13", None)]
    assert answer["english"][3]["label"] == PAIR
    lines = report_english(doc, route)
    assert lines[1:4] == ["Under every reading of the open sentence, no two rules on the same act contradict each other.",
                          "This holds provided that:", "Whenever an agent must help an user, it may help that user."]


def test_fnd1_query_some_each_reading_named_by_its_own_sentence(tmp_path):
    doc, route = loaded(tmp_path)
    data = route.entailment(QUERY)
    assert data["verdict"] == "SOME" and data["proof"]["choice"] == C0 and data["countermodel"]["choice"] == C1
    answer = route.query_answer(QUERY)
    # rd-3 round 3: the proof under the first reading rests on the pair condition (its conflict packages use it), so
    # the plan states it after that result (verdicts_conditions_some), before the countermodel of the second.
    assert data["proof"]["conditional_on"] == [PAIR] and answer["labels"] == [PAIR]
    assert frames(answer) == [("E12", "R2"), ("E3", None), ("P1", None), ("E12", "R3")]
    [shown] = [line for line in answer["english"] if line["model"] is not None]
    # one filled gap the result depends on: the duty's own gap under reading `asks`, answered 'no' (spec 2.2)
    assert shown["gaps"] == [["help_required", ["e0", "e0"], False]] and shown["readings"] == [["rs_1", 1]]
    lines = query_english(doc, QUERY, data)
    assert lines[0].startswith(f"Read sentence 1 as {EVERY_SENTENCE}: the conclusion follows")
    assert lines[1:3] == ["This holds provided that:", "Whenever an agent must help an user, it may help that user."]
    assert lines[3].startswith(f"Read sentence 1 as {ASKS_SENTENCE}: the conclusion does not follow")
    assert lines[3].endswith("Here the text does not say whether e0 must help e0; this situation answers 'no'.")
    assert not any("reading 2" in line or "reading 1" in line for line in lines)


def test_fnd1_query_under_the_first_reading_is_all_naming_it_only(tmp_path):
    doc, route = loaded(tmp_path)
    data = route.entailment(QUERY, assumed=[("rs_1", 0)])
    assert data["verdict"] == "ALL" and data["assumed"] == C0 and data["conditional_on"] == [PAIR]
    answer = route.query_answer(QUERY, C0)
    assert frames(answer)[0] == ("E12", "R2") and answer["english"][0]["readings"] == [["rs_1", 0]]
    assert query_english(doc, QUERY, data)[0].startswith(f"Read sentence 1 as {EVERY_SENTENCE}: the conclusion follows")


def test_fnd1_implication_is_all_conditional_on_the_pair_premise(tmp_path):
    """The entailment certificate alone does not need the pair label (W1's Background has the pair premise), but the
    conflict certificates the answer also rests on do (composition-s2 2.3 as built)."""
    doc, route = loaded(tmp_path)
    data = route.entailment(IMPLIES)
    assert data["verdict"] == "ALL" and data["conditional_on"] == [PAIR]
    assert all(p["conditional_on"] == [PAIR] for p in data["proofs"])
    assert frames(route.query_answer(IMPLIES))[:3] == [("E26", "R2"), ("E3", None), ("P1", None)]


def test_missing_evidence_for_one_of_two_choices_names_that_choice(tmp_path):
    _, route = loaded(tmp_path)
    pieces = genuine(route)
    only = {route._key(route.choices[0]): pieces[route._key(route.choices[0])]}
    conflict = ask(route, "conflict", evidence_of(route, only))
    assert conflict["result"]["status"] == "UNKNOWN"
    assert conflict["result"]["status_text"] == "UNKNOWN: a reading's conflict status is not certified"
    assert [e["conflict"] for e in conflict["per_choice"]] == ["CONFLICT-FREE", "UNKNOWN"]
    query = ask(route, "query", evidence_of(route, only), premises=[], conclusion=QUERY)
    assert {k: query["result"][k] for k in ("verdict", "status", "conflict_status", "choice")} == {
        "verdict": "UNKNOWN", "status": "UNKNOWN (conflict status: UNKNOWN)", "conflict_status": "UNKNOWN", "choice": C1}
    # a query row without a result: UNKNOWN naming the first choice without one
    cert = route._choice(route.choices[0]).certificate_case(QUERY)
    pieces[route._key(route.choices[0])]["certificate"] = cert
    query = ask(route, "query", evidence_of(route, pieces), premises=[], conclusion=QUERY)
    assert (query["result"]["verdict"], query["result"]["choice"]) == ("UNKNOWN", C1)


def test_a_certificate_of_choice_0_supplied_as_choice_1s_is_never_all(tmp_path):
    _, route = loaded(tmp_path)
    pieces = genuine(route)
    cert = route._choice(route.choices[0]).certificate_case(QUERY)
    for key in pieces:
        pieces[key]["certificate"] = cert
    request = case("readings-verdicts", route.environment, route.document, question="query",
                   evidence=evidence_of(route, pieces), premises=[], conclusion=QUERY)
    [answer] = run(LEAN, [request])
    assert answer["result"]["verdict"] != "ALL"
    entry = answer["per_choice"][1]
    assert entry["query"] == "UNKNOWN" and (entry["errors"].get("certificate") or entry["evidence"]["certificate"] is False)
    with pytest.raises(CheckerUnavailable, match="ReadingsConformance"):
        route.check_answer(answer, request)


def test_untaken_readings_are_refused_before_any_condition(tmp_path):
    """SR3: F-ND1 with the narrowing `n1` keeping reading 0, the query under `rs_1:1`: `ReadingsUnsatisfiable`, before
    `restrictionsFor` runs (whose local answer there, `[]`, would differ from the meaning, `[narrowing:n1]`)."""
    raw = env1()
    document, _ = doc1(raw)
    document["narrowings"] = [{"id": "n1", "set": "rs_1", "version": 1, "keeps": ["every"], "by": "reviewer",
                               "reason_spans": ["u1"]}]
    [row] = run(LEAN, [case("readings-verdicts", raw, document, question="query", evidence=[], premises=[],
                            conclusion=QUERY, assumed=C1)])
    assert row["status"] == "error" and row["error"] == "ReadingsUnsatisfiable: no compatible reading takes rs_1@1:1"
    [row] = run(LEAN, [case("readings-verdicts", raw, document, question="conflict", evidence=[])])
    assert row["restrictions"] == ["narrowing:n1"] and [e["choice"] for e in row["per_choice"]] == [C0]


def test_through_ve_document_the_untaken_reading_is_the_same_text(tmp_path):
    _, route = loaded(tmp_path)
    with pytest.raises(VEError) as caught:
        route.entailment(QUERY, assumed=[("rs_9", 0)])
    assert caught.value.message == "ReadingsUnsatisfiable: no compatible reading takes rs_9:0"


# ---------------------------------------------------------------------------------------------------------------
# F-ND2: CONFLICT under the first reading (latent), the witness choice named

def test_fnd2_conflict_under_reading_0_witness_named(tmp_path):
    doc, route = loaded(tmp_path, fnd2)
    result = route.conflict()
    assert result["status"] == "CONFLICT" and result["status_text"] == "CONFLICT under rs_2@1:0"
    assert [w["choice"] for w in result["witnesses"]] == [[["rs_2", 0]]]
    answer = route.conflict_answer()
    [shown] = [line for line in answer["english"] if line["model"] is not None]
    assert (shown["frame"], shown["result"], shown["readings"]) == ("E12", "R4", [["rs_2", 0]])
    assert shown["model"] == "witness@0" and answer["per_choice"][0]["evidence"] == {"conflict": False,
                                                                                       "witness": True}


# ---------------------------------------------------------------------------------------------------------------
# F-ND3: beyond 64 compatible choices only a checked countermodel says anything

def fnd3():
    raw = env1()
    sets, units = [], []
    for k in range(7):
        document, _ = doc1(raw, set_id=f"rs_{k + 1}", unit=f"u{k + 1}", rule=f"must-help-{k + 1}")
        sets += document["reading_sets"]
        units += document["units"]
    return raw, {"units": units, "reading_sets": sets}


def test_fnd3_beyond_64_choices_budget_or_not_all():
    raw, document = fnd3()
    [row] = run(LEAN, [case("readings-verdicts", raw, document, question="query", evidence=[], premises=[],
                            conclusion=QUERY)])
    assert row["result"] == {"verdict": "UNKNOWN", "status": "UNKNOWN", "route": "enumerated",
                             "budget": {"max_choices": 64}, "units": [f"u{k}" for k in range(1, 8)]}
    assert row["english"] == []
    # a countermodel under the reading `asks` of every sentence: nobody asks, the duty's gap filled 'no'
    model = {"complete": True, "domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}}
    choice = [[f"rs_{k}", 1] for k in range(1, 8)]
    evidence = [{"choice": choice, "countermodel": {"kind": "choice-model", "model": model, "filling": {}}}]
    [row] = run(LEAN, [case("readings-verdicts", raw, document, question="query", evidence=evidence, premises=[],
                            conclusion=QUERY)])
    assert row["result"]["status"] == ("UNKNOWN (not ALL: countermodel under "
                                       + ", ".join(f"rs_{k}@1:1" for k in range(1, 8)) + ")")
    assert row["result"]["countermodel"]["choice"] == choice
    assert [(line["frame"], line["result"]) for line in row["english"]] == [("E28", None), ("E12", "R3")]
    # the same model under reading `every` is no countermodel: nothing is claimed
    evidence[0]["choice"] = [[f"rs_{k}", 0] for k in range(1, 8)]
    [row] = run(LEAN, [case("readings-verdicts", raw, document, question="query", evidence=evidence, premises=[],
                            conclusion=QUERY)])
    assert "countermodel" not in row["result"] and row["result"]["status"] == "UNKNOWN"


# ---------------------------------------------------------------------------------------------------------------
# 3.13 through the service: thirty narrowed sets, their thirty labels computed without the 2^30 complete choices

def test_thirty_narrowed_sets_restrictions_without_the_product():
    raw = env1()
    sets, units, narrowings = [], [], []
    for k in range(1, 31):
        document, _ = doc1(raw, set_id=f"rs_{k}", unit=f"u{k}", rule=f"must-help-{k}")
        sets += document["reading_sets"]
        units += document["units"]
        narrowings.append({"id": f"n{k}", "set": f"rs_{k}", "version": 1, "keeps": ["every"], "by": "reviewer",
                           "reason_spans": [f"u{k}"]})
    [row] = run(LEAN, [case("readings-verdicts", raw, {"units": units, "reading_sets": sets,
                                                       "narrowings": narrowings}, question="conflict", evidence=[])])
    assert row["status"] == "ok", row
    assert row["restrictions"] == [f"narrowing:n{k}" for k in range(1, 31)]
    assert [e["choice"] for e in row["per_choice"]] == [[[f"rs_{k}", 0] for k in range(1, 31)]]
    # its latency is measured by docs/readings-defaults/rd3/latency.py and recorded in the DELTA (no test asserts
    # on time: tests/test_hang_guards.py)


# ---------------------------------------------------------------------------------------------------------------
# Lean's answer is untrusted output, checked for its schema and its binding to the request only (DRI ruling of rd-3
# round 3; build checklist 4; review B1 and B2 of rd-3): every field dropped or retyped is unavailable, and every row,
# choice, reading, model, label and dead reading it names is the request's. What the answer concludes from its rows
# (the verdict, its conditions, which lines the plan says) is Lean's, by theorem; the client never re-derives it.

def _checked(route, answer):
    """The request `answer` answers, after checking the genuine answer against it."""
    request = route.requests[id(answer)]
    route.check_answer(answer, request)
    return request


def _genuine_answers(tmp_path):
    """Genuine answers of every result form the fixtures reach: {name: (route, answer)}."""
    for sub in ("fnd1", "fnd2"):
        (tmp_path / sub).mkdir()
    _, route = loaded(tmp_path / "fnd1")
    _, route2 = loaded(tmp_path / "fnd2", fnd2)
    route.entailment(IMPLIES)
    route.entailment(QUERY, assumed=[("rs_1", 1)])
    route.premises()
    route2.conflict()
    return {"conflict CONFLICT-FREE": (route, route.conflict_answer()),
            "conflict CONFLICT": (route2, route2.conflict_answer()),
            "premises": (route, route.premises_answer()),
            "query SOME": (route, route.query_answer(QUERY)),
            "query ALL": (route, route.query_answer(IMPLIES)),
            "query NONE under a reading": (route, route.query_answer(QUERY, [("rs_1", 1)]))}


def _paths(value, path=()):
    """Every member path of a JSON value, each with its value."""
    yield path, value
    if type(value) is dict:
        for key, item in value.items():
            yield from _paths(item, (*path, key))
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from _paths(item, (*path, index))


def _at(value, path):
    for step in path:
        value = value[step]
    return value


RETYPED = (7, True, None, [], {}, "", "UNKNOWN")


def _result_mutants(answer):
    """1-fault mutations of the result: each member dropped, and each value outside a shown model replaced by one
    of another type or another value of its type."""
    for path, value in _paths(answer["result"]):
        if "model" in path or not path:
            continue
        parent, last = path[:-1], path[-1]
        if type(last) is str:
            yield f"drop {path}", lambda a, p=parent, k=last: _at(a["result"], p).pop(k)
        for other in RETYPED:
            if type(other) is not type(value) or other != value:
                yield f"{path} = {other!r}", lambda a, p=parent, k=last, v=other: _at(a["result"], p).__setitem__(k, v)


# The result mutants the client relays: each changes only what Lean concludes from rows the request binds, which
# the DRI ruling of rd-3 round 3 leaves to Lean, by the named theorem or encoder. Pinned, so a new relayed mutant
# fails until it is owned here.
LEAN_OWNED_RESULTS = {
    # verdicts_conditions_conflict_free: conditional_on is conditionsOf of the rows, nothing dropped (round 3 B)
    "conflict CONFLICT-FREE: ('conditional_on',) = []": "Readings.Run.verdicts_conditions_conflict_free",
    # verdicts_conditions_all: likewise for an ALL
    "query ALL: ('conditional_on',) = []": "Readings.Run.verdicts_conditions_all",
    # per choice: a proof's conditional_on is its row's own labels (proofJson; verdicts_conditions_all, _some)
    "query ALL: ('proofs', 0, 'conditional_on') = []": "Readings.Run.verdicts_conditions_all",
    "query ALL: ('proofs', 1, 'conditional_on') = []": "Readings.Run.verdicts_conditions_all",
    "query SOME: ('proof', 'conditional_on') = []": "Readings.Run.verdicts_conditions_some",
    # the fold of the rows (readings_wire_verdicts_conflict, lower_verdicts_*)
    "conflict CONFLICT: ('status',) = 'UNKNOWN'": "Readings.Run.readings_wire_verdicts_conflict",
    # a candidate's status, the fold of the rows taking it (premisesResult)
    "premises: ('candidates', 0, 'status') = 'UNKNOWN'": "Readings.Run.premisesResult",
    "premises: ('candidates', 1, 'status') = 'UNKNOWN'": "Readings.Run.premisesResult",
}


def test_the_result_of_every_form_is_typed_and_bound(tmp_path):
    """Review B1 and the DRI ruling: each result member dropped or retyped, at every depth, is unavailable, and so is
    every value the request or the rows bind (a shown model is bound to the request's piece instead, below); the
    mutants that change only what Lean concludes are exactly `LEAN_OWNED_RESULTS`, each owned by a Lean theorem or
    encoder."""
    relayed = set()
    for name, (route, answer) in _genuine_answers(tmp_path).items():
        request = _checked(route, answer)
        for label, mutate in _result_mutants(answer):
            mutated = copy.deepcopy(answer)
            mutate(mutated)
            if json.dumps(mutated) == json.dumps(answer):
                continue
            try:
                route.check_answer(mutated, request)
            except CheckerUnavailable:
                continue
            relayed.add(f"{name}: {label}")
    assert relayed == set(LEAN_OWNED_RESULTS), "\n".join(sorted(relayed ^ set(LEAN_OWNED_RESULTS)))
    statements = (ROOT / "lean/statements.txt").read_text()
    for owner in set(LEAN_OWNED_RESULTS.values()):
        assert f"theorem VE.{owner}\n" in statements or owner == "Readings.Run.premisesResult", owner


def test_review_b1_findings_cases(tmp_path):
    """The finding's cases: a retyped verdict, and a conflict result of the route alone (which crashed the report)."""
    answers = _genuine_answers(tmp_path)
    route, answer = answers["query SOME"]
    request = _checked(route, answer)
    mutated = copy.deepcopy(answer)
    mutated["result"]["verdict"] = True
    with pytest.raises(CheckerUnavailable):
        route.check_answer(mutated, request)
    route, answer = answers["conflict CONFLICT-FREE"]
    request = _checked(route, answer)
    mutated = copy.deepcopy(answer)
    mutated["result"] = {"route": "enumerated"}
    with pytest.raises(CheckerUnavailable):
        route.check_answer(mutated, request)
    # another question's form of result
    mutated = copy.deepcopy(answer)
    mutated["result"] = copy.deepcopy(answers["premises"][1]["result"])
    with pytest.raises(CheckerUnavailable):
        route.check_answer(mutated, request)


MUTATIONS = {
    "drop route": lambda a: a.pop("route"),
    "another question": lambda a: a.update(question="conflict"),
    "another id": lambda a: a.update(id="readings-verdicts-2"),
    "result a list": lambda a: a.update(result=[]),
    "per_choice dropped": lambda a: a.pop("per_choice"),
    "a row named twice": lambda a: a["per_choice"].append(copy.deepcopy(a["per_choice"][0])),
    "a row's conflict retyped": lambda a: a["per_choice"][0].update(conflict=True),
    "an acceptance as 1": lambda a: a["per_choice"][0]["evidence"].update(conflict=1),
    "an error not a string": lambda a: a["per_choice"][0]["errors"].update(conflict=7),
    "english a string": lambda a: a.update(english="E12"),
    "a line without its frame": lambda a: a["english"][0].pop("frame"),
    "a line's model retyped": lambda a: a["english"][-1].update(model=True),
    "restrictions null": lambda a: a.update(restrictions=None),
    "labels with a bool": lambda a: a.update(labels=[True]),
    "dead_readings an object": lambda a: a.update(dead_readings={}),
    # review B2 of rd-3: rows and the choices the result names are the request's
    "no rows": lambda a: a.update(per_choice=[]),
    "a row dropped": lambda a: a["per_choice"].pop(),
    "rows reordered": lambda a: a["per_choice"].reverse(),
    "a row for a choice that does not exist": lambda a: a["per_choice"][0].update(choice=[["rs_1", 9]]),
    "the proof names a choice no row has": lambda a: a["result"]["proof"].update(choice=[["rs_1", 9]]),
    "a row's word naming a piece it does not note": lambda a: a["per_choice"][1].update(query="proved"),
    "the budget shape on 2 choices": lambda a: a.update(result={
        "verdict": "UNKNOWN", "status": "UNKNOWN", "route": "enumerated", "budget": {"max_choices": 64},
        "units": ["u1"]}),
    "a result assuming readings the request did not": lambda a: a["result"].update(assumed=C0),
    "a row's question word dropped": lambda a: a["per_choice"][0].pop("query"),
    "a row with another question's word": lambda a: a["per_choice"][0].update(premises="model"),
    "a refused piece": lambda a: a["per_choice"][0]["errors"].update(certificate="InvalidInput: refused"),
    "a sent piece left unanswered": lambda a: a["per_choice"][0]["evidence"].pop("certificate"),
    "an answer for a piece not sent": lambda a: a["per_choice"][0]["evidence"].update(unsat=True),
    "a shown model not the request's": lambda a: a["per_choice"][1]["shown"].update(countermodel={}),
    "a row's and the result's shown model both not the request's": lambda a: (
        a["per_choice"][1]["shown"].update(countermodel={}), a["result"]["countermodel"].update(model={})),
    "the result's countermodel not its row's": lambda a: a["result"]["countermodel"].update(model={}),
    "an untaken reading on a query": lambda a: a.update(untaken=[["rs_1", 0]]),
    "a dead note on a query": lambda a: a.update(dead=[{"accepted": True}]),
    # the DRI ruling of rd-3 round 3: every label and reading the answer and its plan name is the request's
    "a label naming no coupling": lambda a: a.update(labels=["coupling:c9"]),
    "a pair label of no predicate": lambda a: a["result"]["proof"].update(conditional_on=["unsaid:pair:x,y"]),
    "a condition that names nothing": lambda a: a["result"]["proof"].update(conditional_on=[""]),
    "a plan line citing a label the request lacks": lambda a: a["english"][1].update(label="narrowing:n9"),
    "a plan line naming a reading the document lacks": lambda a: a["english"][0].update(readings=[["rs_1", 5]]),
    "a plan line showing a piece no row shows": lambda a: a["english"][-1].update(model="certificate@1"),
    "a plan line showing a row that does not exist": lambda a: a["english"][-1].update(model="countermodel@9"),
    "a status line no row relays": lambda a: a["english"].append(
        {"frame": "status", "result": None, "readings": [], "model": None, "gaps": [], "label": "CONFLICT: made up"}),
    "an E17 line for no dead reading": lambda a: a["english"].append(
        {"frame": "E17", "result": None, "readings": [["rs_1", 1]], "model": None, "gaps": [], "label": None}),
}


@pytest.mark.parametrize("mutation", list(MUTATIONS))
def test_a_mutated_verdicts_answer_is_unavailable(tmp_path, mutation):
    _, route = loaded(tmp_path)
    answer = route.query_answer(QUERY)
    request = _checked(route, answer)
    mutated = copy.deepcopy(answer)
    MUTATIONS[mutation](mutated)
    assert json.dumps(mutated) != json.dumps(answer)
    with pytest.raises(CheckerUnavailable):
        route.check_answer(mutated, request)


def test_every_question_binds_its_rows_exactly(tmp_path):
    """Review B2's class: a query (with or without readings named) is bound as exactly as the other questions; a
    conflict answer under a reading lists only the choices taking it."""
    answers = _genuine_answers(tmp_path)
    for name, (route, answer) in answers.items():
        request = _checked(route, answer)
        for mutate in (lambda a: a["per_choice"].pop(), lambda a: a["per_choice"].append(
                {**copy.deepcopy(a["per_choice"][0]), "choice": [["rs_1", 9]]})):
            mutated = copy.deepcopy(answer)
            mutate(mutated)
            with pytest.raises(CheckerUnavailable):
                route.check_answer(mutated, request)
    route, answer = answers["query NONE under a reading"]
    assert [e["choice"] for e in answer["per_choice"]] == [C1]
    request = _checked(route, answer)
    mutated = copy.deepcopy(answer)
    mutated["per_choice"].insert(0, {**copy.deepcopy(answer["per_choice"][0]), "choice": C0})
    with pytest.raises(CheckerUnavailable):
        route.check_answer(mutated, request)


# Review B of rd-3 looprecheck1, as the DRI ruling of round 3 divides it: a row's word names the piece it rests on
# (`ROW_PIECES`), which the request must have sent and the row must note accepted (binding); which word the accepted
# pieces give, and the verdict folded from the words, is Lean's (`nd_rowsHold`, `readings_wire_verdicts_*`).

WORDS = ("CONFLICT-FREE", "CONFLICT", "proved", "refuted", "model", "INCONSISTENT", "UNKNOWN")


def test_every_row_word_names_a_piece_lean_accepted(tmp_path):
    """Each row's conflict word and question word set to every other word: a word that names no piece the row notes
    accepted is unavailable; the genuine fixtures note no second accepted piece, so every such mutant is caught."""
    from ve.readings_verdicts import ROW_PIECES
    survivors, backed = [], 0
    for name, (route, answer) in _genuine_answers(tmp_path).items():
        request = _checked(route, answer)
        for k, entry in enumerate(answer["per_choice"]):
            for field in {"conflict", request["question"]}:
                for word in WORDS:
                    if word == entry[field]:
                        continue
                    piece = ROW_PIECES[field].get(word)
                    if word != "UNKNOWN" and piece is not None and entry["evidence"].get(piece) is True:
                        backed += 1
                        continue
                    if word == "UNKNOWN":
                        continue  # UNKNOWN names no piece: whether a row is UNKNOWN is Lean's
                    mutated = copy.deepcopy(answer)
                    mutated["per_choice"][k][field] = word
                    try:
                        route.check_answer(mutated, request)
                    except CheckerUnavailable:
                        continue
                    survivors.append(f"{name}: row {k} {field} = {word}")
    assert survivors == [] and backed == 0, "\n".join(survivors)


def test_review_b_looprecheck1_rows_tied_to_the_evidence_sent(tmp_path):
    """The finding's probes on F-ND1 and F-ND2: each row word naming evidence the row does not note accepted."""
    answers = _genuine_answers(tmp_path)
    # Query: rs_1:1 proved while its only piece is an accepted countermodel turns SOME into ALL.
    route, answer = answers["query SOME"]
    request = _checked(route, answer)
    noted = answer["per_choice"][1]["evidence"]
    assert noted["countermodel"] is True and "certificate" not in noted
    mutated = copy.deepcopy(answer)
    mutated["per_choice"][1]["query"] = "proved"
    with pytest.raises(CheckerUnavailable):
        route.check_answer(mutated, request)
    # Premises: every row INCONSISTENT while Lean accepted a model for each.
    route, answer = answers["premises"]
    request = _checked(route, answer)
    assert {e["premises"] for e in answer["per_choice"]} == {"model"}
    mutated = copy.deepcopy(answer)
    for e in mutated["per_choice"]:
        e["premises"] = "INCONSISTENT"
    with pytest.raises(CheckerUnavailable):
        route.check_answer(mutated, request)
    # Conflict: CONFLICT-FREE rows while the packages' note is false, or missing.
    route, answer = answers["conflict CONFLICT"]
    request = _checked(route, answer)
    assert [e["conflict"] for e in answer["per_choice"]] == ["CONFLICT", "CONFLICT-FREE"]
    for mutate in (lambda e: e.update(conflict="CONFLICT-FREE"),
                   lambda e: (e.update(conflict="CONFLICT-FREE"), e["evidence"].pop("conflict"))):
        mutated = copy.deepcopy(answer)
        mutate(mutated["per_choice"][0])
        with pytest.raises(CheckerUnavailable):
            route.check_answer(mutated, request)


def test_a_reading_s_conflict_notes_are_the_same_in_every_answer(tmp_path, monkeypatch):
    """The same conflict packages get the same note in every request of the route: a later answer that notes them
    otherwise (here, an otherwise consistent query answer whose conflict notes are dropped) is unavailable."""
    from ve import readings_verdicts
    _, route = loaded(tmp_path)
    route.conflict_answer()
    real = readings_verdicts.Enumerated.check_answer

    def downgraded(self, row, case):
        real(self, row, case)
        for entry in row["per_choice"]:
            entry["evidence"]["conflict"] = False
    monkeypatch.setattr(readings_verdicts.Enumerated, "check_answer", downgraded)
    with pytest.raises(CheckerUnavailable, match="differently from one request to the next"):
        route.entailment(QUERY)


def test_beyond_64_choices_rows_are_only_the_requests_evidence():
    """Past 64 choices (no list to bind to) only W2's budget shape, with rows for evidence the request sent."""
    from ve.readings_verdicts import _check_answer as check, _Frame
    raw, document = fnd3()

    def _check_answer(answer, request):
        check(answer, request, _Frame(request, None, True, [f"rs_{k}" for k in range(1, 8)]))
    model = {"complete": True, "domains": {"agent": ["a"], "user": ["u"]}, "constants": {}, "relations": {"asks": []}}
    choice = [[f"rs_{k}", 1] for k in range(1, 8)]
    request = case("readings-verdicts", raw, document, question="query", premises=[], conclusion=QUERY,
                   evidence=[{"choice": choice, "countermodel": {"kind": "choice-model", "model": model,
                                                                 "filling": {}}}])
    [row] = run(LEAN, [request])
    _check_answer(row, request)
    for mutate in (lambda a: a["per_choice"][0].update(choice=[[f"rs_{k}", 0] for k in range(1, 8)]),
                   lambda a: a["per_choice"].append(copy.deepcopy(a["per_choice"][0])),
                   lambda a: a["result"].pop("budget"),
                   lambda a: a["result"].update(units=["u9"])):
        mutated = copy.deepcopy(row)
        mutate(mutated)
        with pytest.raises(CheckerUnavailable):
            _check_answer(mutated, request)
    with pytest.raises(CheckerUnavailable):
        _check_answer(row, {**request, "evidence": []})
    # a row for a choice that does not take the request's reading
    mutated = copy.deepcopy(row)
    mutated["result"]["assumed"] = [["rs_1", 0]]
    with pytest.raises(CheckerUnavailable):
        _check_answer(mutated, {**request, "assumed": [["rs_1", 0]]})


def test_a_choice_result_outside_the_proved_schema_is_unavailable(tmp_path):
    _, route = loaded(tmp_path)
    answer = route.query_answer(QUERY)
    request = _checked(route, answer)
    mutated = copy.deepcopy(answer)
    mutated["per_choice"][0]["conflict"] = "NOT-A-RESULT"
    with pytest.raises(CheckerUnavailable):
        route.check_answer(mutated, request)


def test_a_plan_line_python_cannot_render_is_unavailable(tmp_path, monkeypatch):
    """A line Python cannot word as planned is unavailable, never left out: an unknown frame, Lean's `unworded`
    line (a condition with no wording, `conditionItems`), a shown model under readings other than its choice's, and
    a model of no row."""
    doc, route = loaded(tmp_path)
    answer = copy.deepcopy(route.query_answer(QUERY))
    [k] = [k for k, line in enumerate(answer["english"]) if line["model"] is not None]
    for mutate in (lambda a: a["english"][0].update(frame="E99"),
                   lambda a: a["english"].insert(1, {"frame": "unworded", "result": None, "readings": [],
                                                     "model": None, "gaps": [], "label": PAIR}),
                   lambda a: a["english"][k].update(readings=[["rs_1", 0]]),
                   lambda a: a["english"][k].update(model="countermodel@9")):
        mutated = copy.deepcopy(answer)
        mutate(mutated)
        monkeypatch.setattr(route, "query_answer", lambda *args, **kwargs: mutated)
        with pytest.raises(CheckerUnavailable):
            query_english(doc, QUERY, route.entailment(QUERY))


# ---------------------------------------------------------------------------------------------------------------
# rd-3 looprecheck2 B (conditional overclaim) and the DRI ruling of round 3: an answer's conditions are Lean's

def _without_pair(answer):
    """The reviewer's probe: `answer` with the pair condition removed from every `conditional_on` and from `labels`,
    and its plan made as Lean plans an answer with no condition (E3 and its lines dropped; a CONFLICT-FREE answer's
    E13 for every sentence, which no remaining label mentions)."""
    forged = copy.deepcopy(answer)
    for obj in [forged["result"], *forged["result"].get("proofs", []), forged["result"].get("proof") or {}]:
        if "conditional_on" in obj:
            obj["conditional_on"] = [x for x in obj["conditional_on"] if x != PAIR]
    forged["labels"] = [x for x in forged["labels"] if x != PAIR]
    forged["english"] = [line for line in forged["english"] if line["frame"] not in ("E3", "P1")]
    return forged


def test_review_b_looprecheck2_conditions_are_lean_s(tmp_path):
    """The finding: on F-ND1 the pair condition removed from a genuine CONFLICT-FREE answer and an ALL query, the
    dependent members regenerated. Lean cannot give that answer: its `conditional_on` is `conditionsOf` of the rows
    (`verdicts_conditions_conflict_free`, `verdicts_conditions_all`, audited), and asked the same request Lean gives
    the condition, in `conditional_on`, `labels` and a P1 line citing it. The client checks schema and binding only
    (the probe names nothing the request lacks) and relays Lean's English unchanged: every planned line is one
    sentence, in order, so the condition Lean plans is shown and none is added or dropped."""
    doc, route = loaded(tmp_path)
    audit = (ROOT / "lean/VE/Audit.lean").read_text()
    statements = (ROOT / "lean/statements.txt").read_text()
    for theorem in ("verdicts_conditions_conflict_free", "verdicts_conditions_all", "verdicts_conditions_some",
                    "verdicts_conditions_none", "mem_conditionsOf", "verdictsPlan_cites"):
        assert f"#print axioms VE.Readings.Run.{theorem}\n" in audit
        assert f"theorem VE.Readings.Run.{theorem}\n" in statements
    for answer, every, lines in ((route.conflict_answer(), "E26", report_english),
                                 (route.query_answer(IMPLIES), "E26", None)):
        request = _checked(route, answer)
        result = answer["result"]
        assert result["conditional_on"] == [PAIR] and answer["labels"] == [PAIR]
        assert [line["label"] for line in answer["english"] if line["frame"] == "P1"] == [PAIR]
        forged = _without_pair(answer)
        assert forged != answer and forged["result"]["conditional_on"] == []
        # Lean, asked the very request again, gives the condition: the forgery is not Lean's answer to it.
        [again] = run(LEAN, [request])
        assert again == answer and again != forged
        # The client binds, it does not re-derive: the probe names nothing the request lacks.
        route.check_answer(forged, request)
    wording_lines = report_english(doc, route)
    assert "This holds provided that:" in wording_lines
    assert "Whenever an agent must help an user, it may help that user." in wording_lines
    data = route.entailment(IMPLIES)
    rendered = query_english(doc, IMPLIES, data)
    assert len(rendered) == len(route.query_answer(IMPLIES)["english"])
    assert rendered[1:3] == ["This holds provided that:", "Whenever an agent must help an user, it may help that user."]


def test_python_relays_every_planned_line(tmp_path):
    """Python never builds or omits a condition: for every genuine answer of F-ND1 and F-ND2, Lean's plan cites
    every label of `labels` (and has E3 exactly when there is one), and Python words it as one sentence per line, in
    order, E3 as E3 and each P1 line as its pair sentence. The seeded bug of round 3 (Python skipping the E3 or P1
    lines) fails here."""
    from ve.readings_s2_wording import S2Wording
    pair = "Whenever an agent must help an user, it may help that user."
    for sub, make in (("fnd1", fnd1), ("fnd2", fnd2)):
        (tmp_path / sub).mkdir()
        doc, route = loaded(tmp_path / sub, make)
        answers = [(route.conflict_answer(), None, None), (route.premises_answer(), None, None)]
        if make is fnd1:
            answers += [(route.query_answer(QUERY), QUERY, None), (route.query_answer(IMPLIES), IMPLIES, None),
                        (route.query_answer(QUERY, C1), QUERY, C1)]
        for answer, conclusion, assumed in answers:
            frames_ = [line["frame"] for line in answer["english"]]
            assert all(any(line["label"] == label for line in answer["english"]) for label in answer["labels"])
            assert ("E3" in frames_) == bool(answer["labels"])
            wording = S2Wording(doc, route)
            sentences = (wording.plan(answer) if conclusion is None else
                         wording.query(conclusion, {"assumed": assumed}))
            assert len(sentences) == len(answer["english"])
            for line, sentence in zip(answer["english"], sentences):
                if line["frame"] == "E3":
                    assert sentence == "This holds provided that:"
                if line["frame"] == "P1":
                    assert sentence == pair


# ---------------------------------------------------------------------------------------------------------------
# Malformed requests (build checklist 5): only Lean's error texts, never a verdict

@pytest.mark.parametrize("field, value", [("question", 7), ("question", "everything"), ("assumed", {}),
                                          ("assumed", [["rs_1"]]), ("conclusion", None), ("conclusion", [])])
def test_malformed_requests_are_refused(field, value):
    raw = env1()
    document, _ = doc1(raw)
    fields = {"question": "query", "evidence": [], "premises": [], "conclusion": QUERY, field: value}
    [row] = run(LEAN, [case("readings-verdicts", raw, document, **fields)])
    assert row["status"] == "error" and isinstance(row["error"], str), row


@pytest.mark.parametrize("evidence", [7, True, None, {}, [7], [{"choice": 7}], [{"choice": C0, "conflict": 7}],
                                      [{"choice": C0, "certificate": {"certificate": True}}],
                                      [{"choice": C0, "countermodel": {"model": [], "filling": 7}}]])
def test_malformed_evidence_is_no_verdict(evidence):
    raw = env1()
    document, _ = doc1(raw)
    [row] = run(LEAN, [case("readings-verdicts", raw, document, question="query", evidence=evidence, premises=[],
                            conclusion=QUERY)])
    assert row["status"] == "error" or row["result"]["verdict"] == "UNKNOWN", row


def test_the_superposed_route_is_not_answered_here(tmp_path):
    from tests.test_readings_s2_document import _m6
    doc = load_document(_m6(tmp_path))
    route = context(doc)
    assert route.route == "superposed"
    [row] = run(LEAN, [case("readings-verdicts", route.environment, route.document, question="conflict",
                            evidence=[])])
    assert row["status"] == "error" and row["error"].startswith("UnsupportedProfile: readings-verdicts answers")


def test_answers_are_json_round_trip_stable(tmp_path):
    _, route = loaded(tmp_path)
    answer = route.conflict_answer()
    assert json.loads(json.dumps(answer)) == answer


# ---------------------------------------------------------------------------------------------------------------
# DRI wording sign-off (rd-3 round 3, item 4): every changed English row keeps the base's names, conditions and
# specificity (the lf-12 ruling, items 2(a)-(c)); a row that loses one is fixed in Lean, never signed.

WORDING = ROOT / "docs/readings-defaults/rd3/evidence/wording-round3.json"
GAP = "Here the text does not say whether "
CONDITION_LEADS = ("This holds provided that:", "Whenever ", "Sentence ", "Sentences ", "This does not depend on ")


def _split(line):
    """A line's result and its gap sentences (spec 2.2: one per filled gap the result depends on)."""
    head, *gaps = line.split(f" {GAP}")
    return head, [GAP + g for g in gaps]


def _names(lines):
    """The names a line shows: quoted readings and conclusions, sentence numbers, elements."""
    import re
    text = "\n".join(lines)
    return set(re.findall(r"\*[^*]+\*", text)) | set(re.findall(r"\b(?:sentences? \d+|e\d+)\b", text))


def _keeps_the_base(base, head):
    """lf-12 rule 2: (a) every name the base shows is shown; (b) every condition line of the base is kept, and the head
    adds only condition lines; (c) every result is as specific as the base's, its gap sentences among the base's (spec
    2.2 keeps exactly those the result depends on)."""
    problems = []
    if not _names(base) <= _names(head):
        problems.append(f"names lost: {sorted(_names(base) - _names(head))}")
    results = [_split(line) for line in head]
    for line in base:
        result, gaps = _split(line)
        if line.startswith(CONDITION_LEADS):
            if line not in head:
                problems.append(f"condition lost: {line}")
            continue
        match = [g for r, g in results if r == result]
        if not match:
            problems.append(f"result lost: {result}")
        elif not set(match[0]) <= set(gaps):
            problems.append(f"gap not in the base: {sorted(set(match[0]) - set(gaps))}")
    base_results = {_split(line)[0] for line in base}
    for line in head:
        if not line.startswith(CONDITION_LEADS) and _split(line)[0] not in base_results:
            problems.append(f"result added: {line}")
    return problems


def test_dri_wording_rows_keep_the_base(tmp_path, capsys):
    """Every row of the saved wording delta keeps the base's names, conditions and specificity, and the saved head
    lines are this tree's (recomputed here), so the sign-off ("DRI = orchestrator, 2026-10-09", docs/readings-defaults/
    rd3/DELTA.md) covers the English the branch shows."""
    from tests.test_readings_nd_document import fnd1 as nd1, fnd2 as nd2
    from ve.document import check_document, main
    saved = json.loads(WORDING.read_text())
    assert saved["base"] == "a3476e66" and len(saved["rows"]) == 6
    for row in saved["rows"]:
        assert _keeps_the_base(row["base"], row["head"]) == [], row["case"]
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    path1, path2 = nd1(tmp_path / "a"), nd2(tmp_path / "b")
    query, implies = tmp_path / "query.json", tmp_path / "implies.json"
    query.write_text(json.dumps(QUERY))
    implies.write_text(json.dumps(IMPLIES))

    def readings(*args):
        assert main(["readings", str(path1), *args]) == 0
        return json.loads(capsys.readouterr().out)["english"]
    live = [readings("--conclusion", str(query)), readings("--conclusion", str(query), "--under", "rs_1:0"),
            readings("--conclusion", str(query), "--under", "rs_1:1"), readings("--conclusion", str(implies)),
            check_document(path1)["readings"]["english"], check_document(path2)["readings"]["english"]]
    assert [row["head"] for row in saved["rows"]] == live
