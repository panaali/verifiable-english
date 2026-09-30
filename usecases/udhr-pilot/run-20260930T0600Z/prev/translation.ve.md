---
{
  "environment": {
    "language": "ve.core@0.2",
    "profiles": [
      "documents@1",
      "norms@0",
      "relational-fol@0"
    ],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
      "constants": {},
      "predicates": {
        "compel_association_membership_permitted": {
          "arguments": [
            "actor",
            "person"
          ],
          "description": "The actor is permitted to compel the person to belong to an association",
          "regulated": {
            "act": "{0} compel {1} to belong to an association",
            "default": "allow",
            "role": "permission"
          }
        },
        "declaration_implies_destructive_right": {
          "arguments": [
            "bearer"
          ],
          "description": "This Declaration implies for the bearer a right to engage in any activity or to perform any act aimed at the destruction of any of the rights and freedoms set forth in it"
        },
        "entitled_to_asylum": {
          "arguments": [
            "person"
          ],
          "description": "The person holds the entitlement to seek and to enjoy asylum from persecution (Article 14, paragraph 1)"
        },
        "exercises_contrary_to_un": {
          "arguments": [
            "person",
            "right"
          ],
          "description": "The person exercises the right or freedom contrary to the purposes and principles of the United Nations"
        },
        "genuinely_prosecuted_for_acts_contrary_to_un": {
          "arguments": [
            "person"
          ],
          "description": "The person faces a prosecution that genuinely arises from acts contrary to the purposes and principles of the United Nations"
        },
        "genuinely_prosecuted_for_non_political_crime": {
          "arguments": [
            "person"
          ],
          "description": "The person faces a prosecution that genuinely arises from a non-political crime"
        },
        "right_protects_exercise": {
          "arguments": [
            "person",
            "right"
          ],
          "description": "The right or freedom protects the person's exercise of it"
        }
      },
      "sorts": {
        "actor": {
          "description": "a person, group, or institution capable of compelling a person",
          "verbalisation": {
            "plural": "actors",
            "singular": "actor"
          }
        },
        "bearer": {
          "description": "a State, group or person",
          "verbalisation": {
            "plural": "bearers",
            "singular": "bearer"
          }
        },
        "person": {
          "description": "a human person",
          "verbalisation": {
            "plural": "people",
            "singular": "person"
          }
        },
        "right": {
          "description": "a right or freedom set forth in this Declaration",
          "verbalisation": {
            "plural": "rights",
            "singular": "right"
          }
        }
      }
    }
  },
  "format": "ve-document@1",
  "open_terms": [
    {
      "arguments": [
        "person"
      ],
      "decided_by": "applicable_court",
      "factors": [
        "equal legal standing",
        "equal legal protection",
        "scope of comparators"
      ],
      "jurisdiction": "universal",
      "name": "equal_before_law",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "meaning of dignity",
        "scope of inherence"
      ],
      "jurisdiction": "universal",
      "name": "inherent_dignity",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "which rights",
        "conditions on transfer or loss"
      ],
      "jurisdiction": "universal",
      "name": "inalienable_rights",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "essential for which end",
        "degree of necessity"
      ],
      "jurisdiction": "universal",
      "name": "essential",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "comparison class",
        "measure of importance"
      ],
      "jurisdiction": "universal",
      "name": "greatest_importance",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "meaning of natural",
        "meaning of fundamental",
        "what counts as family"
      ],
      "jurisdiction": "universal",
      "name": "natural_group_unit",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "applicable_court",
      "factors": [
        "legality",
        "reasonableness",
        "procedural safeguards"
      ],
      "jurisdiction": "universal",
      "name": "arbitrary",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "applicable_court",
      "factors": [
        "procedural fairness",
        "public access",
        "independence"
      ],
      "jurisdiction": "universal",
      "name": "fair",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "health needs",
        "living conditions",
        "resources"
      ],
      "jurisdiction": "universal",
      "name": "adequate",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "fairness criteria",
        "comparison group"
      ],
      "jurisdiction": "universal",
      "name": "just",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "hours",
        "work setting",
        "health and rest"
      ],
      "jurisdiction": "universal",
      "name": "reasonable",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "authenticity of election or prosecution",
        "procedural evidence"
      ],
      "jurisdiction": "universal",
      "name": "genuine",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "reciprocal conduct",
        "meaning of brotherhood"
      ],
      "jurisdiction": "universal",
      "name": "spirit_of_brotherhood",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "human_rights_interpreter",
      "factors": [
        "meaning of justice in the Preamble",
        "scope of the claimed foundation"
      ],
      "jurisdiction": "universal",
      "name": "justice",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which purposes and principles count",
        "what makes an act contrary to them"
      ],
      "jurisdiction": "universal",
      "name": "contrary_to_un_purposes_and_principles",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what separates a political from a non-political crime",
        "who classifies the crime"
      ],
      "jurisdiction": "universal",
      "name": "non_political_crime",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which items of the Declaration count as rights and freedoms"
      ],
      "jurisdiction": "universal",
      "name": "rights_and_freedoms_set_forth",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what it is to aim at the destruction of a right",
        "whether purpose or effect decides"
      ],
      "jurisdiction": "universal",
      "name": "aimed_at_destruction_of_rights",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    }
  ],
  "reading_sets": [
    {
      "id": "rs_u017",
      "models": {
        "708a887d17f0a18a2f49f02299b409c0f0469b1b7a99ad8c5a9cce8151c2aedc": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a"
            ],
            "bearer": [
              "b"
            ],
            "person": [
              "p"
            ],
            "right": [
              "r"
            ]
          },
          "relations": {
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "entitled_to_asylum": [],
            "exercises_contrary_to_un": [],
            "genuinely_prosecuted_for_acts_contrary_to_un": [],
            "genuinely_prosecuted_for_non_political_crime": [],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "default": "708a887d17f0a18a2f49f02299b409c0f0469b1b7a99ad8c5a9cce8151c2aedc"
            },
            "who": "translator",
            "why": "Article 1 'should' read as a strict obligation on every human being to act towards each other human being in a spirit of brotherhood. Elaborated and checked as readings/u017.strict.ve.md (W1 rule, obligation-role predicate, deny-completion means 'not required'; no permission predicate is declared). The reciprocal 'each other human being' is in the act phrase only."
          },
          "content": null,
          "id": "strict",
          "kind": "norm",
          "meaning_id": "2c56fa86c37318cd98de4696764e694c87480bb422c45cda616091786923bac3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "strict": "708a887d17f0a18a2f49f02299b409c0f0469b1b7a99ad8c5a9cce8151c2aedc"
            },
            "who": "translator",
            "why": "Article 1 'should' read as a defeasible rule (soft-norms@0): the same obligation holds unless the rule's exception applies, and the source names no decider ('unstated'). Elaborated and checked as readings/u017.default.ve.md; the exception stays an open decision."
          },
          "content": null,
          "id": "default",
          "kind": "norm",
          "meaning_id": "255300345a2e8a066a6a9e32c39df6857fe86844657228f8f7b9145857ec7161"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "strict",
            "default"
          ],
          "reason": "null-content candidates rejected by the 2026-09-29 audit",
          "version": 1
        }
      ],
      "status": "open",
      "unit": "u017",
      "version": 2
    },
    {
      "id": "rs_u052",
      "models": {
        "33eb92177438d50322c091c9cd67b83772e48ab3904f3a90fe6518b3a6159f02": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a"
            ],
            "bearer": [
              "b"
            ],
            "person": [
              "p"
            ],
            "right": [
              "r"
            ]
          },
          "relations": {
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "entitled_to_asylum": [
              [
                "p"
              ]
            ],
            "exercises_contrary_to_un": [],
            "genuinely_prosecuted_for_acts_contrary_to_un": [],
            "genuinely_prosecuted_for_non_political_crime": [
              [
                "p"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "entitlement_withheld": "33eb92177438d50322c091c9cd67b83772e48ab3904f3a90fe6518b3a6159f02"
            },
            "who": "translator",
            "why": "Article 14(2) read as a strict prohibition on invoking the asylum right of paragraph 1 in the described prosecutions (conditions carried by the sort prosecuted_person, so no completion is invented for other people). Elaborated and checked as readings/u052.invocation_barred.ve.md."
          },
          "content": null,
          "id": "invocation_barred",
          "kind": "norm",
          "meaning_id": "a8ea2ba2f6bb5236101acc191db8a3689a0aa0617e1eed3238e227733d4a8b63"
        },
        {
          "admission": {
            "distinguishing_models": {
              "invocation_barred": "33eb92177438d50322c091c9cd67b83772e48ab3904f3a90fe6518b3a6159f02"
            },
            "who": "translator",
            "why": "Article 14(2) read as withholding the entitlement: whoever faces a prosecution genuinely arising from a non-political crime or from acts contrary to UN purposes and principles is not entitled to asylum. A formula in this document; 'genuinely', 'non-political' and 'contrary to UN purposes and principles' are named open terms."
          },
          "content": [
            "forall",
            "person",
            [
              "implies",
              [
                "or",
                [
                  "unary",
                  "genuinely_prosecuted_for_non_political_crime",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "unary",
                  "genuinely_prosecuted_for_acts_contrary_to_un",
                  [
                    "var",
                    0
                  ]
                ]
              ],
              [
                "not",
                [
                  "unary",
                  "entitled_to_asylum",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ]
          ],
          "id": "entitlement_withheld",
          "kind": "asserted",
          "meaning_id": "49873ceba7606dfefce1c9c27ae29dfe2a919932f2200e68280b7a8e9785feff"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "invocation_barred",
            "right_inapplicable"
          ],
          "reason": "null-content candidates rejected by the 2026-09-29 audit",
          "version": 1
        }
      ],
      "status": "open",
      "unit": "u052",
      "version": 2
    },
    {
      "id": "rs_u112",
      "models": {
        "7406c1eb4bddaf378d1ed089aa7ede68d7cc1768d1e8432cf7a6c421e7bad779": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a"
            ],
            "bearer": [
              "b"
            ],
            "person": [
              "p"
            ],
            "right": [
              "r"
            ]
          },
          "relations": {
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "entitled_to_asylum": [],
            "exercises_contrary_to_un": [
              [
                "p",
                "r"
              ]
            ],
            "genuinely_prosecuted_for_acts_contrary_to_un": [],
            "genuinely_prosecuted_for_non_political_crime": [],
            "right_protects_exercise": [
              [
                "p",
                "r"
              ]
            ]
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "scope_limited": "7406c1eb4bddaf378d1ed089aa7ede68d7cc1768d1e8432cf7a6c421e7bad779"
            },
            "who": "translator",
            "why": "Article 29(3) read as an unconditional prohibition ('in no case': no carve-out, no precedence) on exercising a declared right or freedom contrary to UN purposes and principles. Elaborated and checked as readings/u112.exercise_prohibited.ve.md."
          },
          "content": null,
          "id": "exercise_prohibited",
          "kind": "norm",
          "meaning_id": "6ceb92c97cc437e8ce32c3538e7c35395e6d6310aafb348dd73ea8c50011cf7d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "exercise_prohibited": "7406c1eb4bddaf378d1ed089aa7ede68d7cc1768d1e8432cf7a6c421e7bad779"
            },
            "who": "translator",
            "why": "Article 29(3) read as limiting the scope of the rights: no right or freedom protects an exercise that is contrary to UN purposes and principles. A formula in this document."
          },
          "content": [
            "forall",
            "person",
            [
              "forall",
              "right",
              [
                "implies",
                [
                  "binary",
                  "exercises_contrary_to_un",
                  [
                    "var",
                    1
                  ],
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "not",
                  [
                    "binary",
                    "right_protects_exercise",
                    [
                      "var",
                      1
                    ],
                    [
                      "var",
                      0
                    ]
                  ]
                ]
              ]
            ]
          ],
          "id": "scope_limited",
          "kind": "asserted",
          "meaning_id": "d5df98c5ae7336c7e9b5cf6b1f9f797bfd2a2c0a2cae7689f8cf20c7c6032169"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "exercise_restricted"
          ],
          "reason": "null-content candidates rejected by the 2026-09-29 audit",
          "version": 1
        }
      ],
      "status": "open",
      "unit": "u112",
      "version": 2
    },
    {
      "id": "rs_u114",
      "models": {
        "994f626febf885597a280b59c6ea7316ae8890e01770b5da89ada7a3d6250586": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a"
            ],
            "bearer": [
              "b"
            ],
            "person": [
              "p"
            ],
            "right": [
              "r"
            ]
          },
          "relations": {
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [
              [
                "b"
              ]
            ],
            "entitled_to_asylum": [],
            "exercises_contrary_to_un": [],
            "genuinely_prosecuted_for_acts_contrary_to_un": [],
            "genuinely_prosecuted_for_non_political_crime": [],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "no_implied_right": "994f626febf885597a280b59c6ea7316ae8890e01770b5da89ada7a3d6250586"
            },
            "who": "translator",
            "why": "Article 30 read as a prohibition on interpreting the Declaration as implying, for any State, group or person, a right to destroy declared rights. Elaborated and checked as readings/u114.interpretive_ban.ve.md."
          },
          "content": null,
          "id": "interpretive_ban",
          "kind": "norm",
          "meaning_id": "43ede036d7830ea165274b71c96928bd8154135b35d1673c8219d4f952200f7f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "interpretive_ban": "994f626febf885597a280b59c6ea7316ae8890e01770b5da89ada7a3d6250586"
            },
            "who": "translator",
            "why": "Article 30 read as a statement of the Declaration's content: it implies for no State, group or person a right to engage in any activity or act aimed at destroying any declared right. A formula in this document."
          },
          "content": [
            "forall",
            "bearer",
            [
              "not",
              [
                "unary",
                "declaration_implies_destructive_right",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "id": "no_implied_right",
          "kind": "asserted",
          "meaning_id": "bd89f5f0d9b0d242d2063e2b5036d239242020a64eade2e9196c3d10dd42dca5"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "interpretive_bar"
          ],
          "reason": "null-content candidates rejected by the 2026-09-29 audit",
          "version": 1
        }
      ],
      "status": "open",
      "unit": "u114",
      "version": 2
    }
  ],
  "units": [
    {
      "id": "u001",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        0,
        41
      ],
      "support": "none"
    },
    {
      "id": "u002",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        41,
        54
      ],
      "support": "none"
    },
    {
      "id": "u003",
      "kind": [
        "unformalised",
        "causation"
      ],
      "meaning": {
        "unformalised": "causation"
      },
      "span": [
        54,
        236
      ],
      "support": "none"
    },
    {
      "id": "u004",
      "kind": [
        "unformalised",
        "causation"
      ],
      "meaning": {
        "unformalised": "causation"
      },
      "span": [
        236,
        363
      ],
      "support": "none"
    },
    {
      "id": "u005",
      "kind": [
        "attributed",
        "unstated",
        "says",
        "asserted"
      ],
      "meaning": {
        "unformalised": "attribution"
      },
      "span": [
        363,
        552
      ],
      "support": "none"
    },
    {
      "id": "u006",
      "kind": [
        "unformalised",
        "modality_belief"
      ],
      "meaning": {
        "unformalised": "modality_belief"
      },
      "span": [
        552,
        747
      ],
      "support": "none"
    },
    {
      "id": "u007",
      "kind": [
        "unformalised",
        "modality_belief"
      ],
      "meaning": {
        "unformalised": "modality_belief"
      },
      "span": [
        747,
        838
      ],
      "support": "none"
    },
    {
      "id": "u008a",
      "kind": [
        "attributed",
        "peoples_of_un",
        "believes",
        "asserted"
      ],
      "meaning": {
        "unformalised": "attribution"
      },
      "span": [
        838,
        1037
      ],
      "support": "none"
    },
    {
      "id": "u008b",
      "kind": [
        "attributed",
        "peoples_of_un",
        "intends",
        "norm"
      ],
      "meaning": {
        "unformalised": "attribution"
      },
      "span": [
        1037,
        1134
      ],
      "support": "none"
    },
    {
      "id": "u009",
      "kind": [
        "attributed",
        "member_states",
        "promised",
        "norm"
      ],
      "meaning": {
        "unformalised": "attribution"
      },
      "span": [
        1134,
        1330
      ],
      "support": "none"
    },
    {
      "id": "u010",
      "kind": [
        "unformalised",
        "other_evaluative_open_claim"
      ],
      "meaning": {
        "unformalised": "other_evaluative_open_claim"
      },
      "span": [
        1330,
        1462
      ],
      "support": "none"
    },
    {
      "id": "u011",
      "kind": "meta",
      "meaning": {
        "contextual": "preamble_transition_or_speaker"
      },
      "span": [
        1462,
        1479
      ],
      "support": "none"
    },
    {
      "id": "u012",
      "kind": "meta",
      "meaning": {
        "contextual": "preamble_transition_or_speaker"
      },
      "span": [
        1479,
        1502
      ],
      "support": "none"
    },
    {
      "id": "u013a",
      "kind": [
        "attributed",
        "general_assembly",
        "says",
        "norm"
      ],
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        1502,
        1622
      ],
      "support": "none"
    },
    {
      "id": "u013ba",
      "kind": [
        "unformalised",
        "norms"
      ],
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        1622,
        1817
      ],
      "support": "none"
    },
    {
      "id": "u013bb",
      "kind": [
        "unformalised",
        "norms"
      ],
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        1817,
        2058
      ],
      "support": "none"
    },
    {
      "id": "u014",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2058,
        2072
      ],
      "support": "none"
    },
    {
      "id": "u015",
      "kind": [
        "unformalised",
        "time"
      ],
      "meaning": {
        "unformalised": "time"
      },
      "span": [
        2072,
        2136
      ],
      "support": "none"
    },
    {
      "id": "u016",
      "kind": [
        "unformalised",
        "other_metaphorical_endowment"
      ],
      "meaning": {
        "unformalised": "other_metaphorical_endowment"
      },
      "span": [
        2136,
        2179
      ],
      "support": "none"
    },
    {
      "id": "u017",
      "kind": "norm",
      "meaning": {
        "open": [
          "spirit_of_brotherhood"
        ]
      },
      "span": [
        2179,
        2244
      ],
      "support": "none"
    },
    {
      "id": "u018",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2244,
        2258
      ],
      "support": "none"
    },
    {
      "id": "u019",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        2258,
        2509
      ],
      "support": "none"
    },
    {
      "id": "u020",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        2509,
        2776
      ],
      "support": "none"
    },
    {
      "id": "u021",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2776,
        2790
      ],
      "support": "none"
    },
    {
      "id": "u022",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        2790,
        2855
      ],
      "support": "none"
    },
    {
      "id": "u023",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2855,
        2869
      ],
      "support": "none"
    },
    {
      "id": "u024",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        2869,
        2915
      ],
      "support": "none"
    },
    {
      "id": "u025",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        2915,
        2984
      ],
      "support": "none"
    },
    {
      "id": "u026",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2984,
        2998
      ],
      "support": "none"
    },
    {
      "id": "u027",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        2998,
        3095
      ],
      "support": "none"
    },
    {
      "id": "u028",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3095,
        3109
      ],
      "support": "none"
    },
    {
      "id": "u029",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3109,
        3187
      ],
      "support": "none"
    },
    {
      "id": "u030",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3187,
        3201
      ],
      "support": "none"
    },
    {
      "id": "u031",
      "kind": [
        "unformalised",
        "norms"
      ],
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3201,
        3229
      ],
      "support": "none"
    },
    {
      "id": "u032",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3229,
        3306
      ],
      "support": "none"
    },
    {
      "id": "u033a",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3306,
        3402
      ],
      "support": "none"
    },
    {
      "id": "u033b",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3402,
        3455
      ],
      "support": "none"
    },
    {
      "id": "u034",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3455,
        3469
      ],
      "support": "none"
    },
    {
      "id": "u035",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3469,
        3637
      ],
      "support": "none"
    },
    {
      "id": "u036",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3637,
        3651
      ],
      "support": "none"
    },
    {
      "id": "u037",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3651,
        3719
      ],
      "support": "none"
    },
    {
      "id": "u038",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3719,
        3734
      ],
      "support": "none"
    },
    {
      "id": "u039",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3734,
        3935
      ],
      "support": "none"
    },
    {
      "id": "u040",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3935,
        3950
      ],
      "support": "none"
    },
    {
      "id": "u041",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3950,
        4151
      ],
      "support": "none"
    },
    {
      "id": "u042",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        4151,
        4351
      ],
      "support": "none"
    },
    {
      "id": "u043",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        4351,
        4469
      ],
      "support": "none"
    },
    {
      "id": "u044",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        4469,
        4484
      ],
      "support": "none"
    },
    {
      "id": "u045a",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        4484,
        4584
      ],
      "support": "none"
    },
    {
      "id": "u045b",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        4584,
        4633
      ],
      "support": "none"
    },
    {
      "id": "u046",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        4633,
        4724
      ],
      "support": "none"
    },
    {
      "id": "u047",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        4724,
        4739
      ],
      "support": "none"
    },
    {
      "id": "u048",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        4739,
        4837
      ],
      "support": "none"
    },
    {
      "id": "u049",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        4837,
        4935
      ],
      "support": "none"
    },
    {
      "id": "u050",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        4935,
        4950
      ],
      "support": "none"
    },
    {
      "id": "u051",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        4950,
        5042
      ],
      "support": "none"
    },
    {
      "id": "u052",
      "kind": "norm",
      "meaning": {
        "open": [
          "genuine",
          "non_political_crime",
          "contrary_to_un_purposes_and_principles"
        ]
      },
      "span": [
        5042,
        5224
      ],
      "support": "none"
    },
    {
      "id": "u053",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        5224,
        5239
      ],
      "support": "none"
    },
    {
      "id": "u054",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5239,
        5284
      ],
      "support": "none"
    },
    {
      "id": "u055",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5284,
        5392
      ],
      "support": "none"
    },
    {
      "id": "u056",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        5392,
        5407
      ],
      "support": "none"
    },
    {
      "id": "u057",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5407,
        5545
      ],
      "support": "none"
    },
    {
      "id": "u058",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5545,
        5636
      ],
      "support": "none"
    },
    {
      "id": "u059",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5636,
        5733
      ],
      "support": "none"
    },
    {
      "id": "u060",
      "kind": [
        "unformalised",
        "other_evaluative_open_claim"
      ],
      "meaning": {
        "unformalised": "other_evaluative_open_claim"
      },
      "span": [
        5733,
        5799
      ],
      "support": "none"
    },
    {
      "id": "u061",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5799,
        5857
      ],
      "support": "none"
    },
    {
      "id": "u062",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        5857,
        5872
      ],
      "support": "none"
    },
    {
      "id": "u063",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5872,
        5960
      ],
      "support": "none"
    },
    {
      "id": "u064",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5960,
        6018
      ],
      "support": "none"
    },
    {
      "id": "u065",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        6018,
        6033
      ],
      "support": "none"
    },
    {
      "id": "u066",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6033,
        6104
      ],
      "support": "none"
    },
    {
      "id": "u067",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6104,
        6166
      ],
      "support": "none"
    },
    {
      "id": "u068",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6166,
        6329
      ],
      "support": "none"
    },
    {
      "id": "u069",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        6329,
        6344
      ],
      "support": "none"
    },
    {
      "id": "u070",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6344,
        6405
      ],
      "support": "none"
    },
    {
      "id": "u071a",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6405,
        6470
      ],
      "support": "none"
    },
    {
      "id": "u071b",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6470,
        6573
      ],
      "support": "none"
    },
    {
      "id": "u072",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        6573,
        6588
      ],
      "support": "none"
    },
    {
      "id": "u073",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6588,
        6664
      ],
      "support": "none"
    },
    {
      "content": {
        "norm": {
          "guard": [
            "top"
          ],
          "name": "no-compelled-association-membership",
          "over": [],
          "predicate": "compel_association_membership_permitted",
          "sign": false,
          "unless": []
        }
      },
      "id": "u074",
      "kind": "norm",
      "meaning": "specified",
      "span": [
        6664,
        6721
      ],
      "status": "CHECKED",
      "support": "none"
    },
    {
      "id": "u075",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        6721,
        6736
      ],
      "support": "none"
    },
    {
      "id": "u076",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6736,
        6861
      ],
      "support": "none"
    },
    {
      "id": "u077",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6861,
        6938
      ],
      "support": "none"
    },
    {
      "id": "u078",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        6938,
        7015
      ],
      "support": "none"
    },
    {
      "id": "u079a",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7015,
        7124
      ],
      "support": "none"
    },
    {
      "id": "u079b",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7124,
        7200
      ],
      "support": "none"
    },
    {
      "id": "u080",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        7200,
        7215
      ],
      "support": "none"
    },
    {
      "id": "u081",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7215,
        7281
      ],
      "support": "none"
    },
    {
      "id": "u082",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7281,
        7558
      ],
      "support": "none"
    },
    {
      "id": "u083",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        7558,
        7573
      ],
      "support": "none"
    },
    {
      "id": "u084a",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7573,
        7606
      ],
      "support": "none"
    },
    {
      "id": "u084b",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7606,
        7636
      ],
      "support": "none"
    },
    {
      "id": "u084c",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7636,
        7679
      ],
      "support": "none"
    },
    {
      "id": "u084d",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7679,
        7721
      ],
      "support": "none"
    },
    {
      "id": "u085",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7721,
        7806
      ],
      "support": "none"
    },
    {
      "id": "u086",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        7806,
        8022
      ],
      "support": "none"
    },
    {
      "id": "u087",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8022,
        8119
      ],
      "support": "none"
    },
    {
      "id": "u088",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        8119,
        8134
      ],
      "support": "none"
    },
    {
      "id": "u089",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8134,
        8260
      ],
      "support": "none"
    },
    {
      "id": "u090",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        8260,
        8275
      ],
      "support": "none"
    },
    {
      "id": "u091",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8275,
        8476
      ],
      "support": "none"
    },
    {
      "id": "u092",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8476,
        8639
      ],
      "support": "none"
    },
    {
      "id": "u093",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8639,
        8712
      ],
      "support": "none"
    },
    {
      "id": "u094",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8712,
        8802
      ],
      "support": "none"
    },
    {
      "id": "u095",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        8802,
        8817
      ],
      "support": "none"
    },
    {
      "id": "u096",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8817,
        8857
      ],
      "support": "none"
    },
    {
      "id": "u097",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8857,
        8933
      ],
      "support": "none"
    },
    {
      "id": "u098",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8933,
        8975
      ],
      "support": "none"
    },
    {
      "id": "u099a",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        8975,
        9045
      ],
      "support": "none"
    },
    {
      "id": "u099b",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9045,
        9126
      ],
      "support": "none"
    },
    {
      "id": "u100a",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9126,
        9205
      ],
      "support": "none"
    },
    {
      "id": "u100b",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9205,
        9285
      ],
      "support": "none"
    },
    {
      "id": "u101",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9285,
        9389
      ],
      "support": "none"
    },
    {
      "id": "u102",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9389,
        9475
      ],
      "support": "none"
    },
    {
      "id": "u103",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9475,
        9577
      ],
      "support": "none"
    },
    {
      "id": "u104",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        9577,
        9592
      ],
      "support": "none"
    },
    {
      "id": "u105a",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9592,
        9677
      ],
      "support": "none"
    },
    {
      "id": "u105b",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9677,
        9696
      ],
      "support": "none"
    },
    {
      "id": "u105c",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9696,
        9755
      ],
      "support": "none"
    },
    {
      "id": "u106",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9755,
        9926
      ],
      "support": "none"
    },
    {
      "id": "u107",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        9926,
        9941
      ],
      "support": "none"
    },
    {
      "id": "u108",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        9941,
        10085
      ],
      "support": "none"
    },
    {
      "id": "u109",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        10085,
        10100
      ],
      "support": "none"
    },
    {
      "id": "u110",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        10100,
        10218
      ],
      "support": "none"
    },
    {
      "id": "u111a",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        10218,
        10441
      ],
      "support": "none"
    },
    {
      "id": "u111b",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        10441,
        10555
      ],
      "support": "none"
    },
    {
      "id": "u112",
      "kind": "norm",
      "meaning": {
        "open": [
          "rights_and_freedoms_set_forth",
          "contrary_to_un_purposes_and_principles"
        ]
      },
      "span": [
        10555,
        10676
      ],
      "support": "none"
    },
    {
      "id": "u113",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        10676,
        10691
      ],
      "support": "none"
    },
    {
      "id": "u114",
      "kind": "norm",
      "meaning": {
        "open": [
          "rights_and_freedoms_set_forth",
          "aimed_at_destruction_of_rights"
        ]
      },
      "span": [
        10691,
        10916
      ],
      "support": "none"
    }
  ]
}
---
# Universal Declaration of Human Rights

