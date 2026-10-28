"""The tests whose result can depend on git history: `tests/history-dependent.json` and its lint.

A test reads history when it starts git or reads a `.git` directory or file: its result can then change when
commits, refs or the object store change, with every tracked file the same. Such a result binds the commit it
ran on and is never carried to another commit (docs/test-architecture/histdep/REPORT.md says where each
record binds it). The list is an inventory and a lint only: no gate, merge or nightly run skips or reuses a
test because of it. The selector reads it only to run the lint when a change can make it stale (`INPUTS`,
`named_sources`, tools/select_tests.py `history_inventory`).

Where the list comes from, two inputs, no hand edits:

* `tests/history-map.json`, saved from the coverage map the selector uses (`tools/test_map.py`) by
  `history_tests.py save-map`: each test unit the map records starting git, and each function the unit ran
  that starts git or reads `.git` in the source (`sites`), so a read the map's recorder cannot see (it skips
  `.git`, tools/test_map_recorder.py) is still found through the function that does it.
* the source the unit can run, scanned now (`_Sources.reach`): its own file, every module it imports (the top
  level), every function or class its code names, through imports, transitively, the conftest and
  `pytest_plugins` fixtures it uses, every repository script or module it starts or loads (a `.py` or `.sh` path, a
  path built from `__file__`, `-m module`, `spec_from_file_location`), and, where it imports a module by a name the
  source does not spell out (`importlib.import_module(name)`), every module a string of that file names. A new
  test that reaches git through a helper, an import or a child process is found before any map has recorded it;
  `tests/test_history_tests.py` checks that every unit the map saw read history is found from its source alone.

`--write` writes the list from both; `--check` is the lint. It fails when a unit that starts git or reads
`.git` is not listed (`missing`), when an entry differs from what `--write` gives (`changed`), or when the
file is malformed; it reports, without failing, an entry whose unit no longer reads history (`stale`: the
unit is gone, or none of the functions that made it read history still does). `tests/test_history_tests.py`
runs the lint on the tree, so it fails in the gate. The lint reads the two inputs and Python sources only:
it starts no git itself.

A site is found by the shape of the code (`sites`): a command whose program is git (`tools/git_words.py`, which
the run-time recorder tests/read_recorder.py uses too: `git`, `/usr/bin/git`, git after a launcher such as `env`
or in `sh -c "cd x && git log"`, a `python -c` program that starts it), a program that holds git
(`_Scanner._names_git_program`: a variable whose name says git or that is assigned a value that does, `git =
shutil.which("git")`, starred or summed, `[*GIT, "log"]`, `GIT + ["log"]`, split, looked up or chosen), a lookup
of git (`shutil.which("git")`), a path made from ".git", or a pytest run (`-m pytest`, `pytest.main`), whose test
files the source does not name, which lists the unit on the safe side. A module- or class-level name bound to the
git program by the same test (`GIT = ("git", "-c", ...)`, `PROGRAM = "git"`) is a site of the name
(`_Scanner.programs`): code that names it, in any module and under any alias, reaches it. The map then says which
units ran each site's function; what a unit reaches in the source counts whatever ran. The reach
over-approximates: a unit that names a function or a name that starts git is listed even if it never calls it.
It does not follow a call it cannot resolve in the source (a method of an object of unknown class, `getattr` by
a computed name, a program assembled at run time from parts that do not name git); the conftests' session hooks
run for the whole run, not for one unit, and are not followed.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
try:
    from git_words import names_git, program_is_git as _program_is_git, words as _command_words
finally:
    sys.path.remove(str(ROOT / "tools"))
LIST = "tests/history-dependent.json"
MAP_EXTRACT = "tests/history-map.json"
FORMAT = "ve-history-tests@1"
MAP_FORMAT = "ve-history-map@1"
# The files besides the sources the list names (`named_sources`) whose change can make the lint fail: its two
# inputs and its own code.
INPUTS = (LIST, MAP_EXTRACT, "tools/history_tests.py", "tools/git_words.py")
START, READ = "starts git", "reads .git"
# A pytest run started by the code: the source does not say which test files it runs (a list in data, a directory,
# the whole suite), so the unit is listed, which is the safe side.
PYTEST = "runs pytest"
# Calls that start a process from a command whose first word is the program.
PROCESS_CALLS = frozenset({"run", "Popen", "check_output", "check_call", "call", "system", "popen", "getoutput",
                           "getstatusoutput", "create_subprocess_exec", "create_subprocess_shell", "spawnlp",
                           "spawnvp", "execlp", "execvp", "execvpe", "posix_spawn", "posix_spawnp"})
# String methods that compare or split a name: a ".git" handed to one is matched, not opened.
NAME_METHODS = frozenset({"startswith", "endswith", "split", "rsplit", "partition", "rpartition", "replace",
                          "index", "find", "rfind", "count", "removeprefix", "removesuffix", "strip"})
# Options git takes before its subcommand that have a separate value.
GIT_VALUE_OPTIONS = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path",
                               "--config-env"})
# Programs that start the program a later argument names (`env git log`, `timeout 9 git fetch`) or run a shell
# command (`sh -c "git log"`): a later argument that names git starts it.
LAUNCHERS = frozenset({"env", "sh", "bash", "zsh", "dash", "ksh", "nice", "nohup", "timeout", "xargs", "sudo",
                       "setsid", "stdbuf", "time", "exec", "command", "uv", "flock", "ionice", "taskset", "chrt"})
# Calls that find a program to start: what `shutil.which("git")` returns is what starts git.
LOOKUP_CALLS = frozenset({"which"})
# Calls that import a module named by a string or load a file as a module or a program: what they return is used
# through a variable, so all of the file counts.
IMPORT_CALLS = frozenset({"import_module", "__import__"})
LOAD_CALLS = frozenset({"spec_from_file_location", "run_path", "SourceFileLoader"})
# pytest calls that use a fixture named by a string.
FIXTURE_CALLS = frozenset({"usefixtures", "getfixturevalue"})
# The words, besides "git", of a variable name that holds the git program (`git`, `GIT_BIN`, `git_executable`).
PROGRAM_WORDS = frozenset({"bin", "binary", "exe", "executable", "program", "cmd", "command"})
# A string that may name a module (`ve.norm_defaults_contract`) or a script (`tools/gate.py`).
_MODULE_NAME = re.compile(r"[A-Za-z_][\w]*(\.[A-Za-z_]\w*)+|[\w./-]+\.py")
# Directories never searched for a module or a script.
_SKIPPED_DIRECTORIES = frozenset({".git", ".venv", "node_modules", "__pycache__", "target", ".lake"})


@dataclass(frozen=True, order=True)
class Site:
    """Code that starts git (`kind` START, with its subcommand when the source names it) or reads `.git`."""
    file: str
    qualname: str
    kind: str
    line: int
    command: str = ""

    def what(self) -> str:
        if self.kind == START:
            return f"git {self.command}" if self.command else "git"
        return ".git" if self.kind == READ else "pytest"

    def text(self) -> str:
        return f"{self.file}:{self.qualname} ({self.what()}, line {self.line})"


def _string(node) -> str | None:
    """The text of a string constant, or the literal start of an f-string."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr) and node.values and isinstance(node.values[0], ast.Constant) \
            and isinstance(node.values[0].value, str):
        return node.values[0].value
    return None


