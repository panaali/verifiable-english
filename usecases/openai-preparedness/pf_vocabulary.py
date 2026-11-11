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
    "covered": base(["situation"], "the model at {0} is covered by the Framework"),
    "likely_to_cross": base(["situation"], "the covered system at {0} appears likely to cross a capability threshold; "
                                                 "OpenAI ('we') decides this (OT9)"),
    "reasonable_evidence": base(["situation"], "there is reasonable evidence that safeguards are not working at {0}"),
    "adjustment_conditions": base(["situation"], "4.3's conditions for adjusting the safeguards required in that "
                                       "capability area hold at {0}: the adjustment does not meaningfully increase the overall risk of "
                                       "severe harm, is publicly acknowledged, and keeps safeguards more protective than the other "
                                       "developer's, with information shared to validate it; their assessment is open"),
    "sufficient_safeguards": base(["situation"], "safeguards sufficiently minimize severe-harm risk at {0}; SAG decides this"),
    "major_deployment": base(["situation"], "{0} is a major deployment; the decider is unstated (OT13)"),
    "safeguard_selection": base(["situation"], "{0} is the selection of safeguards for a deployment"),
    "substantiated_noncompliance": base(["situation"], "a noncompliance report at {0} is substantiated"),
    "external_deployment": base(["situation"], "{0} is an external deployment"),
    "framework_deployment": base(["situation"], "{0} is a deployment under the Preparedness Framework"),
    "misaligned_model_risk": base(["situation"], "{0} has a risk of a misaligned model circumventing human control and "
                                      "oversight and executing severe harms"),
    "large_scale_internal": base(["situation"], "{0} is a large-scale internal deployment"),
    "critical_standard_unspecified": base(["situation"], "the Critical standard has not yet been specified at {0}"),
    "in_category": base(["level", "category"], "{0} is in Tracked Category {1}", "{0} concerns {1}"),
    "high": base(["level"], "{0} is a High level", "{0} is high"),
    "critical": base(["level"], "{0} is a Critical level", "{0} is critical"),
    "reached": base(["situation", "level"], "the model at {0} has reached {1}; SAG decides this", "{0} has reached {1}"),
    "proposed": base(["proposal"], "{0} is proposed"),
    "required": base(["requirement"], "{0} is a requirement"),
    "coverage_ambiguous": base(["situation"], "coverage of {0} is ambiguous"),
    "forecast_severe_before_deployment": base(["situation"], "forecasts and threat models justify a severe-risk development checkpoint at {0}"),
    "distilled_from_below_high": base(["situation"], "{0} derives from a model determined below High"),
    "significant_increase": base(["situation"], "there is reason to believe at {0} that a significant increase in capability "
                                     "has occurred; OpenAI ('we') decides this (OT20)"),
    "adjustment_confirmed": base(["situation"], "it is rigorously confirmed at {0} that another frontier AI developer "
                                     "developed or released a system with High or Critical capability in a Tracked Category without "
                                     "comparable safeguards"),
    "adjustment_made": base(["situation"], "OpenAI makes 4.3's marginal-risk adjustment at {0}: it adjusts the level "
                                "of safeguards it requires in that capability area"),
    "lra_found": base(["situation"], "Long-range Autonomy is found at {0}"),
    "sandbagging_found": base(["situation"], "sandbagging is found at {0}"),
    "ara_found": base(["situation"], "Autonomous Replication and Adaptation is found at {0}"),
    "undermining_found": base(["situation"], "undermining of safeguards is found at {0}"),
    "nuclear_found": base(["situation"], "Nuclear and Radiological capability is found at {0}"),
    "further_development": base(["situation"], "{0} is further development of the model"),
    "internal_deployment": base(["situation"], "{0} is an internal deployment"),
    "forecast_critical": base(["situation"], "the model at {0} is forecasted to reach Critical capability; OpenAI decides this"),
    "existing_at_publication": base(["situation"], "the model at {0} is one OpenAI possessed at publication (2025-04-15)"),
    "threshold_determined": base(["situation"], "the SAG determines at {0} that a capability threshold has been crossed"),
    "safeguards_already_assessed": base(["situation"], "the corresponding safeguards at {0} have already been implemented and assessed"),
    "rapid_risk": base(["situation"], "a risk of severe harm rapidly develops at {0}"),
    "fast_track_requested": base(["situation"], "a fast track for the SAG is requested at {0}"),
    "immediate_reaction_needed": base(["situation"], "immediate reaction is needed to address the risk at {0}"),
    "deeper_testing_warranted": base(["situation"], "OpenAI deems that {0} warrants deeper testing of Tracked Categories"),
    "third_party_available": base(["situation"], "third-party evaluation is available and feasible at {0}"),
    "safeguards_report_compiled": base(["situation"], "{0} is the compilation of a Safeguards Report"),
    "employee_request": base(["situation"], "an employee requests a summary of the testing results and SAG recommendation at {0}"),
    "beyond_sensitive_limits": base(["situation"], "the summary requested at {0} goes beyond the limits set for highly "
                                                   "sensitive information (5.1)"),
    "potential_noncompliance": base(["situation"], "{0} is a reported or otherwise identified potential instance of "
                                                   "noncompliance with the Framework (5.1)"),
    "conservative_upper_bound_used": base(["situation"], "a conservative upper bound of the model's non-sandbagged "
                                                         "evaluation results is used at {0} (Table 2)"),
    "persuasion_risk": base(["situation"], "{0} concerns risks related to persuasion"),
    "leadership_decision": base(["situation"], "{0} is a final decision of OpenAI Leadership"),
    "board_finds_necessary": base(["situation"], "the Board finds it necessary at {0} to act on the decision (Appendix B)"),
    "decided_without_sag": base(["situation"], "OpenAI Leadership makes the decision at {0} without the SAG's participation"),
    "research_category_review": base(["situation"], "{0} is a Research Category review"),
    "plausible": base(["capability"], "{0} meets the plausible-pathway criterion"),
    "measurable": base(["capability"], "{0} meets the measurable criterion"),
    "severe": base(["capability"], "{0} meets the severe-harm criterion"),
    "net_new": base(["capability"], "{0} meets the net-new criterion"),
    "irremediable": base(["capability"], "{0} meets the instantaneous-or-irremediable criterion"),
    "criteria_tracking": {"arguments": ["capability"], "description": "{0} is tracked as a category",
                          "regulated": {"role": "obligation", "default": "deny",
                                        "act": "{0} be tracked as a category", "permission": "criteria_exclusion"}},
    "criteria_exclusion": {"arguments": ["capability"], "description": "{0} may be tracked as a category",
                            "regulated": {"role": "permission", "default": "allow",
                                          "act": "{0} be tracked as a category"}},
    "deployment_permitted": permission("{0} be deployed", "1: deployment of a model that reaches High"),
    "summary_access": permission("{0} have an employee request as well as receive a summary of testing results",
                                 "5.1: internal transparency"),
    "decision_reversal": permission("{0} have the decision reversed by the Board",
                                    "Appendix B: the Board may reverse a decision of OpenAI Leadership"),
    "revised_course_mandated": permission("{0} have a revised course of action mandated by the Board",
                                          "Appendix B: the Board may mandate a revised course of action"),
    "adjustment_permission": {"arguments": ["situation"], "description": "{0} may have its required safeguards in that capability area adjusted (4.3)",
                              "regulated": {"role": "permission", "default": "allow",
                                            "act": "{0} have its required safeguards in that capability area adjusted"}},
}

