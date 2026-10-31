"""The inventory of tests that read git history (tests/history-dependent.json) and its lint."""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import types

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import history_tests  # noqa: E402
import regen_generated  # noqa: E402
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
    """The lint on this checkout: every unit that starts git or reads .git is listed, as generated. The lint
    itself reads the saved extract and Python sources only: it starts no git and reads no .git."""
    events, active = [], [True]

    def hook(event, args):  # an audit hook stays for the process: it records only while the lint runs
        if active[0] and (event in ("subprocess.Popen", "os.posix_spawn", "os.exec", "os.system") or event == "open"
                          and isinstance(args[0], (str, Path)) and "/.git" in str(args[0])):
            events.append((event, args[:2]))

    sys.addaudithook(hook)
    try:
        findings = history_tests.lint()
    finally:
        active[0] = False
    assert findings.errors == []
    assert events == []


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


# The tools the merge refresh starts in a scratch checkout: copies, so that their ROOT is the scratch checkout.
SCRATCH_COPIES = ("regen_generated.py", "history_tests.py")


def test_a_clean_merge_keeps_a_stale_list_and_the_merge_refresh_rewrites_it(tmp_path):
    """history-tests-merge-fail (Mac train FAILs of df-e1r 2632f102, jt-e1r f71e1343 and rd9-docroute, Oct 29-30): a
    branch wrote the list on its own tree; main then added a test that starts git and listed it; the sync merge kept
    the branch's list without a conflict (`regenerate` keeps ours), so the candidate's lint failed ('missing: ...')
    while main's own run, on a list main's branch wrote, passed. The merge train's refresh of the registry's
    `at_merge` entries (`--check --at-merge`, then `--write --at-merge`) finds the list stale and rewrites it. Only
    history-tests runs here (`--only`): the other entries' inputs are not in the scratch checkout."""
    (tmp_path / "tools").mkdir()
    for path in (ROOT / "tools").glob("*.py"):
        if path.name in SCRATCH_COPIES:
            (tmp_path / "tools" / path.name).write_bytes(path.read_bytes())
        else:
            (tmp_path / "tools" / path.name).symlink_to(path)
    root = _root(tmp_path, {"tests/test_old.py": GIT_LOG})
    saved = json.loads((root / history_tests.MAP_EXTRACT).read_text())
    text = lambda: json.dumps(history_tests.generate(saved, root), indent=1) + "\n"  # noqa: E731
    base = text()
    (root / "tests/test_branch.py").write_text(textwrap.dedent(GIT_LOG))
    branch = text()                                     # the branch's own write, before it synced with main
    (root / "tests/test_branch.py").unlink()
    (root / "tests/test_main.py").write_text(textwrap.dedent(GIT_LOG))
    main = text()
    (root / "tests/test_branch.py").write_text(textwrap.dedent(GIT_LOG))  # the merged tree holds both tests
    assert regen_generated.merge_text(history_tests.LIST, base, branch, main) == (branch, True)
    (root / history_tests.LIST).write_text(branch)
    assert history_tests.lint(root).errors[0].startswith("missing: tests/test_main.py reads history and is not listed")

    def refresh(mode: str) -> int:
        return subprocess.run([sys.executable, "tools/regen_generated.py", mode, "--at-merge", "--only", "history-tests"],
                              cwd=root, env={**os.environ, "VE_REGEN_LOG": "off"}, capture_output=True,
                              timeout=HANG_TIMEOUT).returncode

    assert refresh("--check") == 1
    assert refresh("--write") == 0
    assert refresh("--check") == 0
    assert history_tests.lint(root).errors == []
    listed = [row["test"] for row in json.loads((root / history_tests.LIST).read_text())["tests"]]
    assert [unit for unit in listed if unit.startswith("tests/")] == [
        "tests/test_branch.py", "tests/test_main.py", "tests/test_old.py"]


def test_deleting_any_entry_of_the_committed_list_fails():
    # The committed list is what --write gives (test_the_tree_passes), so it stands for the generated one here.
    listed = json.loads((ROOT / history_tests.LIST).read_text())
    expected = json.loads((ROOT / history_tests.LIST).read_text())
    assert listed["tests"]
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
        ("which", START, ""), ("Repo.head", START, ""), ("outer", START, "diff"),
        ("outer.<locals>.<lambda>", START, "fetch")}
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


