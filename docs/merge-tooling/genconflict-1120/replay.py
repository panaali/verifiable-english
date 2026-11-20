"""Replay of three merges the train declined (genconflict-1120), and the time of a plain `--resolve`.

    python3 docs/merge-tooling/genconflict-1120/replay.py --worktree DIR [--pairs] [--timing N] > replay.txt

Pairs: each real pair whose merge conflicted only on files carrying hashes of the safety-framework environment
is merged in a scratch worktree DIR (created detached at main if missing; never ve-integration) on top of its
first commit plus an overlay commit of this checkout's tools/regen_generated.py, .gitattributes and
route_fixtures.py, with the `ve-generated` driver as the repository configures it. Then, as merge-train does,
`--resolve --only lake-build --only checker-pins` and a plain `--resolve` (each timed), and the five derived
files are compared with the agent sync's result commit.

Timing: a clean merge of a one-line doc commit into main, then a plain `--resolve`, with main's tool and with
this checkout's (overlaid), N rounds alternating; per-entry seconds come from each run's own timing log.

Needs the Lean toolchain (the resolve builds and pins ve_service) and the pinned FSF text. Recorded once.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
M = Path.home() / "code/manage-agents"
OVERLAY = (".gitattributes", "tools/regen_generated.py", "docs/en-e3-norm/en-2b/route_fixtures.py")
FILES = ("conformance/english-lean/lexicon-report.json", "tests/data/route-cases.jsonl",
         "usecases/safety-framework/results.json", "usecases/safety-framework/coverage.json",
         "usecases/safety-framework/spans.json")
PAIRS = (("f1", "228142ff", "ef7ecd59", "f02219f5"), ("f2", "61b159e4", "727d1d21", "505ec3a5"),
         ("f7", "23d551568", "09bea097", "f4df75c5"))
NEW = ("english-lexicon-report", "route-cases", "usecase-safety-framework")
ENV = {**os.environ, "PATH": f"{Path.home()}/.local/bin:{Path.home()}/.elan/bin:{Path.home()}/.cargo/bin:"
       + os.environ.get("PATH", "")}


def run(args, cwd, env=None) -> tuple[int, str, float]:
    start = time.monotonic()
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env or ENV)
    return done.returncode, done.stdout + done.stderr, time.monotonic() - start


def git(wt, *args) -> str:
    code, out, _ = run(["git", *args], wt)
    if code:
        raise SystemExit(f"git {' '.join(args)}: {out}")
    return out


def reset(wt: Path, rev: str) -> None:
    if run(["git", "rev-parse", "-q", "--verify", "MERGE_HEAD"], wt)[0] == 0:
        run(["git", "merge", "--abort"], wt)
    git(wt, "reset", "-q", "--hard")
    git(wt, "clean", "-fdq")
    git(wt, "checkout", "-q", "--detach", rev)


def overlay(wt: Path) -> str:
    for name in OVERLAY:
        (wt / name).write_bytes((ROOT / name).read_bytes())
    git(wt, "add", "--", *OVERLAY)
    git(wt, "-c", "user.name=replay", "-c", "user.email=replay@localhost", "commit", "-q", "--no-verify", "-m",
        "overlay: genconflict-1120 tools")
    return git(wt, "rev-parse", "HEAD").strip()


def resolve(wt: Path, tag: str, *only: str) -> tuple[int, float, dict, str]:
    """(exit code, wall seconds, {entry: seconds of its write and check}, output tail) of one --resolve."""
    log = Path(f"/tmp/genconflict-replay-{tag}.jsonl")
    log.unlink(missing_ok=True)
    argv = ["uv", "run", "python", "tools/regen_generated.py", "--resolve", *(a for o in only for a in ("--only", o))]
    code, out, seconds = run(["zsh", str(M / "iso.sh"), f"exp-genconflict-{tag}", "24G", "--", *argv], wt,
                             {**ENV, "VE_REGEN_LOG": str(log)})
    entries: dict = {}
    for line in log.read_text().splitlines() if log.is_file() else ():
        row = json.loads(line)
        entries[row["entry"]] = round(entries.get(row["entry"], 0) + row["seconds"], 1)
    return code, seconds, entries, "\n".join(out.splitlines()[-6:])


def unmerged(wt: Path) -> list[str]:
    return git(wt, "diff", "--name-only", "--diff-filter=U").split()


def compare(wt: Path, agent: str, ours: str, theirs: str) -> list[str]:
    rows = []
    for path in FILES:
        mine = (wt / path).read_bytes()
        committed = {rev: run(["git", "show", f"{rev}:{path}"], wt)[1].encode() for rev in (agent, ours, theirs)}
        if mine == committed[agent]:
            rows.append(f"    {path}: byte-equal to the agent's result")
            continue
        same = [name for name, rev in (("ours", ours), ("theirs", theirs)) if mine == committed[rev]]
        rows.append(f"    {path}: DIFFERS from the agent's result ({len(mine)} vs {len(committed[agent])} bytes"
                    + (f"; equal to {', '.join(same)}" if same else "") + ")")
        _, text, _ = run(["bash", "-c", f"diff <(git show {agent}:{path}) {path} | head -12"], wt)
        rows.extend(f"      {line[:160]}" for line in text.splitlines())
    return rows


def pairs(wt: Path) -> None:
    for name, ours, theirs, agent in PAIRS:
        print(f"== {name}: {ours} + {theirs} -> agent sync {agent}")
        reset(wt, ours)
        top = overlay(wt)
        code, out, _ = run(["git", "merge", "-q", "--no-commit", "--no-ff", theirs], wt)
        print(f"  git merge (driver installed): exit {code}; conflicted: {' '.join(unmerged(wt)) or '(none)'}")
        code1, s1, _, tail1 = resolve(wt, f"{name}-build", "lake-build", "checker-pins")
        print(f"  --resolve --only lake-build --only checker-pins: exit {code1}, {s1:.0f} s")
        code2, s2, entries, tail2 = resolve(wt, f"{name}-plain")
        print(f"  --resolve: exit {code2}, {s2:.0f} s; new entries: "
              + ", ".join(f"{e} {entries[e]} s" for e in NEW if e in entries))
        if code1 or code2:
            print("    " + (tail1 if code1 else tail2).replace("\n", "\n    "))
        print(*compare(wt, agent, top, theirs), sep="\n")
        staged = [p for p in git(wt, "diff", "--cached", "--name-only", agent).split() if p not in OVERLAY]
        print(f"  other files differing from the agent's tree: {' '.join(staged) or '(none)'}")
        reset(wt, "main")


def timing(wt: Path, rounds: int) -> None:
    main = git(ROOT, "rev-parse", "main").strip()
    reset(wt, main)
    (wt / "docs/merge-tooling.md").write_text((wt / "docs/merge-tooling.md").read_text() + "\n")
    git(wt, "-c", "user.name=replay", "-c", "user.email=replay@localhost", "commit", "-q", "-a", "--no-verify",
        "-m", "a one-line doc change")
    other = git(wt, "rev-parse", "HEAD").strip()
    print(f"== plain --resolve after a clean merge of a doc commit into main {main[:10]}")
    for n in range(rounds):
        for label in ("main", "branch"):
            reset(wt, main)
            if label == "branch":
                overlay(wt)
            run(["git", "merge", "-q", "--no-commit", "--no-ff", other], wt)
            code, seconds, entries, tail = resolve(wt, f"time-{label}-{n}")
            print(f"  round {n + 1} {label}'s tool: exit {code}, {seconds:.0f} s; entries run: {len(entries)}; "
                  + ", ".join(f"{e} {entries[e]} s" for e in NEW if e in entries))
            if code:
                print("    " + tail.replace("\n", "\n    "))
    reset(wt, main)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--worktree", type=Path, required=True)
    parser.add_argument("--pairs", action="store_true")
    parser.add_argument("--timing", type=int, default=0, metavar="ROUNDS")
    args = parser.parse_args()
    wt = args.worktree.resolve()
    if wt.name == "ve-integration":
        raise SystemExit("never in ve-integration")
    if not wt.exists():
        git(ROOT, "worktree", "add", "-q", "--detach", str(wt), "main")
        run(["zsh", str(M / "lean-prep.sh"), str(wt), "genconflict-replay"], wt)
    print(f"# genconflict-1120 replay, tools from {git(ROOT, 'rev-parse', '--short', 'HEAD').strip()}, "
          f"{time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}, {os.uname().nodename}", flush=True)
    if args.pairs:
        pairs(wt)
    if args.timing:
        timing(wt, args.timing)
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
