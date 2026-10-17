"""Readings under the soft completion through `ve document` (docs/spec/rd-9-soft-chain.md 3.8 and 8.3; plan SC-8).

F-SD1 written as a document goes through `ve document load`, `check`, `render` and `readings --conclusion`. Lean's
readings route admits it, separates its readings on filled sides and answers every verdict (`readings-verdicts`
under the soft completion, SC-5); Python builds no `fill`, `X` or `Coh_T`: its untrusted generators propose
packages, certificates and models over the formulas of Lean's layered row for each choice, and Lean checks them.
Before SC-8 the document was refused ("norm-defaults@0 documents on the soft and rights routes await the Lean
route"); the refusal now names the rights route only (3.11 row 7).
"""
from __future__ import annotations

import copy
import json
import re

import pytest

from tests import lean_routes
from tests.test_readings_s1_document import default, s1_document, strict
from tests.test_readings_s1_lean import entry, env_rights, situation_id
from tests.test_readings_sd_lean import env_sd, sigma_default
from ve.document import check_document, load_document, main, render_document
from ve.errors import UnsupportedProfile

QUERY = ["forall", "agent", ["forall", "user", ["binary", "avoid_required", ["var", 1], ["var", 0]]]]
GAP = re.compile(r" Here the text does not say whether [^;]+; this situation answers '(yes|no)'\.")
RESERVED = ("unsaid__", "unsaid--", "soft__")  # what no English line may show (spec 2.5)
MUST = "*Every agent must avoid deceiving each user.*"
SHOULD = "*Every agent should avoid deceiving each user.*"


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def recorded(raw, sigma):
    """The set with 8.1's σ recorded for both pairs (the generator's own run is `test_fsd1_generator_*`)."""
    sid = situation_id(raw, sigma)

    def situations(reading_set):
        reading_set = copy.deepcopy(reading_set)
        reading_set["situations"] = {sid: sigma}
        for r in reading_set["readings"]:
            r["admission"]["distinguishing_models"] = {o["id"]: sid for o in reading_set["readings"]
                                                       if o["id"] != r["id"]}
        return reading_set
    return situations


def fsd1(tmp_path, sigma=None, raw=None):
    raw = raw or env_sd()
    return s1_document(tmp_path, [strict(), default()], raw=raw, situations=recorded(raw, sigma or sigma_default()))


def shown(lines):
    """No English line names a filled table, a decision table or a generated rule (spec 2.5)."""
    assert lines and not [line for line in lines if any(prefix in line for prefix in RESERVED)], lines
    return lines


def query(tmp_path, capsys, path, *under):
    conclusion = tmp_path / "conclusion.json"
    conclusion.write_text(json.dumps(QUERY))
    assert main(["readings", str(path), "--conclusion", str(conclusion),
                 *[arg for set_index in under for arg in ("--under", set_index)]]) == 0
    return json.loads(capsys.readouterr().out)


def test_fsd1_load_takes_the_enumerated_route_of_the_soft_completion(tmp_path):
    doc = load_document(fsd1(tmp_path))
    s2 = doc["readings_s2"]
    assert (s2["route"], s2["finding"], s2["choices"]) == (
        "enumerated", {"text": "ReadingsNotSuperposable: rs1", "cause": "the unspecified completion"},
        [[["rs1", 0]], [["rs1", 1]]])
    assert s2["soft_premises"] == [{"set": "rs1", "index": 0, "premises": []},
                                   {"set": "rs1", "index": 1, "premises": []}]
    # no W1 norm-defaults container over soft units (3.8): the completion is Lean's readings route's
    assert doc["norm_defaults"] is None


def test_fsd1_check_folds_leans_verdicts(tmp_path):
    report = check_document(fsd1(tmp_path))
    readings = report["readings"]
    assert readings["route"] == "enumerated" and readings["choices_checked"] == 2
    assert readings["conflict"]["status"] == "CONFLICT-FREE"
    assert [c["status"] for c in readings["conflict"]["choices"]] == ["CONFLICT-FREE", "CONFLICT-FREE"]
    assert report["premises"]["status"] == "model"
    english = shown(readings["english"])
    assert english[:2] == ["The readings of sentence 1 were checked one way at a time, not together.",
                           "Under every reading of the open sentence, no two rules on the same act contradict each "
                           "other."]
    [pair] = readings["sets"][0]["pairs"]
    assert pair["wording"] == "E14"


