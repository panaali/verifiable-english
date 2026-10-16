"""Contemporaneous shadow comparisons: today's, the `modes` and the `answers` selections against full runs.

  python3 docs/test-architecture/cutoff/shadow.py write --worktree W --runs DIR
  python3 docs/test-architecture/cutoff/shadow.py check

`changes.json` pins ten real Lean changes: the three newest Lean merges on main, each against its
first parent, and seven Lean branches in flight on 2026-10-16, each against its merge base with
main. For each, DIR holds the full run of its head on the Mac test runner (the gate's own
collection, `-m "not live"`, run by measure.py --full-suite while these selections were made) and
the recording's answers replayed on the base's and the head's builds there. `write` checks the
head out in W, a scratch worktree, with this batch's two new modules copied in, and computes the
three selections for the change as `tools/select_tests.py` would on that head: today's and `modes`
with the nearest version-7 map recorded at an ancestor of the base (what R1 reads), `answers` with
the recording's own map. A failure of the full run outside a selection is a miss of that selection,
unless the same test also fails on the base (`base_failures`, run on the runner the same way).
`check` reads only the saved rows.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHANGES = HERE / "changes.json"
EVIDENCE = HERE / "evidence/shadow.json"
NEW_MODULES = ("tools/answer_cutoff.py", "tools/answer_replay.py")
FAILED = re.compile(r"^(?:FAILED|ERROR) (tests/[^ ]+?\.py(?:::[^ ]+)?)(?: - .*)?$")


def git(worktree: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(worktree), *args], check=True, capture_output=True, text=True).stdout.strip()


def full_run_failures(log: Path) -> list[str]:
    """The failed and erroring tests of a full run, from pytest's short summary in its log."""
    return sorted({match.group(1) for line in log.read_text(errors="replace").splitlines()
                   if (match := FAILED.match(line.strip()))})


def summary_line(log: Path) -> str | None:
    lines = [line for line in log.read_text(errors="replace").splitlines()
             if re.search(r"\b(passed|failed)\b.* in [0-9.]+s", line)]
    return lines[-1].strip() if lines else None


def unit_of(test: str) -> str:
    return test.split("::", 1)[0]


def row_for(change: dict, worktree: Path, runs: Path) -> dict:
    git(worktree, "checkout", "-q", "-f", "--detach", change["head"])
    git(worktree, "clean", "-fdq")
    for path in NEW_MODULES:
        shutil.copy(ROOT / path, worktree / path)
    code = f"""
import json, sys
sys.path.insert(0, "tools")
import answer_cutoff, answer_replay, select_tests, test_map
change = json.loads(sys.argv[1])
runs = sys.argv[2]
paths = select_tests.git_lines("diff", "--no-renames", "--name-only", change["base"], change["head"])
r1 = test_map.find_map(change["base"])
coverage = (lambda: select_tests.Coverage(test_map.load(r1), r1)) if r1 else (lambda: None)
today = select_tests.select(paths, base=change["base"], after=change["head"], coverage=coverage())
modes = answer_cutoff.select("modes", paths, base=change["base"], after=change["head"], coverage=coverage())
answers = answer_cutoff.select_answers(runs + "/diff-" + change["label"] + ".json", paths, base=change["base"],
                                       after=change["head"], build=change["head_build"],
                                       head_pinned=change.get("head_pinned"))
print(json.dumps({{"r1_map": r1 and r1.name, "paths": paths,
                  "today": today["selected"], "today_full": today["full_reasons"],
                  "modes": modes["selected"], "answers": answers["selected"],
                  "answers_cutoff": answers["cutoff"], "units": today["full_count"],
                  "drift": today["map"] and today["map"]["files_changed_since"],
                  "answers_drift": answers["map"]["files_changed_since"]}}))
"""
    result = subprocess.run(["uv", "run", "--frozen", "--group", "dev", "python", "-c", code, json.dumps(change),
                             str(runs)], cwd=worktree, capture_output=True, text=True, check=True)
    plans = json.loads(result.stdout.strip().splitlines()[-1])
    log = runs / f"full-{change['label']}" / "mac.log"
    failed = full_run_failures(log)
    pre = set(change.get("base_failures", ()))
    row = {"label": change["label"], "kind": change["kind"], "base": change["base"], "head": change["head"],
           "full_run": summary_line(log), "full_failures": failed, "base_failures": sorted(pre), **plans}
    for name in ("today", "modes", "answers"):
        selected = set(plans[name])
        row[f"{name}_count"] = len(selected)
        row[f"{name}_misses"] = sorted(test for test in failed if unit_of(test) not in selected and test not in pre)
    return row


