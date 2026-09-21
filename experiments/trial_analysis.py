"""Offline complete paired assignment checks and conservative endpoint scoring."""
from collections import Counter
import gzip
import json


def read_jsonl(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def paired_effects(trials, items, *, judge, conditions, samples=1, prompt_hash=None):
    """Return condition[1] - condition[0], clustered by hidden TEMPLATE.

    `items` is the complete preregistered endpoint inventory. Missing, duplicated
    or extra samples abort; recorded failures stay in their assigned denominator.
    Item/vocabulary group IDs are never treated as independent clusters.
    """
    if samples < 1 or len(conditions) != 2 or conditions[0] == conditions[1]:
        raise ValueError("Require positive samples and two distinct conditions")
    inventory = {item["id"]: item for item in items}
    if not inventory or len(inventory) != len(items):
        raise ValueError("Require nonempty, unique endpoint inventory")
    selected, failures = {}, Counter()
    for trial in trials:
        if trial["judge"] != judge or trial["condition"] not in conditions:
            continue
        if trial["item_id"] not in inventory:
            continue  # Other registered endpoints may share the trials file.
        item = inventory[trial["item_id"]]
        if any(trial.get(key) != item[key] for key in ("label", "split", "group")):
            raise ValueError("Trial metadata does not match frozen item")
        if type(trial.get("sample")) is not int or not 0 <= trial["sample"] < samples:
            raise ValueError("Unexpected sample index")
        key = (item["id"], trial["sample"], trial["condition"])
        if key in selected:
            raise ValueError("Duplicate trial assignment")
        if prompt_hash and trial.get("prompt_sha") != prompt_hash(item, trial["condition"]):
            raise ValueError("Trial prompt hash does not match current materials")
        failed = (trial.get("ok") is not True or bool(trial.get("error"))
                  or bool(trial.get("parse_error")) or bool(trial.get("tool_events"))
                  or type(trial.get("approved")) is not bool)
        selected[key] = int(item["label"] == "bad") if failed else int(trial["approved"])
        failures[trial["condition"]] += failed
    expected = {(item_id, sample, condition) for item_id in inventory
                for sample in range(samples) for condition in conditions}
    if set(selected) != expected:
        raise ValueError(f"Incomplete paired assignment: missing {len(expected - set(selected))} trials")
    effects = [(item["payload"]["_audit"]["template"],
                selected[item_id, sample, conditions[1]] - selected[item_id, sample, conditions[0]])
               for item_id, item in inventory.items() for sample in range(samples)]
    return effects, {"items": len(items), "samples": samples, "assigned_trials": len(expected),
                     "failures": {condition: failures[condition] for condition in conditions}}
