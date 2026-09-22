"""Structured-review arm: packets for reviewers who answer from the source alone (no VE).

For each sampled item, write review_packets/<id>.json with the verbatim source, the
world, and 10 questions: the item's own questions plus request variants from the
harness perturbation generator restricted to the item's own world (Cedar/K8s/IAM:
request fields only; Alloy: the item's instances). Answers are hidden; the key is
in review_packets/keys.json (reference answers)."""
import copy, json, random
import harness as H, reference

SAMPLE = ["c05_cit_3a", "c11_cit_4f", "c13_document_cloud", "c17_sales_static", "k05_crontab_default_roles",
          "k07_subresource_wildcard", "w03_mfa_selfmanage", "l07_marksweep_mark"]
out, keys = H.HERE / "review_packets", {}
out.mkdir(exist_ok=True)
for iid in SAMPLE:
    item = H.load_item(iid)
    rng = random.Random(f"review-{iid}")
    qs = [dict(q) for q in item["questions"]][:6]
    if item["family"] != "alloy":
        pool = []
        for p in H.perturbations(item, 400):
            req = p["request"]
            if req not in [q["request"] for q in qs] + pool:
                pool.append(req)
        for req in rng.sample(pool, len(pool)):
            if len(qs) >= 10:
                break
            qs.append({"description": "variant", "request": req})
    packet = {"id": iid, "family": item["family"], "task": item["question"],
              "sources": item["sources"], "world": item.get("world"),
              "questions": [{"n": i, **({"request": q["request"]} if "request" in q else {"target": q["target"], "instance": q["instance"]})}
                            for i, q in enumerate(qs)]}
    (out / f"{iid}.json").write_text(json.dumps(packet, indent=1) + "\n")
    keys[iid] = [H.ref_answer(item, q) if "request" not in q or q.get("recorded_decision") is not None or True else None for q in qs]
(out / "keys.json").write_text(json.dumps(keys, indent=1) + "\n")
print({k: len(v) for k, v in keys.items()})
