"""The lean-first A/B base-record cache (`tools/lean_first_cache.py`, speed-abcache): a hit gives the records a
recording writes, every key part is a miss when it changes, a dirty root or an unpinned build stores nothing, and a
damaged entry is a miss. Tiny fake segments of genuine record shapes; no checker runs."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools import lean_first_cache as cache
from tools import lean_first_diff as diff
from tools import lean_share

# Genuine records (lf-18's recording of the quantity corpus) and two pilot outcomes, one quoting its scratch path.
QUANTITY = [{"case": "007c8b643cc94fe0", "op": "prove", "outcome": {"returned": None},
             "source_sha256": "e29d26f78f469f1d4be7949626771516e4274821745e9d04ee0a2dcb40d09f21"},
            {"case": "018f715f0e072b38", "op": "admission",
             "outcome": {"raised": {"code": "InvalidInput", "message": "duplicate lemma"}},
             "source_sha256": "86a7c8f3809dae614a5da4bdafe2a511b2abf1cc69872624957c212d99d3f745"}]
BLOB = "0123456789abcdef0123456789abcdef01234567"
SOURCES = {row["case"]: row["source_sha256"] for row in QUANTITY} | {"pilot/a:x.ve.md": BLOB, "pilot/b:y.ve.md": BLOB}


def pilots(stem: str) -> list[dict]:
    return [{"case": "pilot/a:x.ve.md", "op": "document_check", "source_sha256": BLOB, "authority": "default",
             # genuine reports hold line breaks JSON leaves raw, which `str.splitlines` splits at
             "outcome": {"exit": 0, "stdout": "checked\u2028line\u0085next\u2029end", "stderr": []}},
            {"case": "pilot/b:y.ve.md", "op": "document_check", "source_sha256": BLOB, "authority": "default",
             "outcome": {"exit": 1, "stdout": f"cannot read {stem}.pilots/{BLOB}.ve.md", "stderr": ["error"]}}]


def recorded(out: Path, corpora, authorities) -> str:
    """What the fake child writes: the recorder's order (corpus, then authority)."""
    rows = []
    for corpus in corpora:
        if corpus == "pilots":
            rows += [{"corpus": corpus, **row} for row in pilots(str(out.with_suffix("")))]
        else:
            rows += [{"corpus": corpus, "authority": a, **row} for a in authorities for row in QUANTITY]
    return "".join(diff.line(row) for row in rows)


