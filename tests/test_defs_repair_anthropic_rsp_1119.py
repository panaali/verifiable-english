"""defs-repair-anthropic-rsp-1119: each KEPT row of the RSP definitions audit carries its source definition verbatim.

The audit (manage-agents reviews/defs-carried-1119, rows-anthropic-rsp-x.tsv, read at VE e53db4e8fc) lists, per row, a
term a rule depends on, the source passage that defines it and the carrier the rule is shown: the legend of a predicate
the rule's block uses (rsp_vocabulary.py, shown as its environment.d1.json description), the legend of D2's harm
constant (stage0.HARMS) or D3's coverage-date legend (stage0.COVERAGE_WORDS on a "publication within" question's start
day). Each sentence below is stored with its location in the pinned text (usecases/pinned_sources.json, rsp-3.4.txt;
runs the PDF extract interrupts are stored as their runs). The checks compare after the project's quote normalisation
(tools/fidmech/segment.py `norm`: whitespace, quote styles, dashes, ligatures); when the pinned text is stored at its
pin, each run is also checked in it (never downloaded).
"""
from __future__ import annotations

import json
import re

import pytest

import test_rsp_fidelity_fix as fix
import test_safetyfw_usecases as base
from tests.pinned_source import pinned_source
from tools.fidmech.segment import norm

RSP = base.RSP
V, S0 = base.rsp_vocabulary, base.rsp_stage0

