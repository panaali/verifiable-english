"""A pytest plugin that records what a run reads from the checkout, for `tools/run_cache.py`.

Loaded with `-p tests.read_recorder` and `VE_RECORD_READS=<prefix>`, it installs an audit hook (PEP 578) in
each pytest process (the controller and every xdist worker) before any test module is imported, and records,
relative to the checkout (`VE_READS_ROOT`, by default this repository):

* every file opened (the `open` event: `open()`, `Path.read_text`, `io.open_code`);
* every directory listed (`os.listdir`, `os.scandir`: `glob`, `Path.glob`, `Path.iterdir` and `os.walk`);
* every program started (`subprocess.Popen`, `os.posix_spawn`, `os.exec`);
* at the end, the file of every module imported (`sys.modules`): an import from bytecode opens no source.

Each process writes `<prefix>.<pid>.json`: `{"files": [...], "directories": [...], "programs": [...]}`. Files
and directories under SKIPPED (the virtual environment, git, the native build directories, caches) are not
recorded, nor is the interpreter as a program: the run cache keys the interpreter, the lock and the binaries.
"""

import json
import os
import sys

ROOT = os.path.realpath(os.environ.get("VE_READS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT = os.environ.get("VE_RECORD_READS")
SKIPPED = (".git", ".venv", "lean/.lake", "rust/target", ".cargo-home", ".pytest_cache", ".hypothesis", ".cache")
# A program is recorded wherever it is in the checkout (the Lean and Rust binaries are), but the interpreter.
PROGRAMS_SKIPPED = (".venv",)
_READS = {"files": set(), "directories": set(), "programs": set()}


def relative(path, base=None, skipped=SKIPPED):
    """`path` relative to ROOT, or None: outside it, under `skipped`, in a `__pycache__`, or not a path."""
    if isinstance(path, os.PathLike):
        path = os.fspath(path)
    if isinstance(path, bytes):
        path = os.fsdecode(path)
    if not isinstance(path, str) or not path:
        return None
    absolute = os.path.normpath(os.path.join(base or os.getcwd(), path))
    if absolute != ROOT and not absolute.startswith(ROOT + os.sep):
        absolute = os.path.realpath(absolute)
        if absolute != ROOT and not absolute.startswith(ROOT + os.sep):
            return None
    name = os.path.relpath(absolute, ROOT).replace(os.sep, "/")
    if "__pycache__" in name.split("/") or any(name == s or name.startswith(s + "/") for s in skipped):
        return None
    return name


def _add(kind, path, base=None):
    name = relative(path, base, PROGRAMS_SKIPPED if kind == "programs" else SKIPPED)
    if name is not None:
        _READS[kind].add(name)


def _program(argv, base=None):
    if isinstance(argv, (str, bytes, os.PathLike)):
        argv = [argv]
    if argv:
        first = argv[0]
        if isinstance(first, (str, bytes, os.PathLike)) and os.sep in os.fsdecode(os.fspath(first)):
            _add("programs", first, base)


def _hook(event, args):
    try:
        if event == "open":
            _add("files", args[0])
        elif event in ("os.listdir", "os.scandir"):
            _add("directories", "." if args[0] is None else args[0])
        elif event == "subprocess.Popen":
            executable, argv, cwd = args[0], args[1], args[2]
            _program([executable] if executable else argv, os.fsdecode(cwd) if cwd else None)
        elif event in ("os.posix_spawn", "os.exec"):
            _program([args[0]])
    except Exception:  # noqa: BLE001 - an audit hook must never change what the audited call does
        pass


if OUTPUT:
    sys.addaudithook(_hook)


def pytest_sessionfinish(session, exitstatus):
    if not OUTPUT:
        return
    for module in list(sys.modules.values()):
        _add("files", getattr(module, "__file__", None))
    with open(f"{OUTPUT}.{os.getpid()}.json", "w") as handle:
        json.dump({kind: sorted(names) for kind, names in _READS.items()}, handle)
