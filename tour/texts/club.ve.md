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
          "description": "a member",
          "verbalisation": {
            "singular": "member",
            "plural": "members"
          }
        }
      },
      "predicates": {
        "active": {
          "arguments": [
            "member"
          ],
          "description": "whether the member is active",
          "verbalisation": "{0} is active"
        },
        "eligible": {
          "arguments": [
            "member"
          ],
          "description": "whether the member is eligible",
          "verbalisation": "{0} is eligible"
        },
        "junior": {
          "arguments": [
            "member"
          ],
          "description": "whether the member is junior",
          "verbalisation": "{0} is junior"
        },
        "supervised": {
          "arguments": [
            "member"
          ],
          "description": "whether the member is supervised",
          "verbalisation": "{0} is supervised"
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
      "id": "c1",
      "span": [
        0,
        40
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "none",
      "surface": "english",
      "content": {
        "fence": "c1"
      }
    },
    {
      "id": "c2",
      "span": [
        40,
        82
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "none",
      "surface": "english",
      "content": {
        "fence": "c2"
      }
    },
    {
      "id": "c3",
      "span": [
        82,
        97
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "none",
      "surface": "english",
      "content": {
        "fence": "c3"
      }
    },
    {
      "id": "c4",
      "span": [
        97,
        111
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "none",
      "surface": "english",
      "content": {
        "fence": "c4"
      }
    }
  ]
}
---
Every member who is active is eligible.
Every member who is junior is supervised.
Ann is active.
Bo is junior.
```ve c1
Every member who is active is eligible.
```
```ve c2
Every member who is junior is supervised.
```
```ve c3
Ann is active.
```
```ve c4
Bo is junior.
```
