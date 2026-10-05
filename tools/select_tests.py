"""Select the tests a change can affect, and the builds and checks they need.

Run ``python3 tools/select_tests.py`` for the working tree, ``--base REV`` for a
branch, ``--commit REV`` for one commit, or ``--paths P...`` for named files
(compared with HEAD; a path whose content cannot be compared counts as wholly
changed). ``--run`` executes the printed commands in order, in the foreground;
``--explain`` lists why each test was selected. docs/TESTING.md has the rules.

How a change selects tests:

* Python: `ast` splits the old and new file into functions (by qualified name)
  and import-time statements. Comments and docstrings are not part of either.
  A changed function selects the tests that executed it in the coverage map
  (tools/test_map.py). A changed import-time statement selects the functions,
  here or in importing modules, that read a name it binds; one that acts at
  import (a top-level call, a registering decorator) selects every test that
  imported the module. A new function nothing in the change calls by name
  selects every test that ran a function of its file. An added or deleted
  module selects every test that imported it, even when it binds nothing
  (empty, a docstring, `pass`); an added one, which the map cannot have seen
  imported, also every test whose static closure now imports it.
* The static graph is the tree after the change plus each changed file as it
  was before, so a deleted module or fixture still leads to its users.
* Lean: the executables whose root imports the module, then the tests that
  ran them; Rust: the tests that ran a Rust binary, and `cargo test`.
* Every file, whatever its kind: the tests that read it, and, for an added or
  removed file, the tests that listed any directory above it, the root "."
  included (it may make its directory appear or vanish). Documentation only
  selects these. `kind_of` and `file_impact` are the one rule for both the
  plan and the drift check below.
* The map is recorded for an earlier commit. Code that changed since then
  ("drift") may call the changed code anew: drift units that name what changed
  add their own tests. Tests the map does not cover (new, failed or opaque when
  recorded, or changed since) are selected by the static graph
  (tools/source_graph.py), which is also the whole answer without a usable map.
* Unknown files, `tests/conftest.py`, `pyproject.toml` and `uv.lock` select
  everything. Anything selected beyond documentation also runs SMOKE.

``--impacted`` is the other, map-free fast path: only the tests whose static
dependencies (imports, conftest files, named data and native checkers) changed,
plus ALWAYS; it runs them in one plain pytest process (docs/TESTING.md).
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from functools import cache
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import time

from change_units import Summary, delta
from layer_policy import ROOT, lean_default_targets, lean_executables, python_exports
import nested_pytest
import source_graph
import test_map

TESTS = sorted((ROOT / "tests").glob("test_*.py"))
EXTRA_UNITS = test_map.EXTRA_UNITS
# Fast tests across parser, environment, wire and both native backends.
SMOKE = ("tests/test_conformance.py", "tests/test_surface_registry.py", "tests/test_definitions.py")
UV_PYTHON = ("uv", "run", "--frozen", "--group", "dev", "python")
# Every pytest run the plan prints starts with this (tools/nested_pytest.py).
PYTEST = nested_pytest.command([], python=UV_PYTHON)
CHECK_PYTHON = (*UV_PYTHON, "tools/check_python_layers.py")
CHECK_LEAN = ("python3", "tools/check_lean_imports.py")
CHECK_RUST = ("python3", "tools/check_rust_deps.py")
AUDIT = ("python3", "lean/audit.py")
# Cargo with path-independent flags, so the release binary matches lean/checkers.lock.
CARGO = ["python3", "tools/rust_build.py"]
DOCUMENT_SUFFIXES = (".md", ".rst", ".pdf", ".png", ".svg", ".tex", ".bib")
EVERYTHING = {"tests/conftest.py", "pyproject.toml", "uv.lock", ".gitignore"}
LEAN_PROJECT = {"lean/lakefile.toml", "lean/lean-toolchain", "lean/lake-manifest.json"}
RUST_PROJECT = {"rust/Cargo.toml", "rust/Cargo.lock", "rust-toolchain.toml"}
PYTHON_LAYER_INPUTS = {".importlinter", "tools/layer-exceptions.json", "tools/check_python_layers.py",
                       "tools/layer_policy.py"}
LEAN_LAYER_INPUTS = {"tools/lean-layer-exceptions.json", "tools/check_lean_imports.py",
                     "tools/lean_header_imports.lean", "tools/layer_policy.py"}
RUST_LAYER_INPUTS = {"tools/rust-module-exceptions.json", "tools/check_rust_deps.py",
                     "tools/layer_policy.py"}
KNOWN_AREAS = {"ve", "ve_experiments", "experiments", "tests", "tools", "conformance", "lean", "rust",
               "usecases", "docs", "paper", "examples", "data", "bench", "design"}
# Cached drift results depend on this file's rules as well as the graph's.
SELECTOR_VERSION = hashlib.sha256(source_graph.CODE_VERSION.encode()
                                  + Path(__file__).read_bytes()).hexdigest()[:16]


def units() -> list[str]:
    return [p.relative_to(ROOT).as_posix() for p in TESTS] + sorted(EXTRA_UNITS)


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(("git", *args), cwd=ROOT, text=True,
                            capture_output=True, check=True)
    return [line for line in result.stdout.splitlines() if line]


def changed_paths(base: str | None, commit: str | None) -> list[str]:
    if commit:
        return git_lines("diff-tree", "--no-renames", "--no-commit-id", "--name-only", "-r",
                         f"{commit}^", commit)
    if base:
        return git_lines("diff", "--no-renames", "--name-only", f"{base}...HEAD")
    return sorted(set(git_lines("diff", "--no-renames", "--name-only", "HEAD") +
                      git_lines("ls-files", "--others", "--exclude-standard")))


def blobs(specs: list[str]) -> dict[str, str | None]:
    """Contents of `rev:path` specs in one git call; None for a missing blob."""
    if not specs:
        return {}
    out = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, check=True, capture_output=True,
                         input="".join(f"{spec}\n" for spec in specs).encode()).stdout
    found, position = {}, 0
    for spec in specs:
        end = out.index(b"\n", position)
        header = out[position:end].split()
        position = end + 1
        if header[-1] == b"missing" or len(header) != 3:
            found[spec] = None
            continue
        size = int(header[2])
        found[spec] = out[position:position + size].decode("utf-8", errors="replace")
        position += size + 1
    return found


@dataclass
class Change:
    path: str
    old: str | None          # None: absent before
    new: str | None          # None: absent after
    known: bool = True       # False: contents unknown, the whole file counts as changed

    presence_known: bool = True  # False: it may also have appeared or vanished

    @property
    def presence_changed(self) -> bool:
        return not self.presence_known or (self.old is None) != (self.new is None)


def read_changes(paths: list[str], *, base: str, after: str | None) -> list[Change]:
    """Old contents from `base`; new ones from `after` (a revision) or the working tree."""
    specs = [f"{base}:{p}" for p in paths] + ([f"{after}:{p}" for p in paths] if after else [])
    contents = blobs(specs)
    changes = []
    for path in paths:
        old = contents[f"{base}:{path}"]
        if after:
            new = contents[f"{after}:{path}"]
        else:
            file = ROOT / path
            new = file.read_text(encoding="utf-8", errors="replace") if file.is_file() else None
        changes.append(Change(path, old, new))
    return changes


class Coverage:
    """The coverage map, indexed for lookups by file."""

    def __init__(self, data: dict, path: Path | None = None):
        self.path = path
        self.commit = data["commit"]
        self.tests = data["tests"]
        self.functions = data["functions"]
        self.reads = data["reads"]
        self.dirs = data["dirs"]
        self.programs = data["programs"]
        self.status = data["status"]
        self.recorded = {test for test, status in data["status"].items()
                         if status["exit"] in (0, 5) and not status["opaque"]}

    def _names(self, indices) -> set[str]:
        return {self.tests[i] for i in indices}

    def tests_of(self, file: str, qualname: str) -> set[str]:
        """Tests that ran the function `qualname`, or anything nested in it."""
        prefix = qualname + "."
        return self._names(i for name, indices in self.functions.get(file, {}).items()
                           if name == qualname or name.startswith(prefix) for i in indices)

    def importers(self, file: str) -> set[str]:
        return self._names(self.functions.get(file, {}).get("<module>", ()))

    def file_wide(self, file: str, defs: set[str]) -> set[str]:
        """Tests that ran any of the functions `defs` of the file."""
        return set().union(*(self.tests_of(file, q) for q in defs)) if defs else set()

    def readers(self, path: str) -> set[str]:
        return self._names(self.reads.get(path, ()))

    def listers(self, path: str) -> set[str]:
        """Tests that listed any directory above `path`, the root "." included.

        A file that appears or vanishes changes its directory's listing; as the
        first or last file there it also makes that directory appear or vanish,
        which changes the parent's listing, and so on up to the root.
        """
        return self._names(i for directory in directories_above(path) for i in self.dirs.get(directory, ()))

    def runners(self, predicate) -> set[str]:
        return self._names(i for name, indices in self.programs.items() if predicate(name)
                           for i in indices)


class Selection:
    def __init__(self, graph: source_graph.Graph, coverage: Coverage | None,
                 unmapped: set[str], all_units: list[str]):
        self.graph = graph
        self.coverage = coverage
        self.unmapped = unmapped          # units the static graph answers for
        self.all_units = all_units
        self.reasons: dict[str, set[str]] = {}
        self.full: list[str] = []
        self.code = False                 # something beyond documentation changed
        self.lean = self.audit = self.rust = False
        self.checks: set[tuple[str, ...]] = set()
        self.notes: list[str] = []
        self._closures: dict[str, tuple[set[str], set[str]]] = {}

    def add(self, tests, reason: str) -> None:
        for test in tests:
            if test in self.all_units:
                self.reasons.setdefault(test, set()).add(reason)

    def closure(self, test: str) -> tuple[set[str], set[str]]:
        if test not in self._closures:
            self._closures[test] = self.graph.closure(test)
        return self._closures[test]

    def static(self, predicate, reason: str, *, everyone: bool = False) -> None:
        """Static answer for unmapped units (for every unit without a map)."""
        for test in (self.all_units if everyone or self.coverage is None else self.unmapped):
            files, mentions = self.closure(test)
            if predicate(files, mentions):
                self.add([test], reason + " (static)")


def directories_above(path: str) -> list[str]:
    """Every directory that holds `path`, nearest first, ending with the root "."
    (the recorder's name for it)."""
    found = []
    parent = posixpath.dirname(path)
    while parent:
        found.append(parent)
        parent = posixpath.dirname(parent)
    return [*found, "."]


def mentions_path(path: str):
    """Predicate: a closure names the file or one of its directories."""
    directories = {f"dir:{directory}" for directory in directories_above(path)}
    return lambda files, mentions: path in mentions or bool(directories & mentions)


def parse(change: Change) -> tuple[Summary | None, Summary | None]:
    """Both versions of a Python file; marks the change unknown if either is not valid Python."""
    module, package = source_graph.module_name(change.path)
    try:
        return (source_graph.summary_of(change.old, module, package) if change.old is not None else None,
                source_graph.summary_of(change.new, module, package) if change.new is not None else None)
    except SyntaxError:
        change.known = False
        return None, None


def python_change(sel: Selection, change: Change, old: Summary | None, new: Summary | None,
                  called: dict[tuple[str, str], frozenset[str]]) -> None:
    path = change.path
    d = delta(old, new) if change.known else None
    mapped(sel, change, (old, new, d), called)
    sel.static(mentions_path(path), f"names {path}")
    if (path.startswith("tests/test_") or path in EXTRA_UNITS) and change.new is not None:
        sel.add([path], "changed test")
    if d is not None and d.empty and not change.presence_changed:
        return  # comments and docstrings only
    sel.code = True
    if path.startswith(("ve/", "ve_experiments/", "experiments/")) and (
            d is None or d.imports_changed or change.presence_changed):
        sel.checks.add(CHECK_PYTHON)
    # The map cannot have seen anyone import a module that did not exist: for an
    # added one the static graph answers for every unit.
    sel.static(lambda files, _: path in files, f"imports {path}", everyone=change.old is None)


def mapped(sel: Selection, change: Change, python=None, called=None) -> None:
    if sel.coverage is not None:
        file_impact(sel.coverage, sel.graph, set(sel.all_units), sel.add, change.path,
                    change.presence_changed, python, called)


EVERYTHING_KIND, PYTHON, LEAN, RUST, DATA = KINDS = ("everything", "python", "lean", "rust", "data")


def kind_of(path: str) -> str:
    """Which rule a changed path falls under, for the plan and the drift check alike."""
    top = path.split("/", 1)[0]
    if path in EVERYTHING or ("/" not in path and not path.endswith(DOCUMENT_SUFFIXES)
                              and path not in RUST_PROJECT and path != ".importlinter") \
            or ("/" in path and top not in KNOWN_AREAS):
        return EVERYTHING_KIND
    if path.endswith(".py"):
        return PYTHON
    if is_lean_input(path):
        return LEAN
    if is_rust_input(path):
        return RUST
    return DATA


def file_impact(coverage: Coverage, graph: source_graph.Graph, all_units: set[str], add, path: str,
                presence_changed: bool, python=None, called=None) -> None:
    """Report through `add(tests, reason)` the mapped tests a change to one file can affect.

    The one rule for every kind of file, used by the plan and by the drift
    check: the tests that read the file; for a file that appeared or vanished,
    the tests that listed its directory; then what its kind adds. `python` is
    (old summary, new summary, delta) for a Python file, the delta None when
    the contents are unknown or not valid Python.
    """
    kind = kind_of(path)
    if kind == EVERYTHING_KIND:
        add(all_units, f"{path} changes everything")
        return
    add(coverage.readers(path), f"reads {path}")
    if presence_changed:
        add(coverage.listers(path), f"lists the directory of {path}")
    if kind == PYTHON:
        old, new, d = python if python is not None else (None, None, None)
        # Presence counts whatever the module binds: deleting an empty one breaks its importers.
        if d is None or not d.empty or presence_changed:
            python_impact(coverage, graph, all_units, add, path, old, new, d, called or {})
    elif kind == LEAN:
        add(coverage.runners(runs_lean(lean_programs(graph, path, presence_changed))), f"runs Lean via {path}")
    elif kind == RUST:
        add(coverage.runners(runs_rust), f"runs Rust via {path}")


def python_impact(coverage: Coverage, graph: source_graph.Graph, all_units: set[str], add,
                  path: str, old: Summary | None, new: Summary | None, d,
                  called: dict[tuple[str, str], frozenset[str]]) -> None:
    """Report through `add(tests, reason)` the mapped tests one module's change can affect."""
    defs = set((old.units if old else {}) | (new.units if new else {}))
    if d is None:
        defs |= set(coverage.functions.get(path, {}))  # contents unknown: whatever ran there
    # A module that appears or vanishes changes what importing it does, whatever it binds.
    if d is None or d.effect or d.decorated or path.endswith("__init__.py") or (old is None) != (new is None):
        add(coverage.importers(path) | coverage.file_wide(path, defs), f"{path}: import-time change")
        if d is None:
            return
    for qualname in d.changed | d.removed:
        add(coverage.tests_of(path, qualname), f"{path}:{qualname}")
    for qualname in sorted(d.added):
        name = qualname.rsplit(".", 1)[-1]
        if not any(name in references for key, references in called.items() if key != (path, qualname)):
            # Nothing in the change calls it by name: it may be dispatched dynamically.
            add(coverage.file_wide(path, defs - d.added), f"{path}: new {qualname} not called by name")
    if d.binds:
        taint(coverage, graph, all_units, add, path, old, new, set(d.binds), set())


def taint(coverage: Coverage, graph: source_graph.Graph, all_units: set[str], add, path: str,
          old: Summary | None, new: Summary | None, names: set[str],
          seen: set[tuple[str, frozenset[str]]]) -> None:
    """Report the functions that read a changed module-level name, here and in importers."""
    key = (path, frozenset(names))
    if key in seen:
        return
    seen.add(key)
    versions = [s for s in (old, new) if s is not None]
    callables: set[str] = set()
    grew = True
    while grew:
        grew = False
        for summary in versions:
            for statement in summary.statements:
                if statement.is_import:
                    continue  # importers of a changed name are reached through the graph
                if statement.references & (names | callables) and not statement.binds <= names:
                    names |= statement.binds
                    grew = True
            for unit in summary.units.values():
                if unit.references & names and unit.top not in callables:
                    callables.add(unit.top)  # import-time calls of it compute changed values
                    grew = True
    for summary in versions:
        for unit in summary.units.values():
            if unit.references & names:
                add(coverage.tests_of(path, unit.qualname), f"{path}:{unit.qualname} reads a changed name")
    if path in all_units:
        add([path], f"{path} reads a changed name")
    for importer in graph.reverse.get(path, ()):
        imported = graph.imported_names.get((importer, path), set())
        summary = graph.summaries.get(importer)
        if summary is None:
            continue
        if "<module>" in imported:
            reached = names & summary.attributes  # `module.NAME`
        elif "*" in imported:
            reached = set(names)
        else:
            reached = imported & names
        if reached:
            taint(coverage, graph, all_units, add, importer, None, summary, reached, seen)


def lean_programs(graph: source_graph.Graph, path: str, presence_changed: bool) -> set[str]:
    """Executables a Lean input can change: those whose root imports the module."""
    if path.endswith(".lean") and not presence_changed:
        return graph.executables_using(".".join(Path(path).with_suffix("").parts[1:]))
    return set(lean_executables())  # a project file, or a module that appeared or vanished


def runs_lean(executables: set[str]):
    programs = {f"lean/.lake/build/bin/{name}" for name in executables} | {"lake", "lean"}
    return lambda name: name in programs


def runs_rust(name: str) -> bool:
    return name.startswith("rust/target/") or name in ("cargo", "rustc")


def lean_change(sel: Selection, change: Change) -> None:
    path = change.path
    sel.code = sel.lean = sel.audit = True
    if path.endswith(".lean"):
        sel.checks.add(CHECK_LEAN)
    executables = lean_programs(sel.graph, path, change.presence_changed)
    mapped(sel, change)
    tokens = {f"lean-exe:{name}" for name in executables} | {"lean-tool"}
    sel.static(lambda _, mentions: bool(tokens & mentions), f"runs Lean via {path}")
    sel.static(mentions_path(path), f"names {path}")


def rust_change(sel: Selection, change: Change) -> None:
    sel.code = sel.rust = True
    if change.path.endswith((".rs", "Cargo.toml")):
        sel.checks.add(CHECK_RUST)
    mapped(sel, change)
    sel.static(lambda _, mentions: "rust" in mentions, f"runs Rust via {change.path}")


def data_change(sel: Selection, change: Change, rust_sources: dict[str, str]) -> None:
    path = change.path
    if not path.endswith(DOCUMENT_SUFFIXES):
        sel.code = True
    mapped(sel, change)
    sel.static(mentions_path(path), f"names {path}")
    name = posixpath.basename(path)
    if any(name in text for text in rust_sources.values()):
        sel.rust = True  # Rust tests embed fixtures with include_bytes!


def rust_texts() -> dict[str, str]:
    return {path: (ROOT / path).read_text(encoding="utf-8", errors="replace")
            for path in git_lines("ls-files", "rust/*.rs")}


def is_lean_input(path: str) -> bool:
    return path.endswith(".lean") and path.startswith("lean/") or path in LEAN_PROJECT


def is_rust_input(path: str) -> bool:
    return path in RUST_PROJECT or (path.startswith("rust/") and path.endswith((".rs", "Cargo.toml")))


def uncertain_since(coverage: Coverage, graph: source_graph.Graph, all_units: set[str],
                    base: str) -> tuple[set[str], int]:
    """Units whose coverage at `base` may differ from the map's, and how many files differ.

    Cached per (map commit, base commit) next to the graph cache.
    """
    base_commit = git_lines("rev-parse", base)[0]
    cache = source_graph.cache_path(ROOT).with_name(
        f"uncertain-{coverage.commit[:16]}-{base_commit[:16]}-{SELECTOR_VERSION}.json")
    try:
        cached = json.loads(cache.read_text())
        return set(cached["uncertain"]), cached["drift"]
    except (OSError, ValueError, KeyError):
        pass
    status = dict(line.split("\t", 1)[::-1] for line in git_lines(
        "diff", "--no-renames", "--name-status", coverage.commit, base_commit))
    python = [p for p in status if p.endswith(".py")]
    contents = blobs([f"{rev}:{p}" for p in python for rev in (coverage.commit, base_commit)])
    versions = {p: (contents[f"{coverage.commit}:{p}"], contents[f"{base_commit}:{p}"]) for p in python}
    found = uncertain_units(coverage, graph, all_units, status, versions)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"uncertain": sorted(found), "drift": len(status)}))
    return found, len(status)


