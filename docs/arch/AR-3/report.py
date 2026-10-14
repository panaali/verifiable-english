"""Save AR-3's scope (evidence/scope.json): the merge base, the commits of `main..HEAD --no-merges` and each changed
path's added and deleted lines, so the report's numbers are checked against this record, not a moving HEAD.

Run on the batch's last code commit: uv run python docs/arch/AR-3/report.py
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import gate_collection  # noqa: E402

OUT = Path(__file__).resolve().parent / "evidence/scope.json"


def main() -> int:
    base = gate_collection.merge_base()
    head = gate_collection.rev("HEAD")
    log = gate_collection.git(["log", "--no-merges", "--format=%H%x00%s", f"main..{head}"]).stdout.decode()
    commits = [dict(zip(("sha", "subject"), line.split("\0"))) for line in log.splitlines()]
    numstat = gate_collection.git(["diff", "--no-renames", "--numstat", base, head]).stdout.decode()
    files = {}
    for line in numstat.splitlines():
        added, deleted, path = line.split("\t")
        files[path] = {"added": int(added), "deleted": int(deleted)}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"range": "main..HEAD --no-merges", "base": base, "head": head,
                               "commits": commits, "files": files}, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(commits)} commits, {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
