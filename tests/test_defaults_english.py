"""The English of answers that hold unless an exception applies (defeasible plan 2.8, spec 4; batch DF-1b, df-1bb).

One fixture per sentence form: DE1, DE1′, DE2, DE2·u, DE2′, DE2′·u, DE3, DE4, DE4·u, DE6, DE6′ with DE11, DE7 with
DE7a, DE7a·u, DE7b and DE7b·u, and DE12. The genuine ones go through `ve.defaults.ask` (Lean's rows); the variants
render a row of the shape Lean gives on the plan's fixture documents (`ve.defaults_english.sentences`, which binds
every name a label gives to the request). Lean selects every form: the tests change Lean's `form`, `basis`,
`forced` and `deciders` and the sentence follows them.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ve import defaults_english
from ve.document import main
from ve.errors import CheckerUnavailable
from tests.test_defaults_lean import DOCS, HOLISTIC, STRICT, UNLESS_URGENT, X_ALL, asked, env, rule, un

R1_ASSISTANT = ("This assumes that the exception to rule r1 does not apply. The assistant decides where it applies; "
                "the text names no case.")
EVERY = "Every assistant must do x"
CONFLICT = ("Rules r1 and r2 conflict here unless one of them gives way: e0 must do x, and e0 must not do x. The text "
            "ranks neither above the other, and names no exception that applies here.")
NOT_ALL = ["not", X_ALL]
SOMEONE = [["exists", "assistant", ["top"]]]


def english(monkeypatch, name, conclusion=X_ALL, premises=()):
    out, _ = asked(monkeypatch, name, conclusion, premises)
    return out["english"]


def case(name, **extra):
    environment, norms = DOCS[name]
    return {"environment": environment, "norms": norms, "conclusion": X_ALL, **extra}


def follows(basis="needs", form="short", assumptions=("default:exception:r1",)):
    return {"verdict": "FOLLOWS", "basis": basis, "form": form, "assumptions": list(assumptions),
            "deciders": ["assistant"]}


# -- genuine answers through Lean

def test_de1_and_de2_short_form(monkeypatch):
    assert english(monkeypatch, "alpha") == [
        f"Unless an exception applies, the conclusion follows: {EVERY}.", R1_ASSISTANT]


def test_de1_long_and_de2_conditions(monkeypatch):
    assert english(monkeypatch, "beta", UNLESS_URGENT) == [
        "Under the assumptions listed below, the conclusion follows: For every assistant, if it is not the case that "
        "that assistant is urgent, then that assistant must do x.",
        "This assumes that the exception to rule r1 applies only where the text says it does: that assistant is "
        "urgent. The assistant decides any other case."]


def test_de3_switch(monkeypatch):
    assert english(monkeypatch, "epsilon") == [
        f"Under the assumptions listed below, the conclusion follows: {EVERY}.", R1_ASSISTANT,
        "This assumes that the user has not turned rule r1 off."]


def test_de4_ranking(monkeypatch):
    shown = english(monkeypatch, "delta")
    assert shown[0] == f"Under the assumptions listed below, the conclusion follows: {EVERY}."
    assert shown[-1] == ("This assumes that, on do x, the helpfulness consideration does not outweigh the safety "
                         "consideration. The assistant decides where it does.")


def test_de6_no_exception_holds(monkeypatch):
    """DF-α, with an assistant, asked whether not every assistant must do x: the countermodel has no exception
    (`forced` empty), so DE6."""
    assert english(monkeypatch, "alpha", NOT_ALL, SOMEONE) == [
        "Even if no exception applies, the conclusion does not follow. It fails here: e0 is an assistant."]


def test_de6_long_and_de11_at_beta_one(monkeypatch):
    """DF-β (i): the text's own exception holds at the situation, so DE6′ and DE11, never DE6."""
    assert english(monkeypatch, "beta") == [
        "Even if no exception applies beyond those the text states, the conclusion does not follow. It fails here: "
        "e0 is an assistant; e0 is urgent.",
        "The text's own exception to rule r1 applies here: e0 is urgent."]


def test_de11_once_per_forced_entry_in_lean_order(monkeypatch):
    shown = english(monkeypatch, "beta2")
    assert shown[1:] == ["The text's own exception to rule r1 applies here: e0 is urgent.",
                         "The text's own exception to rule r2 applies here: e0 is urgent."]


def test_de7_and_de7a(monkeypatch):
    assert english(monkeypatch, "gamma") == [CONFLICT, "Which rule gives way is left to the assistant."]


def test_de7b_two_deciders(monkeypatch):
    assert english(monkeypatch, "gamma'") == [
        CONFLICT, "Whether rule r1 gives way is left to the assistant, and whether rule r2 gives way is left to "
                  "the operator."]


# -- the variants, from rows of Lean's shape

