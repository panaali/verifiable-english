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
  selects every test that ran a function of its file.
* Lean: the executables whose root imports the module, then the tests that
  ran them; Rust: the tests that ran a Rust binary, and `cargo test`.
* Any other file: the tests that read it, and, for an added or removed file,
  the tests that listed its directory. Documentation only selects its readers.
* The map is recorded for an earlier commit. Code that changed since then
  ("drift") may call the changed code anew: drift units that name what changed
  add their own tests. Tests the map does not cover (new, failed or opaque when
  recorded, or changed since) are selected by the static graph
  (tools/source_graph.py), which is also the whole answer without a usable map.
* Unknown files, `tests/conftest.py`, `pyproject.toml` and `uv.lock` select
  everything. Anything selected beyond documentation also runs SMOKE.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import posixpath
import subprocess
import sys
import time

from change_units import Summary, delta
from layer_policy import ROOT, lean_default_targets, lean_executables
import source_graph
import test_map

TESTS = sorted((ROOT / "tests").glob("test_*.py"))
EXTRA_UNITS = test_map.EXTRA_UNITS
# Fast tests across parser, environment, wire and both native backends.
SMOKE = ("tests/test_conformance.py", "tests/test_surface_registry.py", "tests/test_definitions.py")
CHECK_PYTHON = ("uv", "run", "--frozen", "--group", "dev", "python", "tools/check_python_layers.py")
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
# A map whose commit is this many changed files away from the base is not used.
STALE_DRIFT = 400


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

    @property
    def presence_changed(self) -> bool:
        return (self.old is None) != (self.new is None)


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
        """Tests that listed the nearest recorded directory above `path`."""
        parent = posixpath.dirname(path)
        while parent:
            if parent in self.dirs:
                return self._names(self.dirs[parent])
            parent = posixpath.dirname(parent)
        return set()

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


def mentions_path(path: str):
    """Predicate: a closure names the file or one of its directories."""
    directories = set()
    parent = posixpath.dirname(path)
    while parent:
        directories.add(f"dir:{parent}")
        parent = posixpath.dirname(parent)
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
    path, coverage, graph = change.path, sel.coverage, sel.graph
    if coverage is not None:
        sel.add(coverage.readers(path), f"reads {path}")
    sel.static(mentions_path(path), f"names {path}")
    if (path.startswith("tests/test_") or path in EXTRA_UNITS) and change.new is not None:
        sel.add([path], "changed test")
    d = delta(old, new) if change.known else None
    if d is not None and d.empty:
        if change.presence_changed:
            sel.code = True
        return  # comments and docstrings only
    sel.code = True
    if path.startswith(("ve/", "ve_experiments/", "experiments/")) and (
            d is None or d.imports_changed or change.presence_changed):
        sel.checks.add(CHECK_PYTHON)
    sel.static(lambda files, _: path in files, f"imports {path}")
    if coverage is None:
        return
    defs = set((old.units if old else {}) | (new.units if new else {}))
    if d is None or d.effect or d.decorated or path.endswith("__init__.py"):
        sel.add(coverage.importers(path) | coverage.file_wide(path, defs),
                f"{path}: import-time change")
        if d is None:
            return
    for qualname in d.changed | d.removed:
        sel.add(coverage.tests_of(path, qualname), f"{path}:{qualname}")
    for qualname in sorted(d.added):
        name = qualname.rsplit(".", 1)[-1]
        if not any(name in references for key, references in called.items() if key != (path, qualname)):
            # Nothing in the change calls it by name: it may be dispatched dynamically.
            sel.add(coverage.file_wide(path, defs - d.added),
                    f"{path}: new {qualname} not called by name in the change")
    if d.binds:
        taint(sel, path, old, new, set(d.binds), set())


def taint(sel: Selection, path: str, old: Summary | None, new: Summary | None,
          names: set[str], seen: set[tuple[str, frozenset[str]]]) -> None:
    """Select functions that read a changed module-level name, here and in importers."""
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
                sel.add(sel.coverage.tests_of(path, unit.qualname), f"{path}:{unit.qualname} reads a changed name")
    if path in sel.all_units:
        sel.add([path], f"{path} reads a changed name")
    for importer in sel.graph.reverse.get(path, ()):
        imported = sel.graph.imported_names.get((importer, path), set())
        summary = sel.graph.summaries.get(importer)
        if summary is None:
            continue
        if "<module>" in imported:
            reached = names & summary.identifiers
        elif "*" in imported:
            reached = set(names)
        else:
            reached = imported & names
        if reached:
            taint(sel, importer, None, summary, reached, seen)


