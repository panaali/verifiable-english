"""Measure the numbers of the architecture map (`docs/ARCHITECTURE.md`) on one commit and render its tables.

The map's sizes, counts and trust classes are not typed by hand: this tool reads the tree of a commit from git
(`git ls-tree`, `git cat-file`), so uncommitted files never enter a number, and saves what it measured with the
commit's id in `docs/architecture/numbers.json`. The tables between the `<!-- numbers:NAME -->` and
`<!-- /numbers:NAME -->` markers of the map are rendered from that file and nothing else.

Every number comes from a file or a parser, never from a regular expression over source text: line counts are
newline counts of the committed blobs, the service's modes are the `MODES` tuple of
`ve/backends/service_schema.py` read with Python's `ast`, the Lean executables and Rust crates come from
`lean/lakefile.toml` and `rust/Cargo.toml` read with `tomllib`, and the trust classes, decoder total, layer
exceptions and collected test IDs are read from their JSON files.

Usage:
  ``python tools/architecture_numbers.py --write [--rev REV]``  measure REV (default `HEAD`), save the JSON and
                                                               re-render the map's tables;
  ``python tools/architecture_numbers.py --check``             render from the saved JSON and fail (exit 1) when a
                                                               table in the map differs; no measurement.
"""
from __future__ import annotations

import argparse
import ast
from fnmatch import fnmatchcase
import json
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DOC = Path("docs/ARCHITECTURE.md")
NUMBERS = Path("docs/architecture/numbers.json")
MIB = 1024 * 1024

# Line totals: name -> the glob over committed paths it sums (`*` stays within a directory, `**/` spans them).
LINE_GLOBS = {
    "ve_python": "ve/**/*.py",
    "ve_backends_python": "ve/backends/**/*.py",
    "ve_backends_schema_json": "ve/backends/lean_service_schema/*.json",
    "lean": "lean/**/*.lean",
    "tools_python": "tools/**/*.py",
    "tests_python": "tests/**/*.py",
    "conformance_python": "conformance/**/*.py",
}
# Single files whose length the map quotes.
BACKEND_FILES = ("ve/backends/relay.py", "ve/backends/lean_service.py", "ve/backends/service_schema.py")
SERVICE_FILES = ("lean/VE/Service/Protocol.lean", "lean/VE/Service/Standalone.lean",
                 "lean/VE/Service/Document.lean", "lean/VE/Service/Family.lean")
INVENTORIES = tuple(f"lean/{name}.txt" for name in ("statements", "declarations", "axioms", "predicates"))
LINE_FILES = BACKEND_FILES + SERVICE_FILES + INVENTORIES
LARGEST_VE = 3
# The trust classes the map shows (`docs/trust-baseline.json` `totals`); `budget` is kept whole.
TRUST_TOTALS = ("K", "S", "D", "G", "C", "P", "T", "o", "D[V]", "D[R]", "D[I]", "G[V]", "G[R]", "G[I]", "trusted",
                "lines")
BYTE_PREFIXES = {"docs": "docs/", "docs_lean_first": "docs/lean-first/", "tracked": ""}


def matches(path: str, pattern: str) -> bool:
    """`fnmatch` with `**/` matching zero or more whole directories and `*` matching within one."""
    if "**/" in pattern:
        head, tail = pattern.split("**/", 1)
        if not path.startswith(head):
            return False
        rest = path[len(head):].split("/")
        return any(matches("/".join(rest[i:]), tail) for i in range(len(rest)))
    parts, pattern_parts = path.split("/"), pattern.split("/")
    return len(parts) == len(pattern_parts) and all(map(fnmatchcase, parts, pattern_parts))


def lines(data: bytes) -> int:
    return data.count(b"\n")


def modes(source: bytes) -> list[str]:
    """The literal `MODES` tuple of the client's schema module, read with Python's parser."""
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and [getattr(t, "id", None) for t in node.targets] == ["MODES"]:
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                break
            if isinstance(value, tuple) and value and all(isinstance(m, str) for m in value):
                return list(value)
            break
    raise ValueError("ve/backends/service_schema.py has no literal MODES tuple")


