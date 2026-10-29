#!/usr/bin/env python3
"""JT-E3 agreement and instrument sensitivity; no model calls."""
from __future__ import annotations

import csv
from fractions import Fraction
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REF = "64339b6ce"
CLASSES = ["attitude", "classification", "exception", "judgment", "proportion"]
PILOTS = Path("/home/seyran/code/manage-agents/pilots")


def from_ref(path):
    return subprocess.check_output(["git", "show", f"{REF}:{path}"], text=True)


def kappa(table):
    labels = list(table)
    assert all(set(table[a]) == set(labels) for a in labels)
    n = sum(sum(row.values()) for row in table.values())
    if not n:
        raise ValueError("empty confusion table")
    po = Fraction(sum(table[a][a] for a in labels), n)
    pe = Fraction(sum(sum(table[a].values()) * sum(table[b][a] for b in labels)
                      for a in labels), n * n)
    if pe == 1:
        raise ValueError("kappa undefined when expected agreement is one")
    return po, pe, (po - pe) / (1 - pe)


def frame():
    rows = list(csv.DictReader(from_ref("research/judgment-terms/open_term_class.tsv").splitlines(), delimiter="\t"))
    assert len(rows) == 91
    return {(r["pilot"], r["term"]): r for r in rows}


def ledger(pilot):
    if pilot == "constitution":
        path = PILOTS / "claude-constitution/run-20261012T1800Z/units.json"
        return json.loads(path.read_text())
    if pilot == "udhr":
        path = PILOTS / "udhr/run-20261012T1800Z/units.json"
        return json.loads(path.read_text())["units"]
    return json.loads(from_ref("research/judgment-terms/run-jt0p/units.json"))["units"]


def count_units(units, pilot, classes, excluded, without_borderline):
    n = size = 0
    for unit in units:
        terms = unit.get("open_terms") or []
        kept = [t for t in terms if (pilot, t) in classes
                and classes[(pilot, t)]["class"] == "judgment"
                and t not in excluded
                and not (without_borderline and classes[(pilot, t)]["borderline"] == "yes")]
        if kept:
            n += 1
            size += unit["span"][1] - unit["span"][0]
    return {"units": n, "bytes": size}


def analyze(claude, codex):
    sample = list(csv.DictReader((HERE / "SAMPLE.tsv").open(), delimiter="\t"))
    ids = [f'{r["pilot"]}:{r["term"]}' for r in sample]
    assert [x["id"] for x in claude] == ids
    assert [x["id"] for x in codex] == ids
    table = {a: {b: 0 for b in CLASSES} for a in CLASSES}
    disagree = {r["term"] for r, a, b in zip(sample, claude, codex, strict=True)
                if a["class"] != b["class"]}
    for a, b in zip(claude, codex, strict=True):
        table[a["class"]][b["class"]] += 1
    po, pe, kap = kappa(table)
    classes = frame()
    counts = {}
    for pilot in ("udhr", "udhr_jt0p", "constitution"):
        units = ledger(pilot)
        frame_pilot = "constitution" if pilot == "constitution" else "udhr"
        counts[pilot] = {
            f'disagree_{d}_borderline_{b}': count_units(
                units, frame_pilot, classes, disagree if d == "excluded" else set(), b == "excluded")
            for d in ("included", "excluded") for b in ("included", "excluded")
        }
    assert counts["udhr"]["disagree_included_borderline_included"] == {"units": 18, "bytes": 1945}
    assert counts["udhr_jt0p"]["disagree_included_borderline_included"] == {"units": 20, "bytes": 2143}
    assert counts["constitution"]["disagree_included_borderline_included"] == {"units": 507, "bytes": 88989}
    return {"table": table, "n": 60, "observed": str(po), "expected": str(pe),
            "kappa": str(kap), "kappa_decimal": round(float(kap), 6),
            "verdict": "PASS" if kap >= Fraction(7, 10) else "FAIL",
            "disagree_terms": sorted(disagree), "counts": counts}


def main():
    from runner import parse_answer
    claude = parse_answer((HERE / "claude.json").read_text())
    codex = parse_answer((HERE / "codex.json").read_text())
    result = analyze(claude, codex)
    (HERE / "RESULTS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f'{result["verdict"]}: kappa {result["kappa_decimal"]}; disagreements {len(result["disagree_terms"])}')


if __name__ == "__main__":
    main()
