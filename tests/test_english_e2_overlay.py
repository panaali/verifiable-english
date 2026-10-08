"""The overlay refusals at the public boundary (spec D16, D17, 2.8; fixtures rl8 to rl10, ev15c, ev17, ovc; review A2
of English Lean E2).

On the admission path Python's producer selects the fallback where it would raise, and Lean's overlay check
refuses the overlay (`InvalidOverlay`, class `VEError`, Lean's text). Every other caller of the producer keeps
its own refusal. `display_environment`'s checks still run first, before any Lean call.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from conformance import english_lean_s3_fixtures as fixtures
from ve import Environment, ast
from ve import english as EN
from ve.backends import english_lean as L
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]


def overlay(env, *, sorts=None, predicates=None):
    return {"format": "ve.english-vocabulary@1", "environment_id": env.environment_id,
            "sorts": sorts or {}, "predicates": predicates or {}, "constants": {}}


def entry(wording, negative=None):
    out = {"verbalisation": wording, "suggested": False}
    if negative:
        out["negative_verbalisation"] = negative
    return out


def _with(raw, name, arguments, wording):
    raw["vocabulary"]["predicates"][name] = {"arguments": arguments, "description": name, "verbalisation": wording}
    return raw


def case(name):
    """The overlays of spec 8.11 that the check refuses: environment, overlay, Lean's failure, Python's message."""
    if name == "ov1b":
        env = Environment(_with(fixtures.F(), "inspected", ["service"], "{0} is inspected"))
        return env, overlay(env, predicates={"inspected": entry("{0} is reviewed")}), \
            ["O1", "predicate", "inspected"], "Duplicate English wording"
    if name == "ov2b":
        env = Environment(_with(fixtures.FR(), "hazard", ["action", "harm"], "{0} endangers {1}"))
        return env, overlay(env, predicates={"hazard": entry("{0} risks {1}")}), \
            ["O2", "predicate", "hazard"], "reuses a risk@0 wording"
    if name == "ov3b":
        env = Environment(_with(fixtures.F(), "stable", ["service"], "{0} is stable"))
        return env, overlay(env, predicates={"stable": entry("{0} never fails")}), \
            ["O3", "predicate", "stable"], "template linter: predicates/stable"
    if name == "ov4b":
        env = Environment(_with(fixtures.F(), "checked", ["service"], "{0} is checked"))
        return env, overlay(env, predicates={"checked": entry("{0} is checked", "{0} is never checked")}), \
            ["O3", "predicate", "checked"], "template linter: predicates/checked"
    if name == "ov5b":
        raw = fixtures.F()
        raw["vocabulary"]["sorts"]["item"] = {"description": "item"}
        env = Environment(raw)
        return env, overlay(env, sorts={"item": {"verbalisation": {"singular": "every item",
                                                                    "plural": "every items"},
                                                   "suggested": False}}), \
            ["O3", "sort", "item"], "template linter: sorts/item"
    raise KeyError(name)


REFUSED = ("ov1b", "ov2b", "ov3b", "ov4b", "ov5b")
TEXTS = {"O1": "The vocabulary overlay gives {} a wording that another symbol already has. No text was read.",
         "O2": "The vocabulary overlay gives {} a wording that risk@0 reserves. No text was read.",
         "O3": "The vocabulary overlay entry for {} cannot be used as written. No text was read."}


@pytest.mark.parametrize("name", REFUSED)
def test_rl9_lean_refuses_the_overlay_on_the_admission_path(name):
    """Lean's shadow adapter still refuses the overlay with the E2 site and text."""
    env, vocabulary, failure, _ = case(name)
    words = EN.EnglishVocabulary(env, vocabulary=vocabulary, _defer_overlay_refusals=True)
    with pytest.raises(VEError) as caught:
        EN._lean_reading(env, "Legacy is deployed." if "risk" not in name else "Wait leads to injury.",
                         words, {'vocabulary': vocabulary})
    error = caught.value
    assert type(error) is VEError, type(error)
    reading = error.lean_reading
    assert (reading.status, reading.response["code"], reading.response["failure"]) == (
        "invalidGrammar", "InvalidOverlay", failure)
    assert str(error) == TEXTS[failure[0]].format(failure[2])


