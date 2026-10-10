"""Where a service mode lives: its Lean module, response schema, Python relays and tests.

    uv run python tools/repo_map.py routes          # one row per service mode
    uv run python tools/repo_map.py route <mode>    # that row in full, one file per line
    uv run python tools/repo_map.py file <path>     # the modes, layer, tests and generator of a file
    uv run python tools/repo_map.py --check         # exit 1 when a mode and its schema file disagree

Nothing here is typed in: every column is read from the repository's own data each run, so the map
cannot go stale. A column those sources cannot fill prints "unknown".

* Modes: `MODES` of `ve/backends/service_schema.py` (imported).
* Schema: `ve/backends/lean_service_schema/<mode>.json` when that file exists.
* Lean: `lean/statements.txt` (written by `tools/lean_statements.py` from the compiled environment).
  `VE.Service.runMode` in `lean/VE/Service/Protocol.lean` dispatches every mode, and the audited
  equation `VE.Service.runMode_<constructor>` states what it runs; the dump's `-- uses name@Module`
  line of that theorem names the implementing constants and their modules (the dispatch's own
  module dropped). A theorem names its mode through the constructor `VE.Service.Mode.<c>` it uses;
  the constructor matches the one mode equal to it once case, `-` and `.` are ignored. The modules
  map to files through `tools/source_graph.py`. `ve/assurance-manifest.json` bindings record a
  dispatch file for only some modes and `lean/declarations.txt` lists every constant but not which
  one a mode runs, so neither fills this column; `route` prints the manifest bindings beside it.
* Relays: the import graph of `tools/source_graph.py` (the one the test selector uses). The relay
  entries are the module-level functions whose first parameter is `mode` in the service client
  (`ve/backends/lean_service.py`), the files it imports and the files that import it; a relay of a
  mode is a file under `ve/` or `ve_experiments/` that calls such an entry, imported from its file,
  with the mode as a string literal (first argument or `mode=`), read with Python's own parser.
* Tests: the coverage map of `tools/test_map.py` (the newest cached ancestor map, or `$VE_TESTMAP`):
  the test files that ran a function holding a relay call. Without a map (or with `--static`), the
  test files whose static imports reach a relay file.
* `file`: the layer from `tools/layer_policy.py` (`source_layer`); the generator that owns a generated
  file from `tools/regen_generated.py --owner` when that tool exists and offers the option.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for _path in (str(ROOT), str(ROOT / "tools")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from ve.backends.service_schema import MODES  # noqa: E402
import layer_policy  # noqa: E402
import source_graph  # noqa: E402
import test_map  # noqa: E402

SCHEMA_DIRECTORY = "ve/backends/lean_service_schema"
STATEMENTS = "lean/statements.txt"
MANIFEST = "ve/assurance-manifest.json"
SERVICE_CLIENT = "ve/backends/lean_service.py"
REGEN = "tools/regen_generated.py"
DISPATCH = "VE.Service.runMode"      # lean/VE/Service/Protocol.lean
MODE_TYPE = "VE.Service.Mode"
PRODUCT = ("ve/", "ve_experiments/")
UNKNOWN = "unknown"
# Schema files in the directory that belong to no mode, and why (checked by --check).
SHARED_SCHEMAS = {
    "common.json": "definitions every mode's schema refers to (`common.json#/$defs/...`)",
    "envelope.json": "the response line and handshake around every mode's rows",
}


@dataclass
class Route:
    mode: str
    schema: str | None = None
    lean: list[tuple[str, str]] = field(default_factory=list)       # (file or module, constant)
    lean_source: str | None = None                                    # the theorem read
    bindings: list[tuple[str, list[str]]] = field(default_factory=list)  # (operation, dispatch files)
    relays: dict[str, set[str]] = field(default_factory=dict)        # file -> qualnames holding a call
    entries: set[str] = field(default_factory=set)                   # entry functions called
    tests: list[str] | None = None                                    # None: unknown


def _norm(name: str) -> str:
    return re.sub(r"[^0-9a-z]", "", name.lower())


# -- Lean ---------------------------------------------------------------------------------------
def statement_uses(text: str) -> dict[str, list[tuple[str, str]]]:
    """{theorem: [(constant, module)]} from the `-- uses` lines of a statements dump."""
    uses: dict[str, list[tuple[str, str]]] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("theorem "):
            current = line.split()[1]
        elif current and line.strip().startswith("-- uses "):
            pairs = []
            for item in line.strip().removeprefix("-- uses ").split():
                name, at, module = item.rpartition("@")
                if at:
                    pairs.append((name, module))
            uses[current] = pairs
    return uses


def lean_dispatch(root: Path, graph) -> dict[str, tuple[str, list[tuple[str, str]]]]:
    """{mode: (theorem, [(file or module, constant)])} from the dispatch equations."""
    path = root / STATEMENTS
    if not path.exists():
        return {}
    uses = statement_uses(path.read_text(encoding="utf-8"))
    by_norm: dict[str, list[str]] = {}
    for mode in MODES:
        by_norm.setdefault(_norm(mode), []).append(mode)
    found: dict[str, tuple[str, list[tuple[str, str]]]] = {}
    for theorem, pairs in uses.items():
        if not theorem.startswith(DISPATCH + "_"):
            continue
        modules = {name: module for name, module in pairs}
        if DISPATCH not in modules:
            continue
        home = modules[DISPATCH]  # the dispatch's own module: the mode type and its helpers
        constructors = [name.removeprefix(MODE_TYPE + ".") for name in modules
                        if name.startswith(MODE_TYPE + ".") and name.count(".") == MODE_TYPE.count(".") + 1]
        if len(constructors) != 1 or len(by_norm.get(_norm(constructors[0]), [])) != 1:
            continue
        [mode] = by_norm[_norm(constructors[0])]
        implementing = [(graph.lean_modules.get(module, module), name) for name, module in pairs
                        if module != home]
        if implementing and mode not in found:
            found[mode] = (theorem, implementing)
    return found


def manifest_bindings(root: Path) -> dict[str, list[tuple[str, list[str]]]]:
    path = root / MANIFEST
    if not path.exists():
        return {}
    found: dict[str, list[tuple[str, list[str]]]] = {}
    for operation in json.loads(path.read_text(encoding="utf-8")).get("operations", []):
        for binding in (operation.get("lean") or {}).get("bindings", []):
            if binding.get("executable") == "ve_service" and binding.get("mode") in MODES:
                found.setdefault(binding["mode"], []).append((operation["id"], list(binding.get("dispatch", []))))
    return found


# -- Python ---------------------------------------------------------------------------------------
def _parse(root: Path, path: str) -> ast.Module | None:
    try:
        return ast.parse((root / path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return None


def relay_entries(root: Path, graph) -> dict[str, set[str]]:
    """{file: names} of the module-level functions taking `mode` first, around the service client."""
    if SERVICE_CLIENT not in graph.summaries:
        return {}
    around = graph.importers(SERVICE_CLIENT) | graph.edges.get(SERVICE_CLIENT, set())
    entries: dict[str, set[str]] = {}
    for path in sorted(around):
        # Only a file whose text holds "mode" can define such a function; the rest are not parsed.
        if not path.startswith(PRODUCT) or "mode" not in (root / path).read_text(encoding="utf-8", errors="replace"):
            continue
        tree = _parse(root, path)
        for node in tree.body if tree else ():
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                arguments = node.args.posonlyargs + node.args.args
                if arguments and arguments[0].arg == "mode":
                    entries.setdefault(path, set()).add(node.name)
    return entries


def module_constants(tree: ast.Module) -> dict[str, str]:
    """Module-level names bound once to a string literal (`MODE = "english.read"`)."""
    bound: dict[str, list[object]] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                bound.setdefault(target.id, []).append(value.value if isinstance(value, ast.Constant) else None)
    return {name: values[0] for name, values in bound.items() if len(values) == 1 and isinstance(values[0], str)}


def _mode_literals(call: ast.Call, constants: dict[str, str]) -> list[str]:
    values = list(call.args[:1]) + [k.value for k in call.keywords if k.arg == "mode"]
    texts = [v.value if isinstance(v, ast.Constant) else constants.get(v.id) if isinstance(v, ast.Name) else None
             for v in values]
    return [text for text in texts if isinstance(text, str) and text in MODES]


def mode_calls(tree: ast.Module, constants: dict[str, str]) -> list[tuple[str, str, str, str | None, str]]:
    """(qualname, callee kind, callee name, base name, mode) for each call naming a mode. Qualnames are
    `co_qualname`'s, as the coverage map records them (comprehensions are inlined since Python 3.12)."""
    found = []
    stack: list[tuple[ast.AST, str]] = [(tree, "")]   # node, the qualname prefix of its scope
    while stack:
        node, prefix = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            outside = node.decorator_list + (node.bases if isinstance(node, ast.ClassDef) else
                                             node.args.defaults + [d for d in node.args.kw_defaults if d])
            stack.extend((item, prefix) for item in outside)
            inner = prefix + node.name + ("." if isinstance(node, ast.ClassDef) else ".<locals>.")
            stack.extend((item, inner) for item in node.body)
            continue
        if isinstance(node, (ast.Lambda, ast.GeneratorExp)):
            inner = prefix + ("<lambda>" if isinstance(node, ast.Lambda) else "<genexpr>") + ".<locals>."
            stack.extend((child, inner) for child in ast.iter_child_nodes(node))
            continue
        if isinstance(node, ast.Call):
            qualname = prefix.removesuffix(".").removesuffix(".<locals>") or "<module>"
            for mode in _mode_literals(node, constants):
                if isinstance(node.func, ast.Name):
                    found.append((qualname, "name", node.func.id, None, mode))
                elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    found.append((qualname, "attribute", node.func.attr, node.func.value.id, mode))
        stack.extend((child, prefix) for child in ast.iter_child_nodes(node))
    return found


