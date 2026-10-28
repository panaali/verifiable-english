"""Builds the D1 span-accounting document over the pinned RSP v3.4 text (PLAN sections 7 and 10, metric M3).

    python usecases/anthropic-rsp/build_document.py [--source PATH] [--check]

As safety-framework's builder, whose unit-spec helpers and coverage measurement it imports: the pinned text
(`rsp-3.4.txt`, 59,410 bytes, SHA-256 in PLAN section 1) is not committed, because the PDF states no licence. The
builder reads it from `--source` (default: the stored copy in `~/code/manage-agents/pilots/anthropic-rsp/source/`),
checks its hash, partitions every byte into the units of `UNITS`, loads the document with VE (`ve.document`), and
writes:

- `rsp.d1.ve.md` next to the source (the `ve-document@1` with the source prose, never committed);
- `spans.json` here: unit ids, byte spans, kinds, statuses, reasons and feature families, no prose;
- `coverage.json` here: `ve.document.coverage` of the loaded document, and the master map in which a unit routed to
  D2 or D3 takes CHECKED when that document's stage-0 check (`stage0.py`, P3 and P4) admits it with its evidence.

Each unit starts at its anchor (the first occurrence after the previous anchor) and runs to the next one; the first
starts at byte 0. Every reading set is written as a W2 set with pending readings: the readings of each are the rules
and premises `READINGS` names, which the run harness (`usecase-rsp-run`) evaluates per choice. `--check` fails if the
committed `spans.json` or `coverage.json` would change, and writes no file.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import rsp_translation as T  # noqa: E402
import rsp_vocabulary as V  # noqa: E402

DEFAULT_SOURCE = Path.home() / "code/manage-agents/pilots/anthropic-rsp/source/rsp-3.4.txt"
TEXT_SHA256 = "c7de7fe2f1f44cdd650efb327ecd798f1140034cf6328eb2e494de587c2c3063"
TEXT_BYTES = 59410
FSF_NAMES = ("vocabulary", "translation", "build_document", "measure_r1")


def _safety_framework():
    """safety-framework's `build_document` and `measure_r1`, loaded as that case's test loads them: its siblings stand
    under their bare names only while they import, so that no other use case's module of the same name is shadowed."""
    saved = {name: sys.modules.pop(name) for name in FSF_NAMES if name in sys.modules}
    sys.path.insert(0, str(REPO / "usecases" / "safety-framework"))
    try:
        return {name: importlib.import_module(name) for name in ("build_document", "measure_r1")}
    finally:
        sys.path.pop(0)
        for name in FSF_NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


FSF = _safety_framework()
meta, label, believes, hedged, causal, unformalised, facts, rule, condition, readings, routed = (
    getattr(FSF["build_document"], name) for name in ("meta", "label", "believes", "hedged", "causal",
                                                       "unformalised", "facts", "rule", "condition", "readings",
                                                       "routed"))


def history():
    """A changelog entry for v1.0 to v3.3: history, with no force in v3.4 (narrowing N2)."""
    return {**label("explanation"), "history": True}


def waits(spec, *families):
    """`spec` with the feature families its unit waits for beyond the ones its kind, reason or set implies."""
    return {**spec, "waits": list(families)}


WE = "company"
# Open terms (PLAN 3.2): token -> (decider, what, factors). Names and deciders are tokens; the decider is the text's
# own ("we" is the company, never identified with the RSO, CEO, Board or LTBT: PLAN 8, O10).
OPEN_TERMS = {
    "ot1_crossed": (WE, "the model has crossed threshold Tk (3.3; T4: \"if we determine\")", ["the row's description"]),
    "ot2_more_capable": (WE, "significantly more capable than all models for which we have publicly analyzed risks "
                         "(3.1 off-cycle bullet 1)", ["a prior Risk Report, System Card, or other public artifact"]),
    "ot3a_internal_risk": (WE, "in-scope internal models: risks that significantly exceed those of models covered by "
                           "a prior Risk Report (3.1)", []),
    "ot3b_exceeds_all": (WE, "risks that significantly exceed those of all publicly analyzed models (3.1 off-cycle "
                         "bullet 2)", ["a prior Risk Report, System Card, or other public artifact"]),
    "ot4_significantly_redacted": ("rso_ceo_board_or_ltbt", "significantly redacted (3.6)", []),
    "ot5_highly_capable": (WE, "highly capable (3.6)", ["defined by OT1 for T4"]),
    "ot6_strong_argument": ("unstated", "a strong argument that risk is contained (section 1)",
                            ["the right column's \"This will likely require\" lists"]),
    "ot7_as_needed": (WE, "delay \"as needed\" (Appendix A)", []),
    "ot8_evidence": (WE, "clear or strong evidence about competitors (Appendix A)", []),
    "ot9_significant_lead": (WE, "a significant lead (Appendix A)", []),
    "ot10_material_safety_risk": (WE, "a substantiated report involves a material safety risk (4.4)", []),
    "ot11_noteworthy": ("unstated", "noteworthy changes and deviations (3.2, 3.3)", []),
    "ot12_timing": ("unstated", "\"promptly\", \"regularly\", \"On approximately an annual basis\" (3.4, 4.2, 4.4, "
                    "4.6, "
                    "4.7)", []),
    "ot13_asl3_protections": ("external_reference", "the ASL-3 protections (row T1)",
                              ["classifier guards", "access controls", "red-teaming, bug bounties and threat "
                               "intelligence", "security controls"]),
    "ot14_high_stakes_reliance": ("unstated", "T3's \"highly relied on\", \"extensive access to sensitive assets\", "
                                  "\"moderate capacity for autonomous, goal-directed operation and subterfuge\"", []),
    "ot15_full_substitution": (WE, "T4 (1): fully substitute for our entire set of Research Scientists and Research "
                               "Engineers, at competitive costs", ["within a factor of 5 (quantified)"]),
    "ot16_double_rate": (WE, "T4 (2)(a): double the rate of progress", ["footnote 8", "footnote 9"]),
    "ot17_attributable": (WE, "T4 (2)(b): the doubling plausibly attributable to automation",
                          ["increased headcount, compute, or general productivity"]),
    "ot18_marginal_justification": (WE, "the industry-wide risk is high and the decision rests partly on a marginal "
                                    "risk analysis (3.3)", ["footnote 11"]),
    "ot19_major_role": ("unstated", "marginal risk analysis plays a major role in a decision to move forward (3.4)",
                        []),
    "ot20_corrective_action": ("unstated", "appropriate and proportional corrective action (4.4)", []),
    "ot21_harm_description": ("unstated", "the threshold rows' harm descriptions (rows T1 and T2)",
                              ["footnotes 4 to 7 (examples)"]),
    "ot22_autonomous_research": ("unstated", "large-scale, fully autonomous research (3.1)", []),
    "ot23_soon_develop": (WE, "\"imminently develop\", \"will soon develop\" (Appendix A)", []),
    "ot24_conflicts_of_interest": (WE, "conflicts of interest with respect to Anthropic (3.6.1)",
                                   ["the \"At a minimum\" clauses (N3)"]),
    "ot25_reviewer_criteria": (WE, "the reviewer criteria of 3.6.1 and row T4's \"expert, experienced, credible, "
                               "candid and disinterested\"", ["the examples of 3.6.1"]),
    "ot26_upleveling": (WE, "Appendix A \"General upleveling\": a significant improvement, comparable (or lower) "
                        "effort or cost", []),
    "ot28_continuation": (WE, "(b)'s continuation clause (under RS3c = third)", []),
}

