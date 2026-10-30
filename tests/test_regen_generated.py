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
import builtins
import dataclasses
import fnmatch
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys

from hypothesis import given, settings, strategies as st
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import regen_generated as R  # noqa: E402
from subprocesses import HANG_TIMEOUT  # noqa: E402
import trust_map  # noqa: E402

TRACKED = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()


@pytest.fixture(autouse=True)
def _no_timing_log(monkeypatch):
    """The runs these tests make leave no line in the checkout's timing log (`RegenLog`); a test of the log
    points it under tmp_path."""
    monkeypatch.setenv("VE_REGEN_LOG", "off")


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


def _unfreshened(entries) -> list[str]:
    """Entries owning a `ve/` file whose `fresh` names no gate stage and no test function of the suite."""
    gate = (ROOT / "tools/gate.py").read_text()
    problems = []
    for entry in entries:
        if not any(pattern.startswith("ve/") for pattern in entry.paths):
            continue
        if entry.fresh.startswith("gate:"):
            if f'stage="{entry.fresh.removeprefix("gate:")}"' not in gate:
                problems.append(f"{entry.name}: no gate stage {entry.fresh}")
            continue
        path, _, name = entry.fresh.partition("::")
        functions = ({node.name for node in ast.parse((ROOT / path).read_text()).body
                      if isinstance(node, ast.FunctionDef)}
                     if path.startswith("tests/test_") and path in TRACKED else set())
        if name not in functions:
            problems.append(f"{entry.name}: no automatic check {entry.fresh!r}")
    return problems


def test_every_table_the_product_reads_is_checked_by_the_suite_or_the_gate():
    """Review F1 (me-1a): a generated file under `ve/` whose check only runs by hand drifts from its owner
    (`ve/numbers_phrases.json` had only a mocked test). Each such entry names the test or gate stage that runs
    its check unmocked."""
    assert _unfreshened(R.GENERATED) == []
    numbers = next(entry for entry in R.GENERATED if entry.name == "numbers-phrases")
    for fresh in ("", "tests/test_numbers_phrases.py::test_no_such_test", "gate:No such stage",
                  "tests/test_numbers_phrases.py"):
        assert _unfreshened([dataclasses.replace(numbers, fresh=fresh)]) != []
    assert "fresh: gate:Wire contract check" in R.listing()


def test_gitattributes_is_generated_from_the_registry():
    assert R.check_attributes() == 0
    lines = (ROOT / ".gitattributes").read_text().splitlines()
    for entry in R.GENERATED:
        for pattern in entry.paths:
            assert f"{pattern} merge={R.DRIVER}" in lines
    for name in ("lean/checkers.lock", "lean/VE/Audit.lean", "lean/axioms.txt"):
        done = subprocess.run(["git", "check-attr", "merge", "--", name], cwd=ROOT, capture_output=True, text=True)
        assert done.stdout.strip() == f"{name}: merge: {R.DRIVER}"


def test_the_listing_names_every_entry_and_command():
    listing = R.listing()
    for entry in R.GENERATED:
        assert f"{entry.name} [{entry.merge}]" in listing
    assert "write: write_attributes() in this script" in listing
    assert "write: python tools/lean_statements.py\n" in listing


def test_owner_agrees_with_git_on_every_tracked_file():
    """git itself is the oracle of the attribute patterns: a tracked file has the driver exactly when an
    entry owns it."""
    done = subprocess.run(["git", "check-attr", "--stdin", "merge"], cwd=ROOT, input="\n".join(TRACKED) + "\n",
                          capture_output=True, text=True, check=True)
    by_git = {line.rsplit(": merge: ", 1)[0]: line.rsplit(": merge: ", 1)[1] for line in done.stdout.splitlines()}
    assert by_git.keys() == set(TRACKED)
    disagree = [name for name in TRACKED if (by_git[name] == R.DRIVER) != (R.owner(name) is not None)]
    assert not disagree, disagree[:10]


def test_entries_run_in_dependency_order():
    order = [entry.name for entry in R.GENERATED]
    for before, after in (("wire-contract", "frozen-inventory"), ("english-grammar", "frozen-inventory"),
                          ("english-run-copy", "frozen-inventory"), ("lean-roots", "lake-build"),
                          ("lake-build", "lean-statements"), ("lean-statements", "lean-audit-manifests"),
                          ("lean-audit-manifests", "frozen-inventory"),
                          ("lake-build", "checker-pins"), ("checker-pins", "english-codes"),
                          ("lake-build", "response-schemas"), ("assurance-manifest", "assurance-doc")):
        assert order.index(before) < order.index(after), (before, after)
    # The test collection is no generated file: the gate takes it from the merge base (tools/gate_collection.py).
    assert "gate-collection" not in order and R.owner("tools/gate-collection.json") is None



def test_audit_manifests_are_generated_from_the_declaration_list():
    """AR-1: `lean/audit.py --write` writes both manifests and the record from lean/declarations.txt, so a merge
    takes either side and the writer rebuilds them (collision rule: take either side, run the writer)."""
    entry = R.owner("lean/VE/Audit.lean")
    assert entry is R.owner("lean/ResponseShapeAudit.lean") is R.owner("lean/axioms.txt")
    assert entry.name == "lean-audit-manifests" and entry.merge == "regenerate"
    assert entry.write == ((R.PY, "lean/audit.py", "--write"),) and entry.check == ((R.PY, "lean/audit.py", "--check"),)
    assert R.merge_text("lean/VE/Audit.lean", "base\n", "ours\n", "theirs\n") == ("ours\n", True)


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


