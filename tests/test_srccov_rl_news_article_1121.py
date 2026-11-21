"""srccov-rl-news-article-1121: the news-article units tagged 'none: translation omission' and why none is carried.

The source-coverage map (row srccov-news-article-s7-1-1119, pin e53db4e8fc) tags five units of
`usecases/news-article/source.md` 'none: translation omission'. The verify step dropped all five
(docs/infra/srccov-rl-news-article-1121/REPORT.md, table 0):

- S0001 c2, S0010 c2, S0011 c1 need a new predicate in `environment.json`. Every claims.ve predicate
  must have reviewed English wording in `environment.english.json` (tests/test_english.py
  test_reviewed_overlays_preserve_all_historical_views_and_identities), and the overlay linter
  accepts a binary template only from the fixed idiom list (`IDIOMS`, ve/english_vocabulary.py, with
  its Lean copy `idioms2` in lean/VE/EnglishGrammar/Lexicon.lean). Every source-worded template is
  refused, so the carry needs a Lean and Python change, which this row does not allow. Also, any
  vocabulary change rebinds the overlay digest and drops it to 'unreviewed', and the builder cannot
  write the review record.
- S0008 c3 (an expectation, and the sentence does not say who held it), S0011 c2 (a preference) and
  S0014 c2 (a purpose) are attitude or purpose content. They wait for srccov-design-attributed-1119
  or for a purpose design.

These tests read the source and the carriers from the repository. They pin the drop reasons, so a
test fails when a reason stops holding (for example, an idiom is added), which means a unit can now
be carried.
"""
import json
from pathlib import Path

import pytest

from tests.omission_rule import omit_norm
from ve.environment import Environment
from ve.english import EnglishVocabulary
from ve.english_vocabulary import overlay_provenance
from ve.errors import VEError

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
# The clauses that need a new predicate, with source-worded English templates for it.
NEEDS_PREDICATE = [
    ("S0001", "signaled", ["institution", "text"], "{0} signaled {1}"),
    ("S0001", "signaled", ["institution", "text"], "{0} signaled that {1}"),
    ("S0010", "issued_after", ["text", "moment"], "{0} was issued after {1}"),
    ("S0010", "issued_after", ["text", "moment"], "{0} issued after {1}"),
    ("S0011", "gave_forward_guidance", ["text"], "{0} gave forward guidance about future decisions"),
    ("S0011", "gave_forward_guidance_about", ["text", "moment"], "{0} gave forward guidance about {1}"),
]


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


@pytest.mark.parametrize("unit,name,arguments,template", NEEDS_PREDICATE,
                         ids=[f"{u}-{t}" for u, _, _, t in NEEDS_PREDICATE])
def test_the_overlay_linter_refuses_the_wording_a_carry_needs(unit, name, arguments, template):
    data = json.loads(ENV_RAW)
    assert name not in data["vocabulary"]["predicates"]
    description = "Recorded as " + template.replace("{0} ", "the subject ").replace("{1}", "this") + "."
    data["vocabulary"]["predicates"][name] = {"arguments": arguments, "description": description}
    env = Environment.from_json(json.dumps(data).encode())
    overlay = json.loads(json.dumps(OVERLAY))
    overlay["environment_id"] = env.environment_id
    overlay["predicates"][name] = {"verbalisation": template, "suggested": False}
    with pytest.raises(VEError, match=f"fails the template linter: predicates/{name}$"):
        EnglishVocabulary(env, vocabulary=overlay)
