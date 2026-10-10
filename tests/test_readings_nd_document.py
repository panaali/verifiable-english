"""Readings under the unspecified completion through `ve document` (readings-defaults plan RD-2b; spec 3, 4.2, 4.3).

F-ND1 and F-ND2 (spec 8.3) written as documents go through `ve document load`, `check`, `render` and
`readings --conclusion` with Python's fold still in place (RD-3 moves it to Lean): every verdict rests on evidence
Lean's `readings-choice` checked on the choice's filled document, and every name, text and filled document is Lean's.
A generator run on F-ND1 reads Lean's filled document from `readings-elaborate` before any situation is recorded.
The relay binds `fill_premises`, `filled` and the completion's elaborate row to the request: each genuine row is
mutated field by field and every mutation is `CheckerUnavailable`, never an answer.
"""
from __future__ import annotations

import copy
import json
import re

import pytest

from tests import lean_routes
from tests.test_document import unit, write_doc
from tests.test_readings_nd_lean import PROBE1, base1, doc1, doc2, env1, env2, norm, reading, reading_set
from tests.test_readings_s1_lean import entry, situation_id
from ve.document import _environment, check_document, load_document, main, render_document
from ve.errors import CheckerUnavailable, VEError
from ve.readings import s1_content_meaning_id

EVERY = "*Every agent must help each user*"
ASKS = '*Every agent must help each user, if that user has the recorded relation "asks" to that agent*'
MUST_X = "*Every act must be done, if that act may be tried*"
QUERY = ["forall", "agent", ["forall", "user", ["binary", "help_required", ["var", 1], ["var", 0]]]]
GAP = re.compile(r" Here the text does not say whether [^;]+; this situation answers '(yes|no)'\.")
RESERVED = ("unsaid__", "unsaid--")  # what no English line may show (spec 2.5)


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def as_document(tmp_path, raw, document, texts):
    """The readings document as a `ve-document@1` file: one sentence per unit, each reading's meaning id computed."""
    env = _environment(raw)
    document = copy.deepcopy(document)
    for reading_set_ in document["reading_sets"]:
        for r in reading_set_["readings"]:
            r["meaning_id"] = s1_content_meaning_id(env, reading_set_["id"], r)
    units, text = [], b""
    for u in document["units"]:
        sentence = texts[u["id"]].encode()
        units.append(unit(u["id"], len(text), len(text) + len(sentence), "norm", "specified", u.get("content")))
        text += sentence
    return write_doc(tmp_path, text, units, environment_json=raw, reading_sets=document["reading_sets"])


def fnd1(tmp_path):
    document, _ = doc1(env1())
    return as_document(tmp_path, env1(), document, {"u1": "Every agent must help each user.\n"})


def fnd2(tmp_path):
    document, _ = doc2(env2())
    return as_document(tmp_path, env2(), document, {"u0": "Nothing may be done.\n",
                                                    "u2": "Every act must be done if it may be tried.\n"})


def test_fnd3_128_choices_gets_a_decided_public_conflict(tmp_path):
    """RD-6b's E10 boundary: the superposed certificate decides all 128 choices."""
    raw = env1()
    sets, units, texts = [], [], {}
    for k in range(7):
        name = f"u{k + 1}"
        document, _ = doc1(raw, set_id=f"rs_{k + 1}", unit=name, rule=f"must-help-{k + 1}")
        sets.extend(document["reading_sets"])
        units.extend(document["units"])
        texts[name] = f"Every agent must help each user, sentence {k + 1}.\n"
    path = as_document(tmp_path, raw, {"units": units, "reading_sets": sets}, texts)
    report = check_document(path)["readings"]
    assert (report["route"], report["choice_count"], report["choices_checked"]) == \
        ("superposed", "over 64", 128)
    assert report["conflict"]["status"] == "CONFLICT-FREE"
    assert report["english"][0] == \
        "Under every reading of the 7 open sentences, no two rules on the same act contradict each other."
    from tests.test_readings_nd_lean import LEAN, case, one
    from ve.readings_route import _completion_elaborate
    wire_document = {"units": units, "reading_sets": sets}
    answer = one(LEAN, "readings-elaborate", raw, wire_document)
    request = case("readings-elaborate", raw, wire_document)
    assert _completion_elaborate(answer, request)["choices_checked"] == 128
    forged = copy.deepcopy(answer)
    forged["choices_checked"] = 129
    with pytest.raises(CheckerUnavailable, match="invalid answer"):
        _completion_elaborate(forged, request)