@pytest.fixture
def world(tmp_path, monkeypatch):
    root = tmp_path / "root"
    (root / "lean").mkdir(parents=True)
    (root / "lean/Main.lean").write_text("-- a\n")
    (root / ".gitignore").write_text(".lake/\ntarget/\n")
    git = lambda *args: subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)  # noqa: E731
    git("init", "-q")
    git("add", ".")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c")
    recorder = tmp_path / "recorder.py"
    recorder.write_text("one\n")
    state = {"digest": "d" * 64, "calls": [], "lean": {}}
    monkeypatch.setattr(lean_share, "key", lambda lean: {"lean_tree": lean_share.lean_tree(lean), **state["lean"]})
    monkeypatch.setattr(cache, "sources", lambda corpus, root, out: (state["digest"], SOURCES.get))
    monkeypatch.setattr(cache, "pinned_checkers", lambda root, builds: None)
    for name in ("VE_LEAN_SERVICE", "VE_RUST_JSONL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(cache, "RECORDER", (str(recorder),))
    monkeypatch.setattr(diff, "expected_cases", lambda root, corpora, authorities: {
        (c, a): {row["case"]: diff.only(row["op"]) for row in (pilots("") if c == "pilots" else QUANTITY)}
        for c in corpora for a in diff.authorities_of(c, authorities)})

    def child(root, out, corpora, authorities, workers, scratch=None):
        state["calls"].append((list(corpora), list(authorities)))
        out.write_text(recorded(scratch or out, corpora, authorities))
        state.get("during", lambda: None)()
        return state.get("code", 0)
    monkeypatch.setattr(diff, "run_child", child)
    monkeypatch.delenv("VE_AB_CACHE", raising=False)
    state.update(root=root, git=git, recorder=recorder, cache=tmp_path / "cache", tmp=tmp_path)
    return state


def run(world, name="base.jsonl", corpora=("quantity", "pilots"), authorities=("python", "lean")):
    out = world["tmp"] / "ab" / name
    out.parent.mkdir(exist_ok=True)
    world["calls"].clear()
    args = argparse.Namespace(root=str(world["root"]), out=str(out), corpus=list(corpora),
                              authority=list(authorities), workers=1, cache=str(world["cache"]))
    assert diff.record(args) == 0
    return out.read_text(), list(world["calls"])


def entries(world):
    return sorted((world["cache"] / "v1").glob("[0-9a-f]*"))


def test_hit_returns_the_records_a_recording_writes(world):
    cold, calls = run(world)
    assert calls == [(["quantity", "pilots"], ["python", "lean"])]
    assert cold == recorded(world["tmp"] / "ab/base.jsonl", ["quantity", "pilots"], ["python", "lean"])
    assert len(entries(world)) == 3  # quantity/python, quantity/lean, pilots/default
    warm, calls = run(world)
    assert (warm, calls) == (cold, [])
    # Another output path: the pilot diagnostic quotes that recording's own scratch directory, as recording would.
    other, calls = run(world, "elsewhere.jsonl")
    assert calls == [] and other == recorded(world["tmp"] / "ab/elsewhere.jsonl", ["quantity", "pilots"],
                                             ["python", "lean"])
    assert other != cold
    stored = "".join(path.joinpath("segment.jsonl").read_text() for path in entries(world))
    assert cache.SCRATCH in stored and str(world["tmp"]) not in stored


def test_store_layout_names_every_key_part(world):
    run(world, corpora=("quantity",), authorities=("python",))
    [entry] = entries(world)
    meta = json.loads((entry / "meta.json").read_text())
    assert set(meta["key"]) == {"format", "commit", "lean_build", "recorder", "python", "env", "checkers", "corpus",
                                "authority", "corpus_sha256"}
    assert entry.name == cache._json_sha256(meta["key"])
    assert meta["records"] == 2 and meta["sha256"] == cache._sha256((entry / "segment.jsonl").read_bytes())
    assert {oct(path.stat().st_mode & 0o777) for path in entry.iterdir()} == {"0o644"}
    assert oct(entry.stat().st_mode & 0o777) == "0o755"
    assert not list((world["cache"] / "v1").glob("tmp-*"))


def change_commit(world, monkeypatch):
    world["git"]("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "again", "--allow-empty")


def change_lean(world, monkeypatch):
    world["lean"]["toolchain"] = "another"


def change_recorder(world, monkeypatch):
    world["recorder"].write_text("two\n")


def change_corpus(world, monkeypatch):
    world["digest"] = "e" * 64


def change_env(world, monkeypatch):
    monkeypatch.setenv("VE_AUTHORITY_OVERRIDES", "another")


def change_python(world, monkeypatch):
    monkeypatch.setattr(sys, "version", sys.version + " another")


def _build(world, relative: str, data: bytes) -> None:
    path = world["root"] / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o755)


def change_service_build(world, monkeypatch):
    _build(world, "lean/.lake/build/bin/ve_service", b"rebuilt")


def change_route_build(world, monkeypatch):
    """A route executable the recording runs beside `ve_service` (ve/backends/english_lean.py, senses.py, ...)."""
    _build(world, "lean/.lake/build/bin/ve_english_route", b"rebuilt")


def change_rust_build(world, monkeypatch):
    _build(world, "rust/target/release/ve", b"rebuilt")


def change_service_override(world, monkeypatch):
    """`VE_LEAN_SERVICE` names a build elsewhere (`OVERRIDES`): its contents are keyed, not only its path."""
    world["override"].write_bytes(b"rebuilt")


def change_rust_override(world, monkeypatch):
    world["override"].write_bytes(b"rebuilt")


OVERRIDES = {change_service_override: "VE_LEAN_SERVICE", change_rust_override: "VE_RUST_JSONL"}


BUILD_CHANGES = [change_service_build, change_route_build, change_rust_build, change_service_override,
                 change_rust_override]


@pytest.mark.parametrize("change", [change_commit, change_lean, change_recorder, change_corpus, change_env,
                                    change_python, *BUILD_CHANGES])
def test_each_key_part_changed_is_a_miss(world, monkeypatch, change):
    for relative in ("lean/.lake/build/bin/ve_service", "lean/.lake/build/bin/ve_english_route",
                     "rust/target/release/ve"):
        _build(world, relative, b"built")
    world["override"] = world["tmp"] / "elsewhere" / "checker"
    world["override"].parent.mkdir()
    world["override"].write_bytes(b"built")
    if change in OVERRIDES:
        monkeypatch.setenv(OVERRIDES[change], str(world["override"]))
    cold, _ = run(world)
    change(world, monkeypatch)
    again, calls = run(world)
    assert calls == [(["quantity", "pilots"], ["python", "lean"])] and again == cold
    assert len(entries(world)) == 6


def test_the_authority_is_part_of_the_key(world):
    run(world, corpora=("quantity",), authorities=("python",))
    text, calls = run(world, corpora=("quantity",), authorities=("python", "lean"))
    assert calls == [(["quantity"], ["lean"])]
    assert text == recorded(world["tmp"] / "ab/base.jsonl", ["quantity"], ["python", "lean"])


def test_the_test_runner_settings_are_not_keyed(world, monkeypatch):
    run(world)
    monkeypatch.setenv("VE_TEST_MIN_WORKERS", "17")
    assert run(world)[1] == []


def test_a_dirty_root_is_neither_read_nor_stored(world):
    run(world)
    (world["root"] / "untracked.txt").write_text("x")
    text, calls = run(world, "dirty.jsonl")
    assert calls == [(["quantity", "pilots"], ["python", "lean"])]
    assert len(entries(world)) == 3
    (world["root"] / "untracked.txt").unlink()
    world["cache"] = world["tmp"] / "fresh"
    (world["root"] / "lean/Main.lean").write_text("-- changed\n")
    run(world)
    assert not (world["cache"] / "v1").exists()


def test_a_key_that_changes_while_recording_stores_nothing(world):
    world["during"] = lambda: world["recorder"].write_text("edited while recording\n")
    cold, _ = run(world)
    assert cold == recorded(world["tmp"] / "ab/base.jsonl", ["quantity", "pilots"], ["python", "lean"])
    assert not (world["cache"] / "v1").exists()


def test_a_failed_recording_writes_and_stores_nothing(world):
    world["code"] = 3
    out = world["tmp"] / "failed.jsonl"
    args = argparse.Namespace(root=str(world["root"]), out=str(out), corpus=["quantity"], authority=["python"],
                              workers=1, cache=str(world["cache"]))
    assert diff.record(args) == 3
    assert out.read_text() == "" and not (world["cache"] / "v1").exists()


def test_prune_keeps_what_was_stored_or_used_lately(world):
    run(world)
    old, used, fresh = entries(world)
    for path in (old, used):
        os.utime(path, (1, 1))
    (world["cache"] / "refused").mkdir()
    (world["cache"] / "refused/x").mkdir()
    lookups = {}
    for entry in (old, used, fresh):
        lookups[entry.name] = json.loads((entry / "meta.json").read_text())["key"]
    assert cache.lookup(world["cache"], lookups[used.name], SOURCES.get, world["tmp"] / "ab/base.jsonl")
    cache.prune(world["cache"])
    assert entries(world) == sorted([used, fresh]) and not list((world["cache"] / "refused").iterdir())


def test_an_unpinned_build_is_not_stored(world, monkeypatch):
    def unpinned(root, builds):
        raise cache.Miss("not pinned")
    monkeypatch.setattr(cache, "pinned_checkers", unpinned)
    run(world)
    assert not (world["cache"] / "v1").exists()


def test_pinned_checkers_reads_the_root_lock(tmp_path, monkeypatch):
    for name in ("VE_LEAN_SERVICE", "VE_RUST_JSONL"):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "lean/.lake/build/bin").mkdir(parents=True)
    (tmp_path / "rust/target/release").mkdir(parents=True)
    (tmp_path / "lean/.lake/build/bin/ve_service").write_bytes(b"lean")
    (tmp_path / "rust/target/release/ve").write_bytes(b"rust")
    lock = {"ve_service": [cache._sha256(b"lean")], "rust_jsonl": [cache._sha256(b"rust")]}
    (tmp_path / "lean/checkers.lock").write_text(json.dumps(lock))
    (tmp_path / "lean/.lake/build/bin/ve_service").chmod(0o755)
    (tmp_path / "lean/.lake/build/bin/ve_service.trace").write_text("not a checker")
    builds = cache.checker_builds(tmp_path)
    assert builds == {"lean/ve_service": cache._sha256(b"lean"), "ve_service": cache._sha256(b"lean"),
                      "rust_jsonl": cache._sha256(b"rust")}
    cache.pinned_checkers(tmp_path, builds)
    (tmp_path / "rust/target/release/ve").write_bytes(b"rebuilt")
    with pytest.raises(cache.Miss):
        cache.pinned_checkers(tmp_path, cache.checker_builds(tmp_path))
    (tmp_path / "rust/target/release/ve").unlink()
    with pytest.raises(cache.Miss):
        cache.pinned_checkers(tmp_path, cache.checker_builds(tmp_path))


