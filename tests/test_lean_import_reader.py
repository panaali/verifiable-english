"""tools/check_lean_imports.imports accepts only plain headers, and reads those as Lean does.

The reader does not re-implement Lean's header parser. It accepts a strict
line-based layout and raises HeaderError for anything else. The oracle is the
pinned toolchain itself: tools/lean_header_imports.lean runs
`Lean.Parser.parseHeader` over each case, and whenever the reader accepts a
header, Lean must parse it without error and read the same module list.
`lean --deps`, which the hook and tools/check_lean_imports.py use as a second
opinion, is checked here to refute a wrong reading.
"""
from __future__ import annotations

import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_lean_imports import HeaderError, imports, lean_disagreements, pinned_lean  # noqa: E402

REJECT = "reject"
# precommit-loop.final.md B: Lean reads VE.Surface after the comment `/-/-/`.
STACKED = ["/-/-/import VE.Surface\n", "import VE.Core.Bridge /-/-/import VE.Surface\n"]
# (source, the imports the reader returns, or REJECT)
CASES = [
    *((source, REJECT) for source in STACKED),
    # Plain headers.
    ("", []),
    ("import VE.Core.Bridge\nimport VE.Surface\n\nnamespace VE\nend VE\n", ["VE.Core.Bridge", "VE.Surface"]),
    ("-- c\n\nimport VE.Surface\n", ["VE.Surface"]),
    ("  -- indented c /- -/\nimport VE.Surface\n", ["VE.Surface"]),
    ("/- c -/\nimport VE.Surface\n", ["VE.Surface"]),
    ("/- multi\n  line\n-/\nimport VE.Core.Bridge\n/- between -/\nimport VE.Surface\n",
     ["VE.Core.Bridge", "VE.Surface"]),
    ("  /- indented -/  \nimport VE.Surface\n", ["VE.Surface"]),
    ("/- --/\nimport VE.Surface\n", ["VE.Surface"]),  # `-/` closes the comment even after `-`
    ("/-\nx -/\nimport VE.Surface\n", ["VE.Surface"]),
    ("/- a -/\n/- b -/\nimport VE.Surface\n", ["VE.Surface"]),
    ("import VE.Core.Bridge\r\nimport VE.Surface\r\n", ["VE.Core.Bridge", "VE.Surface"]),
    ("import VE.Surface   \n", ["VE.Surface"]),
    ("import VE.Surface", ["VE.Surface"]),
    ("import VE.Surface.all\n", ["VE.Surface.all"]),
    ("import Lean.Data.Json\nimport Std\n", ["Lean.Data.Json", "Std"]),
    ("import x'\n", ["x'"]),
    ("import VE.Surface\n«", ["VE.Surface"]),
    # The header ends at the first command; nothing after it is an import.
    ("import VE.Core.Bridge\ndef x := 1\nimport VE.Surface\n", ["VE.Core.Bridge"]),
    ("import VE.Core.Bridge\n/-- doc -/\ndef x := 1\n", ["VE.Core.Bridge"]),
    ("import VE.Core.Bridge\n\n/-! module doc -/\n", ["VE.Core.Bridge"]),
    ("/-! module doc -/\nimport VE.Surface\n", []),
    ("/-- doc -/ import VE.Surface\n", []),
    ("-/\nimport VE.Surface\n", []),
    ('def s := "import VE.Surface"\n', []),
    ("def «an import VE.Surface» := 1\n", []),
    ("import VE.Core.Bridge\ndef «an import VE.Surface» := 1\n", ["VE.Core.Bridge"]),
    ("import VE.Core.Bridge\n\nnamespace «import VE.Surface»\nend «import VE.Surface»\n", ["VE.Core.Bridge"]),
    ("def x := Foo.import\nimportant VE.Surface\n", []),
    ("theorem t : True := by\n  trivial\n-- import VE.Surface\n", []),
    # Nested, stacked or overlapping comment delimiters, and text after `-/`.
    ("/-/-/\nimport VE.Surface\n", REJECT),
    ("/- a /-/\nimport VE.Surface\n", REJECT),
    ("/- c /- nested -/ -/\nimport VE.Surface\n", REJECT),
    ("/- c /- nested -/ -/ import VE.Surface\n", REJECT),
    ("/- a -//- b -/import VE.Surface\n", REJECT),
    ("/- c -/ import VE.Surface\n", REJECT),
    ("/- c -/ -- c\nimport VE.Surface\n", REJECT),
    ("/- a\n-/ import VE.Surface\n", REJECT),
    ("/- unterminated\nimport VE.Surface\n", REJECT),
    ("import VE.Surface /- unterminated\n", REJECT),
    # Imports sharing a line, spanning lines, or in another form.
    ("import VE.Core.Bridge import VE.Surface\n", REJECT),
    ("import VE.Core.Bridge import«VE».Surface\n", REJECT),
    ("import VE.Core.Bridge/- c -/import VE.Surface\n", REJECT),
    ("import VE.Surface -- c\n", REJECT),
    ("import VE.Surface /- c -/\n", REJECT),
    ("import\n  VE.Surface\n", REJECT),
    ("import --/ c\n  VE.Surface\n", REJECT),
    ("import /- c -/ VE.Surface\n", REJECT),
    ("  import VE.Surface\n", REJECT),
    ("prelude\nimport VE.Surface\n", REJECT),
    ("prelude import VE.Syntax import VE.Surface\n", REJECT),
    ("module\n\npublic import VE.Surface\n", REJECT),
    ("module\npublic section\n", REJECT),
    ("meta import VE.Surface\n", REJECT),
    ("import «VE».Surface\n", REJECT),
    ("import«VE».Surface\n", REJECT),
    ("import VE.«Surface».Run\n", REJECT),
    ("import «an import VE.Surface»\n", REJECT),
    ("import αβ.x₁\n", REJECT),
    ("import VE.Surface?\n", REJECT),
    ("import all\n", REJECT),
    ("import all VE.Surface\n", REJECT),
    ("import import VE.Surface\n", REJECT),
    ("import VE.Surface.\n", REJECT),
    ("importVE.Surface\n", REJECT),
    # Whitespace Lean rejects or might not read as whitespace.
    ("import\tVE.Surface\n", REJECT),
    ("\timport VE.Surface\n", REJECT),
    ("\t\nimport VE.Surface\n", REJECT),
    ("import VE.Core.Bridge\rimport VE.Surface\n", REJECT),
    ("-- c\rimport VE.Surface\n", REJECT),
    ("﻿import VE.Surface\n", REJECT),
    (" import VE.Surface\n", REJECT),
]
# Legitimate headers from the repository, verbatim.
TREE = sorted(path for path in (ROOT / "lean").rglob("*.lean") if ".lake" not in path.parts)


