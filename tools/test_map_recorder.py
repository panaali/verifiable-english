"""Record what one process of a test-map run executes, reads and starts.

Each process appends JSON lines to `$VE_TESTMAP_OUT/<pid>.jsonl`, flushing
every line, so a child that a test kills still leaves what it did up to then:

  ["f", file, qualname]   a code object under the root started (sys.monitoring)
  ["r", file]             a file under the root was opened, other than by import
  ["d", directory]        a directory under the root was listed by test code
                          (not by the import system or pytest itself)

`origin` decides who an open or a listing is for: the innermost frame of
code under the root or of infrastructure (import system, site, pytest).
  ["x", program, cwd]     a process was started; `program` is root-relative
                          when under the root, else its base name
  ["c", pid, python, here]  a child process id, whether it runs Python, and whether
                          it records here: this environment's interpreter with this
                          recording's variables, so its site hook starts the recorder
                          before any code under the root runs (`_records_here`)
  ["o", reason]           something the recorder could not see into
  ["m", operation]        an assurance manifest operation entry was read
  ["p", operation]        only its presence was checked during registration
  ["v", mode]             a Lean service request used this mode

Paths are relative to $VE_TESTMAP_ROOT. tools/test_map.py installs a `.pth`
hook in the project environment that calls `start()` whenever VE_TESTMAP_OUT
is set, so a Python child of the project environment records too: an explicit
`env=` gets the two recording variables added (unless it sets its own, as a
nested recording does). A Python child that leaves no record (another
interpreter, or `-S`, which skips the hook) marks its test as opaque, unless it
records here and so died before the recorder started (a child a test kills at
once). A forked child starts its own file and re-arms every code object.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
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
        if event == "ve.manifest.operation":
            _emit(["m", args[0]])
        elif event == "ve.manifest.presence":
            _emit(["p", args[0]])
        elif event == "ve.manifest.all":
            _emit(["m", "*"])
        elif event == "ve.service.mode":
            _emit(["v", args[0]])
        elif event == "open":
            relative = _relative(args[0])
            # Imports, pytest's assertion rewriting, tracebacks and warnings read
            # Python sources to run or show them; a test's own read is data.
            if relative == "ve/assurance-manifest.json" and _loading_manifest():
                return
            if relative is not None and not (relative.endswith(".py") and _origin() != TEST):
                _emit(["r", relative])
        elif event in ("os.listdir", "os.scandir"):
            relative = _relative(args[0] if args else ".")
            if relative is not None and _origin() != INFRASTRUCTURE:
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
            if _python(program) and "-S" in list(argv or ())[1:4]:
                _emit(["o", f"python child without site, so without the recorder: {argv!r}"])
    except Exception:  # an audit hook must never break the audited call
        pass


def _loading_manifest() -> bool:
    """The import-time shared load is superseded by operation audit events."""
    frame = sys._getframe(1)
    while frame is not None:
        if frame.f_code.co_name == "_load" and frame.f_code.co_filename == os.path.join(
                _state["root"], "ve/assurance.py"):
            return True
        frame = frame.f_back
    return False


TEST, DISPLAY, INFRASTRUCTURE = "test", "display", "infrastructure"
# Code that opens and lists files for its own purposes: the import system,
# site setup, and pytest with its plugin machinery and plugins.
INFRASTRUCTURE_CODE = ("<frozen importlib", "<frozen zipimport", "<frozen site>", "/site.py",
                       "/_pytest/", "/pluggy/", "/importlib/metadata/", "/_hypothesis_pytestplugin.py")
# Standard-library code that reads a source file to show lines of it.
DISPLAY_CODE = ("/linecache.py", "/traceback.py", "/warnings.py", "<frozen linecache>")
INSPECT_CODE = ("/inspect.py",)


def origin(filenames, root: str, own=frozenset()) -> str:
    """Who an open or a directory listing is for, from the code filenames of
    the stack, innermost first: TEST, DISPLAY or INFRASTRUCTURE.

    The innermost frame that is code under the root (the test, its helpers,
    the project) or infrastructure decides. Everything else, the standard
    library and third-party packages, acts for whoever called it, so
    `pathlib`, `glob` or a parser loading its grammar count for the test.
    Pytest frames further out do not matter: every test runs under them.
    Between the open and that frame, a traceback, warning or linecache frame
    means a source line is being shown (DISPLAY), unless `inspect`, whose
    result a test may compare, asked for it; the outermost of these wins. A
    stack with no deciding frame (`python -c`) counts as the test's.
    """
    display = False
    for name in filenames:
        if any(marker in name for marker in INFRASTRUCTURE_CODE):
            return INFRASTRUCTURE
        if name.startswith(root + os.sep) and name not in own:
            break
        if name.endswith(DISPLAY_CODE):
            display = True
        elif name.endswith(INSPECT_CODE):
            display = False
    return DISPLAY if display else TEST


def _origin() -> str:
    def stack(frame):
        while frame is not None:
            yield frame.f_code.co_filename
            frame = frame.f_back
    # From the audit hook's frame (the recorder's own file, so passed over) outward.
    return origin(stack(sys._getframe(1)), _state["root"], _state["own"])


def _which(program: str) -> str | None:
    from shutil import which
    return which(program)


def _records_here(program: str, argv: list, env) -> bool:
    """Whether a Python child started as `program` with `env` (None: this process's) writes its records
    to this recording: an interpreter of this environment (its site-packages hold the hook), the site
    hook not skipped, and this recording's variables. Its record file then exists from before any code
    under the root runs, so a missing one means it ran none."""
    env = os.environ if env is None else env
    located = program if os.sep in program else (_which(program) or program)
    return (os.path.isabs(located) and os.path.basename(located).startswith("python")
            and os.path.dirname(os.path.normpath(located)) == os.path.dirname(os.path.abspath(sys.executable))
            and "-S" not in [os.fsdecode(a) for a in argv[1:4] if isinstance(a, (str, bytes))]
            and env.get("VE_TESTMAP_OUT") == _state["out"]
            and env.get("VE_TESTMAP_ROOT") == os.environ.get("VE_TESTMAP_ROOT"))


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
                env.setdefault(name, os.environ[name])  # a nested recording keeps its own
            kwargs["env"] = env
        original(self, args, *rest, **kwargs)
        _emit(["c", self.pid, _python(program), _python(program) and _records_here(program, argv, env)])

    subprocess.Popen.__init__ = init


def _wrap_path_glob() -> None:
    # On Python 3.12, pathlib can return an empty glob for a missing directory
    # without calling os.scandir. The audit hook then sees no listing, even
    # though adding that directory can change the test's result.
    for method in ("glob", "rglob"):
        original = getattr(Path, method)

        def listed(self, *args, _original=original, **kwargs):
            if not self.is_dir():
                relative = _relative(self)
                if relative is not None and _origin() != INFRASTRUCTURE:
                    _emit(["d", relative])
            return _original(self, *args, **kwargs)

        setattr(Path, method, listed)


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
    _wrap_path_glob()
    os.register_at_fork(after_in_child=_after_fork)
