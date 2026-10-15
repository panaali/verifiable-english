"""`CE4`, the constitution's four sets, under the soft completion (docs/spec/rd-9-soft-chain-PLAN.md 5.2: C1 to C8;
plan SC-4, SC-5 and SC-8; rd-9-looprecheck2 A2).

`CE4` is built from the pilot's pinned translation (`tests/ce4.py`: run 20261010T1800Z, commit 76922d6c), never
retyped. C1 to C4 and C1.4 go through Lean's readings route (`readings-validate`, `readings-choice`) with spec 8.2's
σ; C1 to C8 go through `ve document` (`load`, `check`, `render`, `readings --conclusion`), where Python's untrusted
generators propose the evidence and Lean decides every verdict. Every expected value is the plan's (*derived*); the
generators' search on `CE4` (the plan's "found or not found") is recorded by
`test_the_generator_on_ce4_records_what_it_finds`.

R14: every answer here is about the pilot's translation, not the constitution's text. C5 reports no conflict; a conflict
the route reported about the constitution would be a CANDIDATE (R14 source check pending: SC-9 external check, FOLLOW-UP), never a conflict in the source
(`tests/test_rd9_r14_candidates.py`).
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
from types import SimpleNamespace

import pytest

from tests import ce4, lean_routes
from tests.subprocesses import HANG_TIMEOUT
from tests.test_document import write_doc
from tests.test_readings_s1_lean import run, situation_id
from tests.test_readings_sd_lean import choice_case
from ve.document import check_document, load_document, main, render_document
from ve.environment import Environment
from ve.norm_defaults import unsaid_name
from ve.readings import s1_content_meaning_id
from ve.softnorms import SoftEnvironment

LEAN = "ve_readings_route"
RESERVED = ("unsaid__", "unsaid--", "soft__")  # what no English line may show (spec 2.5)
GAP = re.compile(r" Here the text does not say whether [^;]+; this situation answers '(yes|no)'\.")
DENIAL = "force-u0125-s04-p2"
CLARIFY = "force-u0036-s05"
# C1 to C4: the set, the witness's value, the other reading's, the gap Lean selects and the E14 source word.
PAIRS = {
    "C1": (DENIAL, True, False, ["denial_of_being_claude_permitted", ["c"], True], "should"),
    "C2": (CLARIFY, False, True, ["clarification_required", ["c", "s"], False], "should"),
    "C3": ("force-u0156-s03", True, False, ["system_prompt_deception_permitted", ["c", "u"], True], "shouldn’t"),
    "C4": ("force-u0263-s04-p2", False, True, ["exploit_instruction_compliance_required", ["c", "s"], False],
           "should"),
}
# C1 to C4 rendered (2.2): the supposition, then the one gap sentence Lean selects, then "Under (1)".
LINES = {
    "C1": ("suppose the decider decides the exception applies to c. Here the text does not say whether c may "
           "directly deny being Claude; this situation answers 'yes'. Under (1) c is not permitted to."),
    "C2": ("suppose the decider decides the exception applies to c and s. Here the text does not say whether c must "
           "seek clarification in s; this situation answers 'no'. Under (1) c still must."),
    "C3": ("suppose the decider decides the exception applies to c and u. Here the text does not say whether c may "
           "actively deceive u about system prompt existence-or-content; this situation answers 'yes'. Under (1) c "
           "is not permitted to."),
    "C4": ("suppose the decider decides the exception applies to c and s. Here the text does not say whether c must "
           "comply with the instruction against unintended exploits in s; this situation answers 'no'. Under (1) c "
           "still must."),
}
# SC-8's generator run on `CE4`, recorded: found for every ordered pair. C2 and C4 separate on the outcome (the gap
# left empty, 'no'); C1 and C3 on which rule selects the point (the default rule, excepted, does not), with no gap.
FOUND = {set_id: {("strict", "default"): True, ("default", "strict"): True} for set_id in ce4.SETS}
C6 = ["forall", "claude_instance", ["not", ["unary", "denial_of_being_claude_permitted", ["var", 0]]]]
C7 = ["forall", "claude_instance", ["forall", "situation", [
    "implies", ["unary", "genuine_ambiguity", ["var", 0]], ["binary", "clarification_required", ["var", 1], ["var", 0]]]]]


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


# The pinned source and the rewriting (5.2).

def test_ce4_is_the_pilots_pinned_translation():
    """The copy is the translation at pilot commit 76922d6c byte for byte (its git blob id); where the repository
    still holds that commit, the blob is read back from it."""
    data = ce4.pinned_bytes()
    found = subprocess.run(["git", "cat-file", "blob", f"{ce4.PILOT_COMMIT}:{ce4.PILOT_PATH}"],
                           capture_output=True, timeout=HANG_TIMEOUT, cwd=ce4.COPY.parent)
    if found.returncode == 0:
        assert found.stdout == data


def test_ce4_frame_and_the_default_rewrite():
    """The frame of 5.2; each `default` candidate is the strict rule with `mode: default`, an unstated exception and
    no `unless`; the `strict` candidates and the source words are the translation's; no open term is left."""
    front, body = ce4.translation()
    raw = ce4.environment()
    assert set(raw["vocabulary"]["sorts"]) == set(ce4.SORTS) and raw["vocabulary"]["constants"] == {}
    predicates = raw["vocabulary"]["predicates"]
    assert set(predicates) == {*ce4.BASE, *ce4.REGULATED}
    assert all(predicates[p]["regulated"]["default"] == "unspecified" for p in ce4.REGULATED)
    assert not any(p.startswith("exception_to_") for p in predicates)
    assert "soft-norms@0" in raw["profiles"] and "norm-defaults@0" in raw["profiles"]
    for R, source in zip(ce4.reading_sets(), front["reading_sets"]):
        strict, default = R["readings"]
        assert strict["content"] == source["readings"][0]["content"]
        rule = default["content"]["norm"]
        assert rule["mode"] == "default" and rule["unless"] == [] and rule["exception"] == ce4.UNSTATED
        assert {**rule, "unless": source["readings"][1]["content"]["norm"]["unless"]} == {
            **source["readings"][1]["content"]["norm"], "mode": "default", "exception": ce4.UNSTATED}
    text, units, moved = ce4.source_text()
    for R in front["reading_sets"]:
        a, b = R["source_word"]
        assert text[moved[R["id"]][0]:moved[R["id"]][1]] == body[a:b]


