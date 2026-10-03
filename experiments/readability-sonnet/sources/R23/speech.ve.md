---
{
 "format": "ve-document@2",
 "environment": {
  "language": "ve.core@0.2",
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "speech_acts": {
   "task": "t1",
   "definites": {
    "the token": "token1",
    "the desk": "desk1",
    "the writing desk": "desk1"
   }
  },
  "profiles": [
   "norms@0",
   "relational-fol@0",
   "speech-acts@0"
  ],
  "vocabulary": {
   "sorts": {
    "user": {
     "description": "user"
    },
    "control": {
     "description": "control"
    },
    "token": {
     "description": "token"
    },
    "desk": {
     "description": "desk"
    },
    "service": {
     "description": "service"
    },
    "thing": {
     "description": "thing"
    },
    "query": {
     "description": "query"
    }
   },
   "predicates": {
    "reviewed": {
     "arguments": [
      "service"
     ],
     "description": "reviewed",
     "verbalisation": "{0} is reviewed"
    },
    "cat": {
     "arguments": [
      "thing"
     ],
     "description": "cat",
     "verbalisation": "{0} is a cat"
    },
    "animal": {
     "arguments": [
      "thing"
     ],
     "description": "animal",
     "verbalisation": "{0} is an animal"
    },
    "disabled": {
     "arguments": [
      "control"
     ],
     "description": "disabled"
    },
    "done_click": {
     "arguments": [
      "user",
      "control"
     ],
     "description": "done_click"
    },
    "done_open": {
     "arguments": [
      "user",
      "desk"
     ],
     "description": "done_open"
    },
    "done_submit": {
     "arguments": [
      "user",
      "query"
     ],
     "description": "done_submit"
    },
    "click_required": {
     "arguments": [
      "user",
      "control"
     ],
     "description": "click_required",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} click {1}",
      "permission": "click_permitted"
     }
    },
    "click_permitted": {
     "arguments": [
      "user",
      "control"
     ],
     "description": "click_permitted",
     "regulated": {
      "role": "permission",
      "default": "allow",
      "act": "{0} click {1}"
     }
    },
    "share_permitted": {
     "arguments": [
      "user",
      "token"
     ],
     "description": "share_permitted",
     "regulated": {
      "role": "permission",
      "default": "allow",
      "act": "{0} share {1}"
     }
    },
    "submit_required": {
     "arguments": [
      "user",
      "query"
     ],
     "description": "submit_required",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} submit a proof of {1}",
      "permission": "submit_permitted"
     }
    },
    "submit_permitted": {
     "arguments": [
      "user",
      "query"
     ],
     "description": "submit_permitted",
     "regulated": {
      "role": "permission",
      "default": "allow",
      "act": "{0} submit a proof of {1}"
     }
    },
    "open_required": {
     "arguments": [
      "user",
      "desk"
     ],
     "description": "open_required",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} open {1}",
      "permission": "open_permitted"
     }
    },
    "open_permitted": {
     "arguments": [
      "user",
      "desk"
     ],
     "description": "open_permitted",
     "regulated": {
      "role": "permission",
      "default": "allow",
      "act": "{0} open {1}"
     }
    }
   },
   "constants": {
    "alice": {
     "sort": "user",
     "description": "alice"
    },
    "check": {
     "sort": "control",
     "description": "check"
    },
    "token1": {
     "sort": "token",
     "description": "token1"
    },
    "desk1": {
     "sort": "desk",
     "description": "desk1"
    },
    "atlas": {
     "sort": "service",
     "description": "atlas"
    },
    "beacon": {
     "sort": "service",
     "description": "beacon"
    },
    "tom": {
     "sort": "thing",
     "description": "tom"
    },
    "q1": {
     "sort": "query",
     "description": "q1"
    }
   }
  }
 },
 "units": [
  {
   "id": "u1",
   "span": [
    0,
    28
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "none",
   "content": {
    "ast": [
     "unary",
     "cat",
     [
      "const",
      "tom"
     ]
    ]
   }
  },
  {
   "id": "u2",
   "span": [
    28,
    95
   ],
   "kind": "asserted",
   "meaning": "specified",
   "support": "none",
   "content": {
    "ast": [
     "forall",
     "thing",
     [
      "implies",
      [
       "unary",
       "cat",
       [
        "var",
        0
       ]
      ],
      [
       "unary",
       "animal",
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
   "id": "u3",
   "span": [
    95,
    166
   ],
   "kind": "question",
   "meaning": "specified",
   "support": "none",
   "content": {
    "question": {
     "mode": "follows",
     "query": "q1"
    }
   }
  }
 ],
 "queries": [
  {
   "id": "q1",
   "premises": [
    "u1",
    "u2"
   ],
   "target": {
    "ast": [
     "unary",
     "animal",
     [
      "const",
      "tom"
     ]
    ]
   }
  }
 ]
}
---
Tom is classified as "cat".
Every thing that is classified as "cat" is classified as "animal".
Does it follow from these premises that tom is classified as "animal"?