JSON = st.recursive(st.none() | st.booleans() | st.integers(-3, 3) | st.sampled_from(["a", "b", "c"]),
                    lambda inner: st.lists(inner, max_size=3) | st.dictionaries(st.sampled_from("xyz"), inner,
                                                                                    max_size=3), max_leaves=8)


@settings(max_examples=300, deadline=None)
@given(base=JSON, change=JSON)
def test_json_merge_takes_a_one_sided_change_and_agrees_with_itself(base, change):
    """A change on one side only is the merge, whichever side made it; identical sides merge to themselves."""
    assert R._text(R.merge_json(base, change, base)) == R._text(change)
    assert R._text(R.merge_json(base, base, change)) == R._text(change)
    assert R._text(R.merge_json(base, change, change)) == R._text(change)


@settings(max_examples=300, deadline=None)
@given(base=st.dictionaries(st.sampled_from("abcdef"), st.integers(0, 3), max_size=4),
       ours=st.dictionaries(st.sampled_from("ghij"), st.integers(0, 3), max_size=3),
       theirs=st.dictionaries(st.sampled_from("klmn"), st.integers(0, 3), max_size=3))
def test_json_merge_of_disjoint_additions_keeps_both_in_either_order(base, ours, theirs):
    left = R.merge_json(base, {**base, **ours}, {**base, **theirs})
    right = R.merge_json(base, {**base, **theirs}, {**base, **ours})
    assert left == right == {**base, **ours, **theirs}


def test_assurance_manifest_merge_recomputes_the_decoder_total(monkeypatch):
    manifest = json.loads((ROOT / "ve/assurance-manifest.json").read_text())
    ours, theirs = json.loads(json.dumps(manifest)), json.loads(json.dumps(manifest))
    first, second = ours["lean_decoders"]["files"][0], theirs["lean_decoders"]["files"][1]
    first["ranges"][-1][1] += 5
    ours["lean_decoders"]["total_lines"] += 5
    second["ranges"][-1][1] += 7
    theirs["lean_decoders"]["total_lines"] += 7
    original_import = builtins.__import__

    def reject_manifest_import(name, *args, **kwargs):
        if name == "assurance_manifest":
            raise AssertionError("the merged manifest is not on disk yet")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_manifest_import)
    text, clean = R.merge_text("ve/assurance-manifest.json", json.dumps(manifest), json.dumps(ours),
                               json.dumps(theirs))
    assert clean
    assert json.loads(text)["lean_decoders"]["total_lines"] == manifest["lean_decoders"]["total_lines"] + 12


TRUST_MERGES = json.loads((ROOT / "tests/data/regen_trust_merges.json").read_text())


@pytest.mark.parametrize("merge", TRUST_MERGES)
def test_trust_merge_adds_file_deltas_and_recomputes_both_derived_values(merge):
    """Small file rows cut from the base, parents and committed resolutions of three real syncs."""
    case = TRUST_MERGES[merge]
    text, clean = R.merge_text("docs/trust-baseline.json", *(json.dumps(case[side]) for side in
                                                         ("base", "ours", "theirs")))
    assert clean
    merged = json.loads(text)
    assert merged == case["merged"]
    assert merged["totals"] == trust_map.totals(merged["files"])
    assert merged["budget"] == trust_map.budget(merged["totals"])
    assert merged["budget"] != case["ours"]["budget"]


def test_trust_merge_of_the_ar4_budget_file_keeps_main_budget_and_both_allowances():
    """AR-4's budget file has no per-file counts: the merge keeps main's measured budget as a value (no
    recomputation from `files`, which would crash) and both sides' allowances."""
    def side(budget, allowances):
        return {"comment": trust_map.COMMENT, "budget": budget, "allowances": allowances}

    old = {"class": "V", "lines": 3, "reason": "old", "signature": "R6 (DRI-RULINGS.md)", "commit": "abc1234"}
    new = {**old, "lines": 5, "reason": "branch growth", "signature": "DRI, sync note, 2026-10-14"}
    base = side({"K": 1, "S": 2, "V": 3}, [old])
    ours = side({"K": 1, "S": 2, "V": 3}, [old, new])
    theirs = side({"K": 1, "S": 2, "V": 9}, [old])
    text, clean = R.merge_text("docs/trust-baseline.json", *(json.dumps(s) for s in (base, ours, theirs)))
    assert clean
    assert json.loads(text) == side({"K": 1, "S": 2, "V": 9}, [old, new])


def test_trust_merge_adds_equal_concurrent_values_and_missing_base_rows():
    row = trust_map.empty_counts()
    ours = {"files": {"New.lean": {**row, "K": 2, "trusted": 2}}}
    theirs = {"files": {"New.lean": {**row, "K": 2, "trusted": 2}}}
    for side in (ours, theirs):
        side["totals"] = trust_map.totals(side["files"])
        side["budget"] = trust_map.budget(side["totals"])
    base = {"files": {}, "totals": trust_map.totals({}), "budget": trust_map.budget(trust_map.totals({}))}
    text, clean = R.merge_text("docs/trust-baseline.json", *(json.dumps(side) for side in (base, ours, theirs)))
    assert clean
    assert json.loads(text)["files"]["New.lean"]["K"] == 4
    assert json.loads(text)["budget"]["K"] == 4


