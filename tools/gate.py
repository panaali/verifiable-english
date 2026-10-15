#!/usr/bin/env python3
"""Full offline verification gate. Run from any directory: python3 tools/gate.py."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import lake_outputs, nested_pytest, quarantine, rust_build  # noqa: E402
POLICY = ROOT / "tools/gate-optional.json"
LEAN_BINARIES = ("ve_conformance", "ve_service", "ve_senses_route")
REQUIRED_STAGES = ("toolchains", "lean_build", "lean_audit", "rust_build",
                   "cargo_test", "pytest")
REQUIRED_FAMILIES = (
    "test_conformance.py", "test_lean_conformance.py", "test_rust_conformance.py",
    "test_p0_three_way.py", "test_norms_three_way.py", "test_nary_differential.py",
    "test_data_three_way.py", "test_definitions_differential.py",
    "test_lean_certificates.py", "test_closure_certificates.py",
    "test_grammar_backends.py",
)
# Every stage runs with an environment built from nothing but these names.
# Toolchains are located under the account's home directory from the password
# database, never from HOME, PATH, ELAN_HOME, RUSTUP_HOME or any other
# inherited variable, and are put on PATH as their own bin directories so that
# no elan or rustup proxy can select a different version.
SYSTEM_PATH = ("/usr/bin", "/bin")
UV_LOCATIONS = (".local/bin/uv", ".cargo/bin/uv", "/usr/local/bin/uv", "/usr/bin/uv")
ALLOWED_ENVIRONMENT = (
    "PATH",                             # pinned Rust and Lean bin dirs, uv, SYSTEM_PATH
    "HOME", "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME",  # fresh, in scratch
    "TMPDIR",                           # fresh, in scratch
    "LANG", "LC_ALL",                   # C.UTF-8
    "GIT_CONFIG_NOSYSTEM",              # 1: no /etc/gitconfig
    "UV_CACHE_DIR",                     # fresh, in scratch
    "UV_NO_CONFIG",                     # 1: no uv.toml from the user, system or ancestors;
                                        # ancestor workspaces: uv_workspace_ancestors
    "LAKE_CACHE_DIR",                   # fresh, in scratch
    "CARGO_HOME",                       # fresh, in scratch; seeded by isolated_cargo
    "PYTHONNOUSERSITE",                 # 1
    "PYTHONPYCACHEPREFIX",              # fresh, in scratch: no bytecode cached before the gate
    "PYTEST_DISABLE_PLUGIN_AUTOLOAD",   # 1
)
# Added only for the stage that needs them.
STAGE_ENVIRONMENT = {
    "cargo": ("CARGO_NET_OFFLINE", "CARGO_ENCODED_RUSTFLAGS"),
    "source identity": ("GIT_INDEX_FILE",),  # a fresh index in scratch, read from the commit
    "pytest": ("VE_GATE_PYTEST_RESULT", "VE_GATE_PYTEST_PROGRESS", "VE_NATIVE_PREBUILT", "VE_LEAN_PREBUILT",
               "VE_RUST_PREBUILT", "VE_RUST_BINARY"),
}
# The gate's pytest invocation, shared by its collection run, its suite run and the
# collection of the merge base (tools/gate_collection.py), so both sides are collected
# alike. Plugin autoload is off in the gate, so every plugin is named here or by
# tools/nested_pytest.py.
PYTEST_ARGS = ("-q", "-p", "tools.gate_pytest", "-o", "addopts=-ra", "-m", "not live", "tests")
# The stages a rerun of failed tests (`--rerun-failed`) takes from the failed gate it reruns: on the same
# tree and toolchains they are the same, and the failed gate passed them before its suite ran.
REUSED_STAGES = ("lean_audit", "cargo_test")
# The failures of a gate whose failed tests can be rerun alone: tests that failed or have no result.
RERUNNABLE = frozenset({"pytest", "pytest command"})


def pytest_args(files: list[str] | None = None) -> tuple[str, ...]:
    """PYTEST_ARGS over `files` (test files under tests/) instead of the whole of tests/."""
    return PYTEST_ARGS if files is None else (*PYTEST_ARGS[:-1], *files)


def collection_command(python: list[str], files: list[str] | None = None) -> list[str]:
    return nested_pytest.command(["--collect-only", *pytest_args(files)], python=python)


def suite_command(python: list[str], workers: str, files: list[str] | None = None) -> list[str]:
    """The suite on xdist, even on one worker: merge_pytest_events reads each worker's collection."""
    return nested_pytest.command(pytest_args(files), workers=workers if workers == "auto" else int(workers),
                                 xdist=True, python=python)


def merge_pytest_events(collection: dict, suite: dict) -> dict:
    """The collection run's IDs with the suite run's results. Every xdist worker of the
    suite run must have collected exactly the collection run's selection."""
    workers = suite.get("workers")
    if not isinstance(workers, dict) or not workers:
        raise RuntimeError("the suite run recorded no worker collection")
    for worker, ids in sorted(workers.items()):
        if ids != collection["selected"]:
            raise RuntimeError(f"worker {worker} collected {len(ids)} tests, not the collection run's "
                               f"{len(collection['selected'])}")
    return {**collection, "tests": suite["tests"], "workers": workers}


