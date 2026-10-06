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
import re
import subprocess
import sys
from types import SimpleNamespace

import pytest

from conformance.alternatives import environment as alternatives_environment
from subprocesses import HANG_TIMEOUT, expired_waits
from ve import admission, alternatives, discourse, norm_defaults_route, readings_route, reports_route, risk
from ve.backends import lean as lean_backend
from tools.hooks import precommit
from ve.errors import CheckerUnavailable, VEError

ROOT = Path(__file__).resolve().parents[1]
# Code the suite runs: tests and their helpers, the conformance harness, the
# product, and the pre-commit hook the hook tests run.
SCANNED = ("tests", "conformance", "ve", "tools/hooks")
# Product and hook constants are defaults a setting replaces, never a wait.
CONSTANT_WAITS = ("ve", "tools/hooks")
# Names of the settings and module constants that hold a wall-clock deadline.
DEADLINE_NAME = re.compile(r"(TIMEOUT|_SECONDS)$")

# The only code that may hold a wait shorter than HANG_TIMEOUT, a sleep, a short deadline
# setting or an assertion on time, by `path::function`. There is no blanket exemption by
# size: a short wait anywhere else fails test_no_short_wait_outside_the_reviewed_allowlist.
# Each entry is reviewed: the deadline is injected (an instrumented clock or an
# instrumented child that records the wait it is given; nothing waits it out), or no
# process the wait could bound is started, or the wait reaps a process already killed.
INJECTED = {
    # Product: reaping a service process that was asked to stop, then killed.
    "ve/backends/lean_service.py::_stop": "reaps a process already signalled (2 s) or killed (10 s)",
    "ve/backends/rust_jsonl.py::_failure": "reaps a checker process that ended its output or stopped reading",
    "ve/backends/rust_jsonl.py::close": "reaps a checker process already killed",
    # Event polls bounded by HANG_TIMEOUT: a marker file, a lock, a killed process group.
    "tests/conftest.py::_stop_build_group": "polls /proc for a process group already sent SIGKILL",
    "tests/test_native_build_lock.py::_wait_for": "polls for a marker file, bounded by HANG_TIMEOUT",
    "tests/test_native_build_lock.py::_acquire": "polls for a lock, bounded by HANG_TIMEOUT",
    "tests/test_gate_integrity.py::test_terminated_gate_cannot_leave_old_pass_record":
        "polls for a marker file, bounded by HANG_TIMEOUT",
    # An adversarial delay (a parent scheduled late); the outcome is decided by a lock, not by it.
    "tests/test_native_build_lock.py::test_orphaned_builder_keeps_exclusive_lock": "late-parent reproducer",
    # Instrumented waits: the test records the wait each call is given; no child runs against it.
    "tests/test_hang_guards.py::test_an_explicit_route_timeout_is_kept": "instrumented service pool",
    "tests/test_hang_guards.py::test_every_precommit_wait_follows_the_setting_else_its_default":
        "instrumented subprocess.run and oracle clock",
    "tests/test_lean_service.py::test_users_keep_the_mode_deadlines":
        "expire_service_waits frozen clock; instrumented handshake",
    "tests/test_stage2_dispatch.py::test_rust_wait_is_the_default_unless_configured": "instrumented Rust checker",
    # Injected expired deadlines against never-answering fakes (expired_waits, expire_service_waits).
    "tests/test_lean_service.py::test_the_setting_replaces_the_request_and_startup_defaults":
        "expire_service_waits; asserts the setting is each attempt's wait",
    "tests/test_lean_service.py::test_the_injected_clock_records_a_miscomputed_deadline":
        "expire_service_waits; asserts each seeded deadline mutant records another wait",
    "tests/test_stage2_dispatch.py::test_rust_checker_slower_than_the_setting_is_stopped_at_it":
        "expired_waits; asserts the setting is the wait",
    "tests/test_hang_guards.py::test_a_wire_check_that_outlasts_its_wait_blocks_the_commit":
        "expired_waits; asserts the setting is the wait",
    "tests/test_assurance_manifest.py::test_bundle_separates_rejection_from_unavailability":
        "expired_waits; asserts the setting is the wait",
    "tests/test_assurance_manifest.py::test_argument_separates_lean_rejection_from_unavailability":
        "expired_waits; asserts the setting is the wait",
    # Injected clocks for operation budgets.
    "tests/test_assist_deadline.py::*": "autouse controlled_operation_clock: time.monotonic advances only by _busy",
    "tests/test_assist_recovery_replay.py::test_recorded_deadline_cannot_swallow_enclosing_replay_deadline":
        "injected time.monotonic",
    "tests/test_english_unambiguity.py::test_earley_time_budget_rejects_in_worker_thread": "injected _monotonic clock",
    "tests/test_english_unambiguity.py::test_earley_alarm_budget_restores_signal_state": "fake alarm",
    "tests/test_english_unambiguity.py::test_earley_time_budget_with_host_alarm": "injected _monotonic clock",
    # The CPU meter's own tests: they measure the meter, not the product.
    "tests/test_cpu_bounds.py::test_time_a_child_spends_waiting_is_not_charged": "tests run_cpu_bounded",
    "tests/test_cpu_bounds.py::test_a_child_that_spins_past_its_limit_is_stopped": "tests run_cpu_bounded",
    "tests/test_cpu_bounds.py::test_child_cpu_counts_only_children_that_end_inside_the_block": "tests ChildCPU",
    # The guards' own examples: sources the static guard parses, and lowered settings the
    # runtime guard refuses before any real checker starts (or that only a fake sees).
    "tests/test_hang_guards.py::test_the_elapsed_guard_sees_each_form": "guard example sources",
    "tests/test_hang_guards.py::test_a_real_checker_started_with_a_lowered_setting_is_refused":
        "refused before the real checker starts",
    "tests/test_hang_guards.py::test_a_lowered_setting_for_a_fake_checker_is_allowed": "a fake child only",
}