@pytest.mark.parametrize("kind", ["K", "S", "V"])
def test_trust_merge_refuses_allowance_consumed_on_both_sides(kind, capsys):
    """F1: two --write operations must not count inherited signed growth twice."""
    def row(value):
        counts = trust_map.empty_counts()
        column = "G" if kind == "V" else kind
        counts[column] = value
        if kind == "V":
            counts["G[V]"] = value
        counts["trusted"] = value
        counts["lines"] = value
        return counts

    def side(files, signed):
        total = trust_map.totals(files)
        return json.dumps({"totals": total, "budget": trust_map.budget(total),
                           "signed": signed, "history": [], "files": files})

    allowance = {"change": "x", "signed": "DRI", "allow": {kind: 5}}
    base = side({"A.lean": row(10)}, [allowance])
    ours = side({"A.lean": row(16)}, [])
    theirs = side({"A.lean": row(15), "B.lean": row(2)}, [])
    text, clean = R.merge_text("docs/trust-baseline.json", base, ours, theirs)
    assert not clean and text == ours
    assert "$.signed: both sides consumed base allowance" in capsys.readouterr().err

    # One branch consumes the allowance; the other still carries it. The file
    # growth is incorporated once and the allowance disappears from the merge.
    merged_text, clean = R.merge_text("docs/trust-baseline.json", base, ours,
                                      side({"A.lean": row(10), "B.lean": row(2)}, [allowance]))
    assert clean
    merged = json.loads(merged_text)
    assert merged["budget"][kind] == 18
    assert merged["signed"] == []


def test_trust_merge_refuses_partial_duplicate_allowance_consumption(capsys):
    """The same signed record may occur twice; consuming one copy on each side still overlaps."""
    row = trust_map.empty_counts()
    allowance = {"change": "x", "signed": "DRI", "allow": {"V": 1}}
    def side(signed):
        return json.dumps({"files": {"A.lean": row}, "signed": signed,
                           "totals": trust_map.totals({"A.lean": row}), "budget": trust_map.budget(row)})
    text, clean = R.merge_text("docs/trust-baseline.json", side([allowance, allowance]),
                               side([allowance]), side([allowance]))
    assert not clean
    assert text == side([allowance])
    assert "$.signed" in capsys.readouterr().err


@pytest.mark.parametrize("delete_count", [False, True])
def test_trust_merge_refuses_delete_versus_change(capsys, delete_count):
    case = TRUST_MERGES["17573bbb"]
    base = case["base"]
    ours = json.loads(json.dumps(base))
    theirs = json.loads(json.dumps(base))
    module = "ResponseShape.lean"
    if delete_count:
        del ours["files"][module]["trusted"]
    else:
        del ours["files"][module]
    theirs["files"][module]["trusted"] += 1
    text, clean = R.merge_text("docs/trust-baseline.json", *(json.dumps(side) for side in
                                                         (base, ours, theirs)))
    assert not clean
    assert text == json.dumps(ours)
    assert module in capsys.readouterr().err


def test_trust_non_file_fields_keep_structural_json_merge(capsys):
    case = TRUST_MERGES["17573bbb"]
    base = {**case["base"], "signed": [], "history": [], "section11": {"n": 1}, "comment": "base"}
    ours = {**case["ours"], "signed": [{"change": "ours", "signed": "DRI"}],
            "history": ["ours"], "section11": {"n": 2}, "comment": "ours"}
    theirs = {**case["theirs"], "signed": [{"change": "theirs", "signed": "DRI"}],
              "history": ["theirs"], "section11": {"n": 3}, "comment": "base"}
    _, clean = R.merge_text("docs/trust-baseline.json", *(json.dumps(side) for side in
                                                     (base, ours, theirs)))
    assert not clean
    assert "$.section11.n" in capsys.readouterr().err
    theirs["section11"]["n"] = 1
    text, clean = R.merge_text("docs/trust-baseline.json", *(json.dumps(side) for side in
                                                        (base, ours, theirs)))
    assert clean
    merged = json.loads(text)
    assert merged["signed"] == [ours["signed"][0], theirs["signed"][0]]
    assert merged["history"] == ["ours", "theirs"]
    assert merged["section11"] == {"n": 2}
    assert merged["comment"] == "ours"


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
    # Removal of 1111 by ours kept, 3333 and 4444 added by each side; the derived files, the audit manifest
    # included (AR-1), are either side's (`lean/audit.py --write` rebuilds it).
    assert lock == {"ve_service": ["2222", "3333", "4444"], "rust_jsonl": ["9999"]}
    assert audit == AUDIT + "#print axioms VE.ours\n"
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


def test_resolve_takes_the_deletion_of_a_retired_file(tmp_path, capsys):
    # A branch that still edits a deleted generated file (AR-3's collision rule: take the deletion).
    root = _repository(tmp_path, driver=False)
    [retired] = R.RETIRED
    _git(root, "checkout", "-q", "base")
    _commit(root, {retired: "[]\n"}, "the retired file at the base")
    for branch, files in (("theirs", {retired: '["tests/a.py::test_a"]\n'}), ("ours", {})):
        _git(root, "checkout", "-q", branch)
        _git(root, "merge", "-q", "--no-edit", "base")
        if files:
            _commit(root, files, "edit the retired file")
    _git(root, "rm", "-q", retired)
    _git(root, "commit", "-q", "-m", "delete the retired file")
    _git(root, "merge", "--no-commit", "-q", "theirs", check=False)
    assert retired in _git(root, "diff", "--name-only", "--diff-filter=U").stdout.split()
    assert R.resolve((), root) == 0
    assert not (root / retired).exists() and _git(root, "diff", "--name-only", "--diff-filter=U").stdout == ""
    assert f"resolved {retired} (deleted: " in capsys.readouterr().out
    _check_merged(root)


