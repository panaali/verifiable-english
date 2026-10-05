"""Regressions for verification-gate accounting, isolation, and run identity."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import tomllib

import pytest

from subprocesses import HANG_TIMEOUT
from tools import gate, nested_pytest


def empty_result():
    return {"counts": {}, "failures": [], "skips": []}


def events():
    return {"collected": ["tests/a.py::test_a", "tests/b.py::test_b"],
            "selected": ["tests/a.py::test_a", "tests/b.py::test_b"],
            "deselected": [], "collection_reports": [],
            "tests": {"tests/a.py::test_a": {"outcome": "passed"},
                      "tests/b.py::test_b": {"outcome": "passed"}},
            "workers": {"gw0": ["tests/a.py::test_a", "tests/b.py::test_b"]}}


# The gate's two pytest runs: the serial collection, then the suite under xdist.
PYTEST_STAGES = ("Python collection", "Python suite")


@pytest.mark.parametrize("change,reason", [
    (lambda e: e["collected"].pop(), "baseline"),
    (lambda e: e["selected"].pop(), "without a deselection report"),
    (lambda e: e["collection_reports"].append(
        {"nodeid": "tests/c.py", "outcome": "skipped", "reason": "importorskip"}), "collection"),
])
def test_gate_rejects_missing_tests_and_module_skips(change, reason):
    result = empty_result()
    observed = events()
    change(observed)
    gate.interpret_pytest(result, observed, {"optional_tests": [], "deselected_tests": []},
                          events()["collected"])
    assert reason in str(result["failures"])


@pytest.mark.parametrize("body,conftest", [
    ("import pytest\npytest.skip('module unavailable', allow_module_level=True)\n", ""),
    ("import pytest\npytest.importorskip('ve_gate_absent_test_backend')\n", ""),
    ("def test_first(): pass\ndef test_second(): pass\n",
     "def pytest_collection_modifyitems(items):\n    items[:] = items[:1]\n"),
])
def test_pytest_plugin_observes_collection_bypasses(tmp_path, body, conftest):
    (tmp_path / "test_sample.py").write_text(body)
    if conftest:
        (tmp_path / "conftest.py").write_text(conftest)
    output = tmp_path / "events.json"
    env = nested_pytest.environment(os.environ, VE_GATE_PYTEST_RESULT=str(output),
                                    PYTHONPATH=str(gate.ROOT))
    run = subprocess.run(nested_pytest.command(["-q", "-p", "tools.gate_pytest", "-o", "addopts=",
                                                str(tmp_path)]),
                         cwd=gate.ROOT, env=env, capture_output=True, text=True)
    assert run.returncode in (0, 5), run.stdout + run.stderr
    observed = json.loads(output.read_text())
    if conftest:
        assert len(observed["collected"]) == 2
        assert len(observed["selected"]) == 1
        assert not observed["deselected"]
    else:
        assert observed["collection_reports"][0]["outcome"] == "skipped"


# One representative ambient override from every earlier environment finding,
# plus the ambient HOME and PATH every toolchain lookup used to start from.
POISON = {"PYTEST_ADDOPTS": "--ignore=tests/test_lean_conformance.py",
          "PYTEST_PLUGINS": "drop_tests", "CARGO_TARGET_DIR": "/tmp/stale",
          "CARGO_BUILD_TARGET": "other-target", "CARGO_HOME": "/tmp/poisoned-cargo-home",
          "RUSTFLAGS": "--cfg fake", "RUSTC": "/tmp/fake-rustc", "RUSTC_WRAPPER": "/bin/false",
          "RUSTC_WORKSPACE_WRAPPER": "/bin/false", "RUSTDOC": "/tmp/fake-rustdoc",
          "RUSTUP_TOOLCHAIN": "nightly", "RUSTUP_HOME": "/tmp/fake-rustup",
          "GIT_DIR": "/tmp/fake-git", "GIT_WORK_TREE": "/tmp/fake-worktree",
          "GIT_INDEX_FILE": "/tmp/fake-index", "GIT_CONFIG_GLOBAL": "/tmp/fake-config",
          "PYTHONPATH": "/tmp/fake-tools", "PYTHONHOME": "/tmp/fake-python",
          "UV_PYTHON": "/tmp/fake-python", "UV_CACHE_DIR": "/tmp/fake-uv-cache",
          "UV_INDEX_URL": "http://127.0.0.1:9/simple", "UV_CONFIG_FILE": "/tmp/fake-uv.toml",
          "LEAN_CC": "/bin/false", "LEAN_AR": "/bin/false", "LEAN_PATH": "/tmp/fake-oleans",
          "LEAN_SYSROOT": "/tmp/fake-lean", "LAKE_ARTIFACT_CACHE": "true",
          "LAKE_CACHE_DIR": "/tmp/fake-lake-cache", "LAKE_HOME": "/tmp/fake-lake",
          "ELAN_TOOLCHAIN": "leanprover/lean4:v4.0.0", "ELAN_HOME": "/tmp/fake-elan",
          "CC": "/bin/false", "LD_LIBRARY_PATH": "/tmp/fake-lib", "LD_PRELOAD": "/tmp/fake.so",
          "VE_LEAN_PREBUILT": "", "HOME": "/tmp/fake-home"}


def poison(monkeypatch, tmp_path):
    for name, value in POISON.items():
        monkeypatch.setenv(name, value)
    # Earlier PATH entries shadow every tool the gate runs.
    shadow = tmp_path / "shadow-bin"
    shadow.mkdir()
    for tool in ("lake", "lean", "cargo", "rustc", "uv", "git", "python3", "elan", "rustup"):
        (shadow / tool).write_text("#!/bin/sh\necho shadowed; exit 1\n")
        (shadow / tool).chmod(0o755)
    monkeypatch.setenv("PATH", f"{shadow}:{os.environ['PATH']}")


def normalized(value, scratch):
    return json.loads(json.dumps(value).replace(str(scratch), "<scratch>"))


def test_gate_environment_is_an_allowlist(tmp_path, monkeypatch):
    clean = gate.gate_environment(tmp_path / "clean")
    poison(monkeypatch, tmp_path)
    env = gate.gate_environment(tmp_path / "poisoned")
    assert set(env) == set(gate.ALLOWED_ENVIRONMENT)
    assert normalized(env, tmp_path / "poisoned") == normalized(clean, tmp_path / "clean")
    assert all(value.startswith(str(tmp_path / "poisoned")) for name, value in env.items()
               if name in ("HOME", "TMPDIR", "UV_CACHE_DIR", "LAKE_CACHE_DIR", "CARGO_HOME",
                           "PYTHONPYCACHEPREFIX"))
    # No bytecode cached before the gate is loaded in place of its source.
    assert not any(Path(env["PYTHONPYCACHEPREFIX"]).iterdir())
    with pytest.raises(RuntimeError, match="unlisted"):
        gate.record_environment({"environment": {}}, "base", {**env, "LEAN_CC": "/bin/false"})
    with pytest.raises(RuntimeError, match="unlisted"):
        gate.record_environment({"environment": {}}, "base", {**env, "VE_RUST_BINARY": "/x"})


def test_gate_environment_uses_real_repository_and_recorder(tmp_path, monkeypatch):
    fake_tools = tmp_path / "tools"
    fake_tools.mkdir()
    (fake_tools / "__init__.py").write_text("")
    (fake_tools / "gate_pytest.py").write_text("raise RuntimeError('fake recorder loaded')\n")
    marker = tmp_path / "sitecustomize-loaded"
    (tmp_path / "sitecustomize.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "absent-git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path))
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "fake-index"))
    env = gate.gate_environment(tmp_path / "scratch")
    sha, _ = gate.source_identity(env)
    assert sha == subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=gate.ROOT,
                                           env=env, text=True).strip()
    run = subprocess.run([sys.executable, "-c", "from tools import gate_pytest; "
                          "print(gate_pytest.__file__)"], cwd=gate.ROOT, env=env,
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert run.stdout.strip() == str(gate.ROOT / "tools/gate_pytest.py")
    assert not marker.exists()


def test_poisoned_toolchain_variables_do_not_reach_real_tools(tmp_path, monkeypatch):
    # Every override is live for the real tools: each wrapper would leave a mark.
    marker = tmp_path / "wrapper-ran"
    wrapper = tmp_path / "wrapper"
    wrapper.write_text(f"#!/bin/sh\ntouch {marker}\nexit 1\n")
    wrapper.chmod(0o755)
    poison(monkeypatch, tmp_path)
    for name in ("RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "LEAN_CC", "LEAN_AR", "CC"):
        monkeypatch.setenv(name, str(wrapper))
    monkeypatch.setenv("LAKE_CACHE_DIR", str(tmp_path / "poisoned-lake-cache"))
    env = gate.gate_environment(tmp_path / "scratch")
    result = {"toolchains": {}}
    gate.check_toolchains(result, env)
    lean_bin = gate.lean_toolchain(gate.account_home()) / "bin"
    assert Path(result["toolchains"]["paths"]["lean"]).parent == lean_bin
    assert Path(result["toolchains"]["paths"]["lake"]).parent == lean_bin
    assert "version 4.24.0" in result["toolchains"]["lean"]

    # A Lean package whose executable must be compiled and linked by Lake.
    package = tmp_path / "leanpkg"
    package.mkdir()
    (package / "lakefile.toml").write_text(
        'name = "probe"\ndefaultTargets = ["probe"]\n[[lean_exe]]\nname = "probe"\nroot = "Main"\n')
    (package / "Main.lean").write_text('def main : IO Unit := IO.println "probe"\n')
    # A directory toolchain file elan would honour instead of the pin.
    (package / "lean-toolchain").write_text("leanprover/lean4:v4.0.0\n")
    # Lake, unlike uv, never joins an ancestor package.
    (tmp_path / "lakefile.toml").write_text("invalid = [\n")
    lean = subprocess.run(["lean", "--version"], cwd=package, env=env, capture_output=True, text=True)
    assert lean.returncode == 0 and "version 4.24.0" in lean.stdout, lean.stdout + lean.stderr
    built = subprocess.run(["lake", "build"], cwd=package, env=env, capture_output=True, text=True)
    assert built.returncode == 0, built.stdout + built.stderr
    assert not any(Path(env["LAKE_CACHE_DIR"]).iterdir()), "Lake used an artifact cache"
    assert not (tmp_path / "poisoned-lake-cache").exists()
    ran = subprocess.run([str(package / ".lake/build/bin/probe")], env=env, capture_output=True,
                         text=True)
    assert ran.stdout == "probe\n"

    crate = tmp_path / "crate"
    (crate / "src").mkdir(parents=True)
    (crate / "src/main.rs").write_text("fn main() {}\n")
    (crate / "Cargo.toml").write_text('[package]\nname = "gate-probe"\nversion = "0.1.0"\nedition = "2021"\n')
    cargo = subprocess.run(["cargo", "build", "--offline", "--manifest-path", str(crate / "Cargo.toml")],
                           cwd=gate.scratch_of(env), env=env, capture_output=True, text=True)
    assert cargo.returncode == 0, cargo.stderr
    assert (crate / "target/debug/gate-probe").is_file()

    uv = subprocess.run(["uv", "run", "--frozen", "--no-sync", "python", "-c",
                         "import os, sys; print(sys.prefix, os.environ.get('PYTHONPATH'))"],
                        cwd=gate.ROOT, env=env, capture_output=True, text=True)
    assert uv.returncode == 0, uv.stderr
    assert uv.stdout.split() == [str(gate.ROOT / ".venv"), "None"]
    assert not marker.exists()


def pin_rust_binary(root, data=b"binary"):
    # The gate refuses a Rust build whose hash checkers.lock does not pin.
    lock = root / "lean/checkers.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(json.dumps({"rust_jsonl": [hashlib.sha256(data).hexdigest()]}))


def test_poisoned_ambient_environment_leaves_gate_result_unchanged(tmp_path, monkeypatch):
    root = tmp_path / "root"
    for name in ("lean/lean-toolchain", "rust-toolchain.toml", "uv.lock", "rust/Cargo.lock"):
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_bytes((gate.ROOT / name).read_bytes())
    for binary in [root / "rust/target/release/ve",
                   *(root / "lean/.lake/build/bin" / name for name in gate.LEAN_BINARIES)]:
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_text("binary")
        binary.chmod(0o755)
    pin_rust_binary(root)
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"version": 1, "optional_tests": [], "deselected_tests": []}))
    collection = tmp_path / "collection.json"
    collection.write_text(json.dumps(events()["collected"]))
    monkeypatch.setattr(gate, "ROOT", root)
    monkeypatch.setattr(gate, "POLICY", policy)
    monkeypatch.setattr(gate, "COLLECTION", collection)
    monkeypatch.setattr(gate, "REQUIRED_FAMILIES", ())
    versions = {"uv version": "uv 0.0.0", "lake version": "Lake (Lean version 4.24.0)",
                "lean version": "Lean (version 4.24.0)", "rustc version": "rustc 1.98.1 (x)",
                "cargo version": "cargo 1.98.1 (x)", "commit": "sha", "worktree status": "",
                "Python environment": str(root / ".venv"),
                "native Rust tests": "test result: ok. 2 passed; 0 failed; 0 ignored;"}

    def run(label):
        seen = []

        def fake_command(args, *, env, stage, cwd=None):
            seen.append({"args": args, "cwd": str(cwd), "env": dict(env), "stage": stage})
            if stage in PYTEST_STAGES:
                Path(env["VE_GATE_PYTEST_RESULT"]).write_text(json.dumps(events()))
            return versions.get(stage, "")

        monkeypatch.setattr(gate, "command", fake_command)
        output = tmp_path / f"{label}.json"
        monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(output)])
        code = gate.main()
        record = json.loads(output.read_text())
        scratch = Path(record["environment"]["base"]["HOME"]).parent
        return code, normalized(record, scratch), normalized(seen, scratch)

    clean = run("clean")
    assert clean[0] == 0, clean[1]["failures"]
    poison(monkeypatch, tmp_path)
    poisoned = run("poisoned")
    assert poisoned == clean
    allowed = set(gate.ALLOWED_ENVIRONMENT).union(*gate.STAGE_ENVIRONMENT.values())
    assert {name for row in poisoned[2] for name in row["env"]} <= allowed
    for row in poisoned[2]:
        assert "shadow-bin" not in row["env"]["PATH"]
        assert "fake" not in json.dumps(row["env"])
    assert set(poisoned[1]["environment"]) == {"base", "cargo", "pytest"}


def test_cargo_ignores_home_cache_and_manifest_configs(tmp_path, monkeypatch):
    source = tmp_path / "source"
    crate = source / "rust"
    (crate / "src").mkdir(parents=True)
    (crate / "src/main.rs").write_text("fn main() {}\n")
    (crate / "Cargo.toml").write_text('[package]\nname = "gate-config-probe"\nversion = "0.1.0"\nedition = "2021"\n')
    (crate / "Cargo.lock").write_text('version = 4\n\n[[package]]\nname = "gate-config-probe"\nversion = "0.1.0"\n')
    poisoned_home = tmp_path / "home"
    for directory in (source / ".cargo-home", poisoned_home / ".cargo", crate / ".cargo"):
        directory.mkdir(parents=True)
        (directory / "config.toml").write_text("invalid = [\n")
    real_root = gate.ROOT
    monkeypatch.setattr(gate, "ROOT", source)
    monkeypatch.setenv("HOME", str(poisoned_home))
    monkeypatch.setenv("CARGO_HOME", str(poisoned_home / ".cargo"))
    monkeypatch.setattr(gate, "ROOT", real_root)
    env = rust_environment(tmp_path / "scratch")
    monkeypatch.setattr(gate, "ROOT", source)
    with gate.isolated_cargo(env) as (cargo_env, cwd):
        assert not cwd.is_relative_to(source)
        assert cargo_env["CARGO_HOME"] != str(source / ".cargo-home")
        assert not (Path(cargo_env["CARGO_HOME"]) / "config.toml").exists()
        run = subprocess.run(["cargo", "metadata", "--offline", "--no-deps",
                              "--format-version", "1", "--manifest-path", str(crate / "Cargo.toml")],
                             cwd=cwd, env=cargo_env, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr


def rust_environment(scratch):
    env = gate.gate_environment(scratch)
    pin = tomllib.loads((gate.ROOT / "rust-toolchain.toml").read_text())["toolchain"]["channel"]
    rust = gate.rust_toolchain(gate.account_home(), pin, env)
    env["PATH"] = f"{rust / 'bin'}:{env['PATH']}"
    return env


@pytest.mark.parametrize("location", [".cargo/config.toml", ".cargo/config", "scratch/.cargo/config.toml",
                                      "scratch/cargo-home/config.toml"])
def test_gate_refuses_cargo_config_in_any_ancestor(tmp_path, location):
    # A world-writable ancestor such as /tmp can hold a config whose runner
    # prints a passing cargo test summary without running any test.
    env = rust_environment(tmp_path / "scratch")
    config = tmp_path / location
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text('[target."cfg(all())"]\nrunner = "echo test result: ok. 9 passed; 0 failed; 0 ignored;"\n'
                      "invalid = [\n")
    workdir = tmp_path / "scratch/cargo"
    workdir.mkdir()
    read = subprocess.run(["cargo", "metadata", "--offline", "--no-deps", "--format-version", "1",
                           "--manifest-path", str(gate.ROOT / "rust/Cargo.toml")],
                          cwd=workdir, env=env, capture_output=True, text=True)
    assert read.returncode != 0 and str(config) in read.stderr, read.stderr
    workdir.rmdir()
    with pytest.raises(RuntimeError, match="ambient configuration"):
        with gate.isolated_cargo(env):
            pass
    config.unlink()
    workdir.rmdir()
    with gate.isolated_cargo(env) as (cargo_env, cwd):
        assert cwd == workdir and cargo_env["CARGO_NET_OFFLINE"] == "true"


def ancestor_workspace(tmp_path):
    # A copy of the checkout's Python project whose own lock is invalid, below a
    # parent workspace that lists it as a member and carries a valid lock.
    outer = tmp_path / "outer"
    checkout = outer / "checkout"
    checkout.mkdir(parents=True)
    for name in ("pyproject.toml", ".python-version"):
        (checkout / name).write_bytes((gate.ROOT / name).read_bytes())
    (checkout / "uv.lock").write_text("invalid = [\n")
    lock = (gate.ROOT / "uv.lock").read_text().replace(
        'source = { editable = "." }', 'source = { editable = "checkout" }')
    (outer / "uv.lock").write_text(lock.replace(
        "\n[[package]]", '\n[manifest]\nmembers = ["verifiable-english"]\n\n[[package]]', 1))
    (outer / "pyproject.toml").write_text('[tool.uv.workspace]\nmembers = ["checkout"]\n')
    return outer, checkout


def test_gate_refuses_ancestor_uv_workspace(tmp_path, monkeypatch):
    outer, checkout = ancestor_workspace(tmp_path)
    env = gate.gate_environment(tmp_path / "scratch")
    sync = ["uv", "sync", "--locked", "--group", "dev", "--dry-run", "--offline"]
    joined = subprocess.run(sync, cwd=checkout, env=env, capture_output=True, text=True)
    assert joined.returncode == 0, joined.stderr
    assert str(outer / ".venv") in joined.stderr
    monkeypatch.setattr(gate, "ROOT", checkout)
    monkeypatch.setattr(gate, "command", lambda *args, **kwargs: pytest.fail("uv invoked"))
    with pytest.raises(RuntimeError, match="ancestor workspace"):
        gate.check_python_project({"toolchains": {}}, env)
    (outer / "pyproject.toml").unlink()
    alone = subprocess.run(sync, cwd=checkout, env=env, capture_output=True, text=True)
    assert alone.returncode != 0 and "uv.lock" in alone.stderr, alone.stderr


@pytest.mark.parametrize("ancestor,refused", [
    ('[tool.uv.workspace]\nmembers = ["*"]\n', True),
    ('[project]\nname = "outer"\n[tool.uv.workspace]\n', True),
    ("invalid = [\n", True),
    ('tool = "uv"\n', True),
    ("[tool]\nuv = 1\n", True),
    ('[project]\nname = "outer"\n', False),
    ("[tool.uv]\nmanaged = true\n", False),
    ("[tool.black]\nline-length = 1\n", False),
], ids=["workspace", "project-workspace", "malformed", "tool-string", "uv-integer", "project",
        "uv-settings", "other-tool"])
def test_ancestor_pyproject_kinds(tmp_path, ancestor, refused):
    checkout = tmp_path / "a/b/checkout"
    checkout.mkdir(parents=True)
    (tmp_path / "a/pyproject.toml").write_text(ancestor)
    (checkout / "pyproject.toml").write_text('[tool.uv.workspace]\nmembers = ["*"]\n')
    expected = [tmp_path / "a/pyproject.toml"] if refused else []
    assert gate.uv_workspace_ancestors(checkout) == expected


def test_gate_rejects_python_environment_outside_checkout(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "ROOT", tmp_path / "checkout")
    stages = {"Python version": "Python 3.14.7",
              "Python environment": str(tmp_path / ".venv")}
    monkeypatch.setattr(gate, "command", lambda args, *, env, stage, cwd=None: stages.get(stage, ""))
    with pytest.raises(RuntimeError, match="selected the environment"):
        gate.check_python_project({"toolchains": {}}, {})
    stages["Python environment"] = str(tmp_path / "checkout/.venv")
    gate.check_python_project({"toolchains": {}}, {})


def test_cargo_workspace_root_ignores_ancestor_workspaces(tmp_path):
    # The Rust mirror: rust/Cargo.toml declares its own [workspace], so Cargo
    # stops there and never takes an ancestor workspace's Cargo.lock.
    assert "workspace" in tomllib.loads((gate.ROOT / "rust/Cargo.toml").read_text())
    rust = tmp_path / "outer/checkout/rust"
    (rust / "member/src").mkdir(parents=True)
    (rust / "member/src/lib.rs").write_text("")
    (rust / "member/Cargo.toml").write_text(
        '[package]\nname = "member"\nversion = "0.1.0"\nedition = "2021"\n')
    (rust / "Cargo.toml").write_text('[workspace]\nmembers = ["member"]\nresolver = "2"\n')
    (tmp_path / "outer/Cargo.toml").write_text('[workspace]\nmembers = ["checkout/rust/member"]\n')
    (tmp_path / "outer/Cargo.lock").write_text("invalid = [\n")
    env = rust_environment(tmp_path / "scratch")
    with gate.isolated_cargo(env) as (cargo_env, cwd):
        run = subprocess.run(["cargo", "metadata", "--offline", "--no-deps", "--format-version", "1",
                              "--manifest-path", str(rust / "Cargo.toml")],
                             cwd=cwd, env=cargo_env, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)["workspace_root"] == str(rust)


def test_cargo_registry_seed_takes_only_locked_archives(tmp_path, monkeypatch):
    good, stale = b"locked crate", b"edited crate"
    index = "index.crates.io-0000000000000000"
    registry = tmp_path / "root/.cargo-home/registry"
    for name, data in (("good-1.0.0.crate", good), ("bad-1.0.0.crate", stale)):
        (registry / "cache" / index).mkdir(parents=True, exist_ok=True)
        (registry / "cache" / index / name).write_bytes(data)
    (registry / "src" / index / "good-1.0.0").mkdir(parents=True)
    (registry / "src" / index / "good-1.0.0/lib.rs").write_text("edited source")
    (registry / "index" / index).mkdir(parents=True)
    (registry / "index" / index / "config.json").write_text("{}")
    (tmp_path / "root/rust").mkdir()
    checksum = hashlib.sha256(good).hexdigest()
    (tmp_path / "root/rust/Cargo.lock").write_text(
        f'version = 4\n\n[[package]]\nname = "good"\nversion = "1.0.0"\nchecksum = "{checksum}"\n')
    monkeypatch.setattr(gate, "ROOT", tmp_path / "root")
    home = tmp_path / "cargo-home"
    gate.seed_registry(home)
    assert (home / "registry/cache" / index / "good-1.0.0.crate").read_bytes() == good
    assert not (home / "registry/cache" / index / "bad-1.0.0.crate").exists()
    assert not (home / "registry/src").exists()
    assert (home / "registry/index" / index / "config.json").is_file()


def test_fsmonitor_hook_cannot_hide_edited_source(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = gate.gate_environment(tmp_path / "scratch")
    identity = ["-c", "user.name=gate", "-c", "user.email=gate@example.invalid"]
    for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "init"]):
        subprocess.run(["git", *identity, *args], cwd=repo, env=env, check=True)
    (repo / "source.py").write_text("one\n")
    subprocess.run(["git", "add", "source.py"], cwd=repo, env=env, check=True)
    subprocess.run(["git", *identity, "commit", "-q", "-m", "source"], cwd=repo, env=env, check=True)
    # The hook reports that nothing has changed since any token.
    hook = tmp_path / "fsmonitor"
    hook.write_text("#!/bin/sh\nprintf 'token\\0'\n")
    hook.chmod(0o755)
    subprocess.run(["git", "config", "core.fsmonitor", str(hook)], cwd=repo, env=env, check=True)
    subprocess.run(["git", "status", "--porcelain"], cwd=repo, env=env, check=True)
    (repo / "source.py").write_text("two\n")
    plain = subprocess.run(["git", "status", "--porcelain"], cwd=repo, env=env,
                           capture_output=True, text=True, check=True)
    assert plain.stdout == ""
    monkeypatch.setattr(gate, "ROOT", repo)
    assert gate.source_identity(env)[1] is True


def test_gate_rejects_untracked_source_before_build(tmp_path, monkeypatch):
    output = tmp_path / "record.json"
    monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(output)])
    seen = []

    def fake_command(args, *, env, stage, cwd=None):
        seen.append(stage)
        if stage == "commit":
            return "old"
        assert stage == "worktree status"
        assert "--untracked-files=all" in args
        return "?? tests/conftest.py"

    monkeypatch.setattr(gate, "command", fake_command)
    assert gate.main() == 1
    assert seen == ["commit", "worktree status"]
    assert json.loads(output.read_text())["dirty"] is True


def test_terminated_gate_cannot_leave_old_pass_record(tmp_path):
    output = tmp_path / "record.json"
    output.write_text('{"status":"passed"}')
    started = tmp_path / "started"
    # The handler lets the gate's cleanup remove its scratch directory; the
    # record must already be failed when the first work starts (an event, not
    # an interval: under load the child can take any time to get there).
    script = ("import signal, sys, time\nfrom pathlib import Path\nfrom tools import gate\n"
              "signal.signal(signal.SIGTERM, lambda *args: sys.exit(1))\n"
              "started = Path(sys.argv[2])\n"
              "def work(*args, **kwargs):\n"
              "    started.touch()\n"
              f"    time.sleep({HANG_TIMEOUT})\n"
              "gate.command = work\n"
              "sys.argv = ['gate.py', '--output', sys.argv[1]]\n"
              "gate.main()\n")
    process = subprocess.Popen([sys.executable, "-c", script, str(output), str(started)],
                               cwd=gate.ROOT, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + HANG_TIMEOUT
        while not started.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        assert started.exists(), "the gate never started work"
        assert json.loads(output.read_text())["status"] == "failed", "gate did not reset the record before work"
    finally:
        process.send_signal(signal.SIGTERM)
        process.wait(timeout=HANG_TIMEOUT)
    assert json.loads(output.read_text())["status"] == "failed"


@pytest.mark.parametrize("interruption", [KeyboardInterrupt, TypeError, AttributeError])
def test_interrupted_gate_cannot_record_pass(tmp_path, monkeypatch, interruption):
    output = tmp_path / "record.json"
    output.write_text('{"status":"passed"}')
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"version": 1}))
    collection = tmp_path / "collection.json"
    collection.write_text(json.dumps(["tests/a.py::test_a"]))
    monkeypatch.setattr(gate, "POLICY", policy)
    monkeypatch.setattr(gate, "COLLECTION", collection)
    monkeypatch.setattr(gate, "check_toolchains", lambda result, env: None)
    monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(output)])

    def fake_command(args, *, env, stage, cwd=None):
        if stage == "commit":
            return "unchanged"
        if stage == "worktree status":
            return ""
        if stage == "Lean build":
            raise interruption("interrupted")
        if stage == "Python environment":
            return str(gate.ROOT / ".venv")
        return ""

    monkeypatch.setattr(gate, "command", fake_command)
    with pytest.raises(interruption):
        gate.main()
    record = json.loads(output.read_text())
    assert record["status"] == "failed"
    assert record["stages"] == ["toolchains"]


@pytest.mark.parametrize("change_head,change_worktree", [(False, False), (True, False),
                                                         (False, True)])
def test_gate_resets_record_uses_own_binary_and_checks_source_at_end(
        tmp_path, monkeypatch, change_head, change_worktree):
    rust_binary = tmp_path / "rust/target/release/ve"
    rust_binary.parent.mkdir(parents=True)
    rust_binary.write_text("binary")
    pin_rust_binary(tmp_path)
    (tmp_path / "rust/Cargo.lock").write_text("version = 4\n")
    for name in gate.LEAN_BINARIES:
        binary = tmp_path / "lean/.lake/build/bin" / name
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_text("binary")
        binary.chmod(0o755)
    rust_binary.chmod(0o755)
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"version": 1, "optional_tests": [], "deselected_tests": []}))
    collection = tmp_path / "collection.json"
    collection.write_text(json.dumps(events()["collected"]))
    output = tmp_path / "record.json"
    output.write_text('{"status":"passed"}')
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "POLICY", policy)
    monkeypatch.setattr(gate, "COLLECTION", collection)
    monkeypatch.setattr(gate, "REQUIRED_FAMILIES", ())
    monkeypatch.setattr(gate, "check_toolchains", lambda result, env: None)
    monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(output)])
    sha_calls = 0
    seen = []

    def fake_command(args, *, env, stage, cwd=None):
        nonlocal sha_calls
        seen.append((args, dict(env), stage))
        if stage == "commit":
            sha_calls += 1
            assert json.loads(output.read_text())["status"] == "failed"
            return "new" if change_head and sha_calls == 2 else "old"
        if stage == "worktree status":
            assert "--untracked-files=all" in args
            return "?? tests/conftest.py" if change_worktree and sha_calls == 2 else ""
        if stage == "Python environment":
            return str(tmp_path / ".venv")
        if stage == "native Rust tests":
            return "test result: ok. 2 passed; 0 failed; 0 ignored;"
        if stage in PYTEST_STAGES:
            Path(env["VE_GATE_PYTEST_RESULT"]).write_text(json.dumps(events()))
        return ""

    monkeypatch.setattr(gate, "command", fake_command)
    code = gate.main()
    record = json.loads(output.read_text())
    assert code == int(change_head or change_worktree)
    assert record["status"] == ("failed" if code else "passed")
    assert "lean_audit" in record["stages"]
    cargo = [row for row in seen if row[2] in ("Rust build", "native Rust tests")]
    assert len(cargo) == 2
    # The host build the Rust backend loads; an explicit --target changes its hash.
    assert all("--target-dir" in row[0] and "--target" not in row[0] for row in cargo)
    assert all(f"--remap-path-prefix={row[1]['CARGO_HOME']}=/cargo-home"
               in row[1]["CARGO_ENCODED_RUSTFLAGS"].split("\x1f") for row in cargo)
    assert all(row[1]["CARGO_HOME"] != str(tmp_path / ".cargo-home") for row in cargo)
    assert all(row[1]["CARGO_NET_OFFLINE"] == "true" for row in cargo)
    pytest_env = next(row[1] for row in seen if row[2] == "Python suite")
    assert pytest_env["VE_RUST_BINARY"] == str(rust_binary)
    assert [row[2] for row in seen].count("commit") == 2


def test_gate_refuses_a_rust_build_checkers_lock_does_not_pin(tmp_path, monkeypatch):
    # A build that embeds its checkout's paths has a hash no lock can pin for
    # every checkout; the gate stops before the suite instead of reporting
    # every Rust-backed test as CheckerUnavailable.
    rust_binary = tmp_path / "rust/target/release/ve"
    for binary in [rust_binary, *(tmp_path / "lean/.lake/build/bin" / name for name in gate.LEAN_BINARIES)]:
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_text("binary")
        binary.chmod(0o755)
    (tmp_path / "rust/Cargo.lock").write_text("version = 4\n")
    pin_rust_binary(tmp_path, b"another build")
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"version": 1, "optional_tests": [], "deselected_tests": []}))
    collection = tmp_path / "collection.json"
    collection.write_text(json.dumps(events()["collected"]))
    output = tmp_path / "record.json"
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "POLICY", policy)
    monkeypatch.setattr(gate, "COLLECTION", collection)
    monkeypatch.setattr(gate, "check_toolchains", lambda result, env: None)
    monkeypatch.setattr(sys, "argv", ["gate.py", "--output", str(output)])
    stages = []

    def fake_command(args, *, env, stage, cwd=None):
        stages.append(stage)
        return str(tmp_path / ".venv") if stage == "Python environment" else ""

    monkeypatch.setattr(gate, "command", fake_command)
    assert gate.main() == 1
    record = json.loads(output.read_text())
    assert record["status"] == "failed"
    assert "rust_build" not in record["stages"]
    assert any("not pinned in lean/checkers.lock" in failure["reason"] for failure in record["failures"])
    assert "Python suite" not in stages
