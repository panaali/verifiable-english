"""E2's untrusted `english.read` answers: every status, every node, against the real service (review B1, B3, B4,
B5 of English Lean E2; build checklist 4, 5, 13, 15).

The genuine answers come from the persistent `ve_service`, one per status (`one` with an obligation, `none` with
advice, `many`, `budget`, a lexical and a sentence rejection, `IllTyped`, `invalidGrammar` and `InvalidOverlay`).
Every one-fault mutant of every JSON node (each value replaced by another type, an empty or a 10,000-deep value;
each key dropped or added; each list item dropped or repeated) must either be refused as `CheckerUnavailable`, or
change only content the relay cannot recompute and lists as such (`FREE`): Lean's display texts, spans,
derivation trees and advice. Nothing else may escape `read`.
"""
from __future__ import annotations

import copy
import json
import re

import pytest

from conformance import english_lean_s3_fixtures as fixtures
from ve import Environment
from ve import english as EN
from ve.backends import english_lean as L
from ve.backends import relay
from ve.english_grammar import codes, export
from ve.errors import CheckerUnavailable, VEError


def _env(raw: dict, **changes) -> Environment:
    return Environment({**raw, **changes})


def _deployed_service() -> dict:
    raw = fixtures.F()
    raw["vocabulary"]["sorts"]["dservice"] = {"description": "dservice",
                                             "verbalisation": {"singular": "deployed service",
                                                               "plural": "deployed services"}}
    return raw


# status label -> (environment JSON, source, case changes, expected status, code)
GENUINE = {
    "one": (fixtures.F, "Legacy is deployed. Therefore legacy is deployed.", {}, "one", None),
    "none": (fixtures.F, "They are deployed.", {}, "none", "NoDerivation"),
    "many": (_deployed_service, "Every deployed service is reviewed.", {}, "many", "Ambiguous"),
    "lexical": (fixtures.F, "Légacy is deployed. Alice owns legacy # x.", {}, "rejected", "BadCharacter"),
    "sentence": (fixtures.F, "Every deployed service is not reviewed.", {}, "rejected", "BlockedWording"),
    "premise": (fixtures.F, "Therefore legacy is deployed.", {}, "rejected", "ConclusionWithoutPremise"),
    "lexicon": (fixtures.FA, "Wait is available to robot.", {"select": ("safe", "{0} is safe")}, "invalidGrammar",
                "InvalidGrammar"),
    "overlay": (fixtures.F, "Legacy is deployed.", {"overlay": "O3"}, "invalidGrammar", "InvalidOverlay"),
}


def genuine(label: str):
    """The real service's answer for a fixture, the identities the relay expects, the environment and source."""
    build, source, changes, status, code = GENUINE[label]
    raw = build()
    if changes.get("overlay") == "O3":
        raw["vocabulary"]["predicates"]["stable"] = {"arguments": ["service"], "description": "Stable.",
                                                    "verbalisation": "{0} is stable"}
    env = Environment(raw)
    options = {}
    if changes.get("overlay") == "O3":
        options = {"vocabulary": {"format": "ve.english-vocabulary@1", "environment_id": env.environment_id,
                                  "sorts": {}, "constants": {},
                                  "predicates": {"stable": {"verbalisation": "{0} never fails",
                                                            "suggested": False}}}}
    words = EN.EnglishVocabulary(env, _defer_overlay_refusals=True, **options)
    if "select" in changes:
        # A lexicon Python's producer never makes (spec lx29: `LA` selects `safe`'s declared wording), so V6
        # refuses it: the genuine `invalidGrammar` answer.
        name, wording = changes["select"]
        words.predicates[name] = wording
    case = L.request(env, source, words, options)
    row = relay.decide_once("english.read", case)
    assert row["status"] == "ok", row
    response = row["result"]
    assert response["status"] == status and response.get("code") == code, response
    return response, L.identities(env, source, words, case["lexicon"]), env, source, words, options


