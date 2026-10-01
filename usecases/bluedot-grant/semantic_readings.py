"""Authored readings for the 93 unchanged source spans.

Every unit has one explicit entry.  A unit is CHECKED only when its formula
uses shared vocabulary (relations between named constants, quantifiers,
equality, the five defined terms, or the merged causation word ``prevents``)
and states what the span says, no more.  A unit that mentions one of the five
defined terms either uses that term's predicate or stays OPEN on it.  Plans,
labels and headings are LABELLED; a stated link the merged routes cannot
express is UNFORMALISED.

Kinds keep the speaker: OLD, NEW and PASTE wording is attributed to that text,
and each candidate answer to its candidate.  Only the author's notes are
asserted, so only they enter the premise set.  ``RESOLUTIONS`` records every
pronoun, ellipsis or context restriction the author resolved.
"""
from __future__ import annotations


def C(name):
    return ["const", name]


def V(index):
    return ["var", index]


def un(pred, term):
    return ["unary", pred, term if type(term) is list else C(term)]


def bi(pred, left, right):
    return ["binary", pred, left if type(left) is list else C(left),
            right if type(right) is list else C(right)]


def conj(*items):
    result = items[-1]
    for item in reversed(items[:-1]):
        result = ["and", item, result]
    return result


def disj(*items):
    result = items[-1]
    for item in reversed(items[:-1]):
        result = ["or", item, result]
    return result


def neg(item):
    return ["not", item]


def implies(left, right):
    return ["implies", left, right]


def forall(sort, body):
    return ["forall", sort, body]


def exists(sort, body):
    return ["exists", sort, body]


def eq(left, right):
    return ["eq", left, right]


def sort(singular, plural, description):
    return {"description": description,
            "verbalisation": {"singular": singular, "plural": plural}}


SORTS = {
    "item": sort("item", "items", "a named thing the draft talks about"),
    "claim": sort("claim", "claims", "a claim submitted for checking"),
    "proof": sort("proof", "proofs", "a proof of a claim"),
    "comparison": sort("comparison", "comparisons", "a comparison of methods"),
    "artefact": sort("artefact", "artefacts", "a benchmark artefact"),
    "formalisation": sort("formalisation", "formalisations", "a formalisation of a source task"),
    "pathway": sort("pathway", "pathways", "a documented pathway to harm"),
    "evidence": sort("evidence item", "evidence items", "an item of evidence"),
    "candidate": sort("candidate", "candidates", "a short-answer candidate"),
    "field": sort("field", "fields", "a form field"),
    "foundation_leaf": sort("foundation leaf", "foundation leaves", "a declared foundation leaf"),
    "chooser": sort("chooser", "choosers", "an overseer choosing a checking regime"),
    "action": sort("action", "actions", "a checking practice"),
    "harm": sort("harm", "harms", "an oversight harm"),
}


def rel(arguments, verbalisation):
    return {"arguments": arguments, "description": verbalisation.replace("{0} ", "").replace(" {1}", ""),
            "verbalisation": verbalisation}


