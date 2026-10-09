"""Nested pytest runs do not depend on the outer run's plugin settings (testperf review B).

`tools/gate.py` runs the suite with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1. The contract input recorder's nested
run passed `-n` without loading xdist, so `test_gate_corpus_holds_every_contract_and_soft_test_input` exited
4 ("unrecognized arguments: -n") under the gate and passed in an ordinary run. Every pytest command another
process runs is now built by `tools/nested_pytest.py`, which names its plugins and gives the run an
environment of its own; these tests run such commands under each ambient setting and fail on a pytest command
built anywhere else.
"""
import ast
import json
import os
from pathlib import Path
import subprocess

import pytest

from conformance import wire_contract_gate
from tests.subprocesses import HANG_TIMEOUT
from tools import nested_pytest

ROOT = Path(__file__).resolve().parents[1]
# Outer-run settings a nested run must not depend on: the gate's (autoload off), an ordinary run's
# (autoload on), and ambient options, plugins and xdist identity that would change the nested run.
AMBIENT = {
    "gate": {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
    "ordinary": {},
    "addopts": {"PYTEST_ADDOPTS": "-n 3 --ignore=tests", "PYTEST_PLUGINS": "ve_absent_plugin"},
    "xdist-worker": {"PYTEST_XDIST_WORKER": "gw5", "PYTEST_XDIST_WORKER_COUNT": "8",
                     "PYTEST_CURRENT_TEST": "tests/x.py::y (call)"},
}
# Each test notes the process it ran in; the first also needs the hypothesis plugin's option.
SAMPLE = '''import os
from pathlib import Path


def note():
    (Path(__file__).parent / ("worker-" + os.environ.get("PYTEST_XDIST_WORKER", "main"))).touch()


def test_plugins(request):
    request.config.getoption("--hypothesis-show-statistics")
    note()


def test_second():
    note()
'''


def _clean(monkeypatch, ambient):
    for name in list(os.environ):
        if name.startswith("PYTEST_"):
            monkeypatch.delenv(name)
    for name, value in ambient.items():
        monkeypatch.setenv(name, value)


@pytest.mark.parametrize("ambient", sorted(AMBIENT))
@pytest.mark.parametrize("workers", [1, 2])
def test_nested_run_is_the_same_under_every_ambient_setting(tmp_path, monkeypatch, ambient, workers):
    _clean(monkeypatch, AMBIENT[ambient])
    (tmp_path / "test_sample.py").write_text(SAMPLE)
    run = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", "-o", "addopts=",
                                                "--rootdir", str(tmp_path), str(tmp_path)], workers=workers),
                         cwd=tmp_path, env=nested_pytest.environment(os.environ), capture_output=True, text=True,
                         timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "2 passed" in run.stdout, run.stdout
    ran = {path.name for path in tmp_path.glob("worker-*")}
    # One worker runs in the pytest process; more run on xdist, never as the outer run's worker.
    if workers == 1:
        assert ran == {"worker-main"}
    else:
        assert ran and ran <= {"worker-gw0", "worker-gw1"}


def test_record_test_inputs_runs_under_the_gate_environment(tmp_path, monkeypatch):
    """The reproduced failure: the recorder's parallel run under the gate's environment."""
    _clean(monkeypatch, AMBIENT["gate"])
    monkeypatch.setattr(wire_contract_gate, "RECORDED_TESTS", ("tests/test_softnorms_public_contract.py",))
    output = tmp_path / "inputs.json"
    result = wire_contract_gate.record_test_inputs(output, workers=2)
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-4000:]
    assert "7 passed" in result.stdout and " skipped" not in result.stdout, result.stdout[-4000:]
    recorded = json.loads(output.read_text())
    assert recorded and {Path(label.split("::")[0]).name for label, _, _ in recorded} == {
        "test_softnorms_public_contract.py"}


@pytest.mark.parametrize("arguments", [["-n", "2"], ["-n2"], ["--numprocesses=2"], ["--dist=loadfile"],
                                       ["-p", "xdist"], ["-p", "hypothesis.extra.pytestplugin"]])
def test_plugin_options_go_through_the_builder(arguments):
    with pytest.raises(ValueError):
        nested_pytest.command(["-q", *arguments])


@pytest.mark.parametrize("workers", [0, -1, True, 2.0, "2"])
def test_worker_count_is_a_positive_int(workers):
    with pytest.raises(ValueError):
        nested_pytest.command(["-q"], workers=workers)


def test_environment_drops_the_outer_runs_settings():
    base = {"PATH": "/bin", "PYTEST_ADDOPTS": "-x", "PYTEST_PLUGINS": "p", "PYTEST_XDIST_WORKER": "gw0",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "", "VE_GATE_PYTEST_RESULT": "/r", "VE_GATE_PYTEST_PROGRESS": "/p",
            "VE_TEST_PROFILE_DIR": "/d", "VE_NATIVE_PREBUILT": "1"}
    assert nested_pytest.environment(base, VE_GATE_PYTEST_RESULT="/mine") == {
        "PATH": "/bin", "VE_NATIVE_PREBUILT": "1", "VE_GATE_PYTEST_RESULT": "/mine",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}


