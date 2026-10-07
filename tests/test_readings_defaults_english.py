"""The English of readings under unspecified defaults (docs/spec/readings-defaults.md 2.1 to 2.5): the new wordings
E30, E31, E32 and R7, the reused filled-gap and pair sentences, and the `<reading>` slot of review A4, each through
W7's all-derivations gate (`ve/readings_s2_english.py`)."""
from __future__ import annotations

import re

import pytest

from ve.errors import VEError
from ve.readings_s2_english import (DEFAULTS, PROVIDED, S2A, TEMPLATES, Slots, checked_alone, derivations,
                                    each_alone, every_result, every_result_of_sentence, gap_sentences, gated,
                                    named_result, pair_line, result_sentence, sentence_slots)

EVERY = "*Every agent must help each user*"
ASKING = "*Every agent must help each user, if that user asks that agent*"
CONCLUSION = "*For every agent, for every user, that agent must help that user.*"
SITUATION = "a is an agent; u is a user"
CLAUSE = "a must help u"
PAIR = "Whenever an agent must help a user, it may help that user."
SLOTS = Slots(numbers={"1", "2", "3"}, readings={EVERY, ASKING, "*must*", "*should*"}, conclusions={CONCLUSION},
              situations={SITUATION}, clauses={CLAUSE, "u must help a"})
CERTIFIED = ("conflict_free", "follows", "inconsistent")
SITUATED = ("countermodel", "conflict", "premise_model")


def test_the_new_wordings_pass_the_gate_with_their_exact_text():
    assert every_result_of_sentence(2, "conflict_free", SLOTS) == (
        "Under every reading of sentence 2, no two rules on the same act contradict each other.")
    assert checked_alone(3, SLOTS) == ("Sentence 3 was checked by itself, with the terms its readings declare; VE did "
                                       "not check it together with the other sentences.")
    assert each_alone(SLOTS) == "Each open sentence below was checked by itself, under each of its readings."
    assert named_result([(1, ASKING)], "undecided", SLOTS, clause=CLAUSE) == (
        f"Read sentence 1 as {ASKING}: the text does not say whether a must help u: no rule decides this situation.")
    assert named_result([(1, ASKING)], "countermodel", SLOTS, situation=SITUATION, gaps=[(CLAUSE, False)]) == (
        f"Read sentence 1 as {ASKING}: the conclusion does not follow. It fails here: a is an agent; u is a user. "
        "Here the text does not say whether a must help u; this situation answers 'no'.")
    assert pair_line(PAIR, SLOTS) == PAIR


def test_every_instance_has_exactly_one_derivation_its_own():
    """Instances of every new template and of S2a's, over every result and with 0, 1 and 2 filled gaps after a
    shown situation, with reading names in the sentence form of review A4: each is read by exactly one registered
    template, the one it was built from."""
    built = [(checked_alone(1, SLOTS), "E31"), (each_alone(SLOTS), "E32"), (pair_line(PAIR, SLOTS), "P1")]
    for kind in CERTIFIED:
        built.append((every_result_of_sentence(1, kind, SLOTS, conclusion=CONCLUSION), "E30"))
        built.append((every_result(1, kind, SLOTS, conclusion=CONCLUSION), "E26"))
        built.append((every_result(2, kind, SLOTS, conclusion=CONCLUSION), "E10"))
    for kind in SITUATED:
        for gaps in ((), ((CLAUSE, True),), ((CLAUSE, False), ("u must help a", True))):
            built.append((named_result([(1, EVERY), (2, "*must*")], kind, SLOTS, situation=SITUATION, gaps=gaps),
                          "E12"))
    built.append((named_result([(1, ASKING)], "undecided", SLOTS, clause=CLAUSE), "E12"))
    for text, name in built:
        assert [d[0] for d in derivations(text, SLOTS)] == [name], text


def test_the_new_templates_are_registered_beside_s2a():
    assert set(DEFAULTS) == {"E30", "E31", "E32", "P1"} and set(DEFAULTS) <= set(TEMPLATES)
    assert not set(DEFAULTS) & set(S2A)


@pytest.mark.parametrize("build", [
    lambda: every_result_of_sentence(1, "countermodel", SLOTS),             # E30 claims every reading: certificates
    lambda: result_sentence("follows", conclusion=CONCLUSION, gaps=[(CLAUSE, True)]),  # gaps follow a situation
    lambda: result_sentence("undecided", clause=CLAUSE, gaps=[(CLAUSE, True)]),
    lambda: gap_sentences([(CLAUSE, 1)]),                                   # bool, never an int
    lambda: gap_sentences([("", True)]),
    lambda: named_result([(1, ASKING)], "undecided", SLOTS, clause="b must help v"),  # not a clause shown
    lambda: named_result([(1, ASKING)], "countermodel", SLOTS, situation=SITUATION, gaps=[("b must help v", True)]),
    lambda: checked_alone(9, SLOTS),                                        # not a sentence number
    lambda: named_result([(1, "reading 1")], "conflict_free", SLOTS),       # "reading <i>" is no slot value
    lambda: pair_line("Wherever an agent must help a user, it may help that user.", SLOTS),
])
def test_what_the_gate_refuses(build):
    with pytest.raises(VEError):
        build()