def relay_sites(root: Path, graph) -> dict[str, list[tuple[str, str, str]]]:
    """{mode: [(file, qualname, entry)]} of the calls that relay each mode."""
    entries = relay_entries(root, graph)
    sites: dict[str, list[tuple[str, str, str]]] = {}
    for path in graph.files:
        summary = graph.summaries.get(path) if path.endswith(".py") and path.startswith(PRODUCT) else None
        # A file holds a mode in a call (or a constant) only if a mode is among its string literals.
        if summary is None or summary.constants.isdisjoint(MODES):
            continue
        tree = _parse(root, path)
        if tree is None:
            continue
        found = mode_calls(tree, module_constants(tree))
        if not found:
            continue
        # Local names bound by `from X import name [as alias]` and `import X as local`, resolved to files.
        names: dict[str, tuple[str, str]] = {}
        modules: dict[str, str] = {}
        for edge in graph.summaries[path].imports:
            target = graph.resolve(path, edge.module)
            if edge.names is None:
                if target:
                    modules[edge.local or edge.module.split(".")[0]] = target
                continue
            for name, alias in edge.names:
                submodule = graph.resolve(path, f"{edge.module}.{name}")
                if submodule:
                    modules[alias] = submodule
                elif target:
                    names[alias] = (target, name)
        own = entries.get(path, set())
        for qualname, kind, callee, base, mode in found:
            entry = None
            if kind == "name":
                if callee in own:
                    entry = f"{path}:{callee}"
                elif callee in names and names[callee][1] in entries.get(names[callee][0], ()):
                    entry = f"{names[callee][0]}:{names[callee][1]}"
            elif base in modules and callee in entries.get(modules[base], ()):
                entry = f"{modules[base]}:{callee}"
            if entry:
                sites.setdefault(mode, []).append((path, qualname, entry))
    return sites


