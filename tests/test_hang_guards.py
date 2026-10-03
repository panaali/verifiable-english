"""No wall-clock wait the suite reaches is a load-dependent bound on a real checker.

A merge-train suite under heavy load (2 h 14 min) failed a W6a test on the Rust
client's 5 s default, and a recheck found tests still waiting 120 s on real Lean
checkers. Waits that only guard against a hang must be the suite's HANG_TIMEOUT:
in tests directly, and in the product and harness through their settings
(`VE_RUST_TIMEOUT`, `VE_LEAN_SERVICE_TIMEOUT`, `VE_LEAN_SERVICE_STARTUP_TIMEOUT`,
`VE_LEAN_TIMEOUT`, `VE_CONFORMANCE_HANG_TIMEOUT`, `VE_PRECOMMIT_TIMEOUT`), which
tests/conftest.py raises to HANG_TIMEOUT.

A wait of at most SHORT seconds is a deliberate deadline: a fault test against a
fake that hangs, or reaping a process already killed.
"""
import ast
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from conformance.alternatives import environment as alternatives_environment
from subprocesses import HANG_TIMEOUT
from ve import admission, alternatives, discourse, norm_defaults_route, readings_route, reports_route, risk
from ve.backends import lean as lean_backend
from tools.hooks import precommit
from ve.errors import CheckerUnavailable, VEError

ROOT = Path(__file__).resolve().parents[1]
SHORT = 10
# Code the suite runs: tests and their helpers, the conformance harness, the
# product, and the pre-commit hook the hook tests run.
SCANNED = ("tests", "conformance", "ve", "tools/hooks")
# Product and hook constants are defaults a setting replaces, never a wait.
CONSTANT_WAITS = ("ve", "tools/hooks")


