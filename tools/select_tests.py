"""Select tests at the changed layer and every outer layer.

Run ``python3 tools/select_tests.py --base origin/main`` for a branch diff,
``--commit REV`` for a historical commit, or pass changed paths after ``--paths``.
``--impacted`` is the fast path: only the tests whose dependencies changed
(docs/TESTING.md).
Unknown inputs deliberately select the full suite. ``--run`` executes the
printed commands sequentially; it never starts a background process.
"""
from __future__ import annotations

import argparse
import ast
from functools import cache
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from check_lean_imports import imports as lean_imports
from pytest_run import pytest_command, pytest_environment
from layer_policy import (NAMES, ROOT, lean_default_targets, lean_executables, lean_layer,
                          python_exports, python_imports, python_layer, source_layer)

TESTS = sorted((ROOT / "tests").glob("test_*.py"))
# These exercise the public wire across languages, routes, and frozen fixtures.
ALWAYS = {
    "tests/test_conformance.py", "tests/test_lean_conformance.py",
    "tests/test_replay_conservativity.py", "tests/test_p0_three_way.py",
    "tests/test_difffuzz.py",
}
TEST_LAYER_OVERRIDES = {
    # Wall-clock deadlines and randomized histories are measurements.
    "tests/test_assist_deadline.py": 5,
    "tests/test_assist_recovery_replay.py": 5,
}
CHECKS = (
    ("uv", "run", "--frozen", "--group", "dev", "python", "tools/check_python_layers.py"),
    ("python3", "tools/check_lean_imports.py"),
    ("python3", "tools/check_rust_deps.py"),
    ("python3", "tools/test_layer_policy.py"),
)
# Cargo with path-independent flags, so the release binary matches lean/checkers.lock.
CARGO = ["python3", "tools/rust_build.py"]


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


EXPORTS = python_exports(ROOT)


@cache
def test_dependencies(path: Path) -> frozenset[str]:
    """Local test modules providing fixtures or helper functions."""
    tree = ast.parse(path.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.removeprefix("tests.").split(".")[0]
                         for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.removeprefix("tests.").split(".")[0])
    return frozenset(f"tests/{name}.py" for name in names
                     if name.startswith("test_") and (ROOT / "tests" / f"{name}.py").exists())


@cache
def test_layer(path: Path, seen: frozenset[Path] = frozenset()) -> int:
    """Classify by direct providers and transitively imported test helpers."""
    relative = path.relative_to(ROOT).as_posix()
    if relative in TEST_LAYER_OVERRIDES:
        return TEST_LAYER_OVERRIDES[relative]
    if path in seen:
        return 1
    seen = seen | {path}
    tree = ast.parse(path.read_text())
    layers = []
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
            if node.module == "ve":
                names += [EXPORTS.get(alias.name, f"ve.{alias.name}")
                          for alias in node.names]
        for name in names:
            if name == "experiments" or name.startswith("experiments.") or name.startswith("ve_experiments"):
                layers.append(5)
            elif name.startswith("ve."):
                layer = python_layer(name)
                if layer:
                    layers.append(layer)
    source = path.read_text()
    # These are non-import edges: tests invoke binaries or read generated data.
    if "usecases" in source or "experiments/" in source:
        layers.append(5)
    if "rust/target/" in source or "VE_W5_RUST_BIN" in source:
        layers.append(4)
    if "lean/.lake/" in source or any(name in source for name in lean_executables()):
        layers.append(4)
    if '"-m", "ve"' in source or "'-m', 've'" in source:
        layers.append(4)
    layers.extend(test_layer(ROOT / dependency, seen)
                  for dependency in test_dependencies(path))
    return max(layers, default=5)


@cache
def reverse_imports() -> dict[str, set[str]]:
    """Local source imports plus reviewed edges, indexed by imported module."""
    edges = set()
    for top in ("ve", "ve_experiments"):
        for source in (ROOT / top).rglob("*.py"):
            relative = source.relative_to(ROOT).with_suffix("")
            package = relative.name == "__init__"
            module = ".".join(relative.parts[:-1] if package else relative.parts)
            edges.update((module, imported) for imported in
                         python_imports(module, source.read_text(), EXPORTS,
                                        root=ROOT, package=package))
    for source in (ROOT / "lean").rglob("*.lean"):
        if ".lake" in source.parts:
            continue
        module = ".".join(source.relative_to(ROOT / "lean").with_suffix("").parts)
        edges.update((module, imported) for imported in lean_imports(source.read_text()))
    for ledger in ("layer-exceptions.json", "lean-layer-exceptions.json"):
        edges.update(tuple(edge.split(" -> ")) for edge in
                     json.loads((ROOT / "tools" / ledger).read_text()))
    reverse: dict[str, set[str]] = {}
    for importer, imported in edges:
        reverse.setdefault(imported, set()).add(importer)
    return reverse


def reverse_importers(path: str) -> set[str]:
    """Include all transitive consumers of a changed source module."""
    if not path.endswith((".py", ".lean")):
        return set()
    language = ("python" if path.startswith(("ve/", "ve_experiments/")) else
                "lean" if path.startswith("lean/") else None)
    if language is None:
        return set()
    module = ".".join(Path(path).with_suffix("").parts[(0 if language == "python" else 1):])
    if module.endswith(".__init__"):
        module = module.removesuffix(".__init__")
    reverse = reverse_imports()
    reached = {module}
    while True:
        targets = reached | ({imported for imported in reverse
                              if imported.startswith(module + ".")}
                             if path.endswith("/__init__.py") else set())
        added = {importer for imported in targets
                 for importer in reverse.get(imported, ())} - reached
        if not added:
            break
        reached.update(added)
    return reached - {module}


