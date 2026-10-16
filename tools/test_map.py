"""Record and load the per-test coverage map used by tools/select_tests.py.

`python3 tools/test_map.py record` runs every test file in its own pytest
process (and tools/test_layer_policy.py) with tools/test_map_recorder.py
loaded into each Python process of the project environment (through a `.pth`
hook that exists only while recording), then writes one map for the clean HEAD commit
to the shared cache (`$VE_TESTMAP_CACHE`, default ~/.cache/ve-testmap). The
map says, per test unit, which functions under the root it executed, which
files it read and which directories it listed, which programs it started,
and which assurance manifest entries it read or checked for presence.
It unions the edges of the newest earlier map, so a function that a randomized
test reaches only on some runs stays mapped. Run it nightly; automatic
selection runs the full suite without a usable map.
"""
from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
import contextlib
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

import lake_outputs
from layer_policy import ROOT, lean_default_targets, lean_executables
import nested_pytest
import test_map_recorder

# 2: directory listings by the import system and pytest are not recorded.
# 3: a test's own reads and listings count even though pytest runs it (version 2
#    dropped any made with a pytest frame anywhere on the stack), so earlier maps
#    lack edges and are not used.
# 4: listings of directories that hold no tracked file (or do not exist yet) are kept.
# 5: the assurance-manifest operations each test reads are recorded (`operations`).
# 6: an operation only checked for presence (`presence`) is recorded apart from an entry read.
# 7: each request's Lean service mode is recorded separately from its executable.
VERSION = 7
# How maps of each format version became usable when it was introduced: ("converter", N - 1), a
# converter in CONVERTERS from the version before; or ("recorded", commit), a map recorded with it at
# that main commit and published with the change. A version with neither leaves selection without a
# map until one is recorded (a test in tests/test_select_tests.py fails when VERSION has no entry).
FORMAT_CHANGES = {7: ("converter", 6)}
EDGE_KEYS = ("f", "r", "d", "x", "m", "p", "v")
# Seconds one test file may run while recorded: a hang guard, not a budget. At one hour the
# heaviest files (test_assist, test_assist_invariants, test_wire_gate_corpus) timed out on the
# loaded VM and stayed unrecorded; they start first (`by_length`).
UNIT_TIMEOUT = 4 * 3600
# Test units outside pytest: the selector's own unittest suite.
EXTRA_UNITS = {"tools/test_layer_policy.py": ["uv", "run", "--frozen", "--group", "dev", "python",
                                               "tools/test_layer_policy.py"]}


def cache_dir() -> Path:
    return Path(os.environ.get("VE_TESTMAP_CACHE") or Path.home() / ".cache/ve-testmap")


def builds_dir() -> Path:
    """Where this machine records the digests of its Lean builds (`record_build`). Kept apart from
    the maps, which travel between machines: a digest is a fact about one platform's build."""
    return Path(os.environ.get("VE_LEAN_BUILDS") or Path.home() / ".cache/ve-lean-builds")


def git(*args: str, root: Path = ROOT, check: bool = True) -> str:
    return subprocess.run(("git", *args), cwd=root, text=True, capture_output=True,
                          check=check).stdout.strip()


def units(root: Path = ROOT) -> list[str]:
    return sorted(p.relative_to(root).as_posix()
                  for p in (root / "tests").glob("test_*.py")) + sorted(EXTRA_UNITS)


def unit_command(unit: str, options: Sequence[str] = ()) -> list[str]:
    return EXTRA_UNITS.get(unit) or nested_pytest.command(["-q", "-p", "no:cacheprovider", *options, unit],
                                                          python=["uv", "run", "--frozen", "--group", "dev", "python"])


def environment(out: Path | None = None) -> dict[str, str]:
    env = nested_pytest.environment(os.environ)
    env.setdefault("UV_CACHE_DIR", "/tmp/ve-layers-uv-cache")
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", "")
    if out is not None:
        env.update(VE_NATIVE_PREBUILT="1", VE_LEAN_PREBUILT="1", VE_TESTMAP_OUT=str(out),
                   VE_TESTMAP_ROOT=str(ROOT.resolve()))
    return env


HOOK = test_map_recorder.HOOK