## Preamble

Whereas recognition of the inherent dignity and of the equal and inalienable rights of all members of the human family is the foundation of freedom, justice and peace in the world,

Whereas disregard and contempt for human rights have resulted in barbarous acts which have outraged the conscience of mankind, and the advent of a world in which human beings shall enjoy freedom of speech and belief and freedom from fear and want has been proclaimed as the highest aspiration of the common people,

Whereas it is essential, if man is not to be compelled to have recourse, as a last resort, to rebellion against tyranny and oppression, that human rights should be protected by the rule of law,

Whereas it is essential to promote the development of friendly relations between nations,

Whereas the peoples of the United Nations have in the Charter reaffirmed their faith in fundamental human rights, in the dignity and worth of the human person and in the equal rights of men and women and have determined to promote social progress and better standards of life in larger freedom,

Whereas Member States have pledged themselves to achieve, in co-operation with the United Nations, the promotion of universal respect for and observance of human rights and fundamental freedoms,

Whereas a common understanding of these rights and freedoms is of the greatest importance for the full realization of this pledge,

Now, therefore,

The General Assembly,

Proclaims this Universal Declaration of Human Rights as a common standard of achievement for all peoples and all nations, to the end that every individual and every organ of society, keeping this Declaration constantly in mind, shall strive by teaching and education to promote respect for these rights and freedoms and by progressive measures, national and international, to secure their universal and effective recognition and observance, both among the peoples of Member States themselves and among the peoples of territories under their jurisdiction.

