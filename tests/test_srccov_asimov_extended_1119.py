"""srccov-asimov-extended-1119: the source-coverage rows of asimov-extended that need no rule line.

Row s7-1 (unit S0005, kept): the source's attribution clause `written by "the Asimov extension author" for this use
case` is carried word for word, after the project's quote normalisation (`tests/omission_rule.py` `omit_norm`), on the
legend of each of the ten predicates that only the additions (rules 14-29 of `usecases/asimov-extended/rules.ve`)
derive. The clause is read from the in-repo source `usecases/asimov-extended/source.md`, inside the S0005 sentence.

Row s7-2 (unit S0007, dropped): its record was to be a comment in `rules.ve`, the only record file the map allows for
this document. The norm-English reader has no comment line (`ve/norm_english.py` `parse_english`: every line that is not
a precedence line must be the block `Rule N.`), so the record cannot be written; the last test pins that reason.
"""
import json
import re
import sys
from pathlib import Path

import pytest

from tests.omission_rule import omit_norm

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "asimov-extended"
SOURCE = (HERE / "source.md").read_text(encoding="utf-8")
ENV = json.loads((HERE / "environment.json").read_text(encoding="utf-8"))
RULES = (HERE / "rules.ve").read_text(encoding="utf-8").splitlines()

# S0005, by its first and last words (units-asimov-extended.tsv, asimov-extended/source.md:L26@1294-1459).
S0005 = ("Rules 14–29 in", "for this use case.")
CLAUSE = 'written by "the Asimov extension author" for this use case'
TAG = "(authored, not Asimov's)"
# The row's carrier keys, with the addition rules that derive each predicate (its own lines in rules.ve).
CARRIERS = {
    "lawful_action": (14,),
    "candidate_action": (15, 16),
    "possibly_harmful": (17, 25),
    "valid_order": (20,),
    "prevails_over": (21, 22),
    "overridden_order": (23,),
    "own_robot_harm": (26,),
    "competes_with": (27,),
    "less_severe_competitor": (28,),
    "beaten_by_a_candidate": (29,),
}
S0007 = "The Three Laws rank laws, not harms, and say nothing about orders that conflict with each other."


def sentence(first, last):
    """The normalised source sentence from `first` to the end of `last`; it starts a paragraph or follows a sentence
    end, and occurs once."""
    raw = SOURCE.find(first)
    assert raw >= 0 and SOURCE.count(first) == 1, first
    assert SOURCE[:raw].endswith("\n\n") or SOURCE[:raw].rstrip()[-1:] in ".;:", SOURCE[raw - 30:raw]
    norm = omit_norm(SOURCE)
    start = norm.find(omit_norm(first))
    assert start >= 0 and norm.count(omit_norm(first)) == 1, first
    end = norm.find(omit_norm(last), start)
    assert end > start, last
    return norm[start:end + len(omit_norm(last))]


def test_the_clause_is_the_source_text_of_s0005():
    unit = sentence(*S0005)
    assert unit.endswith(omit_norm(CLAUSE) + "."), unit
    assert unit.startswith("rules 14-29 in") and "this project's additions" in unit


@pytest.mark.parametrize("key", sorted(CARRIERS))
def test_s0005_is_carried_word_for_word_on_the_addition_legend(key):
    legend = ENV["vocabulary"]["predicates"][key]["description"]
    assert omit_norm(CLAUSE) in omit_norm(legend), (key, legend)
    # The clause attributes the tag it follows, so it comes right after "(authored, not Asimov's)".
    assert legend.endswith(f"{TAG}, {CLAUSE}"), (key, legend)


@pytest.mark.parametrize("key", sorted(CARRIERS))
def test_the_carrier_is_the_legend_of_a_predicate_the_additions_use(key):
    """METHOD amendment 4: a legend carries only if a rule line of the read file uses its symbol."""
    for number in CARRIERS[key]:
        line = RULES[number - 1]
        assert number >= 14 and re.match(rf"Rule {number}\b", line), line
        assert f'"{key}"' in line.split(", if ")[0].split(", unless ")[0], (key, number)
    assert not any(f'"{key}"' in line for line in RULES[:13]), key


def test_the_carried_clause_is_on_exactly_the_tagged_legends():
    tagged = {key for key, entry in ENV["vocabulary"]["predicates"].items() if TAG in entry.get("description", "")}
    carried = {key for key, entry in ENV["vocabulary"]["predicates"].items()
               if CLAUSE in entry.get("description", "")}
    assert tagged == carried == set(CARRIERS)


def test_s0007_has_no_record_form_in_rules_ve():
    """Row s7-2 is dropped: a comment line before rule 14 is refused, so rules.ve cannot hold the record."""
    assert omit_norm(S0007) in omit_norm(SOURCE)
    sys.path.insert(0, str(HERE))
    try:
        import asimov_extended_cases as cases
    finally:
        sys.path.remove(str(HERE))
    from ve.environment import Environment
    from ve.errors import SyntaxError as VESyntaxError
    from ve.norm_english import parse_english

    env = Environment(cases.environment())
    text = cases.source_text()
    assert not any(line.lstrip().startswith(("#", "--", "//")) for line in text.splitlines())
    lines = text.split("\n")
    for marker in ("# ", "-- ", "// "):
        commented = "\n".join(lines[:13] + [marker + S0007] + lines[13:])
        with pytest.raises(VESyntaxError, match="Expected Rule 14 with its own block"):
            parse_english(env, commented)
