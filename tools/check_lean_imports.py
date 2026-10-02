"""Reject new outward Lean imports and stale, exact legacy exceptions."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

from layer_policy import ROOT, lean_layer

LEDGER = ROOT / "tools/lean-layer-exceptions.json"
PLAIN_LAYOUT = ("write the header in the plain layout: one `import A.B.C` per line at column 0, "
                "with only blank lines, full-line `--` comments and `/- ... -/` block comments "
                "(no `/-` inside, nothing after the closing `-/`) between them")
# One plain import: ASCII identifier parts, nothing else on the line.
PLAIN_IMPORT = re.compile(r"import ((?:[A-Za-z_][A-Za-z0-9_']*\.)*[A-Za-z_][A-Za-z0-9_']*) *")
# A line that starts with one of these may continue Lean's header
# (["module"] ["prelude"] {["public"] ["meta"] "import" ["all"] ident}), so it
# must be a plain import. The test is a bare prefix: fail closed.
HEADER_WORDS = ("import", "prelude", "module", "public", "meta")
KEYWORD_NAMES = {"import", "prelude", "module", "public", "meta", "all"}
# `lean --deps` has this long in total to confirm the staged headers.
ORACLE_BUDGET = 3.0


# docs/spec/wire-contract.md 7.3: the wire contract engine chooses diagnostics and never a verdict, so no
# module on a verdict path may import it. Only its own modules, the `ve_diagnose` root and the audit
# manifest (the engine theorems only) do.
DIAGNOSTIC_ONLY = "VE.WireContract"
DIAGNOSTIC_IMPORTERS = frozenset({"DiagnoseMain"})
AUDIT_IMPORTS = frozenset({"VE.WireContract.Engine"})


def diagnostic_only_violation(importer: str, imported: str) -> str | None:
    """The message for an import of a diagnostic-only module that the rule of spec 7.3 does not admit."""
    if imported != DIAGNOSTIC_ONLY and not imported.startswith(DIAGNOSTIC_ONLY + "."):
        return None
    if importer.startswith(DIAGNOSTIC_ONLY + ".") or importer in DIAGNOSTIC_IMPORTERS:
        return None
    if importer == "VE.Audit" and imported in AUDIT_IMPORTS:
        return None
    return (f"{importer} -> {imported}: {DIAGNOSTIC_ONLY}.* is diagnostic only and may be imported by "
            f"{DIAGNOSTIC_ONLY}.*, DiagnoseMain and (the engine only) VE.Audit (docs/spec/wire-contract.md 7.3)")


class HeaderError(ValueError):
    """A Lean header outside the plain layout; `line` is 1-based."""

    def __init__(self, line: int, reason: str) -> None:
        super().__init__(f"line {line}: {reason}; {PLAIN_LAYOUT}")
        self.line = line


def imports(source: str) -> list[str]:
    """The modules a Lean file imports, read from a header in the plain layout.

    The header is the run of lines at the start of the file that are blank,
    full-line `--` comments, ordinary `/- -/` block comments or `import A.B.C`
    lines; it ends at the first other line, which Lean reads as a command (a
    `/--` or `/-!` doc comment, a declaration, ...). Inside that run every
    layout Lean could read differently raises HeaderError instead of being
    interpreted: a block comment containing `/-` (nesting, or delimiters that
    overlap as in `/-/-/`), text after a closing `-/`, an import sharing its
    line with anything, `prelude`/`module`/`public`/`meta` forms, «» names,
    tabs and lone carriage returns. CRLF is read as LF, as Lean's frontend does.
    """
    lines = source.replace("\r\n", "\n").split("\n")
    found: list[str] = []
    number = 0
    while number < len(lines):
        line = lines[number]
        number += 1
        text = line.lstrip(" ")
        if not text or text.startswith("--"):
            if "\r" in line:
                raise HeaderError(number, "carriage return in the header")
            continue
        if not text[0].isprintable():  # a tab, carriage return, byte order mark, Unicode space...
            raise HeaderError(number, f"character {text[0]!r} at the start of a header line")
        if text.startswith("/-") and text[2:3] not in ("-", "!"):
            number = _block_comment(lines, number - 1, len(line) - len(text))
            continue
        if text.startswith(HEADER_WORDS):
            match = PLAIN_IMPORT.fullmatch(line)
            if match is None or "\r" in line:
                raise HeaderError(number, "not a plain `import A.B.C` line")
            if match[1] in KEYWORD_NAMES:
                raise HeaderError(number, f"`{match[1]}` is a header keyword, not a module")
            found.append(match[1])
            continue
        break  # the first command: Lean's header has ended
    return found


def _block_comment(lines: list[str], first: int, column: int) -> int:
    """Check the block comment opening at lines[first][column]; return the next line's index."""
    text = "\n".join(lines[first:])
    start = column
    close = text.find("-/", start + 2)
    if close < 0:
        raise HeaderError(first + 1, "unterminated block comment")
    if "/-" in text[start + 2:close + 2]:
        raise HeaderError(first + 1 + text.count("\n", start, text.index("/-", start + 2)),
                          "`/-` inside a block comment")
    last = first + text.count("\n", 0, close)
    rest = text[close + 2:].split("\n", 1)[0]
    if rest.strip(" "):
        raise HeaderError(last + 1, "text after the closing `-/` of a block comment")
    if "\r" in text[start:close]:
        raise HeaderError(first + 1, "carriage return in a header comment")
    return last + 1


