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


def duty(act, description):
    return {"arguments": ["situation"], "description": description,
            "regulated": {"role": "obligation", "default": "deny", "act": act}}


BASE = {
    "covered": base(["situation"], "the model at {0} is covered by the Framework"),
    "high_capability": base(["situation"], "the model at {0} reaches a High capability threshold; SAG decides this"),
    "critical_capability": base(["situation"], "the model at {0} reaches a Critical capability threshold; SAG decides this"),
    "likely_to_cross": base(["situation"], "the model at {0} appears likely to cross a threshold; SAG decides this"),
    "reasonable_evidence": base(["situation"], "there is reasonable evidence that safeguards are not working at {0}"),
    "adjustment_conditions": base(["situation"], "the three conditions of 4.3 hold at {0}; their assessment is open"),
    "sufficient_safeguards": base(["situation"], "safeguards sufficiently minimize severe-harm risk at {0}; SAG decides this"),
    "major_deployment": base(["situation"], "{0} is a major deployment; OpenAI decides this"),
    "safeguard_selection": base(["situation"], "{0} is the selection of safeguards for a deployment"),
    "substantiated_noncompliance": base(["situation"], "a noncompliance report at {0} is substantiated"),
    "external_deployment": base(["situation"], "{0} is an external deployment"),
    "framework_deployment": base(["situation"], "{0} is a deployment under the Preparedness Framework"),
    "misaligned_model_risk": base(["situation"], "{0} has a risk of a misaligned model circumventing human control and oversight"),
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
    "significant_increase": base(["situation"], "{0} has a significant capability increase"),
    "adjustment_confirmed": base(["situation"], "another developer's unsafeguarded High or Critical release is rigorously confirmed at {0}"),
    "adjustment_made": base(["situation"], "OpenAI adjusts safeguards at {0}"),
    "lra_found": base(["situation"], "Long-range Autonomy is found at {0}"),
    "sandbagging_found": base(["situation"], "sandbagging is found at {0}"),
    "ara_found": base(["situation"], "Autonomous Replication and Adaptation is found at {0}"),
    "undermining_found": base(["situation"], "undermining of safeguards is found at {0}"),
    "nuclear_found": base(["situation"], "Nuclear and Radiological capability is found at {0}"),
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
    "adjustment_permission": {"arguments": ["situation"], "description": "{0} may have safeguards adjusted",
                              "regulated": {"role": "permission", "default": "allow",
                                            "act": "{0} have its required safeguards adjusted"}},
}

ACTS = {
    "misuse_safeguards": ("{0} have misuse safeguards", "Table 1: misuse safeguards for deployment"),
    "security_controls": ("{0} have security controls", "Table 1 and C.3: security controls"),
    "alignment_safeguards": ("{0} have misalignment safeguards", "Table 1: CYB-H large-scale internal safeguards"),
    "halt_development": ("{0} halt further development", "Table 1: halt further development at Critical"),
    "safeguards_before_deployment": ("{0} have safeguards before deployment", "1, 2.2, 4.2: safeguards before deployment"),
    "safeguards_during_development": ("{0} have safeguards during development", "4.4: Critical safeguards during development"),
    "security_practices": ("{0} have security practices", "C.3: required High-level security practices"),
    "evaluations_before_deployment": ("{0} undergo evaluations before deployment", "3.3: Scalable Evaluations before deployment"),
    "capabilities_report": ("{0} have SAG review the Capabilities Report", "3.3: SAG reviews the report"),
    "safeguard_work": ("{0} start safeguard work", "4: work before formal determination"),
    "safeguards_report": ("{0} have a Safeguards Report", "4.1 and 4.2"),
    "risk_paths": ("{0} identify ways severe harm can arise", "4.1: first safeguard-selection step"),
    "specific_safeguards_per_path": ("{0} identify specific safeguards per risk path", "4.1: second safeguard-selection step"),
    "efficacy_methods_per_safeguard": ("{0} identify efficacy methods per safeguard", "4.1: third safeguard-selection step"),
    "efficacy_threshold_per_safeguard": ("{0} identify an efficacy threshold per safeguard", "4.1: third safeguard-selection step"),
    "validate_evidence": ("{0} validate the evidence", "4.2: evidence safeguards fail"),
    "review_sufficiency": ("{0} review safeguard sufficiency", "4.2: review sufficiency"),
    "research_review": ("{0} have research categories reviewed", "2.3: periodic review"),
    "decision_documented": ("{0} have the decision documented", "5.1: SAG documentation"),
    "noncompliance_investigated": ("{0} have noncompliance investigated", "5.1: noncompliance"),
    "corrective_action": ("{0} have corrective action taken", "5.1: substantiated noncompliance"),
    "public_disclosure": ("{0} have public disclosure", "5.2: major deployment disclosure"),
    "safeguards_disclosed": ("{0} have safeguards disclosed", "5.2: beyond High disclosure"),
    "sag_recommendation": ("{0} have SAG recommendations sent to Leadership", "Appendix B: SAG role"),
    "ssc_visibility": ("{0} give SSC visibility into processes", "Appendix B: SSC is the Safety and Security Committee of the OpenAI Board of Directors"),
    "recommendation_informed": ("{0} have Leadership informed by SAG", "Appendix B: SAG recommendation"),
    "annual_review": ("{0} have an annual review", "Appendix B: at least once a year"),
    "misalignment_risk_minimized": ("{0} have safeguards that sufficiently minimize misaligned-model risk", "C.2: safeguards against a misaligned model"),
    "tracking": ("{0} have the category tracked", "2.1: Tracked Category criteria"),
    "coverage_decided": ("{0} have SAG make the final coverage determination", "3.2: ambiguous coverage"),
    "checkpoint_selected": ("{0} have a development checkpoint selected", "3.2: forecast-based checkpoint"),
    "additional_safety_measures": ("{0} require additional safety measures", "footnote 6: ordinarily no additional measures"),
    "adjustment_acknowledged": ("{0} have its adjustment publicly acknowledged", "4.3: adjustment condition"),
    "more_protective": ("{0} keep safeguards more protective than the other developer's", "4.3: adjustment condition"),
    "validation_shared": ("{0} have validation information shared", "4.3: adjustment condition"),
    "misalignment_report": ("{0} have a misalignment safeguards report", "Table 2: Long-range Autonomy response"),
    "sandbagging_bound": ("{0} have sandbagging addressed", "Table 2: Sandbagging response; elicitation or conservative bound remains open"),
    "ara_tracking": ("{0} have the research category tracked", "Table 2: ARA response"),
    "robust_case": ("{0} have a safeguards case robust to the discovered capability", "Table 2: Undermining Safeguards response"),
    "nuclear_safeguards": ("{0} heighten nuclear safeguards", "Table 2: Nuclear response; consultation remains open"),
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