def test_fsd1_render_has_one_gap_sentence_on_the_separation_line(tmp_path):
    """8.3 F-SD1 and F-SD10: E14 with exactly one filled-gap sentence, after the supposition and before "Under (1)"
    (2.2 item 1)."""
    lines = shown(render_document(fsd1(tmp_path)).splitlines())
    [line] = [line for line in lines if line.startswith("This sentence says *shall*.")]
    assert len(GAP.findall(line)) == 1
    assert ("suppose the decider decides the exception applies to a and u. Here the text does not say whether a must "
            "avoid deceiving u; this situation answers 'no'. Under (1) a still must.") in line


def test_fsd1_readings_conclusion_some_all_none(tmp_path, capsys):
    """8.3 F-SD1.verdicts through the CLI: SOME (the strict reading proved, the default one refuted where the
    decider excepts `(a, u)` and the gap is filled 'no'); ALL under `rs1:0`; NONE under `rs1:1`."""
    path = fsd1(tmp_path)
    data = query(tmp_path, capsys, path)
    assert data["verdict"] == "SOME", data
    assert (data["proof"]["choice"], data["countermodel"]["choice"]) == ([["rs1", 0]], [["rs1", 1]])
    follows, fails = shown(data["english"])
    assert follows == ("Read sentence 1 as *must*: the conclusion follows: *For every agent, for every user, that "
                       "agent must avoid deceiving that user.*")
    # the countermodel's decision is the choice's own table, worded by its key (`side`, plan SC-8), then its gap
    assert fails == ("Read sentence 1 as *should*: the conclusion does not follow. It fails here: e0 is an agent; "
                     "e0 is a user; suppose the decider decides the exception applies to e0 and e0. Here the text "
                     "does not say whether e0 must avoid deceiving e0; this situation answers 'no'.")
    assert query(tmp_path, capsys, path, "rs1:0")["verdict"] == "ALL"
    under = query(tmp_path, capsys, path, "rs1:1")
    assert (under["verdict"], under["assumed"]) == ("NONE", [["rs1", 1]])
    assert shown(under["english"]) == [fails]


def test_the_rights_route_keeps_the_narrowed_refusal(tmp_path):
    """3.11 row 7: `ve document` on the rights route under `norm-defaults@0` refuses with the narrowed text."""
    raw = env_rights()
    raw["profiles"] = sorted({*raw["profiles"], "norm-defaults@0"})
    from tests.test_document import unit, write_doc
    text = b"Persons may not be arrested arbitrarily.\n"
    path = write_doc(tmp_path, text, [unit("u1", 0, len(text), "norm", "specified")], environment_json=raw)
    with pytest.raises(UnsupportedProfile, match="^UnsupportedProfile: norm-defaults@0 documents on the rights "
                                                 "route await the Lean route$"):
        load_document(path)


# The generator under the soft completion (plan SC-8): the search proposes the witness's decision tables and the
# shared filling over Lean's `filled` frame, each witness filtered by its reading's `soft_premises` and `Fill_T`.

def _pending(raw, document):
    pending = copy.deepcopy(document)
    for rs in pending["reading_sets"]:
        rs["situations"] = {}
        for r in rs["readings"]:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in rs["readings"]
                                                       if o["id"] != r["id"]}
    return pending


def _run(kind, raw, document):
    from ve.readings_route import run_lean
    [row] = run_lean([{"id": kind, "kind": kind, "environment": raw, "document": document}])
    assert row["status"] == "ok", row
    return row


