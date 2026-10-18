"""Readings with their own vocabulary through `ve document` (docs/spec/readings-defaults.md 1.9, 1.10, 2.4, 4.5, 5
rows 16 to 18, 8.4; plan RD-4b).

A document whose sets carry `companion` is split by Lean into its main case and one case per companion set; each is
checked by itself and the document's meaning is their product. These tests drive the spec's fixtures F-C1 and F-C11
to F-C17 through `ve document check` and `ve document readings --conclusion … --sentence …`, and the cases that need
evidence withheld (F-C16, F-C17, SR4) through Lean's product answer on the request Python built. Every order of the
sentences and sets gets the same answer (review B1 of rd-4b), and the document's UNKNOWN is worded (2.4 item 3). Every
expected value is the spec's or Lean's own answer on the case written as a document of its own (`test_each_case_is_
answered_as_a_document_of_its_own`), and the standalone superposed route agrees on conflict status
(`test_each_case_keeps_its_standalone_conflict_status`); Python decides nothing here.
"""
from __future__ import annotations

import copy
import json

import pytest

from tests import lean_routes
from tests.test_document import unit, write_doc
from tests.test_readings_companions_lean import MAIN_UNIT, alone, environment, merged, regulated, set_a, set_b
from tests.test_readings_nd_lean import doc2, env2
from ve.document import _environment, check_document, load_document, main, render_document
from ve.errors import CheckerUnavailable, VEError
from ve.readings import s1_content_meaning_id
from ve.readings_components import Components

TEXTS = {"u0": "Every agent must greet.\n", "u_a": "Every agent must help each user.\n",
         "u_b": "Every agent must warn each user.\n", "u2": "Every act must be done if it may be tried.\n",
         "x0": "Nothing may be done.\n"}
# F-C17's query, ALL on F-ND1 (spec 8.4): the conclusion of the first companion set's readings.
HELP_PERMITTED = ["forall", "agent", ["forall", "user", ["implies",
                                                         ["binary", "help_required", ["var", 1], ["var", 0]],
                                                         ["binary", "help_permitted", ["var", 1], ["var", 0]]]]]
# F-ND1's query, SOME in the first companion set.
HELP = ["forall", "agent", ["forall", "user", ["binary", "help_required", ["var", 1], ["var", 0]]]]
# Refuted wherever an agent exists: NONE in any component with agents (typed by its sort alone).
NO_AGENT = ["forall", "agent", ["bottom"]]
RESERVED = ("unsaid__", "unsaid--")


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def env_main():
    """F-C1's main frame: one fixed rule, CONFLICT-FREE with its pair condition (its permission unspecified)."""
    return environment({
        "greet_required": {"arguments": ["agent"], "description": "obligation",
                           "regulated": regulated("obligation", "unspecified", "{0} greet",
                                                  permission="greet_permitted")},
        "greet_permitted": {"arguments": ["agent"], "description": "permission",
                            "regulated": regulated("permission", "unspecified", "{0} greet")}}, ("agent",))


def write(tmp_path, raw, document, *, name="sample", **meta):
    """The document as a `ve-document@1` file, one sentence per unit; a reading without its own vocabulary gets its
    meaning id over the main environment (W2's), a companion reading keeps the one over its own (Lean checks it)."""
    env = _environment(raw)
    document = copy.deepcopy(document)
    for reading_set in document["reading_sets"]:
        for r in reading_set["readings"]:
            if "companion" not in r and r["content"] is not None:
                r["meaning_id"] = s1_content_meaning_id(env, reading_set["id"], r)
    units, text = [], b""
    for u in document["units"]:
        sentence = TEXTS[u["id"]].encode()
        units.append(unit(u["id"], len(text), len(text) + len(sentence), "norm", "specified", u.get("content")))
        text += sentence
    folder = tmp_path / name
    folder.mkdir(exist_ok=True)
    return write_doc(folder, text, units, environment_json=raw, reading_sets=document["reading_sets"],
                     **{k: v for k, v in meta.items() if v})


def fc1(tmp_path, **meta):
    a, _, _ = set_a()
    b, _, _ = set_b()
    document = {"units": [MAIN_UNIT, {"id": "u_a"}, {"id": "u_b"}], "reading_sets": [a, b]}
    return write(tmp_path, env_main(), document, **meta)


