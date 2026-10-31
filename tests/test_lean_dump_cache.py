"""The Lean dump cache (`tools/lean_dump_cache.py`): a stored dump is replayed only while every input it is keyed on
is unchanged, and any doubt is a miss that runs the dump.

Each test but the last runs a counting stand-in for the Lean dump in a scratch git tree (a few Lean sources and a
copy of the repository's tools), with the cache under `tmp_path`; the last replays one real dump of this tree.
"""
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "lean"))
import audit  # noqa: E402
import cache_store  # noqa: E402
import lean_dump_cache as C  # noqa: E402
import lean_statements  # noqa: E402
import regen_generated  # noqa: E402

SOURCES = {"lean/VE.lean": "import VE.A\n", "lean/VE/A.lean": "theorem a : True := trivial\n",
           "lean/lean-toolchain": "leanprover/lean4:v4.24.0\n",
           "lean/lakefile.toml": 'name = "scratch"\ndefaultTargets = ["VE"]\n\n[[lean_lib]]\nname = "VE"\n',
           "lean/lake-manifest.json": '{"version": "1.1.0", "packages": []}\n'}


@pytest.fixture(autouse=True)
def hermetic(tmp_path, monkeypatch):
    """The cache and the source graph's parse cache under `tmp_path`."""
    monkeypatch.setenv("VE_RUN_CACHE", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))


class Dump:
    """A scratch tree and a stand-in for its Lean dump that counts its runs and returns texts naming the run."""

    def __init__(self, root: Path, step: str = C.STATEMENTS, count: int = 3):
        self.root, self.step, self.count, self.runs = root, step, count, 0
        self.files: tuple[str, ...] = ()
        self.values: dict[str, str] = {}

    def run(self) -> list[str]:
        self.runs += 1
        return [f"text {index} of run {self.runs}\n" for index in range(self.count)]

    def __call__(self, run=None) -> list[str]:
        return C.cached(self.step, self.root, lambda: lean_statements.sources(self.root), run or self.run, self.count,
                        files=self.files, values=self.values, code_root=self.root)

    def entries(self) -> list[Path]:
        return sorted((self.root.parent / "cache" / self.step).glob("*.json.gz"))


@pytest.fixture
def dump(tmp_path, monkeypatch) -> Dump:
    """The scratch tree, with an installed toolchain of its own (`ELAN_HOME`)."""
    toolchain = tmp_path / "elan/toolchains/leanprover--lean4---v4.24.0"
    for name in ("bin/lean", "bin/lake", "lib/lean/libleanshared.so"):
        (toolchain / name).parent.mkdir(parents=True, exist_ok=True)
        (toolchain / name).write_bytes(name.encode())
    monkeypatch.setenv("ELAN_HOME", str(tmp_path / "elan"))
    root = tmp_path / "tree"
    for name, text in SOURCES.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    (root / "tools").mkdir()
    for path in (ROOT / "tools").glob("*.py"):
        shutil.copy(path, root / "tools" / path.name)
    for name in ("lean/audit.py", "tests/subprocesses.py"):
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, root / name)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, timeout=HANG_TIMEOUT)
    return Dump(root)


def test_a_stored_dump_is_replayed_without_running(dump, capsys):
    first = dump()
    assert dump.runs == 1 and len(dump.entries()) == 1
    assert "from cache" not in capsys.readouterr().err
    assert dump() == first and dump.runs == 1
    key = dump.entries()[0].name.removesuffix(".json.gz")
    assert capsys.readouterr().err == f"lean-statements: from cache {key[:8]}\n"


def test_two_checkouts_of_one_tree_share_an_entry(dump, tmp_path):
    """Worktrees share the store: every keyed path is under the checkout, so another checkout of the same content
    at another path replays the first one's dump."""
    first = dump()
    other = tmp_path / "other"
    shutil.copytree(dump.root, other, ignore=shutil.ignore_patterns(".git"))
    subprocess.run(["git", "init", "-q"], cwd=other, check=True, timeout=HANG_TIMEOUT)
    copy = Dump(other)
    assert copy() == first and copy.runs == 0


