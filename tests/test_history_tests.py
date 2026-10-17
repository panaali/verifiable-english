"""The inventory of tests that read git history (tests/history-dependent.json) and its lint."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import textwrap
import types

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import history_tests  # noqa: E402
from history_tests import READ, START  # noqa: E402


def _sites(tmp_path, source: str, name: str = "tests/test_sample.py") -> set[tuple[str, str, str]]:
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(source))
    return {(site.qualname, site.kind, site.command) for site in history_tests.sites(name, tmp_path)}


def _qualnames(source: str) -> set[str]:
    """Every code object's `co_qualname` in a module: the names the coverage map records."""
    names, todo = set(), [compile(textwrap.dedent(source), "sample", "exec")]
    while todo:
        code = todo.pop()
        names.add(code.co_qualname)
        todo += [const for const in code.co_consts if isinstance(const, types.CodeType)]
    return names


def _root(tmp_path, units: dict[str, str], extract_units: dict | None = None) -> Path:
    """A checkout with these test units, a saved map extract and the list generated from them."""
    for name, source in units.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(textwrap.dedent(source))
    saved = {"format": history_tests.MAP_FORMAT,
             "map": {"commit": "0" * 40, "version": 7, "created": "2026-10-17T00:00:00+00:00", "tests": len(units)},
             "units": extract_units or {}}
    history_tests.write_json(tmp_path / history_tests.MAP_EXTRACT, saved)
    history_tests.write_json(tmp_path / history_tests.LIST, history_tests.generate(saved, tmp_path))
    return tmp_path


def _edit_list(root: Path, change) -> None:
    path = root / history_tests.LIST
    listed = json.loads(path.read_text())
    change(listed)
    history_tests.write_json(path, listed)


GIT_LOG = """
    import subprocess

    def test_log_is_ordered():
        subprocess.run(["git", "log", "--oneline"], check=True)
"""
HERMETIC = """
    def test_adds():
        assert 1 + 1 == 2
"""


def test_the_tree_passes():
    """The lint on this checkout: every unit that starts git or reads .git is listed, as generated."""
    findings = history_tests.lint()
    assert findings.errors == []