def collect(env: dict[str, str], result_file: Path, *, python: list[str] | None = None,
            files: list[str] | None = None) -> dict:
    """Run the gate's collection in `env` (plugin autoload off) and return its events."""
    env = nested_pytest.environment(env, VE_GATE_PYTEST_RESULT=str(result_file))
    command(collection_command(python or [sys.executable], files), env=env, stage="Python collection")
    return json.loads(result_file.read_text())


def retry_command(python: list[str], tests: list[str]) -> list[str]:
    """PYTEST_ARGS over the node IDs `tests`, serially: a quarantined failure's run alone."""
    return nested_pytest.command((*PYTEST_ARGS[:-1], *tests), python=python)


def exit_reason(stage: str, code: int) -> str:
    return f"{stage}: exit {code}"


def command(args: list[str], *, cwd: Path = ROOT, env: dict[str, str], stage: str) -> str:
    print(f"[gate] {stage}: {' '.join(args)}", flush=True)
    try:
        done = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
    except OSError as exc:
        raise RuntimeError(f"{stage}: {exc}") from exc
    print(done.stdout, end="" if done.stdout.endswith("\n") else "\n", flush=True)
    if done.returncode:
        raise RuntimeError(exit_reason(stage, done.returncode))
    return done.stdout.strip()


def version(result: dict, executable: str, args: list[str], *, env: dict[str, str],
            directory: Path, cwd: Path = ROOT) -> str:
    # The checked binary must be the one every later stage resolves from PATH.
    path = shutil.which(executable, path=env["PATH"])
    if path is None:
        raise RuntimeError(f"required backend missing: {executable}")
    if Path(path).parent != directory:
        raise RuntimeError(f"{executable} resolves to {path}, not the pinned {directory}")
    result["toolchains"].setdefault("paths", {})[executable] = path
    return command([path, *args], cwd=cwd, env=env,
                   stage=f"{executable} version").splitlines()[0]


def account_home() -> Path:
    # From the password database: HOME is ambient and the gate replaces it.
    return Path(pwd.getpwuid(os.getuid()).pw_dir)


def lean_toolchain(home: Path) -> Path:
    # elan stores leanprover/lean4:v4.24.0 as toolchains/leanprover--lean4---v4.24.0.
    # Using that directory directly bypasses elan's default, override and
    # ELAN_TOOLCHAIN resolution, which can differ between directories.
    spec = (ROOT / "lean/lean-toolchain").read_text().strip()
    directory = home / ".elan/toolchains" / spec.replace(":", "---").replace("/", "--")
    if not (directory / "bin/lake").is_file():
        raise RuntimeError(f"pinned Lean toolchain {spec} is not installed at {directory}")
    return directory


def rust_toolchain(home: Path, pin: str, env: dict[str, str]) -> Path:
    # A stable toolchain can satisfy the exact pin without downloading another
    # copy. Its bin directory is used directly, so no rustup proxy can install
    # or switch versions during a gate.
    toolchains = home / ".rustup/toolchains"
    for directory in [*sorted(toolchains.glob(f"{pin}-*")), *sorted(toolchains.glob("stable-*"))]:
        rustc = directory / "bin/rustc"
        if not rustc.is_file():
            continue
        probe = subprocess.run([str(rustc), "--version"], env=env, text=True, capture_output=True)
        if probe.returncode == 0 and probe.stdout.startswith(f"rustc {pin} "):
            return directory
    raise RuntimeError(f"required Rust toolchain {pin} is not installed")


def check_toolchains(result: dict, env: dict[str, str]) -> None:
    home = account_home()
    lean_pin = (ROOT / "lean/lean-toolchain").read_text().strip().split(":v")[-1]
    rust_pin = tomllib.loads((ROOT / "rust-toolchain.toml").read_text())["toolchain"]["channel"]
    result["toolchains"]["lean_pin"] = lean_pin
    result["toolchains"]["rust_pin"] = rust_pin
    result["toolchains"]["uv_lock_sha256"] = hashlib.sha256(
        (ROOT / "uv.lock").read_bytes()).hexdigest()
    lean_bin = lean_toolchain(home) / "bin"
    rust_dir = rust_toolchain(home, rust_pin, env)
    env["PATH"] = os.pathsep.join([str(lean_bin), str(rust_dir / "bin"), env["PATH"]])
    result["toolchains"]["uv"] = version(result, "uv", ["--version"], env=env,
                                         directory=scratch_of(env) / "bin")
    # Lake builds in lean/, so check the versions there too.
    for name in ("lake", "lean"):
        result["toolchains"][name] = version(result, name, ["--version"], env=env,
                                             directory=lean_bin, cwd=ROOT / "lean")
    if f"version {lean_pin}" not in result["toolchains"]["lean"]:
        raise RuntimeError(f"Lean version differs from lean/lean-toolchain ({lean_pin})")
    if f"Lean version {lean_pin}" not in result["toolchains"]["lake"]:
        raise RuntimeError(f"Lake's Lean differs from lean/lean-toolchain ({lean_pin})")
    result["toolchains"]["rust_toolchain"] = rust_dir.name
    for name in ("rustc", "cargo"):
        result["toolchains"][name] = version(result, name, ["--version"], env=env,
                                             directory=rust_dir / "bin")
    if not result["toolchains"]["rustc"].startswith(f"rustc {rust_pin} "):
        raise RuntimeError(f"rustc version differs from rust-toolchain.toml ({rust_pin})")
    if not result["toolchains"]["cargo"].startswith(f"cargo {rust_pin} "):
        raise RuntimeError(f"Cargo version differs from rust-toolchain.toml ({rust_pin})")


