"""srccov-rl-eligibility-1121: the kept 'none: translation omission' units are carried by rule lines.

For each kept unit of the source-coverage map (reviews/source-coverage-1119, rows-eligibility.tsv), the rule
line the reader is shown (usecases/eligibility/rules.json) must exist, its gloss must end with the unit's source
sentence word for word (after the counter's quote normalisation, `omit_norm`), the sentence must be on its line
of usecases/eligibility/source/wfp-print.txt (read from the repo), the document's unit record
(translation.GUIDE_SENTENCES) must route the unit to that rule, and every new predicate the rule uses must have
a shown legend (environment.json) whose quoted words are in the source. Verify table, drops and reasons:
docs/infra/srccov-rl-eligibility-1121/REPORT.md.
"""
from __future__ import annotations

import functools
import importlib.util
import json
from pathlib import Path
import re

import pytest

from omission_rule import omit_norm

HERE = Path(__file__).resolve().parents[1] / "usecases" / "eligibility"
SOURCE = HERE / "source" / "wfp-print.txt"

# unit -> (map rows, rule id, S2 line, source sentence, the new predicates the rule uses)
KEPT = {
    "S0406": (("srccov-eligibility-22-1119",), "G1", 39,
              "Any money you get will not affect your other benefits.", {"affects_other_benefits"}),
    "S0424": (("srccov-eligibility-22-1119",), "G2", 64,
              "You’ll be paid into the bank account your benefits are usually paid into.",
              {"jointly_claims_benefits", "paid_into_usual_account"}),
    "S0465": (("srccov-eligibility-14-1119", "srccov-eligibility-26-1119"), "G3", 145,
              "This means the tax deducted from your wages, salary or pension will increase.",
              {"tax_code_changed", "tax_deducted_increases"}),
    "S0467": (("srccov-eligibility-26-1119",), "G4", 148,
              "HMRC will collect 2 payments through your tax code at the same time.",
              {"two_payments_to_collect", "two_payments_through_tax_code"}),
    "S0468": (("srccov-eligibility-26-1119",), "G5", 148,
              "This means you will pay more tax each month.",
              {"two_payments_through_tax_code", "more_tax_each_month"}),
    "S0474": (("srccov-eligibility-26-1119",), "G6", 154,
              "It will show as the ‘Winter Fuel Payment charge’ and will be included in your tax calculation.",
              {"added_to_tax_return", "shown_as_wfp_charge", "in_tax_calculation"}),
    "S0483": (("srccov-eligibility-27-1119",), "G7", 166,
              "If you do not opt out and your total income is over £35,000, you’ll receive the Winter Fuel "
              "Payment but HMRC will take it back.", {"opted_out"}),
}
NEW_PREDICATES = set().union(*(v[4] for v in KEPT.values()))
QUOTE = re.compile(r"\(S2: “(.+)”\)\.$")


def source_lines():
    return SOURCE.read_text(encoding="utf-8").split("\n")


def shown_rules():
    return {r["id"]: r for r in json.loads((HERE / "rules.json").read_text(encoding="utf-8"))["rules"]}


def shown_legends():
    env = json.loads((HERE / "environment.json").read_text(encoding="utf-8"))
    return {name: entry["description"] for name, entry in env["vocabulary"]["predicates"].items()}


def predicates(formula):
    """The predicate names a ve-quantity@1 formula tree uses."""
    found = set()
    if isinstance(formula, list):
        if formula and formula[0] in ("unary", "binary"):
            found.add(formula[1])
        for part in formula:
            found |= predicates(part)
    return found


def carried(gloss, sentence):
    """The carry check: the gloss ends with the source sentence, word for word after `omit_norm`."""
    return omit_norm(gloss).endswith(omit_norm(sentence))


def quoted_in_source(legend, lines):
    """The legend's quoted S2 words, if each occurs in the source after `omit_norm`; else None."""
    match = QUOTE.search(legend)
    if match is None:
        return None
    words = match.group(1)
    return words if any(omit_norm(words) in omit_norm(line) for line in lines) else None


