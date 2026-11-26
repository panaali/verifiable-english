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
        "suspended": {
          "arguments": [
            "member"
          ],
          "description": "whether the member is suspended",
          "verbalisation": "{0} is suspended"
        },
        "junior": {
          "arguments": [
            "member"
          ],
          "description": "whether the member is junior",
          "verbalisation": "{0} is junior"
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
        },
        "cy": {
          "sort": "member",
          "description": "Cy"
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
        80
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
        80,
        95
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
        95,
        112
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "none",
      "surface": "english",
      "content": {
        "fence": "c4"
      }
    },
    {
      "id": "c5",
      "span": [
        112,
        126
      ],
      "status": "CHECKED",
      "kind": "asserted",
      "meaning": "specified",
      "support": "none",
      "surface": "english",
      "content": {
        "fence": "c5"
      }
    }
  ]
}
---
Every member who is active is eligible.
No member who is suspended is eligible.
Ann is active.
Bo is suspended.
Cy is junior.
```ve c1
Every member who is active is eligible.
```
```ve c2
No member who is suspended is eligible.
```
```ve c3
Ann is active.
```
```ve c4
Bo is suspended.
```
```ve c5
Cy is junior.
```
