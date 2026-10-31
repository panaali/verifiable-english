"""Render Q2's reproducible non-model measurement report from saved evidence."""
from __future__ import annotations

import json
import gzip
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/spec/question-answering-q2/evidence"
DESTINATION = ROOT / "docs/spec/question-answering-report.md"
Q26 = ROOT / "docs/question-answering/q2-6/evidence"
DELTA = ROOT / "docs/spec/question-answering-q2/DELTA.md"


def expected_rows(fixtures: list[dict]) -> list[tuple[dict, str]]:
    """Each fixture's spec lead (evidence/expected.json) with the lead Lean returned; a lead that differs needs the
    DELTA.md row its `delta` names, and that row must name the fixture; a lead that agrees names no row."""
    got = {item["id"]: item.get("lead", "refused") for item in fixtures}
    expected = json.loads((Q26 / "expected.json").read_text())["fixtures"]
    if sorted(row["id"] for row in expected) != sorted(got):
        raise ValueError("the expected leads and the replayed fixtures name different fixtures")
    deltas = {line.split("|")[1].strip(): line.split("|")[2] for line in DELTA.read_text().splitlines()
              if line.startswith("| D")}
    for row in expected:
        named = set(re.findall(r"\b[AGU][0-9]+d?\b", deltas.get(row.get("delta"), "")))
        if (row["lead"] != got[row["id"]]) != ("delta" in row) or ("delta" in row and row["id"] not in named):
            raise ValueError(f"{row['id']}: spec lead {row['lead']}, Lean lead {got[row['id']]}, "
                             f"DELTA row {row.get('delta')} does not explain it")
    return [(row, got[row["id"]]) for row in expected]


def wording_counts(wording: dict) -> list[str]:
    fallback = [row for row in wording["fallback"] if row["lines"]]
    lines = [f"Answers that show a quoted fallback wording (a line containing `classified as \"`): {len(fallback)} "
             f"of {len(wording['fallback'])} answers ({', '.join(row['fixture'] for row in fallback)}), on "
             f"{sum(len(row['lines']) for row in fallback)} lines.", "",
             "| Frame | Lines shown | Clauses | Read back with one reading | Not one reading |", "|---|---:|---:|---:|---:|"]
    for frame in wording["frames"]:
        shown = [row for row in wording["situation_lines"] if row["frame"] == frame]
        clauses = [c for row in shown for c in row["clauses"]]
        lines.append(f"| {frame} | {len(shown)} | {len(clauses)} | {sum(c['status'] == 'one' for c in clauses)} | "
                     f"{sum(c['status'] != 'one' for c in clauses)} |")
    return lines


def render() -> str:
    fixtures = json.loads((EVIDENCE / "fixtures.json").read_text())["fixtures"]
    measurements = json.loads((EVIDENCE / "measurements.json").read_text())
    agreement = json.loads(gzip.decompress((EVIDENCE / "agreement.json.gz").read_bytes()))
    wording = json.loads((Q26 / "wording.json").read_text())
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
    lines += ["", "## Fixtures, expected against got", "",
              "The spec's derived lead (docs/spec/question-answering.md 7.2, 7.4, 7.5; saved in "
              "`docs/question-answering/q2-6/evidence/expected.json`) against the lead Lean returned on the recorded "
              "evidence; a lead that differs names the row of `docs/spec/question-answering-q2/DELTA.md` that "
              "explains it.", "", "| Fixture | Spec lead | Spec line | Lean lead | DELTA |", "|---|---|---:|---|---|"]
    for row, got in expected_rows(fixtures):
        lines.append(f"| {row['id']} | {row['lead']} | {row['line']} | {got} | {row.get('delta', '—')} |")
    lines += ["", "## Wording counts", "", wording["method"] + ".", ""] + wording_counts(wording)
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
              f"{'PASS' if u3_wall <= 60 else 'FAIL'}."]
    corpus = agreement.get("corpus")
    lines += ["", "## Agreement on the corpora", ""]
    if corpus is None:
        lines += ["The conformance-corpus agreement comparison is not recorded; this report does not claim that "
                  "agreement gate has passed."]
    else:
        statuses = sorted({status for counts in corpus["counts"].values() for status in counts})
        lines += [corpus["method"] + ".", "", "Scope: " + corpus["scope"] + ".", "",
                  "| Corpus | Queries | " + " | ".join(statuses) + " |",
                  "|---|---:|" + "---:|" * len(statuses)]
        for name, counts in sorted(corpus["counts"].items()):
            lines.append(f"| {name} | {sum(counts.values())} | " +
                         " | ".join(str(counts.get(status, 0)) for status in statuses) + " |")
        checked_conflicts = {verdict: sum(row["status"] == "ask unknown (X1 conflict)" and
                                          row["older"] == verdict for row in corpus["rows"])
                             for verdict in ("ALL", "NONE")}
        lines += ["", "Checked X1 conflicts where the older route answered ALL or NONE: "
                  f"{sum(checked_conflicts.values())} (ALL {checked_conflicts['ALL']}; "
                  f"NONE {checked_conflicts['NONE']})."]
        refused = {}
        for row in corpus["rows"]:
            if row["status"].startswith(("ask refused", "older route")):
                reason = (row.get("note") or row["status"]).split(":", 2)
                key = f"{row['status']}: {reason[1].strip() if len(reason) > 1 else reason[0]}"
                refused[key] = refused.get(key, 0) + 1
        review = corpus["requires_review"]
        lines += ["", f"{corpus['queries']} queries; {len(review)} required review"
                  + (" (no lead contradicts the existing route's verdict)." if not review else ":"), ""]
        lines += [f"- {r['corpus']} `{r.get('case') or ''}`, {r['question']} {r['status'].split(': ', 1)[1]}: "
                  f"{r['review']}." for r in review]
        if refused:
            lines += ["", "Queries not compared, by reason:", ""]
            lines += [f"- {key} ({count})" for key, count in sorted(refused.items())]
    lines += ["", "## Scope", "", "Reading and writing evaluation: sealed and bars registered "
              "(docs/question-answering/q2-6/readability/); not run, no model call.", ""]
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
