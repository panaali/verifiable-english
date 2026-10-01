"""Select tests at the changed layer and every outer layer.

Run ``python3 tools/select_tests.py --base origin/main`` for a branch diff,
``--commit REV`` for a historical commit, or pass changed paths after ``--paths``.
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
import subprocess
import sys

from check_lean_imports import imports as lean_imports
from layer_policy import (NAMES, ROOT, lean_default_targets, lean_executables, lean_layer,
                          python_exports, python_imports, python_layer, source_layer)

TESTS = sorted((ROOT / "tests").glob("test_*.py"))
# These exercise the public wire across languages, routes, and frozen fixtures.
ALWAYS = {
    "tests/test_conformance.py", "tests/test_lean_conformance.py",
    "tests/test_replay_conservativity.py", "tests/test_p0_three_way.py",
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
        commands.append(["cargo", "test", "--locked", "--all-features", "--manifest-path",
                         "rust/Cargo.toml", "--", "--test-threads=1"])
    if rust_release_binary:
        commands.append(["cargo", "build", "--locked", "--release", "--manifest-path",
                         "rust/Cargo.toml", "-p", "ve"])
    if rust_debug_binary:
        commands.append(["cargo", "build", "--locked", "--manifest-path",
                         "rust/Cargo.toml", "-p", "ve"])
    commands.append(["uv", "run", "--frozen", "--group", "dev", "python", "-m",
                     "pytest", "-q", *selected])
    return {"changed": paths, "path_layers": layers, "minimum_layer": minimum,
            "layer_name": NAMES[minimum], "selected": selected,
            "selected_count": len(selected), "full_count": len(TESTS),
            "always": sorted(ALWAYS), "commands": commands,
            "lean_build": lean, "rust_build": rust}


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
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--base", help="merge base for a branch diff")
    source.add_argument("--commit", help="one historical commit")
    source.add_argument("--paths", nargs="+", help="explicit changed paths")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    paths = args.paths if args.paths is not None else changed_paths(args.base, args.commit)
    plan = select(paths, full=args.full)
    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(f"{plan['layer_name']} ({plan['minimum_layer']}): "
              f"{plan['selected_count']}/{plan['full_count']} Python test files")
        print("changed:", ", ".join(paths) or "(none; full fallback)")
        for command in plan["commands"]:
            print("+", " ".join(command))
    return run(plan) if args.run else 0


if __name__ == "__main__":
    raise SystemExit(main())
