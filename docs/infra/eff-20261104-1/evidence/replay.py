#!/usr/bin/env python3
"""eff-20261104-1's replay: what the new `previous` decides on recorded --rescore pairs, and whether each verdict
it carries is the one the recorded full run at the later head gave.

    uv run python docs/infra/eff-20261104-1/evidence/replay.py collect CLOUD_JOBS   # copies the inputs here, once
    uv run python docs/infra/eff-20261104-1/evidence/replay.py replay               # writes replay-result.json

`replay` reads only the copies here and git. No PREV of these has `tool_files`, so both records' inputs are recomputed
from scratch worktrees of the two commits: each tree's own tool modules give `tool` (checked against the digest
recorded there) and `tool_files`, the new `inputs` gives the rest (checked against what was recorded; `previous` reads
the recorded ones, which hold what the run saw, an uncommitted file too). `plan`,
`previous`, `check_only` and `Reads.carry` are this branch's tools/trust_mutants.py over the later tree's other modules.
No Lean runs: a replay decides, it builds nothing."""
from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
# (the name, the reason the recorded run went full, the later head, PREV at it). The task's two pairs first; the others
# give each other input class a measured pair of its own: the "(tool, base)" and "(base)" sweeps whose PREV is committed
# at its later head and whose tree this tool can plan (ap-3d and ap-4a predate `trust_map.inventory`), and the two
# smallest of the table's and the lock's.
PAIRS = [{"name": n, "reason": r, "later": h, "prev": f, "job": f"{n}-{h}"} for n, r, h, f in (
    ("df-5", "tool", "66190bd0", "docs/defeasible/df-5/trust-mutants.json"),
    ("ci-2", "tool", "ad415a76", "docs/commands-imperatives/ci-2/trust-mutants.json"),
    ("ci-2", "base", "921abb0f", "docs/commands-imperatives/ci-2/trust-mutants.json"),
    ("cmp-s3", "table", "1506199f", "docs/composition/cmp-s3/trust-mutants.json"),
    ("ci-1", "table", "ec141e96", "docs/commands-imperatives/ci-1/trust-mutants.json"),
    ("qt-a3db", "lock", "84930ae4", "docs/quantities/qt-a3db/trust-mutants-run1.json"),
    ("cmp-s4c", "lock", "7a87e0ac", "docs/composition/cmp-s4c/trust-mutants.json"),
    ("qt-a4", "tool, base", "7163aafe", "docs/quantities/qt-a4/trust-mutants.json"),
    ("ap-3db", "tool, base", "3cda58df", "docs/act-phrases/ap-3db/trust-mutants-run3.json"))]
KEYS = ("id", "file", "line", "definition", "operator", "before", "after")


def git(*args: str, cwd: Path = REPO) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def collect(jobs: Path) -> None:
    """The PREV committed at the later head as it is, and the later full run's rows with a verdict, from its parts."""
    for pair in PAIRS:
        out = HERE / pair["job"]
        out.mkdir(exist_ok=True)
        (out / "prev.json").write_text(git("show", f"{pair['later']}:{pair['prev']}"))
        rows, parts, inputs = {}, {}, None
        for path in sorted(glob.glob(str(jobs / pair["job"] / "part-*.json"))):
            raw = Path(path).read_bytes()
            data = json.loads(raw)
            assert "partial" not in data and data["rescore"]["mode"] == "full"
            parts[Path(path).name] = hashlib.sha256(raw).hexdigest()
            assert inputs in (None, data["inputs"])
            inputs = data["inputs"]
            for r in data["mutants"]:
                if r["raw_status"] != "OTHER SHARD":
                    assert r["id"] not in rows
                    rows[r["id"]] = {k: r[k] for k in (*KEYS, "raw_status")} | {
                        "detail": r.get("raw_detail", r["detail"])}
        (out / "full-run.json").write_text(json.dumps({
            "job": pair["job"], "head": data["head"], "base": data["base"], "tests": data["tests"], "classes": data["classes"],
            "deep": data["deep"], "full_run": data["rescore"]["full_run"], "inputs": inputs, "parts_sha256": parts,
            "mutants": [rows[i] for i in sorted(rows)]}, indent=0, sort_keys=True) + "\n")


