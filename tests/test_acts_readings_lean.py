"""ap-4: the `act-readings` mode through the service and `ve acts readings` (act-phrases 7, 11.4; plan AP-4 Tests).

Lean lists a phrase's readings under a rule's modal and paraphrases them, and lexes the phrase: token spans in the
phrase's UTF-8 bytes and each act's token indices. These are Lean's answers, relayed by `ve.acts`; the Lean fixtures
are `lean/VE/Acts/RunExamples.lean`. The limits are spec 12's, each on both sides (DRI 2026-11-08 ap-4 item 1).
"""
from __future__ import annotations

import json

import pytest

from tests import lean_routes
from ve import acts
from ve.__main__ import main

pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")


def frame(head, markers=("",), split=(), modifiers=()):
    return {"head": head, "markers": list(markers), "split": list(split), "modifiers": list(modifiers)}


V5 = {"frames": [frame("seek", modifiers=["in"]), frame("enjoy", modifiers=["in"])]}
V8 = {"frames": [frame("participate", ["in"]), frame("enjoy"), frame("share", ["in"])], "adverbs": ["freely"]}
V9 = {"frames": [frame("deprived", ["of"]), frame("denied")], "adverbs": ["arbitrarily"]}
V10 = {"frames": [frame("security", ["in the event of"], ["in the event of"], ["in circumstances"])]}
V11 = {"frames": [frame("take part", ["in"], modifiers=["through"])], "adverbs": ["directly"]}
V12 = {"frames": [frame("form", modifiers=["for"]), frame("join", modifiers=["for"])]}
CITIES = [f"the {n} city" for n in ("first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth")]

# The pilot's phrases (A5, A8 to A12) with their fixed phrases, vocabularies, roles and signs
PILOT = {
    "A5": ("{0} to seek and to enjoy in other countries asylum from persecution", ["other countries"], V5, "plain", True),
    "A8": ("{0} freely to participate in the cultural life of the community, to enjoy the arts and to share in "
           "scientific advancement and its benefits",
           ["the cultural life of the community", "scientific advancement and its benefits"], V8, "plain", True),
    "A9": ("{0} be arbitrarily deprived of their nationality nor denied the right to change their nationality",
           ["the right to change their nationality"], V9, "permission", False),
    "A10": ("{0} to security in the event of unemployment, sickness, disability, widowhood, old age or other lack of "
            "livelihood in circumstances beyond their control", ["other lack of livelihood"], V10, "plain", True),
    "A11": ("{0} to take part in {1} directly or through freely chosen representatives",
            ["freely chosen representatives"], V11, "plain", True),
    "A12": ("{0} to form and to join trade unions for the protection of their interests", [], V12, "plain", True),
}


def ask(phrase, fixed=(), block=None, role="plain", sign=True, form=None):
    block = block or {}
    return acts.readings(phrase, fixed=fixed, frames=block.get("frames", []), adverbs=block.get("adverbs", []),
                         role=role, sign=sign, form=form)


def pilot(name, **overrides):
    phrase, fixed, block, role, sign = PILOT[name]
    return ask(overrides.get("phrase", phrase), fixed, block, overrides.get("role", role), overrides.get("sign", sign))


@pytest.mark.parametrize("name, count", [("A9", 2), ("A10", 2), ("A11", 2), ("A5", 4), ("A8", 4), ("A12", 4)])
def test_the_pilot_phrases_give_the_readings_the_audit_asks_for(name, count):
    found = pilot(name)
    assert found["verdict"] == "LISTED" and len(found["readings"]) == count
    assert "diagnostic" not in found


def test_rs_u055s_phrase_lists_deprivation_only_then_both_acts():
    found = pilot("A9")
    assert [r["paraphrase"] for r in found["readings"]] == [
        "{0} must not be arbitrarily deprived of their nationality, and {0} must not be denied the right to change "
        "their nationality.",
        "{0} must not be arbitrarily deprived of their nationality, and {0} must not be arbitrarily denied the right "
        "to change their nationality."]
    assert [a["act"] for a in found["readings"][1]["acts"]] == [
        "{0} be arbitrarily deprived of their nationality", "{0} be arbitrarily denied the right to change their nationality"]


