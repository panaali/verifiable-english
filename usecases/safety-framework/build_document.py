"""Builds the D1 span-accounting document over the pinned text (PLAN sections 7 and 10, metric M3).

    python usecases/safety-framework/build_document.py [--source PATH] [--check]

The pinned text (`fsf-3.1.txt`, 54,373 bytes, SHA-256 in PLAN section 1) is not
committed: the PDF states no licence. The builder reads it from `--source`
(default: the stored copy in `~/code/manage-agents/pilots/safety-framework/source/`),
checks its hash, partitions every byte into the units of `UNITS`, and writes:

- `fsf.d1.ve.md` next to the source (the `ve-document@1` with the source prose,
  never committed);
- `spans.json` here: unit ids, byte spans, kinds, statuses and reasons, no prose;
- `coverage.json` here: `ve.document.coverage` of the loaded document, and the
  master map in which units checked in D2 or D3 take that document's status.

Each unit starts at its anchor (the first occurrence after the previous anchor)
and runs to the next one; the first starts at byte 0. `--check` fails if the
committed `spans.json` or `coverage.json` would change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import translation as T  # noqa: E402
import vocabulary as V  # noqa: E402
from ve.ast import formula_to_data  # noqa: E402

DEFAULT_SOURCE = Path.home() / "code/manage-agents/pilots/safety-framework/source/fsf-3.1.txt"
TEXT_SHA256 = "18e3375b35c6699a8bf864606e48a20fae0152f1073c37c51e27a0c0f0c53946"
TEXT_BYTES = 54373

# Open terms (PLAN 3.2). Names are tokens; deciders are the text's own.
OPEN_TERMS = {
    "ot1_level_reached": ("developer", "whether a model has reached a level or an alert threshold (1.3.2)",
                          ["early warning evaluations", "expert assessments", "other sources of information"]),
    "ot2_residual_risk_acceptable": ("developer", "the deployment mitigations have brought the residual risk to an "
                                     "acceptable level (1.3.5)",
                                     ["the effectiveness of mitigations", "the scope of the deployment",
                                      "capabilities and mitigations of other publicly available models",
                                      "the historical incidence and severity of related events"]),
    "ot3_governance_determination": ("governance_function", "the appropriate governance function determines the "
                                     "residual risk to be acceptable (2.1.2, 3.1.2)",
                                     ["a safety case where a CCL has been reached"]),
    "ot4_security_adequate": ("developer", "the level of security applied is adequate (1.3.5)",
                              ["mitigations already in place", "the security of other models with similar "
                               "capabilities or risk profiles"]),
    "ot5_open_release_beneficial": ("developer", "the benefits of the open release of model weights outweigh the "
                                    "risks (1.3.5, 2.2)", []),
    "ot6_unlikely_propensities": ("developer", "the model is very unlikely to possess the propensities required "
                                  "for material risk of significant harm through misalignment (1.3.5)", []),
    "ot7_high_risk_internal": ("unstated", "a high-risk internal deployment (Glossary)",
                               ["building internal security infrastructure", "automating ML R&D"]),
    "ot8_low_risk_external": ("unstated", "a low-risk external deployment (Glossary)",
                              ["a small number of trusted testers", "small scale and private releases"]),
    "ot9_frontier_model": ("unstated", "a frontier AI model (Glossary)",
                           ["significant generality", "capabilities near or above other Google models"]),
    "ot10_material_capability_change": ("developer", "meaningful new capabilities or material increases that could "
                                        "materially undermine the justification (1.3.2)",
                                        ["provenance", "size", "modality", "general capability benchmarks"]),
    "ot11_public_safety_disclosure": ("developer", "an unmitigated and material risk to overall public safety, and "
                                      "sharing that will facilitate safety (5.2)", []),
    "ot12_periodic": ("unstated", "\"periodic\" residual risk assessments (3.2.1)", []),
    "ot13_reasonable_grounds": ("developer", "reasonable grounds to believe the adequacy of the Framework or the "
                                "adherence to it has been materially undermined (5.1)", []),
    "ot14_security_level": ("unstated", "security level N: RAND SL N goals and principles (footnote 6)",
                            ["security goals and principles rather than the benchmarks"]),
    "ot15_uplift": ("unstated", "uplift and additional expected harm relative to a baseline without generative AI "
                    "(footnote 8)", ["reference scenarios"]),
    "ot16_adjustment": ("developer", "a model does not possess capabilities meaningfully different from other "
                        "publicly available models that have weaker security applied (2.2)", []),
}

# Reading sets (PLAN 3.1): set id -> (harness set, readings -> rules of that reading).
READINGS = {
    "rs1_bullet2": ("RS1", {"s": ["f9-acc"], "g": ["f9-acc", "f9-dm", "f9-sec"]}),
    "rs1_bullet3": ("RS1", {"s": ["f10-acc"], "g": ["f10-acc", "f10-dm-same or f10-dm-diff", "f10-sec"]}),
    "rs1_bullet4": ("RS1", {"s": ["f11-acc"], "g": ["f11-acc", "f11-dm", "f11-sec"]}),
    "rs2_misuse": ("RS2", {"p": ["f12-p"], "u": ["f12-u"]}),
    "rs2_ml_rd": ("RS2", {"p": ["f13-p"], "u": ["f13-u"]}),
    "rs3_misuse": ("RS3", {"f": [], "ds": ["f16-ds"]}),
    "rs3_ml_rd": ("RS3", {"f": [], "ds": ["f16-ds"]}),
    "rs4_aim": ("RS4aim", {"default": ["f19-default"], "intent": []}),
    "rs4_holistic": ("RS4holistic", {"strict": ["f20-holistic-strict"], "default": ["f20-holistic-default"]}),
    "rs4_within": ("RS4within", {"strict": ["f20-within-strict"], "default": ["f20-within-default"]}),
    "rs4_elicitation": ("RS4elicitation", {"strict": ["f20-elicitation-strict"],
                                           "default": ["f20-elicitation-default"]}),
    "rs5_subsequent": ("RS5", {"d": ["f4-check-d"], "r": ["f4-check-r", "f4-further-r"]}),
    "rs6_insider": ("RS6", {"same": ["f15-same"], "different": ["f15-diff"]}),
    "rs7_footnote4": ("RS7", {"e": ["f3"], "m": []}),
    "rs8_bullet2": ("RS8", {"scope": [], "rel": ["f9-rel"]}),
    "rs8_bullet3": ("RS8", {"scope": [], "rel": ["f10-rel-same or f10-rel-diff"]}),
    "rs8_bullet4": ("RS8", {"scope": [], "rel": ["f11-rel"]}),
    "rs9_bullet3": ("RS9", {"same": ["f10-dm-same"], "different": ["f10-dm-diff"]}),
}

# Unit specifications. Status follows ve.document's inference: content with a specified
# meaning is CHECKED, an open meaning or an open reading set is OPEN, an unformalised
# meaning is UNFORMALISED, and a recognised kind with no formula is LABELLED.
def meta():
    return {"kind": "meta", "meaning": "specified", "support": "none"}


def label(kind="exposition"):
    return {"kind": kind, "meaning": "specified", "support": "none"}


def believes(act="believes"):
    return label(["attributed", "developer", act, "exposition"])


def hedged():
    return label(["hedged", "could", "exposition"])


def causal():
    return label(["causal", "because", "exposition", "exposition"])


def unformalised(reason):
    return {"kind": ["unformalised", reason], "meaning": {"unformalised": reason}, "support": "none"}


def facts(*ids, support="testimony"):
    return {"kind": "asserted", "meaning": "specified", "support": support, "facts": list(ids)}


def _open(terms):
    return {"open": list(terms)} if terms else "specified"


def rule(rule_id, *terms):
    return {"kind": "norm", "meaning": _open(terms), "support": "testimony", "rule": rule_id}


def condition(*terms):
    """A condition of a bullet whose rule sits on the bullet's lead-in: OPEN, no content of its own."""
    return {"kind": "norm", "meaning": _open(terms), "support": "testimony"}