def uv_workspace_ancestors(root: Path) -> list[Path]:
    # UV_NO_CONFIG does not stop workspace discovery: uv joins an ancestor
    # pyproject.toml declaring [tool.uv.workspace] that lists the checkout, then
    # takes that workspace's uv.lock, .python-version and .venv instead of the
    # checkout's. An ancestor uv cannot parse is refused as well.
    found = []
    for parent in root.resolve().parents:
        pyproject = parent / "pyproject.toml"
        if not pyproject.is_file():
            continue
        try:
            tool = tomllib.loads(pyproject.read_text()).get("tool", {})
            uv = tool.get("uv", {}) if isinstance(tool, dict) else None
            declares = not isinstance(uv, dict) or "workspace" in uv
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
            declares = True
        if declares:
            found.append(pyproject)
    return found


def check_python_project(result: dict, env: dict[str, str]) -> None:
    workspaces = uv_workspace_ancestors(ROOT)
    if workspaces:
        raise RuntimeError(f"uv would use an ancestor workspace instead of {ROOT / 'uv.lock'}: "
                           f"{[str(path) for path in workspaces]}")
    command(["uv", "sync", "--locked", "--group", "dev"], env=env, stage="frozen Python lock")
    result["toolchains"]["python"] = command(
        ["uv", "run", "--frozen", "--no-sync", "python", "--version"],
        env=env, stage="Python version")
    # Every later Python stage must run in the environment synced from this lock.
    prefix = command(["uv", "run", "--frozen", "--no-sync", "python", "-c",
                      "import sys; print(sys.prefix)"], env=env, stage="Python environment")
    if prefix != str(ROOT / ".venv"):
        raise RuntimeError(f"uv selected the environment {prefix}, not {ROOT / '.venv'}")


def permitted(nodeid: str, reason: str, entries: list[dict]) -> bool:
    return any((fnmatch.fnmatchcase(nodeid, entry["nodeid"])
                if "*" in entry["nodeid"] else nodeid == entry["nodeid"])
               and entry["reason"] in reason for entry in entries)


def interpret_pytest(result: dict, events: dict, policy: dict, expected: list[str],
                     families: tuple[str, ...] | None = None, *, diff=None, base: str = "") -> None:
    """Record the suite's counts, skips and failures; `families` (default REQUIRED_FAMILIES) must be collected.
    Every `expected` ID (the merge base's collection) must be collected unless a `Test-removed:` trailer of
    `diff` (tools/gate_collection.py, `Changes`) records its removal; no trailer may be stale or malformed."""
    from tools import gate_collection
    tests = events["tests"]
    collected = events["collected"]
    selected = events["selected"]
    deselected = events["deselected"]
    result["counts"].update(collected=len(collected),
                            selected=len(selected),
                            passed=sum(row["outcome"] == "passed" for row in tests.values()),
                            skipped=sum(row["outcome"] == "skipped" for row in tests.values()),
                            failed=sum(row["outcome"] == "failed" for row in tests.values()),
                            deselected=len(deselected))
    if len(collected) != len(set(collected)) or len(selected) != len(set(selected)):
        result["failures"].append({"stage": "coverage", "reason": "duplicate test ID in collection"})
    verdict = gate_collection.missing(expected, collected, diff)
    result.setdefault("collection", {}).update(head_ids=len(collected), added=len(set(collected) - set(expected)),
                                               **verdict.record())
    if verdict.failed():
        result["failures"].append({"stage": "coverage",
                                   "reason": gate_collection.difference_text(base, verdict)})
    if set(selected) | set(deselected) != set(collected) or set(selected) & set(deselected):
        result["failures"].append({"stage": "coverage",
                                   "reason": "tests removed from final collection without a deselection report"})
    if set(tests) - set(selected):
        result["failures"].append({"stage": "coverage",
                                   "reason": "result for test outside final collection"})
    for report in events["collection_reports"]:
        result["failures"].append({"stage": "collection", **report})
    for family in REQUIRED_FAMILIES if families is None else families:
        if not any(node.startswith(f"tests/{family}::") for node in selected):
            result["failures"].append({"stage": "coverage", "reason": f"required family not collected: {family}"})
    for node in selected:
        if node not in tests:
            result["failures"].append({"stage": "pytest", "nodeid": node,
                                       "reason": "collected test has no result"})
    for node, row in tests.items():
        if row["outcome"] == "failed":
            result["failures"].append({"stage": "pytest", "nodeid": node,
                                       "reason": row["reason"]})
        elif row["outcome"] == "skipped":
            reason = row["reason"]
            allowed = permitted(node, reason, policy["optional_tests"])
            result["skips"].append({"nodeid": node, "reason": reason, "allowed": allowed})
            if not allowed:
                result["failures"].append({"stage": "skip policy", "nodeid": node,
                                           "reason": reason})
    for node in events["deselected"]:
        allowed = permitted(node, "Calls real model CLIs; excluded by the non-live gate.",
                            policy["deselected_tests"])
        result["skips"].append({"nodeid": node, "reason": "excluded live model call",
                                "allowed": allowed, "deselected": True})
        if not allowed:
            result["failures"].append({"stage": "deselection policy", "nodeid": node,
                                       "reason": "unlisted deselected test"})