SENTENCES = {
    "FN1": ("rsp-3.4.txt:4 footnote 1", (
        "1 “Catastrophic risk” as used in our RSP refers generally to risks of the most severe potential harms from "
        "advanced AI, such as existential threats or fundamental destabilization of global systems. We use this term "
        "in its plain meaning rather than adopting any specific statutory definition. Where laws such as California "
        "SB 53 define this or similar terms with specific thresholds, we address those requirements in separate "
        "compliance frameworks.",
    )),
    "RIGHT_COLUMN": ("rsp-3.4.txt:4 section 1, the table's right column", (
        "The right column describes our recommendations for industry-wide safety at each threshold.",
    )),
    "LEFT_COLUMN": ("rsp-3.4.txt:4 section 1, the table's left column", (
        "The left column identifies capability thresholds that would call for heightened mitigations.",
    )),
    "MIDDLE_COLUMN": ("rsp-3.4.txt:4 section 1, the table's middle column", (
        "The middle column provides an overview of our planned mitigations, which we have set forth more fully in "
        "our Frontier Safety Roadmap and other sections of this policy.",
    )),
    "FN3": ("rsp-3.4.txt:6 footnote 3", (
        "3 This column summarizes commitments drawn from other sections of this policy and associated artifacts. It "
        "should be read as an overview, not as indicating any separate or additional plans.",
    )),
    "T1": ("rsp-3.4.txt:6 table row T1, left column", (
        "Non-novel chemical/biological weapons production. AI systems with the ability to significantly help "
        "individuals or groups with basic technical backgrounds (e.g., undergraduate STEM degrees) create/obtain and "
        "deploy chemical and/or biological weapons with serious potential for catastrophic damages.",
    )),
    "T2": ("rsp-3.4.txt:7 table row T2, left column (footnote marks 4-7)", (
        "Novel chemical/biological weapons production. AI systems that can functionally substitute for the scarce "
        "human expertise that is currently the primary barrier to novel development of chemical and biological "
        "weapons with potential for catastrophic harm. 4 That is, a well-resourced team 5 could, using the model, "
        "accomplish the end-to-end agent design and deployment (including, as relevant, agent design, verification "
        "and validation, formulation, and dissemination) that would otherwise 6 require recruiting one of a small "
        "number 7 of world-leading specialists.",
    )),
    "T2_FOOTNOTES": ("rsp-3.4.txt:7 footnotes 7, 6, 5, 4", (
        "7 E.g., hundreds. 6 E.g., in a world with access only to the best AI models as of 2023. 5 For example, a "
        "program with millions of dollars available and support from recent PhD’s from top-tier international "
        "programs. We are focused on the sorts of teams that would be realistic for real-world threat actors. 4 In "
        "particular, weapons with the potential to cause events with consequences comparable to or worse than those "
        "of COVID-19.",
    )),
    "T3": ("rsp-3.4.txt:7-8 table row T3, left column (two runs: the extract interleaves the columns)", (
        "Misaligned AI systems in high-stakes settings. AI systems that are highly relied on and have extensive "
        "access to sensitive assets as well as moderate capacity for autonomous, goal-directed operation and "
        "subterfuge—such that it is plausible these AI systems could (if directed toward this goal,",
        "either deliberately or inadvertently) carry out sabotage leading to irreversibly and substantially higher "
        "odds of a later global catastrophe. In the near term, this possibility will likely be most applicable to AI "
        "systems that are extensively used within major AI companies, with the opportunity to manipulate how their "
        "successor systems are trained and deployed as well as the evidence used to assess their safety. Down the "
        "line, this possibility may come to apply to AI systems deployed within government and other high-stakes "
        "settings.",
    )),
    "T4": ("rsp-3.4.txt:8 table row T4, left column", (
        "Automated R&D in key domains. AI systems that can fully automate, or otherwise dramatically accelerate, the "
        "work of large, top-tier teams of human researchers in domains where fast progress could cause threats to "
        "international security and/or rapid disruptions to the global balance of power—for example, energy, "
        "robotics, weapons development, and AI itself.",
    )),
    "SCENARIO_2": ("rsp-3.4.txt:9-10 table row T4, scenario (2) (two runs)", (
        "We would consider scenario (2) to have occurred where (a) we observe or expect double the rate of progress "
        "8 in AI aggregate capabilities compared to both the rate we’d expect and the fastest rate of extended "
        "progress 9 we’ve observed in the absence of significant AI contributions to AI R&D and (b) it is plausible "
        "that this doubling is substantially attributable to the automation of research and/or engineering (as "
        "opposed to other",
        "factors, such as increased headcount, compute, or general productivity), such that continuation of the "
        "trend in AI progress seems likely to lead to even greater acceleration.",
    )),
    "FN8": ("rsp-3.4.txt:9 footnote 8", (
        "8 “Double the rate of progress” means “as much progress in one year as one would see in two years at "
        "baseline.” For example, if baseline progress involved a 3× scaleup in compute and a 3× improvement in "
        "algorithmic efficiency (for a 9× “effective scaleup”), “double the rate of progress” would entail something "
        "like an 81× effective scaleup. This is not the same idea as “doubling researchers’ productivity,” since "
        "doubling inputs does not necessarily double the rate of progress.",
    )),
    "FN9": ("rsp-3.4.txt:9 footnote 9", (
        "9 Over at least three model generations.",
    )),
    "HIGHLY_CAPABLE": ("rsp-3.4.txt:14 section 3.6", (
        "A model is “ highly capable” if we conclude that it crosses the threshold for automated AI R&D described in "
        "Section 1 .",
    )),
    "SIGNIFICANTLY_REDACTED": ("rsp-3.4.txt:14 section 3.6", (
        "“Significantly redacted” means that the redactions omit information a reasonable external safety researcher "
        "would consider important in evaluating the overall level of risk, such that a reader of only the public "
        "version could not meaningfully assess whether they agree with our conclusions. A report shall be deemed "
        "significantly redacted if, in the judgment of the RSO, CEO, Board, or LTBT, it meets this description.",
    )),
    "SCOPE": ("rsp-3.4.txt:11 section 3.1 Scope", (
        "Scope. A Risk Report will cover the risks of Anthropic's models and actions as of a given coverage date, "
        "which will be no more than 30 days prior to the publication of the report. 10",
    )),
    "FACTUAL": ("rsp-3.4.txt:12 section 3.3", (
        "A Risk Report will document the following: 1. Threat model identification: Our criteria for determining "
        "which catastrophic risks (i.e., threat models) we assess. 2. Threat model specification: The relevant "
        "threat models (which will, at a minimum, include those discussed above ). 3. Evidence (including "
        "evaluations) about relevant model capabilities and behaviors: For each in-scope model, capability and "
        "alignment evaluations (conducted internally and by external parties as appropriate), their results, and (as "
        "appropriate) other evidence we considered in assessing the level of risk. 4. Risk mitigations: For each "
        "in-scope model, the mitigations we have implemented as of the coverage date across security, deployment "
        "safeguards, and alignment domains, along with discussion of their effectiveness. 5. Additional relevant "
        "factors: Any other considerations material to our risk analysis.",
    )),
    "ANALYSES": ("rsp-3.4.txt:12 section 3.3", (
        "Our analyses will include: 1. Threat-specific risk assessment: For each threat model, we will analyze "
        "remaining absolute risk–i.e., the leftover risk after accounting for our mitigations. We will also discuss "
        "whether we believe we’ve crossed relevant thresholds in our recommendations for industry-wide safety (see "
        "Section 1 ), and (as relevant) whether we believe we’re meeting the risk mitigation standards corresponding "
        "to them. 2. Overall risk assessment: We will provide an overall risk assessment. 3. Risk-benefit "
        "determination: We will explain whether, and if so why, we believe the identified risks are justified by "
        "corresponding benefits.",
    )),
    "REVIEW": ("rsp-3.4.txt:13 section 3.3", (
        "Review of past Risk Reports and decisions. We will address: 1. Changes in risk mitigation practices "
        "—noteworthy cases in which our risk mitigation practices deviated (including temporarily) or changed from "
        "what we discussed in our previous Risk Report over the relevant period, and their implications for the "
        "overall level of risk. 2. Decisions to internally deploy in-scope models that would not otherwise be "
        "reviewed in a Risk Report (because they happened in between Risk Reports). We will discuss how these "
        "decisions were made and whether they appear reasonable in light of any noteworthy new information that has "
        "come to light since then. 3. Changes to our Frontier Safety Roadmap and any cases where we failed to meet "
        "our goals.",
    )),
    "MARGINAL": ("rsp-3.4.txt:13 section 3.3", (
        "we will additionally address the following: 1. Competitive landscape analysis: What we know about how our "
        "current and future model capabilities and risk mitigations compare to those of relevant competitors. 2. "
        "Role in risk assessment: How these comparisons factored into our risk assessment. 3. Benefits analysis: The "
        "benefits, if any, of continuing to maintain our existing models or of advancing frontier capabilities, "
        "including considerations related to our mission and our ability to contribute to AI safety research and "
        "policy development. 4. Advocacy efforts: The steps we took to raise public awareness of the relevant risks "
        "and to encourage appropriate regulatory action, including our engagement with policymakers and other AI "
        "developers.",
    )),
    "FN11": ("rsp-3.4.txt:13 footnote 11", (
        "11 By “ marginal risk analysis ,” we mean arguing that the risks imposed by our systems in particular are "
        "relatively lower when keeping in mind the risks unavoidably posed by other AI systems.",
    )),
    "REDACTION_REASONS": ("rsp-3.4.txt:14 section 3.5", (
        "Reasons we may redact material include but are not limited to: 1. Legal compliance: To comply with legal "
        "obligations on disclosing information, such as export control regulations, national security restrictions, "
        "or contractual obligations with third parties. 2. Intellectual property protection: To protect proprietary "
        "information, including technical details of our models and training methodologies, trade secrets, or other "
        "confidential business information. 3. Public safety considerations: To protect public safety by not "
        "disclosing information that could be exploited to cause harm. 4. Privacy: To protect the personal privacy "
        "of individuals.",
    )),
    "PUBLIC_REVIEW": ("rsp-3.4.txt:14 section 3.6", (
        "This means working with one or more third-party organizations that will receive private versions of our "
        "Risk Reports (unredacted or with minimal redactions, as discussed below) and publish comprehensive "
        "commentary on them. Commentary will address topics including the quality of our reasoning, the validity of "
        "our risk assessments, the overall level of risk, and whether the redactions we’ve made for the public "
        "version are reasonable and appropriate.",
    )),
    "EXTERNAL_REVIEW": ("rsp-3.4.txt:15-16 section 3.6.3 (two runs: footnote 12 and the page foot between)", (
        "The external review will address: 1. Adequacy of information: Whether the Risk Report contains sufficient "
        "information to assess the identified risks; 2. Analytical rigor: The strength of the Risk Report’s "
        "reasoning and analysis; 3. Areas of disagreement: Whether the external reviewer disagrees with any of the "
        "Risk Report’s key claims and, if so, the reasons for any such disagreements; and 4. Risk reduction "
        "recommendations: Recommendations for further reducing identified risks. The external reviewer will also "
        "evaluate our redaction decisions while avoiding disclosure of the redacted content itself. In particular, "
        "the review will cover: 1. Redaction scope: The general nature and scope of redactions;",
        "2. Redaction justification: Whether the external reviewer generally agrees or disagrees with the publicly "
        "stated reasons for the redactions and, if relevant, the reasons for any disagreements; 3. Balancing test: "
        "Whether the redactions strike a reasonable balance between Anthropic’s legitimate interests and society’s "
        "interest in transparency; and 4. Materiality: Whether any of the redactions in the public report are "
        "material to any of the external reviewer’s substantive disagreements with the report’s claims.",
    )),
    "FN12": ("rsp-3.4.txt:15 footnote 12", (
        "12 For example, we may redact information if sharing it would endanger our legal right to treat it as "
        "confidential. This would be an uncommon situation. It does not mean we would redact information merely "
        "because it is sensitive or to reduce the risk of a leak.",
    )),
    "RSO": ("rsp-3.4.txt:16 section 4.1", (
        "We will maintain the position of RSO, a designated member of staff who is responsible for the "
        "implementation of this policy.",
    )),
    "RSO_DUTIES": ("rsp-3.4.txt:16 section 4.1", (
        "The RSO’s duties will include (but are not limited to): (1) as needed, proposing updates to this policy; "
        "(2) approving relevant model development or deployment decisions based on our risk assessments; (3) "
        "reviewing major contracts (e.g., deployment partnerships) for consistency with this policy; (4) overseeing "
        "the implementation of this policy, including the allocation of sufficient resources; (5) receiving and "
        "addressing reports of potential instances of noncompliance; and (6) making judgment calls on policy "
        "interpretation and application.",
    )),
    "ROADMAP": ("rsp-3.4.txt:3 Introduction", (
        "Frontier Safety Roadmaps are a new requirement under our RSP. These will describe our concrete plans for "
        "making progress across Security, Alignment, Safeguards, and Policy. Goals described in the Roadmaps are "
        "intended to be ambitious, yet achievable—providing the kind of forcing function that we consider to be a "
        "past success of our RSP. These are not hard commitments but rather public goals against which we will "
        "openly grade our progress.",
    )),
    "ASL_APPENDIX_B": ("rsp-3.4.txt:17-18 Appendix B (two runs: footnote 13 and the page foot between)", (
        "We still use this concept to refer to, and distinguish between, present levels of risk mitigations—those "
        "that we maintain for",
        "existing AI models.",
    )),
    "ASL_CHANGELOG": ("rsp-3.4.txt:18 Changelog, RSP v2.0", (
        "ASL definition changed: The term “ASL” now refers to groups of technical and operational safeguards (it "
        "previously also referred to models).",
    )),
}
ROWS = {  # row -> (sentence, carrier, the rule blocks whose legend it reaches)
    "x1": ("FN1", "argument_required", ('f24-argument',)),
    "x2": ("FN1", "lead_delay_needed", ('f24-delay',)),
    "x3": ("FN1", "competitors_evidence", ('f25-delay', 'f25-meet')),
    "x8": ("RIGHT_COLUMN", "advance_recommendations", ('s1-advance-default',)),
    "x9": ("RIGHT_COLUMN", "argument_required", ('f24-argument',)),
    "x10": ("RIGHT_COLUMN", "competitors_evidence", ('f25-delay', 'f25-meet')),
    "x4": ("LEFT_COLUMN", "listed", ('f5-default', 'f5-strict', 'rows-cond', 'rows-uncond', 'threshold-t1', 'threshold-t2', 'threshold-t3', 'threshold-t4')),
    "x5": ("MIDDLE_COLUMN", "plans_in_place", ('rows-cond', 'rows-uncond')),
    "x6": ("FN3", "plans_in_place", ('rows-cond', 'rows-uncond')),
    "x13": ("T1", "listed", ('threshold-t1', 'f5-default', 'f5-strict', 'rows-cond', 'rows-uncond')),
    "x14": ("T1", "harm:harm_of_non_novel_chem_bio_weapons", ()),
    "x15": ("T2", "listed", ('threshold-t2', 'f5-default', 'f5-strict', 'rows-cond', 'rows-uncond')),
    "x16": ("T2", "harm:harm_of_novel_chem_bio_weapons", ()),
    "x21": ("T2_FOOTNOTES", "listed", ('threshold-t2', 'f5-default', 'f5-strict', 'rows-cond', 'rows-uncond')),
    "x22": ("T2_FOOTNOTES", "harm:harm_of_novel_chem_bio_weapons", ()),
    "x17": ("T3", "listed", ('threshold-t3', 'f5-default', 'f5-strict', 'rows-cond', 'rows-uncond')),
    "x18": ("T3", "harm:harm_of_misaligned_high_stakes", ()),
    "x19": ("T4", "listed", ('threshold-t4', 'f5-default', 'f5-strict', 'rows-cond', 'rows-uncond')),
    "x20": ("T4", "harm:harm_of_automated_rd", ()),
    "x24": ("SCENARIO_2", "automation_attributable", ('s2-only-if-third', 's2-suff-third')),
    "x25": ("FN8", "double_rate", ('s2-only-if-third', 's2-suff-third')),
    "x26": ("FN9", "double_rate", ('s2-only-if-third', 's2-suff-third')),
    "x27": ("HIGHLY_CAPABLE", "highly_capable", ('f14-full-review', 'f25-delay', 'f25-meet', 'highly-capable-t4')),
    "x28": ("HIGHLY_CAPABLE", "in_the_lead", ('f24-argument', 'f24-delay')),
    "x29": ("SIGNIFICANTLY_REDACTED", "significantly_redacted", ('f14-full-review',)),
    "x30": ("SCOPE", "in_scope", ('f11-assess', 'f8-autonomous', 'f8-internal', 'f8-public')),
    "x31": ("SCOPE", "coverage:start_day", ()),
    "x33": ("FACTUAL", "factual_documented", ('f11-factual',)),
    "x34": ("ANALYSES", "risk_analysed", ('f11-analyses',)),
    "x35": ("REVIEW", "past_reviewed", ('f11-review',)),
    "x36": ("MARGINAL", "marginal_analysed", ('f11-marginal',)),
    "x37": ("FN11", "marginal_justification", ('f11-marginal',)),
    "x38": ("FN11", "marginal_major_role", ('f12-board-approval',)),
    "x39": ("REDACTION_REASONS", "redaction_reason_listed", ('f13-redact-p',)),
    "x40": ("PUBLIC_REVIEW", "public_review_sought", ('f14-public-review-default',)),
    "x41": ("EXTERNAL_REVIEW", "external_review_process", ('f16-all-sections', 'f16-ask-commentary', 'f16-before-board-default', 'f16-only-legal', 'f16-split-p')),
    "x42": ("EXTERNAL_REVIEW", "full_review", ('f14-full-review',)),
    "x43": ("FN12", "legal_rights_redaction", ('f16-only-legal',)),
    "x44": ("RSO", "rso_maintained", ('f18-rso',)),
    "x45": ("RSO", "executive_submitted", ('f12-approval',)),
    "x46": ("RSO", "governance_notified", ('f12-share',)),
    "x47": ("RSO", "recipient_options", ('f20-recipients',)),
    "x48": ("RSO", "concerns_rso", ('f20-board-recipient',)),
    "x49": ("RSO", "change_approved", ('f23-approval',)),
    "x50": ("RSO_DUTIES", "rso_maintained", ('f18-rso',)),
    "x51": ("ROADMAP", "roadmap_maintained", ('f6-maintain',)),
    "x52": ("ROADMAP", "roadmap_shared", ('f6-share',)),
    "x53": ("ROADMAP", "roadmap_updates", ('f6-updates',)),
    "x54": ("ROADMAP", "past_roadmaps_kept", ('f6-keep-past',)),
    "x55": ("ROADMAP", "goals_kept", ('f6-strive-default',)),
    "x56": ("ROADMAP", "roadmap_review_addressed", ('f11-goal-missed',)),
    "x57": ("ASL_APPENDIX_B", "plans_in_place", ('rows-cond', 'rows-uncond')),
    "x58": ("ASL_CHANGELOG", "plans_in_place", ('rows-cond', 'rows-uncond')),
}