def answers_of(runs: Path, commit: str) -> Path:
    found = sorted((runs / f"replay-{commit[:10]}").glob("answers-*.json.gz"))
    if len(found) != 1:
        raise FileNotFoundError(f"no single replay of {commit[:10]} in {runs}")
    return found[0]


def prepare(runs: Path, recording: Path) -> None:
    """Each change's replay diff (`answer_cutoff.py diff`, the recording build's answers giving the stale
    cases of another base build), its head's build, and whether the head's pins admit it: for a merge, the
    merge gate checked them; for a branch, the head pins a ve_service build the base does not, or its
    Lean tree is the base's."""
    sys.path.insert(0, str(ROOT / "tools"))
    import answer_replay
    index = answer_replay.read_json(recording / "requests.json.gz")
    own = next(path for commit in {c[k] for c in json.loads(CHANGES.read_text()) for k in ("base", "head")}
               if (path := answers_of(runs, commit)) and answer_replay.read_json(path)["service"] == index["service"])
    own_answers = answer_replay.read_json(own)
    changes = json.loads(CHANGES.read_text())
    for change in changes:
        base, head = (answer_replay.read_json(answers_of(runs, change[k])) for k in ("base", "head"))
        diff = answer_replay.diff(base, head)
        diff.update(recording_dir=str(recording), recording_build=own_answers["service"],
                    stale=answer_replay.diff(own_answers, base)["changed"])
        answer_replay.write_json(diff, runs / f"diff-{change['label']}.json")
        pins = [json.loads(git(ROOT, "show", f"{change[k]}:lean/checkers.lock"))["ve_service"] for k in ("base", "head")]
        change.update(head_build=head["service"], base_build=base["service"], changed_answers=len(diff["changed"]),
                      stale_answers=len(diff["stale"]),
                      head_pinned=change["kind"] == "merge" or bool(set(pins[1]) - set(pins[0]))
                      or change["base_lean_tree"] == change["head_lean_tree"])
    CHANGES.write_text(json.dumps(changes, indent=1) + "\n")


def check(data: dict) -> None:
    changes = json.loads(CHANGES.read_text())
    rows = data["rows"]
    assert [row["label"] for row in rows] == [change["label"] for change in changes] and len(rows) == 10
    for row, change in zip(rows, changes, strict=True):
        assert (row["base"], row["head"]) == (change["base"], change["head"])
        assert row["full_run"] and " in " in row["full_run"], row["label"]
        assert set(row["modes"]) <= set(row["today"]), row["label"]
        for name in ("today", "modes", "answers"):
            assert row[f"{name}_count"] == len(row[name])
            assert row[f"{name}_misses"] == sorted(
                test for test in row["full_failures"]
                if unit_of(test) not in set(row[name]) and test not in set(row["base_failures"]))
    print(json.dumps({row["label"]: {name: (row[f"{name}_count"], len(row[f"{name}_misses"]))
                                     for name in ("today", "modes", "answers")} for row in rows}))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    go = sub.add_parser("write")
    go.add_argument("--worktree", type=Path, required=True)
    go.add_argument("--runs", type=Path, required=True)
    go.add_argument("--only", nargs="*")
    ready = sub.add_parser("prepare")
    ready.add_argument("--runs", type=Path, required=True)
    ready.add_argument("--recording", type=Path, required=True)
    sub.add_parser("check")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.runs.resolve(), args.recording.resolve())
        return 0
    if args.command == "check":
        check(json.loads(EVIDENCE.read_text()))
        return 0
    rows = {row["label"]: row for row in json.loads(EVIDENCE.read_text())["rows"]} if EVIDENCE.exists() else {}
    changes = json.loads(CHANGES.read_text())
    for change in changes:
        if args.only and change["label"] not in args.only:
            continue
        rows[change["label"]] = row_for(change, args.worktree.resolve(), args.runs.resolve())
        print(change["label"], {name: (rows[change["label"]][f"{name}_count"],
                                       rows[change["label"]][f"{name}_misses"]) for name in ("today", "modes", "answers")},
              flush=True)
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_text(json.dumps({"rows": [rows[c["label"]] for c in changes if c["label"] in rows]},
                                       indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
