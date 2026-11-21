"""srccov-rl-eligibility-1121: the kept 'none: translation omission' units are carried by rule lines.

For each kept unit of the source-coverage map (reviews/source-coverage-1119, rows-eligibility.tsv), the rule
line the reader is shown (usecases/eligibility/rules.json) must exist, its gloss must end with the unit's source
sentence word for word (after the counter's quote normalisation, `omit_norm`), the sentence must be on its line
of usecases/eligibility/source/wfp-print.txt (read from the repo), the document's unit record
(translation.GUIDE_SENTENCES) must route the unit to that rule, and every new predicate the rule uses must have
a shown legend (environment.json) whose quoted words are in the source, and every condition the sentence sits
under in the pinned page (usecases/eligibility/source/wfp-print.html: each "If ..." heading above it, and the
"If ..." clause of the sentence an anaphoric "It"/"This" refers to) must be carried by the rule's antecedent.
Verify table, drops and reasons: docs/infra/srccov-rl-eligibility-1121/REPORT.md.
"""
from __future__ import annotations

import functools
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re

import pytest

from omission_rule import omit_norm

HERE = Path(__file__).resolve().parents[1] / "usecases" / "eligibility"
SOURCE = HERE / "source" / "wfp-print.txt"
PAGE = HERE / "source" / "wfp-print.html"

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
              {"tax_code_changed", "two_payments_to_collect", "two_payments_through_tax_code"}),
    "S0468": (("srccov-eligibility-26-1119",), "G5", 148,
              "This means you will pay more tax each month.",
              {"tax_code_changed", "two_payments_to_collect", "two_payments_through_tax_code",
               "more_tax_each_month"}),
    "S0474": (("srccov-eligibility-26-1119",), "G6", 154,
              "It will show as the ‘Winter Fuel Payment charge’ and will be included in your tax calculation.",
              {"completes_self_assessment", "files_online", "included_automatically", "shown_as_wfp_charge",
               "in_tax_calculation"}),
    "S0483": (("srccov-eligibility-27-1119",), "G7", 166,
              "If you do not opt out and your total income is over £35,000, you’ll receive the Winter Fuel "
              "Payment but HMRC will take it back.", {"opted_out"}),
}
NEW_PREDICATES = set().union(*(v[4] for v in KEPT.values()))
QUOTE = re.compile(r"\(S2: (“[^”]+”(?:; “[^”]+”)*)\)\.$")
ANAPHOR = ("It ", "This ", "They ", "That ")


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


def quotes(legend):
    """The S2 words a legend quotes (its closing `(S2: “…”; “…”).`), or () if it has none."""
    match = QUOTE.search(legend)
    return tuple(re.findall(r"“([^”]+)”", match.group(1))) if match else ()


def quoted_in_source(legend, lines):
    """The legend's quoted S2 words, if each occurs in the source after `omit_norm`; else None."""
    words = quotes(legend)
    if not words or not all(any(omit_norm(w) in omit_norm(line) for line in lines) for w in words):
        return None
    return words


class Blocks(HTMLParser):
    """The <main> text of the pinned page as blocks (tag, text), one per heading, paragraph or list
    item, in page order (the blocks source/extract_text.py writes one per line)."""

    TAGS = {"h1", "h2", "h3", "h4", "p", "li"}

    def __init__(self):
        super().__init__()
        self.depth, self.tag, self.text, self.blocks = 0, None, [], []

    def flush(self):
        text = " ".join("".join(self.text).split())
        if self.tag and text:
            self.blocks.append((self.tag, text))
        self.tag, self.text = None, []

    def handle_starttag(self, tag, attrs):
        self.depth += tag == "main"
        if self.depth and tag in self.TAGS:
            self.flush()
            self.tag = tag

    def handle_endtag(self, tag):
        if self.depth and tag in self.TAGS:
            self.flush()
        self.depth -= tag == "main"

    def handle_data(self, data):
        if self.depth and self.tag:
            self.text.append(data)