def _subcommand(arguments) -> str:
    """The git subcommand an argument vector names after its options, or "" when the source does not say."""
    skip = False
    for node in arguments:
        if skip:
            skip = False
            continue
        text = _string(node)
        if text is None or not isinstance(node, ast.Constant):
            return ""
        if text.startswith("-"):
            skip = text in GIT_VALUE_OPTIONS
            continue
        return text
    return ""


def _callee(call: ast.Call) -> str:
    return call.func.attr if isinstance(call.func, ast.Attribute) else (
        call.func.id if isinstance(call.func, ast.Name) else "")


def _names_git_path(text: str) -> bool:
    return text == ".git" or text.startswith(".git/") or "/.git/" in text or text.endswith("/.git")


def _identifier(node) -> str:
    return node.id if isinstance(node, ast.Name) else (node.attr if isinstance(node, ast.Attribute) else "")


def _python(node) -> bool:
    """Whether an argument vector's element is a Python interpreter (`sys.executable`, "python3")."""
    if isinstance(node, ast.Attribute) and node.attr == "executable":
        return True
    text = _string(node)
    return text is not None and isinstance(node, ast.Constant) and os.path.basename(text).startswith("python")


_VISITORS: dict[type, object] = {}


class _Scanner(ast.NodeVisitor):
    """Each site of one file, under the qualified name of the code object that runs it (`co_qualname`), and
    what each piece of code can run (`refs`): the names it loads, the modules it imports, the scripts it starts.

    A piece of code (`node`) is a code object by its qualified name, except that the module's
    `if __name__ == "__main__":` block is `<main>`: it runs when the file is started, not when it is imported."""

    def __init__(self, file: str, tree: ast.Module):
        self.file = file
        self.scope = ["<module>"]
        self.nodes = ["<module>"]
        self.prefix = [""]
        self.parents: list[ast.AST] = []
        self.found: set[Site] = set()
        self.sites_of: dict[str, set[Site]] = {}
        self.refs: dict[str, set[tuple]] = {}
        self.params: dict[str, tuple[str, ...]] = {}
        self.defs: dict[str, str] = {}               # a module-level function or class: name -> qualname
        self.fixtures: dict[str, tuple[str, bool]] = {}  # a module-level pytest fixture: name -> (qualname, autouse)
        self.bindings: dict[str, list[tuple]] = {}   # a name an import binds -> what it imports
        self.stars: list[tuple[str, int]] = []       # `from m import *`: (m, level)
        # Code that imports or loads a module the source does not name (`importlib.import_module(name)`): it may
        # load any module or script that a string of this file names (`"ve.norm_defaults_contract"`).
        self.dynamic: set[str] = set()
        # The values assigned to each name in each code object (by qualified name), for a program or a path held
        # in a variable (`git = shutil.which("git")`, `TOOL = ROOT / "tools/x.py"`).
        self.assigned: dict[tuple[str, str], list[ast.AST]] = {}
        self._assignments(tree, "<module>", "")
        # A module's or class's named argument vector (`GIT = ("git", "-c", ...)`) starts nothing where it is
        # bound: the code that uses the name does.
        self.vectors: dict[str, ast.AST] = {}
        bindings = [(prefix, statement) for prefix, body in
                    [("", tree.body), *((node.name + ".", node.body) for node in tree.body if isinstance(node, ast.ClassDef))]
                    for statement in body if isinstance(statement, (ast.Assign, ast.AnnAssign))
                    and statement.value is not None and all(isinstance(target, ast.Name) for target in (
                        statement.targets if isinstance(statement, ast.Assign) else [statement.target]))]
        self.bound: set[int] = set()  # every bound vector, also one a class binds to a module's name (`Repo.GIT`)
        for _, statement in bindings:
            if self._vector(statement.value):
                targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                self.vectors.update((target.id, statement.value) for target in targets)
                self.bound.add(id(statement.value))
        # Each module- or class-level name bound to the git program (`GIT = ("git", "-c", ...)`, `PROGRAM = "git"`,
        # `GIT = os.environ.get("GIT", "git")`), under its qualified name (`GIT`, `Repo.GIT`): code that names it,
        # in this file or through an import of any form, reaches this site (`_Sources.name`), whatever the name
        # is called where it is used (`from m import GIT as tool`, `[*m.GIT, "log"]`).
        self.programs: dict[str, Site] = {}
        for prefix, statement in bindings:
            vector = id(statement.value) in self.bound
            for target in statement.targets if isinstance(statement, ast.Assign) else [statement.target]:
                if vector or self._names_git_program(target) or self._names_git_program(statement.value):
                    self.programs[prefix + target.id] = Site(
                        file, prefix + target.id, START, statement.lineno,
                        _subcommand(statement.value.elts[1:]) if vector else "")
        self.defs.update((name, name) for name in self.programs if "." not in name)
        # `pytest_plugins = ["answer_store"]` imports each plugin module.
        for statement in tree.body:
            if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "pytest_plugins"
                                                         for target in statement.targets):
                for node in ast.walk(statement.value):
                    if _string(node) is not None and isinstance(node, ast.Constant):
                        self._ref(("plugin", node.value))

    def _assignments(self, node, scope: str, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._assignments(child, prefix + child.name, prefix + child.name + ".<locals>.")
            elif isinstance(child, ast.ClassDef):
                self._assignments(child, prefix + child.name, prefix + child.name + ".")
            else:
                if isinstance(child, (ast.Assign, ast.AnnAssign, ast.NamedExpr)) and child.value is not None:
                    for target in child.targets if isinstance(child, ast.Assign) else [child.target]:
                        if isinstance(target, ast.Name):
                            self.assigned.setdefault((scope, target.id), []).append(child.value)
                self._assignments(child, scope, prefix)

    def code(self) -> set[str]:
        """Every piece of code of the file and every name it binds to git (`programs`): all a script runs."""
        return {"<module>", "<main>", *self.refs, *self.sites_of, *self.params, *self.programs}

    def _values(self, name: str) -> list[ast.AST]:
        """The values assigned to a name where the current code would find it: in itself, else in the code
        around it, out to the module."""
        return next((self.assigned[(scope, name)] for scope in reversed(self.scope) if (scope, name) in self.assigned),
                    [])

    def _add(self, kind: str, node: ast.AST, command: str = "") -> None:
        site = Site(self.file, self.scope[-1], kind, node.lineno, command)
        self.found.add(site)
        self.sites_of.setdefault(self.nodes[-1], set()).add(site)

    def _ref(self, ref: tuple) -> None:
        self.refs.setdefault(self.nodes[-1], set()).add(ref)

    def _enter(self, name: str, node: ast.AST, inner: str) -> None:
        qualname = self.prefix[-1] + name
        self.scope.append(qualname)
        self.nodes.append(qualname)
        self.prefix.append(qualname + inner)
        self.parents.append(node)

    def _leave(self) -> None:
        self.scope.pop()
        self.nodes.pop()
        self.prefix.pop()
        self.parents.pop()

    def _outer(self, nodes) -> None:
        for node in nodes:
            if node is not None:
                self.visit(node)

    def visit_FunctionDef(self, node) -> None:
        # Decorators, defaults and annotations run in the enclosing code object.
        self._outer([*node.decorator_list, *node.args.defaults, *node.args.kw_defaults])
        module_level = self.scope[-1] == "<module>"
        self._enter(node.name, node, ".<locals>.")
        qualname = self.scope[-1]
        arguments = node.args
        self.params[qualname] = tuple(argument.arg for argument in [*arguments.posonlyargs, *arguments.args,
                                                                    *arguments.kwonlyargs])
        if module_level:
            self.defs[node.name] = qualname
            for decorator in node.decorator_list:
                call = decorator if isinstance(decorator, ast.Call) else None
                if _identifier(call.func if call else decorator) == "fixture":
                    autouse = any(keyword.arg == "autouse" and isinstance(keyword.value, ast.Constant)
                                  and keyword.value.value is True for keyword in (call.keywords if call else ()))
                    self.fixtures[node.name] = (qualname, autouse)
        for statement in node.body:
            self.visit(statement)
        self._leave()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node) -> None:
        self._outer([*node.decorator_list, *node.bases, *node.keywords])
        if self.scope[-1] == "<module>":
            self.defs[node.name] = node.name
        self._enter(node.name, node, ".")
        for statement in node.body:
            self.visit(statement)
        self._leave()

    def visit_Lambda(self, node) -> None:
        self._outer([*node.args.defaults, *node.args.kw_defaults])
        self._enter("<lambda>", node, ".<locals>.")
        self.visit(node.body)
        self._leave()

    def visit_GeneratorExp(self, node) -> None:
        # The first iterable is evaluated outside; list, set and dict comprehensions are inlined (PEP 709).
        self.visit(node.generators[0].iter)
        self._enter("<genexpr>", node, ".<locals>.")
        self.visit(node.elt)
        for number, generator in enumerate(node.generators):
            if number:
                self.visit(generator.iter)
            self.visit(generator.target)
            for condition in generator.ifs:
                self.visit(condition)
        self._leave()

    def visit_If(self, node) -> None:
        test = node.test
        if self.nodes[-1] == "<module>" and isinstance(test, ast.Compare) and isinstance(test.left, ast.Name) \
                and test.left.id == "__name__" and len(test.comparators) == 1 \
                and _string(test.comparators[0]) == "__main__":
            self.visit(test)
            self.nodes.append("<main>")
            for statement in node.body:
                self.visit(statement)
            self.nodes.pop()
            for statement in node.orelse:
                self.visit(statement)
            return
        self.generic_visit(node)

    def visit_Import(self, node) -> None:
        for alias in node.names:
            self._ref(("import", alias.name, 0))
            if alias.asname:
                self.bindings.setdefault(alias.asname, []).append(("module", alias.name, 0))
            else:
                first = alias.name.split(".")[0]
                self.bindings.setdefault(first, []).append(("module", first, 0))

    def visit_ImportFrom(self, node) -> None:
        module = node.module or ""
        self._ref(("import", module, node.level))
        for alias in node.names:
            if alias.name == "*":
                self.stars.append((module, node.level))
            else:
                self._ref(("from", module, node.level, alias.name))
                self.bindings.setdefault(alias.asname or alias.name, []).append(
                    ("from", module, node.level, alias.name))

    def visit(self, node) -> None:
        kind = node.__class__
        method = _VISITORS.get(kind)
        if method is None:
            method = _VISITORS[kind] = getattr(_Scanner, "visit_" + kind.__name__, _Scanner.generic_visit)
        method(self, node)

    def generic_visit(self, node) -> None:
        self.parents.append(node)
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        self.parents.pop()

    def visit_List(self, node) -> None:
        self._argument_vector(node)
        self.generic_visit(node)

    visit_Tuple = visit_List

    def visit_Call(self, node) -> None:
        callee = _callee(node)
        if node.args and callee in PROCESS_CALLS:
            self._program(node.args[0], node)
        for keyword in node.keywords:
            if keyword.arg == "executable" and callee in PROCESS_CALLS:
                self._program(keyword.value, node)
        first = _string(node.args[0]) if node.args and isinstance(node.args[0], ast.Constant) else None
        if first is not None:
            if callee in LOOKUP_CALLS and _program_is_git(first):
                self._add(START, node)
            elif callee in IMPORT_CALLS:
                self._ref(("import", first, 0))
                self._ref(("main", first))
        elif callee in IMPORT_CALLS and node.args:
            self.dynamic.add(self.nodes[-1])
        if callee in LOAD_CALLS:
            arguments = [*node.args[1 if callee == "spec_from_file_location" else 0:],
                         *(keyword.value for keyword in node.keywords)]
            if not any(self._script(argument) for argument in arguments):
                self.dynamic.add(self.nodes[-1])
        if callee == "main" and isinstance(node.func, ast.Attribute) and _identifier(node.func.value) == "pytest":
            self._add(PYTEST, node)
        if callee in FIXTURE_CALLS:
            for argument in node.args:
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    self._ref(("fixture", argument.value))
        self.generic_visit(node)

    def _script(self, node) -> bool:
        """A path that a process or a loader runs: a repository script counts whole (`ROOT / "tools/gate.py"`)."""
        text, anchored = self._path(node)
        if text and text.endswith((".py", ".sh")):
            self._ref(("script", text, anchored))
            return True
        return False

    def _program(self, program, call) -> None:
        """A process call's program: a command string (`"git log"`, `"cd x && git log"` for a shell, `"python3
        tools/gate.py"`) or an expression that holds git (`_names_git_program`). An argument vector written in the
        call is its own site (`_argument_vector`)."""
        text = _string(program)
        if text is not None and isinstance(program, ast.Constant):
            for word in _command_words(text):
                if word.endswith((".py", ".sh")):
                    self._ref(("script", word, False))
        if text is not None:
            if _program_is_git(text):
                words = text.split()
                self._add(START, call, words[1] if len(words) > 1 and isinstance(program, ast.Constant)
                          and not words[1].startswith("-") else "")
            elif names_git(text):
                self._add(START, call)
        elif not isinstance(program, (ast.List, ast.Tuple)) and self._names_git_program(program):
            self._add(START, call)

    def _names_git_program(self, node, depth: int = 0) -> bool:
        """Whether an expression used as a program, or bound to a name, holds git: the one test for both.

        A string whose first word is git (`"git"`, `f"git -C {root} log"`); a variable whose name says so (`git`,
        `GIT_BIN`, `m.GIT`) or that a value assigned to it in this file holds git (`git = shutil.which("git")`);
        a call other than a process call handed git or called on it (`os.environ.get("GIT", "git")`, `"git
        log".split()`, `list(GIT)`);
        the first element of a vector or of a sum (`[*GIT, "log"]`, `GIT + ["log"]`), either branch of a choice
        (`os.environ.get("GIT") or "git"`). A name bound to this file's own vector is not: the code that loads it
        is the site (`visit_Name`), with the subcommand."""
        if depth > 8:
            return False
        recurse = lambda inner: self._names_git_program(inner, depth + 1)  # noqa: E731
        text = _string(node)
        if text is not None:
            return _program_is_git(text)
        if isinstance(node, ast.Starred):
            return recurse(node.value)
        if isinstance(node, ast.BinOp):
            return isinstance(node.op, ast.Add) and recurse(node.left)
        if isinstance(node, ast.BoolOp):
            return any(recurse(value) for value in node.values)
        if isinstance(node, ast.IfExp):
            return recurse(node.body) or recurse(node.orelse)
        if isinstance(node, (ast.List, ast.Tuple)):
            return bool(node.elts) and id(node) not in self.bound and recurse(node.elts[0])
        if isinstance(node, ast.Call):  # what a process call returns is git's output, not the program
            return _callee(node) not in PROCESS_CALLS and any(recurse(argument) for argument in [*node.args, *(keyword.value for keyword in node.keywords)]) \
                or isinstance(node.func, ast.Attribute) and recurse(node.func.value)
        if isinstance(node, ast.Name) and node.id in self.vectors:
            return False
        words = [word for word in re.split(r"[^a-z]+", _identifier(node).lower()) if word]
        if "git" in words and set(words) <= PROGRAM_WORDS | {"git"}:
            return True
        return isinstance(node, ast.Name) and any(recurse(value) for value in self._values(node.id))

    def visit_Attribute(self, node) -> None:
        chain, value = [node.attr], node.value
        while isinstance(value, ast.Attribute):
            chain.insert(0, value.attr)
            value = value.value
        if isinstance(value, ast.Name) and isinstance(node.ctx, ast.Load):
            self._ref(("attribute", value.id, *chain))
        self.generic_visit(node)

    def _path(self, node, depth: int = 0) -> tuple[str | None, bool]:
        """The path an expression makes, as far as this file says: `(text, True)` relative to the root when it is
        built from `__file__` (`Path(__file__).resolve().parents[1] / "tools" / "gate.py"`), `(text, False)` for
        literal parts after an unknown base, `(None, False)` when the source does not say."""
        if depth > 8:
            return None, False
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value, False
        if isinstance(node, ast.Name):
            if node.id == "__file__":
                return self.file, True
            values = self._values(node.id)
            return self._path(values[0], depth + 1) if len(values) == 1 else (None, False)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            (left, anchored), (right, _) = self._path(node.left, depth + 1), self._path(node.right, depth + 1)
            if right is None:
                return None, False
            if left is None:
                return right, False
            return os.path.normpath(os.path.join(left, right)), anchored
        if isinstance(node, ast.Call):
            if _callee(node) in ("Path", "PurePath", "str", "fspath", "resolve", "absolute", "realpath", "abspath") \
                    and len(node.args) <= 1:
                inner = node.args[0] if node.args else (node.func.value if isinstance(node.func, ast.Attribute)
                                                        else None)
                return self._path(inner, depth + 1) if inner is not None else (None, False)
            if _callee(node) == "join" and node.args:
                parts = [self._path(argument, depth + 1) for argument in node.args]
                if all(text is not None for text, _ in parts):
                    return os.path.normpath(os.path.join(*(text for text, _ in parts))), parts[0][1]
            return None, False
        if isinstance(node, ast.Attribute) and node.attr == "parent":
            text, anchored = self._path(node.value, depth + 1)
            return (os.path.dirname(text) or ".", anchored) if text is not None else (None, False)
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and node.value.attr == "parents" \
                and isinstance(node.slice, ast.Constant) and type(node.slice.value) is int:
            text, anchored = self._path(node.value.value, depth + 1)
            if text is None:
                return None, False
            for _ in range(node.slice.value + 1):
                text = os.path.dirname(text) or "."
            return text, anchored
        return None, False

    def visit_Constant(self, node) -> None:
        if isinstance(node.value, str):
            if _names_git_path(node.value) and self._opened(node):
                self._add(READ, node)

    def visit_Name(self, node) -> None:
        if isinstance(node.ctx, ast.Load):
            self._ref(("name", node.id))
        if isinstance(node.ctx, ast.Load) and node.id in self.vectors:
            vector = self.vectors[node.id]
            arguments = vector.elts[1:]
            parent = self.parents[-1] if self.parents else None
            if isinstance(parent, ast.Starred) and len(self.parents) > 1 and \
                    isinstance(self.parents[-2], (ast.List, ast.Tuple)):
                elements = self.parents[-2].elts
                arguments = [*arguments, *elements[[e is parent for e in elements].index(True) + 1:]]
            self._add(START, node, _subcommand(arguments))

    @staticmethod
    def _vector(node) -> bool:
        return isinstance(node, (ast.List, ast.Tuple)) and bool(node.elts) \
            and isinstance(node.elts[0], ast.Constant) and isinstance(node.elts[0].value, str) \
            and _program_is_git(node.elts[0].value)

    def _argument_vector(self, node) -> None:
        if id(node) in self.bound or not node.elts:
            return
        elements, first = node.elts, node.elts[0]
        if self._vector(node):
            self._add(START, node, _subcommand(elements[1:]))
        elif isinstance(first, ast.Constant) and isinstance(first.value, str) and first.value.split() \
                and os.path.basename(first.value.split()[0]) in LAUNCHERS:
            if any(isinstance(element, ast.Constant) and names_git(element.value) for element in elements[1:]):
                self._add(START, node)
        elif self._names_git_program(first):  # `[git, "log"]`, `[*GIT, "log"]` with `GIT` imported
            self._add(START, node)
        if any(_string(option) == "-m" and _string(value) == "pytest" and isinstance(value, ast.Constant)
               for option, value in zip(elements, elements[1:])):
            self._add(PYTEST, node)
        python = next((number for number, element in enumerate(elements) if _python(element)), None)
        launched = isinstance(first, ast.Constant) and isinstance(first.value, str) and first.value.split() \
            and os.path.basename(first.value.split()[0]) in LAUNCHERS
        # The script a Python or a launcher in the vector runs, or the vector's program when a process call
        # starts it directly (`subprocess.run([ROOT / "tools/x.sh"])`); a list of file names is data.
        parent = self.parents[-1] if self.parents else None
        started = isinstance(parent, ast.Call) and _callee(parent) in PROCESS_CALLS and parent.args \
            and parent.args[0] is node
        for element in elements[: len(elements) if python is not None or launched else int(bool(started))]:
            if not isinstance(element, ast.Starred):
                self._script(element)
        if python is None:
            return
        for number in range(python + 1, len(elements) - 1):
            option, value = _string(elements[number]), elements[number + 1]
            if option == "-m" and isinstance(value, ast.Constant) and value.value == "pytest":
                continue
            if option == "-m" and isinstance(value, ast.Constant) and isinstance(value.value, str):
                self._ref(("main", value.value))
            elif option == "-c" and isinstance(value, ast.Constant) and isinstance(value.value, str):
                self._program_text(value.value, node)

    def _program_text(self, text: str, node) -> None:
        """A `python -c` program: what it does is done here; what it imports or runs, this code runs."""
        try:
            tree = ast.parse(text)
        except (SyntaxError, ValueError):
            return
        inner = _Scanner(self.file, tree)
        inner.visit(tree)
        for site in inner.found:
            self._add(site.kind, node, site.command)
        for refs in inner.refs.values():
            for ref in refs:
                self._ref(ref)
        for name, imports in inner.bindings.items():
            self.bindings.setdefault(name, []).extend(imports)

    def _opened(self, node) -> bool:
        """Whether a ".git" string is used as a path: joined to another path, handed to a call or named,
        but not compared, not one name in a list of names and not handed to a string method that matches
        names. A path with a separator in it (".git/HEAD") counts wherever else it stands."""
        child = node
        for parent in reversed(self.parents):
            if isinstance(parent, ast.Compare):
                return False
            if isinstance(parent, (ast.Tuple, ast.List, ast.Set)):
                if child is node and len(parent.elts) > 1:
                    return False
            elif isinstance(parent, ast.Call):
                return not (_callee(parent) in NAME_METHODS and child is not parent.func)
            elif isinstance(parent, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                return True
            elif not isinstance(parent, (ast.BinOp, ast.keyword)):
                return child is not node or "/" in node.value
            child = parent
        return True


def _scan(file: str, root: Path) -> _Scanner | None:
    try:
        tree = ast.parse((root / file).read_text(encoding="utf-8"), file)
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
        return None
    scanner = _Scanner(file, tree)
    scanner.visit(tree)
    if scanner.dynamic:
        names = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)
                 and isinstance(node.value, str) and _MODULE_NAME.fullmatch(node.value)}
        for node in scanner.dynamic:
            scanner.refs.setdefault(node, set()).update(("named", name) for name in names)
    return scanner


