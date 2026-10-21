#!/usr/bin/env python3
"""Replay the eff-20261021-1 corpus (review F2): each hand mutant's selection, generation and verdict, measured.

    uv run python docs/infra/eff-20261021-1/replay.py --work DIR [--item ITEM ...]

For each corpus row of evidence.json and each of its trees (`reviewed_head`, `fixed_head`, or `fixed_tree` when the
fixed commit's declarations.txt is stale), the tool itself says, in a detached worktree under DIR:
- `plan`: the definition holding the row's `before` text, its trust_map class, whether tools/trust_mutants.py
  selects it (trusted, a line changed over `base`), and every mutant either tool version writes on that line;
- `run`: the verdict of the row's `replay` mutant (an operator and its own before/after text on that line) under
  today's tool (tools/trust_mutants.py at TOOL_COMMIT) and the proposed one (the same with prototype.patch:
  tier-4 operators and the separately timed `--pytest` phase), the tool's `main` run on that one mutant only.
Raw tool output is kept in replay/<item>-<tree>-<tool>[-deep].json; evidence.json's measured columns are written
from it, and verify_evidence.py checks the columns against those files. A finished run is never repeated.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOL_COMMIT = "7855620f3e06be59bd94730ef404689d3a18e558"  # the branch's merge base: main's trust_mutants.py
TOOLS = ("today", "proposed")
JOBS = "4"


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def worktree(path: Path, commit: str) -> Path:
    if not path.is_dir():
        git("worktree", "add", "-q", "--detach", str(path), commit)
    if git("rev-parse", "HEAD", cwd=path) != git("rev-parse", commit):
        raise SystemExit(f"{path} is not at {commit}")
    return path


def tool(work: Path, name: str) -> Path:
    path = worktree(work / f"tool-{name}", TOOL_COMMIT)
    if name == "proposed" and not git("diff", "--name-only", cwd=path):
        subprocess.run(["git", "apply", str(HERE / "prototype.patch")], cwd=path, check=True)
    return path


def located(text: str, before: str, near: int) -> int | None:
    """The line of `before`'s first line nearest `near` in `text`."""
    first = before.strip().split("\n")[0].strip()
    lines = [i + 1 for i, line in enumerate(text.split("\n")) if first in line]
    return min(lines, key=lambda n: abs(n - near)) if lines else None


def drive(argv: list[str]) -> int:
    """In a child process: `plan` or `run` with one tool version (`--tool DIR`)."""
    parser = argparse.ArgumentParser()
    parser.add_argument("what", choices=("plan", "run"))
    parser.add_argument("--tool", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--rows", required=True, help="JSON: [{file, line, replay}]")
    args, rest = parser.parse_known_args(argv)
    sys.path[:0] = [str(args.tool)]
    from tools import trust_map, trust_mutants as tm  # noqa: PLC0415 (the chosen tool version)
    rows = json.loads(args.rows)
    if args.what == "plan":
        classified, _, _ = trust_map.walk(args.root, args.root / "tools/trust-classes.json",
                                          args.root / "lean/statements.txt")
        found, _, fatal = tm.plan(args.root, args.base)
        changed = tm.changed_lines(args.root, args.base)
        out = []
        for r in rows:
            f = r["file"].removeprefix("lean/")
            if r["line"] is None:  # the tree no longer has the row's `before` text
                out.append({"definition": None, "class": None, "trusted": False, "changed": False, "selected": False,
                            "mutants": []})
                continue
            d = next((c for c in classified if c.module == f and c.decl.start <= r["line"] <= c.decl.end), None)
            out.append({"definition": d.decl.name if d else None, "class": d.cls if d else None,
                        "trusted": bool(d and d.trusted), "changed": r["line"] in changed.get(f, set()),
                        "selected": any(m.file == f and m.definition == (d and d.decl.name) for m in found),
                        "mutants": [[m.operator, m.before, m.after] for m in found if m.file == f and m.line == r["line"]]})
        print(json.dumps({"fatal": fatal, "operators": list(tm.OPERATORS), "rows": out}))
        return 0
    keys = {(r["file"].removeprefix("lean/"), r["line"], *r["replay"]) for r in rows}
    plan = tm.plan

    def narrowed(root: Path, base: str):
        found, tree, fatal = plan(root, base)
        return [m for m in found if (m.file, m.line, m.operator, m.before, m.after) in keys], tree, fatal
    tm.plan = narrowed
    return tm.main(["--root", str(args.root), "--base", args.base, *rest])


def child(tool_dir: Path, what: str, root: Path, base: str, rows: list[dict], *rest: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(Path(__file__).resolve()), "drive", what, "--tool", str(tool_dir),
                           "--root", str(root), "--base", base, "--rows", json.dumps(rows), *rest],
                          capture_output=True, text=True, check=False)