def budget_answer():
    """`budget` is not reachable at the service's work budget on a short text; its shape is the `none` answer
    with Lean's `budgetFields` (Run.lean), which the validator must accept and fuzz like the rest."""
    response, expected, env, source, words, options = genuine("none")
    response = {k: v for k, v in response.items() if k != "advice"}
    response.update(status="budget", code="Budget", **{"class": "ResourceLimit"},
                    text="Sentence 1 needs more work than the limit allows. No verdict was reached.")
    return response, expected, env, source, words, options


ANSWERS = {label: (lambda label=label: genuine(label)) for label in GENUINE} | {"budget": budget_answer}

# The content the relay cannot recompute: Lean's display texts, spans, trees and advice, and the failure an
# `invalidGrammar` names (Lean's diagnosis of a vocabulary; the relay raises `CheckerUnavailable` whatever it
# says, and an overlay failure's site and kind are still checked).
FREE = re.compile(r"^/(text|span(/\d+)?|spans/\d+/\d+|sentence|advice(/(id|text))?|obligations/\d+/unproved|"
                  r"(derivation|witnesses)/\d+/\d+(/\d+)?|failure/[012])$")
def _deep(levels: int) -> list:
    value: list = []
    for _ in range(levels):
        value = [value]
    return value


DEEP = _deep(10000)
OPTIONAL = {"advice"}


def _paths(value, path=""):
    yield path, value
    if type(value) is dict:
        for key, item in value.items():
            yield from _paths(item, f"{path}/{key}")
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from _paths(item, f"{path}/{index}")


def _replace(value, path: str, new):
    out = copy.deepcopy(value)
    keys = [k for k in path.split("/")[1:]]
    node = out
    for key in keys[:-1]:
        node = node[int(key)] if type(node) is list else node[key]
    last = keys[-1]
    if type(node) is list:
        if new is _DROP:
            del node[int(last)]
        elif new is _REPEAT:
            node.insert(int(last), copy.deepcopy(node[int(last)]))
        else:
            node[int(last)] = new
    elif new is _DROP:
        del node[last]
    else:
        node[last] = new
    return out


_DROP, _REPEAT = object(), object()


def mutants(response: dict):
    """Every one-fault mutant: (label, path, mutant, may_pass)."""
    for path, value in _paths(response):
        if not path:
            continue
        for label, new in (("7", 7), ("true", True), ("null", None), ("[]", []), ("{}", {}), ("''", ""),
                           ("'x'", "x"), ("-1", -1), ("1.5", 1.5), ("deep", DEEP)):
            if type(new) is type(value) and new == value:
                continue
            same_type = type(new) is type(value) and not (type(value) is list and new == [])
            yield f"{path}={label}", path, _replace(response, path, new), same_type and bool(FREE.match(path))
        last = path.rsplit("/", 1)[1]
        parent_is_list = last.isdigit()
        yield f"drop {path}", path, _replace(response, path, _DROP), (
            not parent_is_list and last in OPTIONAL) or (parent_is_list and bool(FREE.match(path)))
        if parent_is_list:
            yield f"repeat {path}", path, _replace(response, path, _REPEAT), bool(FREE.match(path))
    for path, value in _paths(response):
        if path and type(value) is dict:
            yield f"add {path}/extra", path, _replace(response, path, {**value, "extra": 1}), False
    yield "add /extra", "", {**response, "extra": 1}, False


@pytest.mark.parametrize("label", sorted(ANSWERS))
def test_the_genuine_answer_of_each_status_is_well_formed(label):
    response, expected, env, source, *_ = ANSWERS[label]()
    assert L.response_problem(response, expected, env, source) is None


@pytest.mark.parametrize("label", sorted(ANSWERS))
def test_every_one_fault_mutant_fails_closed_or_changes_only_free_content(monkeypatch, label):
    response, expected, env, source, words, options = ANSWERS[label]()
    refused = passed = 0
    for name, path, mutant, may_pass in mutants(response):
        monkeypatch.setattr(L, "TRANSPORT", lambda _case, mutant=mutant: mutant)
        try:
            L.read(env, source, words, options)
        except CheckerUnavailable:
            refused += 1
            continue
        except Exception as exc:  # anything else escaping the boundary is the bug this test exists for
            pytest.fail(f"{label} {name}: {type(exc).__name__}: {exc}")
        assert may_pass, f"{label} {name}: accepted"
        passed += 1
    assert refused >= 40, (label, refused, passed)