def measure(read, sizes: dict[str, int]) -> dict:
    """The map's numbers over one tree: `sizes` maps every committed path to its byte size, `read(path)` gives
    the committed bytes of one path."""
    paths = sorted(sizes)

    def glob_lines(pattern):
        found = [p for p in paths if matches(p, pattern)]
        if not found:
            raise ValueError(f"no committed file matches {pattern}")
        return sum(lines(read(p)) for p in found)

    def load(path):
        return json.loads(read(path))

    ve_files = sorted(((lines(read(p)), p) for p in paths if matches(p, "ve/**/*.py")), key=lambda x: (-x[0], x[1]))
    tests = [p for p in paths if matches(p, "tests/**/*.py")]
    crates = tomllib.loads(read("rust/Cargo.toml").decode())["workspace"]["members"]
    trust = load("docs/trust-baseline.json")
    return {
        "lines": {name: glob_lines(pattern) for name, pattern in LINE_GLOBS.items()},
        "file_lines": {path: lines(read(path)) for path in LINE_FILES},
        "largest_ve_python": [{"path": p, "lines": n} for n, p in ve_files[:LARGEST_VE]],
        "rust_lines": {crate: glob_lines(f"rust/{crate}/src/**/*.rs") for crate in sorted(crates)},
        "files": {
            "lean_ve_modules": sum(matches(p, "lean/VE/**/*.lean") for p in paths),
            "response_shape_lean": sum(p.startswith("lean/ResponseShape") and p.endswith(".lean")
                                       or p == "lean/ResponseDecode.lean" for p in paths),
            "tests_test_modules": sum(p.rsplit("/", 1)[-1].startswith("test_") for p in tests),
            "tests_other_modules": sum(not p.rsplit("/", 1)[-1].startswith("test_") for p in tests),
        },
        "mib": {name: round(sum(s for p, s in sizes.items() if p.startswith(prefix)) / MIB)
                for name, prefix in BYTE_PREFIXES.items()},
        "counts": {
            "service_modes": len(modes(read("ve/backends/service_schema.py"))),
            "lean_executables": len(tomllib.loads(read("lean/lakefile.toml").decode())["lean_exe"]),
            "runtime_dependencies": len(tomllib.loads(read("pyproject.toml").decode())["project"]["dependencies"]),
            "python_layer_exceptions": len(load("tools/layer-exceptions.json")),
            "lean_layer_exceptions": len(load("tools/lean-layer-exceptions.json")),
            "collected_test_ids": len(load("tools/gate-collection.json")),
            "pinned_decoder_lines": load("ve/assurance-manifest.json")["lean_decoders"]["total_lines"],
        },
        "trust": {"totals": {k: trust["totals"][k] for k in TRUST_TOTALS}, "budget": trust["budget"]},
    }


def git(*args: str, data: bytes | None = None) -> bytes:
    return subprocess.run(["git", "-C", str(ROOT), *args], input=data, capture_output=True, check=True).stdout


def read_tree(rev: str):
    """The committed sizes of `rev` and a reader of its blobs."""
    commit = git("rev-parse", "--verify", f"{rev}^{{commit}}").decode().strip()
    sizes, blobs = {}, {}
    for line in git("ls-tree", "-r", "-l", "-z", commit).split(b"\0"):
        if not line:
            continue
        meta, path = line.split(b"\t", 1)
        mode, kind, blob, size = meta.split()
        if kind == b"blob":
            sizes[path.decode()] = int(size)
            blobs[path.decode()] = blob.decode()
    cache = {}

    def read(path):
        if path not in cache:
            cache[path] = git("cat-file", "blob", blobs[path])
        return cache[path]
    return commit, sizes, read


def number(value: int) -> str:
    return f"{value:,}"