def _names_the_list(path: Path) -> bool:
    """Whether code (not a docstring or comment) in `path` names the list or imports or runs its lint."""
    text = path.read_text(encoding="utf-8")
    if "history-dependent" not in text and "history_tests" not in text:
        return False
    tree = ast.parse(text)
    docstrings = {id(node.body[0].value) for node in ast.walk(tree)
                  if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                  and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings \
                and ("history-dependent" in node.value or "history_tests" in node.value):
            return True
        if isinstance(node, ast.Import) and any(alias.name.split(".")[-1] == "history_tests" for alias in node.names) \
                or isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[-1] == "history_tests":
            return True
    return False


def test_only_the_lint_reads_the_list():
    """The list is an inventory and a lint only: no gate, merge or cache code reads it, so no run skips or reuses
    a test because of it. Only its lint, the lint's test, the generated-file registry, which runs the lint as the
    list's writer and checker, the lineage revision lint, and the selector, which runs the lint when a change can
    make the list stale (the next test), and the selector's test name it."""
    readers = sorted(path.relative_to(ROOT).as_posix() for directory in ("tools", "tests", "ve", "conformance")
                     for path in (ROOT / directory).rglob("*.py") if _names_the_list(path))
    assert readers == ["tests/test_history_tests.py", "tests/test_lineage_lint.py", "tests/test_select_tests.py",
                       "tools/history_tests.py",
                       "tools/regen_generated.py", "tools/select_tests.py"]


def test_the_selector_reads_the_list_only_to_run_its_lint():
    """tools/select_tests.py reaches the lint's module in `history_inventory` alone, and names no other file of it;
    tests/test_select_tests.py checks that what it answers only adds tests/test_history_tests.py to a plan."""
    tree = ast.parse((ROOT / "tools/select_tests.py").read_text(encoding="utf-8"))
    rule = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "history_inventory")
    inside = {id(node) for node in ast.walk(rule)}
    uses = [node for node in ast.walk(tree) if isinstance(node, ast.Name) and node.id == "history_tests"]
    assert uses and all(id(node) in inside for node in uses)
    assert {node.attr for node in ast.walk(rule) if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name) and node.value.id == "history_tests"} == {"named_sources", "INPUTS"}


def test_every_unit_the_saved_map_saw_read_history_is_found_from_its_source_alone():
    """The coverage map is the run-time oracle: each unit it saw start git (in any Python process of the run,
    children included) or run a function that reads `.git` is found by the source reach alone, as a new test
    would be before any map records it. A pytest run on files the source does not name counts as a start."""
    saved = json.loads((ROOT / history_tests.MAP_EXTRACT).read_text())
    sources = history_tests._Sources(ROOT)
    missed = []
    for unit, record in saved["units"].items():
        if not (ROOT / unit).is_file():
            continue
        kinds = {site.kind for site in sources.reach(unit)}
        if record["git"] and not kinds & {START, history_tests.PYTEST} or not record["git"] and READ not in kinds:
            missed.append(unit)
    assert saved["units"] and missed == []


def _new_test(tmp_path, units: dict[str, str]) -> list[str]:
    """The lint's `missing` errors once `units` are added to a checkout whose list was generated without them."""
    root = _root(tmp_path, {"tests/test_plain.py": HERMETIC})
    assert history_tests.lint(root).errors == []
    for name, source in units.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(textwrap.dedent(source))
    return [error for error in history_tests.lint(root).errors if error.startswith("missing: ")]


HELPER = """
    import subprocess

    def head():
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True).stdout

    def plain():
        return 1
"""


def test_a_new_test_that_reaches_git_only_through_an_import_or_a_helper_fails(tmp_path):
    """F1: a test that is not in the saved extract was judged by the git calls of its own file only. Git started
    at import (`conformance/frozen_norm_defaults.py`, also by an import made for its effect only), in a helper
    called through any import form, or in a namespace package's module is found through the code the test can
    run; a helper that is imported but whose git function is never named is not."""
    errors = _new_test(tmp_path, {
        "conformance/oracle.py": "import subprocess\nSOURCE = subprocess.check_output(['git', 'show', 'x:y'])\n",
        "tools/helper.py": HELPER,
        "tests/test_import.py": "from conformance import oracle\n\ndef test_x():\n    assert oracle\n",
        "tests/test_from.py": "from helper import head\n\ndef test_x():\n    assert head()\n",
        "tests/test_attribute.py": "import tools.helper\n\ndef test_x():\n    assert tools.helper.head()\n",
        "tests/test_alias.py": "import sys\nsys.path.insert(0, 'tools')\nimport helper as h\n\n"
                               "def test_x():\n    assert h.head()\n",
        "tests/test_side_effect.py": "import conformance.oracle  # noqa: F401\n\ndef test_x():\n    pass\n",
        "tests/test_unused.py": "from helper import plain\n\ndef test_x():\n    assert plain() == 1\n"})
    assert errors == [
        "missing: tests/test_alias.py reads history and is not listed (starts git (git rev-parse) in tools/helper.py)",
        "missing: tests/test_attribute.py reads history and is not listed (starts git (git rev-parse) in "
        "tools/helper.py)",
        "missing: tests/test_from.py reads history and is not listed (starts git (git rev-parse) in tools/helper.py)",
        "missing: tests/test_import.py reads history and is not listed (starts git (git show) in "
        "conformance/oracle.py)",
        "missing: tests/test_side_effect.py reads history and is not listed (starts git (git show) in "
        "conformance/oracle.py)"]


