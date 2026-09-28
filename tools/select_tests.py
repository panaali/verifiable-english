"""Select tests at the changed layer and every outer layer.

Run ``python3 tools/select_tests.py --base origin/main`` for a branch diff,
``--commit REV`` for a historical commit, or pass changed paths after ``--paths``.
Unknown inputs deliberately select the full suite. ``--run`` executes the
printed commands sequentially; it never starts a background process.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import sys

from layer_policy import NAMES, ROOT, python_layer, source_layer

TESTS = sorted((ROOT / "tests").glob("test_*.py"))
# These exercise the public wire across languages, routes, and frozen fixtures.
ALWAYS = {
    "tests/test_conformance.py", "tests/test_lean_conformance.py",
    "tests/test_replay_conservativity.py", "tests/test_p0_three_way.py",
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
        return git_lines("diff-tree", "--no-commit-id", "--name-only", "-r",
                         f"{commit}^", commit)
    if base:
        return git_lines("diff", "--name-only", f"{base}...HEAD")
    return sorted(set(git_lines("diff", "--name-only", "HEAD") +
                      git_lines("ls-files", "--others", "--exclude-standard")))


def exports() -> dict[str, str]:
    tree = ast.parse((ROOT / "ve/__init__.py").read_text())
    result = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
            for alias in node.names:
                result[alias.asname or alias.name] = f"ve.{node.module}"
    return result


EXPORTS = exports()


def test_layer(path: Path) -> int:
    """Classify by imported provider; the highest direct provider owns the test."""
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
            if name.startswith("ve_experiments"):
                layers.append(5)
            elif name.startswith("ve."):
                layer = python_layer(name)
                if layer:
                    layers.append(layer)
    source = path.read_text()
    # These are non-import edges: tests invoke binaries or read generated data.
    if "usecases/" in source or "experiments/" in source:
        layers.append(5)
    if "rust/target/" in source or "VE_W5_RUST_BIN" in source:
        layers.append(4)
    if "lean/.lake/" in source or "ve_conformance" in source:
        layers.append(4)
    return max(layers, default=5)


def select(paths: list[str], *, full: bool = False) -> dict:
    paths = sorted(set(path.removeprefix("./") for path in paths))
    layers = {path: source_layer(path) for path in paths}
    # A changed test always runs itself. Its imports determine which other tests
    # share its layer. Shared fixtures and unmapped paths instead start at 1.
    for path in paths:
        if path.startswith("tests/test_") and path.endswith(".py"):
            layers[path] = test_layer(ROOT / path) if (ROOT / path).exists() else 1
    fallback = full or not paths or None in layers.values()
    minimum = 1 if fallback else min(layers.values())
    classified = {path.relative_to(ROOT).as_posix(): test_layer(path) for path in TESTS}
    selected = sorted(path for path, layer in classified.items()
                      if layer >= minimum or path in ALWAYS or path in paths)
    lean = (fallback or any(p.startswith("lean/") or p.startswith("conformance/") for p in paths)
            or not (ROOT / "lean/.lake/build/bin/ve_conformance").exists())
    rust = fallback or any(p.startswith("rust/") or p.startswith("conformance/") for p in paths)
    rust_binary = (rust or (any("rust/target/" in (ROOT / p).read_text()
                               or "VE_W5_RUST_BIN" in (ROOT / p).read_text()
                               for p in selected)
                            and not (ROOT / "rust/target/release/ve").exists()))
    commands = [list(cmd) for cmd in CHECKS]
    if lean:
        commands.append(["lake", "build"])
    commands.append(["python3", "lean/audit.py"])
    if rust:
        commands.append(["cargo", "test", "--locked", "--all-features", "--manifest-path",
                         "rust/Cargo.toml", "--", "--test-threads=1"])
    if rust_binary:
        commands.append(["cargo", "build", "--locked", "--release", "--manifest-path",
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