def sites(file: str, root: Path = ROOT) -> set[Site]:
    """Every site in one Python file (root-relative); none when it is missing or does not parse."""
    scanner = _scan(file, root)
    return scanner.found if scanner else set()


def _test_map():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import test_map
    finally:
        sys.path.remove(str(ROOT / "tools"))
    return test_map


def units(root: Path = ROOT) -> list[str]:
    """The test units, as the coverage map names them (tools/test_map.py)."""
    return _test_map().units(root)


class _Sources:
    """The sites and references of each file, scanned once, and what a test unit can run (`reach`)."""

    def __init__(self, root: Path):
        self.root = root
        self.scanned: dict[str, _Scanner | None] = {}
        self.index: dict[str, list[str]] | None = None
        self.memo: dict[tuple, object] = {}
        self.closed: dict[tuple[str, str], frozenset[Site]] = {}

    def _memo(self, key: tuple, compute):
        if key not in self.memo:
            self.memo[key] = compute()
        return self.memo[key]

    def scanner(self, file: str) -> _Scanner | None:
        if file not in self.scanned:
            self.scanned[file] = _scan(file, self.root)
        return self.scanned[file]

    def of(self, file: str) -> set[Site]:
        scanner = self.scanner(file)
        return scanner.found if scanner else set()

    def at(self, file: str, qualname: str) -> set[Site]:
        return {site for site in self.of(file) if site.qualname == qualname}

    # Modules and scripts, found the way the tests' imports find them: next to the importing file, at the root,
    # in tests/ or tools/ (both on the tests' path), else any file of the tree with that dotted path.
    def _directory(self, relative: str) -> bool:
        return self._memo(("directory", relative), lambda: (self.root / relative).is_dir())

    def _file(self, relative: str) -> bool:
        return self._memo(("file", relative), lambda: (self.root / relative).is_file())

    def _python_files(self) -> dict[str, list[str]]:
        """Every Python file of the tree by its name, outside the virtual environment, git and build directories."""
        if self.index is None:
            self.index = {}
            for directory, names, files in os.walk(self.root):
                names[:] = sorted(name for name in names if name not in _SKIPPED_DIRECTORIES
                                  and not name.startswith("."))
                base = Path(directory).relative_to(self.root).as_posix()
                for name in files:
                    if name.endswith((".py", ".sh")):
                        self.index.setdefault(name, []).append(name if base == "." else f"{base}/{name}")
        return self.index

    def _in(self, base: str, parts: list[str]) -> list[str]:
        """The files `import a.b` runs from directory `base`: each package's `__init__.py` and the module."""
        files, directory = [], base
        for number, part in enumerate(parts):
            directory = f"{directory}/{part}" if directory else part
            if number < len(parts) - 1:
                if not self._directory(directory):
                    return []
                if self._file(f"{directory}/__init__.py"):
                    files.append(f"{directory}/__init__.py")
        if self._file(f"{directory}.py"):
            return files + [f"{directory}.py"]
        if self._file(f"{directory}/__init__.py") or self._directory(directory):
            # A namespace package (`conformance/`, `tools/`) has no `__init__.py`: the name stands for its
            # directory, so `from conformance import frozen_norm_defaults` finds the submodule in it.
            return files + [f"{directory}/__init__.py"]
        return []

    def modules(self, importer: str, dotted: str, level: int = 0) -> list[str]:
        return self._memo(("modules", Path(importer).parent.as_posix(), dotted, level),
                          lambda: self._modules(importer, dotted, level))

    def _modules(self, importer: str, dotted: str, level: int) -> list[str]:
        parts = [part for part in dotted.split(".") if part]
        here = Path(importer).parent.as_posix()
        if level:
            base = Path(importer).parents[level - 1].as_posix() if level <= len(Path(importer).parents) else "."
            return self._in("" if base == "." else base, parts) if parts else (
                [f"{base}/__init__.py"] if self._file(f"{base}/__init__.py") else [])
        if not parts or parts[0] in sys.stdlib_module_names:
            return []
        for base in dict.fromkeys(("" if here == "." else here, "", "tests", "tools")):
            files = self._in(base, parts)
            if files:
                return files
        tail = "/".join(parts)
        return sorted(file for name in (f"{parts[-1]}.py", "__init__.py") for file in self._python_files().get(name, ())
                      if file == f"{tail}.py" or file.endswith(f"/{tail}.py") or file.endswith(f"/{tail}/__init__.py"))

    def scripts(self, importer: str, text: str, anchored: bool) -> list[str]:
        """The repository Python files a path names: exactly the file when the path is built from the root
        (`ROOT / "tools" / "gate.py"`); else the file at the root, or every file whose path ends with it
        (`HERE / "report.py"` with an unknown `HERE`)."""
        text = os.path.normpath(text) if text else ""
        if anchored:
            return [text] if not text.startswith("..") and self._file(text) else []
        text = text.lstrip("./")
        if not text or text.startswith("/") or "*" in text:
            return []
        if self._file(text):
            return [text]
        return sorted(file for file in self._python_files().get(text.rsplit("/", 1)[-1], ())
                      if file.endswith(f"/{text}"))

    def name(self, file: str, name: str, seen: frozenset = frozenset()) -> list[tuple]:
        """What a name in a file's code is, as far as the source says: a function or class of a file
        (`("def", file, qualname)`) or a module (`("module", file)`); nothing for a local, a builtin or a value."""
        if (file, name) in seen:
            return []
        seen = seen | {(file, name)}
        scanner = self.scanner(file)
        if scanner is None:
            return []
        if name in scanner.defs:
            return [("def", file, scanner.defs[name])]
        found = []
        for binding in scanner.bindings.get(name, ()):
            if binding[0] == "module":
                found += [("module", module) for module in self.modules(file, binding[1], binding[2])[-1:]]
            else:
                found += self.imported(file, binding[1], binding[2], binding[3], seen)
        if not found:
            for module, level in scanner.stars:
                for star in self.modules(file, module, level)[-1:]:
                    found += self.name(star, name, seen)
        return found

    def imported(self, file: str, module: str, level: int, name: str, seen: frozenset = frozenset()) -> list[tuple]:
        """What `from module import name` in `file` binds: a submodule, or the name in the module."""
        package = self.modules(file, module, level)
        if not package:
            return []
        submodule = self.modules(package[-1], name, 1) if package[-1].endswith("/__init__.py") else []
        if submodule:
            return [("module", submodule[-1])]
        return self.name(package[-1], name, seen) or [("module", package[-1])]

    def attribute(self, file: str, chain: tuple[str, ...]) -> list[tuple]:
        """What an attribute chain rooted at a name (`gate.lake_outputs.drop_stale`) is, as far as the source says.
        After `import tools.gate` the chain `tools.gate.x` starts at the longest module it names."""
        targets, rest = self.name(file, chain[0]), chain[1:]
        scanner = self.scanner(file)
        if scanner and any(binding[:2] == ("module", chain[0]) for binding in scanner.bindings.get(chain[0], ())):
            for length in range(len(chain), 1, -1):
                files = self.modules(file, ".".join(chain[:length]))
                if files:
                    targets, rest = [("module", module) for module in files], chain[length:]
                    break
        found = []
        for attribute in rest:
            found += targets
            following = []
            for target in targets:
                if target[0] == "module":
                    submodule = self.modules(target[1], attribute, 1) if target[1].endswith("/__init__.py") else []
                    following += [("module", submodule[-1])] if submodule else self.name(target[1], attribute)
            targets = following
        return found + targets

    def targets(self, file: str, ref: tuple) -> list[tuple]:
        return self._memo(("targets", file, ref), lambda: self._targets(file, ref))

    def _targets(self, file: str, ref: tuple) -> list[tuple]:
        kind = ref[0]
        if kind == "name":
            return self.name(file, ref[1])
        if kind == "attribute":
            return self.attribute(file, ref[1:])
        if kind == "import":
            return [("module", module) for module in self.modules(file, ref[1], ref[2])]
        if kind == "plugin":
            return [("module", module) for module in self.modules(file, ref[1])]
        if kind == "from":  # the import runs the module, or the submodule it names; a use of the name runs the rest
            return [target for target in self.imported(file, ref[1], ref[2], ref[3]) if target[0] == "module"]
        if kind == "script":
            return [("script", script) for script in self.scripts(file, ref[1], ref[2])]
        if kind == "named":  # a module or a script loaded by a name in data: all of it counts
            if ref[1].endswith(".py"):
                return [("script", script) for script in self.scripts(file, ref[1], False)]
            files = self.modules(file, ref[1]) if ref[1].split(".")[0] not in sys.stdlib_module_names else []
            return [("module", module) for module in files[:-1]] + [("script", module) for module in files[-1:]]
        if kind == "main":  # `python -m a.b` runs a/b.py or a/b/__main__.py from the working directory
            parts = ref[1].split(".")
            files = self._in("", parts)
            main = self._in("", [*parts, "__main__"]) if files and files[-1].endswith("__init__.py") else []
            return [("module", file) for file in files[:-1]] + [("script", file) for file in (main or files)[-1:]]
        return []

    def nodes(self, target: tuple) -> list[tuple[str, str]]:
        return self._memo(("nodes", target), lambda: self._nodes(target))

    def _nodes(self, target: tuple) -> list[tuple[str, str]]:
        """The pieces of code a target runs: a module's top level; all of a script started as a program or a test
        file run by pytest (its `__main__` block, every function); a function's or class's code with everything
        defined in it, and the top level of its module. A shell script is one piece."""
        file = target[1]
        if file.endswith(".sh"):
            return [(file, "<script>")]
        scanner = self.scanner(file)
        if scanner is None:
            return []
        if target[0] == "module":
            return [(file, "<module>")]
        if target[0] == "script":
            return [(file, key) for key in scanner.code()]
        qualname = target[2]
        return [(file, "<module>")] + [(file, key) for key in scanner.code() - {"<module>", "<main>"}
                                       if key == qualname or key.startswith(qualname + ".")]

    def conftests(self, unit: str) -> list[str]:
        """The conftest files pytest loads for a unit: in its directory and each one above it, to the root."""
        found, directory = [], Path(unit).parent
        while True:
            name = "conftest.py" if directory.as_posix() == "." else f"{directory.as_posix()}/conftest.py"
            if self._file(name):
                found.append(name)
            if directory.as_posix() == ".":
                return found
            directory = directory.parent

    def own(self, node: tuple[str, str]) -> set[Site]:
        """The sites in one piece of code; a shell script's, one per line that names git."""
        file, key = node
        if key == "<script>":
            def lines():
                try:
                    text = (self.root / file).read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    return set()
                return {Site(file, key, START, number) for number, line in enumerate(text.splitlines(), 1)
                        if not line.lstrip().startswith("#") and names_git(line)}
            return self._memo(("shell", file), lines)
        facts = self.scanner(file)
        if facts is None:
            return set()
        return facts.sites_of.get(key, set()) | ({facts.programs[key]} if key in facts.programs else set())

    def edges(self, node: tuple[str, str]) -> list[tuple[str, str]]:
        """The pieces of code one piece can run: what each name, import and script in it is."""
        def compute():
            file, key = node
            facts = self.scanner(file)
            return list(dict.fromkeys(item for ref in (facts.refs.get(key, ()) if facts else ())
                                      for target in self.targets(file, ref) for item in self.nodes(target)))
        return self._memo(("edges", node), compute)

    def closure(self, start: tuple[str, str]) -> frozenset[Site]:
        """Every site the code `start` can run, transitively; each strongly connected group of code (Tarjan,
        without recursion) is closed once and shared."""
        closed = self.closed
        if start in closed:
            return closed[start]
        index: dict[tuple, int] = {start: 0}
        low = {start: 0}
        stack, on_stack = [start], {start}
        work = [(start, iter(self.edges(start)))]
        while work:
            node, children = work[-1]
            for child in children:
                if child in closed:
                    continue
                if child not in index:
                    index[child] = low[child] = len(index)
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(self.edges(child))))
                    break
                if child in on_stack:
                    low[node] = min(low[node], index[child])
            else:
                work.pop()
                if work:
                    parent = work[-1][0]
                    low[parent] = min(low[parent], low[node])
                if low[node] == index[node]:
                    component = []
                    while True:
                        member = stack.pop()
                        on_stack.discard(member)
                        component.append(member)
                        if member == node:
                            break
                    members, found = set(component), set()
                    for member in component:
                        found |= self.own(member)
                        for child in self.edges(member):
                            if child not in members:
                                found |= closed[child]
                    result = frozenset(found)
                    for member in component:
                        closed[member] = result
        return closed[start]

    def reach(self, unit: str) -> set[Site]:
        """Every site the source of a test unit can run: all of its own file, the modules it imports, the
        functions and classes it names, the scripts it starts, transitively, and the fixtures of its conftests
        and their `pytest_plugins` that it uses: autouse ones, those its functions or the fixtures it uses take
        as arguments, those it names in `usefixtures`/`getfixturevalue`. The conftests' hooks run for the whole
        session, not for a unit, and are not followed."""
        scanner = self.scanner(unit)
        if scanner is None:
            return set()
        providers = self.conftests(unit)
        roots = [(unit, key) for key in scanner.code()]
        roots += [(conftest, "<module>") for conftest in providers]
        for conftest in list(providers):
            facts = self.scanner(conftest)
            for ref in (facts.refs.get("<module>", ()) if facts else ()):
                if ref[0] == "plugin":
                    providers += [target[1] for target in self.targets(conftest, ref) if target[1] not in providers]
        names = {name for key in scanner.params for name in scanner.params[key]}
        names |= {ref[1] for refs in scanner.refs.values() for ref in refs if ref[0] == "fixture"}
        used: set[tuple[str, str]] = set()
        while True:
            more = [(provider, qualname) for provider in providers for name, (qualname, autouse)
                    in (self.scanner(provider).fixtures.items() if self.scanner(provider) else ())
                    if (autouse or name in names) and (provider, qualname) not in used]
            if not more:
                break
            for provider, qualname in more:
                used.add((provider, qualname))
                facts = self.scanner(provider)
                roots += self.nodes(("def", provider, qualname))
                names |= set(facts.params.get(qualname, ()))
                names |= {ref[1] for ref in facts.refs.get(qualname, ()) if ref[0] == "fixture"}
        return set().union(*(self.closure(root) for root in roots))


