"""defs-repair-safety-framework-1119: each FSF source definition the audit filed stands, whole, in a shown, counted legend.

The definitions audit (manage-agents reviews/defs-carried-1119/rows-safety-framework-x.tsv, read at VE e53db4e8fc)
filed 44 P1 rows for the FSF document. Each row names a term a rule depends on, the predicate whose legend carries it
and the passage of the pinned source (FSF 3.1, fsf-3.1.txt: one PDF page per line) that defines it: the row's whole
quote, stored below in the source's own bytes with its line and section (`AUDIT_QUOTE_SHA256` ties each to the audit's
quote column). A definition is carried only when the WHOLE quote stands unbroken (METHOD amendment 3, the audit's
`carried.py`) both in what a reader is shown (environment.d1.json and vocabulary.py's output, after the project's quote
normalisation `omit_norm`: NFKC, curly quotes, case, whitespace) and in what the definitions counter counts
(tools/defs_carried_counter.py reads the literal strings of the entry: a computed or citation-led legend, or an escape
such as \\" that the literal keeps, is shown but not counted). Pieces that are each carried but split by other text do
not count. When the pinned text is stored at its pin, each quote must also be in it, at its line, byte for byte; the
test never downloads it and never skips (tests/pinned_source.py).

Rows x33 and x34 are DROPPED: fsf-repair-f6-sl2plus-1119 already carries them in the `recommends` legend. They are
checked here like the kept rows, shown AND counted (review F2). Row x31 was dropped on the same ground but was only
shown: its inner quotes were written \\" in the literal, which the counter keeps; they are now “ ” and x31 is kept.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import tokenize
from typing import NamedTuple

import pytest

from omission_rule import omit_norm
from tests.pinned_source import pinned_source
from tools import defs_carried_counter as counter

HERE = Path(__file__).resolve().parents[1] / "usecases" / "safety-framework"
GOV = "governance_found_acceptable_with_safety_case_where_ccl_reached"
INHERENT = "Glossary, Inherent Risk Assessment"
FRONTIER_SECTION = "Glossary, Frontier AI Models or Models"

# The source passages, in the bytes of fsf-3.1.txt (sha256 18e3375b…c53946, usecases/pinned_sources.json).
FRONTIER_GENERALITY = (
    "Frontier AI models’ agentic and reasoning-based general capabilities near or exceed those of other Google "
    "models.")
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


# A passage the source prints as two parts the merged rows had quoted apart; the row's quote is the whole run.
FRONTIER = f"{FRONTIER_GENERALITY} {FRONTIER_VERSIONS}"
SECURITY_MITIGATIONS = f"{SECURITY_MITIGATIONS_FIRST} {SECURITY_MITIGATIONS_REST}"
RRA = f"{RRA_FIRST} {RRA_REST}"
SAFETY_CASES = f"{SAFETY_CASES_FIRST} {SAFETY_CASES_REST}"


class Row(NamedTuple):
    term: str
    carrier: str
    block: str
    line: int
    location: str
    quote: str


# row -> (defined term, carrier predicate, a rule or fact block that uses it, source line, section, the row's whole
# quote). One quote per row: a check of its parts one by one cannot see text inserted between them (review F1).
ROWS = {
    "x1": Row("Frontier AI Models / model / version", "frontier", "f2", 18, FRONTIER_SECTION, FRONTIER),
    "x2": Row("Frontier AI Models / model / version", "subsequent", "f4-check-d", 18, FRONTIER_SECTION,
               FRONTIER_VERSIONS),
    "x3": Row("Risk Domains", "concerns", "bridge-one-domain", 18, "Glossary, Risk Domains", RISK_DOMAINS),
    "x4": Row("misuse risk", "misuse", "closure-ccl-kinds", 2, "footnote 2", FOOTNOTE_2),
    "x5": Row("ML R&D and misalignment risk", "ml_rd_and_misalignment", "closure-ccl-kinds", 2, "footnote 3",
               FOOTNOTE_3),
    "x7": Row("Critical Capability Levels (CCLs)", "critical", "closure-ccl-kinds", 18, "Glossary, Thresholds",
               CCL_GLOSSARY),
    "x8": Row("CCLs", "critical", "closure-ccl-kinds", 4, "section 1.2", CCL_1_2),
    "x9": Row("Tracked Capability Levels (TCLs)", "tracked", "closure-tcls", 18, "Glossary, Thresholds",
               TCL_GLOSSARY),
    "x10": Row("TCLs", "tracked", "closure-tcls", 4, "section 1.2", TCL_1_2),
    "x11": Row("alert thresholds", "approaches", "f6", 18, "Glossary, Thresholds", ALERT_GLOSSARY),
    "x12": Row("alert thresholds", "approaches", "f6", 5, "section 1.3.2", ALERT_1_3_2),
    "x13": Row("critical capability assessment", "reached", "f10-acc", 18, INHERENT, CCA),
    "x14": Row("critical capability assessment", "further_assessed", "f4-further-r", 18, INHERENT, CCA),
    "x15": Row("critical capability assessment", "further_need_checked", "f4-need-d", 18, INHERENT, CCA),
    "x16": Row("material capability change assessments", "change_assessed", "f5", 19, "Glossary", MCCA),
    "x17": Row("material capability change assessments", "assessed", "f2", 19, "Glossary", MCCA),
    "x18": Row("material capability increases", "could_undermine_justification", "f4-check-d", 19, "Glossary", MCI),
    "x19": Row("deployment mitigations", "mitigates", "f10-acc", 19, "Glossary, Risk Mitigation",
               DEPLOYMENT_MITIGATIONS),
    "x20": Row("deployment mitigations", "harm_mitigated", "f9-dm", 19, "Glossary, Risk Mitigation",
               DEPLOYMENT_MITIGATIONS),
    "x21": Row("deployment mitigations", "severe_harm_mitigated", "f10-dm-diff", 19, "Glossary, Risk Mitigation",
               DEPLOYMENT_MITIGATIONS),
    "x22": Row("deployment mitigations", "significant_harm_mitigated", "f11-dm", 19, "Glossary, Risk Mitigation",
               DEPLOYMENT_MITIGATIONS),
    "x23": Row("deployment mitigations", "residual_assessed", "f7-rra", 19, "Glossary, Risk Mitigation",
               DEPLOYMENT_MITIGATIONS),
    "x24": Row("two categories of mitigations", "mitigates", "f10-acc", 6, "section 1.3.3", TWO_CATEGORIES),
    "x25": Row("external deployments", "external", "activities-development", 19, "Glossary", EXTERNAL),
    "x26": Row("security mitigations", "secured", "f10-sec", 19, "Glossary", SECURITY_MITIGATIONS_REST),
    "x27": Row("security mitigations", "applies", "f10-acc", 19, "Glossary", SECURITY_MITIGATIONS),
    "x28": Row("RAND Security Levels", "recommends", "f10-acc", 19, "Glossary (footnote mark 14)", RAND_LEVELS),
    "x29": Row("security levels", "recommends", "f10-acc", 9, "section 2.1.1 (footnote mark 6)",
               SECURITY_LEVELS_2_1_1),
    "x30": Row("security level N", "recommends", "f10-acc", 9, "footnote 6", FOOTNOTE_6),
    "x31": Row("Security Level 2+", "recommends", "f10-acc", 9, "section 2.1.1", SL2_PLUS),
    "x33": Row("security level 3 (footnote 12)", "recommends", "f10-acc", 15, "footnote 12 (table 3.2.2.a)",
               FOOTNOTE_12),
    "x34": Row("security level 4 (footnote 13)", "recommends", "f10-acc", 15, "footnote 13 (table 3.2.2.a)",
               FOOTNOTE_13),
    "x35": Row("recommended security level", "recommends", "f10-acc", 11, "section 2.2", RECOMMEND_2_2),
    "x36": Row("uplift relative to a baseline (misuse T/CCLs)", "misuse", "closure-ccl-kinds", 11, "footnote 8",
               FOOTNOTE_8),
    "x37": Row("Stealth TCL / ML R&D CCLs", "ml_rd_and_misalignment", "closure-ccl-kinds", 14, "section 3.2",
               TIERED_3_2),
    "x38": Row("ML R&D CCLs", "ml_rd_and_misalignment", "closure-ccl-kinds", 14, "section 3.2.2", ML_RD_CCLS_3_2_2),
    "x39": Row("adequate deployment mitigations", GOV, "f13-p", 14, "section 3.1.2 step 2", DEEM_3_1_2),
    "x40": Row("residual risk assessments", "residual_assessed", "f7-rra", 20, "Glossary", RRA_REST),
    "x41": Row("residual risk assessments", "periodic_assessed", "f17-pra", 20, "Glossary", RRA),
    "x42": Row("residual risk assessments", "periodic_covers_internal", "f17-hri", 20, "Glossary", RRA),
    "x43": Row("residual risk assessments", "safety_case", "f7-sc", 20, "Glossary", RRA),
    "x44": Row("safety cases", "safety_case", "f7-sc", 20, "Glossary (footnote mark 15)", SAFETY_CASES_REST),
    "x45": Row("safety cases", GOV, "f12-p", 20, "Glossary (footnote mark 15)", SAFETY_CASES),
    "x46": Row("safety cases", "material_safety_case_update", "f14", 20, "Glossary (footnote mark 15)", SAFETY_CASES),
}
# Rows this item does not edit: fsf-repair-f6-sl2plus-1119 already carries them, shown and counted. The condition test
# checks them like every other row, so a drop that is only shown fails here (review F2).
DROPPED = ("x33", "x34")

# sha256 (UTF-8) of each row's `quote` cell in the audit TSV (manage-agents reviews/defs-carried-1119/
# rows-safety-framework-x.tsv): the stored quote is the audit's whole quote, so a passage cut short at a sentence end,
# or one part of a split quote, fails here and not only in review (review note C1).
AUDIT_QUOTE_SHA256 = {
    "x1": "e3beb7fd70d314f81d37202f19429e1f8481f794b351eaae8d1ee6262b96f06f",
    "x2": "dde4f9b83f83bd45dfafcf07c30ac4dca1bb057f8143fc848944c9d25853fd26",
    "x3": "09ee382fb1e95566503d1f02a68ce036503f19c63142a43783bfdf10f0e051fe",
    "x4": "b1e5df599836ac2d1b63802a4ba41c535a8db87738919c20ab0c0e692a07de85",
    "x5": "d7eca639f80c4f761dc373df0847c2cc617ca8fbdb07a00b0794680ef6d4cd97",
    "x7": "c08cadffae6a25c58d85f684650d32278db0ae7e74a8ecadc203da2d3ad15f1d",
    "x8": "f109605983633f675df85ca35b730d4aa3322ce0dc16abe0380114655a847b67",
    "x9": "ad76684653620daec0cab97a5f5778fe8360bba3e9ef024458654898c88ee212",
    "x10": "3a8fbb6c6d1731832c302d8da135ee9b9c7dff325b4d7dc04677c4dd0bf4edec",
    "x11": "a2343696c04cabd1cf9a73b357cd7827605b6b40644fa7978d12b91e05a4c8c1",
    "x12": "26b62d7855f0a300bc425ccab85fa3a20f57ca31f32aa5437747e0d49c3460e0",
    "x13": "6b0dc4b24f3720463cd13378f065908c5df0a077cce028950bb3611ab48e06f9",
    "x14": "6b0dc4b24f3720463cd13378f065908c5df0a077cce028950bb3611ab48e06f9",
    "x15": "6b0dc4b24f3720463cd13378f065908c5df0a077cce028950bb3611ab48e06f9",
    "x16": "89db60ecd1fdd76c22a27d73e22e343c59b011aed99bf69168a57ad91002d933",
    "x17": "89db60ecd1fdd76c22a27d73e22e343c59b011aed99bf69168a57ad91002d933",
    "x18": "2bbf3aae9597301097fd331a705aa0d67bf71e4514e195f0803c7d20cd22ab2a",
    "x19": "702946ab980918b830c7580c90e685fbb9432cfa68c85be33f436021fb97894e",
    "x20": "702946ab980918b830c7580c90e685fbb9432cfa68c85be33f436021fb97894e",
    "x21": "702946ab980918b830c7580c90e685fbb9432cfa68c85be33f436021fb97894e",
    "x22": "702946ab980918b830c7580c90e685fbb9432cfa68c85be33f436021fb97894e",
    "x23": "702946ab980918b830c7580c90e685fbb9432cfa68c85be33f436021fb97894e",
    "x24": "6144d5e6fdd82f71a31b1109074e9065002c7d417e8d69c925045d5076f865ce",
    "x25": "0337b5834d02844ba59fc708645ed1edcff89388fe8ca8298285cc0a43c6c26b",
    "x26": "1cec90585d38bf8068b4eeb159863d41490d32f405ef989ac0a9f210a5e500bd",
    "x27": "0ffbabcae67720f77b844292e17797722a1d3d3a960ac600cffde5fe3ada3b7a",
    "x28": "c6ebb9eb02f750c82fdea4778b5fdd64443d67ac4f917f970031497bde03f1f4",
    "x29": "bd67bdac6e30ec640287cc581b9f7fadd48dc266307034ee5be6a5a7b2a78e7d",
    "x30": "173ac4a600ce09533eb7cf907402a372661894356772d5deafbca8a14650b802",
    "x31": "bbe6ac60fc49ffbc7096ef22dac506bc7a839a9b3a8cc928721313a1763e128c",
    "x33": "9f70be8f91f1e4dfd138e211bf2d8bf854fcd5d0fa91148ec4a020bddf622f44",
    "x34": "3e812709f15829a293fc2a62afd10bc4d0a86b1ff24d481d2b7d0792208baf27",
    "x35": "c64bbe8af1e5911b48af97aa550c3aa2f86c786f2c4eb635e8bfeb81ac39587d",
    "x36": "6bfbe24a9241a1dc5e670807e25ae353a49708e4b6c7a011a2cd57c27dfeec51",
    "x37": "4746391f87aea06e7c049dd1296215507e34b5b123f4d2f5dc599d84c51e9e33",
    "x38": "0faa6616f792403e67fe584b1fb5469b23fe538ea5658b527cca1e14d960280b",
    "x39": "2ed79946bb9353116c5213a27bf752e269067f9fc023a593bd4c5b1a7fc24362",
    "x40": "3a68e63c28e76ef74fa6c34b3d75fd86cafcf9731c81ee3a37eee47e95ea4c50",
    "x41": "119bfc4cc17bd38bba1ca3df5e3c03c9263db863262d8fec828019f2047b9332",
    "x42": "119bfc4cc17bd38bba1ca3df5e3c03c9263db863262d8fec828019f2047b9332",
    "x43": "119bfc4cc17bd38bba1ca3df5e3c03c9263db863262d8fec828019f2047b9332",
    "x44": "14afe6d026621e381172360897e7fa5a3bc00354f831b910e0c9b9cd61c442a5",
    "x45": "032f75ec7d17b4bd225a7ec3e8e2f6c28dfc5a86b739b280ed5d46f925f06879",
    "x46": "032f75ec7d17b4bd225a7ec3e8e2f6c28dfc5a86b739b280ed5d46f925f06879",
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


def _counted(key, path=HERE / "vocabulary.py"):
    """The meaning text the definitions counter reads from the literal strings of `key`'s vocabulary.py entry."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return " ".join(meaning for meaning, _raw in counter._omit_legend_segments(counter.legend_raw(key, lines)))