def retry_quarantined(result: dict, events: dict, env: dict[str, str], python: list[str], scratch: Path, *,
                      enabled: bool, day=None) -> None:
    """Run each failed test of the active quarantine (tools/quarantine.py) once more, alone and serially. One
    that passes there no longer fails the gate, and `result["quarantine"]` keeps both outcomes; one that fails
    again, or has no result, still fails it. With `enabled` false (`--no-quarantine`, the nightly) nothing is
    retried and every failure blocks. A malformed quarantine file fails the gate (ValueError)."""
    record = result["quarantine"] = {"enabled": enabled, "active": [], "expired": [], "retried": {}}
    if not enabled:
        return
    entries = quarantine.load()
    day = day or quarantine.today()
    active = quarantine.active(entries, day)
    record.update(day=day.isoformat(), active=sorted(active), expired=quarantine.expired(entries, day))
    failed = sorted(nodeid for nodeid, row in events["tests"].items()
                    if row.get("outcome") == "failed" and nodeid in active)
    if not failed:
        return
    retry_file = scratch / "pytest-quarantine.json"
    try:
        command(retry_command(python, failed), env={**env, "VE_GATE_PYTEST_RESULT": str(retry_file)},
                stage="Quarantine retry")
    except RuntimeError:
        pass  # a retry that fails exits 1: its events say which test failed again
    try:
        retried = json.loads(retry_file.read_text())["tests"]
    except (OSError, ValueError, KeyError, TypeError):
        retried = {}
    for nodeid in failed:
        row = retried.get(nodeid) if isinstance(retried, dict) else None
        outcome = row.get("outcome", "no result") if isinstance(row, dict) else "no result"
        entry = active[nodeid]
        record["retried"][nodeid] = {"suite": "failed", "alone": outcome, "owner": entry["owner"],
                                     "expires": entry["expires"], "evidence": entry["evidence"]}
        if outcome == "passed":
            result["failures"] = [failure for failure in result["failures"]
                                  if not (failure["stage"] == "pytest" and failure.get("nodeid") == nodeid)]
            result["counts"].update(failed=result["counts"]["failed"] - 1, passed=result["counts"]["passed"] + 1)
    # The suite exited 1 for its failed tests; when each of them passed alone, that exit is theirs alone.
    if not any(failure["stage"] == "pytest" for failure in result["failures"]):
        result["failures"] = [failure for failure in result["failures"] if failure != {
            "stage": "pytest command", "reason": exit_reason("Python suite", 1)}]


def write_result(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def source_identity(env: dict[str, str]) -> tuple[str, bool]:
    # Repository config can make status trust cached filesystem state instead
    # of the worktree: an fsmonitor hook or a stale untracked cache hides edits.
    # So can the repository's index: an entry rewritten in the second of an edit
    # keeps its stat data and is no longer racy, and assume-unchanged or
    # skip-worktree bits skip the file. A change status finds there (a staged
    # one too) is dirty; a clean tree is then checked again against a fresh
    # index read from the commit, which has no stat data, so every tracked
    # file's content is compared. The repository's own index is never written.
    git = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
           "-c", "core.untrackedCache=false"]
    status = [*git, "status", "--porcelain", "--untracked-files=all"]
    sha = command([*git, "rev-parse", "HEAD"], cwd=ROOT, env=env, stage="commit")
    if command(status, cwd=ROOT, env=env, stage="worktree status"):
        return sha, True
    index = scratch_of(env) / "source-index"
    fresh = {**env, "GIT_INDEX_FILE": str(index)}
    index.unlink(missing_ok=True)
    try:
        command([*git, "read-tree", sha], cwd=ROOT, env=fresh, stage="worktree index")
        dirty = bool(command(status, cwd=ROOT, env=fresh, stage="worktree content"))
    finally:
        index.unlink(missing_ok=True)
    return sha, dirty


