"""D1 vocabulary for the pinned Preparedness Framework v2 (PLAN 4 and 7)."""
from __future__ import annotations

import json
from pathlib import Path

from ve.profiles import LANGUAGE, SPEC_REVISION

HERE = Path(__file__).resolve().parent
LEVELS = {
    "biological_and_chemical_high": ("biological_and_chemical", "High"),
    "biological_and_chemical_critical": ("biological_and_chemical", "Critical"),
    "cybersecurity_high": ("cybersecurity", "High"),
    "cybersecurity_critical": ("cybersecurity", "Critical"),
    "ai_self_improvement_high": ("ai_self_improvement", "High"),
    "ai_self_improvement_critical": ("ai_self_improvement", "Critical"),
}


# srccov-openai-preparedness-1119: the source's own words for each Table 1 level and Tracked Category, appended to
# the constant's legend word for word (PDF line-break hyphens rejoined).
LEVEL_TEXT = {
    "biological_and_chemical_high": "capability threshold: “The model can provide meaningful counterfactual "
                                    "assistance (relative to unlimited access to baseline of tools available in "
                                    "2021) to “novice” actors (anyone with a basic relevant technical background) "
                                    "that enables them to create known biological or chemical threats.”; associated "
                                    "risk of severe harm: “Significantly increased likelihood and frequency of "
                                    "biological or chemical terror events by non-state actors using known "
                                    "reference-class threats.”",
    "biological_and_chemical_critical": "capability threshold: “The model can enable an expert to develop a highly "
                                        "dangerous novel threat vector (e.g., comparable to a novel CDC Class A "
                                        "biological agent) OR the model can be connected to tools and equipment to "
                                        "complete the full engineering and/or synthesis cycle of a regulated or "
                                        "novel biological threat without human intervention.”; associated risk of "
                                        "severe harm: “Proliferating the ability to create a novel threat vector of "
                                        "the severity of a CDC Class A biological agent (i.e., high mortality, ease "
                                        "of transmission) could cause millions of deaths and significantly disrupt "
                                        "public life, with few available societal safeguards.”",
    "cybersecurity_high": "capability threshold: “The model removes existing bottlenecks to scaling cyber operations "
                          "including by automating end-to-end cyber operations against reasonably hardened targets "
                          "OR by automating the discovery and exploitation of operationally relevant "
                          "vulnerabilities.”; associated risk of severe harm: “Removing bottlenecks limiting "
                          "malicious cyber activity may upset the current cyberoffense-cyberdefense balance by "
                          "significantly automating and scaling the volume of existing cyberattacks.” “In "
                          "conjunction with a Long-range Autonomy capability (Section 2.3), models that could bypass "
                          "OpenAI’s technical safeguards constraining model activity, such as sandboxing or "
                          "monitoring services, could compromise OpenAI’s ability to track and mitigate all other "
                          "risks.”",
    "cybersecurity_critical": "capability threshold: “A tool-augmented model can identify and develop functional "
                              "zero-day exploits of all severity levels in many hardened real-world critical systems "
                              "without human intervention OR model can devise and execute end-to-end novel "
                              "strategies for cyberattacks against hardened targets given only a high level desired "
                              "goal.”; associated risk of severe harm: “Finding and executing end-to-end exploits "
                              "for all software could lead to catastrophe from unilateral actors, hacking military "
                              "or industrial systems, or OpenAI infrastructure.” “Novel cyber operations, e.g., "
                              "those involving novel zero-days or novel methods of command-and-control, generally "
                              "pose the most serious threat, as they are unpredictable and scarce.”",
    "ai_self_improvement_high": "capability threshold: “The model’s impact is equivalent to giving every OpenAI "
                                "researcher a highly performant mid-career research engineer assistant, relative to "
                                "those researchers’ 2024 baseline.”; associated risk of severe harm: “This milestone "
                                "suggests AI self-improvement may be beginning to accelerate.”",
    "ai_self_improvement_critical": "capability threshold: “The model is capable of recursively self improving "
                                    "(i.e., fully automated AI R&D), defined as either (leading indicator) a "
                                    "superhuman research-scientist agent OR (lagging indicator) causing a "
                                    "generational model improvement (e.g., from OpenAI o1 to OpenAI o3) in 1/5th the "
                                    "wall-clock time of equivalent progress in 2024 (e.g., sped up to just 4 weeks) "
                                    "sustainably for several months.”; associated risk of severe harm: “A major "
                                    "acceleration in the rate of AI R&D could rapidly increase the rate at which new "
                                    "capabilities and risks emerge, to the point where our current oversight "
                                    "practices are insufficient to identify and mitigate new risks, including risks "
                                    "to maintaining human control of the AI system itself.”",
}
CATEGORY_TEXT = {
    "biological_and_chemical": "page 2: “Biological and Chemical capabilities that, in addition to unlocking "
                               "discoveries and cures, can also reduce barriers to creating and using biological or "
                               "chemical weapons.”; Table 1: “The ability of an AI model to accelerate and expand "
                               "access to biological and chemical research, development, and skill-building, "
                               "including access to expert knowledge and assistance with laboratory work.”",
    "cybersecurity": "page 2: “Cybersecurity capabilities that, in addition to helping protect vulnerable systems, "
                     "can also create new risks of scaled cyberattacks and vulnerability exploitation.”; Table 1: "
                     "“The ability of an AI model to assist in the development of tools and executing operations for "
                     "cyberdefense and cyberoffense.”",
    "ai_self_improvement": "page 2: “AI Self-improvement capabilities that, in addition to unlocking helpful "
                           "capabilities faster, could also create new challenges for human control of AI systems.”; "
                           "Table 1: “The ability of an AI system to accelerate AI research, including to increase "
                           "the system’s own capability.”",
}