def render(saved: dict) -> dict[str, str]:
    """The map's tables, by marker name, from the saved numbers."""
    n = saved["numbers"]
    lines_, files, f, counts, mib = n["lines"], n["file_lines"], n["files"], n["counts"], n["mib"]
    largest = ", ".join(f"`{Path(x['path']).name}` {number(x['lines'])}" for x in n["largest_ve_python"])
    service = ", ".join(f"{Path(p).stem} {number(files[p])}" for p in SERVICE_FILES)
    inventories = " + ".join(number(files[p]) for p in INVENTORIES)
    rust = " + ".join(f"{number(v)} (`{k}`)" for k, v in n["rust_lines"].items())
    sizes = [
        ("Python `ve/`", "`ve/**/*.py`", f"{number(lines_['ve_python'])} lines", f"largest: {largest}"),
        ("Python relay and transport", "`ve/backends/`", f"{number(lines_['ve_backends_python'])} lines",
         f"plus {number(lines_['ve_backends_schema_json'])} lines of generated JSON schemas; "
         + ", ".join(f"`{Path(p).name}` {number(files[p])}" for p in BACKEND_FILES)),
        ("Lean", "`lean/**/*.lean`", f"{number(lines_['lean'])} lines",
         f"{number(f['lean_ve_modules'])} modules under `lean/VE/`; service modules: {service}"),
        ("Response shapes", "`lean/ResponseShape*`, `lean/ResponseDecode.lean`",
         f"{number(f['response_shape_lean'])} files", "schemas, encoders and their fit proofs"),
        ("Generated Lean inventories (committed)", "`lean/{statements,declarations,axioms,predicates}.txt`",
         f"{inventories} lines", "written by `tools/lean_statements.py` and `lean/audit.py`"),
        ("Rust", "`rust/*/src/**/*.rs`", f"{number(sum(n['rust_lines'].values()))} lines", rust),
        ("Tools", "`tools/**/*.py`", f"{number(lines_['tools_python'])} lines", "gate, selection, A/B, fuzz, "
         "trust map, layer checkers"),
        ("Tests", "`tests/**/*.py`", f"{number(lines_['tests_python'])} lines",
         f"{number(f['tests_test_modules'])} test modules, {number(f['tests_other_modules'])} other modules; "
         f"{number(counts['collected_test_ids'])} collected test IDs (`tools/gate-collection.json`); "
         f"{number(lines_['conformance_python'])} lines of Python in `conformance/`"),
        ("Committed files", "the whole tree", f"{number(mib['tracked'])} MiB",
         f"`docs/` {number(mib['docs'])} MiB, of which `docs/lean-first/` {number(mib['docs_lean_first'])} MiB"),
    ]
    count_rows = [
        ("Lean service modes", "`MODES` in `ve/backends/service_schema.py`", counts["service_modes"]),
        ("Lean executables", "`[[lean_exe]]` in `lean/lakefile.toml`", counts["lean_executables"]),
        ("Python runtime dependencies", "`[project] dependencies` in `pyproject.toml`",
         counts["runtime_dependencies"]),
        ("Python layer exceptions", "`tools/layer-exceptions.json`", counts["python_layer_exceptions"]),
        ("Lean layer exceptions", "`tools/lean-layer-exceptions.json`", counts["lean_layer_exceptions"]),
        ("Pinned Lean decoder lines", "`lean_decoders.total_lines` in `ve/assurance-manifest.json`",
         counts["pinned_decoder_lines"]),
    ]
    t, budget = n["trust"]["totals"], n["trust"]["budget"]
    trust_rows = [
        ("K", "kernel definitions read once", number(t["K"])),
        ("S", "reviewed statements and meaning predicates", number(t["S"])),
        ("D", f"decoders (D[V] verdict-bearing {number(t['D[V]'])}, D[R] reject-only {number(t['D[R]'])}, "
              f"D[I] identity {number(t['D[I]'])})", number(t["D"])),
        ("G", f"glue (G[V] {number(t['G[V]'])}, G[R] {number(t['G[R]'])}, G[I] {number(t['G[I]'])})",
         number(t["G"])),
        ("C, P, T, o", "checkers, proofs, tests, other: not trusted",
         " / ".join(number(t[k]) for k in ("C", "P", "T", "o"))),
        ("**trusted**", f"K + S + untied [V] (budget {number(budget['K'])} + {number(budget['S'])} + "
                        f"{number(budget['V'])})", f"**{number(t['trusted'])} of {number(t['lines'])}**"),
    ]
    return {
        "measured": f"Measured on commit `{saved['commit']}` by `tools/architecture_numbers.py`; "
                    f"saved in `{NUMBERS}`.",
        "sizes": table(("Part", "Where", "Size", "Notes"), sizes),
        "counts": table(("Count", "Source", "Value"), [(a, b, number(c)) for a, b, c in count_rows]),
        "trust": table(("Class", "Meaning (consolidation plan 1.1)", "Lines"), trust_rows),
    }


def table(header, rows) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---:" if h in ("Size", "Value", "Lines") else "---"
                                                           for h in header) + "|"]
    out += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(out)


def blocks(text: str) -> dict[str, str]:
    """The text between each `<!-- numbers:NAME -->` and `<!-- /numbers:NAME -->` pair."""
    found = {}
    for part in text.split("<!-- numbers:")[1:]:
        name, rest = part.split(" -->", 1)
        end = f"<!-- /numbers:{name} -->"
        if end not in rest or name in found:
            raise ValueError(f"marker numbers:{name} is unclosed or repeated")
        found[name] = rest.split(end, 1)[0].strip("\n")
    return found


def apply(text: str, rendered: dict[str, str]) -> str:
    if set(blocks(text)) != set(rendered):
        raise ValueError(f"the map's markers {sorted(blocks(text))} are not {sorted(rendered)}")
    for name, body in rendered.items():
        start, end = f"<!-- numbers:{name} -->", f"<!-- /numbers:{name} -->"
        head, rest = text.split(start, 1)
        text = f"{head}{start}\n{body}\n{end}{rest.split(end, 1)[1]}"
    return text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--rev", default="HEAD")
    args = parser.parse_args(argv)
    doc, saved_path = ROOT / DOC, ROOT / NUMBERS
    if args.write:
        commit, sizes, read = read_tree(args.rev)
        saved = {"commit": commit, "numbers": measure(read, sizes)}
        saved_path.parent.mkdir(parents=True, exist_ok=True)
        saved_path.write_text(json.dumps(saved, indent=2, sort_keys=True) + "\n")
        doc.write_text(apply(doc.read_text(), render(saved)))
        return 0
    text = doc.read_text()
    expected = apply(text, render(json.loads(saved_path.read_text())))
    if expected != text:
        print(f"{DOC}: a numbers table differs from {NUMBERS}; run tools/architecture_numbers.py --write",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
