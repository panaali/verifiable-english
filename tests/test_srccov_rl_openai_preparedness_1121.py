"""srccov-rl-openai-preparedness-1121: the condition test for the rule line that carries 4.2's sufficiency basis.

The source-coverage map (manage-agents reviews/source-coverage-1119, an Opus reading at VE pin e53db4e8fc) tagged
four PF units "none: translation omission": 4.2's lead-in "The SAG will make this determination based on:" (S0171)
and three of its four bullets (S0172, S0173, S0186). The fourth bullet, S0187 ("The baseline risk from other
deployments, ..."), is tagged quantifier-scope, out of scope: the line names three of the four grounds, so the block's
header quotes S0187 too and accounting.d1.txt records its loss (`loss 1`, a dropped conjunct). The REPORT
(docs/infra/srccov-rl-openai-preparedness-1121/REPORT.md) keeps the four units and drops the other in-scope units
with a reason each. For each kept unit this file checks that:

* the line exists in the carrier the reader is shown: block `sr-sufficiency` of rules.d1.ve, whose act
  `sufficiency_basis` is a regulated predicate of environment.d1.json;
* the unit's spans.json record routes to it (`blocked_rule`), and the build places exactly these four units on it;
* the unit's sentence is one whole quotation of the block's legend and header, and that quotation equals the
  pinned source text inside the unit's byte span under the case's normalisation (quote_evidence.plain).

For every lead-in of the item's scope (the map's `lead-in:` notes, saved in LEAD_INS) it checks one rule (review F1,
METHOD amendment 8): a block that carries a lead-in either routes each of its items or quotes the item in its header
and records the item's loss in accounting.d1.txt; and a lead-in is routed to a block exactly when the REPORT keeps it.

Every test fails on the pre-change main: the block, the act and the routes do not exist there.
"""
from __future__ import annotations

import dataclasses
import importlib
import importlib.util
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
_SPEC = importlib.util.spec_from_file_location("safetyfw_accounting_1121", REPO / "usecases" / "safetyfw_accounting.py")
A = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(A)

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
# The lead-in's fourth bullet: quantifier-scope (out of scope), not routed to the block; quoted and recorded as a loss.
OMITTED = ("S0187", (36823, 37039), "p12-u197",
           "The baseline risk from other deployments, based on a review of any non-OpenAI deployments of models which "
           "have crossed the capability thresholds and any public evidence of the safeguards applied for those models.")
OMITS = f'{BLOCK} | omits: "{OMITTED[3].removesuffix(".")}" loss 1'

