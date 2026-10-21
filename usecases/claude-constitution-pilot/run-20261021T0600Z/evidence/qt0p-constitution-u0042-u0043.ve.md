---
{
 "format": "ve-document@1",
 "environment": {
  "language": "ve.core@0.2",
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "profiles": [
   "documents@1",
   "norms@0",
   "readings@1",
   "relational-fol@0"
  ],
  "vocabulary": {
   "sorts": {
    "principal_type": {
     "description": "A type of principal, in the source's sense (u0042, u0043): a kind of party whose instructions Claude gives weight to.",
     "verbalisation": {
      "singular": "type of principal",
      "plural": "types of principals"
     }
    }
   },
   "constants": {
    "anthropic": {
     "sort": "principal_type",
     "description": "Anthropic, as a type of principal (u0043.s02)."
    },
    "operators": {
     "sort": "principal_type",
     "description": "Operators, as a type of principal (u0043.s02)."
    },
    "users": {
     "sort": "principal_type",
     "description": "Users, as a type of principal (u0043.s02)."
    }
   },
   "predicates": {
    "claude_principal_type": {
     "arguments": [
      "principal_type"
     ],
     "description": "The type of principal is one of Claude's types of principals.",
     "verbalisation": "{0} is one of Claude's types of principals",
     "negative_verbalisation": "{0} is not one of Claude's types of principals"
    }
   }
  }
 },
 "units": [
  {
   "id": "u0042.presupposition",
   "span": [
    0,
    38
   ],
   "support": "assumption",
   "kind": "asserted",
   "meaning": "specified",
   "content": {
    "ast": [
     "exists",
     "principal_type",
     [
      "exists",
      "principal_type",
      [
       "exists",
       "principal_type",
       [
        "and",
        [
         "unary",
         "claude_principal_type",
         [
          "var",
          2
         ]
        ],
        [
         "and",
         [
          "unary",
          "claude_principal_type",
          [
           "var",
           1
          ]
         ],
         [
          "and",
          [
           "unary",
           "claude_principal_type",
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
             "eq",
             [
              "var",
              2
             ],
             [
              "var",
              1
             ]
            ]
           ],
           [
            "and",
            [
             "not",
             [
              "eq",
              [
               "var",
               2
              ],
              [
               "var",
               0
              ]
             ]
            ],
            [
             "and",
             [
              "not",
              [
               "eq",
               [
                "var",
                1
               ],
               [
                "var",
                0
               ]
              ]
             ],
             [
              "forall",
              "principal_type",
              [
               "implies",
               [
                "unary",
                "claude_principal_type",
                [
                 "var",
                 0
                ]
               ],
               [
                "or",
                [
                 "eq",
                 [
                  "var",
                  0
                 ],
                 [
                  "var",
                  3
                 ]
                ],
                [
                 "or",
                 [
                  "eq",
                  [
                   "var",
                   0
                  ],
                  [
                   "var",
                   2
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
              ]
             ]
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
  {
   "id": "u0043.s01",
   "span": [
    38,
    139
   ],
   "support": "none",
   "kind": [
    "unformalised",
    "counting"
   ],
   "meaning": {
    "unformalised": "counting"
   }
  },
  {
   "id": "u0043.s02",
   "span": [
    139,
    229
   ],
   "status": "MIXED",
   "parts": [
    {
     "id": "u0043.s02.p1",
     "span": [
      139,
      154
     ],
     "status": "LABELLED",
     "support": "none",
     "kind": "meta",
     "meaning": "specified"
    },
    {
     "id": "u0043.s02.p2",
     "span": [
      154,
      229
     ],
     "status": "CHECKED",
     "support": "assumption",
     "kind": "asserted",
     "meaning": "specified",
     "content": {
      "ast": [
       "and",
       [
        "unary",
        "claude_principal_type",
        [
         "const",
         "anthropic"
        ]
       ],
       [
        "and",
        [
         "unary",
         "claude_principal_type",
         [
          "const",
          "operators"
         ]
        ],
        [
         "and",
         [
          "unary",
          "claude_principal_type",
          [
           "const",
           "users"
          ]
         ],
         [
          "and",
          [
           "not",
           [
            "eq",
            [
             "const",
             "anthropic"
            ],
            [
             "const",
             "operators"
            ]
           ]
          ],
          [
           "and",
           [
            "not",
            [
             "eq",
             [
              "const",
              "anthropic"
             ],
             [
              "const",
              "users"
             ]
            ]
           ],
           [
            "and",
            [
             "not",
             [
              "eq",
              [
               "const",
               "operators"
              ],
              [
               "const",
               "users"
              ]
             ]
            ],
            [
             "forall",
             "principal_type",
             [
              "implies",
              [
               "unary",
               "claude_principal_type",
               [
                "var",
                0
               ]
              ],
              [
               "or",
               [
                "eq",
                [
                 "var",
                 0
                ],
                [
                 "const",
                 "anthropic"
                ]
               ],
               [
                "or",
                [
                 "eq",
                 [
                  "var",
                  0
                 ],
                 [
                  "const",
                  "operators"
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
                  "users"
                 ]
                ]
               ]
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
    }
   ]
  }
 ]
}
---
Claude’s three types of principals

Different principals are given different levels of trust and interact with Claude in different ways. At the moment, Claude’s three types of principals are Anthropic, operators, and users.

