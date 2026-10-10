"""The gate's collection is the merge base's, less exactly the tests the diff deletes or re-parametrises
(tools/gate_collection.py), and the collection itself applies the gate's discovery rules to the tree as it
is now."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from tools import gate, gate_collection, nested_pytest


def git(repository, *args):
    return subprocess.run(["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid",
                           "-c", "commit.gpgsign=false", *args], cwd=repository, check=True, capture_output=True,
                          text=True, timeout=HANG_TIMEOUT).stdout.strip()


@pytest.fixture
def repository(tmp_path):
    (tmp_path / "pytest.ini").write_text("[pytest]\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_one.py").write_text("def test_kept(): pass\ndef test_dropped(): pass\n")
    return tmp_path


def commit(repository, files: dict[str, str | None], message="change") -> str:
    """Write (or, for None, delete) `files` and commit the whole tree."""
    for name, text in files.items():
        path = repository / name
        if text is None:
            path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    git(repository, "add", "-A")
    git(repository, "commit", "-q", "--allow-empty", "-m", message)
    return git(repository, "rev-parse", "HEAD")


CASES = "['a', 'b', 'c']"
MODULE = f"""import json, pathlib, pytest
from cases import IMPORTED

CASES = {CASES}
FROM_DATA = json.loads(pathlib.Path(__file__).with_name('cases.json').read_text())


def test_plain():
    pass


@pytest.mark.parametrize('case', {CASES})
def test_literal(case):
    pass


@pytest.mark.parametrize('case', CASES)
def test_named(case):
    pass


@pytest.mark.parametrize('case', FROM_DATA)
def test_data(case):
    pass


@pytest.mark.parametrize('case', IMPORTED)
def test_imported(case):
    pass


class TestGroup:
    def test_member(self):
        pass
