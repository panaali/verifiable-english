"""relb-f3-phrases: plain phrases for the yes/no facts of the eligibility use case.

usecases/eligibility/plain_wordings.json gives one plain wording per yes/no predicate of the eligibility
environment ("{0} has reached pensionable age", "{0} lives with {1}"); each one outside the two mechanical
shapes is a row of the English idiom list (ve/english_vocabulary.py IDIOMS, lean/VE/EnglishGrammar/Lexicon.lean
idioms1/idioms2). Declared as `verbalisation`s in a copy of the environment (translation.py does not read the
file yet), every wording is accepted, and every rule and yes/no fact of the use case is worded with them and
reads back to exactly one reading, itself. On main each wording is refused and falls back to
'is classified as "<name>"'. Planted errors: near misses are refused, a longer phrase never reads as the shorter
predicate or the other way round, argument order is literal, an unrelated or duplicated wording is refused, and
a fact's sentence with its people swapped never reads as the fact.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

from ve.english import english_legend
from ve.environment import Environment
from ve.errors import VEError
from ve.surface.time import parse_w6_sentence, render_w6_sentence
from ve.units import elaborate_quantity, erased_environment

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "usecases" / "eligibility"
sys.path.insert(0, str(HERE))

import translation as T  # noqa: E402

WORDINGS = json.loads((HERE / "plain_wordings.json").read_text())["predicates"]
FALLBACK = ("classified as", "recorded relation")


def environment(wordings=WORDINGS):
    raw = T.environment()
    for name, template in wordings.items():
        raw["vocabulary"]["predicates"][name]["verbalisation"] = template
    return Environment(raw)


def templates(env):
    legend = json.loads(english_legend(erased_environment(env), style="json"))
    return {name: entry["template"] for name, entry in legend["predicates"].items()}


def reading(env, sentence):
    return parse_w6_sentence(env, sentence)["formula"]


def predicates(formula, found):
    if isinstance(formula, list):
        if len(formula) > 1 and formula[0] in ("unary", "binary") and isinstance(formula[1], str):
            found.add(formula[1])
        for part in formula:
            predicates(part, found)
    return found


def yes_no_facts():
    """The distinct profile facts that hold a yes/no predicate (run.py english_facts' enumeration)."""
    data = json.loads((HERE / "cases.json").read_text())
    seen, facts = set(), []
    for case in data["cases"]:
        for fact in T.profile_facts(case, data["defaults"]):
            key = T.key(fact["formula"])
            if key not in seen and predicates(fact["formula"], set()):
                seen.add(key)
                facts.append(fact)
    return facts


@pytest.fixture(scope="module")
def env():
    return environment()


def test_every_yes_no_predicate_has_one_plain_wording():
    assert set(WORDINGS) == set(T.environment()["vocabulary"]["predicates"])
    assert len(WORDINGS) == 49
    assert len(set(WORDINGS.values())) == len(WORDINGS)


def test_every_plain_wording_is_accepted(env):
    used = templates(env)
    refused = {name: used[name] for name, template in WORDINGS.items() if used[name] != template}
    assert refused == {}


def read_back(env, rows, swap):
    """Rows whose wording does not read back to exactly the statement in plain phrases, and (with `swap`) rows
    whose wording with applicant and housemate swapped reads as the statement (a planted error read as right)."""
    failures, wrong = [], []
    for rid, formula in rows:
        canonical, _ = elaborate_quantity(env, T.q(formula))
        sentence = render_w6_sentence(env, canonical)
        if parse_w6_sentence(env, sentence) != canonical or any(f in sentence for f in FALLBACK):
            failures.append((rid, sentence))
        swapped = sentence.replace("applicant", "\0").replace("housemate", "applicant").replace("\0", "housemate")
        if swap and swapped != sentence:
            try:
                if parse_w6_sentence(env, swapped) == canonical:
                    wrong.append((rid, swapped))
            except VEError:
                pass
    return failures, wrong


def test_every_rule_reads_back_in_plain_phrases(env):
    """56 rules: one reading, the rule itself, worded only with the declared phrases."""
    rows = [(r["id"], r["formula"]) for r in T.rules()]
    assert len(rows) == 56
    assert read_back(env, rows, swap=False) == ([], [])


def test_every_yes_no_fact_reads_back_in_plain_phrases(env):
    """80 yes/no facts: one reading, the fact itself, in plain phrases; the same sentence with applicant and
    housemate swapped never reads as the fact."""
    rows = [(f["id"], f["formula"]) for f in yes_no_facts()]
    assert len(rows) == 80
    assert read_back(env, rows, swap=True) == ([], [])


@pytest.mark.parametrize("sentence", [
    "Applicant is detained.",                                   # a part of "is detained in custody"
    "Applicant is entitled.",                                   # a part of "is entitled to a winter fuel payment"
    "Applicant has moved to Scotland.",                         # a part of "Scotland or Northern Ireland"
    "Applicant is a partner of housemate during the week.",     # a near miss of "throughout the week"
    "Applicant lives with.",
    "Applicant is paid state_pension for the qualifying week.", # a compound constant name must be quoted
])
def test_near_misses_are_refused(env, sentence):
    with pytest.raises(VEError):
        parse_w6_sentence(env, sentence)


@pytest.mark.parametrize("sentence, expected", [
    ("Applicant is a partner of housemate.", ["binary", "partner_of", ["const", "applicant"], ["const", "housemate"]]),
    ("Applicant is a partner of housemate throughout the week.",
     ["binary", "partners_throughout", ["const", "applicant"], ["const", "housemate"]]),
    ("Applicant shares a home with housemate.", ["binary", "shares_home", ["const", "applicant"], ["const", "housemate"]]),
    ("Applicant shares a home with housemate throughout the week.",
     ["binary", "home_throughout", ["const", "applicant"], ["const", "housemate"]]),
    ("Applicant is excluded.", ["unary", "excluded", ["const", "applicant"]]),
    ("Applicant is excluded as a prisoner.", ["unary", "excluded_custody", ["const", "applicant"]]),
    ("Housemate lives with applicant.", ["binary", "lives_with", ["const", "housemate"], ["const", "applicant"]]),
    ("If applicant has reached pensionable age, then applicant is entitled to a winter fuel payment.",
     ["implies", ["unary", "reached_pa", ["const", "applicant"]], ["unary", "entitled", ["const", "applicant"]]]),
])
def test_each_phrase_has_one_reading_its_own(env, sentence, expected):
    assert reading(env, sentence) == expected


def test_an_unrelated_wording_is_refused():
    """A wording that shares no content word with its predicate's name or legend is not accepted, even though
    it is an idiom row: "{0} has left care" declared for opted_out (and not for care_ended)."""
    wordings = {**WORDINGS, "opted_out": WORDINGS["care_ended"]}
    del wordings["care_ended"]
    used = templates(environment(wordings))
    assert used["opted_out"] != WORDINGS["care_ended"]
    assert any(f in used["opted_out"] for f in FALLBACK)


def test_a_wording_declared_twice_is_refused_for_both():
    wordings = {**WORDINGS, "excluded_hospital": WORDINGS["excluded_custody"]}
    used = templates(environment(wordings))
    assert used["excluded_hospital"] != WORDINGS["excluded_custody"]
    assert used["excluded_custody"] != WORDINGS["excluded_custody"]


def test_a_wording_outside_the_idiom_list_is_refused():
    """The guard is the closed list: a natural wording that is no idiom row keeps the fallback."""
    wordings = {**WORDINGS, "more_tax_each_month": "{0} pays more tax each month"}
    used = templates(environment(wordings))
    assert any(f in used["more_tax_each_month"] for f in FALLBACK)
