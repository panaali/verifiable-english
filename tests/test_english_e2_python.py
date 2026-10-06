"""Python producer behavior needed by the E2 overlay relay (spec 2.8, 8.11)."""

import pytest

from conformance import english_lean_s3_fixtures as fixtures
from ve import Environment
from ve.english import EnglishVocabulary
from ve.english_grammar import export
from ve.errors import VEError


def _overlay(env, *, sorts=None, predicates=None, constants=None):
    return {
        "format": "ve.english-vocabulary@1",
        "environment_id": env.environment_id,
        "sorts": sorts or {},
        "predicates": predicates or {},
        "constants": constants or {},
    }


@pytest.mark.parametrize("site", ("O1", "O2", "O3"))
def test_overlay_refusals_can_be_deferred_for_lean_admission(site):
    raw = fixtures.FR() if site == "O2" else fixtures.F()
    predicates = raw["vocabulary"]["predicates"]
    if site == "O1":
        predicates["inspected"] = {
            "arguments": ["service"], "description": "Inspected.",
            "verbalisation": "{0} is inspected",
        }
        name, wording = "inspected", "{0} is reviewed"
    elif site == "O2":
        predicates["hazard"] = {
            "arguments": ["action", "harm"], "description": "Hazard.",
            "verbalisation": "{0} endangers {1}",
        }
        name, wording = "hazard", "{0} risks {1}"
    else:
        predicates["stable"] = {
            "arguments": ["service"], "description": "Stable.",
            "verbalisation": "{0} is stable",
        }
        name, wording = "stable", "{0} never fails"
    env = Environment(raw)
    overlay = _overlay(env, predicates={name: {"verbalisation": wording, "suggested": False}})
    expected = {"O1": "Duplicate English wording", "O2": "reuses a risk@0 wording",
                "O3": "template linter"}[site]
    with pytest.raises(VEError, match=expected):
        EnglishVocabulary(env, vocabulary=overlay)

    words = EnglishVocabulary(env, vocabulary=overlay, _defer_overlay_refusals=True)
    fallback = f'{{0}} is classified as "{name}"' if site != "O2" else (
        '{0} has the recorded relation "hazard" to {1}')
    assert words.predicates[name] == fallback
    assert export(words)["environment_id"] == words.env.environment_id


def test_deferred_overlay_refusals_do_not_skip_display_environment_validation():
    env = Environment(fixtures.FA())
    overlay = _overlay(env, predicates={"available": {
        "verbalisation": "{0} can use {1}", "suggested": False,
    }})
    with pytest.raises(VEError, match="AlternativesVerbalisation"):
        EnglishVocabulary(env, vocabulary=overlay, _defer_overlay_refusals=True)


def test_deferred_overlay_refusals_still_require_suggested_consent():
    env = Environment(fixtures.F())
    overlay = _overlay(env, predicates={"reviewed": {
        "verbalisation": "{0} is reviewed", "suggested": True,
    }})
    with pytest.raises(VEError, match="accept-suggested-vocabulary"):
        EnglishVocabulary(env, vocabulary=overlay, _defer_overlay_refusals=True)


def test_argument_failure_text_preserves_prover_status(monkeypatch):
    from types import SimpleNamespace
    from ve import Const, Document, Unary
    from ve import english, entailment
    from ve.errors import SyntaxError as VESyntaxError

    env = Environment(fixtures.F())
    document = Document((Unary("deployed", Const("legacy")),
                         Unary("reviewed", Const("legacy"))))
    monkeypatch.setattr(english, "_parse_english_document",
                        lambda *_args, **_kwargs: (document, "source", None, (1,)))
    monkeypatch.setattr(entailment, "prove_entailment",
                        lambda *_args, **_kwargs: SimpleNamespace(status="Unknown"))
    with pytest.raises(VESyntaxError, match="earlier premises: Unknown"):
        english.parse_english_argument(env, "source")