def test_a_base_recorded_with_an_old_pinned_build_is_not_reused(tmp_path, monkeypatch):
    """Review F1's probe: the lock pins old builds too, so a root checked out at a new commit but not rebuilt
    passes the pin check. Its segment is keyed by the build it ran, so the rebuilt root records again."""
    for name in ("VE_LEAN_SERVICE", "VE_RUST_JSONL"):
        monkeypatch.delenv(name, raising=False)
    root = tmp_path / "root"
    (root / "lean/.lake/build/bin").mkdir(parents=True)
    (root / "rust/target/release").mkdir(parents=True)
    (root / "lean/lean-toolchain").write_text((diff.ROOT / "lean/lean-toolchain").read_text())
    (root / ".gitignore").write_text(".lake/\ntarget/\n")
    (root / "rust/target/release/ve").write_bytes(b"r")
    lock = {"ve_service": [cache._sha256(b"old"), cache._sha256(b"new")], "rust_jsonl": [cache._sha256(b"r")]}
    (root / "lean/checkers.lock").write_text(json.dumps(lock))
    git = lambda *args: subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)  # noqa: E731
    git("init", "-q")
    git("add", ".")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c")
    calls = []
    monkeypatch.setattr(lean_share, "key", lambda lean: {"lean_tree": lean_share.lean_tree(lean)})
    monkeypatch.setattr(cache, "sources", lambda *args: ("d" * 64, SOURCES.get))
    monkeypatch.setattr(diff, "expected_cases", lambda root, corpora, authorities: {
        (c, a): {row["case"]: diff.only(row["op"]) for row in QUANTITY}
        for c in corpora for a in diff.authorities_of(c, authorities)})
    monkeypatch.setattr(diff, "run_child", lambda root, out, corpora, authorities, workers, scratch=None: (
        calls.append(1) or out.write_text(recorded(scratch or out, corpora, authorities)) and 0))

    def record(build: bytes) -> bool:
        service = root / "lean/.lake/build/bin/ve_service"
        service.write_bytes(build)
        service.chmod(0o755)
        calls.clear()
        assert diff.record(argparse.Namespace(root=str(root), out=str(tmp_path / "base.jsonl"), corpus=["quantity"],
                                              authority=["lean"], workers=1, cache=str(tmp_path / "cache"))) == 0
        return bool(calls)
    assert record(b"old")  # recorded and stored: the old build is pinned
    assert len(list((tmp_path / "cache/v1").iterdir())) == 1
    assert record(b"new")  # rebuilt: another key, recorded again
    assert not record(b"new")