PREDICATES = {
    "tested_against": rel(["item", "item"], "{0} is tested against {1}"),
    "tested_on": rel(["item", "item"], "{0} is tested on {1}"),
    "tested_to_improve": rel(["item", "item"], "{0} is tested to improve {1}"),
    "developed_to_improve": rel(["item", "item"], "{0} is developed to improve {1}"),
    "proposed": rel(["item"], "{0} is proposed"),
    "applies_to": rel(["item", "item"], "{0} is for {1}"),
    "tests": rel(["item", "harm"], "{0} tests {1}"),
    "misstates_task": rel(["formalisation"], "{0} misstates the task"),
    "accepted_without_proof": rel(["foundation_leaf"], "{0} is accepted without proof"),
    "honest": rel(["claim"], "{0} is honest"),
    "unresolved": rel(["claim"], "{0} is unresolved"),
    "proof_of": rel(["proof", "claim"], "{0} is a proof of {1}"),
    "required_by": rel(["evidence", "item"], "{0} is required by {1}"),
    "needs_quality_review": rel(["evidence"], "{0} still needs quality review"),
    "null_result": rel(["item"], "{0} is a null result"),
    "negative_result": rel(["item"], "{0} is a negative result"),
    "published": rel(["item"], "{0} is published"),
    "copied_from": rel(["item", "item"], "{0} is copied from {1}"),
    "used_as": rel(["item", "item"], "{0} is used as {1}"),
    "current_form_text": rel(["item"], "{0} is the current form text"),
    "supplies_context": rel(["item"], "{0} supplies the surrounding context"),
    "follows": rel(["item", "item"], "{0} follows {1}"),
    "conditional_on": rel(["item", "item"], "{0} is conditional on {1}"),
    "establishes_truth_of": rel(["item", "item"], "{0} establishes the truth of {1}"),
    "establishes_fidelity_of": rel(["item", "item"], "{0} establishes the faithful formalisation of {1}"),
    "benefit_of": rel(["item", "item"], "{0} is a benefit of {1}"),
    "claims": rel(["item", "item"], "{0} claims {1}"),
    "asserts": rel(["item", "item"], "{0} asserts {1}"),
    "reports": rel(["item", "item"], "{0} reports {1}"),
    "concerns": rel(["item", "item"], "{0} concerns {1}"),
    "guarantees": rel(["item", "item"], "{0} guarantees {1}"),
    "schedules": rel(["item", "item"], "{0} is the development schedule of {1}"),
    "counts_cost": rel(["comparison", "item"], "{0} includes the cost of {1}"),
    "revised": rel(["field"], "{0} is revised"),
    "includes": rel(["item", "item"], "{0} includes {1}"),
    "pasted": rel(["candidate"], "{0} is pasted"),
    "pasted_with": rel(["candidate", "item"], "{0} is pasted with {1}"),
    "replaces": rel(["item", "item"], "{0} replaces {1}"),
    "states": rel(["item", "item"], "{0} states {1}"),
    "tests_transfer": rel(["artefact"], "{0} tests transfer"),
    "included_in": rel(["artefact", "item"], "{0} is included in {1}"),
    # The merged causation profile's base relations (alternatives@0).
    "available": rel(["action", "chooser"], "{0} is available to {1}"),
    "leads_to": rel(["action", "harm"], "{0} leads to {1}"),
}