def tree_identity(env: dict[str, str]) -> str:
    """The tree of HEAD: the gated sources, whatever commit carries them (`--rerun-failed` matches on it)."""
    return command(["git", "--no-optional-locks", "rev-parse", "HEAD^{tree}"], cwd=ROOT, env=env, stage="tree")


def read_previous(path: Path) -> dict | None:
    """The gate record at `path`, read before this gate replaces it, or None."""
    try:
        record = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    return record if isinstance(record, dict) else None


def rerun_refusal(previous: dict | None, tree: str, toolchains: dict) -> str | None:
    """Why the failed tests of `previous` cannot be rerun alone on this gate, or None. Only a gate of this tree,
    clean, on these toolchains, whose suite ran and whose every failure is a test that failed or has no result
    (`RERUNNABLE`) can be: anything else needs the full gate."""
    if previous is None:
        return "no previous gate record"
    if previous.get("status") != "failed":
        return f"the previous gate's status is {previous.get('status')!r}, not 'failed'"
    if not tree or previous.get("tree_sha") != tree:
        return f"the previous gate ran on tree {previous.get('tree_sha')!r}, not {tree!r}"
    if previous.get("dirty") is not False:
        return "the previous gate did not run on a clean worktree"
    if not isinstance(previous.get("toolchains"), dict) or \
            toolchain_identity(previous["toolchains"]) != toolchain_identity(toolchains):
        return "the previous gate ran on other toolchains"
    if "pytest" not in previous.get("stages", []):
        return "the previous gate's suite did not complete"
    failures = previous.get("failures")
    if not isinstance(failures, list) or not failures:
        return "the previous gate records no failure"
    others = [failure for failure in failures if not isinstance(failure, dict)
              or failure.get("stage") not in RERUNNABLE
              or failure.get("stage") == "pytest" and not failed_test(failure.get("nodeid"))]
    if others:
        return f"the previous gate failed outside its tests: {others[:3]}"
    if not failed_tests(previous):
        return "the previous gate names no failed test"
    return None


def toolchain_identity(toolchains: dict) -> dict:
    """The recorded toolchains but uv's path, which is in each gate's own scratch directory."""
    paths = toolchains.get("paths", {})
    return {**toolchains, "paths": {name: path for name, path in paths.items() if name != "uv"}
            if isinstance(paths, dict) else paths}


def failed_test(nodeid) -> bool:
    return isinstance(nodeid, str) and nodeid.startswith("tests/") and "::" in nodeid


def failed_tests(previous: dict) -> list[str]:
    return sorted({failure["nodeid"] for failure in previous["failures"] if failure.get("stage") == "pytest"})