def trees(row: dict) -> dict[str, str]:
    return {"reviewed": row["reviewed_head"], "fixed": row.get("fixed_tree") or row["fixed_head"]}


KILLS = ("KILLED", "KILLED-BY-PYTEST")


def status(row: dict, rows: list[dict], kind: str, name: str, raw: Path = HERE / "replay", deep: bool = False) -> str:
    """The row's measured verdict in tree `kind` under tool `name`, from the raw files alone: NOT SELECTED (the
    tool never mutates its definition), NOT GENERATED (no operator writes the row's `replay` mutant there), or the
    status the tool gave that mutant (before --allow)."""
    plan = json.loads((raw / f"{row['item']}-{kind}-{name}-plan.json").read_text())
    i = rows.index(row)
    p, line = plan["rows"][i], plan["lines"][i]
    if plan["fatal"]:
        return "CANNOT RUN"
    if line is None:
        return "TEXT CHANGED"
    if not p["selected"]:
        return "NOT SELECTED"
    if not row["replay"] or row["replay"][0] not in plan["operators"] or row["replay"] not in p["mutants"]:
        return "NOT GENERATED"
    run = json.loads((raw / f"{row['item']}-{kind}-{name}{'-deep' if deep else ''}.json").read_text())
    file = row["file"].removeprefix("lean/")
    [m] = [m for m in run["mutants"] if (m["file"], m["line"], m["operator"], m["before"], m["after"])
           == (file, line, *row["replay"])]
    return m["raw_status"]


def derive(row: dict, rows: list[dict], raw: Path = HERE / "replay") -> dict:
    """The measured columns of a corpus row (one owner: verify_evidence.py checks evidence.json against this)."""
    plan = json.loads((raw / f"{row['item']}-reviewed-today-plan.json").read_text())["rows"][rows.index(row)]
    got = {k: {n: status(row, rows, k, n, raw) for n in TOOLS} for k in ("reviewed", "fixed")}
    reviewed, fixed = got["reviewed"], got["fixed"]
    if reviewed["today"] == "NOT SELECTED":
        gap = "unselected"
    elif reviewed["today"] == "NOT GENERATED":
        gap = "G1" if reviewed["proposed"] == "NOT GENERATED" else (
            "G1 and G2 (a proposed operator generates it; only the pytest phase kills it at the fixed tree)"
            if fixed["proposed"] == "KILLED-BY-PYTEST" else f"G1 (a proposed operator generates it: {fixed['proposed']} "
                                                              "at the fixed tree)")
    elif reviewed["today"] in KILLS:
        gap = "G1 (the generated form at this line is killed at the reviewed tree already)"
    elif reviewed["today"] == "SURVIVOR" and fixed["today"] in KILLS:
        gap = "none (today's Lean phase kills it at the fixed tree)"
    elif reviewed["today"] == "SURVIVOR" and fixed["proposed"] == "KILLED-BY-PYTEST":
        gap = "G2"
    else:
        gap = f"open (fixed tree: {fixed['today']} today, {fixed['proposed']} proposed)"
    out = {"definition": plan["definition"], "trust_class": plan["class"], "trusted": plan["trusted"],
           "measured": got, "legacy_verdict": reviewed["today"], "fixed_verdict": fixed["proposed"],
           "pair": reviewed["proposed"] == "SURVIVOR" and fixed["proposed"] in KILLS, "gap": gap}
    if (raw / f"{row['item']}-reviewed-proposed-deep.json").is_file() and reviewed["proposed"] not in (
            "NOT SELECTED", "NOT GENERATED"):
        out["reviewed_verdict_deep"] = status(row, rows, "reviewed", "proposed", raw, deep=True)
        if out["reviewed_verdict_deep"] == "SURVIVOR":  # else no fixed run: it cannot make a pair
            out["fixed_verdict_deep"] = status(row, rows, "fixed", "proposed", raw, deep=True)
        out["pair_deep"] = out["reviewed_verdict_deep"] == "SURVIVOR" and out.get("fixed_verdict_deep") in KILLS
    return out