def uncertain_units(coverage: Coverage, graph: source_graph.Graph, all_units: set[str],
                    status: dict[str, str], versions: dict[str, tuple[str | None, str | None]]) -> set[str]:
    """Units whose recorded run may differ now, given what changed since the map.

    `status` maps each changed path to git's A/D/M letter; `versions` gives the
    map-time and current text of each changed Python file. A test that ran
    none of the changed code (no changed function, no module whose
    import-time statements changed, no changed file it read or program it
    ran) runs the same way now as when it was recorded, so its map entry
    still holds. Every other test is uncertain.
    """
    found: set[str] = set()
    # Keep what deleted and changed files imported and named at the map's commit.
    graph = graph.overlay({path: versions[path][0] if path in versions else (None if letter == "A" else "")
                           for path, letter in status.items()})

    def add(tests, _reason=""):
        found.update(test for test in tests if test in all_units)

    parsed = {}
    for path, (before, after) in versions.items():
        module, package = source_graph.module_name(path)
        try:
            parsed[path] = (source_graph.summary_of(before, module, package) if before is not None else None,
                            source_graph.summary_of(after, module, package) if after is not None else None)
        except SyntaxError:
            parsed[path] = None
    called = {}
    for path, pair in parsed.items():
        if pair is not None:
            for qualname, references in delta(*pair).references.items():
                called[(path, qualname)] = references
    for path, letter in status.items():
        add([path])  # a changed test's own record is stale
        python = None
        if path in parsed:
            pair = parsed[path]
            python = (None, None, None) if pair is None else (*pair, delta(*pair))
        # Any letter but M (T: a file became a link or back) may change what is there.
        file_impact(coverage, graph, all_units, add, path, letter != "M", python, called)
        if kind_of(path) == PYTHON and letter == "A":
            # Added since the map: no recorded test can have imported it.
            add(test for test in all_units if path in graph.closure(test)[0])
    return found