def pinned_lean(toolchain: str) -> list[str] | None:
    """The command that runs the pinned toolchain's `lean`, or None if it is not installed.

    Never installs anything: elan's `lean +TOOLCHAIN` would download a missing
    toolchain, so it is used only for one `elan toolchain list` shows, and
    only to find that toolchain's own binary (a timeout then kills `lean`
    itself, not elan's proxy).
    """
    toolchain = toolchain.strip()
    try:
        elan = shutil.which("elan")
        if elan is not None:
            listed = subprocess.run([elan, "toolchain", "list"], capture_output=True, text=True,
                                    timeout=2, check=False).stdout
            proxy = Path(elan).with_name("lean")
            if toolchain not in {line.split()[0] for line in listed.splitlines() if line.split()} \
                    or not proxy.exists():
                return None
            prefix = subprocess.run([str(proxy), f"+{toolchain}", "--print-prefix"], capture_output=True,
                                    text=True, timeout=2, check=False).stdout.strip()
            lean = Path(prefix) / "bin/lean"
            return [str(lean)] if prefix and lean.exists() else None
        lean = shutil.which("lean")
        version = toolchain.rpartition(":v")[2]
        if lean is not None and version and f"(version {version}," in subprocess.run(
                [lean, "--version"], capture_output=True, text=True, timeout=2, check=False).stdout:
            return [lean]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def lean_disagreements(lean: list[str], files: dict[str, tuple[Path, list[str]]],
                       budget: float = ORACLE_BUDGET) -> tuple[dict[str, str], int]:
    """Ask the pinned toolchain's own header parser (`lean --deps`) what each file imports.

    `files` maps a name to (a file holding the source, the imports `imports`
    read). Returns the files whose imports Lean reads differently, with a
    message, and how many files were confirmed or refuted within `budget`
    seconds; files left unchecked rely on the plain-layout grammar alone.
    """
    deadline = time.monotonic() + budget
    with tempfile.TemporaryDirectory(prefix="ve-lean-deps-") as folder:
        # `lean --deps` resolves each import to an .olean path under a search
        # root holding the module's top-level directory; it needs no .olean.
        root = Path(folder)
        for _, claimed in files.values():
            for module in claimed:
                (root / module.split(".")[0]).mkdir(exist_ok=True)
        env = {**os.environ, "LEAN_PATH": str(root)}

        def ask(item: tuple[str, tuple[Path, list[str]]]) -> tuple[str, str | None] | None:
            name, (path, claimed) = item
            left = deadline - time.monotonic()
            if left <= 0:
                return None
            try:
                result = subprocess.run([*lean, "--deps", str(path)], env=env, capture_output=True,
                                        text=True, timeout=left, check=False)
            except subprocess.TimeoutExpired:
                return None
            lines = result.stdout.splitlines()
            if result.returncode or not lines or Path(lines[0]).name != "Init.olean":
                problem = (result.stderr.strip().splitlines() or ["no output"])[0]
                return name, f"the pinned Lean cannot read this header (`lean --deps`: {problem})"
            library = Path(lines[0]).parent  # the implicit `import Init` comes first
            read = []
            for line in lines[1:]:
                path = Path(line)
                base = root if path.is_relative_to(root) else library
                read.append(".".join(path.relative_to(base).with_suffix("").parts)
                            if path.suffix == ".olean" and path.is_relative_to(base) else line)
            if read != claimed:
                return name, f"the pinned Lean reads imports {read}, not {claimed}"
            return name, None

        with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as pool:
            answers = [answer for answer in pool.map(ask, files.items()) if answer is not None]
    return {name: message for name, message in answers if message is not None}, len(answers)


def main() -> int:
    paths = {".".join(path.relative_to(ROOT / "lean").with_suffix("").parts): path
             for path in (ROOT / "lean").rglob("*.lean") if ".lake" not in path.parts}
    unmapped = sorted(module for module in paths if lean_layer(module) is None)
    edges = set()
    unknown = set()
    headers = []
    read = {}
    for importer, path in paths.items():
        try:
            read[importer] = imports(path.read_text())
        except HeaderError as error:
            headers.append(f"{path.relative_to(ROOT)}: {error}")
    toolchain = ROOT / "lean/lean-toolchain"
    lean = pinned_lean(toolchain.read_text()) if toolchain.exists() else None
    if lean is not None:
        wrong, _ = lean_disagreements(lean, {importer: (paths[importer], found)
                                             for importer, found in read.items()}, budget=60)
        headers.extend(f"{paths[importer].relative_to(ROOT)}: {message}; {PLAIN_LAYOUT}"
                       for importer, message in sorted(wrong.items()))
    diagnostic = sorted(message for importer, found in read.items() for imported in found
                        if (message := diagnostic_only_violation(importer, imported)) is not None)
    for importer, found in read.items():
        for imported in found:
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
    for message in (f"Lean header not in the plain layout: {x}" for x in sorted(headers)):
        print(message, file=sys.stderr)
    for message in (f"missing local Lean import: {x}" for x in sorted(unknown)):
        print(message, file=sys.stderr)
    for message in diagnostic:
        print(f"diagnostic-only Lean import: {message}", file=sys.stderr)
    for edge in sorted(edges - expected.keys()):
        print(f"new outward Lean import: {edge}", file=sys.stderr)
    for edge in sorted(expected.keys() - edges):
        print(f"stale Lean exception: {edge}", file=sys.stderr)
    if unmapped or headers or unknown or diagnostic or edges != expected.keys():
        return 1
    print(f"Lean layer graph kept ({len(paths)} modules, {len(edges)} reviewed legacy edges)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