# Reading sets (PLAN 3.1): set id -> (harness set, readings -> the rules or premises of that reading). An entry
# `a or b` is one of two blocks by another set's choice; `case:` names a premise the case states, not a block.
ROWS = {"cond": ["rows-cond"], "uncond": ["rows-uncond"], "ov": []}
ARGUMENT = {"F": [], "Ds_strict": ["f5-strict"], "Ds_default": ["f5-default"]}


def _aim(harness, rule_id):
    return (harness, {"default": [rule_id], "intent": []})


def _force(harness, stem):
    return (harness, {"strict": [f"{stem}-strict"], "default": [f"{stem}-default"]})


def _may(harness, rule_id):
    return (harness, {"P": [rule_id], "M": []})


READINGS = {
    **{f"rs1_t{k}": ("RS1", ROWS) for k in range(1, 5)},
    **{f"rs2_t{k}": ("RS2 and RS2force", ARGUMENT) for k in range(1, 5)},
    "rs12_strive_advance": _aim("RS12advance", "s1-advance-default"),
    "rs8_evidentiary": _force("RS8evidence", "f5-evidence"),
    "rs3o_t4": ("RS3o", {"suff": ["t4-suff"], "iff": ["t4-suff", "t4-only-if"]}),
    "rs3i_t4": ("RS3i", {"suff": ["s2-suff-result or s2-suff-third"],
                         "iff": ["s2-suff-result or s2-suff-third", "s2-only-if-result or s2-only-if-third"]}),
    "rs3c_t4": ("RS3c", {"third": ["s2-suff-third"], "result": ["s2-suff-result"]}),
    "rs12_less_ambitious": _aim("RS12strive", "f6-strive-default"),
    "rs9_cadence": ("RS9", {"window": ["case: each interval at least 3 and at most 6 months (D3)"],
                            "bound": ["case: each interval at most 6 months (D3)"]}),
    "rs11_off_cycle": ("RS11", {"at": ["f9-public", "case: due at the deployment (D3)"], "trigger": ["f9-public"]}),
    "rs12_candid": _aim("RS12candid", "f10-candid-default"),
    "rs8_strong_attempt": _force("RS8attempt", "f10-attempt"),
    "rs13_external_feedback": ("RS13", {"default": ["f12-external-default"], "frequency": []}),
    "rs7_ultimate": ("RS7", {"exec": [], "final": ["f12-final"]}),
    "rs12_minimize_redactions": _aim("RS12minimize", "f13-minimize-default"),
    "rs6_redaction_reasons": _may("RS6redact", "f13-redact-p"),
    "rs12_justify_redactions": _aim("RS12justify", "f13-justify-default"),
    "rs12_public_review": _aim("RS12review", "f14-public-review-default"),
    "rs8_revenue_example": _force("RS8revenue", "f15-revenue"),
    "rs12_review_before_board": _aim("RS12before", "f16-before-board-default"),
    "rs6_split": _may("RS6split", "f16-split-p"),
    "rs6_public_notice": _may("RS6notice", "f20-notice-p"),
    "rs5_all_competitors": ("RS5", {"import": ["f25-meet", "f25-delay", "case: at least one such competitor"],
                                    "noimport": ["f25-meet", "f25-delay"]}),
    "rs4_not_necessarily": ("RS4", {"scope": [], "rel": ["f26-need-not-delay"]}),
}
# The feature family each harness set waits for (PLAN 7): an addressee or existential import is scope (SC), a force
# word's default reading is a default (DF), an aim is an attitude (AT), a cadence or a deadline is time (ET); a set
# whose readings differ in which rules hold is a reading set VE cannot yet decide (readings).
SET_FAMILIES = {"RS1": "readings", "RS2 and RS2force": "SC", "RS3o": "readings", "RS3i": "readings",
                "RS3c": "readings", "RS4": "readings", "RS5": "SC", "RS7": "readings", "RS9": "ET", "RS11": "ET",
                "RS13": "DF", **{f"RS6{s}": "readings" for s in ("redact", "split", "notice")},
                **{f"RS8{s}": "DF" for s in ("evidence", "attempt", "revenue")},
                **{f"RS12{s}": "AT" for s in ("advance", "strive", "candid", "minimize", "justify", "review",
                                               "before")}}
