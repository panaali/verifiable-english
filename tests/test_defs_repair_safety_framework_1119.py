"""defs-repair-safety-framework-1119: each kept FSF source definition is carried word for word in a shown legend.

The definitions audit (manage-agents reviews/defs-carried-1119/rows-safety-framework-x.tsv, read at VE e53db4e8fc)
filed 44 P1 rows for the FSF document. Each kept row names a term a rule depends on, the predicate whose legend
carries it and the passage of the pinned source (FSF 3.1, fsf-3.1.txt: one PDF page per line) that defines it. The
passages are stored below in the source's own bytes with their line and section. Each must stand, after the project's
quote normalisation (`omit_norm`: NFKC, curly quotes, case, whitespace), in the committed legend
(environment.d1.json, what a reader is shown), in vocabulary.py's output, and in the literal legend strings the
definitions counter reads (tools/defs_carried_counter.py: a computed or citation-led legend is shown but not
counted). When the pinned text is stored at its pin, each passage must also be in it, at its line, byte for byte; the
test never downloads it (tests/pinned_source.py).

Rows x1 and x45 were PARTIAL-COVER (F2, F3): the merged rows already carry their first sentence, so the passage is
stored in two pieces, each carried. Rows x31, x33 and x34 are dropped: fsf-repair-f6-sl2plus-1119 carries them word
for word in the `recommends` legend, which DROPPED checks (docs/usecases/safety-framework/
defs-repair-safety-framework-1119/REPORT.md).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
from typing import NamedTuple

import pytest

from omission_rule import omit_norm
from tests.pinned_source import pinned_source
from tools import defs_carried_counter as counter

HERE = Path(__file__).resolve().parents[1] / "usecases" / "safety-framework"
GOV = "governance_found_acceptable_with_safety_case_where_ccl_reached"
INHERENT = "Glossary, Inherent Risk Assessment"
FRONTIER = "Glossary, Frontier AI Models or Models"

# The source passages, in the bytes of fsf-3.1.txt (sha256 18e3375b…c53946, usecases/pinned_sources.json).
# The Glossary's second sentence as fsf-repair-f2-glossary-1119 quotes it, without its full stop.
FRONTIER_GENERALITY = (
    "Frontier AI models’ agentic and reasoning-based general capabilities near or exceed those of other Google "
    "models")
FRONTIER_VERSIONS = (
    "There may be many different checkpoints and versions of the same model along the entire model lifecycle: we "
    "consider checkpoints and versions the same model if their base capabilities stem primarily from the same "
    "foundational training run, but will conduct additional testing on new versions as specified in Section 1.3 . "
    "When we refer to “model” in this Framework, we may be referring to a checkpoint or version of the model.")
RISK_DOMAINS = (
    "CBRN: risks of models assisting in the development, preparation, and/or execution of a chemical, biological, "
    "radiological, or nuclear (“CBRN”) threat. Cyber: risks of models assisting in the development, preparation, "
    "and/or execution of a cyber attack. Harmful Manipulation: risks of models with high manipulative capabilities "
    "potentially being misused in ways that could reasonably result in large scale harm. ML R&D and Misalignment: "
    "risks of models’ ML R&D capabilities or misaligned propensities reducing society’s overall ability to manage "
    "AI risks. Such capabilities may serve as a substantial cross-cutting risk factor for several pathways (e.g. "
    "through misalignment, misuse or structural risks) to severe harm.")
FOOTNOTE_2 = (
    "2 As in, in the context of the Framework, risks of threat actors using critical capabilities of deployed or "
    "exfiltrated models to cause harm.")
FOOTNOTE_3 = (
    "3 In the context of the Framework, we address specific scenarios where model misalignment may create the risk "
    "of significant or severe harm, and scenarios where ML R&D capabilities may heighten misalignment, misuse, and "
    "structural risks.")
CCL_GLOSSARY = (
    "Critical Capability Levels (CCLs): are the main capability thresholds around which we have built the "
    "Framework process. They represent the capability levels at which, absent mitigation measures, frontier AI "
    "models or systems may pose heightened risk of severe harm.")
CCL_1_2 = (
    "The Framework is built primarily around capability thresholds called “Critical Capability Levels (CCLs).” "
    "These are capability levels at which, absent mitigation measures, frontier AI models or systems may pose "
    "heightened risk of severe harm. CCLs are determined by identifying and analyzing the main foreseeable paths "
    "through which a model could result in severe harm: we then define the CCLs as the minimal set of capabilities "
    "a model must possess to do so.")
TCL_GLOSSARY = (
    "Tracked Capability Levels (TCLs): are capability thresholds which capture a lower level of risks than our "
    "CCLs. They represent the capability levels at which, absent mitigation measures, frontier AI models or "
    "systems may pose heightened risk of significant but not severe levels of harm.")
TCL_1_2 = (
    "This update to the Framework introduces “Tracked Capability Levels (TCLs).” TCLs are meant to capture "
    "significant risks that may manifest at a lower capability threshold than our CCLs and we apply our mitigation "
    "and risk acceptance determination process proportionately.")
ALERT_GLOSSARY = (
    "Alert Thresholds: are thresholds which we set marginally earlier than our CCLs. Crossing these thresholds "
    "indicates a CCL may be reached in the foreseeable future, due to the speed of capability progress. In "
    "particular, they are meant to account for the possibility of models reaching a CCL before the next critical "
    "capability assessment cycle.")
ALERT_1_3_2 = (
    "For CCLs, we define “alert thresholds,” which may draw on evaluation results, expert assessments, and other "
    "sources of information; that are designed to flag when a CCL may be reached before a critical capability "
    "assessment is conducted again.")
CCA = (
    "Critical Capability Assessments: determine a model’s proximity to T/CCLs through the use of early warning "
    "evaluations and other sources of evidence.")
MCCA = (
    "Material Capability Change Assessments: indicate whether a critical capability assessment is required. These "
    "assessments are typically conducted upon the completion of new post-training runs on various checkpoints, and "
    "they are primarily aimed at determining whether updated versions of a model have developed material "
    "capability increases relative to the last checkpoint subject to a critical capability assessment. May also be "
    "used to assess whether a critical capability assessment is required of non-frontier AI models.")
MCI = (
    "Material Capability Increases: are meaningful new capabilities or material increases in model performance "
    "that we believe could materially undermine our justifications for a model’s level of risk being acceptable, "
    "for example, by reaching a CCL that the previous version of the model had not reached.")
DEPLOYMENT_MITIGATIONS = (
    "Deployment Mitigations: are safety measures we implement which are intended to counter the misuse or "
    "misaligned expression of critical capabilities in deployments. They may include safety post-training, "
    "input/output/chain-of-thought monitoring and analysis, account moderation, jailbreak detection and patching, "
    "user verification, and bug bounties.")
TWO_CATEGORIES = (
    "We have two categories of mitigations: security mitigations (such as preventing the exfiltration of model "
    "weights), and deployment mitigations (such as safety fine-tuning and monitoring and response) intended to "
    "counter the misuse or misaligned expression of critical capabilities in deployments.")
EXTERNAL = (
    "External Deployments: represent model releases to entities outside of Google. They can include both low-risk "
    "external deployments as well as general purpose releases to the broader public.")
SECURITY_MITIGATIONS_FIRST = (
    "Security Mitigations: are safety measures we implement which are intended to prevent the unauthorized "
    "modification or exfiltration of model weights by unauthorized actors.")
SECURITY_MITIGATIONS_REST = (
    "They may include identity and access management practices, and hardening interface-access to unreleased model "
    "parameters, among other measures. We communicate the level of security we consider appropriate to models "
    "which cross our thresholds using the RAND model weight security framework.")
RAND_LEVELS = (
    "RAND Security Levels: indicate security goals and principles relevant to frontier developers aiming to "
    "protect their model weights from various actors - with the strength and type of security measures differing "
    "for each category of actor. 14")
SECURITY_LEVELS_2_1_1 = (
    "We use security levels to indicate security goals/principles in line with the corresponding level in the RAND "
    "model weight security framework. 6")
FOOTNOTE_6 = (
    "6 In other words, “security level N ” indicates security controls and detections at a level generally aligned "
    "with RAND SL N . See https://www.rand.org/pubs/research_reports/RRA2849-1.html , pp 21-22. In aligning our "
    "security levels with RAND’s, we are referring to the security goals and principles in the RAND framework, "
    "rather than the benchmarks (i.e. concrete measures) also described in the RAND report.")
SL2_PLUS = (
    'We also define and recommend "Security Level 2+," which uses RAND Security Level 2 (SL2) as a baseline, with '
    "additional security measures designed to address risks from insider threats and well-resourced non-state "
    "external actors.")
FOOTNOTE_12 = (
    "12 This level may include mitigations aligned with SL 2+, plus additional mitigations designed to prevent "
    "unilateral access, harden infrastructure, and prevent data exfiltration.")
FOOTNOTE_13 = (
    "13 This level may include mitigations aligned with SL 2+ and 3, plus additional mitigations aimed to isolate "
    "model weights, enhanced data center security, further hardening of infrastructure and minimizing potential "
    "attack surface.")
RECOMMEND_2_2 = (
    "We recommend a security level for each CCL, which reflects our assessment of the minimum appropriate level of "
    "security the field of frontier AI should apply to models reaching each CCL.")
FOOTNOTE_8 = (
    "8 Here, and in other misuse T/CCLs, we intend this to mean relative to a baseline without generative AI.")
TIERED_3_2 = (
    "We set a Stealth and Situational Awareness TCL that indicates a baseline level of model capability above "
    "which misalignment risks may begin to arise. At this capability level we apply a proportionate set of "
    "mitigation and risk acceptance determination processes. ● We set ML R&D CCLs that indicate higher capability "
    "levels at which misalignment, misuse and structural risks are heightened and may reach a severe scale. At "
    "these capability levels we apply a stronger set of mitigations, and follow the risk acceptance process as "
    "detailed in the rest of the framework.")
ML_RD_CCLS_3_2_2 = (
    "We define ML R&D CCLs at capability levels at which misalignment, misuse and structural risks may reach a "
    "severe scale.")
DEEM_3_1_2 = (
    "In particular, we will deem deployment mitigations adequate if the evidence suggests that for the T/CCLs the "
    "model has reached, the increase in likelihood of harm from the proposed deployment has been reduced to an "
    "acceptable level.")
RRA_FIRST = (
    "Residual Risk Assessments: the process of evaluating the level of risk that remains after all planned "
    "mitigation strategies have been implemented.")
RRA_REST = (
    "This is part of the risk management process, following a critical capability assessment and the effect of "
    "mitigations. The residual risk should be brought within the acceptable levels, as determined by the T/CCLs as "
    "relevant.")
SAFETY_CASES_FIRST = (
    "Safety Cases: are an assessable argument showing how severe risks associated with a model's CCLs have been "
    "reduced to an acceptable level.")
SAFETY_CASES_REST = (
    "Residual risk assessments will be supplemented with a safety case when a model reaches a CCL, and inform a "
    "model’s risk acceptance determination. 15 For misuse risk, such an argument may be based, for example, on "
    "considerations such as the effectiveness of mitigations, the scope of the deployment, what capabilities and "
    "mitigations are available on other publicly available models, and the historical incidence and severity of "
    "related events.")


class Row(NamedTuple):
    term: str
    carrier: str
    block: str
    line: int
    location: str
    pieces: tuple


# row -> (defined term, carrier predicate, a rule or fact block that uses it, source line, section, passage pieces)
ROWS = {
    "x1": Row("Frontier AI Models / model / version", "frontier", "f2", 18, FRONTIER,
               (FRONTIER_GENERALITY, FRONTIER_VERSIONS)),
    "x2": Row("Frontier AI Models / model / version", "subsequent", "f4-check-d", 18, FRONTIER,
               (FRONTIER_VERSIONS,)),
    "x3": Row("Risk Domains", "concerns", "bridge-one-domain", 18, "Glossary, Risk Domains", (RISK_DOMAINS,)),
    "x4": Row("misuse risk", "misuse", "closure-ccl-kinds", 2, "footnote 2", (FOOTNOTE_2,)),
    "x5": Row("ML R&D and misalignment risk", "ml_rd_and_misalignment", "closure-ccl-kinds", 2, "footnote 3",
               (FOOTNOTE_3,)),
    "x7": Row("Critical Capability Levels (CCLs)", "critical", "closure-ccl-kinds", 18, "Glossary, Thresholds",
               (CCL_GLOSSARY,)),
    "x8": Row("CCLs", "critical", "closure-ccl-kinds", 4, "section 1.2", (CCL_1_2,)),
    "x9": Row("Tracked Capability Levels (TCLs)", "tracked", "closure-tcls", 18, "Glossary, Thresholds",
               (TCL_GLOSSARY,)),
    "x10": Row("TCLs", "tracked", "closure-tcls", 4, "section 1.2", (TCL_1_2,)),
    "x11": Row("alert thresholds", "approaches", "f6", 18, "Glossary, Thresholds", (ALERT_GLOSSARY,)),
    "x12": Row("alert thresholds", "approaches", "f6", 5, "section 1.3.2", (ALERT_1_3_2,)),
    "x13": Row("critical capability assessment", "reached", "f10-acc", 18, INHERENT,
               (CCA,)),
    "x14": Row("critical capability assessment", "further_assessed", "f4-further-r", 18, INHERENT,
               (CCA,)),
    "x15": Row("critical capability assessment", "further_need_checked", "f4-need-d", 18, INHERENT,
               (CCA,)),
    "x16": Row("material capability change assessments", "change_assessed", "f5", 19, "Glossary", (MCCA,)),
    "x17": Row("material capability change assessments", "assessed", "f2", 19, "Glossary", (MCCA,)),
    "x18": Row("material capability increases", "could_undermine_justification", "f4-check-d", 19, "Glossary",
               (MCI,)),
    "x19": Row("deployment mitigations", "mitigates", "f10-acc", 19, "Glossary, Risk Mitigation",
               (DEPLOYMENT_MITIGATIONS,)),
    "x20": Row("deployment mitigations", "harm_mitigated", "f9-dm", 19, "Glossary, Risk Mitigation",
               (DEPLOYMENT_MITIGATIONS,)),
    "x21": Row("deployment mitigations", "severe_harm_mitigated", "f10-dm-diff", 19, "Glossary, Risk Mitigation",
               (DEPLOYMENT_MITIGATIONS,)),
    "x22": Row("deployment mitigations", "significant_harm_mitigated", "f11-dm", 19, "Glossary, Risk Mitigation",
               (DEPLOYMENT_MITIGATIONS,)),
    "x23": Row("deployment mitigations", "residual_assessed", "f7-rra", 19, "Glossary, Risk Mitigation",
               (DEPLOYMENT_MITIGATIONS,)),
    "x24": Row("two categories of mitigations", "mitigates", "f10-acc", 6, "section 1.3.3", (TWO_CATEGORIES,)),
    "x25": Row("external deployments", "external", "activities-development", 19, "Glossary", (EXTERNAL,)),
    "x26": Row("security mitigations", "secured", "f10-sec", 19, "Glossary", (SECURITY_MITIGATIONS_REST,)),
    "x27": Row("security mitigations", "applies", "f10-acc", 19, "Glossary",
               (SECURITY_MITIGATIONS_FIRST, SECURITY_MITIGATIONS_REST)),
    "x28": Row("RAND Security Levels", "recommends", "f10-acc", 19, "Glossary (footnote mark 14)", (RAND_LEVELS,)),
    "x29": Row("security levels", "recommends", "f10-acc", 9, "section 2.1.1 (footnote mark 6)",
               (SECURITY_LEVELS_2_1_1,)),
    "x30": Row("security level N", "recommends", "f10-acc", 9, "footnote 6", (FOOTNOTE_6,)),
    "x35": Row("recommended security level", "recommends", "f10-acc", 11, "section 2.2", (RECOMMEND_2_2,)),
    "x36": Row("uplift relative to a baseline (misuse T/CCLs)", "misuse", "closure-ccl-kinds", 11, "footnote 8",
               (FOOTNOTE_8,)),
    "x37": Row("Stealth TCL / ML R&D CCLs", "ml_rd_and_misalignment", "closure-ccl-kinds", 14, "section 3.2",
               (TIERED_3_2,)),
    "x38": Row("ML R&D CCLs", "ml_rd_and_misalignment", "closure-ccl-kinds", 14, "section 3.2.2",
               (ML_RD_CCLS_3_2_2,)),
    "x39": Row("adequate deployment mitigations", GOV, "f13-p", 14, "section 3.1.2 step 2",
               (DEEM_3_1_2,)),
    "x40": Row("residual risk assessments", "residual_assessed", "f7-rra", 20, "Glossary", (RRA_REST,)),
    "x41": Row("residual risk assessments", "periodic_assessed", "f17-pra", 20, "Glossary", (RRA_FIRST, RRA_REST)),
    "x42": Row("residual risk assessments", "periodic_covers_internal", "f17-hri", 20, "Glossary",
               (RRA_FIRST, RRA_REST)),
    "x43": Row("residual risk assessments", "safety_case", "f7-sc", 20, "Glossary", (RRA_FIRST, RRA_REST)),
    "x44": Row("safety cases", "safety_case", "f7-sc", 20, "Glossary (footnote mark 15)", (SAFETY_CASES_REST,)),
    "x45": Row("safety cases", GOV, "f12-p", 20, "Glossary (footnote mark 15)",
               (SAFETY_CASES_FIRST, SAFETY_CASES_REST)),
    "x46": Row("safety cases", "material_safety_case_update", "f14", 20, "Glossary (footnote mark 15)",
               (SAFETY_CASES_FIRST, SAFETY_CASES_REST)),
}
# Dropped rows: already carried word for word in the `recommends` legend by fsf-repair-f6-sl2plus-1119.
DROPPED = {
    "x31": (9, "section 2.1.1", SL2_PLUS),
    "x33": (15, "footnote 12 (table 3.2.2.a)", FOOTNOTE_12),
    "x34": (15, "footnote 13 (table 3.2.2.a)", FOOTNOTE_13),
}


def _vocabulary():
    """usecases/safety-framework/vocabulary.py, loaded under its own name (usecases/eligibility has bare-name twins)."""
    spec = importlib.util.spec_from_file_location("defs_repair_fsf_vocabulary", HERE / "vocabulary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _committed():
    return json.loads((HERE / "environment.d1.json").read_text(encoding="utf-8"))


def _shown(key):
    """The legend of `key` as the reader is shown it (committed) and as vocabulary.py writes it."""
    return (_committed()["vocabulary"]["predicates"][key]["description"],
            _vocabulary().environment()["vocabulary"]["predicates"][key]["description"])


def _counted(key):
    """The meaning text the definitions counter reads from the literal strings of `key`'s vocabulary.py entry."""
    lines = (HERE / "vocabulary.py").read_text(encoding="utf-8").splitlines()
    return " ".join(meaning for meaning, _raw in counter._omit_legend_segments(counter.legend_raw(key, lines)))