def test_a_retired_file_has_no_entry():
    assert all(R.owner(path) is None for path in R.RETIRED)


def test_resolve_fails_when_measured_tree_exceeds_merged_trust_budget(tmp_path, monkeypatch):
    case = TRUST_MERGES["6aafef85"]
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "base")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    path = "docs/trust-baseline.json"
    _commit(root, {path: json.dumps(case["base"], indent=2) + "\n"}, "base")
    _git(root, "checkout", "-q", "-b", "theirs")
    _commit(root, {path: json.dumps(case["theirs"], indent=2) + "\n"}, "theirs")
    _git(root, "checkout", "-q", "-b", "ours", "base")
    _commit(root, {path: json.dumps(case["ours"], indent=2) + "\n"}, "ours")
    assert _git(root, "merge", "--no-commit", "theirs", check=False).returncode != 0
    assert _git(root, "diff", "--name-only", "--diff-filter=U").stdout.split() == [path]

    measured = json.loads(json.dumps(case["merged"]["files"]))
    measured["ResponseShape/Schemas/Document.lean"]["trusted"] += 1

    def trust_check(entry, steps, root=R.ROOT):
        assert entry.name == "trust-tables"
        assert steps == entry.check
        baseline = json.loads((tmp_path / "repo" / path).read_text())
        assert baseline["files"] == case["merged"]["files"]
        return int(bool(trust_map.check(measured, baseline["budget"], [])))

    monkeypatch.setattr(R, "_run", trust_check)
    assert R.resolve(R.selected(["trust-tables"], []), root) == 1
    assert _git(root, "diff", "--name-only", "--diff-filter=U").stdout.split() == [path]


def test_resolve_needs_a_merge_in_progress(tmp_path):
    root = _repository(tmp_path, driver=False)
    assert R.resolve((), root) == 2


# Checking by rewriting


def test_check_by_rewriting_restores_the_committed_files(tmp_path):
    (tmp_path / "out").mkdir()
    target = tmp_path / "out/table.json"
    target.write_text("committed\n")
    changes = tmp_path / "changes.py"
    changes.write_text("from pathlib import Path\nPath('out/table.json').write_text('changed')\n"
                       "Path('out/extra.json').write_text('new')\n")
    entry = R.Generated("probe", ("out/*.json",), ((sys.executable, str(changes)),), None)
    assert R._check_by_rewriting(entry, tmp_path) == 1
    assert target.read_text() == "committed\n" and not (tmp_path / "out/extra.json").exists()
    same = tmp_path / "same.py"
    same.write_text("pass\n")
    assert R._check_by_rewriting(R.Generated("probe", entry.paths, ((sys.executable, str(same)),), None),
                                 tmp_path) == 0


# The Lean service before the entries that start it (eff-20261019-1, PIPELINE-LIMITS L58)
#
# Hermetic: a fake Lake (`lake.py`) builds `bin/ve_service` as the text "built from <lean/Source.lean>" and answers
# `--no-build ve_service` as Lake does (exit 3 when it would rebuild); a fake service user refuses a build that is
# not pinned or not current, as the client and the handshake do; lean/checkers.lock is `tmp_path`'s.


FAKE_LAKE = """import pathlib, sys
root = pathlib.Path(sys.argv[1])
with (root / "lake.log").open("a") as log:
    log.write(" ".join(sys.argv[2:]) + "\\n")
exe, built = root / "bin/ve_service", "built from " + (root / "lean/Source.lean").read_text()
if "--no-build" in sys.argv:
    sys.exit(0 if exe.is_file() and exe.read_text() == built else 3)
exe.parent.mkdir(exist_ok=True)
exe.write_text(built)
"""

FAKE_USER = """import hashlib, json, pathlib, sys
root, name, change = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
exe = root / "bin/ve_service"
build = exe.read_text()
with (root / "service.log").open("a") as log:
    log.write(f"{name} {build}\\n".replace("\\n", "|", build.count("\\n")))
if hashlib.sha256(build.encode()).hexdigest() not in json.loads((root / "lean/checkers.lock").read_text())["ve_service"]:
    sys.exit(f"CheckerUnavailable: {exe} has unlisted build")
if build != "built from " + (root / "lean/Source.lean").read_text():
    sys.exit("unexpected handshake")
(root / "out").mkdir(exist_ok=True)
(root / "out" / name).write_text(build)
if change:  # a writer of a Lean file in the service's closure (english-lexicon-fixtures)
    (root / "lean/Source.lean").write_text(change[0])
"""


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _service_tree(tmp_path, monkeypatch, *, source: str, built: str | None, pins: list[str], users):
    """A fake tree: lean/Source.lean, a build of `built` (None: none), the lock with `pins`, and GENERATED =
    the service users `users` ((name, mark, Lean text it writes or None) in order, "BUILD" and "PINS" placing the
    two real entries' fakes)."""
    (tmp_path / "lean").mkdir()
    (tmp_path / "lean/Source.lean").write_text(source)
    if built is not None:
        (tmp_path / "bin").mkdir()
        (tmp_path / "bin/ve_service").write_text(f"built from {built}")
    (tmp_path / "lean/checkers.lock").write_text(
        json.dumps({"rust_jsonl": ["r"], "ve_service": sorted(pins)}, indent=2) + "\n")  # as _write_lock writes it
    lake, user = tmp_path / "lake.py", tmp_path / "user.py"
    lake.write_text(FAKE_LAKE)
    user.write_text(FAKE_USER)
    run = lambda script, *args: (sys.executable, str(script), str(tmp_path), *args)  # noqa: E731
    entries = []
    for name, mark, change in users:
        if name == "BUILD":
            entries.append(R.Generated(R.BUILD, (), (run(lake),), (run(lake),), cwd="lean"))
        elif name == "PINS":
            entries.append(R.Generated(R.PINS, ("lean/checkers.lock",), ("pin_checkers",), ("check_pins",),
                                       merge="json"))
        else:
            write = run(user, name, *([change] if change else []))
            entries.append(R.Generated(name, (f"out/{name}", "lean/Source.lean") if change else (f"out/{name}",),
                                       (write,), (run(user, name),), service=mark))
    monkeypatch.setattr(R, "GENERATED", tuple(entries))
    monkeypatch.setattr(R, "ROOT", tmp_path)
    monkeypatch.setattr(R, "LOCK", tmp_path / "lean/checkers.lock")
    monkeypatch.setattr(R, "owned_files", lambda entry, root=tmp_path: sorted(
        {path for pattern in entry.paths for path in root.glob(pattern) if path.is_file()}))
    exe = tmp_path / "bin/ve_service"
    monkeypatch.setattr(R, "_service_digest", lambda: _digest(exe.read_text()) if exe.is_file() else None)
    monkeypatch.setenv("VE_REGEN_NO_RUST", "1")
    return tmp_path


