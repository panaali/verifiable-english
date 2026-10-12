"""The builders' entry file (AGENTS.md) names only what exists, and tools/repo_map.py derives its map.

AGENTS.md: every backticked path exists (a glob matches), every backticked Lean name is a declaration of
`lean/declarations.txt`, and every backticked command runs something that exists: its script, its `-m`
module, its `lake build` targets (from `lean/lakefile.toml`) or its program; a script that parses its
arguments with argparse answers `--help` with exit 0, and a `repo_map.py` command parses with the tool's
own parser. CLAUDE.md is a symlink to it.

repo_map.py: `routes` prints every mode of `MODES` exactly once, each with its existing schema file;
`--check` passes on the tree and fails on a scratch copy of the schema directory with a file removed or
added; two known routes print the right Lean module and relay (see `KNOWN`). Tests: a coverage map answers
only for the test files it recorded and can still vouch for; every other test file, and every one when the
map's commit is not in the repository or a map from a real ancestor vouches for none (a relay file changed
since), gets the static answer, never an empty one (review F1). `file` names
a path the same way however it is spelled (F2). The `routes` and `file` commands run as programs (F3).
The import graph's cache and the account's map cache are under tmp_path (as in tests/test_select_tests.py);
the graph starts from the account's summaries when they exist, which only saves time: entries are keyed by
content.
"""
from __future__ import annotations

import collections
import contextlib
import gzip
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tomllib

import pytest

from tools import repo_map, test_map
from ve.backends.service_schema import MODES

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
TOOL = ROOT / "tools/repo_map.py"
SUFFIXES = (".md", ".py", ".lean", ".json", ".jsonl", ".txt", ".toml", ".lock", ".sha256")
LEAN_NAME = re.compile(r"(?:VE|ResponseShape)(?:\.[A-Za-z_][\w']*)+")
# Two routes and the files that implement them, by hand:
# * readings-route: lean-first batch 3 moved the readings route executable into the service as this mode;
#   `VE.Readings.Run.runCaseReported` answers it, and `ve/readings_route.py` names the mode in its docstring
#   and sends it with `relay.rows`.
# * rights: `VE.Rights.Run.runCaseReported` answers it; `ve/rights_route.py` ("Relay rights decisions ...
#   from the Lean rights route") sends it with `relay.decide_once`.
# * english.read: sent through a module constant (`MODE = "english.read"` in `ve/backends/english_lean.py`).
KNOWN = {
    "readings-route": ("lean/VE/Readings/Run.lean", "ve/readings_route.py"),
    "rights": ("lean/VE/Rights/Run.lean", "ve/rights_route.py"),
    "english.read": ("lean/VE/EnglishGrammar/Run.lean", "ve/backends/english_lean.py"),
}


@pytest.fixture(scope="module")
def cache_env(tmp_path_factory):
    cache = tmp_path_factory.mktemp("cache")
    summaries = Path.home() / ".cache/ve-testselect/summaries.pickle"
    if summaries.is_file():
        (cache / "ve-testselect").mkdir()
        shutil.copy(summaries, cache / "ve-testselect/summaries.pickle")
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("XDG_CACHE_HOME", str(cache))
        patch.setenv("VE_TESTMAP_CACHE", str(cache / "ve-testmap"))  # no map unless a test writes one
        patch.delenv("VE_TESTMAP", raising=False)
        yield {**os.environ}


@pytest.fixture(scope="module")
def built(cache_env):
    routes, tests = repo_map.build(ROOT, static=True)
    assert tests.coverage is None
    return routes, tests.source


@pytest.fixture(scope="module")
def printed(built):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        repo_map.print_routes(*built)
    return out.getvalue().splitlines()


def tool(*args, env=None, cwd=ROOT):
    return subprocess.run([sys.executable, str(TOOL), *args], cwd=cwd, env=env, capture_output=True, text=True)


# -- AGENTS.md --------------------------------------------------------------------------------------------
def spans() -> list[str]:
    return re.findall(r"`([^`\n]+)`", AGENTS.read_text(encoding="utf-8"))


def is_path(span: str) -> bool:
    return " " not in span and "<" not in span and ("/" in span or span.endswith(SUFFIXES)) \
        and not LEAN_NAME.fullmatch(span)


def commands() -> list[tuple[Path, list[str]]]:
    """(working directory, argv) of each backticked command, `cd DIR &&` and `NAME=value` prefixes applied."""
    found = []
    for span in spans():
        if " " not in span:
            continue
        cwd, words = ROOT, shlex.split(span.replace("$(git merge-base HEAD main)", "BASE"))
        if words[:1] == ["cd"] and words[2:3] == ["&&"]:
            cwd, words = ROOT / words[1], words[3:]
        while words and re.fullmatch(r"[A-Z_]+=\S*", words[0]):
            words = words[1:]
        if words and words[0] in ("uv", "python", "python3", "lake", "git"):
            found.append((cwd, words))
    return found