def columns(evidence: dict) -> None:
    for row in evidence["corpus"]:
        rows = [r for r in evidence["corpus"] if r["item"] == row["item"]]
        if (HERE / "replay" / f"{row['item']}-fixed-proposed-plan.json").is_file():
            for k in ("definition", "trust_class", "trusted", "measured", "legacy_verdict", "fixed_verdict",
                      "reviewed_verdict_deep", "fixed_verdict_deep", "pair", "pair_deep", "gap"):
                row.pop(k, None)
            row.update(derive(row, rows))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["drive"]:
        return drive(argv[1:])
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--item", action="append", default=[])
    args = parser.parse_args(argv)
    evidence = json.loads((HERE / "evidence.json").read_text())
    raw = HERE / "replay"
    raw.mkdir(exist_ok=True)
    tools = {name: tool(args.work, name) for name in TOOLS}
    for item in dict.fromkeys(r["item"] for r in evidence["corpus"]):
        if args.item and item not in args.item:
            continue
        rows = [r for r in evidence["corpus"] if r["item"] == item]
        spec = evidence["replay"].get(item, {})
        for kind in ("reviewed", "fixed"):
            commit = trees(rows[0])[kind]
            root = worktree(args.work / "heads" / commit[:9], commit)
            for c in spec.get("build", {}).get(kind, []):  # what the item's fixtures read from the checkout
                subprocess.run(["lake", "build", c], cwd=root / "lean", check=True, capture_output=True, env={
                    **os.environ, "PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}{os.environ['PATH']}"})
            lines = [{"file": r["file"], "line": located((root / r["file"]).read_text(), r["before"], r["line"]),
                      "replay": r["replay"]} for r in rows]
            for name, path in tools.items():
                out = raw / f"{item}-{kind}-{name}-plan.json"
                if not out.is_file():
                    done = child(path, "plan", root, rows[0]["base"], lines)
                    if done.returncode:
                        raise SystemExit(done.stderr)
                    out.write_text(json.dumps({"tree": commit, "lines": [x["line"] for x in lines],
                                               **json.loads(done.stdout)}, ensure_ascii=False, indent=1) + "\n")
                plan = json.loads(out.read_text())
                todo = [x for x, p in zip(lines, plan["rows"]) if x["replay"] and x["replay"][0] in plan["operators"]
                        and x["replay"] in p["mutants"]]
                for deep in ([False, True] if spec.get("deep") and name == "proposed" else [False]):
                    out = raw / f"{item}-{kind}-{name}{'-deep' if deep else ''}.json"
                    if not todo or out.is_file() or plan["fatal"]:
                        continue
                    if deep and kind == "fixed" and any(  # a pair needs a SURVIVOR at the reviewed tree
                            m["raw_status"] != "SURVIVOR" for m in json.loads(
                                (raw / f"{item}-reviewed-{name}-deep.json").read_text())["mutants"]):
                        continue
                    named = spec.get("pytest", [])  # one list, or one per tree
                    named = named.get(kind, []) if isinstance(named, dict) else named
                    pytest = [a for t in named if name == "proposed" for a in ("--pytest", t)]
                    done = child(path, "run", root, rows[0]["base"], todo, "--jobs", JOBS, "--max-mutants", "1000",
                                 "--json", str(out), *pytest, *(["--deep"] if deep else []))
                    print(f"{item} {kind} {name}{' deep' if deep else ''}: exit {done.returncode}\n"
                          f"{done.stdout[-1500:]}{done.stderr[-1500:]}", flush=True)
                    if done.returncode == 2:
                        out.unlink(missing_ok=True)
                        raise SystemExit(f"{item} {kind} {name}: the tool cannot run")
    columns(evidence)
    (HERE / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
