"""srccov-rl-news-article-1121: the news-article units tagged 'none: translation omission' and why none is carried.

The source-coverage map (row srccov-news-article-s7-1-1119, pin e53db4e8fc) tags five units of
`usecases/news-article/source.md` 'none: translation omission'. The verify step dropped all five
(docs/infra/srccov-rl-news-article-1121/REPORT.md, table 0):

- S0001 c2, S0010 c2, S0011 c1 need a new predicate in `environment.json`. Every claims.ve predicate
  must have reviewed English wording in `environment.english.json` (tests/test_english.py
  test_reviewed_overlays_preserve_all_historical_views_and_identities). The overlay linter does not
  block a carry: its base shape (ve/printer.py) accepts a present-tense two-place wording such as
  `{0} signals {1}` (not every present-tense wording: it refuses an auxiliary first word and a final
  by/to/of/from/with/for); only the article's past-tense wordings (`{0} signaled {1}`, `{0} was issued
  after {1}`) would need an idiom. What blocks the carry is the review binding: any vocabulary change
  rebinds the overlay digest and drops it to 'unreviewed', and the new `ve/reviewed-overlays.json`
  record needs a reviewer who is not the builder, in a file outside this row's paths.
- S0008 c3 (an expectation, and the sentence does not say who held it), S0011 c2 (a preference) and
  S0014 c2 (a purpose) are attitude or purpose content. They wait for srccov-design-attributed-1119
  or for a purpose design.

These tests read the source and the carriers from the repository. They pin the drop reasons, so a
test fails when a reason stops holding (for example, the overlay review stops being bound to the
environment id), which means a unit can now be carried.
"""
import json
from pathlib import Path

import pytest

from tests.omission_rule import omit_norm
from ve import parse, render
from ve.environment import Environment
from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning, parse_english
from ve.english_vocabulary import overlay_provenance
from ve.errors import VEError
from ve.identity import meaning_id
from ve.printer import _AUXILIARIES, _CONVERSE_ENDINGS

REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "usecases" / "news-article"
SOURCE = (CASE / "source.md").read_text(encoding="utf-8")
ENV_RAW = (CASE / "environment.json").read_bytes()
OVERLAY = json.loads((CASE / "environment.english.json").read_text(encoding="utf-8"))
CLAIMS = (CASE / "claims.ve").read_text(encoding="utf-8")

# unit -> (numbered source sentence, the clause tagged 'none: translation omission', the map's own clause quote)
UNITS = {
    "S0001": ("1. ", "signaled that further rate increases could come in the following months"),
    "S0008": ("5. ", "at the time expecting he would cut rates"),
    "S0010": ("7. ", "issued after a two-day meeting"),
    "S0011": ("8. ", "The statement gave no forward guidance about future decisions, which is Warsh's preference"),
    "S0014": ("10. ", "to explain the decision further"),
}
# The words each clause adds to what claims.ve and its legends already say (absent at the verify commit).
NEW_WORDS = {
    "S0001": ("following months", "further rate increases", "signaled"),
    "S0008": ("cut rates", "expecting"),
    "S0010": ("two-day",),
    "S0011": ("forward guidance", "future decisions", "preference"),
    "S0014": ("explain the decision",),
}
# The clauses that need a new predicate, with the article's past-tense wordings for it. These are not
# the base shape, so they would need an idiom; they are not the drop reason (see PRESENT_TENSE).
PAST_TENSE = [
    ("S0001", "signaled", ["institution", "text"], "{0} signaled {1}"),
    ("S0001", "signaled", ["institution", "text"], "{0} signaled that {1}"),
    ("S0010", "issued_after", ["text", "moment"], "{0} was issued after {1}"),
    ("S0010", "issued_after", ["text", "moment"], "{0} issued after {1}"),
    ("S0011", "gave_forward_guidance", ["text"], "{0} gave forward guidance about future decisions"),
    ("S0011", "gave_forward_guidance_about", ["text", "moment"], "{0} gave forward guidance about {1}"),
]

