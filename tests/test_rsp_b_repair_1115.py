"""rsp-b-repair-1115: the four B repairs of the RSP blocker classification (DRI decisions 2026-11-15, item 2).

X36: the D2 and D3 documents (the audit's D2D3 unit) have an accounting line, and every word it records is a word
those documents do not carry. X37/X38: in_scope's legend quotes both 3.1 sentences. X40: the full-review act's legend
quotes F14's whole sentence. X43: F6's rule has its own cause condition ("simply because we are unable to achieve
them"): a revision for that cause is to be avoided, a revision for another cause is not F6's case. The carrier checks
use the omission counter's own token rule (tests/test_rsp_fidelity_fix.py's emulation of it).
"""
import json
import re

import pytest

import test_rsp_fidelity_fix as fix
import test_safetyfw_usecases as base

RSP = base.RSP
rsp_run, rsp_translation, rsp_vocabulary, rsp_stage0 = (base.rsp_run, base.rsp_translation, base.rsp_vocabulary,
                                                        base.rsp_stage0)
needs_lean = fix.needs_lean
rsp_modules = base.rsp_modules
SAVED_ACCOUNTING = base.REPO / "docs/usecases/safetyfw/anthropic-rsp/accounting.json"


def _rule_carrier(block_id):
    """The counter's carrier of a rules.d1.ve block: one token set per body statement (quoted literals and comments
    stripped) and one per legend of a predicate the block uses (its vocabulary-file entry)."""
    body = fix._block("rules.d1.ve", block_id).text
    environment = json.loads((RSP / "environment.d1.json").read_text())
    lines = (RSP / "rsp_vocabulary.py").read_text().splitlines()
    statements = [re.sub(r"\s*(#|--|//).*$", "", re.sub(r'"[^"]*"', " ", line)) for line in body.splitlines()
                  if not line.lstrip().startswith(fix.COMMENT_STARTS)]
    entries = ["\n".join(re.sub(r"\s#.*$", "", line) for line in fix._legend_entry_lines(key, lines)
                         if not line.lstrip().startswith(fix.COMMENT_STARTS))
               for key in fix._used_predicates(body, environment)]
    return [set(re.findall(r"[a-z0-9_]+", fix._counter_norm(s))) for s in statements + entries if s.strip()]


def _carried(words, block_id):
    want = fix._omitted_words(words)
    return bool(want) and any(want <= segment for segment in _rule_carrier(block_id))


def _entries(block_id):
    acc = fix._accounting()
    [entries] = [e for _, b, e, _ in acc.read_sidecar(RSP / "accounting.d1.txt") if b == block_id]
    return entries


def _counted(text):
    return re.sub(r"\s+", " ", fix._counter_norm(text))


# --- X36: the D2D3 accounting line ----------------------------------------------------------------------------------

# Footnote 1's clause is no longer a loss: D2's catastrophic legend carries the footnote whole
# (rsp-repair-r1-catastrophic-1119). Nor is 3.1's Scope sentence: D3's coverage-date legend carries it whole
# (defs-repair-anthropic-rsp-1119), so the D2D3 line omits nothing.
D2D3_LOSSES = ()


def _d2d3_carriers():
    """Every word D2 and D3 state: the harm constants' words (D2), the changelog dates, the date questions, the
    receipt count and the date constants' descriptions (D3)."""
    harms = " ".join(words for _, words in rsp_stage0.HARMS.values())
    dates = json.dumps([rsp_stage0.CHANGELOG, rsp_stage0.DATE_QUESTIONS, rsp_stage0.RECEIPT_COUNT])
    env = rsp_stage0.date_environment(("start_day", "limit_day"))
    described = " ".join(c.description for c in env.constants.values())
    return _counted(" ".join((harms, dates, described)))


def test_d2d3_line_exists_parses_and_is_saved():
    """One D2D3 line, the last of the sidecar, read by the tool as the D2D3 collection with no problem; the saved
    --source report agrees; its losses are exactly the clause below, class 1."""
    acc = fix._accounting()
    lines = acc.read_sidecar(RSP / "accounting.d1.txt")
    d2d3 = [line for line in lines if line[1] == "D2D3"]
    assert len(d2d3) == 1 and d2d3[0][3] is None and d2d3[0][0] == lines[-1][0]
    entries = d2d3[0][2]
    assert [(e["words"], e["reason"], e["arg"]) for e in entries if e["reason"] == "loss"] == [
        (words, "loss", "1") for words in D2D3_LOSSES]
    assert {e["reason"] for e in entries} <= {"loss", "exposition"}
    saved = json.loads(SAVED_ACCOUNTING.read_text())
    for report in (acc.account(RSP), saved):
        assert report["problems"] == []
        assert [c for c in report["collections"] if c["id"] == "D2D3"] == [
            {"id": "D2D3", "entries": entries, "problems": []}]


def test_d2d3_records_only_words_d2_and_d3_do_not_carry():
    """Each recorded loss is absent from every D2/D3 carrier, and the effective date's word is carried (v3.4's date
    constant quotes page 1), so it is not recorded."""
    carriers = _d2d3_carriers()
    for words in D2D3_LOSSES:
        assert _counted(words) not in carriers, words
    assert "effective july 8, 2026" in carriers
    line = (RSP / "accounting.d1.txt").read_text(encoding="utf-8")
    assert '"Effective' not in line and '"July 8, 2026' not in line
    # The harms D2 states are carried in their own words (S1-T1 .. S5 rest on them).
    for words in ("serious potential for catastrophic damages", "potential for catastrophic harm",
                  "such as existential threats or fundamental destabilization of global systems",
                  "threats to international security and/or rapid disruptions to the global balance of power"):
        assert words in carriers, words