def resolve_map(base: str, coverage) -> Coverage | None:
    if isinstance(coverage, Coverage) or coverage is None:
        return coverage
    if isinstance(coverage, dict):
        test_map.validate(coverage)
        return Coverage(coverage)
    if coverage == "auto":
        # A map recorded by `--run` for exactly this tree is fresh: nothing drifted.
        tree = test_map.tree_map_path(git_lines("rev-parse", f"{base}^{{tree}}")[0])
        try:
            data = test_map.load(tree)
            data["commit"] = git_lines("rev-parse", base)[0]
            return Coverage(data, tree)
        except (OSError, ValueError, EOFError):
            pass
    path = Path(coverage) if coverage != "auto" else test_map.find_map(base)
    if path is None or not path.exists():
        return None
    return Coverage(test_map.load(path), path)


def select(paths: list[str] | None = None, *, full: bool = False, base: str = "HEAD",
           after: str | None = None, changes: list[Change] | None = None,
           coverage="auto", assume_fresh: bool = False) -> dict:
    """Plan for `changes` (or `paths`, compared between `base` and `after`/the working tree).

    `coverage` is a map path, a loaded map, None for the static graph only, or
    "auto" for the nearest cached map recorded at an ancestor of `base`.
    `assume_fresh` treats the map as if recorded at `base` (an estimate, for
    reports only: it skips the drift check that keeps selection safe).
    """
    started = time.monotonic()
    if changes is None:
        paths = sorted(set(path.removeprefix("./") for path in paths or []))
        changes = read_changes(paths, base=base, after=after)
        if after is None:
            for change in changes:
                if change.old == change.new:  # named but not edited: assume anything changed
                    change.known = change.presence_known = False
    paths = [change.path for change in changes]
    # The tree after the change, plus each changed file as it was before it: a
    # deleted module or fixture still leads to the tests that used it.
    graph = source_graph.load(ROOT).overlay({change.path: change.old for change in changes})
    all_units = units()
    cov = resolve_map(base, coverage)
    unmapped = set(all_units)
    uncertain: set[str] = set()
    drift_files = 0
    if cov is not None:
        try:
            uncertain, drift_files = (set(), 0) if assume_fresh else uncertain_since(
                cov, graph, set(all_units), base)
        except subprocess.CalledProcessError:
            cov = None  # the map's commit is not in this repository
    if cov is not None:
        unmapped = (set(all_units) - cov.recorded) | uncertain
    sel = Selection(graph, cov, unmapped, all_units)
    if full or not changes:
        sel.full.append("requested" if full else "no changed paths")
    parsed = {change.path: parse(change) for change in changes if change.path.endswith(".py")}
    called: dict[tuple[str, str], frozenset[str]] = {}
    for change in changes:
        if change.path in parsed and change.known:
            for qualname, references in delta(*parsed[change.path]).references.items():
                called[(change.path, qualname)] = references
    rust_sources = None
    for change in changes:
        path = change.path
        kind = kind_of(path)
        if kind == EVERYTHING_KIND:
            sel.full.append(path)
            continue
        if path in PYTHON_LAYER_INPUTS or path == ".importlinter":
            sel.checks.add(CHECK_PYTHON)
        if path in LEAN_LAYER_INPUTS:
            sel.checks.add(CHECK_LEAN)
        if path in RUST_LAYER_INPUTS:
            sel.checks.add(CHECK_RUST)
        if path == "lean/audit.py":
            sel.audit = True
        if kind == PYTHON:
            python_change(sel, change, *parsed[path], called)
        elif kind == LEAN:
            lean_change(sel, change)
        elif kind == RUST:
            rust_change(sel, change)
        else:
            if rust_sources is None:
                rust_sources = rust_texts()
            data_change(sel, change, rust_sources)
    source_graph.save_summaries()
    return finish(sel, changes, paths, started, drift_files)


