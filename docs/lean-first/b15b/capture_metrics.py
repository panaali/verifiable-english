"""Freeze main..HEAD implementation metrics before the report commit.

Evidence tests read the saved JSON. They never recompute a diff against a
moving HEAD (which would change after a sync or merge).
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("evidence") / "change-metrics.json"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def main() -> None:
    # The branch point is the main revision this batch started from. A later
    # advance of main must not put unrelated commits into this snapshot.
    base = git("merge-base", "main", "HEAD").strip()
    head = git("rev-parse", "HEAD").strip()
    commit_list = git("log", "--format=%H", "--reverse", "--no-merges",
                      f"{base}..{head}").splitlines()
    files, binary = [], []
    for line in git("diff", "--numstat", base, head).splitlines():
        added, deleted, path = line.split("\t", 2)
        if (added, deleted) == ("-", "-"):
            binary.append(path)  # the frozen non-vacuity oracle (gzip): no line counts
            continue
        if not (added.isdecimal() and deleted.isdecimal()):
            raise ValueError(f"ambiguous numstat: {line}")
        files.append({"path": path, "added": int(added), "deleted": int(deleted)})
    report = {
        "range": f"{base}..{head} --no-merges",
        "base": base,
        "implementation_head": head,
        "commits": commit_list,
        "files": files,
        "binary_files": binary,
        "totals": {
            "added": sum(f["added"] for f in files),
            "deleted": sum(f["deleted"] for f in files),
            "lean_added": sum(f["added"] for f in files if f["path"].endswith(".lean")),
            "lean_deleted": sum(f["deleted"] for f in files if f["path"].endswith(".lean")),
            "python_decision_deleted": sum(f["deleted"] for f in files
                                           if f["path"].startswith("ve/") and f["path"].endswith(".py")),
            "rust_deleted": sum(f["deleted"] for f in files
                                if f["path"].startswith("rust/") and f["path"].endswith(".rs")),
        },
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"range": report["range"], "commits": len(commit_list), **report["totals"]}))


if __name__ == "__main__":
    main()
