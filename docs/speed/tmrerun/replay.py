#!/usr/bin/env python3
"""Step 1 (MEASURE): replay the Oct 20 reruns under the --again carry rule of rule.py (`Reads`).

    uv run python docs/speed/tmrerun/replay.py [--out docs/speed/tmrerun/replay.json]

For each pair of consecutive commits at which an item's sweep ran, both are checked out detached in a scratch
directory (the item's branches are only read), the tool plans each (`plan`: no build) and the second run's mutants are
matched to the first's by `Reads.key`. A mutant is carried when the first run's verdict on it is KILLED or INVALID
and `Reads.carry` keeps it on the second tree. The first run's verdicts are its saved evidence where there is one; else
(PROXY: me-6b and ap-1b saved only their last run) the second run's verdict on the same key, its killing check found in
the first tree by its text. ap-1b's second run is saved here (evidence/, copied from its worktree when it finished: it
is committed nowhere else). Minutes saved: carried mutants times the first run's seconds per mutant (its wall time
over its mutants at its jobs)."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "tools"), str(Path(__file__).resolve().parent)]
import rule  # noqa: E402
import trust_mutants as tm  # noqa: E402

AP = ["lean/VE/Service/ActsExamples.lean", "lean/VE/Compose/Examples.lean", "lean/VE/Acts/LexicalExamples.lean"]
# item, first commit, second, base, first run's evidence (commit:path, "log:" a log, or None), second run's, its
# seconds and mutants (the first run's when saved), --test
PAIRS = [
    ("df-1ac", "ccf71608f", "6bd8247b0", "c5197da78", "7f4aa4226:docs/defeasible/df-1ac/trust-mutants.json",
     "a3d0ff6b3:docs/defeasible/df-1ac/trust-mutants.json", []),
    ("df-1ac", "6bd8247b0", "f484e28cc", "c5197da78", "a3d0ff6b3:docs/defeasible/df-1ac/trust-mutants.json",
     "257158960:docs/defeasible/df-1ac/trust-mutants.json", []),
    ("me-6b", "ce08d10a9", "0c83cac0b", "c5197da78", None, "db34c272d:docs/math-evidence-me-6b/trust-mutants.json", []),
    ("ap-1b", "0a2e3fb87", "270b9b6c7", "2296317a9", None, "file:evidence/ap-1b-270b9b6c7.json", AP),
]
FIRST = {"ap-1b": (7200, 176, 8)}  # a first run that saved no evidence: the task's "176 mutants, 2 h per run"


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


class Tree:
    """One commit, checked out detached, planned."""

    def __init__(self, scratch: Path, commit: str, base: str, tests: list[str]):
        self.root = scratch / commit
        if not self.root.is_dir():
            git("worktree", "add", "-q", "--detach", str(self.root), commit)
        self.found, self.tree, fatal = tm.plan(self.root, base)
        assert not fatal, fatal
        self.tests = [t.removeprefix("lean/") for t in tests]
        self.reads = rule.Reads(self.root, self.tree, [])
        for m in self.found:
            m.key, m.reads, m.killed_at, m.carried_from = self.reads.key(m), "", None, ""
        self.by_key = {m.key: m for m in self.found}

    def prev(self, m: tm.Mutant, status: str, f: str, s: int, e: int, n: int) -> dict:
        """The evidence row the tool writes for m KILLED at the check f:s-e (line n)."""
        m.status, m.detail = status, f"lean/{f}:{n}: Expression"
        self.reads.verdict(m)
        return {"key": m.key, "status": m.status, "detail": m.detail, "reads": m.reads, "killed_at": m.killed_at}


def located(tree: Tree, f: str, text: str, near: int) -> tuple[int, int] | None:
    """The check of `f` in `tree` whose lines are `text`, nearest line `near`."""
    lines = tree.reads.texts[f].split("\n")
    spans = [(s, e) for s, e, r, _ in tree.tree.roles.get(f, ()) if r == "check" and "\n".join(lines[s - 1:e]) == text]
    return min(spans, key=lambda x: abs(x[0] - near), default=None)


def match(rows: list[dict], found: list[tm.Mutant]) -> dict[str, dict]:
    """Evidence rows by the key of the planned mutant they are (file, line, definition, operator, before, after)."""
    left = {}
    for m in found:
        left.setdefault((m.file, m.line, m.definition, m.operator, m.before, m.after), []).append(m)
    out = {}
    for row in rows:
        if mine := left.get((row["file"], row["line"], row["definition"], row["operator"], row["before"], row["after"])):
            out[mine.pop(0).key] = row
    return out


def replay(scratch: Path, item, c1, c2, base, first, second, tests) -> dict:
    one, two = Tree(scratch, c1, base, tests), Tree(scratch, c2, base, tests)
    evidence = lambda spec: json.loads(  # noqa: E731
        (Path(__file__).parent / spec[5:]).read_text() if spec.startswith("file:") else git("show", spec))
    later = evidence(second)
    if first:
        data = evidence(first)
        seconds, mutants, jobs = data["seconds"], len(data["mutants"]), data["jobs"]
        rows = match(data["mutants"], one.found)
        prevs, verdicts = {}, {key: row["status"] for key, row in rows.items()}
        for key, row in rows.items():  # the row as this tool writes it on the first tree (`Reads.verdict`)
            m = one.by_key[key]
            m.status, m.detail = row["status"], row["detail"]
            one.reads.verdict(m)
            prevs[key] = {"key": key, "status": m.status, "detail": m.detail, "reads": m.reads,
                          "killed_at": m.killed_at}
        notes = f"saved evidence ({len(rows)} of {mutants} rows matched)"
    else:  # PROXY: the second run's verdict on the same key, its check found in the first tree
        seconds, mutants, jobs = FIRST.get(item, (later["seconds"], len(later["mutants"]), later["jobs"]))
        prevs, verdicts = {}, {key: row["status"] for key, row in match(later["mutants"], two.found).items()}
        for key, row in match(later["mutants"], two.found).items():
            if key not in one.by_key or row["status"] not in ("KILLED", "INVALID"):
                continue
            m1, m2 = one.by_key[key], two.by_key[key]
            if row["status"] == "INVALID":
                m1.status, m1.detail = "INVALID", row["detail"]
                one.reads.verdict(m1)
                prevs[key] = {"key": key, "status": "INVALID", "detail": row["detail"], "reads": m1.reads}
                continue
            m2.status, m2.detail = row["status"], row["detail"]
            two.reads.verdict(m2)
            if m2.killed_at is None:  # a kill at no check of lean/ (an outside file): nothing to locate
                continue
            (f, n), (s2, e2) = two.reads.killer(row["detail"]), m2.killed_at
            if span := located(one, f, "\n".join(two.reads.texts[f].split("\n")[s2 - 1:e2]), s2):
                prevs[key] = one.prev(m1, "KILLED", f, *span, n - s2 + span[0])
        notes = "PROXY: the second run's verdicts"
    why: Counter = Counter()  # why each mutant reruns
    for m2 in two.found:
        p = prevs.get(m2.key)
        if p and p.get("reads"):
            two.reads.carry(m2, p, c1)
        if m2.carried_from:
            why["carried"] += 1
        elif m2.key not in one.by_key:
            why["a new mutant (its declaration or edit changed)"] += 1
        elif verdicts.get(m2.key, "NOT RUN") not in ("KILLED", "INVALID"):
            why[f"a {verdicts.get(m2.key, 'NOT RUN')} verdict (never carried)"] += 1
        elif not (p and p.get("reads")):
            why["its killing check is not in the first tree"] += 1
        elif two.reads.scope(m2) != one.reads.scope(one.by_key[m2.key]):
            why["its declaration's scope changed"] += 1
        else:
            why["its killing check or what that reads changed"] += 1
    per = seconds / mutants
    return {"item": item, "first": c1, "second": c2, "mutants": len(two.found), "carried": why["carried"],
            "rerun": len(two.found) - why["carried"], "seconds_per_mutant": round(per, 1), "jobs": jobs,
            "minutes_saved": round(why["carried"] * per / 60, 1), "basis": notes, "why": dict(why)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("replay.json"))
    parser.add_argument("--check", action="store_true", help="exit 1 when the replay differs from --out (unwritten)")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="tmrerun-") as scratch:
        try:
            rows = [replay(Path(scratch), *pair) for pair in PAIRS]
        finally:
            for path in Path(scratch).iterdir():
                git("worktree", "remove", "--force", str(path))
    for r in rows:
        print(" | ".join(str(r[k]) for k in ("item", "first", "second", "mutants", "carried", "rerun",
                                              "minutes_saved", "why")))
    for name, part in (("every pair", rows), ("each item's last pair", rows[1:])):
        total, carried = sum(r["mutants"] for r in part), sum(r["carried"] for r in part)
        print(f"{name}: carried {carried} of {total} rerun mutants ({100 * carried / total:.0f}%)")
    if args.check:
        saved = json.loads(args.out.read_text())
        print("the saved replay" + (" holds" if saved == rows else " DIFFERS"))
        return int(saved != rows)
    args.out.write_text(json.dumps(rows, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