# The counter's provenance lead (uc-audit.py.reads-1119 `_omit_legend_segments`): a legend string that starts with a section
# citation and quotes a sentence is documentation, never counted; a carried definition must sit in another string.
CITATION_LEAD = re.compile(r"\s*(?:[A-Z]?\d+(?:\.\d+)*[a-z]?\s*(?::|at\s+\{\d\})|\(?section\b)", re.I)
LITERAL_RUN = re.compile(r'"(?:[^"\\]|\\.)*"(?:\s*"(?:[^"\\]|\\.)*")*')


def sentence(name):
    return " ".join(SENTENCES[name][1])


def _vocabulary_rows():
    return [(row, name, key) for row, (name, key, _) in ROWS.items() if ":" not in key]


def _legend_strings(key):
    """The legend strings of a vocabulary entry: each run of implicitly joined literals, the entry's key dropped."""
    lines = (RSP / "rsp_vocabulary.py").read_text(encoding="utf-8").splitlines()
    text = "\n".join(line for line in fix._legend_entry_lines(key, lines) if not line.lstrip().startswith("#"))
    runs = ["".join(re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(0))).replace('\\"', '"')
            for m in LITERAL_RUN.finditer(text)]
    return runs[1:]


def _coverage_legends(monkeypatch):
    """D3's start-day legend for each date question d3() checks, read from the environments d3() builds."""
    seen = []
    build = S0.date_environment

    def record(extra=(), words=None):
        env = build(extra, words)
        seen.append(env)
        return env

    monkeypatch.setattr(S0, "date_environment", record)
    monkeypatch.setattr(S0, "_proved", lambda env, stated, goal: True)
    S0.d3.__wrapped__()
    out = {}
    for env in seen:
        if "start_day" in env.constants:
            out.setdefault("start", []).append(env.constants["start_day"].description)
    return out["start"]


