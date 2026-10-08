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

import pytest

from tests import lean_routes
from tests.test_readings_nd_document import ASKS as ASKS_SENTENCE, EVERY as EVERY_SENTENCE, QUERY, fnd1, fnd2
from tests.test_readings_nd_lean import case, doc1, env1, run
from ve.document import load_document
from ve.errors import CheckerUnavailable, VEError
from ve.readings_s2_wording import query_english, report_english
from ve.readings_verdicts import _check_answer, context

LEAN = "ve_readings_route"
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
    assert frames(answer) == [("E12", "R2"), ("E12", "R3")]
    [shown] = [line for line in answer["english"] if line["model"] is not None]
    # one filled gap the result depends on: the duty's own gap under reading `asks`, answered 'no' (spec 2.2)
    assert shown["gaps"] == [["help_required", ["e0", "e0"], False]] and shown["readings"] == [["rs_1", 1]]
    lines = query_english(doc, QUERY, data)
    assert lines[0].startswith(f"Read sentence 1 as {EVERY_SENTENCE}: the conclusion follows")
    assert lines[1].startswith(f"Read sentence 1 as {ASKS_SENTENCE}: the conclusion does not follow")
    assert lines[1].endswith("Here the text does not say whether e0 must help e0; this situation answers 'no'.")
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
    answer = ask(route, "query", evidence_of(route, pieces), premises=[], conclusion=QUERY)
    assert answer["result"]["verdict"] != "ALL"
    entry = answer["per_choice"][1]
    assert entry["query"] == "UNKNOWN" and (entry["errors"].get("certificate") or entry["evidence"]["certificate"] is False)
    with pytest.raises(CheckerUnavailable, match="ReadingsConformance"):
        _check_answer(answer, "query")


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
# Lean's answer is untrusted output (build checklist 4): every field dropped, emptied or retyped is unavailable

def _genuine_answer(tmp_path):
    _, route = loaded(tmp_path)
    return route, route.query_answer(QUERY)


MUTATIONS = {
    "drop route": lambda a: a.pop("route"),
    "another question": lambda a: a.update(question="conflict"),
    "result a list": lambda a: a.update(result=[]),
    "per_choice dropped": lambda a: a.pop("per_choice"),
    "a row named twice": lambda a: a["per_choice"].append(copy.deepcopy(a["per_choice"][0])),
    "a row's conflict retyped": lambda a: a["per_choice"][0].update(conflict=True),
    "an acceptance as 1": lambda a: a["per_choice"][0]["evidence"].update(conflict=1),
    "an error not a string": lambda a: a["per_choice"][0]["errors"].update(conflict=7),
    "english a string": lambda a: a.update(english="E12"),
    "a line without its frame": lambda a: a["english"][0].pop("frame"),
    "a line's model retyped": lambda a: a["english"][1].update(model=True),
    "restrictions null": lambda a: a.update(restrictions=None),
    "labels with a bool": lambda a: a.update(labels=[True]),
    "dead_readings an object": lambda a: a.update(dead_readings={}),
}


@pytest.mark.parametrize("mutation", list(MUTATIONS))
def test_a_mutated_verdicts_answer_is_unavailable(tmp_path, mutation):
    route, answer = _genuine_answer(tmp_path)
    _check_answer(answer, "query", [route.choice_json(c) for c in route.choices], exact=False)
    mutated = copy.deepcopy(answer)
    MUTATIONS[mutation](mutated)
    with pytest.raises(CheckerUnavailable):
        _check_answer(mutated, "query", [route.choice_json(c) for c in route.choices], exact=False)


def test_a_row_for_a_choice_lean_did_not_list_is_unavailable(tmp_path):
    route, answer = _genuine_answer(tmp_path)
    mutated = copy.deepcopy(answer)
    mutated["per_choice"][0]["choice"] = [["rs_1", 7]]
    with pytest.raises(CheckerUnavailable):
        _check_answer(mutated, "query", [route.choice_json(c) for c in route.choices], exact=False)
    conflict = copy.deepcopy(route.conflict_answer())
    conflict["per_choice"] = conflict["per_choice"][:1]
    with pytest.raises(CheckerUnavailable):
        _check_answer(conflict, "conflict", [route.choice_json(c) for c in route.choices])


def test_a_plan_line_python_cannot_render_is_unavailable(tmp_path, monkeypatch):
    doc, route = loaded(tmp_path)
    answer = copy.deepcopy(route.query_answer(QUERY))
    for mutate in (lambda a: a["english"][0].update(frame="E99"),
                   lambda a: a["english"][1].update(readings=[["rs_1", 0]]),
                   lambda a: a["english"][1].update(model="countermodel@9")):
        mutated = copy.deepcopy(answer)
        mutate(mutated)
        monkeypatch.setattr(route, "query_answer", lambda *args, **kwargs: mutated)
        with pytest.raises(CheckerUnavailable):
            query_english(doc, QUERY, route.entailment(QUERY))


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
