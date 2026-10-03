"""Recompute one reading item's key with VE and print the checker's verdict.

    uv run python experiments/readability-sonnet/ve_key.py R01

The printed JSON is what items.json records as `ve_output` for the item.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

if __name__ == "__main__":
    for item_id in sys.argv[1:]:
        r = build.compute(build.item_by_id(item_id))
        print(json.dumps({"label": r["label"], "verdict": r["verdict"]}, sort_keys=True, default=str))