"""
BASE = {"pytest.ini": "[pytest]\n", "tests/test_mod.py": MODULE, "tests/cases.py": f"IMPORTED = {CASES}\n",
        "tests/cases.json": '["a", "b", "c"]', "tests/test_other.py": "def test_other():\n    pass\n"}


@pytest.fixture
def history(tmp_path):
    """A repository whose first commit is BASE."""
    repository = tmp_path / "repository"
    repository.mkdir()
    git(repository, "init", "-q", "-b", "main")
    commit(repository, BASE, "base")
    return repository


def compare(repository, base, head):
    """(explained, refused) for the head's collection against the base's, each collected at its commit."""
    sides = []
    for sha in (base, head):
        git(repository, "checkout", "-q", "--detach", sha)
        sides.append(gate_collection.collect(repository))
    return gate_collection.missing(sides[0], sides[1], gate_collection.changes(base, head, root=repository))


# Each drops tests; the diff explains exactly those whose file or function it deletes or whose
# parametrisation in the test module it changes.
DROPS = {
    "deleted test file": ({"tests/test_other.py": None}, {"tests/test_other.py::test_other": "its file is deleted"}),
    "deleted test function": ({"tests/test_mod.py": MODULE.replace("def test_plain():\n    pass\n", "")},
                              {"tests/test_mod.py::test_plain": "its test function test_plain is deleted"}),
    "deleted class": ({"tests/test_mod.py": MODULE.split("class TestGroup")[0]},
                      {"tests/test_mod.py::TestGroup::test_member": "its class TestGroup is deleted"}),
    "renamed test file": ({"tests/test_other.py": None, "tests/test_renamed.py": BASE["tests/test_other.py"]},
                          {"tests/test_other.py::test_other": "its file is deleted"}),
    "shrunk literal list": ({"tests/test_mod.py": MODULE.replace(f"'case', {CASES}", "'case', ['a', 'b']")},
                            {"tests/test_mod.py::test_literal[c]": "the parametrisation of test_literal changed"}),
    "shrunk module list": ({"tests/test_mod.py": MODULE.replace(f"CASES = {CASES}", "CASES = ['a', 'b']")},
                           {"tests/test_mod.py::test_named[c]": "the parametrisation of test_named changed"}),
}


@pytest.mark.parametrize("files, expected", DROPS.values(), ids=DROPS)
def test_the_diff_explains_a_deleted_or_reparametrised_test(history, files, expected):
    base = git(history, "rev-parse", "HEAD")
    head = commit(history, files)
    explained, refused = compare(history, base, head)
    assert (explained, refused) == (expected, [])


# Each drops tests the diff does not delete or re-parametrise in their module: the gate fails on them. (A
# conftest hook that removes collected items is the selection check's: tests/test_gate_integrity.py.)
REFUSED = {
    "parameters from a data file": ({"tests/cases.json": '["a", "b"]'}, ["tests/test_mod.py::test_data[c]"]),
    "parameters from an imported module": ({"tests/cases.py": "IMPORTED = ['a', 'b']\n"},
                                           ["tests/test_mod.py::test_imported[c]"]),
    "conftest ignores a module": ({"tests/conftest.py": "collect_ignore = ['test_other.py']\n"},
                                  ["tests/test_other.py::test_other"]),
}


@pytest.mark.parametrize("files, expected", REFUSED.values(), ids=REFUSED)
def test_a_test_dropped_without_its_change_is_refused(history, files, expected):
    base = git(history, "rev-parse", "HEAD")
    head = commit(history, files)
    explained, refused = compare(history, base, head)
    assert (explained, refused) == ({}, expected)


@pytest.mark.parametrize("body", [
    "import pytest\npytest.skip('backend unavailable', allow_module_level=True)\n",
    "import ve_gate_absent_test_backend\n",
], ids=["module skip", "import error"])
def test_a_module_dropped_at_collection_fails_twice(history, body):
    # A collection report fails the collection; its IDs are refused as well, since its
    # test function and parametrisation are unchanged.
    base = git(history, "rev-parse", "HEAD")
    head = commit(history, {"tests/test_other.py": body + BASE["tests/test_other.py"]})
    with pytest.raises(gate_collection.CollectionError, match="tests/test_other.py"):
        gate_collection.collect(history)
    git(history, "checkout", "-q", "--detach", base)
    expected = gate_collection.collect(history)
    diff = gate_collection.changes(base, head, root=history)
    collected = [nodeid for nodeid in expected if not nodeid.startswith("tests/test_other.py")]
    assert gate_collection.missing(expected, collected, diff) == ({}, ["tests/test_other.py::test_other"])


def test_an_added_test_passes_and_an_unchanged_file_explains_nothing(history):
    base = git(history, "rev-parse", "HEAD")
    head = commit(history, {"tests/test_new.py": "def test_new(): pass\n"})
    explained, refused = compare(history, base, head)
    assert (explained, refused) == ({}, [])
    diff = gate_collection.changes(base, head, root=history)
    assert diff.reason("tests/test_other.py::test_other") is None
    assert diff.statuses == {"tests/test_new.py": "A"}


def test_the_worktree_side_reads_the_files_not_the_commit(history):
    base = git(history, "rev-parse", "HEAD")
    (history / "tests/test_other.py").write_text("def test_else(): pass\n")
    diff = gate_collection.changes(base, None, root=history)
    assert diff.reason("tests/test_other.py::test_other") == "its test function test_other is deleted"


PARAMETRISATION = {
    "decorator": ("@pytest.mark.parametrize('x', [1, 2])\ndef test_f(x): pass\n",
                  "@pytest.mark.parametrize('x', [1])\ndef test_f(x): pass\n", True),
    "referenced name, transitively": ("A = [1, 2]\nB = A\n@pytest.mark.parametrize('x', B)\ndef test_f(x): pass\n",
                                      "A = [1]\nB = A\n@pytest.mark.parametrize('x', B)\ndef test_f(x): pass\n", True),
    "fixture params": ("@pytest.fixture(params=[1, 2])\ndef x(request): return request.param\ndef test_f(x): pass\n",
                       "@pytest.fixture(params=[1])\ndef x(request): return request.param\ndef test_f(x): pass\n",
                       True),
    "pytest_generate_tests": ("def pytest_generate_tests(m): m.parametrize('x', [1, 2])\ndef test_f(x): pass\n",
                              "def pytest_generate_tests(m): m.parametrize('x', [1])\ndef test_f(x): pass\n", True),
    "class decorator": ("@pytest.mark.parametrize('x', [1, 2])\nclass TestC:\n    def test_f(self, x): pass\n",
                        "@pytest.mark.parametrize('x', [1])\nclass TestC:\n    def test_f(self, x): pass\n", True),
    "body only": ("def test_f(): assert 1\n", "def test_f(): assert 2\n", False),
    "unrelated name": ("A = [1, 2]\nB = 3\n@pytest.mark.parametrize('x', A)\ndef test_f(x): pass\n",
                       "A = [1, 2]\nB = 4\n@pytest.mark.parametrize('x', A)\ndef test_f(x): pass\n", False),
    "line numbers only": ("A = [1, 2]\n@pytest.mark.parametrize('x', A)\ndef test_f(x): pass\n",
                          "\n\nA = [1, 2]\n\n@pytest.mark.parametrize('x', A)\ndef test_f(x): pass\n", False),
}


@pytest.mark.parametrize("before, after, changed", PARAMETRISATION.values(), ids=PARAMETRISATION)
def test_what_counts_as_the_parametrisation(before, after, changed):
    import ast
    sides = []
    for text in (before, after):
        module = ast.parse("import pytest\n" + text)
        names = ["TestC", "test_f"] if "class TestC" in text else ["test_f"]
        sides.append(gate_collection.parametrisation(module, gate_collection._locate(module, names)))
    assert (sides[0] != sides[1]) is changed


# --- the record ---------------------------------------------------------------------------------------------

def test_a_record_round_trips_and_binds_its_commit_and_tree(history):
    first = git(history, "rev-parse", "HEAD")
    ids = ["tests/b.py::test_b", "tests/a.py::test_a"]
    assert gate_collection.read_record(first, cwd=history) is None
    gate_collection.write_record(first, ids, cwd=history)
    assert gate_collection.read_record(first, cwd=history) == sorted(ids)
    second = commit(history, {"tests/test_new.py": "def test_new(): pass\n"})
    # Another commit has no record; one with the same tree uses its parent's.
    assert gate_collection.read_record(second, cwd=history) is None
    assert gate_collection.recorded(second, cwd=history) is None
    git(history, "checkout", "-q", "-b", "side", first)
    merge = commit(history, {}, "a commit with its parent's tree")
    assert gate_collection.recorded(merge, cwd=history) == (first, sorted(ids))
    # A note copied to another commit names the wrong commit and tree.
    text = gate_collection.record_text(first, git(history, "rev-parse", f"{first}^{{tree}}"), ids)
    subprocess.run(["git", "notes", f"--ref={gate_collection.NOTES_REF}", "add", "-f", "-m", text, second],
                   cwd=history, check=True, capture_output=True, timeout=HANG_TIMEOUT,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"})
    assert gate_collection.read_record(second, cwd=history) is None


GOOD = {"format": gate_collection.FORMAT, "commit_sha": "c" * 40, "tree_sha": "t" * 40,
        "collected": ["tests/a.py::test_a", "tests/b.py::test_b"]}
# Each field retyped or rebound: the record is ignored and the base collected again.
BAD = {
    "format retyped": {"format": 1}, "format other": {"format": "ve-gate-collection@2"},
    "commit other": {"commit_sha": "d" * 40}, "commit retyped": {"commit_sha": None},
    "tree other": {"tree_sha": "u" * 40}, "tree retyped": {"tree_sha": ["t" * 40]},
    "collected empty": {"collected": []}, "collected retyped": {"collected": "tests/a.py::test_a"},
    "collected unsorted": {"collected": ["tests/b.py::test_b", "tests/a.py::test_a"]},
    "collected duplicated": {"collected": ["tests/a.py::test_a", "tests/a.py::test_a"]},
    "id retyped": {"collected": [True, "tests/a.py::test_a"]}, "id number": {"collected": [7]},
    "id null": {"collected": [None]}, "id object": {"collected": [{}]},
    "extra field": {"extra": 1}, "missing field": {"collected": None},
}


@pytest.mark.parametrize("change", BAD.values(), ids=BAD)
def test_a_record_retyped_or_rebound_is_ignored(change):
    record = {**GOOD, **change}
    if change == {"collected": None}:
        del record["collected"]
    assert gate_collection.parse_record(json.dumps(GOOD), "c" * 40, "t" * 40) == GOOD["collected"]
    assert gate_collection.parse_record(json.dumps(record), "c" * 40, "t" * 40) is None


@pytest.mark.parametrize("text", ["", "{", "[]", "null", "7", '"x"'])
def test_a_record_that_is_not_an_object_is_ignored(text):
    assert gate_collection.parse_record(text, "c" * 40, "t" * 40) is None


def test_the_merge_base_is_the_fork_point_or_on_main_the_first_parent(history):
    fork = git(history, "rev-parse", "HEAD")
    git(history, "checkout", "-q", "-b", "topic")
    commit(history, {"tests/test_topic.py": "def test_topic(): pass\n"})
    git(history, "checkout", "-q", "main")
    later = commit(history, {"tests/test_main.py": "def test_main(): pass\n"})
    assert gate_collection.merge_base("topic", cwd=history) == fork
    assert gate_collection.merge_base("main", cwd=history) == fork
    assert later != fork


def test_the_base_is_collected_in_a_scratch_worktree_and_the_worktree_removed(history, tmp_path):
    base = git(history, "rev-parse", "HEAD")
    commit(history, {"tests/test_other.py": None})
    ids = gate_collection.collect_commit(base, tmp_path / "scratch", build_env=dict(os.environ),
                                         env={name: os.environ[name] for name in gate_collection.INHERITED
                                              if name in os.environ}, python=[sys.executable], root=history)
    assert "tests/test_other.py::test_other" in ids
    assert "tests/test_other.py::test_other" not in gate_collection.collect(history)
    assert len(git(history, "worktree", "list").splitlines()) == 1
    assert not (tmp_path / "scratch/base-worktree").exists()


def test_the_base_collection_refuses_another_toolchain(history, tmp_path):
    base = commit(history, {"rust-toolchain.toml": "[toolchain]\nchannel = '1.0.0'\n"})
    commit(history, {"rust-toolchain.toml": "[toolchain]\nchannel = '2.0.0'\n"})
    with pytest.raises(gate_collection.CollectionError, match="rust-toolchain.toml"):
        gate_collection.collect_commit(base, tmp_path / "scratch", build_env=dict(os.environ), env=dict(os.environ),
                                       python=[sys.executable], root=history)
    assert len(git(history, "worktree", "list").splitlines()) == 1


def rust_trees(tmp_path, pinned: bool):
    root, tree = tmp_path / "root", tmp_path / "tree"
    (root / gate_collection.RUST_BINARY).parent.mkdir(parents=True)
    (root / gate_collection.RUST_BINARY).write_bytes(b"head build")
    (tree / "lean").mkdir(parents=True)
    pin = hashlib.sha256(b"head build" if pinned else b"base build").hexdigest()
    (tree / "lean/checkers.lock").write_text(json.dumps({"rust_jsonl": [pin]}))
    return root, tree


def test_the_base_takes_the_heads_rust_binary_when_its_lock_pins_it(tmp_path, monkeypatch):
    root, tree = rust_trees(tmp_path, pinned=True)
    monkeypatch.setattr(gate_collection, "build", lambda *a, **kw: pytest.fail("built"))
    gate_collection.build_rust(tree, root, {})
    assert (tree / gate_collection.RUST_BINARY).read_bytes() == b"head build"


def test_the_base_builds_its_own_rust_binary_otherwise(tmp_path, monkeypatch):
    root, tree = rust_trees(tmp_path, pinned=False)
    builds = []
    monkeypatch.setattr(gate_collection, "build", lambda args, **kw: builds.append((args, kw)))
    gate_collection.build_rust(tree, root, {"CARGO_HOME": str(tmp_path / "cargo-home")})
    [(args, kw)] = builds
    assert args[:2] == ["cargo", "build"] and "--locked" in args and "--release" in args
    assert args[args.index("--manifest-path") + 1] == str(tree / "rust/Cargo.toml")
    assert args[args.index("--target-dir") + 1] == str(tree / "rust/target")
    # Offline, from the gate's registry, with the tree's paths remapped as every pinned build's are.
    assert kw["env"]["CARGO_NET_OFFLINE"] == "true" and kw["env"]["CARGO_HOME"] == str(tmp_path / "cargo-home")
    assert f"--remap-path-prefix={tree.resolve()}=/ve" in kw["env"]["CARGO_ENCODED_RUSTFLAGS"].split("\x1f")


# --- the gate ------------------------------------------------------------------------------------------------

def gate_events(collected):
    return {"collected": collected, "selected": collected, "deselected": [], "collection_reports": [],
            "tests": {nodeid: {"outcome": "passed"} for nodeid in collected}}


def test_the_gate_fails_on_every_unexplained_missing_id_and_lists_the_explained():
    base = ["tests/a.py::test_a", "tests/b.py::test_old", "tests/c.py::test_gone"]
    collected = ["tests/a.py::test_a", "tests/d.py::test_new"]
    reasons = {"tests/c.py::test_gone": "its file is deleted"}
    result = {"counts": {}, "failures": [], "skips": []}
    gate.interpret_pytest(result, gate_events(collected), {"optional_tests": [], "deselected_tests": []}, base,
                          families=(), explain=reasons.get, base="b" * 40)
    assert result["failures"] == [{"stage": "coverage",
                                   "reason": gate_collection.difference_text("b" * 40, ["tests/b.py::test_old"])}]
    assert result["collection"] == {"head_ids": 2, "added": 1, "removed": reasons,
                                    "refused": ["tests/b.py::test_old"]}
    text = result["failures"][0]["reason"]
    assert text.splitlines()[1:-1] == ["  tests/b.py::test_old"] and "b" * 40 in text


def test_without_an_explanation_every_missing_id_fails():
    result = {"counts": {}, "failures": [], "skips": []}
    gate.interpret_pytest(result, gate_events(["tests/x.py::test_x"]), {"optional_tests": [], "deselected_tests": []},
                          ["tests/a.py::test_a", "tests/x.py::test_x"], families=())
    assert [failure["stage"] for failure in result["failures"]] == ["coverage"]
    assert result["collection"]["refused"] == ["tests/a.py::test_a"]


class FakeRepository:
    """gate_collection's git-facing functions answered here: `records` holds the notes."""

    def __init__(self, monkeypatch, records):
        self.records, self.collected, self.written = records, [], []
        monkeypatch.setattr(gate_collection, "rev", lambda name, **kw: name.split("^")[0])
        monkeypatch.setattr(gate_collection, "merge_base", lambda **kw: "base")
        monkeypatch.setattr(gate_collection, "recorded", lambda commit, **kw: (
            (commit, self.records[commit]) if commit in self.records else None))
        monkeypatch.setattr(gate_collection, "collect_commit", self.collect_commit)
        monkeypatch.setattr(gate_collection, "write_record", lambda commit, ids, **kw: self.written.append(
            (commit, ids)))
        monkeypatch.setattr(gate_collection, "changes", lambda base, head, **kw: gate_collection.Changes(
            base, head, {}))

    def collect_commit(self, commit, scratch, **kw):
        self.collected.append((commit, kw["python"]))
        return ["tests/a.py::test_a"]