# Every lead-in of the item's 104 units: (lead-in, its byte span, the REPORT's verdict, its items with their byte
# spans). Saved from the map (reviews/source-coverage-1119: the `lead-in:` notes of openai-preparedness.md and the
# spans of units-openai-preparedness.tsv), so the test reads no file outside the repository.
LEAD_INS = (
    ("S0020", (4999, 5014), "DROPPED",
     (("S0021", (5015, 5278)), ("S0022", (5279, 5511)), ("S0023", (5512, 5686)), ("S0024", (5687, 5880)),
      ("S0025", (5881, 6013)), ("S0026", (6014, 6210)), ("S0027", (6211, 6410)), ("S0028", (6411, 6674)),
      ("S0029", (6675, 6824)))),
    ("S0030", (6825, 6922), "DROPPED",
     (("S0031", (6923, 7000)), ("S0032", (7001, 7153)), ("S0033", (7154, 7343)), ("S0034", (7344, 7519)),
      ("S0035", (7520, 7742)), ("S0036", (7743, 7802)), ("S0037", (7803, 7992)), ("S0038", (7993, 8227)),
      ("S0039", (8228, 8342)), ("S0040", (8343, 8741)), ("S0041", (8742, 8843)), ("S0042", (8844, 9028)))),
    ("S0126", (27237, 27288), "DROPPED",
     (("S0127", (27289, 27430)), ("S0128", (27431, 27627)), ("S0129", (27628, 27783)), ("S0130", (27784, 28068)))),
    ("S0147", (30839, 30857), "DROPPED",
     (("S0148", (30858, 31055)), ("S0149", (31056, 31291)), ("S0150", (31292, 31568)), ("S0151", (31571, 31692)))),
    ("S0171", (34586, 34632), "KEPT",
     (("S0172", (34633, 34718)), ("S0173", (34719, 34850)), ("S0186", (36739, 36822)), ("S0187", (36823, 37039)))),
    ("S0190", (37321, 37388), "DROPPED", (("S0191", (37389, 37557)), ("S0192", (37558, 37937)))),
    ("S0259", (48713, 48764), "DROPPED",
     (("S0260", (48765, 48912)), ("S0261", (48913, 49138)), ("S0262", (49139, 49314)), ("S0263", (49315, 49518)))),
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
    assert OMITS in (PF / "accounting.d1.txt").read_text(encoding="utf-8").splitlines()


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


def test_the_legend_quotes_the_carried_sentences_and_the_header_adds_the_fourth_bullet():
    """The legend quotes what the line carries; the header quotes the whole list, its fourth bullet last (review F1).
    The legend must not quote the fourth bullet: the accounting counts a used legend's words as carried."""
    assert _legend_quotes() == [Q.plain(unit[3]) for unit in UNITS]
    assert [Q.plain(q) for q in Q.quotes(_block())] == _legend_quotes() + [Q.plain(OMITTED[3])]


class _Lines:
    """Sidecar lines in memory, read by the accounting tool's own parser (A.read_sidecar reads a path's text)."""

    def __init__(self, lines):
        self.lines = lines

    def exists(self):
        return True

    def read_text(self, encoding="utf-8"):
        return "\n".join(self.lines) + "\n"


def _routes(spans, a, b):
    """The rule blocks that a spans record overlapping source bytes [a, b) routes to."""
    return {r.get("blocked_rule") or r.get("rule") for r in spans.values()
            if r["span"][0] < b and a < r["span"][1] and (r.get("blocked_rule") or r.get("rule"))}


def _lead_in_faults(blocks, spans, sidecar_lines, texts=None):
    """METHOD amendment 8 for a carried lead-in: each item is routed to the block that carries the lead-in, or quoted in
    that block's header with a `loss` entry of the block's accounting line that quotes it. `texts` (unit -> source
    sentence) ties each loss to its own item when the pinned source is at hand; without it, the number of unrouted items
    is checked against distinct loss entries the header quotes."""
    faults = []
    lines = {block_id: entries for _n, block_id, entries, _p in A.read_sidecar(_Lines(sidecar_lines))}
    for lead_in, (a, b), verdict, items in LEAD_INS:
        carriers = _routes(spans, a, b)
        if bool(carriers) != (verdict == "KEPT"):
            faults.append(f"{lead_in}: routed to {sorted(carriers)} but the REPORT says {verdict}")
        for block_id in sorted(carriers):
            header = [Q.plain(q) for q in Q.quotes(blocks[block_id])]
            losses = [Q.plain(e["words"]) for e in lines.get(block_id) or [] if e["reason"] == "loss"]
            quoted = [w for w in losses if any(w in h for h in header)]
            unrouted = [item for item, (c, d) in items if block_id not in _routes(spans, c, d)]
            for item in unrouted:
                if texts is None:
                    continue
                sentence = Q.plain(texts[item])
                if not any(sentence == h for h in header):
                    faults.append(f"{lead_in}: {block_id}'s header does not quote its item {item}")
                if not any(w and sentence.startswith(w) for w in quoted):
                    faults.append(f"{lead_in}: {block_id}'s accounting line records no loss for its item {item}")
            if texts is None and len(set(quoted)) < len(unrouted):
                faults.append(f"{lead_in}: {block_id} leaves {unrouted} unrouted with {len(set(quoted))} quoted "
                              f"loss entries")
    return faults


def _blocks():
    return {b.id: b for name in ("rules.d1.ve", "facts.d1.ve") for b in T.read_blocks(name)}


def _sidecar():
    return (PF / "accounting.d1.txt").read_text(encoding="utf-8").splitlines()


def _texts(source):
    return {item: source[c:d].decode().removeprefix("• ") for *_rest, items in LEAD_INS for item, (c, d) in items}


def _without_fourth_bullet(blocks):
    """Review F1's commit: the header quotes the lead-in and three bullets only."""
    block = blocks[BLOCK]
    source = block.source.replace(f" “{OMITTED[3]}”", "")
    assert source != block.source
    return {**blocks, BLOCK: dataclasses.replace(block, source=source)}


def test_a_carried_lead_in_accounts_for_every_item():
    """Needs no source (review F1): every lead-in the REPORT keeps is routed, every one it drops is not, and each item
    a carried lead-in's block does not route has a loss entry the header quotes."""
    assert _lead_in_faults(_blocks(), _spans(), _sidecar()) == []


def test_a_carried_lead_in_accounts_for_every_item_by_its_source_text():
    """With the pinned source: each unrouted item's own sentence is quoted in the header and named by a loss entry."""
    source = pinned_source("openai-preparedness").read_bytes()
    texts = _texts(source)
    assert Q.plain(texts[OMITTED[0]]) == Q.plain(OMITTED[3])
    assert _lead_in_faults(_blocks(), _spans(), _sidecar(), texts) == []


@pytest.mark.parametrize("mutant", ["no fourth bullet in the header", "omits nothing", "loss dropped",
                                    "dropped lead-in routed", "lead-in dropped from the route"])
def test_the_lead_in_check_refuses_review_f1_and_its_variants(mutant):
    """Each mutant of the fixed tree is refused: F1 itself (the header and accounting of commit d6b73703: three
    bullets, `omits: nothing`), a loss entry removed, and a route that contradicts the REPORT's verdict either way."""
    blocks, spans, sidecar = _blocks(), _spans(), _sidecar()
    if mutant == "no fourth bullet in the header":
        blocks = _without_fourth_bullet(blocks)
        sidecar = [f"{BLOCK} | omits: nothing" if line == OMITS else line for line in sidecar]
    elif mutant == "omits nothing":
        sidecar = [f"{BLOCK} | omits: nothing" if line == OMITS else line for line in sidecar]
    elif mutant == "loss dropped":
        sidecar = [line for line in sidecar if line != OMITS]
    elif mutant == "dropped lead-in routed":
        spans = {**spans, "p16-u272": {**spans["p16-u272"], "blocked_rule": BLOCK}}
    else:
        spans = {**spans, UNITS[0][2]: {k: v for k, v in spans[UNITS[0][2]].items() if k != "blocked_rule"}}
    assert _lead_in_faults(blocks, spans, sidecar), mutant


def test_the_accounting_tool_refuses_omits_nothing_for_the_block(tmp_path):
    """The tool, not only this file, holds the loss: with the fourth bullet in the header, `omits: nothing` leaves its
    words unaccounted."""
    side = tmp_path / "accounting.d1.txt"
    side.write_text("\n".join(f"{BLOCK} | omits: nothing" if line == OMITS else line for line in _sidecar()) + "\n",
                    encoding="utf-8")
    problems = A.account(PF, sidecar=side)["problems"]
    assert f"{BLOCK}: unaccounted word 'baseline' is in no entry" in problems
    assert all(p.startswith(f"{BLOCK}: ") for p in problems)
    assert A.account(PF)["problems"] == []


def test_the_fourth_bullet_keeps_its_own_record():
    """S0187's spans record is unchanged: UNFORMALISED for quantifier scope, routed to no block."""
    record = _spans()[OMITTED[2]]
    a, b = OMITTED[1]
    assert record["span"][0] <= a < b <= record["span"][1]
    assert (record["status"], record["reason"], record["waits"]) == ("UNFORMALISED", "quantifier_scope", ["SC"])
    assert "blocked_rule" not in record and "rule" not in record


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
