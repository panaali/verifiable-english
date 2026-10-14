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
    "instructs": {
     "arguments": [
      "operator"
     ],
     "description": "{0} instructs",
     "verbalisation": "{0} instructs",
     "regulated": {
      "role": "plain",
      "default": "unspecified"
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
    55
   ],
   "kind": "norm",
   "meaning": "specified",
   "support": "assumption",
   "content": {
    "norm": {
     "name": "g1",
     "predicate": "instructs",
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
Every operator instructs, unless an exception applies.