def test_the_gate_takes_the_base_record_and_collects_only_without_one(monkeypatch, tmp_path):
    repository = FakeRepository(monkeypatch, {"base": ["tests/r.py::test_r"]})
    result = {}
    ids, explain = gate.base_collection(result, None, {}, {}, tmp_path)
    assert (ids, repository.collected, repository.written) == (["tests/r.py::test_r"], [], [])
    assert result["collection"] == {"base": "base", "base_source": "record of base", "base_ids": 1}
    assert explain("tests/r.py::test_r") is None
    ids, _ = gate.base_collection(result, "other", {}, {}, tmp_path)
    assert ids == ["tests/a.py::test_a"]
    assert repository.collected == [("other", [str(gate.ROOT / ".venv/bin/python")])]
    # Recorded, so the next gate on that base reads it.
    assert repository.written == [("other", ["tests/a.py::test_a"])]
    assert result["collection"]["base_source"] == "collected" and result["collection"]["base_record"] == "written"
    assert type(result["collection"]["base_seconds"]) is float


def test_a_record_that_cannot_be_written_does_not_fail_the_gate(monkeypatch):
    def refuse(commit, ids, **kw):
        raise RuntimeError("cannot lock ref")
    monkeypatch.setattr(gate_collection, "write_record", refuse)
    assert gate.record_collection("c", ["tests/a.py::test_a"], {}) == "not written: cannot lock ref"