def extract(data: dict, root: Path = ROOT) -> dict:
    """The part of a coverage map (`tools/test_map.py` `load`) the list is derived from: each unit that started
    git, with the functions it ran that start git in the source, and each unit that ran a function that reads
    `.git`, which the map's recorder does not record. A function that starts git counts only for a unit the map
    saw start git (it may not have reached the call); a `.git` read has no such record, so running the function
    counts."""
    sources = _Sources(root)
    tests = data["tests"]
    started = {tests[i] for i in data["programs"].get("git", ())}
    found: dict[str, set[str]] = {}
    for file, qualnames in data["functions"].items():
        for qualname, indices in qualnames.items():
            kinds = {site.kind for site in sources.at(file, qualname)}
            for i in indices:
                if READ in kinds or START in kinds and tests[i] in started:
                    found.setdefault(tests[i], set()).add(f"{file}:{qualname}")
    return {"format": MAP_FORMAT,
            "map": {"commit": data["commit"], "version": data["version"], "created": data["created"],
                    "tests": len(tests)},
            "units": {unit: {"git": unit in started, "sites": sorted(found.get(unit, ()))}
                      for unit in sorted(started | set(found))}}


def _why(found: set[Site], recorded_without_site: bool) -> str:
    parts = []
    runs = sorted({site.file for site in found if site.kind == PYTEST})
    starts = sorted(site for site in found if site.kind == START)
    if starts:
        commands = sorted({f"git {site.command}" for site in starts if site.command})
        parts.append("starts git" + (f" ({', '.join(commands)})" if commands else "") + " in "
                     + ", ".join(sorted({site.file for site in starts})))
    reads = sorted(site for site in found if site.kind == READ)
    if reads:
        parts.append("reads .git in " + ", ".join(sorted({site.file for site in reads})))
    if runs:
        parts.append("runs pytest on test files the source does not name, in " + ", ".join(runs))
    if recorded_without_site:
        parts.append("the coverage map records it starting git from code with no site in the tree's Python")
    return "; ".join(parts)