def native_commands(paths: list[str], selected: list[str], fallback: bool) -> tuple[list[list[str]], bool, bool]:
    """The checks, the native builds the selection needs, and the pytest run of `selected`."""
    selected_sources = [(ROOT / p).read_text() for p in selected]
    lean = (fallback or any(p.startswith("lean/") or p.startswith("conformance/") for p in paths)
            or not (ROOT / "lean/.lake/build/bin/ve_conformance").exists()
            or any(any(name in source for source in selected_sources)
                   and not (ROOT / "lean/.lake/build/bin" / name).exists()
                   for name in lean_executables()))
    rust = fallback or any(p.startswith("rust/") or p.startswith("conformance/") for p in paths)
    rust_release_binary = (rust or (any("rust/target/release/ve" in (ROOT / p).read_text()
                                       or "VE_W5_RUST_BIN" in (ROOT / p).read_text()
                                       for p in selected)
                                    and not (ROOT / "rust/target/release/ve").exists()))
    rust_debug_binary = (rust or (any("rust/target/debug/ve" in (ROOT / p).read_text()
                                     for p in selected)
                                  and not (ROOT / "rust/target/debug/ve").exists()))
    commands = [list(cmd) for cmd in CHECKS]
    if lean:
        commands.append(["lake", "build"])
        # Harness executables such as ve_risk_eval are outside defaultTargets.
        named = sorted(name for name in lean_executables()
                       if name not in lean_default_targets()
                       and any(name in source for source in selected_sources))
        if named:
            commands.append(["lake", "build", *named])
    commands.append(["python3", "lean/audit.py"])
    if rust:
        commands.append([*CARGO, "test", "--locked", "--all-features", "--manifest-path",
                         "rust/Cargo.toml", "--", "--test-threads=1"])
    if rust_release_binary:
        commands.append([*CARGO, "build", "--locked", "--release", "--manifest-path",
                         "rust/Cargo.toml", "-p", "ve"])
    if rust_debug_binary:
        commands.append([*CARGO, "build", "--locked", "--manifest-path",
                         "rust/Cargo.toml", "-p", "ve"])
    commands.append(pytest_command(["uv", "run", "--frozen", "--group", "dev", "python"], "-q", *selected))
    return commands, lean, rust


def select(paths: list[str], *, full: bool = False) -> dict:
    paths = sorted(set(path.removeprefix("./") for path in paths))
    layers = {path: source_layer(path) for path in paths}
    # A changed test always runs itself. Its imports determine which other tests
    # share its layer. Shared fixtures and unmapped paths instead start at 1.
    for path in paths:
        if path.startswith("tests/test_") and path.endswith(".py"):
            layers[path] = test_layer(ROOT / path) if (ROOT / path).exists() else 1
        for importer in reverse_importers(path):
            layer = python_layer(importer) if not path.startswith("lean/") else lean_layer(importer)
            if layer is not None:
                layers[path] = min(layers[path], layer)
    fallback = full or not paths or None in layers.values()
    minimum = 1 if fallback else min(layers.values())
    classified = {path.relative_to(ROOT).as_posix(): test_layer(path) for path in TESTS}
    changed_tests = {path for path in paths if path.startswith("tests/test_") and path.endswith(".py")}
    dependent_tests = set(changed_tests)
    while True:
        added = {path for path in classified
                 if test_dependencies(ROOT / path) & dependent_tests} - dependent_tests
        if not added:
            break
        dependent_tests.update(added)
    selected = sorted(path for path, layer in classified.items()
                      if layer >= minimum or path in ALWAYS or path in dependent_tests)
    commands, lean, rust = native_commands(paths, selected, fallback)
    return {"changed": paths, "path_layers": layers, "minimum_layer": minimum,
            "layer_name": NAMES[minimum], "selected": selected,
            "selected_count": len(selected), "full_count": len(TESTS),
            "always": sorted(ALWAYS), "commands": commands,
            "lean_build": lean, "rust_build": rust}


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
def lean_executables_of(module: str) -> frozenset[str]:
    """The Lean executables whose import closure holds `module`."""
    forward: dict[str, set[str]] = {}
    for imported, importers in reverse_imports().items():
        for importer in importers:
            forward.setdefault(importer, set()).add(imported)
    found = set()
    for name, root in lean_executables().items():
        seen, todo = set(), [root]
        while todo:
            current = todo.pop()
            if current not in seen:
                seen.add(current)
                todo.extend(forward.get(current, ()))
        if module in seen:
            found.add(name)
    return frozenset(found)


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


def run(plan: dict) -> int:
    env = pytest_environment(os.environ)
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
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--base", help="merge base for a branch diff")
    source.add_argument("--commit", help="one historical commit")
    source.add_argument("--paths", nargs="+", help="explicit changed paths")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--impacted", action="store_true",
                        help="the fast path: only the tests whose dependencies changed")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    paths = args.paths if args.paths is not None else changed_paths(args.base, args.commit)
    plan = (impacted if args.impacted else select)(paths, full=args.full)
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        if args.impacted:
            print(f"impacted{' (full fallback)' if plan['fallback'] else ''}: "
                  f"{plan['selected_count']}/{plan['full_count']} Python test files")
            for path in plan["unreached"]:
                print(f"no test reaches {path}: full suite")
            for path in plan["scripts_without_tests"]:
                print(f"warning: no test reaches {path}")
        else:
            print(f"{plan['layer_name']} ({plan['minimum_layer']}): "
                  f"{plan['selected_count']}/{plan['full_count']} Python test files")
        print("changed:", ", ".join(paths) or "(none; full fallback)")
        for command in plan["commands"]:
            print("+", " ".join(command))
    return run(plan) if args.run else 0


if __name__ == "__main__":
    raise SystemExit(main())
