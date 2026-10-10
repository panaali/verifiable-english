"""Measure AR-3 (evidence/measure.json): the committed baseline it removes, the rule replayed over main's history
of that baseline, and one collection of the merge base in a scratch worktree, timed and compared with the
baseline committed at the base.

Run from the checkout after `(cd lean && lake build)`, with `lake` and `cargo` on PATH:
    uv run python docs/arch/AR-3/measure.py
"""
from __future__ import annotations

from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import gate_collection  # noqa: E402

OUT = Path(__file__).resolve().parent / "evidence/measure.json"
BASELINE = "tools/gate-collection.json"
DAYS = 14


def text(*args: str) -> str:
    return gate_collection.git(list(args)).stdout.decode()


def baseline(commit: str) -> list[str] | None:
    shown = gate_collection.git(["show", f"{commit}:{BASELINE}"], check=False)
    return json.loads(shown.stdout) if shown.returncode == 0 else None


def main() -> int:
    base = gate_collection.merge_base()
    ended = datetime.fromisoformat(text("log", "-1", "--format=%cI", base).strip())
    since = (ended - timedelta(days=DAYS)).isoformat()
    window = ["--since", since, base, "--", BASELINE]
    pinned = baseline(base)
    # The rule replayed: each first-parent commit of main that changed the baseline, its parent as the base.
    replay = []
    for commit in reversed(text("log", "--first-parent", "--format=%H", *window).split()):
        parent = gate_collection.rev(f"{commit}^1")
        before, after = baseline(parent), baseline(commit)
        if before is None or after is None:
            continue
        explained, refused = gate_collection.missing(before, after, gate_collection.changes(parent, commit))
        replay.append({"commit": commit, "subject": text("log", "-1", "--format=%s", commit).strip(),
                       "removed": len(explained) + len(refused), "explained": len(explained), "refused": refused})
    # One collection of the base as the gate takes it without a record.
    with tempfile.TemporaryDirectory(prefix="ve-ar3-measure-") as scratch:
        env = {name: os.environ[name] for name in gate_collection.INHERITED if name in os.environ}
        started = time.monotonic()
        collected = gate_collection.collect_commit(base, Path(scratch), build_env=dict(os.environ),
                                                   env={**env, "VE_NATIVE_PREBUILT": "1"}, python=[sys.executable])
        seconds = round(time.monotonic() - started, 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "base": base, "since": since, "days": DAYS,
        "baseline": {"lines": len(gate_collection.git(["show", f"{base}:{BASELINE}"]).stdout.splitlines()),
                     "bytes": len(gate_collection.git(["show", f"{base}:{BASELINE}"]).stdout),
                     "ids": len(pinned),
                     "commits": len(text("log", "--no-merges", "--format=%H", *window).split()),
                     "first_parent_commits": len(replay)},
        "replay": {"commits": replay, "removed": sum(row["removed"] for row in replay),
                   "explained": sum(row["explained"] for row in replay),
                   "refused": sum(len(row["refused"]) for row in replay)},
        "base_collection": {"seconds": seconds, "ids": len(collected),
                            "only_collected": sorted(set(collected) - set(pinned)),
                            "only_pinned": sorted(set(pinned) - set(collected))},
    }, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
