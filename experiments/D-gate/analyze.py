"""D gate analysis (PREREG-DRAFT.md). Reads runs/<arm>/answers.jsonl and ground_truth.json.

    python3 experiments/D-gate/analyze.py high [low]

Per sample, an answer is an error if it differs from the reference verifier's answer; UNPARSED
counts as an error; ENDPOINT_ERROR samples are excluded and reported (the prereg's stop rule
applies if they exceed 10%). Item error = mean over its samples. Primary statistic: mean item error
over all decided items; 95% CI by cluster bootstrap over artefacts (10,000 resamples, seed 0).
Gate: PASS iff the point estimate >= 0.15.
"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = 0.15


def item_errors(arm, gt):
    per = defaultdict(list)
    excluded = 0
    for line in open(HERE / "runs" / arm / "answers.jsonl"):
        r = json.loads(line)
        if r["answer"] == "ENDPOINT_ERROR":
            excluded += 1
            continue
        if gt.get(r["id"]) in ("YES", "NO"):
            per[r["id"]].append(float(r["answer"] != gt[r["id"]]))
    return {k: sum(v) / len(v) for k, v in per.items()}, excluded


def cluster_boot(err, cluster, n=10000, seed=0):
    rnd = random.Random(seed)
    by = defaultdict(list)
    for k, e in err.items():
        by[cluster[k]].append(e)
    cl = sorted(by)
    stats = []
    for _ in range(n):
        xs = [e for c in (rnd.choice(cl) for _ in cl) for e in by[c]]
        stats.append(sum(xs) / len(xs))
    stats.sort()
    return stats[int(0.025 * n)], stats[int(0.975 * n) - 1]


def summary(err, items, gt, sel=lambda i: True):
    ks = [k for k in err if sel(items[k])]
    if not ks:
        return None
    return dict(n=len(ks), error=round(sum(err[k] for k in ks) / len(ks), 4))


def main():
    gt = {r["id"]: r["answer"] for r in json.loads((HERE / "ground_truth.json").read_text())["items"]}
    items = {i["id"]: i for i in json.loads((HERE / "items.json").read_text())}
    cluster = {k: i["cluster"] for k, i in items.items()}
    report = {}
    for arm in sys.argv[1:] or ["high"]:
        err, excluded = item_errors(arm, gt)
        est = sum(err.values()) / len(err)
        lo, hi = cluster_boot(err, cluster)
        report[arm] = dict(
            items=len(err), clusters=len({cluster[k] for k in err}), endpoint_errors_excluded=excluded,
            error=round(est, 4), ci95_cluster=[round(lo, 4), round(hi, 4)],
            gate="PASS" if est >= GATE else "FAIL (closes this sample only)",
            false_approval_on_NO_items=summary(err, items, gt, lambda i: gt[i["id"]] == "NO"),
            false_rejection_on_YES_items=summary(err, items, gt, lambda i: gt[i["id"]] == "YES"),
            original=summary(err, items, gt, lambda i: i["variant"] == "original"),
            planted_edit=summary(err, items, gt, lambda i: i["variant"] == "planted-edit"),
            cedar=summary(err, items, gt, lambda i: i["family"] == "cedar"),
            k8s=summary(err, items, gt, lambda i: i["family"] == "k8s"),
            excluding_edge_items=summary(err, items, gt, lambda i: not any(t.startswith("edge") for t in i["tags"])),
            by_ve_coverage={c: summary(err, items, gt, lambda i, c=c: i["ve_coverage"]["category"] == c)
                            for c in sorted({i["ve_coverage"]["category"] for i in items.values()})},
            per_item={k: round(v, 3) for k, v in sorted(err.items())})
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
