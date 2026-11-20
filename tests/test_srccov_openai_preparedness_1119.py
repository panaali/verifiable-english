"""srccov-openai-preparedness-1119: the PF legends carry their source text, and twelve no-rule units are recorded.

The condition test of the source-coverage item for openai-preparedness (map reviews/source-coverage-1119, rows
srccov-openai-preparedness-{1-6,15-22,29,30}-1119 and the out-of-scope-unrecorded units). Two claims:

* Carries. Each entry of CARRIES is one passage of the pinned PF v2 text (tests/pinned_source.py), located by its
  first and last words (after an anchor heading where the passage also occurs earlier in 4.2). Under the case's own
  quote normalisation (source/quote_evidence.py `plain`: page numbers inside sentences, line-break hyphens,
  whitespace and quote styles ignored) it must equal one whole “…” quotation of the named legend in
  environment.d1.json, the vocabulary the reader is shown (tests/test_safetyfw_usecases.py checks it is
  pf_vocabulary.py's output), and it must lie inside its source unit's byte span. Without the source, the legend
  must still hold a quotation that starts and ends with the entry's words.
* Records. Each unit of RECORDS is a spans.json unit at LABELLED with kind exposition, placed by a `label` entry of
  build_document.py PLACEMENTS; together they cover the source unit's text (a change-log item's leading number "N. "
  excepted where it sits in the unit before, which also holds other text).

Both fail on main at 09bea0972d, where these legends lack the quotations and these units are UNFORMALISED.
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
B, Q = MODULES["build_document"], MODULES["quote_evidence"]
ANCHORS = {"": "", "C.1": "C.1 Safeguards against malicious users Several",
           "C.2": "C.2 Safeguards against a misaligned model In addition"}

# (source unit, its byte span in the pinned text, vocabulary section, legend key, first words, last words, anchor)
CARRIES = (
    ('S0005', (716, 889), 'constants', 'biological_and_chemical', 'Biological and Chemical capabilities that', 'chemical weapons.', ''),
    ('S0064', (13336, 13820), 'constants', 'biological_and_chemical', 'The ability of an AI model to accelerate and expand access', 'assistance with laboratory work.', ''),
    ('S0006', (890, 1058), 'constants', 'cybersecurity', 'Cybersecurity capabilities that', 'vulnerability exploitation.', ''),
    ('S0071', (15162, 15375), 'constants', 'cybersecurity', 'The ability of an AI model to assist in the development', 'cyberdefense and cyberoffense.', ''),
    ('S0007', (1059, 1221), 'constants', 'ai_self_improvement', 'AI Self-improvement capabilities that', 'human control of AI systems.', ''),
    ('S0083', (17475, 17739), 'constants', 'ai_self_improvement', 'The ability of an AI system to accelerate AI research', 'own capability.', ''),
    ('S0065', (13821, 14105), 'constants', 'biological_and_chemical_high', 'The model can pro- vide meaningful', 'logical or chemical threats.', ''),
    ('S0066', (14106, 14256), 'constants', 'biological_and_chemical_high', 'Significantly increased like- lihood', 'reference-class threats.', ''),
    ('S0068', (14328, 14769), 'constants', 'biological_and_chemical_critical', 'The model can en- able an expert', 'without human inter- vention.', ''),
    ('S0069', (14770, 15038), 'constants', 'biological_and_chemical_critical', 'Proliferating the ability to create a novel threat vector', 'few available societal safeguards.', ''),
    ('S0072', (15376, 15632), 'constants', 'cybersecurity_high', 'The model removes existing bottlenecks', 'operationally relevant vulnerabilities.', ''),
    ('S0073', (15633, 15822), 'constants', 'cybersecurity_high', 'Removing bottlenecks limit- ing', 'volume of existing cyberattacks.', ''),
    ('S0074', (15823, 16099), 'constants', 'cybersecurity_high', 'In conjunction with a Long- range Autonomy capability', 'mitigate all other risks.', ''),
    ('S0080', (16773, 17106), 'constants', 'cybersecurity_critical', 'A tool-augmented model can identify', 'given only a high level desired goal.', ''),
    ('S0081', (17107, 17290), 'constants', 'cybersecurity_critical', 'Finding and executing end- to-end exploits', 'OpenAI in- frastructure.', ''),
    ('S0082', (17291, 17474), 'constants', 'cybersecurity_critical', 'Novel cyber operations, e.g.,', 'unpredictable and scarce.', ''),
    ('S0084', (17740, 17925), 'constants', 'ai_self_improvement_high', 'The model’s impact is equivalent to giving every OpenAI researcher', '2024 baseline.', ''),
    ('S0085', (17926, 18001), 'constants', 'ai_self_improvement_high', 'This milestone suggests AI self-improvement', 'beginning to accelerate.', ''),
    ('S0087', (18272, 18749), 'constants', 'ai_self_improvement_critical', 'The model is ca- pable of recursively self improving', 'for several months.', ''),
    ('S0088', (18750, 19042), 'constants', 'ai_self_improvement_critical', 'A major acceleration in the rate of AI R&D', 'human control of the AI system itself.', ''),
    ('S0047', (10064, 10305), 'predicates', 'plausible', 'It must be possible to identify a causal pathway', 'enabled by frontier AI.', ''),
    ('S0048', (10306, 10449), 'predicates', 'measurable', 'We can construct or adopt capability evaluations', 'potential for the severe harm.', ''),
    ('S0049', (10450, 10783), 'predicates', 'severe', 'There is a plausible threat model within the capability area', 'would create severe harm.', ''),
    ('S0049', (10450, 10783), 'predicates', 'net_new', 'The outcome cannot currently be realized', 'without access to frontier AI.', ''),
    ('S0050', (10784, 10964), 'predicates', 'irremediable', 'The outcome is such that once realized', 'feasible measures to remediate.', ''),
    ('S0097', (20483, 20921), 'predicates', 'lra_found', 'ability for a model to exe- cute a long-horizon', 'attacks when needed)', ''),
    ('S0099', (21097, 21306), 'predicates', 'sandbagging_found', 'ability and propensity to respond to safety or capability', 'validity of such evaluations.', ''),
    ('S0100', (21307, 21817), 'predicates', 'ara_found', 'ability to survive, replicate', 'tracked in other Tracked Categories.', ''),
    ('S0101', (21818, 22147), 'predicates', 'undermining_found', 'ability and propensity for the model to act to undermine', 'in safeguards code, etc.', ''),
    ('S0102', (22148, 22543), 'predicates', 'nuclear_found', 'ability to meaningfully counterfactually enable', 'while remaining undetected.', ''),
    ('S0015', (2346, 2498), 'predicates', 'sufficient_safeguards', 'By “severe harm” in this document', 'of economic damage.', ''),
    ('S0046', (9883, 10063), 'sorts', 'category', 'Tracked Categories are those capabilities which we track most closely', 'threshold level is crossed.', ''),
    ('S0055', (11899, 12010), 'predicates', 'high', 'High capability thresholds mean capabilities that significantly increase existing risk vectors for severe harm.', 'severe harm.', ''),
    ('S0235', (44531, 44674), 'predicates', 'high', 'High capability thresholds mean capabilities that significantly increase existing risk vectors for severe harm under', 'relevant threat model.', ''),
    ('S0057', (12261, 12418), 'predicates', 'critical', 'Critical capability thresholds mean capabilities that present a meaningful risk of a qualitatively new threat vector for severe harm with no ready precedent.', 'no ready precedent.', ''),
    ('S0236', (44675, 44864), 'predicates', 'critical', 'Critical capability thresholds mean capabilities that present a meaningful risk of a qualitatively new threat vector for severe harm with no ready precedent under', 'relevant threat model.', ''),
    ('S0012', (1816, 2050), 'predicates', 'research_category_review', 'These are areas of capability that could pose risks of severe harm', 'capability elicitation techniques.', ''),
    ('S0052', (11064, 11363), 'predicates', 'research_category_review', 'Research Categories are capabilities that, while they do not meet', 'to Tracked Categories).', ''),
    ('S0090', (19445, 19752), 'predicates', 'research_category_review', 'These capabilities either need more research and threat modeling', 'existing Tracked Category risks.', ''),
    ('S0243', (45805, 45967), 'predicates', 'research_category_review', 'Introduce Research Categories', 'additional work is needed now.', ''),
    ('S0245', (46230, 46370), 'predicates', 'research_category_review', 'These include Long-range Autonomy, Sandbagging', 'Nuclear and Radiological.', ''),
    ('S0242', (45727, 45804), 'predicates', 'research_category_review', 'We are moving Nuclear and Radiological capabilities into Research Categories.', 'Research Categories.', ''),
    ('S0135', (28927, 29153), 'predicates', 'covered', 'The Preparedness Framework applies to any new or updated deployment', 'existing Safeguards Report.', ''),
    ('S0136', (29154, 29195), 'predicates', 'covered', 'Examples of such covered deployments are:', 'deployments are:', ''),
    ('S0137', (29196, 29285), 'predicates', 'covered', 'every frontier model (e.g., OpenAI o1 or OpenAI o3)', 'deploy externally', ''),
    ('S0138', (29286, 29432), 'predicates', 'covered', 'any agentic system (including significant agents deployed only internally)', 'capability frontier', ''),
    ('S0139', (29433, 29682), 'predicates', 'covered', 'any significant change in the deployment conditions of an existing model', 'no longer reasonably applicable', ''),
    ('S0140', (29683, 29781), 'predicates', 'covered', 'incremental updates or distilled models with unexpectedly significant increases', 'increases in capability.', ''),
    ('S0127', (27289, 27430), 'predicates', 'evaluations_before_deployment', 'Scalable Evaluations: automated evaluations designed', 'has been crossed.', ''),
    ('S0128', (27431, 27627), 'predicates', 'evaluations_before_deployment', 'Scalable evaluations have associated “indicative thresholds,”', 'reached a capability threshold.', ''),
    ('S0129', (27628, 27783), 'predicates', 'evaluations_before_deployment', 'Deep Dives: designed to provide additional evidence', 'has been crossed.', ''),
    ('S0247', (46630, 46860), 'predicates', 'evaluations_before_deployment', 'We also define “scalable evaluations,”', 'validate the scalable evaluations.', ''),
    ('S0145', (30483, 30771), 'predicates', 'reached', 'The determination that a threshold has been reached is informed', 'robustness of evaluation results.', ''),
    ('S0287', (52847, 52964), 'predicates', 'misuse_safeguards', 'Safeguards should sufficiently minimize the risk of severe harm associated with misuse', 'model’s capabilities.', 'C.1'),
    ('S0288', (52965, 53121), 'predicates', 'misuse_safeguards', 'This can be done by establishing that all plausible known vectors', 'the following claims:', 'C.1'),
    ('S0289', (53122, 53378), 'predicates', 'misuse_safeguards', 'Robustness: Users cannot use the model', 'circumvent those refusals.', 'C.1'),
    ('S0290', (53379, 53682), 'predicates', 'misuse_safeguards', 'Usage Monitoring: If a model does not refuse', 'acceptable time frame.', 'C.1'),
    ('S0291', (53683, 53843), 'predicates', 'misuse_safeguards', 'Trust-based Access: The actors who gain access', 'under our threat model.', 'C.1'),
    ('S0175', (34945, 35228), 'predicates', 'misuse_safeguards', 'Robustness: Malicious users cannot use the model', 'circumvent those refusals.', ''),
    ('S0304', (55454, 55570), 'predicates', 'misuse_safeguards', 'Blocking access for users and organizations that violate', 'potential permanent bans', 'C.1'),
    ('S0314', (56582, 57025), 'predicates', 'alignment_safeguards', 'In addition to human misuse, several of the Tracked Category capabilities', 'subversion by an adversary.', 'C.2'),
    ('S0316', (57180, 57336), 'predicates', 'alignment_safeguards', 'This can be done by establishing that all plausible known vectors', 'the following claims:', 'C.2'),
    ('S0321', (58065, 58290), 'predicates', 'alignment_safeguards', 'System Architecture: The model can’t take actions', 'restricted permissions.', 'C.2'),
    ('S0322', (58291, 58556), 'predicates', 'alignment_safeguards', 'These misalignment claims may be further complemented', 'another model’s capabilities.', 'C.2'),
    ('S0330', (59395, 59502), 'predicates', 'alignment_safeguards', 'Evi- dence of taking harmful actions', 'dence of misalignment', 'C.2'),
    ('S0337', (60045, 60252), 'predicates', 'alignment_safeguards', 'Large scale usage or testing in realistic', 'avoiding harm).', 'C.2'),
    ('S0338', (60253, 60353), 'predicates', 'alignment_safeguards', 'Examples against would include trying to escape a container', 'appease them, etc.', 'C.2'),
    ('S0344', (60846, 61044), 'predicates', 'alignment_safeguards', 'Red-teamers can train an arbitrarily', 'high recall rate', 'C.2'),
    ('S0352', (61655, 62111), 'predicates', 'security_practices', 'Robust security practices and controls are essential', 'High capability thresholds.', ''),
    ('S0353', (62112, 62274), 'predicates', 'security_practices', 'Our security approach integrates industry best practices', 'frontier AI technologies.', ''),
    ('S0354', (62275, 62456), 'predicates', 'security_practices', 'Our security practices are designed to protect', 'and FedRAMP .', ''),
    ('S0355', (62457, 62639), 'predicates', 'security_practices', 'While nascent, AI- specific security standards', 'securing AI systems.', ''),
    ('S0356', (62640, 62766), 'predicates', 'security_practices', 'This may include efforts emerging from the Cloud Security Alliance', 'AI updates.', ''),
    ('S0357', (62767, 62834), 'predicates', 'security_practices', 'We will require the following practices for High capability models:', 'capability models:', ''),
    ('S0358', (62835, 63045), 'predicates', 'security_practices', 'Security Threat Modeling and Risk Management', 'posed by adversaries.', ''),
    ('S0359', (63046, 63307), 'predicates', 'security_practices', 'These models address both external and internal threats', 'regularly reviewed and updated.', ''),
    ('S0360', (63308, 63616), 'predicates', 'security_practices', 'This includes updating the Security framework', 'to further reduce risk.', ''),
    ('S0361', (63617, 63748), 'predicates', 'security_practices', 'Internal and external assessments to validate these controls', 'provided to OpenAI leadership.', ''),
    ('S0362', (63749, 64209), 'predicates', 'security_practices', 'Defense in Depth – Layered Security Architecture', 'networks, and endpoints.', ''),
    ('S0363', (64210, 64352), 'predicates', 'security_practices', 'Leverage hardware-backed security', 'performing operations.', ''),
    ('S0364', (64353, 64598), 'predicates', 'security_practices', 'Access Management – Principle of Least Privilege', 'separation of duties.', ''),
    ('S0365', (64599, 64651), 'predicates', 'security_practices', 'Ensure all access is regularly audited and reviewed.', 'audited and reviewed.', ''),
    ('S0366', (64652, 65001), 'predicates', 'security_practices', 'Identity and Device Management: Employees must authenticate', 'meeting security baselines.', ''),
    ('S0367', (65002, 65078), 'predicates', 'security_practices', 'Access must be logged and reviewed for detection', 'investigative purposes.', ''),
    ('S0368', (65079, 65262), 'predicates', 'security_practices', 'Secure Development and Supply Chain – Secure Development Lifecycle', 'in engineering processes.', ''),
    ('S0369', (65263, 65599), 'predicates', 'security_practices', 'Apply security reviews and validation to higher-sensitivity', 'approved before deployment.', ''),
    ('S0370', (65600, 65683), 'predicates', 'security_practices', 'Changes to critical infrastructure should undergo multi-person', 'approval and review.', ''),
    ('S0371', (65684, 66055), 'predicates', 'security_practices', 'This process should include maintaining comprehensive records', 'revert to previous states.', ''),
    ('S0371', (65684, 66055), 'predicates', 'security_practices', '– Software Supply Chain Integrity', 'and software libraries.', ''),
    ('S0372', (66056, 66692), 'predicates', 'security_practices', 'Operational Security – Monitoring and Incident Response', 'and emerging threats.', ''),
    ('S0373', (66693, 66773), 'predicates', 'security_practices', 'Encourage reporting of good-faith security research', 'bug bounty programs.', ''),
    ('S0374', (66774, 67414), 'predicates', 'security_practices', 'Auditing and Transparency – Independent Security Audits', 'risk management programs.', ''),
)

# (source unit, the byte span its record must cover, spans.json units, the source text's first words)
RECORDS = (
    ("S0209", (40601, 40646), ("p13-u219",), "• Clear internal decision-making practices."),
    ("S0211", (40747, 40773), ("p13-u221",), "• Internal Transparency."),
    ("S0230", (43794, 43860), ("p15-u242",), "Clarify the relationship among capabilities"),
    ("S0234", (44452, 44530), ("p15-u246",), "Define how High and Critical capability thresholds"),
    ("S0240", (45248, 45401), ("p15-u252",), "Update the Tracked Categories of frontier capability"),
    ("S0248", (46864, 46907), ("p15-u260",), "Provide risk-specific safeguard guidelines."),
    ("S0252", (47442, 47680), ("p15-u264",), "Clarify approach to establishing safeguard efficacy"),
    ("S0255", (48173, 48208), ("p16-u267", "p16-u268"), "12. Clarify the governance process."),
    ("S0286", (52538, 52846), ("p17-u302",), "C.1 Safeguards against malicious users Several"),
    ("S0324", (58816, 58913), ("p20-u341",), "Claim Potential safeguards Potential safeguard"),
    ("S0339", (60354, 60390), ("p20-u356",), "Reliable and Robust System Oversight"),
)


def _environment():
    return json.loads((PF / "environment.d1.json").read_text(encoding="utf-8"))["vocabulary"]


def _quotes(kind, key):
    """The whole “…” quotations of a legend, one nesting level kept (quote_evidence.quotes, the case's reader)."""
    return Q.quotes(SimpleNamespace(source=_environment()[kind][key]["description"]))


def _passage(text, first, last, anchor):
    """The source passage from `first` to `last` (after `anchor`), and its UTF-8 byte span in the pinned text."""
    start = text.index(first, text.index(ANCHORS[anchor]) if anchor else 0)
    end = text.index(last, start) + len(last)
    return text[start:end], (len(text[:start].encode()), len(text[:end].encode()))


def _id(entry):
    return f"{entry[0]}-{entry[3]}-{entry[4][:12]}"


@pytest.mark.parametrize("entry", CARRIES, ids=_id)
def test_the_legend_quotes_the_source_passage_whole(entry):
    """The condition test for a carry: the passage, read from the pinned source inside its unit's byte span, is one
    whole quotation of the legend under the case's normalisation (fails on main: no such quotation)."""
    unit, (a, b), kind, key, first, last, anchor = entry
    text = pinned_source("openai-preparedness").read_text(encoding="utf-8")
    passage, (start, end) = _passage(text, first, last, anchor)
    assert a <= start < end <= b, (unit, start, end)
    assert Q.plain(passage) in [Q.plain(q) for q in _quotes(kind, key)], (unit, key)


@pytest.mark.parametrize("entry", CARRIES, ids=_id)
def test_the_legend_holds_the_passage_without_the_source(entry):
    """Needs no source: one quotation of the legend starts with the entry's first words and ends with its last."""
    _unit, _span, kind, key, first, last, _anchor = entry
    assert any(Q.plain(q).startswith(Q.plain(first)) and Q.plain(q).endswith(Q.plain(last))
               for q in _quotes(kind, key)), (key, first)


def test_the_carries_reach_every_kept_unit_once_per_passage():
    """The table names 90 source units in 30 legends; no passage is listed twice."""
    assert len({entry[0] for entry in CARRIES}) == 90
    assert len({(entry[2], entry[3]) for entry in CARRIES}) == 30
    assert len({(entry[3], entry[4], entry[6]) for entry in CARRIES}) == len(CARRIES) == 92


@pytest.mark.parametrize("record", RECORDS, ids=lambda r: r[0])
def test_the_unit_is_recorded_as_labelled_exposition(record):
    """The condition test for a record: the spans.json units are LABELLED exposition, wait for nothing, and cover the
    source unit's text (fails on main: they are UNFORMALISED known gaps)."""
    unit, (a, b), ids, _first = record
    units = {u["id"]: u for u in json.loads((PF / "spans.json").read_text(encoding="utf-8"))["units"]}
    spans = sorted(units[i]["span"] for i in ids)
    for i in ids:
        assert (units[i]["status"], units[i]["kind"], units[i]["waits"]) == ("LABELLED", "exposition", []), (unit, i)
    assert all(x[1] == y[0] for x, y in zip(spans, spans[1:]))
    assert spans[0][0] <= a < b <= spans[-1][1], unit


def test_the_records_are_the_label_placements_of_the_build():
    """With the source: the build's `label` placements are exactly these units, each source unit starts with its
    words, and none of them holds a claim marker (the case's own LABELLED condition)."""
    source = pinned_source("openai-preparedness").read_bytes()
    spans = B.segments(source)
    pages = [0] + [i + 1 for i, byte in enumerate(source) if byte == 10]
    placed = set()
    for phrase, (kind, ident, waits) in B.PLACEMENTS.items():
        if kind == "label":
            assert (ident, waits) == ("exposition", ())
            index = B._located(source, spans, phrase)
            placed.add(f"p{sum(p <= spans[index][0] for p in pages)}-u{index + 1}")
    assert placed == {i for record in RECORDS for i in record[2]}
    for unit, (a, b), ids, first in RECORDS:
        assert source[a:b].decode().startswith(first), unit
        assert not B.CLAIM_MARKER.search(source[a:b]), unit
