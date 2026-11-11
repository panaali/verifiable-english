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
    }
   },
   "predicates": {
    "publish_about_permitted": {
     "arguments": [
      "person",
      "item"
     ],
     "description": "{0} publish {1}",
     "regulated": {
      "role": "permission",
      "default": "deny",
      "act": "{0} publish {1}"
     }
    },
    "attacks_honour_of_someone": {
     "arguments": [
      "item"
     ],
     "description": "{0} attacks the honour of a person",
     "verbalisation": "{0} attacks the honour of a person"
    }
   },
   "constants": {
    "bob": {
     "sort": "person",
     "description": "bob"
    },
    "leak": {
     "sort": "item",
     "description": "leak"
    }
   }
  }
 },
 "units": [
  {
   "id": "u1",
   "span": [
    0,
    85
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
      "not",
      [
       "unary",
       "attacks_honour_of_someone",
       [
        "var",
        0
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
    85,
    126
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "ast": [
     "unary",
     "attacks_honour_of_someone",
     [
      "const",
      "leak"
     ]
    ]
   }
  },
  {
   "id": "u3",
   "span": [
    126,
    156
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
       "leak"
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
       "leak"
      ]
     ]
    ],
    "unit": "u3"
   }
  ]
 }
}
---
Every person may publish each item, unless that item attacks the honour of a person.
The leak attacks the honour of a person.
Bob may not publish the leak.