def _log(root, name) -> list[str]:
    path = root / name
    return path.read_text().splitlines() if path.is_file() else []


def _pins(root) -> list[str]:
    return json.loads((root / "lean/checkers.lock").read_text())["ve_service"]


USERS = (("english-lexicon-fixtures", "write", None), ("BUILD", "", None), ("PINS", "", None),
         ("english-codes", "write", None))


def test_write_with_an_unpinned_service_bootstraps_once_then_runs_every_entry(tmp_path, monkeypatch, capsys):
    """The defect: the first service user refused the built ve_service (not pinned), so `write` stopped before
    lake-build and checker-pins. Now the run builds and pins it first, once, and ends with the final build pinned
    beside the pins it started with."""
    root = _service_tree(tmp_path, monkeypatch, source="v1", built="v1", pins=["old"], users=USERS)
    assert R.main(["--write"]) == 0
    out = capsys.readouterr().out
    assert out.count("== bootstrap: the built ve_service") == 1 and "is not pinned" in out
    assert _log(root, "service.log") == ["english-lexicon-fixtures built from v1", "english-codes built from v1"]
    assert sorted(path.name for path in (root / "out").iterdir()) == ["english-codes", "english-lexicon-fixtures"]
    assert _pins(root) == sorted(["old", _digest("built from v1")])
    assert json.loads((root / "lean/checkers.lock").read_text())["rust_jsonl"] == ["r"]
    # The bootstrap is the two entries' own steps: a query, the build, a query that confirms it; then the run's
    # own build.
    assert _log(root, "lake.log") == ["--no-build ve_service", "", "--no-build ve_service", ""]


def test_a_bootstrap_pin_the_final_build_supersedes_is_removed(tmp_path, monkeypatch, capsys):
    """A writer changes a Lean file of the service's closure after the bootstrap: the next user gets a build of
    the changed tree, and the bootstrap's first pin, which is no build of the final tree, goes again."""
    users = (("english-lexicon-fixtures", "write", "v2"), ("route-cases", "write", None), *USERS[1:])
    root = _service_tree(tmp_path, monkeypatch, source="v1", built="v1", pins=["old"], users=users)
    assert R.main(["--write"]) == 0
    out = capsys.readouterr().out
    assert out.count("== bootstrap:") == 2
    assert _log(root, "service.log") == ["english-lexicon-fixtures built from v1", "route-cases built from v2",
                                         "english-codes built from v2"]
    assert _pins(root) == sorted(["old", _digest("built from v2")])
    assert f"not the final build: {_digest('built from v1')}" in out


def test_a_pin_the_lock_had_before_the_run_is_never_removed(tmp_path, monkeypatch):
    """After a merge the lock holds both sides' pins; one of them is the build the bootstrap makes, and the
    final build is another: that pin stays (only pins this run added go)."""
    users = (("english-lexicon-fixtures", "write", "v2"), *USERS[1:])
    root = _service_tree(tmp_path, monkeypatch, source="v1", built="v0", pins=["old", _digest("built from v1")],
                         users=users)
    assert R.main(["--write"]) == 0
    assert _log(root, "service.log")[0] == "english-lexicon-fixtures built from v1"  # stale v0: rebuilt first
    assert _pins(root) == sorted(["old", _digest("built from v1"), _digest("built from v2")])


def test_a_pinned_and_current_service_runs_no_bootstrap(tmp_path, monkeypatch, capsys):
    """One question to Lake before the first user; no build beyond the run's own lake-build, no pin change."""
    root = _service_tree(tmp_path, monkeypatch, source="v1", built="v1", pins=["old", _digest("built from v1")],
                         users=USERS)
    before = (root / "lean/checkers.lock").read_text()
    assert R.main(["--write"]) == 0
    assert "bootstrap" not in capsys.readouterr().out
    assert _log(root, "lake.log") == ["--no-build ve_service", ""]
    assert (root / "lean/checkers.lock").read_text() == before


def test_write_only_a_service_user_bootstraps_without_selecting_the_build(tmp_path, monkeypatch):
    """`--write --only english-codes` still builds and pins first (the two entries are not selected); the
    build it pinned is the final one and stays."""
    root = _service_tree(tmp_path, monkeypatch, source="v1", built="v0", pins=["old"], users=USERS)
    assert R.main(["--write", "--only", "english-codes"]) == 0
    assert _log(root, "service.log") == ["english-codes built from v1"]
    assert _pins(root) == sorted(["old", _digest("built from v1")])