def fuzz_cases(count: int = 600) -> list[str]:
    """Random headers: mostly whole lines, sometimes pieces glued inside a line."""
    lines = ["import VE.Surface", "import VE.Core.Bridge", "import Std", "import VE.Surface  ", "", " ",
             "-- c", "  -- /- c", "/- c -/", "/- a", "b -/", "-/", "/- --/", "/-/-/", "/- /- n -/ -/",
             "/-! d -/", "/-- d -/", "def x := 1", "prelude", "module", "public import VE.Surface",
             "import «VE».Surface", "import", "  VE.Surface", "\t", "\r", "«", "import VE.Surface -- c"]
    glue = ["import", "VE.Surface", " ", "/-", "-/", "/", "-", "--", "!", "\n", "«", "»", "\r"]
    generator = random.Random(20260929)
    cases = []
    for _ in range(count):
        chosen = [generator.choice(lines) for _ in range(generator.randint(1, 8))]
        for _ in range(generator.choice([0, 0, 1, 2])):
            spot = generator.randrange(len(chosen))
            at = generator.randint(0, len(chosen[spot]))
            chosen[spot] = chosen[spot][:at] + generator.choice(glue) + chosen[spot][at:]
        cases.append("\n".join(chosen) + generator.choice(["", "\n"]))
    return cases


def read(source: str) -> list[str] | str:
    try:
        return imports(source)
    except HeaderError:
        return REJECT


@pytest.fixture(scope="module")
def lean_reads(tmp_path_factory):
    """Lean's own reading of every case: its module list, or None where it reports an error."""
    lean = shutil.which("lean")
    assert lean is not None, "lean is required for the complete test suite"
    folder = tmp_path_factory.mktemp("headers")
    sources = [source for source, _ in CASES] + fuzz_cases() + [path.read_text() for path in TREE]
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


def test_stacked_comment_delimiters_are_rejected(lean_reads):
    # Lean reads the import these headers hide; the reader must not read [] or one import.
    for source, reason in zip(STACKED, ["`/-` inside a block comment", "not a plain `import A.B.C` line"]):
        assert "VE.Surface" in lean_reads[source], repr(source)
        with pytest.raises(HeaderError, match=f"^line 1: {reason}; write the header in the plain layout"):
            imports(source)


def test_listed_headers_are_rejected_or_read_as_lean_reads_them(lean_reads):
    for source, expected in CASES:
        assert read(source) == expected, repr(source)
        if expected is not REJECT:
            assert lean_reads[source] == expected, repr(source)  # Lean parses it without error