# A situation at which each set's readings differ (the W2 set's distinguishing model): the case's facts as atoms
# over one situation `s`.
DISTINGUISHING = {"RS1": [("crossed", "s", "novel_chem_bio_weapons")], "RS2 and RS2force": [
    ("crossed", "s", "automated_rd")], "RS3o": [("full_substitution_at_competitive_cost", "s")],
    "RS3i": [("double_rate", "s"), ("automation_attributable", "s")], "RS3c": [("double_rate", "s"),
                                                                              ("automation_attributable", "s")],
    "RS4": [("competitor_better_mitigation", "s"), ("clear_evidence", "s")],
    "RS5": [("competitors_strong_measures", "s"), ("clear_evidence", "s"), ("highly_capable", "s")],
    "RS7": [("risk_report_approved", "s")], "RS9": [], "RS11": [("publicly_deployed", "s"),
                                                               ("more_capable_than_analyzed", "s")],
    "RS13": [], "RS6redact": [("redaction_reason_listed", "s")], "RS6split": [("external_review_process", "s")],
    "RS6notice": [("substantiated", "s"), ("material_safety_risk", "s")],
    "RS8evidence": [("crossed", "s", "automated_rd")], "RS8attempt": [], "RS8revenue": [
        ("candidate_revenue_dependent", "s")], "RS12strive": [("goal_revised_less_ambitious", "s")],
    **{f"RS12{s}": [] for s in ("advance", "candid", "minimize", "justify", "review")},
    "RS12before": [("external_review_process", "s")]}

