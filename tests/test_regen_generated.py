"""tools/regen_generated.py: the generated-file inventory, its merge strategies and the merge-train flow.

* The registry is complete: every script of the repository with a writing mode is a writer or checker of an
  entry or is listed in `NOT_REGENERATED` with a reason, every pattern names a tracked file, and
  `.gitattributes` is generated from the registry.
* `merge_json` keeps both sides' additions and removals, merges records by their key, and refuses a value
  both sides changed differently; the assurance manifest's decoder total is recomputed from the merge.
* End to end, on throwaway repositories with the registry's paths: with the `ve-generated` driver installed,
  `git merge` resolves the generated files (a JSON ledger by structure, an audit manifest by union, a derived
  file by either side) and stops only on other files; without it, `--resolve` resolves conflicts that are all
  in generated files and stages them, and refuses (exit 2, nothing changed) when another file conflicts or a
  JSON value both sides changed.
* A check by rewriting restores the committed files whatever the writer did.
"""
from __future__ import annotations

import ast
import fnmatch
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import regen_generated as R  # noqa: E402

TRACKED = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()


# The registry


def _write_mode_scripts() -> set[str]:
    """Tracked scripts (outside tests and experiments) with a flag that writes a committed file."""
    found = set()
    for name in TRACKED:
        if not name.endswith(".py") or name.startswith(("tests/test_", "experiments/", "ve_experiments/")):
            continue
        try:
            tree = ast.parse((ROOT / name).read_text())
        except (SyntaxError, UnicodeDecodeError):
            continue
        if any(isinstance(node, ast.Constant) and isinstance(node.value, str)
               and (node.value in R.WRITE_FLAGS or node.value.startswith("--write-")) for node in ast.walk(tree)):
            found.add(name)
    return found


def _referenced(entry) -> set[str]:
    """The scripts an entry's commands run, as repository paths."""
    names = set()
    for steps in (entry.write or (), entry.check or ()):
        for step in steps:
            if isinstance(step, str):
                continue
            parts = list(step)
            for i, part in enumerate(parts):
                if part.endswith(".py"):
                    names.add(str(Path(entry.cwd) / part) if entry.cwd != "." else part)
                elif i and parts[i - 1] == "-m" and part.replace(".", "/") + ".py" in TRACKED:
                    names.add(part.replace(".", "/") + ".py")
    return names


def test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason():
    registered = set().union(*(_referenced(entry) for entry in R.GENERATED)) | {"tools/regen_generated.py"}
    unlisted = sorted(name for name in _write_mode_scripts() - registered
                      if not any(fnmatch.fnmatchcase(name, pattern) for pattern in R.NOT_REGENERATED))
    assert not unlisted, f"register these writers in GENERATED or NOT_REGENERATED: {unlisted}"
    for name in registered - {"tools/regen_generated.py"}:
        assert name in TRACKED, f"GENERATED runs a script that is not tracked: {name}"
    for pattern, reason in R.NOT_REGENERATED.items():
        assert reason and any(fnmatch.fnmatchcase(name, pattern) for name in TRACKED), pattern


def test_every_pattern_names_a_tracked_file_and_owns_it():
    for entry in R.GENERATED:
        for pattern in entry.paths:
            matched = [name for name in TRACKED if fnmatch.fnmatchcase(name, pattern)
                       and name.count("/") == pattern.count("/")]
            assert matched, f"{entry.name}: {pattern} names no tracked file"
            for name in matched:
                assert R.owner(name) is entry, (name, R.owner(name))
    assert R.owner("ve/document.py") is None and R.owner("lean/VE/Route/Wire.lean") is None


def test_gitattributes_is_generated_from_the_registry():
    assert R.check_attributes() == 0
    lines = (ROOT / ".gitattributes").read_text().splitlines()
    for entry in R.GENERATED:
        for pattern in entry.paths:
            assert f"{pattern} merge={R.DRIVER}" in lines
    for name in ("lean/checkers.lock", "lean/VE/Audit.lean", "lean/axioms.txt"):
        done = subprocess.run(["git", "check-attr", "merge", "--", name], cwd=ROOT, capture_output=True, text=True)
        assert done.stdout.strip() == f"{name}: merge: {R.DRIVER}"