def _literal_seconds(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            return float(node.value)
        except ValueError:
            return None
    return None


def _name(node):
    """The dotted name of a call's function: `time.sleep`, `monkeypatch.setenv`, `wait`."""
    if isinstance(node, ast.Attribute):
        return f"{_name(node.value)}.{node.attr}"
    return node.id if isinstance(node, ast.Name) else ""


class _Waits(ast.NodeVisitor):
    """Every wall-clock wait in a module, with the function it is in:
    `timeout` keywords and parameter defaults; positional waits of `wait`, `join` and
    `result`; `time.sleep`; and deadline settings (`setenv("VE_..._TIMEOUT", "1")`,
    `setattr(module, "EARLEY_SECONDS", 1)`, an environment entry or assignment)."""

    def __init__(self):
        self.functions, self.found = ["<module>"], []

    def add(self, kind, value):
        self.found.append((self.functions[-1], kind, value))

    def visit_FunctionDef(self, node):
        if not isinstance(node, ast.Lambda):  # a default belongs to the function declaring it
            self.functions.append(node.name)
        arguments = node.args
        positional = [*arguments.posonlyargs, *arguments.args]
        for argument, default in zip(positional[len(positional) - len(arguments.defaults):],
                                     arguments.defaults):
            if argument.arg == "timeout":
                self.add("timeout", default)
        for argument, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
            if argument.arg == "timeout" and default is not None:
                self.add("timeout", default)
        self.generic_visit(node)
        if not isinstance(node, ast.Lambda):
            self.functions.pop()

    visit_AsyncFunctionDef = visit_Lambda = visit_FunctionDef

    def visit_Call(self, node):
        name = _name(node.func)
        for keyword in node.keywords:
            if keyword.arg == "timeout":
                self.add("timeout", keyword.value)
        if name.rsplit(".", 1)[-1] in ("wait", "join", "result") and node.args and "." in name and \
                isinstance(node.args[0], ast.Constant) and type(node.args[0].value) in (int, float):
            self.add("timeout", node.args[0])
        if name in ("time.sleep", "sleep"):
            self.add("sleep", node.args[0] if node.args else None)
        if name.rsplit(".", 1)[-1] in ("setenv", "setattr", "setdefault") and len(node.args) >= 2:
            key = node.args[-2]
            if isinstance(key, ast.Constant) and isinstance(key.value, str) and DEADLINE_NAME.search(key.value):
                self.add("setting", node.args[-1])
        self.generic_visit(node)

    def visit_Dict(self, node):
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and isinstance(key.value, str) and \
                    key.value.startswith("VE_") and DEADLINE_NAME.search(key.value):
                self.add("setting", value)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Constant) and \
                    isinstance(target.slice.value, str) and DEADLINE_NAME.search(target.slice.value):
                self.add("setting", node.value)
        self.generic_visit(node)