def _via(found: set[Site]) -> list[str]:
    by_function: dict[tuple[str, str], set[str]] = {}
    for site in found:
        by_function.setdefault((site.file, site.qualname), set()).add(site.what())
    return [f"{file}:{qualname}: {', '.join(sorted(whats))}" for (file, qualname), whats in sorted(by_function.items())]


def generate(saved: dict, root: Path = ROOT) -> dict:
    """The list: each unit whose source reaches a site (`_Sources.reach`), or that ran a function of `saved` (the map
    extract) that still has one, or that the map saw start git from code with no site at all."""
    sources = _Sources(root)
    present = units(root)
    rows = []
    for unit in present:
        record = saved["units"].get(unit, {"git": False, "sites": []})
        carried = set().union(*(sources.at(*site.split(":", 1)) for site in record["sites"]))
        own = sources.reach(unit)
        unexplained = record["git"] and not record["sites"]
        if not (carried or own or unexplained):
            continue
        recorded = (["coverage map"] if carried or unexplained else []) + (["source"] if own else [])
        rows.append({"test": unit, "why": _why(carried | own, unexplained), "recorded": recorded,
                     "via": _via(carried | own)})
    return {"format": FORMAT, "map": saved["map"], "tests": rows}


def validate_extract(data) -> list[str]:
    errors = []
    if not isinstance(data, dict) or data.get("format") != MAP_FORMAT:
        return [f"{MAP_EXTRACT}: format is not {MAP_FORMAT}"]
    header = data.get("map")
    if not isinstance(header, dict) or not isinstance(header.get("commit"), str) \
            or type(header.get("version")) is not int or not isinstance(header.get("created"), str) \
            or type(header.get("tests")) is not int:
        errors.append(f"{MAP_EXTRACT}: map is not {{commit, version, created, tests}}")
    records = data.get("units")
    if not isinstance(records, dict):
        return errors + [f"{MAP_EXTRACT}: units is not an object"]
    for unit, record in records.items():
        if not isinstance(record, dict) or set(record) != {"git", "sites"} or type(record["git"]) is not bool \
                or not isinstance(record["sites"], list) or not all(
                    isinstance(site, str) and ":" in site for site in record["sites"]) \
                or not (record["git"] or record["sites"]):
            errors.append(f"{MAP_EXTRACT}: {unit}: not {{git: bool, sites: [\"file:qualname\", ...]}} with "
                          "git or a site")
    return errors


