"""Record and load the per-test coverage map used by tools/select_tests.py.

`python3 tools/test_map.py record` runs every test file in its own pytest
process (and tools/test_layer_policy.py) with tools/test_map_recorder.py
loaded into each Python process of the project environment (through a `.pth`
hook that exists only while recording), then writes one map for the clean HEAD commit
to the shared cache (`$VE_TESTMAP_CACHE`, default ~/.cache/ve-testmap). The
map says, per test unit, which functions under the root it executed, which
files it read and which directories it listed, and which programs it started.
It unions the edges of the newest earlier map, so a function that a randomized
test reaches only on some runs stays mapped. Run it nightly; selection falls
back to the static import graph without a usable map.
"""
from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
import datetime
import gzip
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

from layer_policy import ROOT, lean_default_targets, lean_executables
import nested_pytest

# 2: directory listings by the import system and pytest are not recorded.
# 3: a test's own reads and listings count even though pytest runs it (version 2
#    dropped any made with a pytest frame anywhere on the stack), so earlier maps
#    lack edges and are not used.
# 4: listings of directories that hold no tracked file (or do not exist yet) are kept.
VERSION = 4
UNIT_TIMEOUT = 3600  # seconds one test file may run while recorded
# Test units outside pytest: the selector's own unittest suite.
EXTRA_UNITS = {"tools/test_layer_policy.py": ["uv", "run", "--frozen", "--group", "dev", "python",
                                               "tools/test_layer_policy.py"]}


def cache_dir() -> Path:
    return Path(os.environ.get("VE_TESTMAP_CACHE") or Path.home() / ".cache/ve-testmap")


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


HOOK = "_ve_testmap"


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


def build_natives() -> None:
    """Build every binary once, so the per-file processes only read them."""
    env = environment()
    named = sorted(set(lean_executables()) - lean_default_targets())
    for command, cwd in ((["lake", "build"], ROOT / "lean"),
                         (["lake", "build", *named] if named else None, ROOT / "lean"),
                         ([sys.executable, "tools/rust_build.py", "build", "--locked", "--release",
                           "--manifest-path", "rust/Cargo.toml"], ROOT),
                         ([sys.executable, "tools/rust_build.py", "build", "--locked",
                           "--manifest-path", "rust/Cargo.toml", "-p", "ve"], ROOT)):
        if command is None:
            continue  # no executable outside the default targets
        subprocess.run(command, cwd=cwd, env=env, check=True, stdout=subprocess.DEVNULL)


def tracked_paths(root: Path = ROOT) -> set[str]:
    """Tracked files: the only files whose reads a map keeps."""
    return set(git("ls-files", "-z", root=root).split("\0")) - {""}


def read_unit(directory: Path, files: set[str]) -> dict:
    """Fold one unit's per-process records into sets of paths.

    Reads count for tracked files only; listings count for every directory
    under the root, including ones that hold no tracked file or do not exist
    yet: adding the first file there changes what the test listed.
    """
    seen = {"f": set(), "r": set(), "d": set(), "x": set()}
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
            elif kind == "c" and record[2]:
                children.append(record[1])
            elif kind == "o":
                opaque.append(record[1])
    opaque += [f"python child {pid} left no record" for pid in children if pid not in written]
    return {**seen, "opaque": sorted(set(opaque))}


class Stop:
    """Ends a recorded run early: after `stop()` no unit starts, and each running unit's process group is
    killed. Each unit runs in its own session, so its group holds every process it started."""

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
        result["f"] = {tuple(item) for item in result["f"]}
        return {key: set(value) if key in ("r", "d", "x") else value for key, value in result.items()}
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    start = time.monotonic()
    stop = stop or Stop()
    with log.open("w") as handle:
        process = stop.start(unit_command(unit, options), cwd=ROOT, env=environment(out), stdout=handle,
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
            shutil.rmtree(out)
            return {"exit": "stopped", "seconds": round(time.monotonic() - start, 1)}
    result = read_unit(out, tracked)
    result.update(exit=code, seconds=round(time.monotonic() - start, 1))
    done.write_text(json.dumps({key: sorted(value) if isinstance(value, set) else value
                                for key, value in result.items()}))
    shutil.rmtree(out)
    return result


def build_map(results: dict[str, dict], commit: str) -> dict:
    tests = sorted(results)
    index = {test: i for i, test in enumerate(tests)}
    functions: dict[str, dict[str, set[int]]] = {}
    reads: dict[str, set[int]] = {}
    dirs: dict[str, set[int]] = {}
    programs: dict[str, set[int]] = {}
    for test, result in results.items():
        i = index[test]
        for file, qualname in result["f"]:
            functions.setdefault(file, {}).setdefault(qualname, set()).add(i)
        for table, key in ((reads, "r"), (dirs, "d"), (programs, "x")):
            for item in result[key]:
                table.setdefault(item, set()).add(i)
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
    }


def unit_edges(data: dict) -> dict[str, dict]:
    """Invert a map back to per-test sets (the form `merge` and tests use)."""
    tests = data["tests"]
    edges = {test: {"f": set(), "r": set(), "d": set(), "x": set()} for test in tests}
    for file, qualnames in data["functions"].items():
        for qualname, indices in qualnames.items():
            for i in indices:
                edges[tests[i]]["f"].add((file, qualname))
    for table, key in (("reads", "r"), ("dirs", "d"), ("programs", "x")):
        for item, indices in data[table].items():
            for i in indices:
                edges[tests[i]][key].add(item)
    return edges


def merge(results: dict[str, dict], previous: dict) -> None:
    """Add an earlier map's edges for units that still exist and passed both times."""
    old = unit_edges(previous)
    for test, result in results.items():
        if test in old and result["exit"] in (0, 5) and previous["status"][test]["exit"] in (0, 5):
            for key in ("f", "r", "d", "x"):
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


def find_map(base: str, root: Path = ROOT) -> Path | None:
    """The cached map nearest below `base`: of the maps recorded at its ancestors,
    the one with the fewest commits between it and `base`. $VE_TESTMAP overrides."""
    if os.environ.get("VE_TESTMAP"):
        return Path(os.environ["VE_TESTMAP"])
    directory = cache_dir()
    if not directory.is_dir():
        return None
    best = None
    for path in sorted(directory.glob("*.json.gz"), key=lambda p: p.stat().st_mtime, reverse=True)[:30]:
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
            except (OSError, ValueError, EOFError):
                continue  # unreadable, or recorded by another version of the recorder
            best = (int(distance.stdout), path)
    return best[1] if best else None


def load(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        data = json.load(handle)
    validate(data, str(path))
    return data


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
    for table in ("reads", "dirs", "programs"):
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
    unit starts and the running ones are killed. Only the units that ran to the end have a result."""
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
    try:
        with ThreadPoolExecutor(jobs) as pool:
            results = dict(pool.map(one, selected))
    finally:
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
    results = record_units(selected, work, args.jobs, args.timeout)
    previous = find_map(commit)
    if previous is not None and not args.no_merge:
        merge(results, load(previous))
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
    results = record_units(redo, work, args.jobs, args.timeout) if redo else {}
    edges = unit_edges(previous)
    for unit in sorted(everything - set(redo)):
        # Runs the same as when recorded: none of what it executed or read has changed.
        results[unit] = {**edges[unit], **previous["status"][unit]}
    data = build_map(results, commit)
    data["updated_from"] = previous["commit"]
    return finish(args, work, data, redo)


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
    args = parser.parse_args()
    if args.command == "record":
        return record(args)
    if args.command == "update":
        return update(args)
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