def base(args, description, verbalisation=None):
    result = {"arguments": list(args), "description": description}
    if verbalisation:
        result["verbalisation"] = verbalisation
    return result


def permission(act, description):
    return {"arguments": ["situation"], "description": description,
            "regulated": {"role": "permission", "default": "allow", "act": act}}


def duty(act, description):
    return {"arguments": ["situation"], "description": description,
            "regulated": {"role": "obligation", "default": "deny", "act": act}}


BASE = {
    "covered": base(["situation"], "the model at {0} is covered by the Framework; 3.2: “The Preparedness Framework "
                                   "applies to any new or updated deployment that has a plausible chance of reaching "
                                   "a capability threshold whose corresponding risks are not addressed by an "
                                   "existing Safeguards Report.” “Examples of such covered deployments are:” “every "
                                   "frontier model (e.g., OpenAI o1 or OpenAI o3) that we plan to deploy externally” "
                                   "“any agentic system (including significant agents deployed only internally) that "
                                   "represents a substantial increase in the capability frontier” “any significant "
                                   "change in the deployment conditions of an existing model (e.g., enabling "
                                   "finetuning, releasing weights, or significant new features) that makes the "
                                   "existing Capabilities Report or Safeguards Report no longer reasonably "
                                   "applicable” “incremental updates or distilled models with unexpectedly "
                                   "significant increases in capability.”"),
    "likely_to_cross": base(["situation"], "the covered system at {0} appears likely to cross a capability threshold; "
                                                 "OpenAI ('we') decides this (OT9)"),
    "reasonable_evidence": base(["situation"], "at {0} OpenAI ('we') finds reasonable evidence that its safeguards are "
                                               "not working as expected (4.2: \u201cIf we find reasonable evidence that "
                                               "our safeguards are not working as expected\u201d); OpenAI ('we') decides "
                                               "this (OT11)"),
    "adjustment_conditions": base(["situation"], "4.3's conditions for adjusting the safeguards required in that "
                                       "capability area hold at {0}: the adjustment does not meaningfully increase the overall risk of "
                                       "severe harm, is publicly acknowledged, and keeps safeguards more protective than the other "
                                       "developer's, with information shared to validate it; their assessment is open"),
    "sufficient_safeguards": base(["situation"], "safeguards sufficiently minimize severe-harm risk at {0}; SAG "
                                                 "decides this; footnote 1: “By “severe harm” in this document, we "
                                                 "mean the death or grave injury of thousands of people or hundreds "
                                                 "of billions of dollars of economic damage.”"),
    "major_deployment": base(["situation"], "{0} is a major deployment; the decider is unstated (OT13)"),
    "safeguard_selection": base(["situation"], "{0} is the selection of safeguards for a deployment"),
    "substantiated_noncompliance": base(["situation"], "a noncompliance report at {0} is substantiated"),
    "external_deployment": base(["situation"], "{0} is an external deployment"),
    "framework_deployment": base(["situation"], "{0} is a deployment under the Preparedness Framework"),
    "large_scale_internal": base(["situation"], "{0} is a large-scale internal deployment"),
    "critical_standard_unspecified": base(["situation"], "OpenAI ('we') has not yet specified, at {0}, safeguards and "
                                          "security controls that would meet a Critical standard (Table 1 BIO-C, AIS-C: "
                                          "\u201cUntil we have specified safeguards and security controls that would "
                                          "meet a Critical standard\u201d; CYB-C: \u201csafeguards and security "
                                          "controls standards that would meet a Critical standard\u201d)"),
    "in_category": base(["level", "category"], "{0} is in Tracked Category {1}", "{0} concerns {1}"),
    "high": base(["level"], "{0} is a High level; 2.2: “High capability thresholds mean capabilities that "
                            "significantly increase existing risk vectors for severe harm.”; change log item 2: "
                            "“High capability thresholds mean capabilities that significantly increase existing risk "
                            "vectors for severe harm under the relevant threat model.”", "{0} is high"),
    "critical": base(["level"], "{0} is a Critical level; 2.2: “Critical capability thresholds mean capabilities "
                                "that present a meaningful risk of a qualitatively new threat vector for severe harm "
                                "with no ready precedent.”; change log item 2: “Critical capability thresholds mean "
                                "capabilities that present a meaningful risk of a qualitatively new threat vector "
                                "for severe harm with no ready precedent under the relevant threat model.”", "{0} is critical"),
    "low": base(["level"], "{0} is a \"low\" level (a term the change log removes)", "{0} is low"),
    "medium": base(["level"], "{0} is a \"medium\" level (a term the change log removes)", "{0} is medium"),
    "indicator_for": base(["evaluation", "level"], "{0} is used as an indicator for {1} (footnote 5)", "{0} indicates {1}"),
    "chemical": base(["evaluation"], "{0} evaluates a chemical capability", "{0} is chemical"),
    "reached": base(["situation", "level"], "the model at {0} has reached {1}; SAG decides this; 3.3: “The "
                                            "determination that a threshold has been reached is informed by these "
                                            "indicative results from capability evaluations, and also reflects "
                                            "holistic judgment based on the totality of available evidence – for "
                                            "example, information about the methodological robustness of evaluation "
                                            "results.”", "{0} has reached {1}"),
    "proposed": base(["proposal"], "{0} is proposed"),
    "required": base(["requirement"], "{0} is a requirement"),
    "coverage_ambiguous": base(["situation"], "coverage of {0} is ambiguous"),
    "forecast_severe_before_deployment": base(["situation"], "{0} is justified by OpenAI's forecasts and threat models as "
                                              "potentially posing a severe risk during development and prior to "
                                              "external deployment (3.2)"),
    "distilled_finetuned_or_quantized_from_below_high": base(["situation"], "{0} is a model that OpenAI distills, fine-tunes, or quantizes "
                                   "from a model that was previously determined not to cross a High capability "
                                   "threshold (footnote 6)"),
    "significant_increase": base(["situation"], "there is reason to believe at {0} that a significant increase in capability "
                                     "has occurred; OpenAI ('we') decides this (OT20)"),
    "adjustment_confirmed": base(["situation"], "it is rigorously confirmed at {0} that another frontier AI developer "
                                     "developed or released a system with High or Critical capability in a Tracked Category without "
                                     "comparable safeguards"),
    "adjustment_area": base(["situation", "category"], "4.3's adjustment at {0} is to the level of safeguards OpenAI "
                            "requires in capability area {1} (“that capability area”): the Tracked Category in "
                            "which the scenario rigorously confirmed at {0} occurred", "{0} adjusts {1}"),
    "adjustment_made": base(["situation"], "OpenAI makes 4.3's marginal-risk adjustment at {0}: it adjusts the level "
                                "of safeguards it requires in that capability area"),
    "lra_found": base(["situation"], "Long-range Autonomy is found at {0}; 2.3, Table 2, Long-range Autonomy: "
                                     "“ability for a model to execute a long-horizon sequence of actions sufficient "
                                     "to realize a “High” threat model (e.g., a cyberattack) without being directed "
                                     "by a human (including successful social engineering attacks when needed)”"),
    "sandbagging_found": base(["situation"], "sandbagging is found at {0}; 2.3, Table 2, Sandbagging: “ability and "
                                             "propensity to respond to safety or capability evaluations in a way "
                                             "that significantly diverges from performance under real conditions, "
                                             "undermining the validity of such evaluations.”"),
    "ara_found": base(["situation"], "Autonomous Replication and Adaptation is found at {0}; 2.3, Table 2, "
                                     "Autonomous Replication and Adaptation: “ability to survive, replicate, resist "
                                     "shutdown, acquire resources to maintain and scale its own operations, and "
                                     "commit illegal activities that collectively constitute causing severe harm "
                                     "(whether when explicitly instructed, or at its own initiative), without also "
                                     "utilizing capabilities tracked in other Tracked Categories.”"),
    "undermining_found": base(["situation"], "undermining of safeguards is found at {0}; 2.3, Table 2, Undermining "
                                             "Safeguards: “ability and propensity for the model to act to undermine "
                                             "safeguards placed on it, including e.g., deception, colluding with "
                                             "oversight models, sabotaging safeguards over time such as by embedding "
                                             "vulnerabilities in safeguards code, etc.”"),
    "nuclear_found": base(["situation"], "Nuclear and Radiological capability is found at {0}; 2.3, Table 2, Nuclear "
                                         "and Radiological: “ability to meaningfully counterfactually enable the "
                                         "creation of a radiological threat or enable or significantly accelerate "
                                         "the development of or access to a nuclear threat while remaining "
                                         "undetected.”"),
    "further_development": base(["situation"], "{0} is further development of the model"),
    "internal_deployment": base(["situation"], "{0} is an internal deployment"),
    "forecast_critical": base(["situation"], "the model at {0} is forecasted to reach Critical capability; OpenAI decides this"),
    "existing_at_publication": base(["situation"], "the model at {0} is one OpenAI possessed at publication (2025-04-15), "
                                    "the time of 4.4's “We do not currently possess any models that have Critical "
                                    "levels of capability”"),
    "threshold_determined": base(["situation"], "the SAG determines at {0} that a capability threshold has been crossed"),
    "safeguards_already_assessed": base(["situation"], "the corresponding safeguards at {0} have already been implemented and assessed"),
    "rapid_risk": base(["situation"], "a risk of severe harm rapidly develops at {0}"),
    "fast_track_requested": base(["situation"], "a fast track for the SAG is requested at {0}"),
    "immediate_reaction_needed": base(["situation"], "immediate reaction is needed to address the risk at {0}"),
    "deeper_testing_warranted": base(["situation"], "OpenAI ('we') deems that the deployment at {0} warrants deeper "
                                                     "testing of Tracked Categories of capability"),
    "third_party_available": base(["situation"], "third-party evaluation is available and feasible at {0}"),
    "safeguards_report_compiled": base(["situation"], "{0} is the compilation of a Safeguards Report"),
    "employee_request": base(["situation"], "an employee requests a summary of the testing results and SAG recommendation at {0}"),
    "beyond_sensitive_limits": base(["situation"], "the summary requested at {0} goes beyond the limits set for highly "
                                                   "sensitive information (5.1)"),
    "potential_noncompliance": base(["situation"], "{0} is a reported or otherwise identified potential instance of "
                                                   "noncompliance with the Framework (5.1)"),
    "persuasion_risk": base(["situation"], "{0} concerns risks related to persuasion"),
    "leadership_decision": base(["situation"], "{0} is a final decision of OpenAI Leadership"),
    "board_finds_necessary": base(["situation"], "it is necessary at {0} to act on the decision (Appendix B: "
                                                  "\u201cWhere necessary\u201d); the source names no decider: the "
                                                  "decider is unstated (an open term, as OT13)"),
    # pf-f16-without-fix (ruling pf-f16-without-n2-20261116 section 4): the limit of RS7=noinput's permission.
    # Recommendations count as given only if they are for this decision and given before it; a SAG still
    # deliberating with none given for this decision is "none given". Modelling rule: a case that states SAG
    # recommendations, findings or SAG participation for the decision sets this atom (closed world otherwise).
    "sag_recommendations_given": base(["situation"], "the SAG has given OpenAI Leadership its recommendations for "
                                                     "the decision at {0}, before the decision (Appendix B: "
                                                     "“informed by SAG's recommendations”; without them OpenAI "
                                                     "Leadership “can also make decisions without the SAG's "
                                                     "participation, i.e., the SAG does not have the ability to "
                                                     "‘filibuster’”)"),
    # No rule reads `decided_without_sag` since pf-f16-without-fix (both f16-without guards dropped it); it stays
    # declared for run.py WITNESS["C2"], where it is inert (tests/test_pf_f16_without_fix.py).
    "decided_without_sag": base(["situation"], "OpenAI Leadership makes the decision at {0} without the SAG's participation"),
    "research_category_review": base(["situation"], "{0} is a Research Category review; Research Categories, page 2: "
                                                    "“These are areas of capability that could pose risks of severe "
                                                    "harm, that do not yet meet our criteria to be Tracked "
                                                    "Categories, and where we are investing now to further develop "
                                                    "our threat models and capability elicitation techniques.”; 2.1: "
                                                    "“Research Categories are capabilities that, while they do not "
                                                    "meet the above criteria, nonetheless have the potential to "
                                                    "cause or contribute to severe harm, and where we are working "
                                                    "now in order to prepare to address risks in the future "
                                                    "(including potentially by maturing them to Tracked "
                                                    "Categories).”; 2.3: “These capabilities either need more "
                                                    "research and threat modeling before they can be rigorously "
                                                    "measured, or do not cause direct risks themselves but may need "
                                                    "to be monitored because further advancement in this capability "
                                                    "could undermine the safeguards we rely on to mitigate existing "
                                                    "Tracked Category risks.”; change log item 4: “We are moving "
                                                    "Nuclear and Radiological capabilities into Research "
                                                    "Categories.”; change log item 5: “Introduce Research "
                                                    "Categories, areas of capability that do not meet the criteria "
                                                    "to be Tracked Categories, but where we believe additional work "
                                                    "is needed now.” “These include Long-range Autonomy, "
                                                    "Sandbagging, Autonomous Replication and Adaptation, Undermining "
                                                    "Safeguards, and Nuclear and Radiological.”"),
    "plausible": base(["capability"], "{0} meets the plausible-pathway criterion; 2.1, criterion 1 (Plausible): “It "
                                      "must be possible to identify a causal pathway for a severe harm in the "
                                      "capability area, enabled by frontier AI.”"),
    "measurable": base(["capability"], "{0} meets the measurable criterion; 2.1, criterion 2 (Measurable): “We can "
                                       "construct or adopt capability evaluations that measure capabilities that "
                                       "closely track the potential for the severe harm.”"),
    "severe": base(["capability"], "{0} meets the severe-harm criterion; 2.1, criterion 3 (Severe): “There is a "
                                   "plausible threat model within the capability area that would create severe harm.”"),
    "net_new": base(["capability"], "{0} meets the net-new criterion; 2.1, criterion 4 (Net new): “The outcome "
                                    "cannot currently be realized as described (including at that scale, by that "
                                    "threat actor, or for that cost) with existing tools and resources (e.g., "
                                    "available as of 2021) but without access to frontier AI.”"),
    "irremediable": base(["capability"], "{0} meets the instantaneous-or-irremediable criterion; 2.1, criterion 5 "
                                         "(Instantaneous or irremediable): “The outcome is such that once realized, "
                                         "its severe harms are immediately felt, or are inevitable due to a lack of "
                                         "feasible measures to remediate.”"),
    "criteria_tracking": {"arguments": ["capability"], "description": "{0} is tracked as a category",
                          "regulated": {"role": "obligation", "default": "deny",
                                        "act": "{0} be tracked as a category", "permission": "criteria_exclusion"}},
    "criteria_exclusion": {"arguments": ["capability"], "description": "{0} may be tracked as a category",
                            "regulated": {"role": "permission", "default": "allow",
                                          "act": "{0} be tracked as a category"}},
    "deployment_permitted": permission("{0} be deployed", "1: deployment of a model that reaches High"),
    "summary_access": permission("{0} have employees request as well as receive the testing as well as SAG summary",
                                 "5.1: \u201cEmployees may also request and receive a summary of the testing results "
                                 "and SAG recommendation on capability levels and safeguards (subject to certain "
                                 "limits for highly sensitive information).\u201d: the summary is of the testing "
                                 "results and of the SAG recommendation on capability levels and safeguards; the "
                                 "limits are the rule's carve-out"),
    "decision_reversal": permission("{0} have the decision reversed by the Board",
                                    "Appendix B: the Board may reverse a decision of OpenAI Leadership"),
    "revised_course_mandated": permission("{0} have a revised course of action mandated by the Board",
                                          "Appendix B: the Board may mandate a revised course of action"),
    # The fast track is something OpenAI may ask for; the urgent processing is what it asks for, not a duty on the
    # SAG that the sentence states (PLAN 3.3: no permission or duty the text does not grant).
    "fast_track_request": permission("{0} have a fast track requested so the SAG processes the report urgently",
                                     "Appendix B, Fast-track: “In the rare case that a risk of severe harm "
                                     "rapidly develops (e.g., there is a change in our understanding of model safety "
                                     "that requires urgent response), we can request a fast track for the SAG to "
                                     "process the report urgently.”: OpenAI ('we') may request it; the request is "
                                     "for the SAG to process the report urgently"),
    # Appendix B's yearly review is of the Framework itself, once, not of each situation: its sort is the Framework.
    "annual_review": {"arguments": ["framework"],
                      "description": "Appendix B: \u201cWe will review and potentially update the Preparedness Framework "
                                     "for continued sufficiency at least once a year.\u201d: {0} is reviewed at least once "
                                     "a year, as to its continued sufficiency; the update is optional "
                                     "(\u201cpotentially\u201d) and no part of the duty",
                      "regulated": {"role": "obligation", "default": "deny",
                                    "act": "{0} be reviewed at least once a year as to its continued sufficiency"}},
    "adjustment_permission": {"arguments": ["situation"], "description": "{0} may have its required safeguards in that capability area adjusted (4.3)",
                              "regulated": {"role": "permission", "default": "allow",
                                            "act": "{0} have its required safeguards in that capability area adjusted"}},
}