def test_a_tree_whose_inputs_cannot_be_read_runs_the_dump(dump):
    """Not a git checkout: the code digest cannot be taken, so the dump runs and nothing is stored."""
    shutil.rmtree(dump.root / ".git")
    dump()
    dump()
    assert dump.runs == 2 and dump.entries() == []


def test_the_code_digest_follows_imports_to_the_helpers(dump):
    """The digest covers the two scripts and what their imports reach, transitively: the cache and its store, the
    source graph and the modules it imports."""
    files = C.code_files(dump.root)
    assert {"tools/lean_statements.py", "lean/audit.py", "tools/lean_dump_cache.py", "tools/cache_store.py",
            "tools/source_graph.py", "tools/layer_policy.py", "tests/subprocesses.py"} <= set(files)
    assert "tools/gate.py" not in files


def _edit(name, text=None):
    def change(dump, monkeypatch):
        path = dump.root / name
        path.write_text(path.read_text() + "\n-- edited\n" if text is None else text)
    return change


CHANGES = {
    "a Lean source edited": _edit("lean/VE/A.lean"),
    "a Lean source added": _edit("lean/VE/B.lean", "theorem b : True := trivial\n"),
    "a Lean source removed": lambda dump, monkeypatch: (dump.root / "lean/VE/A.lean").unlink(),
    "a Lean source renamed": lambda dump, monkeypatch: (dump.root / "lean/VE/A.lean").rename(
        dump.root / "lean/VE/Z.lean"),
    "the toolchain": _edit("lean/lean-toolchain", "leanprover/lean4:v4.25.0\n"),
    "the installed toolchain's library": lambda dump, monkeypatch: (
        dump.root.parent / "elan/toolchains/leanprover--lean4---v4.24.0/lib/lean/libleanshared.so").write_bytes(b"x"),
    "the installed toolchain's lean": lambda dump, monkeypatch: (
        dump.root.parent / "elan/toolchains/leanprover--lean4---v4.24.0/bin/lean").unlink(),
    "the lakefile": _edit("lean/lakefile.toml", SOURCES["lean/lakefile.toml"] + "\n# edited\n"),
    "a lakefile.lean added": _edit("lean/lakefile.lean", "import Lake\n"),
    "the Lake manifest": _edit("lean/lake-manifest.json", '{"version": "1.1.0", "packages": [], "name": "x"}\n'),
    "tools/lean_statements.py": _edit("tools/lean_statements.py", None),
    "lean/audit.py": _edit("lean/audit.py", None),
    "the cache's store": _edit("tools/cache_store.py", None),
    "a module imported through another": _edit("tools/layer_policy.py", None),
    "the format": lambda dump, monkeypatch: monkeypatch.setattr(C, "FORMAT", C.FORMAT + "-next"),
    "a Lean setting of the environment": lambda dump, monkeypatch: monkeypatch.setenv("LEAN_PATH", "/x"),
    "the lake program": lambda dump, monkeypatch: monkeypatch.setattr(C.shutil, "which", lambda _: None),
    "the platform": lambda dump, monkeypatch: monkeypatch.setattr(C.platform, "platform", lambda: "other"),
    "the step": lambda dump, monkeypatch: setattr(dump, "step", C.AUDIT),
    "a caller's file": lambda dump, monkeypatch: (dump.root / "lean/declarations.txt").write_text("x\n"),
    "a caller's value": lambda dump, monkeypatch: dump.values.update(texts="other"),
}


@pytest.mark.parametrize("change", CHANGES)
def test_each_keyed_input_changed_is_a_miss(dump, monkeypatch, change):
    if change in ("a caller's file", "a caller's value"):
        dump.files, dump.values = ("lean/declarations.txt",), {"texts": "digest"}
    first = dump()
    assert dump() == first and dump.runs == 1
    CHANGES[change](dump, monkeypatch)
    second = dump()
    assert dump.runs == 2 and second != first, change
    assert dump() == second and dump.runs == 2, "the changed inputs' dump is stored and replayed"


def _rewrite(dump, change):
    [path] = dump.entries()
    entry = cache_store.load(path)
    change(entry)
    with gzip.open(path, "wt") as handle:
        json.dump(entry, handle)