@pytest.mark.parametrize("row", sorted(ROWS, key=lambda r: int(r[1:])))
def test_each_kept_definition_is_carried_word_for_word_in_its_legend(row):
    """The condition test: every piece of the row's source passage stands in the carrier's legend, shown and counted
    (fails on main at 941208a12d, where these legends lack them)."""
    r = ROWS[row]
    for piece in r.pieces:
        for legend in _shown(r.carrier):
            assert omit_norm(piece) in omit_norm(legend), (row, r.carrier, piece[:60])
        assert omit_norm(piece) in _counted(r.carrier), (row, r.carrier, piece[:60])


@pytest.mark.parametrize("row", sorted(ROWS, key=lambda r: int(r[1:])))
def test_each_carrier_is_a_predicate_its_rule_uses(row):
    """The audit's carrier guard: a legend counts only on a predicate the row's rule (or fact) block uses."""
    r = ROWS[row]
    blocks = {**counter.rule_blocks((HERE / "rules.d1.ve").read_text(encoding="utf-8")),
              **counter.rule_blocks((HERE / "facts.d1.ve").read_text(encoding="utf-8"))}
    assert r.carrier in counter.used_predicates(blocks[r.block][1], _committed()), (row, r.block)


def test_the_dropped_rows_are_already_carried():
    """x31, x33, x34 were dropped as carried word for word by fsf-repair-f6-sl2plus-1119; this keeps that true."""
    for row, (_line, _loc, passage) in DROPPED.items():
        for legend in _shown("recommends"):
            assert omit_norm(passage) in omit_norm(legend), row


