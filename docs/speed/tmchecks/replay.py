#!/usr/bin/env python3
"""REPORT section 1b: replay speed-tmrerun's carry rule (rule.py, `Reads`) on sc-1b 5a0051f93 -> 24504cdd5, and
check every carried verdict against the full sweep at 24504cdd5.

    uv run python docs/speed/tmchecks/replay.py [--rule tools|tmrerun] [--full FULL.json] [--out replay.json]

Both commits are checked out detached in a scratch directory (feature/sc-1b is only read), the tool plans each
(`plan`: no build), and the saved 5a0051f93 evidence's rows are matched to the first plan's mutants by (file, line,
definition, operator, before, after). Each KILLED and INVALID row gets the digest of what it reads on the first tree
(`Reads.verdict`); each mutant of the second plan is carried when that digest reads the same there (`Reads.carry`).
`--rule tmrerun` reads rule.py from infra/speed-tmrerun (git show), `--rule tools` the rule as moved into
tools/trust_mutants.py (`Reads`). With --full, every carried verdict is compared with that run's verdict on the
same mutant (status, and the killing check's file)."""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "tools")]
import trust_mutants as tm  # noqa: E402

SAVED = Path("/home/seyran/code/manage-agents/reviews/speed-tmchecks-inputs/sc-1b-5a0051f93.json")
FIRST, SECOND, BASE = "5a0051f93", "24504cdd5", "e9e63dda7ff2ca089c8d8f03e3657b76a55c1cfa"


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def rule(which: str, scratch: Path):
    if which == "tools":
        return tm
    path = scratch / "docs/speed/tmrerun/rule.py"  # where it sits on its branch: it reads parents[3]
    path.parent.mkdir(parents=True)
    path.write_text(git("show", "infra/speed-tmrerun:docs/speed/tmrerun/rule.py"))
    spec = importlib.util.spec_from_file_location("tmrerun_rule", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ident(m) -> tuple:
    return (m["file"], m["line"], m["definition"], m["operator"], m["before"], m["after"]) if isinstance(m, dict) \
        else (m.file, m.line, m.definition, m.operator, m.before, m.after)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rule", choices=("tools", "tmrerun"), default="tmrerun")
    parser.add_argument("--full", type=Path, help="the full sweep's evidence at 24504cdd5")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    saved = json.loads(SAVED.read_text())
    with tempfile.TemporaryDirectory(prefix="tmchecks-") as scratch:
        reads_of = rule(args.rule, Path(scratch)).Reads
        trees = {}
        try:
            for commit in (FIRST, SECOND):
                root = Path(scratch) / commit
                git("worktree", "add", "-q", "--detach", str(root), commit)
                found, tree, fatal = tm.plan(root, BASE)
                assert not fatal, fatal
                trees[commit] = (found, tree, reads_of(root, tree, []))
        finally:
            for commit in trees:
                git("worktree", "remove", "--force", str(Path(scratch) / commit))
            git("worktree", "prune")
    (one, _, r1), (two, _, r2) = trees[FIRST], trees[SECOND]
    assert [ident(m) for m in one] == [ident(m) for m in saved["mutants"]], "the saved rows are not the first plan"
    prevs = {}
    for m, row in zip(one, saved["mutants"]):
        m.status, m.detail = row["raw_status"], row["detail"]
        r1.verdict(m)
        prevs[ident(m), m.start] = {"status": m.status, "detail": m.detail, "reads": m.reads, "killed_at": m.killed_at}
    why, carried = Counter(), {}
    for m in two:
        m.reads, m.killed_at, m.carried_from = "", None, ""
        p = prevs.get((ident(m), m.start))  # one line can hold two equal edits
        if p and p["reads"]:
            r2.carry(m, p, FIRST)
        if m.carried_from:
            why[f"carried {m.status}"] += 1
            carried[m.id] = (m.status, m.detail)
        elif p is None:
            why["a new mutant"] += 1
        elif p["status"] not in ("KILLED", "INVALID"):
            why[f"raw {p['status']} (never carried)"] += 1
        elif not p["reads"]:
            why["its kill cites no check of lean/"] += 1
        else:
            why["its killing check, or what that reads, changed"] += 1
    result = {"rule": args.rule, "first": FIRST, "second": SECOND, "mutants": len(two), "carried": len(carried),
              "rerun": len(two) - len(carried), "why": dict(sorted(why.items()))}
    if args.full:
        full = {m["id"]: m for m in json.loads(args.full.read_text())["mutants"]}
        assert sorted(full) == sorted(m.id for m in two) and all(ident(full[m.id]) == ident(m) for m in two)
        differ = [(i, s, full[i]["raw_status"], d, full[i]["detail"]) for i, (s, d) in carried.items()
                  if s != full[i]["raw_status"] or (s == "KILLED" and d.split(":")[0] != full[i]["detail"].split(":")[0])]
        same_line = sum(d.split(": ")[0] == full[i]["detail"].split(": ")[0] for i, (s, d) in carried.items())
        result["full"] = {"head": json.loads(args.full.read_text())["head"], "differ": differ,
                          "same_killing_line": same_line,
                          "rerun_full_verdicts": dict(Counter(full[m.id]["raw_status"] for m in two
                                                              if m.id not in carried))}
    print(json.dumps(result, indent=1))
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    return int(bool(result.get("full", {}).get("differ")))


if __name__ == "__main__":
    sys.exit(main())
