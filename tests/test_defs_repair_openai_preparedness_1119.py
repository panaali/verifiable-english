"""defs-repair-openai-preparedness-1119: each P1 source definition of the PF audit is carried word for word.

The definitions audit (manage-agents reviews/defs-carried-1119/openai-preparedness.md, rows-openai-preparedness.tsv)
lists 48 P1 rows: a term a PF rule depends on, its definition in the pinned Preparedness Framework v2 text, and the
predicate whose legend carries it. Each row's quote (its inventory entries joined with one space) is appended, after the
old text and a label naming its section, to that predicate's legend in usecases/openai-preparedness/pf_vocabulary.py.
Ten rows use another carrier than the row names: existing_at_publication, the one predicate only the FACTS unit uses (shown
once with every answer, counted for every rule). Rows 18-25 leave `reached` by the DRI decision of 2026-11-20 (manage-agents
reviews/dri-decisions-20261120-defs-repair-openai-preparedness-1119.md, item 1a: prompt size); rows 11 and 40 leave
`in_category` and `third_party_evaluation`, which rules f3-* and f15-third-party read, because their quotes would break
those rules' fidelity tests ("covered" in 2.1; the “…” runs of change log item 6) (docs/.../REPORT.md).

The condition: the quote is in the legend the reader is SHOWN (environment.d1.json `description`, as pf_vocabulary.py
builds it) and in the legend the counter COUNTS (the entry's literal strings in pf_vocabulary.py, read by the counter's
own legend_raw and _omit_legend_segments, copied byte for byte in tools/defs_carried_counter.py), both after the
counter's quote normalisation omit_norm. The sentences are stored here with their source location; when the pinned text
is stored at its pinned path with its pinned hash (tests/pinned_source.py; never downloaded), each must be in it.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from tests.pinned_source import pinned_source
from tools.defs_carried_counter import _omit_legend_segments, legend_raw, omit_norm

REPO = Path(__file__).resolve().parents[1]
HERE = REPO / "usecases" / "openai-preparedness"
EVIDENCE = REPO / "docs/usecases/openai-preparedness/defs-repair-openai-preparedness-1119/evidence"
LEAD = "; the Framework's words, "
# Text-extraction artefacts of the pinned text that the audit's quotes repair (openai-preparedness.md section 1), each
# with how often it occurs in the pinned text; a hyphen at a PDF line break ("real- world", "lev- els") cannot tell a
# compound from a split word, so the source check drops a hyphen between letters on both sides.
EXTRACTION_FIXES = (("T racked", "Tracked", 2),("Y ou ", "You ", 1), ("amalicious", "a malicious", 1))

# entry: (first line, last line of pf-v2.txt, one PDF page per line; section; the sentence as the row quotes it)
SOURCE = {
    'E01': (2, 2, 'fn 1',
            '1 By “severe harm” in this document, we mean the death or grave injury of thousands of people or '
            'hundreds of billions of dollars of economic damage.'),
    'E02': (2, 2, '§intro ("which we call")',
            'We currently focus this work on three areas of frontier capability, which we call Tracked Categories: • '
            'Biological and Chemical capabilities that, in addition to unlocking discoveries and cures, can also '
            'reduce barriers to creating and using biological or chemical weapons. • Cybersecurity capabilities '
            'that, in addition to helping protect vulnerable systems, can also create new risks of scaled '
            'cyberattacks and vulnerability exploitation. • AI Self-improvement capabilities that, in addition to '
            'unlocking helpful capabilities faster, could also create new challenges for human control of AI systems.'),
    'E03': (5, 5, '§2.1',
            'Tracked Categories are those capabilities which we track most closely, measuring them during each '
            'covered deployment and preparing safeguards for when a threshold level is crossed.'),
    'E04': (2, 2, '§intro',
            'In this updated version of the Framework we also introduce a set of Research Categories. These are '
            'areas of capability that could pose risks of severe harm, that do not yet meet our criteria to be '
            'Tracked Categories, and where we are investing now to further develop our threat models and capability '
            'elicitation techniques.'),
    'E05': (5, 5, '§2.1',
            'Research Categories are capabilities that, while they do not meet the above criteria, nonetheless have '
            'the potential to cause or contribute to severe harm, and where we are working now in order to prepare '
            'to address risks in the future (including potentially by maturing them to Tracked Categories).'),
    'E06': (7, 8, '§2.3',
            'There are also some areas of frontier capability that do not meet the criteria to be Tracked '
            'Categories, but where we believe work is required now in order to prepare to effectively address risks '
            'of severe harms in the future. These capabilities either need more research and threat modeling before '
            'they can be rigorously measured, or do not cause direct risks themselves but may need to be monitored '
            'because further advancement in this capability could undermine the safeguards we rely on to mitigate '
            'existing Tracked Category risks. We call these Research Categories, and in these areas we will take the '
            'following steps, both internally and in collaboration with external experts: • Further developing the '
            'threat models for the area, • Advancing the science of capability measurement in the area and investing '
            'towards the development of rigorous evaluations (which could be achieved internally or via '
            'partnerships), and • Sharing summaries of our findings with the public where feasible.'),
    'E07': (15, 15, '§A item 5',
            'Introduce Research Categories, areas of capability that do not meet the criteria to be Tracked '
            'Categories, but where we believe additional work is needed now.'),
    'E08': (5, 5, '§2.1 list 1',
            'Plausible: It must be possible to identify a causal pathway for a severe harm in the capability area, '
            'enabled by frontier AI.'),
    'E09': (5, 5, '§2.1 list 2',
            'Measurable: We can construct or adopt capability evaluations that measure capabilities that closely '
            'track the potential for the severe harm.'),
    'E10': (5, 5, '§2.1 list 3',
            'Severe: There is a plausible threat model within the capability area that would create severe harm.1'),
    'E11': (5, 5, '§2.1 list 4',
            'Net new: The outcome cannot currently be realized as described (including at that scale, by that threat '
            'actor, or for that cost) with existing tools and resources (e.g., available as of 2021) but without '
            'access to frontier AI.'),
    'E12': (5, 5, '§2.1 list 5',
            'Instantaneous or irremediable: The outcome is such that once realized, its severe harms are immediately '
            'felt, or are inevitable due to a lack of feasible measures to remediate.'),
    'E13': (5, 5, '§2.2',
            'Capability thresholds concretely describe things an AI system might be able to help someone do or might '
            'be able to do on its own that could meaningfully increase risk of severe harm.'),
    'E14': (5, 5, '§2.2',
            'High capability thresholds mean capabilities that significantly increase existing risk vectors for '
            'severe harm.'),
    'E15': (5, 5, '§2.2',
            'Critical capability thresholds mean capabilities that present a meaningful risk of a qualitatively new '
            'threat vector for severe harm with no ready precedent.'),
    'E16': (15, 15, '§A item 2',
            'High capability thresholds mean capabilities that significantly increase existing risk vectors for '
            'severe harm under the relevant threat model.'),
    'E17': (15, 15, '§A item 2',
            'Critical capability thresholds mean capabilities that present a meaningful risk of a qualitatively new '
            'threat vector for severe harm with no ready precedent under the relevant threat model.'),
    'E18': (6, 6, 'Table 1 col 1',
            'Biological and Chemical5: The ability of an AI model to accelerate and expand access to biological and '
            'chemical research, development, and skill-building, including access to expert knowledge and assistance '
            'with laboratory work.'),
    'E19': (6, 6, 'Table 1 col 1',
            'Cybersecurity: The ability of an AI model to assist in the development of tools and executing '
            'operations for cyberdefense and cyberoffense.'),
    'E20': (7, 7, 'Table 1 col 1',
            'AI Self-improvement: The ability of an AI system to accelerate AI research, including to increase the '
            'system’s own capability.'),
    'E21': (6, 6, 'Table 1 BIO [High]',
            '[High] The model can provide meaningful counterfactual assistance (relative to unlimited access to '
            'baseline of tools available in 2021) to “novice” actors (anyone with a basic relevant technical '
            'background) that enables them to create known biological or chemical threats.'),
    'E22': (6, 6, 'Table 1 BIO [Critical]',
            '[Critical] The model can enable an expert to develop a highly dangerous novel threat vector (e.g., '
            'comparable to a novel CDC Class A biological agent) OR the model can be connected to tools and '
            'equipment to complete the full engineering and/or synthesis cycle of a regulated or novel biological '
            'threat without human intervention.'),
    'E23': (6, 6, 'Table 1 CYB [High]',
            '[High] The model removes existing bottlenecks to scaling cyber operations including by automating '
            'end-to-end cyber operations against reasonably hardened targets OR by automating the discovery and '
            'exploitation of operationally relevant vulnerabilities.'),
    'E24': (7, 7, 'Table 1 CYB [Critical]',
            '[Critical] A tool-augmented model can identify and develop functional zero-day exploits of all severity '
            'levels in many hardened real-world critical systems without human intervention OR model can devise and '
            'execute end-to-end novel strategies for cyberattacks against hardened targets given only a high level '
            'desired goal.'),
    'E25': (7, 7, 'Table 1 AIS [High]',
            '[High] The model’s impact is equivalent to giving every OpenAI researcher a highly performant '
            'mid-career research engineer assistant, relative to those researchers’ 2024 baseline.'),
    'E26': (7, 7, 'Table 1 AIS [Critical]',
            '[Critical] The model is capable of recursively self improving (i.e., fully automated AI R&D), defined '
            'as either (leading indicator) a superhuman research-scientist agent OR (lagging indicator) causing a '
            'generational model improvement (e.g., from OpenAI o1 to OpenAI o3) in 1/5th the wall-clock time of '
            'equivalent progress in 2024 (e.g., sped up to just 4 weeks) sustainably for several months.'),
    'E27': (6, 6, 'Table 1 BIO [Critical] risk cell',
            'Proliferating the ability to create a novel threat vector of the severity of a CDC Class A biological '
            'agent (i.e., high mortality, ease of transmission) could cause millions of deaths and significantly '
            'disrupt public life, with few available societal safeguards.'),
    'E28': (8, 8, 'Table 2 row 1',
            'Long-range Autonomy: ability for a model to execute a long-horizon sequence of actions sufficient to '
            'realize a “High” threat model (e.g., a cyberattack) without being directed by a human (including '
            'successful social engineering attacks when needed)'),
    'E29': (8, 8, 'Table 2 row 2',
            'Sandbagging: ability and propensity to respond to safety or capability evaluations in a way that '
            'significantly diverges from performance under real conditions, undermining the validity of such '
            'evaluations.'),
    'E30': (8, 8, 'Table 2 row 3',
            'Autonomous Replication and Adaptation: ability to survive, replicate, resist shutdown, acquire '
            'resources to maintain and scale its own operations, and commit illegal activities that collectively '
            'constitute causing severe harm (whether when explicitly instructed, or at its own initiative), without '
            'also utilizing capabilities tracked in other Tracked Categories.'),
    'E31': (8, 8, 'Table 2 row 4',
            'Undermining Safeguards: ability and propensity for the model to act to undermine safeguards placed on '
            'it, including e.g., deception, colluding with oversight models, sabotaging safeguards over time such as '
            'by embedding vulnerabilities in safeguards code, etc.'),
    'E32': (8, 8, 'Table 2 row 5',
            'Nuclear and Radiological: ability to meaningfully counterfactually enable the creation of a '
            'radiological threat or enable or significantly accelerate the development of or access to a nuclear '
            'threat while remaining undetected.'),
    'E33': (9, 9, '§3.1 list 1',
            'Scalable Evaluations: automated evaluations designed to measure proxies that approximate whether a '
            'capability threshold has been crossed. Scalable evaluations have associated “indicative thresholds,” '
            'which are levels of performance that we have pre-determined to indicate that a deployment may have '
            'reached a capability threshold.'),
    'E34': (15, 15, '§A item 6',
            'We also define “scalable evaluations,” which are automated, and distinguish these from “deep dive” '
            'evaluations that may include consultation with human experts and are designed in part to validate the '
            'scalable evaluations.'),
    'E35': (9, 9, '§3.1 list 2',
            'Deep Dives: designed to provide additional evidence validating the scalable evaluations’ findings on '
            'whether a capability threshold has been crossed. These may include a wide range of evidence gathering '
            'activities, such as human expert red-teaming, expert consultations, resource-intensive third party '
            'evaluations (e.g., bio wet lab studies, assessments by independent third party evaluators), and any '
            'other activity requested by SAG.'),
    'E36': (10, 10, '§3.2',
            'The Preparedness Framework applies to any new or updated deployment that has a plausible chance of '
            'reaching a capability threshold whose corresponding risks are not addressed by an existing Safeguards '
            'Report. Examples of such covered deployments are: • every frontier model (e.g., OpenAI o1 or OpenAI o3) '
            'that we plan to deploy externally • any agentic system (including significant agents deployed only '
            'internally) that represents a substantial increase in the capability frontier • any significant change '
            'in the deployment conditions of an existing model (e.g., enabling finetuning, releasing weights, or '
            'significant new features) that makes the existing Capabilities Report or Safeguards Report no longer '
            'reasonably applicable • incremental updates or distilled models with unexpectedly significant increases '
            'in capability. 6'),
    'E37': (10, 10, '§3.3',
            'The results of these evaluations, and any noteworthy observations that should affect interpretation of '
            'the results, are compiled into a Capabilities Report that is submitted to the SAG.'),
    'E38': (15, 15, '§A item 8',
            'Establish Capabilities Reports and Safeguards Reports, the key artifacts we use to support informed '
            'decision-making under the Preparedness Framework in the context of systems that are capable enough to '
            'pose severe risks.'),
    'E39': (11, 11, '§4.2',
            'We compile the information on the planned safeguards needed to minimize the risk of severe harm into a '
            'Safeguards Report. The Safeguards Report should include the following information: • Identified ways a '
            'risk of severe harm can be realized for the given deployment, each mapped to the associated security '
            'controls and safeguards • Details about the efficacy of those safeguards • An assessment on the '
            'residual risk of severe harm based on the deployment • Any notable limitations with the information '
            'provided'),
    'E40': (4, 4, '§1',
            'An internal, cross-functional group of OpenAI leaders called the Safety Advisory Group (SAG) oversees '
            'the Preparedness Framework and makes expert recommendations on the level and type of safeguards '
            'required for deploying frontier capabilities safely and securely.'),
    'E41': (16, 16, '§B SAG Membership',
            'The SAG Chair makes any final decisions needed for the SAG. This role is expected to rotate, as '
            'appointed by OpenAI Leadership.'),
    'E42': (16, 16, '§B',
            'OpenAI Leadership, i.e., the CEO or a person designated by them, is responsible for: • Making all final '
            'decisions, including accepting any residual risks and making deployment go/no-go decisions, informed by '
            'SAG’s recommendations. • Resourcing the implementation of the Preparedness Framework (e.g., additional '
            'work on safeguards where necessary).'),
    'E43': (16, 16, '§B',
            'The Safety and Security Committee (SSC) of the OpenAI Board of Directors (Board) will be given '
            'visibility into processes, and can review decisions and otherwise require reports and information from '
            'OpenAI Leadership as necessary to fulfill the Board’s oversight role.'),
    'E44': (11, 11, '§4.1',
            'We consider separate safeguards for two of the main ways in which risks can be realized: a malicious '
            'user, who can leverage the model to cause the severe harm, and a misaligned model, which autonomously '
            'causes the harm.'),
    'E45': (17, 17, '§C.1',
            'Safeguards should sufficiently minimize the risk of severe harm associated with misuse of the model’s '
            'capabilities. This can be done by establishing that all plausible known vectors of enabling severe harm '
            'are sufficiently addressed by one or more of the following claims: • Robustness: Users cannot use the '
            'model to cause the harm because they cannot elicit the capability, such as because the model is '
            'modified to refuse to provide assistance to harmful tasks and is robust to jailbreaks that would '
            'circumvent those refusals. • Usage Monitoring: If a model does not refuse and provides assistance to '
            'harmful tasks, monitors can stop or catch adversarial users before their misuse has achieved an '
            'unacceptable scale of harm, through a combination of automated and human detection and enforcement '
            'within an acceptable time frame. • Trust-based Access: The actors who gain access to the model will not '
            'use it in a way that presents an associated risk of severe harm under our threat model.'),
    'E46': (19, 19, '§C.2',
            'Safeguards should sufficiently minimize the risk associated with a misaligned model circumventing human '
            'control and oversight and executing severe harms. This can be done by establishing that all plausible '
            'known vectors of enabling severe harm are sufficiently addressed by one or more of the following '
            'claims: • Lack of Autonomous Capability: The model is not capable of carrying out tasks autonomously, '
            'including the risk of severe harm. • Value Alignment: The model consistently applies human values in '
            'novel settings (without any instructions) to avoid taking actions that cause harm, and has shown '
            'sufficiently minimal indications of misaligned behaviors like deception or scheming. • Instruction '
            'Alignment: The model consistently understands and follows user or system instructions, even when vague, '
            'and those instructions rule out pathways to causing severe harm. • Reliable and Robust System '
            'Oversight: Effective AI and human oversight of model actions detects and prevents execution of harm or '
            'subversion of safeguards. • System Architecture: The model can’t take actions that cause harm because '
            'it lacks access to output channels or mechanisms to persist sufficiently to execute the harm, due to '
            'containerization and restricted permissions.'),
    'E47': (21, 22, '§C.3',
            'We will require the following practices for High capability models: • Security Threat Modeling and Risk '
            'Management – Comprehensive Security Threat Models: Ensure OpenAI employs security threat modeling that '
            'systematically identifies and mitigates risks posed by adversaries. These models address both external '
            'and internal threats, explicitly mapping vulnerabilities and attack vectors relevant to frontier AI '
            'model access or misuse. – Continuous Review and Iteration: Ensure security threat models are regularly '
            'reviewed and updated. This includes updating the Security framework, policies, and controls as '
            'technologies and threats evolve. – Continuous Monitoring and Validation: Ensure security threat models '
            'and updates inform where security and data privacy controls should be implemented, improved, and '
            'monitored to further reduce risk. Internal and external assessments to validate these controls are '
            'conducted regularly and reports are provided to OpenAI leadership. • Defense in Depth – Layered '
            'Security Architecture: Adopt a layered security strategy, ensuring robust protection through multiple '
            'defensive barriers, including physical and datacenter security, network segmentation and controls, '
            'workload isolation, data encryption, and other overlapping and complementary security controls. – Zero '
            'Trust Principles: Embrace Zero Trust principles in the design and operation of infrastructure, '
            'networks, and endpoints. Leverage hardware-backed security and modern authentication standards and '
            'controls for accessing critical resources and performing operations. • Access Management – Principle of '
            'Least Privilege: Ensure access to systems and data is limited based on job functions, need-to-know, and '
            'operational requirements in alignment with the principles of least privilege and separation of duties. '
            'Ensure all access is regularly audited and reviewed. For all models, especially those presenting High '
            'capabilities, access must be strictly limited, protected with strong multi-factor authentication, and '
            'may require additional approvals for access. – Identity and Device Management: Employees must '
            'authenticate using multi-factor authentication (MFA) and managed devices meeting security baselines. '
            'Access must be logged and reviewed for detection and investigative purposes. • Secure Development and '
            'Supply Chain – Secure Development Lifecycle: Integrate automated code analysis, formal security '
            'reviews, and penetration testing in engineering processes. Apply security reviews and validation to '
            'higher-sensitivity critical components prior to deployment. – Change Management: Establish and maintain '
            'a formal change management process to ensure that all modifications to systems, applications, and '
            'infrastructure are properly authorized, documented, tested, and approved before deployment. Changes to '
            'critical infrastructure should undergo multi-person approval and review. This process should include '
            'maintaining comprehensive records of changes and implementing rollback procedures to revert to previous '
            'states. – Software Supply Chain Integrity: Enforce supply chain security measures, including sourcing '
            'hardware and software from reputable sources, and continuous vetting and monitoring of third-party '
            'suppliers and software libraries. • Operational Security – Monitoring and Incident Response: Monitor '
            'security and event logs continuously to detect, triage, and respond to security incidents rapidly by '
            '24x7 on-call staff. – Vulnerability Management: Ensure known vulnerabilities are addressed through '
            'consistent patching and corrective actions, minimizing exploitation opportunities. – Adversarial '
            'Testing and Red-Teaming: Conduct adversarial testing and red-teaming exercises to proactively identify '
            'and mitigate potential vulnerabilities within corporate, research, and product systems, ensuring '
            'resilience against unknown vulnerabilities and emerging threats. Encourage reporting of good-faith '
            'security research through bug bounty programs. • Auditing and Transparency – Independent Security '
            'Audits: Ensure security controls and practices are validated regularly by third-party auditors to '
            'ensure compliance with relevant standards and robustness against identified threats. – Transparency in '
            'Security Practices: Ensure security findings, remediation efforts, and key metrics from internal and '
            'independent audits are periodically shared with internal stakeholders and summarized publicly to '
            'demonstrate ongoing commitment and accountability. – Governance and Oversight: Ensure that management '
            'provides oversight over the information security and risk management programs.'),
    'E48': (13, 13, '§4.3',
            'We recognize that another frontier AI model developer might develop or release a system with High or '
            'Critical capability in one of this Framework’s Tracked Categories and may do so without instituting '
            'comparable safeguards to the ones we have committed to.'),
    'E49': (2, 2, '§intro',
            'The Preparedness Framework is OpenAI’s approach to tracking and preparing for frontier capabilities '
            'that create new risks of severe harm.1'),
}
# row: (term, carrier predicate, label before the quote, entries joined with one space = the row's quote)
ROWS = {
    1: ('severe harm', 'high', 'footnote 1', ('E01',)),
    2: ('High capability thresholds', 'high', '2.2 and change log item 2', ('E14', 'E16')),
    3: ('Critical capability thresholds', 'critical', '2.2 and change log item 2', ('E15', 'E17')),
    4: ('BIO-H level (Table 1)', 'high', 'Table 1, Biological and Chemical, High', ('E21',)),
    5: ('CYB-H level (Table 1)', 'high', 'Table 1, Cybersecurity, High', ('E23',)),
    6: ('AIS-H level (Table 1)', 'high', 'Table 1, AI Self-improvement, High', ('E25',)),
    7: ('BIO-C level (Table 1)', 'critical', 'Table 1, Biological and Chemical, Critical', ('E22',)),
    8: ('CYB-C level (Table 1)', 'critical', 'Table 1, Cybersecurity, Critical', ('E24',)),
    9: ('AIS-C level (Table 1); recursively self improving', 'critical', 'Table 1, AI Self-improvement, Critical', ('E26',)),
    10: ('CDC Class A biological agent', 'critical', 'Table 1, Biological and Chemical, Critical, its risk', ('E27',)),
    11: ('Tracked Categories', 'existing_at_publication', 'introduction and 2.1', ('E02', 'E03')),
    12: ('Biological and Chemical (category)', 'in_category', 'Table 1', ('E18',)),
    13: ('Cybersecurity (category)', 'in_category', 'Table 1', ('E19',)),
    14: ('AI Self-improvement (category)', 'in_category', 'Table 1', ('E20',)),
    15: ('Research Categories', 'research_review', 'introduction, 2.1, 2.3 and change log item 5', ('E04', 'E05', 'E06', 'E07')),
    16: ('Research Categories', 'research_category_review', 'introduction, 2.1, 2.3 and change log item 5', ('E04', 'E05', 'E06', 'E07')),
    17: ('Research Categories', 'ara_tracking', 'introduction, 2.1, 2.3 and change log item 5', ('E04', 'E05', 'E06', 'E07')),
    18: ('capability thresholds', 'existing_at_publication', '2.2', ('E13',)),
    19: ('Safety Advisory Group (SAG)', 'existing_at_publication', 'section 1', ('E40',)),
    20: ('covered (deployments)', 'existing_at_publication', '3.2', ('E36',)),
    21: ('Preparedness Framework', 'existing_at_publication', 'introduction', ('E49',)),
    22: ('OpenAI Leadership', 'existing_at_publication', 'Appendix B', ('E42',)),
    23: ('malicious user / misaligned model', 'existing_at_publication', '4.1', ('E44',)),
    24: ('Safeguards Report (content)', 'existing_at_publication', '4.2', ('E39',)),
    25: ('Capabilities Reports and Safeguards Reports (change log 8)', 'existing_at_publication', 'change log item 8', ('E38',)),
    26: ('Capabilities Report', 'capabilities_report', '3.3', ('E37',)),
    27: ('Capabilities Report', 'third_party_evaluation', '3.3', ('E37',)),
    28: ('Plausible (criterion)', 'criteria_tracking', '2.1', ('E08',)),
    29: ('Measurable (criterion)', 'criteria_tracking', '2.1', ('E09',)),
    30: ('Severe (criterion)', 'criteria_tracking', '2.1', ('E10',)),
    31: ('Net new (criterion)', 'criteria_tracking', '2.1', ('E11',)),
    32: ('Instantaneous or irremediable (criterion)', 'criteria_tracking', '2.1', ('E12',)),
    33: ('Long-range Autonomy', 'misalignment_report', 'Table 2', ('E28',)),
    34: ('Sandbagging', 'sandbagging_response', 'Table 2', ('E29',)),
    35: ('Autonomous Replication and Adaptation', 'ara_tracking', 'Table 2', ('E30',)),
    36: ('Undermining Safeguards', 'robust_case', 'Table 2', ('E31',)),
    37: ('Nuclear and Radiological', 'nuclear_safeguards', 'Table 2', ('E32',)),
    38: ('Scalable Evaluations', 'evaluations_before_deployment', '3.1 and change log item 6', ('E33', 'E34')),
    39: ('Scalable Evaluations', 'capabilities_report_submitted', '3.1 and change log item 6', ('E33', 'E34')),
    40: ('Deep Dives', 'existing_at_publication', '3.1 and change log item 6', ('E35', 'E34')),
    41: ('SAG Chair', 'chair_coordination', 'Appendix B, SAG Membership', ('E41',)),
    42: ('Board (OpenAI Board of Directors)', 'board_finds_necessary', 'Appendix B', ('E43',)),
    43: ('High standard against misuse (Appendix C.1)', 'misuse_safeguards', 'Appendix C.1', ('E45',)),
    44: ('High standard against misalignment (Appendix C.2)', 'alignment_safeguards', 'Appendix C.2', ('E46',)),
    45: ('High standard against misalignment (Appendix C.2)', 'misalignment_risk_minimized', 'Appendix C.2', ('E46',)),
    46: ('security controls meeting High standard (Appendix C.3)', 'security_controls', 'Appendix C.3', ('E47',)),
    47: ('security practices (Appendix C.3)', 'security_practices', 'Appendix C.3', ('E47',)),
    48: ('another developer scenario (4.3)', 'adjustment_confirmed', '4.3', ('E48',)),
}


def _vocabulary():
    spec = importlib.util.spec_from_file_location("pf_vocabulary_defs_repair_1119", HERE / "pf_vocabulary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VOCABULARY = _vocabulary()


def row_quote(row):
    return " ".join(SOURCE[e][3] for e in ROWS[row][3])


def shown():
    """{predicate: description} as committed and as pf_vocabulary.py builds it (they must be equal)."""
    committed = json.loads((HERE / "environment.d1.json").read_text(encoding="utf-8"))["vocabulary"]["predicates"]
    built = VOCABULARY.environment()["vocabulary"]["predicates"]
    return ({k: v["description"] for k, v in committed.items()}, {k: v["description"] for k, v in built.items()})


def counted(key):
    """The meaning segments (citations cut, normalised) the counter counts for the predicate's legend."""
    lines = (HERE / "pf_vocabulary.py").read_text(encoding="utf-8").splitlines()
    return [meaning for meaning, _raw in _omit_legend_segments(legend_raw(key, lines)) if meaning]