def finish(sel: Selection, changes: list[Change], paths: list[str], started: float,
           drift_files: int) -> dict:
    full = bool(sel.full)
    if full:
        selected = list(sel.all_units)
        sel.lean = sel.audit = sel.rust = True
        sel.checks |= {CHECK_PYTHON, CHECK_LEAN, CHECK_RUST}
    else:
        if sel.code:
            sel.add(SMOKE, "smoke")
        selected = sorted(sel.reasons)
    pytest_files = [t for t in selected if t.startswith("tests/")]
    extra = [t for t in selected if t in EXTRA_UNITS]
    sources = {t: (ROOT / t).read_text() for t in selected if (ROOT / t).exists()}
    executables = lean_executables()
    cov = sel.coverage

    def uses(token_test, program: str) -> bool:
        return (cov is not None and token_test in cov.recorded and token_test in cov.runners(
            lambda name: name == program)) or program.rsplit("/", 1)[-1] in sources.get(token_test, "")

    needed_lean = {name for name in executables
                   if any(uses(t, f"lean/.lake/build/bin/{name}") for t in selected)} if selected else set()
    lean = sel.lean or any(not (ROOT / "lean/.lake/build/bin" / name).exists() for name in needed_lean)
    rust_users = [t for t in selected if "rust/target/" in sources.get(t, "") or "VE_W5_RUST_BIN" in sources.get(t, "")
                  or (cov is not None and t in cov.runners(lambda n: n.startswith("rust/target/")))]
    rust_release = sel.rust or (bool(rust_users) and not (ROOT / "rust/target/release/ve").exists())
    rust_debug = sel.rust or (any("rust/target/debug/ve" in sources.get(t, "") for t in selected)
                              and not (ROOT / "rust/target/debug/ve").exists())
    commands = [list(check) for check in (CHECK_PYTHON, CHECK_LEAN, CHECK_RUST) if check in sel.checks]
    if lean:
        commands.append(["lake", "build"])
        # Harness executables outside defaultTargets must be named.
        named = sorted(name for name in executables if name not in lean_default_targets()
                       and (full or name in needed_lean or sel.lean))
        if named:
            commands.append(["lake", "build", *named])
    if sel.audit:
        commands.append(list(AUDIT))
    if sel.rust:
        commands.append([*CARGO, "test", "--locked", "--all-features", "--manifest-path",
                         "rust/Cargo.toml", "--", "--test-threads=1"])
    if rust_release:
        commands.append([*CARGO, "build", "--locked", "--release", "--manifest-path",
                         "rust/Cargo.toml", "-p", "ve"])
    if rust_debug:
        commands.append([*CARGO, "build", "--locked", "--manifest-path",
                         "rust/Cargo.toml", "-p", "ve"])
    for unit in extra:
        commands.append(list(EXTRA_UNITS[unit]))
    if pytest_files:
        commands.append(nested_pytest.command(["-q", *pytest_files], python=UV_PYTHON))
    return {"changed": paths, "selected": selected, "selected_count": len(selected),
            "full_count": len(sel.all_units), "full": full, "full_reasons": sel.full,
            "smoke": list(SMOKE), "reasons": {t: sorted(r) for t, r in sorted(sel.reasons.items())},
            "map": None if cov is None else {"commit": cov.commit, "path": str(cov.path or ""),
                                             "files_changed_since": drift_files,
                                             "uncertain_units": len(sel.unmapped)},
            "unmapped": sorted(sel.unmapped) if cov is not None else "all (static graph only)",
            "commands": commands, "lean_build": lean, "rust_build": sel.rust,
            "seconds": round(time.monotonic() - started, 2)}


