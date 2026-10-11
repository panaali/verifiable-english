"""Compare the complete nine-corpus recordings and save an exact delta."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tools import lean_first_diff as diff

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


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
        if row["corpus"] in ("norm_defaults", "document"):
            if "raised" not in row["base"] or "raised" not in row["head"]:
                raise RuntimeError(f"accepted output changed: {row['corpus']}/{row['case']}/{row['op']}")
            reason = "invalid input is rejected with a different code, text, or diagnostic path"
        elif row["corpus"] == "pilots" and klass == "wording" and all(
                "Cannot read sense pack" in str(row[side]) for side in ("base", "head")):
            reason = "the same missing sense pack names each recorder's temporary directory"
        else:
            raise RuntimeError(f"unexpected corpus difference: {row['corpus']}/{row['case']}/{row['op']}")
        if klass == "wording":
            for base, head in diff.text_pairs(row["base"], row["head"]):
                pair = {"base": base, "head": head}
                if pair not in delta[klass]:
                    delta[klass].append(pair)
        else:
            delta[klass].append({key: row[key] for key in ("corpus", "authority", "case", "op", "base", "head")} |
                                {"reason": reason})
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
