"""Measure what raising `actions_version` rewrote in recorded test files (arch-20261105-2, the "why now" figures).

    uv run python docs/infra/arch-20261105-2/measure.py --since 2026-10-31 --rev main --out evidence/before.json

Evidence tooling, not a test. Three figures, each from git history at `--rev`, non-merge commits since `--since`:

- `version_commits`: the commits that changed `lean/VE/EnglishGrammar/Fixed/Version.lean`.
- `fixtures`: for every commit that changed a file in `tests/fixtures/ask/`, the parsed JSON of each changed file at
  the commit and at its parent, and the JSON paths whose value differs (an added or deleted file is counted apart).
- `pins`: for every commit that changed `lean/VE/Senses/RunExamples.lean`, each `#guard pin (E) == "h"` whose hash
  changed for the same `E`. A change is explained by the version alone when both hashes are the SHA-256 of the
  answer Lean gives to `E` at `--lean-rev` (the checkout's built tree) with its `actions_version` set to the version
  of that side's commit: then the answers on both sides and at `--lean-rev` differ only in the version. Any other
  change (a real change, or one a later commit moved again) is counted as not explained; nothing is guessed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
VERSION = "lean/VE/EnglishGrammar/Fixed/Version.lean"
FIXTURES = "tests/fixtures/ask"
EXAMPLES = "lean/VE/Senses/RunExamples.lean"
PIN = re.compile(r'^#guard pin \((.*)\) == "([0-9a-f]{64})"$', re.MULTILINE)
DEF = re.compile(r'def actionsVersion : String := "([^"]*)"')
VERSION_FIELD = re.compile(r'"actions_version":"[^"]*"')


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def show(commit: str, path: str) -> str | None:
    done = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else None


def commits(rev: str, since: str, path: str) -> list[str]:
    return git("log", "--format=%H", "--no-merges", f"--since={since}", rev, "--", path).split()


def paths(a, b, at: str = "") -> list[str]:
    """The JSON paths where `a` and `b` differ (a type change, a missing key or a list length counts at its node)."""
    if type(a) is not type(b):
        return [at or "/"]
    if isinstance(a, dict):
        out = []
        for key in sorted(a.keys() | b.keys()):
            out += [f"{at}/{key}"] if key not in a or key not in b else paths(a[key], b[key], f"{at}/{key}")
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [at or "/"]
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in paths(x, y, f"{at}/{i}")]
    return [] if a == b else [at or "/"]


def fixtures(rev: str, since: str) -> dict:
    edits, added, deleted, fields, per_commit = 0, 0, 0, Counter(), {}
    for commit in commits(rev, since, FIXTURES):
        changed = git("diff-tree", "--no-commit-id", "-r", "--name-only", f"{commit}^", commit, "--", FIXTURES).split()
        mine = Counter()
        for path in changed:
            old, new = show(f"{commit}^", path), show(commit, path)
            if old is None:
                added += 1
                continue
            if new is None:
                deleted += 1
                continue
            edits += 1
            for p in sorted(set(paths(json.loads(old), json.loads(new)))):
                fields[p] += 1
                mine[p] += 1
        per_commit[commit] = {"files": len(changed), "fields": dict(sorted(mine.items()))}
    return {"commits": len(per_commit), "file_edits": edits, "files_added": added, "files_deleted": deleted,
            "changed_fields": dict(sorted(fields.items())), "per_commit": per_commit}


def version_at(commit: str) -> str | None:
    text = show(commit, VERSION)
    found = DEF.search(text or "")
    return found.group(1) if found else None


def answers(exprs: list[str]) -> dict[str, str]:
    """The compact JSON of Lean's answer to each pinned expression, from the checkout's built `RunExamples`."""
    lines = ["import VE.Senses.RunExamples",
             "open Lean VE.EnglishGrammar VE.Senses VE.Senses.Fixtures VE.Senses.Run VE.Senses.RunExamples"]
    lines += [f"#eval IO.println ({e}).compress" for e in exprs]
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "pins.lean"
        source.write_text("\n".join(lines) + "\n")
        env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}:{os.environ['PATH']}"}
        done = subprocess.run(["lake", "env", "lean", str(source)], cwd=ROOT / "lean", env=env, check=True,
                              capture_output=True, text=True)
    out = done.stdout.splitlines()
    if len(out) != len(exprs):
        raise SystemExit(f"{len(out)} answers for {len(exprs)} expressions")
    return dict(zip(exprs, out))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def with_version(answer: str, version: str | None) -> str:
    return VERSION_FIELD.sub(lambda _: f'"actions_version":"{version}"', answer)


IMPORT = re.compile(r"^import (\S+)", re.MULTILINE)


def closure(commit: str) -> set[str]:
    """The repository Lean files `RunExamples` imports at `commit`, itself included (a module of the toolchain is not
    a file of the repository and is skipped)."""
    seen, todo = set(), [EXAMPLES]
    while todo:
        path = todo.pop()
        if path in seen:
            continue
        text = show(commit, path)
        if text is None:
            continue
        seen.add(path)
        todo += [f"lean/{m.replace('.', '/')}.lean" for m in IMPORT.findall(text)]
    return seen


def requests(text: str | None) -> list[str]:
    """`RunExamples` without its `#guard` lines: the definitions the pinned requests are built from."""
    return [line for line in (text or "").splitlines() if line.strip() and not line.startswith("#guard")]


def static_reason(commit: str) -> str | None:
    """Why every answer of `RunExamples` other than its version is the same at `commit` as at its parent, or None:
    the commit changes no Lean file the module imports except `Version.lean`, and no definition of the module
    itself (Lean is deterministic, so the same definitions give the same answers)."""
    changed = set(git("diff-tree", "--no-commit-id", "-r", "--name-only", f"{commit}^", commit).split())
    relevant = (changed & (closure(f"{commit}^") | closure(commit))) - {VERSION, EXAMPLES}
    if relevant:
        return None
    if requests(show(f"{commit}^", EXAMPLES)) != requests(show(commit, EXAMPLES)):
        return None
    return "no imported Lean file but Version.lean changed, and no definition of RunExamples"


def pins(rev: str, since: str) -> dict:
    head = {e: h for e, h in PIN.findall(Path(ROOT / EXAMPLES).read_text())}
    live = answers(list(head))
    sanity = sorted(e for e, h in head.items() if sha(live[e]) != h)
    changes, rows = Counter(), []
    for commit in commits(rev, since, EXAMPLES):
        old = dict(PIN.findall(show(f"{commit}^", EXAMPLES) or ""))
        new = dict(PIN.findall(show(commit, EXAMPLES) or ""))
        v_old, v_new = version_at(f"{commit}^"), version_at(commit)
        moved = [e for e in new if e in old and old[e] != new[e]]
        matched = [e for e in moved if e in live and sha(with_version(live[e], v_old)) == old[e]
                   and sha(with_version(live[e], v_new)) == new[e]]
        reason = static_reason(commit) if moved and v_old != v_new else None
        explained = moved if reason else matched
        changes["pin_changes"] += len(moved)
        changes["explained_by_version"] += len(explained)
        changes["explained_by_head_answer"] += len(matched)
        changes["explained_statically"] += len(moved) if reason else 0
        changes["pin_changes_in_version_commits"] += len(moved) if v_old != v_new else 0
        changes["added"] += len(new.keys() - old.keys())
        changes["removed"] += len(old.keys() - new.keys())
        rows.append({"commit": commit, "version": [v_old, v_new], "pin_changes": len(moved),
                     "explained_by_version": len(explained), "explained_by_head_answer": len(matched),
                     "static": reason,
                     "changed_imports": sorted((set(git("diff-tree", "--no-commit-id", "-r", "--name-only",
                                                        f"{commit}^", commit).split())
                                                & (closure(f"{commit}^") | closure(commit))) - {VERSION}),
                     "not_explained": sorted(e[:120] for e in moved if e not in explained)})
    return {"commits": len(rows), **dict(sorted(changes.items())), "head_pins": len(head),
            "head_pins_not_reproduced": sanity,
            "answers_with_version": sum(1 for e in head if VERSION_FIELD.search(live[e])),
            "per_commit": rows}


def without_version(answer: str) -> str:
    return re.sub(r'"actions_version":"[^"]*",?', "", answer)


def answers_at(worktree: Path, commit: str) -> dict[str, dict]:
    """Lean's answer to each pinned expression of `RunExamples` as it is at `commit`, built in `worktree`: the
    module's own text without its `#guard` lines (a stale pin must not stop the build), then one `#eval` per pin.
    Per expression: its pin there, the SHA-256 of the answer, and of the answer with `actions_version` left out."""
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}:{os.environ['PATH']}"}
    subprocess.run(["git", "checkout", "-q", "--detach", commit], cwd=worktree, check=True)
    text = (worktree / EXAMPLES).read_text()
    imports = IMPORT.findall(text)
    subprocess.run(["lake", "build", *imports], cwd=worktree / "lean", env=env, check=True, capture_output=True)
    pinned = PIN.findall(text)
    body, guard = [], False
    for line in text.splitlines():
        # A `#guard` and its indented continuation lines go; the namespace stays open for the `#eval`s.
        guard = line.startswith("#guard") or (guard and line[:1] in (" ", "\t"))
        if not guard and not line.startswith("end VE.Senses.RunExamples"):
            body.append(line)
    body += [f"#eval IO.println ({e}).compress" for e, _ in pinned]
    source = worktree / "lean" / "MeasurePins.lean"
    source.write_text("\n".join(body) + "\n")
    try:
        done = subprocess.run(["lake", "env", "lean", str(source)], cwd=worktree / "lean", env=env, check=True,
                              capture_output=True, text=True)
    finally:
        source.unlink()
    out = [line for line in done.stdout.splitlines() if line.startswith("{")]
    if len(out) != len(pinned):
        raise SystemExit(f"{commit}: {len(out)} answers for {len(pinned)} pins")
    return {e: {"pin": h, "answer": sha(a), "without_version": sha(without_version(a)),
                "version": (re.search(r'"actions_version":"([^"]*)"', a) or [None, None])[1], "raw": a}
            for (e, h), a in zip(pinned, out)}


def stale(worktree: Path, commit: str) -> dict:
    """A commit that re-pins with the version unchanged in it (its parent's pins stale since an earlier version bump):
    for each re-pinned answer, the versions under which the commit's own answer hashes to the parent's stale pin."""
    before = PIN.findall(show(f"{commit}^", EXAMPLES) or "")
    after = answers_at(worktree, commit)
    versions = sorted({v for c in git("log", "--format=%H", commit, "--", VERSION).split()[:20]
                       for v in [version_at(c)] if v}, key=int)
    rows = {}
    for e, pin in before:
        if e in after and after[e]["pin"] != pin:
            rows[e[:120]] = [v for v in versions if sha(with_version(after[e]["raw"], v)) == pin]
    return {"commit": commit, "versions_tried": versions, "stale_pin_matches": rows,
            "explained": sum(1 for v in rows.values() if v), "re_pinned": len(rows)}


def built(worktree: Path, rev: str, since: str, rows: list[dict]) -> dict:
    """For each commit whose pin changes `pins` could not explain, the answers at its parent and at it, compared with
    the version left out: equal means the version alone explains the change. Each side's answers are checked against
    that side's pins (a stale parent pin is reported, not trusted)."""
    out = {}
    cache: dict[str, dict] = {}
    for row in rows:
        if not row["not_explained"]:
            continue
        commit = row["commit"]
        for side in (f"{commit}^", commit):
            full = git("rev-parse", side).strip()
            if full not in cache:
                cache[full] = answers_at(worktree, full)
                print(f"answers at {full[:9]}: {len(cache[full])}", flush=True)
        before, after = cache[git("rev-parse", f"{commit}^").strip()], cache[commit]
        moved = [e for e in after if e in before and before[e]["pin"] != after[e]["pin"]]
        same = [e for e in moved if before[e]["without_version"] == after[e]["without_version"]]
        out[commit] = {"pin_changes": len(moved), "explained_by_version": len(same),
                       "versions": sorted({str(before[e]["version"]) + "->" + str(after[e]["version"]) for e in moved}),
                       "real_changes": sorted(e[:120] for e in moved if e not in same),
                       "parent_pins_stale": sorted(e[:120] for e in before if before[e]["pin"] != before[e]["answer"]),
                       "pins_not_reproduced": sorted(e[:120] for e in after if after[e]["pin"] != after[e]["answer"])}
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", default="2026-10-31")
    parser.add_argument("--rev", default="main")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--no-pins", action="store_true", help="skip the Lean pin measurement")
    parser.add_argument("--build-at", type=Path,
                        help="a scratch git worktree (with a lean/.lake to start from) to build the commits whose pin "
                             "changes the HEAD answers do not explain")
    parser.add_argument("--stale-check", metavar="COMMIT",
                        help="with --build-at: only check a re-pinning commit's stale parent pins (see `stale`)")
    args = parser.parse_args()
    if args.stale_check:
        found = stale(args.build_at, git("rev-parse", args.stale_check).strip())
        args.out.write_text(json.dumps(found, indent=1, sort_keys=True) + "\n")
        print(json.dumps({k: v for k, v in found.items() if k != "stale_pin_matches"}))
        return 0
    rev = git("rev-parse", args.rev).strip()
    saved = {"rev": rev, "since": args.since, "version_commits": len(commits(rev, args.since, VERSION)),
             "fixtures": fixtures(rev, args.since)}
    if not args.no_pins:
        saved["pins"] = pins(rev, args.since)
        if args.build_at:
            saved["pins"]["built"] = built(args.build_at, rev, args.since, saved["pins"]["per_commit"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(saved, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in saved.items() if k != "fixtures" and k != "pins"}),
          {k: v for k, v in saved["fixtures"].items() if k != "per_commit"},
          {k: v for k, v in saved.get("pins", {}).items() if k != "per_commit"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