def test_the_rows_name_kept_sentences_and_carriers_only():
    """53 KEPT rows, every sentence used, each vocabulary carrier a predicate of the environment."""
    assert len(ROWS) == 53 and {name for name, _, _ in ROWS.values()} == set(SENTENCES)
    predicates = V.environment()["vocabulary"]["predicates"]
    assert all(key in predicates for _, _, key in _vocabulary_rows())


def test_each_sentence_is_in_the_pinned_source():
    """Each stored run is in the pinned text (normalised), once; skipped when the text is not stored."""
    path = pinned_source("anthropic-rsp")
    source = norm(path.read_text(encoding="utf-8"))
    missing = [(name, run[:40]) for name, (_, runs) in SENTENCES.items() for run in runs
               if source.count(norm(run)) != 1]
    assert missing == []


@pytest.mark.parametrize("row,name,key", _vocabulary_rows())
def test_vocabulary_legend_carries_the_sentence(row, name, key):
    """The committed description (what the reader is shown) and the built one contain the sentence whole, inside one
    legend string that is not a citation-led provenance string."""
    want = norm(sentence(name))
    committed = json.loads((RSP / "environment.d1.json").read_text(encoding="utf-8"))["vocabulary"]["predicates"]
    assert want in norm(committed[key]["description"]), row
    assert want in norm(V.environment()["vocabulary"]["predicates"][key]["description"]), row
    holders = [s for s in _legend_strings(key) if want in norm(s)]
    assert any(not CITATION_LEAD.match(s) for s in holders), row