TOOL_DIGESTS = """
import hashlib, json, os, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(root / "tools")]
import trust_mutants
loaded = {Path(f).resolve() for m in list(sys.modules.values()) if isinstance(f := getattr(m, "__file__", None), str)}
named = sorted((p.relative_to(root).as_posix(), p) for p in loaded
               if p.is_relative_to(root / "tools") or p.is_relative_to(root / "lean"))
h, each = hashlib.sha256(), {}
for name, path in named:
    data = path.read_bytes()
    h.update(f"{name}\\0{len(data)}\\0".encode() + data)
    each[name] = hashlib.sha256(data).hexdigest()
print(json.dumps({"tool": h.hexdigest(), "tool_files": each}))
"""

DECIDE = """
import json, os, sys
from pathlib import Path
later, earlier, prev_in, full_path, tools_later, tools_earlier = sys.argv[1:7]
later, earlier = Path(later), Path(earlier)
sys.path[:0] = [str(later / "tools")]
import trust_mutants as tm
assert tm.ROOT == later.resolve(), tm.ROOT
prev, full = json.loads(Path(prev_in).read_text()), json.loads(Path(full_path).read_text())
tools = [json.loads(Path(p).read_text()) for p in (tools_earlier, tools_later)]
def split(root, record):
    # As `main` splits --test: a file under lean/, or an outside one.
    tests = [t.removeprefix("lean/") for t in record["tests"] if (root / "lean" / t.removeprefix("lean/")).is_file()]
    return tests, [(root / t).resolve() for t in record["tests"] if t.removeprefix("lean/") not in tests]
def digests(root, base, tool, record):
    return {**tm.inputs(root, base, *split(root, record), record["deep"], tuple(record["classes"])), **tool}
old, now = digests(earlier, prev["base"], tools[0], prev), digests(later, full["base"], tools[1], full)
recomputed_old, recomputed_now = old, now
# What `previous` reads is what was recorded (a run may have seen uncommitted bytes), with the digests no old record has.
old, now = {**prev["inputs"], "tool_files": tools[0]["tool_files"]}, {**full["inputs"], "tool_files": tools[1]["tool_files"]}
checks = {
  "earlier_tool_digest_is_the_recorded": tools[0]["tool"] == prev["inputs"]["tool"],
  "later_tool_digest_is_the_recorded": tools[1]["tool"] == full["inputs"]["tool"],
  "earlier_inputs_are_the_recorded": {k: k == "files" and sorted(
      x for x in recomputed_old[k].keys() | prev["inputs"][k].keys()
      if recomputed_old[k].get(x) != prev["inputs"][k].get(x)) or recomputed_old[k] == prev["inputs"][k]
      for k in ("lean", "tests", "base", "options", "files")},
  "later_inputs_are_the_recorded": {k: k == "files" and sorted(
      x for x in recomputed_now[k].keys() | full["inputs"][k].keys()
      if recomputed_now[k].get(x) != full["inputs"][k].get(x)) or recomputed_now[k] == full["inputs"][k]
      for k in ("lean", "tests", "base", "options", "files")},
}
tests, outside = split(later, full)
found, tree, fatal = tm.plan(later, full["base"], tuple(full["classes"]))
assert not fatal, fatal
for t in outside:
    tree.imported |= {x for x in tm.imports(t.read_text()) if x in tree.files}
reads = tm.Reads(later, tree, outside)
named = {Path(os.path.relpath(t, later)).as_posix() for t in outside}
record = Path(sys.argv[7])
record.write_text(json.dumps({**prev, "inputs": old}))
got = tm.previous(record, now, found, lambda names: tm.check_only(names, tm.reach(reads, found), named, tm.lake_reads(later, outside)))
out = {"checks": checks, "mutants_planned": len(found),
       "plan_is_the_full_runs": [[getattr(m, k) for k in ("id", "file", "line", "definition", "operator", "before", "after")] for m in found] == [
           [r[k] for k in ("id", "file", "line", "definition", "operator", "before", "after")] for r in full["mutants"]],
       "tool_files_moved": sorted(k for k in old["tool_files"].keys() | now["tool_files"].keys()
                                  if old["tool_files"].get(k) != now["tool_files"].get(k))}
if isinstance(got, str):
    out.update(mode="full", full_run=got, carried=[], rerun=[m.id for m in found])
else:
    mode, head, verdicts, changed, plan_only = got
    carried, rerun, wrong = {}, [], []
    for m in found:
        c = reads.carry(m, verdicts[m.id], tm.targets(tree, m, tests, full["deep"])) if mode == "checks" else None
        if c:
            carried[m.id] = c
        else:
            rerun.append(m.id)
    rows = {r["id"]: r for r in full["mutants"]}
    differ = [{"id": i, "carried": c, "full": [rows[i]["raw_status"], rows[i]["detail"]]} for i, c in carried.items()
              if c[0] != rows[i]["raw_status"]]
    detail = [{"id": i, "carried": c[1], "full": rows[i]["detail"]} for i, c in carried.items()
              if c[0] == rows[i]["raw_status"] and c[1] != rows[i]["detail"]]
    prev_rows = {r["id"]: r for r in prev["mutants"]}
    from collections import Counter
    out.update(mode=mode, head=head, changed=changed, plan_only=plan_only, carried=sorted(carried), rerun=rerun,
               carried_by_status=dict(Counter(c[0] for c in carried.values())),
               rerun_by_prev_status=dict(Counter(prev_rows[i]["raw_status"] for i in rerun)),
               rerun_by_full_status=dict(Counter(rows[i]["raw_status"] for i in rerun)),
               rerun_killed_or_invalid_in_prev=[i for i in rerun if prev_rows[i]["raw_status"] in ("KILLED", "INVALID")],
               verdicts_differ=differ, details_differ=detail)
print(json.dumps(out))
"""


