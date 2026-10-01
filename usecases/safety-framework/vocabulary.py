"""The D1 vocabulary of the safety-framework case (PLAN sections 3.2 and 7).

`python usecases/safety-framework/vocabulary.py` writes `environment.d1.json`;
the test checks that the committed file equals this output. The completion
defaults are a forced choice (PLAN 3.3): the committed file says "deny" for
every regulated predicate, and the harness flips all of them to "allow" for the
second run. Every scored verdict is selection-based, so the two runs differ only
in completed outcomes (metric M7).

English wordings must pass VE's template linter, which accepts one adjective
after "is" or one verb between two arguments. A wording that cannot say what
the source says in one adjective has no verbalisation: VE then writes it as
`is classified as "<name>"`, and the name is the source's own phrase. The
description of each predicate is the legend a reader checks it against; open
terms name their decider (PLAN 3.2).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANGUAGE = "ve.core@0.2"
SPEC_REVISION = "ve-v0.2-expand2-2026-09-25"
PROFILES = ["norms@0", "relational-fol@0", "soft-norms@0"]

SORTS = {
    "proposal": "a proposed activity for a model at one moment: further development, an internal or external "
                "deployment, or a step of the framework's own process. Every rule speaks about every proposal",
    "level": "a capability level named by the framework (a Tracked or a Critical Capability Level)",
    "domain": "a risk domain named by the framework",
    "measure": "a security level, or a named group of security measures, that the framework recommends",
    "threat": "a source of risk that a security measure addresses",
}


def _base(args, description, verbalisation=None):
    entry = {"arguments": list(args), "description": description}
    if verbalisation is not None:
        entry["verbalisation"] = verbalisation
    return entry


def _open(args, description, decider, verbalisation=None, term=None):
    """An open-term predicate: VE never decides it; the case stipulates the decider's finding."""
    text = f"{description}. Open term {term}, decided by {decider}" if term else f"{description}. Decided by {decider}"
    return _base(args, text, verbalisation)