def readings(path):
    return check_document(path)["readings"]


def query(capsys, path, conclusion, *args):
    conclusion_path = path.parent / "conclusion.json"
    conclusion_path.write_text(json.dumps(conclusion))
    assert main(["readings", str(path), "--conclusion", str(conclusion_path), *args]) == 0
    return json.loads(capsys.readouterr().out)


def shown(lines):
    """No English line names a filled table or a generated rule (spec 2.5)."""
    assert lines and not [line for line in lines if any(prefix in line for prefix in RESERVED)], lines
    return lines


# ---------------------------------------------------------------------------------------------------------------
# F-C1 through `ve document check`

def test_fc1_check_three_components_conflict_free_with_a_model(tmp_path):
    report = check_document(fc1(tmp_path))
    rd = report["readings"]
    assert rd["route"] == "components"
    assert [(c["component"], c["route"], c["units"]) for c in rd["components"]] == [
        ("main", "w2", ["u0"]), ("rs_a", "enumerated", ["u_a"]), ("rs_b", "enumerated", ["u_b"])]
    assert rd["conflict"]["status"] == rd["status"] == "CONFLICT-FREE"
    assert [c["status"] for c in rd["conflict"]["components"]] == ["CONFLICT-FREE"] * 3
    assert report["premises"]["status"] == "model"
    assert [c["status"] for c in report["premises"]["components"]] == ["model"] * 3
    # F-C16 (→): every unit with content is Lean-decided
    assert rd["decided_units"] == ["u0", "u_a", "u_b"]
    # each companion component is separated as F-ND1 is
    assert [s["set"] for s in rd["sets"]] == ["rs_a", "rs_b"] and rd["separations"]["outcome"] == 2
    english = shown(rd["english"])
    assert english.count("Each open sentence below was checked by itself, under each of its readings.") == 2
    for n in (2, 3):
        alone_line = (f"Sentence {n} was checked by itself, with the terms its readings declare; VE did not check it "
                      "together with the other sentences.")
        assert english.count(alone_line) == 2
        # E30 replaces E26 for a companion component (2.4 item 1)
        assert f"Under every reading of sentence {n}, no two rules on the same act contradict each other." in english
    assert not any(line.startswith("Under every reading of the open sentence") for line in english)


def test_each_case_is_answered_as_a_document_of_its_own(tmp_path):
    """Each component's own answer inside the product is Lean's answer on that case written as a document of its
    own (F-C1, "per-component answers as F-ND1's")."""
    from ve.readings_components import context
    from tests.test_readings_nd_lean import one
    doc = load_document(fc1(tmp_path))
    route = context(doc)
    row = route.conflict_answer()
    case = route.requests[id(row)]
    a, _, ca = set_a()
    for name, s, companion, unit_id in (("rs_a", a, ca, "u_a"),):
        evidence = [{k: v for k, v in e.items() if k != "component"} for e in case["evidence"]
                    if e["component"] == name]
        own = one("ve_readings_route", "readings-verdicts", merged(companion), alone(s, [{"id": unit_id}]),
                  question="conflict", evidence=evidence)
        assert route.sub(row, name) == own


def test_each_case_keeps_its_standalone_conflict_status(tmp_path):
    """The product's enumerated component and its standalone superposed route agree on conflict status."""
    from ve.readings_components import context
    from ve.readings_verdicts import context as standalone_context
    doc = load_document(fc1(tmp_path))
    route = context(doc)
    row = route.conflict_answer()
    a, _, ca = set_a()
    for name, s, companion, unit_id in (("rs_a", a, ca, "u_a"),):
        own_path = write(tmp_path, merged(companion), alone(s, [{"id": unit_id}]), name="own")
        own = standalone_context(load_document(own_path)).conflict_answer()
        assert route.sub(row, name)["result"]["status"] == own["result"]["status"]


def test_fc1_render_reads_each_set_in_its_component(tmp_path):
    lines = shown(render_document(fc1(tmp_path)).splitlines())
    assert sum(line.startswith("These two readings differ here: ") for line in lines) == 2


# ---------------------------------------------------------------------------------------------------------------
# A query typed in one component (4.5; 5 rows 16 to 18; F-C13, F-C14)