def short_waits(path: Path, *, constants: bool) -> list[str]:
    """`path::function: line: what` for each wait in `path` that is shorter than HANG_TIMEOUT
    seconds, each sleep, and (with `constants`) each wait that is a module constant rather
    than a configured value."""
    visitor = _Waits()
    visitor.visit(ast.parse(path.read_text(), str(path)))
    found = []
    for function, kind, value in visitor.found:
        where = f"{path.relative_to(ROOT).as_posix()}::{function}: {getattr(value, 'lineno', '?')}"
        seconds = None if value is None else _literal_seconds(value)
        if kind == "sleep":
            found.append(f"{where}: sleeps")
        elif seconds is not None and seconds < HANG_TIMEOUT:
            found.append(f"{where}: {'waits' if kind == 'timeout' else 'sets a deadline of'} {seconds:g} s")
        elif kind == "timeout" and constants and isinstance(value, ast.Name) and value.id.lstrip("_").isupper():
            found.append(f"{where}: waits the constant {value.id}")
    return found


def scanned_files():
    for directory in SCANNED:
        yield from sorted(path for path in (ROOT / directory).rglob("*.py") if "__pycache__" not in path.parts)


def findings():
    """Every short wait, sleep and assertion on time in the scanned code."""
    for path in scanned_files():
        relative = path.relative_to(ROOT).as_posix()
        yield from short_waits(path, constants=relative.startswith(tuple(f"{d}/" for d in CONSTANT_WAITS)))
        if relative.startswith("tests/"):
            yield from elapsed_assertions(path)


def allowlisted(line):
    """The INJECTED entry that covers a finding (`path::function`, or `path::*`), else None."""
    where = line.split(": ", 1)[0]
    module = where.split("::", 1)[0] + "::*"
    return where if where in INJECTED else module if module in INJECTED else None


def test_no_short_wait_outside_the_reviewed_allowlist():
    assert [line for line in findings() if allowlisted(line) is None] == []


def test_every_allowlist_entry_still_covers_a_short_wait():
    """A stale entry would let a new short wait into a function that no longer needs one."""
    assert sorted(set(INJECTED) - {allowlisted(line) for line in findings()}) == []


@pytest.mark.parametrize("source, expected", [
    # The recheck's examples: a helper's default and a call on a real Lean checker.
    ("def raw_session(executable, lines, timeout=120): pass\n", ["waits 120 s"]),
    ("subprocess.run([binary, '-'], timeout=120)\n", ["waits 120 s"]),
    ("LeanService(path, timeout=120, batch_cases=4096)\n", ["waits 120 s"]),
    ("def run(*, timeout: float = 120.0): pass\n", ["waits 120 s"]),
    ("f = lambda timeout=600: timeout\n", ["waits 600 s"]),
    ("run(case, timeout=HANG_TIMEOUT)\n", []),
    ("run(case, timeout=1800)\n", []),
    # wire-s5 recheck: a fake's healthy retry given 0.5 s failed under load. No size is exempt.
    ("LeanService(fake, timeout=0.5)\n", ["waits 0.5 s"]),
    ("proc.wait(timeout=10)\n", ["waits 10 s"]),
    ("proc.wait(5)\n", ["waits 5 s"]),
    ("future.result(2)\n", ["waits 2 s"]),
    ("time.sleep(0.2)\n", ["sleeps"]),
    ("monkeypatch.setenv('VE_LEAN_SERVICE_TIMEOUT', '0.5')\n", ["sets a deadline of 0.5 s"]),
    ("monkeypatch.setenv('VE_LEAN_SERVICE_TIMEOUT', '1234.5')\n", ["sets a deadline of 1234.5 s"]),
    ("monkeypatch.setattr(unambiguity, 'EARLEY_SECONDS', 1)\n", ["sets a deadline of 1 s"]),
    ("run(env={'VE_RUST_TIMEOUT': '5'})\n", ["sets a deadline of 5 s"]),
    ("os.environ['VE_PRECOMMIT_TIMEOUT'] = '3'\n", ["sets a deadline of 3 s"]),
    ("monkeypatch.setenv('VE_RUST_TIMEOUT', str(HANG_TIMEOUT))\n", []),
], ids=["helper default", "subprocess call", "service", "annotated keyword-only default", "lambda default",
        "hang guard", "hang guard literal", "fault deadline", "reaping keyword", "positional wait",
        "future result", "sleep", "service setting", "instrumented setting", "parse budget",
        "environment entry", "environment assignment", "hang guard setting"])
