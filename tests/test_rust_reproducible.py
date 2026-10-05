"""The Rust checker build is path-independent, so lean/checkers.lock pins it in every checkout.

Regression: a merge pinned a binary built in one worktree, and every other
worktree's clean build failed the hash check, because Rust embedded the
absolute ``CARGO_HOME/registry/src`` paths of dependency crates.
"""
from __future__ import annotations

import os
from pathlib import Path
import pwd
import re
import shutil
import subprocess
import tomllib

import pytest

from subprocesses import HANG_TIMEOUT
from tools import gate, rust_build

ROOT = Path(__file__).resolve().parents[1]
BINARY = (Path(os.environ["VE_RUST_BINARY"]) if os.environ.get("VE_RUST_PREBUILT")
          else rust_build.RELEASE_BINARY)


def built_binary() -> Path:
    assert BINARY.is_file(), f"Rust release build missing: {BINARY}"
    return BINARY


def test_release_binary_embeds_no_machine_path():
    data = built_binary().read_bytes()
    paths = {ROOT, ROOT.resolve(), rust_build.CARGO_HOME, Path(pwd.getpwuid(os.getuid()).pw_dir)}
    if "CARGO_HOME" in os.environ:
        paths.add(Path(os.environ["CARGO_HOME"]))
    for path in paths:
        assert str(path).encode() not in data, f"{BINARY} embeds {path}"
    assert b"/cargo-home/registry/src/" in data


def test_release_binary_is_pinned():
    digest = rust_build.digest(built_binary())
    assert digest in rust_build.pinned_digests(), (
        f"{BINARY} ({digest}) is not in lean/checkers.lock; after a Rust change, "
        "run python3 tools/rust_build.py and pin the printed hash")


def test_remap_flags_name_every_embedded_prefix(tmp_path):
    root = tmp_path / "check out"
    flags = rust_build.remap_flags(root=root, cargo_home=root / ".cargo-home",
                                   target_dir=root / "rust/target")
    assert flags == [f"--remap-path-prefix={root}=/ve",
                     f"--remap-path-prefix={root}/.cargo-home=/cargo-home",
                     f"--remap-path-prefix={root}/rust/target=/ve-target"]
    # A space stays inside one flag: the encoding separates flags by 0x1f only.
    encoded = rust_build.encoded_rustflags(root=root, cargo_home=root / ".cargo-home",
                                           target_dir=root / "rust/target")
    assert encoded.split("\x1f") == flags
    env = rust_build.cargo_env({"RUSTFLAGS": "--remap-path-prefix=/x=/y"})
    assert env["CARGO_HOME"] == str(rust_build.CARGO_HOME)
    assert env["CARGO_TARGET_DIR"] == str(rust_build.TARGET_DIR)
    assert env["CARGO_ENCODED_RUSTFLAGS"] == rust_build.encoded_rustflags(
        root=ROOT, cargo_home=rust_build.CARGO_HOME, target_dir=rust_build.TARGET_DIR)


def test_remap_flags_map_symlinked_paths_both_ways(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    flags = rust_build.remap_flags(root=link, cargo_home=link / "c", target_dir=link / "t")
    assert f"--remap-path-prefix={link}=/ve" in flags
    assert f"--remap-path-prefix={real}=/ve" in flags


BUILD_CALL = re.compile(r"""["']cargo["']\s*,\s*["'](build|test)["']|\bcargo\s*,\s*["'](build|test)["']""")


def test_every_cargo_entry_point_uses_the_reproducible_flags():
    # A build without the flags overwrites rust/target/release/ve with an
    # unpinned binary, or rebuilds everything with other flags.
    sources = [*ROOT.glob("tests/*.py"), *ROOT.glob("tools/*.py"), *ROOT.glob("rust/*.py"),
               *ROOT.glob("usecases/**/*.py"), *ROOT.glob("conformance/**/*.py")]
    offenders = [str(path.relative_to(ROOT)) for path in sources
                 if BUILD_CALL.search(path.read_text()) and "rust_build" not in path.read_text()
                 and path.name not in ("test_gate_integrity.py", "test_rust_reproducible.py")]
    assert offenders == []


def test_a_copy_of_the_workspace_elsewhere_builds_the_same_binary(tmp_path):
    # Another checkout path, another CARGO_HOME (with a space) and another
    # target directory give the pinned bytes.
    cargo = shutil.which("cargo")
    assert cargo is not None, "cargo is required for the complete test suite"
    other = tmp_path / "other checkout"
    (other / "rust").mkdir(parents=True)
    shutil.copyfile(ROOT / "rust-toolchain.toml", other / "rust-toolchain.toml")
    for name in ("Cargo.toml", "Cargo.lock"):
        shutil.copyfile(ROOT / "rust" / name, other / "rust" / name)
    workspace = tomllib.loads((ROOT / "rust/Cargo.toml").read_text())["workspace"]
    for crate in workspace["members"]:
        shutil.copytree(ROOT / "rust" / crate, other / "rust" / crate,
                        ignore=shutil.ignore_patterns("target"))
    cargo_home = tmp_path / "cargo home"
    cargo_home.mkdir()
    gate.seed_registry(cargo_home)
    target_dir = tmp_path / "target"
    env = {**os.environ, "CARGO_HOME": str(cargo_home), "CARGO_TARGET_DIR": str(target_dir),
           "CARGO_NET_OFFLINE": "true",
           "CARGO_ENCODED_RUSTFLAGS": rust_build.encoded_rustflags(
               root=other, cargo_home=cargo_home, target_dir=target_dir)}
    built = subprocess.run([cargo, "build", "-j", "2", "--locked", "--release", "--manifest-path",
                            str(other / "rust/Cargo.toml")], cwd=other, env=env,
                           capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert built.returncode == 0, built.stdout + built.stderr
    assert rust_build.digest(target_dir / "release/ve") == rust_build.digest(built_binary())


@pytest.mark.parametrize("args", [[], ["--check"]])
def test_build_entry_point_reports_the_pin(args, monkeypatch, capsys, tmp_path):
    lock = tmp_path / "checkers.lock"
    binary = tmp_path / "ve"
    binary.write_bytes(b"build")
    lock.write_text('{"rust_jsonl": ["%s"]}' % rust_build.digest(tmp_path / "ve")[::-1])
    calls = []
    monkeypatch.setattr(rust_build, "LOCK", lock)
    monkeypatch.setattr(rust_build, "RELEASE_BINARY", binary)
    monkeypatch.setattr(rust_build.shutil, "which", lambda name: "/bin/cargo")
    monkeypatch.setattr(rust_build.subprocess, "run",
                        lambda argv, **kw: calls.append((argv, kw)) or subprocess.CompletedProcess(argv, 0))
    monkeypatch.setattr("sys.argv", ["rust_build.py", *args])
    assert rust_build.main() == (1 if args else 0)
    assert "NOT pinned" in capsys.readouterr().out
    [(argv, kw)] = calls
    assert argv == ["/bin/cargo", *rust_build.DEFAULT_BUILD]
    assert "CARGO_ENCODED_RUSTFLAGS" in kw["env"]
