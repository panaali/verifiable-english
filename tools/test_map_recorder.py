"""Record what one process of a test-map run executes, reads and starts.

Each process appends JSON lines to `$VE_TESTMAP_OUT/<pid>.jsonl`, flushing
every line, so a child that a test kills still leaves what it did up to then:

  ["f", file, qualname]   a code object under the root started (sys.monitoring)
  ["r", file]             a file under the root was opened, other than by import
  ["d", directory]        a directory under the root was listed
  ["x", program, cwd]     a process was started; `program` is root-relative
                          when under the root, else its base name
  ["c", pid, python]      a child process id, and whether it runs Python
  ["o", reason]           something the recorder could not see into

Paths are relative to $VE_TESTMAP_ROOT. tools/test_map.py installs a `.pth`
hook in the project environment that calls `start()` whenever VE_TESTMAP_OUT
is set, so a Python child of the project environment records too: an explicit
`env=` gets the two recording variables added. A Python child that leaves no
record (another interpreter, or `-I`/`-E`) marks its test as opaque. A forked
child starts its own file and re-arms every code object.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

_state: dict = {}


def _relative(path) -> str | None:
    """Root-relative path of `path`, or None outside the root."""
    try:
        if isinstance(path, int) or path is None:
            return None
        path = os.fsdecode(path)
        absolute = os.path.normpath(os.path.join(os.getcwd(), path))
    except (TypeError, ValueError, OSError):
        return None
    root = _state["root"]
    if absolute == root:
        return "."
    if not absolute.startswith(root + os.sep):
        return None
    relative = absolute[len(root) + 1:]
    if relative.startswith((".venv" + os.sep, ".git" + os.sep)) or "__pycache__" in relative:
        return None
    return relative


def _emit(record) -> None:
    key = tuple(record)
    if key in _state["seen"]:
        return
    _state["seen"].add(key)
    _state["file"].write(json.dumps(record) + "\n")
    _state["file"].flush()


def _open_output() -> None:
    _state["file"] = open(os.path.join(_state["out"], f"{os.getpid()}.jsonl"), "a",
                          encoding="utf-8")
    _state["seen"] = set()


def _on_start(code, _offset):
    filename = code.co_filename
    if filename.startswith(_state["root"] + os.sep) and filename not in _state["own"]:
        relative = _relative(filename)
        if relative is not None:
            _emit(["f", relative, code.co_qualname])
    return sys.monitoring.DISABLE


def _python(program: str) -> bool:
    name = os.path.basename(program)
    return name.startswith("python") or os.path.realpath(program) == os.path.realpath(sys.executable)


def _audit(event, args):
    try:
        if event == "open":
            # Imports read sources and caches through importlib; those are not data reads.
            if sys._getframe(1).f_code.co_filename.startswith("<frozen importlib"):
                return
            relative = _relative(args[0])
            if relative is not None and not (relative.endswith(".py") and _source_lookup()):
                _emit(["r", relative])
        elif event in ("os.listdir", "os.scandir"):
            relative = _relative(args[0] if args else ".")
            if relative is not None:
                _emit(["d", relative])
        elif event in ("subprocess.Popen", "os.posix_spawn", "os.exec"):
            program, argv = os.fsdecode(args[0]), args[1]
            if isinstance(argv, (str, bytes)):
                argv = [argv]
            located = program if os.sep in program else (_which(program) or program)
            _emit(["x", _relative(located) or os.path.basename(program),
                   _relative(args[2] if event == "subprocess.Popen" and args[2] else ".")])
            for argument in list(argv or ())[1:]:
                if isinstance(argument, (str, bytes, os.PathLike)):
                    relative = _relative(argument)
                    if relative is not None and os.path.isfile(os.path.join(_state["root"], relative)):
                        _emit(["r", relative])
            if _python(program) and any(flag in ("-I", "-E", "-S") for flag in list(argv or ())[1:3]):
                _emit(["o", f"python child without the recorder: {argv!r}"])
    except Exception:  # an audit hook must never break the audited call
        pass


def _source_lookup() -> bool:
    """Is this open a traceback, warning or assertion-rewrite reading source lines?

    Those reads show code, they do not test it. `inspect.getsource` reads
    through linecache too, and a test may compare what it returns, so a read
    under `inspect` still counts.
    """
    frame, lookup = sys._getframe(2), False
    while frame is not None:
        name = frame.f_code.co_filename
        if name.endswith("inspect.py"):
            return False
        if name.endswith(("linecache.py", "traceback.py", "warnings.py")) or "/_pytest/" in name:
            lookup = True
        frame = frame.f_back
    return lookup


def _which(program: str) -> str | None:
    from shutil import which
    return which(program)


def _wrap_popen() -> None:
    original = subprocess.Popen.__init__

    def init(self, args, *rest, **kwargs):
        env = kwargs.get("env")
        argv = [args] if isinstance(args, (str, bytes, os.PathLike)) else list(args)
        program = os.fsdecode(kwargs.get("executable") or (argv[0] if argv else ""))
        python = _python(program) or os.path.basename(program) == "uv"
        if env is not None and python:
            env = dict(env)
            for name in ("VE_TESTMAP_OUT", "VE_TESTMAP_ROOT"):
                env[name] = os.environ[name]
            kwargs["env"] = env
        original(self, args, *rest, **kwargs)
        _emit(["c", self.pid, _python(program)])

    subprocess.Popen.__init__ = init


def _after_fork() -> None:
    _open_output()
    sys.monitoring.restart_events()


def start() -> None:
    if _state:
        return
    _state["root"] = os.path.realpath(os.environ["VE_TESTMAP_ROOT"])
    _state["out"] = os.environ["VE_TESTMAP_OUT"]
    _state["own"] = {os.path.abspath(__file__)}
    _open_output()
    monitoring = sys.monitoring
    tool = next(i for i in (4, 3, 2, 1, 0) if monitoring.get_tool(i) is None)
    monitoring.use_tool_id(tool, "ve-testmap")
    monitoring.register_callback(tool, monitoring.events.PY_START, _on_start)
    monitoring.set_events(tool, monitoring.events.PY_START)
    sys.addaudithook(_audit)
    _wrap_popen()
    os.register_at_fork(after_in_child=_after_fork)
