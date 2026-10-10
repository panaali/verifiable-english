"""A cache for a nested pytest run whose output is a function of what it reads: `cached_run`.

`tests/test_wire_gate_corpus.py` re-runs 32 test files under the contract input recorder (about 1,180 s of
tests that the outer suite also runs) to record the inputs they submit. That record is cached here, under
a key of everything the run can read:

* static: the content of the starting files (the recorded test files and the plugins and modules that run
  them) and of every Python file their imports reach (`tools/source_graph.py`, with the `conftest.py` files
  above them); the gate's Lean binaries and the Rust binary; the tracked Lean sources, toolchain, lakefile
  and manifest (tests run `lake env lean` on scripts that read the built modules); the interpreter's
  version, `uv.lock`, the run's settings, and its `VE_` environment and `PYTHONPATH` but its output paths;
* dynamic, recorded by `tests/read_recorder.py` in every process of the run that made the entry: each file
  it opened or imported, each directory it listed (by its entries' names) and each program it started.

An entry is named by the static key and holds the dynamic inputs' digests; it is used only when every one
of them is unchanged, so a stale key or a changed read re-runs. Only a run that `ok` accepts is stored, and
only when the static inputs did not change while it ran. `VE_RUN_CACHE=off` turns the cache off; a path
puts it there. By default it is in the git common directory, shared by the checkout's worktrees.
`tests/test_run_cache.py` changes each kind of keyed input and checks that the entry is not used.
"""
from __future__ import annotations

from collections.abc import Callable
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FORMAT = "ve-run-cache@1"
# Entries kept per cache directory, newest first (the wire gate corpus's is about 10 MB compressed).
KEEP = 4
# The settings that name the run's own output (a fresh temporary path each run), not an input: the record,
# the reads, the gate's and the profiler's outputs, and the English comparator's log (tests/conftest.py).
OUTPUT_SETTINGS = ("VE_CONTRACT_INPUTS", "VE_RECORD_READS", "VE_READS_ROOT", "VE_GATE_PYTEST_RESULT",
                   "VE_GATE_PYTEST_PROGRESS", "VE_TEST_PROFILE_DIR", "VE_RUN_CACHE", "VE_ENGLISH_COMPARATOR_DIR",
                   "VE_SHADOW_LOG")
LEAN_INPUTS = ("lakefile.toml", "lakefile.lean", "lake-manifest.json", "lean-toolchain")
PLUGIN = "tests.read_recorder"


def cache_directory(root: Path = ROOT) -> Path | None:
    """Where entries are kept (`VE_RUN_CACHE`, else the git common directory's `ve-run-cache`), or None
    when the cache is off."""
    setting = os.environ.get("VE_RUN_CACHE")
    if setting == "off":
        return None
    if setting:
        return Path(setting)
    from tests.subprocesses import HANG_TIMEOUT
    found = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root,
                           capture_output=True, text=True, timeout=HANG_TIMEOUT)
    return Path(found.stdout.strip()) / "ve-run-cache" if found.returncode == 0 and found.stdout.strip() else None


def file_digest(path: Path) -> str:
    if not path.is_file():
        return "absent"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def listing_digest(path: Path) -> str:
    try:
        names = sorted(os.listdir(path))
    except OSError:
        return "absent"
    return hashlib.sha256("\n".join(names).encode("utf-8", "surrogateescape")).hexdigest()


def rust_binary(root: Path, environment: dict) -> Path:
    return Path(environment.get("VE_RUST_BINARY") or root / "rust/target/release/ve")


def static_inputs(root: Path, starts: list[str], settings: dict, environment: dict) -> dict[str, str]:
    """{input: digest} of the static inputs (the module docstring)."""
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import source_graph
    finally:
        sys.path.remove(str(ROOT / "tools"))
    from tools.gate import LEAN_BINARIES
    graph = source_graph.load(root)
    python = set(starts)
    for start in starts:
        if start in graph.summaries:
            python |= graph.closure(start)[0]
    inputs = {f"file:{name}": file_digest(root / name) for name in sorted(python)}
    lean = [name for name in source_graph.tracked(root) if name.startswith("lean/")
            and (name.endswith(".lean") or name.rsplit("/", 1)[-1] in LEAN_INPUTS)]
    inputs.update((f"file:{name}", file_digest(root / name)) for name in lean)
    inputs.update((f"program:lean/.lake/build/bin/{name}", file_digest(root / "lean/.lake/build/bin" / name))
                  for name in LEAN_BINARIES)
    inputs["program:rust"] = file_digest(rust_binary(root, environment))
    inputs["file:uv.lock"] = file_digest(root / "uv.lock")
    inputs["python"] = sys.version
    inputs["settings"] = json.dumps(settings, sort_keys=True)
    inputs["environment"] = json.dumps(run_settings(root, environment))
    return inputs