def test_the_guard_sees_each_form_of_wait(tmp_path, monkeypatch, source, expected):
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    path = tmp_path / "example.py"
    path.write_text(source)
    assert [line.split(": ", 2)[2] for line in short_waits(path, constants=False)] == expected


def test_the_guard_names_the_function_holding_the_wait(tmp_path, monkeypatch):
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    path = tmp_path / "example.py"
    path.write_text("def test_a():\n    def inner():\n        run(timeout=1)\n    run(timeout=2)\n"
                    "class Fake:\n    def wait(self, timeout=3): pass\n")
    assert short_waits(path, constants=False) == ["example.py::inner: 3: waits 1 s",
                                                  "example.py::test_a: 4: waits 2 s",
                                                  "example.py::wait: 6: waits 3 s"]


def test_the_guard_sees_a_product_constant_wait(tmp_path, monkeypatch):
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    path = tmp_path / "example.py"
    path.write_text("LEAN_REPLAY_TIMEOUT = 60\n"
                    "run(case, timeout=LEAN_REPLAY_TIMEOUT)\n"
                    "run(case, timeout=configured_timeout(LEAN_REPLAY_TIMEOUT))\n"
                    "run(case, timeout=timeout)\n")
    assert short_waits(path, constants=True) == ["example.py::<module>: 2: waits the constant LEAN_REPLAY_TIMEOUT"]
    assert short_waits(path, constants=False) == []


# Every product caller of a statement-layer Lean route, and a call that reaches it. Since lean-first batch 1
# each route is a mode of the Lean service: a request waits its mode's CPU deadline, with the wall-clock cap
# `VE_LEAN_SERVICE_TIMEOUT` sets (tests/test_lean_service.py), so a caller passes no wait of its own.
CALLERS = {
    "soft route": ("soft-norms", lambda tmp: __import__("ve.soft_route", fromlist=["_run"])._run(
        {"id": "soft", "kind": "soft-elaborate"})),
    "norm-defaults route": ("norm-defaults", lambda tmp: norm_defaults_route.run_cases([{"id": "n"}])),
    "readings route": ("readings-route", lambda tmp: readings_route.run_lean([{"id": "r"}])),
    "reports route": ("reports", lambda tmp: reports_route.run_case("reports-elaborate", {}, {})),
    "risk route": ("risk", lambda tmp: risk.run_case({"id": "r", "kind": "risk-elaborate", "environment": {}})),
    "alternatives route": ("alternatives", lambda tmp: alternatives.run_case(
        {"id": "a", "kind": "alt-elaborate", "environment": alternatives_environment()})),
    "discourse route": ("discourse", lambda tmp: discourse.lean_admission(b"x", tmp)),
    "W6 quantity admission": ("quantity", lambda tmp: admission._lean_quantity_admission(
        SimpleNamespace(to_dict=dict), {})),
}


@pytest.fixture
def waits(monkeypatch):
    """The (mode, timeout) of every request a route caller makes, each of which is then unavailable."""
    from ve.backends import relay
    monkeypatch.delenv("VE_AUTHORITY", raising=False)
    seen = []

    class Recording:
        def run_bound(self, mode, cases, *, timeout=None):
            seen.append((mode, timeout))
            raise CheckerUnavailable("CheckerUnavailable: recorded")
    monkeypatch.setattr(relay, "_pool_for", lambda executable=None: Recording())
    return seen


@pytest.mark.parametrize("name", CALLERS)
def test_each_lean_route_caller_leaves_the_wait_to_its_mode(waits, tmp_path, name):
    mode, call = CALLERS[name]
    with pytest.raises((CheckerUnavailable, VEError)):
        call(tmp_path)
    assert waits == [(mode, None)]


