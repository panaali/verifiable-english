"""srccov-rl-openai-preparedness-1121: the condition test for the rule line that carries 4.2's sufficiency basis.

The source-coverage map (manage-agents reviews/source-coverage-1119, an Opus reading at VE pin e53db4e8fc) tagged
four PF units "none: translation omission": 4.2's lead-in "The SAG will make this determination based on:" (S0171)
and three of its four bullets (S0172, S0173, S0186). The fourth bullet, S0187 ("The baseline risk from other
deployments, ..."), is tagged quantifier-scope, out of scope: the line names three of the four grounds, so the block's
header quotes S0187 too and accounting.d1.txt records its loss (`loss 1`, a dropped conjunct). The REPORT
(docs/infra/srccov-rl-openai-preparedness-1121/REPORT.md) keeps the four units and Appendix B's lead-in S0259 (review
F2: routed to f16-sag-recommend, the one line that carries one of its items) and drops the other in-scope units with a
reason each. For each kept unit this file checks that:

* the line exists in the carrier the reader is shown: block `sr-sufficiency` of rules.d1.ve, whose act
  `sufficiency_basis` is a regulated predicate of environment.d1.json;
* the unit's spans.json record routes to it (`blocked_rule`), and the build places exactly these four units on it;
* the unit's sentence is one whole quotation of the block's legend and header, and that quotation equals the
  pinned source text inside the unit's byte span under the case's normalisation (quote_evidence.plain).

For every lead-in of the item's scope (the map's `lead-in:` notes, saved in LEAD_INS) it checks one rule (review F1,
METHOD amendment 8): a block that carries a lead-in either routes each of its items or quotes the item in its header
and records the item's loss in accounting.d1.txt; and a lead-in is routed to a block exactly when the REPORT keeps it.
Review F2: the verdict and the reason of each lead-in follow from where its items are carried (MAP_CARRIED, the
REPORT's "already carried at main" legends and the routes of spans.json): no carrying line, dropped; one, kept on that
line; more than one, dropped because a unit routes to one block. The REPORT's rows and its rule paragraph must say so.

Every test fails on the pre-change main: the block, the act and the routes do not exist there.
"""
from __future__ import annotations

import dataclasses
import importlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.pinned_source import pinned_source

REPO = Path(__file__).resolve().parents[1]
PF = REPO / "usecases" / "openai-preparedness"
REPORT = REPO / "docs" / "infra" / "srccov-rl-openai-preparedness-1121" / "REPORT.md"
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
    ("S0259", (48713, 48764), "KEPT",
     (("S0260", (48765, 48912)), ("S0261", (48913, 49138)), ("S0262", (49139, 49314)), ("S0263", (49315, 49518)))),
)

# Review F2: the map's CARRIED-OTHER-WORDS items among the lead-ins' items, each with the carrier a line reads it
# through (a rule block or a reading set), saved from openai-preparedness.md and its spans notes. The REPORT's
# "already carried at main" rows add the legend that carries an item (S0028), and spans.json adds the routes the build
# gives (this item's sr-sufficiency and f16-sag-recommend lines).
MAP_CARRIED = {"S0025": "rs3-no-deploy", "S0026": "f3-develop", "S0148": "rs16-recommend", "S0150": "rs8-distilled",
               "S0262": "f16-sag-recommend"}
LEGEND_CARRIED = re.compile(r"already carried at main: the legend of `([a-z_]+)`")
NONE_CARRIES = "no line carries its items"
SPLIT = "its items are carried by more than one line"


def _rows(report):
    """The verify table: unit -> (verdict, reason)."""
    cells = (line.split("|") for line in report.splitlines() if line.startswith("| S0"))
    return {c[1].strip(): (c[3].strip(), c[4].strip()) for c in cells}


def _item_carriers(spans, rows, carried):
    """Lead-in -> item -> the carriers that carry the item (map, REPORT legend row, spans.json route of the item)."""
    out = {}
    for lead_in, (a, b), _verdict, items in LEAD_INS:
        out[lead_in] = {}
        for item, (c, d) in items:
            found = {carried[item]} if item in carried else set()
            found |= set(LEGEND_CARRIED.findall(rows.get(item, ("", ""))[1]))
            found |= {r.get("blocked_rule") or r.get("rule") for r in spans.values() if c <= r["span"][0] < d
                      and r["span"][1] <= d + 1 and (r.get("blocked_rule") or r.get("rule"))}
            out[lead_in][item] = found
    return out


