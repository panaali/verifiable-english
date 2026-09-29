"""Reject new outward Lean imports and stale, exact legacy exceptions."""
from __future__ import annotations

import json
import re
import sys

from layer_policy import ROOT, lean_layer

LEDGER = ROOT / "tools/lean-layer-exceptions.json"
# The header grammar of the pinned toolchain (Lean.Parser.Module.header):
#   ["module"] ["prelude"] {["public"] ["meta"] "import" ["all"] ident}
# Lean reads nothing else as an import: the header ends at the first other
# token, and an `import` after it is a command error, not an import.
HEADER_KEYWORDS = frozenset({"module", "prelude", "public", "meta", "import", "all"})
BLOCK = re.compile(r"/-|-/")
# Lean's isIdRest: ASCII alphanumerics, _ ' ! ?, isLetterLike, isSubScriptAlnum.
ORDINARY_PART_REST = re.compile(r"[A-Za-z0-9_'!?À-ÖØ-öø-ſΑ-ΟΡ΢"
                                r"Τ-Ωα-κμ-ϻἀ-῾℀-⅏"
                                r"\U0001d49c-\U0001d59f₀-₉ₐ-ₜᵢ-ᵪⱼ]*")


def _id_first(char: str) -> bool:
    """Lean's isIdFirst: ASCII letters, `_`, and isLetterLike."""
    code = ord(char)
    return (char.isascii() and (char.isalpha() or char == "_")
            or (0x3b1 <= code <= 0x3c9 and code != 0x3bb)
            or (0x391 <= code <= 0x3a9 and code not in (0x3a0, 0x3a3))
            or 0x3ca <= code <= 0x3fb or 0x1f00 <= code <= 0x1ffe or 0x2100 <= code <= 0x214f
            or 0x1d49c <= code <= 0x1d59f
            or (0xc0 <= code <= 0xff and code not in (0xd7, 0xf7)) or 0x100 <= code <= 0x17f)


def _skip_whitespace(source: str, index: int) -> int | None:
    """Lean's `whitespace`: spaces, newlines, `--` and nested `/- -/` comments.

    None marks what Lean rejects there: a tab, an isolated carriage return, or
    an unterminated comment. `/--` and `/-!` are doc-comment tokens, not space.
    """
    while index < len(source):
        char = source[index]
        if char in " \n":
            index += 1
        elif char in "\t\r":
            return None
        elif source.startswith("--", index):
            end = source.find("\n", index)
            index = len(source) if end < 0 else end
        elif source.startswith("/-", index) and source[index + 2:index + 3] not in ("-", "!"):
            depth, index = 1, index + 2
            while depth:
                mark = BLOCK.search(source, index)
                if mark is None:
                    return None
                depth += 1 if mark[0] == "/-" else -1
                index = mark.end()
        else:
            break
    return index


def _token(source: str, index: int) -> tuple[str, str | tuple[str, ...], int] | None:
    """Read the token at `index` as Lean's identFn does.

    Returns ("keyword", word, end) for a header keyword, ("ident", parts, end)
    for an identifier (a «quoted» part is one part, taken verbatim), or None for
    any other token, which ends the header.
    """
    start, parts = index, []
    while True:
        if source.startswith("«", index):
            close = source.find("»", index + 1)
            if close < 0:
                return None  # unterminated identifier escape
            parts.append(source[index + 1:close])
            index = close + 1
        elif index < len(source) and _id_first(source[index]):
            end = ORDINARY_PART_REST.match(source, index + 1).end()
            parts.append(source[index:end])
            index = end
        else:
            return None
        following = source[index + 1:index + 2]
        if not (source.startswith(".", index) and following and (following == "«" or _id_first(following))):
            break
        index += 1
    raw = source[start:index]
    if raw in HEADER_KEYWORDS:  # a keyword token beats an identifier of equal length
        return "keyword", raw, index
    return "ident", tuple(parts), index


def imports(source: str) -> list[str]:
    """Read the modules a Lean file's header imports, as the header parser does.

    Only the header is read, so an `import` inside a later declaration name,
    string or comment is never an import. The source is taken as Lean's
    frontend reads it (CRLF becomes LF). A name's parts are joined with `.`,
    quoted parts verbatim, which is how a module path maps to its name here.
    """
    source = source.replace("\r\n", "\n")
    found: list[str] = []

    def keyword(at: int | None, word: str) -> int | None:
        """The position after `word` and its whitespace, or None if absent."""
        token = None if at is None else _token(source, at)
        return _skip_whitespace(source, token[2]) if token and token[:2] == ("keyword", word) else None

    index = _skip_whitespace(source, 0)
    for word in ("module", "prelude"):
        index = keyword(index, word) or index
    while index is not None:
        at = index
        for word in ("public", "meta"):
            at = keyword(at, word) or at
        if (at := keyword(at, "import")) is None:
            break
        at = keyword(at, "all") or at
        token = _token(source, at)
        if not token or token[0] != "ident":
            break
        found.append(".".join(token[1]))
        index = _skip_whitespace(source, token[2])
    return found


def main() -> int:
    paths = {".".join(path.relative_to(ROOT / "lean").with_suffix("").parts): path
             for path in (ROOT / "lean").rglob("*.lean") if ".lake" not in path.parts}
    unmapped = sorted(module for module in paths if lean_layer(module) is None)
    edges = set()
    unknown = set()
    for importer, path in paths.items():
        for imported in imports(path.read_text()):
            if imported not in paths:
                if imported.startswith("VE.") or imported in {"VE", "Iceberg"}:
                    unknown.add(f"{importer} -> {imported}")
                continue  # Lean and Std library imports
            importer_layer = lean_layer(importer)
            imported_layer = lean_layer(imported)
            if importer_layer is not None and imported_layer is not None and importer_layer < imported_layer:
                edges.add(f"{importer} -> {imported}")
    expected = json.loads(LEDGER.read_text())
    for message in (f"unmapped Lean module: {x}" for x in unmapped):
        print(message, file=sys.stderr)
    for message in (f"missing local Lean import: {x}" for x in sorted(unknown)):
        print(message, file=sys.stderr)
    for edge in sorted(edges - expected.keys()):
        print(f"new outward Lean import: {edge}", file=sys.stderr)
    for edge in sorted(expected.keys() - edges):
        print(f"stale Lean exception: {edge}", file=sys.stderr)
    if unmapped or unknown or edges != expected.keys():
        return 1
    print(f"Lean layer graph kept ({len(paths)} modules, {len(edges)} reviewed legacy edges)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
