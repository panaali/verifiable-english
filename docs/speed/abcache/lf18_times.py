"""Minutes per corpus and records per (corpus, authority) of an A/B recording, per side.

    uv run python docs/speed/abcache/lf18_times.py /tmp/lf18/ab > docs/speed/abcache/evidence/lf18-ab-times.json
    uv run python docs/speed/abcache/lf18_times.py DIR SIDE:STARTED:RECORDS ...  # this item's runs (REPORT.md 2)

A side is `<side>` with the file whose birth is its start (default `<side>.log`) and its records (default
`<side>.jsonl`, the child's output; under `--cache`, `<out>.part0`).

The recorder writes the corpora in order (probe, conformance, pilots, readings, discourse, rights, quantity,
norm_defaults, document) and creates a scratch directory when a corpus starts: `<side>.pilots`, `.discourse`,
`.rights`, `.norm_defaults`, `.document`. Their birth times (`stat %W`) split a side's run into spans; the corpus
files (`<side>.*.json`) are written before the child starts, and `<side>.jsonl`'s last write ends the run.
Readings has no directory (it is inside the pilots span) and quantity none (inside the rights span).
"""
from __future__ import annotations

import collections
import json
from pathlib import Path
import subprocess
import sys


def birth(path: Path) -> int:
    return int(subprocess.run(["stat", "--format=%W", str(path)], check=True, capture_output=True,
                              text=True).stdout)


def side(directory: Path, name: str, started: str = "", records: str = "") -> dict:
    log, jsonl = directory / (started or f"{name}.log"), directory / (records or f"{name}.jsonl")
    marks = [("corpus files", birth(log)), ("probe+conformance", birth(jsonl))]
    for corpus, label in (("pilots", "pilots+readings"), ("discourse", "discourse"), ("rights", "rights+quantity"),
                          ("norm_defaults", "norm_defaults"), ("document", "document")):
        marks.append((label, birth(directory / f"{name}.{corpus}")))
    end = int(jsonl.stat().st_mtime)
    spans = {label: round(((marks[i + 1][1] if i + 1 < len(marks) else end) - start) / 60, 1)
             for i, (label, start) in enumerate(marks)}
    records = collections.Counter()
    with jsonl.open() as stream:
        for line in stream:
            row = json.loads(line)
            records[f"{row['corpus']}/{row['authority']}"] += 1
    return {"minutes": spans, "total_minutes": round((end - marks[0][1]) / 60, 1), "records": dict(records)}


def main() -> None:
    directory, sides = Path(sys.argv[1]), [arg.split(":") for arg in sys.argv[2:]] or [["base"], ["head"]]
    print(json.dumps({parts[0]: side(directory, *parts) for parts in sides}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