def readings(set_id, *terms):
    return {"kind": "norm", "meaning": _open(terms), "support": "testimony", "reading_set": set_id}


def routed(document, why):
    return {**label("meta"), "routed": document, "why": why}


UNITS = [
    # Page 1
    ("Frontier Safety Framework Frontier", "p1-title", meta()),
    ("Published : April 17, 2026", "p1-published", routed("D3", "version_3_1_date")),
    # Page 2: Overview
    ("Frontier Safety Framework Overview", "p2-heading", meta()),
    ("The Frontier Safety Framework is a set of protocols", "ov-purpose", label()),
    ("It complements Google", "ov-complements", label()),
    ("The Framework is informed by", "ov-informed", label()),
    ("The core components of such Frameworks", "ov-components", label()),
    ("In the Framework, we specify protocols", "ov-tcl-ccl", label("definition")),
    ("The Framework addresses misuse risk", "ov-addresses", label()),
    ("For each type of risk, we define", "ov-each-type", label()),
    ("Risk assessment will necessarily involve", "ov-cross-cutting", unformalised("process_description")),
    ("Please refer to the Glossary", "ov-glossary-pointer", meta()),
    ("The safety and security of frontier AI models is a global public good", "ov-public-good", believes()),
    ("The protocols here represent our current understanding", "ov-current", label()),
    ("Importantly, there are certain mitigations", "ov-social-value", causal()),
    ("The Framework is based on early", "ov-early", label()),
    ("We may change our approach", "ov-may-change", hedged()),
    ("We will review the Framework periodically", "ov-review-periodically", unformalised("no_deadline_or_trigger")),
    ("3 In the context of the Framework, we address", "fn3", label()),
    ("2 As in, in the context of the Framework", "fn2", label("definition")),
    ("1 See https://", "fn1-urls", meta()),
    ("Frontier Safety Framework | 2", "p2-footer", meta()),
    # Page 3: contents
    ("Frontier Safety Framework Table of Contents", "p3-contents", meta()),
    # Page 4: 1.1 and 1.2
    ("Frontier Safety Framework Section 1: Framework", "s1-heading", meta()),
    ("This section describes the central components", "s1-intro", label()),
    ("1.1 Scope", "s11-heading", meta()),
    ("The Frontier Safety Framework focuses on possible severe risks", "s11-focus", label()),
    ("The Framework complements Google", "s11-complements", label()),
    ("The approaches and mitigations outlined in the Framework are not exclusive", "s11-not-exclusive", label()),
    ("1.2 Critical Capability Levels and Tracked", "s12-heading", meta()),
    ("The Framework is built primarily around", "s12-built", label()),
    ("These are capability levels at which, absent mitigation measures", "s12-ccl-definition",
     routed("D2", "CCLs: might lead to severe harm")),
    ("CCLs are determined by identifying", "s12-determined", label("explanation")),
    ("CCLs are one important component", "s12-component", label()),
    ("We identify CCLs for two kinds of risks", "s12-two-kinds", facts("closure-ccl-kinds")),
    ("For misuse risk , we define CCLs in the following risk domains", "s12-misuse-domains",
     facts("closure-misuse-ccls")),
    ("● CBRN: Risks of models assisting", "s12-domain-definitions", label("definition")),
    ("For machine learning R&D and misalignment risks , we define CCLs", "s12-ml-rd-ccls", label()),
    ("Such capabilities may serve as a substantial", "s12-cross-cutting", hedged()),
    ("This update to the Framework introduces", "s12-introduces", label()),
    ("TCLs are meant to capture significant risks", "s12-tcl-purpose", label()),
    ("We identify TCLs for CBRN", "s12-tcl-domains", facts("closure-tcls")),
    ("We may include TCLs for additional risks", "s12-may-include", hedged()),
    ("Similarly to CCLs, early warning evaluations will be used", "s12-tcl-proximity",
     unformalised("no_trigger_stated")),
    ("Frontier Safety Framework | 4", "p4-footer", meta()),
    # Page 5: 1.3 to 1.3.2
    ("Frontier Safety Framework 1.3 Risk Management Process", "s13-heading", meta()),
    ("We conduct our risk management process as appropriate", "s13-process", unformalised("as_appropriate")),
    ("1.3.1 Risk Identification", "s131-heading", meta()),
    ("The first part of our risk management process", "s131-first", label()),
    ("We identify potential risks that could stem", "s131-identify", label()),
    ("We consider a wide range of risks", "s131-consider", label()),
    ("As explained above, we have identified risk domains", "s131-domains", label()),
    ("As part of our broader research", "s131-continue", unformalised("as_appropriate")),
    ("For each of the four identified domains", "s131-four-domains",
     facts("bridge-one-domain", support="assumption")),
    ("1.3.2 Inherent Risk Assessment", "s132-heading", meta()),
    ("To understand whether a model may, without appropriate mitigations", "s132-purpose", label()),
    ("We conduct a critical capability assessment prior to", "s132-cca",
     rule("f2", "ot9_frontier_model")),
    ("For external deployment of subsequent versions", "s132-subsequent",
     readings("rs5_subsequent", "ot10_material_capability_change")),
    ("To understand if a subsequent version of the model has meaningful", "s132-mcca", rule("f5")),
    ("These assessments draw on model characteristics", "s132-mcca-factors", label("example")),
    ("To understand if such a change in capability", "s132-light-weight", hedged()),
    ("We may also apply material capability change assessments", "s132-non-frontier", hedged()),
    ("Central to our critical capability assessments are", "s132-early-warning", label("definition")),
    ("For CCLs, we define", "s132-alert-thresholds", facts("closure-alert-thresholds")),
    ("In our evaluations, we seek to apply", "s132-scaffolding", unformalised("aim_without_force")),
    ("We may run early warning evaluations more ", "s132-may-run", hedged()),
    ("4 A critical capability assessment may not be conducted", "fn4",
     readings("rs7_footnote4", "ot8_low_risk_external", "ot3_governance_determination")),
    ("Frontier Safety Framework | 5", "p5-footer", meta()),
    # Page 6: 1.3.2 continued to 1.3.4
    ("Frontier Safety Framework frequently", "p6-header", meta()),
    ("frequently or adjust alert thresholds", "s132-may-run-continued", hedged()),
    ("We conduct further analysis", "s132-further-analysis", unformalised("as_appropriate")),
    ("In particular, we strive to learn", "s132-strive", unformalised("aim_without_force")),
    ("Actionable insights from these processes", "s132-insights", label()),
    ("Our approach to model evaluations and inherent risk assessments", "s132-means", believes()),
    ("Where appropriate, we may engage", "s132-engage", hedged()),
    ("Note on Machine Learning R&D CCLs:", "note-ml-rd-must", readings("rs4_elicitation")),
    ("However, as a frontier AI company, we do not expect", "note-ml-rd-expect", believes("expects")),
    ("As a result, to assess the ML R&D CCLs, we may use", "note-ml-rd-may-use", hedged()),
    ("1.3.3 Risk Mitigation", "s133-heading", meta()),
    ("We apply safety and security mitigations throughout", "s133-apply", unformalised("where_appropriate")),
    ("When a model reaches an alert threshold for a CCL", "s133-alert", rule("f6", "ot1_level_reached")),
    ("This will inform the formulation", "s133-inform", unformalised("event_order")),
    ("Central to most response plans", "s133-central", label()),
    ("However, if we assess that risks stemming", "s133-update-threshold", hedged()),
    ("We have two categories of mitigations", "s133-categories", label("definition")),
    ("The mitigations described in this document are limited", "s133-limited", label()),
    ("Because we cannot always anticipate", "s133-determined-later", hedged()),
    ("These mitigations also reflect considerations", "s133-reflect", label()),
    ("1.3.4 Residual Risk Assessment", "s134-heading", meta()),
    ("We will use various processes", "s134-various", unformalised("unspecified_process")),
    ("● Security mitigations : security infrastructure", "s134-security", label()),
    ("Frontier Safety Framework | 6", "p6-footer", meta()),
    # Page 7: 1.3.4 continued, 1.3.5
    ("Frontier Safety Framework ● Deployment mitigations", "p7-header", meta()),
    ("● Deployment mitigations : we will use", "s134-deployment", unformalised("unspecified_process")),
    ("Models reaching TCLs or CCLs will be subject", "s134-rra", rule("f7-rra", "ot1_level_reached")),
    ("For models reaching CCLs, the residual risk assessment will be informed", "s134-safety-case",
     rule("f7-sc", "ot1_level_reached")),
    ("See the deployment mitigations sections below", "s134-see", meta()),
    ("1.3.5 Risk Acceptance Determination", "s135-heading", meta()),
    ("The Framework outlines the risk acceptance determination", "s135-intro", label()),
    ("● A model for which inherent risk assessment indicates no T/CCL", "s135-bullet1",
     rule("f8", "ot1_level_reached")),
    ("● A model for which the inherent risk assessment indicates a misuse", "s135-bullet2",
     readings("rs1_bullet2", "ot1_level_reached")),
    ("○ We assess that the deployment mitigations have brought the residual risk of harm", "s135-bullet2-dm",
     condition("ot2_residual_risk_acceptable")),
    ("This is required only for external deployment, not internal", "s135-bullet2-only",
     readings("rs8_bullet2")),
    ("○ Security mitigations have been applied", "s135-bullet2-sec",
     condition("ot4_security_adequate", "ot5_open_release_beneficial", "ot14_security_level")),
    ("● A model for which the inherent risk assessment indicates a ML R&D CCL", "s135-bullet3",
     readings("rs1_bullet3", "ot1_level_reached")),
    ("○ We assess that the deployment mitigations have brought the residual risk of severe", "s135-bullet3-dm",
     readings("rs9_bullet3", "ot2_residual_risk_acceptable")),
    ("This is required only for external deployment and high-risk", "s135-bullet3-only",
     readings("rs8_bullet3", "ot7_high_risk_internal")),
    ("○ Security mitigations have been applied", "s135-bullet3-sec",
     condition("ot4_security_adequate", "ot5_open_release_beneficial", "ot14_security_level")),
    ("5 Note that deployment mitigations for the ML R&D CCLs", "fn5", label("explanation")),
    ("Frontier Safety Framework | 7", "p7-footer", meta()),
    # Page 8: 1.3.5 continued
    ("Frontier Safety Framework ● A model", "p8-header", meta()),
    ("● A model for which the inherent risk assessment indicates the TCL", "s135-bullet4",
     readings("rs1_bullet4", "ot1_level_reached")),
    ("○ We assess that the deployment mitigations have brought the residual risk of significant",
     "s135-bullet4-dm", condition("ot2_residual_risk_acceptable", "ot6_unlikely_propensities")),
    ("This is required only for external deployment and high-risk", "s135-bullet4-only",
     readings("rs8_bullet4", "ot7_high_risk_internal")),
    ("○ We assess that the level of security applied is adequate", "s135-bullet4-sec",
     condition("ot4_security_adequate", "ot5_open_release_beneficial")),
    ("Note: Assessing frontier AI capabilities", "s135-note", label()),
    ("The mitigation and the effects of such mitigation should also be assessed holistically",
     "s135-holistic", readings("rs4_holistic")),
    ("Frontier Safety Framework | 8", "p8-footer", meta()),
    # Page 9: Section 2, 2.1, 2.1.1
    ("Frontier Safety Framework Section 2: Misuse", "s2-heading", meta()),
    ("This section describes our mitigation approach for models that pose risks of significant or severe harm "
     "through misuse", "s2-intro", label()),
    ("2.1 Mitigation Approach", "s21-heading", meta()),
    ("There are two categories of mitigations to address", "s21-categories", label("definition")),
    ("For security, we have several levels", "s21-levels", label()),
    ("Regarding deployment mitigations for models reaching T/CCLs", "s21-process", label()),
    ("This structured process for deployment mitigations", "s21-centered", label()),
    ("2.1.1 Security Mitigations", "s211-heading", meta()),
    ("Security mitigations against exfiltration or unauthorized modification risk, such as", "s211-important",
     label()),
    ("This is because the release or unauthorized modification", "s211-because", causal()),
    ("Using Google’s Secure AI Framework", "s211-saif", unformalised("external_reference")),
    ("We use security levels to indicate", "s211-levels", unformalised("external_reference")),
    ("We also define and recommend", "s211-sl2plus", facts("measures-sl2plus")),
    ("These additional measures may include", "s211-may-include", label("example")),
    ("Because AI security is an area of active research", "s211-expect", believes("expects")),
    ("6 In other words", "fn6", unformalised("external_reference")),
    ("Frontier Safety Framework | 9", "p9-footer", meta()),
    # Page 10: 2.1.2
    ("Frontier Safety Framework 2.1.2 Deployment Mitigations", "s212-heading", meta()),
    ("The following mitigation process for external deployments", "s212-applied", label()),
    ("1. Development and assessment of mitigations", "s212-step1", unformalised("iterative_process")),
    ("b. Assessing the robustness", "s212-step1b", label("example")),
    ("c. Where the model has reached a CCL, the residual", "s212-step1c", rule("f7-sc", "ot1_level_reached")),
    ("2. Pre-deployment review of residual risk assessment: external deployments of a model take place only after",
     "s212-step2", readings("rs2_misuse", "ot3_governance_determination")),
    ("In particular, we will deem deployment mitigations adequate", "s212-deem", unformalised("degree_term")),
    ("3. Post-deployment processes", "s212-step3", hedged()),
    ("Material updates to a safety case will be submitted", "s212-submitted", rule("f14")),
    ("This process is designed to ensure", "s212-designed", label("explanation")),
    ("With iteration on mitigations and residual risk assessments, we believe", "s212-believe", believes()),
    ("7 See section 5", "fn7", meta()),
    ("Frontier Safety Framework | 10", "p10-footer", meta()),
    # Page 11: 2.2 and 2.2.1
    ("Frontier Safety Framework While we monitor", "p11-header", meta()),
    ("While we monitor for potential future risks", "s22-insider-assessment", believes()),
    ("At this stage, additional mitigations beyond", "s22-insider-not-required", readings("rs6_insider")),
    ("2.2 Misuse Capability Levels", "s22-heading", meta()),
    ("We set out below a set of CBRN", "s22-set-out", label()),
    ("We expect these to evolve over time.", "s22-expect", believes("expects")),
    ("We recommend a security level for each CCL", "s22-recommend",
     readings("rs3_misuse", "ot14_security_level", "ot16_adjustment")),
    ("In practice, our overall security posture", "s22-posture", hedged()),
    ("These recommended security levels reflect", "s22-adjusted", unformalised("may_be_adjusted")),
    ("Relatedly, we believe these recommendations", "s22-believe", believes()),
    ("2.2.1 Chemical, Biological", "s221-heading", meta()),
    ("This risk domain focuses on risks of models assisting in the development, preparation and/or execution of a "
     "CBRN", "s221-focus", label("definition")),
    ("Table 2.2.1.a", "s221-table-heading", meta()),
    ("CBRN uplift level 1: Provides", "s221-ccl", facts("levels-cbrn")),
    ("The difficulty of building defenses", "s221-rationale", label("explanation")),
    ("CBRN Tracked Capability Level The CBRN TCL", "s221-tcl", routed("D2", "the CBRN TCL: significant but not severe")),
    ("8 Here, and in other misuse T/CCLs", "fn8", unformalised("degree_term")),
    ("Frontier Safety Framework | 11", "p11-footer", meta()),
    # Page 12: 2.2.2 and 2.2.3
    ("Frontier Safety Framework 2.2.2 Cyber", "s222-heading", meta()),
    ("This risk domain focuses on risks of models assisting in the development, preparation, and/or execution of "
     "a cyber", "s222-focus", label("definition")),
    ("Table 2.2.2.a", "s222-table-heading", meta()),
    ("Cyber uplift level 1: Provides", "s222-ccl", facts("levels-cyber")),
    ("Models able to greatly assist cyber attack", "s222-rationale", label("explanation")),
    ("2.2.3 Harmful Manipulation", "s223-heading", meta()),
    ("This risk domain focuses on risks of models with high manipulative", "s223-focus", label("definition")),
    ("Note: The research into harmful manipulation", "s223-note", label()),
    ("Table 2.2.3.a", "s223-table-heading", meta()),
    ("Harmful manipulation level 1 (exploratory): Possesses", "s223-ccl", facts("levels-manipulation")),
    ("The lower velocity of harm scenarios", "s223-rationale", label("explanation")),
    ("Frontier Safety Framework | 12", "p12-footer", meta()),
    # Page 13: Section 3, 3.1, 3.1.1, 3.1.2 step 1
    ("Frontier Safety Framework Section 3", "s3-heading", meta()),
    ("This section describes our mitigation approach for models that pose risks of significant or severe harm "
     "through machine", "s3-intro", label()),
    ("3.1 Mitigation Approach", "s31-heading", meta()),
    ("As with misuse T/CCLs", "s31-similar", label()),
    ("3.1.1 Security Mitigations", "s311-heading", meta()),
    ("Security mitigations against exfiltration and unauthorized modification risk are important for models "
     "reaching ML", "s311-important", label()),
    ("In addition, exfiltration of highly capable models", "s311-likelihood", causal()),
    ("Below, we rely again on security levels", "s311-rely", unformalised("external_reference")),
    ("9 Security mitigations also protect", "fn9-a", label()),
    ("3.1.2 Deployment Mitigations", "s312-heading", meta()),
    ("The following mitigation process will be applied for deployments", "s312-applied", label()),
    ("The approach is similar to misuse", "s312-similar", label()),
    ("1. Development and assessment of mitigations", "s312-step1", unformalised("iterative_process")),
    ("b. Assessing the robustness", "s312-step1b", label("example")),
    ("c. Where the model has reached a CCL, the residual", "s312-step1c", rule("f7-sc", "ot1_level_reached")),
    ("10 See section 6", "fn10", meta()),
    ("9 While the RAND framework", "fn9-b", unformalised("external_reference")),
    ("Frontier Safety Framework | 13", "p13-footer", meta()),
    # Page 14: 3.1.2 steps 2 and 3, 3.2, 3.2.1
    ("Frontier Safety Framework 2. Pre-deployment", "p14-header", meta()),
    ("2. Pre-deployment review of residual risk assessment: external deployments and high-risk", "s312-step2",
     readings("rs2_ml_rd", "ot3_governance_determination", "ot7_high_risk_internal")),
    ("In particular, we will deem deployment mitigations adequate", "s312-deem", unformalised("degree_term")),
    ("3. Post-deployment processes", "s312-step3", hedged()),
    ("Material updates to a safety case will be submitted", "s312-submitted", rule("f14")),
    ("This process is designed to ensure", "s312-designed", label("explanation")),
    ("With iteration on mitigations and residual risk assessments, we believe", "s312-believe", believes()),
    ("3.2 ML R&D and Misalignment Capability Levels", "s32-heading", meta()),
    ("We take a tiered approach", "s32-tiered", label()),
    ("3.2.1 Stealth and Situational Awareness", "s321-heading", meta()),
    ("The Stealth and Situational Awareness TCL is defined as follows", "s321-tcl",
     facts("levels-stealth")),
    ("When a model has reached this TCL, we will carry out periodic", "s321-periodic",
     rule("f17-pra", "ot1_level_reached", "ot12_periodic")),
    ("This assessment may take into account", "s321-may", label("example")),
    ("Since misalignment risks can manifest", "s321-internal", label("explanation")),
    ("If the risk assessment deems the residual risk from internal deployment", "s321-safeguards",
     rule("f17-add", "ot1_level_reached")),
    ("3.2.2 ML R&D Critical Capability Levels", "s322-heading", meta()),
    ("We define ML R&D CCLs at capability levels", "s322-define", routed("D2", "ML R&D CCLs: severe")),
    ("We expect these to evolve over time.", "s322-expect", believes("expects")),
    ("We recommend a security level for each of these", "s322-recommend",
     readings("rs3_ml_rd", "ot14_security_level", "ot16_adjustment")),
    ("Frontier Safety Framework | 14", "p14-footer", meta()),
    # Page 15: table 3.2.2.a
    ("Frontier Safety Framework CCLs, which reflect", "p15-header", meta()),
    ("CCLs, which reflect our assessment", "s322-recommend-continued", label()),
    ("Table 3.2.2.a", "s322-table-heading", meta()),
    ("ML R&D acceleration level 1: Has been used", "s322-acceleration", facts("levels-ml-rd-acceleration")),
    ("Unrestricted access to models at this level of capability could significantly", "s322-acceleration-rationale",
     label("explanation")),
    ("ML R&D automation level 1: Can fully automate", "s322-automation", facts("levels-ml-rd-automation")),
    ("We recommend Security level 4", "s322-automation-recommend", unformalised("addressed_to_the_field")),
    ("Unrestricted access to models at this level of capability could give", "s322-automation-rationale",
     label("explanation")),
    ("This could be catastrophic", "s322-catastrophic", routed("D2", "catastrophic: unranked")),
    ("Therefore, we recommend models at this level", "s322-exceptional", unformalised("addressed_to_the_field")),
    ("13 This level may include", "fn13", hedged()),
    ("12 This level may include", "fn12", hedged()),
    ("11 The same caveats", "fn11", unformalised("may_be_adjusted")),
    ("Frontier Safety Framework | 15", "p15-footer", meta()),
    # Page 16: Section 4
    ("Frontier Safety Framework Section 4", "s4-heading", meta()),
    ("We have in place a well-established", "s41-structure", believes()),
    ("Responsibilities for assessing and mitigating", "s41-responsibilities", label()),
    ("This includes legal, compliance, and safety reviews", "s41-reviews", label()),
    ("Frontier Safety Framework | 16", "p16-footer", meta()),
    # Page 17: Section 5
    ("Frontier Safety Framework Section 5", "s5-heading", meta()),
    ("The Frontier Safety Framework will be reviewed at least once a year", "s51-yearly",
     rule("f18-yearly")),
    ("—more frequently if we have reasonable grounds", "s51-frequent", rule("f18-frequent", "ot13_reasonable_grounds")),
    ("The process will involve", "s51-process", unformalised("process_description")),
    ("Following this assessment, we may", "s51-may-update", hedged()),
    ("The updated version and framework assessment will be reviewed", "s51-governance-bodies",
     unformalised("event_order")),
    ("5.2 Disclosures", "s52-heading", meta()),
    ("If we assess that a model has reached a CCL that poses", "s52-aim",
     readings("rs4_aim", "ot1_level_reached", "ot11_public_safety_disclosure")),
    ("Where appropriate, and subject to adequate confidentiality", "s52-may-include", label("example")),
    ("We may also consider disclosing", "s52-may-also", hedged()),
    ("We will continue to review and evolve", "s52-continue", unformalised("no_deadline_or_trigger")),
    ("5.3 Past Updates and Changes", "s53-heading", meta()),
    ("● Version 3.1 (April 17, 2026)", "s53-v31", routed("D3", "version_3_1_date")),
    ("○ Introduced CBRN TCLs", "s53-changes", label()),
    ("● Version 3.0 (September 22, 2025)", "s53-v30", routed("D3", "version_3_0_date")),
    ("● Version 2.0 (February 4, 2025)", "s53-v20", routed("D3", "version_2_0_date")),
    ("● Version 1.0 (May 17, 2024)", "s53-v10", routed("D3", "version_1_0_date")),
    ("Frontier Safety Framework | 17", "p17-footer", meta()),
    # Page 18: Glossary
    ("Frontier Safety Framework Glossary", "g-heading", meta()),
    ("Frontier AI Models or Models :", "g-frontier", label("definition")),
    ("There may be many different checkpoints", "g-checkpoints", label("definition")),
    ("When we refer to “model”", "g-model", label("definition")),
    ("Risk Domains CBRN:", "g-domains", label("definition")),
    ("Thresholds Critical Capability Levels (CCLs):", "g-ccl", routed("D2", "CCLs: severe")),
    ("Tracked Capability Levels (TCLs):", "g-tcl", facts("tcl-not-ccl")),
    ("Alert Thresholds:", "g-alert", label("definition")),
    ("Inherent Risk Assessment Inherent Risk Assessments:", "g-inherent", label("definition")),
    ("Critical Capability Assessments: determine", "g-cca", label("definition")),
    ("● Early Warning Evaluations:", "g-early-warning", label("definition")),
    ("Frontier Safety Framework | 18", "p18-footer", meta()),
    # Page 19
    ("Frontier Safety Framework modeling", "p19-header", meta()),
    ("modeling to determine a model’s proximity", "g-early-warning-continued", label("definition")),
    ("Material Capability Change Assessments: indicate", "g-mcca", label("definition")),
    ("● Material Capability Increases:", "g-increases", label("definition")),
    ("Risk Mitigation Response Plans:", "g-response-plans", label("definition")),
    ("Deployment Mitigations: are safety measures", "g-deployment-mitigations", label("definition")),
    ("● External Deployments:", "g-external", facts("activities-low-risk")),
    ("● Low-Risk External Deployments:", "g-low-risk", label("definition")),
    ("● Internal Deployments:", "g-internal", facts("activities-internal-external")),
    ("● High-Risk Internal Deployments:", "g-high-risk", facts("activities-high-risk")),
    ("Security Mitigations: are safety measures", "g-security-mitigations", label("definition")),
    ("We communicate the level of security", "g-communicate", unformalised("external_reference")),
    ("● RAND Security Levels:", "g-rand", unformalised("external_reference")),
    ("14 14 See https://", "fn14", meta()),
    ("Frontier Safety Framework | 19", "p19-footer", meta()),
    # Page 20
    ("Frontier Safety Framework Residual Risk Assessment", "p20-header", meta()),
    ("Residual Risk Assessments: the process", "g-rra", label("definition")),
    ("This is part of the risk management process, following", "g-rra-part", label("definition")),
    ("The residual risk should be brought within", "g-within", readings("rs4_within")),
    ("Safety Cases: are an assessable argument", "g-safety-cases", label("definition")),
    ("Residual risk assessments will be supplemented with a safety case", "g-safety-case-when",
     rule("f7-sc", "ot1_level_reached")),
    ("15 For misuse risk, such an argument may be based", "g-safety-case-misuse", label("example")),
    ("For ML R&D and misalignment risk, such an argument", "g-safety-case-ml-rd", label("example")),
    ("15 See also, for reference", "fn15", meta()),
    ("Frontier Safety Framework | 20", "p20-footer", meta()),
]
# 1.3.5 "further development or deployment" (activities-development) has no unit of its own:
# it is part of the bullet lead-ins; the premise is listed with the activity premises.
EXTRA_PREMISE_UNITS = {"activities-development": "s135-bullet2"}

