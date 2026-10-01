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
        "item": {
          "description": "a named thing the draft talks about",
          "verbalisation": {
            "singular": "item",
            "plural": "items"
          }
        },
        "claim": {
          "description": "a claim submitted for checking",
          "verbalisation": {
            "singular": "claim",
            "plural": "claims"
          }
        },
        "proof": {
          "description": "a proof of a claim",
          "verbalisation": {
            "singular": "proof",
            "plural": "proofs"
          }
        },
        "comparison": {
          "description": "a comparison of methods",
          "verbalisation": {
            "singular": "comparison",
            "plural": "comparisons"
          }
        },
        "artefact": {
          "description": "a benchmark artefact",
          "verbalisation": {
            "singular": "artefact",
            "plural": "artefacts"
          }
        },
        "formalisation": {
          "description": "a formalisation of a source task",
          "verbalisation": {
            "singular": "formalisation",
            "plural": "formalisations"
          }
        },
        "pathway": {
          "description": "a documented pathway to harm",
          "verbalisation": {
            "singular": "pathway",
            "plural": "pathways"
          }
        },
        "evidence": {
          "description": "an item of evidence",
          "verbalisation": {
            "singular": "evidence item",
            "plural": "evidence items"
          }
        },
        "candidate": {
          "description": "a short-answer candidate",
          "verbalisation": {
            "singular": "candidate",
            "plural": "candidates"
          }
        },
        "field": {
          "description": "a form field",
          "verbalisation": {
            "singular": "field",
            "plural": "fields"
          }
        },
        "foundation_leaf": {
          "description": "a declared foundation leaf",
          "verbalisation": {
            "singular": "foundation leaf",
            "plural": "foundation leaves"
          }
        },
        "harm": {
          "description": "an oversight harm",
          "verbalisation": {
            "singular": "harm",
            "plural": "harms"
          }
        }
      },
      "predicates": {
        "tested_against": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is tested against",
          "verbalisation": "{0} is tested against {1}"
        },
        "tested_on": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is tested on",
          "verbalisation": "{0} is tested on {1}"
        },
        "tested_to_improve": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is tested to improve",
          "verbalisation": "{0} is tested to improve {1}"
        },
        "developed_to_improve": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is developed to improve",
          "verbalisation": "{0} is developed to improve {1}"
        },
        "proposed": {
          "arguments": [
            "item"
          ],
          "description": "is proposed",
          "verbalisation": "{0} is proposed"
        },
        "adopted": {
          "arguments": [
            "item"
          ],
          "description": "is adopted",
          "verbalisation": "{0} is adopted"
        },
        "is_evidence": {
          "arguments": [
            "item"
          ],
          "description": "is evidence",
          "verbalisation": "{0} is evidence"
        },
        "mandatory_for": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is mandatory for",
          "verbalisation": "{0} is mandatory for {1}"
        },
        "applies_to": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is for",
          "verbalisation": "{0} is for {1}"
        },
        "tests": {
          "arguments": [
            "item",
            "harm"
          ],
          "description": "tests",
          "verbalisation": "{0} tests {1}"
        },
        "misstates_task": {
          "arguments": [
            "formalisation"
          ],
          "description": "misstates the task",
          "verbalisation": "{0} misstates the task"
        },
        "accepted_without_proof": {
          "arguments": [
            "foundation_leaf"
          ],
          "description": "is accepted without proof",
          "verbalisation": "{0} is accepted without proof"
        },
        "honest": {
          "arguments": [
            "claim"
          ],
          "description": "is honest",
          "verbalisation": "{0} is honest"
        },
        "unresolved": {
          "arguments": [
            "claim"
          ],
          "description": "is unresolved",
          "verbalisation": "{0} is unresolved"
        },
        "proof_of": {
          "arguments": [
            "proof",
            "claim"
          ],
          "description": "is a proof of",
          "verbalisation": "{0} is a proof of {1}"
        },
        "required_by": {
          "arguments": [
            "evidence",
            "item"
          ],
          "description": "is required by",
          "verbalisation": "{0} is required by {1}"
        },
        "needs_quality_review": {
          "arguments": [
            "evidence"
          ],
          "description": "still needs quality review",
          "verbalisation": "{0} still needs quality review"
        },
        "null_result": {
          "arguments": [
            "item"
          ],
          "description": "is a null result",
          "verbalisation": "{0} is a null result"
        },
        "negative_result": {
          "arguments": [
            "item"
          ],
          "description": "is a negative result",
          "verbalisation": "{0} is a negative result"
        },
        "published": {
          "arguments": [
            "item"
          ],
          "description": "is published",
          "verbalisation": "{0} is published"
        },
        "copied_from": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is copied from",
          "verbalisation": "{0} is copied from {1}"
        },
        "used_as": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is used as",
          "verbalisation": "{0} is used as {1}"
        },
        "current_form_text": {
          "arguments": [
            "item"
          ],
          "description": "is the current form text",
          "verbalisation": "{0} is the current form text"
        },
        "supplies_context": {
          "arguments": [
            "item"
          ],
          "description": "supplies the surrounding context",
          "verbalisation": "{0} supplies the surrounding context"
        },
        "follows": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "follows",
          "verbalisation": "{0} follows {1}"
        },
        "conditional_on": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is conditional on",
          "verbalisation": "{0} is conditional on {1}"
        },
        "establishes_truth_of": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "establishes the truth of",
          "verbalisation": "{0} establishes the truth of {1}"
        },
        "establishes_fidelity_of": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "establishes the faithful formalisation of",
          "verbalisation": "{0} establishes the faithful formalisation of {1}"
        },
        "benefit_of": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is a benefit of",
          "verbalisation": "{0} is a benefit of {1}"
        },
        "claims": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "claims",
          "verbalisation": "{0} claims {1}"
        },
        "asserts": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "asserts",
          "verbalisation": "{0} asserts {1}"
        },
        "reports": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "reports",
          "verbalisation": "{0} reports {1}"
        },
        "concerns": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "concerns",
          "verbalisation": "{0} concerns {1}"
        },
        "guarantees": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "guarantees",
          "verbalisation": "{0} guarantees {1}"
        },
        "schedules": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "is the development schedule of",
          "verbalisation": "{0} is the development schedule of {1}"
        },
        "counts_cost": {
          "arguments": [
            "comparison",
            "item"
          ],
          "description": "includes the cost of",
          "verbalisation": "{0} includes the cost of {1}"
        },
        "revised": {
          "arguments": [
            "field"
          ],
          "description": "is revised",
          "verbalisation": "{0} is revised"
        },
        "includes": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "includes",
          "verbalisation": "{0} includes {1}"
        },
        "pasted": {
          "arguments": [
            "candidate"
          ],
          "description": "is pasted",
          "verbalisation": "{0} is pasted"
        },
        "pasted_with": {
          "arguments": [
            "candidate",
            "item"
          ],
          "description": "is pasted with",
          "verbalisation": "{0} is pasted with {1}"
        },
        "replaces": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "replaces",
          "verbalisation": "{0} replaces {1}"
        },
        "states": {
          "arguments": [
            "item",
            "item"
          ],
          "description": "states",
          "verbalisation": "{0} states {1}"
        },
        "tests_transfer": {
          "arguments": [
            "artefact"
          ],
          "description": "tests transfer",
          "verbalisation": "{0} tests transfer"
        },
        "included_in": {
          "arguments": [
            "artefact",
            "item"
          ],
          "description": "is included in",
          "verbalisation": "{0} is included in {1}"
        },
        "same_task": {
          "arguments": [
            "comparison"
          ],
          "description": "author-choice clause of matched_cost: uses the same task for both arms",
          "verbalisation": "{0} uses the same task for both arms"
        },
        "budget_preregistered": {
          "arguments": [
            "comparison"
          ],
          "description": "author-choice clause of matched_cost: has a budget registered before the comparison starts",
          "verbalisation": "{0} has a budget registered before the comparison starts"
        },
        "totals_within_tolerance": {
          "arguments": [
            "comparison"
          ],
          "description": "author-choice clause of matched_cost: has arm totals that differ by at most 5% of the larger total",
          "verbalisation": "{0} has arm totals that differ by at most 5% of the larger total"
        },
        "matched_cost": {
          "arguments": [
            "comparison"
          ],
          "description": "Author choice signed by grant-author. Rule: same task; budget registered before the comparison starts; count authoring, formalisation, proof production, compute and review for both arms; absolute total-cost difference at most 5% of the larger total. Why: A comparison must count the work that each method actually requires.",
          "verbalisation": "{0} is at matched cost",
          "defined": {
            "arguments": [
              "comparison"
            ],
            "body": [
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
                "and",
                [
                  "unary",
                  "budget_preregistered",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "and",
                  [
                    "binary",
                    "counts_cost",
                    [
                      "var",
                      0
                    ],
                    [
                      "const",
                      "authoring"
                    ]
                  ],
                  [
                    "and",
                    [
                      "binary",
                      "counts_cost",
                      [
                        "var",
                        0
                      ],
                      [
                        "const",
                        "formalisation_work"
                      ]
                    ],
                    [
                      "and",
                      [
                        "binary",
                        "counts_cost",
                        [
                          "var",
                          0
                        ],
                        [
                          "const",
                          "proof_production"
                        ]
                      ],
                      [
                        "and",
                        [
                          "binary",
                          "counts_cost",
                          [
                            "var",
                            0
                          ],
                          [
                            "const",
                            "compute"
                          ]
                        ],
                        [
                          "and",
                          [
                            "binary",
                            "counts_cost",
                            [
                              "var",
                              0
                            ],
                            [
                              "const",
                              "review"
                            ]
                          ],
                          [
                            "unary",
                            "totals_within_tolerance",
                            [
                              "var",
                              0
                            ]
                          ]
                        ]
                      ]
                    ]
                  ]
                ]
              ]
            ]
          }
        },
        "provenance_recorded": {
          "arguments": [
            "artefact"
          ],
          "description": "author-choice clause of real_artefact: has a recorded provenance hash",
          "verbalisation": "{0} has a recorded provenance hash"
        },
        "independent_task": {
          "arguments": [
            "artefact"
          ],
          "description": "author-choice clause of real_artefact: was created for a non-benchmark task",
          "verbalisation": "{0} was created for a non-benchmark task"
        },
        "predates_selection": {
          "arguments": [
            "artefact"
          ],
          "description": "author-choice clause of real_artefact: was created before it was selected",
          "verbalisation": "{0} was created before it was selected"
        },
        "no_seeded_flaw": {
          "arguments": [
            "artefact"
          ],
          "description": "author-choice clause of real_artefact: has no flaw seeded by the evaluators",
          "verbalisation": "{0} has no flaw seeded by the evaluators"
        },
        "real_artefact": {
          "arguments": [
            "artefact"
          ],
          "description": "Author choice signed by grant-author. Rule: provenance SHA-256 recorded; created for a non-benchmark task; created before it was selected; no flaw seeded by the evaluators. Why: The transfer arm should use material made for an independent purpose.",
          "verbalisation": "{0} is a real artefact",
          "defined": {
            "arguments": [
              "artefact"
            ],
            "body": [
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
                "and",
                [
                  "unary",
                  "independent_task",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "and",
                  [
                    "unary",
                    "predates_selection",
                    [
                      "var",
                      0
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
              ]
            ]
          }
        },
        "proof_cost_recorded": {
          "arguments": [
            "proof"
          ],
          "description": "author-choice clause of affordable_proof: has its proof cost recorded",
          "verbalisation": "{0} has its proof cost recorded"
        },
        "formalisation_cost_recorded": {
          "arguments": [
            "proof"
          ],
          "description": "author-choice clause of affordable_proof: has its formalisation cost recorded",
          "verbalisation": "{0} has its formalisation cost recorded"
        },
        "certificate_complete": {
          "arguments": [
            "proof"
          ],
          "description": "author-choice clause of affordable_proof: has a complete certificate",
          "verbalisation": "{0} has a complete certificate"
        },
        "certificate_checked": {
          "arguments": [
            "proof"
          ],
          "description": "author-choice clause of affordable_proof: has a certificate the checker accepts",
          "verbalisation": "{0} has a certificate the checker accepts"
        },
        "claim_budget_preregistered": {
          "arguments": [
            "proof"
          ],
          "description": "author-choice clause of affordable_proof: has a budget registered before the claim",
          "verbalisation": "{0} has a budget registered before the claim"
        },
        "claim_deadline_preregistered": {
          "arguments": [
            "proof"
          ],
          "description": "author-choice clause of affordable_proof: has a deadline registered before the claim",
          "verbalisation": "{0} has a deadline registered before the claim"
        },
        "within_budget": {
          "arguments": [
            "proof"
          ],
          "description": "author-choice clause of affordable_proof: has a total cost within its registered budget",
          "verbalisation": "{0} has a total cost within its registered budget"
        },
        "within_deadline": {
          "arguments": [
            "proof"
          ],
          "description": "author-choice clause of affordable_proof: has an elapsed time within its registered deadline",
          "verbalisation": "{0} has an elapsed time within its registered deadline"
        },
        "affordable_proof": {
          "arguments": [
            "proof"
          ],
          "description": "Author choice signed by grant-author. Rule: proof cost and formalisation cost recorded; the checker accepts a complete certificate; budget and deadline registered before the claim; total cost within that budget and elapsed time within that deadline. Why: Affordability must include the full route to a checked certificate.",
          "verbalisation": "{0} is an affordable proof",
          "defined": {
            "arguments": [
              "proof"
            ],
            "body": [
              "and",
              [
                "unary",
                "proof_cost_recorded",
                [
                  "var",
                  0
                ]
              ],
              [
                "and",
                [
                  "unary",
                  "formalisation_cost_recorded",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "and",
                  [
                    "unary",
                    "certificate_complete",
                    [
                      "var",
                      0
                    ]
                  ],
                  [
                    "and",
                    [
                      "unary",
                      "certificate_checked",
                      [
                        "var",
                        0
                      ]
                    ],
                    [
                      "and",
                      [
                        "unary",
                        "claim_budget_preregistered",
                        [
                          "var",
                          0
                        ]
                      ],
                      [
                        "and",
                        [
                          "unary",
                          "claim_deadline_preregistered",
                          [
                            "var",
                            0
                          ]
                        ],
                        [
                          "and",
                          [
                            "unary",
                            "within_budget",
                            [
                              "var",
                              0
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
                      ]
                    ]
                  ]
                ]
              ]
            ]
          }
        },
        "source_pinned": {
          "arguments": [
            "formalisation"
          ],
          "description": "author-choice clause of misleading_formalisation: has a pinned source-task hash",
          "verbalisation": "{0} has a pinned source-task hash"
        },
        "formula_pinned": {
          "arguments": [
            "formalisation"
          ],
          "description": "author-choice clause of misleading_formalisation: has a pinned formula hash",
          "verbalisation": "{0} has a pinned formula hash"
        },
        "answer_changing_counterexample": {
          "arguments": [
            "formalisation"
          ],
          "description": "author-choice clause of misleading_formalisation: has a concrete input with a different answer",
          "verbalisation": "{0} has a concrete input with a different answer"
        },
        "two_reproductions": {
          "arguments": [
            "formalisation"
          ],
          "description": "author-choice clause of misleading_formalisation: has the difference reproduced by two distinct reviewers",
          "verbalisation": "{0} has the difference reproduced by two distinct reviewers"
        },
        "reviewers_blind": {
          "arguments": [
            "formalisation"
          ],
          "description": "author-choice clause of misleading_formalisation: has every reproducing reviewer blind to the arm",
          "verbalisation": "{0} has every reproducing reviewer blind to the arm"
        },
        "misleading_formalisation": {
          "arguments": [
            "formalisation"
          ],
          "description": "Author choice signed by grant-author. Rule: source task and formula hashes pinned; a concrete input on which the formula and the source task give different answers; two distinct reviewers, each blind to the arm, reproduce that difference. Why: A fidelity failure needs an inspectable difference from the source task.",
          "verbalisation": "{0} is a misleading formalisation",
          "defined": {
            "arguments": [
              "formalisation"
            ],
            "body": [
              "and",
              [
                "unary",
                "source_pinned",
                [
                  "var",
                  0
                ]
              ],
              [
                "and",
                [
                  "unary",
                  "formula_pinned",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "and",
                  [
                    "unary",
                    "answer_changing_counterexample",
                    [
                      "var",
                      0
                    ]
                  ],
                  [
                    "and",
                    [
                      "unary",
                      "two_reproductions",
                      [
                        "var",
                        0
                      ]
                    ],
                    [
                      "unary",
                      "reviewers_blind",
                      [
                        "var",
                        0
                      ]
                    ]
                  ]
                ]
              ]
            ]
          }
        },
        "pathway_documented": {
          "arguments": [
            "pathway"
          ],
          "description": "author-choice clause of catastrophic_risk: has a documented pathway",
          "verbalisation": "{0} has a documented pathway"
        },
        "evidence_recorded": {
          "arguments": [
            "pathway"
          ],
          "description": "author-choice clause of catastrophic_risk: has its pathway evidence recorded",
          "verbalisation": "{0} has its pathway evidence recorded"
        },
        "severity_assessed": {
          "arguments": [
            "pathway"
          ],
          "description": "author-choice clause of catastrophic_risk: has a recorded severity assessment",
          "verbalisation": "{0} has a recorded severity assessment"
        },
        "meets_severity_threshold": {
          "arguments": [
            "pathway"
          ],
          "description": "author-choice clause of catastrophic_risk: reaches human extinction or at least 1,000,000 projected deaths",
          "verbalisation": "{0} reaches human extinction or at least 1,000,000 projected deaths"
        },
        "catastrophic_risk": {
          "arguments": [
            "pathway"
          ],
          "description": "Author choice signed by grant-author. Rule: documented pathway to human extinction or at least 1,000,000 projected deaths; pathway evidence and a severity assessment recorded; possibility is a separate judgment and is never inferred from this classification. Why: The grant question needs a severity boundary and a separate possibility judgment.",
          "verbalisation": "{0} is a catastrophic risk",
          "defined": {
            "arguments": [
              "pathway"
            ],
            "body": [
              "and",
              [
                "unary",
                "pathway_documented",
                [
                  "var",
                  0
                ]
              ],
              [
                "and",
                [
                  "unary",
                  "evidence_recorded",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "and",
                  [
                    "unary",
                    "severity_assessed",
                    [
                      "var",
                      0
                    ]
                  ],
                  [
                    "unary",
                    "meets_severity_threshold",
                    [
                      "var",
                      0
                    ]
                  ]
                ]
              ]
            ]
          }
        }
      },
      "constants": {
        "verified_checker": {
          "sort": "item",
          "description": "the verified checker"
        },
        "evidence_layer": {
          "sort": "item",
          "description": "the auditable evidence layer"
        },
        "cross_examination": {
          "sort": "item",
          "description": "cross-examination"
        },
        "smuggled_premises": {
          "sort": "item",
          "description": "smuggled premises"
        },
        "equivocation": {
          "sort": "item",
          "description": "equivocation"
        },
        "shifting_definitions": {
          "sort": "item",
          "description": "shifting definitions"
        },
        "mandatory_checked_proofs": {
          "sort": "item",
          "description": "mandatory checked proofs"
        },
        "obfuscated_arguments": {
          "sort": "item",
          "description": "obfuscated arguments"
        },
        "vex": {
          "sort": "item",
          "description": "VEX"
        },
        "statistical_claims": {
          "sort": "item",
          "description": "statistical claims"
        },
        "approximate_claims": {
          "sort": "item",
          "description": "approximate claims"
        },
        "formalisable_claims": {
          "sort": "item",
          "description": "formalisable claims"
        },
        "oversight": {
          "sort": "item",
          "description": "oversight of untrusted AI work"
        },
        "deference_control": {
          "sort": "item",
          "description": "the deference control"
        },
        "shifting_definition_control": {
          "sort": "item",
          "description": "the shifting-definition control"
        },
        "smuggled_premise_control": {
          "sort": "item",
          "description": "the smuggled-premise control"
        },
        "benchmark": {
          "sort": "item",
          "description": "the benchmark"
        },
        "harness": {
          "sort": "item",
          "description": "the harness"
        },
        "failure_analysis": {
          "sort": "item",
          "description": "the failure analysis"
        },
        "old_text": {
          "sort": "item",
          "description": "OLD"
        },
        "form_edits_file": {
          "sort": "item",
          "description": "FORM-EDITS-2026-09-21.md"
        },
        "rapid_draft": {
          "sort": "item",
          "description": "bluedot-rapid-draft-v3.md"
        },
        "superseded_wording": {
          "sort": "item",
          "description": "the superseded wording of bluedot-rapid-draft-v3.md"
        },
        "correction": {
          "sort": "item",
          "description": "the correction"
        },
        "recheck_section": {
          "sort": "item",
          "description": "section 3 of /Users/seyran/code/manage-agents/reviews/obfuscation-recheck.md"
        },
        "positioning_section": {
          "sort": "item",
          "description": "section 4 of /Users/seyran/code/ve-integration/design/positioning-vs-debate-theory.md"
        },
        "positioning_correction": {
          "sort": "item",
          "description": "Correction 2 of /Users/seyran/code/ve-integration/design/positioning-vs-debate-theory.md"
        },
        "guarantee": {
          "sort": "item",
          "description": "the guarantee of mandatory proof"
        },
        "declared_foundations": {
          "sort": "item",
          "description": "the declared foundations"
        },
        "prevention": {
          "sort": "item",
          "description": "mandatory proof preventing arbitrary false sub-claims from being accepted as new assumptions"
        },
        "sound_proof_checking": {
          "sort": "item",
          "description": "sound proof checking in general"
        },
        "draft": {
          "sort": "item",
          "description": "this draft"
        },
        "debate_novelty": {
          "sort": "item",
          "description": "novelty for proofs plus debate"
        },
        "english_surface_benefit": {
          "sort": "item",
          "description": "a benefit from VE's English surface"
        },
        "stability_caveat": {
          "sort": "item",
          "description": "the existing stability caveat"
        },
        "estimated_leaves": {
          "sort": "item",
          "description": "estimated leaves"
        },
        "proved_subclaims": {
          "sort": "item",
          "description": "proved sub-claims"
        },
        "evidence_requirements": {
          "sort": "item",
          "description": "evidence requirements"
        },
        "evidence_quality": {
          "sort": "item",
          "description": "evidence quality"
        },
        "vex_result": {
          "sort": "item",
          "description": "a VEX result"
        },
        "completed_extension": {
          "sort": "item",
          "description": "a completed extension"
        },
        "evidence_layer_milestones": {
          "sort": "item",
          "description": "the existing evidence-layer milestones"
        },
        "revised_form_text": {
          "sort": "item",
          "description": "the revised form text"
        },
        "new_results": {
          "sort": "item",
          "description": "new experimental results"
        },
        "cost_advantage": {
          "sort": "item",
          "description": "a cost advantage"
        },
        "character_counts": {
          "sort": "item",
          "description": "the character counts"
        },
        "spaces": {
          "sort": "item",
          "description": "spaces"
        },
        "punctuation": {
          "sort": "item",
          "description": "punctuation"
        },
        "labels": {
          "sort": "item",
          "description": "labels"
        },
        "trailing_newlines": {
          "sort": "item",
          "description": "trailing newlines"
        },
        "its_label": {
          "sort": "item",
          "description": "the candidate's label"
        },
        "its_count": {
          "sort": "item",
          "description": "the candidate's count"
        },
        "contribution_edit": {
          "sort": "item",
          "description": "the contribution edit"
        },
        "harms_edit": {
          "sort": "item",
          "description": "the harms edit"
        },
        "indicated_sentence": {
          "sort": "item",
          "description": "the indicated sentence"
        },
        "indicated_paragraph": {
          "sort": "item",
          "description": "the indicated paragraph"
        },
        "extra_space": {
          "sort": "item",
          "description": "the extra space in the revised passages"
        },
        "proof_rule": {
          "sort": "item",
          "description": "the proof rule"
        },
        "proof_rule_limits": {
          "sort": "item",
          "description": "the limits of the proof rule"
        },
        "authoring": {
          "sort": "item",
          "description": "authoring"
        },
        "formalisation_work": {
          "sort": "item",
          "description": "formalisation"
        },
        "proof_production": {
          "sort": "item",
          "description": "proof production"
        },
        "compute": {
          "sort": "item",
          "description": "compute"
        },
        "review": {
          "sort": "item",
          "description": "review"
        },
        "revised_comparison": {
          "sort": "comparison",
          "description": "the matched-cost comparison in the revised form text"
        },
        "false_confidence": {
          "sort": "harm",
          "description": "increased false confidence"
        },
        "premise_confidence": {
          "sort": "harm",
          "description": "increased false confidence about premise truth"
        },
        "fidelity_confidence": {
          "sort": "harm",
          "description": "increased false confidence about faithful formalisation"
        },
        "false_subclaim_accepted": {
          "sort": "harm",
          "description": "an arbitrary false sub-claim accepted as a new assumption"
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
            "binary",
            "tested_against",
            [
              "const",
              "verified_checker"
            ],
            [
              "const",
              "cross_examination"
            ]
          ],
          [
            "and",
            [
              "binary",
              "tested_against",
              [
                "const",
                "evidence_layer"
              ],
              [
                "const",
                "cross_examination"
              ]
            ],
            [
              "and",
              [
                "binary",
                "tested_on",
                [
                  "const",
                  "verified_checker"
                ],
                [
                  "const",
                  "smuggled_premises"
                ]
              ],
              [
                "and",
                [
                  "binary",
                  "tested_on",
                  [
                    "const",
                    "verified_checker"
                  ],
                  [
                    "const",
                    "equivocation"
                  ]
                ],
                [
                  "and",
                  [
                    "binary",
                    "tested_on",
                    [
                      "const",
                      "verified_checker"
                    ],
                    [
                      "const",
                      "shifting_definitions"
                    ]
                  ],
                  [
                    "and",
                    [
                      "binary",
                      "tested_on",
                      [
                        "const",
                        "evidence_layer"
                      ],
                      [
                        "const",
                        "smuggled_premises"
                      ]
                    ],
                    [
                      "and",
                      [
                        "binary",
                        "tested_on",
                        [
                          "const",
                          "evidence_layer"
                        ],
                        [
                          "const",
                          "equivocation"
                        ]
                      ],
                      [
                        "binary",
                        "tested_on",
                        [
                          "const",
                          "evidence_layer"
                        ],
                        [
                          "const",
                          "shifting_definitions"
                        ]
                      ]
                    ]
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "3f167dfcc53809bb7419e5273f1cc00e59751e3fd25d91d0fcd6334a172b4090"
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
        "candidate_1",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "binary",
            "tested_on",
            [
              "const",
              "mandatory_checked_proofs"
            ],
            [
              "const",
              "obfuscated_arguments"
            ]
          ],
          [
            "and",
            [
              "unary",
              "proposed",
              [
                "const",
                "vex"
              ]
            ],
            [
              "and",
              [
                "unary",
                "is_evidence",
                [
                  "const",
                  "vex"
                ]
              ],
              [
                "implies",
                [
                  "unary",
                  "adopted",
                  [
                    "const",
                    "vex"
                  ]
                ],
                [
                  "and",
                  [
                    "binary",
                    "mandatory_for",
                    [
                      "const",
                      "vex"
                    ],
                    [
                      "const",
                      "statistical_claims"
                    ]
                  ],
                  [
                    "binary",
                    "mandatory_for",
                    [
                      "const",
                      "vex"
                    ],
                    [
                      "const",
                      "approximate_claims"
                    ]
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "6bff4ef20b9f9759c63cf66b03df599a4f69b04cc38d56deac56eac97e528950"
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
        "candidate_2",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "binary",
            "tested_to_improve",
            [
              "const",
              "mandatory_checked_proofs"
            ],
            [
              "const",
              "oversight"
            ]
          ],
          [
            "and",
            [
              "binary",
              "applies_to",
              [
                "const",
                "mandatory_checked_proofs"
              ],
              [
                "const",
                "formalisable_claims"
              ]
            ],
            [
              "and",
              [
                "binary",
                "developed_to_improve",
                [
                  "const",
                  "vex"
                ],
                [
                  "const",
                  "oversight"
                ]
              ],
              [
                "and",
                [
                  "unary",
                  "is_evidence",
                  [
                    "const",
                    "vex"
                  ]
                ],
                [
                  "implies",
                  [
                    "unary",
                    "adopted",
                    [
                      "const",
                      "vex"
                    ]
                  ],
                  [
                    "and",
                    [
                      "binary",
                      "mandatory_for",
                      [
                        "const",
                        "vex"
                      ],
                      [
                        "const",
                        "statistical_claims"
                      ]
                    ],
                    [
                      "binary",
                      "mandatory_for",
                      [
                        "const",
                        "vex"
                      ],
                      [
                        "const",
                        "approximate_claims"
                      ]
                    ]
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "19ebb1e81053364c0221dff065b6b816dcdde2cb008ec4f3ed82f092744ca3f3"
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
      "status": "LABELLED",
      "kind": [
        "attributed",
        "old_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u013",
      "span": [
        854,
        974
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "old_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": {
        "open": [
          "matched_cost"
        ]
      },
      "support": "none"
    },
    {
      "id": "u014",
      "span": [
        974,
        1105
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "old_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": {
        "open": [
          "misleading_formalisation"
        ]
      },
      "support": "none"
    },
    {
      "id": "u015",
      "span": [
        1105,
        1190
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "old_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": {
        "open": [
          "real_artefact"
        ]
      },
      "support": "none"
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
      "status": "OPEN",
      "kind": [
        "attributed",
        "new_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": {
        "open": [
          "misleading_formalisation"
        ]
      },
      "support": "none"
    },
    {
      "id": "u018",
      "span": [
        1414,
        1508
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "new_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": {
        "open": [
          "matched_cost"
        ]
      },
      "support": "none"
    },
    {
      "id": "u019",
      "span": [
        1508,
        1609
      ],
      "status": "LABELLED",
      "kind": [
        "attributed",
        "new_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u020",
      "span": [
        1609,
        1681
      ],
      "status": "LABELLED",
      "kind": [
        "attributed",
        "new_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u021",
      "span": [
        1681,
        1744
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "new_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": {
        "open": [
          "real_artefact"
        ]
      },
      "support": "none"
    },
    {
      "id": "u022",
      "span": [
        1744,
        1812
      ],
      "status": "OPEN",
      "kind": "question",
      "meaning": {
        "open": [
          "catastrophic_risk"
        ]
      },
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
      "status": "OPEN",
      "kind": [
        "attributed",
        "old_text",
        "says",
        "asserted"
      ],
      "meaning": {
        "open": [
          "matched_cost"
        ]
      },
      "support": "none"
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
      "status": "UNFORMALISED",
      "kind": [
        "attributed",
        "new_text",
        "says",
        [
          "unformalised",
          "causal_means"
        ]
      ],
      "meaning": {
        "unformalised": "causal_means"
      },
      "support": "none"
    },
    {
      "id": "u027",
      "span": [
        2287,
        2349
      ],
      "status": "OPEN",
      "kind": "question",
      "meaning": {
        "open": [
          "catastrophic_risk"
        ]
      },
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
      "status": "UNFORMALISED",
      "kind": [
        "attributed",
        "old_text",
        "says",
        [
          "hedged",
          "could",
          [
            "unformalised",
            "causal_route_excludes_definitions"
          ]
        ]
      ],
      "meaning": {
        "unformalised": "causal_route_excludes_definitions"
      },
      "support": "none"
    },
    {
      "id": "u030",
      "span": [
        2446,
        2529
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
            "or",
            [
              "binary",
              "tests",
              [
                "const",
                "deference_control"
              ],
              [
                "const",
                "premise_confidence"
              ]
            ],
            [
              "binary",
              "tests",
              [
                "const",
                "deference_control"
              ],
              [
                "const",
                "fidelity_confidence"
              ]
            ]
          ],
          [
            "and",
            [
              "or",
              [
                "binary",
                "tests",
                [
                  "const",
                  "shifting_definition_control"
                ],
                [
                  "const",
                  "premise_confidence"
                ]
              ],
              [
                "binary",
                "tests",
                [
                  "const",
                  "shifting_definition_control"
                ],
                [
                  "const",
                  "fidelity_confidence"
                ]
              ]
            ],
            [
              "and",
              [
                "or",
                [
                  "binary",
                  "tests",
                  [
                    "const",
                    "smuggled_premise_control"
                  ],
                  [
                    "const",
                    "premise_confidence"
                  ]
                ],
                [
                  "binary",
                  "tests",
                  [
                    "const",
                    "smuggled_premise_control"
                  ],
                  [
                    "const",
                    "fidelity_confidence"
                  ]
                ]
              ],
              [
                "and",
                [
                  "or",
                  [
                    "binary",
                    "tests",
                    [
                      "const",
                      "deference_control"
                    ],
                    [
                      "const",
                      "premise_confidence"
                    ]
                  ],
                  [
                    "or",
                    [
                      "binary",
                      "tests",
                      [
                        "const",
                        "shifting_definition_control"
                      ],
                      [
                        "const",
                        "premise_confidence"
                      ]
                    ],
                    [
                      "binary",
                      "tests",
                      [
                        "const",
                        "smuggled_premise_control"
                      ],
                      [
                        "const",
                        "premise_confidence"
                      ]
                    ]
                  ]
                ],
                [
                  "or",
                  [
                    "binary",
                    "tests",
                    [
                      "const",
                      "deference_control"
                    ],
                    [
                      "const",
                      "fidelity_confidence"
                    ]
                  ],
                  [
                    "or",
                    [
                      "binary",
                      "tests",
                      [
                        "const",
                        "shifting_definition_control"
                      ],
                      [
                        "const",
                        "fidelity_confidence"
                      ]
                    ],
                    [
                      "binary",
                      "tests",
                      [
                        "const",
                        "smuggled_premise_control"
                      ],
                      [
                        "const",
                        "fidelity_confidence"
                      ]
                    ]
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "cd6230d3ca9005cbf5091948a86cae70066786b9a9198a48973e123c00407f8c"
    },
    {
      "id": "u031",
      "span": [
        2529,
        2588
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "old_text",
        "says",
        "asserted"
      ],
      "meaning": {
        "open": [
          "real_artefact"
        ]
      },
      "support": "none"
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
        [
          "attributed",
          "applicant",
          "promised",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "forall",
          "item",
          [
            "implies",
            [
              "or",
              [
                "unary",
                "null_result",
                [
                  "var",
                  0
                ]
              ],
              [
                "unary",
                "negative_result",
                [
                  "var",
                  0
                ]
              ]
            ],
            [
              "unary",
              "published",
              [
                "var",
                0
              ]
            ]
          ]
        ]
      },
      "meaning_id": "5af8f8e26f6971c47957a608c8eda3a2f43597b1cfad11f0cfcff5fdf374eb10"
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
        "old_text",
        "says",
        [
          "attributed",
          "applicant",
          "expects",
          "asserted"
        ]
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
      "status": "UNFORMALISED",
      "kind": [
        "attributed",
        "new_text",
        "says",
        [
          "hedged",
          "could",
          [
            "unformalised",
            "causal_route_excludes_definitions"
          ]
        ]
      ],
      "meaning": {
        "unformalised": "causal_route_excludes_definitions"
      },
      "support": "none"
    },
    {
      "id": "u036",
      "span": [
        2808,
        2857
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "new_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
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
      },
      "meaning_id": "2791f77e0646ce20fd420318a65c06a48049d58d7702353b26fd84f2d184ac75"
    },
    {
      "id": "u037",
      "span": [
        2857,
        2898
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "new_text",
        "says",
        [
          "hedged",
          "could",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "exists",
          "formalisation",
          [
            "unary",
            "misstates_task",
            [
              "var",
              0
            ]
          ]
        ]
      },
      "meaning_id": "fa0c0c6ef4c8436c0d2ac9e54fd0724d77b84895d1f292e4df00118e3fd96fb5"
    },
    {
      "id": "u038",
      "span": [
        2898,
        2969
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "new_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "forall",
          "claim",
          [
            "implies",
            [
              "and",
              [
                "unary",
                "honest",
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "exists",
                  "proof",
                  [
                    "and",
                    [
                      "binary",
                      "proof_of",
                      [
                        "var",
                        0
                      ],
                      [
                        "var",
                        1
                      ]
                    ],
                    [
                      "unary",
                      "affordable_proof",
                      [
                        "var",
                        0
                      ]
                    ]
                  ]
                ]
              ]
            ],
            [
              "unary",
              "unresolved",
              [
                "var",
                0
              ]
            ]
          ]
        ]
      },
      "meaning_id": "06589d19d138f0f1cb711d2a837d6815669a4702dafb105f377efa13d058f4bb"
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
        "new_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "implies",
          [
            "unary",
            "adopted",
            [
              "const",
              "vex"
            ]
          ],
          [
            "and",
            [
              "exists",
              "evidence",
              [
                "binary",
                "required_by",
                [
                  "var",
                  0
                ],
                [
                  "const",
                  "vex"
                ]
              ]
            ],
            [
              "forall",
              "evidence",
              [
                "implies",
                [
                  "binary",
                  "required_by",
                  [
                    "var",
                    0
                  ],
                  [
                    "const",
                    "vex"
                  ]
                ],
                [
                  "unary",
                  "needs_quality_review",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "7dca1515df049cee76a68bdf30a61abb26c0ddbf5641f8bcf996e9712d525228"
    },
    {
      "id": "u040",
      "span": [
        3030,
        3119
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "new_text",
        "says",
        "asserted"
      ],
      "meaning": {
        "open": [
          "misleading_formalisation"
        ]
      },
      "support": "none"
    },
    {
      "id": "u041",
      "span": [
        3119,
        3149
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "new_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "forall",
          "artefact",
          [
            "implies",
            [
              "and",
              [
                "unary",
                "real_artefact",
                [
                  "var",
                  0
                ]
              ],
              [
                "binary",
                "included_in",
                [
                  "var",
                  0
                ],
                [
                  "const",
                  "benchmark"
                ]
              ]
            ],
            [
              "unary",
              "tests_transfer",
              [
                "var",
                0
              ]
            ]
          ]
        ]
      },
      "meaning_id": "642f9361b739d292d337b122f0172c52ba8a7ecdc51272243b201c27db734663"
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
        "new_text",
        "says",
        [
          "attributed",
          "applicant",
          "promised",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "forall",
            "item",
            [
              "implies",
              [
                "or",
                [
                  "unary",
                  "null_result",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "unary",
                  "negative_result",
                  [
                    "var",
                    0
                  ]
                ]
              ],
              [
                "unary",
                "published",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          [
            "and",
            [
              "unary",
              "published",
              [
                "const",
                "benchmark"
              ]
            ],
            [
              "and",
              [
                "unary",
                "published",
                [
                  "const",
                  "harness"
                ]
              ],
              [
                "unary",
                "published",
                [
                  "const",
                  "failure_analysis"
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "74d35899c431b933a702d551c36208d98043e6a7bd3205c22ccf9e05cdfe99f8"
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
            "binary",
            "copied_from",
            [
              "const",
              "old_text"
            ],
            [
              "const",
              "form_edits_file"
            ]
          ],
          [
            "and",
            [
              "unary",
              "current_form_text",
              [
                "const",
                "form_edits_file"
              ]
            ],
            [
              "unary",
              "supplies_context",
              [
                "const",
                "rapid_draft"
              ]
            ]
          ]
        ]
      },
      "meaning_id": "563c60cd8e00c58dffcceda69032062983abd8f3aabebc07c367fa228affa7f5"
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
          "not",
          [
            "binary",
            "used_as",
            [
              "const",
              "superseded_wording"
            ],
            [
              "const",
              "old_text"
            ]
          ]
        ]
      },
      "meaning_id": "8e411a7a665e00e075ab96f44d34f159b6be1c1887e3d3819e1a792efe79c5c1"
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
            "binary",
            "follows",
            [
              "const",
              "correction"
            ],
            [
              "const",
              "recheck_section"
            ]
          ],
          [
            "and",
            [
              "binary",
              "follows",
              [
                "const",
                "correction"
              ],
              [
                "const",
                "positioning_section"
              ]
            ],
            [
              "binary",
              "follows",
              [
                "const",
                "correction"
              ],
              [
                "const",
                "positioning_correction"
              ]
            ]
          ]
        ]
      },
      "meaning_id": "925502592f3b5761980d8933d56de245a4a7e913ed182bfc8002346cd3c70fa5"
    },
    {
      "id": "u047",
      "span": [
        3676,
        3768
      ],
      "status": "UNFORMALISED",
      "kind": [
        "unformalised",
        "causal_route_excludes_definitions"
      ],
      "meaning": {
        "unformalised": "causal_route_excludes_definitions"
      },
      "support": "none"
    },
    {
      "id": "u048",
      "span": [
        3768,
        3826
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "binary",
          "conditional_on",
          [
            "const",
            "guarantee"
          ],
          [
            "const",
            "declared_foundations"
          ]
        ]
      },
      "meaning_id": "3dbe72072958b242002078dcba4f2a9f761373dc0781594270dad027a80b645b"
    },
    {
      "id": "u049",
      "span": [
        3826,
        3887
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "not",
            [
              "binary",
              "establishes_truth_of",
              [
                "const",
                "guarantee"
              ],
              [
                "const",
                "declared_foundations"
              ]
            ]
          ],
          [
            "not",
            [
              "binary",
              "establishes_fidelity_of",
              [
                "const",
                "guarantee"
              ],
              [
                "const",
                "declared_foundations"
              ]
            ]
          ]
        ]
      },
      "meaning_id": "32e8e97593393f15e0b7ff6db58f7d97490f6d4d2979b561c45472dac0db4d0b"
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
          "forall",
          "claim",
          [
            "implies",
            [
              "and",
              [
                "unary",
                "honest",
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "unary",
                  "unresolved",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ],
            [
              "exists",
              "proof",
              [
                "and",
                [
                  "binary",
                  "proof_of",
                  [
                    "var",
                    0
                  ],
                  [
                    "var",
                    1
                  ]
                ],
                [
                  "unary",
                  "affordable_proof",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "ca34424d51143725115d7c8669c75c886d76d171016c6e9109c8cc3721819e87"
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
          "forall",
          "claim",
          [
            "implies",
            [
              "and",
              [
                "exists",
                "proof",
                [
                  "binary",
                  "proof_of",
                  [
                    "var",
                    0
                  ],
                  [
                    "var",
                    1
                  ]
                ]
              ],
              [
                "forall",
                "proof",
                [
                  "implies",
                  [
                    "binary",
                    "proof_of",
                    [
                      "var",
                      0
                    ],
                    [
                      "var",
                      1
                    ]
                  ],
                  [
                    "not",
                    [
                      "unary",
                      "within_budget",
                      [
                        "var",
                        0
                      ]
                    ]
                  ]
                ]
              ]
            ],
            [
              "unary",
              "unresolved",
              [
                "var",
                0
              ]
            ]
          ]
        ]
      },
      "meaning_id": "8ac2ae834da731a19e66de7a4a3ad3810ec2363d8abc8d177a3727e631ea041a"
    },
    {
      "id": "u052",
      "span": [
        3986,
        4043
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "binary",
          "benefit_of",
          [
            "const",
            "prevention"
          ],
          [
            "const",
            "sound_proof_checking"
          ]
        ]
      },
      "meaning_id": "23d0b95337602e844904cf78d02c58114f2ba21fee5168593bee391eb74b1cfb"
    },
    {
      "id": "u053",
      "span": [
        4043,
        4121
      ],
      "status": "UNFORMALISED",
      "kind": [
        "unformalised",
        "vague_evaluation"
      ],
      "meaning": {
        "unformalised": "vague_evaluation"
      },
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
            "not",
            [
              "binary",
              "claims",
              [
                "const",
                "draft"
              ],
              [
                "const",
                "debate_novelty"
              ]
            ]
          ],
          [
            "not",
            [
              "binary",
              "claims",
              [
                "const",
                "draft"
              ],
              [
                "const",
                "english_surface_benefit"
              ]
            ]
          ]
        ]
      },
      "meaning_id": "eb62309fe921d12cd7fd9eacea0a485ce31dfaf213ed15acfcde2733e5ca99fd"
    },
    {
      "id": "u055",
      "span": [
        4204,
        4284
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "binary",
            "concerns",
            [
              "const",
              "stability_caveat"
            ],
            [
              "const",
              "estimated_leaves"
            ]
          ],
          [
            "not",
            [
              "binary",
              "concerns",
              [
                "const",
                "stability_caveat"
              ],
              [
                "const",
                "proved_subclaims"
              ]
            ]
          ]
        ]
      },
      "meaning_id": "0d5c58ebc8c3e7e9633e864b52a87ed9308eaa962fda26e1df0dc97fe1be5f12"
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
        "new_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "unary",
            "proposed",
            [
              "const",
              "vex"
            ]
          ],
          [
            "and",
            [
              "unary",
              "is_evidence",
              [
                "const",
                "vex"
              ]
            ],
            [
              "implies",
              [
                "unary",
                "adopted",
                [
                  "const",
                  "vex"
                ]
              ],
              [
                "and",
                [
                  "binary",
                  "mandatory_for",
                  [
                    "const",
                    "vex"
                  ],
                  [
                    "const",
                    "statistical_claims"
                  ]
                ],
                [
                  "binary",
                  "mandatory_for",
                  [
                    "const",
                    "vex"
                  ],
                  [
                    "const",
                    "approximate_claims"
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "852446402ab0be71d42dad7e0c1505197a3697de32f08c5ac06a9b6e01a4674c"
    },
    {
      "id": "u057",
      "span": [
        4375,
        4432
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "not",
          [
            "binary",
            "guarantees",
            [
              "const",
              "evidence_requirements"
            ],
            [
              "const",
              "evidence_quality"
            ]
          ]
        ]
      },
      "meaning_id": "16cc54122728895e1203f3fca71c76a82ae4c3e44d3107e4b37e39a4fbd3c75c"
    },
    {
      "id": "u058",
      "span": [
        4432,
        4485
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "not",
            [
              "binary",
              "claims",
              [
                "const",
                "draft"
              ],
              [
                "const",
                "vex_result"
              ]
            ]
          ],
          [
            "not",
            [
              "binary",
              "claims",
              [
                "const",
                "draft"
              ],
              [
                "const",
                "completed_extension"
              ]
            ]
          ]
        ]
      },
      "meaning_id": "c4a3257600b098f8c02ee113d35b966eb0699188e7a500f628b8ea55d81ee0a5"
    },
    {
      "id": "u059",
      "span": [
        4485,
        4557
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "binary",
          "schedules",
          [
            "const",
            "evidence_layer_milestones"
          ],
          [
            "const",
            "vex"
          ]
        ]
      },
      "meaning_id": "b39f52d9d50fa0a4c80661745585d3d444259649d3a1e014ebf7ce1d07f82fbc"
    },
    {
      "id": "u060",
      "span": [
        4557,
        4744
      ],
      "status": "UNFORMALISED",
      "kind": [
        "unformalised",
        "motivation_link"
      ],
      "meaning": {
        "unformalised": "motivation_link"
      },
      "support": "none"
    },
    {
      "id": "u061",
      "span": [
        4744,
        4835
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "not",
            [
              "binary",
              "reports",
              [
                "const",
                "revised_form_text"
              ],
              [
                "const",
                "new_results"
              ]
            ]
          ],
          [
            "not",
            [
              "binary",
              "asserts",
              [
                "const",
                "revised_form_text"
              ],
              [
                "const",
                "cost_advantage"
              ]
            ]
          ]
        ]
      },
      "meaning_id": "5d1091690b7442abd76a3ccda6f224df766693afc4d6f3a4b1b5dda251c3e85d"
    },
    {
      "id": "u062",
      "span": [
        4835,
        4915
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
            "matched_cost",
            [
              "const",
              "revised_comparison"
            ]
          ],
          [
            "and",
            [
              "binary",
              "counts_cost",
              [
                "const",
                "revised_comparison"
              ],
              [
                "const",
                "formalisation_work"
              ]
            ],
            [
              "binary",
              "counts_cost",
              [
                "const",
                "revised_comparison"
              ],
              [
                "const",
                "proof_production"
              ]
            ]
          ]
        ]
      },
      "meaning_id": "a6a666917f8a10b82f72b2e8e8a06134f8acc23123c90f4734d0168e5f5abee4"
    },
    {
      "id": "u063",
      "span": [
        4915,
        5091
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "author",
        "says",
        "asserted"
      ],
      "meaning": {
        "open": [
          "real_artefact"
        ]
      },
      "support": "none"
    },
    {
      "id": "u064",
      "span": [
        5091,
        5247
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "author",
        "says",
        "asserted"
      ],
      "meaning": {
        "open": [
          "misleading_formalisation"
        ]
      },
      "support": "none"
    },
    {
      "id": "u065",
      "span": [
        5247,
        5284
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "forall",
          "field",
          [
            "not",
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
      },
      "meaning_id": "cb45f49dbcd75d33fb599296a751f8cbc2f49feb4237a3a22a28c3613bcd6d18"
    },
    {
      "id": "u066",
      "span": [
        5284,
        5377
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "and",
          [
            "binary",
            "includes",
            [
              "const",
              "character_counts"
            ],
            [
              "const",
              "spaces"
            ]
          ],
          [
            "and",
            [
              "binary",
              "includes",
              [
                "const",
                "character_counts"
              ],
              [
                "const",
                "punctuation"
              ]
            ],
            [
              "and",
              [
                "not",
                [
                  "binary",
                  "includes",
                  [
                    "const",
                    "character_counts"
                  ],
                  [
                    "const",
                    "labels"
                  ]
                ]
              ],
              [
                "not",
                [
                  "binary",
                  "includes",
                  [
                    "const",
                    "character_counts"
                  ],
                  [
                    "const",
                    "trailing_newlines"
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "3cc38ac6780382f8ff55c400de100ead614fff612c94aa147410265923ca6f1f"
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
            "exists",
            "candidate",
            [
              "unary",
              "pasted",
              [
                "var",
                0
              ]
            ]
          ],
          [
            "and",
            [
              "forall",
              "candidate",
              [
                "forall",
                "candidate",
                [
                  "implies",
                  [
                    "and",
                    [
                      "unary",
                      "pasted",
                      [
                        "var",
                        0
                      ]
                    ],
                    [
                      "unary",
                      "pasted",
                      [
                        "var",
                        1
                      ]
                    ]
                  ],
                  [
                    "eq",
                    [
                      "var",
                      0
                    ],
                    [
                      "var",
                      1
                    ]
                  ]
                ]
              ]
            ],
            [
              "forall",
              "candidate",
              [
                "implies",
                [
                  "unary",
                  "pasted",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "and",
                  [
                    "not",
                    [
                      "binary",
                      "pasted_with",
                      [
                        "var",
                        0
                      ],
                      [
                        "const",
                        "its_label"
                      ]
                    ]
                  ],
                  [
                    "not",
                    [
                      "binary",
                      "pasted_with",
                      [
                        "var",
                        0
                      ],
                      [
                        "const",
                        "its_count"
                      ]
                    ]
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "6d64e69fc0e8533faab035befdff2e741797d08489e9be1cadde6e5bfec85d8f"
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
            "binary",
            "replaces",
            [
              "const",
              "contribution_edit"
            ],
            [
              "const",
              "indicated_sentence"
            ]
          ],
          [
            "and",
            [
              "binary",
              "replaces",
              [
                "const",
                "harms_edit"
              ],
              [
                "const",
                "indicated_paragraph"
              ]
            ],
            [
              "and",
              [
                "forall",
                "item",
                [
                  "implies",
                  [
                    "binary",
                    "replaces",
                    [
                      "const",
                      "contribution_edit"
                    ],
                    [
                      "var",
                      0
                    ]
                  ],
                  [
                    "eq",
                    [
                      "var",
                      0
                    ],
                    [
                      "const",
                      "indicated_sentence"
                    ]
                  ]
                ]
              ],
              [
                "forall",
                "item",
                [
                  "implies",
                  [
                    "binary",
                    "replaces",
                    [
                      "const",
                      "harms_edit"
                    ],
                    [
                      "var",
                      0
                    ]
                  ],
                  [
                    "eq",
                    [
                      "var",
                      0
                    ],
                    [
                      "const",
                      "indicated_paragraph"
                    ]
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "79f461dd888be7952d2b2852e8bbe2789dd41cba47bfe322b9a2a382ea8be5df"
    },
    {
      "id": "u069",
      "span": [
        5528,
        5585
      ],
      "status": "UNFORMALISED",
      "kind": [
        "unformalised",
        "vague_comparison"
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
            "binary",
            "states",
            [
              "const",
              "extra_space"
            ],
            [
              "const",
              "proof_rule"
            ]
          ],
          [
            "binary",
            "states",
            [
              "const",
              "extra_space"
            ],
            [
              "const",
              "proof_rule_limits"
            ]
          ]
        ]
      },
      "meaning_id": "891bb11a5ffacbee9bb203d9204e2443fb146608583648ca7cf7c2d3befa4f42"
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
        "candidate_1",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "binary",
            "tested_on",
            [
              "const",
              "mandatory_checked_proofs"
            ],
            [
              "const",
              "obfuscated_arguments"
            ]
          ],
          [
            "and",
            [
              "unary",
              "proposed",
              [
                "const",
                "vex"
              ]
            ],
            [
              "and",
              [
                "unary",
                "is_evidence",
                [
                  "const",
                  "vex"
                ]
              ],
              [
                "implies",
                [
                  "unary",
                  "adopted",
                  [
                    "const",
                    "vex"
                  ]
                ],
                [
                  "and",
                  [
                    "binary",
                    "mandatory_for",
                    [
                      "const",
                      "vex"
                    ],
                    [
                      "const",
                      "statistical_claims"
                    ]
                  ],
                  [
                    "binary",
                    "mandatory_for",
                    [
                      "const",
                      "vex"
                    ],
                    [
                      "const",
                      "approximate_claims"
                    ]
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "6bff4ef20b9f9759c63cf66b03df599a4f69b04cc38d56deac56eac97e528950"
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
        "candidate_2",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "binary",
            "tested_to_improve",
            [
              "const",
              "mandatory_checked_proofs"
            ],
            [
              "const",
              "oversight"
            ]
          ],
          [
            "and",
            [
              "binary",
              "applies_to",
              [
                "const",
                "mandatory_checked_proofs"
              ],
              [
                "const",
                "formalisable_claims"
              ]
            ],
            [
              "and",
              [
                "binary",
                "developed_to_improve",
                [
                  "const",
                  "vex"
                ],
                [
                  "const",
                  "oversight"
                ]
              ],
              [
                "and",
                [
                  "unary",
                  "is_evidence",
                  [
                    "const",
                    "vex"
                  ]
                ],
                [
                  "implies",
                  [
                    "unary",
                    "adopted",
                    [
                      "const",
                      "vex"
                    ]
                  ],
                  [
                    "and",
                    [
                      "binary",
                      "mandatory_for",
                      [
                        "const",
                        "vex"
                      ],
                      [
                        "const",
                        "statistical_claims"
                      ]
                    ],
                    [
                      "binary",
                      "mandatory_for",
                      [
                        "const",
                        "vex"
                      ],
                      [
                        "const",
                        "approximate_claims"
                      ]
                    ]
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "19ebb1e81053364c0221dff065b6b816dcdde2cb008ec4f3ed82f092744ca3f3"
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
      "status": "OPEN",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": {
        "open": [
          "misleading_formalisation"
        ]
      },
      "support": "none"
    },
    {
      "id": "u079",
      "span": [
        6390,
        6484
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": {
        "open": [
          "matched_cost"
        ]
      },
      "support": "none"
    },
    {
      "id": "u080",
      "span": [
        6484,
        6585
      ],
      "status": "LABELLED",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u081",
      "span": [
        6585,
        6657
      ],
      "status": "LABELLED",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u082",
      "span": [
        6657,
        6720
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        [
          "attributed",
          "applicant",
          "intends",
          "asserted"
        ]
      ],
      "meaning": {
        "open": [
          "real_artefact"
        ]
      },
      "support": "none"
    },
    {
      "id": "u083",
      "span": [
        6720,
        6783
      ],
      "status": "OPEN",
      "kind": "question",
      "meaning": {
        "open": [
          "catastrophic_risk"
        ]
      },
      "support": "none"
    },
    {
      "id": "u084",
      "span": [
        6783,
        7045
      ],
      "status": "UNFORMALISED",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        [
          "unformalised",
          "causal_means"
        ]
      ],
      "meaning": {
        "unformalised": "causal_means"
      },
      "support": "none"
    },
    {
      "id": "u085",
      "span": [
        7045,
        7102
      ],
      "status": "OPEN",
      "kind": "question",
      "meaning": {
        "open": [
          "catastrophic_risk"
        ]
      },
      "support": "none"
    },
    {
      "id": "u086",
      "span": [
        7102,
        7149
      ],
      "status": "UNFORMALISED",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        [
          "hedged",
          "could",
          [
            "unformalised",
            "causal_route_excludes_definitions"
          ]
        ]
      ],
      "meaning": {
        "unformalised": "causal_route_excludes_definitions"
      },
      "support": "none"
    },
    {
      "id": "u087",
      "span": [
        7149,
        7198
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
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
      },
      "meaning_id": "2791f77e0646ce20fd420318a65c06a48049d58d7702353b26fd84f2d184ac75"
    },
    {
      "id": "u088",
      "span": [
        7198,
        7239
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        [
          "hedged",
          "could",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "exists",
          "formalisation",
          [
            "unary",
            "misstates_task",
            [
              "var",
              0
            ]
          ]
        ]
      },
      "meaning_id": "fa0c0c6ef4c8436c0d2ac9e54fd0724d77b84895d1f292e4df00118e3fd96fb5"
    },
    {
      "id": "u089",
      "span": [
        7239,
        7310
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "forall",
          "claim",
          [
            "implies",
            [
              "and",
              [
                "unary",
                "honest",
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "exists",
                  "proof",
                  [
                    "and",
                    [
                      "binary",
                      "proof_of",
                      [
                        "var",
                        0
                      ],
                      [
                        "var",
                        1
                      ]
                    ],
                    [
                      "unary",
                      "affordable_proof",
                      [
                        "var",
                        0
                      ]
                    ]
                  ]
                ]
              ]
            ],
            [
              "unary",
              "unresolved",
              [
                "var",
                0
              ]
            ]
          ]
        ]
      },
      "meaning_id": "06589d19d138f0f1cb711d2a837d6815669a4702dafb105f377efa13d058f4bb"
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
        "paste_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "implies",
          [
            "unary",
            "adopted",
            [
              "const",
              "vex"
            ]
          ],
          [
            "and",
            [
              "exists",
              "evidence",
              [
                "binary",
                "required_by",
                [
                  "var",
                  0
                ],
                [
                  "const",
                  "vex"
                ]
              ]
            ],
            [
              "forall",
              "evidence",
              [
                "implies",
                [
                  "binary",
                  "required_by",
                  [
                    "var",
                    0
                  ],
                  [
                    "const",
                    "vex"
                  ]
                ],
                [
                  "unary",
                  "needs_quality_review",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "7dca1515df049cee76a68bdf30a61abb26c0ddbf5641f8bcf996e9712d525228"
    },
    {
      "id": "u091",
      "span": [
        7371,
        7460
      ],
      "status": "OPEN",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        "asserted"
      ],
      "meaning": {
        "open": [
          "misleading_formalisation"
        ]
      },
      "support": "none"
    },
    {
      "id": "u092",
      "span": [
        7460,
        7490
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "paste_text",
        "says",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "forall",
          "artefact",
          [
            "implies",
            [
              "and",
              [
                "unary",
                "real_artefact",
                [
                  "var",
                  0
                ]
              ],
              [
                "binary",
                "included_in",
                [
                  "var",
                  0
                ],
                [
                  "const",
                  "benchmark"
                ]
              ]
            ],
            [
              "unary",
              "tests_transfer",
              [
                "var",
                0
              ]
            ]
          ]
        ]
      },
      "meaning_id": "642f9361b739d292d337b122f0172c52ba8a7ecdc51272243b201c27db734663"
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
        "paste_text",
        "says",
        [
          "attributed",
          "applicant",
          "promised",
          "asserted"
        ]
      ],
      "meaning": "specified",
      "support": "none",
      "content": {
        "ast": [
          "and",
          [
            "forall",
            "item",
            [
              "implies",
              [
                "or",
                [
                  "unary",
                  "null_result",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "unary",
                  "negative_result",
                  [
                    "var",
                    0
                  ]
                ]
              ],
              [
                "unary",
                "published",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          [
            "and",
            [
              "unary",
              "published",
              [
                "const",
                "benchmark"
              ]
            ],
            [
              "and",
              [
                "unary",
                "published",
                [
                  "const",
                  "harness"
                ]
              ],
              [
                "unary",
                "published",
                [
                  "const",
                  "failure_analysis"
                ]
              ]
            ]
          ]
        ]
      },
      "meaning_id": "74d35899c431b933a702d551c36208d98043e6a7bd3205c22ccf9e05cdfe99f8"
    }
  ],
  "open_terms": [
    {
      "name": "matched_cost",
      "arguments": [
        "comparison"
      ],
      "decided_by": "grant-author",
      "necessary": [],
      "sufficient": [],
      "factors": [
        "OLD wording written before the author's rule, or a milestone plan item recorded only as a plan; applying the definition would add content the span does not state."
      ],
      "precedents": [],
      "jurisdiction": "this-draft",
      "version": 1
    },
    {
      "name": "real_artefact",
      "arguments": [
        "artefact"
      ],
      "decided_by": "grant-author",
      "necessary": [],
      "sufficient": [],
      "factors": [
        "OLD wording, a milestone plan item, or a list of retained items; the span does not say which artefacts the defined predicate classifies."
      ],
      "precedents": [],
      "jurisdiction": "this-draft",
      "version": 1
    },
    {
      "name": "misleading_formalisation",
      "arguments": [
        "formalisation"
      ],
      "decided_by": "grant-author",
      "necessary": [],
      "sufficient": [],
      "factors": [
        "Used as an error class or as the name of a control; the span does not say how the control or class relates to the defined predicate on formalisations."
      ],
      "precedents": [],
      "jurisdiction": "this-draft",
      "version": 1
    },
    {
      "name": "catastrophic_risk",
      "arguments": [
        "pathway"
      ],
      "decided_by": "bluedot",
      "necessary": [],
      "sufficient": [],
      "factors": [
        "The funder's form heading. BlueDot, not the grant author, decides the sense of its question, and the draft gives no reduction estimate."
      ],
      "precedents": [],
      "jurisdiction": "this-draft",
      "version": 1
    }
  ],
  "reading_sets": [
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
          "meaning_id": "563c60cd8e00c58dffcceda69032062983abd8f3aabebc07c367fa228affa7f5",
          "content": [
            "and",
            [
              "binary",
              "copied_from",
              [
                "const",
                "old_text"
              ],
              [
                "const",
                "form_edits_file"
              ]
            ],
            [
              "and",
              [
                "unary",
                "current_form_text",
                [
                  "const",
                  "form_edits_file"
                ]
              ],
              [
                "unary",
                "supplies_context",
                [
                  "const",
                  "rapid_draft"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Provenance of the OLD wording and of the context.",
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
          "meaning_id": "8e411a7a665e00e075ab96f44d34f159b6be1c1887e3d3819e1a792efe79c5c1",
          "content": [
            "not",
            [
              "binary",
              "used_as",
              [
                "const",
                "superseded_wording"
              ],
              [
                "const",
                "old_text"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "'its' is bluedot-rapid-draft-v3.md. Resolution: 'its' -> bluedot-rapid-draft-v3.md.",
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
          "meaning_id": "925502592f3b5761980d8933d56de245a4a7e913ed182bfc8002346cd3c70fa5",
          "content": [
            "and",
            [
              "binary",
              "follows",
              [
                "const",
                "correction"
              ],
              [
                "const",
                "recheck_section"
              ]
            ],
            [
              "and",
              [
                "binary",
                "follows",
                [
                  "const",
                  "correction"
                ],
                [
                  "const",
                  "positioning_section"
                ]
              ],
              [
                "binary",
                "follows",
                [
                  "const",
                  "correction"
                ],
                [
                  "const",
                  "positioning_correction"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "The three cited sources of the correction.",
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
          "meaning_id": "3dbe72072958b242002078dcba4f2a9f761373dc0781594270dad027a80b645b",
          "content": [
            "binary",
            "conditional_on",
            [
              "const",
              "guarantee"
            ],
            [
              "const",
              "declared_foundations"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "'the guarantee' is the guarantee of mandatory proof. Resolution: 'the guarantee' -> the guarantee of mandatory proof.",
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
          "meaning_id": "32e8e97593393f15e0b7ff6db58f7d97490f6d4d2979b561c45472dac0db4d0b",
          "content": [
            "and",
            [
              "not",
              [
                "binary",
                "establishes_truth_of",
                [
                  "const",
                  "guarantee"
                ],
                [
                  "const",
                  "declared_foundations"
                ]
              ]
            ],
            [
              "not",
              [
                "binary",
                "establishes_fidelity_of",
                [
                  "const",
                  "guarantee"
                ],
                [
                  "const",
                  "declared_foundations"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "'It' is the guarantee, the subject of the preceding clause; 'their' is the declared foundations. Resolution: 'It' -> the guarantee of mandatory proof, the subject of the preceding clause; 'their' -> the declared foundations.",
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
          "meaning_id": "ca34424d51143725115d7c8669c75c886d76d171016c6e9109c8cc3721819e87",
          "content": [
            "forall",
            "claim",
            [
              "implies",
              [
                "and",
                [
                  "unary",
                  "honest",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "not",
                  [
                    "unary",
                    "unresolved",
                    [
                      "var",
                      0
                    ]
                  ]
                ]
              ],
              [
                "exists",
                "proof",
                [
                  "and",
                  [
                    "binary",
                    "proof_of",
                    [
                      "var",
                      0
                    ],
                    [
                      "var",
                      1
                    ]
                  ],
                  [
                    "unary",
                    "affordable_proof",
                    [
                      "var",
                      0
                    ]
                  ]
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "'needs' is read as needed to leave the 'unresolved' status; uses the defined affordable_proof predicate. Resolution: 'needs' -> needed for the claim not to remain unresolved.",
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
          "meaning_id": "8ac2ae834da731a19e66de7a4a3ad3810ec2363d8abc8d177a3727e631ea041a",
          "content": [
            "forall",
            "claim",
            [
              "implies",
              [
                "and",
                [
                  "exists",
                  "proof",
                  [
                    "binary",
                    "proof_of",
                    [
                      "var",
                      0
                    ],
                    [
                      "var",
                      1
                    ]
                  ]
                ],
                [
                  "forall",
                  "proof",
                  [
                    "implies",
                    [
                      "binary",
                      "proof_of",
                      [
                        "var",
                        0
                      ],
                      [
                        "var",
                        1
                      ]
                    ],
                    [
                      "not",
                      [
                        "unary",
                        "within_budget",
                        [
                          "var",
                          0
                        ]
                      ]
                    ]
                  ]
                ]
              ],
              [
                "unary",
                "unresolved",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "'beyond budget' is the negation of affordable_proof's within_budget clause; 'the claim' is the claim those proofs prove. Resolution: 'the claim' -> the claim the over-budget proofs are proofs of; 'beyond budget' -> total cost not within the registered budget (the within_budget clause of affordable_proof).",
            "distinguishing_models": {}
          }
        }
      ]
    },
    {
      "id": "reading-u052",
      "unit": "u052",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "23d0b95337602e844904cf78d02c58114f2ba21fee5168593bee391eb74b1cfb",
          "content": [
            "binary",
            "benefit_of",
            [
              "const",
              "prevention"
            ],
            [
              "const",
              "sound_proof_checking"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "'This' is note 2's protection against arbitrary false sub-claims. Resolution: 'This' -> note 2's protection: mandatory proof preventing arbitrary false sub-claims from being accepted as new assumptions.",
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
          "meaning_id": "eb62309fe921d12cd7fd9eacea0a485ce31dfaf213ed15acfcde2733e5ca99fd",
          "content": [
            "and",
            [
              "not",
              [
                "binary",
                "claims",
                [
                  "const",
                  "draft"
                ],
                [
                  "const",
                  "debate_novelty"
                ]
              ]
            ],
            [
              "not",
              [
                "binary",
                "claims",
                [
                  "const",
                  "draft"
                ],
                [
                  "const",
                  "english_surface_benefit"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Nothing is claimed; the draft does not claim that there is no novelty. Resolution: 'is claimed' -> claimed by this draft.",
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
          "meaning_id": "0d5c58ebc8c3e7e9633e864b52a87ed9308eaa962fda26e1df0dc97fe1be5f12",
          "content": [
            "and",
            [
              "binary",
              "concerns",
              [
                "const",
                "stability_caveat"
              ],
              [
                "const",
                "estimated_leaves"
              ]
            ],
            [
              "not",
              [
                "binary",
                "concerns",
                [
                  "const",
                  "stability_caveat"
                ],
                [
                  "const",
                  "proved_subclaims"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "The caveat's scope.",
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
          "meaning_id": "16cc54122728895e1203f3fca71c76a82ae4c3e44d3107e4b37e39a4fbd3c75c",
          "content": [
            "not",
            [
              "binary",
              "guarantees",
              [
                "const",
                "evidence_requirements"
              ],
              [
                "const",
                "evidence_quality"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "A negated relation.",
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
          "meaning_id": "c4a3257600b098f8c02ee113d35b966eb0699188e7a500f628b8ea55d81ee0a5",
          "content": [
            "and",
            [
              "not",
              [
                "binary",
                "claims",
                [
                  "const",
                  "draft"
                ],
                [
                  "const",
                  "vex_result"
                ]
              ]
            ],
            [
              "not",
              [
                "binary",
                "claims",
                [
                  "const",
                  "draft"
                ],
                [
                  "const",
                  "completed_extension"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Nothing is claimed. Resolution: 'is claimed' -> claimed by this draft.",
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
          "meaning_id": "b39f52d9d50fa0a4c80661745585d3d444259649d3a1e014ebf7ce1d07f82fbc",
          "content": [
            "binary",
            "schedules",
            [
              "const",
              "evidence_layer_milestones"
            ],
            [
              "const",
              "vex"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "'its' is VEX. Resolution: 'its' -> VEX.",
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
          "meaning_id": "5d1091690b7442abd76a3ccda6f224df766693afc4d6f3a4b1b5dda251c3e85d",
          "content": [
            "and",
            [
              "not",
              [
                "binary",
                "reports",
                [
                  "const",
                  "revised_form_text"
                ],
                [
                  "const",
                  "new_results"
                ]
              ]
            ],
            [
              "not",
              [
                "binary",
                "asserts",
                [
                  "const",
                  "revised_form_text"
                ],
                [
                  "const",
                  "cost_advantage"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Two negated relations.",
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
          "meaning_id": "a6a666917f8a10b82f72b2e8e8a06134f8acc23123c90f4734d0168e5f5abee4",
          "content": [
            "and",
            [
              "unary",
              "matched_cost",
              [
                "const",
                "revised_comparison"
              ]
            ],
            [
              "and",
              [
                "binary",
                "counts_cost",
                [
                  "const",
                  "revised_comparison"
                ],
                [
                  "const",
                  "formalisation_work"
                ]
              ],
              [
                "binary",
                "counts_cost",
                [
                  "const",
                  "revised_comparison"
                ],
                [
                  "const",
                  "proof_production"
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "A present-tense report by the author, so asserted; 'the matched-cost comparison' uses the defined matched_cost predicate. Resolution: 'the matched-cost comparison' -> the comparison in the revised form text.",
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
          "meaning_id": "cb45f49dbcd75d33fb599296a751f8cbc2f49feb4237a3a22a28c3613bcd6d18",
          "content": [
            "forall",
            "field",
            [
              "not",
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
            "why": "The budget is one field.",
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
          "meaning_id": "3cc38ac6780382f8ff55c400de100ead614fff612c94aa147410265923ca6f1f",
          "content": [
            "and",
            [
              "binary",
              "includes",
              [
                "const",
                "character_counts"
              ],
              [
                "const",
                "spaces"
              ]
            ],
            [
              "and",
              [
                "binary",
                "includes",
                [
                  "const",
                  "character_counts"
                ],
                [
                  "const",
                  "punctuation"
                ]
              ],
              [
                "and",
                [
                  "not",
                  [
                    "binary",
                    "includes",
                    [
                      "const",
                      "character_counts"
                    ],
                    [
                      "const",
                      "labels"
                    ]
                  ]
                ],
                [
                  "not",
                  [
                    "binary",
                    "includes",
                    [
                      "const",
                      "character_counts"
                    ],
                    [
                      "const",
                      "trailing_newlines"
                    ]
                  ]
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "What the stated counts include.",
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
          "meaning_id": "79f461dd888be7952d2b2852e8bbe2789dd41cba47bfe322b9a2a382ea8be5df",
          "content": [
            "and",
            [
              "binary",
              "replaces",
              [
                "const",
                "contribution_edit"
              ],
              [
                "const",
                "indicated_sentence"
              ]
            ],
            [
              "and",
              [
                "binary",
                "replaces",
                [
                  "const",
                  "harms_edit"
                ],
                [
                  "const",
                  "indicated_paragraph"
                ]
              ],
              [
                "and",
                [
                  "forall",
                  "item",
                  [
                    "implies",
                    [
                      "binary",
                      "replaces",
                      [
                        "const",
                        "contribution_edit"
                      ],
                      [
                        "var",
                        0
                      ]
                    ],
                    [
                      "eq",
                      [
                        "var",
                        0
                      ],
                      [
                        "const",
                        "indicated_sentence"
                      ]
                    ]
                  ]
                ],
                [
                  "forall",
                  "item",
                  [
                    "implies",
                    [
                      "binary",
                      "replaces",
                      [
                        "const",
                        "harms_edit"
                      ],
                      [
                        "var",
                        0
                      ]
                    ],
                    [
                      "eq",
                      [
                        "var",
                        0
                      ],
                      [
                        "const",
                        "indicated_paragraph"
                      ]
                    ]
                  ]
                ]
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "Respectively: the contribution edit replaces only the sentence, and the harms edit only the paragraph. Resolution: 'sentence and paragraph' -> respectively, the contribution sentence and the harms paragraph.",
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
          "meaning_id": "891bb11a5ffacbee9bb203d9204e2443fb146608583648ca7cf7c2d3befa4f42",
          "content": [
            "and",
            [
              "binary",
              "states",
              [
                "const",
                "extra_space"
              ],
              [
                "const",
                "proof_rule"
              ]
            ],
            [
              "binary",
              "states",
              [
                "const",
                "extra_space"
              ],
              [
                "const",
                "proof_rule_limits"
              ]
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "'its' is the proof rule; 'the extra space' is in the revised passages. Resolution: 'its' -> the proof rule; 'the extra space' -> in the revised passages.",
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
