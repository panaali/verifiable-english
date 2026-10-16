"""tools/lean_share.py: a stored Lean build is used only under its own key and only after its checks (test-architecture
plan 3.8, "Shared builds"). A build of another tree, another architecture or another toolchain is never offered; a
tampered entry, an unpinned checker or a build Lake finds out of date is refused, and the worktree is left as it was.

The project is a real one-module Lake project built once per module by the pinned toolchain, in a private git
repository under the test's temporary directory; the store is the test's own."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tools import lake_outputs, lean_share

ROOT = Path(__file__).resolve().parents[1]
GIT = ["git", "-c", "user.name=VE", "-c", "user.email=ve@example.invalid", "-c", "commit.gpgsign=false",
       "-c", "init.defaultBranch=main"]
LAKEFILE = """name = "tiny"
defaultTargets = ["Tiny", "ve_service"]

[[lean_lib]]
name = "Tiny"

[[lean_exe]]
name = "ve_service"
root = "Main"
"""
MANIFEST = {"version": "1.1.0", "packagesDir": ".lake/packages", "packages": [], "name": "tiny", "lakeDir": ".lake"}


def git(cwd: Path, *args: str) -> str:
    return subprocess.run([*GIT, *args], cwd=cwd, capture_output=True, text=True, check=True,
                          timeout=HANG_TIMEOUT).stdout


def lake_build(lean: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([lake_outputs.lean_executable(None, "lake"), "build", *args], cwd=lean,
                          capture_output=True, text=True, check=False, timeout=HANG_TIMEOUT)


def write_tree(lean: Path, value: int) -> None:
    (lean / "Tiny.lean").write_text(f"def Tiny.value : Nat := {value}\n")


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """A committed repository whose `lean/` is built, with its `ve_service` pinned in `lean/checkers.lock`."""
    repository = tmp_path_factory.mktemp("lean-share") / "source"
    lean = repository / "lean"
    lean.mkdir(parents=True)
    (repository / ".gitignore").write_text(".lake/\n")
    (lean / "lakefile.toml").write_text(LAKEFILE)
    (lean / "lean-toolchain").write_text((ROOT / "lean/lean-toolchain").read_text())
    (lean / "lake-manifest.json").write_text(json.dumps(MANIFEST))
    (lean / "Main.lean").write_text('import Tiny\ndef main : IO Unit := IO.println s!"{Tiny.value}"\n')
    write_tree(lean, 1)
    done = lake_build(lean)
    assert done.returncode == 0, done.stdout + done.stderr
    digest = lean_share._sha256(lean / ".lake/build/bin/ve_service")
    (lean / "checkers.lock").write_text(json.dumps({"ve_service": [digest]}))
    git(repository, "init", "-q")
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "-m", "tiny")
    return lean


def clone(built: Path, tmp_path: Path, name: str = "worktree") -> Path:
    """A fresh checkout of the built repository: the same `lean/` tree, no build."""
    target = tmp_path / name
    subprocess.run([*GIT, "clone", "-q", str(built.parent), str(target)], check=True, capture_output=True,
                   timeout=HANG_TIMEOUT)
    return target / "lean"


def published(built: Path, tmp_path: Path, **options) -> tuple[Path, Path]:
    store = tmp_path / "store"
    return store, lean_share.publish(built, store, **options)


def refused(lean: Path, store: Path, match: str, **options) -> None:
    with pytest.raises(lean_share.Refused, match=match):
        lean_share.restore(lean, store, **options)


def test_a_stored_build_restores_up_to_date_and_never_shares_a_file_lake_rewrites(built, tmp_path):
    store, entry = published(built, tmp_path)
    lean = clone(built, tmp_path)
    assert lean_share.restore(lean, store) == entry
    assert lake_build(lean, "--no-build").returncode == 0
    assert lake_outputs.stale(lean) == [] and lake_outputs.obsolete(lean) == []
    seal = json.loads((entry / "pins.json").read_text())
    shared = {name for name, record in seal["files"].items() if record["link"]}
    assert "build/bin/ve_service" in shared and any(name.endswith(".olean") for name in shared)
    assert all(name == "build/bin/ve_service" or name.endswith(".olean") for name in shared)
    service = lean / ".lake/build/bin/ve_service"
    assert service.stat().st_ino == (entry / "lake/build/bin/ve_service").stat().st_ino
    assert not os.access(service, os.W_OK)
    # A later build in the worktree replaces its links; the store keeps every byte it sealed.
    write_tree(lean, 2)
    done = lake_build(lean)
    assert done.returncode == 0, done.stdout + done.stderr
    assert service.stat().st_ino != (entry / "lake/build/bin/ve_service").stat().st_ino
    assert lean_share.verify(store) == []


def test_a_build_of_another_tree_is_never_offered(built, tmp_path):
    store, entry = published(built, tmp_path)
    lean = clone(built, tmp_path)
    write_tree(lean, 2)
    git(lean.parent, "commit", "-q", "-am", "another tree")
    refused(lean, store, "no stored build for this key")
    # Moved under the other tree's key, it is refused by its seal, and never offered again.
    other = lean_share.entry_id(lean_share.key(lean))
    os.chmod(entry, 0o755)
    entry.rename(entry.with_name(other))
    refused(lean, store, "the seal's key is another entry's")
    assert not entry.with_name(other).exists() and len(list((store / "refused").iterdir())) == 1
    assert not (lean / ".lake").exists()


def test_a_forged_seal_for_another_tree_is_refused_by_lake_and_the_worktree_restored(built, tmp_path):
    """Defence in depth: a seal rewritten to name this tree still holds another tree's build, which Lake finds out
    of date; the worktree's own build comes back."""
    store, entry = published(built, tmp_path)
    lean = clone(built, tmp_path)
    write_tree(lean, 2)
    git(lean.parent, "commit", "-q", "-am", "another tree")
    own = lean / ".lake/own-build"
    own.parent.mkdir()
    own.write_text("the worktree's own build")
    value = lean_share.key(lean)
    seal = json.loads((entry / "pins.json").read_text())
    seal["key"] = value
    os.chmod(entry, 0o755)
    os.chmod(entry / "pins.json", 0o644)
    (entry / "pins.json").write_text(json.dumps(seal))
    entry.rename(entry.with_name(lean_share.entry_id(value)))
    refused(lean, store, "Lake finds targets that need a build")
    assert own.read_text() == "the worktree's own build"
    assert sorted(path.name for path in lean.iterdir() if path.name.startswith(".lake")) == [".lake"]