def _rewrite(entry: Path, transform) -> None:
    """Rewrite an entry's segment and give `meta.json` its new digest and count, so only the content check is left."""
    data = transform((entry / "segment.jsonl").read_text()).encode()
    (entry / "segment.jsonl").write_bytes(data)
    meta = json.loads((entry / "meta.json").read_text())
    meta.update(sha256=cache._sha256(data), records=data.count(b"\n"))
    (entry / "meta.json").write_text(json.dumps(meta))


DAMAGE = {
    "flipped byte": lambda e: (e / "segment.jsonl").write_bytes(
        (e / "segment.jsonl").read_bytes().replace(b"duplicate", b"duplicatf")),
    "truncated": lambda e: (e / "segment.jsonl").write_bytes((e / "segment.jsonl").read_bytes()[:-40]),
    "no meta": lambda e: (e / "meta.json").unlink(),
    "meta not JSON": lambda e: (e / "meta.json").write_text("{"),
    "no segment": lambda e: (e / "segment.jsonl").unlink(),
    "another key": lambda e: (e / "meta.json").write_text((e / "meta.json").read_text().replace('"lean"', '"python"')),
    "a whole record dropped": lambda e: _rewrite(e, lambda t: "".join(t.splitlines(keepends=True)[1:])),
    "a record twice": lambda e: _rewrite(e, lambda t: t + t.splitlines(keepends=True)[0]),
    "no final newline": lambda e: _rewrite(e, lambda t: t[:-1]),
    "not canonical": lambda e: _rewrite(e, lambda t: t.replace('"case":', '"case": ')),
    "another source": lambda e: _rewrite(e, lambda t: t.replace("e29d26", "e29d27")),
    "another authority": lambda e: _rewrite(e, lambda t: t.replace('"authority":"lean"', '"authority":"python"')),
    "not a record": lambda e: _rewrite(e, lambda t: t.replace('"returned":null', '"returned":null,"x":1')),
    "retyped": lambda e: _rewrite(e, lambda t: t.replace('"code":"InvalidInput"', '"code":7')),
}