def test_a_query_typed_in_one_component_is_all_with_e30(tmp_path, capsys):
    data = query(capsys, fc1(tmp_path), HELP_PERMITTED)
    assert (data["verdict"], data["component"], data["sentence"]) == ("ALL", "rs_a", None)
    [own] = [c for c in data["components"] if c["component"] == "rs_a"]
    assert own["result"]["verdict"] == "ALL" and own["question"] == "query"
    assert [c["question"] for c in data["components"]] == ["premises", "query", "premises"]
    english = shown(data["english"])
    assert english[:3] == [
        "Each open sentence below was checked by itself, under each of its readings.",
        "Sentence 2 was checked by itself, with the terms its readings declare; VE did not check it together with the "
        "other sentences.",
        "Under every reading of sentence 2, the conclusion follows: *For every agent, for every user that that "
        "agent must help, that agent may help that user.*"]


def test_fc14_conclusion_typing(tmp_path, capsys):
    path = fc1(tmp_path)
    for conclusion in (["forall", "agent", ["unary", "zzz", ["var", 0]]], ["bottom"]):
        with pytest.raises(VEError) as caught:
            query(capsys, path, conclusion)
        if conclusion == ["bottom"]:
            # ⊥ uses no term: it fits every sentence
            assert caught.value.message == ("InvalidInput: the conclusion's terms fit sentences 1, 2, 3; name one "
                                            "with --sentence")
        else:
            assert caught.value.message == "InvalidInput: the conclusion uses terms of no sentence checked by itself"
    with pytest.raises(VEError, match="^InvalidInput: the conclusion's terms fit sentences 1, 2, 3; name one with "
                                      "--sentence$"):
        query(capsys, path, NO_AGENT)
    assert query(capsys, path, NO_AGENT, "--sentence", "u_b")["component"] == "rs_b"
    assert query(capsys, path, NO_AGENT, "--sentence", "u0")["component"] == "main"
    assert query(capsys, path, HELP)["component"] == "rs_a"
    with pytest.raises(VEError, match="^InvalidInput: the conclusion's terms do not fit sentence 3$"):
        query(capsys, path, HELP, "--sentence", "u_b")
    with pytest.raises(VEError, match="^InvalidInput: --sentence names u9, which is not a sentence of the "
                                      "document$"):
        query(capsys, path, HELP, "--sentence", "u9")


def test_fc13_under_names_sets_of_the_query_s_component_only(tmp_path, capsys):
    path = fc1(tmp_path)
    with pytest.raises(VEError, match="^InvalidInput: --under names rs_b, which is not a reading set of the "
                                      "sentence the conclusion is about$"):
        query(capsys, path, HELP, "--under", "rs_b:0")
    data = query(capsys, path, HELP, "--under", "rs_a:0")
    assert (data["verdict"], data["component"]) == ("ALL", "rs_a")
    [own] = [c for c in data["components"] if c["component"] == "rs_a"]
    assert own["result"]["assumed"] == [["rs_a", 0]]
    assert query(capsys, path, HELP, "--under", "rs_a:1")["verdict"] == "NONE"
    assert query(capsys, path, HELP)["verdict"] == "SOME"


# ---------------------------------------------------------------------------------------------------------------
# F-C11, F-C12: the split contract (A3)

def test_fc11_a_narrowing_is_listed_under_its_component_only(tmp_path):
    narrowing = {"id": "n1", "set": "rs_a", "version": 1, "keeps": ["every"], "by": "w",
                 "reason_spans": ["u0"]}
    rd = readings(fc1(tmp_path, narrowings=[narrowing]))
    by = {c["component"]: c for c in rd["components"]}
    assert by["rs_a"]["conflict"]["restrictions"] == ["narrowing:n1"]
    assert by["rs_b"]["conflict"]["restrictions"] == [] and by["main"]["conflict"].get("restrictions", []) == []
    assert [c["choice"] for c in by["rs_a"]["conflict"]["choices"]] == [[["rs_a", 0]]]


