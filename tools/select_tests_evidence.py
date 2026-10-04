"""Measure tools/select_tests.py on past commits and on seeded bugs.

``replay`` runs, for each of the last N non-merge commits before --head:
  * the layer selector as it was at --head (in a temporary worktree), and
  * this selector with the nearest cached map that is an ancestor of the
    commit's parent ("nightly"), and with that map taken as recorded at the
    parent ("fresh", what `test_map.py update` after each merge would give;
    an estimate, since it skips the drift check).
It writes docs/testselect-evidence.json.

``mutants`` takes the first --count replayed commits that changed a Python
function under ve/ or tools/ and, in --worktree checked out at --at (a
revision with a map recorded at it, so selection is as precise as it gets),
applies one seeded mutation inside a function that commit changed, selects for
that change, and runs the selected pytest files until the first failure. A
failure counts once the same test passes without the mutant; a test that also
fails without it is deselected and the run repeated. A mutant the selection
does not catch is run against every other test file, to tell an escape from a
mutant no test detects (then the next seed is tried).

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
                  "test_map_recorder.py", "test_layer_policy.py")


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


def mutate(source: str, qualname: str, seed: str) -> tuple[str, str] | None:
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


def run_command(worktree: Path, command, log: Path) -> int:
    env = dict(os.environ)
    env.setdefault("UV_CACHE_DIR", "/tmp/ve-layers-uv-cache")
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    with log.open("w") as handle:
        return subprocess.run(list(command), cwd=worktree, env=env, stdout=handle, stderr=subprocess.STDOUT,
                              check=False).returncode


def run_pytest(worktree: Path, files: list[str], log: Path, *, first_failure: bool, workers: int = 14) -> int:
    env = dict(os.environ)
    env.setdefault("UV_CACHE_DIR", "/tmp/ve-layers-uv-cache")
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    command = ["uv", "run", "--frozen", "--group", "dev", "python", "-m", "pytest", "-q",
               *(["-n", str(min(workers, len(files)))] if workers > 1 else []),
               *(["--maxfail=1"] if first_failure else []), *files]
    with log.open("w") as handle:
        return subprocess.run(command, cwd=worktree, env=env, stdout=handle, stderr=subprocess.STDOUT,
                              check=False).returncode


def first_failure(log: Path) -> tuple[str | None, bool]:
    """The first failing test id in a pytest log, and whether it failed while collecting."""
    line = next((line for line in log.read_text(errors="replace").splitlines()
                 if line.startswith(("FAILED ", "ERROR "))), None)
    if line is None:
        return None, False
    failure = line.split()[1]
    return failure, line.startswith("ERROR ") and "::" not in failure


def mutants(args: argparse.Namespace) -> int:
    """Seeded bugs in the functions recent commits changed, at one revision with its own map."""
    data = json.loads(EVIDENCE.read_text())
    worktree = Path(args.worktree)
    git("checkout", "-q", "--force", "--detach", args.at, cwd=worktree)
    for name in SELECTOR_FILES:
        shutil.copy(ROOT / "tools" / name, worktree / "tools" / name)
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
        module, package = select_tests.source_graph.module_name(path)
        d = select_tests.delta(
            select_tests.source_graph.summary_of(git("show", f"{commit}^:{path}"), module, package),
            select_tests.source_graph.summary_of(git("show", f"{commit}:{path}"), module, package))
        current = (worktree / path).read_text()
        functions = sorted((d.changed | d.added) & set(
            select_tests.source_graph.summary_of(current, module, package).units))
        if not functions:
            continue
        undetected = []
        for seed in range(args.seeds):
            qualname = random.Random(f"{commit}:{seed}").choice(functions)
            mutated = mutate(current, qualname, f"{commit}:{seed}")
            if mutated is None:
                continue
            (worktree / path).write_text(mutated[0])
            plan = json.loads(subprocess.run(
                ["python3", "tools/select_tests.py", "--json", "--paths", path], cwd=worktree,
                capture_output=True, text=True, check=True).stdout)
            files = [t for t in plan["selected"] if t.startswith("tests/")]
            result = {"commit": commit, "file": path, "function": qualname, "seed": seed,
                      "mutation": mutated[1], "selected": plan["selected_count"], "units": plan["full_count"],
                      "map": plan["map"]["commit"][:10] if plan["map"] else None,
                      "uncertain": plan["map"]["uncertain_units"] if plan["map"] else None,
                      "flaky": [], "failure": None}
            started = time.monotonic()
            for attempt in range(3):
                log = logs / f"{commit}-{seed}-{attempt}.log"
                deselect = [f"--deselect={test}" for test in result["flaky"]]
                result["selected_exit"] = run_pytest(worktree, [*deselect, *files], log, first_failure=True) \
                    if files else 0
                failure, collection = first_failure(log) if files else (None, False)
                if failure is None:
                    break
                # A catch counts only if the same test passes without the mutant.
                (worktree / path).write_text(current)
                baseline = run_pytest(worktree, ["--collect-only", failure] if collection else [failure],
                                      logs / f"{commit}-{seed}-{attempt}-baseline.log",
                                      first_failure=True, workers=1)
                (worktree / path).write_text(mutated[0])
                if baseline == 0:
                    result["failure"] = failure
                    break
                result["flaky"].append(failure)  # fails without the mutant too
            extra = [unit for unit in plan["selected"] if unit in select_tests.EXTRA_UNITS]
            for unit in extra if result["failure"] is None else ():
                if run_command(worktree, select_tests.EXTRA_UNITS[unit], logs / f"{commit}-{seed}-extra.log"):
                    (worktree / path).write_text(current)
                    if run_command(worktree, select_tests.EXTRA_UNITS[unit],
                                   logs / f"{commit}-{seed}-extra-baseline.log") == 0:
                        result["failure"] = unit
                    (worktree / path).write_text(mutated[0])
            result["selected_seconds"] = round(time.monotonic() - started)
            if result["failure"] is None:
                # Not caught by the selection: does any other test catch it?
                others = sorted({p.relative_to(worktree).as_posix() for p in (worktree / "tests").glob("test_*.py")}
                                - set(files))
                for attempt in range(3):
                    log = logs / f"{commit}-{seed}-rest-{attempt}.log"
                    result["rest_exit"] = run_pytest(
                        worktree, [*(f"--deselect={t}" for t in result["flaky"]), *others], log, first_failure=True)
                    failure, collection = first_failure(log)
                    result["rest_failure"] = failure
                    if failure is None:
                        break
                    # An escape only if it fails alone with the mutant and passes alone without it.
                    alone = ["--collect-only", failure] if collection else [failure]
                    with_mutant = run_pytest(worktree, alone, logs / f"{commit}-{seed}-rest-{attempt}-alone.log",
                                             first_failure=True, workers=1)
                    (worktree / path).write_text(current)
                    without = run_pytest(worktree, alone, logs / f"{commit}-{seed}-rest-{attempt}-baseline.log",
                                         first_failure=True, workers=1)
                    (worktree / path).write_text(mutated[0])
                    if with_mutant and not without:
                        break
                    result["flaky"].append(failure)
                    result["rest_exit"], result["rest_failure"] = 0, None
            (worktree / path).write_text(current)
            print(json.dumps(result), flush=True)
            if result["failure"] or result.get("rest_exit"):
                result["undetected_before"] = undetected
                rows.append(result)  # caught, or an escape to report
                break
            undetected.append(f"{qualname}: {mutated[1]}")  # no test detects it; try the next seed
        data["mutants"] = rows
        EVIDENCE.write_text(json.dumps(data, indent=1) + "\n")
    git("checkout", "-q", "--force", "--", ".", cwd=worktree)
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
    lines += ["", f"Totals over {total} commits ending at `{data['head']}`: before {sum(r['before'] for r in replay)}, "
              f"after (nightly map) {sum(r['nightly'] for r in replay)}, "
              f"after (fresh map) {sum(r['fresh'] for r in replay)} test-file runs; "
              f"`lean/audit.py` before {sum(r['before_lean_audit'] for r in replay)} times, "
              f"after {sum(r['lean_audit'] for r in replay)} times; "
              f"selection time before {max(r['before_seconds'] for r in replay)} s at most, "
              f"after {max(r['seconds'] for r in replay)} s at most."]
    if data.get("mutants"):
        lines += ["", "| Commit | Function | Mutation | Selected | First failing test | Caught | Earlier seeds no test detects |",
                  "|---|---|---|---:|---|---|---|"]
        for row in data["mutants"]:
            caught = "yes" if row["failure"] else ("ESCAPED" if row.get("rest_exit") else "no test detects it")
            lines.append(f"| `{row['commit'][:8]}` | `{row['file']}:{row['function']}` | {row['mutation']} | "
                         f"{row['selected']}/{row['units']} | `{row['failure'] or row.get('rest_failure') or '-'}` | {caught} | "
                         f"{'; '.join(row.get('undetected_before') or []) or '-'} |")
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
    mut.add_argument("--at", required=True, help="revision to mutate; needs a map recorded at it")
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