def script_of(cwd: Path, words: list[str]) -> tuple[Path | None, list[str]]:
    """The script or module file a python command runs, and its arguments."""
    if words[:2] == ["uv", "run"]:
        words = words[2:]
    assert words[0] in ("python", "python3"), words
    if words[1] == "-m":
        stem = cwd / words[2].replace(".", "/")
        return next((p for p in (stem.with_suffix(".py"), stem / "__init__.py") if p.is_file()), None), words[3:]
    return cwd / words[1], words[2:]


def test_agents_md_is_short_and_claude_md_is_its_symlink():
    assert len(AGENTS.read_text(encoding="utf-8").splitlines()) <= 150
    claude = ROOT / "CLAUDE.md"
    assert claude.is_symlink() and os.readlink(claude) == "AGENTS.md"


def test_every_path_named_in_agents_md_exists():
    paths = [span for span in spans() if is_path(span)]
    assert len(paths) >= 20, paths  # the parse found the file's paths
    missing = [p for p in paths if not (any(ROOT.glob(p)) if "*" in p else (ROOT / p).exists())]
    assert not missing, f"AGENTS.md names paths that do not exist: {missing}"


def test_every_lean_name_in_agents_md_is_declared():
    names = [span for span in spans() if LEAN_NAME.fullmatch(span)]
    assert names
    declared = {line.split()[2].rpartition("@")[0] for line in
                (ROOT / "lean/declarations.txt").read_text(encoding="utf-8").splitlines()
                if not line.startswith("--") and len(line.split()) >= 3}
    assert not [n for n in names if n not in declared]


def test_every_command_named_in_agents_md_exists_and_the_fast_ones_answer_help(cache_env):
    found = commands()
    assert len(found) >= 10, found
    lakefile = tomllib.loads((ROOT / "lean/lakefile.toml").read_text())
    targets = {entry["name"] for kind in ("lean_exe", "lean_lib") for entry in lakefile.get(kind, [])}
    helped = set()
    for cwd, words in found:
        if words[0] == "lake":  # lake runs in lean/ (AGENTS.md: `cd lean && ... lake build`)
            assert ((cwd if cwd != ROOT else ROOT / "lean") / "lakefile.toml").is_file(), words
            assert words[1] == "build" and set(words[2:]) <= targets, words
            continue
        if words[0] == "git":
            assert shutil.which("git"), words
            continue
        script, arguments = script_of(cwd, words)
        assert script is not None and script.is_file(), words
        if script == TOOL:
            parsed = repo_map.make_parser().parse_args(arguments)
            assert parsed.command or parsed.check
            assert getattr(parsed, "mode", MODES[0]) in MODES
            assert getattr(parsed, "path", None) is None or (ROOT / parsed.path).exists() or "<" in parsed.path
        if "argparse" in script.read_text(encoding="utf-8") and script not in helped:
            helped.add(script)
            done = subprocess.run([sys.executable, str(script), "--help"], cwd=cwd, env=cache_env,
                                  capture_output=True, text=True)
            assert done.returncode == 0, (script, done.stderr[-2000:])
    assert TOOL in helped


# -- repo_map.py ----------------------------------------------------------------------------------------------
def rows(printed: list[str]) -> list[list[str]]:
    header = printed.index("mode | Lean module(s) | response schema | Python relays | tests")
    return [line.split(" | ") for line in printed[header + 1:]]


def test_routes_lists_every_mode_exactly_once(printed):
    listed = collections.Counter(row[0] for row in rows(printed))
    assert listed == collections.Counter(MODES), listed
    assert all(len(row) == 5 for row in rows(printed))


def test_every_printed_schema_file_exists(printed):
    for row in rows(printed):
        assert row[2] == f"{repo_map.SCHEMA_DIRECTORY}/{row[0]}.json"
        assert (ROOT / row[2]).is_file()


def test_every_printed_lean_and_relay_file_exists(built):
    routes, _ = built
    assert sum(1 for r in routes if r.lean) > len(MODES) // 2
    for route in routes:
        assert all((ROOT / where).is_file() for where in repo_map.lean_files(route)), route
        assert all((ROOT / path).is_file() and path.startswith(repo_map.PRODUCT) for path in route.relays), route


@pytest.mark.parametrize("mode", sorted(KNOWN))
def test_known_routes_print_their_lean_module_and_relay(built, mode):
    routes, _ = built
    route = next(r for r in routes if r.mode == mode)
    lean, relay = KNOWN[mode]
    assert repo_map.lean_files(route) == [lean]
    assert relay in route.relays
    assert route.tests  # the static import graph reaches the relay from some test