# A distinguishing situation per reading set: a case of cases.json at which the readings
# give different answers in results.json.
DISTINGUISHING = {"RS1": "A-L2-EXT", "RS2": "A-L0-EXT", "RS3": "B-L2", "RS4aim": "K9-L2", "RS4holistic": "K6",
                  "RS4within": "B-L2", "RS4elicitation": "K6", "RS5": "K3", "RS6": "B-L2", "RS7": "A-L0-LRX",
                  "RS8": "A-L2-INT", "RS9": "A-L6-HRI"}


def spans(source):
    starts, cursor = [], 0
    for anchor, uid, _ in UNITS:
        at = source.find(anchor.encode(), cursor)
        if at < 0:
            raise SystemExit(f"anchor not found after byte {cursor}: {uid} {anchor!r}")
        starts.append(0 if not starts else at)
        cursor = at + 1
    return list(zip(starts, starts[1:] + [len(source)]))


def situation_model(env, case_id):
    """The case as a model over the document environment (regulated tables empty)."""
    import run as R
    from ve.model import FiniteModel
    atoms = R.fact_atoms() | R.case_atoms(R.CASES[case_id])
    relations = {p: [] for p in env.predicates}
    for atom in atoms:
        relations[atom[0]].append(list(atom[1:]))
    return FiniteModel.from_dict(env, {"complete": True, "domains": R.DOMAINS,
                                       "constants": {c: c for c in env.constants},
                                       "relations": {p: sorted(r) for p, r in relations.items()}})