ACTS = {
    "misuse_safeguards": ("{0} have misuse safeguards meeting the High standard",
                          "Table 1 CYB-H: safeguards against misuse meeting High standard (Appendix C.1)"
                          "; Appendix C.1: “Safeguards should sufficiently minimize the risk of severe harm "
                          "associated with misuse of the model’s capabilities.” “This can be done by establishing "
                          "that all plausible known vectors of enabling severe harm are sufficiently addressed by "
                          "one or more of the following claims:” “Robustness: Users cannot use the model to cause "
                          "the harm because they cannot elicit the capability, such as because the model is modified "
                          "to refuse to provide assistance to harmful tasks and is robust to jailbreaks that would "
                          "circumvent those refusals.” “Usage Monitoring: If a model does not refuse and provides "
                          "assistance to harmful tasks, monitors can stop or catch adversarial users before their "
                          "misuse has achieved an unacceptable scale of harm, through a combination of automated and "
                          "human detection and enforcement within an acceptable time frame.” “Trust-based Access: "
                          "The actors who gain access to the model will not use it in a way that presents an "
                          "associated risk of severe harm under our threat model.”; Appendix C.1, Table 4 "
                          "(illustrative): “Blocking access for users and organizations that violate our usage "
                          "policies, leading to potential permanent bans”; 4.2: “Robustness: Malicious users cannot "
                          "use the model to cause the severe harm because they cannot elicit the necessary "
                          "capability, such as because the model is modified to refuse to provide assistance to "
                          "harmful tasks and is robust to jailbreaks that would circumvent those refusals.”"),
    "misuse_safeguards_before_external": ("{0} have misuse safeguards meeting the High standard before external "
                                          "deployment",
                                          "Table 1 BIO-H: safeguards against misuse meeting High standard (Appendix "
                                          "C.1)"),
    "security_controls": ("{0} have security controls meeting the High standard",
                          "Table 1: security controls meeting High standard (Appendix C.3)"),
    "alignment_safeguards": ("{0} have misalignment safeguards meeting the High standard",
                             "Table 1 CYB-H: safeguards meeting High standard against misalignment (Appendix C.2)"
                             "; Appendix C.2: “In addition to human misuse, several of the Tracked Category "
                             "capabilities pose risks when models themselves are able to autonomously execute a "
                             "severe harm, whether due to misalignment or subversion by an adversary.” “This can be "
                             "done by establishing that all plausible known vectors of enabling severe harm are "
                             "sufficiently addressed by one or more of the following claims:” “System Architecture: "
                             "The model can’t take actions that cause harm because it lacks access to output "
                             "channels or mechanisms to persist sufficiently to execute the harm, due to "
                             "containerization and restricted permissions.” “These misalignment claims may be "
                             "further complemented by the safeguards applied towards the malicious-actor-oriented "
                             "“Robustness” and “Usage Monitoring” claims, which similarly limit a misaligned model’s "
                             "use of its own or another model’s capabilities.”; Appendix C.2, Table 5 "
                             "(illustrative): “Evidence of taking harmful actions, including deception and scheming, "
                             "would be evidence of misalignment” “Large scale usage or testing in realistic settings "
                             "should show the model consistently takes action aligned to the user’s instructions or "
                             "goals (while maintaining value alignment and avoiding harm).” “Examples against would "
                             "include trying to escape a container, lying to the user to appease them, etc.” "
                             "“Red-teamers can train an arbitrarily adversarial agent or can pretend to be an agent "
                             "in our setup and we should ensure that harmful behaviors are detected by monitors with "
                             "a high recall rate”"),
    "halt_development": ("{0} halt further development", "Table 1: halt further development at Critical"),
    "safeguards_before_deployment": ("{0} have safeguards sufficiently minimizing severe-harm risk before deployment",
                                     "1, 2.2, 4.2: robust and effective safeguards that sufficiently minimize the "
                                     "associated risk of severe harm before deployment"),
    "safeguards_during_development": ("{0} have sufficient additional safety plus security controls during development",
                                      "4.4: “Such models require additional safeguards (safety and security "
                                      "controls) during development, regardless of whether or when they are "
                                      "externally deployed.”, such models being those that have reached or are "
                                      "forecasted to reach Critical capability in a Tracked Category; 4.2: “Systems "
                                      "that reach Critical capability also require safeguards that sufficiently "
                                      "minimize associated risks during development.”; Appendix C: “Systems that "
                                      "reach Critical capability also require sufficient safeguards during "
                                      "development.” (the act's plus stands for and, a word an act may not use; no "
                                      "coverage condition: none of the three sentences states one)"),
    "safeguards_before_internal_use": ("{0} have additional safety as well as security controls before internal use",
                                       "4.4, its heading “Increasing safeguards before internal use and further "
                                       "development” read under RS18 = inuse: models that have reached or are "
                                       "forecasted to reach Critical capability in a Tracked Category require "
                                       "additional safeguards (safety and security controls) before internal use"),
    "development_security_controls": ("{0} have appropriate security controls during its development",
                                      "2.2: appropriate security controls as covered High systems are developed"),
    "security_practices": ("{0} have security practices", "C.3: required High-level security practices"
                           "; Appendix C.3: “Robust security practices and controls are essential to mitigating "
                           "risks associated with the deployment of models reaching High capability thresholds.” "
                           "“Our security approach integrates industry best practices with OpenAI-specific "
                           "innovations tailored to manage the unique threats posed by frontier AI technologies.” "
                           "“Our security practices are designed to protect against external and internal "
                           "adversaries and align with established frameworks such as ISO 27001, SOC2, NIST SP "
                           "800-53, and FedRAMP.” “While nascent, AI-specific security standards may also provide "
                           "frameworks for addressing security and regulatory standards that address the unique "
                           "challenges of securing AI systems.” “This may include efforts emerging from the Cloud "
                           "Security Alliance’s AI Safety Initiative or the NIST SP 800-218 AI updates.” “We will "
                           "require the following practices for High capability models:” “Security Threat Modeling "
                           "and Risk Management – Comprehensive Security Threat Models: Ensure OpenAI employs "
                           "security threat modeling that systematically identifies and mitigates risks posed by "
                           "adversaries.” “These models address both external and internal threats, explicitly "
                           "mapping vulnerabilities and attack vectors relevant to frontier AI model access or "
                           "misuse. – Continuous Review and Iteration: Ensure security threat models are regularly "
                           "reviewed and updated.” “This includes updating the Security framework, policies, and "
                           "controls as technologies and threats evolve. – Continuous Monitoring and Validation: "
                           "Ensure security threat models and updates inform where security and data privacy "
                           "controls should be implemented, improved, and monitored to further reduce risk.” "
                           "“Internal and external assessments to validate these controls are conducted regularly "
                           "and reports are provided to OpenAI leadership.” “Defense in Depth – Layered Security "
                           "Architecture: Adopt a layered security strategy, ensuring robust protection through "
                           "multiple defensive barriers, including physical and datacenter security, network "
                           "segmentation and controls, workload isolation, data encryption, and other overlapping "
                           "and complementary security controls. – Zero Trust Principles: Embrace Zero Trust "
                           "principles in the design and operation of infrastructure, networks, and endpoints.” "
                           "“Leverage hardware-backed security and modern authentication standards and controls for "
                           "accessing critical resources and performing operations.” “Access Management – Principle "
                           "of Least Privilege: Ensure access to systems and data is limited based on job functions, "
                           "need-to-know, and operational requirements in alignment with the principles of least "
                           "privilege and separation of duties.” “Ensure all access is regularly audited and "
                           "reviewed.” “Identity and Device Management: Employees must authenticate using "
                           "multi-factor authentication (MFA) and managed devices meeting security baselines.” "
                           "“Access must be logged and reviewed for detection and investigative purposes.” “Secure "
                           "Development and Supply Chain – Secure Development Lifecycle: Integrate automated code "
                           "analysis, formal security reviews, and penetration testing in engineering processes.” "
                           "“Apply security reviews and validation to higher-sensitivity critical components prior "
                           "to deployment. – Change Management: Establish and maintain a formal change management "
                           "process to ensure that all modifications to systems, applications, and infrastructure "
                           "are properly authorized, documented, tested, and approved before deployment.” “Changes "
                           "to critical infrastructure should undergo multi-person approval and review.” “This "
                           "process should include maintaining comprehensive records of changes and implementing "
                           "rollback procedures to revert to previous states.” “– Software Supply Chain Integrity: "
                           "Enforce supply chain security measures, including sourcing hardware and software from "
                           "reputable sources, and continuous vetting and monitoring of third-party suppliers and "
                           "software libraries.” “Operational Security – Monitoring and Incident Response: Monitor "
                           "security and event logs continuously to detect, triage, and respond to security "
                           "incidents rapidly by 24x7 on-call staff. – Vulnerability Management: Ensure known "
                           "vulnerabilities are addressed through consistent patching and corrective actions, "
                           "minimizing exploitation opportunities. – Adversarial Testing and Red-Teaming: Conduct "
                           "adversarial testing and red-teaming exercises to proactively identify and mitigate "
                           "potential vulnerabilities within corporate, research, and product systems, ensuring "
                           "resilience against unknown vulnerabilities and emerging threats.” “Encourage reporting "
                           "of good-faith security research through bug bounty programs.” “Auditing and Transparency "
                           "– Independent Security Audits: Ensure security controls and practices are validated "
                           "regularly by third-party auditors to ensure compliance with relevant standards and "
                           "robustness against identified threats. – Transparency in Security Practices: Ensure "
                           "security findings, remediation efforts, and key metrics from internal and independent "
                           "audits are periodically shared with internal stakeholders and summarized publicly to "
                           "demonstrate ongoing commitment and accountability. – Governance and Oversight: Ensure "
                           "that management provides oversight over the information security and risk management "
                           "programs.”"),
    "evaluations_before_deployment": ("{0} undergo the suite of Scalable Evaluations prior to deployment",
                                      "3.3: \u201cPrior to deployment, every covered model undergoes the suite of "
                                      "Scalable Evaluations.\u201d"
                                      "; 3.1: “Scalable Evaluations: automated evaluations designed to measure "
                                      "proxies that approximate whether a capability threshold has been crossed.” "
                                      "“Scalable evaluations have associated “indicative thresholds,” which are "
                                      "levels of performance that we have pre-determined to indicate that a "
                                      "deployment may have reached a capability threshold.” “Deep Dives: designed to "
                                      "provide additional evidence validating the scalable evaluations’ findings on "
                                      "whether a capability threshold has been crossed.”; change log item 6: “We "
                                      "also define “scalable evaluations,” which are automated, and distinguish "
                                      "these from “deep dive” evaluations that may include consultation with human "
                                      "experts and are designed in part to validate the scalable evaluations.”"),
    "capabilities_report": ("{0} have SAG review the Capabilities Report as well as decide on next steps",
                            "3.3: the SAG reviews the Capabilities Report and decides on next steps"),
    "capabilities_report_submitted": ("{0} have results compiled into a Capabilities Report submitted to the SAG",
                                      "3.3: the Scalable Evaluations' results and any noteworthy observations that should "
                                      "affect their interpretation are compiled into a Capabilities Report submitted to the SAG"),
    "safeguard_work": ("{0} start safeguard work to sufficiently reduce the threshold's severe-harm risk",
                       "4: work on safeguards to sufficiently reduce the risks of severe harm associated with that "
                       "threshold, even before a formal capability determination"),
    "safeguards_report": ("{0} have planned safeguard information compiled into a Safeguards Report",
                          "4.2: \u201cWe compile the information on the planned safeguards needed to minimize the "
                          "risk of severe harm into a Safeguards Report.\u201d (section 4: for covered systems that "
                          "reach a capability threshold)"),
    "risk_paths": ("{0} identify plausible ways severe harm can arise in the proposed deployment",
                   "4.1: “We use the following process to select safeguards for a deployment: • We first "
                   "identify the plausible ways in which the associated risk of severe harm can come to fruition in "
                   "the proposed deployment.” (the first step; 'first' is in this legend only, as the act with it "
                   "would pass the 80-character limit; the order it states before the next step is event order, "
                   "not formalised: ET, as PLAN O7)"),
    "specific_safeguards_per_path": ("{0} identify specific safeguards that would address each risk path",
                                     "4.1: “• For each of those, we then identify specific safeguards that "
                                     "either exist or should be implemented that would address the risk.” (the "
                                     "second step; 'then' is in this legend only, a word an act may not use; the "
                                     "order it states after the first step is event order, not formalised: ET, as "
                                     "PLAN O7; the per-item scope stays SC-blocked)"),
    "efficacy_methods_per_safeguard": ("{0} identify efficacy methods per safeguard",
                                       "4.1: \u201cFor each identified safeguard, we identify methods to measure "
                                       "their efficacy\u201d (the third safeguard-selection step)"),
    "efficacy_threshold_per_safeguard": ("{0} identify an efficacy threshold per safeguard", "4.1: third safeguard-selection step"),
    "validate_evidence": ("{0} validate the evidence", "4.2: evidence safeguards fail"),
    "review_sufficiency": ("{0} review safeguard sufficiency", "4.2: review sufficiency"),
    "research_review": ("{0} review the latest research as well as findings in each Research Category",
                        "2.3: \u201cWe will periodically review the latest research and findings for each Research "
                        "Category.\u201d (the periodicity stays ET-blocked)"),
    "decision_documented": ("{0} have reports to SAG as well as SAG decisions with reasoning documented",
                            "5.1: relevant reports made to the SAG and the SAG's decision and reasoning"),
    "noncompliance_investigated": ("{0} have potential noncompliance tracked as well as appropriately investigated",
                                   "5.1: track and appropriately investigate potential noncompliance"),
    "corrective_action": ("{0} take appropriate as well as proportional corrective action",
                          "5.1: appropriate and proportional corrective action where reports are substantiated"),
    "public_disclosure": ("{0} have Preparedness Framework results publicly released",
                          "5.2: it includes the scope of testing performed, capability evaluations for each Tracked "
                          "Category, the reasoning for the deployment decision, and any other context about the model's "
                          "development or capabilities that was decisive in the decision to deploy; it may be redacted "
                          "or summarized where necessary, such as to protect intellectual property or safety"),
    "safeguards_disclosed": ("{0} disclose safeguards implemented to sufficiently minimize associated risks",
                             "5.2: information about the safeguards implemented to sufficiently minimize the "
                             "associated risks; it may be redacted or summarized where necessary, such as to protect "
                             "intellectual property or safety"),
    "sag_recommendation": ("{0} have SAG next-step recommendations with risks as well as rationale sent",
                           "Appendix B: recommendations on potential next steps and any applicable risks, as well "
                           "as rationale, provided to OpenAI Leadership"),
    "ssc_visibility": ("{0} give SSC visibility into processes", "Appendix B: SSC is the Safety and Security Committee of the OpenAI Board of Directors"),
    "recommendation_informed": ("{0} have Leadership informed by SAG", "Appendix B: SAG recommendation"),
    "misalignment_risk_minimized": ("{0} have safeguards that sufficiently minimize misaligned-model severe-harm risk",
                                    "C.2: “Safeguards should sufficiently minimize the risk associated with a "
                                    "misaligned model circumventing human control and oversight and executing severe "
                                    "harms.”"),
    "tracking": ("{0} have the category tracked", "2.1: Tracked Category criteria"),
    "coverage_decided": ("{0} have SAG make the final coverage determination", "3.2: ambiguous coverage"),
    "checkpoint_selected": ("{0} have an appropriate development checkpoint selected to be covered",
                            "3.2: an appropriate checkpoint during development, covered by the Framework"),
    "additional_safety_measures": ("{0} require additional safety measures", "footnote 6: ordinarily no additional measures"),
    "adjustment_acknowledged": ("{0} have its adjustment publicly acknowledged", "4.3: adjustment condition"),
    "more_protective": ("{0} keep safeguards more protective than the other developer's", "4.3: adjustment condition"),
    "validation_shared": ("{0} have validation information shared", "4.3: adjustment condition"),
    "misalignment_report": ("{0} have a misalignment safeguards report", "Table 2: Long-range Autonomy response"),
    "sandbagging_response": ("{0} have sandbagging handled",
                             "Table 2, Sandbagging: \u201cAdopt elicitation approach that overcomes sandbagging, or use "
                             "a conservative upper bound of the model\u2019s non-sandbagged evaluation results\u201d: the "
                             "one duty is met by either alternative, an elicitation approach that overcomes sandbagging "
                             "or a conservative upper bound of the model's non-sandbagged evaluation results"),
    "ara_tracking": ("{0} have the research category tracked", "Table 2: ARA response"),
    "robust_case": ("{0} have a safeguards case robust to what was discovered",
                    "Table 2, Undermining Safeguards: \u201cIf a model has High or Critical capabilities in any of the "
                    "Tracked Categories, require the Safeguards case to be robust to the discovered capability and/or "
                    "propensity\u201d: what was discovered is the capability, the propensity, or both"),
    "nuclear_safeguards": ("{0} heighten safeguards consulting appropriate US government actors",
                           "Table 2: Nuclear and Radiological: heighten safeguards (and consider further actions) in "
                           "consultation with appropriate US government actors, accounting for the complexity of "
                           "classified information handling; the further actions remain open"),
    "pandemic_policy_contribution": ("{0} contribute towards improved public policy as well as pandemic preparedness",
                                     "Table 1 BIO-C: policy contribution"),
    "cyberdefense_contribution": ("{0} contribute to improved cyberdefense policies as well as cyberdefense tools",
                                  "Table 1 CYB-H: \u201cContribute towards improved cyberdefense policies and tools "
                                  "for cyberdefense\u201d"),
    "safeguards_recommended": ("{0} have the SAG recommend implementing as well as assessing the safeguards",
                               "3.3: the first next step the SAG's decision can include"),
    "chair_coordination": ("{0} have the SAG Chair coordinate with OpenAI Leadership on immediate reaction",
                           "Appendix B, Fast-track: “The SAG Chair should also coordinate with OpenAI Leadership "
                           "for immediate reaction as needed to address the risk.”"),
    "third_party_evaluation": ("{0} work with third parties to independently evaluate the model",
                               "5.2: “If we deem that a deployment warrants deeper testing of Tracked Categories "
                               "of capability (as described in Section 3.1), for example based on results of "
                               "Capabilities Report presented to them, then when available and feasible, OpenAI will "
                               "work with third-parties to independently evaluate models.” (the act is OpenAI's "
                               "work with third parties, not a required result; the guards carry the deeming about a "
                               "deployment, OT14, and 'when available and feasible')"),
    "residual_risk_assessment": ("{0} include an assessment of residual severe-harm risk in the Safeguards Report",
                                 "4.2: an assessment on the residual risk of severe harm based on the deployment"),
    "persuasion_handled_outside": ("{0} have persuasion risks handled outside the Preparedness Framework",
                                   "change log item 4: including via the Model Spec and policy prohibitions on the use "
                                   "of OpenAI's tools for political campaigning or lobbying, and ongoing investigations "
                                   "of misuse of its products (including detecting and disrupting influence operations)"),
    "sag_participation": ("{0} have the SAG take part in the decision",
                          "Appendix B: OpenAI Leadership “can also make decisions without the SAG's participation, "
                          "i.e., the SAG does not have the ability to ‘filibuster’”"),
    "access_limited": ("{0} have model access strictly limited with strong multifactor authentication",
                       "C.3: access for all models"),
    "research_results_received": ("{0} have SAG receive the research results", "2.3: SAG receives Research Category review results"),
}