@pytest.mark.parametrize("row", sorted(r for r, (_, _, blocks) in ROWS.items() if blocks))
def test_the_carrier_is_a_predicate_each_rule_block_uses(row):
    """The legend reaches the row's rules: each named block uses the carrier predicate (the counter's used rule)."""
    _, key, blocks = ROWS[row]
    environment = json.loads((RSP / "environment.d1.json").read_text(encoding="utf-8"))
    for block_id in blocks:
        [block] = [b for name in ("rules.d1.ve", "facts.d1.ve") for b in base.rsp_translation.read_blocks(name)
                   if b.id == block_id]
        assert key in fix._used_predicates(block.text, environment), (row, block_id)


@pytest.mark.parametrize("row", sorted(r for r, (_, key, _) in ROWS.items() if key.startswith("harm:")))
def test_d2_harm_legend_carries_its_rows_definition(row):
    """D2 sends each threshold's harm constant with its row's left column whole (and T2's footnotes)."""
    name, key, _ = ROWS[row]
    constants = S0.risk_environment(S0.HARMS)["vocabulary"]["constants"]
    assert norm(sentence(name)) in norm(constants[key.split(":", 1)[1]]["description"]), row


def test_d3_coverage_date_legend_carries_the_scope_sentence(monkeypatch):
    """d3() builds D3b's environment with the start day described by 3.1's Scope sentence; D4 and D5 (other start
    days) do not get it."""
    legends = _coverage_legends(monkeypatch)
    want = norm(sentence("SCOPE"))
    kinds = [question for item, (_, _, _, question, _) in S0.DATE_QUESTIONS.items() if item != "D3a"]
    assert len(legends) == len(kinds) + 1  # the receipt count builds one more
    for question, legend in zip(kinds + ["receipt"], legends):
        assert (want in norm(legend)) == (question == "publication within"), question


def test_no_recorded_loss_is_a_carried_sentence():
    """accounting.d1.txt records no loss that a row now carries for the same block (or for D2D3)."""
    acc = fix._accounting()
    reach = {}
    for name, key, blocks in ROWS.values():
        for block_id in blocks or ("D2D3",):
            reach.setdefault(block_id, []).append(norm(sentence(name)))
    stale = [(block_id, e["words"]) for _, block_id, entries, _ in acc.read_sidecar(RSP / "accounting.d1.txt")
             for e in entries or () if e["reason"] == "loss"
             and any(norm(e["words"]) in s for s in reach.get(block_id, ()))]
    assert stale == []
