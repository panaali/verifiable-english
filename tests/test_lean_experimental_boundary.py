"""The experimental tier's import boundary (docs/spec/kernel-boundary.md section 5, KB-1).

`tools/check_lean_imports.py` fails when a module that `VE.Service.Protocol` or `Serve` imports, directly or
transitively, imports a `VE.Experimental.*` module, and when a module under `lean/VE/Experimental/` has no line
`Expires: YYYY-MM-DD` in its first docstring or that date has passed. No such module exists on main, so both rules
are tested on trees under `tmp_path`, with an injected date.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from check_lean_imports import expiry_problems, experimental_imports, imports, lean_modules  # noqa: E402

TODAY = date(2026, 11, 12)
EXPERIMENT = '/-! A trial design.\n\nExpires: {expires}\n-/\nnamespace VE.Experimental.Trial\nend VE.Experimental.Trial\n'


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

    missing = ["VE.Experimental.Trial: an experimental module's first docstring needs one line `Expires: YYYY-MM-DD`"]
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


def test_the_expiry_rule_reads_the_first_actual_doc_comment_not_text_inside_strings_or_comments():
    """kb-1 review F3: a doc-comment opener inside a string, a character literal, a `--` comment or a plain `/- -/`
    comment (which nests) is not the module's docstring; with `/--` and `/-!`, each with the actual docstring expired
    or missing, a future date hidden in any of them is refused. An unclosed string or comment is refused too."""
    def problems(text: str) -> list[str]:
        return expiry_problems({"VE.Experimental.Trial": Fake(text)}, TODAY)

    expired = ["VE.Experimental.Trial: expired on 2000-01-01; promote it to the shell or delete it"]
    missing = ["VE.Experimental.Trial: an experimental module's first docstring needs one line `Expires: YYYY-MM-DD`"]
    for opener in ("/--", "/-!"):
        decoy = opener + "\nExpires: 2099-01-01\n-/"
        actual = opener + " Trial.\nExpires: 2000-01-01\n-/\n"
        for hide in ('def t : String := "' + decoy + '"\n', 'def t : String := r#"' + decoy + '"#\n',
                     "def t := '\"'\ndef u : String := \"" + decoy + '"\n',
                     "-- " + decoy.replace("\n", " ") + "\n", "/- outer /- inner -/\n" + decoy + "\n-/\n",
                     'def t : String := "\\"" ++ "' + decoy + '"\n'):
            assert problems(hide + actual + "def x := 1\n") == expired, hide
            assert problems(hide + "def x := 1\n") == missing, hide
            assert problems(hide + actual.replace("2000-01-01", "2026-12-31")) == [], hide
    assert problems('def t : String := "/-! Expires: 2099-01-01 -/\n') == missing  # an unclosed string
    assert problems("/-! Trial.\nExpires: 2099-01-01\n") == missing  # an unclosed docstring
    assert problems("def h' := 1\n/-! Trial.\nExpires: 2026-12-31\n-/\n") == []  # a primed name is no char literal


class Fake:
    def __init__(self, text: str):
        self.text = text

    def read_text(self) -> str:
        return self.text