@functools.cache
def translation():
    """usecases/eligibility/translation.py, loaded by path under its own name (never the bare
    `translation`, which other use cases also have); it imports only the standard library."""
    spec = importlib.util.spec_from_file_location("_srccov_rl_eligibility_translation", HERE / "translation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("unit", sorted(KEPT))
def test_each_kept_unit_is_on_its_source_line(unit):
    """The unit's sentence is read from the repo's source at the line the map gives."""
    _, _, line, sentence, _ = KEPT[unit]
    assert omit_norm(sentence) in omit_norm(source_lines()[line - 1]), (unit, line)


@pytest.mark.parametrize("unit", sorted(KEPT))
def test_each_kept_unit_has_its_rule_line_in_the_shown_rules(unit):
    """rules.json (the rule lines the reader is shown) holds the unit's rule; its gloss ends with the sentence
    word for word, its source cites the S2 line, and it uses exactly the new predicates named for it."""
    _, rid, line, sentence, new = KEPT[unit]
    rule = shown_rules().get(rid)
    assert rule is not None, (unit, rid)
    assert rule["role"] is None and rule["rule"] == rid
    assert rule["source"].startswith(f"S2:{line},"), rule["source"]
    assert carried(rule["gloss"], sentence), (unit, rule["gloss"])
    assert predicates(rule["formula"]) & NEW_PREDICATES == new, (unit, predicates(rule["formula"]))


@pytest.mark.parametrize("unit", sorted(KEPT))
def test_each_kept_unit_routes_to_its_rule(unit):
    """The document's unit record (translation.GUIDE_SENTENCES) routes the unit to its rule, line and sentence."""
    _, rid, line, sentence, _ = KEPT[unit]
    assert translation().GUIDE_SENTENCES[rid] == (unit, line, sentence)


def test_the_unit_record_lists_exactly_the_kept_units():
    """No dropped unit is routed to a line, and no kept unit is routed twice."""
    routed = [unit for unit, _, _ in translation().GUIDE_SENTENCES.values()]
    assert sorted(routed) == sorted(KEPT)
    assert sorted(rid for _, rid, *_ in KEPT.values()) == sorted(translation().GUIDE_SENTENCES)


@pytest.mark.parametrize("predicate", sorted(NEW_PREDICATES))
def test_each_new_predicate_has_a_shown_legend_quoting_the_source(predicate):
    """Each new predicate's shown legend quotes S2 words that are in the source, and a kept rule uses it
    (a legend of an unused symbol carries nothing: METHOD amendment 4)."""
    legend = shown_legends()[predicate]
    assert quoted_in_source(legend, source_lines()) is not None, (predicate, legend)
    rules = shown_rules()
    assert any(predicate in predicates(rules[rid]["formula"]) for _, rid, *_ in KEPT.values())


def test_the_guide_rules_define_nothing():
    """No guide rule defines a staged target, so no staged answer reads one."""
    rules = shown_rules()
    for _, rid, *_ in KEPT.values():
        assert rules[rid]["defines"] == [], rid


def test_the_carry_check_refuses_a_gloss_without_the_sentence():
    _, rid, _, sentence, _ = KEPT["S0483"]
    gloss = shown_rules()[rid]["gloss"]
    assert carried(gloss, sentence)
    assert not carried(gloss[: -len(sentence)], sentence)
    assert not carried(gloss.replace("£35,000", "£30,000"), sentence)


def test_the_legend_check_refuses_words_not_in_the_source():
    lines = source_lines()
    legend = shown_legends()["opted_out"]
    assert quoted_in_source(legend, lines) == "opt out of receiving Winter Fuel Payment"
    assert quoted_in_source(legend.replace("opt out of", "opt in to"), lines) is None
    assert quoted_in_source(legend.replace("(S2: “", "(“"), lines) is None