UNITS = [
    # Page 1
    ("Responsible Scaling Policy Version 3.4", "p1-title", meta()),
    ("Effective July 8, 2026", "p1-effective", routed("D3", "v3_4_effective_date")),
    ("For more information, see", "p1-more-info", meta()),
    # Page 2
    ("Contents Contents Introduction", "p2-contents", meta()),
    # Page 3: Introduction
    ("Introduction Our Responsible Scaling Policy", "intro-purpose", label()),
    ("We have always intended", "intro-living", believes("intends")),
    ("We will continually update the RSP", "intro-update", unformalised("no_deadline_or_trigger")),
    ("The major components of this third iteration", "intro-components", label()),
    ("Our recommendations for industry-wide safety outline", "intro-recommendations", label()),
    ("We lay this out in a table that maps", "intro-table", believes()),
    ("We also include our planned mitigations", "intro-planned", label()),
    ("This approach represents a change", "intro-change", label("explanation")),
    ("The overall level of catastrophic risk from AI depends", "intro-collective", believes()),
    ("Our previous RSP committed to", "intro-previous", label("explanation")),
    ("But from a societal perspective", "intro-societal", believes()),
    ("If one AI developer paused development", "intro-pause", causal()),
    ("Although this situation has not yet arisen", "intro-prepare", believes("expects")),
    ("We now separate our plans as a company", "intro-separate", label()),
    ("We aspire to advance the latter", "intro-aspire", unformalised("aim_without_force")),
    ("But we cannot commit to following them", "intro-cannot-commit", label()),
    ("Frontier Safety Roadmaps are a new requirement", "intro-roadmaps", label()),
    ("These will describe our concrete plans", "intro-roadmaps-describe", label()),
    ("Goals described in the Roadmaps are intended", "intro-goals", label()),
    ("These are not hard commitments", "intro-not-hard", label("explanation")),
    ("Risk Reports are another new requirement", "intro-risk-reports", label()),
    ("Risk Reports will provide detailed information", "intro-rr-contents", label()),
    ("They will be published online", "intro-rr-published", label()),
    ("As detailed below, we also aim to subject", "intro-aim-review", unformalised("aim_without_force")),
    ("Finally, our governance commitments", "intro-governance", label()),
    ("Our RSP is only one part", "intro-one-part", label()),
    ("Further, t he RSP may serve", "intro-may-serve", hedged()),
    ("We want to keep it focused", "intro-focused", believes("intends")),
    ("Responsible Scaling Policy, Anthropic 3", "p3-footer", meta()),
    # Page 4: section 1
    ("catastrophic risks we prioritize most", "intro-focused-2", believes("intends")),
    ("1 Where regulatory requirements exceed", "intro-separate-documents", unformalised("external_reference")),
    ("1. Our Recommendations for Industry-Wide Safety", "s1-heading", meta()),
    ("This section outlines our recommendations", "s1-outlines", label()),
    ("We lay this out in a three-column table", "s1-table", label()),
    ("The distinction between our plans", "s1-distinction", label("explanation")),
    ("In particular, we cannot unilaterally", "s1-cannot-commit", label()),
    ("However, these recommendations will drive", "s1-drive", label()),
    ("● We use these recommendations as the north star", "s1-north-star", label()),
    ("We will strive to advance these recommendations", "s1-strive", readings("rs12_strive_advance")),
    ("● We have also adopted a set of competitor-contingent", "s1-competitor", label()),
    ("At this point in AI", "s1-no-detail", label()),
    ("Our recommendations for industry-wide safety are thus structured", "s1-structured", label()),
    ("This leaves ", "s1-flexibility", label()),
    ("But it creates a challenge", "s1-challenge", hedged()),
    ("1 “Catastrophic risk” as used in our RSP", "fn1-catastrophic",
     routed("D2", "existential threats are catastrophic risks (S5)")),
    ("We use this term in its plain meaning", "fn1-plain-meaning", label("definition")),
    ("Where laws such as California SB 53", "fn1-sb53", unformalised("external_reference")),
    ("Responsible Scaling Policy, Anthropic 4", "p4-footer", meta()),
    # Page 5
    ("Ultimately, the best way for these recommendations", "s1-ultimately", believes("expects")),
    ("2 To the extent this takes the form", "s1-harmonize", unformalised("addressed_to_others")),
    ("In the shorter run, independent bodies", "s1-shorter-run", hedged()),
    ("We expect that the recommendations", "s1-expect-evolve", believes("expects")),
    ("We hope these recommendations", "s1-hope", unformalised("hope")),
    ("2 Note that an AI developer might provide", "fn2-single-analysis", hedged()),
    ("Additionally, determinations of which AI developers", "fn2-spare", unformalised("addressed_to_others")),
    ("Responsible Scaling Policy, Anthropic 5", "p5-footer", meta()),
    # Page 6: table row T1
    ("Capability or usage threshold Mitigations", "p6-table-header", meta()),
    ("Non-novel chemical/biological weapons production.", "t1-name", facts("threshold-t1")),
    ("AI systems with the ability to", "t1-description", condition("ot21_harm_description")),
    ("We will maintain or improve on our ASL-3 protections", "t1-plan",
     readings("rs1_t1", "ot1_crossed", "ot13_asl3_protections")),
    ("Speci", "t1-plan-robust", waits(condition(), "readings")),
    ("We expect to continuously meet", "t1-expect", believes("expects")),
    ("A frontier developer should make a strong argument that individual users", "t1-argument",
     readings("rs2_t1", "ot1_crossed", "ot6_strong_argument", "ot21_harm_description")),
    ("This will likely require: ● Restrictions", "t1-likely-require", label("example")),
    ("3 This column summarizes commitments", "fn3-overview", label("explanation")),
    ("Responsible Scaling Policy, Anthropic 6", "p6-footer", meta()),
    # Page 7: rows T2 and T3 (the columns interleave)
    ("Capability or usage threshold Mitigations", "p7-table-header", meta()),
    ("Novel chemical/biological weapons production.", "t2-name", facts("threshold-t2")),
    ("AI systems that can functionally substitute", "t2-description", condition("ot21_harm_description")),
    ("We will apply protections at least as strong", "t2-plan",
     readings("rs1_t2", "ot1_crossed", "ot13_asl3_protections")),
    ("A frontier developer should make a strong argument that threat actors", "t2-argument",
     readings("rs2_t2", "ot1_crossed", "ot6_strong_argument", "ot21_harm_description")),
    ("This will likely require similar measures", "t2-likely-require", label("example")),
    ("This would likely mean security roughly in line with RAND SL4", "t2-rand-sl4",
     unformalised("external_reference")),
    ("Misaligned AI systems in high-stakes settings.", "t3-name", facts("threshold-t3")),
    ("AI systems that are highly relied on", "t3-description", condition("ot14_high_stakes_reliance")),
    ("We will detail the state of our AI systems", "t3-plan", readings("rs1_t3", "ot1_crossed")),
    ("We expect to continually be able to meet", "t3-expect", believes("expects")),
    ("A frontier developer should make a strong argument that AI systems will not carry out sabotage", "t3-argument",
     readings("rs2_t3", "ot1_crossed", "ot6_strong_argument")),
    ("This case may initially be relatively simple", "t3-may-initially", hedged()),
    ("As risk becomes harder to rule out", "t3-likely-include", label("example")),
    ("7 E.g., hundreds.", "fn4-7-examples", label("example")),
    ("4 In particular, weapons with the potential", "fn4-covid", label("definition")),
    ("Responsible Scaling Policy, Anthropic 7", "p7-footer", meta()),
    # Page 8: rows T3 and T4
    ("Capability or usage threshold Mitigations", "p8-table-header", meta()),
    ("either deliberately or inadvertently) carry out sabotage", "t3-description-2",
     condition("ot14_high_stakes_reliance")),
    ("In the near term, this possibility will likely", "t3-near-term", believes("expects")),
    ("Down the line, this possibility may come", "t3-down-the-line", hedged()),
    ("guarantees about an evolving technology", "t3-expect-2", believes("expects")),
    ("of: ● Internal compartmentalization", "t3-likely-include-2", label("example")),
    ("Automated R&D in key domains.", "t4-name", facts("threshold-t4")),
    ("AI systems that can fully automate, or otherwise", "t4-description", label("definition")),
    ("For now, our evaluations will focus", "t4-focus", label("explanation")),
    ("We will: ● Resource and complete", "t4-plan-moonshot", readings("rs1_t4", "ot1_crossed")),
    ("● Achieve an “eyes on everything” state", "t4-plan-eyes", waits(condition(), "readings")),
    ("A frontier developer should make a strong argument that: ● No user", "t4-argument",
     readings("rs2_t4", "ot1_crossed", "ot6_strong_argument")),
    ("This will likely require similar measures to those listed in row 1", "t4-likely-require", label("example")),
    ("Accomplishing this would likely mean security roughly in line with RAND SL4", "t4-rand-sl4",
     unformalised("external_reference")),
    ("Security requirements would be calibrated", "t4-calibrated", label("explanation")),
    ("Actors subject to such a regime would not need", "t4-actors", label("explanation")),
    ("Responsible Scaling Policy, Anthropic 8", "p8-footer", meta()),
    # Page 9
    ("Capability or usage threshold Mitigations", "p9-table-header", meta()),
    ("tractable to assess than capabilities", "t4-focus-2", label("explanation")),
    ("Additionally, AI R&D alone could cause", "t4-could-accelerate", causal()),
    ("We will consider this threshold to be met if we determine", "t4-definition",
     readings("rs3o_t4", "ot15_full_substitution")),
    ("at competitive costs (i.e., within a factor of 5)", "t4-cost-factor",
     waits(condition("ot15_full_substitution"), "QT")),
    ("; or (2) there is", "t4-scenario-2", condition("ot17_attributable")),
    ("We would consider scenario (2) to have occurred where", "t4-scenario-2-definition",
     readings("rs3i_t4", "ot16_double_rate", "ot17_attributable")),
    ("for all critical AI-development activities", "t4-plan-eyes-2", waits(condition(), "readings")),
    ("● Perform systematic alignment assessments", "t4-plan-alignment", waits(condition(), "readings")),
    ("● Develop our internal red-teaming", "t4-plan-red-teaming", waits(condition(), "readings")),
    ("to be treated as threats to each other", "t4-actors-2", label("explanation")),
    ("● Even malicious employees and other insiders", "t4-argument-insiders", condition("ot6_strong_argument")),
    ("This requires (among other things) accounting", "t4-insiders-requires", label("explanation")),
    ("This will likely require an internal Usage Policy", "t4-insiders-likely", label("example")),
    ("● AI models have not been deliberately", "t4-argument-goals", condition("ot6_strong_argument")),
    ("This will likely require similar measures to those listed above", "t4-goals-likely", label("example")),
    ("In particular, at this point AI systems might be responsible", "t4-evidentiary",
     readings("rs8_evidentiary", "ot1_crossed")),
    ("9 Over at least three model generations.", "fn9-generations", label("definition")),
    ("8 “Double the rate of progress” means", "fn8-double-rate", label("definition")),
    ("For example, if baseline progress involved", "fn8-example", label("example")),
    ("This is not the same idea as", "fn8-not-productivity", label("explanation")),
    ("Responsible Scaling Policy, Anthropic 9", "p9-footer", meta()),
    # Page 10
    ("Capability or usage threshold Mitigations", "p10-table-header", meta()),
    ("factors, such as increased headcount", "t4-scenario-2-factors", label("example")),
    ("), such that continuation of the trend", "t4-continuation", readings("rs3c_t4", "ot28_continuation")),
    ("This capability threshold is intended", "t4-highly-capable", label("definition")),
    ("It may be sensible to add earlier", "t4-may-add", hedged()),
    ("● Publish Risk Reports with the status of", "t4-plan-publish", condition("ot25_reviewer_criteria")),
    ("We broadly expect to lead the industry", "t4-expect", believes("expects")),
    ("Responsible Scaling Policy, Anthropic 10", "p10-footer", meta()),
    # Page 11: section 2, section 3, 3.1
    ("2. Frontier Safety Roadmap We will maintain", "s2-maintain", rule("f6-maintain")),
    ("Maintaining and reporting on this Roadmap", "s2-part-of-work", label()),
    ("It will be shared with all full-time employees", "s2-share", rule("f6-share")),
    ("We will provide updates on whether we achieve the goals", "s2-updates", rule("f6-updates")),
    ("Our Frontier Safety Roadmap is subject to change.", "s2-subject-to-change", label()),
    ("Some changes may simply", "s2-may-reflect", hedged()),
    ("However, we will strive to avoid situations", "s2-strive", readings("rs12_less_ambitious")),
    ("By establishing this expectation, we hope", "s2-hope", unformalised("hope")),
    ("Publishing our Frontier Safety Roadmap may also help", "s2-may-help", hedged()),
    ("Our current Frontier Safety Roadmap is available at", "s2-available", unformalised("external_reference")),
    ("We will also keep past Roadmaps available", "s2-keep-past", rule("f6-keep-past")),
    ("3. Risk Reports We will publish Risk Reports", "s3-publish", rule("f7-publish")),
    ("These have signi", "s3-system-cards", label()),
    ("3.1. Scope and Timing", "s31-heading", meta()),
    ("Scope. A Risk Report will cover the risks", "s31-coverage-date",
     routed("D3", "coverage date no more than 30 days before publication (D3a, D3b)")),
    ("10 It will cover all publicly deployed models", "s31-public", rule("f8-public")),
    (", as well as any internally deployed models", "s31-internal", rule("f8-internal", "ot3a_internal_risk")),
    ("While there are a variety of reasons", "s31-at-minimum", rule("f8-autonomous", "ot22_autonomous_research")),
    ("Models ﬁtting the above description", "s31-in-scope-name", label("definition")),
    ("We may also voluntarily include", "s31-voluntary", hedged()),
    ("Timing. We will publish a Risk Report every 3-6 months.", "s31-timing", waits(readings("rs9_cadence"), "QT")),
    ("Note that unlike system cards", "s31-not-each-release", label("explanation")),
    ("Off-cycle updates.", "s31-off-cycle", label()),
    ("● When we publicly deploy a model that we determine", "s31-off-cycle-public",
     readings("rs11_off_cycle", "ot2_more_capable")),
    ("10 A Risk Report may include information", "fn10-more-recent", hedged()),
    ("Responsible Scaling Policy, Anthropic 11", "p11-footer", meta()),
    # Page 12: 3.1 (end), 3.2, 3.3
    ("● Within 30 days of determining", "s31-off-cycle-internal", waits(rule("f9-internal", "ot3b_exceeds_all"), "ET")),
    ("3.2. General Expectations for Risk Reports", "s32-heading", meta()),
    ("Several principles guide", "s32-principles", label()),
    ("● We intend for our Risk Reports", "s32-intend", readings("rs12_candid")),
    ("● In particular, we will acknowledge", "s32-acknowledge", unformalised("degree_term")),
    ("● We will put signi", "s32-effort", unformalised("degree_term")),
    ("● When a Risk Report describes risk mitigations", "s32-in-line", rule("f10-in-line", "ot11_noteworthy")),
    ("We should make a strong attempt", "s32-strong-attempt", readings("rs8_strong_attempt")),
    ("3.3. Contents", "s33-heading", meta()),
    ("Factual information. We will describe", "s33-factual", rule("f11-factual")),
    ("1. Threat model identi", "s33-factual-items-1", label("definition")),
    ("3. Evidence (including evaluations)", "s33-evidence", unformalised("as_appropriate")),
    ("4. Risk mitigations:", "s33-factual-items-4", label("definition")),
    ("Risk analyses. We will provide our reasoning", "s33-risk-analyses", rule("f11-analyses")),
    ("Our analyses will include:", "s33-analysis-items", label("definition")),
    ("Responsible Scaling Policy, Anthropic 12", "p12-footer", meta()),
    # Page 13: 3.3 (end), 3.4
    ("4. Looking forward:", "s33-looking-forward", label("definition")),
    ("Review of past Risk Reports and decisions.", "s33-review", rule("f11-review")),
    ("1. Changes in risk mitigation practices", "s33-review-items", label("definition")),
    ("3. Changes to our Frontier Safety Roadmap", "s33-goals-missed", rule("f11-goal-missed")),
    ("Marginal risk and ecosystem analysis.", "s33-marginal", rule("f11-marginal", "ot18_marginal_justification")),
    ("1. Competitive landscape analysis", "s33-marginal-items", label("definition")),
    ("We will conduct the assessments above with respect to each in-scope model.", "s33-each-model",
     rule("f11-assess")),
    ("To avoid redundancy, we will likely", "s33-groupings", believes("expects")),
    ("3.4. Procedures", "s34-step1", unformalised("process_description")),
    ("2. Review and feedback:", "s34-step2", rule("f12-internal-feedback")),
    ("We may also use this feedback", "s34-may-refine", hedged()),
    ("We will usually also seek feedback", "s34-usually", readings("rs13_external_feedback")),
    ("3. Executive approval:", "s34-step3", rule("f12-approval")),
    ("The CEO and RSO will make the ultimate determination", "s34-ultimate", readings("rs7_ultimate")),
    ("4. Governance noti", "s34-step4", waits(rule("f12-share", "ot12_timing"), "ET")),
    ("11 By “ marginal risk analysis", "fn11-marginal", label("definition")),
    ("Responsible Scaling Policy, Anthropic 13", "p13-footer", meta()),
    # Page 14: 3.4 step 5, 3.5, 3.6
    ("5. Modi", "s34-step5", rule("f12-board-approval", "ot19_major_role")),
    ("3.5. Publication and Redactions", "s35-publish", rule("f7-publish")),
    ("We will aim to minimize redactions", "s35-aim", readings("rs12_minimize_redactions")),
    ("Reasons we may redact material", "s35-reasons", readings("rs6_redaction_reasons")),
    ("We will disclose the existence of each redaction", "s35-disclose", rule("f13-disclose")),
    ("and aim to give a brief justi", "s35-aim-justify", readings("rs12_justify_redactions")),
    ("3.6. External Review We will work toward", "s36-work-toward", readings("rs12_public_review")),
    ("This means working with one or more", "s36-means", label("definition")),
    ("Commentary will address topics", "s36-commentary", label()),
    ("Our intent is for external reviewers", "s36-intent", believes("intends")),
    ("But there are no well-established", "s36-experiment", label("explanation")),
    ("At a minimum, we will complete a full external review", "s36-full-review",
     rule("f14-full-review", "ot5_highly_capable", "ot4_significantly_redacted")),
    ("● A model is “ highly capable” if we conclude", "s36-highly-capable", facts("highly-capable-t4")),
    ("● “Signi", "s36-significantly-redacted", condition("ot4_significantly_redacted")),
    ("Note that unredacted reports will be shared", "s36-employees", label("explanation")),
    ("In addition, upon the LTBT", "s36-ltbt-request", rule("f14-ltbt-request")),
    ("Responsible Scaling Policy, Anthropic 14", "p14-footer", meta()),
    # Page 15: 3.6.1 to 3.6.3
    ("3.6.1. Selecting external reviewers", "s361-select", condition("ot25_reviewer_criteria")),
    ("It’s particularly important", "s361-important", label("explanation")),
    ("● Have reputational and other incentives", "s361-candid", condition("ot25_reviewer_criteria")),
    ("For example, external review parties should not", "s361-should-not", readings("rs8_revenue_example")),
    ("● Do not have con", "s361-conflicts", condition("ot24_conflicts_of_interest")),
    ("At a minimum, a reviewing organization itself may not", "s361-financial-interest",
     rule("f15-financial-interest")),
    ("In selecting external reviewers, we will consult", "s361-consult", rule("f15-select-approval")),
    ("3.6.2. Timing and access", "s362-one-week", rule("f16-share-one-week")),
    ("We will ask the external reviewers to provide public commentary", "s362-ask-30-days", rule("f16-ask-commentary")),
    ("We will try to work toward a process", "s362-try", readings("rs12_review_before_board")),
    ("All sections of the Risk Report will be shared", "s362-all-sections", rule("f16-all-sections")),
    (", but we may choose to split", "s362-may-split", readings("rs6_split")),
    ("For purposes of external review, the only redactions", "s362-only-legal", rule("f16-only-legal")),
    ("12 We expect that we will also invest", "s362-expect", believes("expects")),
    ("3.6.3. Contents of external review", "s363-contents", label("definition")),
    ("The external reviewer will also evaluate", "s363-redactions", label("definition")),
    ("12 For example, we may redact information", "fn12-example", label("example")),
    ("Responsible Scaling Policy, Anthropic 15", "p15-footer", meta()),
    # Page 16: 3.6.3 (end), section 4
    ("2. Redaction justi", "s363-redaction-items", label("definition")),
    ("Public comments. We will ask the external reviewer", "s363-public-comments", rule("f16-ask-commentary")),
    ("External reviewers will be bound by obligations", "s363-bound", label()),
    ("4. Governance We commit to the following", "s4-commit", label()),
    ("1. Responsible Scaling O", "s4-rso", rule("f18-rso")),
    ("The RSO’s duties will include", "s4-rso-duties", label("definition")),
    ("2. Long Term Bene", "s4-ltbt-brief", rule("f19-brief-ltbt", "ot12_timing")),
    ("3. Internal transparency:", "s4-unredacted-200", rule("f19-unredacted")),
    ("We will share minimally-redacted Risk Reports", "s4-minimally-redacted", rule("f19-minimally-redacted")),
    ("4. Noncompliance reporting:", "s4-noncompliance-process", rule("f20-process")),
    ("Staff will have more than one option", "s4-recipients", rule("f20-recipients")),
    ("When we receive a report, we will promptly investigate", "s4-investigate",
     rule("f20-investigate", "ot12_timing", "ot20_corrective_action")),
    ("We will provide quarterly updates to the Board", "s4-quarterly", rule("f20-quarterly")),
    ("If we determine that a report is (1) substantiated", "s4-notify-board",
     rule("f20-notify-board", "ot10_material_safety_risk", "ot12_timing")),
    (" and we may provide public notice", "s4-may-public-notice", readings("rs6_public_notice")),
    ("Finally, we will protect reporters from retaliation", "s4-retaliation", rule("f20-retaliation")),
    (", and where a report concerns the conduct of the RSO", "s4-rso-report", rule("f20-board-recipient")),
    ("5. Employee agreements:", "s4-non-disparagement", rule("f21-no-impeding")),
    ("If we offer agreements with a non-disparagement clause", "s4-clause", rule("f21-clause")),
    ("6. Internal review:", "s4-internal-review", rule("f22-internal-review", "ot12_timing")),
    ("7. Procedural compliance review:", "s4-compliance-review", rule("f22-third-party-review", "ot12_timing")),
    ("This review will focus on procedural compliance", "s4-compliance-focus", label("definition")),
    ("8. Policy changes:", "s4-changes", rule("f23-approval")),
    ("If we update the RSP, we will publicly share", "s4-publish-update", rule("f23-publish")),
    ("Responsible Scaling Policy, Anthropic 16", "p16-footer", meta()),
    # Page 17: 4.8 (end), Appendix A, Appendix B
    ("its effective date and will record the differences", "s4-publish-update-2", waits(condition(), "ET")),
    ("We will maintain the current version of the RSP", "s4-website", rule("f23-website")),
    ("Appendices Appendix A: Commitments Related to Competitors", "appa-heading", meta()),
    ("These commitments are necessarily high-level", "appa-limited", label()),
    ("In many cases, we will not have enough information", "appa-best-judgment", label("explanation")),
    ("But to the extent that other relevant AI developers", "appa-may-help", hedged()),
    ("Further, the commitments below do not preclude", "appa-not-preclude", label()),
    ("Mitigating the risks from our models is a top priority", "appa-priority", believes("intends")),
    ("Scenario Commitment Anthropic in the lead.", "appa-lead-scenario",
     condition("ot5_highly_capable", "ot23_soon_develop", "ot8_evidence")),
    ("We will require a strong argument that catastrophic risk is contained", "appa-lead-argument",
     rule("f24-argument", "ot5_highly_capable", "ot8_evidence", "ot6_strong_argument")),
    ("We will delay AI development and deployment as needed to achieve this, until", "appa-lead-delay",
     rule("f24-delay", "ot7_as_needed", "ot9_significant_lead")),
    ("Competitors have strong safety measures.", "appa-strong-scenario",
     readings("rs5_all_competitors", "ot8_evidence", "ot6_strong_argument", "ot23_soon_develop")),
    ("For our highly capable frontier models, we will meet or exceed", "appa-strong-meet",
     rule("f25-meet", "ot5_highly_capable", "ot8_evidence")),
    ("Until we are able to do so, we will delay", "appa-strong-delay", rule("f25-delay", "ot7_as_needed")),
    ("General upleveling.", "appa-uplevel-scenario", condition("ot8_evidence", "ot26_upleveling")),
    ("We will make a signi", "appa-uplevel-effort", rule("f26-effort", "ot8_evidence", "ot26_upleveling")),
    ("However, we will not necessarily delay", "appa-uplevel-not-delay", readings("rs4_not_necessarily")),
    ("Appendix B: Notes on ASLs", "appb-earlier", label("explanation")),
    ("We still use this concept", "appb-still", label()),
    ("13 This and other italicized instances", "fn13-highly-capable", label("definition")),
    ("Responsible Scaling Policy, Anthropic 17", "p17-footer", meta()),
    # Page 18: Appendix B (end), Changelog (history under N2; the dates are routed to D3)
    ("existing AI models. (For example", "appb-still-2", label()),
    ("However, when de", "appb-prefer", unformalised("preference")),
    ("Changelog September 19, 2023 (RSP v1.0)", "cl-v1-0-date", routed("D3", "v1.0 date (D1)")),
    ("RSP-2023 (aka RSP v1.0)", "cl-v1-0", history()),
    ("October 15, 2024 (RSP v2.0)", "cl-v2-0-date", routed("D3", "v2.0 date (D1)")),
    ("RSP-2024: This update introduces", "cl-v2-0", history()),
    ("Responsible Scaling Policy, Anthropic 18", "p18-footer", meta()),
    # Page 19
    ("to (a) match expected efforts", "cl-v2-0-2", history()),
    ("March 31, 2025 (RSP v2.1)", "cl-v2-1-date", routed("D3", "v2.1 date (D1)")),
    ("RSP-2025 : This update clari", "cl-v2-1", history()),
    ("Responsible Scaling Policy, Anthropic 19", "p19-footer", meta()),
    # Page 20
    ("May 14, 2025 (RSP v2.2)", "cl-v2-2-date", routed("D3", "v2.2 date (D1)")),
    ("ASL-3 Security : This update excludes", "cl-v2-2", history()),
    ("February 24, 2026 (RSP v3.0)", "cl-v3-0-date", routed("D3", "v3.0 date (D1)")),
    ("This update is a comprehensive rewrite", "cl-v3-0", history()),
    ("For a summary of changes and the thinking behind them, see here", "cl-v3-0-see-here",
     unformalised("external_reference")),
    ("April 2, 2026 (RSP v3.1)", "cl-v3-1-date", routed("D3", "v3.1 date (D1)")),
    ("This revision addresses the following points", "cl-v3-1", history()),
    ("April 29, 2026 (RSP v3.2)", "cl-v3-2-date", routed("D3", "v3.2 date (D1)")),
    ("This update authorizes the LTBT", "cl-v3-2", history()),
    ("May 26, 2026 (RSP v3.3)", "cl-v3-3-date", routed("D3", "v3.3 date (D1)")),
    ("This update (1) revises our threshold", "cl-v3-3", history()),
    ("July 8, 2026 (RSP v3.4)", "cl-v3-4-date", routed("D3", "v3.4 date (D1, D2)")),
    ("This update makes ﬁve changes:", "cl-v3-4", label("explanation")),
    ("Responsible Scaling Policy, Anthropic 20", "p20-footer", meta()),
    # Page 21
    ("2. It now requires that fully unredacted", "cl-v3-4-2", label("explanation")),
    ("Responsible Scaling Policy, Anthropic 21", "p21-footer", meta()),
]