def _literal_seconds(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    return None


def _waits(tree):
    """(line, seconds or constant name) of every `timeout` keyword and parameter default."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for keyword in node.keywords:
                if keyword.arg == "timeout":
                    yield keyword.value
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            arguments = node.args
            positional = [*arguments.posonlyargs, *arguments.args]
            for argument, default in zip(positional[len(positional) - len(arguments.defaults):],
                                         arguments.defaults):
                if argument.arg == "timeout":
                    yield default
            for argument, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
                if argument.arg == "timeout" and default is not None:
                    yield default


def short_waits(path: Path, *, constants: bool) -> list[str]:
    """The waits in `path` longer than SHORT and shorter than HANG_TIMEOUT seconds, and (with
    `constants`) the waits that are a module constant rather than a configured value."""
    found = []
    for value in _waits(ast.parse(path.read_text(), str(path))):
        seconds = _literal_seconds(value)
        if seconds is not None and SHORT < seconds < HANG_TIMEOUT:
            found.append(f"{path.relative_to(ROOT)}:{value.lineno}: waits {seconds} s")
        elif constants and isinstance(value, ast.Name) and value.id.lstrip("_").isupper():
            found.append(f"{path.relative_to(ROOT)}:{value.lineno}: waits the constant {value.id}")
    return found


def scanned_files():
    for directory in SCANNED:
        yield from sorted(path for path in (ROOT / directory).rglob("*.py") if "__pycache__" not in path.parts)


def test_no_wait_the_suite_reaches_is_shorter_than_the_hang_guard():
    found = [line for path in scanned_files()
             for line in short_waits(path, constants=path.relative_to(ROOT).as_posix().startswith(
                 tuple(f"{directory}/" for directory in CONSTANT_WAITS)))]
    assert found == []


@pytest.mark.parametrize("source, expected", [
    # The recheck's examples: a helper's default and a call on a real Lean checker.
    ("def raw_session(executable, lines, timeout=120): pass\n", ["waits 120 s"]),
    ("subprocess.run([binary, '-'], timeout=120)\n", ["waits 120 s"]),
    ("LeanService(path, timeout=120, batch_cases=4096)\n", ["waits 120 s"]),
    ("def run(*, timeout: float = 120.0): pass\n", ["waits 120.0 s"]),
    ("f = lambda timeout=600: timeout\n", ["waits 600 s"]),
    ("run(case, timeout=HANG_TIMEOUT)\n", []),
    ("run(case, timeout=1800)\n", []),
    ("run(fake, timeout=0.5)\n", []),
    ("proc.wait(timeout=10)\n", []),
], ids=["helper default", "subprocess call", "service", "annotated keyword-only default", "lambda default",
        "hang guard", "hang guard literal", "fault deadline", "reaping a killed process"])
def test_the_guard_sees_each_form_of_wait(tmp_path, monkeypatch, source, expected):
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    path = tmp_path / "example.py"
    path.write_text(source)
    assert [line.split(": ", 1)[1] for line in short_waits(path, constants=False)] == expected


def test_the_guard_sees_a_product_constant_wait(tmp_path, monkeypatch):
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    path = tmp_path / "example.py"
    path.write_text("LEAN_REPLAY_TIMEOUT = 60\n"
                    "run(case, timeout=LEAN_REPLAY_TIMEOUT)\n"
                    "run(case, timeout=configured_timeout(LEAN_REPLAY_TIMEOUT))\n"
                    "run(case, timeout=timeout)\n")
    assert short_waits(path, constants=True) == ["example.py:2: waits the constant LEAN_REPLAY_TIMEOUT"]
    assert short_waits(path, constants=False) == []


# Every product caller of a one-shot Lean runner: its default wait, and a call that reaches the runner.
CALLERS = {
    "soft route": (120, lambda fake: lean_backend.run_soft_case(fake, {"id": "soft"})),
    "norm-defaults route": (120, lambda fake: norm_defaults_route.run_cases([], fake)),
    "readings route": (120, lambda fake: readings_route.run_lean([], executable=fake)),
    "reports route": (60, lambda fake: reports_route.run_case("reports-elaborate", {}, {})),
    "risk route": (180, lambda fake: risk.run_case({"id": "r", "kind": "risk-elaborate", "environment": {}},
                                                   binary=fake)),
    "alternatives route": (180, lambda fake: alternatives.run_case(
        {"id": "a", "kind": "alt-elaborate", "environment": alternatives_environment()}, binary=fake)),
    "discourse route": (300, lambda fake: discourse.lean_admission(b"x", fake.parent)),
    "W6 quantity admission": (60, lambda fake: admission._lean_quantity_admission(
        SimpleNamespace(to_dict=dict), {})),
}


@pytest.fixture
def waits(tmp_path, monkeypatch):
    """The timeout of every runner call, each of which then times out; the runner is a file."""
    fake = tmp_path / "runner"
    fake.write_text("")
    monkeypatch.setattr(reports_route, "EXECUTABLE", fake)
    monkeypatch.setenv("VE_DISCOURSE_ROUTE", str(fake))
    monkeypatch.delenv("VE_AUTHORITY", raising=False)
    seen = []

    def run(argv, **options):
        seen.append(options["timeout"])
        raise subprocess.TimeoutExpired(argv, options["timeout"])
    monkeypatch.setattr(lean_backend, "subprocess", SimpleNamespace(run=run, TimeoutExpired=subprocess.TimeoutExpired))
    return fake, seen


@pytest.mark.parametrize("name", CALLERS)
def test_each_lean_runner_caller_waits_the_setting_else_its_default(waits, monkeypatch, name):
    fake, seen = waits
    default, call = CALLERS[name]
    monkeypatch.delenv("VE_LEAN_TIMEOUT")
    with pytest.raises((CheckerUnavailable, VEError)):
        call(fake)
    monkeypatch.setenv("VE_LEAN_TIMEOUT", "1234.5")
    with pytest.raises((CheckerUnavailable, VEError)):
        call(fake)
    assert seen == [default, 1234.5]


@pytest.mark.parametrize("text", ["0", "-1", "nan", "inf", "", "ten"])
def test_an_invalid_lean_timeout_is_unavailable_before_any_runner_starts(waits, monkeypatch, text):
    fake, seen = waits
    monkeypatch.setenv("VE_LEAN_TIMEOUT", text)
    for name, (_, call) in CALLERS.items():
        with pytest.raises(CheckerUnavailable, match="VE_LEAN_TIMEOUT"):
            call(fake)
    assert seen == []


def test_an_explicit_lean_timeout_is_kept(waits, monkeypatch):
    fake, seen = waits
    for call in (lambda: lean_backend.run_norm_defaults_cases(fake, [], timeout=7),
                 lambda: lean_backend.run_readings_cases(fake, [], timeout=7),
                 lambda: risk.run_case({"id": "r", "kind": "risk-elaborate", "environment": {}},
                                       binary=fake, timeout=7)):
        with pytest.raises(CheckerUnavailable):
            call()
    assert seen == [7, 7, 7]


def test_the_suite_raises_every_checker_setting_to_the_hang_guard():
    import conftest
    for variable in conftest.CHECKER_TIMEOUTS:
        assert float(os.environ[variable]) == HANG_TIMEOUT, variable
    assert lean_backend.configured_timeout(60.0) == HANG_TIMEOUT


def test_every_precommit_wait_follows_the_setting_else_its_default(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "tools"))  # as the hook loads it
    import check_lean_imports as reader
    monkeypatch.delenv("VE_PRECOMMIT_TIMEOUT")
    defaults = (precommit.WIRE_CHECK_TIMEOUT, reader.ORACLE_BUDGET, reader.PROBE_WAIT)
    assert defaults == (30, 3, 2)
    assert [precommit.configured_wait(default) for default in defaults] == [30, 3, 2]
    monkeypatch.setenv("VE_PRECOMMIT_TIMEOUT", "1234.5")
    assert [precommit.configured_wait(default) for default in defaults] == [1234.5] * 3
    for text in ("0", "-1", "nan", "inf", "", "ten"):
        monkeypatch.setenv("VE_PRECOMMIT_TIMEOUT", text)
        with pytest.raises(ValueError, match="VE_PRECOMMIT_TIMEOUT"):
            precommit.configured_wait(30)


CLOCKS = {"monotonic", "perf_counter", "time", "monotonic_ns", "perf_counter_ns", "time_ns"}


def elapsed_assertions(path: Path) -> list[str]:
    """The `assert` statements in `path` that read a clock or an `elapsed` value: elapsed time
    is never an acceptance criterion (tests/subprocesses.py; measure CPU seconds or an event)."""
    found = []
    for node in ast.walk(ast.parse(path.read_text(), str(path))):
        if isinstance(node, ast.Assert):
            for inner in ast.walk(node.test):
                clock = (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                         and inner.func.attr in CLOCKS and isinstance(inner.func.value, ast.Name)
                         and inner.func.value.id == "time")
                if clock or (isinstance(inner, ast.Name) and inner.id == "elapsed"):
                    found.append(f"{path.relative_to(ROOT)}:{node.lineno}: asserts on elapsed time")
                    break
    return found


def test_no_test_accepts_on_elapsed_time():
    assert [line for path in sorted((ROOT / "tests").rglob("*.py")) if "__pycache__" not in path.parts
            for line in elapsed_assertions(path)] == []


@pytest.mark.parametrize("source, flagged", [
    ("assert time.monotonic() - started < 5\n", True),
    ("assert elapsed < 10, result.stderr\n", True),
    ("assert time.perf_counter() - t0 < 1\n", True),
    ("assert cpu.seconds < 10\n", False),
    ("assert deadline > 0\n", False),
], ids=["monotonic", "elapsed", "perf_counter", "CPU seconds", "other name"])
def test_the_elapsed_guard_sees_each_form(tmp_path, monkeypatch, source, flagged):
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    path = tmp_path / "example.py"
    path.write_text(source)
    assert bool(elapsed_assertions(path)) == flagged


def reachable_test_modules() -> list[str]:
    """The test modules that code outside tests/ imports (`tests.NAME`), and those they import in turn."""
    def imported(path):
        for node in ast.walk(ast.parse(path.read_text(), str(path))):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                if node.module.startswith("tests."):
                    yield node.module.split(".")[1]
                elif node.module == "tests":
                    yield from (alias.name for alias in node.names)
    todo = [name for directory in ("conformance", "tools", "usecases", "ve")
            for path in (ROOT / directory).rglob("*.py") if "__pycache__" not in path.parts
            for name in imported(path)]
    seen = set()
    while todo:
        name = todo.pop()
        if name not in seen and (ROOT / "tests" / f"{name}.py").exists():
            seen.add(name)
            todo.extend(imported(ROOT / "tests" / f"{name}.py"))
    return sorted(seen)


def test_test_modules_other_code_imports_load_outside_pytest():
    """Only pytest puts tests/ on the path: a test module the harness imports as `tests.NAME`
    imports the hang guard as `tests.subprocesses` (a bare `subprocesses` broke
    conformance/soft_norms.py, and so the gate corpus, outside pytest)."""
    modules = reachable_test_modules()
    assert {"subprocesses", "test_soft_norms_lean", "test_wire_contract_lean"} <= set(modules)
    code = "import importlib, sys\nfor name in sys.argv[1:]:\n    importlib.import_module('tests.' + name)\n"
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    result = subprocess.run([sys.executable, "-c", code, *modules], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stderr