def replay() -> None:
    result = {}
    tool = (REPO / "tools/trust_mutants.py").read_bytes()
    for pair in PAIRS:
        here = HERE / pair["job"]
        with tempfile.TemporaryDirectory(prefix="ve-replay-") as tmp:
            scratch = Path(tmp)
            trees = {which: scratch / which for which in ("earlier", "later")}
            try:
                commits = {"earlier": json.loads((here / "prev.json").read_text())["head"], "later": pair["later"]}
                for which, tree in trees.items():
                    git("worktree", "add", "-q", "--detach", str(tree), commits[which])
                    done = subprocess.run([sys.executable, "-c", TOOL_DIGESTS, str(tree)], capture_output=True, text=True,
                                          env={"PATH": "/usr/bin:/bin"})
                    if done.returncode:
                        raise SystemExit(done.stderr[-3000:])
                    (scratch / f"tools-{which}.json").write_text(done.stdout.splitlines()[-1])
                (trees["later"] / "tools/trust_mutants.py").write_bytes(tool)
                done = subprocess.run([sys.executable, "-c", DECIDE, str(trees["later"]), str(trees["earlier"]),
                                       str(here / "prev.json"), str(here / "full-run.json"),
                                       str(scratch / "tools-later.json"), str(scratch / "tools-earlier.json"),
                                       str(scratch / "record.json")], capture_output=True, text=True,
                                      env={"PATH": "/usr/bin:/bin"})
                result[pair["job"]] = {**pair, "earlier": commits["earlier"], **(json.loads(
                    done.stdout.splitlines()[-1]) if not done.returncode else {
                        "mode": "not replayed", "error": done.stderr.strip().splitlines()[-1]})}
            finally:
                for tree in trees.values():
                    subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=REPO, capture_output=True)
    (HERE / "replay-result.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    collect(Path(sys.argv[2])) if sys.argv[1] == "collect" else replay()