def spans(source):
    starts, cursor = [], 0
    for anchor, uid, _ in UNITS:
        at = source.find(anchor.encode(), cursor)
        if at < 0:
            raise SystemExit(f"anchor not found after byte {cursor}: {uid} {anchor!r}")
        starts.append(0 if not starts else at)
        cursor = at + 1
    return list(zip(starts, starts[1:] + [len(source)]))


def situation_model(harness_set):
    """The distinguishing situation of a set as a complete model over the D1 vocabulary (regulated tables empty)."""
    from ve.model import FiniteModel
    env = T.environment()
    relations = {p: [] for p in env.predicates}
    for name, *args in DISTINGUISHING[harness_set]:
        relations[name].append(list(args))
    return FiniteModel.from_dict(env, {"complete": True, "domains": {"situation": ["s"], "threshold": list(
        V.THRESHOLDS)}, "constants": {c: c for c in V.THRESHOLDS}, "relations": relations})


def open_term_declarations(names=None):
    return [{"name": name, "arguments": [], "decided_by": decider, "necessary": [], "sufficient": [],
             "factors": [what] + factors, "precedents": [], "jurisdiction": "rsp_v3_4", "version": 1}
            for name, (decider, what, factors) in OPEN_TERMS.items() if names is None or name in names]


def environment():
    """The D1 environment: the vocabulary's profiles (`norms@0`, `relational-fol@0`, `soft-norms@0`)."""
    return V.environment()


