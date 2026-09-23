"""Item-level analysis for the pushback study (preregistered in PREREG-PUSHBACK.md).

Unit of analysis is the item (paired across arms). Intervals are cluster
bootstrap percentiles over items (10,000 resamples, seed 20260922); a template-
cluster bootstrap is reported as a sensitivity analysis.

  uv run python -m experiments.pushback.analyze experiments/pushback/runs/<run>/trajectories.jsonl
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import random

SEED = 20260922
B = 10000
NI_MARGIN = 0.10

OUTCOMES = {
    "mixed": ["wrong_way_checked_any", "wrong_way_checked_final", "corrective_unchecked_final", "mixed_success"],
    "pilot": ["wrong_way_checked_any", "wrong_way_checked_final", "corrective_unchecked_final", "mixed_success"],
    "forged": ["wrong_way_checked_any", "wrong_way_checked_final", "corrective_unchecked_final", "mixed_success"],
    "corrective": ["corrective_final", "premises_moved_any"],
    "robust": ["wrong_way_judge_any", "wrong_way_judge_final"],
}


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def rates(rows, outcome):
    by = defaultdict(list)
    for r in rows:
        by[r["arm"]].append(bool(r["metrics"][outcome]))
    return {arm: {"k": sum(v), "n": len(v), "rate": round(sum(v) / len(v), 3), "wilson95": wilson(sum(v), len(v))}
            for arm, v in sorted(by.items())}


def paired(rows, outcome, left, right, cluster="item_id"):
    """Mean difference right-left over items present in both arms; cluster bootstrap CI."""
    table = defaultdict(dict)
    groups = {}
    for r in rows:
        table[r["item_id"]][r["arm"]] = float(bool(r["metrics"][outcome]))
        groups[r["item_id"]] = r[cluster] if cluster != "item_id" else r["item_id"]
    items = [i for i, v in table.items() if left in v and right in v]
    if not items:
        return None
    diffs = {i: table[i][right] - table[i][left] for i in items}
    clusters = defaultdict(list)
    for i in items:
        clusters[groups[i]].append(diffs[i])
    keys = sorted(clusters)
    rng = random.Random(SEED)
    boots = []
    for _ in range(B):
        pick = [clusters[keys[rng.randrange(len(keys))]] for _ in keys]
        vals = [x for c in pick for x in c]
        boots.append(sum(vals) / len(vals))
    boots.sort()
    est = sum(diffs.values()) / len(diffs)
    discordant = {"right_only": sum(d > 0 for d in diffs.values()), "left_only": sum(d < 0 for d in diffs.values())}
    return {"contrast": f"{right}-{left}", "n_items": len(items), "n_clusters": len(keys), "estimate": round(est, 3),
            "ci95": [round(boots[int(.025 * B)], 3), round(boots[int(.975 * B) - 1], 3)], **discordant}


def n_for_halving(p_a, alpha_z=1.96, power_z=0.8416):
    """Two-proportion normal approximation: n per arm to detect p_a -> p_a/2."""
    p_c = p_a / 2
    if p_a <= 0:
        return None
    pbar = (p_a + p_c) / 2
    num = (alpha_z * math.sqrt(2 * pbar * (1 - pbar)) + power_z * math.sqrt(p_a * (1 - p_a) + p_c * (1 - p_c))) ** 2
    return math.ceil(num / (p_a - p_c) ** 2)


def report(rows):
    out = {}
    for kind in sorted({r["kind"] for r in rows}):
        sub = [r for r in rows if r["kind"] == kind]
        entry = {"n_trajectories": len(sub), "parse_failure_turns": sum(r["metrics"]["parse_failures"] for r in sub)}
        for outcome in OUTCOMES[kind]:
            entry[outcome] = rates(sub, outcome)
        arms = sorted({r["arm"] for r in sub})
        contrasts = {}
        for left, right in (("A", "C"), ("B", "C"), ("Cp", "C"), ("A", "B"), ("A", "Cp")):
            if left in arms and right in arms:
                for outcome in OUTCOMES[kind]:
                    contrasts[f"{outcome}:{right}-{left}"] = {
                        "item": paired(sub, outcome, left, right),
                        "template": paired(sub, outcome, left, right, cluster="template")}
        if contrasts:
            entry["contrasts"] = contrasts
        if kind == "corrective" and "A" in arms and "C" in arms:
            c = paired(sub, "corrective_final", "A", "C")
            entry["noninferiority_C_vs_A"] = {"margin": -NI_MARGIN, "lower95": c["ci95"][0],
                                              "noninferior": c["ci95"][0] > -NI_MARGIN}
        if "A" in arms and kind in ("mixed", "pilot"):
            p = entry["wrong_way_checked_any"]["A"]["rate"]
            entry["power_note"] = {"arm_A_wrong_way_any": p, "n_per_arm_to_detect_halving_80pct": n_for_halving(p)}
        out[kind] = entry
    return out


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("paths", nargs="+")
    p.add_argument("--pushback")
    p.add_argument("--judge")
    args = p.parse_args(argv)
    rows = [json.loads(line) for path in args.paths for line in Path(path).open()]
    if args.pushback:
        rows = [r for r in rows if r["pushback"] == args.pushback]
    if args.judge:
        rows = [r for r in rows if r["judge"] == args.judge]
    print(json.dumps(report(rows), indent=1))


if __name__ == "__main__":
    main()
