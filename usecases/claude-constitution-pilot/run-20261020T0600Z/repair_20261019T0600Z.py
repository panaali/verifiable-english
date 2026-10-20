#!/usr/bin/env python3
"""Run 20261019T0600Z, audit repair of 20261018T1800Z (u0042.presupposition UNFAITHFUL; u0043.s02.p2 flagged for the same cause).

The audit found the content of QT-0p exact but its English the quoted fallback `Y1 is classified as "claude_principal_type"` (the lint refuses
"is one of Claude's types of principals"). Repair: the sort `principal_type` gets the noun "principal type of Claude" (it held "type of principal"; sort nouns of the form "<noun> of Claude" are admitted: "instance of Claude"
already is), so the sort holds Claude's types of principals and the unary predicate `claude_principal_type` is removed with every trace. The closure is still over Claude's types only
(the sort holds Claude's types, never "all principal types"); the sort and the three constants keep their names (a sort named `claude_principal_type` collides with `claude_instance`
in the variable names of the situation texts: "claude_instance is an instance of Claude").

    uv run python .../repair_20261019T0600Z.py          # edits translation-without-content.ve.md in place; refuses a second run
"""
from __future__ import annotations
import json, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
TARGET = RUN / "translation-without-content.ve.md"
SPLIT = b"---\n"
OLD = NEW = "principal_type"
SORT = {"description": "A type of principal that is Claude's, in the source's sense (u0042, u0043.s02): a kind of party whose instructions Claude gives weight to, counted among Claude's own types "
                       "of principals. The sort holds Claude's types only; it says nothing about other principals' types.",
        "verbalisation": {"singular": "principal type of Claude", "plural": "principal types of Claude"}}




def main():
    raw = TARGET.read_bytes()
    _, front, body = raw.split(SPLIT, 2)
    meta = json.loads(front)
    voc = meta["environment"]["vocabulary"]
    assert "claude_principal_type" in voc["predicates"], "repair already applied"
    voc["sorts"] = {k: (SORT if k == OLD else v) for k, v in voc["sorts"].items()}
    del voc["predicates"]["claude_principal_type"]
    for k in ("anthropic", "operators", "users"):
        assert voc["constants"][k]["sort"] == OLD
        voc["constants"][k]["sort"] = NEW
    c = lambda n: ["const", n]
    # u0042.presupposition: there are three pairwise different Claude principal types, and every one is one of them (de Bruijn: 2, 1, 0 are the three existentials)
    ast42 = ["exists", NEW, ["exists", NEW, ["exists", NEW,
             ["and", ["not", ["eq", ["var", 2], ["var", 1]]],
              ["and", ["not", ["eq", ["var", 2], ["var", 0]]],
               ["and", ["not", ["eq", ["var", 1], ["var", 0]]],
                ["forall", NEW, ["or", ["eq", ["var", 0], ["var", 3]], ["or", ["eq", ["var", 0], ["var", 2]], ["eq", ["var", 0], ["var", 1]]]]]]]]]]]
    ast43 = ["and", ["not", ["eq", c("anthropic"), c("operators")]],
             ["and", ["not", ["eq", c("anthropic"), c("users")]],
              ["and", ["not", ["eq", c("operators"), c("users")]],
               ["forall", NEW, ["or", ["eq", ["var", 0], c("anthropic")], ["or", ["eq", ["var", 0], c("operators")], ["eq", ["var", 0], c("users")]]]]]]]
    done = []
    for u in meta["units"]:
        if u["id"] == "u0042.presupposition":
            assert u["content"]["ast"][0] == "exists"
            u["content"]["ast"] = ast42
            done.append(u["id"])
        elif u["id"] == "u0043.s02":
            p2 = next(p for p in u["parts"] if p["id"] == "u0043.s02.p2")
            p2["content"]["ast"] = ast43
            done.append(p2["id"])
    assert done == ["u0042.presupposition", "u0043.s02.p2"], done
    TARGET.write_bytes(SPLIT + json.dumps(meta, ensure_ascii=False).encode() + b"\n" + SPLIT + body)
    assert b"claude_principal_type" not in json.dumps(voc["predicates"]).encode()
    print("repaired", done)


if __name__ == "__main__":
    main()
