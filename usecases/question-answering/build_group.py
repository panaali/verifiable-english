"""Regenerate the small, source-bound G fixture in the question-answering spec."""
from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SENTENCES = (
    "Every member is registered.\n",
    "Every member who is registered is eligible.\n",
    "Ann is verified.\n",
)
ENVIRONMENT = {
    "language": "ve.core@0.2",
    "profiles": ["documents@1", "relational-fol@0"],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
        "sorts": {"member": {"description": "a member of the group", "verbalisation":
                              {"singular": "member", "plural": "members"}}},
        "predicates": {
            name: {"arguments": ["member"], "description": f"whether the member is {name}",
                   "verbalisation": "{0} is " + name}
            for name in ("registered", "eligible", "verified")
        },
        "constants": {
            "ann": {"sort": "member", "description": "Ann"},
            "bo": {"sort": "member", "description": "Bo"},
        },
    },
}


def build() -> str:
    offset = 0
    units = []
    for index, sentence in enumerate(SENTENCES, 1):
        end = offset + len(sentence.encode("utf-8"))
        uid = f"g{index}"
        units.append({"id": uid, "span": [offset, end], "status": "CHECKED",
                      "kind": "asserted", "meaning": "specified", "support": "none",
                      "surface": "english", "content": {"fence": uid}})
        offset = end
    meta = {"format": "ve-document@1", "environment": ENVIRONMENT, "units": units}
    fences = "".join(f"```ve g{i}\n{sentence}```\n" for i, sentence in enumerate(SENTENCES, 1))
    return "---\n" + json.dumps(meta, indent=2, ensure_ascii=False) + "\n---\n" + "".join(SENTENCES) + fences


if __name__ == "__main__":
    (HERE / "group.ve.md").write_text(build())
