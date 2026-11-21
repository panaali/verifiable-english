"""srccov-rl-openai-preparedness-1121: the condition test for the rule line that carries 4.2's sufficiency basis.

The source-coverage map (manage-agents reviews/source-coverage-1119, an Opus reading at VE pin e53db4e8fc) tagged
four PF units "none: translation omission": 4.2's lead-in "The SAG will make this determination based on:" (S0171)
and its three bullets (S0172, S0173, S0186). The REPORT (docs/infra/srccov-rl-openai-preparedness-1121/REPORT.md)
keeps them and drops the other in-scope units with a reason each. For each kept unit this file checks that:

* the line exists in the carrier the reader is shown: block `sr-sufficiency` of rules.d1.ve, whose act
  `sufficiency_basis` is a regulated predicate of environment.d1.json;
* the unit's spans.json record routes to it (`blocked_rule`), and the build places exactly these four units on it;
* the unit's sentence is one whole quotation of the block's legend and header, and that quotation equals the
  pinned source text inside the unit's byte span under the case's normalisation (quote_evidence.plain).

Every test fails on the pre-change main: the block, the act and the routes do not exist there.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.pinned_source import pinned_source

REPO = Path(__file__).resolve().parents[1]
PF = REPO / "usecases" / "openai-preparedness"
NAMES = ("pf_vocabulary", "pf_translation", "build_document", "quote_evidence")


def _load():
    saved = {name: sys.modules.pop(name) for name in NAMES if name in sys.modules}
    sys.path.insert(0, str(PF))
    sys.path.insert(0, str(PF / "source"))
    try:
        return {name: importlib.import_module(name) for name in NAMES}
    finally:
        sys.path.remove(str(PF / "source"))
        sys.path.remove(str(PF))
        for name in NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


MODULES = _load()
T, B, Q = MODULES["pf_translation"], MODULES["build_document"], MODULES["quote_evidence"]

BLOCK = "sr-sufficiency"
PREDICATE = "sufficiency_basis"
ACT = "{0} have SAG base safeguard sufficiency on capability plus risks plus safeguards"
LINE = "Rule 1. Every situation must have SAG base safeguard sufficiency on capability plus risks plus safeguards."

# (map unit, its UTF-8 byte span in the pinned text (units-openai-preparedness.tsv), spans.json unit, sentence)
UNITS = (
    ("S0171", (34586, 34632), "p11-u181", "The SAG will make this determination based on:"),
    ("S0172", (34633, 34718), "p11-u182",
     "The level of capability in the Tracked Category based on the Capabilities Report."),
    ("S0173", (34719, 34850), "p11-u183",
     "The associated risks of severe harm, as described in the threat model and where needed, advice of internal or "
     "external experts."),
    ("S0186", (36739, 36822), "p12-u196",
     "The safeguards in place and their effectiveness based on the Safeguards Report."),
)


def _predicates():
    return json.loads((PF / "environment.d1.json").read_text(encoding="utf-8"))["vocabulary"]["predicates"]


def _block():
    [block] = [b for b in T.read_blocks("rules.d1.ve") if b.id == BLOCK]
    return block


def _legend_quotes():
    return [Q.plain(q) for q in Q.quotes(SimpleNamespace(source=_predicates()[PREDICATE]["description"]))]


def _spans():
    return {u["id"]: u for u in json.loads((PF / "spans.json").read_text(encoding="utf-8"))["units"]}


def test_the_rule_line_is_in_the_carrier_the_reader_is_shown():
    """rules.d1.ve holds the block, read on every reading choice, and its line states the act of a regulated
    predicate of environment.d1.json (the vocabulary the reader is shown)."""
    block = _block()
    assert block.when == () and block.text == LINE
    assert block.text == "Rule 1. Every situation must " + ACT.removeprefix("{0} ") + "."
    entry = _predicates()[PREDICATE]
    assert entry["regulated"] == {"role": "obligation", "default": "deny", "act": ACT}
    assert entry["arguments"] == ["situation"]
    assert BLOCK in T.RS0_STATEMENTS, "a future tense process statement is an RS0 statement (PLAN 3.1)"
    assert f"{BLOCK} | omits: nothing" in (PF / "accounting.d1.txt").read_text(encoding="utf-8").splitlines()


def test_the_line_parses_to_the_act_with_no_condition():
    """VE's English parser reads the line as the act's unconditional duty."""
    norm = json.loads(T.parsed_rule(BLOCK))
    assert (norm["predicate"], norm["sign"], norm["guard"]) == (PREDICATE, True, ["top"])


@pytest.mark.parametrize("unit", UNITS, ids=lambda u: u[0])
def test_the_unit_routes_to_the_line(unit):
    """The spans.json unit that holds the source unit is a blocked rule of the block (no clause map is claimed, so it
    stays UNFORMALISED), and a `rule` placement of the build names the block with a prefix of the sentence."""
    name, (a, b), span_id, sentence = unit
    record = _spans()[span_id]
    assert record["span"][0] <= a < b <= record["span"][1], name
    assert record["blocked_rule"] == BLOCK, name
    assert (record["status"], record["reason"], record["waits"]) == ("UNFORMALISED", "unmapped_clause", ["AP"]), name
    assert any(value == ("rule", BLOCK, ()) and sentence.startswith(phrase)
               for phrase, value in B.PLACEMENTS.items()), name


def test_only_these_units_route_to_the_line():
    assert sorted(i for i, u in _spans().items() if u.get("blocked_rule") == BLOCK or u.get("rule") == BLOCK) == \
        sorted(unit[2] for unit in UNITS)


@pytest.mark.parametrize("unit", UNITS, ids=lambda u: u[0])
def test_the_legend_and_header_quote_the_sentence_whole(unit):
    """Needs no source: the sentence is one whole quotation of the act's legend and of the block's header."""
    _name, _span, _id, sentence = unit
    assert Q.plain(sentence) in _legend_quotes()
    assert Q.plain(sentence) in [Q.plain(q) for q in Q.quotes(_block())]


def test_the_legend_quotes_exactly_the_four_sentences():
    assert _legend_quotes() == [Q.plain(unit[3]) for unit in UNITS]
    assert [Q.plain(q) for q in Q.quotes(_block())] == _legend_quotes()


@pytest.mark.parametrize("unit", UNITS, ids=lambda u: u[0])
def test_the_legend_text_is_the_source_text_of_the_unit(unit):
    """With the pinned source: the legend's quotation of the unit equals the source text inside the unit's byte span
    (after its bullet), under the case's normalisation."""
    name, (a, b), _id, sentence = unit
    source = pinned_source("openai-preparedness").read_bytes()
    passage = source[a:b].decode().removeprefix("• ")
    assert Q.plain(passage) == Q.plain(sentence), name
    assert Q.plain(passage) in _legend_quotes(), name


def test_the_build_places_exactly_these_units_on_the_block():
    """With the pinned source: the build's placements of the block locate exactly the four spans units."""
    source = pinned_source("openai-preparedness").read_bytes()
    spans = B.segments(source)
    pages = [0] + [i + 1 for i, byte in enumerate(source) if byte == 10]
    placed = {f"p{sum(p <= spans[index][0] for p in pages)}-u{index + 1}"
              for phrase, (kind, ident, _waits) in B.PLACEMENTS.items() if ident == BLOCK
              for index in [B._located(source, spans, phrase)]}
    assert placed == {unit[2] for unit in UNITS}
    assert not Q.quote_faults([_block()], source.decode())