def test_no_committed_baseline_or_writer_remains():
    assert not (gate.ROOT / "tools/gate-collection.json").exists()
    assert not hasattr(gate, "COLLECTION") and not hasattr(gate_collection, "write")
    assert "--write-collection" not in (gate.ROOT / "tools/gate.py").read_text()


# --- the collection itself ----------------------------------------------------------------------------------

# Each changes which IDs the gate collects only through pytest's discovery
# rules, which the collection must apply exactly as the gate's own run does: with
# the rule the file is (or is not) collected, and without it the reverse.
DISCOVERY = {
    "python_files": ({"pytest.ini": "[pytest]\npython_files = check_*.py\n"},
                     "tests/check_three.py", True),
    "collect_ignore": ({"tests/conftest.py": "collect_ignore = ['test_three.py']\n"},
                       "tests/test_three.py", False),
    "norecursedirs": ({"pytest.ini": "[pytest]\nnorecursedirs = skipped\n"},
                      "tests/skipped/test_three.py", False),
}


@pytest.mark.parametrize("rules,path,collected", DISCOVERY.values(), ids=DISCOVERY)
def test_collection_applies_the_gates_discovery_rules(repository, rules, path, collected):
    (repository / path).parent.mkdir(parents=True, exist_ok=True)
    (repository / path).write_text("def test_hidden(): pass\n")
    for name, text in rules.items():
        (repository / name).write_text(text)
    assert (f"{path}::test_hidden" in gate_collection.collect(repository)) == collected
    (repository / "pytest.ini").write_text("[pytest]\n")
    (repository / "tests/conftest.py").unlink(missing_ok=True)
    assert (f"{path}::test_hidden" in gate_collection.collect(repository)) != collected