def test_header_errors_name_the_line_and_the_plain_layout():
    with pytest.raises(HeaderError) as caught:
        imports("-- c\n\nimport VE.Core.Bridge\n/- a -/\n/- b -//-/-/import VE.Surface\n")
    assert caught.value.line == 5
    assert str(caught.value).startswith("line 5: text after the closing `-/` of a block comment; "
                                        "write the header in the plain layout")
    with pytest.raises(HeaderError) as caught:
        imports("/- a\n\n b -/ import VE.Surface\n")
    assert caught.value.line == 3
    with pytest.raises(HeaderError, match="^line 3: `/-` inside a block comment") as caught:
        imports("-- c\n/- a\n b /-/\nimport VE.Surface\n")


def test_random_headers_are_rejected_or_read_as_lean_reads_them(lean_reads):
    cases = fuzz_cases()
    accepted = [source for source in cases if read(source) is not REJECT]
    assert len(cases) // 5 < len(accepted) < len(cases) * 4 // 5  # both outcomes are exercised
    parsed = [source for source in accepted if lean_reads[source] is not None]
    assert len(parsed) > len(accepted) * 3 // 4
    assert sum(bool(lean_reads[source]) for source in parsed) >= 40
    for source in parsed:  # a header Lean reports an error in never compiles, so it adds no edge
        assert lean_reads[source] == imports(source), repr(source)


def test_every_tree_module_is_plain_and_read_as_lean_reads_it(lean_reads):
    assert len(TREE) > 100
    for path in TREE:
        source = path.read_text()
        assert lean_reads[source] is not None, path
        assert imports(source) == lean_reads[source], path


@pytest.fixture(scope="module")
def lean_command():
    command = pinned_lean((ROOT / "lean/lean-toolchain").read_text())
    assert command is not None, "the pinned Lean toolchain is required for the complete test suite"
    return command


def test_pinned_lean_is_the_toolchain_binary_not_a_proxy(lean_command):
    # A timeout must kill `lean` itself; killing elan's proxy could leave it holding the pipes.
    assert len(lean_command) == 1
    elan = shutil.which("elan")
    if elan is not None:
        assert Path(lean_command[0]).resolve() != Path(elan).resolve()
    version = (ROOT / "lean/lean-toolchain").read_text().strip().rpartition(":v")[2]
    assert f"(version {version}," in subprocess.run([*lean_command, "--version"], capture_output=True,
                                                    text=True, check=True).stdout


def test_pinned_lean_never_installs_a_toolchain():
    started = time.monotonic()
    assert pinned_lean("leanprover/lean4:v0.0.1-not-installed") is None
    assert pinned_lean("") is None
    assert time.monotonic() - started < 5


def test_lean_deps_confirms_every_accepted_header(lean_command, tmp_path):
    files = {}
    for number, source in enumerate([source for source, expected in CASES if expected is not REJECT]):
        files[source] = (tmp_path / f"case{number}.lean", imports(source))
        files[source][0].write_bytes(source.encode())
    for path in TREE:
        files[str(path)] = (path, imports(path.read_text()))
    wrong, checked = lean_disagreements(lean_command, files, budget=120)
    assert wrong == {}
    assert checked == len(files)


def test_lean_deps_refutes_a_wrong_reading(lean_command, tmp_path):
    # What the reader of 59029c86 returned for the stacked-delimiter examples.
    claims = {STACKED[0]: [], STACKED[1]: ["VE.Core.Bridge"],
              "import VE.Surface /- unterminated\n": ["VE.Surface"]}
    files = {}
    for number, (source, claimed) in enumerate(claims.items()):
        files[source] = (tmp_path / f"case{number}.lean", claimed)
        files[source][0].write_bytes(source.encode())
    wrong, checked = lean_disagreements(lean_command, files, budget=120)
    assert checked == 3
    assert wrong[STACKED[0]] == "the pinned Lean reads imports ['VE.Surface'], not []"
    assert wrong[STACKED[1]] == ("the pinned Lean reads imports ['VE.Core.Bridge', 'VE.Surface'], "
                                 "not ['VE.Core.Bridge']")
    assert wrong["import VE.Surface /- unterminated\n"].startswith("the pinned Lean cannot read this header")


def test_lean_deps_budget_leaves_files_to_the_grammar(lean_command, tmp_path):
    (tmp_path / "a.lean").write_text("import VE.Surface\n")
    wrong, checked = lean_disagreements(lean_command, {"a": (tmp_path / "a.lean", [])}, budget=0)
    assert (wrong, checked) == ({}, 0)
