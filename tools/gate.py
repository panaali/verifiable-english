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
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "tools/gate-optional.json"
COLLECTION = ROOT / "tools/gate-collection.json"
LEAN_BINARIES = ("ve_conformance", "ve_norms_route")
REQUIRED_STAGES = ("toolchains", "lean_build", "lean_audit", "rust_build",
                   "cargo_test", "pytest")
REQUIRED_FAMILIES = (
    "test_conformance.py", "test_lean_conformance.py", "test_rust_conformance.py",
    "test_p0_three_way.py", "test_norms_three_way.py", "test_nary_differential.py",
    "test_data_three_way.py", "test_definitions_differential.py",
    "test_lean_certificates.py", "test_closure_certificates.py",
    "test_grammar_backends.py",
)


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


def version(executable: str, args: list[str], *, env: dict[str, str]) -> str:
    path = shutil.which(executable, path=env["PATH"])
    if path is None:
        raise RuntimeError(f"required backend missing: {executable}")
    return command([path, *args], env=env, stage=f"{executable} version").splitlines()[0]


def check_toolchains(result: dict, env: dict[str, str]) -> None:
    lean_pin = (ROOT / "lean/lean-toolchain").read_text().strip().split(":v")[-1]
    rust_pin = tomllib.loads((ROOT / "rust-toolchain.toml").read_text())["toolchain"]["channel"]
    result["toolchains"]["lean_pin"] = lean_pin
    result["toolchains"]["rust_pin"] = rust_pin
    result["toolchains"]["uv_lock_sha256"] = hashlib.sha256(
        (ROOT / "uv.lock").read_bytes()).hexdigest()
    result["toolchains"]["uv"] = version("uv", ["--version"], env=env)
    result["toolchains"]["lake"] = version("lake", ["--version"], env=env)
    result["toolchains"]["lean"] = version("lean", ["--version"], env=env)
    if f"version {lean_pin}" not in result["toolchains"]["lean"]:
        raise RuntimeError(f"Lean version differs from lean/lean-toolchain ({lean_pin})")
    # A stable toolchain can satisfy the exact pin without downloading another
    # copy. Never let rustup silently install or switch versions during a gate.
    for candidate in (rust_pin, "stable"):
        probe = subprocess.run(["rustup", "run", candidate, "rustc", "--version"],
                               env=env, text=True, capture_output=True)
        if probe.returncode == 0 and probe.stdout.startswith(f"rustc {rust_pin} "):
            env["RUSTUP_TOOLCHAIN"] = candidate
            break
    else:
        raise RuntimeError(f"required Rust toolchain {rust_pin} is not installed")
    result["toolchains"]["rust_toolchain"] = env["RUSTUP_TOOLCHAIN"]
    result["toolchains"]["rustc"] = version("rustc", ["--version"], env=env)
    result["toolchains"]["cargo"] = version("cargo", ["--version"], env=env)
    if not result["toolchains"]["cargo"].startswith(f"cargo {rust_pin} "):
        raise RuntimeError(f"Cargo version differs from rust-toolchain.toml ({rust_pin})")


def permitted(nodeid: str, reason: str, entries: list[dict]) -> bool:
    return any((fnmatch.fnmatchcase(nodeid, entry["nodeid"])
                if "*" in entry["nodeid"] else nodeid == entry["nodeid"])
               and entry["reason"] in reason for entry in entries)


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
                                   "reason": f"collection differs from baseline: {len(missing)} missing, "
                                             f"{len(unexpected)} unexpected; missing={missing[:10]}, "
                                             f"unexpected={unexpected[:10]}"})
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
    sha = command(["git", "rev-parse", "HEAD"], env=env, stage="commit")
    dirty = bool(command(["git", "status", "--porcelain", "--untracked-files=all"],
                         env=env, stage="worktree status"))
    return sha, dirty


def gate_environment() -> dict[str, str]:
    # Build and discovery tools must not inherit ambient overrides of their
    # executable, repository, import path, or configuration.
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("PYTEST_", "CARGO_", "PYTHON", "RUST", "GIT_",
                                  "UV_", "VE_"))}
    env["PATH"] = str(Path.home() / ".elan/bin") + os.pathsep + os.environ["PATH"]
    env["UV_CACHE_DIR"] = str(ROOT / ".cache/uv")
    env["CARGO_HOME"] = str(ROOT / ".cargo-home")
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return env


@contextmanager
def isolated_cargo(env: dict[str, str]):
    # Cargo discovers config from its current directory's ancestors and from
    # CARGO_HOME. Keep both outside the checkout and the user's home. Copy the
    # existing registry cache so the locked build remains offline.
    with tempfile.TemporaryDirectory(prefix="ve-gate-cargo-", dir="/tmp") as directory:
        workdir = Path(directory)
        cargo_home = workdir / "cargo-home"
        cargo_home.mkdir()
        registry = ROOT / ".cargo-home/registry"
        if registry.is_dir():
            shutil.copytree(registry, cargo_home / "registry")
        cargo_env = {**env, "CARGO_HOME": str(cargo_home), "CARGO_NET_OFFLINE": "true"}
        yield cargo_env, workdir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "gate-result.json")
    args = parser.parse_args()
    output = args.output.resolve()
    env = gate_environment()
    result = {"schema_version": 1, "commit_sha": "", "dirty": False,
              "toolchains": {}, "stages": [], "counts": {}, "skips": [], "failures": [],
              "status": "failed"}
    # A killed process must never leave the previous run's passing record intact.
    write_result(output, result)
    started_clean = False
    completed = False
    try:
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
        command(["uv", "sync", "--locked", "--group", "dev"], env=env, stage="frozen Python lock")
        result["toolchains"]["python"] = command(
            ["uv", "run", "--frozen", "--no-sync", "python", "--version"],
            env=env, stage="Python version")
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

        host = command(["rustc", "-vV"], env=env, stage="Rust host")
        match = re.search(r"^host: (\S+)$", host, re.MULTILINE)
        if not match:
            raise RuntimeError("rustc did not report a host target")
        target = match.group(1)
        target_dir = ROOT / "rust/target"
        cargo_options = ["--target-dir", str(target_dir), "--target", target]

        with isolated_cargo(env) as (cargo_env, cargo_cwd):
            command(["cargo", "build", *cargo_options, "--locked", "--release", "--manifest-path",
                     str(ROOT / "rust/Cargo.toml")], cwd=cargo_cwd, env=cargo_env,
                    stage="Rust build")
            rust_binary = target_dir / target / "release/ve"
            if not rust_binary.is_file() or not os.access(rust_binary, os.X_OK):
                raise RuntimeError(f"Rust build did not produce {rust_binary}")
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

        with tempfile.TemporaryDirectory(prefix="ve-gate-") as directory:
            events_file = Path(directory) / "pytest.json"
            env["VE_GATE_PYTEST_RESULT"] = str(events_file)
            env["VE_GATE_PYTEST_PROGRESS"] = str(Path(directory) / "current-test.txt")
            env["VE_LEAN_PREBUILT"] = "1"
            env["VE_RUST_PREBUILT"] = "1"
            env["VE_RUST_BINARY"] = str(rust_binary)
            try:
                command(["uv", "run", "--frozen", "--no-sync", "python", "-m", "pytest",
                         "-q", "-p", "hypothesis.extra.pytestplugin",
                         "-p", "tools.gate_pytest", "-o", "addopts=-ra",
                         "-m", "not live", "tests"], env=env, stage="Python suite")
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