# The same three clauses with a present-tense wording, and a claims.ve test line that uses it. The lines are
# probes of the linter and the round trip, not proposed carries: the S0011 line states that guidance was
# given, while the source says none was. The linter's base shape accepts each wording; of the drop reasons,
# the overlay review binding is the one that a wording cannot avoid.
PRESENT_TENSE = [
    ("S0001", "signals", ["institution", "text"], "{0} signals {1}", "@fed signals @new_statement."),
    ("S0010", "follows", ["text", "moment"], "{0} follows {1}", "@new_statement follows @sept_meeting."),
    ("S0011", "gives_forward_guidance_about", ["text", "moment"], "{0} gives forward guidance about {1}",
     "@new_statement gives_forward_guidance_about @sept_meeting."),
]
REPORT = REPO / "docs" / "infra" / "srccov-rl-news-article-1121" / "REPORT.md"


def with_predicate(name, arguments, template):
    """environment.json plus one predicate, and the overlay rebound to it with `template` for that predicate."""
    data = json.loads(ENV_RAW)
    assert name not in data["vocabulary"]["predicates"]
    description = "Recorded as " + template.replace("{0} ", "the subject ").replace("{1}", "this") + "."
    data["vocabulary"]["predicates"][name] = {"arguments": arguments, "description": description}
    env = Environment.from_json(json.dumps(data).encode())
    overlay = json.loads(json.dumps(OVERLAY))
    overlay["environment_id"] = env.environment_id
    overlay["predicates"][name] = {"verbalisation": template, "suggested": False}
    return env, overlay


def numbered_sentence(prefix):
    """The normalised numbered paraphrase sentence of source.md that starts with `prefix` (one line)."""
    lines = [line for line in SOURCE.splitlines() if line.startswith(prefix)]
    assert len(lines) == 1, prefix
    return omit_norm(lines[0])


def shown_text():
    """What the reader is shown for this document: the claims and every legend of environment.json and the overlay."""
    env = json.loads(ENV_RAW)
    legends = [entry.get("description", "") for category in env["vocabulary"].values() for entry in category.values()]
    return omit_norm("\n".join([CLAIMS, *legends, json.dumps(OVERLAY, ensure_ascii=False)]))


@pytest.mark.parametrize("unit", sorted(UNITS))
def test_the_clause_is_in_its_source_sentence(unit):
    prefix, clause = UNITS[unit]
    assert omit_norm(clause) in numbered_sentence(prefix), unit


@pytest.mark.parametrize("unit", sorted(UNITS))
def test_the_clause_is_not_carried_by_claims_or_legends(unit):
    """Verify step: no carrier the reader is shown already holds the clause, so no unit is dropped as already carried."""
    shown = shown_text()
    assert omit_norm(UNITS[unit][1]) not in shown, unit
    for words in NEW_WORDS[unit]:
        assert omit_norm(words) in numbered_sentence(UNITS[unit][0]), (unit, words)
        assert omit_norm(words) not in shown, (unit, words)


def test_the_document_declares_only_relational_fol():
    """An attitude (S0008 c3, S0011 c2) or a purpose (S0014 c2) has no construct in the declared profile."""
    env = json.loads(ENV_RAW)
    assert (env["language"], env["profile"]) == ("ve.core@0", "relational-fol@0")
    assert not set(env) - {"language", "profile", "spec_revision", "vocabulary"}


def test_every_predicate_needs_reviewed_overlay_wording():
    """The overlay words every predicate and is reviewed, and the review is bound to the environment id."""
    env = Environment.from_json(ENV_RAW)
    assert set(OVERLAY["predicates"]) == set(env.predicates)
    assert OVERLAY["environment_id"] == env.environment_id
    assert overlay_provenance(OVERLAY)["review_status"] == "reviewed"
    rebound = dict(OVERLAY, environment_id="0" * 64)
    assert overlay_provenance(rebound)["review_status"] == "unreviewed"


@pytest.mark.parametrize("unit,name,arguments,template", PAST_TENSE,
                         ids=[f"{u}-{t}" for u, _, _, t in PAST_TENSE])
def test_the_overlay_linter_refuses_only_the_past_tense_wordings(unit, name, arguments, template):
    """The article's past-tense wordings are not the base shape (no idiom holds them). Not a drop reason:
    a present-tense wording passes (test_a_present_tense_wording_passes_and_only_the_review_blocks)."""
    env, overlay = with_predicate(name, arguments, template)
    with pytest.raises(VEError, match=f"fails the template linter: predicates/{name}$"):
        EnglishVocabulary(env, vocabulary=overlay)


@pytest.mark.parametrize("unit,name,arguments,template,line", PRESENT_TENSE,
                         ids=[f"{u}-{t}" for u, _, _, t, _ in PRESENT_TENSE])
