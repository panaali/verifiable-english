"""Lean-first batch 3b: the timing tables of DELTA.md, rendered from the evidence files.

    uv run --frozen python docs/lean-first/b3b/report.py [--write]

Without `--write` it prints the tables; with it, it replaces the generated block of `DELTA.md`.
`tests/test_lean_first_b3b_report.py` checks that the block equals this rendering, so every number in it comes
from `evidence/` (`udhr_timing.py` outputs, `timing.py` outputs and the profiler's lines; the review round's from
`udhr_timing.py alternate`).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import statistics

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
BEGIN = "<!-- BEGIN GENERATED: python docs/lean-first/b3b/report.py --write -->\n"
END = "<!-- END GENERATED -->"
CASES = (("udhr-1-set.json", "first set", 1, 4, 12), ("udhr-10-sets.json", "first 10 sets", 10, 30, 72),
         ("udhr-whole.json", "whole document", 39, 176, 734))


def cpu(side):
    return side["user"] + side["sys"]


def change(base, head):
    text = f"{(head - base) / base:+.0%}"
    return "0%" if text in ("+0%", "-0%") else text.replace("-", "−")


def udhr_rows():
    rows = ["| Case | Sets | Candidates | Pairs | Run | Load | Base CPU (s) | Head CPU (s) | Change | Head wall (s) "
            "| Answers |", "|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|"]
    for name, label, sets, candidates, pairs in CASES:
        for k, run in enumerate(json.loads((EVIDENCE / name).read_text())["runs"], 1):
            rows.append(f"| {label} | {sets} | {candidates} | {pairs} | {k} | {run['load_before']}–{run['load_after']} "
                        f"| {cpu(run['base']):,.1f} | {cpu(run['head']):,.1f} "
                        f"| {change(cpu(run['base']), cpu(run['head']))} | {run['head']['wall']:,.1f} "
                        f"| {'identical' if run['identical'] else 'DIFFERENT'} |")
    return rows


def profile(name):
    steps = {}
    for line in (EVIDENCE / name).read_text().splitlines():
        m = re.match(r"(.+?): wall ([\d.]+) s, cpu ([\d.]+) s$", line)
        if m:
            key = m[1].split(" ")[0] if m[1].split(" ")[0] in ("rows", "pairs", "findings") else m[1]
            steps[key] = steps.get(key, 0.0) + float(m[3])
    return steps


def profile_rows():
    split = profile("profile-split.txt")
    total = sum(split[k] for k in ("admitReadings", "rows", "pairs", "findings"))
    rows = ["| Step of the head's whole-document call | CPU (s) | Share |", "|---|---:|---:|"]
    for key, label in (("admitReadings", "admission: 4.1's checks, `free D` and 176 candidates validated once each"),
                       ("pairs", "pairs: 734 ordered pairs"), ("rows", "candidate rows"), ("findings", "4.6 findings")):
        rows.append(f"| {label} | {split[key]:,.1f} | {split[key] / total:.0%} |")
    rows.append(f"| **total** | **{total:,.1f}** | |")
    blocks, pair = profile("profile-blocks.txt"), profile("profile-pair.txt")
    rows += ["", "| One validation or one pair (head, whole document) | CPU (s) |", "|---|---:|"]
    for key in ("validateRights", "softSemanticCheck", "checkSoft", "targets", "rightsSemanticCheck"):
        rows.append(f"| `{key}` | {blocks[key]:.2f} |")
    for key in ("pairFacts", "sideValue witness", "sideValue other, every assignment", "conflict formula, built",
                "outcome formula, built", "conflict formula, evaluated", "outcome formula, evaluated"):
        rows.append(f"| pair `rs_u087`: {key} | {pair[key]:.2f} |")
    return rows


def corpus_rows():
    data = json.loads((EVIDENCE / "corpus-timing.json").read_text())
    rows = ["| Readings corpus run (1,137 documents through `readings_route.validate`) | Base Lean CPU (s) "
            "| Head Lean CPU (s) | Change | Outcomes (ok / rejected / unavailable), both sides |",
            "|---|---:|---:|---:|---|"]
    for run in data["readings_corpus"]:
        b, h = run["base"], run["head"]
        same = all(b[k] == h[k] for k in ("ok", "rejected", "unavailable"))
        rows.append(f"| {run['run']} | {b['children_cpu']:.1f} | {h['children_cpu']:.1f} "
                    f"| {change(b['children_cpu'], h['children_cpu'])} "
                    f"| {b['ok']} / {b['rejected']} / {b['unavailable']}{'' if same else ' (DIFFERENT)'} |")
    one, per = data["one_process"], data["per_process"]
    for k, (b, h) in enumerate(zip(one["base_cpu"], one["head_cpu"]), 1):
        rows.append(f"| the same cases in one process, run {k} | {b:.2f} | {h:.2f} | {change(b, h)} | |")
    rows.append(f"| the same cases, one process each, alternating | {per['base_cpu']:.1f} | {per['head_cpu']:.1f} "
                f"| {change(per['base_cpu'], per['head_cpu'])} | |")
    rows += ["", "| 100 start-ups on an empty batch (user + sys, s) | Base, lake output | Head, lake output "
             "| Head, fresh copy of the same bytes |", "|---|---:|---:|---:|"]
    for k, run in enumerate(data["startup_100_empty"]["runs"], 1):
        rows.append(f"| run {k} | {run['base_lake_output']:.2f} | {run['head_lake_output']:.2f} "
                    f"| {run['head_copy']:.2f} |")
    rows += ["", "| Constitution pilot S1 document (`ve document check`, children CPU, two runs) | Base (s) | Head (s) |",
             "|---|---|---|"]
    for name, runs in data["pilots"]["base"].items():
        head = data["pilots"]["head"][name]
        rows.append(f"| `{name.split(':')[0]}` | {', '.join(f'{r['children_cpu']:.1f}' for r in runs)} "
                    f"| {', '.join(f'{r['children_cpu']:.1f}' for r in head)} |")
    return rows


REVIEW = (("review-b1-reproducer.json", "review B1's reproducer: 12 cells, ten fixed default rules"),
          ("review-first-error.json", "the first set's default candidate ill-formed, 119 candidates after it"),
          ("review-udhr-1-set.json", "UDHR first set"))


def review_rows():
    rows = ["| Case | Rounds | Load | Base, min / median CPU (s) | Before the fixes, min / median | Head, min / median "
            "| Head against before, min / median | Rounds the head is faster | Answers |",
            "|---|---:|---|---:|---:|---:|---:|---:|---|"]
    for name, label in REVIEW:
        data = json.loads((EVIDENCE / name).read_text())
        cpus = {side: [run["cpu"] for run in runs] for side, runs in data["runs"].items()}
        least = {side: min(xs) for side, xs in cpus.items()}
        middle = {side: statistics.median(xs) for side, xs in cpus.items()}
        faster = sum(h < b for h, b in zip(cpus["head"], cpus["before"]))
        rows.append(f"| {label} | {data['rounds']} | {data['load_before']}–{data['load_after']} "
                    + "".join(f"| {least[side]:,.2f} / {middle[side]:,.2f} " for side in ("base", "before", "head"))
                    + f"| {change(least['before'], least['head'])} / {change(middle['before'], middle['head'])} "
                    f"| {faster} of {data['rounds']} | {'identical' if data['identical'] else 'DIFFERENT'} |")
    return rows


def render():
    return "\n".join(["### UDHR readings call (paired runs)", "", *udhr_rows(), "", "### Where the head's CPU goes", "",
                      *profile_rows(), "", "### Other measured workloads", "", *corpus_rows(), "",
                      "### Review round (B1, B2): base, the head before the fixes, the head", "",
                      *review_rows()]) + "\n"


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