CONSTANTS = {name: {"sort": s, "description": d} for name, (s, d) in {
    "verified_checker": ("item", "the verified checker"),
    "evidence_layer": ("item", "the auditable evidence layer"),
    "cross_examination": ("item", "cross-examination"),
    "smuggled_premises": ("item", "smuggled premises"),
    "equivocation": ("item", "equivocation"),
    "shifting_definitions": ("item", "shifting definitions"),
    "mandatory_checked_proofs": ("item", "mandatory checked proofs"),
    "obfuscated_arguments": ("item", "obfuscated arguments"),
    "vex": ("item", "VEX"),
    "statistical_claims": ("item", "statistical claims"),
    "approximate_claims": ("item", "approximate claims"),
    "formalisable_claims": ("item", "formalisable claims"),
    "oversight": ("item", "oversight of untrusted AI work"),
    "deference_control": ("item", "the deference control"),
    "shifting_definition_control": ("item", "the shifting-definition control"),
    "smuggled_premise_control": ("item", "the smuggled-premise control"),
    "benchmark": ("item", "the benchmark"),
    "harness": ("item", "the harness"),
    "failure_analysis": ("item", "the failure analysis"),
    "old_text": ("item", "OLD"),
    "form_edits_file": ("item", "FORM-EDITS-2026-09-21.md"),
    "rapid_draft": ("item", "bluedot-rapid-draft-v3.md"),
    "superseded_wording": ("item", "the superseded wording of bluedot-rapid-draft-v3.md"),
    "correction": ("item", "the correction"),
    "recheck_section": ("item", "section 3 of /Users/seyran/code/manage-agents/reviews/obfuscation-recheck.md"),
    "positioning_section": ("item", "section 4 of /Users/seyran/code/ve-integration/design/positioning-vs-debate-theory.md"),
    "positioning_correction": ("item", "Correction 2 of /Users/seyran/code/ve-integration/design/positioning-vs-debate-theory.md"),
    "guarantee": ("item", "the guarantee of mandatory proof"),
    "declared_foundations": ("item", "the declared foundations"),
    "prevention": ("item", "mandatory proof preventing arbitrary false sub-claims from being accepted as new assumptions"),
    "sound_proof_checking": ("item", "sound proof checking in general"),
    "draft": ("item", "this draft"),
    "debate_novelty": ("item", "novelty for proofs plus debate"),
    "english_surface_benefit": ("item", "a benefit from VE's English surface"),
    "stability_caveat": ("item", "the existing stability caveat"),
    "estimated_leaves": ("item", "estimated leaves"),
    "proved_subclaims": ("item", "proved sub-claims"),
    "evidence_requirements": ("item", "evidence requirements"),
    "evidence_quality": ("item", "evidence quality"),
    "vex_result": ("item", "a VEX result"),
    "completed_extension": ("item", "a completed extension"),
    "evidence_layer_milestones": ("item", "the existing evidence-layer milestones"),
    "revised_form_text": ("item", "the revised form text"),
    "new_results": ("item", "new experimental results"),
    "cost_advantage": ("item", "a cost advantage"),
    "character_counts": ("item", "the character counts"),
    "spaces": ("item", "spaces"),
    "punctuation": ("item", "punctuation"),
    "labels": ("item", "labels"),
    "trailing_newlines": ("item", "trailing newlines"),
    "its_label": ("item", "the candidate's label"),
    "its_count": ("item", "the candidate's count"),
    "contribution_edit": ("item", "the contribution edit"),
    "harms_edit": ("item", "the harms edit"),
    "indicated_sentence": ("item", "the indicated sentence"),
    "indicated_paragraph": ("item", "the indicated paragraph"),
    "extra_space": ("item", "the extra space in the revised passages"),
    "proof_rule": ("item", "the proof rule"),
    "proof_rule_limits": ("item", "the limits of the proof rule"),
    "authoring": ("item", "authoring"),
    "formalisation_work": ("item", "formalisation"),
    "proof_production": ("item", "proof production"),
    "compute": ("item", "compute"),
    "review": ("item", "review"),
    "revised_comparison": ("comparison", "the matched-cost comparison in the revised form text"),
    "proof_label": ("action", "a proof label"),
    "mandatory_proof": ("action", "mandatory proof"),
    "false_confidence": ("harm", "increased false confidence"),
    "premise_confidence": ("harm", "increased false confidence about premise truth"),
    "fidelity_confidence": ("harm", "increased false confidence about faithful formalisation"),
    "false_subclaim_accepted": ("harm", "an arbitrary false sub-claim accepted as a new assumption"),
}.items()}

# Kinds.  Speakers are the quoted text, never the checker.
OLD = ["attributed", "old_text", "says", "asserted"]
NEW = ["attributed", "new_text", "says", "asserted"]
PASTE = ["attributed", "paste_text", "says", "asserted"]


def nested(holder, inner):
    return ["attributed", holder, "says", inner]


COULD = ["hedged", "could", "asserted"]
PROMISED = ["attributed", "applicant", "promised", "asserted"]
PLAN = ["attributed", "applicant", "intends", "asserted"]
CANDIDATE_1 = ["attributed", "candidate_1", "says", "asserted"]
CANDIDATE_2 = ["attributed", "candidate_2", "says", "asserted"]

# Shared contents.  Each NEW sentence and its PASTE copy have one reading.
ISSUES = ("smuggled_premises", "equivocation", "shifting_definitions")
TITLE_OLD = conj(*[bi("tested_against", tool, "cross_examination")
                   for tool in ("verified_checker", "evidence_layer")],
                 *[bi("tested_on", tool, issue)
                   for tool in ("verified_checker", "evidence_layer") for issue in ISSUES])
TITLE_ONE = conj(bi("tested_on", "mandatory_checked_proofs", "obfuscated_arguments"),
                 un("proposed", "vex"),
                 bi("applies_to", "vex", "statistical_claims"),
                 bi("applies_to", "vex", "approximate_claims"))
TITLE_TWO = conj(bi("tested_to_improve", "mandatory_checked_proofs", "oversight"),
                 bi("applies_to", "mandatory_checked_proofs", "formalisable_claims"),
                 bi("developed_to_improve", "vex", "oversight"),
                 bi("applies_to", "vex", "statistical_claims"),
                 bi("applies_to", "vex", "approximate_claims"))
