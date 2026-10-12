"""Render Q2's reproducible non-model measurement report from saved evidence."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/spec/question-answering-q2/evidence"
DESTINATION = ROOT / "docs/spec/question-answering-report.md"


def render() -> str:
    fixtures = json.loads((EVIDENCE / "fixtures.json").read_text())["fixtures"]
    measurements = json.loads((EVIDENCE / "measurements.json").read_text())
    agreement = json.loads((EVIDENCE / "agreement.json").read_text())
    lines = ["# Question answering: Q2 non-model evidence", "",
             "The recorded answer fixtures were replayed through Lean's `ask` mode by "
             "`tests/test_ask_fixtures.py`. The table records those saved results; it does not infer a "
             "new answer from the expected column.", "",
             "| Fixture | Route | Lead | Rows | Replay wall s |", "|---|---|---|---:|---:|"]
    for item in fixtures:
        if "error" in item:
            lines.append(f"| {item['id']} | — | refused: {item['error']} | 0 | — |")
        else:
            lines.append(f"| {item['id']} | {item['route']} | {item['lead']} | {item['rows']} | "
                         f"{item['lean_seconds']} |")
    lines += ["", "## Timed requests", "", measurements["method"] + ".", "",
              "| Fixture | `english.question` Lean CPU s | `ask` Lean CPU s | `ve ask` wall s |",
              "|---|---:|---:|---:|"]
    for ident, row in measurements["fixtures"].items():
        lines.append(f"| {ident} | {row['english.question']['cpu_s']} | {row['ask']['cpu_s']} | "
                     f"{row['ve ask']['wall_s']} |")
    lines += ["", "## Existing verdict route", "", agreement["method"] + ".", "",
              "| Fixture | Ask lead | Older verdict | Comparison |", "|---|---|---|---|"]
    for row in agreement["rows"]:
        lines.append(f"| {row['fixture']} | {row['ask']} | {row['older'] or '—'} | {row['status']} |")
    ask_cpu = {ident: row["ask"]["cpu_s"] for ident, row in measurements["fixtures"].items()}
    u3_wall = measurements["fixtures"]["U3"]["ve ask"]["wall_s"]
    lines += ["", "The registered limits are `ask` CPU ≤ 2 s and U3 `ve ask` wall ≤ 60 s. "
              "These measurements used a warm persistent Lean service for CPU and a cold CLI process for wall time. "
              "`ask` CPU: " + ", ".join(f"{ident} {'PASS' if cpu <= 2 else 'FAIL'}" for ident, cpu in ask_cpu.items()) +
              "; U3 CLI wall: "
              f"{'PASS' if u3_wall <= 60 else 'FAIL'}.",
              "", "## Scope", "", "The evaluation made no model calls. Reader and writer accuracy, including the "
              "comparison of ‘No.’ and ‘Not necessarily.’, remains unmeasured. The conformance-corpus "
              "agreement comparison with the older verdict routes is not yet recorded; this report does not claim "
              "that agreement gate has passed.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    expected = render()
    if len(sys.argv) == 2 and sys.argv[1] == "--check":
        if not DESTINATION.exists() or DESTINATION.read_text() != expected:
            raise SystemExit("question-answering report differs from saved evidence")
    elif len(sys.argv) == 2 and sys.argv[1] == "--write":
        DESTINATION.write_text(expected)
    else:
        raise SystemExit("usage: question_answering_report.py --write|--check")
