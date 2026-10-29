"""The D1 vocabulary of the anthropic-rsp case (PLAN sections 3.2 and 7).

`python usecases/anthropic-rsp/rsp_vocabulary.py` writes `environment.d1.json`; the test checks that the committed
file equals this output. As in safety-framework, every rule speaks about a `situation` (a moment of the policy's
process), the completion default is a forced choice ("deny" here; the run harness flips it, PLAN 3.3), each predicate's
description is the legend a reader checks it against, and each open term names its decider. A wording that cannot
say what the source says in one adjective or one verb has no verbalisation, so VE writes `is classified as "<name>"`
with the source's own phrase.
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
    "situation": "a moment of the policy's process at which a rule may apply: a model's development or deployment, a "
                 "Risk Report, a selection of external reviewers, a noncompliance report, an update of the policy, or "
                 "a scenario of Appendix A. Every rule speaks about every situation",
    "threshold": "a capability or usage threshold of the section 1 table",
}
THRESHOLDS = {
    "non_novel_chem_bio_weapons": "T1: \"Non-novel chemical/biological weapons production\" (section 1 table, row 1)",
    "novel_chem_bio_weapons": "T2: \"Novel chemical/biological weapons production\" (row 2)",
    "misaligned_high_stakes": "T3: \"Misaligned AI systems in high-stakes settings\" (row 3)",
    "automated_rd": "T4: \"Automated R&D in key domains\" (row 4)",
}


def _base(args, description, verbalisation=None):
    entry = {"arguments": list(args), "description": description}
    if verbalisation is not None:
        entry["verbalisation"] = verbalisation
    return entry


def _open(args, description, decider, term, verbalisation=None):
    """An open-term predicate: VE never decides it; the case stipulates the decider's finding."""
    return _base(args, f"{description}. Open term {term}, decided by {decider}", verbalisation)


def _regulated(role, args, act, description):
    return {"arguments": list(args), "description": description, "regulated": {"role": role, "default": "deny",
                                                                                **({"act": act} if act else {})}}


def _duty(act, description, args=("situation",)):
    return _regulated("obligation", args, act, description)


def _may(act, description):
    """A permission: "may" (RS6 P) or, with "must not", a prohibition."""
    return _regulated("permission", ("situation",), act, description)