def _as_counted(quote):
    """A quote as the counter's meaning text holds it: the counter's own reading (citations cut, its omit_norm) of a
    one-string legend holding the quote, its straight quotes written curly as a legend writes them."""
    [(meaning, _raw)] = counter._omit_legend_segments(['"key": _base([],', '"' + quote.replace('"', "“") + '")'])
    return meaning


def _carried(quote, key, path=HERE / "vocabulary.py"):
    """(shown, counted): the whole quote stands unbroken in the shown legend and in the counted meaning text."""
    shown = all(omit_norm(quote) in omit_norm(legend) for legend in _shown(key))
    return shown, _as_counted(quote) in _counted(key, path)


@pytest.mark.parametrize("row", sorted(ROWS, key=lambda r: int(r[1:])))
def test_each_definition_is_carried_whole_in_its_legend(row):
    """The condition test: the row's whole quote stands unbroken in the carrier's legend, shown and counted (fails on
    main at 941208a12d for the 42 kept rows; at 610eafced7 for x1 and x45, split by other text, and x31, not counted)."""
    r = ROWS[row]
    assert _carried(r.quote, r.carrier) == (True, True), (row, r.carrier, r.quote[:60])


def test_a_split_quote_or_a_kept_escape_is_not_carried(tmp_path):
    """The condition test can fail on each review finding's shape: a quote split by other text (F1, x1 at 610eafced7)
    and a quote whose inner quotes the literal writes as \\" (F2, x31 at 610eafced7) are not carried, while each part
    of the split quote is."""
    source = (HERE / "vocabulary.py").read_text(encoding="utf-8")
    split = source.replace('Google models. There may "\n', 'Google models\\")"\n". The Glossary entry goes on: '
                           '\\"There may "\n', 1)
    escaped = source.replace('"“Security Level 2+,” which', '"\\"Security Level 2+,\\" which', 1)
    assert split != source and escaped != source
    for text, row in ((split, "x1"), (escaped, "x31")):
        path = tmp_path / f"{row}.py"
        path.write_text(text, encoding="utf-8")
        assert _carried(ROWS[row].quote, ROWS[row].carrier, path)[1] is False, row
    path = tmp_path / "x1.py"
    assert all(_as_counted(part) in _counted("frontier", path) for part in (FRONTIER_GENERALITY[:-1], FRONTIER_VERSIONS))


