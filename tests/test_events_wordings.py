"""et-5, T9: who judges which `events@0` wording (events-time-causation plan 2.7, spec 2).

The profile wordings, `before`'s "{0} is before {1}" and the two link forms, are fixed by the profile and checked by
Lean, so the author lint (`ve/english.py`) does not judge them: their wordings are the source-word catalogue's `fixed`
rows (`lean/VE/EnglishGrammar/SourceWords.lean`, read through `ve/english_grammar/source_words.json`). Role wordings
are the author's verb phrases and stay under the lint. The twelve source words of 2.7 are refused in authored text
with their advice (Lean's `advice`, pinned by `SourceWordsExamples.lean`)."""
from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path

from tests.test_events_answer import LINKS, rich_case
from tests.test_norm_defaults_three_way import lean_executable  # noqa: F401  (the route fixture)
from ve import events
from ve.english import lint_english_vocabulary
from ve.english_grammar import source_words
from ve.environment import Environment

PROFILE_WORDINGS = ("before", *LINKS)
SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec" / "events-time-causation.md"
TWELVE = ("until", "by", "within", "during", "while", "since", "always", "eventually", "whenever", "resulted in",
          "led to", "caused")


def _issues(environment):
    """The author lint's codes per predicate, over the projection of an environment Lean's route accepts."""
    issues = lint_english_vocabulary(Environment(environment, _validated_projection=True))
    out = {}
    for issue in issues:
        name = issue.path.split("/")[3]
        out.setdefault(name, set()).add(issue.code)
    return out


def _environment(shared=False, **roles):
    """The rich fixture's environment, with one contributed link unless `shared` (two links of one form share its
    wording), and `roles` rewording predicates."""
    environment = deepcopy(rich_case()["environment"])
    if not shared:
        del environment["vocabulary"]["predicates"]["contributed_to_stay"]
        environment["events"]["links"] = [link for link in environment["events"]["links"]
                                          if link["predicate"] != "contributed_to_stay"]
    for name, wording in roles.items():
        environment["vocabulary"]["predicates"][name]["verbalisation"] = wording
    return environment


def _without_block(environment):
    environment = deepcopy(environment)
    del environment["events"]
    environment["profiles"] = [p for p in environment["profiles"] if p != "events@0"]
    return environment


def test_the_profile_wordings_are_not_judged_by_the_author_lint():
    """With the block, `before`'s and the links' wordings have no issue. Without it, the lint judges them as measured
    in phase 1 (PH2; spec 2): `before` BINARY_AUXILIARY, "contributed to" BINARY_CONVERSE and BINARY_VERB, "was
    necessary for" BINARY_AUXILIARY, BINARY_CONVERSE and LOGICAL_WORD."""
    environment = _environment()
    assert not set(_issues(environment)) & {"before", "contributed_to", "necessary_for"}
    judged = _issues(_without_block(environment))
    assert judged["before"] == {"BINARY_AUXILIARY"}
    assert judged["contributed_to"] == {"BINARY_CONVERSE", "BINARY_VERB"}
    assert judged["necessary_for"] == {"BINARY_AUXILIARY", "BINARY_CONVERSE", "LOGICAL_WORD"}


def test_two_links_sharing_a_wording_keep_duplicate_template():
    """The exemption lifts shape checks only: two contributed links share "{0} contributed to {1}", and each keeps
    DUPLICATE_TEMPLATE, as without the block."""
    shared = _issues(_environment(shared=True))
    assert shared["contributed_to"] == shared["contributed_to_stay"] == {"DUPLICATE_TEMPLATE"}
    assert "necessary_for" not in shared