def test_an_explicit_route_timeout_is_kept(waits):
    for call in (lambda: readings_route.run_lean([{"id": "r"}], timeout=7),
                 lambda: risk.run_case({"id": "r", "kind": "risk-elaborate", "environment": {}}, timeout=7)):
        with pytest.raises(CheckerUnavailable):
            call()
    assert waits == [("readings-route", 7), ("risk", 7)]


def test_the_suite_raises_every_checker_setting_to_the_hang_guard():
    import conftest
    for variable in conftest.CHECKER_TIMEOUTS:
        assert float(os.environ[variable]) == HANG_TIMEOUT, variable
    assert lean_backend.configured_timeout(60.0) == HANG_TIMEOUT


class StagedIndex:
    """The part of the hook's index its waiting checks read: `staged` paths and their contents."""

    def __init__(self, snapshot, staged, policy):
        self.snapshot, self.blobs, self._policy = snapshot, staged, policy
        self.changed = {path: SimpleNamespace(status="M", mode="100644") for path in staged}

    def staged(self, predicate=lambda path: True):
        return sorted(path for path in self.changed if predicate(path))

    def listing(self):
        return dict.fromkeys(self.blobs, "0" * 40)

    def read(self, names):
        return {name: self.blobs.get(name) for name in names}

    def policy(self):
        return self._policy


@pytest.fixture
def precommit_waits(tmp_path, monkeypatch):
    """Run the hook's waiting checks, recording the wait of each child they would start (none starts)."""
    monkeypatch.syspath_prepend(str(ROOT / "tools"))  # as the hook loads it
    import check_lean_imports as reader
    import layer_policy
    seen = []

    def run(argv, **options):
        seen.append((Path(argv[0]).name if argv[0] != sys.executable else "python", argv[1], options["timeout"]))
        stdout = "Lean (version 4.99.0, x86_64)" if argv[1] == "--version" else ""
        return subprocess.CompletedProcess(argv, 1 if argv[1] == "--deps" else 0, stdout, "refused")
    fake = SimpleNamespace(run=run, TimeoutExpired=subprocess.TimeoutExpired)
    monkeypatch.setattr(precommit, "subprocess", fake)
    monkeypatch.setattr(precommit, "NOTES", [])
    monkeypatch.setattr(reader, "subprocess", fake)
    monkeypatch.setattr(reader, "shutil", SimpleNamespace(which={"lean": "/toolchain/bin/lean"}.get))
    monkeypatch.setattr(reader, "time", SimpleNamespace(monotonic=lambda: 0.0))  # the whole budget is left
    policy = SimpleNamespace(layer_policy=layer_policy, check_lean_imports=reader)
    staged = {"lean/VE/Syntax.lean": b"import VE.Core\n", precommit.LEAN_TOOLCHAIN: b"leanprover/lean4:v4.99.0\n",
              "tools/wire_contract.py": b"# staged\n"}

    def checks():
        seen.clear()
        precommit.check_layers(StagedIndex(tmp_path, staged, policy))
        precommit.check_wire_contract(StagedIndex(tmp_path, staged, policy))
        return list(seen)
    return reader, checks


def test_every_precommit_wait_follows_the_setting_else_its_default(precommit_waits, monkeypatch):
    """A recheck paused a real wire check that a hook test ran at the 30 s default: it failed
    after 30 s. Each default is checked at the call that would start the child; no child starts."""
    reader, checks = precommit_waits
    assert (precommit.WIRE_CHECK_TIMEOUT, reader.ORACLE_BUDGET, reader.PROBE_WAIT) == (30, 3, 2)
    monkeypatch.delenv("VE_PRECOMMIT_TIMEOUT")
    assert checks() == [("lean", "--version", 2), ("lean", "--deps", 3), ("python", "tools/wire_contract.py", 30)]
    monkeypatch.setenv("VE_PRECOMMIT_TIMEOUT", "1234.5")
    assert [wait for *_, wait in checks()] == [1234.5] * 3
    for text in ("0", "-1", "nan", "inf", "", "ten"):
        monkeypatch.setenv("VE_PRECOMMIT_TIMEOUT", text)
        with pytest.raises(ValueError, match="VE_PRECOMMIT_TIMEOUT"):
            precommit.configured_wait(30)


