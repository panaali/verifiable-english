#!/usr/bin/env python3
"""Shared Lean builds (test-architecture plan 3.8, "Shared builds"): one checked copy of a worktree's `lean/.lake`
per key, restored into another worktree of the same Lean tree instead of building it again.

The key (`key`) names what the build depends on:
- `lean_tree`: the `lean/` tree of HEAD (`git ls-tree -r HEAD`), without `lean/checkers.lock`, which no build reads
  (the pins are checked on their own, below). `lean/` must be clean: a worktree with uncommitted Lean changes
  neither publishes nor restores.
- `toolchain`: `lean --version` and `lake --version` of the toolchain `lean/lean-toolchain` selects, and the
  variables Lake reads to choose its compiler, archiver and toolchain (`LAKE_ENV`).
- `platform`: the operating system and `uname -m`, so an aarch64 build is never offered to x86_64, or the reverse.
- `lake_manifest`: the SHA-256 of `lean/lake-manifest.json`.
- `pins`: whose pins vouch for the build's checker (`PINNED`): `lean/checkers.lock` (the worktree's lock, the x86
  authority) or `runner-local:<runner>`. A runner whose pins are local, such as the Mac runner (it pins its own
  builds, uncommitted), keeps them in `<store>/pins/<runner>.json`.

An entry, `<store>/v1/<SHA-256 of the key>/`, holds `lake/` (the build) and `pins.json` (the seal): the key, the
SHA-256, size and mode of every file, and the checkers' digests. `publish` fills a scratch directory, writes the
pins (a runner-local authority's pins file) and then the seal, makes the entry read-only and renames it into
place. An entry is never rewritten: a second publish of the same key keeps the first.

`restore` checks a build before it is used, and refuses it on any difference (exit 3; the caller builds as before):
1. the seal's key is this worktree's key, field by field;
2. the entry holds exactly the seal's files, each with its SHA-256 (a tampered entry is moved to `<store>/refused/`
   and never offered again);
3. every checker in `PINNED` is pinned by the key's authority (for `lean/checkers.lock`, this worktree's lock);
4. in the worktree, after the copy: no executable is stale or obsolete (`tools/lake_outputs.py`), and Lake itself
   finds every target up to date for this tree (`lake build --no-build`). On a refusal here the worktree's previous
   `lean/.lake` is put back.

Executables and `.olean` files are shared as read-only hard links when the store is on the worktree's file system.
Lean 4.24 writes both to a new file and renames it (`.olean` by `rename`, an executable through the linker's
temporary file), so a later build in the worktree replaces the link and never writes into the store. Lake rewrites
the other files (`.c`, traces, `.ilean`, `.setup.json`) in place, so they are copied. A read-only link turns any
in-place write into an error, and every restore hashes the whole entry again.

Where it runs: worktrees (R0, R1, builders) and the train's candidate worktree, before `lake build`. The gate never
reads the store: it runs `lake build` itself (which rebuilds whatever Lake's traces do not match), the stale check and
the pins. The nightly (R3) does not restore (`VE_LEAN_SHARE=off`), so it builds everything every night.

    python3 tools/lean_share.py key               # print this worktree's key and entry
    python3 tools/lean_share.py restore           # exit 0: restored; exit 3: nothing usable, build as before
    python3 tools/lean_share.py publish           # after a successful `lake build`: store this build
    python3 tools/lean_share.py verify            # check every entry; exit 1 when one fails
    python3 tools/lean_share.py prune --keep 8    # keep the 8 entries restored or published last
Options: --store DIR (default: $VE_LEAN_SHARE, else ~/.cache/ve-lean-share; VE_LEAN_SHARE=off turns restore and
publish off), --pins lean/checkers.lock|runner-local:<runner> (default: the lock on x86_64, else
runner-local:<host name>), --copy (never link).
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import contextlib
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import pwd
import re
import shutil
import socket
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import lake_outputs  # noqa: E402

LEAN = ROOT / "lean"
FORMAT = 1
LOCK_PINS = "lean/checkers.lock"
RUNNER_PINS = re.compile(r"runner-local:([A-Za-z0-9][A-Za-z0-9._-]*)")
# The checkers whose builds are pinned (lean/checkers.lock): a build is offered only when each is present and pinned.
PINNED = ("ve_service",)
# The environment Lake reads to choose the compiler, archiver and toolchain it builds with (Lake 4.24's IO.getEnv
# calls, without those that only locate caches or homes).
LAKE_ENV = ("AR", "CC", "ELAN_TOOLCHAIN", "LAKE_OVERRIDE_LEAN", "LEAN", "LEAN_AR", "LEAN_CC", "LEAN_GITHASH",
            "LEAN_SYSROOT", "MACOSX_DEPLOYMENT_TARGET")
SEAL = "pins.json"
# Not part of a build: the client's digest cache, keyed by the file's inode (ve/backends/lean_service.py).
UNSHARED_SUFFIXES = (".sha256-cache",)


class Refused(Exception):
    """No stored build may be used here; the message says why."""


def _timeout(env: dict) -> float:
    return float(env.get("VE_LEAN_TIMEOUT", "600"))


def _git(lean: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=lean, capture_output=True, text=True, check=False)
    if done.returncode:
        raise Refused(f"git {' '.join(args)}: {done.stderr.strip()[-500:]}")
    return done.stdout


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _hash_all(paths: list[Path]) -> list[str]:
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as pool:
        return list(pool.map(_sha256, paths))


def lean_tree(lean: Path = LEAN) -> str:
    """SHA-256 of the `lean/` tree of HEAD without the pins; refused when `lean/` differs from HEAD."""
    prefix = _git(lean, "rev-parse", "--show-prefix").strip()
    pins = prefix + "checkers.lock"
    changed = _git(lean, "diff", "--name-only", "-z", "HEAD", "--", ".").split("\0")
    changed += _git(lean, "ls-files", "--others", "--exclude-standard", "--full-name", "-z", "--", ".").split("\0")
    if dirty := sorted(name for name in changed if name and name != pins):
        raise Refused(f"lean/ differs from HEAD ({', '.join(dirty[:5])}{', ...' if len(dirty) > 5 else ''})")
    entries = [entry for entry in _git(lean, "ls-tree", "-r", "-z", "--full-name", "HEAD", "--", ".").split("\0")
               if entry and entry.split("\t", 1)[-1] != pins]
    if not entries:
        raise Refused("HEAD has no lean/ tree")
    return hashlib.sha256("\0".join(entries).encode()).hexdigest()


def toolchain(lean: Path = LEAN, env: dict | None = None) -> dict:
    """The versions of the toolchain `lean/lean-toolchain` selects, and the environment Lake builds with."""
    env = dict(os.environ if env is None else env)
    versions = {}
    for name in ("lean", "lake"):
        try:
            done = subprocess.run([lake_outputs.lean_executable(env, name), "--version"], cwd=lean, env=env,
                                  capture_output=True, text=True, check=False, timeout=_timeout(env))
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
            raise Refused(f"{name} --version: {error}") from None
        if done.returncode or not done.stdout.strip():
            raise Refused(f"{name} --version failed: {done.stderr.strip()[-500:]}")
        versions[name] = done.stdout.strip()
    return {**versions, "env": {name: env.get(name) for name in LAKE_ENV}}


def machine() -> dict:
    return {"system": platform.system(), "machine": platform.machine()}


def default_pins() -> str:
    return LOCK_PINS if platform.machine() in ("x86_64", "AMD64") else f"runner-local:{socket.gethostname()}"


def key(lean: Path = LEAN, pins: str | None = None, env: dict | None = None) -> dict:
    """What a build of `lean` depends on (module docstring); refused when it cannot be known."""
    pins = default_pins() if pins is None else pins
    if pins != LOCK_PINS and not RUNNER_PINS.fullmatch(pins):
        raise Refused(f"unknown pins authority {pins!r}: {LOCK_PINS} or runner-local:<runner>")
    manifest = lean / "lake-manifest.json"
    return {"format": FORMAT, "lean_tree": lean_tree(lean), "toolchain": toolchain(lean, env),
            "platform": machine(),
            "lake_manifest": _sha256(manifest) if manifest.is_file() else None, "pins": pins}


def entry_id(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def default_store(env: dict | None = None) -> Path | None:
    """`$VE_LEAN_SHARE`, else the account's ~/.cache/ve-lean-share; None when VE_LEAN_SHARE=off."""
    value = (os.environ if env is None else env).get("VE_LEAN_SHARE")
    if value == "off":
        return None
    return Path(value) if value else Path(pwd.getpwuid(os.getuid()).pw_dir) / ".cache/ve-lean-share"