def test_de12_after_the_assumptions_only_when_unsettled():
    assert defaults_english.sentences(case("alpha"), follows("unsettled")) == [
        f"Unless an exception applies, the conclusion follows: {EVERY}.", R1_ASSISTANT,
        "Whether it also holds without these assumptions was not checked."]
    assert defaults_english.sentences(case("alpha"), follows("needs"))[-1] == R1_ASSISTANT


def test_form_is_lean_s():
    """The same assumptions under Lean's other `form` give the other head: Python never chooses it."""
    short, long = (defaults_english.sentences(case("epsilon"), follows(form=f)) for f in ("short", "long"))
    assert short[0].startswith("Unless an exception applies,") and long[0].startswith("Under the assumptions")
    assert short[1:] == long[1:]


def test_strict_basis_uses_lean_deciders():
    assert defaults_english.sentences(case("zeta"), follows("strict", "short", ())) == [
        "This holds whatever the assistant decides."]
    assert defaults_english.sentences(case("zeta"), {**follows("strict", "short", ()),
                                                      "deciders": ["unstated"]}) == [
        "This holds whatever is decided where the text names no decider."]
    assert defaults_english.sentences(case("zeta"), {**follows("strict", "short", ()),
                                                      "deciders": ["assistant", "unstated"]}) == [
        "This holds whatever the assistant decides, and whatever is decided where the text names no decider."]
    assert defaults_english.sentences(case("zeta"), {**follows("strict", "short", ()),
                                                      "deciders": ["assistant", "operator"]}) == [
        "This holds whatever the assistant and the operator decide."]


def _unstated(sufficient=()):
    environment = env()
    return {"environment": environment, "conclusion": X_ALL,
            "norms": [rule("r1", "x_required", True, sufficient=sufficient, decider="unstated")]}


def test_de2_unstated():
    assert defaults_english.sentences(_unstated(), follows())[1] == (
        "This assumes that the exception to rule r1 does not apply. The text names no case where it applies, and no "
        "one who decides.")


def test_de2_conditions_unstated():
    two = env(base=["calm", "urgent"])
    request = {**_unstated([un("calm"), un("urgent")]), "environment": two}
    assert defaults_english.sentences(request, follows(form="long"))[1] == (
        "This assumes that the exception to rule r1 applies only where the text says it does: that assistant is "
        "calm, or that assistant is urgent. The text names no one who decides any other case.")


def test_de2_document_decider_stands_for_unstated():
    """A rule that names no decider has the document's (`exception_decider`), as Lean's `exceptionDecider`."""
    request = _unstated()
    del request["norms"][0]["norm"]["exception"]["decided_by"]
    request["environment"]["vocabulary"]["soft"] = {**STRICT, "exception_decider": "operator"}
    assert defaults_english.sentences(request, follows())[1].endswith(
        "The operator decides where it applies; the text names no case.")


def test_de4_unstated():
    unstated = {**HOLISTIC, "outranking": {"mode": "holistic", "decided_by": "unstated"}}
    request = {**case("delta"), "environment": env(unstated)}
    shown = defaults_english.sentences(request, follows(form="long", assumptions=[
        "default:ranking:helpfulness:safety:x_permitted"]))
    assert shown[1] == ("This assumes that, on do x, the helpfulness consideration does not outweigh the safety "
                        "consideration. The text names no one who decides where it does.")


def _collision(deciders):
    model = {"complete": True, "constants": {}, "domains": {"assistant": ["e0"]}, "relations": {}}
    request = {**case("gamma"), "kind": "defaults-coherence", "collision": {"model": model, "filling": {},
                                                                            "rules": ["r1", "r2"]}}
    row = {"verdict": "COLLISION", "pairs": [{"rules": ["r1", "r2"], "status": "collision"}],
           "collision": {"rules": ["r1", "r2"], "tuple": ["e0"], "deciders": deciders}}
    return defaults_english.sentences(request, row)


@pytest.mark.parametrize("deciders, sentence", [
    (["unstated"], "The text names no one who decides which rule gives way."),
    (["operator", "unstated"], "Whether rule r1 gives way is left to the operator; the text names no one who decides "
                               "whether rule r2 gives way."),
    (["unstated", "operator"], "Whether rule r2 gives way is left to the operator; the text names no one who decides "
                               "whether rule r1 gives way."),
    (["user"], "Which rule gives way is left to the user."),
    (["user", "operator"], "Whether rule r1 gives way is left to the user, and whether rule r2 gives way is left to "
                           "the operator."),
])
def test_de7_decider_sentence_is_lean_s_deciders(deciders, sentence):
    assert _collision(deciders) == [CONFLICT, sentence]


@pytest.mark.parametrize("verdict", ["COHERENT", "UNKNOWN"])
def test_no_collision_no_de7(verdict):
    request = {**case("gamma"), "kind": "defaults-coherence"}
    assert defaults_english.sentences(request, {"verdict": verdict, "pairs": []}) == []