def shown(lines):
    """No English line names a filled table or a generated rule (spec 2.5)."""
    assert lines and not [line for line in lines if any(prefix in line for prefix in RESERVED)], lines
    return lines


# ---------------------------------------------------------------------------------------------------------------
# F-ND1: load, check, render, readings --conclusion

def test_fnd1_load_relays_leans_route_and_filled_document(tmp_path):
    from ve.readings_verdicts import Superposed, context
    doc = load_document(fnd1(tmp_path))
    s2 = doc["readings_s2"]
    assert (s2["route"], s2["finding"], s2["choices"]) == (
        "superposed", None, [[["rs_1", 0]], [["rs_1", 1]]])
    assert [entry["label"] for entry in s2["fill"]] == ["unsaid:pair:help_required,help_permitted"]
    # validate's and elaborate's filled documents are Lean's, the same
    assert doc["readings_s1"]["filled"] == s2["filled"]
    assert [(e["set"], e["index"]) for e in s2["fill_premises"]] == [("rs_1", 0), ("rs_1", 1)]
    route = context(doc)
    assert isinstance(route, Superposed) and route.completion
    assert route.choices == [{"rs_1": 0}, {"rs_1": 1}]
    # the readings' documents are Lean's filled ones; the slot shows what the author wrote
    candidate = route.source.set_by_id("rs_1").candidates[0]
    assert candidate.content.body["over"] and not candidate.authored.body["over"]
    assert sorted(route.source.filled_tables.values()) == ["help_permitted", "help_required"]


def test_fnd1_check_every_choice_conflict_free_with_a_model(tmp_path):
    report = check_document(fnd1(tmp_path))
    readings = report["readings"]
    assert readings["conflict"]["status"] == "CONFLICT-FREE"
    # RD-3's per-choice statuses are kept on the superposed route (review B3 of rd-6b): one certificate under no
    # assumed reading makes every compatible choice CONFLICT-FREE (`readings_wire_nd_conflict_sound`).
    assert [c["status"] for c in readings["conflict"]["choices"]] == ["CONFLICT-FREE", "CONFLICT-FREE"]
    assert readings["conflict"]["reading_premises_used"] == ["unsaid:pair:help_required,help_permitted"]
    assert readings["status"] == ("CONFLICT-FREE among rules on the same act, conditional on 0 coherence premises and "
                                  "1 reading premises")
    assert report["premises"]["status"] == "model"
    assert report["premises"]["route"] == "superposed"
    assert [c["status"] for c in report["premises"]["choices"]] == ["model", "model"]
    assert [c["status"] for c in report["premises"]["candidates"]] == ["model", "model"]
    # RD-3's lines but the enumerated route's "checked one way at a time", which the superposed route makes false
    # (pending the DRI's sign-off, docs/readings-defaults/rd6b/DELTA.md).
    assert shown(readings["english"]) == [
        "Under every reading of the open sentence, no two rules on the same act contradict each other.",
        "This holds provided that:", "Whenever an agent must help an user, it may help that user.",
        "This does not depend on how sentence 1 is read.",
        f"Read sentence 1 as {EVERY}: the sentences of this document can all be true together, as here: nothing exists."]
    [pair] = readings["sets"][0]["pairs"]
    assert pair["wording"] == "E19"


def test_fnd1_render_shows_the_situation_with_its_filled_gaps(tmp_path):
    text = render_document(fnd1(tmp_path))
    lines = shown(text.splitlines())
    assert lines[3:5] == ["One reading is: Every agent must help each user.",
                          'Another reading is: Every agent must help each user, if that user has the recorded '
                          'relation "asks" to that agent.']
    [pair] = [line for line in lines if line.startswith("These two readings differ here: ")]
    assert pair == (
        "These two readings differ here: a is an agent; u is a user. Here the text does not say whether a may help "
        "u; this situation answers 'yes'. Here the text does not say whether a must help u; this situation answers "
        f"'no'. Under {EVERY}, a still must. Under {ASKS}, a is not required to.")