def _pins_file(store: Path, pins: str) -> Path:
    return store / "pins" / f"{RUNNER_PINS.fullmatch(pins).group(1)}.json"


def _read_pins(path: Path) -> set[str]:
    """The checker digests a pins file lists, in lean/checkers.lock's format ({"ve_service": [...]})."""
    try:
        values = json.loads(path.read_text())[PINNED[0]]
    except (OSError, ValueError, KeyError, TypeError):
        raise Refused(f"cannot read the pins in {path}") from None
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise Refused(f"cannot read the pins in {path}")
    return set(values)


def pinned(lean: Path, store: Path, pins: str) -> set[str]:
    """The checker digests the authority `pins` lists: this worktree's lock, or the runner's own pins."""
    if pins == LOCK_PINS:
        return _read_pins(lean / "checkers.lock")
    path = _pins_file(store, pins)
    return _read_pins(path) if path.exists() else set()


def _check_pins(lean: Path, store: Path, pins: str, checkers: dict[str, str]) -> None:
    allowed = pinned(lean, store, pins)
    for name in PINNED:
        if checkers.get(name) not in allowed:
            raise Refused(f"{name} {checkers.get(name)} is not pinned by {pins}")


def _up_to_date(lean: Path, env: dict | None) -> None:
    """Lake's own verdict: every default target is up to date for these sources (`lake build --no-build`)."""
    env = dict(os.environ if env is None else env)
    done = subprocess.run([lake_outputs.lean_executable(env, "lake"), "build", "--no-build"], cwd=lean, env=env,
                          capture_output=True, text=True, check=False, timeout=_timeout(env))
    if done.returncode:
        needs = [line for line in done.stdout.splitlines() if line.startswith("✖")][:3]
        raise Refused(f"Lake finds targets that need a build: {'; '.join(needs) or done.stderr.strip()[-300:]}")