## Article 1

All human beings are born free and equal in dignity and rights. They are endowed with reason and conscience and should act towards one another in a spirit of brotherhood.

## Article 2

Everyone is entitled to all the rights and freedoms set forth in this Declaration, without distinction of any kind, such as race, colour, sex, language, religion, political or other opinion, national or social origin, property, birth or other status. Furthermore, no distinction shall be made on the basis of the political, jurisdictional or international status of the country or territory to which a person belongs, whether it be independent, trust, non-self-governing or under any other limitation of sovereignty.

## Article 3

Everyone has the right to life, liberty and security of person.

## Article 4

No one shall be held in slavery or servitude; slavery and the slave trade shall be prohibited in all their forms.

## Article 5

No one shall be subjected to torture or to cruel, inhuman or degrading treatment or punishment.

## Article 6

Everyone has the right to recognition everywhere as a person before the law.

## Article 7

All are equal before the law and are entitled without any discrimination to equal protection of the law. All are entitled to equal protection against any discrimination in violation of this Declaration and against any incitement to such discrimination.

## Article 8

Everyone has the right to an effective remedy by the competent national tribunals for acts violating the fundamental rights granted him by the constitution or by law.

## Article 9

No one shall be subjected to arbitrary arrest, detention or exile.

## Article 10

