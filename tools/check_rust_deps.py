"""Check workspace crate dependencies against the inward-only rule.

Inside a crate listed in MODULE_GROUPS, every `src/*.rs` module is also
assigned a group (1 kernel, 2 profile, 3 surface) and its `crate::` and
`super::` paths, in `use` trees and inline, must point inward unless the exact
edge is in MODULE_LEDGER, which rejects stale keys as the other ledgers do. A name the crate root re-exports (`pub use eval::evaluate`)
resolves to the module defining it. `lib.rs` is the crate's declaring and
re-exporting facade (like `ve/__init__.py`), so it is not checked as an
importer; its own items (`Error`, `Result`, `MAX_*`, `error`) are kernel.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tomllib

from layer_policy import ROOT

WORKSPACE = ROOT / "rust"
CRATE_LAYERS = {"ve-core": 1, "ve": 4}
MODULE_LEDGER = ROOT / "tools/rust-module-exceptions.json"
MODULE_GROUPS = {"ve-core": {
    **dict.fromkeys(("lib", "ast", "environment", "model", "wire", "semantics", "graph"), 1),
    **dict.fromkeys(("eval", "route", "search", "order", "units", "risk", "readings", "discourse"), 2),
    "surface": 3,
}}
# Comments, string and character literals: no `crate::` inside them is a path.
NOISE = re.compile(r'//[^\n]*|/\*.*?\*/|r(#*)".*?"\1|b?"(?:\\.|[^"\\])*"|b?\'(?:\\.|[^\'\\])\'', re.S)
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\*")


def dependencies(table: dict) -> list[tuple[str, object]]:
    result = []
    for name in ("dependencies", "dev-dependencies", "build-dependencies"):
        result.extend(table.get(name, {}).items())
    for target in table.get("target", {}).values():
        result.extend(dependencies(target))
    return result


def crate_errors() -> list[str]:
    workspace = tomllib.loads((WORKSPACE / "Cargo.toml").read_text())
    members = workspace["workspace"]["members"]
    names = {}
    manifests = {}
    for member in members:
        path = WORKSPACE / member / "Cargo.toml"
        data = tomllib.loads(path.read_text())
        name = data["package"]["name"]
        names[name] = member
        manifests[name] = data
    errors = []
    if set(names) != set(CRATE_LAYERS):
        errors.append(f"unmapped crates: {sorted(set(names) ^ set(CRATE_LAYERS))}")
    member_paths = {(WORKSPACE / member).resolve(): crate for crate, member in names.items()}
    workspace_deps = dict(dependencies(workspace.get("workspace", {})))
    for name, manifest in manifests.items():
        for alias, raw_spec in dependencies(manifest):
            spec = raw_spec if isinstance(raw_spec, dict) else {}
            if spec.get("workspace"):
                inherited = workspace_deps.get(alias)
                if inherited is None:
                    errors.append(f"missing workspace dependency: {name} -> {alias}")
                    continue
                spec = {**(inherited if isinstance(inherited, dict) else {}), **spec}
            dependency = spec.get("package", alias)
            if "path" in spec:
                base = WORKSPACE if raw_spec is not spec and isinstance(raw_spec, dict) and raw_spec.get("workspace") else WORKSPACE / names[name]
                target = (base / spec["path"]).resolve()
                if target not in member_paths:
                    errors.append(f"unmapped path dependency: {name} -> {alias}")
                elif member_paths[target] != dependency:
                    errors.append(f"mismatched path dependency: {name} -> {alias}")
                else:
                    dependency = member_paths[target]
            if dependency in names and CRATE_LAYERS.get(name, 0) < CRATE_LAYERS.get(dependency, 6):
                errors.append(f"outward crate dependency: {name} -> {dependency}")
    return errors


def use_paths(text: str, start: int) -> list[tuple[list[str], str | None]]:
    """The paths of the use tree (or plain path) at text[start:], each with its `as` alias."""
    position = start

    def skip() -> None:
        nonlocal position
        while position < len(text) and text[position].isspace():
            position += 1

    def tree() -> list[tuple[list[str], str | None]]:
        nonlocal position
        skip()
        if text.startswith("{", position):
            position += 1
            found = []
            while True:
                skip()
                if text.startswith("}", position):
                    position += 1
                    return found
                found.extend(tree())
                skip()
                if text.startswith(",", position):
                    position += 1
        match = IDENT.match(text, position)
        if match is None:
            return []
        position = match.end()
        skip()
        if text.startswith("::", position):
            position += 2
            return [([match[0], *path], alias) for path, alias in tree()]
        alias = None
        if re.match(r"as\s", text[position:position + 3]):
            position += 2
            skip()
            rename = IDENT.match(text, position)
            if rename is not None:
                alias, position = rename[0], rename.end()
        return [([match[0]], alias)]

    return tree()


def crate_paths(text: str) -> list[list[str]]:
    """Every path written `crate::...` or `super::...`, in `use` trees and inline.

    In a top-level module `super` is the crate root; inside a nested `mod` it is
    the file's own module, which can only add edges (fail closed).
    """
    code = NOISE.sub(" ", text)
    return [path for match in re.finditer(r"(?<![A-Za-z0-9_:])(?:crate|super)\s*::", code)
            for path, _ in use_paths(code, match.end())]


def root_exports(lib: str) -> dict[str, str]:
    """Names the crate root re-exports, mapped to the module that defines them."""
    code = NOISE.sub(" ", lib)
    exports = {}
    for match in re.finditer(r"\bpub(?:\s*\([^)]*\))?\s+use\s+", code):
        for path, alias in use_paths(code, match.end()):
            if len(path) > 1:
                exports[alias or path[-1]] = path[0]
    return exports


def module_edges(crate: str, source: Path, groups: dict[str, int]) -> tuple[set[str], list[str]]:
    """Outward intra-crate edges of one crate, and its unmapped modules."""
    files = {path.stem: path for path in sorted(source.glob("*.rs"))}
    unmapped = sorted({*(f"{crate}: {name}" for name in files if name not in groups),
                       *(f"{crate}: {path.relative_to(source).as_posix()}" for path in source.rglob("*.rs")
                         if path.parent != source)})
    exports = root_exports(files["lib"].read_text()) if "lib" in files else {}
    edges = set()
    for importer, path in files.items():
        if importer == "lib" or importer not in groups:
            continue
        for segments in crate_paths(path.read_text()):
            head = segments[0]
            if head in {"*", "self", "super"}:
                continue
            target = head if head in files else exports.get(head, "lib")
            if target in groups and groups[importer] < groups[target]:
                edges.add(f"{crate}: {importer} -> {target}")
    return edges, unmapped


def module_errors() -> list[str]:
    workspace = tomllib.loads((WORKSPACE / "Cargo.toml").read_text())
    members = {tomllib.loads((WORKSPACE / member / "Cargo.toml").read_text())["package"]["name"]: member
               for member in workspace["workspace"]["members"]}
    edges, unmapped = set(), []
    for crate, groups in MODULE_GROUPS.items():
        if crate in members:
            found, missing = module_edges(crate, WORKSPACE / members[crate] / "src", groups)
            edges |= found
            unmapped += missing
    expected = json.loads(MODULE_LEDGER.read_text())
    return [*(f"unmapped Rust module: {name}" for name in unmapped),
            *(f"new outward Rust module import: {edge}" for edge in sorted(edges - expected.keys())),
            *(f"stale Rust module exception: {edge}" for edge in sorted(expected.keys() - edges))]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crates-only", action="store_true",
                        help="check the crate graph only (the pre-commit hook's snapshot has manifests, "
                             "not Rust sources)")
    args = parser.parse_args(argv or [])
    errors = crate_errors() + ([] if args.crates_only else module_errors())
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    message = f"Rust crate graph kept ({len(CRATE_LAYERS)} crates)"
    if not args.crates_only:
        message += f"; module graph kept ({len(json.loads(MODULE_LEDGER.read_text()))} reviewed legacy edges)"
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
