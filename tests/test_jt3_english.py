"""JT-3's English rows through the service (docs/spec/judgment-terms.md 9.1 and 9.5; DRI 2026-11-02, jt-3 items 1 to 4).

The declaration line reads to a W2 record and its predicate; the refusal is Lean's, in authoring only, with its bound
names opted in. The lines' other rows are `lean/VE/EnglishGrammar/JudgmentLinesExamples.lean`'s. These are identifier
wording: JT-E1r and JT-E1s failed, so nothing here measures what a reader understands, and no test compares a line with a
section 2.4 template (withdrawn by the fallback).
"""
from __future__ import annotations

import copy
import json

import pytest

from ve import judgment_lines
from ve.__main__ import main as ve_main
from ve.backends import english_lean
from ve.backends.relay import decide
from ve.backends.service_schema import check_row
from ve.english import EnglishVocabulary
from ve.environment import Environment
from ve.errors import SyntaxError as VESyntaxError, VEError

GOVERNED = 'Whether an act is classified as "arbitrary" is a judgment for the governance function.'
UNSTATED = 'Whether an act is classified as "arbitrary" is a judgment; the text does not say who makes it.'
UNFAIR = ('Whether a person has the recorded relation "treats_unfairly" to a person (the same or another) is a judgment; '
          "the text does not say who makes it.")
ENV = {"language": "ve.core@0.2", "profiles": ["relational-fol@0"], "spec_revision": "ve-v0.2-expand2-2026-09-25",
       "vocabulary": {
           "constants": {"atlas": {"description": "a limit", "sort": "limit"}},
           "predicates": {p: {"arguments": ["limit"], "description": p} for p in
                          ("reasonable_limit", "reasonable_grounds", "due_date", "published", "arbitrarily_set")},
           "sorts": {"limit": {"description": "a limit"}}}}
REASONABLE = ("'Reasonable' is a judgment. Say who decides it ('… is a judgment for the operator'), or define it "
              "('In this document, a reasonable limit means …').")
QUOTED = ("'Arbitrarily' is a judgment. Say who decides it ('… is a judgment for the operator'), or define it "
          """('In this document, "arbitrarily" means …').""")


def said(predicate: str) -> str:
    return f'Atlas is classified as "{predicate}".'


@pytest.fixture(scope="module")
def env():
    return Environment.from_dict(ENV)


def raw(env, source: str, **fields) -> dict:
    """Lean's whole `english.read` row, identities included."""
    case = english_lean.request(env, source, EnglishVocabulary(env, _defer_overlay_refusals=True), {})
    return decide("english.read", [{**case, **fields}])[0]


@pytest.mark.parametrize("line, name, sorts, decider", [
    (GOVERNED, "arbitrary", ["act"], "governance_function"), (UNSTATED, "arbitrary", ["act"], "unstated"),
    (UNFAIR, "treats_unfairly", ["person", "person"], "unstated")])
def test_a_line_reads_to_its_w2_record_and_predicate(line, name, sorts, decider):
    row = judgment_lines.declare(line, "udhr")
    assert row["predicate"] == {"name": name, "arguments": sorts}
    assert row["record"] == {"name": name, "arguments": sorts, "decided_by": decider, "necessary": [], "sufficient": [],
                             "factors": [], "precedents": [], "jurisdiction": "udhr", "version": 1}


@pytest.mark.parametrize("line, code", [
    ("The act is arbitrary.", "JudgmentLine"), (GOVERNED.replace("for the", "for"), "JudgmentLine"),
    (GOVERNED.replace("an act", "a act"), "JudgmentLine"), (GOVERNED + " ", "JudgmentLine"),
    (GOVERNED.replace("governance function", "unresolved decider"), "JudgmentDecider"),
    (GOVERNED.replace("governance function", "unstated"), "JudgmentLine"), ("", "JudgmentLine")])
def test_any_other_spelling_is_refused_by_lean(line, code):
    with pytest.raises(VEError, match=f"^{code}: "):
        judgment_lines.declare(line, "udhr")


def mutants(row: dict):
    deep: list = []
    for _ in range(10_000):
        deep = [deep]
    for path in (("line",), ("record",), ("predicate",), ("record", "name"), ("record", "arguments"),
                 ("record", "decided_by"), ("record", "necessary"), ("record", "version"), ("record", "jurisdiction"),
                 ("predicate", "name"), ("predicate", "arguments")):
        for value in (7, True, None, {}, 1.5, [7], [None], deep, "\ud800"):
            mutated = copy.deepcopy(row)
            parent = mutated
            for key in path[:-1]:
                parent = parent[key]
            parent[path[-1]] = value
            yield mutated
            del parent[path[-1]]
            yield mutated
    yield {**row, "extra": 1}


REBOUND = [("record", "name", "absent"), ("predicate", "name", "absent"), ("record", "arguments", ["absent"]),
           ("predicate", "arguments", ["act", "act"]), ("record", "arguments", []), ("record", "decided_by", "absent"),
           ("record", "jurisdiction", "other"), ("line", None, UNSTATED)]


def relayed(row: dict, case: dict) -> bool:
    """Whether the relay accepts `row`: the generated schema, then the binding."""
    try:
        check_row(judgment_lines.MODE, row, case, 0)
    except Exception:  # noqa: BLE001 - the relay answers any refusal of the row `CheckerUnavailable`
        return False
    return judgment_lines.answer_problem(row, case) is None


