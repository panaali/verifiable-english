"""Check workspace crate dependencies against the inward-only rule.

Inside a crate listed in MODULE_GROUPS, every `src/*.rs` module is also
assigned a group (1 kernel, 2 profile, 3 surface) and every path it writes, in
`use` trees and inline (generic arguments such as `parse::<u8>()` end a path),
must point inward unless the exact edge is in MODULE_LEDGER, which rejects
stale keys as the other ledgers do. The source is tokenized as rustc reads it
(nested block comments, raw strings, Unicode identifiers compared after NFC,
raw identifiers). A path resolves in the scope it is written in: `crate::`,
`super::` and `self::` paths, and paths through any name a `use` item binds
(`use crate as root`, `use super::{self as up}`, chained aliases), and the
strings of any attribute but a builtin one, which a proc macro may expand
into a path (`#[serde(with = "crate::surface::f")]`). Every
module's `use` items are re-exports others may name: the crate root's (and,
from inside, a module's own) private ones and every module's `pub` ones,
including module aliases and globs, at any inline-module depth, chained. Where
resolution is ambiguous it fails closed (adds edges). `#[path]`,
`#[macro_use]`, `#[macro_export]` (also under `cfg_attr`), `include!` (also
renamed), `extern crate self`, a macro metavariable after `::` and characters
rustc rejects outside literals are refused, because they move code or names
past this resolution. `lib.rs` is the crate's declaring and re-exporting
facade (like `ve/__init__.py`): its `use` items count where they are named,
and its own items (`Error`, `Result`, `MAX_*`, `error`) and the paths inside
them are kernel.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tomllib
from typing import NamedTuple
import unicodedata

from layer_policy import ROOT

WORKSPACE = ROOT / "rust"
CRATE_LAYERS = {"ve-core": 1, "ve": 4}
MODULE_LEDGER = ROOT / "tools/rust-module-exceptions.json"
MODULE_GROUPS = {"ve-core": {
    **dict.fromkeys(("lib", "ast", "environment", "model", "wire", "semantics", "graph"), 1),
    **dict.fromkeys(("eval", "route", "search", "order", "units", "risk", "readings", "discourse"), 2),
    "surface": 3,
}}
# What rustc skips between tokens (Pattern_White_Space, line comments), string literals
# (kept as tokens: a proc-macro attribute may expand one into a path), and the other
# literals, lifetimes and numbers. A raw string ends at a quote with as many `#`.
SKIPPED = re.compile(r"""
    [\t\n\x0b\x0c\r\x20\x85‎‏  ]+
  | //[^\n]*
  | [bc]?r(?P<hashes>\#*)"
  | [bc]?"(?P<string>(?:\\.|[^"\\])*)"
  | b?'(?:\\(?:u\{[^}']*\}|x[0-9A-Fa-f]{2}|.)|[^'\\\n\r\t])'
  | '(?:r\#)?[^\W\d]\w*
  | \d\w*
""", re.S | re.X)
BLOCK = re.compile(r"/\*|\*/")
# Attributes that load another file as a module or move macro names past path resolution.
MOVING_ATTRIBUTES = {"path", "macro_use", "macro_export"}
# Strict and reserved keywords other than the path keywords: never the head of a path.
KEYWORDS = set("""as async await become box break const continue do dyn else enum extern false final fn for
gen if impl in let loop macro match mod move mut override priv pub ref return static struct trait true try
type typeof unsafe unsized use virtual where while yield""".split())
# Builtin attributes whose arguments are lints, configuration predicates, layouts or text.
BUILTIN_ATTRIBUTES = {"allow", "warn", "deny", "forbid", "expect", "cfg", "doc", "repr", "inline", "must_use",
                      "deprecated", "test", "ignore", "should_panic", "non_exhaustive", "cold", "track_caller"}


class Token(NamedTuple):
    kind: str  # "ident" (NFC, without `r#`), "::", "punct", "string" (contents), or "invalid" (rejected by rustc)
    text: str
    raw: bool = False


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


def identifier(text: str, position: int) -> tuple[str, bool, int] | None:
    """The identifier at text[position:] (`_` or XID_Start, then XID_Continue), its rawness and end."""
    starts = [(position + 2, True), (position, False)] if text.startswith("r#", position) else [(position, False)]
    for start, raw in starts:
        if start < len(text) and (text[start] == "_" or text[start].isidentifier()):
            end = start + 1
            while end < len(text) and ("_" + text[end]).isidentifier():
                end += 1
            return unicodedata.normalize("NFC", text[start:end]), raw, end
    return None


def tokens(text: str) -> list[Token]:
    """The tokens rustc reads that a path can consist of or end at, and string literals."""
    found: list[Token] = []
    position = 0
    while position < len(text):
        if text.startswith("/*", position):  # block comments nest
            depth, end = 0, len(text)
            for mark in BLOCK.finditer(text, position):
                depth += 1 if mark[0] == "/*" else -1
                if depth == 0:
                    end = mark.end()
                    break
            position = end
            continue
        match = SKIPPED.match(text, position)
        if match is not None:
            position = match.end()
            if match["string"] is not None:
                found.append(Token("string", match["string"]))
            elif match["hashes"] is not None:
                close = text.find('"' + match["hashes"], position)
                end = len(text) if close < 0 else close
                found.append(Token("string", text[position:end]))
                position = min(len(text), end + 1 + len(match["hashes"]))
            continue
        name = identifier(text, position)
        if name is not None:
            found.append(Token("ident", name[0], name[1]))
            position = name[2]
        elif text.startswith("::", position):
            found.append(Token("::", "::"))
            position += 2
        else:
            character = text[position]
            found.append(Token("punct" if character.isascii() else "invalid", character))
            position += 1
    return found


def at(stream: list[Token], position: int, text: str) -> bool:
    """Whether stream[position] is the punctuation (or `::`) `text`."""
    return 0 <= position < len(stream) and stream[position].kind in {"punct", "::"} and stream[position].text == text


def keyword(stream: list[Token], position: int, word: str) -> bool:
    return (0 <= position < len(stream) and stream[position].kind == "ident" and not stream[position].raw
            and stream[position].text == word)


def keyword_at(stream: list[Token], position: int) -> bool:
    return stream[position].kind == "ident" and not stream[position].raw and stream[position].text in KEYWORDS


def use_tree(stream: list[Token], position: int) -> tuple[list[tuple[list[str], str | None]], int]:
    """The paths of the use tree (or plain path) at stream[position:], each with its `as` alias, and its end.

    A path ends at its last identifier, so generic arguments (`parse::<u8>()`)
    and an empty group (`surface::{}`) keep the prefix before them. A leading
    `::` (an extern crate path) becomes the segment `::`.
    """
    if at(stream, position, "::"):
        found, end = use_tree(stream, position + 1)
        return [(["::", *path], alias) for path, alias in found], end
    if at(stream, position, "{"):
        found, position = [], position + 1
        while position < len(stream) and not at(stream, position, "}"):
            inner, end = use_tree(stream, position)
            found += inner
            position = end if end > position else position + 1
            if at(stream, position, ","):
                position += 1
        return found, position + 1
    if at(stream, position, "*"):
        return [(["*"], None)], position + 1
    if position >= len(stream) or stream[position].kind != "ident":
        return [], position
    name = stream[position].text
    position += 1
    if at(stream, position, "::"):
        inner, end = use_tree(stream, position + 1)
        return [([name, *path], alias) for path, alias in inner] or [([name], None)], end
    if keyword(stream, position, "as") and position + 1 < len(stream) and stream[position + 1].kind == "ident":
        return [([name], stream[position + 1].text)], position + 2
    return [([name], None)], position


def anchor(path: list[str], module: str, depth: int, in_use: bool) -> list[list[str]]:
    """The crate-relative paths a path written in `module`, `depth` inline modules deep, may stand for.

    Each `super` leaves one enclosing inline `mod`; leaving the file's top level
    reaches the crate root. A path that stays inside the file becomes
    `[module, ...]`, whose inline module names `member` skips (the crate root's
    inline modules are the root's own scope). Any other head is a name in the
    module's scope; a `use` path is also read from the crate root (fail closed,
    as in edition 2015). An extern (`::`) or `Self` path names nothing here.
    """
    head, rest = path[0], path[1:]
    if head in {"::", "Self"}:
        return []
    if head == "crate":
        return [rest]
    if head in {"super", "self"}:
        ups = int(head == "super")
        while rest and rest[0] == "super":
            rest, ups = rest[1:], ups + 1
        return [rest] if module == "lib" or ups > depth else [[module, *rest]]
    return [path] if module == "lib" else [[module, *path], *([path] if in_use else [])]


class Module(NamedTuple):
    bindings: list[tuple[str, list[str], bool]]  # name (`*` for a glob), crate-relative target, `pub`
    inline: set[str]  # inline `mod name { ... }` blocks, whose items count as the file's own
    uses: list[list[str]]  # crate-relative paths of the `use` items
    paths: list[list[str]]  # crate-relative paths written anywhere else
    unsupported: list[str]


def public(stream: list[Token], position: int) -> bool:
    """Whether the item whose keyword is at stream[position] has a `pub` or `pub(...)` visibility."""
    before = position - 1
    if at(stream, before, ")"):
        level = 0
        while before >= 0:
            level += at(stream, before, ")") - at(stream, before, "(")
            if level == 0:
                break
            before -= 1
        before -= 1
    return keyword(stream, before, "pub")


def closing(stream: list[Token], position: int, opening: str, close: str) -> int:
    """The index of the bracket that closes the one at stream[position] (or the end)."""
    level = 0
    for index in range(position, len(stream)):
        level += at(stream, index, opening) - at(stream, index, close)
        if level == 0:
            return index
    return len(stream)


def unsupported(stream: list[Token]) -> list[str]:
    """The constructs that move code or names past path resolution, in order of appearance."""
    found = []
    for index, token in enumerate(stream):
        if token.kind == "invalid":
            found.append(token.text)
        elif at(stream, index, "#"):
            start = index + 1 + at(stream, index + 1, "!")
            if at(stream, start, "["):
                names = {item.text for item in stream[start:closing(stream, start, "[", "]")] if item.kind == "ident"}
                found += [f"#[{name}" for name in sorted(names & MOVING_ATTRIBUTES)]
        elif token.kind == "ident" and token.text == "include" and at(stream, index + 1, "!"):
            found.append("include!")
        elif keyword(stream, index, "extern") and keyword(stream, index + 1, "crate") and keyword(stream, index + 2, "self"):
            found.append("extern crate self")
        elif token.kind == "::" and at(stream, index + 1, "$"):
            found.append("::$")
    return found


def parse_module(module: str, text: str) -> Module:
    """One file's `use` bindings, inline modules, written paths and unsupported constructs."""
    stream = tokens(text)
    spans, inline, declared = [], set(), set()
    for index in range(len(stream)):
        if keyword(stream, index, "mod") and index + 1 < len(stream) and stream[index + 1].kind == "ident":
            declared.add(index + 1)
            if at(stream, index + 2, "{"):
                spans.append((index, closing(stream, index + 2, "{", "}")))
                inline.add(stream[index + 1].text)

    def depth(index: int) -> int:
        return sum(start < index < end for start, end in spans)

    # Inside a builtin attribute, a one-word path that is not a macro call (`allow(x)`, `cfg(test)`)
    # and a string (`doc = "..."`) name nothing. Any other attribute may be a proc macro that turns
    # a string into a path (`serde(with = "crate::surface::f")`), so its strings are read as code.
    builtin, macro_strings = set(), []
    for index in range(len(stream)):
        start = index + 1 + at(stream, index + 1, "!")
        if at(stream, index, "#") and at(stream, start, "["):
            end = closing(stream, start, "[", "]")
            name = stream[start + 1] if start + 1 < len(stream) else Token("punct", "]")
            if (name.kind == "ident" and not name.raw and name.text in BUILTIN_ATTRIBUTES
                    and not at(stream, start + 2, "::")):
                builtin.update(range(start, end))
            else:
                macro_strings += [item for item in range(start, end) if stream[item].kind == "string"]

    bindings, uses, problems, consumed = [], [], unsupported(stream), set()
    for index in range(len(stream)):
        if not keyword(stream, index, "use") or at(stream, index + 1, "<"):  # `use<'a>` captures lifetimes
            continue
        found, end = use_tree(stream, index + 1)
        consumed.update(range(index, end))
        visible = public(stream, index)
        for path, alias in found:
            uses += anchor(path, module, depth(index), True)
            if path[-1] == "include":
                problems.append("include!")
            if len(path) > 1 and path[-1] == "self":
                path = path[:-1]
            name = alias or path[-1]
            if name == "*":
                path = path[:-1]
            if name != "_" and path:
                bindings += [(name, target, visible) for target in anchor(path, module, depth(index), True)]
    paths = [anchored for index, path in written_paths(stream, consumed | declared, builtin)
             for anchored in anchor(path, module, depth(index), False)]
    for index in macro_strings:
        paths += [anchored for _, path in written_paths(tokens(stream[index].text), set(), set())
                  for anchored in anchor(path, module, depth(index), False)]
    return Module(bindings, inline, uses, paths, list(dict.fromkeys(problems)))


def written_paths(stream: list[Token], skipped: set[int], builtin: set[int]) -> list[tuple[int, list[str]]]:
    """Every path (and the index it starts at) outside `skipped` that is not a field or method name."""
    found = []
    for index, token in enumerate(stream):
        field = at(stream, index - 1, ".") and not at(stream, index - 2, ".")  # `..x` is a range
        if (token.kind != "ident" or index in skipped or keyword_at(stream, index)
                or at(stream, index - 1, "::") or field):
            continue
        paths, end = use_tree(stream, index)
        if index in builtin and end == index + 1 and not at(stream, end, "!"):
            continue
        found += [(index, path) for path, _ in paths]
    return found


def resolve(path: list[str], modules: dict[str, Module], viewer: str, seen: frozenset = frozenset()) -> set[str]:
    """The crate modules a crate-relative path, written in module `viewer`, may depend on."""
    if not path or path[0] in {"::", "crate", "super", "self", "Self"}:
        return set()
    head = path[0]
    if head == "*":
        return set(modules)
    if head in modules and head != "lib":
        return {head} | member(head, path[1:], modules, viewer, seen)
    return {"lib"} | member("lib", path, modules, viewer, seen)


def member(module: str, path: list[str], modules: dict[str, Module], viewer: str, seen: frozenset) -> set[str]:
    """The modules `module::path` may resolve through, following `module`'s `use` bindings.

    The viewer sees its own private bindings and the crate root's (every module
    is the root's descendant); other modules show only `pub` ones. A binding's
    target was written in `module`, so it resolves with `module` as viewer. The
    crate root also names its child modules.
    """
    while path and path[0] in modules[module].inline:
        path = path[1:]
    if not path:
        return set()
    private = module in {viewer, "lib"}
    if (module, path[0], private) in seen:
        return set()
    seen = seen | {(module, path[0], private)}
    visible = [(name, target) for name, target, pub in modules[module].bindings if pub or private]
    if path[0] == "*":
        if module == "lib":
            return set(modules)
        targets = [target for _, target in visible]
    else:
        targets = ([[*target, *path[1:]] for name, target in visible if name == path[0]]
                   + [[*target, *path] for name, target in visible if name == "*"])
    found = set()
    if module == "lib" and path[0] in modules and path[0] != "lib":
        found |= resolve(path, modules, viewer, seen)
    for target in targets:
        found |= resolve(target, modules, module, seen)
    return found


def module_edges(crate: str, source: Path, groups: dict[str, int]) -> tuple[set[str], list[str]]:
    """Outward intra-crate edges of one crate, and its unmapped or unsupported modules."""
    files = {path.stem: path for path in sorted(source.glob("*.rs"))}
    modules = {name: parse_module(name, path.read_text()) for name, path in files.items()}
    errors = sorted({*(f"unmapped Rust module: {crate}: {name}" for name in files if name not in groups),
                     *(f"unmapped Rust module: {crate}: {path.relative_to(source).as_posix()}"
                       for path in source.rglob("*.rs") if path.parent != source)})
    errors += [f"unsupported Rust construct: {crate}: {name}: {problem!r}"
               for name, module in modules.items() for problem in module.unsupported]
    modules.setdefault("lib", Module([], set(), [], [], []))
    edges = set()
    for importer, module in modules.items():
        if importer not in groups:
            continue
        # The root's `use` items are the facade: they count where they are named.
        for path in module.paths + ([] if importer == "lib" else module.uses):
            for target in resolve(path, modules, importer):
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