CORRUPTIONS = {
    "not gzip": lambda dump, path: path.write_bytes(b"not an entry"),
    "truncated": lambda dump, path: path.write_bytes(path.read_bytes()[:len(path.read_bytes()) // 2]),
    "empty": lambda dump, path: path.write_bytes(b""),
    "a JSON list": lambda dump, path: path.write_bytes(gzip.compress(b"[1, 2, 3]")),
    "not JSON": lambda dump, path: path.write_bytes(gzip.compress(b"{ not json")),
    "a directory": lambda dump, path: (path.unlink(), path.mkdir()),
    "outputs missing": lambda dump, path: _rewrite(dump, lambda entry: entry.pop("outputs")),
    "outputs not a list": lambda dump, path: _rewrite(dump, lambda entry: entry.update(outputs="text")),
    "an output not text": lambda dump, path: _rewrite(dump, lambda entry: entry["outputs"].__setitem__(1, 7)),
    "an output short": lambda dump, path: _rewrite(dump, lambda entry: entry["outputs"].pop()),
    "an output extra": lambda dump, path: _rewrite(dump, lambda entry: entry["outputs"].append("x")),
    "another format": lambda dump, path: _rewrite(dump, lambda entry: entry.update(format="ve-lean-dump-cache@0")),
    "another step": lambda dump, path: _rewrite(dump, lambda entry: entry.update(step=C.AUDIT)),
    "another key": lambda dump, path: _rewrite(dump, lambda entry: entry.update(key="0" * 64)),
    "inputs missing": lambda dump, path: _rewrite(dump, lambda entry: entry.pop("inputs")),
}


@pytest.mark.parametrize("corruption", CORRUPTIONS)
def test_a_corrupt_entry_is_a_miss_and_the_dump_runs(dump, corruption):
    dump()
    [path] = dump.entries() or [None]
    CORRUPTIONS[corruption](dump, path)
    again = dump()
    assert dump.runs == 2 and again == [f"text {index} of run 2\n" for index in range(3)], corruption
    if corruption != "a directory":  # a directory cannot be replaced by a file: no entry, and no error
        assert dump() == again and dump.runs == 2, "the miss stores a valid entry"


RECORDED = {
    "a Lean source's digest": "lean:lean/VE/A.lean",
    "the toolchain's digest": "file:lean/lean-toolchain",
    "a code file's digest": "code:tools/cache_store.py",
    "the platform": "platform",
}


@pytest.mark.parametrize("recorded", RECORDED)
def test_an_entry_whose_recorded_inputs_are_not_the_current_ones_is_a_miss(dump, recorded):
    """The entry is named by its key, but its recorded inputs are what is checked on lookup: one recorded digest
    changed, or one recorded input removed or added, is not used."""
    dump()
    _rewrite(dump, lambda entry: entry["inputs"].__setitem__(RECORDED[recorded], "0" * 64))
    dump()
    assert dump.runs == 2
    _rewrite(dump, lambda entry: entry["inputs"].pop(RECORDED[recorded]))
    dump()
    assert dump.runs == 3
    _rewrite(dump, lambda entry: entry["inputs"].__setitem__("lean:lean/VE/Extra.lean", "0" * 64))
    dump()
    assert dump.runs == 4


def test_off_never_reads_or_writes(dump, monkeypatch):
    dump()
    monkeypatch.setenv("VE_RUN_CACHE", "off")

    def refuse(*_args, **_kwargs):
        raise AssertionError("the cache was used while off")
    for name in ("load", "store", "touch", "entry_path"):
        monkeypatch.setattr(cache_store, name, refuse)
    monkeypatch.setattr(C, "inputs", refuse)
    assert dump() == [f"text {index} of run 2\n" for index in range(3)]
    assert dump() == [f"text {index} of run 3\n" for index in range(3)]
    assert dump.runs == 3


def test_the_cache_directory(monkeypatch):
    """`VE_RUN_CACHE` unset: the git common directory's, in a subdirectory per step; `off`: none."""
    monkeypatch.delenv("VE_RUN_CACHE")
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=ROOT,
                            capture_output=True, text=True, check=True, timeout=HANG_TIMEOUT).stdout.strip()
    assert cache_store.directory(ROOT, C.STATEMENTS) == Path(common) / "ve-run-cache" / C.STATEMENTS
    monkeypatch.setenv("VE_RUN_CACHE", "off")
    assert cache_store.directory(ROOT, C.STATEMENTS) is None


def test_a_dump_that_fails_or_whose_inputs_change_while_it_runs_is_not_stored(dump):
    def failing():
        raise SystemExit("lake env lean failed")
    with pytest.raises(SystemExit):
        dump(failing)
    assert dump.entries() == []

    def editing():
        (dump.root / "lean/VE/A.lean").write_text("theorem a' : True := trivial\n")
        return dump.run()
    dump(editing)
    assert dump.entries() == []
    dump()
    assert dump.runs == 2 and len(dump.entries()) == 1


@pytest.mark.parametrize("source", ["#eval (1 : Nat)\n", "def x : String := include_str \"data.txt\"\n",
                                    "run_cmd pure ()\n", "initialize counter : IO.Ref Nat ← IO.mkRef 0\n",
                                    "elab \"probe\" : term => do\n  let _ ← IO.FS.readFile \"x\"\n  return .const ``Nat []\n"])
def test_a_tree_that_runs_code_while_it_elaborates_is_never_cached(dump, capsys, source):
    """Such code could read a file the key does not name; in a comment or a string it is no code."""
    (dump.root / "lean/VE/B.lean").write_text(source)
    dump()
    dump()
    assert dump.runs == 2 and dump.entries() == []
    assert "lean-statements: not cached: lean/VE/B.lean runs code while it elaborates" in capsys.readouterr().err
    (dump.root / "lean/VE/B.lean").write_text("/- " + source.replace("-/", "") + " -/\n-- #eval 1\n"
                                              "def s : String := \"#eval include_str\"\n")
    dump()
    dump()
    assert dump.runs == 3 and len(dump.entries()) == 1


def test_the_real_tree_runs_no_code_while_it_elaborates():
    assert C.evaluates(ROOT, lean_statements.sources(ROOT)) is None


def test_two_concurrent_stores_of_one_key_leave_one_valid_entry(tmp_path, monkeypatch):
    """Both writers have written their whole entry before either renames it into place."""
    barrier = threading.Barrier(2, timeout=HANG_TIMEOUT)
    opened = cache_store.gzip.open

    class Held:
        def __init__(self, handle):
            self.handle = handle

        def __enter__(self):
            return self.handle.__enter__()

        def __exit__(self, *exc):
            self.handle.__exit__(*exc)
            barrier.wait()
            return False

    monkeypatch.setattr(cache_store.gzip, "open", lambda *args, **kwargs: Held(opened(*args, **kwargs)))
    path = cache_store.entry_path(tmp_path / "store", "k" * 64)
    errors = []

    def write(index):
        try:
            cache_store.store(path, {"writer": index, "outputs": ["x" * 100_000]}, C.KEEP)
        except Exception as error:  # noqa: BLE001 - reported below
            errors.append(error)
    threads = [threading.Thread(target=write, args=(index,)) for index in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(HANG_TIMEOUT)
    assert errors == []
    assert sorted(os.listdir(path.parent)) == [path.name]
    monkeypatch.setattr(cache_store.gzip, "open", opened)
    assert cache_store.load(path)["writer"] in (0, 1)


def test_the_store_keeps_the_newest_entries(tmp_path):
    folder = tmp_path / "store"
    for index in range(C.KEEP + 3):
        path = cache_store.entry_path(folder, f"{index:064d}")
        cache_store.store(path, {"index": index}, C.KEEP)
        os.utime(path, (1_000_000 + index, 1_000_000 + index))
    kept = sorted(cache_store.load(path)["index"] for path in folder.glob("*.json.gz"))
    assert kept == list(range(3, C.KEEP + 3))


def test_the_steps_are_the_regeneration_entries():
    """The line a replay prints names the entry of tools/regen_generated.py that the step serves."""
    assert regen_generated.owner("lean/statements.txt").name == C.STATEMENTS
    assert regen_generated.owner("lean/axioms.txt").name == C.AUDIT
    assert regen_generated.owner("lean/statements.txt").check == ((regen_generated.PY, "tools/lean_statements.py",
                                                                   "--check"),)


def test_the_command_lines_use_the_cache(monkeypatch, capsys):
    """`tools/lean_statements.py`'s command line asks for the cache (its one dump serves `--check` and the write);
    `dump_all` called without it, as the tests of fixture trees call it, does not."""
    asked = []

    def dump_all(root=lean_statements.ROOT, cache=False):
        asked.append(cache)
        return tuple(lean_statements.inventory_path(name).read_text() for name in (
            lean_statements.STATEMENTS, lean_statements.PREDICATES, lean_statements.DECLARATIONS))
    monkeypatch.setattr(lean_statements, "dump_all", dump_all)
    assert lean_statements.main(["--check"]) == 0 and asked == [True]
    assert "PASS:" in capsys.readouterr().out


def test_only_the_explicit_audit_modes_are_cached():
    """The plain `lean/audit.py`, the gate's lean_audit stage, always runs Lean."""
    assert audit.cached_mode([]) is False
    assert audit.cached_mode(["--check"]) is True and audit.cached_mode(["--write"]) is True


@pytest.fixture
def audit_tree(tmp_path, monkeypatch):
    """The audit pointed at a copy of this tree's Lean sources and lists, with the committed record as Lean's
    output (`axiom_outputs` counted), and the code digest of the two scripts alone (the digest is tested above)."""
    lean = tmp_path / "lean"
    shutil.copytree(ROOT / "lean", lean, ignore=shutil.ignore_patterns(".lake", "__pycache__"))
    monkeypatch.setattr(audit, "ROOT", lean)
    monkeypatch.setattr(C, "code_files", lambda code_root: list(C.CODE_STARTS))
    record, runs = lean_statements.inventory_path("lean/axioms.txt").read_text(), []

    def outputs(imports, texts, jobs=None):
        runs.append(len(texts))
        return [record] + [""] * (len(texts) - 1)
    monkeypatch.setattr(audit, "axiom_outputs", outputs)
    return lean, runs


def test_the_audit_replays_lean_output_and_checks_it_as_fresh(audit_tree, capsys):
    lean, runs = audit_tree
    audit.main(["--check"], cache=True)
    cold = capsys.readouterr()
    audit.main(["--check"], cache=True)
    warm = capsys.readouterr()
    assert len(runs) == 1 and warm.out == cold.out and "PASS:" in warm.out
    assert warm.err.startswith("lean-audit-manifests: from cache ") and "from cache" not in cold.err
    before = {name: (lean / name).read_bytes() for name in (*audit.MANIFESTS, "axioms.txt")}
    audit.main(["--write"], cache=True)
    assert len(runs) == 1 and {name: (lean / name).read_bytes() for name in before} == before
    audit.main(["--check"])
    assert len(runs) == 2, "without the cache the audit runs Lean"
    # The replayed output goes through the same checks: a record that no longer matches it fails.
    (lean / "axioms.txt").write_text(before["axioms.txt"].decode()[:-200])
    with pytest.raises(AssertionError, match="axioms.txt is stale"):
        audit.main(["--check"], cache=True)
    assert len(runs) == 2
    # The declaration list is keyed: a changed one is a miss.
    declarations = lean / "declarations.txt"
    declarations.write_text(declarations.read_text() + "\n")
    audit.main(["--write"], cache=True)
    assert len(runs) == 3


def test_a_replayed_dump_is_the_cold_dump_of_the_real_tree(capsys):
    """One real cold and warm pair: the replay is byte for byte what Lean dumped."""
    if shutil.which("lake") is None:
        pytest.skip("lake is not on PATH")
    cold = lean_statements.dump_all(cache=True)
    assert "from cache" not in capsys.readouterr().err
    warm = lean_statements.dump_all(cache=True)
    assert "lean-statements: from cache " in capsys.readouterr().err
    assert [text.encode() for text in warm] == [text.encode() for text in cold]