def _check_worktree_build(lean: Path, env: dict | None, *, obsolete: bool) -> list[Path]:
    """Refused unless every executable a lakefile target names is traced as built and Lake finds the build up to
    date; with `obsolete`, a file no target names is refused too. The obsolete files (when allowed)."""
    found = lake_outputs.obsolete(lean)
    if obsolete and found:
        raise Refused(f"files no lakefile target names: {', '.join(path.name for path in found)}")
    if stale := [path for path in lake_outputs.stale(lean, env) if path not in found]:
        raise Refused(f"executables whose traces do not record them: {', '.join(path.name for path in stale)}")
    _up_to_date(lean, env)
    return found


def _files(root: Path) -> list[str]:
    """The regular files under `root`, as sorted POSIX paths relative to it; anything else is refused."""
    found = []
    for directory, subdirectories, names in os.walk(root):
        for name in [*names, *subdirectories]:
            path = Path(directory) / name
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise Refused(f"{path} is not a regular file or directory")
        found += [(Path(directory) / name).relative_to(root).as_posix() for name in names]
    return sorted(found)


def _shared(relative: str, executables: set[str]) -> bool:
    """Whether Lake replaces this file by renaming a new one over it (so it may be a hard link to the store)."""
    parts = relative.split("/")
    return relative.endswith(".olean") or (parts[:2] == ["build", "bin"] and len(parts) == 3
                                           and parts[2] in executables)