def test_a_failed_bootstrap_build_stops_the_run_and_names_the_build(tmp_path, monkeypatch, capsys):
    root = _service_tree(tmp_path, monkeypatch, source="v1", built="v0", pins=["old"], users=USERS)
    (root / "lake.py").write_text(FAKE_LAKE + "sys.exit(1)\n")  # every build fails
    assert R.main(["--write"]) == 1
    assert "regen_generated: failed: lake-build" in capsys.readouterr().err
    assert _log(root, "service.log") == [] and _pins(root) == ["old"]


def test_resolve_of_two_pinned_sides_builds_and_pins_the_merged_service_in_one_run(tmp_path, monkeypatch):
    """L58/L82: each side pinned its own build; the merged Lean tree builds one neither pinned. One `--resolve`
    builds and pins it before the first user, runs every writer and check, and stages the lock with both
    sides' pins and the merged build."""
    root = _service_tree(tmp_path, monkeypatch, source="1\n2\n3\n", built="1\n2\n3\n",
                         pins=[_digest("built from 1\n2\n3\n")], users=USERS)
    (root / ".gitignore").write_text("bin/\n*.log\n")
    for args in (("init", "-q", "-b", "base"), ("config", "user.email", "t@example.com"), ("config", "user.name", "t")):
        _git(root, *args)
    _commit(root, {}, "base")
    sides = {"theirs": "1\n2\n3t\n", "ours": "1o\n2\n3\n"}
    for side, source in sides.items():
        _git(root, "checkout", "-q", "-b", side, "base")
        lock = json.loads((root / "lean/checkers.lock").read_text())
        _commit(root, {"lean/Source.lean": source, "lean/checkers.lock": json.dumps(
            {**lock, "ve_service": sorted([*lock["ve_service"], _digest(f"built from {source}")])}, indent=2) + "\n"},
            side)
    (root / "bin/ve_service").write_text(f"built from {sides['ours']}")  # this worktree's build
    _git(root, "merge", "--no-commit", "-q", "theirs", check=False)
    assert _git(root, "rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).returncode == 0
    assert R.resolve(R.GENERATED, root) == 0
    merged = "1o\n2\n3t\n"
    assert (root / "lean/Source.lean").read_text() == merged
    assert _log(root, "service.log") == [f"{name} built from 1o|2|3t|" for name in
                                         ("english-lexicon-fixtures", "english-codes")] * 2  # writers, then checks
    assert _pins(root) == sorted(_digest(f"built from {source}") for source in ("1\n2\n3\n", *sides.values(), merged))
    assert _git(root, "commit", "-q", "--no-edit", check=False).returncode == 0
    assert _git(root, "status", "--porcelain").stdout == ""


@pytest.mark.parametrize("built, pins, cause, why", [
    ("v1", ["old"], "checker-pins", f"the built ve_service {_digest('built from v1')} is not pinned in lean/checkers.lock"),
    ("v0", ["old", _digest("built from v0")], "lake-build", "is not current for the Lean sources"),
    (None, ["old"], "lake-build", "ve_service is not built"),
])
def test_check_with_a_service_that_cannot_start_names_the_cause_once_and_checks_no_user(
        tmp_path, monkeypatch, capsys, built, pins, cause, why):
    root = _service_tree(tmp_path, monkeypatch, source="v1", built=built, pins=pins, users=USERS)
    tracked = {path: path.read_bytes() for path in (root / "lean").rglob("*")}
    assert R.main(["--check"]) == 1
    out, err = capsys.readouterr()
    assert _log(root, "service.log") == []  # no user started the service
    assert {path: path.read_bytes() for path in (root / "lean").rglob("*")} == tracked  # nothing written
    cause_lines = [line for line in err.splitlines() if "the entries that start it are not checked" in line]
    assert len(cause_lines) == 1 and why in cause_lines[0]
    assert "--write --only lake-build --only checker-pins" in cause_lines[0]
    for name in ("english-lexicon-fixtures", "english-codes"):
        assert f"{name}: not checked: needs the pinned service" in out
    summary = err.splitlines()[-1]
    assert summary.startswith(f"regen_generated: failed: {cause}") and summary.count(cause) == 1
    assert summary.endswith("not checked (needs the pinned service): english-lexicon-fixtures, english-codes")
    assert "Traceback" not in out + err


def test_check_with_a_ready_service_checks_every_user_and_asks_lake_once(tmp_path, monkeypatch, capsys):
    root = _service_tree(tmp_path, monkeypatch, source="v1", built="v1", pins=[_digest("built from v1")],
                         users=USERS)
    assert R.main(["--check"]) == 0
    assert _log(root, "service.log") == ["english-lexicon-fixtures built from v1", "english-codes built from v1"]
    assert _log(root, "lake.log") == ["--no-build ve_service", ""]
    assert "not checked" not in "".join(capsys.readouterr())


def test_without_lake_the_pin_alone_decides_as_before(tmp_path, monkeypatch, capsys):
    """A machine without Lake on PATH checked a service user against a pinned build before this change; it still
    does (no question to Lake can be asked), and an unpinned build is still refused."""
    root = _service_tree(tmp_path, monkeypatch, source="v1", built="v0", pins=[_digest("built from v0")],
                         users=USERS)
    monkeypatch.setattr(R, "GENERATED", tuple(
        dataclasses.replace(entry, write=((str(tmp_path / "no-such-lake"),),)) if entry.name == R.BUILD else entry
        for entry in R.GENERATED))
    (root / "user.py").write_text(FAKE_USER.replace('if build != "built from "', 'if False and build != "built from "'))
    assert R.main(["--check", "--only", "english-codes"]) == 0
    assert _log(root, "service.log") == ["english-codes built from v0"]
    (root / "lean/checkers.lock").write_text(json.dumps({"rust_jsonl": [], "ve_service": ["old"]}, indent=2) + "\n")
    assert R.main(["--check", "--only", "english-codes"]) == 1
    assert "is not pinned in lean/checkers.lock" in capsys.readouterr().err


# Which entries start the service: every entry whose commands import the client carries the mark.

SERVICE_CLIENT = "ve/backends/lean_service.py"
# Entries whose commands import the client without starting it, each with the reason; the test below runs each
# check with a service that cannot start.
IMPORTS_ONLY = {
    "binding-census": "imports LeanService inside record_answers, which only --record and --refresh run",
    "history-tests": "reaches it through tools/test_map.py -> select_tests.py -> answer_replay.py, never called",
}


def _function_imports(name: str, seen: set) -> set[str]:
    """The modules a function of tools/regen_generated.py imports, and those of the module functions it calls."""
    if name in seen:
        return set()
    seen.add(name)
    tree = ast.parse((ROOT / "tools/regen_generated.py").read_text())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
    found = set()
    for node in ast.walk(function):
        if isinstance(node, ast.Import):
            found |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and callable(getattr(R, node.func.id, None)) \
                and isinstance(getattr(R, node.func.id), type(R.main)):
            found |= _function_imports(node.func.id, seen)
    return found


@pytest.fixture(scope="module")
def graph(tmp_path_factory):
    import source_graph
    cache = tmp_path_factory.mktemp("cache")
    summaries = Path.home() / ".cache/ve-testselect/summaries.pickle"  # content-keyed parses: speed only
    if summaries.is_file():
        (cache / "ve-testselect").mkdir()
        shutil.copy(summaries, cache / "ve-testselect/summaries.pickle")
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("XDG_CACHE_HOME", str(cache))  # the graph's own cache
        yield source_graph.load(ROOT)


def _service_importers(entries, graph) -> dict[str, list[str]]:
    """{entry: its commands' files whose imports reach the service client}."""
    reaching = graph.importers(SERVICE_CLIENT)
    found = {}
    for entry in entries:
        files = set(_referenced(entry))
        for steps in (entry.write or (), entry.check or ()):
            for step in steps:
                if isinstance(step, str):
                    files |= {graph.resolve("tools/regen_generated.py", module) or module
                              for module in _function_imports(step, set())}
        if hits := sorted(files & reaching):
            found[entry.name] = hits
    return found


def _unmarked(entries, graph) -> list[str]:
    importers = _service_importers(entries, graph)
    return [f"{name}: {files}" for name, files in importers.items()
            if not next(entry for entry in entries if entry.name == name).service
            and name not in (R.BUILD, R.PINS) and name not in IMPORTS_ONLY]


def test_every_entry_whose_commands_import_the_service_client_is_marked(graph):
    """The mark is the one list of the entries the run builds and pins the service for; the source graph finds
    every entry whose writer or check imports the client (directly or through the modules it imports). The two
    entries that build and pin it import it to hash the build, and never start it."""
    importers = _service_importers(R.GENERATED, graph)
    assert _unmarked(R.GENERATED, graph) == []
    for name in ("wire-contract", "english-lexicon-fixtures", "question-fixtures", "route-cases", "english-codes",
                 "question-codes", "checker-pins", *IMPORTS_ONLY):
        assert name in importers, name
    for entry in R.GENERATED:
        assert entry.service in ("", "write", "check"), entry.name
        if entry.service:  # losing the mark fails the test
            assert entry.name in importers and _unmarked([dataclasses.replace(entry, service="")], graph) != []
    assert {name: R.entry_named(name).service for name in ("wire-contract", "binding-census")} == {
        "wire-contract": "check", "binding-census": ""}
    assert set(IMPORTS_ONLY) <= set(importers) and all(IMPORTS_ONLY.values())


TRAP = """import pathlib, runpy, sys
root, marker, kind, target, *args = sys.argv[1:]
sys.path.insert(0, root)
if kind != "-m":
    sys.path.insert(0, str(pathlib.Path(target).parent))  # as `python <script>` does
from ve.backends import lean_service
def started(self):
    pathlib.Path(marker).write_text("started")
    raise lean_service.CheckerUnavailable("CheckerUnavailable: trapped")
lean_service.LeanService._spawn = started
sys.argv = [target, *args]
runpy.run_module(target, run_name="__main__", alter_sys=True) if kind == "-m" else runpy.run_path(target, run_name="__main__")
"""


def _starts_the_service(tmp_path, entry) -> bool:
    """Whether the entry's check starts the Lean service: it runs with a LeanService whose start is recorded."""
    trap = tmp_path / "trap.py"
    trap.write_text(TRAP)
    marker = tmp_path / f"{entry.name}.started"
    for step in entry.check:
        rest = list(step[1:])
        kind, target = ("-m", rest[1]) if rest[0] == "-m" else ("file", str(ROOT / entry.cwd / rest[0]))
        args = rest[2:] if kind == "-m" else rest[1:]
        subprocess.run([sys.executable, str(trap), str(ROOT), str(marker), kind, target, *args],
                       cwd=ROOT / entry.cwd, capture_output=True, timeout=HANG_TIMEOUT)
    return marker.exists()


def test_the_entries_that_import_the_client_only_never_start_the_service(tmp_path):
    for name in IMPORTS_ONLY:
        assert not _starts_the_service(tmp_path, R.entry_named(name)), name
    assert _starts_the_service(tmp_path, R.entry_named("english-codes"))  # the trap sees a start


def test_the_build_entry_builds_the_service():
    """`_Service.ran` takes a successful lake-build as a current ve_service: its step builds the default targets."""
    import tomllib
    lakefile = tomllib.loads((ROOT / "lean/lakefile.toml").read_text())
    assert R.SERVICE_TARGET in lakefile["defaultTargets"]
    assert R.entry_named(R.BUILD).write == (("lake", "build"),)
    assert R.SERVICE_TARGET in {exe["name"] for exe in lakefile["lean_exe"]}


# The writers this batch added to their owners


def test_the_frozen_inventory_writer_reproduces_the_committed_inventory():
    sys.path.insert(0, str(ROOT / "lean/VE/Route"))
    import frozen
    assert frozen.inventory_text() == (ROOT / "lean/VE/Route/frozen-sources.sha256").read_text()


def test_assurance_doc_check_fails_on_a_stale_table(tmp_path, monkeypatch):
    import assurance_manifest
    assert assurance_manifest.main(["--check"]) == 0
    stale = tmp_path / "assurance-manifest.md"
    stale.write_text(assurance_manifest.DOC.read_text().replace("<!-- END GENERATED -->", "stale\n<!-- END GENERATED -->", 1))
    monkeypatch.setattr(assurance_manifest, "DOC", stale)
    assert assurance_manifest.main(["--check"]) == 1
    assert "stale" in stale.read_text()  # --check writes nothing


# The timing log (eff-20261027-1): one line per entry run, in the git common directory; VE_REGEN_LOG=off turns it
# off; a log that cannot be written changes nothing. This file runs with it off (`_no_timing_log`); these tests
# point it into tmp_path.


LOG_KEYS = {"t", "mode", "phase", "entry", "seconds", "rc", "head", "worktree"}


def _log_tree(tmp_path, monkeypatch):
    """A git repository at tmp_path with three entries: `one` (its check passes), `two` (its check fails) and
    `three` (a check, no writer); each step prints a line."""
    root = tmp_path / "tree"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    _commit(root, {"README": "x\n"}, "base")
    step = tmp_path / "step.py"
    step.write_text("import sys\nprint('step', sys.argv[1])\nsys.exit(int(sys.argv[2]))\n")
    run = lambda name, code: (sys.executable, str(step), name, str(code))  # noqa: E731
    monkeypatch.setattr(R, "GENERATED", (
        R.Generated("one", (), (run("write one", 0),), (run("check one", 0),)),
        R.Generated("two", (), (run("write two", 0),), (run("check two", 1),)),
        R.Generated("three", (), None, (run("check three", 0),))))
    monkeypatch.setattr(R, "ROOT", root)
    monkeypatch.setattr(R, "_service_digest", lambda: None)
    monkeypatch.chdir(tmp_path)
    return root


def _lines(path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []


def test_the_regen_log_gets_one_line_per_entry_run_in_the_git_common_directory(tmp_path, monkeypatch):
    root = _log_tree(tmp_path, monkeypatch)
    monkeypatch.delenv("VE_REGEN_LOG")
    log = root / ".git" / R.RegenLog.NAME
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    assert R.main(["--check"]) == 1
    assert R.main(["--write"]) == 0
    lines = _lines(log)
    assert all(set(line) == LOG_KEYS for line in lines)
    assert [(line["mode"], line["phase"], line["entry"], line["rc"]) for line in lines] == [
        ("check", "check", "one", 0), ("check", "check", "two", 1), ("check", "check", "three", 0),
        ("write", "write", "one", 0), ("write", "write", "two", 0)]
    assert all(line["head"] == head and line["worktree"] == str(root) for line in lines)
    assert all(isinstance(line["seconds"], float) and line["seconds"] >= 0 for line in lines)
    assert all(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", line["t"]) for line in lines)


def test_the_regen_log_is_not_written_when_off(tmp_path, monkeypatch):
    root = _log_tree(tmp_path, monkeypatch)
    monkeypatch.setenv("VE_REGEN_LOG", "off")
    assert R.main(["--check"]) == 1
    assert R.main(["--write"]) == 0
    assert not (root / ".git" / R.RegenLog.NAME).exists()
    assert sorted(path.name for path in tmp_path.iterdir()) == ["step.py", "tree"]


def test_an_unwritable_regen_log_changes_neither_the_exit_code_nor_the_output(tmp_path, monkeypatch, capfd):
    root = _log_tree(tmp_path, monkeypatch)
    blocker = tmp_path / "a-file"
    blocker.write_text("")
    results = {}
    for setting in ("off", str(blocker / "log.jsonl"), str(tmp_path), str(root / "log.jsonl")):
        monkeypatch.setenv("VE_REGEN_LOG", setting)
        results[setting] = [(R.main([mode]), capfd.readouterr()) for mode in ("--check", "--write")]
    assert results["off"][0][0] == 1 and "step check two" in results["off"][0][1].out
    assert results[str(blocker / "log.jsonl")] == results["off"]
    assert results[str(tmp_path)] == results["off"]
    assert results[str(root / "log.jsonl")] == results["off"]  # a writable one, for contrast
    assert len(_lines(root / "log.jsonl")) == 5