def counted_form(text):
    """The text as the counter cuts and normalises a legend string (the same function, on the text alone)."""
    [(meaning, _raw)] = _omit_legend_segments(['"x": (', '"' + text + '"'])
    return meaning


def source_window(lines, first, last):
    """Lines first..last (1-based) joined with one space; a continued line drops its page footer (line n ends ' n-1')."""
    parts = []
    for n in range(first, last + 1):
        line = lines[n - 1]
        if n < last:
            footer = f" {n - 1}"
            assert line.endswith(footer), (n, line[-20:])
            line = line[: -len(footer)]
        parts.append(line)
    return " ".join(parts)


def source_norm(text):
    """omit_norm, then the extraction artefacts: no space before closing punctuation or after '(', no hyphen between
    letters (a line-break hyphen, see EXTRACTION_FIXES)."""
    text = re.sub(r" (?=[.,:;)])", "", omit_norm(text))
    text = re.sub(r"(?<=\() ", "", text)
    return re.sub(r"(?<=[a-z])- ?(?=[a-z])", "", text)


def fixed_source(text):
    for raw, fixed, count in EXTRACTION_FIXES:
        assert text.count(raw) == count, raw
        text = text.replace(raw, fixed)
    return text


def test_the_rows_are_the_48_p1_rows_and_each_entry_is_used():
    assert sorted(ROWS) == list(range(1, 49))
    assert {e for row in ROWS.values() for e in row[3]} == set(SOURCE)
    assert len({row[1] for row in ROWS.values()}) == 24
    for first, last, _section, sentence in SOURCE.values():
        assert 1 <= first <= last <= first + 1 and '"' not in sentence and sentence == sentence.strip()


