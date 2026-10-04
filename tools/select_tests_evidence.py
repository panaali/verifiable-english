"""Measure tools/select_tests.py on past commits and on seeded bugs.

``replay`` runs, for each of the last N non-merge commits before --head:
  * the layer selector as it was at --head (in a temporary worktree), and
  * this selector with the nearest cached map that is an ancestor of the
    commit's parent ("nightly"), and with that map taken as recorded at the
    parent ("fresh", what `test_map.py update` after each merge would give;
    an estimate, since it skips the drift check).
It writes docs/testselect-evidence.json.

``mutants`` takes the first --count replayed commits that changed a Python
function under ve/ or tools/, checks out each commit in --worktree, applies
one seeded mutation inside a function that commit changed, selects for that
working-tree change with a fresh map (the smaller, precise selection) and with
the nightly map, and runs the fresh selection's pytest files until the first
failure (and checks that the nightly selection holds that test). A mutant the
selection does not catch is then run against every other test file, to tell
an escape from a mutant no test detects.

``table`` prints the Markdown tables of docs/TESTING.md from the JSON.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time

from layer_policy import ROOT
import select_tests

EVIDENCE = ROOT / "docs/testselect-evidence.json"
SELECTOR_FILES = ("select_tests.py", "change_units.py", "source_graph.py", "test_map.py",
                  "test_map_recorder.py")


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(("git", *args), cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def replay(args: argparse.Namespace) -> int:
    commits = git("log", "--no-merges", "--format=%H", "-n", str(args.count), args.head).split()
    old = Path(tempfile.mkdtemp(prefix="ve-old-selector-"))
    git("worktree", "add", "--detach", str(old), args.head)
    rows = []
    try:
        for commit in commits:
            paths = select_tests.changed_paths(None, commit)
            started = time.monotonic()
            before = json.loads(subprocess.run(
                ["python3", "tools/select_tests.py", "--commit", commit, "--json"], cwd=old,
                capture_output=True, text=True, check=True).stdout)
            before_seconds = time.monotonic() - started
            nightly = select_tests.select(paths, base=f"{commit}^", after=commit)
            fresh = select_tests.select(paths, base=f"{commit}^", after=commit, assume_fresh=True)
            row = {"commit": commit[:10], "changed": paths,
                   "before": before["selected_count"], "before_full": before["full_count"],
                   "before_seconds": round(before_seconds, 1),
                   "nightly": nightly["selected_count"], "fresh": fresh["selected_count"],
                   "units": nightly["full_count"],
                   "map": nightly["map"]["commit"][:10] if nightly["map"] else None,
                   "files_since_map": nightly["map"]["files_changed_since"] if nightly["map"] else None,
                   "uncertain": nightly["map"]["uncertain_units"] if nightly["map"] else None,
                   "seconds": nightly["seconds"], "full": nightly["full"],
                   "lean_audit": list(select_tests.AUDIT) in nightly["commands"],
                   "before_lean_audit": ["python3", "lean/audit.py"] in before["commands"]}
            rows.append(row)
            print(json.dumps(row), flush=True)
    finally:
        git("worktree", "remove", "--force", str(old))
    data = json.loads(EVIDENCE.read_text()) if EVIDENCE.exists() else {}
    data.update(head=git("rev-parse", "--short=10", args.head), replay=rows)
    EVIDENCE.write_text(json.dumps(data, indent=1) + "\n")
    return 0


class Mutator(ast.NodeTransformer):
    """Apply the `target`-th applicable mutation inside one function."""

    SWAPS = {ast.Eq: ast.NotEq, ast.NotEq: ast.Eq, ast.Lt: ast.GtE, ast.GtE: ast.Lt,
             ast.Gt: ast.LtE, ast.LtE: ast.Gt, ast.In: ast.NotIn, ast.NotIn: ast.In,
             ast.Is: ast.IsNot, ast.IsNot: ast.Is}

    def __init__(self, target: int | None):
        self.target, self.seen, self.applied = target, 0, None

    def _hit(self, description: str) -> bool:
        hit = self.seen == self.target
        self.seen += 1
        if hit:
            self.applied = description
        return hit

    def visit_Compare(self, node):
        self.generic_visit(node)
        if type(node.ops[0]) in self.SWAPS and self._hit(f"swap {type(node.ops[0]).__name__}"):
            node.ops[0] = self.SWAPS[type(node.ops[0])]()
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if self._hit(f"swap {type(node.op).__name__}"):
            node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        if self._hit("negate if"):
            node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
        return node

    def visit_Constant(self, node):
        if type(node.value) is int and self._hit(f"constant {node.value} -> {node.value + 1}"):
            return ast.Constant(node.value + 1)
        return node

    def visit_Return(self, node):
        self.generic_visit(node)
        if node.value is not None and self._hit("return None"):
            node.value = ast.Constant(None)
        return node


def mutate(source: str, qualname: str, seed: int) -> tuple[str, str] | None:
    """`source` with one seeded mutation inside `qualname`, and its description."""
    tree = ast.parse(source)
    target = None
    stack = [(node, "") for node in tree.body]
    while stack:
        node, prefix = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = prefix + node.name
            if name == qualname:
                target = node
                break
            stack.extend((child, f"{name}.<locals>.") for child in node.body)
        elif isinstance(node, ast.ClassDef):
            stack.extend((child, f"{prefix}{node.name}.") for child in node.body)
    if target is None:
        return None
    counter = Mutator(None)
    for statement in target.body:
        counter.visit(ast.parse(ast.unparse(statement)))
    if counter.seen == 0:
        return None
    choice = random.Random(f"{seed}:{qualname}").randrange(counter.seen)
    mutator = Mutator(choice)
    body = [mutator.visit(ast.parse(ast.unparse(statement)).body[0]) for statement in target.body]
    lines = source.splitlines(keepends=True)
    first, last = target.body[0].lineno, target.body[-1].end_lineno
    indent = " " * target.body[0].col_offset
    text = "".join(indent + line + "\n" for statement in body
                   for line in ast.unparse(ast.fix_missing_locations(statement)).splitlines())
    return "".join(lines[:first - 1]) + text + "".join(lines[last:]), mutator.applied


def run_pytest(worktree: Path, files: list[str], log: Path, *, first_failure: bool) -> int:
    env = dict(os.environ)
    env.setdefault("UV_CACHE_DIR", "/tmp/ve-layers-uv-cache")
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    command = ["uv", "run", "--frozen", "--group", "dev", "python", "-m", "pytest", "-q",
               "-n", str(min(8, max(1, len(files)))), *(["--maxfail=1"] if first_failure else []), *files]
    with log.open("w") as handle:
        return subprocess.run(command, cwd=worktree, env=env, stdout=handle, stderr=subprocess.STDOUT,
                              check=False).returncode


def mutants(args: argparse.Namespace) -> int:
    data = json.loads(EVIDENCE.read_text())
    worktree = Path(args.worktree)
    logs = Path(tempfile.mkdtemp(prefix="ve-select-mutants-"))
    rows = [row for row in data.get("mutants", []) if row["commit"] not in args.redo]
    done = {row["commit"] for row in rows}
    for row in data["replay"]:
        if len(rows) >= args.count:
            break
        commit = row["commit"]
        candidates = [p for p in row["changed"] if p.endswith(".py") and p.startswith(("ve/", "tools/"))]
        if not candidates or commit in done:
            continue
        path = candidates[0]
        old_text, new_text = git("show", f"{commit}^:{path}"), git("show", f"{commit}:{path}")
        module, package = select_tests.source_graph.module_name(path)
        d = select_tests.delta(select_tests.source_graph.summary_of(old_text, module, package),
                               select_tests.source_graph.summary_of(new_text, module, package))
        functions = sorted(d.changed | d.added)
        if not functions:
            continue
        git("checkout", "-q", "--force", "--detach", commit, cwd=worktree)
        for name in SELECTOR_FILES:
            shutil.copy(ROOT / "tools" / name, worktree / "tools" / name)
        mutated = None
        for seed in range(args.seeds):
            qualname = random.Random(f"{commit}:{seed}").choice(functions)
            mutated = mutate(new_text + "\n", qualname, seed)
            if mutated is None:
                continue
            (worktree / path).write_text(mutated[0])

            def plan(*extra):
                return json.loads(subprocess.run(
                    ["python3", "tools/select_tests.py", "--json", "--paths", path, *extra], cwd=worktree,
                    capture_output=True, text=True, check=True).stdout)

            nightly, fresh = plan(), plan("--assume-fresh")
            files = [t for t in fresh["selected"] if t.startswith("tests/")]
            log = logs / f"{commit}-{seed}-fresh.log"
            started = time.monotonic()
            code = run_pytest(worktree, files, log, first_failure=True) if files else 0
            failure = next((line.split()[1] for line in log.read_text().splitlines()
                            if line.startswith(("FAILED ", "ERROR "))), None) if files else None
            result = {"commit": commit, "file": path, "function": qualname, "seed": seed,
                      "mutation": mutated[1], "selected": fresh["selected_count"],
                      "nightly_selected": nightly["selected_count"], "units": fresh["full_count"],
                      "map": fresh["map"]["commit"][:10] if fresh["map"] else None,
                      "selected_exit": code, "selected_seconds": round(time.monotonic() - started),
                      "failure": failure,
                      "failure_in_nightly": bool(failure) and failure.split("::")[0] in nightly["selected"]}
            if code == 0:
                # Not caught by the selection: does any other test catch it?
                others = sorted(set(t for t in select_tests.units() if t.startswith("tests/")) - set(files))
                rest = run_pytest(worktree, others, logs / f"{commit}-{seed}-rest.log", first_failure=True)
                result.update(rest_exit=rest, rest_files=len(others))
                git("checkout", "-q", "--force", "--", ".", cwd=worktree)
                print(json.dumps(result), flush=True)
                if rest != 0:
                    rows.append(result)  # an escape: recorded, and the commit is done
                    break
                continue  # no test detects this mutant; try the next seed
            git("checkout", "-q", "--force", "--", ".", cwd=worktree)
            print(json.dumps(result), flush=True)
            rows.append(result)
            break
        data["mutants"] = rows
        EVIDENCE.write_text(json.dumps(data, indent=1) + "\n")
    print(f"logs in {logs}")
    return 0


def table(data: dict) -> str:
    """The Markdown tables docs/TESTING.md shows, rendered from the evidence JSON."""
    lines = ["| Commit | Changed files | Before | After (nightly map) | After (fresh map) | Map | Uncertain | Seconds |",
             "|---|---|---:|---:|---:|---|---:|---:|"]
    for row in data["replay"]:
        changed = ", ".join(f"`{p}`" for p in row["changed"][:3]) + (" ..." if len(row["changed"]) > 3 else "")
        lines.append(f"| `{row['commit'][:8]}` | {changed} | {row['before']}/{row['before_full']} | "
                     f"{row['nightly']}/{row['units']} | {row['fresh']}/{row['units']} | "
                     f"`{(row['map'] or 'none')[:8]}` | {row['uncertain']} | {row['seconds']} |")
    replay = data["replay"]
    total = len(replay)
    lines += ["", f"Totals over {total} commits: before {sum(r['before'] for r in replay)}, "
              f"after (nightly map) {sum(r['nightly'] for r in replay)}, "
              f"after (fresh map) {sum(r['fresh'] for r in replay)} test-file runs; "
              f"`lean/audit.py` before {sum(r['before_lean_audit'] for r in replay)} times, "
              f"after {sum(r['lean_audit'] for r in replay)} times; "
              f"selection time before {max(r['before_seconds'] for r in replay)} s at most, "
              f"after {max(r['seconds'] for r in replay)} s at most."]
    if data.get("mutants"):
        lines += ["", "| Commit | Function | Mutation | Selected (fresh / nightly) | First failing test | Caught |",
                  "|---|---|---|---:|---|---|"]
        for row in data["mutants"]:
            caught = "yes" if row["selected_exit"] != 0 else (
                "ESCAPED" if row.get("rest_exit") else "no test detects it")
            lines.append(f"| `{row['commit'][:8]}` | `{row['file']}:{row['function']}` | {row['mutation']} | "
                         f"{row['selected']} / {row['nightly_selected']} of {row['units']} | "
                         f"`{row['failure'] or '-'}` | {caught}{'' if row.get('failure_in_nightly', True) else ' (not in nightly)'} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    rep = sub.add_parser("replay")
    rep.add_argument("--head", default="HEAD")
    rep.add_argument("--count", type=int, default=50)
    mut = sub.add_parser("mutants")
    mut.add_argument("--worktree", required=True, help="a disposable worktree with built binaries")
    mut.add_argument("--count", type=int, default=10)
    mut.add_argument("--seeds", type=int, default=5, help="mutants to try per commit")
    mut.add_argument("--redo", nargs="*", default=[], help="commits to measure again")
    sub.add_parser("table")
    args = parser.parse_args()
    if args.command == "replay":
        return replay(args)
    if args.command == "mutants":
        return mutants(args)
    print(table(json.loads(EVIDENCE.read_text())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