def test_a_build_of_another_architecture_is_never_offered(built, tmp_path, monkeypatch):
    real = lean_share.machine()
    other = "aarch64" if real["machine"] != "aarch64" else "x86_64"
    with monkeypatch.context() as patch:
        patch.setattr(lean_share, "machine", lambda: {**real, "machine": other})
        store, entry = published(built, tmp_path)
    lean = clone(built, tmp_path)
    refused(lean, store, "no stored build for this key")
    os.chmod(entry, 0o755)
    entry.rename(entry.with_name(lean_share.entry_id(lean_share.key(lean))))
    refused(lean, store, "the seal's key is another entry's")
    # and the reverse: this machine's build is not offered to the other architecture
    store, _ = published(built, tmp_path / "reverse")
    monkeypatch.setattr(lean_share, "machine", lambda: {**real, "machine": other})
    refused(lean, store, "no stored build for this key")


@pytest.mark.parametrize("field", ["lean", "lake", "env"])
def test_a_build_of_another_toolchain_is_never_offered(built, tmp_path, monkeypatch, field):
    real = lean_share.toolchain(built)
    changed = {**real, "env": {**real["env"], "LEAN_CC": "/opt/other/clang"}} if field == "env" else \
        {**real, field: real[field].replace("4.", "9.", 1)}
    assert changed != real
    with monkeypatch.context() as patch:
        patch.setattr(lean_share, "toolchain", lambda lean, env=None: changed)
        store, entry = published(built, tmp_path)
    lean = clone(built, tmp_path)
    refused(lean, store, "no stored build for this key")