def test_fc12_an_unseparated_set_stays_in_main_with_w2_s_unknown(tmp_path):
    a, _, _ = set_a()
    b, _, _ = set_b()
    for r in b["readings"]:
        r.pop("companion")
        r["content"] = None
    from ve.model import FiniteModel
    model = {"complete": True, "domains": {"agent": ["a"]}, "constants": {},
             "relations": {"greet_required": [], "greet_permitted": []}}
    model_id = FiniteModel.from_dict(_environment(env_main()), model).model_id
    b["models"] = {model_id: model}
    for r in b["readings"]:
        r["admission"]["distinguishing_models"] = {other["id"]: model_id for other in b["readings"]
                                                 if other["id"] != r["id"]}
    b["situations"] = {}
    document = {"units": [MAIN_UNIT, {"id": "u_a"}, {"id": "u_b"}], "reading_sets": [a, b]}
    rd = readings(write(tmp_path, env_main(), document))
    assert [c["component"] for c in rd["components"]] == ["main", "rs_a"]
    [main_] = [c for c in rd["components"] if c["component"] == "main"]
    assert (main_["route"], main_["unchecked"]) == ("w2", [{"set": "rs_b", "unit": "u_b", "status": "UNKNOWN"}])
    assert rd["conflict"]["status"] == "CONFLICT-FREE"
    # the set left on W2 is never decided; everything else is as on F-C1
    assert rd["decided_units"] == ["u0", "u_a"]


# ---------------------------------------------------------------------------------------------------------------
# F-C15, F-C17: the product gate (`foldK_none`'s `OthersSettled`, `foldK_all`'s `ho`)

def test_fc15_none_needs_every_other_component_consistent(tmp_path, capsys):
    path = fc1(tmp_path)
    data = query(capsys, path, NO_AGENT, "--sentence", "u_a")
    assert (data["verdict"], data["component"]) == ("NONE", "rs_a")
    # the second component's reading 1 asserts ⊥: one of its readings has no model
    from tests.test_readings_components_lean import absurd_b
    a, _, _ = set_a()
    document = {"units": [MAIN_UNIT, {"id": "u_a"}, {"id": "u_b"}], "reading_sets": [a, absurd_b()]}
    path = write(tmp_path, env_main(), document, name="absurd")
    data = query(capsys, path, NO_AGENT, "--sentence", "u_a")
    assert data["verdict"] == "UNKNOWN" and data["reason"] == "another sentence's readings are not all consistent"
    [own] = [c for c in data["components"] if c["component"] == "rs_a"]
    assert own["result"]["verdict"] == "NONE"
    assert data["english"] == []


def fc17(tmp_path):
    a, _, _ = set_a()
    b, _, _ = set_b()
    nd2, _ = doc2(env2())
    nd2["units"][0]["id"] = "x0"
    document = {"units": [nd2["units"][0], nd2["units"][1], {"id": "u_a"}, {"id": "u_b"}],
                "reading_sets": [*nd2["reading_sets"], a, b]}
    return write(tmp_path, env2(), document, name="fc17")


def test_fc17_all_is_gated_on_every_other_component(tmp_path, capsys):
    data = query(capsys, fc17(tmp_path), HELP_PERMITTED, "--sentence", "u_a")
    assert (data["verdict"], data["status"], data["conflict_status"]) == (
        "UNKNOWN", "UNKNOWN (conflict status: CONFLICT)", "CONFLICT")
    assert (data["choice_component"], data["choice"], data["choice_text"]) == ("main", [["rs_2", 0]], "rs_2@1:0")
    [own] = [c for c in data["components"] if c["component"] == "rs_a"]
    assert own["result"]["verdict"] == "ALL"
    # 2.4 item 3 (review B3 of rd-4b): the document's UNKNOWN is worded, naming the other sentence's choice by E12;
    # under its CONFLICT that choice's checked witness (R4), as a CONFLICT is worded.
    assert shown(data["english"]) == [
        "Each open sentence below was checked by itself, under each of its readings.",
        "Read sentence 2 as *Every act must be done, if that act may be tried*: two rules contradict each other here: "
        "e0 is an act. Here the text does not say whether e0 may be tried; this situation answers 'yes'. Here the "
        "text does not say whether e0 must be done; this situation answers 'no'."]
    assert query(capsys, fc1(tmp_path), HELP_PERMITTED, "--sentence", "u_a")["verdict"] == "ALL"


# ---------------------------------------------------------------------------------------------------------------
# Evidence withheld (F-C16 ←, F-C17's second case): Lean's product answer on the request Python built, less a piece