@pytest.mark.parametrize("damage", sorted(DAMAGE))
def test_a_damaged_entry_is_a_miss_and_is_replaced(world, damage):
    cold, _ = run(world, corpora=("quantity",), authorities=("lean",))
    [entry] = entries(world)
    DAMAGE[damage](entry)
    again, calls = run(world, corpora=("quantity",), authorities=("lean",))
    assert calls == [(["quantity"], ["lean"])] and again == cold
    assert len(list((world["cache"] / "refused").iterdir())) == 1
    assert run(world, corpora=("quantity",), authorities=("lean",)) == (cold, [])


def test_without_a_cache_record_runs_as_before(world, monkeypatch):
    calls = []
    monkeypatch.setattr(diff, "run_child", lambda *args, **kwargs: calls.append((args, kwargs)) or 0)
    out = world["tmp"] / "plain.jsonl"
    args = argparse.Namespace(root=str(world["root"]), out=str(out), corpus=["quantity"], authority=["python"],
                              workers=3, cache=None)
    assert diff.record(args) == 0
    assert calls == [((world["root"].resolve(), out.resolve(), ["quantity"], ["python"], 3), {})]


def test_prewarm_refuses_a_commit_without_the_cache(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git = lambda *args: subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)  # noqa
    git("init", "-q")
    (repo / "f").write_text("x")
    git("add", ".")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c")
    commit = git("rev-parse", "HEAD").stdout.strip()
    assert cache.prewarm(commit, tmp_path / "cache", 1, repo=repo) == 2
    assert git("worktree", "list", "--porcelain").stdout.count("worktree ") == 1
    assert [path.name for path in (tmp_path / "cache").iterdir()] == []
    assert sorted(os.listdir(repo)) == [".git", "f"]


# --- the corpus key part (`sources`), run for real (review F2) ---------------------------------------------------

def _gz(path: Path, value) -> None:
    import gzip
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(value).encode()))