def query(tmp_path, capsys, path, *under):
    conclusion = tmp_path / "conclusion.json"
    conclusion.write_text(json.dumps(QUERY))
    assert main(["readings", str(path), "--conclusion", str(conclusion),
                 *[arg for set_index in under for arg in ("--under", set_index)]]) == 0
    return json.loads(capsys.readouterr().out)


def test_fnd1_readings_conclusion_some(tmp_path, capsys):
    """The query of spec 2.6: it follows under the first reading (a certificate Lean accepted with the choice's
    conflict packages) and fails under the second, where the gap is filled 'no' (a base model and filling Lean
    checked)."""
    path = fnd1(tmp_path)
    data = query(tmp_path, capsys, path)
    assert data["verdict"] == "SOME"
    assert (data["proof"]["choice"], data["countermodel"]["choice"]) == ([["rs_1", 0]], [["rs_1", 1]])
    # rd-3 round 3: the proof rests on the pair condition (its conflict packages use it), stated after the result.
    follows, provided, pair, fails = shown(data["english"])
    assert follows == (f"Read sentence 1 as {EVERY}: the conclusion follows: *For every agent, for every user, that "
                       "agent must help that user.*")
    assert (provided, pair) == ("This holds provided that:", "Whenever an agent must help an user, it may help that user.")
    assert fails.startswith(f"Read sentence 1 as {ASKS}: the conclusion does not follow. It fails here: ")
    # every gap of the situation is shown with its answer, and the duty is filled 'no' there
    assert GAP.search(fails) and fails.endswith("must help e0; this situation answers 'no'.")
    assert fails.endswith("It fails here: e0 is an agent; e0 is a user. Here the text does not say whether e0 must "
                          "help e0; this situation answers 'no'.")
    assert len(GAP.findall(fails)) == 1  # Lean's gaps: only the one the conclusion's value reads (review B3 of rd-6b)
    assert query(tmp_path, capsys, path, "rs_1:0")["verdict"] == "ALL"
    # Under the only choice taking rs_1:1 the conclusion fails: NONE, as RD-3 answered (review B3 of rd-6b).
    under = query(tmp_path, capsys, path, "rs_1:1")
    assert (under["verdict"], under["assumed"]) == ("NONE", [["rs_1", 1]])
    assert [c["choice"] for c in under["countermodels"]] == [[["rs_1", 1]]]
    assert shown(under["english"]) == [fails]


# ---------------------------------------------------------------------------------------------------------------
# F-ND2: a latent conflict under one reading

def test_fnd2_check_conflict_under_one_reading_only(tmp_path):
    report = check_document(fnd2(tmp_path))
    conflict = report["readings"]["conflict"]
    assert conflict["status"] == "CONFLICT"
    assert conflict["choice"] == [["rs_2", 0]]
    assert [(c["choice"], c["status"]) for c in conflict["choices"]] == [
        ([["rs_2", 0]], "CONFLICT"), ([["rs_2", 1]], "CONFLICT-FREE")]
    assert report["readings"]["status"] == "CONFLICT: pair conflict on x_required->x_permitted at e0 under rs_2@1:0"
    english = shown(report["readings"]["english"])
    [line] = [line for line in english if "contradict each other here" in line]
    assert line.startswith(f"Read sentence 2 as {MUST_X}: two rules contradict each other here: ")
    # Lean's plan shows the filled gaps the conflict's value reads with nothing filled (readings-defaults 2.2, RD-3):
    # the permission to try, filled 'yes', which triggers the duty, and the duty's own gap; not the third table.
    # On the superposed route they are Lean's too (`gapsOf` of the witness's target, review B3 of rd-6b).
    assert line.endswith("Here the text does not say whether e0 may be tried; this situation answers 'yes'. "
                         "Here the text does not say whether e0 must be done; this situation answers 'no'.")
    assert len(GAP.findall(line)) == 2
    assert english[english.index(line) + 1] == "CONFLICT: pair conflict on x_required->x_permitted at act e0"