def gate_environment(scratch: Path) -> dict[str, str]:
    # Nothing is inherited from the caller: build and discovery tools read
    # overrides of their executable, compiler, linker, cache, repository,
    # import path and configuration from variables too numerous to deny.
    # Home, caches and temporary files live in the gate-owned scratch directory.
    home = scratch / "home"
    directories = {"HOME": home, "XDG_CACHE_HOME": home / ".cache",
                   "XDG_CONFIG_HOME": home / ".config", "XDG_DATA_HOME": home / ".local/share",
                   "TMPDIR": scratch / "tmp", "UV_CACHE_DIR": scratch / "uv-cache",
                   "LAKE_CACHE_DIR": scratch / "lake-cache", "CARGO_HOME": scratch / "cargo-home",
                   "PYTHONPYCACHEPREFIX": scratch / "pycache"}
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
    # Only uv is exposed from outside the toolchains and the system directories.
    tools = scratch / "bin"
    tools.mkdir(exist_ok=True)
    account = account_home()
    for location in UV_LOCATIONS:
        uv = account / location
        if uv.is_file() and os.access(uv, os.X_OK):
            (tools / "uv").symlink_to(uv.resolve())
            break
    env = {name: str(directory) for name, directory in directories.items()}
    env.update(PATH=os.pathsep.join([str(tools), *SYSTEM_PATH]), LANG="C.UTF-8",
               LC_ALL="C.UTF-8", GIT_CONFIG_NOSYSTEM="1", UV_NO_CONFIG="1",
               PYTHONNOUSERSITE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    return env


def scratch_of(env: dict[str, str]) -> Path:
    return Path(env["HOME"]).parent


def record_environment(result: dict, stage: str, env: dict[str, str]) -> dict[str, str]:
    extra = set(env) - set(ALLOWED_ENVIRONMENT) - set(STAGE_ENVIRONMENT.get(stage, ()))
    if extra:
        raise RuntimeError(f"{stage} environment has unlisted variables: {sorted(extra)}")
    result["environment"][stage] = env
    return env


def cargo_configs(workdir: Path, cargo_home: Path) -> list[Path]:
    # Cargo reads .cargo/config and .cargo/config.toml in its current directory
    # and every ancestor, including world-writable ones such as /tmp, then
    # config and config.toml in CARGO_HOME.
    directory = workdir.resolve()
    found = [path for parent in (directory, *directory.parents)
             for path in sorted((parent / ".cargo").glob("config*"))]
    return found + sorted(cargo_home.glob("config*"))


def seed_registry(cargo_home: Path) -> None:
    # Copy the local registry index and only those downloaded .crate archives
    # whose SHA-256 is pinned in Cargo.lock, so the locked build stays offline.
    # Never copy unpacked sources: Cargo trusts an existing src/ tree as is.
    registry = ROOT / ".cargo-home/registry"
    lock = tomllib.loads((ROOT / "rust/Cargo.lock").read_text())
    locked = {package["checksum"] for package in lock.get("package", []) if "checksum" in package}
    if (registry / "index").is_dir():
        shutil.copytree(registry / "index", cargo_home / "registry/index")
    for archive in sorted(registry.glob("cache/*/*.crate")):
        if hashlib.sha256(archive.read_bytes()).hexdigest() in locked:
            target = cargo_home / "registry/cache" / archive.parent.name / archive.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(archive, target)


@contextmanager
def isolated_cargo(env: dict[str, str], target_dir: Path | None = None):
    # Cargo runs in the scratch directory, outside the checkout and any home,
    # with the fresh CARGO_HOME from gate_environment. Its paths are remapped,
    # so the build is byte-identical to a checkout build pinned in checkers.lock.
    workdir = scratch_of(env) / "cargo"
    workdir.mkdir()
    cargo_home = Path(env["CARGO_HOME"])
    configs = cargo_configs(workdir, cargo_home)
    if configs:
        raise RuntimeError(f"Cargo would read ambient configuration: {[str(p) for p in configs]}")
    seed_registry(cargo_home)
    flags = rust_build.encoded_rustflags(root=ROOT, cargo_home=cargo_home,
                                         target_dir=target_dir or ROOT / "rust/target")
    yield {**env, "CARGO_NET_OFFLINE": "true", "CARGO_ENCODED_RUSTFLAGS": flags}, workdir


def base_collection(result: dict, base: str | None, env: dict[str, str], pytest_env: dict[str, str],
                    scratch: Path):
    """(the merge base's collection, base..HEAD's changes and removal records): the base's record, or the base
    collected in a scratch worktree with this gate's Lean build, toolchains and Python environment and
    recorded for the next gate on that base (tools/gate_collection.py)."""
    from tools import gate_collection
    base = (gate_collection.rev(f"{base}^{{commit}}", env=env) if base
            else gate_collection.merge_base(env=env))
    found = gate_collection.recorded(base, env=env)
    collection = result["collection"] = {"base": base}
    if found is not None:
        collection["base_source"], ids = f"record of {found[0]}", found[1]
    else:
        started = time.monotonic()
        # Its own sources first on the import path (PYTHONPATH, set by `collect`), not the checkout's.
        ids = gate_collection.collect_commit(base, scratch, build_env=env, env=pytest_env,
                                             python=[str(ROOT / ".venv/bin/python")])
        collection.update(base_source="collected", base_seconds=round(time.monotonic() - started, 1))
        collection["base_record"] = record_collection(base, ids, env)
    collection["base_ids"] = len(ids)
    return ids, gate_collection.changes(base, "HEAD", env=env)


def record_collection(commit: str, ids: list[str], env: dict[str, str], result: dict | None = None) -> str:
    """Attach the gate result and its IDs to `commit`; a record is a later gate's shortcut, so a failure to
    write it is reported, not a gate failure."""
    from tools import gate_collection
    try:
        gate_collection.write_record(commit, ids, result=result, env=env)
    except RuntimeError as exc:
        return f"not written: {exc}"
    return "written"


def gate_scratch_root() -> Path:
    """Allow a durable scratch root when system /tmp is cleaned during a long gate."""
    return Path(os.environ.get("VE_GATE_SCRATCH_ROOT", "/tmp")).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "gate-result.json")
    parser.add_argument("--workers", default="auto",
                        help="xdist workers for the suite (default auto: the CPUs the load leaves, "
                             "tests/conftest.py)")
    parser.add_argument("--base", help="the commit whose collection the head's is checked against (default: the "
                                           "merge base with main, or on main the first parent)")
    parser.add_argument("--rerun-failed", nargs="?", const="", type=str, metavar="RECORD",
                        help="when the gate RECORD (default: --output) failed only on tests, on this tree and these "
                             "toolchains, rerun only the files of its failed tests (status rerun-passed or failed); "
                             "otherwise run the full gate. A rerun is never a full gate's evidence (status passed)")
    parser.add_argument("--no-quarantine", action="store_true",
                        help="the nightly: no quarantined test (tools/test-quarantine.json) is retried alone, so "
                             "every failure blocks")
    args = parser.parse_args()
    if not (args.workers == "auto" or args.workers.isdecimal() and int(args.workers) > 0):
        parser.error("--workers is a positive count or auto")
    output = args.output.resolve()
    # Read before the record is reset: it is the failed gate a rerun repeats.
    previous = None if args.rerun_failed is None else read_previous(
        Path(args.rerun_failed).resolve() if args.rerun_failed else output)
    result = {"schema_version": 1, "commit_sha": "", "tree_sha": "", "dirty": False, "mode": "full",
              "toolchains": {}, "environment": {}, "stages": [], "counts": {}, "skips": [],
              "failures": [], "status": "failed"}
    rerun = None  # the failed tests' files, when this gate reruns them alone
    head_ids = None  # the head's full collection, recorded for its commit at the end
    # A killed process must never leave the previous run's passing record intact.
    write_result(output, result)
    started_clean = False
    completed = False
    with tempfile.TemporaryDirectory(prefix="ve-gate-", dir=gate_scratch_root()) as directory:
        scratch = Path(directory)
        try:
            env = record_environment(result, "base", gate_environment(scratch))
            result["commit_sha"], result["dirty"] = source_identity(env)
            if result["dirty"]:
                raise RuntimeError("worktree is dirty at gate start")
            started_clean = True
            result["tree_sha"] = tree_identity(env)
            policy = json.loads(POLICY.read_text())
            if policy["version"] != 1:
                raise RuntimeError("unsupported optional-test policy version")
            check_toolchains(result, env)
            check_python_project(result, env)
            if args.rerun_failed is not None:
                refusal = rerun_refusal(previous, result["tree_sha"], result["toolchains"])
                if refusal is None:
                    tests = failed_tests(previous)
                    rerun = sorted({nodeid.split("::", 1)[0] for nodeid in tests})
                    result["mode"] = "rerun-failed"
                    result["rerun_failed"] = {
                        "previous": {key: previous.get(key) for key in ("commit_sha", "tree_sha", "mode", "status")},
                        "tests": tests, "files": rerun, "reused_stages": list(REUSED_STAGES)}
                else:
                    result["rerun_failed"] = {"refused": refusal}
                    print(f"[gate] --rerun-failed: {refusal}; running the full gate", flush=True)
            result["stages"].append("toolchains")

            # Lake trusts an executable's trace; a trace that does not record the binary beside it (copied from
            # another checkout) would keep a stale binary. Drop such traces, and fail if the build leaves one.
            lake_outputs.drop_stale(ROOT / "lean", env=env)
            command(["lake", "build"], cwd=ROOT / "lean", env=env, stage="Lean build")
            if stale := lake_outputs.stale(ROOT / "lean", env=env):
                raise RuntimeError(f"Lean build left executables its traces do not record: {stale}")
            for name in LEAN_BINARIES:
                binary = ROOT / "lean/.lake/build/bin" / name
                if not binary.is_file() or not os.access(binary, os.X_OK):
                    raise RuntimeError(f"Lean build did not produce {binary}")
            result["stages"].append("lean_build")
            # The examples are admitted by this commit's ve_service, so the check follows the build: before it, a
            # binary left by an earlier build would answer with another commit's modes.
            command(["uv", "run", "--frozen", "--no-sync", "python",
                     "tools/wire_contract.py", "--check"], env=env,
                    stage="Wire contract check")

            if rerun is None:
                command(["uv", "run", "--frozen", "--no-sync", "python", "lean/audit.py"],
                        env=env, stage="Lean audit")
                result["stages"].append("lean_audit")

            # The host build at rust/target/release/ve: the executable the Rust
            # backend loads and checkers.lock pins. An explicit --target would
            # change crate metadata and so the hash.
            target_dir = ROOT / "rust/target"
            cargo_options = ["--target-dir", str(target_dir)]

            with isolated_cargo(env, target_dir) as (cargo_env, cargo_cwd):
                record_environment(result, "cargo", cargo_env)
                command(["cargo", "build", *cargo_options, "--locked", "--release", "--manifest-path",
                         str(ROOT / "rust/Cargo.toml")], cwd=cargo_cwd, env=cargo_env,
                        stage="Rust build")
                rust_binary = target_dir / "release/ve"
                if not rust_binary.is_file() or not os.access(rust_binary, os.X_OK):
                    raise RuntimeError(f"Rust build did not produce {rust_binary}")
                if rust_build.digest(rust_binary) not in rust_build.pinned_digests(
                        ROOT / "lean/checkers.lock"):
                    raise RuntimeError(f"Rust build {rust_binary} is not pinned in lean/checkers.lock")
                result["stages"].append("rust_build")

                if rerun is None:
                    rust_tests = command(["cargo", "test", *cargo_options, "--locked", "--release", "--workspace",
                                          "--manifest-path", str(ROOT / "rust/Cargo.toml")],
                                         cwd=cargo_cwd, env=cargo_env, stage="native Rust tests")
                    summaries = re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; "
                                           r"(\d+) ignored;", rust_tests)
                    if not summaries:
                        raise RuntimeError("cargo test produced no parseable test result")
                    result["counts"]["rust_passed"] = sum(int(row[0]) for row in summaries)
                    result["counts"]["rust_ignored"] = sum(int(row[2]) for row in summaries)
                    if result["counts"]["rust_passed"] == 0 or result["counts"]["rust_ignored"]:
                        raise RuntimeError("native Rust tests absent or ignored")
                    result["stages"].append("cargo_test")

            python = ["uv", "run", "--frozen", "--no-sync", "python"]
            collection_file, events_file = scratch / "pytest-collection.json", scratch / "pytest.json"
            pytest_env = record_environment(result, "pytest", nested_pytest.environment(
                env, VE_GATE_PYTEST_RESULT=str(collection_file),
                VE_GATE_PYTEST_PROGRESS=str(scratch / "current-test.txt"),
                VE_NATIVE_PREBUILT="1", VE_LEAN_PREBUILT="1", VE_RUST_PREBUILT="1",
                VE_RUST_BINARY=str(rust_binary)))
            # The collection, serially (xdist workers report no deselection), then the
            # suite on `--workers` xdist workers; a worker must collect that selection.
            collection = collect(pytest_env, collection_file, python=python, files=rerun)
            if rerun is None and not collection["collection_reports"] and \
                    len(collection["collected"]) == len(set(collection["collected"])):
                head_ids = collection["collected"]
            expected, diff = base_collection(result, args.base, env, pytest_env, scratch)
            try:
                command(suite_command(python, args.workers, rerun),
                        env={**pytest_env, "VE_GATE_PYTEST_RESULT": str(events_file)}, stage="Python suite")
            except RuntimeError as exc:
                result["failures"].append({"stage": "pytest command", "reason": str(exc)})
            if not events_file.exists():
                raise RuntimeError("pytest did not write its result events")
            events = merge_pytest_events(collection, json.loads(events_file.read_text()))
            base = result["collection"]["base"]
            if rerun is None:
                interpret_pytest(result, events, policy, expected, diff=diff, base=base)
            else:
                # The base's tests of the rerun files, each of the failed tests among them.
                interpret_pytest(result, events, policy,
                                 [nodeid for nodeid in expected if nodeid.split("::", 1)[0] in rerun], families=(),
                                 diff=diff, base=base)
                outcomes = {nodeid: events["tests"].get(nodeid, {}).get("outcome", "no result")
                            for nodeid in result["rerun_failed"]["tests"]}
                result["rerun_failed"]["outcomes"] = outcomes
            retry_quarantined(result, events, pytest_env, python, scratch, enabled=not args.no_quarantine)
            result["stages"].append("pytest")
            completed = True
        except (OSError, ValueError, KeyError, RuntimeError) as exc:
            result["failures"].append({"stage": "gate", "reason": str(exc)})
        finally:
            if started_clean:
                try:
                    ending_sha, ending_dirty = source_identity(env)
                    result["dirty"] = ending_dirty
                    if ending_sha != result["commit_sha"] or ending_dirty:
                        result["failures"].append({"stage": "source identity",
                                                   "reason": "HEAD or worktree changed during gate"})
                except (OSError, RuntimeError) as exc:
                    result["failures"].append({"stage": "source identity", "reason": str(exc)})
            # Store the complete clean collection in the gate result, including
            # the result's git note, without making every evidence copy 1.8 MB.
            record_head = head_ids is not None and not any(failure["stage"] == "source identity"
                                                         for failure in result["failures"])
            if record_head:
                from tools import gate_collection
                result.setdefault("collection", {})["collected_zlib"] = gate_collection.encode_ids(head_ids)
            if completed and result["stages"] == list(REQUIRED_STAGES) and not result["failures"]:
                result["status"] = "passed"
            # A rerun of failed tests is never a full gate: its own status, which no evidence check accepts.
            elif completed and rerun is not None and not result["failures"] and result["stages"] == [
                    stage for stage in REQUIRED_STAGES if stage not in REUSED_STAGES]:
                result["status"] = "rerun-passed"
            if record_head:
                result["collection"]["head_record"] = "written"
                result["collection"]["head_record"] = record_collection(
                    result["commit_sha"], head_ids, env, result=result)
            write_result(output, result)
            print(f"[gate] {result['status']}: {output}; "
                  f"{result['counts'].get('passed', 0)} passed, "
                  f"{result['counts'].get('skipped', 0)} skipped, "
                  f"{len(result['failures'])} failures", flush=True)
            for skip in result["skips"]:
                print(f"[gate] skip {'allowed' if skip['allowed'] else 'FAILED'}: "
                      f"{skip['nodeid']}: {skip['reason']}", flush=True)
            for nodeid, retry in result.get("quarantine", {}).get("retried", {}).items():
                print(f"[gate] quarantined: {nodeid} failed in the suite and {retry['alone']} alone "
                      f"(owner {retry['owner']}, expires {retry['expires']})", flush=True)
            for failure in result["failures"]:
                print(f"[gate] FAILURE: {failure['stage']}: "
                      f"{failure.get('nodeid', '')} {failure['reason']}", file=sys.stderr, flush=True)
            if result["status"] == "rerun-passed":
                print("[gate] the failed tests passed on rerun; this is not a full gate: run the full gate "
                      "for the final evidence", flush=True)
    return 0 if result["status"] in ("passed", "rerun-passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