def test_role_wordings_stay_under_the_author_lint():
    """T9 (spec 2.1): the lint accepts "{0} happens on {1}", "occurs on", "begins on" and "ends on", and refuses "{0}
    is committed on {1}", "was committed on" and "is dissolved on" (BINARY_AUXILIARY), with the block as without it;
    all pass Lean's shape check (`roleWordingOk`)."""
    for wording in ("{0} happens on {1}", "{0} occurs on {1}", "{0} begins on {1}", "{0} ends on {1}"):
        # The fixture's `stay_begins` and `stay_ends` already use the last two: only that collision is reported.
        assert _issues(_environment(happens_on=wording)).get("happens_on", set()) <= {"DUPLICATE_TEMPLATE"}, wording
    for wording in ("{0} is committed on {1}", "{0} was committed on {1}", "{0} is dissolved on {1}"):
        for environment in (_environment(happens_on=wording), _without_block(_environment(happens_on=wording))):
            assert "BINARY_AUXILIARY" in _issues(environment).get("happens_on", set()), wording


def test_a_link_with_another_wording_is_still_judged():
    """Only a link's own form's fixed wording is exempt: a contributed link worded as the necessary form, or as
    `alternatives@0`'s "{0} leads to {1}" (D11), is judged like any declared wording."""
    for wording in ("{0} was necessary for {1}", "{0} leads to {1}"):
        environment = _environment(contributed_to=wording)
        assert _issues(environment).get("contributed_to") == _issues(_without_block(environment)).get("contributed_to")
    assert "BINARY_AUXILIARY" in _issues(_environment(contributed_to="{0} was necessary for {1}"))["contributed_to"]


def _spec_advice():
    """Spec 2.5's table: each pattern's leading words and its quoted advice."""
    section = SPEC.read_text().split("### 2.5 Authored text")[1].split("The link wordings are disjoint")[0]
    rows = {}
    for line in section.splitlines():
        if line.startswith("| `"):
            patterns, advice = line.strip().strip("|").split(" | ")[:2]
            for pattern in re.findall(r"`([a-z ]+?)(?: <|`)", patterns):
                rows[pattern.strip()] = advice.strip().strip('"')
    return rows


def test_the_advice_is_spec_2_5_s():
    """Each authored refusal's advice is spec 2.5's text for its pattern, word for word."""
    spec = _spec_advice()
    rows = [r for r in source_words()["rows"] if r["profile"] == "events@0" and r["frame"] == "authored"]
    assert {r["word"]: r["kind"]["advice"] for r in rows} == {word: spec[word] for word in TWELVE}


def test_the_fixed_rows_are_read_from_leans_catalogue():
    """The exemption reads Lean's `fixed` rows (frames `before`, `link contributed`, `link necessary`); the twelve
    source words have their authored-text refusal rows with advice and a rewrite."""
    rows = [r for r in source_words()["rows"] if r["profile"] == "events@0"]
    fixed = {r["frame"]: r["kind"]["wording"] for r in rows if r["kind"]["type"] == "fixed"}
    assert fixed == {"before": "{0} is before {1}", "link contributed": "{0} contributed to {1}",
                     "link necessary": "{0} was necessary for {1}"}
    refused = [r for r in rows if r["frame"] == "authored"]
    assert tuple(r["word"] for r in refused) == TWELVE
    assert all(r["kind"]["type"] == "refuse" and r["kind"]["advice"] and r["kind"]["rewrite"] for r in refused)


def test_the_relay_s_english_vocabulary_exempts_the_profile_wordings(lean_executable):
    """Through `ve.events.english`: Lean's route accepts the document, then its vocabulary leaves the profile wordings
    unjudged and keeps judging a role wording."""
    case = rich_case()
    issues = {(i.path.split("/")[3], i.code) for i in events.english(case).issues}
    assert {(name, code) for name, code in issues if name in PROFILE_WORDINGS} == {
        ("contributed_to", "DUPLICATE_TEMPLATE"), ("contributed_to_stay", "DUPLICATE_TEMPLATE")}
    committed = deepcopy(case)
    committed["environment"]["vocabulary"]["predicates"]["happens_on"]["verbalisation"] = "{0} is committed on {1}"
    assert "happens_on" in {i.path.split("/")[3] for i in events.english(committed).issues}

