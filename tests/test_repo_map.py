"""The builders' entry file (AGENTS.md) names only what exists, and tools/repo_map.py derives its map.

AGENTS.md: every backticked path exists (a glob matches), every backticked Lean name is a declaration of
`lean/declarations.txt`, and every backticked command runs something that exists: its script, its `-m`
module, its `lake build` targets (from `lean/lakefile.toml`) or its program; a script that parses its
arguments with argparse answers `--help` with exit 0, and a `repo_map.py` command parses with the tool's
own parser. CLAUDE.md is a symlink to it.

repo_map.py: `routes` prints every mode of `MODES` exactly once, each with its existing schema file;
`--check` passes on the tree and fails on a scratch copy of the schema directory with a file removed or
added; two known routes print the right Lean module and relay (see `KNOWN`); the coverage-map path reads
the map it is given. The import graph's cache is written under tmp_path (as in tests/test_select_tests.py);
it starts from the account's summaries when they exist, which only saves time: entries are keyed by content.
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
        patch.delenv("VE_TESTMAP", raising=False)
        yield {**os.environ}


@pytest.fixture(scope="module")
def built(cache_env):
    routes, source, data = repo_map.build(ROOT, static=True)
    assert data is None
    return routes, source


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


def test_tests_come_from_the_coverage_map_when_one_is_given(built, tmp_path, monkeypatch):
    routes, _ = built
    route = next(r for r in routes if r.mode == "rights")
    [(relay, qualnames)] = [(p, q) for p, q in route.relays.items() if p == KNOWN["rights"][1]]
    unit = {"exit": 0, "seconds": 0.0, "opaque": [], "r": [], "d": [], "x": []}
    data = test_map.build_map({"tests/test_ran_it.py": {**unit, "f": [(relay, sorted(qualnames)[0])]},
                               "tests/test_did_not.py": {**unit, "f": [(relay, "<module>")]}}, "0" * 40)
    path = tmp_path / "map.json.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(data, handle)
    monkeypatch.setenv("VE_TESTMAP", str(path))
    loaded, source = repo_map.coverage(ROOT, static=False)
    assert source == f"coverage map {path}"
    sites = [(p, q) for p, qs in route.relays.items() for q in qs]
    assert repo_map.tests_of(sites, loaded, None) == ["tests/test_ran_it.py"]
    assert repo_map.tests_of([], loaded, None) is None


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