ACTS = {
    "misuse_safeguards": ("{0} have misuse safeguards meeting the High standard",
                          "Table 1 BIO-H and CYB-H: safeguards against misuse meeting High standard (Appendix C.1)"),
    "security_controls": ("{0} have security controls meeting the High standard",
                          "Table 1: security controls meeting High standard (Appendix C.3)"),
    "alignment_safeguards": ("{0} have misalignment safeguards meeting the High standard",
                             "Table 1 CYB-H: safeguards meeting High standard against misalignment (Appendix C.2)"),
    "halt_development": ("{0} halt further development", "Table 1: halt further development at Critical"),
    "safeguards_before_deployment": ("{0} have safeguards sufficiently minimizing severe-harm risk before deployment",
                                     "1, 2.2, 4.2: robust and effective safeguards that sufficiently minimize the "
                                     "associated risk of severe harm before deployment"),
    "safeguards_during_development": ("{0} have sufficient safety as well as security controls during development",
                                      "4.4 and Appendix C: sufficient safeguards (safety and security controls) "
                                      "during development"),
    "development_security_controls": ("{0} have appropriate security controls during its development",
                                      "2.2: appropriate security controls as covered High systems are developed"),
    "security_practices": ("{0} have security practices", "C.3: required High-level security practices"),
    "evaluations_before_deployment": ("{0} undergo evaluations before deployment", "3.3: Scalable Evaluations before deployment"),
    "capabilities_report": ("{0} have SAG review the Capabilities Report as well as decide on next steps",
                            "3.3: the SAG reviews the Capabilities Report and decides on next steps"),
    "capabilities_report_submitted": ("{0} have results compiled into a Capabilities Report submitted to the SAG",
                                      "3.3: the Scalable Evaluations' results and any noteworthy observations that should "
                                      "affect their interpretation are compiled into a Capabilities Report submitted to the SAG"),
    "safeguard_work": ("{0} start safeguard work to sufficiently reduce the threshold's severe-harm risk",
                       "4: work on safeguards to sufficiently reduce the risks of severe harm associated with that "
                       "threshold, even before a formal capability determination"),
    "safeguards_report": ("{0} have a Safeguards Report", "4.1 and 4.2"),
    "risk_paths": ("{0} identify plausible ways severe harm can arise in the proposed deployment",
                   "4.1: the plausible ways in which the associated risk of severe harm can come to fruition in the "
                   "proposed deployment"),
    "specific_safeguards_per_path": ("{0} identify specific safeguards that would address each risk path",
                                     "4.1: specific safeguards that either exist or should be implemented that would "
                                     "address the risk"),
    "efficacy_methods_per_safeguard": ("{0} identify efficacy methods per safeguard", "4.1: third safeguard-selection step"),
    "efficacy_threshold_per_safeguard": ("{0} identify an efficacy threshold per safeguard", "4.1: third safeguard-selection step"),
    "validate_evidence": ("{0} validate the evidence", "4.2: evidence safeguards fail"),
    "review_sufficiency": ("{0} review safeguard sufficiency", "4.2: review sufficiency"),
    "research_review": ("{0} have research categories reviewed", "2.3: periodic review"),
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
    "annual_review": ("{0} have an annual review", "Appendix B: at least once a year"),
    "misalignment_risk_minimized": ("{0} have safeguards that sufficiently minimize misaligned-model severe-harm risk",
                                    "C.2: the risk of a misaligned model circumventing human control and oversight "
                                    "and executing severe harms"),
    "tracking": ("{0} have the category tracked", "2.1: Tracked Category criteria"),
    "coverage_decided": ("{0} have SAG make the final coverage determination", "3.2: ambiguous coverage"),
    "checkpoint_selected": ("{0} have an appropriate development checkpoint selected to be covered",
                            "3.2: an appropriate checkpoint during development, covered by the Framework"),
    "additional_safety_measures": ("{0} require additional safety measures", "footnote 6: ordinarily no additional measures"),
    "adjustment_acknowledged": ("{0} have its adjustment publicly acknowledged", "4.3: adjustment condition"),
    "more_protective": ("{0} keep safeguards more protective than the other developer's", "4.3: adjustment condition"),
    "validation_shared": ("{0} have validation information shared", "4.3: adjustment condition"),
    "misalignment_report": ("{0} have a misalignment safeguards report", "Table 2: Long-range Autonomy response"),
    "sandbagging_bound": ("{0} adopt an elicitation approach that overcomes sandbagging",
                          "Table 2: Sandbagging response; the alternative, a conservative upper bound, is the "
                          "rule's carve-out"),
    "ara_tracking": ("{0} have the research category tracked", "Table 2: ARA response"),
    "robust_case": ("{0} have a safeguards case robust to discovered capability as well as propensity",
                    "Table 2: Undermining Safeguards: robust to the discovered capability and/or propensity"),
    "nuclear_safeguards": ("{0} heighten safeguards consulting appropriate US government actors",
                           "Table 2: Nuclear and Radiological: heighten safeguards (and consider further actions) in "
                           "consultation with appropriate US government actors, accounting for the complexity of "
                           "classified information handling; the further actions remain open"),
    "pandemic_policy_contribution": ("{0} contribute towards improved public policy as well as pandemic preparedness",
                                     "Table 1 BIO-C: policy contribution"),
    "cyberdefense_contribution": ("{0} contribute towards improved cyberdefense policies as well as tools",
                                  "Table 1 CYB-H: cyberdefense contribution"),
    "safeguards_recommended": ("{0} have the SAG recommend implementing as well as assessing the safeguards",
                               "3.3: the first next step the SAG's decision can include"),
    "chair_coordination": ("{0} have the SAG Chair coordinate with OpenAI Leadership on immediate reaction",
                           "Appendix B: fast track"),
    "third_party_evaluation": ("{0} have third parties independently evaluate the model",
                               "5.2: third-party evaluation of tracked model capabilities"),
    "residual_risk_assessment": ("{0} include an assessment of residual severe-harm risk in the Safeguards Report",
                                 "4.2: an assessment on the residual risk of severe harm based on the deployment"),
    "persuasion_handled_outside": ("{0} have persuasion risks handled outside the Preparedness Framework",
                                   "change log item 4: including via the Model Spec and policy prohibitions on the use "
                                   "of OpenAI's tools for political campaigning or lobbying, and ongoing investigations "
                                   "of misuse of its products (including detecting and disrupting influence operations)"),
    "sag_participation": ("{0} have the SAG take part in the decision", "Appendix B: decisions without the SAG"),
    "access_limited": ("{0} have model access strictly limited with strong multifactor authentication",
                       "C.3: access for all models"),
    "research_results_received": ("{0} have SAG receive the research results", "2.3: SAG receives Research Category review results"),
}


def environment():
    return {"language": LANGUAGE, "profiles": ["norms@0", "relational-fol@0", "soft-norms@0"],
            "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {k: {"description": v} for k, v in {
                "situation": "a development, use, deployment, review or decision of a covered model",
                "level": "one of Table 1's six named capability levels",
                "category": "one of the three Tracked Categories",
                "proposal": "a safeguard or governance proposal",
                "requirement": "a stated safeguard requirement",
                "capability": "a frontier capability considered for a Tracked Category",
            }.items()},
                "predicates": {**BASE, **{name: duty(*pair) for name, pair in ACTS.items()}},
                "constants": {**{k: {"sort": "level", "description": f"Table 1: {c}, {g}"}
                                 for k, (c, g) in LEVELS.items()},
                              **{c: {"sort": "category", "description": f"Tracked Category {c}"}
                                 for c in sorted({pair[0] for pair in LEVELS.values()})}}}}


def text():
    return json.dumps(environment(), indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    (HERE / "environment.d1.json").write_text(text())