def test_free_content_is_only_lean_display_content():
    """The listed free paths name no identity, code, class, status, formula, mark or obligation premise."""
    for path in ("/identities/lexicon_id", "/code", "/class", "/status", "/ast/0/1", "/conclusions/0",
                 "/obligations/0/premises/0", "/obligations/0/conclusion", "/fault", "/witnesses/0",
                 "/derivation/0"):
        assert not FREE.match(path), path


# ------------------------------------------------------------------ classes and texts: Lean's (review B1, B4)

def test_the_code_table_is_the_english_grammar_export():
    from tools.english_codes import from_lean
    table = json.loads((L.ROOT / "ve/english_grammar/codes.json").read_text())
    assert table == from_lean()
    classes, statuses, _ = codes()
    assert set(classes.values()) <= set(L.ERROR_CLASSES)
    assert all(code in classes for found in statuses.values() for code in found)


@pytest.mark.parametrize("code", sorted({code for found in codes()[1].values() for code in found}))
def test_every_code_is_raised_as_the_class_lean_names(monkeypatch, code):
    """Review B1: each code's class is raised as that class; `Internal` (CheckerUnavailable) is not an input
    error. The text raised is Lean's, verbatim."""
    classes, statuses, unsentenced = codes()
    status = next(s for s, found in statuses.items() if code in found)
    base, expected, env, source, words, options = genuine("lexical" if status == "rejected" else
                                                          {"invalidGrammar": "lexicon", "many": "many"}.get(status,
                                                                                                           "none"))
    if status == "budget":
        base, expected, env, source, words, options = budget_answer()
    answer = copy.deepcopy(base)
    answer.update(code=code, text=f"Lean's text for {code}.", **{"class": classes[code]})
    if code == "InvalidOverlay":
        answer.pop("fault", None)
        answer["failure"] = ["O3", "predicate", "deployed"]
    if status == "rejected":
        if code in unsentenced:
            answer.pop("sentence", None)
        else:
            answer["sentence"] = 0
    monkeypatch.setattr(L, "TRANSPORT", lambda _case: answer)
    with pytest.raises((VEError, CheckerUnavailable)) as caught:
        EN._lean_reading(env, source, words, options)
    cls = L.ERROR_CLASSES[classes[code]]
    assert type(caught.value) is cls, (code, type(caught.value))
    # `ve.errors`' coded classes write their code before the text, as Lean's coded texts do
    assert str(caught.value).removeprefix(f"{cls.code}: ").startswith(f"Lean's text for {code}."), str(caught.value)


def test_a_class_other_than_leans_is_checker_unavailable(monkeypatch):
    answer, expected, env, source, words, options = genuine("none")
    for wrong in ("VEError", "ResourceLimit", "CheckerUnavailable", "NoSuchError"):
        bad = {**answer, "class": wrong}
        assert L.response_problem(bad, expected, env, source)


def test_invalid_grammar_text_is_leans_and_names_the_failure():
    response, *_ = genuine("lexicon")
    assert response["text"] == ("The vocabulary selection was not accepted (invalidGrammar lexicon: V6 predicate "
                                "safe). No text was read.")
    _, _, env, source, words, options = genuine("lexicon")
    with pytest.raises(CheckerUnavailable) as caught:
        EN._lean_reading(env, source, words, options)
    assert str(caught.value) == response["text"] and caught.value.operation == "english.admission"


def test_the_test_transport_is_checked_like_the_service(monkeypatch):
    """Review B4: there is no second, older validator: an S2-shaped answer (no class, span, obligations or spans)
    from the test transport is malformed, so marked conclusions cannot go unproved."""
    response, expected, env, source, words, options = genuine("one")
    s2 = {k: v for k, v in response.items() if k not in ("obligations", "spans")}
    monkeypatch.setattr(L, "TRANSPORT", lambda _case: s2)
    with pytest.raises(CheckerUnavailable, match="malformed"):
        EN.parse_english(env, source)
    no_obligation = {**response, "obligations": []}
    monkeypatch.setattr(L, "TRANSPORT", lambda _case: no_obligation)
    with pytest.raises(CheckerUnavailable, match="obligations do not match"):
        EN.parse_english_argument(env, source)