def test_p11s_answer_has_leans_token_spans_and_indices():
    """AR1's genuine answer: tokens are UTF-8 spans of the phrase; `from` names the tokens each act reads."""
    phrase = PILOT["A11"][0]
    found = pilot("A11")
    texts = [phrase.encode()[a:b].decode() for a, b in found["tokens"]]
    assert texts == ["{0}", "to", "take", "part", "in", "{1}", "directly", "or", "through",
                     "freely chosen representatives"]
    split, whole = found["readings"]
    assert [[texts[i] for i in act["from"]] for act in split["acts"]] == [
        ["{0}", "to", "directly", "take", "part", "in", "{1}"],
        ["{0}", "to", "take", "part", "in", "{1}", "through", "freely chosen representatives"]]
    assert whole["paraphrase"].endswith(", as one act done in any one of these ways (not each way on its own).")


def test_spans_are_bytes_of_the_phrase_as_written():
    phrase = "{0}  to\tseek  asylum’s"
    found = ask(phrase, block={"frames": [frame("seek")]})
    assert found["tokens"] == [[0, 3], [5, 7], [8, 12], [14, 24]]


def test_an_adverb_inside_the_last_joined_item_reads_over_that_item_only():
    phrase = ("{0} to participate in the cultural life of the community, to enjoy the arts and to freely share in "
              "scientific advancement and its benefits")
    found = pilot("A8", phrase=phrase)
    assert len(found["readings"]) == 2
    assert [a["act"] for a in found["readings"][0]["acts"]] == [
        "{0} to participate in the cultural life of the community", "{0} to enjoy the arts",
        "{0} to freely share in scientific advancement and its benefits"]


def test_the_act_phrase_limit_is_400_bytes():
    phrase = "{0} to seek" + " a" * 193 + " ab"
    assert len(phrase.encode()) == 400
    assert ask(phrase, block={"frames": [frame("seek")]})["verdict"] == "LISTED"
    over = ask(phrase + "c", block={"frames": [frame("seek")]})
    assert over == {"verdict": "LIMIT", "tokens": [], "readings": [],
                    "diagnostic": "ResourceLimit: this act phrase is over 400 bytes"}


def test_a_fixed_phrase_is_at_most_300_bytes():
    fixed = "ab" + " a" * 149
    assert len(fixed.encode()) == 300
    found = ask("{0} to seek " + fixed, [fixed], {"frames": [frame("seek")]})
    assert found["verdict"] == "LISTED" and found["tokens"][-1] == [12, 312]
    over = ask("{0} to seek " + fixed + "c", [fixed + "c"], {"frames": [frame("seek")]})
    assert over["verdict"] == "LIMIT" and over["diagnostic"].startswith("ResourceLimit: fixed phrase ")


def test_64_readings_are_listed_and_more_are_a_limit():
    phrase = "{0} to seek and to enjoy asylum" + "".join(" in " + c for c in CITIES[:6])
    listed = ask(phrase, CITIES, V5, role="obligation")
    assert listed["verdict"] == "LISTED" and len(listed["readings"]) == 64
    over = ask(phrase, CITIES, V5, role="permission", sign=False)
    assert over["verdict"] == "LIMIT"
    assert over["diagnostic"] == "ResourceLimit: this act phrase has too many readings to list; split the sentence"


def test_a_saturated_raw_cap_is_a_limit():
    phrase = "{0} to seek and to enjoy asylum" + "".join(" in " + c for c in CITIES)
    found = ask(phrase, CITIES, V5)
    assert found["verdict"] == "LIMIT" and found["readings"] == []


def test_refusals_are_leans_texts():
    assert ask("{0} to seek asylum", block=V5, sign=False)["diagnostic"] == (
        "InvalidInput: this act phrase has no modal word: a plain act with sign false")
    assert pilot("A9", sign=True)["diagnostic"] == (
        "InvalidInput: this act phrase has no reading under the declared frames and its modal words")
    refused = ask("{0} to seek asylum", block={"frames": [frame("seek"), frame("seek")]})
    assert refused["verdict"] == "REFUSED" and refused["diagnostic"] == "InvalidInput: frame 'seek' is declared twice"


def test_the_command_line_prints_leans_answer(tmp_path, capsys):
    block = tmp_path / "acts.json"
    block.write_text(json.dumps({"fixed": PILOT["A11"][1], **V11}))
    assert main(["acts", "readings", PILOT["A11"][0], "--acts", str(block), "--form", "is entitled"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["readings"][0]["paraphrase"].startswith("{0} is entitled to directly take part in {1}, and ")
    assert main(["acts", "readings", PILOT["A11"][0], "--acts", str(block), "--negated"]) == 2
    capsys.readouterr()
