"""English E2.6: where Lean's English reader refused an environment or a text that Python's reader admitted, found
by the corpus A/B under Lean authority, Lean now reads it as Python did (docs/lean-first/e2/E2.6.md)."""
from __future__ import annotations

import pytest

from tests.test_norms import environment, permission
from ve.backends import english_lean, relay
from ve.english import EnglishVocabulary, _python_reading, parse_english
from ve.errors import AmbiguousDerivation, SyntaxError as VESyntaxError

LEAN = english_lean.ROOT / "lean/.lake/build/bin/ve_service"
pytestmark = pytest.mark.skipif(not LEAN.exists(), reason="the Lean service has not been built")


def test_a_declared_wording_with_an_apostrophe_is_read_as_python_reads_it():
    """`a system prompt's existence-or-content` (the constitution pilots): the apostrophe is a word character, so the
    wording lexes and passes V3, and a text that uses it is read; an apostrophe in an undeclared word has no reading,
    with Lean's diagnosis rather than a refused character."""
    env = environment({"deceive_permitted": permission("allow", act="{0} deceive {1} about a prompt's content",
                                                       args=("agent", "user"))}, sorts=("agent", "user"))
    text = "For every agent, for every user, that agent may deceive that user about a prompt's content."
    words = EnglishVocabulary(env)
    assert parse_english(env, text).formulas == _python_reading(env, text, words, {}).document.formulas
    with pytest.raises(VESyntaxError, match="has no reading with the current vocabulary") as caught:
        parse_english(env, "Every agent is Bob's.")
    assert caught.value.span.start < caught.value.span.end


def test_a_generated_soft_frame_is_read_with_its_decision_predicates():
    """The soft route's E′ (`SoftEnvironment(prime, generated=True)`) declares `soft__` decision predicates that a
    submitted environment may not; the relay says so (`generated`), and Lean's boundary reads it as the soft route
    reads a generated frame. Without the flag, or with it set to anything but `true`, the boundary refuses it."""
    from tests.test_soft_norms_lean import env, ranks, should
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    frame = SoftNormDocument(SoftEnvironment(env(ranks(["a", "b"]))), [should("a", "x_required", True)]).extended_env
    assert "soft__excepted__a" in frame.predicates
    text = "Every assistant must do x."
    assert [type(f).__name__ for f in parse_english(frame, text).formulas] == ["Forall"]
    case = english_lean.request(frame, text, EnglishVocabulary(frame), {})
    assert case["generated"] is True
    unflagged = {k: v for k, v in case.items() if k != "generated"}
    assert relay.rows("english.read", [unflagged])[0]["error"] == "InvalidInput: invalid soft name soft__excepted__a"
    for value in (False, 1, "true", [], {}):
        assert relay.rows("english.read", [{**case, "generated": value}])[0]["error"] == \
            "InvalidInput: generated is true when present"
    plain = english_lean.request(env_plain := SoftEnvironment(env(ranks(["a", "b"]))), text,
                                 EnglishVocabulary(env_plain), {})
    assert "generated" not in plain
    # Under `readings@1` the readings decoder checks the soft frame too, and reads the generated frame alike.
    layered = SoftNormDocument(SoftEnvironment(env(ranks(["a", "b"]), profiles=("norms@0", "readings@1",
                                                                                 "soft-norms@0"))),
                               [should("a", "x_required", True)]).extended_env
    assert "readings@1" in layered.to_dict()["profiles"]
    assert len(parse_english(layered, text).formulas) == 1


def test_two_modal_predicates_may_share_their_modal_form():
    """Two permissions with the act `{0} unlock {1}` both select `{0} may unlock {1}` (their one honest wording):
    the environment is read, and a sentence using the shared wording is refused by both readers, Lean finding its
    two derivations. Two ordinary predicates with one wording stay a V4 failure (LexiconFixtures)."""
    env = environment({"operator_unlock_permitted": permission("allow", act="{0} unlock {1}",
                                                               args=("operator", "constraint")),
                       "user_unlock_permitted": permission("allow", act="{0} unlock {1}", args=("user", "constraint")),
                       "hard": {"arguments": ["constraint"], "description": "hard", "verbalisation": "{0} is hard"}},
                      sorts=("operator", "user", "constraint"))
    words = EnglishVocabulary(env)
    assert words.predicates["operator_unlock_permitted"] == words.predicates["user_unlock_permitted"]
    assert len(parse_english(env, "Every constraint is hard.").formulas) == 1
    shared = "For every operator, for every constraint, that operator may unlock that constraint."
    with pytest.raises(AmbiguousDerivation):
        parse_english(env, shared)
    with pytest.raises(VESyntaxError, match="more than one meaning"):
        _python_reading(env, shared, words, {})
