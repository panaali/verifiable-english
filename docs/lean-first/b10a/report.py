"""Lean-first batch 10a: the tables of DELTA.md, rendered from the evidence files.

    uv run --frozen python docs/lean-first/b10a/report.py [--write]

Without `--write` it prints the tables; with it, it replaces the generated block of `DELTA.md`.
`tests/test_lean_first_b10a_report.py` checks that the block equals this rendering, so every number in it comes
from `evidence/` (the A/B compare and record summaries, `timing.py`'s outputs and the seeded-bug runs).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
BEGIN = "<!-- BEGIN GENERATED: python docs/lean-first/b10a/report.py --write -->\n"
END = "<!-- END GENERATED -->"


def load(name):
    return json.loads((EVIDENCE / name).read_text())


def percent(head, base):
    text = f"{(head - base) / base:+.0%}"
    return "0%" if text in ("+0%", "-0%") else text.replace("-", "−")


def ab_rows():
    compare, records = load("ab-compare.json"), load("ab-records.json")
    totals = compare["totals"]
    rows = ["| Records per side | Same | Wording | Order | Verdict | Availability | Unlisted |",
            "|---:|---:|---:|---:|---:|---:|---:|",
            f"| {sum(compare['records'].values()):,} | {totals.get('same', 0):,} | {totals.get('wording', 0)} "
            f"| {totals.get('order', 0)} | {totals.get('verdict', 0)} | {totals.get('availability', 0)} "
            f"| {compare['unlisted']} |",
            "", "| Corpus / authority | Records per side |", "|---|---:|"]
    rows += [f"| {name} | {count:,} |" for name, count in sorted(compare["records"].items())]
    rows += ["", f"Base records `{records['base']['sha256'][:12]}…`, head records `{records['head']['sha256'][:12]}…` "
                 f"(SHA-256 of the record files, {records['base']['records']:,} and {records['head']['records']:,} lines)."]
    return rows


def timing_rows():
    rows = ["| Workload | Side | Runs | CPU per run (s) | Median CPU (s) | Change | Load |",
            "|---|---|---:|---|---:|---:|---|"]
    route = load("timing-route.json")
    corpora = load("timing.json")
    groups = [(f"`ve_norm_defaults_route`, {route['cases']:,} cases in {route['chunks']} chunks", route["runs"])]
    for what in ("record readings", "record probe"):
        groups.append((f"`lean_first_diff.py {what}`" + (" (lean authority)" if "probe" in what else ""),
                       [r for r in corpora["runs"] if r["what"] == what]))
    for label, runs in groups:
        medians = {}
        for side in ("base", "head"):
            mine = [r for r in runs if r["side"] == side]
            medians[side] = median(r["cpu"] for r in mine)
            loads = f"{min(r['load'] for r in mine)}–{max(r['load'] for r in mine)}"
            change = "" if side == "base" else percent(medians["head"], medians["base"])
            rows.append(f"| {label if side == 'base' else ''} | {side} | {len(mine)} | "
                        f"{', '.join(f'{r['cpu']:.2f}' for r in mine)} | {medians[side]:.2f} | {change} | {loads} |")
    new = load("timing-new-kinds.json")
    rows += ["", "| New kinds (head only) | Cases | CPU per run (s) | CPU per case (ms, best run) |",
             "|---|---:|---|---:|"]
    for name, data in new.items():
        rows.append(f"| {name} | {data['cases']:,} | {', '.join(f'{r['cpu']:.2f}' for r in data['runs'])} | "
                    f"{data['cpu_ms_per_case_min']:.2f} |")
    return rows


def seeded_rows():
    rows = ["| Seeded bug | Failing tests (of 48 in the two new files) | Tests that caught it |", "|---|---:|---|"]
    for name, result in load("seeded-bugs.json").items():
        failed = result["failed"]
        if result.get("build") == "failed":
            rows.append(f"| {name} | — | does not build: {result['log'][0].split(': ', 1)[1]} (proof obligation) |")
            continue
        rows.append(f"| {name} | {len(failed)} | {'; '.join(f'`{t.split('::')[1]}`' for t in failed)} |")
    return rows


def render():
    parts = ["### Gate item 2: corpus A/B", "", *ab_rows(), "",
             "### Gate item 4: latency (paired, base and head alternating)", "", *timing_rows(), "",
             "### Seeded bugs (build checklist 13)", "", *seeded_rows()]
    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    text = render()
    if not args.write:
        print(text)
        return
    delta = HERE / "DELTA.md"
    current = delta.read_text()
    head, rest = current.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    delta.write_text(head + BEGIN + text + END + tail)


if __name__ == "__main__":
    main()