def test_every_retyped_or_rebound_field_is_refused():
    case = {"id": judgment_lines.MODE, "line": GOVERNED, "jurisdiction": "udhr"}
    row = judgment_lines.declare(GOVERNED, "udhr")
    assert relayed(row, case)
    for mutated in mutants(row):
        assert not relayed(mutated, case)
    for member, key, value in REBOUND:
        mutated = copy.deepcopy(row)
        if key is None:
            mutated[member] = value
        else:
            mutated[member][key] = value
        assert not relayed(mutated, case), (member, key, value)
    swapped = judgment_lines.declare(UNFAIR, "udhr")
    assert relayed(swapped, {**case, "line": UNFAIR})


def test_which_decider_a_line_names_is_lean_s():
    """The binding asks only that a decider's words are the line's; `parseLine_renders` carries which ones it means (R8)."""
    row = judgment_lines.declare(GOVERNED, "udhr")
    for decider in ("unstated", "governance"):
        record = {**row["record"], "decided_by": decider}
        assert judgment_lines.answer_problem({**row, "record": record}, {"line": GOVERNED}) is None


def test_the_refusal_names_lean_s_text_and_a_bound_predicate_is_read(env):
    source = said("reasonable_limit")
    refused = raw(env, source, judgments=[])["result"]
    assert (refused["status"], refused["code"], refused["class"], refused["text"]) == (
        "rejected", "UndeclaredEvaluative", "SyntaxError", REASONABLE)
    assert (refused["sentence"], refused["span"]) == (0, [0, len(source)])
    assert raw(env, source, judgments=["reasonable_limit"])["result"]["status"] == "one"
    with pytest.raises(VESyntaxError) as raised:
        judgment_lines.read_authored(env, source, [])
    assert str(raised.value) == refused["text"]
    assert judgment_lines.read_authored(env, source, ["reasonable_limit"]).status == "one"


def test_binding_is_per_predicate_never_per_word(env):
    """Spec 7 and 8.4 bind per predicate: `reasonable_grounds` does not silence `reasonable_limit` (DRI item 3)."""
    result = raw(env, said("reasonable_limit"), judgments=["reasonable_grounds"])["result"]
    assert result["code"] == "UndeclaredEvaluative"
    two = f'{said("reasonable_limit")} {said("reasonable_grounds")}'
    assert raw(env, two, judgments=["reasonable_limit"])["result"]["sentence"] == 1
    assert raw(env, two, judgments=["reasonable_limit", "reasonable_grounds"])["result"]["status"] == "one"


def test_each_definition_form_reaches_the_relay(env):
    assert raw(env, said("arbitrarily_set"), judgments=[])["result"]["text"] == QUOTED


@pytest.mark.parametrize("source", [said("due_date"), "Atlas is published."])
def test_another_sense_and_a_plain_word_are_not_refused(env, source):
    assert raw(env, source, judgments=[])["result"]["status"] == "one"


def test_without_the_field_no_request_is_refused_for_the_word(env):
    """The opt-in keeps every existing request's answer (DRI item 1, condition (a)), and a read refusal is unchanged."""
    assert raw(env, said("reasonable_limit"))["result"]["status"] == "one"
    plain, opted = (raw(env, "Atlas is odd.", **fields)["result"] for fields in ({}, {"judgments": []}))
    assert plain == opted and plain["code"] == "NoDerivation"


@pytest.mark.parametrize("source", [said("reasonable_limit"), "Atlas is published.", "Atlas is odd."])
@pytest.mark.parametrize("judgments", [[], ["reasonable_limit"], ["absent"]])
def test_translation_answers_byte_identically_with_the_field(env, source, judgments):
    """In translation an unbound word is only reported (8.4, 9.5): the field changes no byte (DRI item 1, condition (b))."""
    fields = {"mode": "translation"}
    assert json.dumps(raw(env, source, **fields)) == json.dumps(raw(env, source, judgments=judgments, **fields))


@pytest.mark.parametrize("value", [7, True, None, {}, "reasonable_limit", [7], [None], [["reasonable_limit"]]])
def test_a_malformed_field_is_invalid_input(env, value):
    # `null` does not reach the mode: the service's restricted JSON refuses it.
    with pytest.raises(VEError, match="judgments is a list of strings|restricted JSON"):
        raw(env, "Atlas is published.", judgments=value)


def test_the_field_s_size_is_charged_against_its_limit(env):
    """At the limit the request is read; one more name is `ResourceLimit`, never a reading."""
    names = [f"n{i}" for i in range(4096)]
    assert raw(env, "Atlas is published.", judgments=names)["result"]["status"] == "one"
    with pytest.raises(VEError, match="at most 4096 judgments"):
        raw(env, "Atlas is published.", judgments=[*names, "extra"])


def test_the_command_line_shows_lean_s_answer(env, tmp_path, capsys):
    assert ve_main(["judgments", "declare", GOVERNED, "--jurisdiction", "udhr"]) == 0
    assert json.loads(capsys.readouterr().out)["record"]["decided_by"] == "governance_function"
    assert ve_main(["judgments", "declare", "No.", "--jurisdiction", "udhr"]) == 2
    assert "JudgmentLine:" in capsys.readouterr().out
    path = tmp_path / "env.json"
    path.write_text(json.dumps(ENV), encoding="utf-8")
    assert ve_main(["judgments", "read", said("reasonable_limit"), "--env", str(path)]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["message"] == REASONABLE
    assert ve_main(["judgments", "read", said("reasonable_limit"), "--env", str(path),
                    "--bound", "reasonable_limit"]) == 0
    capsys.readouterr()