@pytest.mark.parametrize("hidden", ["unsaid__help_required", "unsaid--help-required", "ve__here", "may not"])
def test_reserved_names_are_never_shown(hidden):
    slots = Slots(numbers={"1"}, readings={EVERY}, clauses={f"a {hidden} u"})
    with pytest.raises(VEError, match="generated name"):
        named_result([(1, EVERY)], "undecided", slots, clause=f"a {hidden} u")
    with pytest.raises(VEError, match="generated name"):
        gated("P1", f"Whenever {hidden}.", slots)


def test_sentence_slots():
    """Review A4: the candidate's own sentence in italics without its final period; a candidate without content has
    no name; two candidates shown by one sentence are refused."""
    assert sentence_slots("rs_1", ["Every agent must help each user.", None, "A must B. It is an exception to rule x."]) \
        == [EVERY, None, "*A must B. It is an exception to rule x*"]
    with pytest.raises(VEError, match="two readings of rs_1 are shown by the same sentence"):
        sentence_slots("rs_1", ["Every agent must help each user.", "Every agent must help each user."])
    with pytest.raises(VEError, match="the same sentence"):
        sentence_slots("rs_1", ["Every agent must help each user.", "Every agent must help each user"])


def _pair_frame():
    from ve.environment import Environment
    from ve.profiles import LANGUAGE, SPEC_REVISION
    predicates = {
        "asks": {"arguments": ["user", "agent"], "description": "{0} asks {1}"},
        "help_required": {"arguments": ["agent", "user"], "description": "obligation", "regulated": {
            "role": "obligation", "default": "unspecified", "act": "{0} help {1}", "permission": "help_permitted"}},
        "help_permitted": {"arguments": ["agent", "user"], "description": "permission", "regulated": {
            "role": "permission", "default": "unspecified", "act": "{0} help {1}"}}}
    return Environment({"language": LANGUAGE, "spec_revision": SPEC_REVISION,
                        "profiles": sorted({"norm-defaults@0", "norms@0", "readings@1", "relational-fol@0"}),
                        "vocabulary": {"sorts": {s: {"description": s} for s in ("agent", "user")},
                                       "predicates": predicates, "constants": {}}})


def _wording(frame):
    from ve import readings_s2_english
    from ve.readings_s2_wording import S2Wording
    wording = object.__new__(S2Wording)
    wording.E, wording.frame, wording.slots = readings_s2_english, frame, Slots(numbers={"1"})
    return wording


def test_a_used_pair_label_gets_norm_defaults_pair_sentence_as_its_e3_line():
    """F-ND1's conflict answer: `conditional_on: ["unsaid:pair:help_required,help_permitted"]` is worded as E3 with
    norm-defaults 4.1's pair sentence (readings-defaults 2.2, 2.6)."""
    from ve.norm_english import pair_sentence
    frame = _pair_frame()
    wording = _wording(frame)
    # Reused verbatim: norm-defaults' own sentence. (It reads "an user" today: its article rule looks at the first
    # letter only; that is norm-defaults' wording, reported to its owner, not changed here.)
    reused = pair_sentence(frame, "help_required")
    assert reused.startswith("Whenever an agent must help a") and reused.endswith(" user, it may help that user.")
    assert wording.provided(["unsaid:pair:help_required,help_permitted"]) == [PROVIDED, reused]
    assert wording.provided([]) == []


@pytest.mark.parametrize("label", [
    "unsaid:pair:help_required,asks",          # not the declared permission
    "unsaid:pair:help_permitted,help_required",  # a permission is not the pair's obligation
    "unsaid:pair:asks,help_permitted",         # not regulated
    "unsaid:pair:help_required",               # no permission
    "unsaid:pair:,help_permitted",
    "unsaid:pair:nothing,help_permitted",
])
def test_a_pair_label_that_names_no_declared_pair_is_refused(label):
    with pytest.raises(VEError, match="names no declared pair"):
        _wording(_pair_frame()).provided([label])


def test_no_s2_fixture_answer_shows_a_reading_number(tmp_path):
    """Review A4's class: "reading <i>" is never shown. Every report and query sentence of S2a's enumerated fixtures
    M8 and M9, and of the rights fixture M12, names its readings by their sentences or verbs."""
    from tests.test_readings_s2_document import (RIGHTS_ARREST, _claim, _m8, _m9, _query, _report, env_rights,
                                                 every, s2_document)
    lines = []
    for path, conclusion in ((_m8(tmp_path / "m8"), every("avoid_required")),
                             (_m9(tmp_path / "m9"), every("warn_required")),
                             (s2_document(tmp_path / "m12", [("set", "rs9", "u9", [
                                 ("strict", _claim("strict"), "right", None),
                                 ("default", _claim("default"), "right", None)])], raw=env_rights()), RIGHTS_ARREST)):
        lines += _report(path)[0]
        lines += _query(path, conclusion)[1]
    assert any(" as *" in line for line in lines)
    assert not [line for line in lines if re.search(r"\breading [0-9]", line)]