def test_fsd1_generator_finds_the_separating_situation():
    """F-SD1 before any situation is recorded: `readings-elaborate` gives the filled frame; the search finds 8.1's
    σ (the default reading excepted at `(a, u)`, the gap filled 'no') for both ordered pairs, and Lean admits it."""
    from tests.test_readings_s1_lean import k1_document
    from ve.readings_s1 import record_situations, search
    raw = env_sd()
    document, sid = k1_document(raw, situation=sigma_default())
    pending = _pending(raw, document)
    found = search(raw, pending, "rs1", filled=_run("readings-elaborate", raw, pending))
    assert found == {("strict", "default"): (sid, sigma_default()), ("default", "strict"): (sid, sigma_default())}
    recorded_document = copy.deepcopy(pending)
    recorded_document["reading_sets"][0] = record_situations(pending["reading_sets"][0], found)
    validated = _run("readings-validate", raw, recorded_document)
    assert all(p["pair"]["separated"] for p in validated["sets"][0]["pairs"])


def test_generator_records_not_found_where_a_guard_reads_a_gap():
    """Recorded as not found (plan SC-8: "found or not found"): `coherent`'s readings differ only where `y_permitted`,
    unspecified, is filled yes. Python models no `F_p` (no filled readings document exists on the soft chain, 4.1), so
    its search reads `y` as its deny placeholder and finds no separation; Lean admits the situation written by hand."""
    from tests.test_readings_sd_lean import doc4, env4
    from ve.readings_s1 import search
    raw = env4()
    raw["vocabulary"]["predicates"]["x_permitted"]["regulated"]["default"] = "allow"
    pending = _pending(raw, doc4(raw))
    found = search(raw, pending, "rs1", filled=_run("readings-elaborate", raw, pending))
    assert found == {("strict", "default"): None, ("default", "strict"): None}
    base = {"domains": {"assistant": ["a"]}, "constants": {}, "relations": {"c": [], "unsaid__y_permitted": [["a"]]}}
    sigma = entry(base, "default", {"outcome": {"predicate": "x_required", "tuple": ["a"]}}, False,
                  decisions=[{"key": {"excepted": "must-x"}, "tuples": [["a"]]}])
    written = copy.deepcopy(pending)
    written["reading_sets"][0] = recorded(raw, sigma)(written["reading_sets"][0])
    pairs = _run("readings-validate", raw, written)["sets"][0]["pairs"]
    assert [p["pair"]["gaps"] for p in pairs] == [[["y_permitted", ["a"], True]]] * 2
    assert all(p["pair"]["separated"] for p in pairs)


def test_a_verdict_on_a_soft_label_is_unavailable_until_its_sentence_exists(tmp_path):
    """8.3 F-SD4 through `ve document check`: Lean answers CONFLICT-FREE `conditional_on` the coherence premise, and
    Python's packages over `X` are accepted; Lean's plan gives the soft label an `unworded` line (no renderer words a
    coherence premise yet: spec 2.1's weighing-point sentence is not among the existing renderers), so the answer is
    unavailable, never shown without its condition."""
    from tests.test_readings_s1_lean import norm
    from tests.test_readings_sd_lean import env4
    from ve.errors import CheckerUnavailable
    raw = env4()
    raw["vocabulary"]["predicates"]["x_permitted"]["regulated"]["default"] = "allow"
    y = ["unary", "y_permitted", ["var", 0]]
    excepted = norm("must-x", "x_required", True, "default", guard=y)
    excepted["norm"]["exception"]["sufficient"] = [["unary", "c", ["var", 0]]]
    base = {"domains": {"assistant": ["a"]}, "constants": {}, "relations": {"c": [], "unsaid__y_permitted": [["a"]]}}
    sigma = entry(base, "default", {"outcome": {"predicate": "x_required", "tuple": ["a"]}}, False,
                  decisions=[{"key": {"excepted": "must-x"}, "tuples": [["a"]]}])
    path = s1_document(tmp_path, [("strict", norm("must-x", "x_required", True, guard=y), "norm"),
                                  ("default", excepted, "norm")], raw=raw,
                       fixed=[("u0", norm("need-not-x", "x_required", False, "default"))],
                       situations=recorded(raw, sigma), source=b"Assistants shall do x when they may do y.",
                       word=(11, 16))
    with pytest.raises(CheckerUnavailable, match="unknown frame unworded"):
        check_document(path)