GENERATED = ("import pathlib, pytest\nGENERATED = pathlib.Path(__file__).with_name('generated.txt')\n"
             "GENERATED.write_text('{case}')\n"
             "@pytest.mark.parametrize('case', [GENERATED.read_text()])\n"
             "def test_generated(case): pass\n")
IMPORTING = ("import pytest\nfrom ve_gate_generated_case import CASE\n"
             "@pytest.mark.parametrize('case', [CASE])\ndef test_generated(case): pass\n")
# The changed source of a parameter: the test module, whose bytecode pytest
# rewrites and caches, or a module it imports, whose bytecode Python caches.
SOURCES = {
    "test module": ({}, "tests/test_two.py", GENERATED),
    "imported module": ({"tests/test_two.py": IMPORTING}, "tests/ve_gate_generated_case.py",
                        "CASE = '{case}'\n"),
}
# Where the bytecode cached for the earlier source came from.
EARLIER = ("an earlier collection", "an ordinary pytest run")


def ordinary_pytest_run(repository):
    env = {name: value for name, value in os.environ.items()
           if name not in ("PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")}
    subprocess.run(nested_pytest.command(["-p", "no:cacheprovider", "--collect-only", "-q", "tests"]),
                   cwd=repository, env=nested_pytest.environment(env), capture_output=True, check=True,
                   timeout=HANG_TIMEOUT)