Everyone is entitled in full equality to a fair and public hearing by an independent and impartial tribunal, in the determination of his rights and obligations and of any criminal charge against him.

## Article 11

1. Everyone charged with a penal offence has the right to be presumed innocent until proved guilty according to law in a public trial at which he has had all the guarantees necessary for his defence.

2. No one shall be held guilty of any penal offence on account of any act or omission which did not constitute a penal offence, under national or international law, at the time when it was committed. Nor shall a heavier penalty be imposed than the one that was applicable at the time the penal offence was committed.

## Article 12

No one shall be subjected to arbitrary interference with his privacy, family, home or correspondence, nor to attacks upon his honour and reputation. Everyone has the right to the protection of the law against such interference or attacks.

## Article 13

1. Everyone has the right to freedom of movement and residence within the borders of each state.

2. Everyone has the right to leave any country, including his own, and to return to his country.

## Article 14

1. Everyone has the right to seek and to enjoy in other countries asylum from persecution.

2. This right may not be invoked in the case of prosecutions genuinely arising from non-political crimes or from acts contrary to the purposes and principles of the United Nations.

## Article 15

1. Everyone has the right to a nationality.

2. No one shall be arbitrarily deprived of his nationality nor denied the right to change his nationality.

## Article 16

1. Men and women of full age, without any limitation due to race, nationality or religion, have the right to marry and to found a family. They are entitled to equal rights as to marriage, during marriage and at its dissolution.

