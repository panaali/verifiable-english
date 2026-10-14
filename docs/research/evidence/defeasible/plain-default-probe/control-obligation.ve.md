---
{
 "format": "ve-document@1",
 "environment": {
  "language": "ve.core@0.2",
  "profiles": [
   "documents@1",
   "norm-defaults@0",
   "norms@0",
   "relational-fol@0",
   "soft-norms@0"
  ],
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "vocabulary": {
   "sorts": {
    "operator": {
     "description": "an operator",
     "verbalisation": {
      "singular": "operator",
      "plural": "operators"
     }
    }
   },
   "predicates": {
    "instruct_required": {
     "arguments": [
      "operator"
     ],
     "description": "{0} is required to instruct",
     "regulated": {
      "role": "obligation",
      "default": "unspecified",
      "act": "{0} instruct",
      "permission": "instruct_permitted"
     }
    },
    "instruct_permitted": {
     "arguments": [
      "operator"
     ],
     "description": "{0} may instruct",
     "regulated": {
      "role": "permission",
      "default": "unspecified",
      "act": "{0} instruct"
     }
    }
   },
   "constants": {}
  }
 },
 "units": [
  {
   "id": "g1",
   "span": [
    0,
    32
   ],
   "kind": "norm",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "norm": {
     "name": "g1",
     "predicate": "instruct_required",
     "sign": true,
     "guard": [
      "top"
     ],
     "unless": [],
     "over": [],
     "mode": "default",
     "exception": {
      "decided_by": "operator",
      "sufficient": [],
      "necessary": [],
      "factors": []
     }
    }
   }
  }
 ]
}
---
Every operator should instruct.
