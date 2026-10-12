"""Save and check batch 14c evidence after the full gate on committed HEAD.

Usage: python3 docs/lean-first/b14c/finalize_evidence.py gate-result.json
The gate result remains in the worktree because committing it would move HEAD.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from tools.batch_evidence import problems


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/lean-first/b14c/evidence"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, text=True,
                          capture_output=True).stdout.strip()


def scope(main: str, head: str) -> dict:
    commits = [dict(zip(("sha", "subject"), line.split("\t", 1)))
               for line in git("log", "--no-merges", "--format=%H%x09%s",
                               f"{main}..{head}").splitlines()]
    changed = []
    for line in git("diff", "--numstat", f"{main}...{head}").splitlines():
        added, deleted, path = line.split("\t", 2)
        if added.isdecimal() and deleted.isdecimal():
            changed.append({"file": path, "added": int(added), "deleted": int(deleted)})
    lean = [row for row in changed if row["file"].startswith("lean/") and
            row["file"].endswith(".lean") and not row["file"].endswith("/Audit.lean")]
    product_python = [row for row in changed if row["file"].startswith("ve/") and
                      row["file"].endswith(".py")]
    return {"main_tip": main, "merge_base": git("merge-base", main, head),
            "head_commit": head, "commits_no_merges": commits,
            "lean_source_added": sum(row["added"] for row in lean),
            "lean_source_deleted": sum(row["deleted"] for row in lean),
            "product_python_deleted": sum(row["deleted"] for row in product_python),
            "files": changed}


def main() -> int:
    result = Path(sys.argv[1]).resolve()
    gate = json.loads(result.read_text())
    head, main_tip = git("rev-parse", "HEAD"), git("rev-parse", "main")
    comparison = json.loads((EVIDENCE / "ab.json").read_text())
    latency = json.loads((EVIDENCE / "latency.json").read_text())
    comparison["head_commit"] = head
    latency["head_commit"] = head
    errors = problems(head, gate, comparison, latency)
    if errors:
        raise SystemExit("batch evidence failed: " + "; ".join(errors))
    gate["batch14c"] = {"comparison": comparison, "latency": latency,
                        "scope": scope(main_tip, head)}
    result.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n")
    saved = json.loads(result.read_text())
    assert not problems(head, saved, saved["batch14c"]["comparison"],
                        saved["batch14c"]["latency"])
    assert saved["batch14c"]["scope"] == scope(main_tip, head)
    print(f"batch evidence PASS on {head}: {len(saved['batch14c']['scope']['commits_no_merges'])} "
          "non-merge commits; corpus, latency, full gate and scope checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