def lean_change(sel: Selection, change: Change) -> None:
    path = change.path
    sel.code = sel.lean = sel.audit = True
    if path.endswith(".lean"):
        sel.checks.add(CHECK_LEAN)
        module = ".".join(Path(path).with_suffix("").parts[1:])
        executables = sel.graph.executables_using(module)
        if change.presence_changed:
            executables = set(lean_executables())  # a new or removed module may change any root
    else:
        executables = set(lean_executables())
    programs = {f"lean/.lake/build/bin/{name}" for name in executables} | {"lake", "lean"}
    if sel.coverage is not None:
        sel.add(sel.coverage.runners(lambda name: name in programs), f"runs Lean via {path}")
        sel.add(sel.coverage.readers(path), f"reads {path}")
    tokens = {f"lean-exe:{name}" for name in executables} | {"lean-tool"}
    sel.static(lambda _, mentions: bool(tokens & mentions), f"runs Lean via {path}")
    sel.static(mentions_path(path), f"names {path}")


def rust_change(sel: Selection, change: Change) -> None:
    sel.code = sel.rust = True
    if change.path.endswith((".rs", "Cargo.toml")):
        sel.checks.add(CHECK_RUST)
    if sel.coverage is not None:
        sel.add(sel.coverage.runners(lambda name: name.startswith("rust/target/")
                                     or name in ("cargo", "rustc")), f"runs Rust via {change.path}")
        sel.add(sel.coverage.readers(change.path), f"reads {change.path}")
    sel.static(lambda _, mentions: "rust" in mentions, f"runs Rust via {change.path}")


def data_change(sel: Selection, change: Change, rust_sources: dict[str, str]) -> None:
    path = change.path
    document = path.endswith(DOCUMENT_SUFFIXES)
    if not document:
        sel.code = True
    if sel.coverage is not None:
        sel.add(sel.coverage.readers(path), f"reads {path}")
        if change.presence_changed:
            sel.add(sel.coverage.listers(path), f"lists the directory of {path}")
    sel.static(mentions_path(path), f"names {path}")
    name = posixpath.basename(path)
    if any(name in text for text in rust_sources.values()):
        sel.rust = True  # Rust tests embed fixtures with include_bytes!


def rust_texts() -> dict[str, str]:
    return {path: (ROOT / path).read_text(encoding="utf-8", errors="replace")
            for path in git_lines("ls-files", "rust/*.rs")}


def drift_units(paths: list[str], commit: str, base: str) -> dict[str, set[str]]:
    """Per drift Python file, the units changed between the map's commit and the base."""
    contents = blobs([f"{rev}:{p}" for p in paths for rev in (commit, base)])
    found = {}
    for path in paths:
        module, package = source_graph.module_name(path)
        try:
            before = contents[f"{commit}:{path}"]
            after = contents[f"{base}:{path}"]
            d = delta(source_graph.summary_of(before, module, package) if before is not None else None,
                      source_graph.summary_of(after, module, package) if after is not None else None)
        except SyntaxError:
            found[path] = {"*"}
            continue
        found[path] = d.changed | d.added | ({"<module>"} if d.binds or d.effect else set())
    return found


def resolve_map(base: str, coverage) -> Coverage | None:
    if isinstance(coverage, Coverage) or coverage is None:
        return coverage
    if isinstance(coverage, dict):
        return Coverage(coverage)
    path = Path(coverage) if coverage != "auto" else test_map.find_map(base)
    if path is None or not path.exists():
        return None
    return Coverage(test_map.load(path), path)


def select(paths: list[str] | None = None, *, full: bool = False, base: str = "HEAD",
           after: str | None = None, changes: list[Change] | None = None,
           coverage="auto") -> dict:
    """Plan for `changes` (or `paths`, compared between `base` and `after`/the working tree).

    `coverage` is a map path, a loaded map, None for the static graph only, or
    "auto" for the newest cached map recorded at an ancestor of `base`.
    """
    started = time.monotonic()
    if changes is None:
        paths = sorted(set(path.removeprefix("./") for path in paths or []))
        changes = read_changes(paths, base=base, after=after)
        if after is None:
            for change in changes:
                if change.old == change.new:  # named but not edited: assume anything changed
                    change.known = False
    paths = [change.path for change in changes]
    graph = source_graph.load(ROOT)
    all_units = units()
    cov = resolve_map(base, coverage)
    unmapped = set(all_units)
    drift: list[str] = []
    if cov is not None:
        try:
            drift = git_lines("diff", "--no-renames", "--name-only", cov.commit, base)
        except subprocess.CalledProcessError:
            cov = None  # the map's commit is not in this repository
    if cov is not None and len(drift) > STALE_DRIFT:
        cov = None
    if cov is not None:
        unmapped = set(all_units) - cov.recorded
        unmapped |= {p for p in drift if p in all_units}  # their recorded edges are stale
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
        top = path.split("/", 1)[0]
        if path in EVERYTHING or ("/" not in path and not path.endswith(DOCUMENT_SUFFIXES)
                                  and path not in RUST_PROJECT and path != ".importlinter") \
                or ("/" in path and top not in KNOWN_AREAS):
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
        if path.endswith(".py"):
            python_change(sel, change, *parsed[path], called)
        elif path.endswith(".lean") or path in LEAN_PROJECT:
            lean_change(sel, change)
        elif path in RUST_PROJECT or (top == "rust" and (path.endswith(".rs") or path.endswith("Cargo.toml"))):
            rust_change(sel, change)
        else:
            if rust_sources is None:
                rust_sources = rust_texts()
            data_change(sel, change, rust_sources)
    if cov is not None and drift:
        apply_drift(sel, changes, parsed, drift, base)
    source_graph.save_summaries()
    return finish(sel, changes, paths, started)