@pytest.mark.parametrize("victim", ["build/bin/ve_service", "olean", "pins.json", "extra", "missing"])
def test_a_tampered_entry_is_refused_and_withdrawn(built, tmp_path, victim):
    store, entry = published(built, tmp_path)
    os.chmod(entry, 0o755)
    for directory, _, _ in os.walk(entry):
        os.chmod(directory, 0o755)
    olean = next(name for name in json.loads((entry / "pins.json").read_text())["files"] if name.endswith(".olean"))
    if victim == "extra":
        (entry / "lake/build/bin/ve_extra").write_bytes(b"planted")
    elif victim == "missing":
        (entry / "lake" / olean).unlink()
    elif victim == "pins.json":
        seal = json.loads((entry / "pins.json").read_text())
        seal["files"][olean]["sha256"] = "0" * 64
        os.chmod(entry / "pins.json", 0o644)
        (entry / "pins.json").write_text(json.dumps(seal))
    else:
        path = entry / "lake" / (olean if victim == "olean" else victim)
        data = bytearray(path.read_bytes())
        data[len(data) // 2] ^= 0xFF
        # write a copy: the stored file is a read-only link to the published worktree's file
        path.unlink()
        path.write_bytes(bytes(data))
    lean = clone(built, tmp_path)
    assert lean_share.verify(store) != []
    refused(lean, store, "files missing|files the seal does not list|is not the file the seal records")
    assert not entry.exists() and not (lean / ".lake").exists()
    refused(lean, store, "no stored build for this key")


def test_a_checker_the_authority_does_not_pin_is_refused(built, tmp_path):
    store, _ = published(built, tmp_path)
    lean = clone(built, tmp_path)
    (lean / "checkers.lock").write_text(json.dumps({"ve_service": ["0" * 64]}))  # the pins are not in the key
    refused(lean, store, "ve_service [0-9a-f]{64} is not pinned by lean/checkers.lock")
    assert not (lean / ".lake").exists()
    # and a build whose checker the lock does not pin is never stored
    unpinned = clone(built, tmp_path, "unpinned")
    shutil.copytree(built / ".lake", unpinned / ".lake")
    (unpinned / "checkers.lock").write_text(json.dumps({"ve_service": []}))
    with pytest.raises(lean_share.Refused, match="is not pinned"):
        lean_share.publish(unpinned, tmp_path / "other-store")


def test_runner_local_pins_are_their_runners_alone(built, tmp_path):
    store, entry = published(built, tmp_path, pins="runner-local:ve-mac-1")
    seal = json.loads((entry / "pins.json").read_text())
    assert json.loads((store / "pins/ve-mac-1.json").read_text()) == {"ve_service": [seal["checkers"]["ve_service"]]}
    lean = clone(built, tmp_path)
    refused(lean, store, "no stored build for this key", pins=lean_share.LOCK_PINS)
    refused(lean, store, "no stored build for this key", pins="runner-local:another-runner")
    assert lean_share.restore(lean, store, pins="runner-local:ve-mac-1") == entry
    # the runner's pins are checked at restore too, not only when the entry was sealed
    os.chmod(store / "pins/ve-mac-1.json", 0o644)
    (store / "pins/ve-mac-1.json").write_text(json.dumps({"ve_service": []}))
    refused(clone(built, tmp_path, "again"), store, "is not pinned by runner-local:ve-mac-1",
            pins="runner-local:ve-mac-1")


def test_a_build_lake_finds_out_of_date_or_a_dirty_tree_is_never_stored_or_restored(built, tmp_path):
    lean = clone(built, tmp_path)
    shutil.copytree(built / ".lake", lean / ".lake")
    write_tree(lean, 3)
    with pytest.raises(lean_share.Refused, match="lean/ differs from HEAD"):
        lean_share.publish(lean, tmp_path / "store")
    git(lean.parent, "commit", "-q", "-am", "not built")
    with pytest.raises(lean_share.Refused, match="Lake finds targets that need a build"):
        lean_share.publish(lean, tmp_path / "store")
    store, _ = published(built, tmp_path)
    dirty = clone(built, tmp_path, "dirty")
    (dirty / "New.lean").write_text("def x := 1\n")
    refused(dirty, store, "lean/ differs from HEAD")


def test_an_obsolete_executable_is_never_stored(built, tmp_path):
    lean = clone(built, tmp_path)
    shutil.copytree(built / ".lake", lean / ".lake")
    for suffix in ("", ".trace", ".hash"):
        (lean / f".lake/build/bin/ve_removed_route{suffix}").write_text("a target the lakefile no longer has")
    store, entry = published(lean, tmp_path)
    assert not any("ve_removed_route" in name for name in json.loads((entry / "pins.json").read_text())["files"])
    assert (lean / ".lake/build/bin/ve_removed_route").exists()  # publish never changes the worktree's files


def test_the_command_line_off_switch_and_prune(built, tmp_path, monkeypatch, capsys):
    lean = clone(built, tmp_path)
    monkeypatch.setenv("VE_LEAN_SHARE", "off")
    assert lean_share.main(["restore", "--lean", str(lean)]) == 3
    assert "off (VE_LEAN_SHARE=off)" in capsys.readouterr().err
    store = tmp_path / "store"
    monkeypatch.setenv("VE_LEAN_SHARE", str(store))
    assert lean_share.main(["restore", "--lean", str(lean)]) == 3
    assert lean_share.main(["publish", "--lean", str(built)]) == 0
    assert lean_share.main(["restore", "--lean", str(lean), "--copy"]) == 0
    assert all(path.stat().st_nlink == 1 for path in (lean / ".lake").rglob("*") if path.is_file())
    assert lean_share.main(["verify"]) == 0
    assert lean_share.main(["prune", "--keep", "0"]) == 0
    assert list((store / "v1").iterdir()) == [] and lake_build(lean, "--no-build").returncode == 0
