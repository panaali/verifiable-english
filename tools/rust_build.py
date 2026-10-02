#!/usr/bin/env python3
"""Reproducible Rust checker builds: the same source gives the same binary in any checkout.

``lean/checkers.lock`` pins the SHA-256 of ``rust/target/release/ve``. Rust
embeds source paths in the binary (panic locations): Cargo passes workspace
paths relative to the workspace, but dependency sources live under
``CARGO_HOME``, whose absolute path differs between checkouts. Every Cargo
invocation therefore maps the checkout, ``CARGO_HOME`` and the target directory
to fixed names with ``--remap-path-prefix``; the flags' own absolute paths do
not reach the binary (``tests/test_rust_reproducible.py`` builds a second copy
of the workspace elsewhere and compares hashes).

Run ``python3 tools/rust_build.py`` from any directory to build the release
binary and report whether its hash is pinned; ``--check`` fails if it is not.
Other Cargo arguments run Cargo with the same environment, for example
``python3 tools/rust_build.py test --locked --manifest-path rust/Cargo.toml``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "lean/checkers.lock"
CARGO_HOME = ROOT / ".cargo-home"
TARGET_DIR = ROOT / "rust/target"
RELEASE_BINARY = TARGET_DIR / "release/ve"
MANIFEST = ROOT / "rust/Cargo.toml"
DEFAULT_BUILD = ("build", "-j", "2", "--locked", "--release", "--manifest-path", str(MANIFEST))


def remap_flags(*, root: Path, cargo_home: Path, target_dir: Path) -> list[str]:
    """``--remap-path-prefix`` flags for every path a build can embed.

    rustc applies the last matching mapping, so longer prefixes come later:
    a ``CARGO_HOME`` or target directory inside the checkout keeps its own name.
    """
    names = {}
    for path, name in ((root, "/ve"), (cargo_home, "/cargo-home"), (target_dir, "/ve-target")):
        for form in (Path(path).absolute(), Path(path).resolve()):
            names[str(form)] = name
    for path in names:
        if "\x1f" in path:
            raise ValueError(f"path cannot be remapped: {path!r}")
    return [f"--remap-path-prefix={path}={names[path]}" for path in sorted(names, key=len)]


def encoded_rustflags(*, root: Path, cargo_home: Path, target_dir: Path) -> str:
    """``CARGO_ENCODED_RUSTFLAGS``: it takes precedence over ``RUSTFLAGS`` and
    every configured ``rustflags``, and keeps paths with spaces intact."""
    return "\x1f".join(remap_flags(root=root, cargo_home=cargo_home, target_dir=target_dir))


def cargo_env(base=None) -> dict[str, str]:
    """The environment of every Cargo build of this checkout."""
    return {**(os.environ if base is None else base),
            "CARGO_HOME": str(CARGO_HOME), "CARGO_TARGET_DIR": str(TARGET_DIR),
            "CARGO_ENCODED_RUSTFLAGS": encoded_rustflags(root=ROOT, cargo_home=CARGO_HOME,
                                                         target_dir=TARGET_DIR)}


def pinned_digests(lock: Path | None = None) -> list[str]:
    return json.loads((lock or LOCK).read_text())["rust_jsonl"]


def digest(binary: Path) -> str:
    return hashlib.sha256(Path(binary).read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="fail unless the release binary's hash is in lean/checkers.lock")
    parser.add_argument("cargo_args", nargs=argparse.REMAINDER,
                        help="Cargo arguments (default: a locked release build)")
    args = parser.parse_args()
    cargo = shutil.which("cargo")
    if cargo is None:
        print("cargo is not on PATH", file=sys.stderr)
        return 2
    cargo_args = args.cargo_args or list(DEFAULT_BUILD)
    done = subprocess.run([cargo, *cargo_args], cwd=ROOT, env=cargo_env(), check=False)
    if done.returncode:
        return done.returncode
    if cargo_args[0] == "build" and "--release" in cargo_args and RELEASE_BINARY.is_file():
        value = digest(RELEASE_BINARY)
        pinned = value in pinned_digests()
        print(f"{value}  {RELEASE_BINARY}: {'pinned' if pinned else 'NOT pinned'} in {LOCK}")
        if args.check and not pinned:
            return 1
    elif args.check:
        print("--check needs a release build", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
