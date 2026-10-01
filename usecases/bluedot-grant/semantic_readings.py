"""Audited proposition choices for the 93 unchanged source spans.

Each name is a proposition stated by the span, not a finding about the world.
The unit kind records its force.  In particular an intention or possibility
does not enter the assertion premise set.
"""

INTENDS = ["attributed", "applicant", "intends", "asserted"]
OLD = ["attributed", "old_text", "says", "asserted"]
POSSIBLE = ["hedged", "could", "asserted"]
CAUSES = ["causal", "because", "asserted", "asserted"]
INSTRUCTION = "instruction"

# id: (kind, subject, propositions).  The propositions are deliberately
# conjunctions only where every conjunct occurs in the source span.
READINGS = {
    "u003": (OLD, "draft", ("tests_checker", "tests_evidence_layer", "compares_cross_examination")),
    "u007": (INTENDS, "draft", ("tests_mandatory_proofs", "tests_obfuscated_arguments", "proposes_vex")),
    "u009": (INTENDS, "draft", ("tests_mandatory_proofs", "develops_vex", "aims_oversight")),
    "u012": (OLD, "benchmark", ("release_by_oct25", "tests_checker_deference", "tests_adversarial_pushback")),
    "u013": (OLD, "comparison", ("tests_definition_shift", "tests_smuggled_premises", "uses_matched_cost", "includes_certificate_production")),
    "u014": (OLD, "benchmark", ("tests_flaw_localisation", "uses_50_to_5000_steps", "separates_error_classes")),
    "u015": (["attributed", "old_text", "says", "instruction"], "benchmark", ("includes_real_artefacts", "replicates_model_families")),
    "u017": (INTENDS, "benchmark", ("release_by_oct25", "tests_mandatory_proofs", "tests_obfuscated_arguments", "uses_50_to_5000_steps", "separates_error_classes")),
    "u018": (INSTRUCTION, "comparison", ("compares_cross_examination", "uses_matched_cost", "includes_formalisation", "includes_proof_production")),
    "u019": (INSTRUCTION, "benchmark", ("focuses_large_untrusted_artefacts", "focuses_universal_or_negative_claims")),
    "u020": (INSTRUCTION, "benchmark", ("tests_forged_checker", "tests_sustained_pushback")),
    "u021": (INSTRUCTION, "benchmark", ("includes_real_artefacts", "replicates_model_families")),
    "u024": (OLD, "draft", ("claims_implementation", "tests_smuggled_premises", "tests_equivocation", "tests_definition_shift", "compares_cross_examination")),
    "u026": (CAUSES, "proof_rule", ("accepts_only_checked_derivations", "excludes_assumed_false_subclaims", "blocks_barnes_christiano_for_formalised_claims")),
    "u029": (POSSIBLE, "proof_label", ("increases_false_confidence",)),
    "u030": (CAUSES, "controls", ("tests_deference_harm", "tests_definition_shift", "tests_smuggled_premises")),
    "u031": (CAUSES, "artefact_arm", ("includes_real_artefacts", "tests_transfer_beyond_planted_flaws")),
    "u032": (OLD, "draft", ("commits_publish_null_and_negative",)),
    "u035": (POSSIBLE, "proof_label", ("increases_false_confidence",)),
    "u037": (POSSIBLE, "formalisation", ("misstates_task",)),
    "u038": ("asserted", "claim", ("unresolved_without_affordable_proof",)),
    "u039": (INTENDS, "vex", ("requires_evidence", "requires_quality_review")),
    "u040": (CAUSES, "controls", ("tests_forged_checker", "tests_false_foundations", "tests_misleading_formalisation")),
    "u041": (CAUSES, "artefact_arm", ("includes_real_artefacts", "tests_transfer_beyond_planted_flaws")),
    "u042": (INTENDS, "draft", ("commits_publish_null_and_negative", "publishes_benchmark_harness_analysis", "publishes_even_if_no_advantage")),
    "u044": ("asserted", "old_text", ("copied_from_current_form", "context_supplied_by_rapid_draft")),
    "u045": ("asserted", "old_text", ("excludes_superseded_wording",)),
    "u046": ("asserted", "correction", ("cites_obfuscation_recheck", "cites_positioning_review")),
    "u047": (CAUSES, "proof_rule", ("prevents_false_subclaims_as_new_assumptions",)),
    "u050": ("asserted", "honest_answer", ("requires_affordable_proof",)),
    "u051": ("asserted", "claim", ("unresolved_when_proof_beyond_budget",)),
    "u052": (CAUSES, "proof_rule", ("benefit_of_sound_proof_checking",)),
    "u054": ("asserted", "draft", ("claims_no_proofs_debate_novelty", "claims_no_english_surface_benefit")),
    "u056": (INTENDS, "vex", ("proposes_mandatory_evidence", "covers_statistical_claims", "covers_approximate_claims")),
    "u060": (["attributed", "supplied_update", "says", ["causal", "because", "asserted", "asserted"]], "benchmark", ("focus_motivated_by_judge_ceiling", "focuses_large_untrusted_artefacts", "focuses_universal_or_negative_claims", "tests_sustained_pushback")),
    "u063": ("asserted", "draft", ("retains_oct25_milestone", "retains_50_to_5000_range", "retains_real_artefact_tests", "retains_cross_family_replication", "retains_forged_checker_control", "retains_null_publication")),
    "u064": (CAUSES, "controls", ("covers_premise_risk", "covers_meaning_risk", "covers_smuggled_premises", "covers_definition_shift")),
    "u067": (INSTRUCTION, "paste_action", ("selects_one_candidate", "excludes_label", "excludes_count")),
    "u068": ("asserted", "edits", ("replace_only_indicated_sentence", "replace_only_indicated_paragraph")),
    "u070": ("asserted", "extra_space", ("states_proof_rule", "states_proof_limits")),
    "u074": (INTENDS, "draft", ("tests_mandatory_proofs", "tests_obfuscated_arguments", "proposes_vex")),
    "u076": (INTENDS, "draft", ("tests_mandatory_proofs", "develops_vex", "aims_oversight")),
    "u078": (INTENDS, "benchmark", ("release_by_oct25", "tests_mandatory_proofs", "tests_obfuscated_arguments", "uses_50_to_5000_steps", "separates_error_classes")),
    "u079": (INSTRUCTION, "comparison", ("compares_cross_examination", "uses_matched_cost", "includes_formalisation", "includes_proof_production")),
    "u080": (INSTRUCTION, "benchmark", ("focuses_large_untrusted_artefacts", "focuses_universal_or_negative_claims")),
    "u081": (INSTRUCTION, "benchmark", ("tests_forged_checker", "tests_sustained_pushback")),
    "u082": (INSTRUCTION, "benchmark", ("includes_real_artefacts", "replicates_model_families")),
    "u084": (CAUSES, "proof_rule", ("accepts_only_checked_derivations", "excludes_assumed_false_subclaims", "blocks_barnes_christiano_for_formalised_claims")),
    "u086": (POSSIBLE, "proof_label", ("increases_false_confidence",)),
    "u088": (POSSIBLE, "formalisation", ("misstates_task",)),
    "u089": ("asserted", "claim", ("unresolved_without_affordable_proof",)),
    "u090": (INTENDS, "vex", ("requires_evidence", "requires_quality_review")),
    "u091": (CAUSES, "controls", ("tests_forged_checker", "tests_false_foundations", "tests_misleading_formalisation")),
    "u092": (CAUSES, "artefact_arm", ("includes_real_artefacts", "tests_transfer_beyond_planted_flaws")),
    "u093": (INTENDS, "draft", ("commits_publish_null_and_negative", "publishes_benchmark_harness_analysis", "publishes_even_if_no_advantage")),
}