@pytest.mark.parametrize("row", sorted(ROWS, key=lambda r: int(r[1:])))
def test_each_carrier_is_a_predicate_its_rule_uses(row):
    """The audit's carrier guard: a legend counts only on a predicate the row's rule (or fact) block uses."""
    r = ROWS[row]
    blocks = {**counter.rule_blocks((HERE / "rules.d1.ve").read_text(encoding="utf-8")),
              **counter.rule_blocks((HERE / "facts.d1.ve").read_text(encoding="utf-8"))}
    assert r.carrier in counter.used_predicates(blocks[r.block][1], _committed()), (row, r.block)


def test_each_stored_quote_is_the_audit_rows_whole_quote():
    """Every P1 row of the audit is here, once, and its stored quote is the audit's quote byte for byte."""
    assert sorted(AUDIT_QUOTE_SHA256) == sorted(ROWS) and set(DROPPED) <= set(ROWS)
    assert {row: hashlib.sha256(r.quote.encode("utf-8")).hexdigest() for row, r in ROWS.items()} == AUDIT_QUOTE_SHA256


@pytest.mark.parametrize("row", sorted(ROWS, key=lambda r: int(r[1:])))
def test_each_stored_quote_is_in_the_pinned_source_at_its_line(row):
    """With the pinned FSF text stored at its pin: the row's whole quote occurs byte for byte, once in the text, on its
    stated line; it starts at a sentence, list-entry or footnote start and ends at a full stop, with a footnote mark
    kept. Absent and not required (VE_REQUIRE_PINNED_SOURCES unset), only the stored quote's own end is checked; the
    test never downloads and never skips (the fsf-repair-f3-safetycase-1119 pattern)."""
    r = ROWS[row]
    assert re.search(r"\.( \d+)?$", r.quote), row
    path = pinned_source("safety-framework", skip=False)
    if path is None:
        return
    lines = path.read_text(encoding="utf-8").split("\n")
    text = lines[r.line - 1]
    assert text.count(r.quote) == 1 and sum(other.count(r.quote) for other in lines) == 1, (row, r.line)
    start = text.index(r.quote)
    assert start == 0 or re.search(r"(\. |● |: |\d |[a-z] )$", text[:start]), (row, text[start - 20:start])