def test_route_prints_one_mode_in_full(cache_env):
    done = tool("--static", "route", "rights", env=cache_env)
    assert done.returncode == 0, done.stderr
    lines = done.stdout.splitlines()
    assert lines[:2] == ["mode: rights", f"schema: {repo_map.SCHEMA_DIRECTORY}/rights.json"]
    assert f"  {KNOWN['rights'][0]}  (VE.Rights.Run.runCaseReported)" in lines
    assert any(line.startswith(f"  {KNOWN['rights'][1]}  (") for line in lines)
    assert tool("route", "no-such-mode", env=cache_env).returncode == 2


def write_map(path: Path, ran: dict[str, list[tuple[str, str]]], commit: str) -> Path:
    """A coverage map, as `tools/test_map.py` writes one, in which each test file ran the given functions."""
    unit = {"exit": 0, "seconds": 0.0, "opaque": [], "r": [], "d": [], "x": []}
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(test_map.build_map({test: {**unit, "f": functions} for test, functions in ran.items()},
                                     commit), handle)
    return path


def head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


@pytest.fixture
def rights_map(built, cache_env, tmp_path, monkeypatch):
    """A map at HEAD in which one test file ran the rights relay's function and one only imported its file;
    both are test files the static graph reaches the relay from, and neither is changed in the working tree."""
    routes, _ = built
    route = next(r for r in routes if r.mode == "rights")
    relay = KNOWN["rights"][1]
    sites = [(relay, q) for q in sorted(route.relays[relay])]
    changed = set(subprocess.run(["git", "status", "--porcelain", "--no-renames"], cwd=ROOT, capture_output=True,
                                 text=True, check=True).stdout.split())
    ran_it, did_not = [t for t in route.tests if t.startswith("tests/") and t not in changed][:2]
    path = write_map(tmp_path / "map.json.gz", {ran_it: sites[:1], did_not: [(relay, "<module>")]}, head())
    monkeypatch.setenv("VE_TESTMAP", str(path))
    return sites, ran_it, did_not, route.tests


def test_a_map_answers_only_for_the_test_files_it_recorded(rights_map):
    sites, ran_it, did_not, static = rights_map
    _, tests = repo_map.build(ROOT)
    assert tests.coverage is not None and tests.source.startswith("coverage map "), tests.source
    found = tests.of_sites(sites)
    assert ran_it in found and did_not not in found  # the map answers for the two it recorded
    assert set(found) == set(static) - {did_not}       # the static graph for every other test file
    assert tests.of_sites([]) is None


def test_a_test_file_whose_run_may_have_changed_gets_the_static_answer(rights_map, monkeypatch):
    """Drift (`select_tests.uncertain_since`) takes a recorded test file out of the map's hands."""
    sites, ran_it, did_not, _ = rights_map
    real = repo_map.select_tests.uncertain_since
    monkeypatch.setattr(repo_map.select_tests, "uncertain_since",
                        lambda *args: (real(*args)[0] | {did_not}, 1))
    _, tests = repo_map.build(ROOT)
    assert did_not in tests.unmapped and ran_it not in tests.unmapped
    assert did_not in tests.of_sites(sites)


def test_a_map_from_a_commit_not_in_the_repository_gives_the_static_answer(built, tmp_path, monkeypatch):
    """PROBE F1 (review devtime-1): the map lists one test that imported ve/discourse.py; `english.question`'s
    relay function is not in it. Its tests were printed as "0 files"; they are now the static graph's."""
    path = write_map(tmp_path / "m.json.gz", {"tests/test_x.py": [("ve/discourse.py", "<module>")]}, "0" * 40)
    monkeypatch.setenv("VE_TESTMAP", str(path))
    routes, tests = repo_map.build()
    route = {r.mode: r for r in routes}["english.question"]
    assert route.tests is None or route.tests, route.tests
    assert tests.coverage is None and "not in this repository" in tests.source, tests.source
    assert route.tests == next(r for r in built[0] if r.mode == "english.question").tests