def test_entries_run_in_dependency_order():
    order = [entry.name for entry in R.GENERATED]
    for before, after in (("wire-contract", "frozen-inventory"), ("english-grammar", "frozen-inventory"),
                          ("english-run-copy", "frozen-inventory"), ("frozen-inventory", "lake-build"),
                          ("lake-build", "lean-axioms"), ("lake-build", "lean-statements"),
                          ("lake-build", "checker-pins"), ("checker-pins", "english-codes"),
                          ("lake-build", "response-schemas"), ("assurance-manifest", "assurance-doc")):
        assert order.index(before) < order.index(after), (before, after)
    assert order[-1] == "gate-collection"


# merge_json


def test_json_merge_keeps_both_additions_and_both_removals():
    base = {"ve_service": ["a", "b", "c"], "rust_jsonl": ["r1"]}
    ours = {"ve_service": ["b", "c", "d"], "rust_jsonl": ["r1"]}
    theirs = {"ve_service": ["a", "b", "e"], "rust_jsonl": ["r1", "r2"]}
    assert R.merge_json(base, ours, theirs) == {"ve_service": ["b", "d", "e"], "rust_jsonl": ["r1", "r2"]}


def test_json_merge_merges_records_by_key_and_objects_by_field():
    base = {"files": [{"file": "A", "lines": 1}, {"file": "B", "lines": 2}], "n": 1}
    ours = {"files": [{"file": "A", "lines": 10}, {"file": "B", "lines": 2}, {"file": "C", "lines": 3}], "n": 1}
    theirs = {"files": [{"file": "A", "lines": 1}, {"file": "B", "lines": 20}], "n": 1, "extra": True}
    assert R.merge_json(base, ours, theirs) == {
        "files": [{"file": "A", "lines": 10}, {"file": "B", "lines": 20}, {"file": "C", "lines": 3}],
        "n": 1, "extra": True}


def test_json_merge_refuses_a_value_both_sides_changed():
    with pytest.raises(R.Conflict, match=r"\$\.files\.A\.lines"):
        R.merge_json({"files": [{"file": "A", "lines": 1}]}, {"files": [{"file": "A", "lines": 2}]},
                     {"files": [{"file": "A", "lines": 3}]})
    with pytest.raises(R.Conflict):
        R.merge_json({"x": 1}, {"x": True}, {"x": 2})
    # The same change on both sides is no conflict; a deletion on one side wins over no change.
    assert R.merge_json({"x": 1, "y": 1}, {"x": 2}, {"x": 2, "y": 1}) == {"x": 2}


def test_json_merge_keeps_a_sorted_map_sorted_and_the_file_format():
    base = {"files": [{"file": "b"}, {"file": "d"}]}
    ours = {"files": [{"file": "a"}, {"file": "b"}, {"file": "d"}]}
    theirs = {"files": [{"file": "b"}, {"file": "c"}, {"file": "d"}]}
    assert [r["file"] for r in R.merge_json(base, ours, theirs)["files"]] == ["a", "b", "c", "d"]
    unsorted = {"files": [{"file": "z"}, {"file": "b"}]}
    assert [r["file"] for r in R.merge_json(base, unsorted, theirs)["files"]] == ["z", "b", "c"]
    # A file no dump reproduces (a duplicate key) keeps its indent and its escaping.
    assert R._json_format('{\n "a": 1,\n "a": "\\u00ab"\n}\n') == (1, True)
    assert R._json_format(json.dumps({"a": "\u00ab"}, indent=2, ensure_ascii=False) + "\n") == (2, False)