def _escaped_quote_faults(raw):
    """Where an escaped quote (\\") of one run of string literals opens while a quoted passage is already open, closes
    while none is, or another escape sits inside an open passage: the counter keeps every escape, so such a passage is
    shown but not counted. An escaped quote opens after a space, a parenthesis or the run's start and before text."""
    faults, inside = [], False
    for m in re.finditer(r"\\(.)", raw):
        if m.group(1) != '"':
            if inside:
                faults.append(m.start())
            continue
        before = raw[m.start() - 1] if m.start() else " "
        after = raw[m.end()] if m.end() < len(raw) else " "
        opening = before in " (" and not after.isspace() and after not in ".,;:)"
        if opening == inside:
            faults.append(m.start())
        inside = opening
    return faults


def _literal_runs(text):
    """The raw contents of each run of adjacent plain string literals of a Python source (tokenize, not a regex):
    implicit concatenation joined, as the counter joins them; any other token ends a run."""
    runs, run = [], []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.STRING and tok.string[:1] in "\"'" and not tok.string.startswith(('"""', "'''")):
            run.append(tok.string[1:-1])
        elif tok.type not in (tokenize.NL, tokenize.COMMENT):
            if run:
                runs.append("".join(run))
            run = []
    return runs + (["".join(run)] if run else [])


