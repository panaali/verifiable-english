---
{
  "format": "ve-document@1",
  "environment": {
    "language": "ve.core@0.2",
    "profiles": [
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
      "status": "LABELLED",
      "kind": "exposition",
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
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
        "applicant",
        "intends",
        "asserted"
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
      "kind": "exposition",
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
      "kind": "exposition",
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
      "kind": "exposition",
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
      "kind": "exposition",
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
      "kind": "exposition",
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
        "applicant",
        "intends",
        "asserted"
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
        "applicant",
        "intends",
        "asserted"
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
      "kind": "exposition",
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
      "kind": "exposition",
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
        "unformalised",
        "causal_evidence"
      ],
      "meaning": {
        "unformalised": "causal_evidence"
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
      "status": "LABELLED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u030",
      "span": [
        2446,
        2529
      ],
      "status": "UNFORMALISED",
      "kind": [
        "unformalised",
        "causal_evidence"
      ],
      "meaning": {
        "unformalised": "causal_evidence"
      },
      "support": "none"
    },
    {
      "id": "u031",
      "span": [
        2529,
        2588
      ],
      "status": "OPEN",
      "kind": "exposition",
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
      "status": "LABELLED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u033",
      "span": [
        2633,
        2757
      ],
      "status": "UNFORMALISED",
      "kind": [
        "attributed",
        "applicant",
        "expects",
        [
          "unformalised",
          "causal_evidence"
        ]
      ],
      "meaning": {
        "unformalised": "causal_evidence"
      },
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
      "status": "LABELLED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u038",
      "span": [
        2898,
        2969
      ],
      "status": "OPEN",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": {
        "open": [
          "affordable_proof"
        ]
      },
      "support": "none"
    },
    {
      "id": "u039",
      "span": [
        2969,
        3030
      ],
      "status": "LABELLED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u040",
      "span": [
        3030,
        3119
      ],
      "status": "UNFORMALISED",
      "kind": [
        "unformalised",
        "causal_evidence"
      ],
      "meaning": {
        "unformalised": "causal_evidence"
      },
      "support": "none"
    },
    {
      "id": "u041",
      "span": [
        3119,
        3149
      ],
      "status": "OPEN",
      "kind": "exposition",
      "meaning": {
        "open": [
          "real_artefact"
        ]
      },
      "support": "none"
    },
    {
      "id": "u042",
      "span": [
        3149,
        3279
      ],
      "status": "LABELLED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u045",
      "span": [
        3422,
        3465
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u046",
      "span": [
        3465,
        3676
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
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
        "causal_evidence"
      ],
      "meaning": {
        "unformalised": "causal_evidence"
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
              "unary",
              "establishes_foundation_truth",
              [
                "const",
                "proof_rule"
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
      "status": "OPEN",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": {
        "open": [
          "affordable_proof"
        ]
      },
      "support": "none"
    },
    {
      "id": "u051",
      "span": [
        3937,
        3986
      ],
      "status": "OPEN",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": {
        "open": [
          "affordable_proof"
        ]
      },
      "support": "none"
    },
    {
      "id": "u052",
      "span": [
        3986,
        4043
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
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
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
      "status": "UNFORMALISED",
      "kind": [
        "unformalised",
        "causal_evidence"
      ],
      "meaning": {
        "unformalised": "causal_evidence"
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
      "status": "OPEN",
      "kind": "exposition",
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
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": "instruction",
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u068",
      "span": [
        5444,
        5528
      ],
      "status": "LABELLED",
      "kind": "meta",
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": "explanation",
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
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
      "kind": "exposition",
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
      "kind": "exposition",
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
        "applicant",
        "intends",
        "asserted"
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
        "applicant",
        "intends",
        "asserted"
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
      "kind": "exposition",
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
        "unformalised",
        "causal_evidence"
      ],
      "meaning": {
        "unformalised": "causal_evidence"
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
      "status": "LABELLED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
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
      "status": "LABELLED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u089",
      "span": [
        7239,
        7310
      ],
      "status": "OPEN",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": {
        "open": [
          "affordable_proof"
        ]
      },
      "support": "none"
    },
    {
      "id": "u090",
      "span": [
        7310,
        7371
      ],
      "status": "LABELLED",
      "kind": [
        "hedged",
        "could",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
    },
    {
      "id": "u091",
      "span": [
        7371,
        7460
      ],
      "status": "UNFORMALISED",
      "kind": [
        "unformalised",
        "causal_evidence"
      ],
      "meaning": {
        "unformalised": "causal_evidence"
      },
      "support": "none"
    },
    {
      "id": "u092",
      "span": [
        7460,
        7490
      ],
      "status": "OPEN",
      "kind": "exposition",
      "meaning": {
        "open": [
          "real_artefact"
        ]
      },
      "support": "none"
    },
    {
      "id": "u093",
      "span": [
        7490,
        7619
      ],
      "status": "LABELLED",
      "kind": [
        "attributed",
        "applicant",
        "intends",
        "asserted"
      ],
      "meaning": "specified",
      "support": "none"
    }
  ],
  "open_terms": [
    {
      "name": "matched_cost",
      "arguments": [],
      "decided_by": "proposal-author",
      "necessary": [],
      "sufficient": [],
      "factors": [
        "What computational, authoring, and review costs enter the comparison, and how are they measured?"
      ],
      "precedents": [],
      "jurisdiction": "this-draft",
      "version": 1
    },
    {
      "name": "real_artefact",
      "arguments": [],
      "decided_by": "proposal-author",
      "necessary": [],
      "sufficient": [],
      "factors": [
        "What qualifies as a real artifact rather than a planted flaw?"
      ],
      "precedents": [],
      "jurisdiction": "this-draft",
      "version": 1
    },
    {
      "name": "affordable_proof",
      "arguments": [],
      "decided_by": "proposal-author",
      "necessary": [],
      "sufficient": [],
      "factors": [
        "Which proof budgets and hardware make a proof affordable?"
      ],
      "precedents": [],
      "jurisdiction": "this-draft",
      "version": 1
    },
    {
      "name": "misleading_formalisation",
      "arguments": [],
      "decided_by": "proposal-author",
      "necessary": [],
      "sufficient": [],
      "factors": [
        "Who judges fidelity between the source task and its formalisation?"
      ],
      "precedents": [],
      "jurisdiction": "this-draft",
      "version": 1
    },
    {
      "name": "catastrophic_risk",
      "arguments": [],
      "decided_by": "proposal-author",
      "necessary": [],
      "sufficient": [],
      "factors": [
        "Which outcomes count as catastrophic risk, and how is reduction assessed?"
      ],
      "precedents": [],
      "jurisdiction": "this-draft",
      "version": 1
    }
  ],
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
          "meaning_id": "2e79f59122e55dd0188cddb10c23af58fff9efd9413e407f7084313966f2df10",
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
      "id": "reading-u048",
      "unit": "u048",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "e028b698b6207ed02ed04ec93a64be69d6605a3f869ec13bd6bcbb267d56ff87",
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
          "meaning_id": "cc7af9a70606816e3ddb602f68e10f8ab70356f1f9cd10b371fee483217369e7",
          "content": [
            "and",
            [
              "not",
              [
                "unary",
                "establishes_foundation_truth",
                [
                  "const",
                  "proof_rule"
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
      "id": "reading-u055",
      "unit": "u055",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "45916a261d1ed59f2cc742f6dfa9d6be80ee14b1fd1f9d03efda16960ad3f6e0",
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
          "meaning_id": "64516337536cf6105e8f21a4fe41a495219faa641676624c5092215565d4e6d8",
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
          "meaning_id": "9076f0a5f21bd7186d43757169b744d21641bc976a8fd648e85a567dfd4139dc",
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
          "meaning_id": "1213d6e3e85511af91c803d4b928a676e65bd7cbe7c3f75068e468c01608b20f",
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
          "meaning_id": "415aba88d99f96fbbdb8cde1103a912dc6e7920ec4c21827a2006a79f700a077",
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
          "meaning_id": "d82c77fd96baaf9442d0369525bb75921473e499ae0fadf401c2142be5503bd7",
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
      "id": "reading-u065",
      "unit": "u065",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "5e8fc253e425e618235f608530b652ca550bd2a721d30695d23cae7047d97083",
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
          "meaning_id": "d482067aab024b260ea02427d1b4120304963d4ab9acb82dac346e1a1f4d8d6f",
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
      "id": "reading-u087",
      "unit": "u087",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "2e79f59122e55dd0188cddb10c23af58fff9efd9413e407f7084313966f2df10",
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
    }
  ],
  "graph": {
    "root": "accounted-readings",
    "nodes": [
      {
        "name": "claim-u036",
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
        ],
        "label": "readings:reading-u036@1:0"
      },
      {
        "name": "claim-u048",
        "ast": [
          "unary",
          "conditional_on_foundations",
          [
            "const",
            "guarantee"
          ]
        ],
        "label": "readings:reading-u048@1:0"
      },
      {
        "name": "claim-u049",
        "ast": [
          "and",
          [
            "not",
            [
              "unary",
              "establishes_foundation_truth",
              [
                "const",
                "proof_rule"
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
        "label": "readings:reading-u049@1:0"
      },
      {
        "name": "claim-u055",
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
        ],
        "label": "readings:reading-u055@1:0"
      },
      {
        "name": "claim-u057",
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
        ],
        "label": "readings:reading-u057@1:0"
      },
      {
        "name": "claim-u058",
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
        ],
        "label": "readings:reading-u058@1:0"
      },
      {
        "name": "claim-u059",
        "ast": [
          "unary",
          "schedules_development",
          [
            "const",
            "milestones"
          ]
        ],
        "label": "readings:reading-u059@1:0"
      },
      {
        "name": "claim-u061",
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
        ],
        "label": "readings:reading-u061@1:0"
      },
      {
        "name": "claim-u062",
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
        ],
        "label": "readings:reading-u062@1:0"
      },
      {
        "name": "claim-u065",
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
        ],
        "label": "readings:reading-u065@1:0"
      },
      {
        "name": "claim-u066",
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
        ],
        "label": "readings:reading-u066@1:0"
      },
      {
        "name": "claim-u087",
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
        ],
        "label": "readings:reading-u087@1:0"
      },
      {
        "name": "accounted-readings",
        "ast": [
          "top"
        ],
        "premises": [
          "claim-u036",
          "claim-u048",
          "claim-u049",
          "claim-u055",
          "claim-u057",
          "claim-u058",
          "claim-u059",
          "claim-u061",
          "claim-u062",
          "claim-u065",
          "claim-u066",
          "claim-u087"
        ],
        "certificate": {
          "checker_version": "ve-tableau-checker@2",
          "environment_id": "19fa635918c6bb3c4e188458d661cba255b7274a212e2bddb2253879bd5518ba",
          "premise_meaning_ids": [
            "2e79f59122e55dd0188cddb10c23af58fff9efd9413e407f7084313966f2df10",
            "e028b698b6207ed02ed04ec93a64be69d6605a3f869ec13bd6bcbb267d56ff87",
            "cc7af9a70606816e3ddb602f68e10f8ab70356f1f9cd10b371fee483217369e7",
            "45916a261d1ed59f2cc742f6dfa9d6be80ee14b1fd1f9d03efda16960ad3f6e0",
            "64516337536cf6105e8f21a4fe41a495219faa641676624c5092215565d4e6d8",
            "9076f0a5f21bd7186d43757169b744d21641bc976a8fd648e85a567dfd4139dc",
            "1213d6e3e85511af91c803d4b928a676e65bd7cbe7c3f75068e468c01608b20f",
            "415aba88d99f96fbbdb8cde1103a912dc6e7920ec4c21827a2006a79f700a077",
            "d82c77fd96baaf9442d0369525bb75921473e499ae0fadf401c2142be5503bd7",
            "5e8fc253e425e618235f608530b652ca550bd2a721d30695d23cae7047d97083",
            "d482067aab024b260ea02427d1b4120304963d4ab9acb82dac346e1a1f4d8d6f",
            "2e79f59122e55dd0188cddb10c23af58fff9efd9413e407f7084313966f2df10"
          ],
          "conclusion_meaning_id": "f55bb69c086288e0c1ff15fc24640a3b58a6a08d38979bf68de5b77122909430",
          "trace": {
            "rule": "close"
          }
        }
      }
    ]
  }
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
