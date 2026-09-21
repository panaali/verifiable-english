#!/usr/bin/env python3
"""Generate the E0 coverage tables for the paper from committed data.

Data source: experiments/E0/second_rater_metrics.json at the pinned commit of
branch codex/e0-rater (the same commit that docs/spec/v0.1-coverage.md pins).
The file is read with `git show`, so this script needs the repository but no
checkout of that branch. Output: Markdown tables in paper/generated/.

Usage: python3 paper/figures/gen_e0_tables.py
"""
from __future__ import annotations

import json
import pathlib
import subprocess

E0_COMMIT = "46be9e1bafc85e37456cbf56e9dc92b6c8178666"
METRICS = "experiments/E0/second_rater_metrics.json"
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "generated"

DATASETS = [
    ("folio", "FOLIO"),
    ("proofwriter", "ProofWriter"),
    ("cedar", "Cedar"),
    ("gatekeeper", "Gatekeeper"),
    ("alloy", "Alloy"),
    ("fret", "FRET"),
    ("clover", "Clover"),
]


def load() -> dict:
    raw = subprocess.run(
        ["git", "show", f"{E0_COMMIT}:{METRICS}"],
        check=True, capture_output=True, cwd=HERE,
    ).stdout
    return json.loads(raw)


def cell(rate: dict) -> str:
    return "{k}/{n} = {p:.1f}% [{lo:.1f}, {hi:.1f}]".format(
        k=rate["k"], n=rate["n"], p=100 * rate["rate"],
        lo=100 * rate["ci_low"], hi=100 * rate["ci_high"],
    )


def coverage_table(metrics: dict) -> str:
    rows = [
        "| Dataset | Strict fit | Lenient fit | Agreement | Kappa |",
        "|:---|:------------|:------------|---:|---:|",
    ]
    for key, name in DATASETS:
        rates = metrics["second_rates"][key]
        agreement = metrics["agreement"][key]
        binary = agreement["collapsed"]  # FIT = DIRECT or REIFIED; NO_FIT = OPAQUE or NO
        kappa = binary["kappa"]
        rows.append(
            "| {name} | {strict} | {lenient} | {m}/{n} | {kappa} |".format(
                name=name, strict=cell(rates["strict"]), lenient=cell(rates["lenient"]),
                m=binary["matching"], n=binary["n"],
                kappa="undefined" if kappa is None else f"{kappa:.2f}",
            )
        )
    return "\n".join(rows) + "\n"


def constructs_table(metrics: dict) -> str:
    header = "| Missing construct | " + " | ".join(n for _, n in DATASETS) + " | Items |"
    rows = [header, "|---|" + "---:|" * (len(DATASETS) + 1)]
    for entry in metrics["roadmap_independent"]:
        per = entry["per_dataset"]
        rows.append(
            "| {c} | {cells} | {t} |".format(
                c=entry["construct"],
                cells=" | ".join(str(per[k]) for k, _ in DATASETS),
                t=entry["total"],
            )
        )
    return "\n".join(rows) + "\n"


def main() -> None:
    metrics = load()
    OUT.mkdir(exist_ok=True)
    (OUT / "e0-coverage-table.md").write_text(coverage_table(metrics))
    (OUT / "e0-constructs-table.md").write_text(constructs_table(metrics))
    print("wrote", OUT / "e0-coverage-table.md")
    print("wrote", OUT / "e0-constructs-table.md")


if __name__ == "__main__":
    main()