def test_assurance_manifest_merge_recomputes_the_decoder_total():
    manifest = json.loads((ROOT / "ve/assurance-manifest.json").read_text())
    ours, theirs = json.loads(json.dumps(manifest)), json.loads(json.dumps(manifest))
    first, second = ours["lean_decoders"]["files"][0], theirs["lean_decoders"]["files"][1]
    first["ranges"][-1][1] += 5
    ours["lean_decoders"]["total_lines"] += 5
    second["ranges"][-1][1] += 7
    theirs["lean_decoders"]["total_lines"] += 7
    text, clean = R.merge_text("ve/assurance-manifest.json", json.dumps(manifest), json.dumps(ours),
                               json.dumps(theirs))
    assert clean
    assert json.loads(text)["lean_decoders"]["total_lines"] == manifest["lean_decoders"]["total_lines"] + 12


# End to end


def _git(root, *args, check=True):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=check)


def _commit(root, files: dict, message: str):
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", message)


AUDIT = "import VE.A\n\n#print axioms VE.a\n"
LOCK = {"ve_service": ["1111", "2222"], "rust_jsonl": ["9999"]}
LEDGER = "tools/layer-exceptions.json"


def _ledger(reason):
    return json.dumps({"ve.a -> ve.b": reason}, indent=2) + "\n"