BASE = {
    # Level facts (CHECKED premises from the level tables and closure sentences).
    "critical": _base(["level"], "{0} is a Critical Capability Level (CCL): absent mitigation, "
                      "a model at it may pose heightened risk of severe harm (Glossary)", "{0} is critical"),
    "tracked": _base(["level"], "{0} is a Tracked Capability Level (TCL): absent mitigation, a model at it may pose "
                     "heightened risk of significant but not severe harm (Glossary)", "{0} is tracked"),
    "concerns": _base(["level", "domain"], "{0} is a level of the risk domain {1} (the section that defines it)",
                      "{0} concerns {1}"),
    "misuse": _base(["level"], "{0} is a misuse T/CCL: a level of the CBRN, cyber or harmful manipulation "
                    "domains (1.2, Section 2)", "{0} is misuse"),
    "ml_rd_and_misalignment": _base(["level"], "{0} is an ML R&D and misalignment T/CCL (1.2, Section 3)"),
    "recommends": _base(["level", "measure"], "the framework recommends {1} for models reaching {0} "
                        "(tables 2.2.1.a to 3.2.2.a)", "{0} recommends {1}"),
    "includes": _base(["measure", "measure"], "{0} includes {1} (2.1.1: Security Level 2+ adds measures to "
                      "RAND SL2)", "{0} includes {1}"),
    "addresses": _base(["measure", "threat"], "{0} is designed to address risks from {1} (2.1.1)",
                       "{0} addresses {1}"),
    # The model's state. OT1: whether a model has reached a level is decided by the developer.
    "reached": _open(["proposal", "level"], "the model of {0} has reached {1}, as the critical capability "
                     "assessment found", "the developer (\"we\", 1.3.2)", "{0} has reached {1}", "OT1"),
    "approaches": _open(["proposal", "level"], "the model of {0} has reached an alert threshold for {1}",
                        "the developer (\"we\", 1.3.2)", "{0} approaches {1}", "OT1"),
    "at_least_as_strong": _base(["measure", "measure"], "{0} is at least as strong as {1}. The text states no such "
                                "order (footnotes 12 and 13 say only \"may include\"); the vocabulary has the word "
                                "so that question S4 can be asked"),
    "applies": _base(["proposal", "measure"], "security mitigations reaching {1} have been applied to the "
                     "model weights of {0}", "{0} applies {1}"),
    # The activity proposed (Glossary, p. 19).
    "further_development": _base(["proposal"], "{0} is further development of the model"),
    "internal": _base(["proposal"], "{0} is an internal deployment: a release restricted to Google employees for "
                      "internal use", "{0} is internal"),
    "high_risk": _open(["proposal"], "{0} is a high-risk internal deployment: for use cases with the potential to "
                       "enable severe threat scenarios", "no one the text names (unstated)", term="OT7"),
    "external": _base(["proposal"], "{0} is an external deployment: a model release to entities outside Google",
                      "{0} is external"),
    "low_risk": _open(["proposal"], "{0} is a low-risk external deployment: a small scale and private release "
                      "restricted to particular external groups", "no one the text names (unstated)", term="OT8"),
    "first_deployment": _base(["proposal"], "{0} is the first external deployment of a new model"),
    "frontier": _open(["proposal"], "the model of {0} is a frontier AI model (Glossary definition)",
                      "no one the text names (unstated)", "{0} is frontier", "OT9"),
    "subsequent": _base(["proposal"], "{0} is an external deployment of a subsequent version of a model",
                        "{0} is subsequent"),
    "new_capabilities": _open(["proposal"], "the model of {0} has meaningful new capabilities or material "
                              "increases in performance", "the developer (\"we\")", term="OT10"),
    "could_undermine_justification": _open(["proposal"], "the capability increase of {0} could materially "
                                           "undermine the justification for why its risks are acceptable",
                                           "the developer (\"we believe\")", term="OT10"),
    "post_training_run_completed": _base(["proposal"], "a post-training run of the model of {0} has completed"),
    "material_safety_case_update": _base(["proposal"], "{0} is a material update to a safety case"),
    # Findings of the risk acceptance determination (1.3.5).
    "mitigates": _open(["proposal", "level"], "the deployment mitigations of {0} have brought the residual risk "
                       "from {1} (of harm, of severe harm or of significant harm, as the bullet for {1} says) to an "
                       "acceptable level", "the developer (\"We assess\", 1.3.5)", "{0} mitigates {1}", "OT2"),
    "unlikely_misalignment_propensities": _open(
        ["proposal"], "the model of {0} is very unlikely to possess the propensities that would be required for "
        "material risk of significant harm through misalignment risk", "the developer (\"we assess\")", term="OT6"),
    "security_assessed_adequate": _open(["proposal"], "the level of security applied to the model weights of {0} "
                                        "is assessed adequate", "the developer (\"we otherwise assess\")",
                                        term="OT4"),
    "open_release_benefits_outweigh_risks": _open(["proposal"], "the benefits of the open release of the model "
                                                  "weights of {0} outweigh the risks", "the developer (\"we assess\")",
                                                  term="OT5"),
    "like_public_models": _open(["proposal"], "the model of {0} does not possess capabilities meaningfully "
                                "different from other publicly available models that have weaker security applied",
                                "the developer (2.2)", term="OT16"),
    "governance_found_acceptable": _open(["proposal"], "the appropriate governance function has determined the "
                                         "residual risk of {0} to be acceptable",
                                         "the appropriate governance function (unnamed)", term="OT3"),
    "internal_risk_unacceptable_without_safeguards": _open(
        ["proposal"], "the risk assessment deems the residual risk of {0} from internal deployment unacceptable "
        "without additional safeguards", "the developer's periodic risk assessment (3.2.1)"),
    "unmitigated_public_safety_risk": _open(["proposal"], "the CCL that the model of {0} has reached poses an "
                                            "unmitigated and material risk to overall public safety",
                                            "the developer (\"we assess\", 5.2)", term="OT11"),
    "sharing_facilitates_safety": _open(["proposal"], "sharing information about {0} with government authorities "
                                        "will facilitate safety of frontier AI", "the developer (5.2)", term="OT11"),
    "adherence_undermined": _open(["proposal"], "at {0} there are reasonable grounds to believe the adequacy of the "
                                  "Framework or the adherence to it has been materially undermined",
                                  "the developer (\"we have reasonable grounds to believe\", 5.1)", term="OT13"),
    "circumvention_evidence": _base(["proposal"], "post-market monitoring of {0} shows that safeguards are being "
                                    "circumvented (a stipulated situation for gap G8; no rule mentions it)"),
}