def _names(units):
    units = sorted(units)
    return units[0] if len(units) == 1 else ", ".join(units[:-1]) + " and " + units[-1]


def _carrier_faults(report, spans, carried=MAP_CARRIED):
    """Review F2 (METHOD amendment 8): each lead-in's verdict and REPORT reason against the carriers of its items.
    No carrier: DROPPED, "no line carries its items". One: KEPT and routed to it. More: DROPPED, "its items are carried
    by more than one line", each carrier named. Every route spans.json gives a unit that overlaps the list's items (and
    not the lead-in) is a carrier of the list, so a route the saved table misses is refused. The rule paragraph lists
    each lead-in under its class."""
    rows, faults, classes = _rows(report), [], {"none": [], "one": [], "split": []}
    for lead_in, (a, b), _verdict, items in LEAD_INS:
        per_item = _item_carriers(spans, rows, carried)[lead_in]
        lines = set().union(*per_item.values())
        routed = {r.get("blocked_rule") or r.get("rule") or r.get("reading_set") for r in spans.values()
                  if any(r["span"][0] < d and c < r["span"][1] for _item, (c, d) in items)
                  and not (r["span"][0] < b and a < r["span"][1])}
        for route in sorted(routed - {None} - lines):
            faults.append(f"{lead_in}: spans.json routes an item's unit to {route}, which carries none of its items")
        verdict, reason = rows[lead_in]
        kind = "none" if not lines else "one" if len(lines) == 1 else "split"
        classes[kind].append(lead_in)
        expected = "KEPT" if kind == "one" else "DROPPED"
        if verdict != expected:
            faults.append(f"{lead_in}: carried items {sorted(lines)} make it {expected}, the REPORT says {verdict}")
        if kind == "none" and NONE_CARRIES not in reason:
            faults.append(f"{lead_in}: no line carries its items, and its row does not say so")
        if kind != "none" and NONE_CARRIES in reason:
            faults.append(f"{lead_in}: its row says no line carries its items, but {sorted(lines)} carry them")
        if (kind == "split") != (SPLIT in reason):
            word = "omits" if kind == "split" else "says"
            faults.append(f"{lead_in}: {len(lines)} carrying lines, and its row {word} '{SPLIT}'")
        for line in sorted(lines):
            if kind != "none" and f"`{line}`" not in reason:
                faults.append(f"{lead_in}: its row does not name the carrier `{line}`")
        if kind == "one" and _routes(spans, a, b) != lines:
            faults.append(f"{lead_in}: routed to {sorted(_routes(spans, a, b))}, not to its carrier {sorted(lines)}")
    expected_sentences = [f"No line carries the items of {_names(classes['none'])}.",
                          f"The items of {_names(classes['split'])} are carried by more than one line",
                          f"{_names(classes['one'])} each have one line that carries their items"]
    for sentence in expected_sentences:
        if sentence not in report:
            faults.append(f"the rule paragraph lacks: {sentence}")
    return faults



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
    """Review F1's commit d6b73703: the header quotes the lead-in and three bullets only."""
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
        spans = {**spans, "p12-u200": {**spans["p12-u200"], "blocked_rule": BLOCK}}
    else:
        spans = {**spans, UNITS[0][2]: {k: v for k, v in spans[UNITS[0][2]].items() if k != "blocked_rule"}}
    assert _lead_in_faults(blocks, spans, sidecar), mutant



# Review F2: the rows and rule paragraph of commit 2dc12b6f, which said no line carries the items of S0020 and S0259.
F2_ROWS = {"S0020": ('| S0020 | srccov-openai-preparedness-7-1119 | DROPPED | lead-in (amendment 8) of S0021-S0029: no '
                     'line carries its items (S0021 and S0027 wait on the predicate budget, S0022 (temporal) and S0024 '
                     '(modality) are out of scope, the rest are dropped below), so no line can carry its force |'),
           "S0259": ("| S0259 | srccov-openai-preparedness-27-1119 | DROPPED | lead-in of Appendix B's SAG duties "
                     '(S0260-S0263): no line carries its items (S0260 and S0263 wait on the predicate budget; S0261 '
                     '(quantifier-scope) and S0262 are out of scope), so no line can carry its force |')}
