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
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import rust_build  # noqa: E402
POLICY = ROOT / "tools/gate-optional.json"
COLLECTION = ROOT / "tools/gate-collection.json"
LEAN_BINARIES = ("ve_conformance", "ve_service")
# The suite as the gate runs it; tools/gate_collection.py collects with the same arguments.
PYTEST_ARGS = ("-q", "-p", "hypothesis.extra.pytestplugin", "-p", "tools.gate_pytest",
               "-o", "addopts=-ra", "-m", "not live", "tests")
# The documented refresh of COLLECTION after intended test changes.
REFRESH = "uv run python tools/gate_collection.py --write"
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
    "pytest": ("VE_GATE_PYTEST_RESULT", "VE_GATE_PYTEST_PROGRESS", "VE_NATIVE_PREBUILT", "VE_LEAN_PREBUILT",
               "VE_RUST_PREBUILT", "VE_RUST_BINARY"),
}


def command(args: list[str], *, cwd: Path = ROOT, env: dict[str, str], stage: str) -> str:
    print(f"[gate] {stage}: {' '.join(args)}", flush=True)
    try:
        done = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
    except OSError as exc:
        raise RuntimeError(f"{stage}: {exc}") from exc
    print(done.stdout, end="" if done.stdout.endswith("\n") else "\n", flush=True)
    if done.returncode:
        raise RuntimeError(f"{stage}: exit {done.returncode}")
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


def collection_difference(added: list[str], removed: list[str]) -> str:
    """Every ID collected but not pinned and pinned but not collected, and the refresh."""
    lines = [f"The pinned baseline {COLLECTION.relative_to(ROOT)} differs from the collected tests: "
             f"{len(added)} collected but not pinned, {len(removed)} pinned but not collected."]
    for title, ids in (("Collected but not pinned", added), ("Pinned but not collected", removed)):
        if ids:
            lines.append(f"{title}:")
            lines.extend(f"  {nodeid}" for nodeid in ids)
    lines.append(f"If these test changes are intended, run `{REFRESH}` after `(cd lean && lake build)`, check "
                 "every removed ID is meant to go, and commit the file with the change.")
    return "\n".join(lines)


def interpret_pytest(result: dict, events: dict, policy: dict, expected: list[str]) -> None:
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
    missing = sorted(set(expected) - set(collected))
    unexpected = sorted(set(collected) - set(expected))
    if missing or unexpected:
        result["failures"].append({"stage": "coverage",
                                   "reason": collection_difference(unexpected, missing)})
    if set(selected) | set(deselected) != set(collected) or set(selected) & set(deselected):
        result["failures"].append({"stage": "coverage",
                                   "reason": "tests removed from final collection without a deselection report"})
    if set(tests) - set(selected):
        result["failures"].append({"stage": "coverage",
                                   "reason": "result for test outside final collection"})
    for report in events["collection_reports"]:
        result["failures"].append({"stage": "collection", **report})
    for family in REQUIRED_FAMILIES:
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


def write_result(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def source_identity(env: dict[str, str]) -> tuple[str, bool]:
    # Repository config can make status trust cached filesystem state instead
    # of the worktree: an fsmonitor hook or a stale untracked cache hides edits.
    git = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
           "-c", "core.untrackedCache=false"]
    sha = command([*git, "rev-parse", "HEAD"], cwd=ROOT, env=env, stage="commit")
    dirty = bool(command([*git, "status", "--porcelain", "--untracked-files=all"], cwd=ROOT,
                         env=env, stage="worktree status"))
    return sha, dirty


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "gate-result.json")
    args = parser.parse_args()
    output = args.output.resolve()
    result = {"schema_version": 1, "commit_sha": "", "dirty": False,
              "toolchains": {}, "environment": {}, "stages": [], "counts": {}, "skips": [],
              "failures": [], "status": "failed"}
    # A killed process must never leave the previous run's passing record intact.
    write_result(output, result)
    started_clean = False
    completed = False
    with tempfile.TemporaryDirectory(prefix="ve-gate-", dir="/tmp") as directory:
        scratch = Path(directory)
        try:
            env = record_environment(result, "base", gate_environment(scratch))
            result["commit_sha"], result["dirty"] = source_identity(env)
            if result["dirty"]:
                raise RuntimeError("worktree is dirty at gate start")
            started_clean = True
            policy = json.loads(POLICY.read_text())
            if policy["version"] != 1:
                raise RuntimeError("unsupported optional-test policy version")
            expected = json.loads(COLLECTION.read_text())
            if not isinstance(expected, list) or not expected or not all(isinstance(x, str) for x in expected):
                raise RuntimeError("invalid test collection baseline")
            check_toolchains(result, env)
            check_python_project(result, env)
            command(["uv", "run", "--frozen", "--no-sync", "python",
                     "tools/wire_contract.py", "--check"], env=env,
                    stage="Wire contract check")
            result["stages"].append("toolchains")

            command(["lake", "build"], cwd=ROOT / "lean", env=env, stage="Lean build")
            for name in LEAN_BINARIES:
                binary = ROOT / "lean/.lake/build/bin" / name
                if not binary.is_file() or not os.access(binary, os.X_OK):
                    raise RuntimeError(f"Lean build did not produce {binary}")
            result["stages"].append("lean_build")

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

            events_file = scratch / "pytest.json"
            pytest_env = record_environment(result, "pytest", {
                **env, "VE_GATE_PYTEST_RESULT": str(events_file),
                "VE_GATE_PYTEST_PROGRESS": str(scratch / "current-test.txt"),
                "VE_NATIVE_PREBUILT": "1", "VE_LEAN_PREBUILT": "1", "VE_RUST_PREBUILT": "1",
                "VE_RUST_BINARY": str(rust_binary)})
            try:
                command(["uv", "run", "--frozen", "--no-sync", "python", "-m", "pytest",
                         *PYTEST_ARGS], env=pytest_env, stage="Python suite")
            except RuntimeError as exc:
                result["failures"].append({"stage": "pytest command", "reason": str(exc)})
            if not events_file.exists():
                raise RuntimeError("pytest did not write its result events")
            interpret_pytest(result, json.loads(events_file.read_text()), policy, expected)
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
            if completed and result["stages"] == list(REQUIRED_STAGES) and not result["failures"]:
                result["status"] = "passed"
            write_result(output, result)
            print(f"[gate] {result['status']}: {output}; "
                  f"{result['counts'].get('passed', 0)} passed, "
                  f"{result['counts'].get('skipped', 0)} skipped, "
                  f"{len(result['failures'])} failures", flush=True)
            for skip in result["skips"]:
                print(f"[gate] skip {'allowed' if skip['allowed'] else 'FAILED'}: "
                      f"{skip['nodeid']}: {skip['reason']}", flush=True)
            for failure in result["failures"]:
                print(f"[gate] FAILURE: {failure['stage']}: "
                      f"{failure.get('nodeid', '')} {failure['reason']}", file=sys.stderr, flush=True)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