WE = "the company (\"we\")"
BASE = {
    "listed": _base(["threshold"], "{0} is a threshold of the section 1 table", "{0} is listed"),
    "crossed": _open(["situation", "threshold"], "the model of {0} has crossed {1}", WE + " (3.3 \"whether we "
                     "believe we've crossed relevant thresholds\"; T4: \"if we determine\")", "OT1",
                     "{0} has crossed {1}"),
    # Situations the cases stipulate (no open term).
    **{name: _base(["situation"], text) for name, text in {
        "publicly_deployed": "the model of {0} is publicly deployed as of the coverage date (3.1)",
        "internally_deployed": "the model of {0} is internally deployed as of the coverage date (3.1)",
        "risk_report_approved": "{0} is the approval of a Risk Report (3.4 step 4)",
        "ltbt_requested_review": "at {0} the LTBT has requested an external review (3.6)",
        "selecting_reviewers": "{0} is the selection of external reviewers (3.6.1)",
        "candidate_has_financial_interest": "at {0} a candidate reviewing organization has a financial interest in "
                                            "Anthropic (3.6.1)",
        "candidate_revenue_dependent": "at {0} a candidate review team's revenue, reputation and success depend "
                                       "entirely on Anthropic and similar companies (3.6.1, an example)",
        "submitted_under_external_review": "{0} is the submission of a Risk Report to the Board and LTBT under the "
                                           "external review process (3.6.2)",
        "external_review_process": "{0} is a Risk Report under the external review process (3.6.2)",
        "noncompliance_report_received": "at {0} a report of potential noncompliance is received (4.4)",
        "substantiated": "at {0} the noncompliance report is substantiated (4.4)",
        "concerns_rso": "at {0} the noncompliance report concerns the conduct of the RSO (4.4)",
        "non_disparagement_clause_offered": "at {0} an agreement with a non-disparagement clause is offered (4.5)",
        "rsp_change_proposed": "{0} is a change to the RSP (4.8)",
        "rsp_updated": "{0} is an update of the RSP (4.8)",
        "describes_mitigation_and_deviates": "at {0} a Risk Report described a risk mitigation and later practice "
                                             "deviates from it (3.2)",
        "roadmap_goal_missed": "at {0} a Frontier Safety Roadmap goal was not met (3.3)",
        "roadmap_goal_unachieved": "at {0} a Frontier Safety Roadmap goal could not be achieved (section 2)",
        "goal_revised_less_ambitious": "at {0} a Roadmap goal is revised in a less ambitious direction simply "
                                       "because it could not be achieved (section 2)",
        "competitor_better_mitigation": "at {0} a competitor has implemented a risk mitigation that (1) is a "
                                        "significant improvement and (2) we could implement at comparable or lower "
                                        "effort or cost (Appendix A, General upleveling)",
        "competitors_strong_measures": "at {0} all competitors who have developed, or will soon develop, a highly "
                                       "capable frontier model are able to make strong arguments that catastrophic "
                                       "risk is contained (Appendix A)",
        "in_the_lead": "at {0} we have developed or will imminently develop a highly capable model and no other "
                       "competitor will soon develop one (Appendix A, Anthropic in the lead)",
        "redaction_reason_listed": "at {0} material would be redacted for one of the reasons 3.5 lists",
        "scenario_2": "at {0} there is \"dramatic acceleration\" of the pace of AI progress for reasons that likely "
                      "relate to the automation of AI R&D (T4 (2))",
    }.items()},
    # Open terms (PLAN 3.2): the decider is the text's own.
    "highly_capable": _open(["situation"], "the model of {0} is highly capable (3.6: it crosses the threshold for "
                            "automated AI R&D)", WE + " (\"if we conclude\")", "OT5"),
    "more_capable_than_analyzed": _open(["situation"], "the model of {0} is significantly more capable than all "
                                        "models for which we have publicly analyzed the named risks (3.1, off-cycle "
                                        "bullet 1)", WE, "OT2"),
    "exceeds_prior_report": _open(["situation"], "the internal model of {0} could pose risks of high-stakes "
                                  "misalignment or automated R&D that significantly exceed those of models covered "
                                  "by a prior Risk Report (3.1 Scope)", WE, "OT3a"),
    "exceeds_all_analyzed": _open(["situation"], "the internal model of {0} could pose such risks that significantly "
                                  "exceed those of all models for which we have publicly analyzed them (3.1, "
                                  "off-cycle bullet 2)", WE, "OT3b"),
    "significantly_redacted": _open(["situation"], "the Risk Report of {0} is significantly redacted (3.6)",
                                    "the RSO, CEO, Board or LTBT (a sufficient judgment)", "OT4"),
    "strong_argument_made": _open(["situation"], "a strong argument that catastrophic risk is contained is made at "
                                  "{0}", "no one the text names (unstated)", "OT6"),
    "delay_needed": _open(["situation"], "a delay is needed at {0} to achieve the scenario's aim (Appendix A, "
                          "\"as needed\")", WE, "OT7"),
    "clear_evidence": _open(["situation"], "we have clear or strong evidence of the scenario at {0} (Appendix A)",
                            WE + " (\"use our best judgment\")", "OT8"),
    "significant_lead": _open(["situation"], "we believe we have a significant lead at {0} (Appendix A)", WE, "OT9"),
    "material_safety_risk": _open(["situation"], "the substantiated report at {0} involves a material safety risk "
                                  "(4.4)", WE + " (\"If we determine\")", "OT10"),
    "noteworthy": _open(["situation"], "the change or deviation at {0} is noteworthy (3.2)", "no one the text names "
                        "(unstated)", "OT11"),
    "marginal_justification": _open(["situation"], "at {0} the absolute level of risk imposed industry-wide is high "
                                    "and our decision to move forward rests partly on a marginal risk analysis (3.3)",
                                    WE + " (\"If we determine\")", "OT18"),
    "marginal_major_role": _open(["situation"], "at {0} marginal risk analysis plays a major role in a decision to "
                                 "move forward (3.4 step 5)", "no one the text names (unstated)", "OT19"),
    "full_substitution_at_competitive_cost": _open(["situation"], "at {0} our models would be able to fully "
                                                   "substitute for our entire set of Research Scientists and Research "
                                                   "Engineers at competitive costs, within a factor of 5 (T4 (1); the "
                                                   "factor is checked in D3)", WE + " (\"if we determine\")", "OT15"),
    "double_rate": _open(["situation"], "at {0} we observe or expect double the rate of progress in AI aggregate "
                         "capabilities compared to both the rate we'd expect and the fastest rate of extended progress "
                         "we've observed without significant AI contributions (T4 (2)(a), footnotes 8 and 9)", WE,
                         "OT16"),
    "automation_attributable": _open(["situation"], "at {0} it is plausible that the doubling is substantially "
                                        "attributable to the automation of research and/or engineering (T4 (2)(b))",
                                        WE, "OT17"),
    "continuation_accelerates": _open(["situation"], "at {0} continuation of the trend in AI progress seems likely to "
                                      "lead to even greater acceleration (T4 (2), under RS3c = third)", WE, "OT28"),
    "autonomous_research_use": _open(["situation"], "the internal model of {0} is deployed for large-scale, fully "
                                     "autonomous research (3.1)", "no one the text names (unstated)", "OT22"),
}

