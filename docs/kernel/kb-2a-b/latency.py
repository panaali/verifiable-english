"""kb-2a-b (7), DESIGN kb-2a section 3 item 4: wall time and peak memory of `ve document check`, median of 5, each run
in its own scope through manage-agents/iso.sh, on the acceptance document, the UDHR part document and the agent-policy
rules, on two trees (before: the base; after: this branch).

    python3 docs/kernel/kb-2a-b/latency.py --before /path/to/base/checkout --after . --out docs/kernel/kb-2a-b/latency.json

Bound (DESIGN 3 item 4, the bound docs/lean-first/b18/latency.py already uses): for the two existing documents, after at
most 1.25x before and at most 120 s. The documents are read from the `--after` tree, so both trees check the same bytes.
Wall time includes `uv run`'s start and the Lean service's start, the same on both sides."""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path

ISO = Path.home() / "code/manage-agents/iso.sh"
DOCUMENTS = ["tests/data/kb2a/rsp-mixed.ve.md", "usecases/question-answering/udhr-part07.ve.md",
             "usecases/question-answering/agent-policy/a-rules.ve.md"]
RUNS = 5


def once(root: Path, document: Path) -> dict:
    done = subprocess.run(["zsh", str(ISO), "exp-kb2ab-latency", "32G", "--", "/usr/bin/time", "-v", "uv", "run",
                           "python", "-m", "ve", "document", "check", str(document)],
                          cwd=root, capture_output=True, text=True, check=False)
    wall = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (?:(\d+):)?(\d+):([\d.]+)", done.stderr)
    rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", done.stderr)
    seconds = int(wall.group(1) or 0) * 3600 + int(wall.group(2)) * 60 + float(wall.group(3))
    return {"exit": done.returncode, "seconds": seconds, "peak_kb": int(rss.group(1))}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = {"runs": RUNS, "documents": {}}
    for name in DOCUMENTS:
        document = (args.after / name).resolve()
        row = {}
        for side, root in (("before", args.before), ("after", args.after)):
            runs = [once(root.resolve(), document) for _ in range(RUNS)]
            row[side] = {"exits": sorted({r["exit"] for r in runs}),
                         "median_seconds": round(statistics.median(r["seconds"] for r in runs), 2),
                         "median_peak_mb": round(statistics.median(r["peak_kb"] for r in runs) / 1024, 1),
                         "seconds": [r["seconds"] for r in runs]}
        row["ratio"] = round(row["after"]["median_seconds"] / row["before"]["median_seconds"], 3)
        result["documents"][name] = row
    existing = DOCUMENTS[1:]
    result["bound"] = {"existing_documents_at_most_1.25x_and_120s": all(
        result["documents"][d]["ratio"] <= 1.25 and result["documents"][d]["after"]["median_seconds"] <= 120
        for d in existing)}
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