# C1 to C4 and C1.4 through Lean's readings route (SC-4).

@pytest.fixture(scope="module")
def lean_document():
    raw = ce4.environment()
    sets = ce4.reading_sets()
    for R in sets:
        for a in R["readings"]:
            a["meaning_id"] = "m"
    return raw, ce4.wire_document(ce4.with_situations(raw, sets, situation_id))


@pytest.fixture(scope="module")
def validated(lean_document):
    raw, document = lean_document
    [row] = run(LEAN, [{"id": "v", "kind": "readings-validate", "environment": raw, "document": document}])
    assert row["status"] == "ok", row
    return row


@pytest.mark.parametrize("name", sorted(PAIRS))
def test_c1_to_c4_validate_separates_by_the_decision_alone(validated, lean_document, name):
    """C1 to C4: admitted; σ (witness `default`, its exception decided for the tuple, the shared filling) separates
    the pair on filled sides with the one gap the shown value reads; the finding is `SeparatedByDecisionOnly` with
    S1's wording rule (not certified, D5); the default reading alone owns its exception's table."""
    set_id, witness_value, other_value, gap, _ = PAIRS[name]
    raw, document = lean_document
    [entry] = [e for e in validated["sets"] if e["set"] == set_id]
    sid = situation_id(raw, ce4.sigma(set_id))
    facts = {"situation": sid, "witness": "default", "separated": True, "witness_admissible": True,
             "witness_value": witness_value, "other_admissible": True, "other_value": other_value, "gaps": [gap]}
    assert entry["pairs"] == [{"reading": "strict", "other": "default", "pair": facts},
                              {"reading": "default", "other": "strict", "pair": facts}]
    assert entry["findings"] == [f"SeparatedByDecisionOnly: {set_id}: 0, 1 (not certified)"]
    assert [[k["key"] for k in c["owned"]] for c in entry["candidates"]] == [[], [{"excepted": ce4.RULES[set_id]}]]
    # No soft premise: each regulated predicate has one rule, with no exception condition.
    assert all(e["premises"] == [] for e in validated["soft_premises"])


def test_the_filled_tables_are_those_leans_filled_environment_adds(validated, lean_document):
    """On the soft chain no `F_p` unit reads a table (each is a rule of a filled tree), so the tables are read from
    Lean's filled environment, as on the norms chain: every regulated predicate's table, none other. Before this, the
    soft chain had none and C6's countermodel named `unsaid__denial_of_being_claude_permitted` as an author fact."""
    from ve.readings_s1 import Decoded
    raw, document = lean_document
    decoded = Decoded(raw, document, validated["filled"], validated["fill_premises"], validated["soft_premises"])
    assert decoded.doc.filled_tables == {unsaid_name(p): p for p in ce4.REGULATED}


