"""fsf-r1: every unit's status on Oct 1 and today, its answer-key agreement, and the remaining gaps by feature.

    python usecases/safety-framework/measure_r1.py [--check]

Reads saved files only: `spans.json`, `coverage.json`, `results.json` and `readings/results.json` (from `readings_r1.py`)
here, and the Oct 1 `spans.json` and `coverage.json` saved in `docs/usecases/safety-framework/fsf-r1/oct1/`
(main's copies at 93131f96, last changed by 2a5bd3fe on 2026-10-01). It writes `units.json` and `gaps.json` beside
the Oct 1 copies. `--check` fails if either would change.

A unit's items are the answer-key items whose deciding rules (the `rules` of any choice in results.json) include a
rule of the unit; a unit routed to D2 or D3 has the S or D items. Premises bear on every item and get none.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_document as B  # noqa: E402

EVIDENCE = HERE.parents[1] / "docs" / "usecases" / "safety-framework" / "fsf-r1"

# The feature each blocker waits for (feature plan 2026-10-18 names). An OPEN unit's open term is a judgment term
# (JT); an UNFORMALISED unit's reason maps as below; a LABELLED unit's kind is a feature or no claim to check.
UNFORMALISED_FEATURES = {
    "external_reference": "external references",
    "event_order": "process and deadline wording", "no_deadline_or_trigger": "process and deadline wording",
    "no_trigger_stated": "process and deadline wording", "iterative_process": "process and deadline wording",
    "process_description": "process and deadline wording", "unspecified_process": "process and deadline wording",
    "as_appropriate": "judgment terms", "where_appropriate": "judgment terms", "degree_term": "judgment terms",
    "aim_without_force": "attitudes (aims)", "may_be_adjusted": "defeasible (stated adjustments)",
    "addressed_to_the_field": "addressee (a recommendation to the field)",
}
LABELLED_FEATURES = {"hedged": "modality (may, could)", "attributed": "attitudes (beliefs, expectations)",
                     "causal": "causation"}
NO_CLAIM = "no claim to check (layout, exposition, definitions, examples)"


def load(path):
    return json.loads(path.read_text())


def item_rules(node, found=None):
    """Every rule id named in a `rules` list anywhere in one item's result."""
    found = set() if found is None else found
    if type(node) is dict:
        for key, value in node.items():
            if key == "rules" and type(value) is list:
                found.update(v for v in value if type(v) is str)
            else:
                item_rules(value, found)
    elif type(node) is list:
        for value in node:
            item_rules(value, found)
    return found


def unit_rules(record):
    rules = {record[k] for k in ("rule", "restates") if k in record}
    for readings in B.READINGS.get(record.get("reading_set"), (None, {}))[1].values():
        rules.update(part for rule in readings for part in rule.split(" or "))
    return rules


def blockers(record, readings):
    """The features a unit that is not CHECKED waits for; [] for a CHECKED unit."""
    status = record["status"]
    if status == "CHECKED":
        return []
    if status == "UNFORMALISED":
        return [UNFORMALISED_FEATURES[record["reason"]]]
    if status == "LABELLED":
        return [LABELLED_FEATURES.get(record["kind"], NO_CLAIM)]
    found = ["judgment terms"] if record.get("open_terms") else []
    if "reading_set" in record:
        found.append("two readings kept: VE decides each (fsf-r1)" if readings[record["reading_set"]]["content"]
                     else "readings: a reading with no rule or several rules")
    return found or ["unknown"]


def measure():
    spans = load(HERE / "spans.json")["units"]
    oct1 = {u["id"]: u["status"] for u in load(EVIDENCE / "oct1" / "spans.json")["units"]}
    results = load(HERE / "results.json")
    readings = load(HERE / "readings" / "results.json")["sets"]
    rows = {r["id"]: r for r in results["comparison"]}
    by_rule = {}
    for item_id, item in results["items"].items():
        for rule in item_rules(item):
            by_rule.setdefault(rule, set()).add(item_id)
    families = {"D2": "S", "D3": "D"}
    units, attributed = [], set()
    for record in spans:
        items = set().union(*(by_rule.get(r, set()) for r in unit_rules(record)))
        if "routed" in record:
            items |= {i for i in rows if i[0] == families[record["routed"]["document"]]}
        items &= set(rows)
        units.append({"id": record["id"], "bytes": record["span"][1] - record["span"][0],
                      "status_oct1": oct1[record["id"]], "status": record["status"],
                      "blockers": blockers(record, readings),
                      **({"reading_content": True} if record.get("reading_content") else {}),
                      "items": len(items), "items_agree": sum(rows[i]["agree"] for i in items),
                      "items_disagree": sorted(i for i in items if not rows[i]["agree"])})
        attributed |= items
    # Items no unit's rule decides: the silences (no rule selects) and the answers about the whole document.
    rest = sorted(set(rows) - attributed)
    return units, {"items": len(rest), "items_agree": sum(rows[i]["agree"] for i in rest),
                   "items_disagree": [i for i in rest if not rows[i]["agree"]],
                   "answer_key": {"items": len(rows), "agree": sum(r["agree"] for r in rows.values())}}


def gaps(units, unattributed):
    statuses, features = {}, {}
    for u in units:
        statuses[u["status"]] = statuses.get(u["status"], 0) + u["bytes"]
    for u in units:
        for feature in u["blockers"]:
            entry = features.setdefault(feature, {"units": 0, "bytes": 0, "sole_units": 0, "sole_bytes": 0,
                                                  "statuses": {}})
            entry["units"] += 1
            entry["bytes"] += u["bytes"]
            entry["statuses"][u["status"]] = entry["statuses"].get(u["status"], 0) + u["bytes"]
            if len(u["blockers"]) == 1:
                entry["sole_units"] += 1
                entry["sole_bytes"] += u["bytes"]
    coverage = load(HERE / "coverage.json")
    return {"source_bytes": coverage["source_bytes"],
            "master_bytes_by_status": {"oct1": load(EVIDENCE / "oct1" / "coverage.json")["master_bytes_by_status"],
                                       "today": coverage["master_bytes_by_status"]},
            "units_changed_status": [u["id"] for u in units if u["status"] != u["status_oct1"]],
            "items_without_unit": unattributed,
            "status_bytes_recomputed": statuses,
            "features": dict(sorted(features.items(), key=lambda kv: -kv[1]["bytes"]))}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    units, unattributed = measure()
    out = {"units.json": {"units": units}, "gaps.json": gaps(units, unattributed)}
    for name, data in out.items():
        text = json.dumps(data, indent=1, sort_keys=True) + "\n"
        if args.check:
            if (EVIDENCE / name).read_text() != text:
                raise SystemExit(f"{name} is out of date")
        else:
            (EVIDENCE / name).write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