def site_packages() -> Path:
    """The project environment's site-packages, where the start hook goes."""
    found = subprocess.run(["uv", "run", "--frozen", "--group", "dev", "python", "-c",
                            "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
                           cwd=ROOT, env=environment(), text=True, capture_output=True, check=True)
    return Path(found.stdout.strip())


def install_hook(site: Path) -> None:
    """Start the recorder in each project-environment Python whose env sets VE_TESTMAP_OUT."""
    (site / f"{HOOK}.py").write_text(
        "import os, sys\n"
        "if os.environ.get('VE_TESTMAP_OUT'):\n"
        f"    sys.path.insert(0, {str(ROOT / 'tools')!r})\n"
        "    try:\n"
        "        import test_map_recorder\n"
        "        test_map_recorder.start()\n"
        "    finally:\n"
        "        sys.path.pop(0)\n")
    (site / f"{HOOK}.pth").write_text(f"import {HOOK}\n")


def remove_hook(site: Path) -> None:
    for suffix in (".pth", ".py"):
        (site / f"{HOOK}{suffix}").unlink(missing_ok=True)


def build_lean() -> None:
    """Build every Lean executable, then record the build's digests (`record_build`)."""
    env = environment()
    lake_outputs.drop_stale()  # a trace that does not record its binary would keep the stale one
    named = sorted(set(lean_executables()) - lean_default_targets())
    subprocess.run(["lake", "build"], cwd=ROOT / "lean", env=env, check=True, stdout=subprocess.DEVNULL)
    if named:  # executables outside the default targets
        subprocess.run(["lake", "build", *named], cwd=ROOT / "lean", env=env, check=True,
                       stdout=subprocess.DEVNULL)
    record_build()


def build_natives() -> None:
    """Build every binary once, so the per-file processes only read them."""
    build_lean()
    env = environment()
    for command in ([sys.executable, "tools/rust_build.py", "build", "--locked", "--release",
                     "--manifest-path", "rust/Cargo.toml"],
                    [sys.executable, "tools/rust_build.py", "build", "--locked",
                     "--manifest-path", "rust/Cargo.toml", "-p", "ve"]):
        subprocess.run(command, cwd=ROOT, env=env, check=True, stdout=subprocess.DEVNULL)


# --- Lean build digests: the binary-level cutoff of tools/select_tests.py ---
#
# A record names a `lean/` tree (git's tree id of the directory, untracked files included) and gives
# the SHA-256 of each Lean executable built from exactly that tree on this platform. Two records
# with equal digests for an executable mean the two trees built the same program: a test that only
# runs it behaves the same on both. Records are written only for a build that is current: Lake has
# nothing to rebuild for any executable, and every executable's trace records the file on disk.


def platform_tag() -> str:
    return f"{sys.platform}-{platform.machine()}"


def lean_tree(rev: str | None = None, root: Path = ROOT) -> str | None:
    """Git's tree id of `lean/` at `rev`, or in the working tree (None); None when there is none."""
    tree = working_tree_id(root) if rev is None else rev
    found = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{tree}:lean"], cwd=root,
                           capture_output=True, text=True)
    return found.stdout.strip() if found.returncode == 0 else None


def build_record_path(tree: str) -> Path:
    return builds_dir() / f"{platform_tag()}-{tree}.json"


def executable_digests(root: Path = ROOT) -> dict[str, str]:
    """SHA-256 of every built Lean executable the lakefile names."""
    found = {}
    for name in lean_executables(root):
        binary = root / "lean/.lake/build/bin" / name
        if binary.is_file():
            found[name] = hashlib.sha256(binary.read_bytes()).hexdigest()
    return found


def current_build(root: Path = ROOT) -> bool:
    """Whether every Lean executable on disk is the build of the sources as they are now."""
    names = sorted(lean_executables(root))
    if not names or not all((root / "lean/.lake/build/bin" / name).is_file() for name in names):
        return False
    check = subprocess.run(["lake", "build", "--no-build", *names], cwd=root / "lean", env=environment(),
                           capture_output=True)
    return check.returncode == 0 and not lake_outputs.stale(root / "lean")


def record_build(root: Path = ROOT) -> Path | None:
    """Record the current Lean build's digests under its `lean/` tree; None (nothing written) when the
    build is not current or the tree changed while it was hashed."""
    tree = lean_tree(None, root)
    if tree is None or not current_build(root):
        return None
    digests = executable_digests(root)
    if lean_tree(None, root) != tree:
        return None
    path = build_record_path(tree)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps({"lean_tree": tree, "platform": platform_tag(), "digests": digests,
                                     "recorded": datetime.datetime.now(datetime.timezone.utc).isoformat(
                                         timespec="seconds")}, indent=1, sort_keys=True) + "\n")
    temporary.replace(path)
    return path


