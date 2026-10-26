#!/usr/bin/env python3
"""Replay the eff-20261026-1 corpus: does `trust_mutants.py --classes all` select, generate and kill each hand mutant?

    uv run python docs/infra/eff-20261026-1/replay.py plan --work DIR [--item ITEM ...]
    uv run python docs/infra/eff-20261026-1/replay.py run --work DIR [--item ITEM ...]
    uv run python docs/infra/eff-20261026-1/replay.py derive

The tool is this branch's tools/trust_mutants.py, whose default plan is main's byte for byte (evidence.json
`default_plan`). For each corpus row of evidence.json and each of its trees (`reviewed_head`, and `fixed_tree` or
`fixed_head`), in a detached worktree under DIR (its lean/.lake hard-linked from this checkout's build, which the
tool only reads and copies; the same toolchain and manifest), the tool itself says:
- `plan`: the declaration holding the row's `before` text, its trust_map class, whether the default selection and
  `--classes all` select it (a line changed over `base`), and every mutant `--classes all` writes on that line;
- `run`: the verdict of the row's `replay` mutant (an operator and its own before/after text on that line: the
  reviewer's form, or the tool's mutant with its behaviour there, `replay_note`) under `--classes all`: the tool's
  unchanged `main`, its plan narrowed to the item's replay mutants only (the load rule: no whole sweep).
Raw output goes to replay/<item>-<tree>-plan.json and replay/<item>-<tree>.json (the tool's --json) with its log;
`derive` (the one owner of the rule) writes evidence.json's measured columns from them, and check.py checks them
against the files. A finished plan or run is never repeated.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JOBS = "4"
KILLS = ("KILLED",)


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def trees(row: dict) -> dict[str, str]:
    return {"reviewed": row["reviewed_head"], "fixed": row.get("fixed_tree") or row["fixed_head"]}


def worktree(work: Path, commit: str) -> Path:
    """A detached worktree of `commit` under `work`, its lean/.lake hard-linked from this checkout's (read only)."""
    path = work / "heads" / commit[:12]
    if not path.is_dir():
        git("worktree", "add", "-q", "--detach", str(path), commit)
        if (ROOT / "lean/.lake").is_dir():
            subprocess.run(["cp", "-al", str(ROOT / "lean/.lake"), str(path / "lean/.lake")], check=True)
    if git("rev-parse", "HEAD", cwd=path) != git("rev-parse", commit):
        raise SystemExit(f"{path} is not at {commit}")
    return path


def remove(work: Path, commit: str) -> None:
    path = work / "heads" / commit[:12]
    if path.is_dir():
        git("worktree", "remove", "--force", str(path))
    shutil.rmtree(path, ignore_errors=True)


def located(text: str, before: str, near: int) -> int | None:
    """The line of `before`'s first non-blank line nearest `near` in `text`."""
    first = next(line.strip() for line in before.split("\n") if line.strip())
    lines = [i + 1 for i, line in enumerate(text.split("\n")) if first in line]
    return min(lines, key=lambda n: abs(n - near)) if lines else None