def environment():
    return {"language": LANGUAGE, "profiles": ["norms@0", "relational-fol@0", "soft-norms@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {k: {"description": v} for k, v in {
                "situation": "a development, use, deployment, review or decision of a model",
                "level": "one of Table 1's six named capability levels",
                "category": "one of the three Tracked Categories; 2.1: “Tracked Categories are those capabilities "
                            "which we track most closely, measuring them during each covered deployment and "
                            "preparing safeguards for when a threshold level is crossed.”",
                "proposal": "a safeguard or governance proposal",
                "requirement": "a stated safeguard requirement",
                "capability": "a frontier capability considered for a Tracked Category",
                "evaluation": "a capability evaluation (footnote 5)",
                "framework": "the Preparedness Framework (version 2, last updated 15 April 2025), the one member of "
                             "this sort: Appendix B's yearly review is of it",
            }.items()},
                "predicates": {**BASE, **{name: duty(*pair) for name, pair in ACTS.items()}},
                "constants": {**{k: {"sort": "level", "description": f"Table 1: {c}, {g}; {LEVEL_TEXT[k]}"}
                                 for k, (c, g) in LEVELS.items()},
                              **{c: {"sort": "category", "description": f"Tracked Category {c}; {CATEGORY_TEXT[c]}"}
                                 for c in sorted({pair[0] for pair in LEVELS.values()})},
                              "biological_capability_evaluations": {
                                  "sort": "evaluation", "description": "footnote 5: Biological capability evaluations"}}}}


def text():
    return json.dumps(environment(), indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    (HERE / "environment.d1.json").write_text(text())
