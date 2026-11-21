"""srccov-rl-anthropic-rsp-1121: the 3.6.1 reviewer selection criteria are rule lines the reader is shown.

The source-coverage map (reviews/source-coverage-1119 in manage-agents, rows srccov-anthropic-rsp-27/28/29-1119)
tagged eight RSP units 'none: translation omission'. Four are carried here: the lead-in S0219 "We will select external
reviewers that:" and its criteria S0220, S0222 and S0224. Each criterion is one rule line of rules.d1.ve that forbids
selecting a candidate that fails it, the condition a new open-term predicate (OT25, OT24) whose legend in
environment.d1.json quotes the lead-in and the criterion. The span record of each unit in spans.json names the rule
and keeps its open term, so the unit stays OPEN. The other four units are dropped (REPORT section 0).

A run is a list of byte ranges of the pinned source text joined with one space, after the project's quote
normalisation (usecases/safetyfw_accounting.py `norm`). With the pinned text stored, the test reads it
(tests/pinned_source.py); without it, it checks that the legend holds a run with the recorded SHA-256 and length.
"""
import hashlib
import json
import re

import pytest

import test_fsf_repair_f6_sl2plus_1119 as f6
import test_rsp_fidelity_fix as fix
import test_safetyfw_usecases as base
from tests.pinned_source import pinned_source

RSP = base.RSP
LEAD_IN = ("S0219", 36952, 36991)  # "We will select external reviewers that:" (its heading is not a carry)

# (map unit, block id, predicate, the rule line, span record, open term, run pieces, SHA-256, byte length of the run)
KEPT = [
    ("S0220", "f15-expertise", "candidate_lacks_expertise",
     'Rule 1. Every situation must not have the candidate selected as an external reviewer, if that situation is '
     'classified as "candidate_lacks_expertise".',
     "s361-select", "ot25_reviewer_criteria", [LEAD_IN, ("S0220", 36996, 37108)],
     "7728c697a99fb883c054adff07e47113ad274ff944b89b7ac75aab94574ed258", 151),
    ("S0222", "f15-candid", "candidate_lacks_candid_incentives",
     'Rule 1. Every situation must not have the candidate selected as an external reviewer, if that situation is '
     'classified as "candidate_lacks_candid_incentives".',
     "s361-candid", "ot25_reviewer_criteria", [LEAD_IN, ("S0222", 37262, 37437)],
     "75210298301a0acef89b00a96c7db45cc5048107b015b6cd9e56907da55c4d5d", 215),
    ("S0224", "f15-conflicts", "candidate_has_conflict_of_interest",
     'Rule 1. Every situation must not have the candidate selected as an external reviewer, if that situation is '
     'classified as "candidate_has_conflict_of_interest".',
     "s361-conflicts", "ot24_conflicts_of_interest", [LEAD_IN, ("S0224", 37618, 37679)],
     "f24cfa53cf676c26bd92a1e961facfc3e24cb78998fbfaf9e7ba52a586c65faa", 100),
]


def _norm(text):
    return fix._accounting().norm(text).strip()


def _blocks():
    """rules.d1.ve as {block id: (header, rule line)}: the file the reader is shown."""
    lines = (RSP / "rules.d1.ve").read_text(encoding="utf-8").splitlines()
    return {re.match(r"## ([a-z0-9-]+) \|", h)[1]: (h, t) for h, t in zip(lines[::2], lines[1::2])}


def _predicates():
    return json.loads((RSP / "environment.d1.json").read_text(encoding="utf-8"))["vocabulary"]["predicates"]


def _spans():
    return {u["id"]: u for u in json.loads((RSP / "spans.json").read_text(encoding="utf-8"))["units"]}


def _source():
    path = pinned_source("anthropic-rsp", skip=False)
    return None if path is None else path.read_bytes()


def _run_text(source, pieces):
    return " ".join(_norm(source[start:end].decode("utf-8")) for _, start, end in pieces)


def _holds_hashed_run(text, digest, length):
    data = text.encode("utf-8")
    return any(hashlib.sha256(data[i:i + length]).hexdigest() == digest for i in range(len(data) - length + 1))


@pytest.mark.parametrize("unit", KEPT, ids=[k[0] for k in KEPT])
def test_each_kept_unit_has_its_rule_line_in_the_carrier(unit):
    _, block, predicate, line, _, _, _, _, _ = unit
    blocks = _blocks()
    assert block in blocks, block
    header, text = blocks[block]
    assert text == line
    # A commitment ("We will select"), read with every choice, its header quoting the lead-in and the criterion.
    assert header.startswith(f"## {block} | always | RS0 | F15, 3.6.1 \"We will select external reviewers that:\"")
    assert f'classified as "{predicate}"' in text and predicate in _predicates()


@pytest.mark.parametrize("unit", KEPT, ids=[k[0] for k in KEPT])
def test_each_kept_unit_routes_to_its_rule_and_keeps_its_open_term(unit):
    map_unit, block, _, _, record, term, pieces, _, _ = unit
    found = _spans()[record]
    for _, start, end in pieces[1:]:
        assert found["span"][0] <= start and end <= found["span"][1], map_unit
    assert found["rule"] == block and found["kind"] == "norm"
    assert found["open_terms"] == [term] and found["status"] == "OPEN", map_unit
    if map_unit == "S0220":  # the lead-in sits in the same record as the first criterion
        assert found["span"][0] <= LEAD_IN[1] and LEAD_IN[2] <= found["span"][1]


@pytest.mark.parametrize("unit", KEPT, ids=[k[0] for k in KEPT])
def test_each_legend_quotes_the_source_word_for_word(unit):
    map_unit, _, predicate, _, _, _, pieces, digest, length = unit
    legend = _predicates()[predicate]["description"]
    normal = _norm(legend)
    source = _source()
    if source is not None:
        text = _run_text(source, pieces)
        assert hashlib.sha256(text.encode()).hexdigest() == digest and len(text.encode()) == length, map_unit
        assert text in normal, (map_unit, text)
        # The counter cuts citation parentheses whole; the quote must survive that cut.
        assert _norm(f6._cut_inside(text)) in _norm(f6._cut_inside(legend)), map_unit
    assert _holds_hashed_run(normal, digest, length), map_unit
    assert [m.group(0)[:60] for m in f6.CITATION_PARENTHESIS.finditer(legend) if '"' in m.group(0)] == []
    # An open term names its decider: the company, as for every 3.6.1 term (build_document OPEN_TERMS).
    number = "OT24" if predicate == "candidate_has_conflict_of_interest" else "OT25"
    assert legend.endswith(f'Open term {number}, decided by the company ("we")'), predicate


@pytest.mark.skipif(not base.LEAN_SERVICE.exists(), reason="the Lean service is not built")
@pytest.mark.parametrize("unit", KEPT, ids=[k[0] for k in KEPT])
def test_each_rule_parses_to_a_prohibition_guarded_by_its_predicate(unit):
    _, block, predicate, _, _, _, _, _, _ = unit
    parsed = json.loads(base.rsp_translation.parsed_rule(block))
    assert (parsed["predicate"], parsed["sign"], parsed["guard"]) == (
        "candidate_selected", False, ["unary", predicate, ["var", 0]])