2. Marriage shall be entered into only with the free and full consent of the intending spouses.

3. The family is the natural and fundamental group unit of society and is entitled to protection by society and the State.

## Article 17

1. Everyone has the right to own property alone as well as in association with others.

2. No one shall be arbitrarily deprived of his property.

## Article 18

Everyone has the right to freedom of thought, conscience and religion; this right includes freedom to change his religion or belief, and freedom, either alone or in community with others and in public or private, to manifest his religion or belief in teaching, practice, worship and observance.

## Article 19

Everyone has the right to freedom of opinion and expression; this right includes freedom to hold opinions without interference and to seek, receive and impart information and ideas through any media and regardless of frontiers.

## Article 20

1. Everyone has the right to freedom of peaceful assembly and association.

2. No one may be compelled to belong to an association.

## Article 21

1. Everyone has the right to take part in the government of his country, directly or through freely chosen representatives.

2. Everyone has the right of equal access to public service in his country.

3. The will of the people shall be the basis of the authority of government; this will shall be expressed in periodic and genuine elections which shall be by universal and equal suffrage and shall be held by secret vote or by equivalent free voting procedures.

## Article 22

Everyone, as a member of society, has the right to social security and is entitled to realization, through national effort and international co-operation and in accordance with the organization and resources of each State, of the economic, social and cultural rights indispensable for his dignity and the free development of his personality.