def test_the_command_line_lint_passes_on_the_tree():
    run = subprocess.run([sys.executable, "tools/history_tests.py", "--check"], cwd=ROOT, capture_output=True,
                         text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stderr
    assert "every test that reads history is listed" in run.stdout


def test_a_new_test_that_runs_git_log_and_is_not_listed_fails(tmp_path):
    root = _root(tmp_path, {"tests/test_plain.py": HERMETIC})
    assert history_tests.lint(root).errors == []
    (root / "tests/test_new.py").write_text(textwrap.dedent(GIT_LOG))
    errors = history_tests.lint(root).errors
    assert errors[0] == ("missing: tests/test_new.py reads history and is not listed "
                         "(starts git (git log) in tests/test_new.py)")
    assert errors[-1].startswith("run `python tools/history_tests.py --write`")


def test_deleting_any_entry_of_the_committed_list_fails():
    listed = json.loads((ROOT / history_tests.LIST).read_text())
    expected = history_tests.generate(json.loads((ROOT / history_tests.MAP_EXTRACT).read_text()))
    assert listed == expected and listed["tests"]
    for row in listed["tests"]:
        smaller = {**listed, "tests": [other for other in listed["tests"] if other is not row]}
        errors = history_tests.compare(smaller, expected).errors
        assert errors[0].startswith(f"missing: {row['test']} reads history and is not listed ("), row["test"]


def test_every_unit_the_saved_map_saw_start_git_is_listed():
    saved = json.loads((ROOT / history_tests.MAP_EXTRACT).read_text())
    listed = {row["test"] for row in json.loads((ROOT / history_tests.LIST).read_text())["tests"]}
    started = {unit for unit, record in saved["units"].items() if record["git"]}
    assert started and started <= listed
    # The source explains every start the map recorded: each such unit ran a function that starts git.
    assert all(saved["units"][unit]["sites"] for unit in started)


def test_an_entry_whose_unit_no_longer_reads_history_is_reported_stale_without_failing(tmp_path):
    root = _root(tmp_path, {"tests/test_plain.py": HERMETIC, "tests/test_old.py": GIT_LOG})
    assert [row["test"] for row in json.loads((root / history_tests.LIST).read_text())["tests"]] == \
        ["tests/test_old.py"]
    (root / "tests/test_old.py").write_text(textwrap.dedent(HERMETIC))
    findings = history_tests.lint(root)
    assert findings.errors == []
    assert findings.stale == ["stale: tests/test_old.py is listed but no longer reads history"]
    (root / "tests/test_old.py").unlink()
    assert history_tests.lint(root).stale == [
        "stale: tests/test_old.py is listed but no longer reads history (the unit is gone)"]


def test_a_unit_found_only_through_the_map_is_stale_once_its_function_stops_starting_git(tmp_path):
    root = _root(tmp_path, {"tests/test_user.py": HERMETIC, "tools/helper.py": GIT_LOG.replace("test_", "")},
                 {"tests/test_user.py": {"git": True, "sites": ["tools/helper.py:log_is_ordered"]}})
    listed = json.loads((root / history_tests.LIST).read_text())["tests"]
    assert listed == [{"test": "tests/test_user.py", "why": "starts git (git log) in tools/helper.py",
                       "recorded": ["coverage map"], "via": ["tools/helper.py:log_is_ordered: git log"]}]
    assert history_tests.lint(root) == history_tests.Findings([], [])
    (root / "tools/helper.py").write_text("def log_is_ordered():\n    return []\n")
    assert history_tests.lint(root) == history_tests.Findings(
        [], ["stale: tests/test_user.py is listed but no longer reads history"])


def test_an_edited_entry_or_map_header_fails(tmp_path):
    root = _root(tmp_path, {"tests/test_old.py": GIT_LOG})
    _edit_list(root, lambda listed: listed["tests"][0].update(why="reads nothing"))
    assert history_tests.lint(root).errors[0].startswith("changed: tests/test_old.py is listed as ")
    _edit_list(root, lambda listed: listed["tests"][0].update(why="starts git (git log) in tests/test_old.py"))
    assert history_tests.lint(root).errors == []
    _edit_list(root, lambda listed: listed["map"].update(commit="1" * 40))
    assert history_tests.lint(root).errors[0].startswith(f"{history_tests.LIST}: names map ")


def test_a_malformed_list_or_extract_fails(tmp_path):
    root = _root(tmp_path, {"tests/test_old.py": GIT_LOG})
    good = json.loads((root / history_tests.LIST).read_text())
    for broken in ({**good, "extra": 1}, {**good, "tests": [{**good["tests"][0], "why": ""}]},
                   {**good, "tests": good["tests"] * 2}, {**good, "tests": [{**good["tests"][0], "recorded": []}]}):
        history_tests.write_json(root / history_tests.LIST, broken)
        assert history_tests.lint(root).errors, broken
    history_tests.write_json(root / history_tests.LIST, good)
    saved = json.loads((root / history_tests.MAP_EXTRACT).read_text())
    for units in ({"tests/test_x.py": {"git": False, "sites": []}}, {"tests/test_x.py": {"git": 1, "sites": []}},
                  {"tests/test_x.py": {"git": True, "sites": [["a", "b"]]}}):
        history_tests.write_json(root / history_tests.MAP_EXTRACT, {**saved, "units": units})
        assert history_tests.lint(root).errors[0].startswith(history_tests.MAP_EXTRACT), units
    (root / history_tests.LIST).write_text("{")
    assert history_tests.lint(root).errors[0].startswith(f"{history_tests.LIST}: unreadable")


def test_argument_vectors_shell_strings_and_named_vectors_are_sites_of_the_code_that_runs_them(tmp_path):
    source = """
        import os, subprocess
        GIT = ("git", "--no-optional-locks", "-c", "core.quotePath=false")
        NOT_GIT = ["gitk", "log"]

        def show(rev):
            return subprocess.run([*GIT, "show", rev])

        def anything(*args):
            return subprocess.run(("git", *args))

        def at(root):
            return subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"])

        def shell():
            os.system("git status --short")

        def which():
            import shutil
            return shutil.which("git"), "git".upper()

        class Repo:
            def head(self):
                return subprocess.run(GIT + ("log", "-1"))

        def outer():
            return [subprocess.run(["git", "diff"]) for _ in range(1)], (lambda: ["git", "fetch"])
    """
    assert _sites(tmp_path, source) == {
        ("show", START, "show"), ("anything", START, ""), ("at", START, "rev-parse"), ("shell", START, "status"),
        ("Repo.head", START, ""), ("outer", START, "diff"), ("outer.<locals>.<lambda>", START, "fetch")}
    assert {qualname for qualname, _, _ in _sites(tmp_path, source)} <= _qualnames(source)


def test_genexpr_class_body_and_default_sites_carry_the_code_objects_qualname(tmp_path):
    source = """
        import subprocess

        def defaults(run=subprocess.run(["git", "version"])):
            return list(subprocess.run(["git", "log", rev]) for rev in ("a", "b"))

        class Body:
            OUT = subprocess.run(["git", "describe"])

            def method(self):
                def inner():
                    return ["git", "blame"]
                return inner
    """
    found = _sites(tmp_path, source)
    assert found == {("<module>", START, "version"), ("defaults.<locals>.<genexpr>", START, "log"),
                     ("Body", START, "describe"), ("Body.method.<locals>.inner", START, "blame")}
    assert {qualname for qualname, _, _ in found} <= _qualnames(source)


def test_a_git_path_is_a_read_but_a_compared_or_listed_name_is_not(tmp_path):
    source = """
        import os
        from pathlib import Path
        SKIPPED = (".git", ".venv")
        GIT_DIR = ".git"

        def head(root):
            return (Path(root) / ".git/HEAD").read_text()

        def joined(root):
            return open(os.path.join(root, ".git"))

        def config(root):
            return root / ".git" / "config"

        def skipped(name, path):
            return name == ".git" or name in {".git", ".venv"} or path.endswith("/.git") or ".git" in path

        def attributes(root):
            return root / ".gitattributes"
    """
    assert _sites(tmp_path, source) == {("<module>", READ, ""), ("head", READ, ""), ("joined", READ, ""),
                                        ("config", READ, "")}


def test_the_extract_counts_a_start_only_where_the_map_saw_git_and_a_read_wherever_it_ran(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/helper.py").write_text(textwrap.dedent("""
        import subprocess
        from pathlib import Path

        def log():
            return subprocess.run(["git", "log"])

        def head(root):
            return (Path(root) / ".git/HEAD").read_text()

        def plain():
            return 1
    """))
    data = {"commit": "c" * 40, "version": 7, "created": "now", "tests": ["tests/test_a.py", "tests/test_b.py",
                                                                           "tests/test_c.py", "tests/test_d.py"],
            "programs": {"git": [0, 3], "lake": [1]},
            "functions": {"tools/helper.py": {"log": [0, 1], "head": [2], "plain": [0, 1, 2, 3]}}}
    saved = history_tests.extract(data, tmp_path)
    assert saved == {"format": history_tests.MAP_FORMAT,
                     "map": {"commit": "c" * 40, "version": 7, "created": "now", "tests": 4},
                     "units": {"tests/test_a.py": {"git": True, "sites": ["tools/helper.py:log"]},
                               "tests/test_c.py": {"git": False, "sites": ["tools/helper.py:head"]},
                               "tests/test_d.py": {"git": True, "sites": []}}}
    assert history_tests.validate_extract(saved) == []
    for unit in data["tests"]:
        (tmp_path / unit).parent.mkdir(exist_ok=True)
        (tmp_path / unit).write_text(textwrap.dedent(HERMETIC))
    rows = {row["test"]: row for row in history_tests.generate(saved, tmp_path)["tests"]}
    assert set(rows) == {"tests/test_a.py", "tests/test_c.py", "tests/test_d.py"}
    assert rows["tests/test_c.py"]["why"] == "reads .git in tools/helper.py"
    assert rows["tests/test_d.py"] == {
        "test": "tests/test_d.py", "recorded": ["coverage map"], "via": [],
        "why": "the coverage map records it starting git from code with no site in the tree's Python"}


def test_the_lint_starts_no_git_and_reads_no_git_directory():
    events, active = [], [True]

    def hook(event, args):  # an audit hook stays for the process: it records only while the lint runs
        if active[0] and (event in ("subprocess.Popen", "os.posix_spawn", "os.exec", "os.system") or event == "open"
                          and isinstance(args[0], (str, Path)) and "/.git" in str(args[0])):
            events.append((event, args[:2]))

    sys.addaudithook(hook)
    try:
        history_tests.lint()
    finally:
        active[0] = False
    assert events == []
