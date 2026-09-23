"""Independent reference outcomes for P3 items (never imports ``ve``).

Each family is interpreted from its SOURCE artefact by a separate module written
without access to the VE formalisations:

  reference_cedar.py   Cedar policy-language subset interpreter (validated against
                       all 115 decisions recorded by the real Cedar authorizer in
                       the upstream fixtures; see test_reference_cedar.py)
  reference_rbac.py    Kubernetes RBAC authorizer and AWS IAM identity-policy evaluation
  reference_alloy.py   Alloy subset evaluator (parses the verbatim .als text) and a
                       bounded brute-force assertion check

``answer(item, question, world, request) -> bool`` is the single entry point.
"""
from __future__ import annotations

import json


def answer(item: dict, question: dict, world: dict, request: dict | None) -> bool:
    fam = item["family"]
    src = item["sources"]
    if fam == "cedar":
        import reference_cedar
        return reference_cedar.authorize(src["source.cedar"], world.get("linked", []), world["entities"], request)
    if fam == "k8s":
        import reference_rbac
        return reference_rbac.k8s_authorize(world["objects"], request)
    if fam == "iam":
        import reference_rbac
        return reference_rbac.iam_authorize(world["policies"], request)
    if fam == "alloy":
        import reference_alloy
        return reference_alloy.evaluate({k: v for k, v in src.items() if k.endswith(".als")},
                                        question["target"], world)
    raise ValueError(fam)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    for d in sorted((Path(__file__).parent / "items").iterdir()):
        if sys.argv[1:] and d.name not in sys.argv[1:]:
            continue
        item = json.loads((d / "item.json").read_text())
        item["sources"] = {p.name: p.read_text() for p in d.iterdir()
                           if p.name.startswith("source") or p.name in ("relation.als", "linked.json")}
        out = []
        for q in item["questions"]:
            w, r = (q["instance"], None) if item["family"] == "alloy" else (item["world"], q["request"])
            out.append(answer(item, q, w, r))
        print(d.name, "".join("A" if x else "d" for x in out))