F2_PARAGRAPH = ('**The rule for a lead-in** (METHOD amendment 8, review F1). A lead-in is carried only by a line '
                "that carries its items with the lead-in's force. An item that line does not carry (out of scope, or "
                "dropped) is quoted in the block's header and recorded as a `loss` in accounting.d1.txt, so the "
                'omission is visible. The six dropped lead-ins (S0020, S0030, S0126, S0147, S0190, S0259) have no '
                'line that carries their items. S0171 is carried, and its fourth item S0187 is quoted and recorded '
                'as `loss 1`. `test_a_carried_lead_in_accounts_for_every_item` checks this over all seven lead-ins, '
                "from the map's `lead-in:` notes saved in the test.")


def _report():
    return REPORT.read_text(encoding="utf-8")


def test_each_lead_in_has_the_verdict_and_reason_its_items_carriers_give():
    """Review F2: no carrying line, DROPPED with "no line carries its items"; one, KEPT on that line; more than one,
    DROPPED with each carrier named. S0259 is kept on f16-sag-recommend, which carries S0262; S0020's carried items
    are on rs3-no-deploy, f3-develop and the legend of existing_at_publication; S0147's on rs16-recommend and
    rs8-distilled."""
    assert _carrier_faults(_report(), _spans()) == []
    carriers = _item_carriers(_spans(), _rows(_report()), MAP_CARRIED)
    assert set().union(*carriers["S0259"].values()) == {"f16-sag-recommend"}
    assert set().union(*carriers["S0020"].values()) == {"rs3-no-deploy", "f3-develop", "existing_at_publication"}
    assert set().union(*carriers["S0147"].values()) == {"rs16-recommend", "rs8-distilled"}


def test_review_f2_probe():
    """The review's PROBE F2: the S0020 and S0259 rows do not say that no line carries their items, and the REPORT does
    not say it of all six lead-ins it dropped then."""
    r = _report()
    rows = {line.split("|")[1].strip(): line for line in r.splitlines() if line.startswith("| S0")}
    bad = [k for k in ("S0020", "S0259") if NONE_CARRIES in rows[k]]
    assert not bad and "(S0020, S0030, S0126, S0147, S0190, S0259) have no line that carries their items" not in r, bad


def test_the_carriers_the_test_saves_exist():
    """Each saved carrier is a block of rules.d1.ve or facts.d1.ve or a reading set the build places, and each legend
    an "already carried at main" row names is a predicate of environment.d1.json."""
    sets = {ident for kind, ident, _waits in B.PLACEMENTS.values() if kind == "readings"}
    assert {c for c in MAP_CARRIED.values()} <= set(_blocks()) | sets
    legends = set(LEGEND_CARRIED.findall(_report()))
    assert legends and legends <= set(_predicates())


@pytest.mark.parametrize("mutant", ["review F2's rows", "S0259 dropped", "map entry forgotten", "carrier not named",
                                    "a new route", "kept on another line", "paragraph"])
def test_the_carrier_check_refuses_review_f2_and_its_variants(mutant):
    """Each mutant of the fixed tree is refused: F2 itself (the rows and paragraph of commit 2dc12b6f), the kept
    lead-in turned DROPPED, a carried item missing from the saved table, a carrier the row does not name, a route of an
    item's unit to a line that carries none of the list, a kept lead-in routed to another line, a stale paragraph."""
    report, spans, carried = _report(), _spans(), dict(MAP_CARRIED)
    rows = {line.split("|")[1].strip(): line for line in report.splitlines() if line.startswith("| S0")}
    if mutant == "review F2's rows":
        for unit, line in F2_ROWS.items():
            report = report.replace(rows[unit], line)
        paragraph = [p for p in report.splitlines() if p.startswith("**The rule for a lead-in**")][0]
        report = report.replace(paragraph, F2_PARAGRAPH)
    elif mutant == "S0259 dropped":
        report = report.replace(rows["S0259"], rows["S0259"].replace("| KEPT |", "| DROPPED |"))
    elif mutant == "map entry forgotten":
        del carried["S0150"]
    elif mutant == "carrier not named":
        report = report.replace(rows["S0147"], rows["S0147"].replace("`rs8-distilled`", "RS8"))
    elif mutant == "a new route":
        spans = {**spans, "p4-u23": {**spans["p4-u23"], "blocked_rule": "f2-deploy"}}
    elif mutant == "kept on another line":
        spans = {**spans, "p16-u272": {**spans["p16-u272"], "blocked_rule": "f16-informed"}}
    else:
        report = report.replace("No line carries the items of", "No line carries the lists of")
    assert report != _report() or spans != _spans() or carried != MAP_CARRIED
    assert _carrier_faults(report, spans, carried), mutant


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