def _model(relations=None):
    return {"complete": True, "domains": {"claude_instance": ["c"], "situation": ["s"], "user": ["u"]},
            "constants": {}, "relations": {p: [] for p in ce4.BASE} | (relations or {})}


def test_c1_4_status_undecided_under_default_settled_no_under_strict(lean_document, validated):
    """C1.4: with `excepted` {c} the default reading's two admissible fillings (yes {c}, no {}) give opposite values,
    so the point is UNDECIDED, worded by R7; under the strict reading it is SETTLED no."""
    from ve.norm_defaults_english import point_clause
    from ve.readings_s2_english import result_sentence
    raw, document = lean_document
    default = [(s, 1 if s == DENIAL else 0) for s in ce4.SETS]
    strict = [(s, 0) for s in ce4.SETS]
    point = {"predicate": "denial_of_being_claude_permitted", "tuple": ["c"]}
    excepted = _model({"soft__excepted__no_denying_being_claude": [["c"]]})
    undecided = {"kind": "norm-defaults-status", "model": excepted, **point, "method": "undecided",
                 "yes": {unsaid_name(point["predicate"]): [["c"]]}, "no": {}}
    settled = {"kind": "norm-defaults-status", "model": _model(), **point, "method": "table3"}
    rows = run(LEAN, [choice_case(raw, document, default, undecided), choice_case(raw, document, strict, settled)])
    assert rows[0]["inner"]["point_status"] == "UNDECIDED", rows[0]
    assert rows[1]["inner"]["point_status"] == "SETTLED no", rows[1]
    frame = Environment(validated["filled"]["environment"])
    clause = point_clause(frame, SimpleNamespace(constants={}), point["predicate"], ("c",))
    assert result_sentence("undecided", clause=clause) == (
        "the text does not say whether c may directly deny being Claude: no rule decides this situation.")


# C1 to C8 through `ve document` (SC-8): Python's generators propose, Lean decides.

def ce4_document(tmp_path, situations=None):
    """`CE4` as a document: the four sentences, the readings' meaning ids, each set's σ recorded (or `situations`,
    a function of the raw environment and the sets)."""
    raw = ce4.environment()
    env = SoftEnvironment(raw)
    text, units, moved = ce4.source_text()
    sets = ce4.reading_sets()
    for R in sets:
        R["source_word"] = moved[R["id"]]
        for a in R["readings"]:
            a["meaning_id"] = s1_content_meaning_id(env, R["id"], a)
    sets = situations(raw, sets) if situations else ce4.with_situations(raw, sets, situation_id)
    return write_doc(tmp_path, text, units, environment_json=raw, reading_sets=sets)


@pytest.fixture(scope="module")
def document(tmp_path_factory):
    return ce4_document(tmp_path_factory.mktemp("ce4"))


def shown(lines):
    """No English line names a filled table, a decision table or a generated rule (spec 2.5)."""
    assert lines and not [line for line in lines if any(prefix in line for prefix in RESERVED)], lines
    return lines


def test_ce4_load_takes_the_enumerated_route_of_the_soft_completion(document):
    s2 = load_document(document)["readings_s2"]
    assert s2["route"] == "enumerated" and s2["finding"]["cause"] == "the unspecified completion"
    assert len(s2["choices"]) == 16
    assert s2["soft_premises"] == [{"set": s, "index": i, "premises": []} for s in ce4.SETS for i in (0, 1)]


@pytest.mark.parametrize("name", sorted(PAIRS))
def test_c1_to_c4_render_one_gap_sentence_on_each_separation_line(document, name):
    """C1 to C4 rendered: E14 with the source word, the supposition of the default reading's exception, exactly one
    filled-gap sentence (C2's is the plan's "whether c must seek clarification in s ... 'no'"), then "Under (1)"."""
    set_id, _, _, _, word = PAIRS[name]
    lines = shown(render_document(document).splitlines())
    [line] = [line for line in lines if line.startswith(f"This sentence says *{word.replace(chr(8217), chr(39))}*.")
              and LINES[name] in line]
    assert len(GAP.findall(line)) == 1


def test_c5_every_choice_is_conflict_free_with_no_condition(document):
    """C5: 16 compatible choices, each CONFLICT-FREE (each regulated predicate has one rule), `conditional_on: []`;
    the premises have a model."""
    report = check_document(document)
    readings = report["readings"]
    assert readings["route"] == "enumerated" and readings["choices_checked"] == 16
    assert readings["conflict"]["status"] == "CONFLICT-FREE"
    assert readings["conflict"].get("conditional_on", []) == []
    assert [c["status"] for c in readings["conflict"]["choices"]] == ["CONFLICT-FREE"] * 16
    assert report["premises"]["status"] == "model"
    shown(readings["english"])


