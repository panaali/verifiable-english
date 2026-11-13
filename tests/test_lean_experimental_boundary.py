"""The experimental tier's import boundary (docs/spec/kernel-boundary.md section 5, KB-1).

`tools/check_lean_imports.py` fails when a module that `VE.Service.Protocol` or `Serve` imports, directly or
transitively, imports a `VE.Experimental.*` module, and when a module under `lean/VE/Experimental/` has no line
`Expires: YYYY-MM-DD` in its first docstring (the first command after the import header: nothing but `import` lines
and comments before it) or that date has passed. No such module exists on main, so both rules are tested on trees
under `tmp_path`, with an injected date.
"""
from __future__ import annotations

import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from check_lean_imports import (expiry_problems, experimental_imports, first_docstring, header, imports,  # noqa: E402
                                lean_modules)

TODAY = date(2026, 11, 12)
EXPERIMENT = '/-! A trial design.\n\nExpires: {expires}\n-/\nnamespace VE.Experimental.Trial\nend VE.Experimental.Trial\n'
MISSING = ["VE.Experimental.Trial: an experimental module's first docstring, before any code but `import` lines and"
           " comments, needs one line `Expires: YYYY-MM-DD`"]
EXPIRED = ["VE.Experimental.Trial: expired on 2000-01-01; promote it to the shell or delete it"]


def tree(root: Path, files: dict[str, str]) -> tuple[dict[str, Path], dict[str, list[str]]]:
    for name, text in files.items():
        (root / "lean" / name).parent.mkdir(parents=True, exist_ok=True)
        (root / "lean" / name).write_text(text)
    paths = lean_modules(root)
    return paths, {module: imports(path.read_text()) for module, path in paths.items()}


def service(extra: str = "") -> dict[str, str]:
    """A service whose Protocol reaches VE.Route.Run through VE.Service.Modes; Serve imports the Protocol."""
    return {"Serve.lean": "import VE.Service.Protocol\n",
            "VE/Service/Protocol.lean": "import VE.Service.Modes\n",
            "VE/Service/Modes.lean": "import VE.Route.Run\n",
            "VE/Route/Run.lean": extra,
            "VE/Experimental/Trial.lean": EXPERIMENT.format(expires="2026-12-31"),
            "VE/Experimental/Uses.lean": "import VE.Route.Run\nimport VE.Experimental.Trial\n"
                                         + EXPERIMENT.format(expires="2026-12-31")}


def test_a_module_the_service_reaches_may_not_import_an_experimental_one(tmp_path):
    _, read = tree(tmp_path / "clean", service())
    assert experimental_imports(read) == []  # an experimental module may import the shell, and another experiment
    _, read = tree(tmp_path / "transitive", service("import VE.Experimental.Trial\n"))
    [problem] = experimental_imports(read)
    assert problem.startswith("VE.Route.Run -> VE.Experimental.Trial: the service (VE.Service.Protocol, Serve) "
                              "reaches VE.Route.Run")
    files = dict(service(), **{"Serve.lean": "import VE.Service.Protocol\nimport VE.Experimental.Trial\n"})
    _, read = tree(tmp_path / "serve", files)
    assert [p.split(":")[0] for p in experimental_imports(read)] == ["Serve -> VE.Experimental.Trial"]
    files = dict(service(), **{"VE/Service/Protocol.lean": "import VE.Service.Modes\nimport VE.Experimental\n",
                               "VE/Experimental.lean": EXPERIMENT.format(expires="2026-12-31")})
    _, read = tree(tmp_path / "bare", files)
    assert [p.split(":")[0] for p in experimental_imports(read)] == ["VE.Service.Protocol -> VE.Experimental"]
    # A name that only begins like the prefix is not experimental.
    files = dict(service("import VE.ExperimentalNotes\n"), **{"VE/ExperimentalNotes.lean": ""})
    _, read = tree(tmp_path / "prefix", files)
    assert experimental_imports(read) == []