## Article 23

1. Everyone has the right to work, to free choice of employment, to just and favourable conditions of work and to protection against unemployment.

2. Everyone, without any discrimination, has the right to equal pay for equal work.

3. Everyone who works has the right to just and favourable remuneration ensuring for himself and his family an existence worthy of human dignity, and supplemented, if necessary, by other means of social protection.

4. Everyone has the right to form and to join trade unions for the protection of his interests.

## Article 24

Everyone has the right to rest and leisure, including reasonable limitation of working hours and periodic holidays with pay.

## Article 25

1. Everyone has the right to a standard of living adequate for the health and well-being of himself and of his family, including food, clothing, housing and medical care and necessary social services, and the right to security in the event of unemployment, sickness, disability, widowhood, old age or other lack of livelihood in circumstances beyond his control.

2. Motherhood and childhood are entitled to special care and assistance. All children, whether born in or out of wedlock, shall enjoy the same social protection.

## Article 26

1. Everyone has the right to education. Education shall be free, at least in the elementary and fundamental stages. Elementary education shall be compulsory. Technical and professional education shall be made generally available and higher education shall be equally accessible to all on the basis of merit.

2. Education shall be directed to the full development of the human personality and to the strengthening of respect for human rights and fundamental freedoms. It shall promote understanding, tolerance and friendship among all nations, racial or religious groups, and shall further the activities of the United Nations for the maintenance of peace.

3. Parents have a prior right to choose the kind of education that shall be given to their children.

## Article 27

1. Everyone has the right freely to participate in the cultural life of the community, to enjoy the arts and to share in scientific advancement and its benefits.

2. Everyone has the right to the protection of the moral and material interests resulting from any scientific, literary or artistic production of which he is the author.

## Article 28

Everyone is entitled to a social and international order in which the rights and freedoms set forth in this Declaration can be fully realized.

## Article 29

1. Everyone has duties to the community in which alone the free and full development of his personality is possible.

2. In the exercise of his rights and freedoms, everyone shall be subject only to such limitations as are determined by law solely for the purpose of securing due recognition and respect for the rights and freedoms of others and of meeting the just requirements of morality, public order and the general welfare in a democratic society.

3. These rights and freedoms may in no case be exercised contrary to the purposes and principles of the United Nations.

## Article 30

Nothing in this Declaration may be interpreted as implying for any State, group or person any right to engage in any activity or to perform any act aimed at the destruction of any of the rights and freedoms set forth herein.