def validate_list(data) -> list[str]:
    if not isinstance(data, dict) or data.get("format") != FORMAT or set(data) != {"format", "map", "tests"}:
        return [f"{LIST}: not {{format: {FORMAT}, map, tests}}"]
    rows = data["tests"]
    if not isinstance(rows, list):
        return [f"{LIST}: tests is not a list"]
    errors = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"test", "why", "recorded", "via"} \
                or not isinstance(row["test"], str) or not isinstance(row["why"], str) or not row["why"] \
                or not isinstance(row["recorded"], list) or not row["recorded"] \
                or not set(row["recorded"]) <= {"coverage map", "source"} \
                or not isinstance(row["via"], list) or not all(isinstance(item, str) for item in row["via"]):
            errors.append(f"{LIST}: an entry is not {{test, why, recorded, via}} with a reason: {row!r:.200}")
    names = [row.get("test") for row in rows if isinstance(row, dict)]
    if len(set(names)) != len(names):
        errors.append(f"{LIST}: a test is listed twice")
    return errors


@dataclass
class Findings:
    errors: list[str]    # the lint fails
    stale: list[str]     # reported only


def lint(root: Path = ROOT) -> Findings:
    """Compare the committed list with the one `generate` derives from the saved map extract and the tree."""
    def read(name):
        try:
            return json.loads((root / name).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            return error

    saved, listed = read(MAP_EXTRACT), read(LIST)
    errors = [f"{name}: unreadable ({value})" for name, value in ((MAP_EXTRACT, saved), (LIST, listed))
              if isinstance(value, Exception)]
    if errors:
        return Findings(errors, [])
    errors = validate_extract(saved) + validate_list(listed)
    if errors:
        return Findings(errors, [])
    return compare(listed, generate(saved, root), root)


def named_sources(root: Path = ROOT) -> frozenset[str]:
    """The source files the committed list (each `via` entry) and the map extract (each site) name: a change to one,
    a renamed function say, can make the list stale, so the selector runs the lint for it (tools/select_tests.py
    `history_inventory`). A file that is unreadable or malformed names none."""
    named = set()
    for name, valid, entries in (
            (LIST, validate_list, lambda data: (item for row in data["tests"] for item in row["via"])),
            (MAP_EXTRACT, validate_extract, lambda data: (site for record in data["units"].values()
                                                          for site in record["sites"]))):
        try:
            data = json.loads((root / name).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not valid(data):
            named.update(entry.split(":", 1)[0] for entry in entries(data))
    return frozenset(named)


def compare(listed: dict, expected: dict, root: Path = ROOT) -> Findings:
    """The lint's findings for the committed list `listed` against the generated `expected`."""
    errors = []
    if listed["map"] != expected["map"]:
        errors.append(f"{LIST}: names map {listed['map']}, but {MAP_EXTRACT} was saved from {expected['map']}")
    have = {row["test"]: row for row in listed["tests"]}
    want = {row["test"]: row for row in expected["tests"]}
    for unit in sorted(want.keys() - have.keys()):
        errors.append(f"missing: {unit} reads history and is not listed ({want[unit]['why']})")
    for unit in sorted(want.keys() & have.keys()):
        if have[unit] != want[unit]:
            errors.append(f"changed: {unit} is listed as {have[unit]}, the tree gives {want[unit]}")
    if [row["test"] for row in listed["tests"]] != sorted(have):
        errors.append(f"{LIST}: the tests are not in order")
    stale = [f"stale: {unit} is listed but no longer reads history"
             + ("" if (root / unit).is_file() else " (the unit is gone)") for unit in sorted(have.keys() - want.keys())]
    if errors:
        errors.append(f"run `python tools/history_tests.py --write` and commit {LIST}")
    return Findings(errors, stale)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="the lint (exit 1 on a missing or changed entry)")
    action.add_argument("--write", action="store_true", help=f"write {LIST} from {MAP_EXTRACT} and the tree")
    action.add_argument("--save-map", action="store_true",
                        help=f"save {MAP_EXTRACT} from a coverage map (default: the map the selector uses for "
                             "the merge base of HEAD and main)")
    parser.add_argument("--map", type=Path, help="the coverage map --save-map reads")
    parser.add_argument("--base", default=None, help="the commit whose map --save-map finds (default: the merge "
                                                     "base of HEAD and main)")
    args = parser.parse_args(argv)
    if args.save_map:
        test_map = _test_map()
        base = args.base or test_map.git("merge-base", "HEAD", "main")
        path = args.map or test_map.find_map(base)
        if path is None:
            print(f"no usable coverage map for {base}: record one with tools/test_map.py record", file=sys.stderr)
            return 1
        saved = extract(test_map.load(path))
        write_json(ROOT / MAP_EXTRACT, saved)
        print(f"saved {MAP_EXTRACT} from {path}: {len(saved['units'])} units")
        return 0
    if args.write:
        saved = json.loads((ROOT / MAP_EXTRACT).read_text(encoding="utf-8"))
        errors = validate_extract(saved)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        listed = generate(saved)
        write_json(ROOT / LIST, listed)
        print(f"wrote {LIST}: {len(listed['tests'])} tests read history")
        return 0
    findings = lint()
    for line in findings.stale:
        print(line)
    if findings.errors:
        print("\n".join(findings.errors), file=sys.stderr)
        return 1
    print(f"{LIST}: every test that reads history is listed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