def test_a_new_test_that_starts_a_repository_script_or_module_that_starts_git_fails(tmp_path):
    """F1: a child process that runs a repository tool (`[sys.executable, "tools/x.py"]`, `-m tools.x`, a path
    built from `__file__`, a shell script) runs all of it."""
    tool = textwrap.dedent(HELPER) + "\nif __name__ == '__main__':\n    head()\n"
    errors = _new_test(tmp_path, {
        "tools/tool.py": tool, "tools/run.sh": "#!/bin/sh\ncd \"$1\" && git log -1\n",
        "tests/test_script.py": "import subprocess, sys\n\ndef test_x():\n"
                                "    subprocess.run([sys.executable, 'tools/tool.py'])\n",
        "tests/test_module.py": "import subprocess, sys\n\ndef test_x():\n"
                                "    subprocess.run([sys.executable, '-m', 'tools.tool'])\n",
        "tests/test_path.py": "import subprocess, sys\nfrom pathlib import Path\n"
                              "ROOT = Path(__file__).resolve().parents[1]\nTOOL = ROOT / 'tools' / 'tool.py'\n\n"
                              "def test_x():\n    subprocess.run([sys.executable, str(TOOL), '--check'])\n",
        "tests/test_shell.py": "import subprocess\n\ndef test_x():\n    subprocess.run(['sh', 'tools/run.sh', '.'])\n",
        "tests/test_loaded.py": "import importlib.util\nfrom pathlib import Path\n"
                                "SPEC = importlib.util.spec_from_file_location('t', Path(__file__).parents[1] / "
                                "'tools/tool.py')\nT = importlib.util.module_from_spec(SPEC)\n\n"
                                "def test_x():\n    assert T.head()\n"})
    assert [error.split(" reads history")[0] for error in errors] == [
        "missing: tests/test_loaded.py", "missing: tests/test_module.py", "missing: tests/test_path.py",
        "missing: tests/test_script.py", "missing: tests/test_shell.py"]
    assert errors[-1].endswith("(starts git in tools/run.sh)")


def test_a_program_the_scan_cannot_read_as_a_literal_git_still_counts(tmp_path):
    """F1: the program in a variable (`[git, "--version"]` after `git = shutil.which("git")`, tools/gate.py), a
    path to git, a launcher (`env git`, `sh -c "git log"`), a shell command and a `python -c` program."""
    source = """
        import os, shutil, subprocess, sys

        def variable():
            git = shutil.which("git", path=os.environ["PATH"])
            return subprocess.run([git, "--version"])

        def named(git_bin):
            return subprocess.run([git_bin, "log"])

        def assigned():
            program = os.environ.get("GIT", "git")
            return subprocess.check_output([program, "status"])

        def absolute():
            return subprocess.run(["/usr/bin/git", "log"])

        def launched():
            return subprocess.run(["env", "GIT_DIR=x", "git", "log"]), subprocess.run(["sh", "-c", "git log"])

        def shell():
            return subprocess.run("cd repo && git log -1", shell=True)

        def child():
            return subprocess.run([sys.executable, "-c", "import subprocess; subprocess.run(['git', 'log'])"])

        def not_git(git_dir, program):
            return subprocess.run([git_dir, "x"]), subprocess.run([program]), ["sh", "-c", "legit"], \
                subprocess.run([sys.executable, "-c", "print(1)"]), ("/usr/bin/gitk", "log")
    """
    found = _sites(tmp_path, source)
    assert found == {("variable", START, ""), ("named", START, ""), ("assigned", START, ""),
                     ("absolute", START, "log"), ("launched", START, ""), ("shell", START, ""),
                     ("child", START, "log")}
    assert {qualname for qualname, _, _ in found} <= _qualnames(source)