def test_an_argument_without_lean_obligations_is_checker_unavailable(monkeypatch):
    """Review B4: `parse_english_argument` computes no premise of its own."""
    env = Environment(fixtures.F())
    document = EN.parse_english(env, "Legacy is deployed. Legacy is reviewed.")
    reading = EN._Reading(env, document, EN.EnglishVocabulary(env), (1,))
    monkeypatch.setattr(EN, "_parse_english_document",
                        lambda *_args, **_kwargs: (document, "source", None, (1,), reading))
    with pytest.raises(CheckerUnavailable, match="no Lean obligations"):
        EN.parse_english_argument(env, "source")


# ------------------------------------------------------------------ spans (review B3)

def test_a_lexical_rejection_spans_the_offending_character_in_code_points():
    response, expected, env, source, *_ = genuine("lexical")
    assert source[slice(*response["span"])] == "#" and response["span"] == [38, 39]
    with pytest.raises(VEError) as caught:
        EN.parse_english(env, source)
    assert source[caught.value.span.start:caught.value.span.end] == "#"


@pytest.mark.parametrize("source, character", [("Legacy is deployed .", "."), ("Alice owns 007.", "0"),
                                               ('Alice owns "legacy.', '"')])
def test_every_lexical_rejection_with_an_offset_spans_one_character(source, character):
    env = Environment(fixtures.F())
    with pytest.raises(VEError) as caught:
        EN.parse_english(env, source)
    span = caught.value.span
    assert span.end - span.start == 1 and source[span.start] == character, (source, span)


def test_ill_typed_names_the_sentence_whose_formula_fails():
    """Review B3: `IllTyped` points at the faulty formula's sentence, not sentence 1. A reach formula reads
    under the base grammar and fails the typed check of a family without `closure@0`."""
    env = Environment(fixtures.F())
    reach = ("Starting from legacy, legacy is reachable by zero or more steps, where a step from a service to a "
             "second service satisfies this condition: that service is deployed.")
    source = "Legacy is deployed. " + reach
    words = EN.EnglishVocabulary(env)
    response = relay.decide_once("english.read", L.request(env, source, words, {}))["result"]
    assert response["code"] == "IllTyped" and response["class"] == "TypeMismatch", response
    assert response["sentence"] == 1 and response["text"].startswith("Sentence 2 "), response
    assert source[slice(*response["span"])] == reach


def test_a_reading_under_an_environment_the_core_checker_refuses_raises_that_refusal():
    """E2.5 (the reverse corpus on `usecases/eligibility`): Lean reads a text under a `ve-units@1`
    environment, whose formulas the core checker refuses whatever they are (`ast.core_gate`). The public
    outcome is that refusal, as Python's reader gives it, not `CheckerUnavailable`; the comparison and the
    shadow record name it without decoding the formulas."""
    from pathlib import Path
    from ve import ast
    from ve.errors import UnsupportedProfile
    env = Environment.from_json((Path(__file__).resolve().parents[1] /
                                 "usecases/eligibility/environment.json").read_bytes())
    with pytest.raises(UnsupportedProfile):
        ast.core_gate(env)
    text = "Every inpatient person is entitled."
    with pytest.raises(UnsupportedProfile) as raised:
        EN.parse_english(env, text)
    assert not isinstance(raised.value, CheckerUnavailable)
    with pytest.raises(UnsupportedProfile):
        EN._python_reading(env, text, EN.EnglishVocabulary(env), {})
    reading = L.read(env, text, EN.EnglishVocabulary(env), {})
    assert reading.status == "one"
    assert reading.comparison("UnsupportedProfile") == {"code": "UnsupportedProfile", "verdict": "rejected"}
    assert "canonical" not in reading.record() and reading.record()["formulas"] == reading.response["ast"]