def gate_run_collection(repository, scratch):
    # The gate's own pytest run, in its environment, collecting only.
    env = gate.gate_environment(scratch)
    output = scratch / "events.json"
    env.update(PATH=os.environ["PATH"], PYTHONPATH=str(gate.ROOT), VE_GATE_PYTEST_RESULT=str(output))
    subprocess.run(gate.collection_command([sys.executable]), cwd=repository, env=env, capture_output=True,
                   timeout=HANG_TIMEOUT)
    return json.loads(output.read_text())["collected"]


# Both collect the same way: the base's collection (tools/gate_collection.py) and the gate's run.
COLLECTORS = {"base": lambda repository, scratch: gate_collection.collect(repository),
              "gate": gate_run_collection}


@pytest.mark.parametrize("earlier", EARLIER)
@pytest.mark.parametrize("files,changed,template", SOURCES.values(), ids=SOURCES)
@pytest.mark.parametrize("collector", COLLECTORS.values(), ids=COLLECTORS)
def test_collection_reflects_the_tree_now_not_cached_bytecode(repository, tmp_path_factory, collector,
                                                               files, changed, template, earlier):
    # A same-size change within the same second leaves the source's recorded
    # size and whole-second mtime as they were, so cached bytecode looks
    # current: only a fresh compile yields the parameter now in the tree. The
    # mtime is set back exactly, so the same second is not left to timing.
    for name, text in files.items():
        (repository / name).write_text(text)
    source = repository / changed
    source.write_text(template.format(case="y"))
    if earlier == "an earlier collection":
        ids = collector(repository, tmp_path_factory.mktemp("scratch"))
        assert "tests/test_two.py::test_generated[y]" in ids
    else:
        ordinary_pytest_run(repository)
        assert any(source.parent.joinpath("__pycache__").glob(f"{source.stem}.*.pyc"))
    before = source.stat()
    source.write_text(template.format(case="z"))
    os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert source.stat().st_size == before.st_size
    ids = collector(repository, tmp_path_factory.mktemp("scratch"))
    assert [nodeid for nodeid in ids if "test_generated" in nodeid] == [
        "tests/test_two.py::test_generated[z]"]


@pytest.mark.parametrize("body", [
    "import pytest\npytest.skip('backend unavailable', allow_module_level=True)\n",
    "import ve_gate_absent_test_backend\n",
], ids=["module skip", "import error"])
def test_collection_refuses_a_module_dropped_at_collection(repository, body):
    # An expectation taken from such a collection would silently drop its tests.
    (repository / "tests/test_three.py").write_text(body + "def test_hidden(): pass\n")
    with pytest.raises(gate_collection.CollectionError, match="tests/test_three.py"):
        gate_collection.collect(repository)


def test_the_base_is_imported_from_its_own_tree(repository, tmp_path):
    # The base's modules shadow the checkout's: the checkout's `ve` is installed (editable) in the
    # environment, so the collected tree is put first on the import path.
    (repository / "ve").mkdir()
    (repository / "ve/__init__.py").write_text("MARK = 'collected tree'\n")
    (repository / "tests/test_mark.py").write_text(
        "import pytest, ve\n@pytest.mark.parametrize('mark', [ve.MARK])\ndef test_mark(mark): pass\n")
    assert "tests/test_mark.py::test_mark[collected tree]" in gate_collection.collect(repository)