def test_a_new_test_that_uses_a_conftest_fixture_or_a_data_named_module_that_starts_git_fails(tmp_path):
    """F1: a fixture of a conftest or of its `pytest_plugins` (taken as an argument, autouse, or named in
    `usefixtures`), and a module a test imports by a name in data (`importlib.import_module(name)`)."""
    errors = _new_test(tmp_path, {
        "tools/helper.py": HELPER,
        "tests/conftest.py": "import pytest\nfrom helper import head, plain\npytest_plugins = ['plugin']\n\n"
                             "@pytest.fixture\ndef repo_head():\n    return head()\n\n"
                             "@pytest.fixture\ndef unused():\n    return head()\n\n"
                             "def pytest_sessionstart(session):\n    head()\n",
        "tests/plugin.py": "import pytest\nimport subprocess\n\n@pytest.fixture\n"
                           "def logged():\n    return subprocess.run(['git', 'log'])\n",
        "tests/test_argument.py": "def test_x(repo_head):\n    assert repo_head\n",
        "tests/test_plugin.py": "import pytest\n\n@pytest.mark.usefixtures('logged')\ndef test_x():\n    pass\n",
        "tests/test_data.py": "import importlib\nNAMES = {'h': 'tools.helper'}\n\ndef test_x():\n"
                              "    assert importlib.import_module(NAMES['h']).head()\n",
        "tests/test_hermetic.py": "def test_x(tmp_path):\n    assert tmp_path\n"})
    assert [error.split(" reads history")[0] for error in errors] == [
        "missing: tests/test_argument.py", "missing: tests/test_data.py", "missing: tests/test_plugin.py"]


def test_a_new_test_that_runs_pytest_on_files_its_source_does_not_name_fails(tmp_path):
    """A nested pytest run whose files come from data can run any test, so the unit is listed (the safe side)."""
    errors = _new_test(tmp_path, {
        "tools/runner.py": "import sys\n\ndef command(files):\n    return [sys.executable, '-m', 'pytest', *files]\n",
        "tests/test_nested.py": "import subprocess\nfrom runner import command\n\ndef test_x(tmp_path):\n"
                                "    subprocess.run(command([str(tmp_path)]))\n"})
    assert errors == ["missing: tests/test_nested.py reads history and is not listed (runs pytest on test files "
                      "the source does not name, in tools/runner.py)"]


def test_a_new_test_in_the_tree_that_imports_the_frozen_oracle_fails(tmp_path):
    """PROBE F1 on this checkout: a copy of the tree (by links) with one new test that only imports
    `conformance.frozen_norm_defaults`, which runs `git show` at import."""
    for name in os.listdir(ROOT):
        if name != "tests":
            os.symlink(ROOT / name, tmp_path / name)
    (tmp_path / "tests").mkdir()
    for name in os.listdir(ROOT / "tests"):
        os.symlink(ROOT / "tests" / name, tmp_path / "tests" / name)
    (tmp_path / "tests/test_zz_probe.py").write_text(
        "from conformance import frozen_norm_defaults\n\ndef test_x():\n    assert frozen_norm_defaults\n")
    assert "missing: tests/test_zz_probe.py reads history and is not listed (starts git (git show) in " \
        "conformance/frozen_norm_defaults.py)" in history_tests.lint(tmp_path).errors


COMMANDS = """
    import os
    import subprocess
    GIT = ("git", "--no-optional-locks", "-c", "core.quotePath=false")
    PROGRAM = os.environ.get("GIT", "git")
    LAKE = ("lake", "build")
    OUTPUT = subprocess.check_output(["lake", "--version"])
    GITK = "gitk"

    class Repo:
        GIT = ["git", "-C", "repo"]
"""


