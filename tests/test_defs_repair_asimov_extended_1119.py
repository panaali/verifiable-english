"""defs-repair-asimov-extended-1119: the source definitions the asimov-extended rules depend on are carried word for word.

Each carried definition is read from the in-repo source `usecases/asimov-extended/source.md` (no hash-pinned source), by
its first and last words, and must occur, after the project's quote normalisation (`tests/omission_rule.py` `omit_norm`),
in the legend of a predicate or sort that the dependent rules use, in `usecases/asimov-extended/environment.json`.
The extension keeps every v2 predicate entry identical to `usecases/asimov-laws/environment.json`
(`tests/test_asimov_extended.py`), so the definitions bound to v2 predicates are carried on the legend of the sort the
rules quantify over; the REPORT records why.
"""
import json
import re
from pathlib import Path

import pytest

from tests.omission_rule import omit_norm

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "asimov-extended"
SOURCE = (HERE / "source.md").read_text(encoding="utf-8")
ENV = json.loads((HERE / "environment.json").read_text(encoding="utf-8"))
RULES = (HERE / "rules.ve").read_text(encoding="utf-8").splitlines()

# row -> (first words, last words, the audit row's quote, carrier (kind, key), rules using the carrier, the term phrase)
E3 = ("the severity classes and their order:", "decided by the Asimov extension author);",
      "the severity classes and their order: a harm to humanity, then death, then injury, then property damage, with "
      "the robot's own destruction counted as property damage (`environment.json`, decided by the Asimov extension "
      "author);")
E1 = ("`base.ve` is v2's `rules.ve`", "does not change (risk.md 2.2).",
      "`base.ve` is v2's `rules.ve` with one forced rewording: a risk environment rejects the bare word `prevents`, so "
      "rules 9 and 13 say `might prevent`. The meaning of the word does not change (risk.md 2.2).")
E2A = ("An action that no rule forbids", "may be performed.", "An action that no rule forbids may be performed.")
E2B = ("An action is not required unless", "unless a rule derives it.",
       "An action is not required unless a rule requires it, and a derived name is false unless a rule derives it.")
ROWS = {
    "defs-asimov-extended-1-1119": (*E3, ("predicates", "less_severe_competitor"), (28, 29), '"less_severe_competitor"'),
    "defs-asimov-extended-2-1119": (*E3, ("predicates", "beaten_by_a_candidate"), (18, 19, 20, 29),
                                    '"beaten_by_a_candidate"'),
    "defs-asimov-extended-3-1119": (*E1, ("sorts", "harm"), (13,), "might prevent that harm"),
    "defs-asimov-extended-4-1119": (*E1, ("sorts", "harm"), (9,), "might prevent that harm"),
    "defs-asimov-extended-5-1119": (*E2A, ("sorts", "action"), (1, 2, 9, 11, 12, 13, 19), "may be performed"),
    "defs-asimov-extended-6-1119": (*E2B, ("sorts", "action"), (11, 13), "must be performed"),
}


def source_span(first, last):
    """The span of the source from `first` to the end of `last`, normalised; it must start at a sentence or list-entry
    boundary and occur once."""
    norm = omit_norm(SOURCE)
    start = norm.find(omit_norm(first))
    assert start >= 0 and norm.count(omit_norm(first)) == 1, first
    assert start == 0 or norm[:start].rstrip()[-1:] in ".;:-", norm[start - 30:start]
    end = norm.find(omit_norm(last), start)
    assert end > start, last
    return norm[start:end + len(omit_norm(last))]


@pytest.mark.parametrize("row", sorted(ROWS))
def test_the_source_definition_is_carried_word_for_word(row):
    first, last, quote, (kind, key), rules, phrase = ROWS[row]
    span = source_span(first, last)
    assert span == omit_norm(quote), row
    legend = ENV["vocabulary"][kind][key]["description"]
    assert span in omit_norm(legend), (row, legend)


@pytest.mark.parametrize("row", sorted(ROWS))
def test_the_carrier_is_a_legend_the_dependent_rules_use(row):
    _, _, _, (kind, key), rules, phrase = ROWS[row]
    for number in rules:
        line = RULES[number - 1]
        assert line.startswith(f"Rule {number}"), line
        assert phrase in line, (row, number)
        used = f'"{key}"' if kind == "predicates" else re.compile(rf"\b{key}\b")
        assert (used in line) if kind == "predicates" else used.search(line), (row, number, key)


def test_a_sort_carrier_keeps_its_noun():
    """A sort's noun is its name (no verbalisation), so the carried text does not enter the rendered rules."""
    for key in ("action", "harm"):
        sort = ENV["vocabulary"]["sorts"][key]
        assert "verbalisation" not in sort and sort["description"].startswith(key + ". "), sort
