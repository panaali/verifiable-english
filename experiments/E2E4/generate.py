"""Regenerate committed harness-ready JSONL files."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    from .materials import build_items
except ImportError:
    from materials import build_items

ROOT = Path(__file__).resolve().parent


def main() -> None:
    for experiment in ("E2", "E4"):
        for split in ("dev", "scored"):
            path = ROOT / f"{experiment.lower()}-{split}.jsonl"
            rows = build_items(split, experiment)
            path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


if __name__ == "__main__":
    main()
