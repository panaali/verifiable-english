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
          "description": "mandatory checked proofs; \"The contribution here is an implementation and tests of mandatory proof: accepting only what the verified checker derives from declared, reviewed foundations blocks the Barnes-Christiano construction for formalised claims by excluding assumed false sub-claims.\""
        },
        "obfuscated_arguments": {
          "sort": "item",
          "description": "obfuscated arguments"
        },
        "vex": {
          "sort": "item",
          "description": "VEX; \"VEX is presented as proposed mandatory evidence for statistical and approximate claims.\""
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
          "description": "OLD; \"OLD text is copied from FORM-EDITS-2026-09-21.md, the current form text.\""
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
          "description": "section 3 of <ops-repo>/reviews/obfuscation-recheck.md"
        },
        "positioning_section": {
          "sort": "item",
          "description": "section 4 of <repo>/design/positioning-vs-debate-theory.md"
        },
        "positioning_correction": {
          "sort": "item",
          "description": "Correction 2 of <repo>/design/positioning-vs-debate-theory.md"
        },
        "guarantee": {
          "sort": "item",
          "description": "the guarantee of mandatory proof; \"The contribution here is an implementation and tests of mandatory proof: accepting only what the verified checker derives from declared, reviewed foundations blocks the Barnes-Christiano construction for formalised claims by excluding assumed false sub-claims.\""
        },
        "declared_foundations": {
          "sort": "item",
          "description": "the declared foundations"
        },
        "prevention": {
          "sort": "item",
          "description": "mandatory proof preventing arbitrary false sub-claims from being accepted as new assumptions; \"The contribution here is an implementation and tests of mandatory proof: accepting only what the verified checker derives from declared, reviewed foundations blocks the Barnes-Christiano construction for formalised claims by excluding assumed false sub-claims.\""
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
      "meaning_id": "994c26b0562b940711d521d2e8a251f93090a1a669e6511f7cd44a1205b9752b"
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
      "meaning_id": "7eb804d99f68ceda7fe5f6ef7a1aa588ca98b3e362f7160e1e7e1b5c95619e7f"
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
      "meaning_id": "a06f44206c5eb06e749bbc94c18ff85a366640be6d40dc150d675a370e8f90df"
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
      "meaning_id": "f56c09c377a391eb01ceea3d5053dfc47b4290c9b3b306905d6e599dd47f426b"
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
      "meaning_id": "c440602cbb84b0c0d907dc722639ce9ddd2ea957649d89e201b00cc25f4883d7"
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
      "meaning_id": "5c829a9049f95fcde64ae65c5394ba6a5f7f96fd40f6a3bcd6dbaadac0041259"
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
      "meaning_id": "43cfbd7cdeb9e4effa6eb1c0d22a62760c4b01d918e13ce8ab2fadfb78920385"
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
      "meaning_id": "21219f3932d19c276c1276149607e758e263ba81956a2172f171e5ee467a6bf6"
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
      "meaning_id": "4e33dba8e34ec0b9429a3c3cfd0106c206fb494b54b00c14d324bd1a9ec4598f"
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
      "meaning_id": "3e6f63712a43d6fa844587e2eedf047307ba4aa3244c6205610cb86cfe34afe9"
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
      "meaning_id": "fdae13735b080a6aa0dc9b524bc6218daeedca1e9cc1ce05f81f522610c0a76d"
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
      "meaning_id": "e8072833ad2e85d95b0fa4ff9df0aaf2d42189eec9537577a74be575ac0f03c2"
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
      "meaning_id": "5c0f99db6779901e96682a7aa46d4053743eaa4e82d6893b804fe1e0085c6f9f"
    },
    {
      "id": "u046",
      "span": [
        3465,
        3627
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
      "meaning_id": "f71f32ba4f8248cf5c6c16af195b97098c5fa148107742935fdccbeea21d0be5"
    },
    {
      "id": "u047",
      "span": [
        3627,
        3719
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
        3719,
        3777
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
      "meaning_id": "5839148a40ea0b75af10130929775008c3b6104157ba9ab5496e5f06e28ca416"
    },
    {
      "id": "u049",
      "span": [
        3777,
        3838
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
      "meaning_id": "47c820f6361739e21dc47fbf39e0f24963e56a89f453001716f9b7e30c8eb5e3"
    },
    {
      "id": "u050",
      "span": [
        3838,
        3888
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
      "meaning_id": "653ee96758df9e5e49a7e67aa2427e9a95b8e8a4943c275c7b6e75562b72af29"
    },
    {
      "id": "u051",
      "span": [
        3888,
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
      "meaning_id": "4c9a06c3340097350ff858696eec9948807bb764c512592477b2bd94ece2eacd"
    },
    {
      "id": "u052",
      "span": [
        3937,
        3994
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
      "meaning_id": "ddb1546b309140a0728f0a35d144ef51ba9c90ae57db9918e0bed727c38a9e84"
    },
    {
      "id": "u053",
      "span": [
        3994,
        4072
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
        4072,
        4155
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
      "meaning_id": "e42cfb3697c152a034e87474365293aa419ed62c13a67ec2301a80bebf01f2ff"
    },
    {
      "id": "u055",
      "span": [
        4155,
        4235
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
      "meaning_id": "110c755a366e38f5ab4cadd9b306beaa5cc5af60b8dfc69ced2940738a35fb99"
    },
    {
      "id": "u056",
      "span": [
        4235,
        4326
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
      "meaning_id": "e2c06108a1db0d32c39ceb88445218f7ba0740da97988974857b6f0a256f4c7b"
    },
    {
      "id": "u057",
      "span": [
        4326,
        4383
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
      "meaning_id": "53692e1b296334fdb2801757f49e9df40387e638e5d85c3b8b8663dc1c708134"
    },
    {
      "id": "u058",
      "span": [
        4383,
        4436
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
      "meaning_id": "a55019e1a8c7b3b790e459c706229cc4fd68efc8e0277ffa52e1323ee4af9b90"
    },
    {
      "id": "u059",
      "span": [
        4436,
        4508
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
      "meaning_id": "356954cb1cbceaafb90768c903542dc5b602d379801bf4f47d2c4776a7b6d17b"
    },
    {
      "id": "u060",
      "span": [
        4508,
        4695
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
        4695,
        4786
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
      "meaning_id": "d47ff107be9f34a0e62d5319267c393e3b30c320d5bcccb66c963f13773a9762"
    },
    {
      "id": "u062",
      "span": [
        4786,
        4866
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
      "meaning_id": "c03ad7078fb58b228ca847f8fd61dda95bd19d4b30fd550a2efd87219d18eef3"
    },
    {
      "id": "u063",
      "span": [
        4866,
        5042
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
        5042,
        5198
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
        5198,
        5235
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
      "meaning_id": "36d9dd4703c9d9a7f039a029ad384ca78ba2022ff25100393a84fd71b50f4c55"
    },
    {
      "id": "u066",
      "span": [
        5235,
        5328
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
      "meaning_id": "34a0ff8eb3c05a6f8b56a4aa79188f2496b6222a2ae8e4b04f07509f9e93c267"
    },
    {
      "id": "u067",
      "span": [
        5328,
        5395
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
      "meaning_id": "b10628f2a1e386394e31afd8ac6765b4581c9df611a5e1d2ae56ba5c0d0fb01e"
    },
    {
      "id": "u068",
      "span": [
        5395,
        5479
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
      "meaning_id": "23fca9b7ef3743dfe7df046368111b894a701a4c9281f679eb9739df3dc0e395"
    },
    {
      "id": "u069",
      "span": [
        5479,
        5536
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
        5536,
        5591
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
      "meaning_id": "6669b14b46778aefe55d6563746728058b43bda65b22e2acd8409afdfae1c526"
    },
    {
      "id": "u071",
      "span": [
        5591,
        5606
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u072",
      "span": [
        5606,
        5659
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u073",
      "span": [
        5659,
        5675
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u074",
      "span": [
        5675,
        5838
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
      "meaning_id": "7eb804d99f68ceda7fe5f6ef7a1aa588ca98b3e362f7160e1e7e1b5c95619e7f"
    },
    {
      "id": "u075",
      "span": [
        5838,
        5894
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u076",
      "span": [
        5894,
        6075
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
      "meaning_id": "a06f44206c5eb06e749bbc94c18ff85a366640be6d40dc150d675a370e8f90df"
    },
    {
      "id": "u077",
      "span": [
        6075,
        6121
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u078",
      "span": [
        6121,
        6341
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
        6341,
        6435
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
        6435,
        6536
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
        6536,
        6608
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
        6608,
        6671
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
        6671,
        6734
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
        6734,
        6996
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
        6996,
        7053
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
        7053,
        7100
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
        7100,
        7149
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
      "meaning_id": "5c829a9049f95fcde64ae65c5394ba6a5f7f96fd40f6a3bcd6dbaadac0041259"
    },
    {
      "id": "u088",
      "span": [
        7149,
        7190
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
      "meaning_id": "43cfbd7cdeb9e4effa6eb1c0d22a62760c4b01d918e13ce8ab2fadfb78920385"
    },
    {
      "id": "u089",
      "span": [
        7190,
        7261
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
      "meaning_id": "21219f3932d19c276c1276149607e758e263ba81956a2172f171e5ee467a6bf6"
    },
    {
      "id": "u090",
      "span": [
        7261,
        7322
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
      "meaning_id": "4e33dba8e34ec0b9429a3c3cfd0106c206fb494b54b00c14d324bd1a9ec4598f"
    },
    {
      "id": "u091",
      "span": [
        7322,
        7411
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
        7411,
        7441
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
      "meaning_id": "3e6f63712a43d6fa844587e2eedf047307ba4aa3244c6205610cb86cfe34afe9"
    },
    {
      "id": "u093",
      "span": [
        7441,
        7570
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
      "meaning_id": "fdae13735b080a6aa0dc9b524bc6218daeedca1e9cc1ce05f81f522610c0a76d"
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
          "meaning_id": "e8072833ad2e85d95b0fa4ff9df0aaf2d42189eec9537577a74be575ac0f03c2",
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
          "meaning_id": "5c0f99db6779901e96682a7aa46d4053743eaa4e82d6893b804fe1e0085c6f9f",
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
          "meaning_id": "f71f32ba4f8248cf5c6c16af195b97098c5fa148107742935fdccbeea21d0be5",
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
          "meaning_id": "5839148a40ea0b75af10130929775008c3b6104157ba9ab5496e5f06e28ca416",
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
          "meaning_id": "47c820f6361739e21dc47fbf39e0f24963e56a89f453001716f9b7e30c8eb5e3",
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
          "meaning_id": "653ee96758df9e5e49a7e67aa2427e9a95b8e8a4943c275c7b6e75562b72af29",
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
          "meaning_id": "4c9a06c3340097350ff858696eec9948807bb764c512592477b2bd94ece2eacd",
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
          "meaning_id": "ddb1546b309140a0728f0a35d144ef51ba9c90ae57db9918e0bed727c38a9e84",
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
          "meaning_id": "e42cfb3697c152a034e87474365293aa419ed62c13a67ec2301a80bebf01f2ff",
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
          "meaning_id": "110c755a366e38f5ab4cadd9b306beaa5cc5af60b8dfc69ced2940738a35fb99",
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
          "meaning_id": "53692e1b296334fdb2801757f49e9df40387e638e5d85c3b8b8663dc1c708134",
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
          "meaning_id": "a55019e1a8c7b3b790e459c706229cc4fd68efc8e0277ffa52e1323ee4af9b90",
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
          "meaning_id": "356954cb1cbceaafb90768c903542dc5b602d379801bf4f47d2c4776a7b6d17b",
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
          "meaning_id": "d47ff107be9f34a0e62d5319267c393e3b30c320d5bcccb66c963f13773a9762",
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
          "meaning_id": "c03ad7078fb58b228ca847f8fd61dda95bd19d4b30fd550a2efd87219d18eef3",
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
          "meaning_id": "36d9dd4703c9d9a7f039a029ad384ca78ba2022ff25100393a84fd71b50f4c55",
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
          "meaning_id": "34a0ff8eb3c05a6f8b56a4aa79188f2496b6222a2ae8e4b04f07509f9e93c267",
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
          "meaning_id": "23fca9b7ef3743dfe7df046368111b894a701a4c9281f679eb9739df3dc0e395",
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
          "meaning_id": "6669b14b46778aefe55d6563746728058b43bda65b22e2acd8409afdfae1c526",
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
2. The correction follows section 3 of <ops-repo>/reviews/obfuscation-recheck.md and section 4 and Correction 2 of <repo>/design/positioning-vs-debate-theory.md. Mandatory proof prevents arbitrary false sub-claims from being accepted as new assumptions; the guarantee is conditional on the declared foundations. It does not establish their truth or faithful formalisation. An honest answer still needs an affordable proof; proofs beyond budget leave the claim unresolved.
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