# -- Tests --------------------------------------------------------------------------------------------
def coverage(root: Path, static: bool) -> tuple[dict | None, str]:
    """The coverage map and where it came from, or (None, why not)."""
    if static:
        return None, "static import graph (--static)"
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    try:
        path = test_map.find_map(head.stdout.strip() or "HEAD", root=root)
        if path is None:
            return None, "static import graph (no coverage map)"
        return test_map.load(path), f"coverage map {path}"
    except (OSError, ValueError, EOFError) as error:
        return None, f"static import graph (coverage map unreadable: {error})"


def test_units(graph) -> set[str]:
    return {path for path in graph.files if path.startswith("tests/test_") and path.endswith(".py")}


def tests_of(sites: list[tuple[str, str]], data: dict | None, graph) -> list[str] | None:
    """Test files that ran a function holding a site (map), else whose imports reach a site's file."""
    if not sites:
        return None
    if data is not None:
        indices = set()
        for path, qualname in sites:
            indices.update(data["functions"].get(path, {}).get(qualname, ()))
        return sorted(data["tests"][i] for i in indices)
    units = test_units(graph)
    reached = set()
    for path in {path for path, _ in sites}:
        reached |= graph.importers(path) & units
    return sorted(reached)


# -- The map ------------------------------------------------------------------------------------------
def build(root: Path = ROOT, static: bool = False) -> tuple[list[Route], str, dict | None]:
    """Every mode's row, where its tests came from, and the coverage map (None without one)."""
    graph = source_graph.load(root)
    dispatch = lean_dispatch(root, graph)
    bindings = manifest_bindings(root)
    sites = relay_sites(root, graph)
    data, tests_source = coverage(root, static)
    routes = []
    for mode in MODES:
        route = Route(mode)
        schema = f"{SCHEMA_DIRECTORY}/{mode}.json"
        route.schema = schema if (root / schema).is_file() else None
        if mode in dispatch:
            route.lean_source, route.lean = dispatch[mode]
        route.bindings = bindings.get(mode, [])
        for path, qualname, entry in sites.get(mode, []):
            route.relays.setdefault(path, set()).add(qualname)
            route.entries.add(entry)
        route.tests = tests_of([(p, q) for p, qs in route.relays.items() for q in qs], data, graph)
        routes.append(route)
    return routes, tests_source, data