REGULATED = {
    "plans_in_place": _duty("{0} have the plans of the company about {1} in place", "the middle column's plans of "
                            "the row of {1} are in place at {0} (section 1, PROTk)", ("situation", "threshold")),
    "strong_argument": _duty("{0} make a strong argument about {1}", "the strong argument of the right column's row "
                             "of {1} is made at {0} (section 1, ARGk)", ("situation", "threshold")),
    "advance_recommendations": _duty("{0} advance the industry-wide recommendations", "the company works to advance "
                                     "the recommendations at {0} (section 1)"),
    "evidentiary_standards": _duty("{0} have analyses of threats from AIs follow very high evidentiary standards",
                                   "section 1, row 4, at {0}"),
    "roadmap_maintained": _duty("{0} have the Frontier Safety Roadmap maintained", "section 2 at {0}"),
    "roadmap_shared": _duty("{0} have the Roadmap shared as the policy states", "the Roadmap is shared with all "
                            "full-time employees, the Board and the LTBT, and published in redacted form, at {0} "
                            "(section 2)"),
    "roadmap_updates": _duty("{0} have updates provided on whether the Roadmap goals are achieved", "updates on the "
                             "goals, with new goals set when they are achieved, at {0} (section 2)"),
    "past_roadmaps_kept": _duty("{0} have past Roadmaps kept available", "section 2 at {0}"),
    "goals_kept": _duty("{0} avoid the revision", "the company avoids the revision of the goal at {0} (section 2)"),
    "risk_reports_published": _duty("{0} have Risk Reports published", "section 3 at {0}"),
    "in_scope": {"arguments": ["situation"], "description": "the model of {0} is "
                 "an in-scope model of the Risk Report (3.1): a classification, never a duty",
                 "regulated": {"role": "plain", "default": "deny"}},
    "off_cycle_published": _duty("{0} have an off-cycle analysis of its model published", "an analysis of the "
                                 "model's relevant risks is published at {0} (3.1, off-cycle updates)"),
    "candid_reports": _duty("{0} have its Risk Reports candid", "the Risk Reports are direct, candid and informative "
                            "at {0} (3.2)"),
    "deviation_reported": _duty("{0} have the deviation reported", "the change or deviation is tracked and reported "
                                "at {0} (3.2)"),
    "strong_attempt": _duty("{0} make a strong attempt to keep risk from increasing significantly", "ongoing (as "
                            "opposed to temporary) changes do not significantly increase the level of risk (3.2)"),
    "factual_documented": _duty("{0} have the factual information documented in its Risk Report", "the five "
                                "factual items of 3.3 at {0}"),
    "risk_analysed": _duty("{0} have the risk analyses provided", "the four risk analyses of 3.3 at {0}"),
    "past_reviewed": _duty("{0} have past Risk Reports reviewed", "the three review items of 3.3 at {0}"),
    "goal_miss_addressed": _duty("{0} have the missed goal addressed in a Risk Report", "3.3 review item 3 at {0}"),
    "marginal_analysed": _duty("{0} have the marginal risk analyses provided", "the four analyses of 3.3's marginal "
                               "risk paragraph at {0}"),
    "assessed_in_report": _duty("{0} be assessed in a Risk Report", "the assessments of 3.3 are conducted with "
                                "respect to the model of {0}"),
    "internal_feedback": _duty("{0} have comprehensive internal feedback solicited", "3.4 step 2 at {0}"),
    "external_feedback": _duty("{0} have feedback sought from trusted external parties", "3.4 step 2 at {0}"),
    "executive_approved": _duty("{0} have its Risk Report approved by the CEO with the RSO", "the report, with the "
                                "feedback, goes to the CEO and the RSO for final review and approval (3.4 step 3)"),
    "board_approved": _duty("{0} have its Risk Report approved by the Board as well as the LTBT", "explicit "
                            "approval by the Board and the LTBT (3.4 step 5)"),
    "governance_notified": _duty("{0} have its decision shared with the Board as well as the LTBT", "the decisions, "
                                 "the Risk Report and the internal feedback are shared with the Board and the LTBT "
                                 "(3.4 step 4)"),
    "redactions_minimized": _duty("{0} have its redactions minimized", "3.5 at {0}"),
    "redactions_disclosed": _duty("{0} have the existence of each redaction disclosed", "3.5 at {0}"),
    "redactions_justified": _duty("{0} have a brief justification of each redaction given", "3.5 at {0}"),
    "redaction": _may("{0} have the material redacted", "material may be redacted at {0} (3.5)"),
    "public_review_sought": _duty("{0} have comprehensive public external review sought", "3.6 at {0}"),
    "full_review": _duty("{0} have a full external review completed with at least one external reviewer", "3.6 at "
                         "{0}"),
    "ltbt_review": _duty("{0} have an external review conducted", "a public or private external review of the Risk "
                         "Report or sections thereof (3.6)"),
    "candidate_selected": _may("{0} have the candidate selected as an external reviewer", "3.6.1 at {0}"),
    "reviewers_approved": _duty("{0} have the selection approved by the LTBT after consulting the Board", "3.6.1 at "
                                "{0}: the Board consulted, the LTBT's approval obtained"),
    "shared_with_reviewers": _duty("{0} have the report shared with the external reviewers within one week",
                                   "3.6.2 at {0}"),
    "commentary_asked": _duty("{0} have the reviewers asked to comment publicly within thirty days", "3.6.2 at {0}"),
    "early_full_review": _duty("{0} have the full external review completed before the Board review", "3.6.2 at "
                                 "{0}"),
    "sections_shared": _duty("{0} have each section shared with at least one external reviewer", "3.6.2 at {0}"),
    "split_review": _may("{0} have the review split across external reviewers", "3.6.2 at {0}"),
    "only_legal_redactions": _duty("{0} have only legally necessary redactions in the reviewed version", "3.6.2 at "
                                   "{0}"),
    "rso_maintained": _duty("{0} have the position of RSO maintained", "4.1 at {0}"),
    "ltbt_briefed": _duty("{0} have the LTBT briefed", "4.2 at {0}"),
    "unredacted_shared": _duty("{0} have unredacted Risk Reports shared with at least two hundred employees", "4.3 at "
                               "{0}"),
    "minimally_redacted_shared": _duty("{0} have minimally-redacted Risk Reports shared with all regular-clearance "
                                       "staff", "4.3 at {0}"),
    "reporting_process": _duty("{0} have a noncompliance reporting process maintained", "4.4 at {0}"),
    "recipient_options": _duty("{0} offer more than one option of recipient", "4.4 at {0}: including the RSO and at "
                               "least one executive who does not report to the RSO"),
    "investigated": _duty("{0} have the report investigated", "4.4 at {0}: investigated, corrective action if "
                          "substantiated, the report and findings documented"),
    "quarterly_updates": _duty("{0} have quarterly updates on noncompliance reports provided to the Board", "4.4 at "
                               "{0}"),
    "board_notified": _duty("{0} have the Board notified", "4.4 at {0}"),
    "public_notice": _may("{0} have public notice provided", "4.4 at {0}"),
    "retaliation_protection": _duty("{0} have reporters protected from retaliation", "4.4 at {0}"),
    "board_member_recipient": _duty("{0} have a member of the Board among the recipients", "4.4 at {0}"),
    "disparagement_obligation": _may("{0} impose a non-disparagement obligation impeding safety concerns", "a "
                                      "contractual non-disparagement obligation that could impede or discourage "
                                      "raising safety concerns (4.5)"),
    "clause_allows_concerns": _duty("{0} have the clause permit raising safety concerns", "the clause does not "
                                    "preclude raising safety concerns nor disclosing the clause (4.5)"),
    "internal_review": _duty("{0} have an internal review of the implementation conducted", "4.6 at {0}"),
    "compliance_review": _duty("{0} have a third-party procedural compliance review commissioned", "4.7 at {0}"),
    "change_approved": _duty("{0} have the change approved by the Board", "4.8: proposed by the CEO and RSO, "
                             "approved by the Board in consultation with the LTBT"),
    "update_published": _duty("{0} have the updated version published with its differences in the Change Log",
                              "4.8: prior to or on its effective date"),
    "website_version": _duty("{0} have the current version kept on the website", "4.8 at {0}"),
    "argument_required": _duty("{0} require a strong argument about catastrophic risk", "a strong argument that "
                               "catastrophic risk is contained (Appendix A)"),
    "delay": _duty("{0} delay AI development as well as deployment", "Appendix A at {0}"),
    "posture_matched": _duty("{0} at least match the posture of the competitors", "meet or exceed the overall risk "
                             "reduction posture of these competitors (Appendix A)"),
    "significant_effort": _duty("{0} make a significant effort to match the performance standard", "meet or exceed "
                                "that performance standard (Appendix A)"),
}


def constants():
    return {name: {"sort": "threshold", "description": text} for name, text in THRESHOLDS.items()}


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
