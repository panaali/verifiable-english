"""Check workspace crate dependencies against the inward-only rule.

Inside a crate listed in MODULE_GROUPS, every `src/*.rs` module is also
assigned a group (1 kernel, 2 profile, 3 surface) and its `crate::` and
`super::` paths, in `use` trees and inline (generic arguments such as
`parse::<u8>()` end a path), must point inward unless the exact edge is in
MODULE_LEDGER, which rejects stale keys as the other ledgers do. A path resolves
through re-exports to every module it may name: the crate root's imports
(`pub use eval::evaluate`, `pub use crate::surface::parse`, a private `use`,
which child modules see too, a module alias or a glob) and other modules'
`pub use` items, chained. Where resolution is ambiguous it fails closed (adds
edges). `#[path]`, `#[macro_use]`, `#[macro_export]`, `include!` and
`extern crate self` are rejected because they move code or names past this
resolution. `lib.rs` is the crate's declaring and re-exporting facade (like
`ve/__init__.py`), so it is not checked as an importer; its own items
(`Error`, `Result`, `MAX_*`, `error`) are kernel.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tomllib
from typing import NamedTuple

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
IDENT = re.compile(r"(?:r#)?([A-Za-z_][A-Za-z0-9_]*)|(\*)")
# Constructs that move code or names past path resolution; the check fails closed on them.
UNSUPPORTED = re.compile(r"#!?\[\s*(?:path|macro_use|macro_export)\b|\binclude\s*!|\bextern\s+crate\s+self\b")
INLINE_MOD = re.compile(r"\bmod\s+(?:r#)?([A-Za-z_][A-Za-z0-9_]*)\s*\{")


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
    """The paths of the use tree (or plain path) at text[start:], each with its `as` alias.

    A path ends at its last identifier, so generic arguments (`parse::<u8>()`)
    and an empty group (`surface::{}`) keep the prefix before them.
    """
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
                if text.startswith("}", position) or position >= len(text):
                    position += 1
                    return found
                found.extend(tree())
                skip()
                if text.startswith(",", position):
                    position += 1
                elif not text.startswith("}", position):
                    position += 1
        match = IDENT.match(text, position)
        if match is None:
            return []
        name = match[1] or match[2]
        position = match.end()
        skip()
        if text.startswith("::", position):
            position += 2
            return [([name, *path], alias) for path, alias in tree()] or [([name], None)]
        alias = None
        if re.match(r"as\s", text[position:position + 3]):
            position += 2
            skip()
            rename = IDENT.match(text, position)
            if rename is not None:
                alias, position = rename[1] or rename[2], rename.end()
        return [([name], alias)]

    return tree()


def inline_spans(code: str) -> list[tuple[int, int]]:
    """The extent of every inline `mod name { ... }` block in comment-free code."""
    spans = []
    for match in INLINE_MOD.finditer(code):
        depth, end = 0, len(code)
        for position in range(match.end() - 1, len(code)):
            depth += {"{": 1, "}": -1}.get(code[position], 0)
            if depth == 0:
                end = position
                break
        spans.append((match.start(), end))
    return spans


def anchor(keyword: str, path: list[str], module: str, depth: int) -> list[str]:
    """A path written after `crate::` or `super::` at an inline-module depth, made crate-relative.

    Each `super` leaves one enclosing inline `mod`; leaving the file's top level
    reaches the crate root. A path that stays inside the file becomes
    `[module, ...]`, whose inline module names `member` skips.
    """
    if keyword == "crate" or module == "lib":
        return path
    ups = 1
    while path and path[0] == "super":
        path, ups = path[1:], ups + 1
    return path if ups > depth else [module, *path]


def crate_paths(text: str, module: str) -> list[list[str]]:
    """Every path written `crate::...` or `super::...`, in `use` trees and inline, crate-relative."""
    code = NOISE.sub(" ", text)
    spans = inline_spans(code)
    found = []
    for match in re.finditer(r"(?<![A-Za-z0-9_:])(crate|super)\s*::", code):
        depth = sum(start < match.start() < end for start, end in spans)
        found += [anchor(match[1], path, module, depth) for path, _ in use_paths(code, match.end())]
    return found


class Scope(NamedTuple):
    names: dict[str, list[list[str]]]  # name (or `*` for a glob) -> crate-relative paths it may stand for
    inline: set[str]  # inline `mod name { ... }` blocks, whose imports count as the file's own


def scope(module: str, text: str) -> Scope:
    """The names one file makes nameable from elsewhere in the crate.

    The crate root's private `use` items are visible to every module, so all of
    its imports count; another module counts its `pub use` items. Each `use`
    path is read both relative to the crate root and to the module (fail closed:
    an extern crate path then only resolves to the kernel root).
    """
    code = NOISE.sub(" ", text)
    spans = inline_spans(code)
    root = module == "lib"
    pattern = r"(?<![A-Za-z0-9_])use\s+" if root else r"\bpub(?:\s*\([^)]*\))?\s+use\s+"
    names: dict[str, list[list[str]]] = {}
    for match in re.finditer(pattern, code):
        for path, alias in use_paths(code, match.end()):
            if path[-1] == "self" and len(path) > 1:
                path = path[:-1]
            name = alias or path[-1]
            if name == "_":
                continue
            if name == "*":
                path = path[:-1]
            if not path:
                continue
            if path[0] in {"crate", "super"}:
                depth = sum(start < match.start() < end for start, end in spans)
                candidates = [anchor(path[0], path[1:], module, depth)]
            elif path[0] == "self":
                candidates = [path[1:] if root else [module, *path[1:]]]
            else:
                candidates = [path] if root else [path, [module, *path]]
            names.setdefault(name, []).extend(candidate for candidate in candidates if candidate)
    return Scope(names, set(INLINE_MOD.findall(code)))


def resolve(path: list[str], scopes: dict[str, Scope], seen: frozenset = frozenset()) -> set[str]:
    """The crate modules a crate-relative path may depend on."""
    if not path or path[0] in {"self", "super"}:
        return set()
    head = path[0]
    if head == "*":
        return set(scopes)
    if head in scopes and head != "lib":
        return {head} | member(head, path[1:], scopes, seen)
    return {"lib"} | member("lib", path, scopes, seen)


def member(module: str, path: list[str], scopes: dict[str, Scope], seen: frozenset) -> set[str]:
    """The modules `module::path` may resolve through, following its imports."""
    names = scopes[module].names
    while path and path[0] in scopes[module].inline:
        path = path[1:]
    if not path or (module, path[0]) in seen:
        return set()
    seen = seen | {(module, path[0])}
    if path[0] == "*":
        targets = [target for found in names.values() for target in found]
    else:
        targets = ([[*target, *path[1:]] for target in names.get(path[0], [])]
                   + [[*glob, *path] for glob in names.get("*", [])])
    found = set()
    for target in targets:
        found |= resolve(target, scopes, seen)
    return found


def module_edges(crate: str, source: Path, groups: dict[str, int]) -> tuple[set[str], list[str]]:
    """Outward intra-crate edges of one crate, and its unmapped or unsupported modules."""
    files = {path.stem: path for path in sorted(source.glob("*.rs"))}
    texts = {name: path.read_text() for name, path in files.items()}
    errors = sorted({*(f"unmapped Rust module: {crate}: {name}" for name in files if name not in groups),
                     *(f"unmapped Rust module: {crate}: {path.relative_to(source).as_posix()}"
                       for path in source.rglob("*.rs") if path.parent != source)})
    errors += [f"unsupported Rust construct: {crate}: {name}: {found[0]!r}"
               for name, text in texts.items()
               for found in [UNSUPPORTED.search(NOISE.sub(" ", text))] if found]
    scopes = {name: scope(name, text) for name, text in texts.items()}
    scopes.setdefault("lib", Scope({}, set()))
    edges = set()
    for importer, text in texts.items():
        if importer == "lib" or importer not in groups:
            continue
        for segments in crate_paths(text, importer):
            for target in resolve(segments, scopes):
                if target in groups and groups[importer] < groups[target]:
                    edges.add(f"{crate}: {importer} -> {target}")
    return edges, errors


def module_errors() -> list[str]:
    workspace = tomllib.loads((WORKSPACE / "Cargo.toml").read_text())
    members = {tomllib.loads((WORKSPACE / member / "Cargo.toml").read_text())["package"]["name"]: member
               for member in workspace["workspace"]["members"]}
    edges, errors = set(), []
    for crate, groups in MODULE_GROUPS.items():
        if crate in members:
            found, problems = module_edges(crate, WORKSPACE / members[crate] / "src", groups)
            edges |= found
            errors += problems
    expected = json.loads(MODULE_LEDGER.read_text())
    return [*errors,
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