def _commit(repo: Path, branch: str, files: dict, init: bool = False) -> None:
    git = lambda *args: subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)  # noqa: E731
    if init:
        git("init", "-q")
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "root", "--allow-empty")
    git("checkout", "-q", "-B", branch)
    for name, data in files.items():
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_bytes(data)
    git("add", ".")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c", "--allow-empty")


def _write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)


PACKED = b'---\n{"senses": {"packs": ["pack.json"]}}\n---\nA document.\n'
# corpus: (write its inputs, [(edit an input, the case whose source digest must change, or None)], a case)
SOURCE_INPUTS = {
    "probe": (lambda w: _write(w.root / "tests/probe_matrix.py", "a"),
              [(lambda w: _write(w.root / "tests/probe_matrix.py", "b"), "any")], "any"),
    "conformance": (lambda w: [_write(w.root / f"conformance/{name}.json", name) for name in diff.CONFORMANCE],
                    [(lambda w, name=name: _write(w.root / f"conformance/{name}.json", "edited"), f"{name}/x")
                     for name in diff.CONFORMANCE], f"{diff.CONFORMANCE[0]}/x"),
    **{corpus: (lambda w, corpus=corpus: _write(w.out.with_suffix(f".{corpus}.json"), "a"),
                [(lambda w, corpus=corpus: _write(w.out.with_suffix(f".{corpus}.json"), "b"), "any")], "any")
       for corpus in ("readings", "rights", "norm_defaults", "document")},
    **{corpus: (lambda w, path=path: _gz(w.checkout / path, [{"id": "one", "v": 1}, {"id": "two", "v": 1}]),
                [(lambda w, path=path: _gz(w.checkout / path, [{"id": "one", "v": 2}, {"id": "two", "v": 1}]), "one"),
                 (lambda w, path=path: _gz(w.checkout / path, [{"id": "two", "v": 1}]), "one")], "two")
       for corpus, path in (("discourse", diff.DISCOURSE), ("quantity", diff.QUANTITY))},
    "pilots": (lambda w: _commit(w.checkout, "pilot/a", {"usecases/x.ve.md": PACKED, "usecases/pack.json": b"1"},
                                         init=True),
               [(lambda w: _commit(w.checkout, "pilot/a", {"usecases/pack.json": b"2"}), None),  # beside it
                (lambda w: _commit(w.checkout, "pilot/a", {"usecases/x.ve.md": PACKED + b"More.\n"}),
                 "pilot/a:usecases/x.ve.md"),
                (lambda w: _commit(w.checkout, "pilot/b", {"usecases/y.ve.md": b"Another.\n"}), None)],
               "pilot/a:usecases/x.ve.md"),
}


def test_every_corpus_has_its_source_inputs_tested():
    assert sorted(SOURCE_INPUTS) == sorted(diff.CORPORA)


@pytest.mark.parametrize("corpus", sorted(SOURCE_INPUTS))
def test_each_input_a_corpus_reads_changes_its_key(tmp_path, monkeypatch, corpus):
    """`sources` itself (the `world` fixture replaces it): every input a corpus's records read changes its digest,
    and the source digest of the case it belongs to; the files a pilot names beside it change the digest though
    no record carries theirs."""
    w = argparse.Namespace(root=tmp_path / "root", out=tmp_path / "ab/base.jsonl", checkout=tmp_path / "checkout")
    w.checkout.mkdir()
    monkeypatch.setattr(diff, "ROOT", w.checkout)
    write, edits, case = SOURCE_INPUTS[corpus]
    write(w)
    seen = [cache.sources(corpus, w.root, w.out)]
    assert seen[0][1](case) is not None
    for edit, changed in edits:
        before = seen[-1]
        edit(w)
        seen.append(cache.sources(corpus, w.root, w.out))
        assert seen[-1][0] != before[0], (corpus, changed)
        if changed is not None:
            assert seen[-1][1](changed) != before[1](changed)
        assert seen[-1][1](case) is not None
    assert len({digest for digest, _ in seen}) == len(seen)