def query(tmp_path, capsys, path, conclusion, *under):
    file = tmp_path / "conclusion.json"
    file.write_text(json.dumps(conclusion))
    assert main(["readings", str(path), "--conclusion", str(file),
                 *[arg for set_index in under for arg in ("--under", set_index)]]) == 0
    return json.loads(capsys.readouterr().out)


def _with(choice, set_id, index):
    return [[s, index if s == set_id else 0] for s, _ in choice]


ALL_STRICT = [[s, 0] for s in ce4.SETS]


def test_c6_the_denial_query_some_all_none(tmp_path, capsys, document):
    """C6: "∀ c. ¬ denial_of_being_claude_permitted(c)" is SOME (proved where the sentence is read strictly, refuted
    where it is read as a default: the decider excepts c and the gap is filled 'yes'); ALL under `:0`; NONE under
    `:1`, shown with the supposition and the gap sentence."""
    data = query(tmp_path, capsys, document, C6)
    assert data["verdict"] == "SOME", data
    assert (data["proof"]["choice"], data["countermodel"]["choice"]) == (ALL_STRICT, _with(ALL_STRICT, DENIAL, 1))
    assert query(tmp_path, capsys, document, C6, f"{DENIAL}:0")["verdict"] == "ALL"
    none = query(tmp_path, capsys, document, C6, f"{DENIAL}:1")
    assert none["verdict"] == "NONE", none
    for line in shown(none["english"]):
        element = re.search(r"suppose the decider decides the exception applies to (\w+)\.", line)
        assert element is not None, line
        assert line.endswith(f"Here the text does not say whether {element[1]} may directly deny being Claude; this "
                             "situation answers 'yes'.")


def test_c7_the_clarification_query_some_all(tmp_path, capsys, document):
    """C7: "∀ c ∀ s. genuine_ambiguity(s) → clarification_required(c, s)" is SOME; ALL under `force-u0036-s05:0`."""
    data = query(tmp_path, capsys, document, C7)
    assert data["verdict"] == "SOME", data
    assert (data["proof"]["choice"], data["countermodel"]["choice"]) == (ALL_STRICT, _with(ALL_STRICT, CLARIFY, 1))
    follows, fails = shown(data["english"])
    assert "the conclusion does not follow" in fails and GAP.findall(fails) == ["no"]
    assert query(tmp_path, capsys, document, C7, f"{CLARIFY}:0")["verdict"] == "ALL"


def test_c8_decided_units_are_the_four_sets_units(document):
    """C8: every row of C5 decided and every reading's premise status `model`, so Lean's `decided_units` is the four
    sets' units; under an assumed reading the rows cover fewer choices, so none."""
    from ve.readings_verdicts import context
    route = context(load_document(document))
    premises = route.premises_answer()
    assert premises["result"]["status"] == "model"
    assert {e["premises"] for e in premises["per_choice"]} == {"model"}
    assert premises["decided_units"] == ["u0036.s05", "u0125.s04.p2", "u0156.s03", "u0263.s04.p2"]
    assert route._verdicts("conflict", assumed=[[DENIAL, 0]])["decided_units"] == []


def test_the_generator_on_ce4_records_what_it_finds():
    """SC-8: Python's search on `CE4` before any situation is recorded, over Lean's filled frame, recorded as found or
    not found per ordered pair; a found situation is the one Lean admits as separating."""
    from tests.test_readings_sd_document import _pending, _run
    from ve.readings_s1 import record_situations, search
    raw = ce4.environment()
    sets = ce4.reading_sets()
    for R in sets:
        for a in R["readings"]:
            a["meaning_id"] = "m"
    pending = _pending(raw, ce4.wire_document(sets))
    filled = _run("readings-elaborate", raw, pending)
    found = {R["id"]: search(raw, pending, R["id"], filled=filled) for R in sets}
    assert {set_id: {pair: entry is not None for pair, entry in pairs.items()} for set_id, pairs in found.items()} \
        == FOUND, found
    recorded = copy.deepcopy(pending)
    recorded["reading_sets"] = [record_situations(R, {k: v for k, v in found[R["id"]].items() if v is not None})
                                if any(found[R["id"]].values()) else R for R in recorded["reading_sets"]]
    validated = _run("readings-validate", raw, recorded)
    for entry in validated["sets"]:
        if any(found[entry["set"]].values()):
            assert all(p["pair"]["separated"] for p in entry["pairs"]), entry
