"""Replace affected corpus rows after a focused rerecord, preserving all nine corpora."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FIELDS = ("corpus", "authority", "case", "op")
AFFECTED = {"pilots", "norm_defaults", "document"}


def key(row):
    return tuple(row[name] for name in FIELDS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("full", type=Path)
    parser.add_argument("affected", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    replacement = {key(row): row for line in args.affected.open() if (row := json.loads(line))}
    assert len(replacement) == sum(1 for _ in args.affected.open())
    affected = {k[0] for k in replacement}
    assert affected and affected <= AFFECTED
    found = set()
    with args.full.open() as source, args.out.open("w") as output:
        for line in source:
            row = json.loads(line)
            if row["corpus"] in affected:
                k = key(row)
                assert k in replacement
                new = replacement[k]
                assert row["source_sha256"] == new["source_sha256"]
                row = new
                found.add(k)
            output.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    assert found == set(replacement)
    assert sum(1 for _ in args.out.open()) == sum(1 for _ in args.full.open())
    print(f"replaced {len(found)} affected rows in a complete recording")


if __name__ == "__main__":
    main()
