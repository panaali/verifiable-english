"""Lean-first batch 3d: the tables of DELTA.md, rendered from the evidence files.

    uv run --frozen python docs/lean-first/b3d/report.py [--write]

Without `--write` it prints the tables; with it, it replaces the generated block of `DELTA.md`.
`tests/test_lean_first_b3d_report.py` checks that the block equals this rendering, so every number in it comes
from `evidence/` (the A/B summary, `udhr_timing.py` and `timing.py` outputs and the profiler's lines).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
BEGIN = "<!-- BEGIN GENERATED: python docs/lean-first/b3d/report.py --write -->\n"
END = "<!-- END GENERATED -->"
CASES = (("udhr-1-set.json", "first set", 1, 4, 12), ("udhr-10-sets.json", "first 10 sets", 10, 30, 72),
         ("udhr-whole.json", "whole document", 39, 176, 734))
UDHR_RUNS = tuple(name for name, *_ in CASES) + ("corpus-one-process.json",)


def cpu(side):
    return side["user"] + side["sys"]


def change(base, head):
    text = f"{(head - base) / base:+.0%}"
    return "0%" if text in ("+0%", "-0%") else text.replace("-", "−")


def load(path):
    return json.loads((EVIDENCE / path).read_text())


def ab_rows():
    data = load("ab-summary.json")
    totals = data["totals"]
    rows = ["| Records per side | Same | Wording | Order | Verdict | Availability | Unlisted |",
            "|---:|---:|---:|---:|---:|---:|---:|"]
    rows.append(f"| {sum(data['records'].values()):,} | {totals.get('same', 0):,} | {totals.get('wording', 0)} "
                f"| {totals.get('order', 0)} | {totals.get('verdict', 0)} | {totals.get('availability', 0)} "
                f"| {data['unlisted']} |")
    rows += ["", "| Corpus | Records per side |", "|---|---:|"]
    for name, count in sorted(data["records"].items()):
        rows.append(f"| {name.split('/')[0]} | {count:,} |")
    return rows


def udhr_rows():
    rows = ["| Case | Sets | Candidates | Pairs | Run | Load | Base CPU (s) | Head CPU (s) | Change | Head wall (s) "
            "| Answers |", "|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|"]
    for name, label, sets, candidates, pairs in CASES:
        for k, run in enumerate(load(name)["runs"], 1):
            rows.append(f"| {label} | {sets} | {candidates} | {pairs} | {k} | {run['load_before']}–{run['load_after']} "
                        f"| {cpu(run['base']):,.1f} | {cpu(run['head']):,.1f} "
                        f"| {change(cpu(run['base']), cpu(run['head']))} | {run['head']['wall']:,.1f} "
                        f"| {'identical' if run['identical'] else 'DIFFERENT'} |")
    return rows


def pilot_rows():
    rows = ["| Run | Load | Base: wall (s), exit, answer | Head: wall (s), exit, answer | Head CPU, process and "
            "children (s) |", "|---:|---|---|---|---:|"]
    for k, run in enumerate(load("pilot-udhr.json")["runs"], 1):
        b, h = run["base"], run["head"]
        rows.append(f"| {k} | {run['load_before']}–{run['load_after']} | {b['wall']:.1f}, {b['exit']}, {b['status']} "
                    f"| {h['wall']:.1f}, {h['exit']}, {h['status']} ({h['report_bytes']:,} bytes) | {h['cpu']:.1f} |")
    return rows


def profile(name, column=3):
    """Per step, the summed CPU (`column` 3, 10 ms resolution) or wall time (`column` 2) of a profiler output."""
    steps = {}
    for line in (EVIDENCE / name).read_text().splitlines():
        m = re.match(r"(.+?): wall ([\d.]+) s, cpu ([\d.]+) s$", line)
        if m:
            key = m[1].split(" ")[0] if m[1].split(" ")[0] in ("rows", "pairs", "findings") else m[1]
            steps[key] = steps.get(key, 0.0) + float(m[column])
    return steps


def equal_lines(name):
    return [line for line in (EVIDENCE / name).read_text().splitlines() if " = " in line and line.endswith(": true")]


def profile_rows():
    prims, pair = profile("profile-prims.txt", 2), profile("profile-pair.txt", 2)
    rows = ["| On the first UDHR candidate (`prims`), wall time | Specified (s) | As run (s) | Same answer |",
            "|---|---:|---:|---|"]
    same = {line.split(":")[0] for line in equal_lines("profile-prims.txt")}
    for spec, run in (("targets", "targetsIn"), ("checkSoft", "checkSoftOnce"),
                      ("softSemanticCheck", "softSemanticCheckOnce"), ("validateRights", "validateRightsOnce"),
                      ("chainTextSpec", "chainText")):
        extra = " (+ `layersOf` " + f"{prims['layersOf']:.3f})" if run == "targetsIn" else ""
        rows.append(f"| `{spec}` / `{run}` | {prims[spec]:.3f} | {prims[run]:.3f}{extra} "
                    f"| {'yes' if f'{spec} = {run}' in same else 'NOT SHOWN'} |")
    rows.append(f"| layer order of one document (`order`, a topological sort) | {prims['order']:.3f} | | |")
    pair_same = bool(equal_lines("profile-pair.txt"))
    rows.append(f"| pair `rs_u087`: `pairFacts` / `pairFactsIn` (sides built) | {pair['pairFacts']:.3f} "
                f"| {pair['pairFactsIn, sides built']:.3f} | {'yes' if pair_same else 'NOT SHOWN'} |")
    split = profile("profile-split.txt")
    total = sum(split[k] for k in ("admitReadings", "rows", "pairs", "findings"))
    rows += ["", "| Step of the head's whole-document call (`split`) | CPU (s) | Share |", "|---|---:|---:|"]
    for key, label in (("admitReadings", "admission: 4.1's checks, `free D` and 176 candidates validated once each"),
                       ("rows", "candidate rows (`candidateJson`)"),
                       ("pairs", "pairs: 734 ordered pairs, each side built once per set"),
                       ("findings", "4.6 findings")):
        rows.append(f"| {label} | {split[key]:,.1f} | {split[key] / total:.0%} |")
    rows.append(f"| **total** | **{total:,.1f}** | |")
    return rows


def corpus_rows():
    rows = ["| Readings corpus (1,137 documents through `readings_route.validate`) | Load | Base Lean CPU (s) "
            "| Head Lean CPU (s) | Change | Outcomes (ok / rejected / unavailable) |", "|---|---|---:|---:|---:|---|"]
    for k, run in enumerate(load("corpus-timing.json")["runs"], 1):
        b, h = run["base"], run["head"]
        same = all(b[x] == h[x] for x in ("ok", "rejected", "unavailable"))
        rows.append(f"| one route process per document, run {k} | {run['load_before']}–{run['load_after']} "
                    f"| {b['children_cpu']:.1f} | {h['children_cpu']:.1f} "
                    f"| {change(b['children_cpu'], h['children_cpu'])} "
                    f"| {h['ok']} / {h['rejected']} / {h['unavailable']}{'' if same else ' (DIFFERENT)'} |")
    for k, run in enumerate(load("corpus-one-process.json")["runs"], 1):
        rows.append(f"| the same 1,137 route cases in one route process, run {k} | {run['load_before']}–"
                    f"{run['load_after']} | {cpu(run['base']):.2f} | {cpu(run['head']):.2f} "
                    f"| {change(cpu(run['base']), cpu(run['head']))} "
                    f"| answers {'identical' if run['identical'] else 'DIFFERENT'} |")
    return rows


def render():
    return "\n".join(["### Gate item 2: corpus A/B", "", *ab_rows(), "", "### UDHR readings call (paired runs)", "",
                      *udhr_rows(), "", "### UDHR pilot translation through `ve document check` (paired runs)", "",
                      *pilot_rows(), "", "### Where the CPU went, and where the head's goes", "", *profile_rows(),
                      "", "### The readings corpus", "", *corpus_rows()]) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if not args.write:
        print(render(), end="")
        return 0
    delta = HERE / "DELTA.md"
    text = delta.read_text()
    head, rest = text.split(BEGIN, 1)
    delta.write_text(head + BEGIN + render() + END + rest.split(END, 1)[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