# --- Impacted mode: the fast path for local iteration (docs/TESTING.md) ---
#
# A test runs when a file it depends on changed: a local Python module in its import
# closure (tests, their helpers, conformance, tools, ve and ve_experiments), a Lean module
# in an executable that code in that closure names, the Rust checker when that code names
# it, or a data path that code names. A change no test reaches selects the full suite,
# except a Python file outside the product (a script or report generator), which selects
# only ALWAYS and is reported. The gate still runs everything.

PYTHON_ROOTS = ("ve", "ve_experiments", "conformance", "tools", "tests", "usecases", "experiments")
# Path components too generic to tie a data file to the tests naming it.
GENERIC = {"ve", "tests", "tools", "conformance", "usecases", "experiments", "docs", "lean", "rust",
           "src", "data", "examples", "json", "README.md", "VE", "spec"}
# Trees whose directories tests name one component at a time (`ROOT / "usecases" / "asimov-laws"`).
NAMED_TREES = {"usecases", "experiments", "conformance", "docs", "design", "examples", "data", "paper"}
# Test-side code that names these starts (or configures) a native checker: Rust, any
# Lean executable (the service under the Lean authority), or reads the Lean sources.
RUST_SIGNALS = ("rust/target", "VE_RUST", "VE_W5_RUST_BIN", "rust_jsonl", "cargo", "VE_AUTHORITY")
LEAN_SIGNALS = ("LeanService", "lean_service", "lean_runner", "VE_AUTHORITY", ".lake", "lake",
                '*.lean', '.lean"', ".lean'", "lean/VE")
