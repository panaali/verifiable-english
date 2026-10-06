"""Lean-first batch 9: the tables of DELTA.md, rendered from the evidence files.

    python docs/lean-first/b9/report.py [--write]

Without `--write` it prints the tables; with it, it replaces the generated block of `DELTA.md`.
`tests/test_lean_first_b9_report.py` checks that the block equals this rendering, so every number in it
comes from `evidence/` (the A/B compares, `timing.py`'s outputs, the eligibility run and the fuzzer A/B).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
BEGIN = "<!-- BEGIN GENERATED: python docs/lean-first/b9/report.py --write -->\n"
END = "<!-- END GENERATED -->"
COMPARES = ("quantity-compare.json", "core-compare.json", "pilots-compare.json", "layers-compare.json")
CLASSES = ("same", "wording", "order", "verdict", "availability")
OPS = (("elaborate", "`elaborate_quantity`"), ("environment", "W6 `Environment`"),
       ("meaning_id", "`quantity_meaning_id`"), ("countermodel", "`quantity_countermodel`"),
       ("certificate", "`check_quantity_certificate`"), ("admission", "`admit_document`"),
       ("prove", "`prove_quantity`"))


def load(name):
    return json.loads((EVIDENCE / name).read_text())


def number(value) -> str:
    return f"{value:,}" if isinstance(value, int) else f"{value:,.1f}"


def corpus_rows():
    """One row per (corpus, authorities): records per side and the classes of the comparison."""
    rows = []
    for name in COMPARES:
        compare = load(name)
        by_corpus: dict[str, dict] = {}
        for key, count in compare["records"].items():
            corpus, authority = key.split("/")
            entry = by_corpus.setdefault(corpus, {"authorities": [], "records": 0})
            entry["authorities"].append(authority)
            entry["records"] += count
        differences: dict[str, dict] = {}
        for difference in compare["differences"]:
            corpus = differences.setdefault(difference["corpus"], {})
            corpus[difference["class"]] = corpus.get(difference["class"], 0) + 1
        for corpus, entry in sorted(by_corpus.items(), key=lambda item: -item[1]["records"]):
            counts = differences.get(corpus, {})
            counts["same"] = entry["records"] - sum(counts.values())
            rows.append((corpus, sorted(entry["authorities"]), entry["records"], counts))
    order = ["quantity", "probe", "conformance", "pilots", "readings", "discourse"]
    return sorted(rows, key=lambda row: order.index(row[0]))


def render() -> str:
    lines = ["| Corpus | Records per side | " + " | ".join(c.capitalize() for c in CLASSES) + " |",
             "|---|---:|" + "---:|" * len(CLASSES)]
    totals = {c: 0 for c in CLASSES}
    total_records = 0
    for corpus, authorities, records, counts in corpus_rows():
        label = corpus if authorities == ["default"] else f"{corpus} (" + ", ".join(f"`{a}`" for a in authorities) + ")"
        lines.append(f"| {label} | {number(records)} | " +
                     " | ".join(number(counts.get(c, 0)) for c in CLASSES) + " |")
        total_records += records
        for c in CLASSES:
            totals[c] += counts.get(c, 0)
    lines.append(f"| **All** | {number(total_records)} | " + " | ".join(number(totals[c]) for c in CLASSES) + " |")

    eligibility = load("eligibility.json")
    base, head = eligibility["base"], eligibility["head"]
    same = "byte-identical" if base["stdout_sha256"] == head["stdout_sha256"] else "DIFFERENT"
    lines += ["", f"Eligibility harness: base {number(base['wall_s'])} s wall, {number(base['user_s'])} s user CPU; "
              f"head {number(head['wall_s'])} s wall, {number(head['user_s'])} s user CPU "
              f"({head['wall_s'] / base['wall_s']:.2f}× wall); results {same}."]

    tb, th = load("timing-base.json"), load("timing-head.json")
    cpu_base = tb["python_cpu_s"] + tb["children_cpu_s"]
    cpu_head = th["python_cpu_s"] + th["children_cpu_s"]
    lines += ["", f"Quantity corpus in one process: CPU {number(cpu_base)} s at the base "
              f"({number(tb['python_cpu_s'])} s Python, {number(tb['children_cpu_s'])} s Lean) and "
              f"{number(cpu_head)} s at the head ({number(th['python_cpu_s'])} s Python, "
              f"{number(th['children_cpu_s'])} s Lean), {(cpu_head - cpu_base) / cpu_base:+.0%}; wall "
              f"{number(tb['wall_s'])} s → {number(th['wall_s'])} s.", "",
              "| Operation | Calls | p50 wall base → head (ms) | p95 wall base → head (ms) | Total base → head (s) |",
              "|---|---:|---:|---:|---:|"]
    for op, label in OPS:
        b, h = tb["ops"][op], th["ops"][op]
        lines.append(f"| {label} | {number(b['calls'])} | {b['p50_ms']:.1f} → {h['p50_ms']:.1f} | "
                     f"{b['p95_ms']:,.1f} → {h['p95_ms']:,.1f} | {b['total_s']:,.1f} → {h['total_s']:,.1f} |")

    fuzz = load("difffuzz-ab.json")
    runs = fuzz["runs"]
    head_only = sum(len(run["head_only_new"]) for run in runs)
    new_base = sum(run["new"][0] for run in runs)
    new_head = sum(run["new"][1] for run in runs)
    entries = (runs[0]["baseline"][0]["entries"], runs[0]["baseline"][1]["entries"])
    lines += ["", f"Differential fuzzer: {len(runs)} runs (`--ci` and {len(runs) - 1} date seeds), "
              f"{head_only} head-only signatures, {new_base} → {new_head} new findings, baseline "
              f"{entries[0]} → {entries[1]} entries, "
              f"{sum(len(run['head_not_reproduced']) for run in runs)} head entries not reproduced."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    block = render()
    if not args.write:
        print(block, end="")
        return 0
    path = HERE / "DELTA.md"
    text = path.read_text()
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    path.write_text(head + BEGIN + block + END + tail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