def test_a_wire_check_that_outlasts_its_wait_blocks_the_commit(tmp_path, monkeypatch):
    """The pre-commit wire check's child never answers; its deadline, the setting, is injected
    as expired, so nothing waits it out. The check raises, and the hook blocks on any check
    that raises (`precommit.main`: a broken check must block)."""
    monkeypatch.setenv("VE_PRECOMMIT_TIMEOUT", "1234.5")
    waits = expired_waits(monkeypatch, precommit, expire=lambda argv: "tools/wire_contract.py" in argv)
    staged = {"tools/wire_contract.py": b"import threading\nthreading.Event().wait()\n"}
    with pytest.raises(subprocess.TimeoutExpired) as caught:
        precommit.check_wire_contract(StagedIndex(tmp_path, staged, None))
    assert isinstance(caught.value, Exception) and caught.value.timeout == 1234.5
    assert waits == [1234.5]


def _start_child(env=None):
    subprocess.run([sys.executable, "-c", "pass"], env=env, timeout=HANG_TIMEOUT, check=True)


@pytest.mark.parametrize("remove", [
    # The recheck's example: a hook test popped the setting from the environment it gave the hook.
    lambda monkeypatch: _start_child({key: value for key, value in os.environ.items()
                                      if key != "VE_PRECOMMIT_TIMEOUT"}),
    lambda monkeypatch: (monkeypatch.delenv("VE_LEAN_SERVICE_TIMEOUT"), _start_child()),
    lambda monkeypatch: (monkeypatch.delenv("VE_RUST_TIMEOUT"), os.system("true")),
    lambda monkeypatch: (monkeypatch.delenv("VE_LEAN_TIMEOUT"),
                         os.posix_spawn(sys.executable, [sys.executable, "-c", "pass"], dict(os.environ))),
], ids=["popped from a child's environment", "deleted from this process", "os.system", "os.posix_spawn"])
def test_a_child_started_without_a_checker_setting_is_refused(monkeypatch, remove):
    import conftest
    with pytest.raises(conftest.CheckerSettingRemoved, match="started a child without VE_"):
        remove(monkeypatch)
    assert len(conftest.REFUSED) == 1
    conftest.REFUSED.clear()  # the refusal was this test's point


@pytest.mark.parametrize("start", [
    # The wire-s5 recheck's class: a real checker given a short deadline fails under load.
    lambda monkeypatch: (monkeypatch.setenv("VE_LEAN_SERVICE_TIMEOUT", "0.5"),
                         subprocess.Popen([str(ROOT / "lean/.lake/build/bin/ve_service")])),
    lambda monkeypatch: subprocess.run([str(ROOT / "rust/target/release/ve"), "jsonl", "-"],
                                       env={**os.environ, "VE_RUST_TIMEOUT": "5"}, timeout=HANG_TIMEOUT),
    lambda monkeypatch: (monkeypatch.setenv("VE_LEAN_TIMEOUT", "ten"),
                         os.posix_spawn(str(ROOT / "lean/.lake/build/bin/ve_conformance"), ["ve_conformance"],
                                        dict(os.environ))),
], ids=["service setting, this process", "Rust setting, child environment", "unreadable setting, posix_spawn"])
def test_a_real_checker_started_with_a_lowered_setting_is_refused(monkeypatch, start):
    import conftest
    with pytest.raises(conftest.CheckerSettingRemoved, match="started the real checker .* below HANG_TIMEOUT"):
        start(monkeypatch)
    assert len(conftest.REFUSED) == 1
    conftest.REFUSED.clear()  # the refusal was this test's point


def test_a_lowered_setting_for_a_fake_checker_is_allowed(tmp_path, monkeypatch):
    """A deadline test lowers a setting for a fake, or injects the expiry
    (tests/subprocesses.py: expired_waits); only a real checker must get the hang guard."""
    import conftest
    monkeypatch.setenv("VE_LEAN_SERVICE_TIMEOUT", "0.5")
    _start_child()
    assert conftest.lowered_checker_settings(sys.executable, None) == []
    assert conftest.lowered_checker_settings(str(ROOT / "rust/target/release/ve"), None) == [
        "VE_LEAN_SERVICE_TIMEOUT"]
    assert conftest.REFUSED == []


