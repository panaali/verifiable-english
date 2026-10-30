---
{
  "format": "ve-document@1",
  "environment": {
    "language": "ve.core@0.2",
    "profiles": [
      "documents@1",
      "norm-defaults@0",
      "norms@0",
      "readings@1",
      "relational-fol@0",
      "soft-norms@0"
    ],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
      "sorts": {
        "assistant": {
          "description": "assistant"
        },
        "user": {
          "description": "user"
        }
      },
      "predicates": {
        "x_required": {
          "arguments": [
            "assistant"
          ],
          "description": "obligation",
          "regulated": {
            "role": "obligation",
            "default": "deny",
            "act": "{0} do x",
            "permission": "x_permitted"
          }
        },
        "x_permitted": {
          "arguments": [
            "assistant"
          ],
          "description": "permission",
          "regulated": {
            "role": "permission",
            "default": "unspecified",
            "act": "{0} do x"
          }
        }
      },
      "constants": {}
    }
  },
  "units": [
    {
      "id": "u1",
      "span": [
        0,
        24
      ],
      "kind": "norm",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "norm": {
          "name": "s",
          "predicate": "x_required",
          "sign": true,
          "guard": [
            "top"
          ],
          "unless": [],
          "over": [],
          "mode": "default",
          "exception": {
            "decided_by": "unstated",
            "sufficient": [],
            "necessary": [],
            "factors": []
          }
        }
      }
    },
    {
      "id": "u2",
      "span": [
        24,
        38
      ],
      "kind": "asserted",
      "meaning": "specified",
      "support": "assumption",
      "content": {
        "ast": [
          "top"
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
          "top"
        ],
        "unit": "u2"
      }
    ]
  }
}
---
Assistants should do x.
This follows.
