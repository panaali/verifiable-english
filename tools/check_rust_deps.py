"""Check workspace crate dependencies against the inward-only rule.

Inside a crate listed in MODULE_GROUPS, every `src/*.rs` module is also
assigned a group (1 kernel, 2 profile, 3 surface) and every path it writes, in
`use` trees and inline (generic arguments such as `parse::<u8>()` end a path),
must point inward unless the exact edge is in MODULE_LEDGER, which rejects
stale keys as the other ledgers do.

This is a stopgap until the crate split (plan R1-R3), after which cargo
enforces the boundary, so it does not re-implement Rust's name resolution. It
is fail-closed on a strict subset whose dependencies can be read off the
source: paths `crate::<module>::...` (also `super::` reaching the crate root,
raw identifiers, Unicode identifiers compared after NFC; the source is
tokenized as rustc reads it), ordinary `mod` declarations, and `lib.rs`'s
top-level `use` items as the one re-exporting facade (like `ve/__init__.py`),
each naming a crate module directly (`pub use surface::parse;`,
`pub use risk::{Range as RiskRange};`), so `crate::<name>` resolves in one hop.
A path written in another module that does not start at the crate root names
that module's own items or its imports, which count where the `use` is
written. `lib.rs`'s own items (`Error`, `Result`, `MAX_*`, `error`) and the
paths inside them are kernel. Every form that could hide a cross-module
dependency is rejected with a message naming the plain form: aliases and globs
of the crate root, re-exports outside `lib.rs`'s top level, facade re-export
chains and module globs, inline modules named like an imported name or a crate
module, crate paths in attribute or macro strings (escapes decoded) and in
macro definitions, macro transcribers that join a substitution (`$x`, `$(...)`)
to a path token or one repetition to the next (`$root::surface`, `crate $($t)*`,
`$($t)*`), or substitute into a `use`, a `mod` name, a macro name or an
attribute, `#[path]`, `#[macro_use]`, `#[macro_export]`, `include!`,
`extern crate self`, macros 2.0, a macro metavariable after `::` and characters
rustc rejects outside literals.
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
    **dict.fromkeys(("eval", "route", "search", "order", "units", "risk", "readings"), 2),
    "surface": 3,
}}
# What rustc skips between tokens (Pattern_White_Space, line comments), string literals
# (kept as tokens, escapes decoded: a proc macro may expand one into a path), and the other
# literals, lifetimes and numbers. A raw string ends at a quote with as many `#`.
SKIPPED = re.compile(r"""
    [\t\n\x0b\x0c\r\x20\x85‎‏  ]+
  | //[^\n]*
  | [bc]?r(?P<hashes>\#*)"
  | [bc]?"(?P<string>(?:\\.|[^"\\])*)"
  | b?'(?:\\(?:u\{[^}']*\}|x[0-9A-Fa-f]{2}|.)|[^'\\\n\r\t])'
  | '(?:r\#)?[^\W\d]\w*
  | \d\w*
""", re.S | re.X)
BLOCK = re.compile(r"/\*|\*/")
# The escapes of a cooked string literal; a line continuation skips the following whitespace.
ESCAPE = re.compile(r"""\\(?:x(?P<byte>[0-9A-Fa-f]{2})|u\{(?P<unicode>[0-9A-Fa-f][0-9A-Fa-f_]*)\}
                        |(?P<simple>[nrt\\0'"])|\n[\t\n\r\x20]*)""", re.X)
SIMPLE_ESCAPES = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", "0": "\0", "'": "'", '"': '"'}
# Attributes that load another file as a module or move macro names past this check.
MOVING_ATTRIBUTES = {"path", "macro_use", "macro_export"}
# Strict and reserved keywords other than the path keywords: never the head of a path.
KEYWORDS = set("""as async await become box break const continue do dyn else enum extern false final fn for
gen if impl in let loop macro match mod move mut override priv pub ref return static struct trait true try
type typeof unsafe unsized use virtual where while yield""".split())
# Builtin attributes whose arguments are lints, configuration predicates, layouts or text.
BUILTIN_ATTRIBUTES = {"allow", "warn", "deny", "forbid", "expect", "cfg", "doc", "repr", "inline", "must_use",
                      "deprecated", "test", "ignore", "should_panic", "non_exhaustive", "cold", "track_caller"}
PLAIN = "write plain `crate::<module>::...` paths (`use crate::<module>::item;`)"
RULES = {
    "invalid": "a character rustc rejects outside literals",
    "moving": "moves code or names past this check; declare modules with plain `mod name;` and " + PLAIN,
    "macro 2.0": "macros 2.0 resolve names past this check; use `macro_rules!` without crate paths",
    "crate alias": "binds the crate root to a name, so later paths can name modules without `crate::`; " + PLAIN,
    "crate glob": "a glob of the crate root imports every module and re-export unnamed; " + PLAIN,
    "re-export": "re-exports are allowed only at the top level of lib.rs (the facade); " + PLAIN
                 + " where the item is used",
    "facade chain": "a lib.rs re-export through another lib.rs name; re-export from the defining module "
                    "(`pub use <module>::item;`)",
    "facade glob": "a lib.rs glob of a crate module re-exports names this check cannot see; list them "
                   "(`pub use <module>::{a, b};`)",
    "beyond root": "`super` beyond the crate root",
    "shadowing module": "an inline module named like an imported name or a crate module; rename it",
    "string path": "a crate path inside an attribute or macro string; " + PLAIN + " outside strings",
    "macro path": "a crate path inside a macro definition, which resolves where the macro is called; call a "
                  "function instead and " + PLAIN,
    "macro construction": "a macro that joins substituted tokens into a path, or substitutes into a `use`, a "
                          "module name, a macro name or an attribute, builds names this check cannot see; call "
                          "a function instead and " + PLAIN,
}


class Token(NamedTuple):
    kind: str  # "ident" (NFC, without `r#`), "::", "punct", "string" (decoded contents), or "invalid"
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


def cooked(text: str) -> str | None:
    """The value of a cooked string literal's contents, or None for an escape rustc rejects."""
    found, position = [], 0
    while (backslash := text.find("\\", position)) >= 0:
        found.append(text[position:backslash])
        match = ESCAPE.match(text, backslash)
        if match is None:
            return None
        if match["byte"] is not None:
            found.append(chr(int(match["byte"], 16)))
        elif match["unicode"] is not None:
            digits = match["unicode"].replace("_", "")
            value = int(digits, 16) if len(digits) <= 6 else -1
            if not (0 <= value <= 0x10FFFF and not 0xD800 <= value <= 0xDFFF):
                return None
            found.append(chr(value))
        elif match["simple"] is not None:
            found.append(SIMPLE_ESCAPES[match["simple"]])
        position = match.end()
    return "".join(found) + text[position:]


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
                value = cooked(match["string"])
                found.append(Token("string", value) if value is not None else Token("invalid", match[0]))
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


def crate_relative(path: list[str], module: str, depth: int) -> list[str] | None:
    """The crate-root-relative form of a path written in `module`, `depth` inline modules deep.

    Each `super` leaves one enclosing inline `mod`, and leaving the file's top
    level reaches the crate root (one more is an error, returned as `["super"]`).
    None means a name local to the file (its own items and imports) or extern
    (`::`, `Self`). Every path in lib.rs is read from the crate root, at any
    inline depth (fail closed: its inline modules may glob the root).
    """
    head, rest = path[0], path[1:]
    if head == "crate":
        return rest
    if head in {"super", "self"}:
        ups = int(head == "super")
        while rest and rest[0] == "super":
            rest, ups = rest[1:], ups + 1
        outside = depth + (module != "lib")  # how many `super` reach the crate root
        return rest if ups == outside or module == "lib" and ups < outside else ["super"] if ups > outside else None
    return path if module == "lib" and head not in {"::", "Self"} else None


class Module(NamedTuple):
    facade: list[tuple[str, list[str], bool, str]]  # lib.rs's top-level `use` leaves: name, root-relative
    # target, glob, spelling
    paths: list[list[str]]  # root-relative paths it depends on (lib.rs: outside its facade)
    unsupported: list[tuple[str, str]]  # (construct, RULES key)


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


def group_end(stream: list[Token], position: int) -> int:
    """The index closing the delimited group that opens at stream[position], or position if none opens."""
    for opening, close in ("()", "[]", "{}"):
        if at(stream, position, opening):
            return closing(stream, position, opening, close)
    return position


def moving(stream: list[Token]) -> list[tuple[str, str]]:
    """The constructs that move code or names past this check, in order of appearance."""
    found = []
    for index, token in enumerate(stream):
        if token.kind == "invalid":
            found.append((token.text, "invalid"))
        elif at(stream, index, "#"):
            start = index + 1 + at(stream, index + 1, "!")
            if at(stream, start, "["):
                names = {item.text for item in stream[start:closing(stream, start, "[", "]")] if item.kind == "ident"}
                found += [(f"#[{name}", "moving") for name in sorted(names & MOVING_ATTRIBUTES)]
        elif token.kind == "ident" and token.text == "include" and at(stream, index + 1, "!"):
            found.append(("include!", "moving"))
        elif keyword(stream, index, "extern") and keyword(stream, index + 1, "crate") and keyword(stream, index + 2, "self"):
            found.append(("extern crate self", "moving"))
        elif token.kind == "::" and at(stream, index + 1, "$"):
            found.append(("::$", "moving"))
        elif keyword(stream, index, "macro") and index + 1 < len(stream) and stream[index + 1].kind == "ident":
            found.append((f"macro {stream[index + 1].text}", "macro 2.0"))
    return found


def transcribers(stream: list[Token], opening: int, close: int) -> list[tuple[int, int]]:
    """The (start, end) of each rule's transcriber in the macro_rules body stream[opening:close + 1].

    A body that is not a sequence of `(matcher) => {transcriber};` is read as
    one transcriber from where the sequence breaks (fail closed).
    """
    found, index = [], opening + 1
    while index < close:
        matcher_end = group_end(stream, index)
        start = matcher_end + 3
        stop = group_end(stream, start)
        if matcher_end == index or not (at(stream, matcher_end + 1, "=") and at(stream, matcher_end + 2, ">")) \
                or stop == start:
            return found + [(index, close)]
        found.append((start + 1, min(stop, close)))
        index = stop + 1 + at(stream, stop + 1, ";")
    return found


def transcriber_items(stream: list[Token], start: int, end: int) -> list[tuple[str, int, int]]:
    """The items of stream[start:end] as (kind, first index, end index): "sub" for `$name`, `$crate`, `$$`
    and `${...}`, "rep" for `$(...) separator? operator`, "group" for a delimited group, else "token"."""
    items, index = [], start
    while index < end:
        if at(stream, index, "$") and index + 1 < end:
            if at(stream, index + 1, "("):
                after = closing(stream, index + 1, "(", ")") + 1
                after += not any(at(stream, after, operator) for operator in "*+?")  # a separator
                items.append(("rep", index, min(after + 1, end)))
                index = after + 1
                continue
            if at(stream, index + 1, "{") or at(stream, index + 1, "$") or stream[index + 1].kind == "ident":
                items.append(("sub", index, min(group_end(stream, index + 1) + 1, end)))
                index = items[-1][2]
                continue
        stop = min(group_end(stream, index) + 1, end)
        items.append(("group" if stop > index + 1 else "token", index, stop))
        index = stop
    return items


def path_capable(stream: list[Token], item: tuple[str, int, int]) -> bool:
    """Whether the item can be or hold a path segment or `::` (every substitution can)."""
    kind, index, _ = item
    return kind in {"sub", "rep"} or kind == "token" and (
        stream[index].kind == "::" or stream[index].kind == "ident" and not keyword_at(stream, index))


def constructs(stream: list[Token], start: int, end: int) -> bool:
    """Whether the transcriber stream[start:end] builds a name this check cannot see when it expands.

    Paths are runs of segments and `::`, so a substitution next to a segment,
    `::` or another substitution (`$root::surface`, `crate $($t)*`), a
    repetition that joins its iterations (`$($t)*`, separator `::`), and a
    substitution in a `use` item, a `mod` name, a macro name (`$m!`) or an
    attribute (`#[$a]`) are constructions. Paths do not cross delimiters.
    """
    items = transcriber_items(stream, start, end)
    for position, (kind, index, stop) in enumerate(items):
        following = items[position + 1] if position + 1 < len(items) else None
        substituted = kind in {"sub", "rep"}
        if following is not None:
            joined = substituted or following[0] in {"sub", "rep"}
            if joined and path_capable(stream, items[position]) and path_capable(stream, following):
                return True
            if substituted and at(stream, following[1], "!"):
                return True
            if keyword(stream, index, "mod") and following[0] in {"sub", "rep"}:
                return True
        if keyword(stream, index, "use") and not at(stream, index + 1, "<"):
            semicolon = next((item[1] for item in items[position:] if at(stream, item[1], ";")), end)
            if any(at(stream, token, "$") for token in range(index, semicolon)):
                return True
        if at(stream, index, "#"):
            bracket = index + 1 + at(stream, index + 1, "!")
            if at(stream, bracket, "[") and any(at(stream, token, "$")
                                                for token in range(bracket, group_end(stream, bracket))):
                return True
        if kind == "group" and constructs(stream, index + 1, stop - 1):
            return True
        if kind == "rep":
            close = closing(stream, index + 1, "(", ")")
            inner = transcriber_items(stream, index + 2, close)
            separator = close + 1 if stop - close == 3 else None
            if constructs(stream, index + 2, close):
                return True
            if separator is not None and path_capable(stream, ("token", separator, separator + 1)):
                return True
            if separator is None and inner and path_capable(stream, inner[-1]) and path_capable(stream, inner[0]):
                return True
    return False


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


def spelled(path: list[str], alias: str | None = None) -> str:
    return "use " + "::".join(path).replace("::::", "::") + (f" as {alias}" if alias else "")


def parse_module(module: str, text: str, crate_modules: set[str]) -> Module:
    """One file's facade (lib.rs), root-relative paths and unsupported constructs."""
    stream = tokens(text)
    problems = moving(stream)
    spans, inline, declared, level, braces = [], [], set(), [], 0
    for index in range(len(stream)):
        braces -= at(stream, index, "}")
        level.append(braces)
        braces += at(stream, index, "{")
        if keyword(stream, index, "mod") and index + 1 < len(stream) and stream[index + 1].kind == "ident":
            declared.add(index + 1)
            if at(stream, index + 2, "{"):
                spans.append((index, closing(stream, index + 2, "{", "}")))
                inline.append(stream[index + 1].text)

    def depth(index: int) -> int:
        return sum(start < index < end for start, end in spans)

    # Inside a builtin attribute, a one-word path that is not a macro call (`allow(x)`, `cfg(test)`)
    # and a string (`doc = "..."`) name nothing. Any other attribute may be a proc macro that turns
    # a string into a path (`serde(with = "f")`), so its strings are read as code, and a macro call
    # may do the same; neither may hold a crate path.
    builtin, attribute_strings, macro_strings = set(), [], []
    for index in range(len(stream)):
        start = index + 1 + at(stream, index + 1, "!")
        if at(stream, index, "#") and at(stream, start, "["):
            end = closing(stream, start, "[", "]")
            name = stream[start + 1] if start + 1 < len(stream) else Token("punct", "]")
            if (name.kind == "ident" and not name.raw and name.text in BUILTIN_ATTRIBUTES
                    and not at(stream, start + 2, "::")):
                builtin.update(range(start, end))
            else:
                attribute_strings += [item for item in range(start, end) if stream[item].kind == "string"]
        elif keyword(stream, index, "macro_rules") and at(stream, index + 1, "!"):
            close = group_end(stream, index + 3)
            name = stream[index + 2].text if index + 2 < len(stream) else ""
            if any(stream[item].kind == "ident" and stream[item].text in {"crate", "super", "self"}
                   and (at(stream, item + 1, "::") or at(stream, item - 1, "$")) for item in range(index + 3, close)):
                problems.append((f"macro_rules! {name}", "macro path"))
            elif any(constructs(stream, start, stop) for start, stop in transcribers(stream, index + 3, close)):
                problems.append((f"macro_rules! {name}", "macro construction"))
        elif stream[index].kind == "ident" and not keyword_at(stream, index) and at(stream, index + 1, "!"):
            macro_strings += [item for item in range(index + 2, group_end(stream, index + 2))
                              if stream[item].kind == "string"]

    leaves, consumed = [], set()  # (use index, path, alias, public)
    for index in range(len(stream)):
        if not keyword(stream, index, "use") or at(stream, index + 1, "<"):  # `use<'a>` captures lifetimes
            continue
        found, end = use_tree(stream, index + 1)
        consumed.update(range(index, end))
        leaves += [(index, path, alias, public(stream, index)) for path, alias in found]
    facade, paths, bound = [], [], set()
    for index, path, alias, visible in leaves:
        if path[-1] == "include":
            problems.append(("include!", "moving"))
        glob = path[-1] == "*"
        target = path[:-1] if glob or (len(path) > 1 and path[-1] == "self") else path
        if not glob and alias != "_":
            bound.add(alias or target[-1])
        relative = crate_relative(target, module, depth(index))
        at_facade = module == "lib" and depth(index) == 0 and level[index] == 0
        if visible and not at_facade:
            problems.append((spelled(path, alias), "re-export"))
        if relative == ["super"]:
            problems.append((spelled(path, alias), "beyond root"))
        elif relative == []:  # lib.rs reads every path from the root, so its root globs hide nothing
            if not (glob and module == "lib"):
                problems.append((spelled(path, alias), "crate glob" if glob else "crate alias"))
        elif at_facade:
            if relative is not None:
                facade.append((alias or target[-1], relative, glob, spelled(path, alias)))
        elif relative is not None:
            paths.append(relative)
    problems += [(f"mod {name}", "shadowing module") for name in inline if name in bound | crate_modules]

    for index, path in written_paths(stream, consumed | declared, builtin):
        relative = crate_relative(path, module, depth(index))
        if relative == ["super"]:
            problems.append(("::".join(path), "beyond root"))
        elif relative:
            paths.append(relative)
    for index in attribute_strings + macro_strings:
        for _, path in written_paths(tokens(stream[index].text), set(), set()):
            if len(path) > 1 and (path[0] in {"crate", "super", "self"} or path[0] in crate_modules):
                problems.append((stream[index].text, "string path"))
            elif index in attribute_strings and (relative := crate_relative(path, module, depth(index))):
                paths.append(relative)
    return Module(facade, paths, list(dict.fromkeys(problems)))


def facade_targets(lib: Module, crate_modules: set[str]) -> tuple[dict[str, set[str]], list[tuple[str, str]]]:
    """The crate modules each lib.rs re-export name stands for (one hop), and the rejected re-exports."""
    names = {name for name, _, glob, _ in lib.facade if not glob}
    targets: dict[str, set[str]] = {}
    problems = []
    for name, target, glob, construct in lib.facade:
        head = target[0]
        if head in names and target != [name]:
            problems.append((construct, "facade chain"))
        elif glob and head in crate_modules:
            problems.append((construct, "facade glob"))
        elif not glob:
            targets.setdefault(name, set()).add(head if head in crate_modules else "lib")
    return targets, problems


def module_edges(crate: str, source: Path, groups: dict[str, int]) -> tuple[set[str], list[str]]:
    """Outward intra-crate edges of one crate, and its unmapped or unsupported modules."""
    files = {path.stem: path for path in sorted(source.glob("*.rs"))}
    crate_modules = set(files) - {"lib"}
    modules = {name: parse_module(name, path.read_text(), crate_modules) for name, path in files.items()}
    modules.setdefault("lib", Module([], [], []))
    targets, facade_problems = facade_targets(modules["lib"], crate_modules)
    errors = sorted({*(f"unmapped Rust module: {crate}: {name}" for name in files if name not in groups),
                     *(f"unmapped Rust module: {crate}: {path.relative_to(source).as_posix()}"
                       for path in source.rglob("*.rs") if path.parent != source)})
    errors += [f"unsupported Rust construct: {crate}: {name}: {construct!r}: {RULES[rule]}"
               for name, module in modules.items()
               for construct, rule in module.unsupported + (facade_problems if name == "lib" else [])]
    edges = set()
    for importer, module in modules.items():
        if importer not in groups:
            continue
        for path in module.paths:
            head = path[0]
            found = ({head} if head in crate_modules else set()) | targets.get(head, set())
            for target in found:
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