OLD_HARMS = ("premise_confidence", "fidelity_confidence")
OLD_CONTROLS = ("deference_control", "shifting_definition_control", "smuggled_premise_control")
LABEL_HARM = bi("leads_to", "proof_label", "false_confidence")
FOUNDATION_LEAVES = forall("foundation_leaf", un("accepted_without_proof", V(0)))
MISSTATES = exists("formalisation", un("misstates_task", V(0)))
# For every claim: honest and without an affordable proof of it -> unresolved.
UNRESOLVED = forall("claim", implies(
    conj(un("honest", V(0)),
         neg(exists("proof", conj(bi("proof_of", V(0), V(1)), un("affordable_proof", V(0)))))),
    un("unresolved", V(0))))
VEX_EVIDENCE = conj(exists("evidence", bi("required_by", V(0), "vex")),
                    forall("evidence", implies(bi("required_by", V(0), "vex"),
                                               un("needs_quality_review", V(0)))))
TRANSFER = forall("artefact", implies(
    conj(un("real_artefact", V(0)), bi("included_in", V(0), "benchmark")),
    un("tests_transfer", V(0))))
NULL_RESULTS = forall("item", implies(disj(un("null_result", V(0)), un("negative_result", V(0))),
                                      un("published", V(0))))
PUBLICATION = conj(NULL_RESULTS, un("published", "benchmark"), un("published", "harness"),
                   un("published", "failure_analysis"))


def only(subject, target):
    return forall("item", implies(bi("replaces", subject, V(0)), eq(V(0), C(target))))


def checked(kind, content, why):
    return {"status": "CHECKED", "kind": kind, "content": content, "why": why}


def labelled(kind):
    return {"status": "LABELLED", "kind": kind}


def opened(kind, *terms):
    return {"status": "OPEN", "kind": kind, "open": list(terms)}


def unformalised(reason, kind=None):
    return {"status": "UNFORMALISED", "kind": kind or ["unformalised", reason], "reason": reason}


# The Lean alternatives route refuses an environment with definitions, so a
# stated causal link cannot be checked beside the five defined terms.  These
# units stay UNFORMALISED here; causal.ve.md checks the same bytes on the
# merged causation route (see CAUSAL below).
CAUSAL_REASON = "causal_route_excludes_definitions"
CAUSAL_GAP = ["unformalised", CAUSAL_REASON]


def causal(kind):
    return {"status": "UNFORMALISED", "kind": kind, "reason": CAUSAL_REASON}


META = labelled("meta")
OLD_PLAN = nested("old_text", PLAN)
NEW_PLAN = nested("new_text", PLAN)
PASTE_PLAN = nested("paste_text", PLAN)

WHY = {
    "title_old": "Each of the checker and the evidence layer is tested against cross-examination on each named issue; 'Verifiable English:' names the project.",
    "title_one": "Candidate wording only; 'against obfuscated arguments' is the test condition, and VEX is proposed for the two claim classes.",
    "title_two": "Candidate wording only; the purpose 'to improve oversight' is read as applying to both the testing and the developing.",
    "label_could": "A possibility, not a prediction; no severity or likelihood is added.",
    "misstate": "A possibility that some formalisation misstates its task.",
    "leaves": "Universal over declared foundation leaves.",
    "affordable": "Uses the defined affordable_proof predicate.",
    "vex": "VEX requires evidence; that evidence still needs quality review. Nothing requires the review.",
    "transfer": "Uses the defined real_artefact predicate; 'real artefacts' are those in the benchmark.",
    "publish": "A commitment; it is unconditional, so 'even if VE provides no advantage' adds no condition.",
}

