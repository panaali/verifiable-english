"""Check and save the batch 14b A/B corpus comparison.

Usage: python docs/lean-first/b14b/compare.py BASE.json HEAD.json OUT.json
The two files must contain the same generated cases and operation keys. This is
batch evidence, checked at the batch gate and merge; it is not a permanent test.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys


def compare(base: dict, head: dict) -> dict:
    if (base["seed"], base["count"]) != (head["seed"], head["count"]):
        raise ValueError("different corpus seeds or counts")
    left, right = base["records"], head["records"]
    if len(left) != len(right) or not left:
        raise ValueError("missing or empty corpus records")
    differences = []
    for index, (b, h) in enumerate(zip(left, right)):
        key = {name: b.get(name) for name in ("index", "family", "op", "rules", "model",
                                               "allow", "definitions")}
        if key != {name: h.get(name) for name in key}:
            raise ValueError(f"input differs at record {index}")
        if b["answer"] != h["answer"]:
            differences.append({"record": index, "index": key["index"], "family": key["family"],
                                "op": key["op"], "base": b["answer"], "head": h["answer"]})
    return {"seed": base["seed"], "documents": base["count"], "records": len(left),
            "differences": differences, "identical": not differences}


if __name__ == "__main__":
    _, base_path, head_path, out_path = sys.argv
    result = compare(json.loads(Path(base_path).read_text()), json.loads(Path(head_path).read_text()))
    Path(out_path).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{result['records']} records; {len(result['differences'])} differences")
    raise SystemExit(0 if result["identical"] else 1)
