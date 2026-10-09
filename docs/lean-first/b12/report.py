"""Render batch 12's evidence table from the checked JSON artifacts.

    python docs/lean-first/b12/report.py --write
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
BASE = "49d18263"
B12_HEAD = "d772de28"  # approved batch-12 evidence, before the integration merge
BEGIN = "<!-- BEGIN GENERATED: python docs/lean-first/b12/report.py --write -->\n"
END = "<!-- END GENERATED -->"
COMPARES = ("conformance", "probe", "profiles", "pilots")
CLASSES = ("same", "wording", "order", "verdict", "availability")


def load(name: str):
    return json.loads((EVIDENCE / name).read_text())


def line_changes() -> dict[str, tuple[int, int]]:
    output = subprocess.check_output(["git", "diff", "--numstat", BASE, B12_HEAD], cwd=ROOT, text=True)
    rows = [line.split("\t") for line in output.splitlines()]
    return {
        "production Python": (sum(int(a) for a, _, p in rows if p.startswith("ve/") and p.endswith(".py")),
                              sum(int(d) for _, d, p in rows if p.startswith("ve/") and p.endswith(".py"))),
        "Lean": (sum(int(a) for a, _, p in rows if p.startswith("lean/") and p.endswith(".lean")),
                 sum(int(d) for _, d, p in rows if p.startswith("lean/") and p.endswith(".lean"))),
    }


def render() -> str:
    lines = ["| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    totals = {key: 0 for key in CLASSES}
    records = 0
    for name in COMPARES:
        report = load(f"{name}-compare.json")
        count = sum(report["records"].values())
        records += count
        for key in CLASSES:
            totals[key] += report["totals"].get(key, 0)
        lines.append("| " + name + " | " + f"{count:,}" + " | " + " | ".join(
            f"{report['totals'].get(key, 0):,}" for key in CLASSES) + " |")
    lines.append("| **All** | " + f"**{records:,}**" + " | " + " | ".join(
        f"**{totals[key]:,}**" for key in CLASSES) + " |")
    changes = line_changes()
    lines += ["", "Code lines (base to head): " + "; ".join(
        f"{name} +{added:,}/−{deleted:,} (net {added - deleted:+,})"
        for name, (added, deleted) in changes.items()) + "."]
    before = json.loads(subprocess.check_output(
        ["git", "show", f"{BASE}:conformance/difffuzz-baseline.json"], cwd=ROOT, text=True))
    after = json.loads(subprocess.check_output(
        ["git", "show", f"{B12_HEAD}:conformance/difffuzz-baseline.json"], cwd=ROOT, text=True))
    fuzz = load("difffuzz-ab.json")
    runs = fuzz["runs"]
    head_only = sum(len(row["head_only_new"]) for row in runs)
    first = load("difffuzz-first-pass.json")
    reviewed = {entry["signature"] for row in first["runs"] for entry in row["head_only_new"]}
    lines.append(f"Differential fuzz: {len(runs)} runs (CI and 14 date seeds); baseline "
                 f"{len(before['entries']):,} → {len(after['entries']):,}; "
                 f"{head_only} head-only new signatures; "
                 f"{sum(len(row['head_not_reproduced']) for row in runs)} head entries not reproduced.")
    lines.append(f"First-pass date-seed review found {len(reviewed)} distinct head-only signatures.")
    latency = load("latency.json")
    for op, label in (("udhr", "UDHR"), ("eligibility", "Eligibility")):
        row = latency[op]
        lines.append(f"{label}: base {row['median']['base']['wall_s']:.3f} s → head "
                     f"{row['median']['head']['wall_s']:.3f} s; {row['wall_ratio']:.3f}× wall; "
                     f"{row['child_cpu_ratio']:.3f}× child CPU; "
                     f"output {'identical' if row['same_output'] else 'different'}; "
                     f"budget {'pass' if row['within_budget'] else 'FAIL'}.")
    cpu = load("lean-cpu.json")
    lines.append(f"Eligibility isolated Lean CPU: base {cpu['median']['base']['lean_cpu_s']:.3f} s → head "
                 f"{cpu['median']['head']['lean_cpu_s']:.3f} s; {cpu['lean_cpu_ratio']:.3f}×; "
                 f"output {'identical' if cpu['same_output'] else 'different'}; "
                 f"budget {'pass' if cpu['lean_cpu_ratio'] <= 1.20 else 'FAIL'}.")
    gate_path = EVIDENCE / "gate.json"
    if gate_path.exists():
        gate = load("gate.json")
        lines.append(f"Full gate: {gate['status']}; {gate['counts'].get('passed', 0):,} passed, "
                     f"{gate['counts'].get('skipped', 0):,} skipped, {len(gate['failures'])} failures.")
    else:
        lines.append("Full gate: pending committed HEAD run.")
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
