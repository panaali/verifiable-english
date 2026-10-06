"""Lean-first batch 7: the delta of the rights corpus (review B2, B3) from a `lean_first_diff.py compare --json` run.

    uv run --frozen python docs/lean-first/b7/rights_delta.py COMPARE.json docs/lean-first/b7/delta.json

Lists every difference of the rights corpus under the class the comparison gave it, so that the comparison run with
`--delta` has no unlisted difference, and refuses a difference outside the three kinds the review names:

* O1 (`order`): a rejection whose code changes from `InvalidInput` to `UnknownSymbol` with the same text;
* W1 (`wording`): a rejection whose text gains its code as a prefix (`bar` → `DuplicateDeclaration: bar`);
* A1 (`verdict` by the tool, an availability change): a `readings@1` document whose base check raised
  `UnsupportedProfile: Unsupported profile readings@1` and whose head check returns a report.

Nothing is written inside the checkout but the output file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HEADED = "UnsupportedProfile: Unsupported profile readings@1"


def kind(row: dict) -> str:
    base, head = row["base"].get("raised"), row["head"].get("raised")
    if row["class"] == "order" and base["code"] == "InvalidInput" and head["code"] == "UnknownSymbol" \
            and base["message"] == head["message"]:
        return "O1"
    if row["class"] == "wording" and base["code"] == head["code"] and head["message"] == f"{base['code']}: " \
            f"{base['message']}":
        return "W1"
    if row["class"] == "verdict" and row["case"].endswith("/readings@1") and base is not None \
            and base["message"] == HEADED and "returned" in row["head"]:
        return "A1"
    raise SystemExit(f"a difference outside O1, W1 and A1: {row['op']} {row['case']}")


def delta(compared: dict) -> dict:
    out = {"format": "lean-first-delta@1", "batch": "7", "wording": [], "order": [], "verdict": [],
           "availability": []}
    pairs = set()
    counts = {"O1": 0, "W1": 0, "A1": 0}
    for row in compared["differences"]:
        if row["corpus"] != "rights":
            raise SystemExit(f"a difference outside the rights corpus: {row['corpus']}")
        counts[kind(row)] += 1
        if row["class"] == "wording":
            pair = (row["base"]["raised"]["message"], row["head"]["raised"]["message"])
            if pair not in pairs:
                pairs.add(pair)
                out["wording"].append({"base": pair[0], "head": pair[1]})
        else:
            out[row["class"]].append({key: row[key] for key in ("corpus", "authority", "case", "op", "base", "head")})
    out["wording"].sort(key=lambda p: (p["base"], p["head"]))
    out["counts"] = counts
    return out


if __name__ == "__main__":
    result = delta(json.loads(Path(sys.argv[1]).read_text()))
    Path(sys.argv[2]).write_text(json.dumps(result, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps(result["counts"]))