@functools.cache
def page_blocks():
    """Each body block of the page with the headings in force over it: (h2, h3, text)."""
    parser = Blocks()
    parser.feed(PAGE.read_text(encoding="utf-8"))
    parser.flush()
    heads, out = {}, []
    for tag, text in parser.blocks:
        if tag[0] == "h":
            level = int(tag[1])
            heads = {k: v for k, v in heads.items() if k < level}
            heads[level] = text
        else:
            out.append((heads.get(2), heads.get(3), text))
    return tuple(out)


def sentences(text):
    return re.split(r"(?<=[.!?])\s+(?=[A-Z‘“])", text)


def conditions(sentence):
    """The conditions a page sentence sits under: each "If …" heading in force over its block, and,
    when it opens with an anaphor, the "If …" clause of the sentence before it in the block (or that
    whole sentence, when it states no condition: the referent)."""
    found = []
    for h2, h3, text in page_blocks():
        parts = sentences(text)
        hits = [i for i, part in enumerate(parts) if omit_norm(part) == omit_norm(sentence)]
        if not hits:
            continue
        found += [h for h in (h2, h3) if h and h.startswith("If ")]
        i = hits[0]
        if i and sentence.startswith(ANAPHOR):
            before = parts[i - 1]
            found.append(before.split(",")[0] if before.startswith("If ") else before.rstrip("."))
        return tuple(found)
    raise AssertionError(f"sentence not on the page: {sentence}")


def conjunct_atoms(formula):
    """The atoms a formula asserts as conjuncts (each `and` opened, nothing under `not` or `or`)."""
    if formula[0] == "and":
        return conjunct_atoms(formula[1]) | conjunct_atoms(formula[2])
    return {json.dumps(formula)} if formula[0] in ("unary", "binary") else set()


def missing_conditions(formula, wanted, legends):
    """The conditions in `wanted` the rule's antecedent does not carry. One is carried when a guide
    predicate the antecedent asserts has a legend quoting its words, or when it is a condition the
    rules read with existing predicates (translation.SOURCE_CONDITIONS) and the antecedent asserts
    each of that reading's atoms."""
    if formula[0] != "implies":
        return tuple(wanted)
    atoms = conjunct_atoms(formula[1])
    quoted = [omit_norm(w) for atom in map(json.loads, atoms) for w in quotes(legends.get(atom[1], ""))]
    readings = {words: conjunct_atoms(translation().source_condition(words))
                for words in translation().SOURCE_CONDITIONS}
    def carried_by(words):
        bare = omit_norm(words.removeprefix("If "))
        return any(bare in q for q in quoted) or (words in readings and readings[words] <= atoms)
    return tuple(w for w in wanted if not carried_by(w))


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
    assert quoted_in_source(legend, lines) == ("opt out of receiving Winter Fuel Payment",)
    assert quoted_in_source(legend.replace("opt out of", "opt in to"), lines) is None
    assert quoted_in_source(legend.replace("(S2: “", "(“"), lines) is None


# unit -> the conditions it sits under on the page, read by hand (srccov-rl-eligibility-1121 review F1:
# G2 had dropped its h2 and G6 its h2 and lead-in clause).
CONTEXT = {
    "S0406": (),
    "S0424": ("If you live with someone else who’s eligible for the Winter Fuel Payment",
              "If you and your partner jointly claim any of the benefits"),
    "S0465": ("If HMRC changes your tax code", "If HMRC changes your tax code to pay back your Winter Fuel Payment"),
    "S0467": ("If HMRC changes your tax code", "If HMRC needs to collect 2 payments"),
    "S0468": ("If HMRC changes your tax code", "If HMRC needs to collect 2 payments",
              "HMRC will collect 2 payments through your tax code at the same time"),
    "S0474": ("If you complete a Self Assessment tax return", "If you file tax returns online"),
    "S0483": (),
}


