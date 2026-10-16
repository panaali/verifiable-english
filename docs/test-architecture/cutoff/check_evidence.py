"""Check this batch's saved evidence (architecture decision D4: at the batch gate and the merge train,
never as a permanent test). Reads only the files saved here; nothing is recomputed from a moving HEAD.

  python3 docs/test-architecture/cutoff/check_evidence.py
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = HERE / "evidence"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout.strip()


def main() -> int:
    summary = json.loads((EVIDENCE / "summary.json").read_text())
    # The batch's commits, saved with the batch: each must exist and be a non-merge commit between the
    # saved base and the saved last code commit.
    listed = git("rev-list", "--no-merges", f"{summary['base']}..{summary['last_code_commit']}").split()
    assert listed == summary["commits"] and listed, "the saved commit list is not the base..last range"
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())["mutants"]
    assert len(mutants) >= 3 and all(row["result"] == "failed" and row["test"] and row["file"] for row in mutants)
    assert {row["language"] for row in mutants} == {"python"}
    for script in ("seeds.py", "shadow.py"):
        subprocess.run([sys.executable, str(HERE / script), "check"], check=True)
    print(f"{len(listed)} commits, {len(mutants)} seeded bugs, seeds and shadow rows check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
