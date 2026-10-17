"""Compare the complete nine-corpus recordings of the merge base and the batch head, and save an exact delta.

    python docs/lean-first/b16f/make_ab.py BASE HEAD

Every difference must be the one listed kind; any other (an accepted output that changed, a verdict, a wording,
an order or an availability change) stops the script:

* unavailable on both sides with identical outputs (SIGNED by standing ruling R7): a pilot both sides answer
  `CheckerUnavailable`, or both stop at the recorder's 600 s limit.

The recorder writes each pilot with the files it names beside it (`lean_first_diff.write_pilot`), so a senses pilot
no longer reads as a missing pack under each recorder's own temporary directory (review F2): that wording class is
gone, not listed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tools import lean_first_diff as diff

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SIGNED = "unavailable on both sides with identical outputs: SIGNED by standing ruling R7 (DRI-RULINGS.md)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("head", type=Path)
    args = parser.parse_args()
    expected = diff.expected_cases(ROOT)
    first = diff.compare(str(args.base), str(args.head), None, expected=expected)
    delta: dict[str, list] = {k: [] for k in ("order", "verdict", "availability", "unavailable", "wording")}
    for row in first["differences"]:
        klass = row["class"]
        if klass == "unavailable" and row["base"] == row["head"]:
            delta[klass].append({key: row[key] for key in ("corpus", "authority", "case", "op", "base", "head")} |
                                {"reason": SIGNED})
        else:
            raise RuntimeError(f"unexpected corpus difference: {row['corpus']}/{row['case']}/{row['op']}: {klass}")
    checked = diff.compare(str(args.base), str(args.head), delta, expected=expected)
    if checked["unlisted"]:
        raise RuntimeError(f"{checked['unlisted']} unlisted A/B differences")
    checked.update({"base_sha256": hashlib.sha256(args.base.read_bytes()).hexdigest(),
                    "head_sha256": hashlib.sha256(args.head.read_bytes()).hexdigest()})
    evidence = HERE / "evidence"
    evidence.mkdir(exist_ok=True)
    (HERE / "delta.json").write_text(json.dumps(delta, indent=2, ensure_ascii=False) + "\n")
    (evidence / "ab.json").write_text(json.dumps(checked, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"records": checked["records"], "totals": checked["totals"],
                      "unlisted": checked["unlisted"]}, indent=2))


if __name__ == "__main__":
    main()