def test_the_rule_fails_closed_without_a_service_root(tmp_path):
    files = service()
    del files["Serve.lean"]
    _, read = tree(tmp_path, files)
    assert experimental_imports(read) == ["service root Serve is not in the tree"]
    assert experimental_imports(read, require_roots=False) == []  # a layer test's tree: no lakefile, no service
    files["VE/Service/Protocol.lean"] = "import VE.Experimental.Trial\n"
    _, read = tree(tmp_path / "protocol only", files)
    assert [p.split(":")[0] for p in experimental_imports(read, require_roots=False)] == [
        "VE.Service.Protocol -> VE.Experimental.Trial"]


def test_the_repository_service_reaches_no_experimental_module():
    paths = lean_modules(ROOT)
    read = {module: imports(path.read_text()) for module, path in paths.items()}
    assert experimental_imports(read) == [] and expiry_problems(paths, date.today()) == []


def test_an_experimental_module_carries_an_expiry_date_not_yet_passed(tmp_path):
    def problems(text: str, today: date = TODAY) -> list[str]:
        root = tmp_path / str(len(list(tmp_path.iterdir())))
        paths, _ = tree(root, {"VE/Experimental/Trial.lean": text, "VE/Shell.lean": "/-! No date here. -/\n"})
        return expiry_problems(paths, today)

    missing = MISSING
    assert problems(EXPERIMENT.format(expires="2026-11-12")) == []  # expires today: not yet passed
    assert problems(EXPERIMENT.format(expires="2026-11-11")) == [
        "VE.Experimental.Trial: expired on 2026-11-11; promote it to the shell or delete it"]
    assert problems(EXPERIMENT.format(expires="2026-12-31"), today=date(2027, 1, 1)) != []  # an injected later clock
    assert problems(EXPERIMENT.format(expires="2026-02-30")) == ["VE.Experimental.Trial: Expires: 2026-02-30 is not a date"]
    assert problems("namespace VE.Experimental.Trial\nend VE.Experimental.Trial\n") == missing
    assert problems("/-! A trial design. -/\n/-- Expires: 2026-12-31 -/\ndef x := 1\n") == missing  # not the first
    assert problems("/-! A trial design. Expires: 2026-12-31 -/\n") == missing  # not a line of its own
    assert problems(EXPERIMENT.format(expires="2026-12-31") + "/-- Expires: 2027-01-01 -/\ndef x := 1\n") == []
    assert problems("/-! Trial.\nExpires: 2026-12-31\nExpires: 2027-12-31\n-/\n") == missing  # one date, not two


def problems_of(text: str) -> list[str]:
    return expiry_problems({"VE.Experimental.Trial": Fake(text)}, TODAY)


def test_the_expiry_rule_reads_the_first_actual_doc_comment_not_text_inside_strings_or_comments():
    """kb-1 review F3 and F4: the docstring is the first command after the import header; the reader never lexes
    code. Behind comments and imports (header text) the actual docstring is read, never a decoy in a `--` comment.
    Behind any code (a string, a raw string, a character literal, an escaped quote, an interpolation, a character
    literal after a bracket, a «» name, a primed name), the module is refused whatever its docstring says, so a future
    date hidden there never passes. A header outside the plain layout and an unclosed comment are refused too."""
    for opener in ("/--", "/-!"):
        decoy = opener + "\nExpires: 2099-01-01\n-/"
        actual = opener + " Trial.\nExpires: 2000-01-01\n-/\n"
        future = actual.replace("2000-01-01", "2026-12-31")
        for hide in ("-- " + decoy.replace("\n", " ") + "\n", "import A.B\n-- " + decoy.replace("\n", " ") + "\n",
                     "/- A plain comment. -/\nimport A.B\n"):
            assert problems_of(hide + actual + "def x := 1\n") == EXPIRED, hide
            assert problems_of(hide + "def x := 1\n") == MISSING, hide
            assert problems_of(hide + future) == [], hide
        for hide in ('def t : String := "' + decoy + '"\n', 'def t : String := r#"' + decoy + '"#\n',
                     "def t := '\"'\ndef u : String := \"" + decoy + '"\n',
                     'def t : String := "\\"" ++ "' + decoy + '"\n',
                     'def t : String := s!"{"' + decoy.replace("\n", "\\n") + '"}"\n',  # F4: an interpolation
                     'def t : String := s!"{"' + decoy + '"}"\n',
                     "def t : Char × String := ⟨'\"', \"" + decoy + '"⟩\n',  # F4: a character literal after ⟨
                     "def «t" + decoy + "» := 1\n", "def h' := 1\n",
                     "/- outer /- inner -/\n" + decoy + "\n-/\n",  # a nested comment: outside the plain layout
                     "import A.B -- " + decoy.replace("\n", " ") + "\n"):  # an import sharing its line
            assert problems_of(hide + actual + "def x := 1\n") == MISSING, hide
            assert problems_of(hide + future) == MISSING, hide
    assert problems_of('def t : String := "/-! Expires: 2099-01-01 -/\n') == MISSING  # an unclosed string
    assert problems_of("/-! Trial.\nExpires: 2099-01-01\n") == MISSING  # an unclosed docstring
    assert problems_of("import A.B\n\n  /-! Trial.\nExpires: 2026-12-31\n-/\n") == []  # after imports, indented