def test_a_present_tense_wording_passes_and_only_the_review_blocks(unit, name, arguments, template, line):
    """F1 (review of 73da418189): the drop reason for S0001 c2, S0010 c2 and S0011 c1 is the overlay review
    binding, not the linter. A present-tense wording has no linter issue and reads back to the same
    meaning; the one thing that fails is the review status, which only a non-builder record can restore."""
    env, overlay = with_predicate(name, arguments, template)
    words = EnglishVocabulary(env, vocabulary=overlay)
    assert not words.issues
    assert words.predicates[name] == template
    document = parse(env, (CLAIMS + line + "\n").encode())
    with pytest.warns(UnreviewedVocabularyWarning):
        text = render(document, env, "ve_english", vocabulary=overlay)
    copied = parse_english(env, text, vocabulary=overlay)
    assert copied == document and meaning_id(env, copied) == meaning_id(env, document)
    assert overlay_provenance(overlay)["review_status"] == "unreviewed"
    assert words.review_status == "unreviewed"


# Wordings of the false reason the F1 review found, split so this file does not itself contain them.
FALSE_REASONS = ("only from the fixed " + "idiom list", "Lean and Python " + "idiom change",
                 "Every source-worded " + "template is refused", "accepts a binary template only " + "from")


def test_the_report_gives_the_review_binding_as_the_drop_reason():
    """F1: REPORT and this file give the overlay review binding as the reason, never the idiom list."""
    texts = {path.name: " ".join(path.read_text(encoding="utf-8").split()) for path in (REPORT, Path(__file__))}
    for name, text in texts.items():
        for wording in FALSE_REASONS:
            assert wording not in text, (name, wording)
    assert "ve/reviewed-overlays.json" in texts["REPORT.md"]
    assert "test_a_present_tense_wording_passes_and_only_the_review_blocks" in texts["REPORT.md"]


# F2 (review of 9f7fa89790): the REPORT said the base shape takes all present-tense wordings. These are
# present-tense wordings it refuses; the tables come from ve/printer.py, so each refusal it adds is tested.
REFUSED = list(dict.fromkeys(
    [("{0} signals to {1}", "BINARY_CONVERSE"), ("{0} gives guidance to {1}", "BINARY_CONVERSE"),
     ("{0} gets {1}", "BINARY_AUXILIARY")]
    + [(f"{{0}} {word} {{1}}", "BINARY_AUXILIARY") for word in sorted(_AUXILIARIES)]
    + [(f"{{0}} signals {word} {{1}}", "BINARY_CONVERSE") for word in sorted(_CONVERSE_ENDINGS)]
))


@pytest.mark.parametrize("template,code", REFUSED, ids=[t for t, _ in REFUSED])
def test_the_base_shape_refuses_an_auxiliary_or_a_converse_ending(template, code):
    """F2: an auxiliary first word or a final by/to/of/from/with/for is refused, present tense or not; the
    public path raises, and the deferred lint names the rule."""
    env, overlay = with_predicate("signals_new", ["institution", "text"], template)
    with pytest.raises(VEError, match="fails the template linter: predicates/signals_new$"):
        EnglishVocabulary(env, vocabulary=overlay)
    words = EnglishVocabulary(env, vocabulary=overlay, _defer_overlay_refusals=True)
    assert code in {i.code for i in words.issues if i.path.startswith("/vocabulary/predicates/signals_new/")}


def test_the_report_names_both_refusals_of_the_base_shape():
    """F2: the REPORT and this file never claim the base shape takes all present-tense wordings, and the
    REPORT names both refusals with the exact word sets of ve/printer.py."""
    import re
    texts = {path.name: " ".join(path.read_text(encoding="utf-8").split()) for path in (REPORT, Path(__file__))}
    for name, text in texts.items():
        for wording in ("accepts " + "any present-tense", "accepts " + "every present-tense"):
            assert wording not in text, (name, wording)
    report = texts["REPORT.md"]
    auxiliaries = re.search(r"auxiliary first word \(([^;)]*)", report)
    assert auxiliaries and set(auxiliaries[1].replace(",", " ").split()) == _AUXILIARIES
    endings = [set(m.split("/")) for m in re.findall(r"final ([a-z]+(?:/[a-z]+)+)", report)]
    assert _CONVERSE_ENDINGS in endings
    assert "test_the_base_shape_refuses_an_auxiliary_or_a_converse_ending" in report