def lean_files(route: Route) -> list[str]:
    return sorted({where for where, _ in route.lean})


def _cell(values: list[str] | None, limit: int | None = None) -> str:
    if not values:
        return UNKNOWN
    if limit is not None and len(values) > limit:
        return ", ".join(values[:limit]) + f", +{len(values) - limit} more"
    return ", ".join(values)


def print_routes(routes: list[Route], tests_source: str) -> None:
    print(f"# Service modes (tests: {tests_source})")
    print("mode | Lean module(s) | response schema | Python relays | tests")
    for route in routes:
        tests = None if route.tests is None else [f"{len(route.tests)} files"] + route.tests[:2]
        print(" | ".join([route.mode, _cell(lean_files(route)), route.schema or UNKNOWN,
                          _cell(sorted(route.relays)), _cell(tests)]))


def print_route(route: Route, tests_source: str) -> None:
    print(f"mode: {route.mode}")
    print(f"schema: {route.schema or UNKNOWN}")
    print(f"lean ({route.lean_source + ' in ' + STATEMENTS if route.lean_source else UNKNOWN}):")
    for where, constant in sorted(route.lean):
        print(f"  {where}  ({constant})")
    print(f"lean bindings ({MANIFEST}):" + ("" if route.bindings else " none"))
    for operation, files in route.bindings:
        print(f"  {operation}: {', '.join(files) or UNKNOWN}")
    print(f"python relays (calls to {', '.join(sorted(route.entries)) or UNKNOWN}):")
    for path, qualnames in sorted(route.relays.items()):
        print(f"  {path}  ({', '.join(sorted(qualnames))})")
    print(f"tests ({tests_source}):" + ("" if route.tests else f" {UNKNOWN if route.tests is None else 'none'}"))
    for test in route.tests or ():
        print(f"  {test}")