def drive(argv: list[str]) -> int:
    """In a child process: `plan` or `run` of the tool on one tree."""
    parser = argparse.ArgumentParser()
    parser.add_argument("what", choices=("plan", "run"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--rows", required=True, help="JSON: [{file, line, replay}]")
    args, rest = parser.parse_known_args(argv)
    sys.path[:0] = [str(ROOT / "tools"), str(ROOT)]
    from tools import trust_map, trust_mutants as tm  # noqa: PLC0415
    rows = json.loads(args.rows)
    if args.what == "plan":
        classified, _, _ = trust_map.walk(args.root, args.root / "tools/trust-classes.json",
                                          args.root / "lean/statements.txt")
        default, _, fatal = tm.plan(args.root, args.base)
        wide, _, wide_fatal = tm.plan(args.root, args.base, ("all",))
        changed = tm.changed_lines(args.root, args.base)
        out = []
        for r in rows:
            f = r["file"].removeprefix("lean/")
            d = next((c for c in classified if r["line"] and c.module == f and c.decl.start <= r["line"] <= c.decl.end),
                     None)
            name, changes = d.decl.name if d else None, r["line"] in changed.get(f, set())
            seen: dict = {}  # a mutant is [operator, before, after, n]: the n-th such one on the line, by offset
            mutants = []
            for m in sorted((m for m in wide if m.file == f and m.line == r["line"]), key=lambda m: m.start):
                n = seen[m.operator, m.before, m.after] = seen.get((m.operator, m.before, m.after), -1) + 1
                mutants.append([m.operator, m.before, m.after, n])
            out.append({"definition": name, "class": d.cls if d else None, "tied": bool(d and d.tied),
                        "trusted": bool(d and d.trusted), "kind": d.decl.kind if d else None, "changed": changes,
                        # the selection step (`chosen`, a declaration with a changed line), whatever it generates
                        "selected_default": bool(d and changes and tm.chosen(d, tm.TRUSTED)),
                        "selected_all": bool(d and changes and tm.chosen(d, ("all",))),
                        "mutated_default": any(m.file == f and m.definition == name for m in default),
                        "mutated_all": any(m.file == f and m.definition == name for m in wide),
                        "mutants": sorted(mutants, key=lambda x: (x[0], x[1], x[2], x[3]))})
        print(json.dumps({"fatal": fatal + wide_fatal, "operators": list(tm.OPERATORS), "rows": out,
                          "default_mutants": len(default), "all_mutants": len(wide)}))
        return 0
    keys = {(r["file"].removeprefix("lean/"), r["line"], *r["replay"]) for r in rows}
    plan = tm.plan

    def narrowed(root: Path, base: str, classes: tuple[str, ...] = tm.TRUSTED):
        """The plan's mutants that are a row's `replay` (the n-th of its form on its line), ids and order kept."""
        found, tree, fatal = plan(root, base, classes)
        seen: dict = {}
        kept = []
        for m in sorted(found, key=lambda m: (m.file, m.start)):
            n = seen[m.file, m.line, m.operator, m.before, m.after] = seen.get(
                (m.file, m.line, m.operator, m.before, m.after), -1) + 1
            if (m.file, m.line, m.operator, m.before, m.after, n) in keys:
                kept.append(m)
        return [m for m in found if m in kept], tree, fatal
    tm.plan = narrowed
    return tm.main(["--root", str(args.root), "--base", args.base, "--classes", "all", *rest])


def child(what: str, root: Path, base: str, rows: list[dict], *rest: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(Path(__file__).resolve()), "drive", what, "--root", str(root),
                           "--base", base, "--rows", json.dumps(rows), *rest], capture_output=True, text=True,
                          check=False, env={**os.environ, "PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}"
                                                                  f"{os.environ['PATH']}"})


def status(row: dict, rows: list[dict], kind: str, raw: Path = HERE / "replay") -> str:
    """The row's measured verdict in tree `kind` from the raw files alone: TEXT CHANGED (the tree no longer has the
    row's text), NOT SELECTED (`--classes all` never mutates its declaration), NOT GENERATED (no operator writes the
    row's `replay` mutant there), or the status the tool gave that mutant (before --allow)."""
    plan = json.loads((raw / f"{row['item']}-{kind}-plan.json").read_text())
    i = rows.index(row)
    p, line = plan["rows"][i], plan["lines"][i]
    if plan["fatal"]:
        return "CANNOT RUN"
    if line is None:
        return "TEXT CHANGED"
    if not p["selected_all"]:
        return "NOT SELECTED"
    if not row["replay"] or row["replay"] not in p["mutants"]:
        return "NOT GENERATED"
    run = json.loads((raw / f"{row['item']}-{kind}.json").read_text())
    file = row["file"].removeprefix("lean/")
    [m] = [m for m in run["mutants"] if (m["file"], m["line"], m["operator"], m["before"], m["after"])
           == (file, line, *row["replay"][:3])]  # the run holds the replay mutants alone, one per form and line
    return m["raw_status"]


def derive(row: dict, rows: list[dict], raw: Path = HERE / "replay") -> dict:
    """The measured columns of a corpus row (one owner: check.py checks evidence.json against this). A pair is
    SURVIVOR at the reviewed tree and KILLED at the fixed tree under `--classes all`."""
    plan = json.loads((raw / f"{row['item']}-reviewed-plan.json").read_text())["rows"][rows.index(row)]
    got = {k: status(row, rows, k, raw) for k in ("reviewed", "fixed")}
    return {"definition": plan["definition"], "trust_class": plan["class"] + (" tied" if plan["tied"] else "")
            if plan["class"] else None, "trusted": plan["trusted"], "selected_default": plan["selected_default"],
            "selected_all": plan["selected_all"], "generated": row["replay"] is not None
            and got["reviewed"] not in ("NOT SELECTED", "NOT GENERATED", "TEXT CHANGED", "CANNOT RUN"),
            "reviewed_verdict": got["reviewed"], "fixed_verdict": got["fixed"],
            "pair": got["reviewed"] == "SURVIVOR" and got["fixed"] in KILLS}


COLUMNS = ("definition", "trust_class", "trusted", "selected_default", "selected_all", "generated",
           "reviewed_verdict", "fixed_verdict", "pair")


def columns(evidence: dict) -> None:
    for row in evidence["corpus"]:
        rows = [r for r in evidence["corpus"] if r["item"] == row["item"]]
        if (HERE / "replay" / f"{row['item']}-fixed-plan.json").is_file():
            for k in COLUMNS:
                row.pop(k, None)
            row.update(derive(row, rows))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["drive"]:
        return drive(argv[1:])
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("what", choices=("plan", "run", "derive"))
    parser.add_argument("--work", type=Path)
    parser.add_argument("--item", action="append", default=[])
    parser.add_argument("--keep", action="store_true", help="keep the worktrees (default: removed after the run)")
    args = parser.parse_args(argv)
    evidence = json.loads((HERE / "evidence.json").read_text())
    raw = HERE / "replay"
    raw.mkdir(exist_ok=True)
    if args.what != "derive":
        for item in dict.fromkeys(r["item"] for r in evidence["corpus"]):
            if args.item and item not in args.item:
                continue
            rows = [r for r in evidence["corpus"] if r["item"] == item]
            for kind, commit in trees(rows[0]).items():
                plan_file, run_file = raw / f"{item}-{kind}-plan.json", raw / f"{item}-{kind}.json"
                if plan_file.is_file() and (args.what == "plan" or run_file.is_file()):
                    continue
                root = worktree(args.work, commit)
                lines = [{"file": r["file"], "line": located((root / r["file"]).read_text(), r["before"], r["line"])
                          if (root / r["file"]).is_file() else None, "replay": r.get("replay")} for r in rows]
                if not plan_file.is_file():
                    done = child("plan", root, rows[0]["base"], lines)
                    if done.returncode:
                        raise SystemExit(done.stderr)
                    plan_file.write_text(json.dumps({"tree": commit, "lines": [x["line"] for x in lines],
                                                     **json.loads(done.stdout)}, ensure_ascii=False, indent=1) + "\n")
                plan = json.loads(plan_file.read_text())
                todo = [x for x, p in zip(lines, plan["rows"]) if x["replay"] and x["replay"] in p["mutants"]]
                if args.what == "run" and todo and not plan["fatal"]:
                    done = child("run", root, rows[0]["base"], todo, "--jobs", JOBS, "--max-mutants", "1000",
                                 "--json", str(run_file))
                    (raw / f"{item}-{kind}.log").write_text(f"exit {done.returncode}\n{done.stdout}{done.stderr}")
                    print(f"{item} {kind}: exit {done.returncode}\n{done.stdout[-1500:]}{done.stderr[-1500:]}",
                          flush=True)
                    if done.returncode == 2:
                        run_file.unlink(missing_ok=True)
                        raise SystemExit(f"{item} {kind}: the tool cannot run")
                if args.what == "run" and not args.keep:
                    remove(args.work, commit)
    columns(evidence)
    (HERE / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