READINGS = {
    "u001": META, "u002": META,
    "u003": checked(OLD, TITLE_OLD, WHY["title_old"]),
    "u004": META, "u005": META, "u006": META,
    "u007": checked(CANDIDATE_1, TITLE_ONE, WHY["title_one"]),
    "u008": META,
    "u009": checked(CANDIDATE_2, TITLE_TWO, WHY["title_two"]),
    "u010": META, "u011": META,
    # The OLD milestone is superseded plan wording.  It is not a current plan.
    "u012": labelled(OLD_PLAN),
    "u013": opened(OLD_PLAN, "matched_cost"),
    "u014": opened(OLD_PLAN, "misleading_formalisation"),
    "u015": opened(OLD_PLAN, "real_artefact"),
    "u016": META,
    # NEW milestone items are plans, not obligations or commitments.
    "u017": opened(NEW_PLAN, "misleading_formalisation"),
    "u018": opened(NEW_PLAN, "matched_cost"),
    "u019": labelled(NEW_PLAN),
    "u020": labelled(NEW_PLAN),
    "u021": opened(NEW_PLAN, "real_artefact"),
    "u022": opened("question", "catastrophic_risk"),
    "u023": META,
    "u024": opened(OLD, "matched_cost"),
    "u025": META,
    "u026": unformalised("causal_means", nested("new_text", ["unformalised", "causal_means"])),
    "u027": opened("question", "catastrophic_risk"),
    "u028": META,
    "u029": causal(nested("old_text", ["hedged", "could", CAUSAL_GAP])),
    "u030": checked(OLD, conj(*[disj(*[bi("tests", c, h) for h in OLD_HARMS]) for c in OLD_CONTROLS],
                              *[disj(*[bi("tests", c, h) for c in OLD_CONTROLS]) for h in OLD_HARMS]),
                    "Collective reading: each control tests one of these harms, and each harm is tested by one of the controls."),
    "u031": opened(OLD, "real_artefact"),
    "u032": checked(nested("old_text", PROMISED), NULL_RESULTS, "A commitment in the OLD text."),
    "u033": labelled(["attributed", "applicant", "expects", "asserted"]),
    "u034": META,
    "u035": causal(nested("new_text", ["hedged", "could", CAUSAL_GAP])),
    "u036": checked(NEW, FOUNDATION_LEAVES, WHY["leaves"]),
    "u037": checked(nested("new_text", COULD), MISSTATES, WHY["misstate"]),
    "u038": checked(NEW, UNRESOLVED, WHY["affordable"]),
    "u039": checked(NEW, VEX_EVIDENCE, WHY["vex"]),
    "u040": opened(NEW, "misleading_formalisation"),
    "u041": checked(NEW, TRANSFER, WHY["transfer"]),
    "u042": checked(nested("new_text", PROMISED), PUBLICATION, WHY["publish"]),
    "u043": META,
    "u044": checked("asserted", conj(bi("copied_from", "old_text", "form_edits_file"),
                                     un("current_form_text", "form_edits_file"),
                                     un("supplies_context", "rapid_draft")),
                    "Provenance of the OLD wording and of the context."),
    "u045": checked("asserted", neg(bi("used_as", "superseded_wording", "old_text")),
                    "'its' is bluedot-rapid-draft-v3.md."),
    "u046": checked("asserted", conj(*[bi("follows", "correction", s) for s in
                                       ("recheck_section", "positioning_section", "positioning_correction")]),
                    "The three cited sources of the correction."),
    "u047": causal(CAUSAL_GAP),
    "u048": checked("asserted", bi("conditional_on", "guarantee", "declared_foundations"),
                    "'the guarantee' is the guarantee of mandatory proof."),
    "u049": checked("asserted", conj(neg(bi("establishes_truth_of", "guarantee", "declared_foundations")),
                                     neg(bi("establishes_fidelity_of", "guarantee", "declared_foundations"))),
                    "'It' is the guarantee, the subject of the preceding clause; 'their' is the declared foundations."),
    "u050": checked("asserted", forall("claim", implies(
        conj(un("honest", V(0)), neg(un("unresolved", V(0)))),
        exists("proof", conj(bi("proof_of", V(0), V(1)), un("affordable_proof", V(0)))))),
                    "'needs' is read as needed to leave the 'unresolved' status; uses the defined affordable_proof predicate."),
    "u051": checked("asserted", forall("claim", implies(
        conj(exists("proof", bi("proof_of", V(0), V(1))),
             forall("proof", implies(bi("proof_of", V(0), V(1)), neg(un("within_budget", V(0)))))),
        un("unresolved", V(0)))),
                    "'beyond budget' is the negation of affordable_proof's within_budget clause; 'the claim' is the claim those proofs prove."),
    "u052": checked("asserted", bi("benefit_of", "prevention", "sound_proof_checking"),
                    "'This' is note 2's protection against arbitrary false sub-claims."),
    "u053": labelled(["attributed", "author", "believes", "asserted"]),
    "u054": checked("asserted", conj(neg(bi("claims", "draft", "debate_novelty")),
                                     neg(bi("claims", "draft", "english_surface_benefit"))),
                    "Nothing is claimed; the draft does not claim that there is no novelty."),
    "u055": checked("asserted", conj(bi("concerns", "stability_caveat", "estimated_leaves"),
                                     neg(bi("concerns", "stability_caveat", "proved_subclaims"))),
                    "The caveat's scope."),
    "u056": checked(NEW, conj(un("proposed", "vex"), bi("applies_to", "vex", "statistical_claims"),
                              bi("applies_to", "vex", "approximate_claims")),
                    "'is presented as' attributes the description to the revised text."),
    "u057": checked("asserted", neg(bi("guarantees", "evidence_requirements", "evidence_quality")),
                    "A negated relation."),
    "u058": checked("asserted", conj(neg(bi("claims", "draft", "vex_result")),
                                     neg(bi("claims", "draft", "completed_extension"))),
                    "Nothing is claimed."),
    "u059": checked("asserted", bi("schedules", "evidence_layer_milestones", "vex"),
                    "'its' is VEX."),
    "u060": unformalised("motivation_link"),
    "u061": checked("asserted", conj(neg(bi("reports", "revised_form_text", "new_results")),
                                     neg(bi("asserts", "revised_form_text", "cost_advantage"))),
                    "Two negated relations."),
    "u062": checked(PLAN, conj(un("matched_cost", "revised_comparison"),
                               bi("counts_cost", "revised_comparison", "formalisation_work"),
                               bi("counts_cost", "revised_comparison", "proof_production")),
                    "A plan, so attributed as an intention; 'the matched-cost comparison' uses the defined matched_cost predicate."),
    "u063": opened("exposition", "real_artefact"),
    "u064": opened("exposition", "misleading_formalisation"),
    "u065": checked("asserted", forall("field", neg(un("revised", V(0)))), "The budget is one field."),
    "u066": checked("asserted", conj(bi("includes", "character_counts", "spaces"),
                                     bi("includes", "character_counts", "punctuation"),
                                     neg(bi("includes", "character_counts", "labels")),
                                     neg(bi("includes", "character_counts", "trailing_newlines"))),
                    "What the stated counts include."),
    "u067": checked("instruction", conj(
        exists("candidate", un("pasted", V(0))),
        forall("candidate", forall("candidate", implies(conj(un("pasted", V(0)), un("pasted", V(1))),
                                                        eq(V(0), V(1))))),
        forall("candidate", implies(un("pasted", V(0)),
                                    conj(neg(bi("pasted_with", V(0), "its_label")),
                                         neg(bi("pasted_with", V(0), "its_count")))))),
                    "The instructed state: exactly one candidate is pasted, without its label or count; 'its' is the pasted candidate."),
    "u068": checked("asserted", conj(bi("replaces", "contribution_edit", "indicated_sentence"),
                                     bi("replaces", "harms_edit", "indicated_paragraph"),
                                     only("contribution_edit", "indicated_sentence"),
                                     only("harms_edit", "indicated_paragraph")),
                    "Respectively: the contribution edit replaces only the sentence, and the harms edit only the paragraph."),
    "u069": unformalised("vague_comparison", ["attributed", "author", "believes", ["unformalised", "vague_comparison"]]),
    "u070": checked("asserted", conj(bi("states", "extra_space", "proof_rule"),
                                     bi("states", "extra_space", "proof_rule_limits")),
                    "'its' is the proof rule; 'the extra space' is in the revised passages."),
    "u071": META, "u072": META, "u073": META,
    "u074": checked(CANDIDATE_1, TITLE_ONE, WHY["title_one"]),
    "u075": META,
    "u076": checked(CANDIDATE_2, TITLE_TWO, WHY["title_two"]),
    "u077": META,
    "u078": opened(PASTE_PLAN, "misleading_formalisation"),
    "u079": opened(PASTE_PLAN, "matched_cost"),
    "u080": labelled(PASTE_PLAN),
    "u081": labelled(PASTE_PLAN),
    "u082": opened(PASTE_PLAN, "real_artefact"),
    "u083": opened("question", "catastrophic_risk"),
    "u084": unformalised("causal_means", nested("paste_text", ["unformalised", "causal_means"])),
    "u085": opened("question", "catastrophic_risk"),
    "u086": causal(nested("paste_text", ["hedged", "could", CAUSAL_GAP])),
    "u087": checked(PASTE, FOUNDATION_LEAVES, WHY["leaves"]),
    "u088": checked(nested("paste_text", COULD), MISSTATES, WHY["misstate"]),
    "u089": checked(PASTE, UNRESOLVED, WHY["affordable"]),
    "u090": checked(PASTE, VEX_EVIDENCE, WHY["vex"]),
    "u091": opened(PASTE, "misleading_formalisation"),
    "u092": checked(PASTE, TRANSFER, WHY["transfer"]),
    "u093": checked(nested("paste_text", PROMISED), PUBLICATION, WHY["publish"]),
}