def _withheld(path, question, drop, **fields):
    from tests.test_readings_nd_lean import run
    from ve.readings_components import context
    doc = load_document(path)
    route = context(doc)
    route.premises_answer()
    case = route._case(question, **fields)
    case["evidence"] = [e for e in case["evidence"] if not drop(e)]
    [row] = run("ve_readings_route", [case])
    assert row["status"] == "ok", row
    route.check_product(row, case)
    return row


def test_fc16_a_choice_without_evidence_leaves_its_component_undecided(tmp_path):
    row = _withheld(fc1(tmp_path), "premises", lambda e: e["component"] == "rs_b" and e["choice"] == [["rs_b", 1]])
    assert row["decided_units"] == ["u0", "u_a"]
    row = _withheld(fc1(tmp_path), "premises", lambda e: False)
    assert row["decided_units"] == ["u0", "u_a", "u_b"]


def test_fc17_main_conflict_evidence_missing(tmp_path):
    from ve.readings_components import context, english
    path = fc17(tmp_path)
    row = _withheld(path, "query", lambda e: e["component"] == "main",
                    conclusion=HELP_PERMITTED, sentence="u_a", premises=[])
    result = row["result"]
    assert (result["verdict"], result["status"], result["choice_text"]) == (
        "UNKNOWN", "UNKNOWN (conflict status: UNKNOWN)", "rs_2@1:0")
    # 2.4 item 3: the uncertified conflict status under the other sentence's choice, by E12 with R8
    assert [(e["component"], e["line"]["frame"], e["line"]["result"], e["line"]["readings"]) for e in row["english"]] \
        == [(None, "E32", None, []), ("main", "E12", "R8", [["rs_2", 0]])]
    doc = load_document(path)
    assert shown(english(doc, context(doc), row)) == [
        "Each open sentence below was checked by itself, under each of its readings.",
        "Read sentence 2 as *Every act must be done, if that act may be tried*: VE could not check whether two rules "
        "on the same act contradict each other."]


def test_sr4_conflict_under_one_choice_and_unknown_under_the_other_is_not_decided(tmp_path):
    """1.10, SR4 (8.4; review B4 of rd-4b): the main case of F-C17 is CONFLICT under rs_2's reading 0 and
    CONFLICT-FREE under reading 1, so rs_2's unit is Lean-decided; with reading 1's evidence withheld its rows are
    CONFLICT and UNKNOWN, which a folded status (CONFLICT) would hide, and the unit is not decided. The computed
    rows of 8.4 are `#guard`s in lean/VE/Readings/ComponentsExamples.lean."""
    path = fc17(tmp_path)
    row = _withheld(path, "premises", lambda e: False)
    main_ = Components.sub(row, "main")
    assert [e["conflict"] for e in main_["per_choice"]] == ["CONFLICT", "CONFLICT-FREE"]
    assert "u2" in row["decided_units"]
    row = _withheld(path, "premises", lambda e: e["component"] == "main" and e["choice"] == [["rs_2", 1]])
    main_ = Components.sub(row, "main")
    assert [e["conflict"] for e in main_["per_choice"]] == ["CONFLICT", "UNKNOWN"]
    assert "u2" not in row["decided_units"]
    assert row["decided_units"] == [u for u in ["x0", "u2", "u_a", "u_b"] if u in row["decided_units"]]


# ---------------------------------------------------------------------------------------------------------------
# Sentence order (review B1 of rd-4b): Lean lists every unit of the document in the document's order, whichever
# component holds it, and the components in the order of their sets; every entry point answers any order alike

def _ordered(tmp_path, name, units, sets, raw=None):
    return write(tmp_path, raw or env_main(), {"units": units, "reading_sets": sets}, name=name)


def _verdicts(report):
    rd = report["readings"]
    return (rd["status"], rd["conflict"]["status"], report["premises"]["status"],
            sorted((c["component"], c["status"]) for c in rd["conflict"]["components"]),
            sorted((c["component"], c["route"], tuple(c["units"])) for c in rd["components"]))


