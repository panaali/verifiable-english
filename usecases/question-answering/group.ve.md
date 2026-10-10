---
{
  "format": "ve-document@1",
  "environment": {
    "language": "ve.core@0.2",
    "profiles": [
      "documents@1",
      "relational-fol@0"
    ],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
      "sorts": {
        "member": {
          "description": "a member of the group",
          "verbalisation": {
            "singular": "member",
            "plural": "members"
          }
        }
      },
      "predicates": {
        "registered": {
          "arguments": [
            "member"
          ],
          "description": "whether the member is registered",
          "verbalisation": "{0} is registered"
        },
        "eligible": {
          "arguments": [
            "member"
          ],
          "description": "whether the member is eligible",
          "verbalisation": "{0} is eligible"
        },
        "verified": {
          "arguments": [
            "member"
          ],
          "description": "whether the member is verified",
          "verbalisation": "{0} is verified"
        }
      },
      "constants": {
        "ann": {
          "sort": "member",
          "description": "Ann"
        },
        "bo": {
          "sort": "member",
          "description": "Bo"
        }
      }
    }
  },
  "units": [
    {
      "id": "g1",
      "span": [
        0,
        28
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "none",
      "surface": "english",
      "content": {
        "fence": "g1"
      }
    },
    {
      "id": "g2",
      "span": [
        28,
        72
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "none",
      "surface": "english",
      "content": {
        "fence": "g2"
      }
    },
    {
      "id": "g3",
      "span": [
        72,
        89
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "none",
      "surface": "english",
      "content": {
        "fence": "g3"
      }
    }
  ]
}
---
Every member is registered.
Every member who is registered is eligible.
Ann is verified.
```ve g1
Every member is registered.
```
```ve g2
Every member who is registered is eligible.
```
```ve g3
Ann is verified.
```
