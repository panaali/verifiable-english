"""Step 5 table of eff-20261030-1: each chunkable file whole vs in chunks on the Mac, from measure5.sh's logs.

    uv run python docs/infra/eff-20261030-1/step5_table.py <log dir> [--json OUT]

Per file: the whole run's wall time (pytest's "in N s") and peak RSS, each chunk's, the chunked wall time if the
chunks run side by side (the longest chunk) and their summed seconds (the CPU-side cost), and whether the per-node
outcomes are identical: the union of the chunks' (node ID, outcome) pairs equals the whole run's, and no node is in
two chunks. Exit 1 when any file's outcomes differ.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import chunk_table  # noqa: E402

RSS = re.compile(r"^bench-chunk (?P<chunk>\S+): peak RSS (?P<own>[\d.]+) MiB \(largest child (?P<child>[\d.]+) MiB\)")


def run(log: Path) -> dict:
    parsed = chunk_table.parse(log)
    rss = next((found for line in log.read_text(errors="replace").splitlines() if (found := RSS.match(line))), None)
    return {"wall": parsed["wall"], "outcomes": parsed["outcomes"], "counts": parsed["counts"],
            "rss": float(rss["own"]) if rss else None, "child_rss": float(rss["child"]) if rss else None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    rows, same = [], True
    for whole_log in sorted(args.logs.glob("*.1of1.log")):
        stem = whole_log.name.removesuffix(".1of1.log")
        whole = run(whole_log)
        chunks = {log.name: run(log) for log in sorted(args.logs.glob(f"{stem}.*of*.log")) if log != whole_log}
        union: dict[str, str] = {}
        twice = 0
        for chunk in chunks.values():
            twice += len(set(chunk["outcomes"]) & set(union))
            union.update(chunk["outcomes"])
        identical = union == whole["outcomes"] and twice == 0 and bool(union)
        same &= identical
        walls = [chunk["wall"] or 0.0 for chunk in chunks.values()]
        rows.append({"file": f"tests/{stem}.py", "k": len(chunks), "nodes": len(whole["outcomes"]),
                     "whole_wall": whole["wall"], "whole_rss_mib": whole["rss"],
                     "whole_child_rss_mib": whole["child_rss"],
                     "chunk_walls": walls, "chunked_wall": max(walls), "chunk_sum": round(sum(walls), 1),
                     "chunk_rss_mib": [chunk["rss"] for chunk in chunks.values()],
                     "chunk_child_rss_mib": [chunk["child_rss"] for chunk in chunks.values()],
                     "outcomes": {outcome: list(union.values()).count(outcome) for outcome in sorted(set(union.values()))},
                     "identical_outcomes": identical})
    print("| file | k | nodes | whole wall s | chunk walls s | chunked wall s (cut) | chunk sum s | "
          "whole peak RSS MiB | chunk peak RSS MiB | outcomes identical |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        cut = 1 - r["chunked_wall"] / r["whole_wall"] if r["whole_wall"] else 0.0
        print(f"| {r['file']} | {r['k']} | {r['nodes']} | {r['whole_wall']} | {' / '.join(map(str, r['chunk_walls']))} | "
              f"{r['chunked_wall']} ({cut:.0%}) | {r['chunk_sum']} | {r['whole_rss_mib']} | "
              f"{' / '.join(map(str, r['chunk_rss_mib']))} | {r['identical_outcomes']} ({r['outcomes']}) |")
    if args.json:
        args.json.write_text(json.dumps(rows, indent=1) + "\n")
    return 0 if same else 1


if __name__ == "__main__":
    raise SystemExit(main())