def test_a_new_test_that_uses_a_git_command_bound_in_another_module_fails(tmp_path):
    """F4: a git command bound to a name in one module (`tools/gate_collection.py`'s `GIT`) and used in another
    (`from tools.gate_collection import GIT`, then `[*GIT, "log"]`) counts, whatever the name is called where it
    is used and however it is reached: an alias, a module attribute, a class attribute, a re-export, a star
    import, a sum. A module's other names do not."""
    run = "import subprocess\n{}\n\ndef test_x():\n    subprocess.run({})\n"
    errors = _new_test(tmp_path, {
        "tools/commands.py": COMMANDS, "tools/again.py": "from commands import GIT  # noqa: F401\n",
        "tests/test_starred.py": run.format("from commands import GIT", '[*GIT, "log", "-1"]'),
        "tests/test_alias.py": run.format("from commands import GIT as tool", '[*tool, "log"]'),
        "tests/test_module.py": run.format("import commands", '[*commands.GIT, "log"]'),
        "tests/test_sum.py": run.format("from commands import GIT as base", 'list(base) + ["log"]'),
        "tests/test_string.py": run.format("from commands import PROGRAM as program", '[program, "status"]'),
        "tests/test_class.py": run.format("from commands import Repo", '[*Repo.GIT, "log"]'),
        "tests/test_reexport.py": run.format("from again import GIT as command", "command"),
        "tests/test_star.py": run.format("from commands import *  # noqa: F403", '[*GIT, "log"]'),
        "tests/test_other.py": run.format("from commands import LAKE, OUTPUT, GITK", "[*LAKE, OUTPUT, GITK]")})
    assert [error.split(" reads history")[0] for error in errors] == [
        f"missing: tests/test_{name}.py" for name in ("alias", "class", "module", "reexport", "star", "starred",
                                                      "string", "sum")]
    assert errors[-1].endswith("(starts git in tools/commands.py)")


def test_a_name_bound_to_git_is_a_site_of_the_name_and_a_starred_or_summed_one_of_its_use(tmp_path):
    """F4: which module- and class-level names hold the git program (`programs`), by the same test as a program
    in a command, and the use of an imported one as a program: starred, summed, split, looked up or chosen. What
    a process call returns is git's output, not the program."""
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/commands.py").write_text(textwrap.dedent(COMMANDS))
    scanner = history_tests._scan("tools/commands.py", tmp_path)
    assert {name: (site.kind, site.line) for name, site in scanner.programs.items()} == {
        "GIT": (START, 4), "PROGRAM": (START, 5), "Repo.GIT": (START, 11)}
    assert scanner.found == set()
    source = """
        import os, subprocess
        from commands import GIT, LAKE

        def starred():
            return subprocess.run([*GIT, "log"])

        def summed():
            return subprocess.run(GIT + ["log"])

        def split():
            return subprocess.run("git log".split())

        def looked_up():
            return subprocess.run([os.environ.get("GIT", "git"), "log"])

        def chosen():
            return subprocess.run([os.environ.get("GIT") or "git", "log"])

        def output():
            out = subprocess.check_output(["git", "log"])
            return (out, 1), [out.strip()], subprocess.run([*LAKE, "build"]), "gitk log".split()
    """
    found = _sites(tmp_path, source)
    assert found == {("starred", START, ""), ("summed", START, ""), ("split", START, ""), ("looked_up", START, ""),
                     ("chosen", START, ""), ("output", START, "log")}
    assert {qualname for qualname, _, _ in found} <= _qualnames(source)


def test_a_new_test_in_the_tree_that_runs_the_gate_collections_git_vector_fails(tmp_path):
    """PROBE F4 on this checkout: a copy of the tree (by links) with one new test that runs
    `[*GIT, "log", "-1"]` with `GIT` imported from `tools/gate_collection.py`."""
    for name in os.listdir(ROOT):
        if name != "tests":
            os.symlink(ROOT / name, tmp_path / name)
    (tmp_path / "tests").mkdir()
    for name in os.listdir(ROOT / "tests"):
        os.symlink(ROOT / "tests" / name, tmp_path / "tests" / name)
    (tmp_path / "tests/test_zz_probe.py").write_text(
        'import subprocess\nfrom tools.gate_collection import GIT\n\ndef test_x():\n'
        '    subprocess.run([*GIT, "log", "-1"])\n')
    assert any(error.startswith("missing: tests/test_zz_probe.py reads history and is not listed (starts git in ")
               for error in history_tests.lint(tmp_path).errors)


def test_the_run_and_the_source_decide_what_names_git_with_one_definition():
    """tests/read_recorder.py (at run time) and the lint (in the source) both call tools/git_words.py."""
    sys.path.insert(0, str(ROOT))
    from tests import read_recorder
    assert Path(read_recorder.names_git.__code__.co_filename) == Path(history_tests.names_git.__code__.co_filename) \
        == ROOT / "tools/git_words.py"
