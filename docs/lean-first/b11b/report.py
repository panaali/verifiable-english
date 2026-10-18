"""Regenerate the numerical part of batch 11b's report from gate evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEGIN = "<!-- BEGIN GENERATED B11B METRICS -->"
END = "<!-- END GENERATED B11B METRICS -->"


def totals(paths):
    """Read the line counts saved with the batch, independent of later merges."""
    rows = json.loads((HERE / "evidence/production-numstat.json").read_text())
    assert set(rows) == {
        "ve/speech_acts.py", "ve/speech_document.py",
        "lean/VE/SpeechActs/Source/Run.lean", "lean/VE/SpeechActs/Source/Admission/Run.lean",
    }
    return tuple(sum(rows[path][column] for path in paths) for column in ("added", "deleted"))


def render():
    python_added, python_deleted = totals(["ve/speech_acts.py", "ve/speech_document.py"])
    lean_added, lean_deleted = totals(["lean/VE/SpeechActs/Source/Run.lean",
                                      "lean/VE/SpeechActs/Source/Admission/Run.lean"])
    ab = json.loads((HERE / "evidence/ab-compare.json").read_text())
    fuzz = json.loads((HERE / "evidence/difffuzz-ab.json").read_text())
    availability = json.loads((HERE / "evidence/speech-availability.json").read_text())
    latency = json.loads((HERE / "evidence/latency.json").read_text())
    head_p95 = max(row["p95_wall_ms"] for row in latency if row["side"] == "head")
    head_cpu = max(row["p95_child_cpu_ms"] for row in latency if row["side"] == "head")
    assert ab["totals"]["same"] == sum(ab["records"].values())
    assert not ab["differences"] and not ab["unavailable_both"] and ab["unlisted"] == 0
    assert fuzz["all_equal"] and all(row["equal"] for row in fuzz["runs"])
    assert len(availability) == 3 and all(row["class"] == "availability" for row in availability)
    assert len(latency) == 14 and head_p95 < 2000
    return (f"- Listed production files: **{python_deleted:,} Python lines deleted**, "
            f"{python_added:,} added; **{lean_added:,} Lean lines added**, {lean_deleted:,} deleted.\n"
            f"- Corpus A/B: **{ab['totals']['same']:,} identical records**, including "
            f"{ab['records']['pilots/default']:,} historical pilot checks; zero unlisted differences.\n"
            f"- Differential fuzzer: **{len(fuzz['runs'])} runs** (CI plus 14 date seeds), "
            f"{sum(row['new'][0] for row in fuzz['runs'])} base and "
            f"{sum(row['new'][1] for row in fuzz['runs'])} head new-signature appearances; "
            "the signature sets and baseline replays match on every run.\n"
            f"- Speech-only availability: **{len(availability)}** listed changes requiring a DRI signature.\n"
            f"- W2 caller timing: **{len(latency)}** same-host rows (20 calls per side and template); "
            f"maximum head p95 {head_p95:.3f} ms wall and {head_cpu:.3f} ms child CPU.\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    path = HERE / "DELTA.md"
    text = path.read_text()
    start, tail = text.split(BEGIN, 1)
    _, end = tail.split(END, 1)
    replacement = start + BEGIN + "\n\n" + render() + "\n" + END + end
    if args.write:
        path.write_text(replacement)
        print("updated", path)
    else:
        assert text == replacement, "DELTA.md numerical evidence is stale"
        print("PASS: batch 11b report metrics are regenerated from their evidence")


if __name__ == "__main__":
    main()