def _repository(tmp_path, driver: bool, other_conflict: bool = False, ledger_conflict: bool = False):
    """A repository whose branches `ours` and `theirs` both edit a JSON ledger, an audit manifest, a derived
    file (and, if asked, an ordinary file or one ledger value), with `ours` checked out."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "base")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    if driver:
        _git(root, "config", f"merge.{R.DRIVER}.driver",
             f"{sys.executable} {ROOT / 'tools/regen_generated.py'} --merge-driver %O %A %B %P")
    _commit(root, {".gitattributes": R.attributes_text(), "lean/checkers.lock": json.dumps(LOCK, indent=2) + "\n",
                   "lean/VE/Audit.lean": AUDIT, "lean/axioms.txt": "base\n", "ve/code.py": "x = 1\n",
                   LEDGER: _ledger("base")}, "base")
    _git(root, "checkout", "-q", "-b", "theirs")
    _commit(root, {"lean/checkers.lock": json.dumps({**LOCK, "ve_service": ["1111", "2222", "4444"]},
                                                     indent=2) + "\n",
                   **({LEDGER: _ledger("theirs")} if ledger_conflict else {}),
                   "lean/VE/Audit.lean": AUDIT + "#print axioms VE.theirs\n", "lean/axioms.txt": "theirs\n",
                   **({"ve/code.py": "x = 3\n"} if other_conflict else {})}, "theirs")
    _git(root, "checkout", "-q", "-b", "ours", "base")
    _commit(root, {"lean/checkers.lock": json.dumps({"ve_service": ["2222", "3333"], "rust_jsonl": ["9999"]},
                                                     indent=2) + "\n",
                   **({LEDGER: _ledger("ours")} if ledger_conflict else {}),
                   "lean/VE/Audit.lean": AUDIT + "#print axioms VE.ours\n", "lean/axioms.txt": "ours\n",
                   **({"ve/code.py": "x = 2\n"} if other_conflict else {})}, "ours")
    return root


def _merged(root):
    return (json.loads((root / "lean/checkers.lock").read_text()), (root / "lean/VE/Audit.lean").read_text(),
            (root / "lean/axioms.txt").read_text())


def _check_merged(root):
    lock, audit, axioms = _merged(root)
    # Removal of 1111 by ours kept, 3333 and 4444 added by each side; both audit lines; the derived file is
    # either side's (the writers rebuild it).
    assert lock == {"ve_service": ["2222", "3333", "4444"], "rust_jsonl": ["9999"]}
    assert "#print axioms VE.ours\n" in audit and "#print axioms VE.theirs\n" in audit
    assert audit.count("#print axioms VE.a\n") == 1 and "<<<<<<<" not in audit
    assert axioms == "ours\n"


def test_driver_merges_generated_files_without_a_conflict(tmp_path):
    root = _repository(tmp_path, driver=True)
    done = _git(root, "merge", "--no-edit", "-q", "theirs", check=False)
    assert done.returncode == 0, done.stdout + done.stderr
    _check_merged(root)


def test_driver_stops_only_on_ordinary_files(tmp_path):
    root = _repository(tmp_path, driver=True, other_conflict=True)
    done = _git(root, "merge", "--no-edit", "-q", "theirs", check=False)
    assert done.returncode != 0
    assert _git(root, "diff", "--name-only", "--diff-filter=U").stdout.split() == ["ve/code.py"]
    _check_merged(root)


def test_driver_leaves_a_ledger_value_both_sides_changed_in_conflict(tmp_path):
    root = _repository(tmp_path, driver=True, ledger_conflict=True)
    done = _git(root, "merge", "--no-edit", "-q", "theirs", check=False)
    assert done.returncode != 0
    assert _git(root, "diff", "--name-only", "--diff-filter=U").stdout.split() == [LEDGER]


def test_resolve_finishes_a_merge_whose_conflicts_are_all_generated(tmp_path, capsys):
    root = _repository(tmp_path, driver=False)
    done = _git(root, "merge", "--no-commit", "-q", "theirs", check=False)
    assert done.returncode != 0  # without the driver git's own merge stops on them
    assert set(_git(root, "diff", "--name-only", "--diff-filter=U").stdout.split()) == {
        "lean/checkers.lock", "lean/VE/Audit.lean", "lean/axioms.txt"}
    assert R.resolve((), root) == 0
    assert _git(root, "diff", "--name-only", "--diff-filter=U").stdout == ""
    _check_merged(root)
    assert _git(root, "commit", "-q", "--no-edit", check=False).returncode == 0
    assert _git(root, "status", "--porcelain").stdout == ""


def test_resolve_changes_nothing_when_another_file_conflicts(tmp_path, capsys):
    root = _repository(tmp_path, driver=False, other_conflict=True)
    _git(root, "merge", "--no-commit", "-q", "theirs", check=False)
    before = _git(root, "status", "--porcelain").stdout, (root / "lean/checkers.lock").read_text()
    assert R.resolve((), root) == 2
    assert "ve/code.py" in capsys.readouterr().err
    assert (_git(root, "status", "--porcelain").stdout, (root / "lean/checkers.lock").read_text()) == before


def test_resolve_refuses_a_ledger_value_both_sides_changed(tmp_path, capsys):
    root = _repository(tmp_path, driver=False, ledger_conflict=True)
    _git(root, "merge", "--no-commit", "-q", "theirs", check=False)
    before = _git(root, "status", "--porcelain").stdout, (root / "lean/VE/Audit.lean").read_text()
    assert R.resolve((), root) == 2
    assert "ve.a -> ve.b" in capsys.readouterr().err
    assert (_git(root, "status", "--porcelain").stdout, (root / "lean/VE/Audit.lean").read_text()) == before


def test_resolve_needs_a_merge_in_progress(tmp_path):
    root = _repository(tmp_path, driver=False)
    assert R.resolve((), root) == 2


# Checking by rewriting


def test_check_by_rewriting_restores_the_committed_files(tmp_path, monkeypatch):
    target = ROOT / "lean/VE/Route/examples/route-cases.json"
    committed = target.read_bytes()
    script = tmp_path / "writer.py"
    script.write_text(f"from pathlib import Path\nPath({str(target)!r}).write_text('changed')\n")
    entry = R.Generated("probe", ("lean/VE/Route/examples/route-cases.json",), ((sys.executable, str(script)),),
                        None)
    assert R._check_by_rewriting(entry) == 1
    assert target.read_bytes() == committed
    same = tmp_path / "same.py"
    same.write_text("pass\n")
    assert R._check_by_rewriting(R.Generated("probe", entry.paths, ((sys.executable, str(same)),), None)) == 0