# Pytest commands built outside the builder, each with its reason.
UNBUILT = {
    # Outermost, isolated mutant runs: each script changes one file, runs one targeted failing
    # test, restores the source, and records the failure before moving to the next mutant.
    "docs/lean-first/b8/seeds.py",
    "docs/lean-first/b8/lean_seeds.py",
    "docs/lean-first/b16c/seed_faults.py",
    # Frozen with the P1 preregistration (experiments/P1-deference/freeze.json); a serial outermost run
    # from a shell that passes no plugin option.
    "experiments/p1_preflight.py",
    # `pytest.main` under `if __name__ == "__main__"`: the outermost run when the file is executed.
    "tests/test_evidence_bounds.py",
    # Data: the text of a shell action in the agent-policy use case's log, never executed.
    "usecases/agent-policy/emit_log.py",
    # This file: the scan's own examples, which `test_the_scan_finds_each_way_to_build_a_command` parses.
    "tests/test_nested_pytest.py",
}


def _strings(node):
    return [element.value if isinstance(element, ast.Constant) and isinstance(element.value, str) else None
            for element in node.elts]


def pytest_commands(tree):
    """Lines that build a pytest command: a list or tuple whose word `pytest` follows `-m`, `run` or `exec`,
    starts it, or sits among options; a `pytest.main` call; a string holding a pytest shell command."""
    docstrings = {id(body[0].value) for node in ast.walk(tree)
                  if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                  for body in [node.body] if body and isinstance(body[0], ast.Expr)}
    for node in ast.walk(tree):
        if isinstance(node, (ast.List, ast.Tuple)):
            words = _strings(node)
            for index, word in enumerate(words):
                if word in ("pytest", "py.test") and (
                        index == 0 or words[index - 1] in ("-m", "run", "exec")
                        or any(other and other.startswith("-") for other in words)):
                    yield node.lineno
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "main" \
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "pytest":
            yield node.lineno
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            # A shell command: `pytest` after `-m`, `run` or `exec`, or first and followed by an option.
            words = node.value.split()
            if any(word in ("pytest", "py.test") and (
                    (index and words[index - 1] in ("-m", "run", "exec"))
                    or (index == 0 and len(words) > 1 and words[1].startswith("-")))
                   for index, word in enumerate(words)):
                yield node.lineno


def _calls(tree, name):
    return any(isinstance(node, ast.Call) and (
        (isinstance(node.func, ast.Attribute) and node.func.attr == name
         and isinstance(node.func.value, ast.Name) and node.func.value.id == "nested_pytest"))
        for node in ast.walk(tree))


def tracked_python():
    listed = subprocess.run(["git", "ls-files", "-z", "--", "*.py"], cwd=ROOT, capture_output=True, check=True,
                            timeout=HANG_TIMEOUT).stdout.decode().split("\0")
    return [path for path in listed if path and (ROOT / path).is_file()]


def test_every_pytest_command_is_built_by_the_builder():
    """A file that builds a pytest command itself is listed in UNBUILT with its reason; a file that builds
    one with `nested_pytest.command` also gives it `nested_pytest.environment`."""
    found, unpaired = {}, []
    for path in tracked_python():
        tree = ast.parse((ROOT / path).read_bytes(), filename=path)
        lines = sorted(set(pytest_commands(tree)))
        if lines and path != "tools/nested_pytest.py":
            found[path] = lines
        if _calls(tree, "command") and not _calls(tree, "environment"):
            unpaired.append(path)
    assert set(found) == UNBUILT, found
    assert unpaired == []
    # The builder's callers: the gate, the selector, the layer mutations, the gate corpus and these tests.
    users = {path for path in tracked_python()
             if _calls(ast.parse((ROOT / path).read_bytes()), "command")}
    assert {"tools/gate.py", "tools/select_tests.py", "tools/mutation_check.py",
            "conformance/wire_contract_gate.py", "tests/test_gate_integrity.py"} <= users


@pytest.mark.parametrize("source,expected", [
    ('subprocess.run([sys.executable, "-m", "pytest", "-n", "2"])', 1),
    ('subprocess.run(["uv", "run", "pytest", "tests"])', 1),
    ('subprocess.run(("pytest", "-q"))', 1),
    ('subprocess.run("python -m pytest -n 4", shell=True)', 1),
    ('pytest.main(["-q"])', 1),
    ('subprocess.run("pytest -x tests", shell=True)', 1),
    ('STAGES = ("toolchains", "pytest")', 0),
    ('raise RuntimeError("pytest did not write its result events")', 0),
    ('def f():\n    """Run python -m pytest -q."""', 0),
])
def test_the_scan_finds_each_way_to_build_a_command(source, expected):
    assert len(list(pytest_commands(ast.parse(source)))) == expected