# Sources of a test file that neither its imports nor its text name (none so far):
# tests/test_select_tests.py fails for a test file no source path reaches.
EXTRA_SOURCES: dict[str, tuple[str, ...]] = {}
# Product modules that start a native checker only when a test selects its authority or
# builds a client itself (which the test-side code then names), never on their own.
ON_REQUEST = {"ve/backends/lean_service.py", "ve/backends/lean_runner.py", "ve/backends/rust_jsonl.py",
              "ve/backends/dispatch.py", "ve/ast.py", "ve/evaluate.py", "ve/search.py"}
# These exercise the public wire across languages, routes, and frozen fixtures.
ALWAYS = {
    "tests/test_conformance.py", "tests/test_lean_conformance.py",
    "tests/test_replay_conservativity.py", "tests/test_p0_three_way.py",
    "tests/test_difffuzz.py",
}
IMPACTED_CHECKS = (CHECK_PYTHON, CHECK_LEAN, CHECK_RUST, ("python3", "tools/test_layer_policy.py"))
EXPORTS = python_exports(ROOT)


def native_commands(paths: list[str], selected: list[str], fallback: bool) -> tuple[list[list[str]], bool, bool]:
    """The checks, the native builds the selection needs, and the pytest run of `selected`."""
    selected_sources = [(ROOT / p).read_text() for p in selected]
    lean = (fallback or any(p.startswith("lean/") or p.startswith("conformance/") for p in paths)
            or not (ROOT / "lean/.lake/build/bin/ve_conformance").exists()
            or any(any(name in source for source in selected_sources)
                   and not (ROOT / "lean/.lake/build/bin" / name).exists()
                   for name in lean_executables()))
    rust = fallback or any(p.startswith("rust/") or p.startswith("conformance/") for p in paths)
    rust_release_binary = (rust or (any("rust/target/release/ve" in source or "VE_W5_RUST_BIN" in source
                                        for source in selected_sources)
                                    and not (ROOT / "rust/target/release/ve").exists()))
    rust_debug_binary = (rust or (any("rust/target/debug/ve" in source for source in selected_sources)
                                  and not (ROOT / "rust/target/debug/ve").exists()))
    commands = [list(cmd) for cmd in IMPACTED_CHECKS]
    if lean:
        commands.append(["lake", "build"])
        # Harness executables such as ve_risk_eval are outside defaultTargets.
        named = sorted(name for name in lean_executables()
                       if name not in lean_default_targets()
                       and any(name in source for source in selected_sources))
        if named:
            commands.append(["lake", "build", *named])
    commands.append(list(AUDIT))
    if rust:
        commands.append([*CARGO, "test", "--locked", "--all-features", "--manifest-path",
                         "rust/Cargo.toml", "--", "--test-threads=1"])
    if rust_release_binary:
        commands.append([*CARGO, "build", "--locked", "--release", "--manifest-path",
                         "rust/Cargo.toml", "-p", "ve"])
    if rust_debug_binary:
        commands.append([*CARGO, "build", "--locked", "--manifest-path",
                         "rust/Cargo.toml", "-p", "ve"])
    commands.append(nested_pytest.command(["-q", *selected], python=UV_PYTHON))
    return commands, lean, rust


def module_file(name: str) -> str | None:
    """The repository file a dotted module name is, if local (`ve.ast`, `tests.subprocesses`)."""
    path = ROOT.joinpath(*name.split("."))
    for candidate in (path.with_suffix(".py"), path / "__init__.py"):
        if candidate.is_file():
            return candidate.relative_to(ROOT).as_posix()
    return None


@cache
def python_dependencies(relative: str) -> frozenset[str]:
    """The local Python files `relative` imports directly, function-level imports included
    (they run when the function does)."""
    path = ROOT / relative
    try:
        tree = ast.parse(path.read_text(), relative)
    except (SyntaxError, UnicodeDecodeError):
        return frozenset()
    package = Path(relative).parent.parts
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                anchor = package[:len(package) - node.level + 1]
                base = ".".join((*anchor, *([base] if base else [])))
            names.append(base)
            names += [f"{base}.{alias.name}" for alias in node.names]
            if base == "ve":
                names += [EXPORTS[alias.name] for alias in node.names if alias.name in EXPORTS]
    found = set()
    for name in filter(None, names):
        parts = name.split(".")
        for end in range(len(parts), 0, -1):
            prefix = ".".join(parts[:end])
            # A bare name is also a sibling (tools/ scripts import one another bare), a tests/
            # helper (pytest's rootdir import) or a tools/ script (a test puts tools/ on the path).
            target = next(filter(None, (module_file(candidate) for candidate in (
                prefix, ".".join((*package, prefix)), f"tests.{prefix}", f"tools.{prefix}"))), None)
            if target:
                found.add(target)
                break
    found.discard(relative)
    # The `ve` facade imports every module for its reexports; a name taken from it
    # resolves to its defining module above, so the facade itself is not a dependency.
    found.discard("ve/__init__.py")
    return frozenset(found)