def run_settings(root: Path, environment: dict) -> dict[str, str]:
    """The run's `VE_` settings and `PYTHONPATH`, but its output paths, with the checkout as `<root>` (so that
    worktrees share entries; what a path names is keyed by its content)."""
    return {name: value.replace(str(root), "<root>") for name, value in sorted(environment.items())
            if (name.startswith("VE_") or name == "PYTHONPATH") and name not in OUTPUT_SETTINGS}


def key_of(inputs: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps([FORMAT, sorted(inputs.items())]).encode()).hexdigest()


def dynamic_inputs(root: Path, reads: dict[str, set]) -> dict[str, str]:
    """{input: digest} of what the run read (`tests/read_recorder.py`)."""
    inputs = {f"file:{name}": file_digest(root / name) for name in reads["files"]}
    inputs.update((f"directory:{name}", listing_digest(root / name)) for name in reads["directories"])
    inputs.update((f"program:{name}", file_digest(root / name)) for name in reads["programs"])
    return dict(sorted(inputs.items()))


def current(root: Path, inputs: dict[str, str]) -> bool:
    """Whether every recorded dynamic input still has its digest."""
    for name, digest in inputs.items():
        kind, _, path = name.partition(":")
        now = listing_digest(root / path) if kind == "directory" else file_digest(root / path)
        if now != digest:
            return False
    return True


def _reads(prefix: Path) -> dict[str, set]:
    found = {"files": set(), "directories": set(), "programs": set()}
    for path in prefix.parent.glob(f"{prefix.name}.*.json"):
        for kind, names in json.loads(path.read_text()).items():
            found[kind].update(names)
    return found


def _write(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with gzip.open(temporary, "wt") as handle:
        json.dump(entry, handle)
    temporary.replace(path)
    entries = []
    for found in path.parent.glob("*.json.gz"):
        try:
            entries.append((found.stat().st_mtime, found))
        except OSError:  # removed by another run meanwhile
            pass
    for _, stale in sorted(entries, reverse=True)[KEEP:]:
        stale.unlink(missing_ok=True)


def cached_run(output: Path, *, starts: list[str], settings: dict, environment: dict,
               run: Callable[[dict], subprocess.CompletedProcess], ok: Callable[[subprocess.CompletedProcess], bool],
               root: Path = ROOT) -> tuple[subprocess.CompletedProcess, str]:
    """(the run's process, "hit", "miss" or "off"). `run(env)` runs pytest with `-p PLUGIN` in the environment
    `env` (`environment`, with the plugin's settings on a miss) and writes its output to `output`. On a hit,
    `output` gets the stored output and the process is the stored run's (its return code and output)."""
    directory = cache_directory(root)
    if directory is None:
        return run(dict(environment)), "off"
    inputs = static_inputs(root, starts, settings, environment)
    key = key_of(inputs)
    entry_path = directory / f"{key}.json.gz"
    try:
        with gzip.open(entry_path, "rt") as handle:
            entry = json.load(handle)
    except (OSError, ValueError, EOFError):
        entry = None
    if isinstance(entry, dict) and entry.get("format") == FORMAT and entry.get("key") == key \
            and isinstance(entry.get("dynamic"), dict) and current(root, entry["dynamic"]):
        output.write_text(entry["output"])
        entry_path.touch()
        return subprocess.CompletedProcess(entry["args"], entry["returncode"], entry["stdout"], entry["stderr"]), "hit"
    with tempfile.TemporaryDirectory(prefix="ve-reads-") as scratch:
        prefix = Path(scratch) / "reads"
        result = run({**environment, "VE_RECORD_READS": str(prefix), "VE_READS_ROOT": str(root)})
        reads = _reads(prefix)
    # Nothing recorded means the plugin did not run: no entry could be checked later.
    if ok(result) and reads["files"] and key_of(static_inputs(root, starts, settings, environment)) == key:
        _write(entry_path, {"format": FORMAT, "key": key, "static": inputs, "dynamic": dynamic_inputs(root, reads),
                            "output": output.read_text(), "args": [str(a) for a in result.args],
                            "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    return result, "miss"