def test_an_unknown_answer_shows_no_default_sentence():
    assert defaults_english.sentences(case("alpha", kind="defaults-certificate"),
                                      {"verdict": "UNKNOWN", "reason": "no certificate"}) == []


# -- a label the request cannot give is refused, on both sides of each check

@pytest.mark.parametrize("name, label", [
    ("alpha", "default:exception:r1"),
    ("epsilon", "default:switch:r1:user"),
    ("delta", "default:ranking:helpfulness:safety:x_permitted"),
    ("delta", "default:ranking:safety:helpfulness:x_required"),
])
def test_a_label_the_request_gives_is_rendered(name, label):
    assert len(defaults_english.sentences(case(name), follows(form="long", assumptions=[label]))) == 2


@pytest.mark.parametrize("name, label", [
    ("alpha", "default:exception:r9"),                 # no such rule
    ("zeta", "default:exception:r0"),                  # a strict rule
    ("alpha", "default:exception"),                    # no rule
    ("alpha", "default:exception:r1:x"),               # one name too many
    ("alpha", "default:waiver:r1"),                    # no such kind
    ("epsilon", "default:switch:r1:operator"),         # a party that cannot turn the rule off
    ("epsilon", "default:switch:r1"),                  # no party
    ("epsilon", "default:switch:r9:user"),             # no such rule
    ("delta", "default:ranking:helpfulness:care:x_permitted"),  # a rank the source does not declare
    ("delta", "default:ranking:helpfulness:safety:urgent"),     # not a declared act
    ("delta", "default:ranking:helpfulness:safety"),            # no act
])
def test_a_label_the_request_cannot_give_is_refused(name, label):
    with pytest.raises(CheckerUnavailable, match="not an answer to the defaults request"):
        defaults_english.sentences(case(name), follows(form="long", assumptions=[label]))


def test_a_forced_rule_the_request_lacks_is_refused():
    request = case("beta", model={"model": {"domains": {"assistant": ["e0"]}, "relations": {}}, "filling": {}})
    row = {"verdict": "DOES-NOT-FOLLOW", "forced": [{"rule": "r9", "condition": 0, "tuple": ["e0"]}]}
    with pytest.raises(CheckerUnavailable):
        defaults_english.sentences(request, row)


# -- the non-wordings (spec 4)

def test_no_label_prefix_marker_or_by_default(monkeypatch):
    shown = []
    for name, conclusion in [("alpha", X_ALL), ("beta", X_ALL), ("beta", UNLESS_URGENT), ("gamma", X_ALL),
                             ("delta", X_ALL), ("epsilon", X_ALL)]:
        shown += english(monkeypatch, name, conclusion)
    shown += english(monkeypatch, "alpha", NOT_ALL, SOMEONE)
    text = " ".join(shown).lower()
    assert not any(word in text for word in ("default:", "soft__", "unsaid__", "by default"))
    long_or_forced = english(monkeypatch, "epsilon") + english(monkeypatch, "beta")
    assert not any(s.startswith(("Unless an exception applies", "Even if no exception applies,"))
                   for s in long_or_forced)


# -- P-3 (plan 4.2): u0073.s05, one default rule with three stated exception conditions, through the flag

P3 = Path(__file__).resolve().parents[1] / "docs/defeasible/df-1bb/probe"
CLASSIFIED = 'that instruction is classified as "{}"'


def _p3(capsys, question):
    assert main(["readings", str(P3 / "p3-force-u0073-s05.ve.md"), "--conclusion",
                 str(P3 / f"question-p3-{question}.json"), "--assume-no-exception"]) == 0
    return json.loads(capsys.readouterr().out)


def test_p3_follows_long_listing_the_three_conditions(capsys):
    out = _p3(capsys, "none-holds")
    assert (out["answer"]["verdict"], out["answer"]["basis"], out["answer"]["form"]) == ("FOLLOWS", "needs", "long")
    head, assumed = out["english"]
    assert head.startswith("Under the assumptions listed below, the conclusion follows: ")
    conditions = ", or ".join(CLASSIFIED.format(p) for p in ("unsafe", "unethical", "against_guidelines"))
    assert assumed == ("This assumes that the exception to rule comply applies only where the text says it does: "
                       f"{conditions}. The text names no one who decides any other case.")


def test_p3_fails_where_a_condition_holds_naming_it(capsys):
    out = _p3(capsys, "always")
    [entry] = out["answer"]["forced"]
    condition = ("unsafe", "unethical", "against_guidelines")[entry["condition"]]
    assert out["english"][0].startswith("Even if no exception applies beyond those the text states, the conclusion "
                                        "does not follow. It fails here: ")
    assert out["english"][1:] == [
        f'The text\'s own exception to rule comply applies here: e0 is classified as "{condition}".']