@pytest.mark.parametrize("unit", sorted(KEPT))
def test_the_page_reader_finds_the_conditions_each_kept_unit_sits_under(unit):
    """The conditions read from the pinned HTML are the ones read by hand."""
    assert conditions(KEPT[unit][3]) == CONTEXT[unit]


@pytest.mark.parametrize("unit", sorted(KEPT))
def test_each_kept_rule_carries_the_conditions_its_sentence_sits_under(unit):
    """No rule line states more than its source: each heading or lead-in condition over the sentence on
    the page is in the rule's antecedent (review F1: G2, G6)."""
    rid, sentence = KEPT[unit][1], KEPT[unit][3]
    formula = shown_rules()[rid]["formula"]
    assert missing_conditions(formula, conditions(sentence), shown_legends()) == (), (unit, rid)


# The review's failing examples (srccov-rl-eligibility-1121 F1): G2 and G6 as they were at 4d3cfa95.
U = lambda pred: ["unary", pred, ["const", "applicant"]]
WIDE = {
    "S0424": ["implies", ["and", U("jointly_claims_benefits"), U("entitled")], U("paid_into_usual_account")],
    "S0474": ["implies", U("added_to_tax_return"), ["and", U("shown_as_wfp_charge"), U("in_tax_calculation")]],
    "S0467": ["implies", U("two_payments_to_collect"), U("two_payments_through_tax_code")],
}
WIDE_LEGENDS = {"added_to_tax_return": "The amount … (S2: “adding the amount to your Self Assessment tax return”)."}


@pytest.mark.parametrize("unit, missing", [
    ("S0424", ("If you live with someone else who’s eligible for the Winter Fuel Payment",)),
    ("S0474", ("If you complete a Self Assessment tax return", "If you file tax returns online")),
    ("S0467", ("If HMRC changes your tax code",)),
])
def test_the_context_check_refuses_the_wider_lines(unit, missing):
    """The check finds each condition the wider line dropped, and only those."""
    legends = {**shown_legends(), **WIDE_LEGENDS}
    assert missing_conditions(WIDE[unit], conditions(KEPT[unit][3]), legends) == missing


def test_the_context_check_refuses_a_rule_without_an_antecedent():
    assert missing_conditions(U("affects_other_benefits"), ("If x",), {}) == ("If x",)


def test_a_condition_under_not_or_or_is_not_carried():
    """A condition is carried only as a conjunct of the antecedent, never negated or in a disjunction."""
    legends = shown_legends()
    wanted = ("If you file tax returns online",)
    assert missing_conditions(["implies", U("files_online"), U("in_tax_calculation")], wanted, legends) == ()
    assert missing_conditions(["implies", ["not", U("files_online")], U("in_tax_calculation")], wanted, legends) == wanted
    assert missing_conditions(["implies", ["or", U("files_online"), U("entitled")], U("in_tax_calculation")],
                              wanted, legends) == wanted


def test_the_amount_rules_and_g2_share_one_reading_of_the_lives_with_heading():
    """The S2:49 heading is read once (translation.SOURCE_CONDITIONS); the amount rules use that reading."""
    t = translation()
    reading = t.source_condition(t.LIVES_WITH_ELIGIBLE)
    shown = json.dumps(shown_rules())
    assert json.dumps(reading) in shown
    assert conjunct_atoms(reading) == {json.dumps(["binary", "lives_with", ["const", "applicant"], ["const", "housemate"]]),
                                       json.dumps(["unary", "entitled", ["const", "housemate"]])}


def test_the_benefits_legend_names_the_benefits():
    """`jointly_claims_benefits` quotes the benefits "any of the benefits" refers to (S2:51-53)."""
    words = quoted_in_source(shown_legends()["jointly_claims_benefits"], source_lines())
    assert words is not None
    assert {"Pension Credit", "Universal Credit", "income-related Employment and Support Allowance (ESA)"} <= set(words)