@pytest.mark.parametrize("row", sorted(ROWS))
def test_each_row_quote_is_shown_and_counted_in_its_carrier_legend(row):
    """The condition test: the row's whole quote, after its label, in the shown legend (committed and built) and in
    one counted string of the predicate's vocabulary entry."""
    _term, key, label, _entries = ROWS[row]
    quote = row_quote(row)
    committed, built = shown()
    assert committed[key] == built[key], key
    assert omit_norm(f"{label}: {quote}") in omit_norm(committed[key]), (row, key)
    assert any(counted_form(quote) in meaning for meaning in counted(key)), (row, key)


def test_each_carrier_keeps_its_old_legend_and_appends_the_rows_in_order():
    """Information added, nothing removed: each new legend is the legend at main, then LEAD, then its rows' labelled
    quotes in row order (evidence/legends-before.json, saved from main 09bea0972d). Seven of the carriers were also
    extended on main by srccov-openai-preparedness-1119, which only appended too; for them the old legend is the one at
    the merged ve-integration (evidence/legends-before-merge.json), whose prefix is the 09bea0972d legend."""
    before = json.loads((EVIDENCE / "legends-before.json").read_text(encoding="utf-8"))["descriptions"]
    merged = json.loads((EVIDENCE / "legends-before-merge.json").read_text(encoding="utf-8"))["descriptions"]
    committed, _built = shown()
    assert sorted(before) == sorted({row[1] for row in ROWS.values()})
    assert set(merged) <= set(before)
    for key, extended in merged.items():
        assert extended.startswith(before[key] + "; "), key
    for key in before:
        old = merged.get(key, before[key])
        parts = [f"{ROWS[r][2]}: {row_quote(r)}" for r in sorted(ROWS) if ROWS[r][1] == key]
        assert " ".join(committed[key].split()) == " ".join((old + LEAD + " ".join(parts)).split()), key


def test_each_sentence_is_in_the_pinned_source_at_its_lines():
    lines = fixed_source(pinned_source("openai-preparedness").read_text(encoding="utf-8")).split("\n")
    missing = [e for e, (first, last, _section, sentence) in SOURCE.items()
               if source_norm(sentence) not in source_norm(source_window(lines, first, last))]
    assert missing == []


def test_the_source_reader_drops_only_a_continued_page_footer_and_refuses_a_missing_artefact():
    lines = ["cover", "a span that goes on 1", "and ends here. 2"]
    assert source_window(lines, 2, 3) == "a span that goes on and ends here. 2"
    with pytest.raises(AssertionError):
        source_window(["x", "no footer here", "end"], 2, 3)
    assert source_norm("real- world (e.g. x) , y") == source_norm("realworld (e.g. x), y")
    with pytest.raises(AssertionError):
        fixed_source("T racked Y ou only")
