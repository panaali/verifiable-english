"""A pytest plugin that records what a run reads from the checkout, for `tools/run_cache.py`.

Loaded with `-p tests.read_recorder` and `VE_RECORD_READS=<prefix>`, it installs an audit hook (PEP 578) in
each pytest process (the controller and every xdist worker) before any test module is imported, and records,
relative to the checkout (`VE_READS_ROOT`, by default this repository):

* every file opened (the `open` event: `open()`, `Path.read_text`, `io.open_code`);
* every directory listed (`os.listdir`, `os.scandir`: `glob`, `Path.glob`, `Path.iterdir` and `os.walk`);
* every program started (`subprocess.Popen`, `os.posix_spawn`, `os.exec`);
* whether it read history (`history`): started git ("git") or opened a path in a `.git` directory (".git"),
  wherever it is, so the run cache binds the entry to the commit (`tools/run_cache.py`);
* at the end, the file of every module imported (`sys.modules`): an import from bytecode opens no source.

Each process writes `<prefix>.<pid>.json`: `{"files": [...], "directories": [...], "programs": [...],
"history": [...]}`. Files and directories under SKIPPED (the virtual environment, git, the native build
directories, caches) are not recorded as files, nor is the interpreter as a program: the run cache keys the
interpreter, the lock and the binaries. Like the reads, `history` is seen in the run's pytest processes only:
a child process those start runs without this hook.
"""

import json
import os
import sys

ROOT = os.path.realpath(os.environ.get("VE_READS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT = os.environ.get("VE_RECORD_READS")
SKIPPED = (".git", ".venv", "lean/.lake", "rust/target", ".cargo-home", ".pytest_cache", ".hypothesis", ".cache")
# A program is recorded wherever it is in the checkout (the Lean and Rust binaries are), but the interpreter.
PROGRAMS_SKIPPED = (".venv",)
_READS = {"files": set(), "directories": set(), "programs": set(), "history": set()}
GIT_PATH = os.sep + ".git"


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


def _starts_git(words) -> bool:
    """Whether a command starts git: its program, or any argument whose first word is git (`sh -c "git log"`);
    an argument that only names git binds the entry too, which is the safe side."""
    if isinstance(words, (str, bytes, os.PathLike)):
        words = [words]
    for word in words or ():
        if isinstance(word, (str, bytes, os.PathLike)):
            first = os.fsdecode(os.fspath(word)).split(maxsplit=1)
            if first and os.path.basename(first[0]) == "git":
                return True
    return False


def _git_path(path) -> bool:
    """Whether `path` is in a `.git` directory or is one (a worktree's `.git` file), wherever it is."""
    if isinstance(path, os.PathLike):
        path = os.fspath(path)
    if isinstance(path, bytes):
        path = os.fsdecode(path)
    if not isinstance(path, str) or not path:
        return False
    absolute = os.path.normpath(os.path.join(os.getcwd(), path))
    return absolute.endswith(GIT_PATH) or GIT_PATH + os.sep in absolute


def _hook(event, args):
    try:
        if event == "open":
            _add("files", args[0])
            if _git_path(args[0]):
                _READS["history"].add(".git")
        elif event in ("os.listdir", "os.scandir"):
            _add("directories", "." if args[0] is None else args[0])
        elif event == "subprocess.Popen":
            executable, argv, cwd = args[0], args[1], args[2]
            _program([executable] if executable else argv, os.fsdecode(cwd) if cwd else None)
            if _starts_git([executable]) or _starts_git(argv):
                _READS["history"].add("git")
        elif event in ("os.posix_spawn", "os.exec"):
            _program([args[0]])
            if _starts_git([args[0]]) or _starts_git(args[1]):
                _READS["history"].add("git")
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