def unit_of(uid, spec, span, fact_blocks, used_rules, record):
    """The `ve-document@1` unit of one specification, and its record in spans.json (filled in place)."""
    from ve import ast as A
    from ve.ast import formula_to_data
    unit = {"id": uid, "span": list(span), "kind": spec["kind"], "meaning": spec["meaning"], "support": spec["support"]}
    if "facts" in spec:
        formulas = [f for block in spec["facts"] for f in fact_blocks[block]]
        conjunction = formulas[0]
        for f in formulas[1:]:
            conjunction = A.And(conjunction, f)
        unit["content"] = {"ast": formula_to_data(T.environment(), conjunction)}
        record["premises"] = spec["facts"]
    if "rule" in spec:
        if spec["rule"] in used_rules:
            record["restates"] = spec["rule"]
        else:
            used_rules.add(spec["rule"])
            unit["content"] = {"norm": json.loads(T.parsed_rule(spec["rule"]))}
            record["rule"] = spec["rule"]
    return unit


def build(source):
    fact_blocks = {block.id: formulas for block, formulas in T.facts()}
    used_rules, units, reading_sets, records = set(), [], [], []
    for (_, uid, spec), span in zip(UNITS, spans(source)):
        record = {"id": uid, "span": list(span), "kind": spec["kind"] if type(spec["kind"]) is str else spec["kind"][0]}
        units.append(unit_of(uid, spec, span, fact_blocks, used_rules, record))
        if "reading_set" in spec:
            set_id = spec["reading_set"]
            harness_set, choices = READINGS[set_id]
            model = situation_model(harness_set)
            reading_sets.append({
                "id": set_id, "unit": uid, "version": 1, "status": "open",
                "readings": [{"id": choice, "kind": "norm", "meaning_id": "pending", "content": None,
                              "admission": {"who": "translator", "why": f"{harness_set} = {choice}: "
                                                                        + ("; ".join(rules) or "no rule"),
                                            "distinguishing_models": {other: model.model_id for other in choices
                                                                      if other != choice}}}
                             for choice, rules in choices.items()],
                "models": {model.model_id: model.to_dict()}})
            record["reading_set"] = set_id
        if "routed" in spec:
            record["routed"] = {"document": spec["routed"], "carries": spec["why"]}
        if type(spec["meaning"]) is dict and "unformalised" in spec["meaning"]:
            record["reason"] = spec["meaning"]["unformalised"]
        if type(spec["meaning"]) is dict and "open" in spec["meaning"]:
            record["open_terms"] = spec["meaning"]["open"]
        for key in ("history", "waits"):
            if key in spec:
                record[key] = spec[key]
        records.append(record)
    meta_block = {"format": "ve-document@1", "environment": environment(), "units": units,
                  "open_terms": open_term_declarations(), "reading_sets": reading_sets}
    document = b"---\n" + json.dumps(meta_block, indent=1, ensure_ascii=False).encode() + b"\n---\n" + source
    return document, records


