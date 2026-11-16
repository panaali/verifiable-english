"""Moved-check for pf-f9-order-undo: which frozen-key answers move between two results.json files.

Usage: python3 moved_check.py <before results.json> <after results.json> <answer-key.json>
Prints one JSON object: the key's item count, the agree counts before and after, and `moved`, the
key items whose VE answer, status or agreement differs (empty when no keyed answer moves).
"""
import json
import sys


def rows(path):
    return {row["id"]: row for row in json.loads(open(path, encoding="utf-8").read())["comparison"]}


def main(before_path, after_path, key_path):
    key = [item["id"] for item in json.loads(open(key_path, encoding="utf-8").read())["items"]]
    before, after = rows(before_path), rows(after_path)
    moved = [{"id": i, "before": {f: before.get(i, {}).get(f) for f in ("ve", "status", "agree")},
              "after": {f: after.get(i, {}).get(f) for f in ("ve", "status", "agree")}}
             for i in key
             if any(before.get(i, {}).get(f) != after.get(i, {}).get(f) for f in ("ve", "status", "agree"))]
    print(json.dumps({"key_items": len(key), "agree_before": sum(r["agree"] for r in before.values()),
                      "agree_after": sum(r["agree"] for r in after.values()), "moved": moved}, indent=1))
    return 1 if moved else 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:4]))
