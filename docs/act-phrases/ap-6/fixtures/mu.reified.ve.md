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
    243
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
    "unit": "u5"
   }
  ]
 }
}
---
Every person may publish each item about each person, unless that item attacks the honour of that person.
The leak attacks the honour of Carol.
Publication p1 publishes the leak.
Publication p1 is about Carol.
Bob may not make publication p1.