# Readings on the merged causation route (alternatives@0), in causal.ve.md.
# Each keeps its speaker and modality.  No outcome table, completion, risk
# default or severity is supplied.
CAUSAL = {
    "u029": checked(nested("old_text", COULD),
                    disj(*[bi("leads_to", "proof_label", harm) for harm in OLD_HARMS]),
                    "A possibility of either kind of false confidence; no likelihood or severity is added."),
    "u035": checked(nested("new_text", COULD), LABEL_HARM, WHY["label_could"]),
    "u047": checked("asserted", bi("prevents", "mandatory_proof", "false_subclaim_accepted"),
                    "The merged word 'prevents': mandatory proof does not lead to the harm, and another action available to the same chooser does."),
    "u086": checked(nested("paste_text", COULD), LABEL_HARM, WHY["label_could"]),
}
CAUSAL_SORTS = ("chooser", "action", "harm")

# Every pronoun, ellipsis or contextual restriction the author resolved.  Each
# is an author choice recorded here and in the README; none is admitted by the
# discourse route.
RESOLUTIONS = {
    "u030": "'these harms' -> the two harms of u029: increased false confidence about premise truth, and about faithful formalisation",
    "u040": "'these harms' -> the harms of u035-u037 (unit stays OPEN)",
    "u041": "'real artefacts' -> real artefacts included in the benchmark; 'transfer' left unqualified",
    "u045": "'its' -> bluedot-rapid-draft-v3.md",
    "u048": "'the guarantee' -> the guarantee of mandatory proof",
    "u049": "'It' -> the guarantee of mandatory proof, the subject of the preceding clause; 'their' -> the declared foundations",
    "u050": "'needs' -> needed for the claim not to remain unresolved",
    "u051": "'the claim' -> the claim the over-budget proofs are proofs of; 'beyond budget' -> total cost not within the registered budget (the within_budget clause of affordable_proof)",
    "u052": "'This' -> note 2's protection: mandatory proof preventing arbitrary false sub-claims from being accepted as new assumptions",
    "u054": "'is claimed' -> claimed by this draft",
    "u058": "'is claimed' -> claimed by this draft",
    "u059": "'its' -> VEX",
    "u062": "'the matched-cost comparison' -> the comparison in the revised form text",
    "u067": "'its label or count' -> the pasted candidate's label and count",
    "u068": "'sentence and paragraph' -> respectively, the contribution sentence and the harms paragraph",
    "u070": "'its' -> the proof rule; 'the extra space' -> in the revised passages",
    "u091": "'these harms' -> the harms of u086-u088 (unit stays OPEN)",
    "u092": "'real artefacts' -> real artefacts included in the benchmark; 'transfer' left unqualified",
}

OPEN_REASONS = {
    "matched_cost": "OLD wording written before the author's rule, or a milestone plan item recorded only as a plan; applying the definition would add content the span does not state.",
    "real_artefact": "OLD wording, a milestone plan item, or a list of retained items; the span does not say which artefacts the defined predicate classifies.",
    "misleading_formalisation": "Used as an error class or as the name of a control; the span does not say how the control or class relates to the defined predicate on formalisations.",
    "catastrophic_risk": "The funder's form heading. BlueDot, not the grant author, decides the sense of its question, and the draft gives no reduction estimate.",
}
OPEN_DECIDERS = {"matched_cost": "grant-author", "real_artefact": "grant-author",
                 "misleading_formalisation": "grant-author", "catastrophic_risk": "bluedot"}
