"""AP-0, exploratory (added after review, not registered): which of the constitution's M3 lines name a predicate that
an act workaround created.

    uv run python research/act-phrases/ap0_m3_atoms.py [RUN_DIR]

For each norm unit that item 3 tagged other than `none` (evidence m4-act-workaround.json), collect every predicate the
unit's rule names (the unit's norm, or every reading of its reading set): guard, `unless` and regulated predicate.
Then count the lines of the committed constitution rendering (m3-rendered/constitution-translation.md) that name one
of them after "classified as" or "has the recorded relation". Reads the pilot run read-only and writes
docs/research/evidence/act-phrases/m3-workaround-atoms.json. No model call, no Lean run.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(sys.argv[1] if len(sys.argv) > 1 else
           "/home/seyran/code/manage-agents/pilots/claude-constitution/run-20261012T1800Z")
EVIDENCE = ROOT / "docs/research/evidence/act-phrases"
OUT = EVIDENCE / "m3-workaround-atoms.json"
NAME = re.compile(r'(?:classified as|has the recorded relation) "([^"]+)"')
PHRASES = ("classified as", "has the recorded relation")


def names(node, preds):
    """Every predicate name occurring anywhere in a JSON rule."""
    if isinstance(node, str):
        return {node} if node in preds else set()
    if isinstance(node, list):
        return set().union(*(names(child, preds) for child in node)) if node else set()
    if isinstance(node, dict):
        return set().union(*(names(child, preds) for child in node.values())) if node else set()
    return set()


def main():
    text = (RUN / "translation.ve.md").read_text()
    end = text.index("\n---\n", 4)
    doc = json.loads(text[4:end])
    preds = doc["environment"]["vocabulary"]["predicates"]
    tags = {r["unit"]: r["act_workaround"] for r in
            json.loads((EVIDENCE / "m4-act-workaround.json").read_text())["units"]}
    by_unit = {}
    for unit in doc["units"]:
        if unit["id"] not in tags or tags[unit["id"]] == "none":
            continue
        rules = [unit["content"]["norm"]] if (unit.get("content") or {}).get("norm") else [
            r["content"]["norm"] for rs in doc["reading_sets"] if rs["unit"] == unit["id"] for r in rs["readings"]]
        by_unit[unit["id"]] = sorted(set().union(*(names(rule, preds) for rule in rules)))
    created = {n: sorted(u for u, ns in by_unit.items() if n in ns) for ns in by_unit.values() for n in ns}
    rendered = (EVIDENCE / "m3-rendered/constitution-translation.md").read_text()
    lines = [ln for ln in rendered.splitlines() if any(p in ln for p in PHRASES)]
    rows = []
    for ln in lines:
        named = sorted(set(NAME.findall(ln)))
        hits = [n for n in named if n in created]
        rows.append({"line": ln.strip()[:240], "named": named, "workaround_predicates": hits,
                     "units": sorted({u for n in hits for u in created[n]})})
    for r in rows:
        r["tags"] = sorted({tags[u] for u in r["units"]})
    hit = [r for r in rows if r["workaround_predicates"]]
    # Groups A and B (pointer, folded) move the act's content into case atoms; a shortened unit's other predicates
    # are its guard's cases and exceptions.
    ab = [r for r in hit if {"pointer", "folded"} & set(r["tags"])]
    result = {"run": str(RUN), "rule": "exploratory, docs/research/act-phrases-phase1.md 3 (added after review)",
              "m3_lines": len(rows), "lines_naming_a_workaround_predicate": len(hit),
              "lines_naming_none": len(rows) - len(hit),
              "lines_naming_a_pointer_or_folded_unit_predicate": len(ab),
              "lines_naming_only_shortened_unit_predicates": len(hit) - len(ab),
              "units_reached": sorted({u for r in hit for u in r["units"]}),
              "predicates_by_unit": by_unit, "lines": rows}
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: result[k] for k in ("m3_lines", "lines_naming_a_workaround_predicate",
                                             "lines_naming_none", "lines_naming_a_pointer_or_folded_unit_predicate",
                                             "lines_naming_only_shortened_unit_predicates", "units_reached")}))
    for r in rows:
        print("*" if r["workaround_predicates"] else " ", r["tags"], r["units"], r["named"])


if __name__ == "__main__":
    main()
