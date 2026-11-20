"""srccov-math-mini-paper-1119: the paper's Definition D1 is carried word for word in the legend its rule uses.

One kept row of the source-coverage map (reviews/source-coverage-1119/rows-math-mini-paper.tsv):

- srccov-math-mini-paper-s6-1-1119, unit S0001: the first sentence of Definition D1 (paper.template.md) on the
  `lists` legend of environment.json, the predicate the T1 conclusion (and T2) uses.

The sentence is read from the source file, never copied into this test. Markdown emphasis (`*`, `**`) is markup, not
wording, and is dropped from the source before comparison; then both sides go through the project's quote
normalisation (`tests/omission_rule.py:omit_norm`, NFKC, quotes and dashes, case and whitespace).

The map's other rows (S0002-S0004, S0011, S0012, S0015) are dropped (docs/infra/srccov-math-mini-paper-1119/REPORT.md):
their carrier, a comment in a theorem's premises.ve, does not exist in VE, so no record is written and none is tested.
"""

import json
import re
from pathlib import Path

import pytest

from tests.omission_rule import omit_norm

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "usecases/math-mini-paper"


def _section(heading):
    """Lines of paper.template.md from `heading` (exact line) to the next heading of the same or higher level."""
    lines = (PAPER / "paper.template.md").read_text(encoding="utf-8").splitlines()
    start = lines.index(heading)
    level = len(heading) - len(heading.lstrip("#"))
    end = next((i for i in range(start + 1, len(lines))
                if re.match(r"#{1,%d} " % level, lines[i])), len(lines))
    return lines[start + 1:end]


def _first_paragraph(body):
    paragraph = []
    for line in body:
        if not line.strip():
            if paragraph:
                break
            continue
        paragraph.append(line)
    return " ".join(paragraph)


def _first_sentence(paragraph):
    text = re.sub(r"\s+", " ", paragraph.replace("*", "")).strip()
    return re.split(r"(?<=\.)\s+(?=[A-Z])", text)[0]


def source_d1():
    return _first_sentence(_first_paragraph(_section("### Definition D1 (self-listing)")))


def legend(env_file, predicate):
    env = json.loads((PAPER / env_file).read_text(encoding="utf-8"))
    return env["vocabulary"]["predicates"][predicate]["description"]


ROWS = [
    ("srccov-math-mini-paper-s6-1-1119", "S0001", source_d1, "environment.json", "lists",
     "A point y is self-listing for a relation R when R(y, y)."),
]


@pytest.mark.parametrize("row,unit,source,env_file,predicate,map_quote", ROWS, ids=[r[0] for r in ROWS])
def test_source_unit_is_carried_in_the_rules_legend(row, unit, source, env_file, predicate, map_quote):
    sentence = source()
    # The span the map's unit names is the span the source file holds (no truncation, no paraphrase).
    assert sentence == map_quote, (row, unit, sentence)
    assert omit_norm(sentence) in omit_norm(legend(env_file, predicate)), (row, unit, legend(env_file, predicate))


def test_carrier_legend_belongs_to_a_symbol_the_rules_use():
    """A legend of an unused symbol carries nothing (METHOD amendment 4): T1 states the diagonal lemma with `lists`."""
    conclusion = (PAPER / "theorems" / "T1" / "conclusion.ve").read_text()
    assert re.search(r"\(x0 lists x1\)", conclusion) and re.search(r"\(x1 lists x1\)", conclusion), conclusion
    assert re.search(r"\blists\b", (PAPER / "theorems" / "T2" / "conclusion.ve").read_text())