@pytest.mark.parametrize("path", sorted(HERE.parent.glob("*/*vocabulary.py")), ids=lambda p: p.parent.name)
def test_no_quoted_passage_holds_an_escape_the_counter_keeps(path):
    """The class of review F2, over every use case's vocabulary: inside a quoted source passage, inner quotes are
    curly (“ ”), never \\", and no other escape stands, so what the counter counts is what the reader is shown."""
    found = [(run[:60], run[p - 30:p + 30]) for run in _literal_runs(path.read_text(encoding="utf-8"))
             for p in _escaped_quote_faults(run)]
    assert found == []


def test_the_escape_guard_finds_the_x31_shape():
    """The guard can fail: the `recommends` literal as 610eafced7 wrote it is flagged; its fix, a quote that closes
    before a citation, a placeholder quote and a curly-delimited passage are not."""
    assert _escaped_quote_faults(r'(2.1.1): \"We also define and recommend \"Security Level 2+,\" which uses '
                                 r'RAND Security Level 2 (SL2) as a baseline.\" Security level 3') != []
    assert _escaped_quote_faults(r'a \"quoted \n passage\" b') != []
    for ok in (r'(2.1.1): \"We also define and recommend “Security Level 2+,” which uses a baseline.\" Security',
               r'(5.1: \"{REVIEW_PROCESS}\")', r'it: \"A sentence.\" (the 15 is the mark)', r'“Where”'):
        assert _escaped_quote_faults(ok) == [], ok