def _obligation(args, act, description):
    return {"arguments": list(args), "description": description,
            "regulated": {"role": "obligation", "default": "deny", "act": act}}


REGULATED = {
    "assessed": _obligation(["proposal"], "{0} be preceded by a critical capability assessment",
                            "a critical capability assessment (CCA) of the model takes place before {0} (1.3.2)"),
    "modification_checked": _obligation(
        ["proposal"], "{0} be preceded by a determination of any substantial modification",
        "before {0}, the developer determines whether a substantial modification has been made (1.3.2)"),
    "further_assessed": _obligation(["proposal"], "{0} be preceded by a further critical capability assessment",
                                    "a further CCA takes place before {0} (1.3.2)"),
    "change_assessed": _obligation(
        ["proposal"], "{0} be followed by material capability change assessments on various checkpoints",
        "material capability change assessments on various checkpoints follow {0} (1.3.2); the checkpoints are "
        "part of the act, not a situation variable"),
    "proximity_assessed": _obligation(
        ["proposal", "level"], "{0} be followed by an assessment of proximity to {1} with a risk analysis",
        "the proximity of the model of {0} to {1} is assessed and the risk posed is analysed (1.3.3)"),
    "residual_assessed": _obligation(["proposal"], "{0} be subject to a residual risk assessment",
                                     "the model of {0} is subject to a residual risk assessment (1.3.4)"),
    "safety_case": _obligation(["proposal"], "{0} have its residual risk assessment informed by a safety case",
                               "the residual risk assessment for {0} is informed by a supplemental safety case "
                               "(1.3.4)"),
    "periodic_assessed": _obligation(
        ["proposal"], "{0} be subject to periodic residual risk assessments of misalignment risk",
        "periodic residual risk assessments of the misalignment risk posed are carried out for {0} (3.2.1)"),
    "safeguards_added": _obligation(["proposal"], "{0} have the additional safeguards applied",
                                    "the additional safeguards the risk assessment calls for are applied to {0} "
                                    "(3.2.1)"),
    "harm_mitigated": _obligation(
        ["proposal"], "{0} have mitigations make the residual risk of harm acceptable",
        "DM-h: the deployment mitigations of {0} bring the residual risk of harm to an acceptable level "
        "(1.3.5 bullet 2)"),
    "severe_harm_mitigated": _obligation(
        ["proposal"], "{0} have mitigations make the residual risk of severe harm acceptable", "DM-s: as DM-h, for the residual risk of severe harm (1.3.5 bullet 3)"),
    "significant_harm_mitigated": _obligation(
        ["proposal"], "{0} have mitigations make the residual risk of significant harm acceptable", "DM-g: as DM-h, for the residual risk of significant harm (1.3.5 bullet 4)"),
    "secured": _obligation(
        ["proposal"], "{0} have security mitigations that reach the recommended security level",
        "SEC: security mitigations reaching the recommended security level have been applied to the model "
        "weights of {0} (1.3.5 bullets 2 and 3)"),
    "adequately_secured": _obligation(
        ["proposal"], "{0} have a level of security assessed as adequate",
        "SEC-t: the level of security applied to the model weights of {0} is assessed adequate (1.3.5 bullet 4)"),
    "proceed": {"arguments": ["proposal"], "description": "{0} may take place",
                "regulated": {"role": "permission", "default": "deny", "act": "{0} proceed"}},
    "acceptable": {"arguments": ["proposal"], "verbalisation": "{0} is acceptable",
                   "description": "{0} is deemed to pose an acceptable level of (residual) risk (1.3.5): a "
                                  "classification, never a permission to proceed",
                   "regulated": {"role": "plain", "default": "deny"}},
    "case_submitted": _obligation(
        ["proposal"], "{0} be submitted to review by the appropriate governance function",
        "the material update {0} to a safety case is submitted to the appropriate governance function (2.1.2)"),
    "insider_mitigations_added": _obligation(
        ["proposal"], "{0} add mitigations against insider misuse beyond the baseline controls",
        "mitigations against insider misuse beyond the established baseline safeguards are added for {0} (2.2)"),
    "applied": _obligation(["proposal", "measure"], "{0} apply {1} to the model weights",
                           "{1} is applied to the model weights of {0} (2.1.1, 2.2, 3.2.2)"),
    "yearly_review": _obligation(["proposal"], "{0} be covered by a review of the framework at least once a year",
                                 "the framework is reviewed at least once a year, at the time of {0} (5.1)"),
    "frequent_review": _obligation(["proposal"], "{0} be covered by a more frequent review of the framework",
                                   "the framework is reviewed more often than yearly, at the time of {0} (5.1)"),
    "shared": _obligation(
        ["proposal"], "{0} share relevant information with appropriate government authorities",
        "relevant information about the model of {0} is shared with appropriate government authorities (5.2)"),
    "holistic": _obligation(
        ["proposal"], "{0} have its mitigations assessed holistically in proportion to expected impact",
        "the mitigation for {0} and its effects are assessed holistically and proportionately (1.3.5 Note)"),
    "within_levels": _obligation(
        ["proposal"], "{0} have its residual risk brought within the acceptable levels",
        "the residual risk of {0} is brought within the acceptable levels (Glossary, Residual Risk Assessments)"),
    "elicitation_considered": _obligation(
        ["proposal"], "{0} have its risk assessment consider greater elicitation effort by others",
        "the risk assessment for {0} takes into account that other actors may put significantly more effort into "
        "eliciting capabilities (Note on ML R&D CCLs)"),
}