@pytest.mark.parametrize("row", sorted([*ROWS, *DROPPED], key=lambda r: int(r[1:])))
def test_each_stored_passage_is_in_the_pinned_source_at_its_line(row):
    """With the pinned FSF text stored at its pin: each piece occurs byte for byte, once in the text, on its stated
    line; the pieces follow one another there (separated by one space, or by the full stop a piece leaves out); and the
    passage is whole: it starts at a sentence, list-entry or footnote start and ends at a full stop, with a footnote
    mark kept. Absent, it skips (it never downloads)."""
    lines = pinned_source("safety-framework").read_text(encoding="utf-8").split("\n")
    if row in ROWS:
        line, pieces = ROWS[row].line, ROWS[row].pieces
    else:
        line, _loc, passage = DROPPED[row]
        pieces = (passage,)
    text = lines[line - 1]
    for piece in pieces:
        assert text.count(piece) == 1 and sum(other.count(piece) for other in lines) == 1, (row, line, piece[:60])
    start = end = text.index(pieces[0])
    for piece in pieces:
        assert text[end:text.index(piece)] in ("", " ", ". "), (row, piece[:60])
        end = text.index(piece) + len(piece)
    assert start == 0 or re.search(r"(\. |● |: |\d |[a-z] )$", text[:start]), (row, text[start - 20:start])
    assert re.search(r"\.( \d+)?$", text[start:end]), row
