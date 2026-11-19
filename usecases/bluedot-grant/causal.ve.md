---
{
  "format": "ve-document@1",
  "environment": {
    "language": "ve.core@0.2",
    "profiles": [
      "alternatives@0",
      "norms@0",
      "relational-fol@0"
    ],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
      "sorts": {
        "chooser": {
          "description": "an overseer choosing a checking regime",
          "verbalisation": {
            "singular": "chooser",
            "plural": "choosers"
          }
        },
        "action": {
          "description": "a checking practice",
          "verbalisation": {
            "singular": "action",
            "plural": "actions"
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
        "available": {
          "arguments": [
            "action",
            "chooser"
          ],
          "description": "is available to",
          "verbalisation": "{0} is available to {1}"
        },
        "leads_to": {
          "arguments": [
            "action",
            "harm"
          ],
          "description": "leads to",
          "verbalisation": "{0} leads to {1}"
        }
      },
      "constants": {
        "proof_label": {
          "sort": "action",
          "description": "a proof label"
        },
        "mandatory_proof": {
          "sort": "action",
          "description": "mandatory proof; \"The contribution here is an implementation and tests of mandatory proof: accepting only what the verified checker derives from declared, reviewed foundations blocks the Barnes-Christiano construction for formalised claims by excluding assumed false sub-claims.\""
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
    },
    "alternatives": {
      "chooser": "chooser",
      "action": "action",
      "harm": "harm",
      "available": "available",
      "leads_to": "leads_to",
      "outcomes": "signed"
    }
  },
  "units": [
    {
      "id": "u029",
      "span": [
        0,
        93
      ],
      "status": "CHECKED",
      "kind": [
        "attributed",
        "old_text",
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
          "or",
          [
            "binary",
            "leads_to",
            [
              "const",
              "proof_label"
            ],
            [
              "const",
              "premise_confidence"
            ]
          ],
          [
            "binary",
            "leads_to",
            [
              "const",
              "proof_label"
            ],
            [
              "const",
              "fidelity_confidence"
            ]
          ]
        ]
      },
      "meaning_id": "21ef85a6d15aaf6a5be0b04374b17b66f54bb115d99be81d626aa6c07c0935c0"
    },
    {
      "id": "u035",
      "span": [
        93,
        140
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
          "binary",
          "leads_to",
          [
            "const",
            "proof_label"
          ],
          [
            "const",
            "false_confidence"
          ]
        ]
      },
      "meaning_id": "8813ba5dded76e93fadb4761003d86e262f4f4517a8d55413b3c7649bea91bfc"
    },
    {
      "id": "u047",
      "span": [
        140,
        232
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "binary",
          "prevents",
          [
            "const",
            "mandatory_proof"
          ],
          [
            "const",
            "false_subclaim_accepted"
          ]
        ]
      },
      "meaning_id": "2759a08034f20c782fbdb577408ed1a3dd1b68064c74261289a4ea21f5d8f794"
    },
    {
      "id": "u086",
      "span": [
        232,
        279
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
          "binary",
          "leads_to",
          [
            "const",
            "proof_label"
          ],
          [
            "const",
            "false_confidence"
          ]
        ]
      },
      "meaning_id": "8813ba5dded76e93fadb4761003d86e262f4f4517a8d55413b3c7649bea91bfc"
    }
  ],
  "reading_sets": [
    {
      "id": "reading-u047",
      "unit": "u047",
      "version": 1,
      "status": "authored",
      "signature": "grant-author",
      "readings": [
        {
          "id": "chosen",
          "kind": "asserted",
          "meaning_id": "2759a08034f20c782fbdb577408ed1a3dd1b68064c74261289a4ea21f5d8f794",
          "content": [
            "binary",
            "prevents",
            [
              "const",
              "mandatory_proof"
            ],
            [
              "const",
              "false_subclaim_accepted"
            ]
          ],
          "admission": {
            "who": "grant-author",
            "why": "The merged word 'prevents': mandatory proof does not lead to the harm, and another action available to the same chooser does.",
            "distinguishing_models": {}
          }
        }
      ]
    }
  ],
  "graph": {
    "root": "u047",
    "nodes": [
      {
        "name": "u047",
        "ast": [
          "binary",
          "prevents",
          [
            "const",
            "mandatory_proof"
          ],
          [
            "const",
            "false_subclaim_accepted"
          ]
        ],
        "label": "readings:reading-u047@1:0"
      }
    ]
  }
}
---
A proof label could increase false confidence about premise truth or faithful formalisation. A proof label could increase false confidence: Mandatory proof prevents arbitrary false sub-claims from being accepted as new assumptions; A proof label could increase false confidence: 