def owner(root: Path, path: str) -> str:
    tool = root / REGEN
    if not tool.is_file():
        return f"{UNKNOWN} ({REGEN} does not exist)"
    helped = subprocess.run([sys.executable, str(tool), "--help"], cwd=root, capture_output=True, text=True)
    if "--owner" not in helped.stdout:
        return f"{UNKNOWN} ({REGEN} has no --owner)"
    done = subprocess.run([sys.executable, str(tool), "--owner", path], cwd=root, capture_output=True, text=True)
    return done.stdout.strip() or f"none ({REGEN} --owner exit {done.returncode})"


def print_file(root: Path, path: str, routes: list[Route], data: dict | None, tests_source: str) -> None:
    path = Path(os.path.relpath(Path(path).resolve(), root)).as_posix() if Path(path).is_absolute() else path
    modes = [r.mode for r in routes
             if path == r.schema or path in lean_files(r) or path in r.relays or path in (r.tests or ())]
    layer = layer_policy.source_layer(path)
    print(f"file: {path}{'' if (root / path).exists() else ' (does not exist)'}")
    print(f"modes: {', '.join(modes) or 'none'}")
    print(f"layer: {UNKNOWN if layer is None else f'{layer} ({layer_policy.NAMES[layer]})'}")
    if path.startswith("tests/"):
        tests = [path]
    elif data is not None and path in data["functions"]:
        tests = sorted({data["tests"][i] for indices in data["functions"][path].values() for i in indices})
    elif data is None and path.endswith(".py"):
        graph = source_graph.load(root)
        tests = sorted(graph.importers(path) & test_units(graph))
    elif modes and not path.endswith(".py"):  # a mode's Lean module or schema: its route's tests
        tests = sorted({t for r in routes if r.mode in modes for t in r.tests or ()})
    else:
        tests = [data["tests"][i] for i in data["reads"].get(path, ())] if data else []
    print(f"tests ({tests_source}):" + ("" if tests else " none found"))
    for test in tests:
        print(f"  {test}")
    print(f"generator: {owner(root, path)}")


def check(root: Path) -> list[str]:
    """Problems: a mode without its schema file, a schema file without its mode."""
    directory = root / SCHEMA_DIRECTORY
    present = {p.name for p in directory.glob("*.json")} if directory.is_dir() else set()
    problems = [f"mode {mode!r} has no schema file {SCHEMA_DIRECTORY}/{mode}.json"
                for mode in MODES if f"{mode}.json" not in present]
    expected = {f"{mode}.json" for mode in MODES} | set(SHARED_SCHEMAS)
    problems += [f"schema file {SCHEMA_DIRECTORY}/{name} has no mode in MODES"
                 for name in sorted(present - expected)]
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="exit 1 when MODES and the schema files disagree")
    parser.add_argument("--root", type=Path, default=ROOT, help="the tree to read (default: this checkout); MODES always come from this checkout")
    parser.add_argument("--static", action="store_true", help="ignore the coverage map")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("routes", help="one row per service mode")
    one = commands.add_parser("route", help="one mode in full")
    one.add_argument("mode")
    named = commands.add_parser("file", help="the modes, layer, tests and generator of a file")
    named.add_argument("path")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.check:
        problems = check(root)
        for problem in problems:
            print(problem)
        if not problems:
            print(f"PASS: {len(MODES)} modes, each with its schema file; shared: {', '.join(sorted(SHARED_SCHEMAS))}")
        if not args.command:
            return 1 if problems else 0
        if problems:
            return 1
    if not args.command:
        parser.print_help()
        return 2
    if args.command == "route" and args.mode not in MODES:
        print(f"unknown mode {args.mode!r}; modes: {', '.join(MODES)}", file=sys.stderr)
        return 2
    routes, tests_source, data = build(root, args.static)
    if args.command == "routes":
        print_routes(routes, tests_source)
    elif args.command == "route":
        print_route(next(r for r in routes if r.mode == args.mode), tests_source)
    else:
        print_file(root, args.path, routes, data, tests_source)
    return 0


if __name__ == "__main__":
    sys.exit(main())