def load_build(tree: str | None) -> dict[str, str] | None:
    """The executable digests recorded for a `lean/` tree on this platform, or None."""
    if tree is None:
        return None
    try:
        data = json.loads(build_record_path(tree).read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("lean_tree") != tree or data.get("platform") != platform_tag():
        return None
    digests = data.get("digests")
    if not isinstance(digests, dict) or not all(isinstance(k, str) and isinstance(v, str)
                                                for k, v in digests.items()):
        return None
    return digests


def tracked_paths(root: Path = ROOT) -> set[str]:
    """Tracked files: the only files whose reads a map keeps."""
    return set(git("ls-files", "-z", root=root).split("\0")) - {""}


def read_unit(directory: Path, files: set[str]) -> dict:
    """Fold one unit's per-process records into sets of paths.

    Reads count for tracked files only; listings count for every directory
    under the root, including ones that hold no tracked file or do not exist
    yet: adding the first file there changes what the test listed.
    """
    seen = {key: set() for key in EDGE_KEYS}
    children, opaque, written = [], [], set()
    for path in directory.glob("*.jsonl"):
        written.add(int(path.stem))
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                opaque.append(f"truncated record in {path.name}")  # killed mid-write
                continue
            kind = record[0]
            if kind == "f":
                seen["f"].add((record[1], record[2]))
            elif kind == "r" and record[1] in files:
                seen["r"].add(record[1])
            elif kind == "d":
                seen["d"].add(record[1])
            elif kind == "x":
                seen["x"].add(record[1])
            elif kind == "m":
                seen["m"].add(record[1])
            elif kind == "p":
                seen["p"].add(record[1])
            elif kind == "v":
                seen["v"].add(record[1])
            elif kind == "c" and record[2]:
                children.append((record[1], len(record) > 3 and record[3] is True))
            elif kind == "o":
                opaque.append(record[1])
    # A child that records here and left no file died before its recorder started: it ran no code.
    opaque += [f"python child {pid} left no record" for pid, here in children if pid not in written and not here]
    return {**seen, "opaque": sorted(set(opaque))}


STOP_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


class Stop:
    """Ends a recorded run early: after `stop()` no unit starts, and each running unit's process group is
    killed. Each unit runs in its own session, so its group holds every process it started; for the same
    reason a run must stop its units itself when it ends abnormally (`on_exit`)."""

    def __init__(self):
        self._lock = threading.Lock()
        self._running: set[subprocess.Popen] = set()
        self._killed: set[subprocess.Popen] = set()
        self.stopped = False

    def start(self, command: list[str], **options) -> subprocess.Popen | None:
        with self._lock:
            if self.stopped:
                return None
            process = subprocess.Popen(command, start_new_session=True, **options)
            self._running.add(process)
            return process

    def finished(self, process: subprocess.Popen) -> bool:
        """Forget `process`; whether `stop()` killed it."""
        with self._lock:
            self._running.discard(process)
            return process in self._killed

    def stop(self) -> None:
        with self._lock:
            self.stopped = True
            for process in self._running:
                kill_group(process)
                self._killed.add(process)

    @contextlib.contextmanager
    def on_exit(self):
        """Stop when the block raises or the process is interrupted, terminated or hung up. A signal to the
        run's own process group (a harness timeout, Ctrl-C, a closed terminal) does not reach the units'
        sessions, so the run kills them itself, before it waits for its workers. Signal handlers go in only
        on the main thread, where Python runs them; an ignored signal stays ignored."""
        previous = {}

        def handler(number, frame):
            self.stop()
            earlier = previous[number]
            if callable(earlier):
                return earlier(number, frame)  # Ctrl-C's KeyboardInterrupt, or the caller's own handler
            raise SystemExit(128 + number)

        if threading.current_thread() is threading.main_thread():
            for number in STOP_SIGNALS:
                earlier = signal.getsignal(number)
                if earlier is not None and earlier != signal.SIG_IGN:
                    previous[number] = earlier
                    signal.signal(number, handler)
        try:
            yield self
        except BaseException:
            self.stop()
            raise
        finally:
            for number, earlier in previous.items():
                signal.signal(number, earlier)


def kill_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run_unit(unit: str, work: Path, timeout: float, tracked: set[str], *, options: Sequence[str] = (),
             stop: Stop | None = None) -> dict | None:
    """Record one unit, or reuse its finished result from an interrupted run. With `stop`: None when the run
    stopped before the unit started, and exit "stopped" (nothing saved) when it stopped while it ran."""
    name = unit.replace("/", "__")
    out, done, log = work / name, work / f"{name}.result.json", work / f"{name}.log"
    if done.exists():
        result = json.loads(done.read_text())
        for key in EDGE_KEYS:
            result[key] = {tuple(item) for item in result[key]} if key == "f" else set(result[key])
        return result
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    start = time.monotonic()
    stop = stop or Stop()
    env = environment(out)
    with log.open("w") as handle, stop.on_exit():
        process = stop.start(unit_command(unit, options), cwd=ROOT, env=env, stdout=handle,
                             stderr=subprocess.STDOUT)
        if process is None:
            shutil.rmtree(out)
            return None
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_group(process)
            process.wait()
            code = "timeout"
        if stop.finished(process):
            share_with_outer(out, env)
            shutil.rmtree(out)
            return {"exit": "stopped", "seconds": round(time.monotonic() - start, 1)}
    result = read_unit(out, tracked)
    result.update(exit=code, seconds=round(time.monotonic() - start, 1))
    done.write_text(json.dumps({key: sorted(value) if isinstance(value, set) else value
                                for key, value in result.items()}))
    share_with_outer(out, env)
    shutil.rmtree(out)
    return result


def share_with_outer(out: Path, env: dict[str, str]) -> None:
    """A recording made inside a recorded test (the selector's own tests run units this way) hands that
    test's recording the records of the processes it started. They ran code under the same root for the
    outer test too; without them the outer recorder sees Python children that wrote elsewhere, and the
    outer unit is opaque. Records are appended, so a process id used twice keeps both."""
    outer = os.environ.get("VE_TESTMAP_OUT")
    if not outer or not Path(outer).is_dir() or Path(outer).resolve() == out.resolve() \
            or os.path.realpath(os.environ.get("VE_TESTMAP_ROOT", "")) != os.path.realpath(env["VE_TESTMAP_ROOT"]):
        return
    for path in out.glob("*.jsonl"):
        with (Path(outer) / path.name).open("ab") as handle:
            handle.write(path.read_bytes())


def by_length(selected: list[str], previous: dict | None) -> list[str]:
    """The units in recording order: longest first by the seconds `previous` recorded (an unknown unit
    counts as longest), so the slowest files do not start last. Order only: every unit runs."""
    seconds = {test: status["seconds"] for test, status in (previous or {}).get("status", {}).items()}
    return sorted(selected, key=lambda unit: (-seconds.get(unit, float("inf")), unit))


def build_map(results: dict[str, dict], commit: str) -> dict:
    tests = sorted(results)
    index = {test: i for i, test in enumerate(tests)}
    functions: dict[str, dict[str, set[int]]] = {}
    reads: dict[str, set[int]] = {}
    dirs: dict[str, set[int]] = {}
    programs: dict[str, set[int]] = {}
    operations: dict[str, set[int]] = {}
    presence: dict[str, set[int]] = {}
    modes: dict[str, set[int]] = {}
    for test, result in results.items():
        i = index[test]
        for file, qualname in result["f"]:
            functions.setdefault(file, {}).setdefault(qualname, set()).add(i)
        for table, key in ((reads, "r"), (dirs, "d"), (programs, "x")):
            for item in result[key]:
                table.setdefault(item, set()).add(i)
        for op_id in result.get("m", ()):
            operations.setdefault(op_id, set()).add(i)
        for op_id in result.get("p", ()):
            presence.setdefault(op_id, set()).add(i)
        for mode in result.get("v", ()):
            modes.setdefault(mode, set()).add(i)
    return {
        "version": VERSION, "commit": commit,
        "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "tests": tests,
        "status": {test: {"exit": results[test]["exit"], "seconds": results[test]["seconds"],
                          "opaque": results[test]["opaque"]} for test in tests},
        "functions": {f: {q: sorted(s) for q, s in sorted(qs.items())} for f, qs in sorted(functions.items())},
        "reads": {k: sorted(v) for k, v in sorted(reads.items())},
        "dirs": {k: sorted(v) for k, v in sorted(dirs.items())},
        "programs": {k: sorted(v) for k, v in sorted(programs.items())},
        "operations": {k: sorted(v) for k, v in sorted(operations.items())},
        "presence": {k: sorted(v) for k, v in sorted(presence.items())},
        "modes": {k: sorted(v) for k, v in sorted(modes.items())},
    }


def unit_edges(data: dict) -> dict[str, dict]:
    """Invert a map back to per-test sets (the form `merge` and tests use)."""
    tests = data["tests"]
    edges = {test: {"f": set(), "r": set(), "d": set(), "x": set(), "m": set(), "p": set(), "v": set()}
             for test in tests}
    for file, qualnames in data["functions"].items():
        for qualname, indices in qualnames.items():
            for i in indices:
                edges[tests[i]]["f"].add((file, qualname))
    for table, key in (("reads", "r"), ("dirs", "d"), ("programs", "x")):
        for item, indices in data[table].items():
            for i in indices:
                edges[tests[i]][key].add(item)
    for item, indices in data["operations"].items():
        for i in indices:
            edges[tests[i]]["m"].add(item)
    for item, indices in data["presence"].items():
        for i in indices:
            edges[tests[i]]["p"].add(item)
    for item, indices in data["modes"].items():
        for i in indices:
            edges[tests[i]]["v"].add(item)
    return edges


def merge(results: dict[str, dict], previous: dict) -> None:
    """Add an earlier map's edges for units that still exist and passed both times."""
    old = unit_edges(previous)
    for test, result in results.items():
        if test in old and result["exit"] in (0, 5) and previous["status"][test]["exit"] in (0, 5):
            for key in EDGE_KEYS:
                result[key] |= old[test][key]


def tree_map_path(tree: str) -> Path:
    return cache_dir() / f"tree-{tree}.json.gz"


def working_tree_id(root: Path = ROOT) -> str:
    """Git tree id of the working tree: tracked and untracked-but-not-ignored files as they are now."""
    index = Path(git("rev-parse", "--git-path", "index", root=root))
    index = index if index.is_absolute() else root / index
    with tempfile.TemporaryDirectory() as directory:
        copy = Path(directory) / "index"
        if index.exists():
            shutil.copy(index, copy)
        env = {**os.environ, "GIT_INDEX_FILE": str(copy)}
        subprocess.run(["git", "add", "-A"], cwd=root, env=env, check=True, capture_output=True)
        return subprocess.run(["git", "write-tree"], cwd=root, env=env, check=True,
                              capture_output=True, text=True).stdout.strip()


def find_map(base: str, root: Path = ROOT, other_versions: list[Path] | None = None) -> Path | None:
    """The cached map nearest below `base`: of the 30 newest maps recorded at commits, the one at an
    ancestor of `base` with the fewest commits between it and `base`. $VE_TESTMAP overrides. Maps
    `--run` saved for a tree (`tree-*`, `tree_map_path`) name no commit and never qualify, so they
    are left out before the 30 are counted.

    A nearer ancestor map that does not load is skipped with a line on stderr;
    one recorded by another map format version is also appended to `other_versions`."""
    if os.environ.get("VE_TESTMAP"):
        return Path(os.environ["VE_TESTMAP"])
    directory = cache_dir()
    if not directory.is_dir():
        return None
    best = None
    commit_maps = [path for path in directory.glob("*.json.gz") if not path.name.startswith("tree-")]
    for path in sorted(commit_maps, key=lambda p: p.stat().st_mtime, reverse=True)[:30]:
        commit = path.name.split(".", 1)[0]
        distance = subprocess.run(("git", "rev-list", "--count", f"{commit}..{base}"), cwd=root,
                                  capture_output=True, text=True)
        if distance.returncode or subprocess.run(
                ("git", "merge-base", "--is-ancestor", commit, base), cwd=root,
                capture_output=True).returncode:
            continue
        if best is None or int(distance.stdout) < best[0]:
            try:
                load(path)
            except MapVersionError as error:
                print(f"test_map: skipped map {path} for {base[:10]}: recorded by map format version "
                      f"{error.found}, this checkout reads version {VERSION} "
                      "(record a new map: tools/test_map.py record)", file=sys.stderr)
                if other_versions is not None:
                    other_versions.append(path)
                continue
            except (OSError, ValueError, EOFError) as error:
                print(f"test_map: skipped map {path}: unreadable ({error})", file=sys.stderr)
                continue
            best = (int(distance.stdout), path)
    return best[1] if best else None


def load(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        data = convert(json.load(handle))
    validate(data, str(path))
    return data


def from_6(data: dict) -> dict:
    """Version 7 records each unit's Lean service modes; a version 6 map recorded none. With no
    mode recorded, every service user stays in every service selection (`Coverage.service_users`),
    so the map selects at least what it did before."""
    return {**data, "modes": {}}


# Converters to each version from the one before it (FORMAT_CHANGES names which apply).
CONVERTERS = {7: from_6}


def convert(data):
    """A map of an earlier format version, converted to VERSION in place, when each version after it
    has a converter; anything else is returned as it is (validate then names the version)."""
    if not isinstance(data, dict) or type(data.get("version")) is not int:
        return data
    found = data["version"]
    if found >= VERSION or any(version not in CONVERTERS for version in range(found + 1, VERSION + 1)):
        return data
    for version in range(found + 1, VERSION + 1):
        data.update(CONVERTERS[version](data), version=version)
    data["converted_from"] = found
    return data


class MapVersionError(ValueError):
    """A well-formed map header recorded by another map format version."""
    def __init__(self, message: str, found: int):
        super().__init__(message)
        self.found = found


def validate(data, where: str = "map") -> None:
    """Reject a map that `build_map` could not have written; raises ValueError."""
    def fail(reason: str):
        raise ValueError(f"{where}: {reason}")

    def strings(value, what):
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            fail(f"{what} is not a list of strings")

    def indices(value, what):
        if not isinstance(value, list) or not value or not all(
                type(i) is int and 0 <= i < len(tests) for i in value):
            fail(f"{what} is not a non-empty list of test indices")

    if isinstance(data, dict) and type(data.get("version")) is int and data["version"] != VERSION:
        raise MapVersionError(f"{where}: version {data['version']!r}, expected {VERSION}", data["version"])
    if not isinstance(data, dict) or data.get("version") != VERSION:
        fail(f"version {data.get('version') if isinstance(data, dict) else None!r}, expected {VERSION}")
    if not isinstance(data.get("commit"), str):
        fail("commit is not a string")
    tests = data.get("tests")
    strings(tests, "tests")
    if len(set(tests)) != len(tests):
        fail("duplicate test")
    status = data.get("status")
    if not isinstance(status, dict) or set(status) != set(tests):
        fail("status does not name exactly the tests")
    for test, entry in status.items():
        if not isinstance(entry, dict) or type(entry.get("exit")) not in (int, str) \
                or type(entry.get("seconds")) not in (int, float) or not isinstance(entry.get("opaque"), list):
            fail(f"status of {test} is malformed")
    functions = data.get("functions")
    if not isinstance(functions, dict):
        fail("functions is not an object")
    for file, qualnames in functions.items():
        if not isinstance(qualnames, dict):
            fail(f"functions of {file} is not an object")
        for qualname, value in qualnames.items():
            indices(value, f"{file}:{qualname}")
    for table in ("reads", "dirs", "programs", "operations", "presence", "modes"):
        if not isinstance(data.get(table), dict):
            fail(f"{table} is not an object")
        for key, value in data[table].items():
            indices(value, f"{table}[{key}]")
    # A unit recorded as passing ran code: at least its own module.
    ran = {i for qualnames in functions.values() for value in qualnames.values() for i in value}
    silent = [test for i, test in enumerate(tests)
              if status[test]["exit"] in (0, 5) and not status[test]["opaque"] and i not in ran]
    if silent:
        fail(f"{len(silent)} passing units ran no recorded code, e.g. {silent[0]}")


def failed_unit(unit: str, result: dict) -> int:
    """The failures a finished unit counts towards `stop_after`: one when it did not pass."""
    return int(result["exit"] not in (0, 5))


def record_units(selected: list[str], work: Path, jobs: int, timeout: float, *,
                 options: Callable[[str], Sequence[str]] = lambda unit: (), stop_after: int = 0,
                 failures: Callable[[str, dict], int] = failed_unit) -> dict[str, dict]:
    """Run each unit in its own recorded process, starting them in the order of `selected`; a rerun resumes
    from `work`. With `stop_after` N > 0 the run stops once its finished units count N `failures`: no other
    unit starts and the running ones are killed, as they are when the run is interrupted, terminated or
    hung up (`Stop.on_exit`). Only the units that ran to the end have a result."""
    work.mkdir(parents=True, exist_ok=True)
    tracked = tracked_paths()
    print(f"recording {len(selected)} units with {jobs} jobs in {work}", flush=True)
    stop, lock, failed = Stop(), threading.Lock(), 0

    def one(unit):
        nonlocal failed
        result = run_unit(unit, work, timeout, tracked, options=options(unit), stop=stop)
        if result is None or result["exit"] == "stopped":
            return unit, None
        print(f"  {unit}: exit {result['exit']} in {result['seconds']} s, "
              f"{len(result['f'])} functions{', OPAQUE' if result['opaque'] else ''}", flush=True)
        # Counted before this worker takes its next unit, so that unit sees the stop.
        with lock:
            failed += failures(unit, result)
            if stop_after and failed >= stop_after and not stop.stopped:
                print(f"stopping after {failed} failed tests (--maxfail {stop_after})", flush=True)
                stop.stop()
        return unit, result

    site = site_packages()
    install_hook(site)
    pool = ThreadPoolExecutor(jobs)
    try:
        with stop.on_exit():
            results = dict(pool.map(one, selected))
    finally:
        pool.shutdown(cancel_futures=True)
        remove_hook(site)
    return {unit: result for unit, result in results.items() if result is not None}


def write_map(data: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    with gzip.open(temporary, "wt", encoding="utf-8") as handle:
        json.dump(data, handle, separators=(",", ":"))
    temporary.replace(output)


def clean_head(args: argparse.Namespace) -> str | None:
    if git("status", "--porcelain", "--untracked-files=no") and not args.allow_dirty:
        print("refusing to record a map for a modified tree; commit first or pass --allow-dirty",
              file=sys.stderr)
        return None
    return git("rev-parse", "HEAD")


def finish(args: argparse.Namespace, work: Path, data: dict, recorded: list[str]) -> int:
    output = Path(args.output) if args.output else cache_dir() / f"{data['commit']}.json.gz"
    write_map(data, output)
    failed = [unit for unit in recorded if data["status"][unit]["exit"] not in (0, 5)]
    print(f"wrote {output} ({output.stat().st_size // 1024} KiB); recorded {len(recorded)} units; "
          f"{len(failed)} failed and are left to the static graph: {failed}")
    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)
    else:
        print(f"kept results and logs in {work}")
    return 0


def record(args: argparse.Namespace) -> int:
    commit = clean_head(args)
    if commit is None:
        return 2
    if not args.no_build:
        build_natives()
    selected = args.units or units()
    work = Path(args.work) if args.work else Path(tempfile.gettempdir()) / f"ve-testmap-{commit}"
    previous_path = find_map(commit)
    previous = load(previous_path) if previous_path is not None else None
    results = record_units(by_length(selected, previous), work, args.jobs, args.timeout)
    if previous is not None and not args.no_merge:
        merge(results, previous)
    return finish(args, work, build_map(results, commit), selected)


def update(args: argparse.Namespace) -> int:
    """Re-record only the units whose coverage may have changed since the nearest map."""
    commit = clean_head(args)
    if commit is None:
        return 2
    previous_path = find_map(commit)
    if previous_path is None:
        print("no cached map is an ancestor of HEAD; run `record` first", file=sys.stderr)
        return 1
    previous = load(previous_path)
    import select_tests  # the selector decides which recorded edges still hold
    import source_graph
    coverage = select_tests.Coverage(previous, previous_path)
    everything = set(units())
    uncertain, drift = select_tests.uncertain_since(coverage, source_graph.load(ROOT), everything, commit)
    redo = sorted(uncertain | (everything - coverage.recorded))
    print(f"map {previous['commit'][:10]} is {drift} changed files behind; "
          f"{len(redo)} of {len(everything)} units need recording", flush=True)
    if args.dry_run:
        print("\n".join(redo))
        return 0
    if redo and not args.no_build:
        build_natives()
    work = Path(args.work) if args.work else Path(tempfile.gettempdir()) / f"ve-testmap-{commit}"
    results = record_units(by_length(redo, previous), work, args.jobs, args.timeout) if redo else {}
    edges = unit_edges(previous)
    for unit in sorted(everything - set(redo)):
        # Runs the same as when recorded: none of what it executed or read has changed.
        results[unit] = {**edges[unit], **previous["status"][unit]}
    data = build_map(results, commit)
    data["updated_from"] = previous["commit"]
    return finish(args, work, data, redo)


def fresh(base: str, max_age_hours: float, max_behind: int | None = None,
          now: datetime.datetime | None = None) -> int:
    """The freshness check for scripts that choose between selected and full runs: the map `find_map`
    gives `base` (a commit map of this format version, at an ancestor), no older than `max_age_hours`
    and at most `max_behind` commits below `base`. Prints its path and exits 0, or says why not on
    stderr and exits 1, so `fresh=$(... 2>/dev/null)` is empty exactly when there is no fresh map.
    A file's age in the cache says nothing of whether selection can use it."""
    path = find_map(base)
    if path is None:
        print(f"no usable map for {base}: none of this format version (version {VERSION}) at an ancestor",
              file=sys.stderr)
        return 1
    data = load(path)
    behind = int(git("rev-list", "--count", f"{data['commit']}..{base}"))
    try:
        created = datetime.datetime.fromisoformat(data["created"])
    except (KeyError, TypeError, ValueError):
        print(f"map {path} for {base}: no creation time", file=sys.stderr)
        return 1
    age = ((now or datetime.datetime.now(datetime.timezone.utc)) - created).total_seconds() / 3600
    if age > max_age_hours:
        print(f"map {path} for {base}: {age:.1f} h old, more than {max_age_hours:g} h", file=sys.stderr)
        return 1
    if max_behind is not None and behind > max_behind:
        print(f"map {path} for {base}: {behind} commits behind, more than {max_behind}", file=sys.stderr)
        return 1
    print(path)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record", help="record a map for HEAD")
    rec.add_argument("--jobs", type=int, default=8)
    rec.add_argument("--timeout", type=float, default=UNIT_TIMEOUT, help="seconds per test file")
    rec.add_argument("--output", help="map path (default: the shared cache)")
    rec.add_argument("--allow-dirty", action="store_true")
    rec.add_argument("--no-build", action="store_true", help="binaries are already built")
    rec.add_argument("--no-merge", action="store_true", help="do not union the previous map")
    rec.add_argument("--work", help="directory for per-unit results; a rerun resumes from it "
                     "(default: a per-commit directory under the system temporary directory)")
    rec.add_argument("--keep", action="store_true", help="keep per-unit results and logs")
    rec.add_argument("units", nargs="*", help="record only these units (for checks)")
    upd = sub.add_parser("update", help="re-record only the units whose coverage changed since "
                         "the nearest earlier map (run after each merge to main)")
    for option in rec._actions[1:]:
        if option.dest not in ("units", "no_merge"):
            upd._add_action(option)
    upd.add_argument("--dry-run", action="store_true", help="list the units, record nothing")
    show = sub.add_parser("show", help="summarize the map used for HEAD")
    show.add_argument("--map")
    fresh_parser = sub.add_parser("fresh", help="exit 0 and print the map selection would use for --base, "
                                  "when there is one and it is recent enough; else exit 1 and say why")
    fresh_parser.add_argument("--base", default="HEAD", help="the base selection compares with (default HEAD)")
    fresh_parser.add_argument("--max-age-hours", type=float, default=24.0,
                              help="the oldest map creation time accepted (default 24)")
    fresh_parser.add_argument("--max-behind", type=int, default=None,
                              help="the most commits accepted between the map and --base (default: any)")
    sub.add_parser("build-record", help="record the digests of the current Lean build for its lean/ tree "
                   "(the binary cutoff's input; exit 1 when the build is not current)")
    args = parser.parse_args()
    if args.command == "record":
        return record(args)
    if args.command == "update":
        return update(args)
    if args.command == "fresh":
        return fresh(args.base, args.max_age_hours, args.max_behind)
    if args.command == "build-record":
        path = record_build()
        print(f"recorded {path}" if path else "the Lean build is not current for this tree: nothing recorded")
        return 0 if path else 1
    path = Path(args.map) if args.map else find_map("HEAD")
    if path is None:
        print("no cached map is an ancestor of HEAD")
        return 1
    data = load(path)
    print(json.dumps({"path": str(path), "commit": data["commit"], "created": data["created"],
                      "tests": len(data["tests"]),
                      "failed": [t for t, s in data["status"].items() if s["exit"] not in (0, 5)],
                      "opaque": [t for t, s in data["status"].items() if s["opaque"]],
                      "seconds": round(sum(s["seconds"] for s in data["status"].values()))},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
