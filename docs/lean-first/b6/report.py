"""The latency table of DELTA.md, rendered from evidence/udhr-timing.json (build checklist 20).

    python3 docs/lean-first/b6/report.py           # print the table
    python3 docs/lean-first/b6/report.py --write   # replace it in DELTA.md
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BEGIN = "<!-- BEGIN GENERATED LATENCY: python3 docs/lean-first/b6/report.py --write -->\n"
END = "<!-- END GENERATED LATENCY -->"
# The plan's allowances (docs/LEAN-FIRST-PLAN.md section 5.1): CPU growth and the pilot's wall limit.
CPU_RATIO_LIMIT = 1.25
PILOT_WALL_LIMIT = 120.0


def timing():
    return json.loads((HERE / "evidence/udhr-timing.json").read_text())


def ratio(row):
    """Head CPU over base CPU; a run under half a second of CPU on both sides is start-up, not work."""
    if max(row["base"]["cpu"], row["head"]["cpu"]) < 0.5:
        return None
    return round(row["head"]["cpu"] / row["base"]["cpu"], 2)


def summary():
    rows = timing()["runs"]
    worked = [r for r in rows if ratio(r) is not None]
    return {"documents": len({r["document"] for r in rows}), "runs": len(rows),
            "commands": sorted({r["command"] for r in rows}),
            "identical": all(r["output_equal"] and r["base"]["exit"] == r["head"]["exit"] == 0 for r in rows),
            "max_ratio": max(ratio(r) for r in worked),
            "max_ratio_by_command": {c: max(ratio(r) for r in worked if r["command"] == c)
                                     for c in sorted({r["command"] for r in worked})},
            "max_head_wall": max(r["head"]["wall"] for r in rows),
            "max_base_wall": max(r["base"]["wall"] for r in rows)}


def render():
    data = timing()
    lines = [f"Base `{data['base']}` against head `{data['head']}`, both sides started together on each document "
             "(CPU is user + system, Lean services included).", "",
             "| Document | Command | Run | Bytes | Base wall s | Base CPU s | Head wall s | Head CPU s | CPU ratio "
             "| Same output | Load |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|"]
    for row in data["runs"]:
        name = row["document"].split(":", 1)[0].removeprefix("pilot/")
        r = ratio(row)
        lines.append(f"| {name} | {row['command']} | {row['run']} | {row['bytes']:,} | {row['base']['wall']:.2f} "
                     f"| {row['base']['cpu']:.2f} "
                     f"| {row['head']['wall']:.2f} | {row['head']['cpu']:.2f} | {'—' if r is None else f'{r:.2f}'} "
                     f"| {'yes' if row['output_equal'] else 'NO'} | {row['load']} |")
    s = summary()
    by_command = ", ".join(f"{c} {v:.2f}" for c, v in s["max_ratio_by_command"].items())
    lines += ["", f"{s['runs']} runs of {s['documents']} documents ({' and '.join(s['commands'])}), every output "
              f"identical: {'yes' if s['identical'] else 'NO'}. Largest CPU ratio {s['max_ratio']:.2f} ({by_command}; "
              f"allowance {CPU_RATIO_LIMIT}); slowest head run {s['max_head_wall']:.2f} s wall "
              f"(pilot limit {PILOT_WALL_LIMIT:.0f} s). A ratio is omitted when both sides spent under 0.5 s of CPU."]
    return "\n".join(lines) + "\n"


def write():
    path = HERE / "DELTA.md"
    text = path.read_text()
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    path.write_text(head + BEGIN + render() + END + tail)


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        write()
    else:
        print(render(), end="")