def test_the_review_f4_layouts_with_an_expired_docstring_are_refused():
    """kb-1 review F4 (its PROBE): a future date in a string inside an interpolation, or behind a character literal
    `'"'` after `⟨`, both in front of an expired `/-!` docstring (both compile with the pinned Lean v4.24.0)."""
    actual = "/-! Trial.\nExpires: 2000-01-01\n-/\ndef x := 1\n"
    decoy = '"/-!\nExpires: 2099-01-01\n-/"'
    for hide in ('def t : String := s!"{' + decoy + '}"\n', "def t : Char × String := ⟨'\"', " + decoy + "⟩\n"):
        assert problems_of(hide + actual) != [], hide


# Fragments of Lean text, code and header alike, that a lexer could misread; the fuzzer below strings them together.
FRAGMENTS = ['"', "'", "'\"'", 's!"{', "}", "⟨", "⟩", 'r#"', '"#', "«", "»", "--", "/-", "-/", "/--", "/-!", "\\", "\n",
             " ", "def t := ", "import A.B\n", "h'", "/-!\nExpires: 2099-01-01\n-/", "Expires: 2099-01-01"]


def test_a_module_passes_only_on_a_docstring_with_no_code_in_front_of_it():
    """kb-1 review F3/F4 as a class: whatever text comes before an expired actual docstring, the module passes only
    when the docstring it was judged by has nothing but a plain import header in front of it (`imports` reads that
    text through to its end, with no command left), so no string, character literal, interpolation or name in code
    can hide a future date. Seeded, so the same prefixes run every time."""
    rng = random.Random(20261113)
    actual = "\n/-! Trial.\nExpires: 2000-01-01\n-/\ndef x := 1\n"
    passed = 0
    for _ in range(3000):
        text = "".join(rng.choice(FRAGMENTS) for _ in range(rng.randint(1, 8))) + actual
        if problems_of(text) != []:
            continue
        passed += 1
        doc = first_docstring(text)
        at = text.find(doc) - 3
        assert at >= 0 and text[at:at + 3] in ("/--", "/-!"), text
        assert header(text[:at]) == (imports(text[:at]), ""), text  # a plain header, no command before the docstring
    assert passed > 0  # some prefixes are a future docstring of their own, which rightly passes


def test_a_plain_header_before_the_docstring_is_read_and_its_date_decides():
    """The other direction: any plain header (blank lines, `--` comments, plain block comments, imports) before the
    docstring is read through, so a future date passes and a past one is refused. A comment nested inside the
    docstring does not close it (Lean's comments nest), so a date after it is still the docstring's."""
    rng = random.Random(20261114)
    lines = ["", "-- a comment /-! Expires: 2099-01-01 -/", "/- a plain comment -/", "/- two\nlines -/",
             "import A.B", "import Mathlib.Data.List", "  -- indented"]
    for _ in range(500):
        prefix = "".join(rng.choice(lines) + "\n" for _ in range(rng.randint(0, 6)))
        for opener in ("/--", "/-!", "/-! Trial /- a nested -/ note.", "/-- Trial /- a /- deeper -/ nested -/ note."):
            assert problems_of(prefix + opener + " Trial.\nExpires: 2026-12-31\n-/\n") == [], prefix
            assert problems_of(prefix + opener + " Trial.\nExpires: 2000-01-01\n-/\n") == EXPIRED, prefix


class Fake:
    def __init__(self, text: str):
        self.text = text

    def read_text(self) -> str:
        return self.text