def apply_drift(sel: Selection, changes: list[Change], parsed: dict, drift: list[str],
                base: str) -> None:
    """Units changed since the map that name changed code may now reach it."""
    names = set()
    for change in changes:
        names.add(posixpath.basename(change.path))
        if change.path in parsed:
            if not change.known:
                names.add("*")
                continue
            d = delta(*parsed[change.path])
            names |= {q.rsplit(".", 1)[-1] for q in d.changed | d.added | d.removed} | d.binds
        elif change.path.endswith(".lean"):
            names |= {f"lean-exe:{e}" for e in lean_executables()}
    changed = {c.path for c in changes}
    graph = sel.graph
    python = [p for p in drift if p.endswith(".py") and p not in changed and graph.summaries.get(p)
              and ("*" in names or names & (graph.summaries[p].identifiers | graph.summaries[p].constants))]
    if not python:
        return
    for path, drifted in drift_units(python, sel.coverage.commit, base).items():
        summary = graph.summaries[path]
        hits = names & (summary.identifiers | summary.constants)
        for qualname in drifted:
            unit = summary.units.get(qualname)
            if qualname in ("*", "<module>") or unit is None:
                sel.add(sel.coverage.importers(path) | {t for t in sel.all_units
                                                        if path in sel.closure(t)[0]},
                        f"{path} changed since the map and names the change")
            elif unit.references & names or any(n in summary.constants for n in hits):
                tests = sel.coverage.tests_of(path, qualname)
                if not tests and qualname not in sel.coverage.functions.get(path, {}):
                    tests = {t for t in sel.all_units if path in sel.closure(t)[0]}
                sel.add(tests, f"{path}:{qualname} changed since the map")


def finish(sel: Selection, changes: list[Change], paths: list[str], started: float) -> dict:
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
        commands.append(["uv", "run", "--frozen", "--group", "dev", "python", "-m",
                         "pytest", "-q", *pytest_files])
    return {"changed": paths, "selected": selected, "selected_count": len(selected),
            "full_count": len(sel.all_units), "full": full, "full_reasons": sel.full,
            "smoke": list(SMOKE), "reasons": {t: sorted(r) for t, r in sorted(sel.reasons.items())},
            "map": None if cov is None else {"commit": cov.commit, "path": str(cov.path or "")},
            "unmapped": sorted(sel.unmapped) if cov is not None else "all (static graph only)",
            "commands": commands, "lean_build": lean, "rust_build": sel.rust,
            "seconds": round(time.monotonic() - started, 2)}


def run(plan: dict) -> int:
    env = dict(os.environ)
    env.setdefault("UV_CACHE_DIR", "/tmp/ve-layers-uv-cache")
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    if plan["lean_build"]:
        env["VE_LEAN_PREBUILT"] = "1"
    for command in plan["commands"]:
        print("+", " ".join(command), flush=True)
        cwd = ROOT / "lean" if command[:2] == ["lake", "build"] else ROOT
        result = subprocess.run(command, cwd=cwd, env=env, check=False)
        if result.returncode:
            return result.returncode
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--base", help="merge base for a branch diff")
    source.add_argument("--commit", help="one historical commit")
    source.add_argument("--paths", nargs="+", help="explicit changed paths")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--map", help="coverage map (default: newest cached ancestor map)")
    parser.add_argument("--static", action="store_true", help="ignore the coverage map")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--explain", action="store_true", help="print why each test is selected")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    paths = args.paths if args.paths is not None else changed_paths(args.base, args.commit)
    if args.commit:
        base, after = f"{args.commit}^", args.commit
    elif args.base:
        base, after = git_lines("merge-base", args.base, "HEAD")[0], "HEAD"
    else:
        base, after = "HEAD", None
    coverage = None if args.static else (args.map or "auto")
    plan = select(paths, full=args.full, base=base, after=after, coverage=coverage)
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
    return run(plan) if args.run else 0


if __name__ == "__main__":
    raise SystemExit(main())
