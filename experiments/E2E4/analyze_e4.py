"""Analyze E4 paired approvals with templates, never renamed items, as clusters."""
import argparse
import hashlib
import json
from pathlib import Path

from experiments.cluster_stats import cluster_t
from experiments.trial_analysis import read_jsonl, paired_effects
from .materials import load_frozen


def analyze(trials, items, *, judge, samples=1):
    result = {"judge": judge, "model_calls": 0, "cluster_unit": "structural template",
              "effective_sample_size_note": "Scored K=12 templates, not 60 independent items per label; five vocabulary renamings per template are near-replicates.",
              "endpoints": {}}
    for label in ("bad", "good"):
        endpoint = [item for item in items if item["label"] == label]
        effects, assignment = paired_effects(trials, endpoint, judge=judge, samples=samples,
            conditions=("prose_critique", "checked_countermodel"))
        result["endpoints"][label] = {"contrast": "checked_countermodel - prose_critique",
                                       **cluster_t(effects), **assignment}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trials", type=Path)
    parser.add_argument("--judge", required=True)
    parser.add_argument("--split", choices=("dev", "scored"), default="scored")
    parser.add_argument("--samples", type=int, default=1)
    args = parser.parse_args()
    result = analyze(read_jsonl(args.trials), load_frozen(args.split, "E4"), judge=args.judge, samples=args.samples)
    result["trials_sha256"] = hashlib.sha256(args.trials.read_bytes()).hexdigest()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
