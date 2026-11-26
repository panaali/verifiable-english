"""Write the tour's small documents (tour/texts/*.ve.md) from their sentences and word lists.

Each document is ordinary English sentences that VE reads exactly as written: the sentences ARE the rules, so there
is no separate translation to check. Run: uv run python tour/texts/build_texts.py (the test checks the files match).
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def environment(sort, singular, plural, predicates, people):
    return {
        "language": "ve.core@0.2",
        "profiles": ["documents@1", "relational-fol@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {
            "sorts": {sort: {"description": f"a {singular}",
                             "verbalisation": {"singular": singular, "plural": plural}}},
            "predicates": {name: {"arguments": [sort], "description": f"whether the {singular} {wording}",
                                  "verbalisation": "{0} " + wording}
                           for name, wording in predicates},
            "constants": {key: {"sort": sort, "description": name} for key, name in people},
        },
    }


TEXTS = {
    "club": (
        ("Every member who is active is eligible.\n",
         "No member who is suspended is eligible.\n",
         "Ann is active.\n",
         "Bo is suspended.\n",
         "Cy is junior.\n"),
        environment("member", "member", "members",
                    [("active", "is active"), ("eligible", "is eligible"), ("suspended", "is suspended"),
                     ("junior", "is junior")],
                    [("ann", "Ann"), ("bo", "Bo"), ("cy", "Cy")]),
    ),
}


def build(sentences, env, prefix) -> str:
    offset, units = 0, []
    for index, sentence in enumerate(sentences, 1):
        end = offset + len(sentence.encode("utf-8"))
        uid = f"{prefix}{index}"
        units.append({"id": uid, "span": [offset, end], "status": "CHECKED", "kind": "asserted",
                      "meaning": "specified", "support": "none", "surface": "english", "content": {"fence": uid}})
        offset = end
    meta = {"format": "ve-document@1", "environment": env, "units": units}
    fences = "".join(f"```ve {prefix}{i}\n{s}```\n" for i, s in enumerate(sentences, 1))
    return "---\n" + json.dumps(meta, indent=2, ensure_ascii=False) + "\n---\n" + "".join(sentences) + fences


def documents():
    return {f"{name}.ve.md": build(sentences, env, name[0]) for name, (sentences, env) in TEXTS.items()}


if __name__ == "__main__":
    for name, text in documents().items():
        (HERE / name).write_text(text, encoding="utf-8")
