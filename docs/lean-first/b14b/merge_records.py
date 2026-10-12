"""Merge bounded corpus recordings, checking keys and optional case replacement.

``--replace-cases`` replaces all rows for each case present in the last input.
This repairs an earlier recording whose checker was temporarily unavailable.
The normal corpus comparator checks the merged output for complete coverage.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text().split("\n"), 1):
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: incomplete recording") from exc
    return rows


def key(row: dict) -> tuple[str, str, str, str]:
    parts = tuple(row.get(name) for name in ("corpus", "authority", "case", "op"))
    if not all(type(part) is str for part in parts):
        raise ValueError(f"invalid recording key: {parts!r}")
    return parts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--replace-cases", action="store_true")
    parser.add_argument("inputs", type=Path, nargs="+")
    args = parser.parse_args()
    if args.replace_cases and len(args.inputs) < 2:
        parser.error("case replacement requires an original and a replacement input")
    groups = [read(path) for path in args.inputs]
    replacing = {key(row)[:3] for row in groups[-1]} if args.replace_cases else set()
    merged: dict[tuple[str, str, str, str], dict] = {}
    for index, group in enumerate(groups):
        for row in group:
            identity = key(row)
            if args.replace_cases and index < len(groups) - 1 and identity[:3] in replacing:
                continue
            previous = merged.get(identity)
            if previous is not None and previous != row:
                raise ValueError(f"conflicting duplicate recording: {identity!r}")
            merged[identity] = row
    with args.out.open("w") as out:
        for identity in sorted(merged):
            out.write(json.dumps(merged[identity], sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False) + "\n")
    print(f"{len(merged)} unique records from {len(args.inputs)} recordings")


if __name__ == "__main__":
    main()