def test_a_removed_setting_without_a_real_child_or_a_fresh_environment_is_allowed(monkeypatch):
    import conftest
    # The gate's fresh environment holds none of the suite's settings, by design.
    _start_child({"PATH": os.environ["PATH"]})
    _start_child()
    # Instrumented: the setting is removed, and no real child starts.
    monkeypatch.delenv("VE_PRECOMMIT_TIMEOUT")
    assert conftest.removed_checker_settings(None) == ["VE_PRECOMMIT_TIMEOUT"]
    assert precommit.configured_wait(precommit.WIRE_CHECK_TIMEOUT) == 30
    assert conftest.REFUSED == []


CLOCKS = {"monotonic", "perf_counter", "time", "process_time", "thread_time"}
# Words of a name that hold a measured duration or CPU cost (`lean_cpu`, `duration_ms`, `ru_utime`);
# the CPU meter's reading is `cpu.seconds`. A count of CPUs (`cpus`) is not a measure.
MEASURES = {"elapsed", "duration", "latency", "cpu", "utime", "stime", "getrusage"}


def _measure(name):
    return bool(MEASURES & set(name.lower().split("_")))


def _assertions(tree):
    """(function, assert) for every `assert` statement, with the function it is in."""
    def walk(node, function):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Assert):
                yield function, child
            yield from walk(child, child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                            else function)
    yield from walk(tree, "<module>")


def elapsed_assertions(path: Path) -> list[str]:
    """The `assert` statements in `path` that read a clock or a measured duration or CPU cost:
    speed is never a correctness criterion. Elapsed time grows with machine load; CPU time
    is a performance measurement, which tools/bench/perf.py makes against stored baselines.
    A test bounds work by the backends' own budgets, or stops a runaway child with a kernel
    CPU limit (tests/subprocesses.py: run_cpu_bounded) whose overrun fails it."""
    found = []
    for function, node in _assertions(ast.parse(path.read_text(), str(path))):
        for inner in ast.walk(node.test):
            clock = (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                     and inner.func.attr.removesuffix("_ns") in CLOCKS and isinstance(inner.func.value, ast.Name)
                     and inner.func.value.id == "time")
            measure = ((isinstance(inner, ast.Name) and _measure(inner.id))
                       or (isinstance(inner, ast.Attribute) and (inner.attr == "seconds" or _measure(inner.attr))))
            if clock or measure:
                found.append(f"{path.relative_to(ROOT).as_posix()}::{function}: {node.lineno}: asserts on time")
                break
    return found


@pytest.mark.parametrize("source, flagged", [
    ("assert time.monotonic() - started < 5\n", True),
    ("assert elapsed < 10, result.stderr\n", True),
    ("assert time.perf_counter() - t0 < 1\n", True),
    ("assert time.process_time() - started < 10\n", True),
    ("assert time.monotonic_ns() - t0 < 10**9\n", True),
    # The precommit and soft-review CPU bounds moved to tools/bench/perf.py.
    ("assert cpu.seconds < 10\n", True),
    ("assert lean_cpu < 30\n", True),
    ("assert result.duration_ms < 50\n", True),
    ("assert deadline > 0\n", False),
    ("assert waits == [HANG_TIMEOUT]\n", False),
    ("assert usage.ru_utime < 3\n", True),
    ("assert worker_count(cpus=32, load=0) == 32\n", False),
], ids=["monotonic", "elapsed", "perf_counter", "process_time", "nanoseconds", "CPU seconds", "CPU name",
        "duration", "other name", "recorded wait", "rusage", "CPU count"])
def test_the_elapsed_guard_sees_each_form(tmp_path, monkeypatch, source, flagged):
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    path = tmp_path / "example.py"
    path.write_text(source)
    assert bool(elapsed_assertions(path)) == flagged


def reachable_test_modules() -> list[str]:
    """The test modules that code outside tests/ imports (`tests.NAME`, or the string `"tests.NAME"` it
    hands to `importlib`), and those they import in turn."""
    def imported(path):
        for node in ast.walk(ast.parse(path.read_text(), str(path))):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                if node.module.startswith("tests."):
                    yield node.module.split(".")[1]
                elif node.module == "tests":
                    yield from (alias.name for alias in node.names)
            elif isinstance(node, ast.Constant) and type(node.value) is str and re.fullmatch(r"tests\.\w+", node.value):
                yield node.value.split(".")[1]
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
