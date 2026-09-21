"""Recompute planning uncertainty from current, complete dev b-a BAD trials.

No model calls. Refuses scored data and stale prompt hashes. Aggregate approval
counts alone cannot recover the variance of paired template contrasts.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from statistics import mean, stdev

from experiments.cluster_stats import cluster_t, planning_power
from experiments.trial_analysis import read_jsonl, paired_effects
from .materials import HERE, DIFFICULTIES, INSTRUCTIONS, render_cell


def calibrate(trials, items, *, judge, difficulty, style, samples=1, clusters=24):
    if any(trial.get("split") != "dev" for trial in trials):
        raise ValueError("Power calibration accepts dev trials only")
    if difficulty not in DIFFICULTIES or style not in INSTRUCTIONS:
        raise ValueError("Unknown difficulty/style")
    known = {item["id"] for item in items if item["split"] == "dev"}
    if any(trial["item_id"] not in known for trial in trials):
        raise ValueError("Trials contain unknown dev item IDs")
    endpoint = [item for item in items if item["split"] == "dev" and item["label"] == "bad"
                and item["payload"]["_audit"]["stratum"] == "primary"
                and item["payload"]["_audit"]["difficulty"] == difficulty]
    def prompt_hash(item, condition):
        cell, instruction = condition.split("_", 1)
        return hashlib.sha256(render_cell(item, cell, instruction).encode()).hexdigest()[:16]
    effects, assignment = paired_effects(trials, endpoint, judge=judge,
        conditions=(f"a_{style}", f"b_{style}"), samples=samples, prompt_hash=prompt_hash)
    groups = defaultdict(list)
    for template, effect in effects:
        groups[template].append(effect)
    means = {template: mean(values) for template, values in sorted(groups.items())}
    if len(means) < 2:
        raise ValueError("At least two dev template clusters are required")
    result = planning_power(clusters, dev_template_sd=stdev(means.values()), dev_clusters=len(means))
    result.update(judge=judge, difficulty=difficulty, instruction_style=style, contrast="b-a",
                  endpoint="BAD grounding / valid deductions", assignment=assignment,
                  dev_template_means=means, observed_dev_interval=cluster_t(effects), model_calls=0)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trials", type=Path)
    parser.add_argument("--judge", required=True)
    parser.add_argument("--difficulty", choices=DIFFICULTIES, required=True)
    parser.add_argument("--style", choices=INSTRUCTIONS, required=True)
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument("--clusters", type=int, default=24)
    parser.add_argument("--output", type=Path, default=HERE / "power.json")
    args = parser.parse_args()
    materials = HERE / "dev.jsonl.gz"
    result = calibrate(read_jsonl(args.trials), read_jsonl(materials), judge=args.judge,
        difficulty=args.difficulty, style=args.style, samples=args.samples, clusters=args.clusters)
    result["inputs"] = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in (args.trials, materials)}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
