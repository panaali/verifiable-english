"""tools/check_lean_imports.imports reads exactly the imports Lean's header parser reads.

The oracle is the pinned toolchain itself: tools/lean_header_imports.lean runs
`Lean.Parser.parseHeader` over each case. Whenever Lean parses a header without
error, the Python reader must return the same module list; a header Lean
rejects never compiles, so its imports cannot add an edge.
"""
from __future__ import annotations

import json
from pathlib import Path
import random
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_lean_imports import imports  # noqa: E402

# (source, what Lean's header parser reads, or None where it reports an error)
CASES = [
    # precommit-looprecheck1 B1: successive import commands on one line.
    ("import VE.Core.Bridge import«VE».Surface\n", ["VE.Core.Bridge", "VE.Surface"]),
    ("import VE.Core.Bridge import «VE».Surface\n", ["VE.Core.Bridge", "VE.Surface"]),
    ("import«VE».Core.Bridge import«VE».Surface\n", ["VE.Core.Bridge", "VE.Surface"]),
    ("import VE.Core.Bridge/- c -/import VE.Surface\n", ["VE.Core.Bridge", "VE.Surface"]),
    ("prelude import VE.Syntax import VE.Surface\n", ["VE.Syntax", "VE.Surface"]),
    # precommit-looprecheck1 B2: `import` inside a quoted name after the header.
    ("def «an import VE.Surface» := 1\n", []),
    ("import VE.Core.Bridge\ndef «an import VE.Surface» := 1\n", ["VE.Core.Bridge"]),
    ("import VE.Core.Bridge\n\nnamespace «import VE.Surface»\nend «import VE.Surface»\n", ["VE.Core.Bridge"]),
    ("import «an import VE.Surface»\n", ["an import VE.Surface"]),
    ("import VE.«Core import VE».Surface\n", ["VE.Core import VE.Surface"]),
    # Everything after the header is a command, even text shaped like an import.
    ("import VE.Core.Bridge\ndef x := 1\nimport VE.Surface\n", ["VE.Core.Bridge"]),
    ("import VE.Core.Bridge\n/-- doc -/\ndef x := 1\n", ["VE.Core.Bridge"]),
    ("/-! module doc -/\nimport VE.Surface\n", []),
    ("/-- doc -/ import VE.Surface\n", []),
    ('def s := "import VE.Surface"\n', []),
    ("def x := Foo.import\nimportant VE.Surface\n", []),
    ("theorem t : True := by\n  trivial\n-- import VE.Surface\n", []),
    # Forms of an import command.
    ("import\n  VE.Surface\n", ["VE.Surface"]),
    ("import\r\n  VE.Surface\r\n", ["VE.Surface"]),
    ("import /- c /- nested -/ -/ VE.Surface\n", ["VE.Surface"]),
    ("import --/ c\n  VE.Surface\n", ["VE.Surface"]),
    ("/- --/ import VE.Surface\n", ["VE.Surface"]),  # `-/` closes the comment even after `-`
    ("/- --/ -/ import VE.Surface\n", []),
    ("/- a -//- b -/import VE.Surface\n", ["VE.Surface"]),
    ("module\n\npublic import VE.Surface\n", ["VE.Surface"]),
    ("module\nprelude\nmeta import all VE.Surface\npublic meta import VE.Syntax\n", ["VE.Surface", "VE.Syntax"]),
    ("module\npublic section\n", []),
    ("import VE.Surface.all\n", ["VE.Surface.all"]),
    ("import VE.«Surface».Run\n", ["VE.Surface.Run"]),
    ("import VE.«Core.Bridge»\n", ["VE.Core.Bridge"]),
    ("import Lean.Data.Json\nimport Std\n", ["Lean.Data.Json", "Std"]),
    ("import αβ.x₁\n", ["αβ.x₁"]),
    ("", []),
    ("importVE.Surface\n", []),  # one identifier: the header is empty
    ("module\nmodule\nimport VE.Surface\n", []),
    ("import VE.Surface\n«", ["VE.Surface"]),
    # Headers Lean rejects (the file never compiles).
    ("import\tVE.Surface\n", None),
    ("import VE.Core.Bridge\rimport VE.Surface\n", None),
    ("import VE.Surface /- unterminated\n", None),
    ("import «VE.Surface\n", None),
    ("public import VE.Surface\n", None),
    ("import all VE.Surface\n", None),
    ("module\npublic import all VE.Surface\n", None),
    ("import import VE.Surface\n", None),
    ("import VE.Surface.\n", None),
]


def fuzz_cases(count: int = 400) -> list[str]:
    """Random headers built from the pieces the cases above combine."""
    pieces = ["import", "import", "import", "public", "meta", "all", "prelude", "module", "VE.Surface",
              "«VE».Surface", "VE.«Surface»", "«an import VE.Surface»", "VE.Core.Bridge", "def", ":=", "1",
              " ", " ", " ", "\n", "\r\n", "-- c\n", "/- c -/", "/- /- n -/ -/", "/-! d -/", "/-- d -/",
              '"import VE.X"', ".", "\t", "\r", "«", "»", "importVE", "Foo.import", "αβ", "x₁", "λ", "é", " ",
              "--/", "-/", "/-", "?", "'"]
    generator = random.Random(20260929)
    return ["".join(generator.choice(pieces) for _ in range(generator.randint(1, 12))) for _ in range(count)]


@pytest.fixture(scope="module")
def lean_reads(tmp_path_factory):
    lean = shutil.which("lean")
    assert lean is not None, "lean is required for the complete test suite"
    folder = tmp_path_factory.mktemp("headers")
    sources = [source for source, _ in CASES] + fuzz_cases()
    sources += [path.read_text() for path in sorted((ROOT / "lean").rglob("*.lean")) if ".lake" not in path.parts]
    files = []
    for number, source in enumerate(sources):
        files.append(folder / f"case{number}.lean")
        files[-1].write_bytes(source.encode())
    result = subprocess.run([lean, "--run", str(ROOT / "tools/lean_header_imports.lean"), *map(str, files)],
                            cwd=ROOT / "lean", capture_output=True, text=True, timeout=300, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    verdicts = [json.loads(line) for line in result.stdout.splitlines()]
    assert len(verdicts) == len(sources)
    return {source: None if verdict["error"] else verdict["imports"]
            for source, verdict in zip(sources, verdicts)}


def test_listed_headers_read_as_lean_reads_them(lean_reads):
    for source, expected in CASES:
        assert lean_reads[source] == expected, repr(source)  # each expectation is Lean's own reading
        if expected is not None:
            assert imports(source) == expected, repr(source)


def test_random_headers_read_as_lean_reads_them(lean_reads):
    cases = fuzz_cases()
    parsed = [source for source in cases if lean_reads[source] is not None]
    assert len(parsed) > len(cases) // 4  # the sample exercises accepted headers, not just errors
    assert any(lean_reads[source] for source in parsed)
    for source in parsed:
        assert imports(source) == lean_reads[source], repr(source)


def test_every_tree_module_reads_as_lean_reads_it(lean_reads):
    for path in sorted((ROOT / "lean").rglob("*.lean")):
        if ".lake" not in path.parts:
            source = path.read_text()
            assert lean_reads[source] is not None, path
            assert imports(source) == lean_reads[source], path
