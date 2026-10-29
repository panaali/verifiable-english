"""JT-E1 archive and prospective prompt checks. The recorded study is invalid.

Fresh calls require captured display from the real renderer and fresh items (jt-e1b).
This module deliberately cannot turn the frozen JT-E1 rows into another study.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
PROMPT = (
    "Read only the source and displayed lines below as a reader of this document. "
    "For the named conclusion, answer in exactly this format: "
    "`CLASS: SETTLED|TURNS|CONDITIONAL; DECIDER: <name or NONE>; WHY: <one sentence>`. "
    "SETTLED means it holds whatever is judged. TURNS means two admissible judgments can change it. "
    "CONDITIONAL means it is certified only given a judgment criterion. "
    "Name the decider if the text names one; otherwise say NONE. Do not use outside knowledge."
)
CALL_CAP = 100
CW_CAP = 3_000_000
RESERVE_CW = 25_000


def items():
    with (HERE / "items.tsv").open(newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="|"))
    assert len(rows) == 40 and len({r["id"] for r in rows}) == 40
    assert sum(r["id"].startswith("U") for r in rows) == 20
    assert sum(r["id"].startswith("C") for r in rows) == 20
    return rows


def render(row, arm):
    atom, who, conclusion = row["atom"], row["decider"], row["conclusion"]
    if arm not in ("identifier", "english"):
        raise ValueError(arm)
    # Preview only: the declaration is available today, but the zone/criterion
    # answer lines are not. Never infer an answer line from the answer key.
    fallback = f'Open reading: "{row["subject"]}" is classified as "{row["predicate"]}".'
    if arm == "identifier" or row["template"] != "yes":
        legend = fallback
    else:
        legend = (f"Whether {atom} is a judgment; the text does not say who makes it."
                  if who == "unstated" else f"Whether {atom} is a judgment for {who}.")
    decider = ("The text does not name a decider." if who == "unstated"
               else f"Judgment decider: {who}.")
    return f"{PROMPT}\n\nSOURCE: {row['source']}\nCONCLUSION: {conclusion}\n{legend}\n{decider}\n"


def validate_live_display(rows):
    """Require two captured real-renderer arms before any fresh reader call.

    Capture is a separate JT-E1b deliverable once JT-3/JT-4 can render all
    constructor kinds. The original frozen rows contain no such capture.
    """
    for row in rows:
        pair = (row.get("identifier_display"), row.get("english_display"))
        if not all(isinstance(display, str) and display.strip() for display in pair):
            raise ValueError(f"{row['id']}: missing live renderer display")
        if row["template"] != "yes" and pair[0] != pair[1]:
            raise ValueError(f"{row['id']}: rejected template must use identifier fallback")
        if row["decider"] != "unstated" and any(row["decider"] not in display for display in pair):
            raise ValueError(f"{row['id']}: named decider absent from an arm")


def parse_answer(raw):
    match = re.search(r"CLASS:\s*(SETTLED|TURNS|CONDITIONAL)\s*;\s*DECIDER:\s*([^;\n]+)", raw, re.I)
    if not match:
        return None, None
    return match.group(1).upper(), match.group(2).strip().upper()


def score(row, raw):
    cls, decider = parse_answer(raw)
    expected = row["answer"].upper()
    expected_decider = "NONE" if row["decider"] == "unstated" or expected == "SETTLED" else row["decider"].upper()
    correct = cls == expected and decider == expected_decider
    critical = expected in {"TURNS", "CONDITIONAL"} and (
        cls == "SETTLED" or bool(re.search(r"\b(?:is|was|remains)\s+(?:settled|checked)\b", raw, re.I))
    )
    return {"class": cls, "decider": decider, "correct": correct, "critical": critical}


def usage_cw(result):
    usage = result.get("usage", {})
    return sum(int(usage.get(k, 0)) for k in (
        "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))


def within_budget(calls, cw):
    return calls < CALL_CAP and cw + RESERVE_CW <= CW_CAP


def existing():
    return [json.loads(p.read_text()) for p in RAW.glob("*.json")]


def main():
    rows = items()
    validate_live_display(rows)
    raise RuntimeError("JT-E1 is archived; run a fresh-item jt-e1b study, not this runner")


if __name__ == "__main__":
    raise SystemExit(main())