def test_fnd2_query_is_gated_by_the_conflict(tmp_path, capsys):
    """S2a 14.8 (review A2): no entailment verdict while a choice is not CONFLICT-FREE."""
    path = fnd2(tmp_path)
    conclusion = tmp_path / "x.json"
    conclusion.write_text(json.dumps(["forall", "act", ["unary", "x_required", ["var", 0]]]))
    assert main(["readings", str(path), "--conclusion", str(conclusion)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert (data["verdict"], data["status"], data["choice"]) == (
        "UNKNOWN", "UNKNOWN (conflict status: CONFLICT)", [["rs_2", 0]])


def test_fnd2_render(tmp_path):
    lines = shown(render_document(fnd2(tmp_path)).splitlines())
    [pair] = [line for line in lines if line.startswith("These two readings differ here: ")]
    assert pair.startswith("These two readings differ here: a is an act.") and len(GAP.findall(pair)) == 3
    assert pair.endswith("Under *Every act may be tried*, a is permitted to. Under "
                         f"{MUST_X}, a is not permitted to.")


# ---------------------------------------------------------------------------------------------------------------
# Lean's texts, verbatim

def test_fnd5_reserved_name_is_leans_text(tmp_path):
    raw = env1()
    document = {"units": [{"id": "u0", "kind": "norm", "content": norm("be-helpful", "help_required", True)},
                          {"id": "u1"}],
                "reading_sets": [reading_set("rs_1", "u1", [
                    reading("named", norm("unsaid--help-required", "help_permitted", True), {})], {})]}
    path = as_document(tmp_path, raw, document, {"u0": "Agents must help.\n", "u1": "They may help.\n"})
    with pytest.raises(VEError) as caught:
        load_document(path)
    assert str(caught.value) == "InvalidInput: reserved name unsaid--help-required"


# ---------------------------------------------------------------------------------------------------------------
# The generator (plan RD-2b: a generator run on F-ND1 that finds the 3.3 situation)

def pending_fnd1():
    raw = env1()
    document, sid = doc1(raw)
    pending = copy.deepcopy(document)
    rs = pending["reading_sets"][0]
    rs["situations"] = {}
    for r in rs["readings"]:
        r["admission"]["distinguishing_models"] = {o: "pending" for o in r["admission"]["distinguishing_models"]}
    return raw, pending, sid


def elaborated(raw, document):
    from ve.readings_route import run_lean
    [row] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": raw, "document": document}])
    assert row["status"] == "ok" and "filled" in row, row
    return row


def test_generator_finds_separations_from_leans_filled_document():
    """Before any situation is recorded, `readings-elaborate` gives the filled document; the search over it finds a
    separating situation for each ordered pair, which Lean admits. With the 3.3 situation's base as a hint it finds
    exactly the 3.3 situation (witness `every`, `help_permitted` filled yes, probe `help_required(a, u)` true)."""
    from ve.readings_route import run_lean
    from ve.readings_s1 import record_situations, search
    raw, pending, sid = pending_fnd1()
    row = elaborated(raw, pending)
    found = search(raw, pending, "rs_1", filled=row)
    assert set(found) == {("every", "asks"), ("asks", "every")} and all(found.values())
    recorded = copy.deepcopy(pending)
    recorded["reading_sets"][0] = record_situations(pending["reading_sets"][0], found)
    [validated] = run_lean([{"id": "v", "kind": "readings-validate", "environment": raw, "document": recorded}])
    assert validated["status"] == "ok", validated
    assert all(p["pair"]["separated"] for p in validated["sets"][0]["pairs"])
    hinted = search(raw, pending, "rs_1", filled=row, hints=[base1([["a", "u"]])])
    assert hinted[("every", "asks")] == hinted[("asks", "every")] == (sid, entry(base1([["a", "u"]]), "every",
                                                                                    PROBE1, True))


def test_generator_witness_filter_reads_leans_fill_premises():
    """4.2: a witness's base must satisfy its `Fill_T`. F-ND1′'s base (the permission filled 'no' where reading
    `every`'s duty holds) fails it; the 3.3 base holds it; the other reading has no duty there either way."""
    from ve.model import FiniteModel
    from ve.readings_s1 import Decoded
    raw, pending, _ = pending_fnd1()
    row = elaborated(raw, pending)
    decoded = Decoded(raw, pending, row["filled"], row["fill_premises"])
    author = decoded.senv.author_environment()

    def model(permitted):
        return FiniteModel._decode(author, {**base1(permitted), "complete": True}, _defer_model_id=True)
    assert not decoded.fill_holds("rs_1", 0, model([]), [])
    assert decoded.fill_holds("rs_1", 0, model([["a", "u"]]), [])
    assert decoded.fill_holds("rs_1", 1, model([]), [])


def test_generator_without_leans_filled_document_has_no_frame():
    from ve.readings_s1 import search
    raw, pending, _ = pending_fnd1()
    with pytest.raises(CheckerUnavailable):
        search(raw, pending, "rs_1")


# ---------------------------------------------------------------------------------------------------------------
# The relay's binding of Lean's answer (build checklist 4): genuine rows, each field dropped, emptied, duplicated or
# retyped, and the answer bound to another request

def genuine(kind):
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import wire
    raw = env1()
    document, _ = doc1(raw)
    case = {"id": "readings-s1" if kind == "readings-validate" else "readings-s2", "kind": kind,
            "environment": wire(raw), "document": wire(document_wire([{"id": "u1"}], document["reading_sets"]))}
    [row] = run_lean([case])
    assert row["status"] == "ok"
    return case, row


def _set(path, value):
    def mutate(row):
        target = row
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


def _drop(path):
    def mutate(row):
        target = row
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]
    return mutate


def _apply(f):
    return f


COMPLETION_MUTATIONS = {
    "fill_premises dropped": _drop(["fill_premises"]),
    "filled dropped": _drop(["filled"]),
    "fill_premises empty": _set(["fill_premises"], []),
    "a reading's Fill_T twice": _apply(lambda row: row["fill_premises"].append(row["fill_premises"][0])),
    "another reading's index": _set(["fill_premises", 1, "index"], 2),
    "an index as a bool": _set(["fill_premises", 0, "index"], False),
    "a label of no declared pair": _set(["fill_premises", 0, "premises", 0, "label"],
                                        "unsaid:pair:help_permitted,help_required"),
    "a label retyped": _set(["fill_premises", 0, "premises", 0, "label"], 7),
    "the filled environment without a request predicate": _apply(
        lambda row: row["filled"]["environment"]["vocabulary"]["predicates"].pop("asks")),
    "an added regulated predicate": _apply(lambda row: row["filled"]["environment"]["vocabulary"]["predicates"]
                                           .update(extra_required=row["filled"]["environment"]["vocabulary"]
                                                   ["predicates"]["help_required"])),
    "an argument changed": _set(["filled", "environment", "vocabulary", "predicates", "asks", "arguments"],
                                ["agent", "user"]),
    "the units reordered": _apply(lambda row: row["filled"]["units"].reverse()),
    "a reading's unit lost": _apply(lambda row: row["filled"]["units"].pop(0)),
    "a unit's set version retyped": _set(["filled", "units", 0, "version"], True),
    "a generated unit named as a request unit": _set(["filled", "units", 2, "unit"], "u1"),
    "a generated unit named twice": _apply(lambda row: row["filled"]["units"].append(row["filled"]["units"][2])),
    "a generated unit not a rule": _set(["filled", "units", 2, "content"], {"assertion": ["top"]}),
    "a generated rule named otherwise": _set(["filled", "units", 3, "content", "norm", "name"], "other"),
    "a generated rule guarding no added table": _set(["filled", "units", 3, "content", "norm", "guard"],
                                                     ["binary", "asks", ["var", 0], ["var", 1]]),
    "filled as null": _set(["filled"], None),
}
ELABORATE_MUTATIONS = {
    "a finding on the superposed route": _set(["finding"],
                                               {"text": "ReadingsNotSuperposable: rs_1", "cause": "other"}),
    "a choice twice": _apply(lambda row: row["choices"].append(row["choices"][0])),
    "a choice out of range": _set(["choices", 0, 0, 1], 2),
    "a choice of another set": _set(["choices", 0, 0, 0], "rs_2"),
    "a count off by one": _set(["choice_count"], 3),
    "a count as a bool": _set(["choices_checked"], True),
    "the route": _set(["route"], "enumerated"),
}


@pytest.mark.parametrize("mutation", sorted(COMPLETION_MUTATIONS))
@pytest.mark.parametrize("kind", ["readings-validate", "readings-elaborate"])
def test_a_mutated_completion_answer_is_unavailable(kind, mutation, monkeypatch):
    _refused(kind, COMPLETION_MUTATIONS[mutation], monkeypatch)


@pytest.mark.parametrize("mutation", sorted(ELABORATE_MUTATIONS))
def test_a_mutated_elaborate_row_is_unavailable(mutation, monkeypatch):
    _refused("readings-elaborate", ELABORATE_MUTATIONS[mutation], monkeypatch)


def test_genuine_completion_answers_are_relayed():
    from ve.readings_route import _check, _completion_elaborate
    case, row = genuine("readings-validate")
    _check(row, case)
    case, row = genuine("readings-elaborate")
    assert _completion_elaborate(row, case) == {k: v for k, v in row.items() if k not in ("id", "status")}


def test_completion_fields_outside_the_completion_are_unavailable(monkeypatch):
    """`fill_premises` and `filled` belong to a document under the completion: on the same document with the
    profile off they are not Lean's answer to that request."""
    from ve.readings_route import _check
    from ve.readings_s1 import wire
    case, row = genuine("readings-validate")
    plain = {**case, "environment": wire(env1(("norms@0", "readings@1", "relational-fol@0"), "deny"))}
    with pytest.raises(CheckerUnavailable, match="invalid answer"):
        _check(row, plain)


def test_superposed_answer_retypes_each_field_and_rebinds_each_reference():
    """A genuine Lean answer is the seed. Every distinct object field path is retyped, including nested filled
    content and formulas; every request reference in the superposed row is also changed to an absent one."""
    from ve.readings_route import _completion_elaborate
    case, row = genuine("readings-elaborate")
    assert _completion_elaborate(row, case)["route"] == "superposed"

    paths = {}
    def visit(value, path=(), shape=()):
        if type(value) is dict:
            for key, child in value.items():
                marker = shape + (key,)
                paths.setdefault(marker, path + (key,))
                if key not in ("ast", "guard", "unless", "assertion"):
                    visit(child, path + (key,), marker)
        elif type(value) is list and value:
            visit(value[0], path + (0,), shape + ("[]",))
    visit(row)

    def change(path, replacement):
        bad = copy.deepcopy(row)
        parent = bad
        for segment in path[:-1]:
            parent = parent[segment]
        parent[path[-1]] = replacement
        with pytest.raises(CheckerUnavailable, match="invalid answer"):
            _completion_elaborate(bad, case)

    for path in paths.values():
        original = row
        for segment in path:
            original = original[segment]
        replacement = 7 if type(original) is bool else True
        change(path, replacement)

    references = {
        ("id",): "another-request", ("choices", 0, 0, 0): "absent-set",
        ("choices", 0, 0, 1): 99, ("choice_count",): 99, ("choices_checked",): 99,
        ("units", 0, "set"): "absent-set", ("units", 0, "index"): 99,
        ("units", 0, "position"): 99, ("units", 0, "version"): 99,
        ("names", 0, "set"): "absent-set", ("names", 0, "version"): 99,
        ("names", 0, "candidates", 0, "id"): "absent-reading",
        ("names", 0, "candidates", 0, "index"): 99,
        ("names", 0, "candidates", 0, "position"): 99,
        ("fill", 0, "label"): "unsaid:pair:absent,absent",
        ("fill_premises", 0, "set"): "absent-set",
        ("fill_premises", 0, "index"): 99,
        ("filled", "units", 0, "set"): "absent-set",
    }
    for path, replacement in references.items():
        change(path, replacement)
    bad = copy.deepcopy(row)
    bad["filled"]["environment"]["vocabulary"]["predicates"]["invented"] = {"arguments": ["agent", "user"]}
    with pytest.raises(CheckerUnavailable, match="invalid answer"):
        _completion_elaborate(bad, case)
    for field in ("choices", "units", "names", "fill_premises", "filled"):
        bad = copy.deepcopy(row)
        bad[field] = []
        with pytest.raises(CheckerUnavailable, match="invalid answer"):
            _completion_elaborate(bad, case)
    bad = copy.deepcopy(row)
    bad.update(choices=[], choice_count=0, choices_checked=0)
    with pytest.raises(CheckerUnavailable, match="invalid answer"):
        _completion_elaborate(bad, case)
    bad = copy.deepcopy(row)
    bad["units"].append(copy.deepcopy(bad["units"][0]))
    with pytest.raises(CheckerUnavailable, match="invalid answer"):
        _completion_elaborate(bad, case)


def _refused(kind, mutate, monkeypatch):
    from ve.readings_route import _check, _completion_elaborate
    case, row = genuine(kind)
    bad = copy.deepcopy(row)
    mutate(bad)
    check = _check if kind == "readings-validate" else _completion_elaborate
    with pytest.raises(CheckerUnavailable, match="invalid answer"):
        check(bad, case)


def test_filled_environment_is_typed_by_the_schema_and_bound_to_the_request():
    """Review B4 of rd-6b: `filled.environment` was any value. The generated schema alone now rejects every field of
    a genuine filled environment retyped, an extra field at every object of it, and a sort, constant, language or
    revision other than the request's; the client binds the profiles."""
    from ve.backends.service_schema import Invalid, check_row
    from ve.readings_route import _completion_elaborate
    for kind in ("readings-validate", "readings-elaborate"):
        case, row = genuine(kind)
        check_row("readings-route", row, case, 0)
        environment = row["filled"]["environment"]
        assert {"unsaid__help_required", "help_required"} <= set(environment["vocabulary"]["predicates"])

        paths, objects = [], []
        def visit(value, path):
            if type(value) is dict:
                objects.append(path)
                for key, child in value.items():
                    paths.append(path + (key,))
                    visit(child, path + (key,))
            elif type(value) is list:
                for k, child in enumerate(value):
                    paths.append(path + (k,))
                    visit(child, path + (k,))
        visit(environment, ())
        assert len(paths) > 30

        def refused(mutate):
            bad = copy.deepcopy(row)
            mutate(bad["filled"]["environment"])
            with pytest.raises(Invalid):
                check_row("readings-route", bad, case, 0)

        def at(env, path):
            for segment in path:
                env = env[segment]
            return env

        for path in paths:
            original = at(environment, path)
            def retype(env, path=path, original=original):
                at(env, path[:-1])[path[-1]] = 7 if type(original) is not int else "7"
            refused(retype)
        for path in objects:
            refused(lambda env, path=path: at(env, path).update(invented=[]))
        refused(lambda env: env["vocabulary"]["sorts"].update(extra={"description": "extra"}))
        refused(lambda env: env["vocabulary"]["constants"].update(c9={"sort": "agent", "description": "c"}))
        refused(lambda env: env.update(language="ve.core@0"))
        refused(lambda env: env.update(spec_revision="another"))
        refused(lambda env: env["vocabulary"]["predicates"]["help_required"]["regulated"].update(default="unspecified"))
        refused(lambda env: env["vocabulary"]["predicates"]["help_required"]["regulated"].update(role="duty"))

    case, row = genuine("readings-elaborate")
    for profiles in (["norm-defaults@0", "norms@0", "relational-fol@0"], ["relational-fol@0", "norms@0"],
                     ["norms@0", "relational-fol@0", "soft-norms@0"]):
        bad = copy.deepcopy(row)
        bad["filled"]["environment"]["profiles"] = profiles
        with pytest.raises(CheckerUnavailable, match="invalid answer"):
            _completion_elaborate(bad, case)