def test_a_map_from_before_the_relay_changed_gives_the_static_answer(built, cache_env, tmp_path, monkeypatch):
    """Review F1 on the real tree: the map was recorded at an ancestor commit, and `english.question`'s relay
    file changed after it (`read_question` was added after c24aeab2). The one test file the map recorded only
    imported that file, so the map named no test for the relay function; its run may have changed, so the
    static graph answers for it and for every other test file, not the map's empty list."""
    static = next(r for r in built[0] if r.mode == "english.question")
    relay = "ve/backends/english_lean.py"
    assert static.relays.get(relay) and static.tests, (static.relays, static.tests)
    last = subprocess.run(["git", "log", "-1", "--format=%H", "--", relay], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()
    before = subprocess.run(["git", "rev-parse", f"{last}^"], cwd=ROOT, capture_output=True, text=True,
                            check=True).stdout.strip()
    recorded = static.tests[0]
    path = write_map(tmp_path / "m.json.gz", {recorded: [(relay, "<module>")]}, before)
    monkeypatch.setenv("VE_TESTMAP", str(path))
    routes, tests = repo_map.build(ROOT)
    route = {r.mode: r for r in routes}["english.question"]
    assert recorded in tests.unmapped, tests.source
    assert route.tests == static.tests, tests.source


def test_file_answers_for_a_file_the_map_never_saw(rights_map):
    """`file` on a file no recorded test ran (review F1: `ve/readings_components.py` printed "none found")."""
    _, ran_it, did_not, _ = rights_map
    _, tests = repo_map.build(ROOT)
    found = tests.of_file("ve/readings_components.py")
    static = repo_map.tests_from(ROOT, tests.graph, True).of_file("ve/readings_components.py")
    assert found and set(found) == set(static) - {ran_it, did_not}


# "{root}" stands for the checkout's absolute path (filled in by `spelled`, so test IDs do not depend on it).
SPELLINGS = ["ve/discourse.py", "./ve/discourse.py", "ve//discourse.py", "ve/./discourse.py",
             "ve/../ve/discourse.py", "{root}/ve/discourse.py", "{root}/./ve/../ve/discourse.py"]


def spelled(spelling: str) -> str:
    return spelling.replace("{root}", str(ROOT))


@pytest.mark.parametrize("spelling", SPELLINGS)
def test_file_names_a_path_the_same_however_it_is_spelled(spelling):
    assert repo_map.repo_path(ROOT, spelled(spelling)) == "ve/discourse.py"


def test_file_prints_the_same_for_every_spelling(built, cache_env):
    """F2: `./ve/discourse.py` printed "modes: none" and "tests: none found"."""
    routes, _ = built
    tests = repo_map.tests_from(ROOT, repo_map.source_graph.load(ROOT), True)
    printed = {}
    for spelling in SPELLINGS:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            repo_map.print_file(ROOT, spelled(spelling), routes, tests)
        printed[spelling] = out.getvalue()
    assert len(set(printed.values())) == 1, printed
    assert "modes: discourse\n" in printed[SPELLINGS[0]]


def test_file_command_prints_modes_layer_tests_and_generator(cache_env):
    """F3: `file` run as a program, on the spelling F2 found."""
    done = tool("--static", "file", "./ve/discourse.py", env=cache_env)
    assert done.returncode == 0, done.stderr
    lines = done.stdout.splitlines()
    layer = repo_map.layer_policy.source_layer("ve/discourse.py")
    assert lines[:3] == ["file: ve/discourse.py", "modes: discourse",
                         f"layer: {layer} ({repo_map.layer_policy.NAMES[layer]})"]
    assert lines[3] == "tests (static import graph (--static)):" and lines[4].startswith("  tests/")
    assert lines[-1] == "generator: -"
    schema = tool("--static", "file", f"{repo_map.SCHEMA_DIRECTORY}/discourse.json", env=cache_env)
    assert "modes: discourse" in schema.stdout.splitlines()
    assert schema.stdout.splitlines()[-1] == "generator: response-schemas"


def test_routes_command_prints_the_table(printed, cache_env):
    """F3: `routes` run as a program prints what `print_routes` prints in the process."""
    done = tool("--static", "routes", env=cache_env)
    assert done.returncode == 0, done.stderr
    assert done.stdout.splitlines() == printed


def test_check_passes_on_the_tree():
    done = tool("--check")
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.startswith(f"PASS: {len(MODES)} modes")


def test_check_fails_on_a_scratch_copy_with_a_schema_file_removed_or_added(tmp_path):
    scratch = tmp_path / repo_map.SCHEMA_DIRECTORY
    shutil.copytree(ROOT / repo_map.SCHEMA_DIRECTORY, scratch)
    assert tool("--check", "--root", str(tmp_path)).returncode == 0
    (scratch / "rights.json").unlink()
    done = tool("--check", "--root", str(tmp_path))
    assert done.returncode == 1
    assert done.stdout.splitlines() == [f"mode 'rights' has no schema file {repo_map.SCHEMA_DIRECTORY}/rights.json"]
    shutil.copy(ROOT / repo_map.SCHEMA_DIRECTORY / "rights.json", scratch / "rights.json")
    shutil.copy(scratch / "rights.json", scratch / "stray.json")
    done = tool("--check", "--root", str(tmp_path))
    assert done.returncode == 1
    assert done.stdout.splitlines() == [f"schema file {repo_map.SCHEMA_DIRECTORY}/stray.json has no mode in MODES"]