def _place(source: Path, target: Path, link: bool) -> bool:
    """Link (made read-only first) or copy `source` to `target`; whether it was linked."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if link:
        mode = stat.S_IMODE(source.stat().st_mode)
        os.chmod(source, mode & ~0o222)
        try:
            os.link(source, target)
            return True
        except OSError:  # another file system, or links not allowed: copy
            os.chmod(source, mode)
    shutil.copy2(source, target)
    return False


def _read_only(root: Path) -> None:
    for directory, _, names in os.walk(root, topdown=False):
        for name in names:
            path = Path(directory) / name
            os.chmod(path, stat.S_IMODE(path.stat().st_mode) & ~0o222)
        os.chmod(directory, 0o555)


def _remove(path: Path) -> None:
    """Remove a tree that may hold read-only directories (an entry, a refused restore)."""
    if not path.exists() and not path.is_symlink():
        return
    if path.is_dir() and not path.is_symlink():
        for directory, _, _ in os.walk(path):
            os.chmod(directory, 0o755)
        shutil.rmtree(path)
    else:
        path.unlink()


def _used(store: Path, ident: str) -> None:
    stamp = store / "used" / ident
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.touch()


def _seal(entry: Path) -> dict:
    try:
        seal = json.loads((entry / SEAL).read_text())
    except (OSError, ValueError):
        raise Refused(f"{entry}: no readable seal") from None
    if not isinstance(seal, dict) or seal.get("format") != FORMAT or not isinstance(seal.get("files"), dict):
        raise Refused(f"{entry}: the seal is not format {FORMAT}")
    return seal


def check_entry(entry: Path) -> dict:
    """The seal of `entry`, after checking that the entry holds exactly its files with their digests and sizes."""
    seal = _seal(entry)
    if entry_id(seal.get("key")) != entry.name:
        raise Refused(f"{entry.name}: the seal's key is another entry's")
    files, found = seal["files"], _files(entry / "lake")
    if missing := sorted(set(files) - set(found)):
        raise Refused(f"{entry.name}: files missing: {', '.join(missing[:5])}")
    if extra := sorted(set(found) - set(files)):
        raise Refused(f"{entry.name}: files the seal does not list: {', '.join(extra[:5])}")
    for name in found:
        record = files[name]
        if not isinstance(record, dict) or set(record) != {"sha256", "size", "mode", "link"} or \
                type(record["size"]) is not int or type(record["mode"]) is not int or type(record["link"]) is not bool:
            raise Refused(f"{entry.name}: the seal's record of {name} is malformed")
    paths = [entry / "lake" / name for name in found]
    for name, path, digest in zip(found, paths, _hash_all(paths)):
        if files[name]["sha256"] != digest or files[name]["size"] != path.stat().st_size:
            raise Refused(f"{entry.name}: {name} is not the file the seal records")
    for name in PINNED:
        if seal.get("checkers", {}).get(name) != files.get(f"build/bin/{name}", {}).get("sha256"):
            raise Refused(f"{entry.name}: the seal's {name} digest is not its file's")
    return seal


def _quarantine(store: Path, entry: Path) -> None:
    target = store / "refused" / f"{entry.name}-{os.getpid()}-{datetime.datetime.now():%Y%m%dT%H%M%S}"
    target.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.suppress(OSError):
        os.chmod(entry, 0o755)  # moving a directory to another parent rewrites its `..`
        os.rename(entry, target)


def publish(lean: Path, store: Path, pins: str | None = None, *, link: bool = True,
            env: dict | None = None) -> Path:
    """Store this worktree's build under its key (module docstring); the entry. Refused unless the build is
    complete, current and its checkers are pinned."""
    value = key(lean, pins, env)
    pins = value["pins"]
    entries = store / "v1"
    final = entries / entry_id(value)
    if final.is_dir():
        _used(store, final.name)
        return final
    dotlake = lean / ".lake"
    left_out = {path.relative_to(dotlake).as_posix() for path in _check_worktree_build(lean, env, obsolete=False)}
    executables = set(lake_outputs.executables(lean))
    names = [name for name in _files(dotlake) if not name.endswith(UNSHARED_SUFFIXES) and name not in left_out]
    if missing := [name for name in PINNED if f"build/bin/{name}" not in names]:
        raise Refused(f"the build has no {', '.join(missing)}")
    entries.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="tmp-", dir=entries))
    try:
        linked = {name: _place(dotlake / name, scratch / "lake" / name, link and _shared(name, executables))
                  for name in names}
        paths = [scratch / "lake" / name for name in names]
        files = {name: {"sha256": digest, "size": path.stat().st_size, "mode": stat.S_IMODE(path.stat().st_mode),
                        "link": linked[name]}
                 for name, path, digest in zip(names, paths, _hash_all(paths))}
        checkers = {name: files[f"build/bin/{name}"]["sha256"] for name in PINNED}
        if pins == LOCK_PINS:
            _check_pins(lean, store, pins, checkers)
        else:  # the runner's own pins: written before the seal, so a sealed entry is always pinned
            _add_runner_pins(store, pins, checkers)
        seal = {"format": FORMAT, "key": value, "files": files, "checkers": checkers,
                "published": {"commit": _git(lean, "rev-parse", "HEAD").strip(),
                              "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}}
        (scratch / SEAL).write_text(json.dumps(seal, indent=1, sort_keys=True) + "\n")
        _read_only(scratch)
        try:
            os.rename(scratch, final)
        except OSError:
            if not final.is_dir():
                raise
            # another worktree sealed the same key first; its entry stands
    finally:
        _remove(scratch)
    _used(store, final.name)
    return final


def _add_runner_pins(store: Path, pins: str, checkers: dict[str, str]) -> None:
    path = _pins_file(store, pins)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_name(path.name + ".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        listed = sorted((_read_pins(path) if path.exists() else set()) | set(checkers.values()))
        scratch = path.with_name(f".{path.name}.{os.getpid()}")
        scratch.write_text(json.dumps({PINNED[0]: listed}, indent=2) + "\n")
        os.replace(scratch, path)


def restore(lean: Path, store: Path, pins: str | None = None, *, link: bool = True,
            env: dict | None = None) -> Path:
    """Replace `lean/.lake` by the stored build of this key, checked first (module docstring); the entry used.
    Refused (and the worktree unchanged) when there is none or any check fails."""
    value = key(lean, pins, env)
    pins = value["pins"]
    entry = store / "v1" / entry_id(value)
    if not entry.is_dir():
        raise Refused(f"no stored build for this key ({entry.name[:16]})")
    try:
        seal = check_entry(entry)
    except Refused:
        _quarantine(store, entry)
        raise
    if seal["key"] != value:  # check_entry tied the seal to its entry's name; this ties it to the worktree
        raise Refused(f"the stored build's key is not this worktree's: "
                      f"{', '.join(sorted(name for name in value if seal['key'].get(name) != value[name]))}")
    _check_pins(lean, store, pins, seal["checkers"])
    staging = lean / f".lake.share-{os.getpid()}"
    previous = lean / f".lake.previous-{os.getpid()}"
    _remove(staging)
    try:
        for name, record in seal["files"].items():
            target = staging / name
            if not _place(entry / "lake" / name, target, link and record["link"]):
                os.chmod(target, stat.S_IMODE(record["mode"]) | 0o200)
        dotlake = lean / ".lake"
        if dotlake.exists():
            os.rename(dotlake, previous)
        try:
            os.rename(staging, dotlake)
            _check_worktree_build(lean, env, obsolete=True)
        except BaseException:
            _remove(dotlake)
            if previous.exists():
                os.rename(previous, dotlake)
            raise
    finally:
        _remove(staging)
        _remove(previous)
    _used(store, entry.name)
    return entry


def verify(store: Path) -> list[str]:
    """One line per entry that fails its seal (check_entry); the store is not changed."""
    failures = []
    for entry in sorted((store / "v1").glob("*")):
        if entry.name.startswith("tmp-"):
            continue
        try:
            check_entry(entry)
        except Refused as error:
            failures.append(str(error))
    return failures


def prune(store: Path, keep: int) -> list[str]:
    """Remove all but the `keep` entries used last, every refused entry and every publish left unfinished; the
    names removed. A worktree that restored an entry keeps its files: they are its own links or copies."""
    entries = sorted((entry for entry in (store / "v1").glob("*") if not entry.name.startswith("tmp-")),
                     key=lambda entry: (store / "used" / entry.name).stat().st_mtime
                     if (store / "used" / entry.name).exists() else 0.0, reverse=True)
    removed = []
    for entry in [*entries[keep:], *(store / "v1").glob("tmp-*"), *(store / "refused").glob("*")]:
        trash = store / "trash" / f"{entry.name}-{os.getpid()}"
        trash.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(entry, 0o755)  # a restore that starts now finds no entry, never half of one
        os.rename(entry, trash)
        _remove(trash)
        (store / "used" / entry.name).unlink(missing_ok=True)
        removed.append(entry.name)
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("key", "restore", "publish", "verify", "prune"))
    parser.add_argument("--lean", type=Path, default=LEAN, help="the Lake project (default: lean/)")
    parser.add_argument("--store", type=Path, help="the store (default: $VE_LEAN_SHARE or ~/.cache/ve-lean-share)")
    parser.add_argument("--pins", help=f"{LOCK_PINS} or runner-local:<runner> (default: {default_pins()})")
    parser.add_argument("--copy", action="store_true", help="copy every file; never hard-link into the store")
    parser.add_argument("--keep", type=int, default=8, help="prune: the entries to keep")
    args = parser.parse_args(argv)
    store = args.store or default_store()
    lean = args.lean.resolve()

    def say(text: str) -> None:
        print(f"[lean-share] {text}", file=sys.stderr, flush=True)

    try:
        if args.command == "key":
            value = key(lean, args.pins)
            print(json.dumps({"entry": entry_id(value), "key": value}, indent=1, sort_keys=True))
            return 0
        if store is None:
            say(f"{args.command}: off (VE_LEAN_SHARE=off)")
            return 3
        if args.command == "verify":
            failures = verify(store)
            for failure in failures:
                say(f"refused: {failure}")
            return 1 if failures else 0
        if args.command == "prune":
            for name in prune(store, args.keep):
                say(f"removed {name}")
            return 0
        action = publish if args.command == "publish" else restore
        entry = action(lean, store, args.pins, link=not args.copy)
        say(f"{'published' if action is publish else 'restored'} {entry}")
        return 0
    except Refused as error:
        say(f"{args.command}: refused: {error}")
        return 3
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        say(f"{args.command}: failed, nothing used: {error}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