def master(records, statuses, routed_ok):
    """Every byte with its final status: a unit routed to D2 or D3 takes CHECKED when that document is checked."""
    totals = {}
    for record in records:
        status = statuses[record["id"]]
        if "routed" in record and routed_ok[record["routed"]["document"]]:
            status = "CHECKED"
        record["status"] = status
        totals[status] = totals.get(status, 0) + record["span"][1] - record["span"][0]
    return totals


def check_source(source):
    if hashlib.sha256(source).hexdigest() != TEXT_SHA256 or len(source) != TEXT_BYTES:
        raise SystemExit("the source is not the pinned RSP v3.4 text")


def main(argv=None):
    import stage0
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    source = args.source.read_bytes()
    check_source(source)
    document, records = build(source)
    with tempfile.TemporaryDirectory() as scratch:
        # --check writes nothing beside the source, which may be a read-only copy.
        path = Path(scratch) / "rsp.d1.ve.md" if args.check else args.source.parent / "rsp.d1.ve.md"
        report, statuses = FSF["build_document"].measure(document, path)
    totals = master(records, statuses, stage0.routed_checked())
    spans_text = json.dumps({"source_sha256": TEXT_SHA256, "source_bytes": TEXT_BYTES, "units": records},
                            indent=1, ensure_ascii=False) + "\n"
    coverage_text = json.dumps({"document": "rsp.d1.ve.md (built locally, not committed)",
                                "document_sha256": hashlib.sha256(document).hexdigest(),
                                **report, "master_bytes_by_status": totals}, indent=1, sort_keys=True) + "\n"
    if args.check:
        if (HERE / "spans.json").read_text() != spans_text or (HERE / "coverage.json").read_text() != coverage_text:
            raise SystemExit("spans.json or coverage.json is out of date")
        return 0
    (HERE / "spans.json").write_text(spans_text)
    (HERE / "coverage.json").write_text(coverage_text)
    print(json.dumps({"d1": report.get("bytes_by_status"), "master": totals}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
