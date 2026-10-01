---
{
  "format": "ve-document@1",
  "environment": {
    "language": "ve.core@0.2",
    "profiles": [
      "definitions@0",
      "relational-fol@0"
    ],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
      "sorts": {
        "artifact": {
          "description": "an artifact",
          "verbalisation": {
            "singular": "artifact",
            "plural": "artifacts"
          }
        },
        "foundation_leaf": {
          "description": "a declared foundation leaf",
          "verbalisation": {
            "singular": "foundation leaf",
            "plural": "foundation leaves"
          }
        },
        "field": {
          "description": "a form field",
          "verbalisation": {
            "singular": "field",
            "plural": "fields"
          }
        }
      },
      "predicates": {
        "accepted_without_proof": {
          "arguments": [
            "foundation_leaf"
          ],
          "description": "is accepted without proof",
          "verbalisation": "{0} is accepted without proof"
        },
        "claims_vex_result": {
          "arguments": [
            "artifact"
          ],
          "description": "claims a VEX result",
          "verbalisation": "{0} claims a VEX result"
        },
        "claims_completed_extension": {
          "arguments": [
            "artifact"
          ],
          "description": "claims a completed extension",
          "verbalisation": "{0} claims a completed extension"
        },
        "reports_new_result": {
          "arguments": [
            "artifact"
          ],
          "description": "reports a new experimental result",
          "verbalisation": "{0} reports a new experimental result"
        },
        "asserts_cost_advantage": {
          "arguments": [
            "artifact"
          ],
          "description": "asserts a cost advantage",
          "verbalisation": "{0} asserts a cost advantage"
        },
        "revised": {
          "arguments": [
            "field"
          ],
          "description": "is revised",
          "verbalisation": "{0} is revised"
        },
        "includes_formalisation": {
          "arguments": [
            "artifact"
          ],
          "description": "includes formalisation",
          "verbalisation": "{0} includes formalisation"
        },
        "includes_proof_production": {
          "arguments": [
            "artifact"
          ],
          "description": "includes proof production",
          "verbalisation": "{0} includes proof production"
        },
        "includes_spaces": {
          "arguments": [
            "artifact"
          ],
          "description": "includes spaces",
          "verbalisation": "{0} includes spaces"
        },
        "includes_punctuation": {
          "arguments": [
            "artifact"
          ],
          "description": "includes punctuation",
          "verbalisation": "{0} includes punctuation"
        },
        "includes_labels": {
          "arguments": [
            "artifact"
          ],
          "description": "includes labels",
          "verbalisation": "{0} includes labels"
        },
        "includes_trailing_newlines": {
          "arguments": [
            "artifact"
          ],
          "description": "includes trailing newlines",
          "verbalisation": "{0} includes trailing newlines"
        },
        "establishes_foundation_truth": {
          "arguments": [
            "artifact"
          ],
          "description": "establishes foundation truth",
          "verbalisation": "{0} establishes foundation truth"
        },
        "establishes_faithful_formalisation": {
          "arguments": [
            "artifact"
          ],
          "description": "establishes faithful formalisation",
          "verbalisation": "{0} establishes faithful formalisation"
        },
        "guarantees_evidence_quality": {
          "arguments": [
            "artifact"
          ],
          "description": "guarantees evidence quality",
          "verbalisation": "{0} guarantees evidence quality"
        },
        "schedules_development": {
          "arguments": [
            "artifact"
          ],
          "description": "schedules evidence layer development",
          "verbalisation": "{0} schedules evidence layer development"
        },
        "conditional_on_foundations": {
          "arguments": [
            "artifact"
          ],
          "description": "is conditional on declared foundations",
          "verbalisation": "{0} is conditional on declared foundations"
        },
        "concerns_estimated_leaves": {
          "arguments": [
            "artifact"
          ],
          "description": "concerns estimated leaves",
          "verbalisation": "{0} concerns estimated leaves"
        },
        "concerns_proved_subclaims": {
          "arguments": [
            "artifact"
          ],
          "description": "concerns proved subclaims",
          "verbalisation": "{0} concerns proved subclaims"
        },
        "establishes_truth": {
          "arguments": [
            "artifact",
            "artifact"
          ],
          "description": "establishes the truth of",
          "verbalisation": "{0} establishes the truth of {1}"
        },
        "tests_checker": {
          "arguments": [
            "artifact"
          ],
          "description": "tests checker",
          "verbalisation": "{0} tests checker"
        },
        "tests_evidence_layer": {
          "arguments": [
            "artifact"
          ],
          "description": "tests evidence layer",
          "verbalisation": "{0} tests evidence layer"
        },
        "compares_cross_examination": {
          "arguments": [
            "artifact"
          ],
          "description": "compares cross examination",
          "verbalisation": "{0} compares cross examination"
        },
        "tests_mandatory_proofs": {
          "arguments": [
            "artifact"
          ],
          "description": "tests mandatory proofs",
          "verbalisation": "{0} tests mandatory proofs"
        },
        "tests_obfuscated_arguments": {
          "arguments": [
            "artifact"
          ],
          "description": "tests obfuscated arguments",
          "verbalisation": "{0} tests obfuscated arguments"
        },
        "proposes_vex": {
          "arguments": [
            "artifact"
          ],
          "description": "proposes vex",
          "verbalisation": "{0} proposes vex"
        },
        "develops_vex": {
          "arguments": [
            "artifact"
          ],
          "description": "develops vex",
          "verbalisation": "{0} develops vex"
        },
        "aims_oversight": {
          "arguments": [
            "artifact"
          ],
          "description": "aims oversight",
          "verbalisation": "{0} aims oversight"
        },
        "release_by_oct25": {
          "arguments": [
            "artifact"
          ],
          "description": "release by oct25",
          "verbalisation": "{0} release by oct25"
        },
        "tests_checker_deference": {
          "arguments": [
            "artifact"
          ],
          "description": "tests checker deference",
          "verbalisation": "{0} tests checker deference"
        },
        "tests_adversarial_pushback": {
          "arguments": [
            "artifact"
          ],
          "description": "tests adversarial pushback",
          "verbalisation": "{0} tests adversarial pushback"
        },
        "tests_definition_shift": {
          "arguments": [
            "artifact"
          ],
          "description": "tests definition shift",
          "verbalisation": "{0} tests definition shift"
        },
        "tests_smuggled_premises": {
          "arguments": [
            "artifact"
          ],
          "description": "tests smuggled premises",
          "verbalisation": "{0} tests smuggled premises"
        },
        "uses_matched_cost": {
          "arguments": [
            "artifact"
          ],
          "description": "uses matched cost",
          "verbalisation": "{0} uses matched cost"
        },
        "includes_certificate_production": {
          "arguments": [
            "artifact"
          ],
          "description": "includes certificate production",
          "verbalisation": "{0} includes certificate production"
        },
        "tests_flaw_localisation": {
          "arguments": [
            "artifact"
          ],
          "description": "tests flaw localisation",
          "verbalisation": "{0} tests flaw localisation"
        },
        "uses_50_to_5000_steps": {
          "arguments": [
            "artifact"
          ],
          "description": "uses 50 to 5000 steps",
          "verbalisation": "{0} uses 50 to 5000 steps"
        },
        "separates_error_classes": {
          "arguments": [
            "artifact"
          ],
          "description": "separates error classes",
          "verbalisation": "{0} separates error classes"
        },
        "includes_real_artefacts": {
          "arguments": [
            "artifact"
          ],
          "description": "includes real artefacts",
          "verbalisation": "{0} includes real artefacts"
        },
        "replicates_model_families": {
          "arguments": [
            "artifact"
          ],
          "description": "replicates model families",
          "verbalisation": "{0} replicates model families"
        },
        "focuses_large_untrusted_artefacts": {
          "arguments": [
            "artifact"
          ],
          "description": "focuses large untrusted artefacts",
          "verbalisation": "{0} focuses large untrusted artefacts"
        },
        "focuses_universal_or_negative_claims": {
          "arguments": [
            "artifact"
          ],
          "description": "focuses universal or negative claims",
          "verbalisation": "{0} focuses universal or negative claims"
        },
        "tests_forged_checker": {
          "arguments": [
            "artifact"
          ],
          "description": "tests forged checker",
          "verbalisation": "{0} tests forged checker"
        },
        "tests_sustained_pushback": {
          "arguments": [
            "artifact"
          ],
          "description": "tests sustained pushback",
          "verbalisation": "{0} tests sustained pushback"
        },
        "claims_implementation": {
          "arguments": [
            "artifact"
          ],
          "description": "claims implementation",
          "verbalisation": "{0} claims implementation"
        },
        "tests_equivocation": {
          "arguments": [
            "artifact"
          ],
          "description": "tests equivocation",
          "verbalisation": "{0} tests equivocation"
        },
        "accepts_only_checked_derivations": {
          "arguments": [
            "artifact"
          ],
          "description": "accepts only checked derivations",
          "verbalisation": "{0} accepts only checked derivations"
        },
        "excludes_assumed_false_subclaims": {
          "arguments": [
            "artifact"
          ],
          "description": "excludes assumed false subclaims",
          "verbalisation": "{0} excludes assumed false subclaims"
        },
        "blocks_barnes_christiano_for_formalised_claims": {
          "arguments": [
            "artifact"
          ],
          "description": "blocks barnes christiano for formalised claims",
          "verbalisation": "{0} blocks barnes christiano for formalised claims"
        },
        "increases_false_confidence": {
          "arguments": [
            "artifact"
          ],
          "description": "increases false confidence",
          "verbalisation": "{0} increases false confidence"
        },
        "tests_deference_harm": {
          "arguments": [
            "artifact"
          ],
          "description": "tests deference harm",
          "verbalisation": "{0} tests deference harm"
        },
        "tests_transfer_beyond_planted_flaws": {
          "arguments": [
            "artifact"
          ],
          "description": "tests transfer beyond planted flaws",
          "verbalisation": "{0} tests transfer beyond planted flaws"
        },
        "commits_publish_null_and_negative": {
          "arguments": [
            "artifact"
          ],
          "description": "commits publish null and negative",
          "verbalisation": "{0} commits publish null and negative"
        },
        "misstates_task": {
          "arguments": [
            "artifact"
          ],
          "description": "misstates task",
          "verbalisation": "{0} misstates task"
        },
        "unresolved_without_affordable_proof": {
          "arguments": [
            "artifact"
          ],
          "description": "unresolved without affordable proof",
          "verbalisation": "{0} unresolved without affordable proof"
        },
        "requires_evidence": {
          "arguments": [
            "artifact"
          ],
          "description": "requires evidence",
          "verbalisation": "{0} requires evidence"
        },
        "requires_quality_review": {
          "arguments": [
            "artifact"
          ],
          "description": "requires quality review",
          "verbalisation": "{0} requires quality review"
        },
        "tests_false_foundations": {
          "arguments": [
            "artifact"
          ],
          "description": "tests false foundations",
          "verbalisation": "{0} tests false foundations"
        },
        "tests_misleading_formalisation": {
          "arguments": [
            "artifact"
          ],
          "description": "tests misleading formalisation",
          "verbalisation": "{0} tests misleading formalisation"
        },
        "publishes_benchmark_harness_analysis": {
          "arguments": [
            "artifact"
          ],
          "description": "publishes benchmark harness analysis",
          "verbalisation": "{0} publishes benchmark harness analysis"
        },
        "publishes_even_if_no_advantage": {
          "arguments": [
            "artifact"
          ],
          "description": "publishes even if no advantage",
          "verbalisation": "{0} publishes even if no advantage"
        },
        "copied_from_current_form": {
          "arguments": [
            "artifact"
          ],
          "description": "copied from current form",
          "verbalisation": "{0} copied from current form"
        },
        "context_supplied_by_rapid_draft": {
          "arguments": [
            "artifact"
          ],
          "description": "context supplied by rapid draft",
          "verbalisation": "{0} context supplied by rapid draft"
        },
        "excludes_superseded_wording": {
          "arguments": [
            "artifact"
          ],
          "description": "excludes superseded wording",
          "verbalisation": "{0} excludes superseded wording"
        },
        "cites_obfuscation_recheck": {
          "arguments": [
            "artifact"
          ],
          "description": "cites obfuscation recheck",
          "verbalisation": "{0} cites obfuscation recheck"
        },
        "cites_positioning_review": {
          "arguments": [
            "artifact"
          ],
          "description": "cites positioning review",
          "verbalisation": "{0} cites positioning review"
        },
        "prevents_false_subclaims_as_new_assumptions": {
          "arguments": [
            "artifact"
          ],
          "description": "prevents false subclaims as new assumptions",
          "verbalisation": "{0} prevents false subclaims as new assumptions"
        },
        "requires_affordable_proof": {
          "arguments": [
            "artifact"
          ],
          "description": "requires affordable proof",
          "verbalisation": "{0} requires affordable proof"
        },
        "unresolved_when_proof_beyond_budget": {
          "arguments": [
            "artifact"
          ],
          "description": "unresolved when proof beyond budget",
          "verbalisation": "{0} unresolved when proof beyond budget"
        },
        "benefit_of_sound_proof_checking": {
          "arguments": [
            "artifact"
          ],
          "description": "benefit of sound proof checking",
          "verbalisation": "{0} benefit of sound proof checking"
        },
        "claims_no_proofs_debate_novelty": {
          "arguments": [
            "artifact"
          ],
          "description": "claims no proofs debate novelty",
          "verbalisation": "{0} claims no proofs debate novelty"
        },
        "claims_no_english_surface_benefit": {
          "arguments": [
            "artifact"
          ],
          "description": "claims no english surface benefit",
          "verbalisation": "{0} claims no english surface benefit"
        },
        "proposes_mandatory_evidence": {
          "arguments": [
            "artifact"
          ],
          "description": "proposes mandatory evidence",
          "verbalisation": "{0} proposes mandatory evidence"
        },
        "covers_statistical_claims": {
          "arguments": [
            "artifact"
          ],
          "description": "covers statistical claims",
          "verbalisation": "{0} covers statistical claims"
        },
        "covers_approximate_claims": {
          "arguments": [
            "artifact"
          ],
          "description": "covers approximate claims",
          "verbalisation": "{0} covers approximate claims"
        },
        "focus_motivated_by_judge_ceiling": {
          "arguments": [
            "artifact"
          ],
          "description": "focus motivated by judge ceiling",
          "verbalisation": "{0} focus motivated by judge ceiling"
        },
        "retains_oct25_milestone": {
          "arguments": [
            "artifact"
          ],
          "description": "retains oct25 milestone",
          "verbalisation": "{0} retains oct25 milestone"
        },
        "retains_50_to_5000_range": {
          "arguments": [
            "artifact"
          ],
          "description": "retains 50 to 5000 range",
          "verbalisation": "{0} retains 50 to 5000 range"
        },
        "retains_real_artefact_tests": {
          "arguments": [
            "artifact"
          ],
          "description": "retains real artefact tests",
          "verbalisation": "{0} retains real artefact tests"
        },
        "retains_cross_family_replication": {
          "arguments": [
            "artifact"
          ],
          "description": "retains cross family replication",
          "verbalisation": "{0} retains cross family replication"
        },
        "retains_forged_checker_control": {
          "arguments": [
            "artifact"
          ],
          "description": "retains forged checker control",
          "verbalisation": "{0} retains forged checker control"
        },
        "retains_null_publication": {
          "arguments": [
            "artifact"
          ],
          "description": "retains null publication",
          "verbalisation": "{0} retains null publication"
        },
        "covers_premise_risk": {
          "arguments": [
            "artifact"
          ],
          "description": "covers premise risk",
          "verbalisation": "{0} covers premise risk"
        },
        "covers_meaning_risk": {
          "arguments": [
            "artifact"
          ],
          "description": "covers meaning risk",
          "verbalisation": "{0} covers meaning risk"
        },
        "covers_smuggled_premises": {
          "arguments": [
            "artifact"
          ],
          "description": "covers smuggled premises",
          "verbalisation": "{0} covers smuggled premises"
        },
        "covers_definition_shift": {
          "arguments": [
            "artifact"
          ],
          "description": "covers definition shift",
          "verbalisation": "{0} covers definition shift"
        },
        "selects_one_candidate": {
          "arguments": [
            "artifact"
          ],
          "description": "selects one candidate",
          "verbalisation": "{0} selects one candidate"
        },
        "excludes_label": {
          "arguments": [
            "artifact"
          ],
          "description": "excludes label",
          "verbalisation": "{0} excludes label"
        },
        "excludes_count": {
          "arguments": [
            "artifact"
          ],
          "description": "excludes count",
          "verbalisation": "{0} excludes count"
        },
        "replace_only_indicated_sentence": {
          "arguments": [
            "artifact"
          ],
          "description": "replace only indicated sentence",
          "verbalisation": "{0} replace only indicated sentence"
        },
        "replace_only_indicated_paragraph": {
          "arguments": [
            "artifact"
          ],
          "description": "replace only indicated paragraph",
          "verbalisation": "{0} replace only indicated paragraph"
        },
        "states_proof_rule": {
          "arguments": [
            "artifact"
          ],
          "description": "states proof rule",
          "verbalisation": "{0} states proof rule"
        },
        "states_proof_limits": {
          "arguments": [
            "artifact"
          ],
          "description": "states proof limits",
          "verbalisation": "{0} states proof limits"
        },
        "same_task": {
          "arguments": [
            "artifact"
          ],
          "description": "same task",
          "verbalisation": "{0} same task"
        },
        "preregistered_budget": {
          "arguments": [
            "artifact"
          ],
          "description": "preregistered budget",
          "verbalisation": "{0} preregistered budget"
        },
        "all_costs_logged": {
          "arguments": [
            "artifact"
          ],
          "description": "all costs logged",
          "verbalisation": "{0} all costs logged"
        },
        "within_five_percent": {
          "arguments": [
            "artifact"
          ],
          "description": "within five percent",
          "verbalisation": "{0} within five percent"
        },
        "matched_cost": {
          "arguments": [
            "artifact"
          ],
          "description": "same task and preregistered budget; count authoring, formalisation, proof production, compute and review for both arms; absolute total-cost difference <= 5% of the larger total",
          "defined": {
            "arguments": [
              "artifact"
            ],
            "body": [
              "and",
              [
                "and",
                [
                  "and",
                  [
                    "unary",
                    "same_task",
                    [
                      "var",
                      0
                    ]
                  ],
                  [
                    "unary",
                    "preregistered_budget",
                    [
                      "var",
                      0
                    ]
                  ]
                ],
                [
                  "unary",
                  "all_costs_logged",
                  [
                    "var",
                    0
                  ]
                ]
              ],
              [
                "unary",
                "within_five_percent",
                [
                  "var",
                  0
                ]
              ]
            ]
          }
        },
        "provenance_recorded": {
          "arguments": [
            "artifact"
          ],
          "description": "provenance recorded",
          "verbalisation": "{0} provenance recorded"
        },
        "independent_task": {
          "arguments": [
            "artifact"
          ],
          "description": "independent task",
          "verbalisation": "{0} independent task"
        },
        "predates_selection": {
          "arguments": [
            "artifact"
          ],
          "description": "predates selection",
          "verbalisation": "{0} predates selection"
        },
        "no_seeded_flaw": {
          "arguments": [
            "artifact"
          ],
          "description": "no seeded flaw",
          "verbalisation": "{0} no seeded flaw"
        },
        "real_artefact": {
          "arguments": [
            "artifact"
          ],
          "description": "provenance hash and creation date recorded; created for a non-benchmark task before selection; no flaw seeded by the evaluators",
          "defined": {
            "arguments": [
              "artifact"
            ],
            "body": [
              "and",
              [
                "and",
                [
                  "and",
                  [
                    "unary",
                    "provenance_recorded",
                    [
                      "var",
                      0
                    ]
                  ],
                  [
                    "unary",
                    "independent_task",
                    [
                      "var",
                      0
                    ]
                  ]
                ],
                [
                  "unary",
                  "predates_selection",
                  [
                    "var",
                    0
                  ]
                ]
              ],
              [
                "unary",
                "no_seeded_flaw",
                [
                  "var",
                  0
                ]
              ]
            ]
          }
        },
        "costs_recorded": {
          "arguments": [
            "artifact"
          ],
          "description": "costs recorded",
          "verbalisation": "{0} costs recorded"
        },
        "certificate_checked": {
          "arguments": [
            "artifact"
          ],
          "description": "certificate checked",
          "verbalisation": "{0} certificate checked"
        },
        "within_budget": {
          "arguments": [
            "artifact"
          ],
          "description": "within budget",
          "verbalisation": "{0} within budget"
        },
        "within_deadline": {
          "arguments": [
            "artifact"
          ],
          "description": "within deadline",
          "verbalisation": "{0} within deadline"
        },
        "affordable_proof": {
          "arguments": [
            "artifact"
          ],
          "description": "proof and formalisation costs recorded; checker accepts a complete certificate; total cost <= preregistered per-claim budget and elapsed time <= preregistered deadline",
          "defined": {
            "arguments": [
              "artifact"
            ],
            "body": [
              "and",
              [
                "and",
                [
                  "and",
                  [
                    "unary",
                    "costs_recorded",
                    [
                      "var",
                      0
                    ]
                  ],
                  [
                    "unary",
                    "certificate_checked",
                    [
                      "var",
                      0
                    ]
                  ]
                ],
                [
                  "unary",
                  "within_budget",
                  [
                    "var",
                    0
                  ]
                ]
              ],
              [
                "unary",
                "within_deadline",
                [
                  "var",
                  0
                ]
              ]
            ]
          }
        },
        "source_and_formula_pinned": {
          "arguments": [
            "artifact"
          ],
          "description": "source and formula pinned",
          "verbalisation": "{0} source and formula pinned"
        },
        "answer_changing_counterexample": {
          "arguments": [
            "artifact"
          ],
          "description": "answer changing counterexample",
          "verbalisation": "{0} answer changing counterexample"
        },
        "two_blind_reproductions": {
          "arguments": [
            "artifact"
          ],
          "description": "two blind reproductions",
          "verbalisation": "{0} two blind reproductions"
        },
        "misleading_formalisation": {
          "arguments": [
            "artifact"
          ],
          "description": "source task and formula pinned; a concrete input gives different answers; two independent reviewers reproduce the difference without knowing the arm",
          "defined": {
            "arguments": [
              "artifact"
            ],
            "body": [
              "and",
              [
                "and",
                [
                  "unary",
                  "source_and_formula_pinned",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "unary",
                  "answer_changing_counterexample",
                  [
                    "var",
                    0
                  ]
                ]
              ],
              [
                "unary",
                "two_blind_reproductions",
                [
                  "var",
                  0
                ]
              ]
            ]
          }
        },
        "severity_threshold": {
          "arguments": [
            "artifact"
          ],
          "description": "severity threshold",
          "verbalisation": "{0} severity threshold"
        },
        "pathway_documented": {
          "arguments": [
            "artifact"
          ],
          "description": "pathway documented",
          "verbalisation": "{0} pathway documented"
        },
        "evidence_recorded": {
          "arguments": [
            "artifact"
          ],
          "description": "evidence recorded",
          "verbalisation": "{0} evidence recorded"
        },
        "catastrophic_risk": {
          "arguments": [
            "artifact"
          ],
          "description": "documented pathway to human extinction or at least 1,000,000 deaths; pathway evidence and severity assessment recorded; possibility is separately evaluated and is never inferred from this classification alone",
          "defined": {
            "arguments": [
              "artifact"
            ],
            "body": [
              "and",
              [
                "and",
                [
                  "unary",
                  "severity_threshold",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "unary",
                  "pathway_documented",
                  [
                    "var",
                    0
                  ]
                ]
              ],
              [
                "unary",
                "evidence_recorded",
                [
                  "var",
                  0
                ]
              ]
            ]
          }
        }
      },
      "constants": {
        "draft": {
          "sort": "artifact",
          "description": "this grant draft"
        },
        "comparison": {
          "sort": "artifact",
          "description": "the matched-cost comparison"
        },
        "counts": {
          "sort": "artifact",
          "description": "the stated character counts"
        },
        "proof_rule": {
          "sort": "artifact",
          "description": "the mandatory proof rule"
        },
        "requirements": {
          "sort": "artifact",
          "description": "the proposed evidence requirements"
        },
        "milestones": {
          "sort": "artifact",
          "description": "the existing evidence layer milestones"
        },
        "guarantee": {
          "sort": "artifact",
          "description": "the proof guarantee"
        },
        "caveat": {
          "sort": "artifact",
          "description": "the existing stability caveat"
        },
        "foundations": {
          "sort": "artifact",
          "description": "the declared foundations"
        },
        "benchmark": {
          "sort": "artifact",
          "description": "benchmark"
        },
        "proof_label": {
          "sort": "artifact",
          "description": "proof label"
        },
        "controls": {
          "sort": "artifact",
          "description": "controls"
        },
        "artefact_arm": {
          "sort": "artifact",
          "description": "artefact arm"
        },
        "formalisation": {
          "sort": "artifact",
          "description": "formalisation"
        },
        "claim": {
          "sort": "artifact",
          "description": "claim"
        },
        "vex": {
          "sort": "artifact",
          "description": "vex"
        },
        "old_text": {
          "sort": "artifact",
          "description": "old text"
        },
        "correction": {
          "sort": "artifact",
          "description": "correction"
        },
        "honest_answer": {
          "sort": "artifact",
          "description": "honest answer"
        },
        "paste_action": {
          "sort": "artifact",
          "description": "paste action"
        },
        "edits": {
          "sort": "artifact",
          "description": "edits"
        },
        "extra_space": {
          "sort": "artifact",
          "description": "extra space"
        }
      }
    }
  },
  "units": [
    {
      "id": "u001",
      "span": [
        0,
        52
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u002",
      "span": [
        52,
        56
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u003",
      "span": [
        56,
        220
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "old_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "tests_checker",
              [
                "const",
                "draft"
              ]
            ],
            [
              "unary",
              "tests_evidence_layer",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "unary",
            "compares_cross_examination",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    },
    {
      "id": "u004",
      "span": [
        220,
        224
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u005",
      "span": [
        224,
        250
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u006",
      "span": [
        250,
        267
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u007",
      "span": [
        267,
        430
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "tests_mandatory_proofs",
              [
                "const",
                "draft"
              ]
            ],
            [
              "unary",
              "tests_obfuscated_arguments",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "unary",
            "proposes_vex",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    },
    {
      "id": "u008",
      "span": [
        430,
        460
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u009",
      "span": [
        460,
        641
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "tests_mandatory_proofs",
              [
                "const",
                "draft"
              ]
            ],
            [
              "unary",
              "develops_vex",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "unary",
            "aims_oversight",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    },
    {
      "id": "u010",
      "span": [
        641,
        692
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u011",
      "span": [
        692,
        696
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u012",
      "span": [
        696,
        854
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "old_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "release_by_oct25",
              [
                "const",
                "benchmark"
              ]
            ],
            [
              "unary",
              "tests_checker_deference",
              [
                "const",
                "benchmark"
              ]
            ]
          ],
          [
            "unary",
            "tests_adversarial_pushback",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u013",
      "span": [
        854,
        974
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "old_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "and",
              [
                "unary",
                "tests_definition_shift",
                [
                  "const",
                  "comparison"
                ]
              ],
              [
                "unary",
                "tests_smuggled_premises",
                [
                  "const",
                  "comparison"
                ]
              ]
            ],
            [
              "unary",
              "uses_matched_cost",
              [
                "const",
                "comparison"
              ]
            ]
          ],
          [
            "unary",
            "includes_certificate_production",
            [
              "const",
              "comparison"
            ]
          ]
        ]
      }
    },
    {
      "id": "u014",
      "span": [
        974,
        1105
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "old_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "tests_flaw_localisation",
              [
                "const",
                "benchmark"
              ]
            ],
            [
              "unary",
              "uses_50_to_5000_steps",
              [
                "const",
                "benchmark"
              ]
            ]
          ],
          [
            "unary",
            "separates_error_classes",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u015",
      "span": [
        1105,
        1190
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "old_text",
        "says",
        "instruction"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "includes_real_artefacts",
            [
              "const",
              "benchmark"
            ]
          ],
          [
            "unary",
            "replicates_model_families",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u016",
      "span": [
        1190,
        1194
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u017",
      "span": [
        1194,
        1414
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "and",
              [
                "and",
                [
                  "unary",
                  "release_by_oct25",
                  [
                    "const",
                    "benchmark"
                  ]
                ],
                [
                  "unary",
                  "tests_mandatory_proofs",
                  [
                    "const",
                    "benchmark"
                  ]
                ]
              ],
              [
                "unary",
                "tests_obfuscated_arguments",
                [
                  "const",
                  "benchmark"
                ]
              ]
            ],
            [
              "unary",
              "uses_50_to_5000_steps",
              [
                "const",
                "benchmark"
              ]
            ]
          ],
          [
            "unary",
            "separates_error_classes",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u018",
      "span": [
        1414,
        1508
      ],
      "status": "CHECKED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "and",
              [
                "unary",
                "compares_cross_examination",
                [
                  "const",
                  "comparison"
                ]
              ],
              [
                "unary",
                "uses_matched_cost",
                [
                  "const",
                  "comparison"
                ]
              ]
            ],
            [
              "unary",
              "includes_formalisation",
              [
                "const",
                "comparison"
              ]
            ]
          ],
          [
            "unary",
            "includes_proof_production",
            [
              "const",
              "comparison"
            ]
          ]
        ]
      }
    },
    {
      "id": "u019",
      "span": [
        1508,
        1609
      ],
      "status": "CHECKED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "focuses_large_untrusted_artefacts",
            [
              "const",
              "benchmark"
            ]
          ],
          [
            "unary",
            "focuses_universal_or_negative_claims",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u020",
      "span": [
        1609,
        1681
      ],
      "status": "CHECKED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "tests_forged_checker",
            [
              "const",
              "benchmark"
            ]
          ],
          [
            "unary",
            "tests_sustained_pushback",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u021",
      "span": [
        1681,
        1744
      ],
      "status": "CHECKED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "includes_real_artefacts",
            [
              "const",
              "benchmark"
            ]
          ],
          [
            "unary",
            "replicates_model_families",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u022",
      "span": [
        1744,
        1812
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u023",
      "span": [
        1812,
        1816
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u024",
      "span": [
        1816,
        2021
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "old_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "and",
              [
                "and",
                [
                  "unary",
                  "claims_implementation",
                  [
                    "const",
                    "draft"
                  ]
                ],
                [
                  "unary",
                  "tests_smuggled_premises",
                  [
                    "const",
                    "draft"
                  ]
                ]
              ],
              [
                "unary",
                "tests_equivocation",
                [
                  "const",
                  "draft"
                ]
              ]
            ],
            [
              "unary",
              "tests_definition_shift",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "unary",
            "compares_cross_examination",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    },
    {
      "id": "u025",
      "span": [
        2021,
        2025
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u026",
      "span": [
        2025,
        2287
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "accepts_only_checked_derivations",
              [
                "const",
                "proof_rule"
              ]
            ],
            [
              "unary",
              "excludes_assumed_false_subclaims",
              [
                "const",
                "proof_rule"
              ]
            ]
          ],
          [
            "unary",
            "blocks_barnes_christiano_for_formalised_claims",
            [
              "const",
              "proof_rule"
            ]
          ]
        ]
      }
    },
    {
      "id": "u027",
      "span": [
        2287,
        2349
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u028",
      "span": [
        2349,
        2353
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u029",
      "span": [
        2353,
        2446
      ],
      "status": "CHECKED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "unary",
          "increases_false_confidence",
          [
            "const",
            "proof_label"
          ]
        ]
      }
    },
    {
      "id": "u030",
      "span": [
        2446,
        2529
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "tests_deference_harm",
              [
                "const",
                "controls"
              ]
            ],
            [
              "unary",
              "tests_definition_shift",
              [
                "const",
                "controls"
              ]
            ]
          ],
          [
            "unary",
            "tests_smuggled_premises",
            [
              "const",
              "controls"
            ]
          ]
        ]
      }
    },
    {
      "id": "u031",
      "span": [
        2529,
        2588
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "includes_real_artefacts",
            [
              "const",
              "artefact_arm"
            ]
          ],
          [
            "unary",
            "tests_transfer_beyond_planted_flaws",
            [
              "const",
              "artefact_arm"
            ]
          ]
        ]
      }
    },
    {
      "id": "u032",
      "span": [
        2588,
        2633
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "old_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "unary",
          "commits_publish_null_and_negative",
          [
            "const",
            "draft"
          ]
        ]
      }
    },
    {
      "id": "u033",
      "span": [
        2633,
        2757
      ],
      "status": "LABELLED",
      "kind": [
        "attributed",
        "applicant",
        "expects",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u034",
      "span": [
        2757,
        2761
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u035",
      "span": [
        2761,
        2808
      ],
      "status": "CHECKED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "unary",
          "increases_false_confidence",
          [
            "const",
            "proof_label"
          ]
        ]
      }
    },
    {
      "id": "u036",
      "span": [
        2808,
        2857
      ],
      "status": "CHECKED",
      "kind": "exposition",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "forall",
          "foundation_leaf",
          [
            "unary",
            "accepted_without_proof",
            [
              "var",
              0
            ]
          ]
        ]
      }
    },
    {
      "id": "u037",
      "span": [
        2857,
        2898
      ],
      "status": "CHECKED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "unary",
          "misstates_task",
          [
            "const",
            "formalisation"
          ]
        ]
      }
    },
    {
      "id": "u038",
      "span": [
        2898,
        2969
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "unary",
          "unresolved_without_affordable_proof",
          [
            "const",
            "claim"
          ]
        ]
      }
    },
    {
      "id": "u039",
      "span": [
        2969,
        3030
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "requires_evidence",
            [
              "const",
              "vex"
            ]
          ],
          [
            "unary",
            "requires_quality_review",
            [
              "const",
              "vex"
            ]
          ]
        ]
      }
    },
    {
      "id": "u040",
      "span": [
        3030,
        3119
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "tests_forged_checker",
              [
                "const",
                "controls"
              ]
            ],
            [
              "unary",
              "tests_false_foundations",
              [
                "const",
                "controls"
              ]
            ]
          ],
          [
            "unary",
            "tests_misleading_formalisation",
            [
              "const",
              "controls"
            ]
          ]
        ]
      }
    },
    {
      "id": "u041",
      "span": [
        3119,
        3149
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "includes_real_artefacts",
            [
              "const",
              "artefact_arm"
            ]
          ],
          [
            "unary",
            "tests_transfer_beyond_planted_flaws",
            [
              "const",
              "artefact_arm"
            ]
          ]
        ]
      }
    },
    {
      "id": "u042",
      "span": [
        3149,
        3279
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "commits_publish_null_and_negative",
              [
                "const",
                "draft"
              ]
            ],
            [
              "unary",
              "publishes_benchmark_harness_analysis",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "unary",
            "publishes_even_if_no_advantage",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    },
    {
      "id": "u043",
      "span": [
        3279,
        3286
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u044",
      "span": [
        3286,
        3422
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "copied_from_current_form",
            [
              "const",
              "old_text"
            ]
          ],
          [
            "unary",
            "context_supplied_by_rapid_draft",
            [
              "const",
              "old_text"
            ]
          ]
        ]
      }
    },
    {
      "id": "u045",
      "span": [
        3422,
        3465
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "unary",
          "excludes_superseded_wording",
          [
            "const",
            "old_text"
          ]
        ]
      }
    },
    {
      "id": "u046",
      "span": [
        3465,
        3676
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "cites_obfuscation_recheck",
            [
              "const",
              "correction"
            ]
          ],
          [
            "unary",
            "cites_positioning_review",
            [
              "const",
              "correction"
            ]
          ]
        ]
      }
    },
    {
      "id": "u047",
      "span": [
        3676,
        3768
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "unary",
          "prevents_false_subclaims_as_new_assumptions",
          [
            "const",
            "proof_rule"
          ]
        ]
      }
    },
    {
      "id": "u048",
      "span": [
        3768,
        3826
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "unary",
          "conditional_on_foundations",
          [
            "const",
            "guarantee"
          ]
        ]
      }
    },
    {
      "id": "u049",
      "span": [
        3826,
        3887
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "not",
            [
              "binary",
              "establishes_truth",
              [
                "const",
                "proof_rule"
              ],
              [
                "const",
                "foundations"
              ]
            ]
          ],
          [
            "not",
            [
              "unary",
              "establishes_faithful_formalisation",
              [
                "const",
                "proof_rule"
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "u050",
      "span": [
        3887,
        3937
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "unary",
          "requires_affordable_proof",
          [
            "const",
            "honest_answer"
          ]
        ]
      }
    },
    {
      "id": "u051",
      "span": [
        3937,
        3986
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "unary",
          "unresolved_when_proof_beyond_budget",
          [
            "const",
            "claim"
          ]
        ]
      }
    },
    {
      "id": "u052",
      "span": [
        3986,
        4043
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "unary",
          "benefit_of_sound_proof_checking",
          [
            "const",
            "proof_rule"
          ]
        ]
      }
    },
    {
      "id": "u053",
      "span": [
        4043,
        4121
      ],
      "status": "LABELLED",
      "kind": [
        "attributed",
        "author",
        "believes",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u054",
      "span": [
        4121,
        4204
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "claims_no_proofs_debate_novelty",
            [
              "const",
              "draft"
            ]
          ],
          [
            "unary",
            "claims_no_english_surface_benefit",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    },
    {
      "id": "u055",
      "span": [
        4204,
        4284
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "concerns_estimated_leaves",
            [
              "const",
              "caveat"
            ]
          ],
          [
            "not",
            [
              "unary",
              "concerns_proved_subclaims",
              [
                "const",
                "caveat"
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "u056",
      "span": [
        4284,
        4375
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "proposes_mandatory_evidence",
              [
                "const",
                "vex"
              ]
            ],
            [
              "unary",
              "covers_statistical_claims",
              [
                "const",
                "vex"
              ]
            ]
          ],
          [
            "unary",
            "covers_approximate_claims",
            [
              "const",
              "vex"
            ]
          ]
        ]
      }
    },
    {
      "id": "u057",
      "span": [
        4375,
        4432
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "not",
          [
            "unary",
            "guarantees_evidence_quality",
            [
              "const",
              "requirements"
            ]
          ]
        ]
      }
    },
    {
      "id": "u058",
      "span": [
        4432,
        4485
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "not",
            [
              "unary",
              "claims_vex_result",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "not",
            [
              "unary",
              "claims_completed_extension",
              [
                "const",
                "draft"
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "u059",
      "span": [
        4485,
        4557
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "unary",
          "schedules_development",
          [
            "const",
            "milestones"
          ]
        ]
      }
    },
    {
      "id": "u060",
      "span": [
        4557,
        4744
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "supplied_update",
        "says",
        [
          "causal",
          "because",
          "asserted",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "and",
              [
                "unary",
                "focus_motivated_by_judge_ceiling",
                [
                  "const",
                  "benchmark"
                ]
              ],
              [
                "unary",
                "focuses_large_untrusted_artefacts",
                [
                  "const",
                  "benchmark"
                ]
              ]
            ],
            [
              "unary",
              "focuses_universal_or_negative_claims",
              [
                "const",
                "benchmark"
              ]
            ]
          ],
          [
            "unary",
            "tests_sustained_pushback",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u061",
      "span": [
        4744,
        4835
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "not",
            [
              "unary",
              "reports_new_result",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "not",
            [
              "unary",
              "asserts_cost_advantage",
              [
                "const",
                "draft"
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "u062",
      "span": [
        4835,
        4915
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "includes_formalisation",
            [
              "const",
              "comparison"
            ]
          ],
          [
            "unary",
            "includes_proof_production",
            [
              "const",
              "comparison"
            ]
          ]
        ]
      }
    },
    {
      "id": "u063",
      "span": [
        4915,
        5091
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "and",
              [
                "and",
                [
                  "and",
                  [
                    "unary",
                    "retains_oct25_milestone",
                    [
                      "const",
                      "draft"
                    ]
                  ],
                  [
                    "unary",
                    "retains_50_to_5000_range",
                    [
                      "const",
                      "draft"
                    ]
                  ]
                ],
                [
                  "unary",
                  "retains_real_artefact_tests",
                  [
                    "const",
                    "draft"
                  ]
                ]
              ],
              [
                "unary",
                "retains_cross_family_replication",
                [
                  "const",
                  "draft"
                ]
              ]
            ],
            [
              "unary",
              "retains_forged_checker_control",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "unary",
            "retains_null_publication",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    },
    {
      "id": "u064",
      "span": [
        5091,
        5247
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "and",
              [
                "unary",
                "covers_premise_risk",
                [
                  "const",
                  "controls"
                ]
              ],
              [
                "unary",
                "covers_meaning_risk",
                [
                  "const",
                  "controls"
                ]
              ]
            ],
            [
              "unary",
              "covers_smuggled_premises",
              [
                "const",
                "controls"
              ]
            ]
          ],
          [
            "unary",
            "covers_definition_shift",
            [
              "const",
              "controls"
            ]
          ]
        ]
      }
    },
    {
      "id": "u065",
      "span": [
        5247,
        5284
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "not",
          [
            "exists",
            "field",
            [
              "unary",
              "revised",
              [
                "var",
                0
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "u066",
      "span": [
        5284,
        5377
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "includes_spaces",
              [
                "const",
                "counts"
              ]
            ],
            [
              "unary",
              "includes_punctuation",
              [
                "const",
                "counts"
              ]
            ]
          ],
          [
            "and",
            [
              "not",
              [
                "unary",
                "includes_labels",
                [
                  "const",
                  "counts"
                ]
              ]
            ],
            [
              "not",
              [
                "unary",
                "includes_trailing_newlines",
                [
                  "const",
                  "counts"
                ]
              ]
            ]
          ]
        ]
      }
    },
    {
      "id": "u067",
      "span": [
        5377,
        5444
      ],
      "status": "CHECKED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "selects_one_candidate",
              [
                "const",
                "paste_action"
              ]
            ],
            [
              "unary",
              "excludes_label",
              [
                "const",
                "paste_action"
              ]
            ]
          ],
          [
            "unary",
            "excludes_count",
            [
              "const",
              "paste_action"
            ]
          ]
        ]
      }
    },
    {
      "id": "u068",
      "span": [
        5444,
        5528
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "replace_only_indicated_sentence",
            [
              "const",
              "edits"
            ]
          ],
          [
            "unary",
            "replace_only_indicated_paragraph",
            [
              "const",
              "edits"
            ]
          ]
        ]
      }
    },
    {
      "id": "u069",
      "span": [
        5528,
        5585
      ],
      "status": "UNFORMALISED",
      "kind": [
        "attributed",
        "author",
        "believes",
        [
          "unformalised",
          "vague_comparison"
        ]
      ],
      "meaning": {
        "unformalised": "vague_comparison"
      },
      "support": "none"
    },
    {
      "id": "u070",
      "span": [
        5585,
        5640
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "states_proof_rule",
            [
              "const",
              "extra_space"
            ]
          ],
          [
            "unary",
            "states_proof_limits",
            [
              "const",
              "extra_space"
            ]
          ]
        ]
      }
    },
    {
      "id": "u071",
      "span": [
        5640,
        5655
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u072",
      "span": [
        5655,
        5708
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u073",
      "span": [
        5708,
        5724
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u074",
      "span": [
        5724,
        5887
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "tests_mandatory_proofs",
              [
                "const",
                "draft"
              ]
            ],
            [
              "unary",
              "tests_obfuscated_arguments",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "unary",
            "proposes_vex",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    },
    {
      "id": "u075",
      "span": [
        5887,
        5943
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u076",
      "span": [
        5943,
        6124
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "tests_mandatory_proofs",
              [
                "const",
                "draft"
              ]
            ],
            [
              "unary",
              "develops_vex",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "unary",
            "aims_oversight",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    },
    {
      "id": "u077",
      "span": [
        6124,
        6170
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u078",
      "span": [
        6170,
        6390
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "and",
              [
                "and",
                [
                  "unary",
                  "release_by_oct25",
                  [
                    "const",
                    "benchmark"
                  ]
                ],
                [
                  "unary",
                  "tests_mandatory_proofs",
                  [
                    "const",
                    "benchmark"
                  ]
                ]
              ],
              [
                "unary",
                "tests_obfuscated_arguments",
                [
                  "const",
                  "benchmark"
                ]
              ]
            ],
            [
              "unary",
              "uses_50_to_5000_steps",
              [
                "const",
                "benchmark"
              ]
            ]
          ],
          [
            "unary",
            "separates_error_classes",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u079",
      "span": [
        6390,
        6484
      ],
      "status": "CHECKED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "and",
              [
                "unary",
                "compares_cross_examination",
                [
                  "const",
                  "comparison"
                ]
              ],
              [
                "unary",
                "uses_matched_cost",
                [
                  "const",
                  "comparison"
                ]
              ]
            ],
            [
              "unary",
              "includes_formalisation",
              [
                "const",
                "comparison"
              ]
            ]
          ],
          [
            "unary",
            "includes_proof_production",
            [
              "const",
              "comparison"
            ]
          ]
        ]
      }
    },
    {
      "id": "u080",
      "span": [
        6484,
        6585
      ],
      "status": "CHECKED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "focuses_large_untrusted_artefacts",
            [
              "const",
              "benchmark"
            ]
          ],
          [
            "unary",
            "focuses_universal_or_negative_claims",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u081",
      "span": [
        6585,
        6657
      ],
      "status": "CHECKED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "tests_forged_checker",
            [
              "const",
              "benchmark"
            ]
          ],
          [
            "unary",
            "tests_sustained_pushback",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u082",
      "span": [
        6657,
        6720
      ],
      "status": "CHECKED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "includes_real_artefacts",
            [
              "const",
              "benchmark"
            ]
          ],
          [
            "unary",
            "replicates_model_families",
            [
              "const",
              "benchmark"
            ]
          ]
        ]
      }
    },
    {
      "id": "u083",
      "span": [
        6720,
        6783
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u084",
      "span": [
        6783,
        7045
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "accepts_only_checked_derivations",
              [
                "const",
                "proof_rule"
              ]
            ],
            [
              "unary",
              "excludes_assumed_false_subclaims",
              [
                "const",
                "proof_rule"
              ]
            ]
          ],
          [
            "unary",
            "blocks_barnes_christiano_for_formalised_claims",
            [
              "const",
              "proof_rule"
            ]
          ]
        ]
      }
    },
    {
      "id": "u085",
      "span": [
        7045,
        7102
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u086",
      "span": [
        7102,
        7149
      ],
      "status": "CHECKED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "unary",
          "increases_false_confidence",
          [
            "const",
            "proof_label"
          ]
        ]
      }
    },
    {
      "id": "u087",
      "span": [
        7149,
        7198
      ],
      "status": "CHECKED",
      "kind": "meta",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "forall",
          "foundation_leaf",
          [
            "unary",
            "accepted_without_proof",
            [
              "var",
              0
            ]
          ]
        ]
      }
    },
    {
      "id": "u088",
      "span": [
        7198,
        7239
      ],
      "status": "CHECKED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "unary",
          "misstates_task",
          [
            "const",
            "formalisation"
          ]
        ]
      }
    },
    {
      "id": "u089",
      "span": [
        7239,
        7310
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "unary",
          "unresolved_without_affordable_proof",
          [
            "const",
            "claim"
          ]
        ]
      }
    },
    {
      "id": "u090",
      "span": [
        7310,
        7371
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "requires_evidence",
            [
              "const",
              "vex"
            ]
          ],
          [
            "unary",
            "requires_quality_review",
            [
              "const",
              "vex"
            ]
          ]
        ]
      }
    },
    {
      "id": "u091",
      "span": [
        7371,
        7460
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "tests_forged_checker",
              [
                "const",
                "controls"
              ]
            ],
            [
              "unary",
              "tests_false_foundations",
              [
                "const",
                "controls"
              ]
            ]
          ],
          [
            "unary",
            "tests_misleading_formalisation",
            [
              "const",
              "controls"
            ]
          ]
        ]
      }
    },
    {
      "id": "u092",
      "span": [
        7460,
        7490
      ],
      "status": "CHECKED",
      "kind": [
        "causal",
        "because",
        "asserted",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "includes_real_artefacts",
            [
              "const",
              "artefact_arm"
            ]
          ],
          [
            "unary",
            "tests_transfer_beyond_planted_flaws",
            [
              "const",
              "artefact_arm"
            ]
          ]
        ]
      }
    },
    {
      "id": "u093",
      "span": [
        7490,
        7619
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "and",
            [
              "unary",
              "commits_publish_null_and_negative",
              [
                "const",
                "draft"
              ]
            ],
            [
              "unary",
              "publishes_benchmark_harness_analysis",
              [
                "const",
                "draft"
              ]
            ]
          ],
          [
            "unary",
            "publishes_even_if_no_advantage",
            [
              "const",
              "draft"
            ]
          ]
        ]
      }
    }
  ],
  "open_terms": [],
  "reading_sets": [
    {
      "id": "reading-u036",
      "unit": "u036",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "913dcfd9cdc8bd9db32a458ec0ff2a57011df62ebbd834b34f879c506f80fb7d",
          "content": [
            "forall",
            "foundation_leaf",
            [
              "unary",
              "accepted_without_proof",
              [
                "var",
                0
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u038",
      "unit": "u038",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "d140bc9d3a0b99ecc65a0147236d05b43a46dc9d8c6101ddd41baa8f74137cc0",
          "content": [
            "unary",
            "unresolved_without_affordable_proof",
            [
              "const",
              "claim"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u044",
      "unit": "u044",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "3712931d5fd2ccceff66b84aa1526542658121345f07799497343550a3e7dc74",
          "content": [
            "and",
            [
              "unary",
              "copied_from_current_form",
              [
                "const",
                "old_text"
              ]
            ],
            [
              "unary",
              "context_supplied_by_rapid_draft",
              [
                "const",
                "old_text"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u045",
      "unit": "u045",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "6ed5a784e5d91428382ad9ee5935a420a981287b3c1f0c1d9d023fcdc4920ecd",
          "content": [
            "unary",
            "excludes_superseded_wording",
            [
              "const",
              "old_text"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u046",
      "unit": "u046",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "3012af7b01169f7dfa9b8f2ef0a8a5fa327e8f297e26d0978af4112217ad4a8a",
          "content": [
            "and",
            [
              "unary",
              "cites_obfuscation_recheck",
              [
                "const",
                "correction"
              ]
            ],
            [
              "unary",
              "cites_positioning_review",
              [
                "const",
                "correction"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u048",
      "unit": "u048",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "8e402522c951854551da5a9e28620466a2031b9fd92012102f74f7dac02b88c9",
          "content": [
            "unary",
            "conditional_on_foundations",
            [
              "const",
              "guarantee"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u049",
      "unit": "u049",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "9458c1fa08121b017e11eba431e47a0e6a2387e5d687bc5465edc0f0e8ab3985",
          "content": [
            "and",
            [
              "not",
              [
                "binary",
                "establishes_truth",
                [
                  "const",
                  "proof_rule"
                ],
                [
                  "const",
                  "foundations"
                ]
              ]
            ],
            [
              "not",
              [
                "unary",
                "establishes_faithful_formalisation",
                [
                  "const",
                  "proof_rule"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u050",
      "unit": "u050",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "ceed7c3236e4f1091f7a950ec8e3031415aea2874876bdf9f74c91463fc91f50",
          "content": [
            "unary",
            "requires_affordable_proof",
            [
              "const",
              "honest_answer"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u051",
      "unit": "u051",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "7bcc453e32b9ad82c1d586216f8ec6fff62ad97e3344ed3142b12bd08d34cd72",
          "content": [
            "unary",
            "unresolved_when_proof_beyond_budget",
            [
              "const",
              "claim"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u054",
      "unit": "u054",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "a43f36ea25c9f39cd66daa8cc70ffc55d8b9efe8077fdc87640e09090444488c",
          "content": [
            "and",
            [
              "unary",
              "claims_no_proofs_debate_novelty",
              [
                "const",
                "draft"
              ]
            ],
            [
              "unary",
              "claims_no_english_surface_benefit",
              [
                "const",
                "draft"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u055",
      "unit": "u055",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "96350382046f5bd577b7154b89667d6f786fa809a1688f03067bc4289b099157",
          "content": [
            "and",
            [
              "unary",
              "concerns_estimated_leaves",
              [
                "const",
                "caveat"
              ]
            ],
            [
              "not",
              [
                "unary",
                "concerns_proved_subclaims",
                [
                  "const",
                  "caveat"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u057",
      "unit": "u057",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "7ab4f3575a615616a5c3d04cf1723297885881e0fb64377a09a0365864e56c61",
          "content": [
            "not",
            [
              "unary",
              "guarantees_evidence_quality",
              [
                "const",
                "requirements"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u058",
      "unit": "u058",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "c7e4aec60f45c9e479a5f1902e5d860f673367e9c67fcf05fa5dce15d2098683",
          "content": [
            "and",
            [
              "not",
              [
                "unary",
                "claims_vex_result",
                [
                  "const",
                  "draft"
                ]
              ]
            ],
            [
              "not",
              [
                "unary",
                "claims_completed_extension",
                [
                  "const",
                  "draft"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u059",
      "unit": "u059",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "782cd15fc4a9b845706c9aa565a0d7a2d0426fdc062057110ad630ca53932566",
          "content": [
            "unary",
            "schedules_development",
            [
              "const",
              "milestones"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u061",
      "unit": "u061",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "b06030f6978464b1b2e2d593a2601b8d71fe8ff7ed4c0c8b8bab87679d99d51a",
          "content": [
            "and",
            [
              "not",
              [
                "unary",
                "reports_new_result",
                [
                  "const",
                  "draft"
                ]
              ]
            ],
            [
              "not",
              [
                "unary",
                "asserts_cost_advantage",
                [
                  "const",
                  "draft"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u062",
      "unit": "u062",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "4b1a85fd32363f8d7ae10fd1de121a99cda3526112185c04c30c214a499d13d5",
          "content": [
            "and",
            [
              "unary",
              "includes_formalisation",
              [
                "const",
                "comparison"
              ]
            ],
            [
              "unary",
              "includes_proof_production",
              [
                "const",
                "comparison"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u063",
      "unit": "u063",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "86356f9e46b7e8caeb35130fb69af240e5f25b797b26cdc144ac16c4c495cd0f",
          "content": [
            "and",
            [
              "and",
              [
                "and",
                [
                  "and",
                  [
                    "and",
                    [
                      "unary",
                      "retains_oct25_milestone",
                      [
                        "const",
                        "draft"
                      ]
                    ],
                    [
                      "unary",
                      "retains_50_to_5000_range",
                      [
                        "const",
                        "draft"
                      ]
                    ]
                  ],
                  [
                    "unary",
                    "retains_real_artefact_tests",
                    [
                      "const",
                      "draft"
                    ]
                  ]
                ],
                [
                  "unary",
                  "retains_cross_family_replication",
                  [
                    "const",
                    "draft"
                  ]
                ]
              ],
              [
                "unary",
                "retains_forged_checker_control",
                [
                  "const",
                  "draft"
                ]
              ]
            ],
            [
              "unary",
              "retains_null_publication",
              [
                "const",
                "draft"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u065",
      "unit": "u065",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "8df1fc42a3e6e8f356852a288a61e6f2f02f1d27f84e9636b4346a08259eb9d6",
          "content": [
            "not",
            [
              "exists",
              "field",
              [
                "unary",
                "revised",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u066",
      "unit": "u066",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "9ea2030953ee0fff6c8c7226707b0342fea5fa63a51553c746ef48f6b1d14267",
          "content": [
            "and",
            [
              "and",
              [
                "unary",
                "includes_spaces",
                [
                  "const",
                  "counts"
                ]
              ],
              [
                "unary",
                "includes_punctuation",
                [
                  "const",
                  "counts"
                ]
              ]
            ],
            [
              "and",
              [
                "not",
                [
                  "unary",
                  "includes_labels",
                  [
                    "const",
                    "counts"
                  ]
                ]
              ],
              [
                "not",
                [
                  "unary",
                  "includes_trailing_newlines",
                  [
                    "const",
                    "counts"
                  ]
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u068",
      "unit": "u068",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "f984afc80adc4c788d963bb4b94269bb4ae59a15989f07f80717f47ff982e9f8",
          "content": [
            "and",
            [
              "unary",
              "replace_only_indicated_sentence",
              [
                "const",
                "edits"
              ]
            ],
            [
              "unary",
              "replace_only_indicated_paragraph",
              [
                "const",
                "edits"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u070",
      "unit": "u070",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "a6d7dc09f0ca0973507eadf3932690502b531cc1ff7b8bea3f1a49123c657461",
          "content": [
            "and",
            [
              "unary",
              "states_proof_rule",
              [
                "const",
                "extra_space"
              ]
            ],
            [
              "unary",
              "states_proof_limits",
              [
                "const",
                "extra_space"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u087",
      "unit": "u087",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "913dcfd9cdc8bd9db32a458ec0ff2a57011df62ebbd834b34f879c506f80fb7d",
          "content": [
            "forall",
            "foundation_leaf",
            [
              "unary",
              "accepted_without_proof",
              [
                "var",
                0
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u089",
      "unit": "u089",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "d140bc9d3a0b99ecc65a0147236d05b43a46dc9d8c6101ddd41baa8f74137cc0",
          "content": [
            "unary",
            "unresolved_without_affordable_proof",
            [
              "const",
              "claim"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Chosen reading of this source clause; scope is this draft, not an empirical verification.",
            "distinguishing_models": {}
          }
        }
      ]
    }
  ]
}
---
(a) What are you working on? (200 character limit)

OLD
Verifiable English: testing a verified checker and auditable evidence layer against cross-examination on smuggled premises, equivocation and shifting definitions.

NEW
Candidate 1 (recommended; 161 characters):
Verifiable English: testing mandatory checked proofs against obfuscated arguments, with proposed mandatory evidence (VEX) for statistical and approximate claims.

Candidate 2 (179 characters):
Testing mandatory checked proofs for formalisable claims and developing mandatory evidence (VEX) for statistical and approximate claims, to improve oversight of untrusted AI work.

(b) Tell us more about your project - Milestone 2

OLD
2. By 25 October, week 4: release benchmarks and frontier-judge results for deference to authentic versus forged checker findings under adversarial pushback; shifting definitions and smuggled premises against cross-examination at matched cost, including certificate production; and flaw localisation in arguments of 50 to 5,000 steps, separating deduction errors, false premises and misleading formalisation. Include real artefacts and replicate the earlier judge study across model families.

NEW
2. By 25 October, week 4: release benchmarks and frontier-judge results for mandatory proof against obfuscated arguments of 50 to 5,000 steps, separating deduction errors, false foundations and misleading formalisation. Compare with cross-examination at matched cost, including formalisation and proof production. Focus on large untrusted artefacts and universal or negative claims where redoing work is expensive; test authentic versus forged checker findings under sustained pushback. Include real artefacts and replication across model families.

(c) How does this reduce catastrophic risk - contribution sentence

OLD
The contribution here is an implementation and empirical tests of smuggled premises, equivocation and definitions that shift across sub-claims (gerrymandering), against cross-examination at matched cost.

NEW
The contribution here is an implementation and tests of mandatory proof: accepting only what the verified checker derives from declared, reviewed foundations blocks the Barnes-Christiano construction for formalised claims by excluding assumed false sub-claims.

(c) How does this reduce catastrophic risk - harms paragraph

OLD
A proof label could increase false confidence about premise truth or faithful formalisation. The deference, shifting-definition and smuggled-premise controls test these harms; the real-artefact arm tests transfer beyond planted flaws. Null and negative results will be published. The open benchmark, harness and failure analysis should help other oversight researchers even if VE provides no advantage.

NEW
A proof label could increase false confidence: foundation leaves remain accepted without proof, and formalisation may misstate the task. Even an honest claim remains "unresolved" without an affordable proof. VEX would require evidence whose quality still needs review. Forged-checker, false-foundation and misleading-formalisation controls test these harms; real artefacts test transfer. Null and negative results will be published, with the benchmark, harness and failure analysis, even if VE provides no advantage.

Notes

1. OLD text is copied from FORM-EDITS-2026-09-21.md, the current form text. bluedot-rapid-draft-v3.md supplies the surrounding context; its superseded wording is not used as OLD.
2. The correction follows section 3 of /Users/seyran/code/manage-agents/reviews/obfuscation-recheck.md and section 4 and Correction 2 of /Users/seyran/code/ve-integration/design/positioning-vs-debate-theory.md. Mandatory proof prevents arbitrary false sub-claims from being accepted as new assumptions; the guarantee is conditional on the declared foundations. It does not establish their truth or faithful formalisation. An honest answer still needs an affordable proof; proofs beyond budget leave the claim unresolved.
3. This is a benefit of sound proof checking in general. The existing credit to prover-estimator debate section 8 remains appropriate; no novelty for proofs plus debate or benefit from VE's English surface is claimed. The existing stability caveat concerns estimated leaves, not proved sub-claims.
4. VEX is presented as proposed mandatory evidence for statistical and approximate claims. Evidence requirements do not guarantee evidence quality, and no VEX result or completed extension is claimed. The existing evidence-layer milestones remain its development schedule.
5. The supplied update about frontier judges reaching ceiling on short, clean items motivates the focus on large untrusted artefacts, universal or negative claims and sustained pushback. The revised form text does not report new experimental results or assert a cost advantage. Formalisation and proof production are included in the matched-cost comparison.
6. The milestone date, 50-to-5,000-step range, real-artefact tests, cross-family replication, forged-checker control and publication of null and negative results are retained. False-foundation and misleading-formalisation controls cover the remaining premise and meaning risks, including smuggled premises and shifting definitions. No budget or other field is revised.
7. Character counts include spaces and punctuation but exclude labels and trailing newlines. Paste only one short-answer candidate, without its label or count. The contribution and harms edits replace only the indicated sentence and paragraph. The revised passages remain close to the current length; the extra space states the proof rule and its limits.

=== PASTE ===

What are you working on? - Candidate 1 (recommended; 161 characters)
Verifiable English: testing mandatory checked proofs against obfuscated arguments, with proposed mandatory evidence (VEX) for statistical and approximate claims.

What are you working on? - Candidate 2 (179 characters)
Testing mandatory checked proofs for formalisable claims and developing mandatory evidence (VEX) for statistical and approximate claims, to improve oversight of untrusted AI work.

Tell us more about your project - Milestone 2
2. By 25 October, week 4: release benchmarks and frontier-judge results for mandatory proof against obfuscated arguments of 50 to 5,000 steps, separating deduction errors, false foundations and misleading formalisation. Compare with cross-examination at matched cost, including formalisation and proof production. Focus on large untrusted artefacts and universal or negative claims where redoing work is expensive; test authentic versus forged checker findings under sustained pushback. Include real artefacts and replication across model families.

How does this reduce catastrophic risk - contribution sentence
The contribution here is an implementation and tests of mandatory proof: accepting only what the verified checker derives from declared, reviewed foundations blocks the Barnes-Christiano construction for formalised claims by excluding assumed false sub-claims.

How does this reduce catastrophic risk - harms paragraph
A proof label could increase false confidence: foundation leaves remain accepted without proof, and formalisation may misstate the task. Even an honest claim remains "unresolved" without an affordable proof. VEX would require evidence whose quality still needs review. Forged-checker, false-foundation and misleading-formalisation controls test these harms; real artefacts test transfer. Null and negative results will be published, with the benchmark, harness and failure analysis, even if VE provides no advantage.
