"""et-5, T9: who judges which `events@0` wording (events-time-causation plan 2.7, spec 2).

The profile wordings, `before`'s "{0} is before {1}" and the two link forms, are fixed by the profile and checked by
Lean, so the author lint (`ve/english.py`) does not judge them: their wordings are the source-word catalogue's `fixed`
rows (`lean/VE/EnglishGrammar/SourceWords.lean`, read through `ve/english_grammar/source_words.json`). Role wordings
are the author's verb phrases and stay under the lint. The twelve source words of 2.7 are refused in authored text
with their advice (Lean's `advice`, pinned by `SourceWordsExamples.lean`)."""
from __future__ import annotations

from copy import deepcopy

from tests.test_events_answer import LINKS, rich_case
from tests.test_norm_defaults_three_way import lean_executable  # noqa: F401  (the route fixture)
from ve import events
from ve.english import lint_english_vocabulary
from ve.english_grammar import source_words
from ve.environment import Environment

PROFILE_WORDINGS = ("before", *LINKS)
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


def _environment(**roles):
    environment = deepcopy(rich_case()["environment"])
    for name, wording in roles.items():
        environment["vocabulary"]["predicates"][name]["verbalisation"] = wording
    return environment


def _without_block(environment):
    environment = deepcopy(environment)
    del environment["events"]
    environment["profiles"] = [p for p in environment["profiles"] if p != "events@0"]
    return environment


def test_the_profile_wordings_are_not_judged_by_the_author_lint():
    """With the block, none of `before`'s or the links' wordings has an issue; the same environment without it is
    judged as in phase 1 (PH2): `before` BINARY_AUXILIARY, "contributed to" BINARY_CONVERSE, "was necessary for"
    BINARY_AUXILIARY."""
    environment = _environment()
    assert not set(_issues(environment)) & set(PROFILE_WORDINGS)
    judged = _issues(_without_block(environment))
    assert "BINARY_AUXILIARY" in judged["before"]
    assert "BINARY_CONVERSE" in judged["contributed_to"]
    assert "BINARY_AUXILIARY" in judged["necessary_for"]


def test_role_wordings_stay_under_the_author_lint():
    """T9: "{0} happens on {1}" is accepted; "{0} is committed on {1}" passes Lean's shape check but is refused by
    the lint (BINARY_AUXILIARY), with the block as without it."""
    assert "happens_on" not in _issues(_environment())
    committed = _environment(happens_on="{0} is committed on {1}")
    assert "BINARY_AUXILIARY" in _issues(committed).get("happens_on", set())
    assert "BINARY_AUXILIARY" in _issues(_without_block(committed)).get("happens_on", set())


def test_a_link_with_another_wording_is_still_judged():
    """Only a link's own form's fixed wording is exempt: a contributed link worded as the necessary form, or as
    `alternatives@0`'s "{0} leads to {1}" (D11), is judged like any declared wording."""
    other = _environment(contributed_to="{0} was necessary for {1}")
    assert "BINARY_AUXILIARY" in _issues(other).get("contributed_to", set())
    leads = _environment(contributed_to="{0} leads to {1}")
    assert _issues(leads).get("contributed_to") == _issues(_without_block(leads)).get("contributed_to")


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
    issues = {i.path.split("/")[3] for i in events.english(case).issues}
    assert not issues & set(PROFILE_WORDINGS)
    committed = deepcopy(case)
    committed["environment"]["vocabulary"]["predicates"]["happens_on"]["verbalisation"] = "{0} is committed on {1}"
    assert "happens_on" in {i.path.split("/")[3] for i in events.english(committed).issues}