@cache
def closure(relative: str) -> frozenset[str]:
    """`relative` and every local Python file it imports, transitively."""
    seen, todo = set(), [relative]
    while todo:
        current = todo.pop()
        if current not in seen:
            seen.add(current)
            todo.extend(python_dependencies(current))
    return frozenset(seen)


@cache
def test_closure(test: str) -> frozenset[str]:
    """What pytest loads for the test file `test`: its closure and the closure of every
    conftest.py from the repository root down to its directory, which pytest imports
    for each test below it without the test naming it."""
    directories = [ROOT, *(ROOT / part for part in Path(test).parents[:-1][::-1])]
    conftests = [(directory / "conftest.py").relative_to(ROOT).as_posix() for directory in directories
                 if (directory / "conftest.py").is_file()]
    return closure(test).union(*(closure(conftest) for conftest in conftests))


@cache
def text(relative: str) -> str:
    return (ROOT / relative).read_text(errors="replace")


@cache
def strings(relative: str) -> str:
    """The string literals of a Python file's code, docstrings left out, one per line: what
    it can name a path, an executable or a setting with."""
    tree = ast.parse(text(relative), relative)
    docstrings = {id(node.body[0].value) for node in ast.walk(tree)
                  if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                  and node.body and isinstance(node.body[0], ast.Expr)
                  and isinstance(node.body[0].value, ast.Constant)}
    return "\n".join(node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)
                     and isinstance(node.value, str) and id(node) not in docstrings)


@cache
def literals(relative: str) -> str:
    """Every string literal of a Python file, docstrings included, comments left out."""
    try:
        tree = ast.parse(text(relative), relative)
    except SyntaxError:
        return text(relative)
    return "\n".join(node.value for node in ast.walk(tree)
                     if isinstance(node, ast.Constant) and isinstance(node.value, str))


def names_any(body: str, names) -> bool:
    return any(re.search(rf"(?<![\w]){re.escape(name)}(?![\w])", body) for name in names)


@cache
def static_graph() -> source_graph.Graph:
    return source_graph.load(ROOT)


@cache
def lean_executables_of(module: str) -> frozenset[str]:
    """The Lean executables whose import closure holds `module`."""
    return frozenset(static_graph().executables_using(module))


def reaches(test: str, changed: str) -> bool:
    """Whether a change to `changed` can change the outcome of the test file `test`."""
    if changed in test_closure(test) or changed in EXTRA_SOURCES.get(test, ()):
        return True
    # A conftest's imports run for every test, so a change to one reaches them all (above).
    # Native checkers are another matter: the conftest builds them once per session (the
    # plan's own build command covers a native change) and starts none, so whether a test
    # runs one is decided by its own closure.
    native = changed.startswith(("lean/", "rust/"))
    files = closure(test) if native else test_closure(test)
    # Data paths and checker configuration are named by the test side (tests, the harness,
    # tools); a product module names the executables it starts on its own.
    harness = [literals(f) for f in files if not f.startswith(("ve/", "ve_experiments/"))]
    product = [strings(f) for f in files if f.startswith(("ve/", "ve_experiments/")) and f not in ON_REQUEST]
    if changed.startswith("lean/"):
        if Path(changed).suffix == ".lean":
            module = ".".join(Path(changed).with_suffix("").parts[1:])
            names = lean_executables_of(module)
        else:  # lakefile, toolchain or manifest: every executable
            names = frozenset(lean_executables())
        return any(names_any(body, names) for body in harness + product) or \
            any(signal in body for body in harness for signal in LEAN_SIGNALS)
    if changed.startswith("rust/"):
        return any(signal in body for body in harness for signal in RUST_SIGNALS) or \
            "ve/readings_route.py" in files
    # The path, its file name, its directories' paths, and (in a use case, experiment or
    # data tree, whose directories are named on their own) its directories' names.
    path = Path(changed)
    names = {changed, *(parent.as_posix() for parent in path.parents if len(parent.parts) >= 2)}
    if path.name not in GENERIC and len(path.name) >= 4:
        names.add(path.name)
    if path.parts[0] in NAMED_TREES:
        names.update(part for part in path.parts[1:-1] if part not in GENERIC and len(part) >= 4)
    pattern = re.compile("|".join(rf"(?<![\w.-]){re.escape(name)}(?![\w-])" for name in sorted(names))) \
        if names else None
    return any(changed in body or (pattern and pattern.search(body)) for body in harness)


def impacted(paths: list[str], *, full: bool = False) -> dict:
    paths = sorted(set(path.removeprefix("./") for path in paths))
    tests = [path.relative_to(ROOT).as_posix() for path in TESTS]
    reached, unreached, scripts = {}, [], []
    for changed in paths:
        hits = [test for test in tests if (ROOT / changed).exists() and reaches(test, changed)] \
            if not changed.startswith("tests/test_") else [changed] * (ROOT / changed).exists()
        if changed.startswith("tests/test_"):
            hits += [test for test in tests if changed in test_closure(test)]
        reached[changed] = sorted(set(hits))
        if changed == "ve/__init__.py" or not (ROOT / changed).exists():
            unreached.append(changed)  # the facade reexports every layer; a deletion has no reader left
        elif not hits:
            product = not changed.endswith(".py") or changed.startswith("ve/")
            (unreached if product else scripts).append(changed)
    fallback = full or not paths or bool(unreached)
    selected = sorted(tests if fallback else {t for hits in reached.values() for t in hits} | ALWAYS)
    commands, lean, rust = native_commands(paths, selected, fallback)
    return {"mode": "impacted", "changed": paths, "reached": reached, "unreached": unreached,
            "scripts_without_tests": scripts, "fallback": fallback, "selected": selected,
            "selected_count": len(selected), "full_count": len(TESTS), "always": sorted(ALWAYS),
            "commands": commands, "lean_build": lean, "rust_build": rust}


def working_changes(commit: str) -> tuple[dict[str, str], dict[str, tuple[str | None, str | None]]]:
    """Git status letters and Python texts for the working tree against `commit`."""
    status = dict(line.split("\t", 1)[::-1] for line in git_lines(
        "diff", "--no-renames", "--name-status", commit))
    status.update({path: "A" for path in git_lines("ls-files", "--others", "--exclude-standard")})
    python = [p for p in status if p.endswith(".py")]
    old = blobs([f"{commit}:{p}" for p in python])
    versions = {p: (old[f"{commit}:{p}"],
                    (ROOT / p).read_text(encoding="utf-8", errors="replace") if (ROOT / p).is_file() else None)
                for p in python}
    return status, versions


