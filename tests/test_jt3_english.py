"""JT-3's authoring refusal through the service (docs/spec/judgment-terms.md 9.5; DRI 2026-11-02, jt-3 items 1, 3 and 4).

The refusal is Lean's, in authoring only, with its bound names opted in. The declaration, legend and status rows are
`lean/VE/EnglishGrammar/JudgmentLinesExamples.lean`'s, in identifier wording: JT-E1r and JT-E1s failed, so nothing here
measures what a reader understands, and no test compares a line with a section 2.4 template (withdrawn by the fallback).
"""
from __future__ import annotations

import json

import pytest

from ve import judgment_lines
from ve.__main__ import main as ve_main
from ve.backends import english_lean
from ve.backends.relay import decide
from ve.english import EnglishVocabulary
from ve.environment import Environment
from ve.errors import SyntaxError as VESyntaxError, VEError

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


def test_every_retyped_or_rebound_refusal_field_is_refused(env):
    """A relayed refusal is typed and bound by `refusal_problem`: each field dropped or retyped, a code no status has, a
    class that is not Lean's, a span out of the source, a sentence number the source cannot hold."""
    source = said("reasonable_limit")
    words = EnglishVocabulary(env, _defer_overlay_refusals=True)
    expected = english_lean.identities(env, source, words, english_lean.export(words))
    genuine = raw(env, source, judgments=[])["result"]
    assert english_lean.response_problem(genuine, expected, env, source) is None
    deep: list = []
    for _ in range(10_000):
        deep = [deep]

    def refused(answer) -> bool:
        """`read` answers a problem or a too-deep answer `CheckerUnavailable`."""
        try:
            return bool(english_lean.response_problem(answer, expected, env, source))
        except RecursionError:
            return True

    assert not refused(genuine)
    for field in ("status", "code", "class", "text", "sentence", "span"):
        assert refused({k: v for k, v in genuine.items() if k != field}), field
        for value in (7, True, None, {}, [], 1.5, "", deep):
            if value != genuine[field]:
                assert refused({**genuine, field: value}), (field, value)
    for field, value in (("code", "NoDerivation"), ("code", "Undeclared"), ("class", "TypeMismatch"),
                         ("span", [0, len(source) + 1]), ("span", [5, 2]), ("sentence", 1)):
        assert refused({**genuine, field: value}), (field, value)
    assert refused({**genuine, "extra": 1})
    assert refused({k: v for k, v in genuine.items() if k != "identities"})


def test_binding_is_per_predicate_never_per_word(env):
    """Spec 7 and 8.4 bind per predicate: `reasonable_grounds` does not silence `reasonable_limit` (DRI item 3)."""
    result = raw(env, said("reasonable_limit"), judgments=["reasonable_grounds"])["result"]
    assert result["code"] == "UndeclaredEvaluative"
    two = f'{said("reasonable_limit")} {said("reasonable_grounds")}'
    assert raw(env, two, judgments=["reasonable_limit"])["result"]["sentence"] == 1
    assert raw(env, two, judgments=["reasonable_limit", "reasonable_grounds"])["result"]["status"] == "one"


def test_a_word_defined_by_w3_is_not_refused_as_the_real_environment_writes_it():
    """9.5's second way out, on the environment's own shape (`defined` in the predicate's entry); the same word undefined
    is refused."""
    predicates = {**ENV["vocabulary"]["predicates"], "reasonable_limit": {
        "arguments": ["limit"], "description": "reasonable_limit",
        "defined": {"arguments": ["limit"], "body": ["unary", "published", ["var", 0]]}}}
    written = {**ENV, "profiles": ["definitions@0", "relational-fol@0"],
               "vocabulary": {**ENV["vocabulary"], "predicates": predicates}}
    result = raw(Environment.from_dict(written), said("reasonable_limit"), judgments=[])["result"]
    assert result["status"] == "one", result


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


def sibling(env, mode: str, **fields) -> dict:
    """A request to a mode that shares `english.read`'s optional fields (`Run.optionalFields`)."""
    case = english_lean.request(env, "Is Atlas published?", EnglishVocabulary(env, _defer_overlay_refusals=True), {})
    shared = {"environment": case["environment"], "lexicon": case["lexicon"]}
    return {"english.question": {**case, "question": case["source"]}, "english.grammar": shared,
            "english.check": {**shared, "formulas": [], "marks": [], "candidates": []}}[mode] | {"id": mode, **fields}


@pytest.mark.parametrize("mode", ["english.question", "english.grammar", "english.check"])
@pytest.mark.parametrize("judgments", [[], ["reasonable_limit"]])
def test_the_modes_that_share_read_s_fields_refuse_judgments(env, mode, judgments):
    """The field is signed for `english.read` only (DRI item 1): the sibling modes refuse it, as on the merge base,
    never drop the opt-in unread (jt-3 review F1)."""
    assert decide(mode, [sibling(env, mode)])[0]["id"] == mode
    with pytest.raises(VEError, match="fields do not match"):
        decide(mode, [sibling(env, mode, judgments=judgments)])


def test_the_command_line_shows_lean_s_text(tmp_path, capsys):
    path = tmp_path / "env.json"
    path.write_text(json.dumps(ENV), encoding="utf-8")
    assert ve_main(["judgments", "read", said("reasonable_limit"), "--env", str(path)]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["message"] == REASONABLE
    assert ve_main(["judgments", "read", said("reasonable_limit"), "--env", str(path),
                    "--bound", "reasonable_limit"]) == 0
    capsys.readouterr()