LEVELS = {
    "cbrn_uplift_tcl": "L1: CBRN uplift TCL (2.2.1)",
    "cbrn_uplift_level_1": "L2: CBRN uplift level 1 (table 2.2.1.a)",
    "cyber_uplift_level_1": "L3: Cyber uplift level 1 (table 2.2.2.a)",
    "harmful_manipulation_level_1": "L4: Harmful manipulation level 1 (exploratory) (table 2.2.3.a)",
    "stealth_and_situational_awareness_tcl": "L5: Stealth and Situational Awareness TCL (3.2.1)",
    "ml_rd_acceleration_level_1": "L6: ML R&D acceleration level 1 (table 3.2.2.a)",
    "ml_rd_automation_level_1": "L7: ML R&D automation level 1 (table 3.2.2.a)",
}
DOMAINS = {
    "cbrn": "CBRN: chemical, biological, radiological or nuclear threats (1.2)",
    "cyber": "Cyber (1.2)",
    "harmful_manipulation": "Harmful Manipulation (1.2)",
    "ml_rd_and_misalignment_domain": "ML R&D and Misalignment (Glossary, Risk Domains)",
}
MEASURES = {
    "security_level_2_plus": "Security Level 2+ (2.1.1): RAND SL2 with additional measures",
    "security_level_3": "Security level 3 (table 3.2.2.a), generally aligned with RAND SL3 (footnote 6)",
    "security_level_4": "Security level 4 (table 3.2.2.a), generally aligned with RAND SL4 (footnote 6)",
    "insider_threat_measures": "the additional security measures of Security Level 2+ designed to address risks "
                               "from insider threats (2.1.1)",
}
THREATS = {"insiders": "insider threats (2.1.1)"}


def constants():
    result = {}
    for table, sort in ((LEVELS, "level"), (DOMAINS, "domain"), (MEASURES, "measure"), (THREATS, "threat")):
        for name, description in table.items():
            result[name] = {"sort": sort, "description": description}
    return result


def environment(default="deny"):
    predicates = {**copy.deepcopy(BASE), **copy.deepcopy(REGULATED)}
    for entry in predicates.values():
        if "regulated" in entry:
            entry["regulated"]["default"] = default
    return {"language": LANGUAGE, "profiles": list(PROFILES), "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {name: {"description": text} for name, text in SORTS.items()},
                           "predicates": predicates, "constants": constants()}}


def text():
    return json.dumps(environment(), indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    (HERE / "environment.d1.json").write_text(text())
    print("wrote environment.d1.json")