def run_recorded(plan: dict, jobs: int) -> int:
    """Run the selected units one process each under the recorder, then save a map for this tree.

    Units the run did not record keep their entries from the map the plan
    used, unless the working tree changed code they ran: those are marked
    unrecorded, so the static graph answers for them until they run again.
    """
    selected = plan["selected"]
    tree = test_map.working_tree_id()
    test_map.build_natives()
    work = Path(tempfile.mkdtemp(prefix="ve-select-run-"))
    results = test_map.record_units(selected, work, jobs, test_map.UNIT_TIMEOUT)
    failed = [unit for unit in selected if results[unit]["exit"] not in (0, 5)]
    for unit in failed:
        log = work / (unit.replace("/", "__") + ".log")
        print(f"FAILED {unit} (exit {results[unit]['exit']}); log {log}\n"
              + "\n".join(log.read_text(errors="replace").splitlines()[-25:]), flush=True)
    every = set(units())
    base = resolve_map("HEAD", plan["map"]["path"]) if plan["map"] else None
    stale: set[str] = set()
    if base is not None:
        status, versions = working_changes(base.commit)
        stale = uncertain_units(base, source_graph.load(ROOT), every, status, versions) - set(selected)
        edges = test_map.unit_edges({"tests": base.tests, "functions": base.functions, "reads": base.reads,
                                     "dirs": base.dirs, "programs": base.programs})
        for unit in sorted(every - set(selected)):
            if unit in edges and unit in base.status:
                results[unit] = {**edges[unit], **base.status[unit]}
                if unit in stale:
                    results[unit]["exit"] = "stale"  # ran changed code; not re-run here
    data = test_map.build_map(results, base.commit if base is not None else "")
    data["tree"] = tree
    test_map.write_map(data, test_map.tree_map_path(tree))
    shutil.rmtree(work, ignore_errors=True)
    print(f"recorded {len(selected)} units for tree {tree[:10]}; {len(stale)} others left to the "
          f"static graph until they run; {len(failed)} failed", flush=True)
    return 1 if failed else 0


def run(plan: dict, *, record: bool = True, jobs: int = 8) -> int:
    # The selected tests run as the gate runs them, whatever pytest settings the shell has.
    env = nested_pytest.environment(os.environ)
    env.setdefault("UV_CACHE_DIR", "/tmp/ve-layers-uv-cache")
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    if plan["lean_build"]:
        env["VE_LEAN_PREBUILT"] = "1"
    for command in plan["commands"]:
        if record and (command in [list(c) for c in EXTRA_UNITS.values()] or command[:len(PYTEST)] == PYTEST):
            continue  # recorded below, one process per unit
        print("+", " ".join(command), flush=True)
        cwd = ROOT / "lean" if command[:2] == ["lake", "build"] else ROOT
        result = subprocess.run(command, cwd=cwd, env=env, check=False)
        if result.returncode:
            return result.returncode
    if record and plan["selected"]:
        return run_recorded(plan, jobs)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--base", help="merge base for a branch diff")
    source.add_argument("--commit", help="one historical commit")
    source.add_argument("--paths", nargs="+", help="explicit changed paths")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--impacted", action="store_true",
                        help="the map-free fast path: only the tests whose static dependencies "
                             "changed, run in one plain pytest process")
    parser.add_argument("--map",help="coverage map (default: newest cached ancestor map)")
    parser.add_argument("--static", action="store_true", help="ignore the coverage map")
    parser.add_argument("--assume-fresh", action="store_true",
                        help="treat the map as recorded at the base (an estimate for reports; "
                             "skips the drift check, so not safe for real runs)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--explain", action="store_true", help="print why each test is selected")
    parser.add_argument("--run", action="store_true",
                        help="run the plan; each selected test file runs in its own recorded "
                             "process, and the coverage is saved for this tree")
    parser.add_argument("--no-record", action="store_true",
                        help="with --run: one plain pytest process, nothing recorded")
    parser.add_argument("--jobs", type=int, default=8, help="parallel test files for --run")
    args = parser.parse_args()
    paths = args.paths if args.paths is not None else changed_paths(args.base, args.commit)
    if args.impacted:
        plan = impacted(paths, full=args.full)
        if args.json:
            print(json.dumps(plan, indent=2))
            return run(plan, record=False) if args.run else 0
        print(f"impacted{' (full fallback)' if plan['fallback'] else ''}: "
              f"{plan['selected_count']}/{plan['full_count']} Python test files")
        for path in plan["unreached"]:
            print(f"no test reaches {path}: full suite")
        for path in plan["scripts_without_tests"]:
            print(f"warning: no test reaches {path}")
        print("changed:", ", ".join(paths) or "(none; full fallback)")
        for command in plan["commands"]:
            print("+", " ".join(command))
        return run(plan, record=False) if args.run else 0
    if args.commit:
        base, after = f"{args.commit}^", args.commit
    elif args.base:
        base, after = git_lines("merge-base", args.base, "HEAD")[0], "HEAD"
    else:
        base, after = "HEAD", None
    coverage = None if args.static else (args.map or "auto")
    plan = select(paths, full=args.full, base=base, after=after, coverage=coverage,
                  assume_fresh=args.assume_fresh)
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        where = f"map {plan['map']['commit'][:10]}" if plan["map"] else "static graph only"
        print(f"{plan['selected_count']}/{plan['full_count']} test units ({where}, "
              f"{plan['seconds']} s){' FULL: ' + ', '.join(plan['full_reasons']) if plan['full'] else ''}")
        print("changed:", ", ".join(paths) or "(none; full fallback)")
        if args.explain:
            for test, reasons in plan["reasons"].items():
                print(f"  {test}: {'; '.join(reasons[:3])}{' ...' if len(reasons) > 3 else ''}")
        for command in plan["commands"]:
            print("+", " ".join(command))
    return run(plan, record=not args.no_record, jobs=args.jobs) if args.run else 0


if __name__ == "__main__":
    raise SystemExit(main())
