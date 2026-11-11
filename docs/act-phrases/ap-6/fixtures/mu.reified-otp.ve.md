---
{
 "format": "ve-document@1",
 "environment": {
  "language": "ve.core@0.2",
  "profiles": [
   "documents@1",
   "norm-defaults@0",
   "norms@0",
   "relational-fol@0"
  ],
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "vocabulary": {
   "sorts": {
    "person": {
     "description": "person"
    },
    "item": {
     "description": "item"
    },
    "publication": {
     "description": "publication"
    },
    "day": {
     "description": "a day"
    }
   },
   "predicates": {
    "publish_about_permitted": {
     "arguments": [
      "person",
      "publication"
     ],
     "description": "{0} make {1}",
     "regulated": {
      "role": "permission",
      "default": "deny",
      "act": "{0} make {1}"
     }
    },
    "attacks_honour": {
     "arguments": [
      "item",
      "person"
     ],
     "description": "{0} attacks the honour of {1}",
     "verbalisation": "{0} attacks the honour of {1}"
    },
    "publication_of": {
     "arguments": [
      "publication",
      "item"
     ],
     "description": "{0} publishes {1}",
     "verbalisation": "{0} publishes {1}"
    },
    "publication_about": {
     "arguments": [
      "publication",
      "person"
     ],
     "description": "{0} is about {1}",
     "verbalisation": "{0} is about {1}"
    },
    "before": {
     "arguments": [
      "day",
      "day"
     ],
     "description": "before",
     "verbalisation": "{0} is before {1}"
    },
    "publication_on": {
     "arguments": [
      "publication",
      "day"
     ],
     "description": "{0} happens on {1}",
     "verbalisation": "{0} happens on {1}"
    }
   },
   "constants": {
    "bob": {
     "sort": "person",
     "description": "bob"
    },
    "carol": {
     "sort": "person",
     "description": "carol"
    },
    "leak": {
     "sort": "item",
     "description": "leak"
    },
    "p1": {
     "sort": "publication",
     "description": "p1"
    }
   }
  }
 },
 "units": [
  {
   "id": "u1",
   "span": [
    0,
    106
   ],
   "kind": "norm",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "norm": {
     "name": "r19",
     "predicate": "publish_about_permitted",
     "sign": true,
     "guard": [
      "exists",
      "item",
      [
       "and",
       [
        "binary",
        "publication_of",
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
        "exists",
        "person",
        [
         "and",
         [
          "binary",
          "publication_about",
          [
           "var",
           2
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
           "attacks_honour",
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
      ]
     ],
     "unless": [],
     "over": []
    }
   }
  },
  {
   "id": "u2",
   "span": [
    106,
    144
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "binary",
     "attacks_honour",
     [
      "const",
      "leak"
     ],
     [
      "const",
      "carol"
     ]
    ]
   }
  },
  {
   "id": "u3",
   "span": [
    144,
    179
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "binary",
     "publication_of",
     [
      "const",
      "p1"
     ],
     [
      "const",
      "leak"
     ]
    ]
   }
  },
  {
   "id": "u4",
   "span": [
    179,
    210
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "binary",
     "publication_about",
     [
      "const",
      "p1"
     ],
     [
      "const",
      "carol"
     ]
    ]
   }
  },
  {
   "id": "u5",
   "span": [
    210,
    266
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "forall",
     "publication",
     [
      "forall",
      "item",
      [
       "forall",
       "item",
       [
        "implies",
        [
         "and",
         [
          "binary",
          "publication_of",
          [
           "var",
           2
          ],
          [
           "var",
           1
          ]
         ],
         [
          "binary",
          "publication_of",
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
       ]
      ]
     ]
    ]
   }
  },
  {
   "id": "u6",
   "span": [
    266,
    312
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "forall",
     "publication",
     [
      "exists",
      "item",
      [
       "binary",
       "publication_of",
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
   }
  },
  {
   "id": "u7",
   "span": [
    312,
    371
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "forall",
     "publication",
     [
      "forall",
      "person",
      [
       "forall",
       "person",
       [
        "implies",
        [
         "and",
         [
          "binary",
          "publication_about",
          [
           "var",
           2
          ],
          [
           "var",
           1
          ]
         ],
         [
          "binary",
          "publication_about",
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
       ]
      ]
     ]
    ]
   }
  },
  {
   "id": "u8",
   "span": [
    371,
    420
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "forall",
     "publication",
     [
      "exists",
      "person",
      [
       "binary",
       "publication_about",
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
   }
  },
  {
   "id": "u9",
   "span": [
    420,
    461
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "forall",
     "item",
     [
      "forall",
      "person",
      [
       "exists",
       "publication",
       [
        "and",
        [
         "binary",
         "publication_of",
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
         "binary",
         "publication_about",
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
   }
  },
  {
   "id": "u10",
   "span": [
    461,
    512
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "forall",
     "publication",
     [
      "forall",
      "publication",
      [
       "forall",
       "item",
       [
        "forall",
        "person",
        [
         "implies",
         [
          "and",
          [
           "and",
           [
            "binary",
            "publication_of",
            [
             "var",
             3
            ],
            [
             "var",
             1
            ]
           ],
           [
            "binary",
            "publication_about",
            [
             "var",
             3
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
            "binary",
            "publication_of",
            [
             "var",
             2
            ],
            [
             "var",
             1
            ]
           ],
           [
            "binary",
            "publication_about",
            [
             "var",
             2
            ],
            [
             "var",
             0
            ]
           ]
          ]
         ],
         [
          "eq",
          [
           "var",
           3
          ],
          [
           "var",
           2
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
   "id": "u11",
   "span": [
    512,
    545
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "not",
     [
      "binary",
      "publish_about_permitted",
      [
       "const",
       "bob"
      ],
      [
       "const",
       "p1"
      ]
     ]
    ]
   }
  }
 ],
 "reading_sets": [],
 "graph": {
  "root": "claim",
  "nodes": [
   {
    "name": "claim",
    "ast": [
     "not",
     [
      "binary",
      "publish_about_permitted",
      [
       "const",
       "bob"
      ],
      [
       "const",
       "p1"
      ]
     ]
    ],
    "unit": "u11"
   }
  ]
 }
}
---
Every person may publish each item about each person, unless that item attacks the honour of that person.
The leak attacks the honour of Carol.
Publication p1 publishes the leak.
Publication p1 is about Carol.
Each publication has at most one publication_of filler.
Each publication has a publication_of filler.
Each publication has at most one publication_about filler.
Each publication has a publication_about filler.
Every pair of fillers has a publication.
Every pair of fillers has at most one publication.
Bob may not make publication p1.
