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
    # Every planted bug in mutants.py was run and caught, as saved: none added to the table but not run.
    sys.path.insert(0, str(HERE))
    import mutants as planted
    assert [(row["id"], row["file"], row["fault"], row["test"]) for row in mutants] == [
        (ident, name, fault, test) for ident, name, _, _, fault, test in planted.CASES], "mutants.json is not mutants.py's run"
    for script in ("seeds.py", "shadow.py", "tables.py"):
        subprocess.run([sys.executable, str(HERE / script), "--check" if script == "tables.py" else "check"],
                       check=True)
    # The seeds no test caught: every test the modes rule drops for them passed with the seed planted.
    import seeds
    rows = json.loads((EVIDENCE / "seeds.json").read_text())["seeds"]
    missed = sorted(row["id"] for row in rows if seeds.outcome(row) == seeds.MISSED)
    dropped = json.loads((EVIDENCE / "dropped.json").read_text())["seeds"]
    assert sorted(dropped) == missed, (sorted(dropped), missed)
    for seed, row in dropped.items():
        expected = {unit for unit in set(next(r for r in rows if r["id"] == seed)["today"])
                    - set(next(r for r in rows if r["id"] == seed)["modes_selected"]) if unit.startswith("tests/")}
        assert row["files"] == len(expected) and row["exit"] == 0 and not row["failed"], seed
    print(f"{len(listed)} commits, {len(mutants)} seeded bugs, seeds and shadow rows check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
