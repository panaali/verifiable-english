"""The content-keyed entry store shared by the repository's caches (`tools/run_cache.py`, `tools/lean_dump_cache.py`).

An entry is a gzip-compressed JSON object in a cache directory, named by the SHA-256 of its format and inputs
(`key_of`). `directory` says where: `VE_RUN_CACHE=off` turns every cache off, a path puts them there, and by
default they are in the git common directory's `ve-run-cache`, shared by the checkout's worktrees; a named cache
keeps its entries in a subdirectory of its own, so each prunes only its own. `store` writes atomically (a fresh
temporary file, then a rename: two worktrees may store one key at once) and keeps the newest `keep` entries;
`load` returns None for an entry that is missing, unreadable or not a JSON object, so the caller runs as without
a cache.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def directory(root: Path, name: str | None = None) -> Path | None:
    """Where entries are kept (`VE_RUN_CACHE`, else the git common directory's `ve-run-cache`; `name`'s
    subdirectory of it for a named cache), or None when the caches are off."""
    setting = os.environ.get("VE_RUN_CACHE")
    if setting == "off":
        return None
    if setting:
        base = Path(setting)
    else:
        from tests.subprocesses import HANG_TIMEOUT
        found = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root,
                               capture_output=True, text=True, timeout=HANG_TIMEOUT)
        if found.returncode or not found.stdout.strip():
            return None
        base = Path(found.stdout.strip()) / "ve-run-cache"
    return base / name if name else base


def file_digest(path: Path) -> str:
    if not path.is_file():
        return "absent"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def listing_digest(path: Path) -> str:
    try:
        names = sorted(os.listdir(path))
    except OSError:
        return "absent"
    return hashlib.sha256("\n".join(names).encode("utf-8", "surrogateescape")).hexdigest()


def key_of(format_: str, inputs: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps([format_, sorted(inputs.items())]).encode()).hexdigest()


def entry_path(folder: Path, key: str) -> Path:
    return folder / f"{key}.json.gz"


def load(path: Path) -> dict | None:
    """The entry stored at `path`, or None when it is missing, unreadable or not a JSON object."""
    try:
        with gzip.open(path, "rt") as handle:
            entry = json.load(handle)
    except (OSError, ValueError, EOFError):
        return None
    return entry if isinstance(entry, dict) else None


def store(path: Path, entry: dict, keep: int) -> None:
    """Write `entry` at `path` atomically, then remove all but the newest `keep` entries of its directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(handle, "wb") as raw, gzip.open(raw, "wt") as text:
            json.dump(entry, text)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    entries = []
    for found in path.parent.glob("*.json.gz"):
        try:
            entries.append((found.stat().st_mtime, found))
        except OSError:  # removed by another run meanwhile
            pass
    for _, stale in sorted(entries, reverse=True)[keep:]:
        stale.unlink(missing_ok=True)


def touch(path: Path) -> None:
    """Mark a used entry newest, so pruning keeps it."""
    try:
        path.touch()
    except OSError:  # pruned by another run meanwhile: the answer is already read
        pass