def build(source):
    from ve import ast as A
    raw_env = V.environment()
    env = T.environment()
    facts = {block_id: formulas for block_id, _, formulas in T.facts()}
    used_rules, units, reading_sets, records = set(), [], [], []
    for (anchor, uid, spec), span in zip(UNITS, spans(source)):
        unit = {"id": uid, "span": list(span), "kind": spec["kind"], "meaning": spec["meaning"],
                "support": spec["support"]}
        record = {"id": uid, "span": list(span), "kind": spec["kind"] if type(spec["kind"]) is str
                  else spec["kind"][0]}
        if "facts" in spec:
            formulas = [f for block in spec["facts"] for f in facts[block]]
            conjunction = formulas[0]
            for f in formulas[1:]:
                conjunction = A.And(conjunction, f)
            unit["content"] = {"ast": formula_to_data(env, conjunction)}
            record["premises"] = spec["facts"]
        if "rule" in spec:
            if spec["rule"] in used_rules:
                record["restates"] = spec["rule"]
            else:
                used_rules.add(spec["rule"])
                unit["content"] = {"norm": json.loads(T.parsed_rule(spec["rule"]))}
                record["rule"] = spec["rule"]
        if "reading_set" in spec:
            set_id = spec["reading_set"]
            harness_set, choices = READINGS[set_id]
            model = situation_model(env, DISTINGUISHING[harness_set])
            reading_sets.append({
                "id": set_id, "unit": uid, "version": 1, "status": "open",
                "readings": [{"id": choice, "kind": "norm", "meaning_id": "pending", "content": None,
                              "admission": {"who": "translator",
                                            "why": f"{harness_set} = {choice}: rules "
                                                   f"{', '.join(rules) if rules else '(none)'} of rules.d1.ve",
                                            "distinguishing_models": {other: model.model_id
                                                                      for other in choices if other != choice}}}
                             for choice, rules in choices.items()],
                "models": {model.model_id: model.to_dict()}})
            record["reading_set"] = set_id
        if "routed" in spec:
            record["routed"] = {"document": spec["routed"], "carries": spec["why"]}
        if type(spec["meaning"]) is dict and "unformalised" in spec["meaning"]:
            record["reason"] = spec["meaning"]["unformalised"]
        if type(spec["meaning"]) is dict and "open" in spec["meaning"]:
            record["open_terms"] = spec["meaning"]["open"]
        units.append(unit)
        records.append(record)
    open_terms = [{"name": name, "arguments": [], "decided_by": decider, "necessary": [], "sufficient": [],
                   "factors": [what] + factors, "precedents": [], "jurisdiction": "fsf_v3_1", "version": 1}
                  for name, (decider, what, factors) in OPEN_TERMS.items()]
    meta_block = {"format": "ve-document@1", "environment": raw_env, "units": units,
                  "open_terms": open_terms, "reading_sets": reading_sets}
    document = b"---\n" + json.dumps(meta_block, indent=1, ensure_ascii=False).encode() + b"\n---\n" + source
    return document, records


