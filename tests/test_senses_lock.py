"""The senses lock (docs/spec/senses-PLAN.md 2.7, D17): `tools/senses_lock.py` and its pre-commit check."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import senses_lock  # noqa: E402


def reader(root: Path):
    return lambda path: (root / path).read_bytes() if (root / path).is_file() else None


@pytest.fixture
def tree(tmp_path):
    for path in (*senses_lock.HASHED, senses_lock.LOCK, senses_lock.VERSION_TARGET):
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / path, tmp_path / path)
    return tmp_path


def touch(tree: Path, name: str) -> None:
    with (tree / f"lean/VE/Senses/{name}.lean").open("a") as handle:
        handle.write("\n")


def test_the_repository_lock_is_current():
    assert senses_lock.check(reader(ROOT)) == []
    assert ("senses lock", "check_senses_lock") in [(name, check.__name__) for name, check in _hook().CHECKS]


def _hook():
    sys.path.insert(0, str(ROOT / "tools/hooks"))
    import precommit
    return precommit


def test_a_changed_definition_needs_a_new_version(tree):
    base = (tree / senses_lock.LOCK).read_bytes()
    touch(tree, "Project")
    assert any("raise senses_version" in error for error in senses_lock.check(reader(tree)))
    with pytest.raises(SystemExit, match="new --senses-version"):
        senses_lock.write(tree)
    assert senses_lock.write(tree, "2") == [senses_lock.VERSION_TARGET, senses_lock.LOCK]
    assert senses_lock.check(reader(tree), base) == []
    assert b'def sensesVersion : String := "2"' in (tree / senses_lock.VERSION_TARGET).read_bytes()


def test_the_hook_refuses_a_new_hash_with_the_same_version(tree):
    base = (tree / senses_lock.LOCK).read_bytes()
    touch(tree, "Read")
    lock = json.loads(base)
    lock["files"]["lean/VE/Senses/Read.lean"] = hashlib.sha256((tree / "lean/VE/Senses/Read.lean").read_bytes()).hexdigest()
    (tree / senses_lock.LOCK).write_bytes(senses_lock.render_lock(lock["senses_version"], lock["files"]))
    assert senses_lock.check(reader(tree)) == []
    [error] = senses_lock.check(reader(tree), base)
    assert "lean/VE/Senses/Read.lean" in error and "unchanged; raise it" in error


def test_a_version_module_out_of_step_is_refused(tree):
    (tree / senses_lock.VERSION_TARGET).write_bytes(senses_lock.render_version("9"))
    assert any("does not hold senses_version" in error for error in senses_lock.check(reader(tree)))