# --- X37/X38: in_scope quotes both 3.1 sentences --------------------------------------------------------------------

def test_in_scope_legend_quotes_both_31_sentences():
    legend = _counted(fix._legend("in_scope"))
    assert _counted("It will cover all publicly deployed models as of the coverage date, as well as any internally "
                    "deployed models as of the coverage date") in legend
    assert _counted("this will—at a minimum—include any internal models that we are deploying for large-scale, fully "
                    "autonomous research") in legend
    assert "a classification, never a duty" in legend


@pytest.mark.parametrize("block_id", ("f8-public", "f8-autonomous"))
def test_f8_restates_entries_are_carried(block_id):
    """The counter's token rule finds every restates entry of f8-public and f8-autonomous in one carrier segment."""
    entries = [e for e in _entries(block_id) if e["reason"] == "restates"]
    assert entries and all(_carried(e["words"], block_id) for e in entries), block_id


# --- X40: the full-review act's legend quotes F14's whole sentence --------------------------------------------------

def test_full_review_legend_quotes_f14_and_carries_its_entries():
    header = fix._header_quote("f14-full-review")
    assert header.startswith("At a minimum, we will complete") and header in fix._legend("full_review")
    for words in ("At a minimum", "complete a full external review process", "anytime a Risk Report covers"):
        assert _carried(words, "f14-full-review"), words


# --- C X42/X44: the one-line legend quotes ---------------------------------------------------------------------------

@pytest.mark.parametrize("block_id", ("f20-notice-p", "f7-publish"))
def test_c_restates_entries_are_carried(block_id):
    entries = [e for e in _entries(block_id) if e["reason"] == "restates"]
    assert entries and all(_carried(e["words"], block_id) for e in entries), block_id


# --- X43: F6's cause condition ---------------------------------------------------------------------------------------

def test_f6_guard_has_the_revision_and_its_cause():
    guard = fix._rule("f6-strive-default")["guard"]
    assert fix._unaries(guard) == {"goal_revised_less_ambitious", "revised_because_unable"}
    # RS12strive's distinguishing situation (build_document) meets the whole guard, so default and intent differ on it.
    assert {name for name, *_ in base.rsp_build.DISTINGUISHING["RS12strive"]} == fix._unaries(guard)
    assert "simply because we are unable to achieve them" in fix._legend("revised_because_unable")
    assert "simply because" not in fix._legend("goal_revised_less_ambitious")
    for words in ("we will strive to", "where we revise the goals in a less ambitious direction simply because we are "
                  "unable to achieve them"):
        assert _carried(words, "f6-strive-default"), words


def _revision(case_id, *atoms):
    return {"id": case_id, "family": "G", "thresholds": [], "situation": "", "findings": {}, "extra": atoms}


@needs_lean
def test_f6_forbids_a_revision_for_inability_and_not_for_another_cause(rsp_modules):
    """Inability (both atoms): under RS12strive = default F6 is the selected goals_kept rule (the revision is to be
    avoided). Another cause (the revision alone): no reading selects F6, so F6 does not forbid it."""
    unable = rsp_run.query(_revision("rspb-unable", "goal_revised_less_ambitious", "revised_because_unable"),
                           "goals_kept")
    by_reading = {row["choice"]["RS12strive"]: row for row in unable["choices"]}
    assert by_reading["default"]["holds"] and by_reading["default"]["rules"] == ["f6-strive-default"]
    assert not by_reading["intent"]["holds"]
    other = rsp_run.query(_revision("rspb-other", "goal_revised_less_ambitious"), "goals_kept")
    assert other["choices"] and not any(row["holds"] or row["rules"] for row in other["choices"])


@needs_lean
def test_g8_keeps_its_keyed_answer(rsp_modules):
    """G8's case states the cause ("because it was not achieved"): its keyed answer SOME(intent) does not move."""
    key = fix.KEY["G8"]["key"]
    assert key == "SOME(intent)" and rsp_run.same_set(key, fix._answer("G8"))


# --- PLAN 3.1's RS3c row agrees with section 12, item 20(j), and the facts header -----------------------------------

def test_plan_31_does_not_list_rs3c_as_a_reading_set():
    """The row says RS3c is not a reading set and cites 20(j); the accounting tool's PLAN 3.1 parse no longer lists it,
    as neither READING_SETS nor any facts.d1.ve header does."""
    acc = fix._accounting()
    sets, limits = acc.plan_tables(RSP / "PLAN.md")
    assert "RS3c" not in sets and {"RS3i", "RS3o"} <= sets and 20 in limits
    assert "RS3c" not in rsp_translation.READING_SETS
    assert not any(name == "RS3c" for block in rsp_translation.read_blocks("facts.d1.ve") for name, _ in block.when)
    plan = (RSP / "PLAN.md").read_text(encoding="utf-8")
    [row] = [line for line in plan.splitlines() if line.startswith("| RS3c")]
    assert "RS3c is not a reading set (section 12, item 20(j))" in row and "always a third condition" in row
    assert "(j) RS3c is no longer a reading set" in plan