def measure(document, path):
    from ve.document import coverage, load_document
    path.write_bytes(document)
    loaded = load_document(path)
    statuses = {u["id"]: u["status"] for u in loaded["units"]}
    return coverage(loaded), statuses


def master(records, statuses, results):
    """Every byte with its final status: a unit routed to D2 or D3 takes that document's status."""
    d2_d3 = results.get("d2_d3", {})
    routed_ok = {"D2": bool(d2_d3.get("d2", {}).get("environment_id")),
                 "D3": all(v.get("certificate") for k, v in d2_d3.get("d3", {}).items() if k in ("D1", "D3"))}
    totals = {}
    for record in records:
        status = statuses[record["id"]]
        if "routed" in record and routed_ok[record["routed"]["document"]]:
            status = "CHECKED"
        record["status"] = status
        totals[status] = totals.get(status, 0) + record["span"][1] - record["span"][0]
    return totals


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    source = args.source.read_bytes()
    if hashlib.sha256(source).hexdigest() != TEXT_SHA256 or len(source) != TEXT_BYTES:
        raise SystemExit("the source is not the pinned FSF 3.1 text")
    document, records = build(source)
    out = args.source.parent / "fsf.d1.ve.md"
    report, statuses = measure(document, out)
    results = json.loads((HERE / "results.json").read_text())
    totals = master(records, statuses, results)
    spans_text = json.dumps({"source_sha256": TEXT_SHA256, "source_bytes": TEXT_BYTES, "units": records},
                            indent=1) + "\n"
    coverage_text = json.dumps({"document": "fsf.d1.ve.md (built locally, not committed)",
                                "document_sha256": hashlib.sha256(document).hexdigest(),
                                "d1": report, "master_bytes_by_status": totals}, indent=1, sort_keys=True) + "\n"
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