def test_every_order_of_sentences_and_sets_gets_the_same_answer(tmp_path, capsys):
    from itertools import permutations
    a, _, _ = set_a()
    b, _, _ = set_b()
    base = check_document(_ordered(tmp_path, "base", [MAIN_UNIT, {"id": "u_a"}, {"id": "u_b"}], [a, b]))
    for k, units in enumerate(permutations([MAIN_UNIT, {"id": "u_a"}, {"id": "u_b"}])):
        for sets in ([a, b], [b, a]):
            path = _ordered(tmp_path, f"order{k}{sets[0]['id']}", list(units), sets)
            report = check_document(path)
            rd = report["readings"]
            assert _verdicts(report) == _verdicts(base)
            ids = [u["id"] for u in units]
            # the decided units in the document's order, the components main first, then in their sets' order
            assert rd["decided_units"] == [u for u in ids if u in base["readings"]["decided_units"]]
            assert [c["component"] for c in rd["components"]] == ["main", *(x["id"] for x in sets)]
            shown(rd["english"])
    # the order of the finding: a companion sentence before the main one, through readings and render too
    path = _ordered(tmp_path, "finding", [{"id": "u_a"}, MAIN_UNIT, {"id": "u_b"}], [a, b])
    assert check_document(path)["readings"]["decided_units"] == ["u_a", "u0", "u_b"]
    data = query(capsys, path, HELP_PERMITTED)
    assert (data["verdict"], data["component"]) == ("ALL", "rs_a")
    assert data["decided_units"] == ["u_a", "u0", "u_b"]
    assert shown(data["english"])[2].startswith("Under every reading of sentence 1, the conclusion follows")
    assert sum(line.startswith("These two readings differ here: ") for line in
               shown(render_document(path).splitlines())) == 2


def test_fc17_with_its_companions_first_gets_the_same_answer(tmp_path, capsys):
    a, _, _ = set_a()
    b, _, _ = set_b()
    nd2, _ = doc2(env2())
    nd2["units"][0]["id"] = "x0"
    units = [{"id": "u_a"}, nd2["units"][0], {"id": "u_b"}, nd2["units"][1]]
    path = write(tmp_path, env2(), {"units": units, "reading_sets": [b, *nd2["reading_sets"], a]}, name="fc17r")
    rd = check_document(path)["readings"]
    assert rd["conflict"]["status"] == "CONFLICT"
    assert [c["component"] for c in rd["components"]] == ["main", "rs_b", "rs_a"]
    assert rd["decided_units"] == [u["id"] for u in units if u["id"] in rd["decided_units"]]
    data = query(capsys, path, HELP_PERMITTED, "--sentence", "u_a")
    assert (data["verdict"], data["choice_component"], data["choice"]) == ("UNKNOWN", "main", [["rs_2", 0]])
    assert shown(data["english"])[1].startswith("Read sentence 4 as *Every act must be done, if that act may be "
                                                "tried*: two rules contradict each other here: ")


def test_without_companions_nothing_changes(tmp_path):
    """Conservativity (4.6): no component product; RD-6b still chooses the filled superposed route."""
    from tests.test_readings_nd_document import fnd1
    doc = load_document(fnd1(tmp_path))
    assert doc["readings_components"] is None and doc["readings_s2"]["route"] == "superposed"


def test_a_component_outside_the_completion_is_refused(tmp_path):
    raw = env_main()
    raw["profiles"] = [p for p in raw["profiles"] if p != "norm-defaults@0"]
    for decl in raw["vocabulary"]["predicates"].values():
        decl["regulated"]["default"] = "deny"
    a, _, _ = set_a()
    document = {"units": [MAIN_UNIT, {"id": "u_a"}], "reading_sets": [a]}
    with pytest.raises(VEError, match="^UnsupportedProfile: a document with readings that carry their own vocabulary "
                                      "is checked as a product of its sentences only under norm-defaults@0 on the "
                                      "norms chain$"):
        load_document(write(tmp_path, raw, document))


def test_operational_failures_are_unavailable(tmp_path, monkeypatch):
    """A product answer that does not bind is `CheckerUnavailable`, never a verdict (the fuzz is in
    test_readings_components_lean.py)."""
    from ve import readings_route
    doc = load_document(fc1(tmp_path))
    from ve.readings_components import context
    route = context(doc)
    real = readings_route.run_lean

    def forged(cases, **kw):
        rows = real(cases, **kw)
        for row in rows:
            if row.get("route") == "components":
                row["decided_units"] = row["decided_units"] + ["u9"]
        return rows
    monkeypatch.setattr(readings_route, "run_lean", forged)
    with pytest.raises(CheckerUnavailable):
        route.conflict_answer()