@pytest.mark.parametrize("name", REFUSED)
def test_rl10_every_other_caller_keeps_the_producers_refusal(name):
    env, vocabulary, _, message = case(name)
    with pytest.raises(VEError, match=message):
        EN.EnglishVocabulary(env, vocabulary=vocabulary)
    # the statement layer's own reader and renderer run no Lean overlay check, so the producer refuses
    with pytest.raises(VEError, match=message):
        EN.parse_statement_english(env, "Legacy is deployed.", vocabulary=vocabulary)
    formula = ast.Unary("deployed", ast.Const("legacy")) if "risk" not in name else \
        ast.Binary("leads_to", ast.Const("wait"), ast.Const("injury"))
    if name != "ov2b":
        with pytest.raises(VEError, match=message):
            EN.render_english(formula, env, _statement_layer=True, vocabulary=vocabulary)


def test_rl8_display_environment_refuses_before_any_lean_call(monkeypatch):
    """ov11a: an overlay that rewrites an alternatives@0 role's wording is refused by `display_environment`
    (Python's `Environment` of the display environment) before Lean is asked."""
    env = Environment(fixtures.FA())
    vocabulary = overlay(env, predicates={"available": entry("{0} leads to {1}")})
    monkeypatch.setattr(L, "read", lambda *_args: pytest.fail("Lean was asked"))
    with pytest.raises(VEError, match="AlternativesVerbalisation"):
        EN.parse_english(env, "Wait is available to robot.", vocabulary=vocabulary)


def test_ev17_the_overlay_check_comes_before_v6():
    """An overlay the check refuses, sent with a lexicon that fails V6, is `InvalidOverlay` (spec 2.5)."""
    env, vocabulary, failure, _ = case("ov3b")
    words = EN.EnglishVocabulary(env, vocabulary=vocabulary, _defer_overlay_refusals=True)
    words.predicates["deployed"] = "{0} is deployed daily"  # not Python's choice: V6 refuses it
    reading = L.read(env, "Legacy is deployed.", words, {"vocabulary": vocabulary})
    assert (reading.response["code"], reading.response["failure"]) == ("InvalidOverlay", failure)


@pytest.mark.parametrize("name", sorted(p.parent.name for p in ROOT.glob("usecases/*/environment.english.json")))
def test_ovc_and_ev15c_every_corpus_overlay_is_read_with_the_submitted_identity(name):
    """The four corpus overlays: the check refuses none (ovc) and the answer names the submitted environment
    while the lexicon names the display environment (ev15c, D6)."""
    folder = ROOT / "usecases" / name
    env = Environment.from_json((folder / "environment.json").read_bytes())
    vocabulary = json.loads((folder / "environment.english.json").read_text())
    words = EN.EnglishVocabulary(env, vocabulary=vocabulary, _defer_overlay_refusals=True)
    reading = L.read(env, "x.", words, {"vocabulary": vocabulary})
    assert reading.response.get("code") != "InvalidOverlay", reading.response
    assert reading.response["identities"]["environment_id"] == env.environment_id
    assert L.export(words)["environment_id"] == words.env.environment_id != env.environment_id


def test_the_suite_runs_the_english_comparator(tmp_path, monkeypatch):
    """Spec 2.8: the suite sets the comparator (tests/conftest.py); an admission writes one record and returns
    Lean's result."""
    import os
    assert os.environ.get("VE_ENGLISH_COMPARATOR") in ("1", "0")
    log = tmp_path / "records.jsonl"
    monkeypatch.setenv("VE_ENGLISH_COMPARATOR", "1")
    monkeypatch.setenv("VE_SHADOW_LOG", str(log))
    env = Environment(fixtures.F())
    assert EN.parse_english(env, "Legacy is deployed.").formulas
    [record] = [json.loads(line) for line in log.read_text().splitlines()]
    assert record["lean"]["status"] == "one" and record["classes"] == []
