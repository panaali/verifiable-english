"""gi-2a: the train-only files and their one accessor (docs/infra/gen-inv-design/DESIGN.md section 4, steps 1-2).

`regen_generated.train_only()` lists the train-only files; `inventory_path` gives the copy that describes the tree:
the overlay's when it is fresh, the committed one when no module its entry covers differs from the committed
declaration list's record, and otherwise a StaleInventory naming the modules, never a silent fallback (DRI
condition 1(b)). The guard below fails on a literal read of a train-only path anywhere else.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lean_statements as L  # noqa: E402
import regen_generated as R  # noqa: E402
import trust_map  # noqa: E402
from ve.backends import lean_service  # noqa: E402

LISTS = (L.STATEMENTS, L.PREDICATES, L.DECLARATIONS)
AUDITED = ("lean/VE/Audit.lean", "lean/ResponseShapeAudit.lean", "lean/axioms.txt")
OTHERS = ("lean/checkers.lock", "docs/spec/assurance-manifest.md")


def test_the_registry_names_exactly_the_train_only_files():
    assert R.train_only() == (*LISTS, *AUDITED, *OTHERS)
    assert {e.name for e in R.GENERATED if e.writer} == {"lean-statements", "lean-audit-manifests", "checker-pins",
                                                         "assurance-doc"}
    assert {e.writer for e in R.GENERATED} == {"", "train"}
    assert R.listing().count("writer: the merge train") == 4


def test_the_overlay_is_git_ignored_and_the_committed_copies_are_not():
    ignored = lambda path: subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT).returncode == 0  # noqa: E731
    assert all(ignored(f"lean/{L.OVERLAY}/{name}") for name in R.train_only())
    assert not any(ignored(name) for name in R.train_only())


def _tree(root: Path) -> Path:
    """Modules A and B, both manifests, and a committed copy of every train-only file; the declaration list records
    A and B as they are (a manifest's recorded hash is its generated text's, never compared)."""
    for name, text in {"lean/A.lean": "a\n", "lean/B.lean": "b\n", "lean/VE/Audit.lean": "audit\n",
                       "lean/ResponseShapeAudit.lean": "rs\n", **{n: f"committed {n}\n" for n in R.train_only()}}.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    (root / L.DECLARATIONS).write_text("-- header\n" + "".join(
        f"module {m} {L.source_hash(root / f'lean/{m}.lean')}\n" for m in "AB") + f"module VE.Audit {'0' * 64}\n")
    return root


def _overlay(root: Path, monkeypatch, names=LISTS) -> None:
    monkeypatch.setenv(L.SWITCH, "overlay")
    for name in names:
        L.write_inventory(name, f"overlay {name}\n", root)
    monkeypatch.delenv(L.SWITCH)


@pytest.mark.parametrize("name", R.train_only())
def test_unchanged_modules_read_the_committed_copy(tmp_path, name):
    assert L.inventory_path(name, _tree(tmp_path)) == tmp_path / name


@pytest.mark.parametrize("change, named", [
    (lambda root: (root / "lean/A.lean").write_text("a2\n"), ["A"]),
    (lambda root: (root / "lean/C.lean").write_text("c\n"), ["C"]),
    (lambda root: (root / "lean/B.lean").unlink(), ["B"]),
    (lambda root: (root / L.DECLARATIONS).write_text("module A broken\n"), ["A", "B"]),
])
def test_a_changed_module_with_no_overlay_is_a_stale_error_naming_it(tmp_path, change, named):
    root = _tree(tmp_path)
    change(root)
    for name in (*LISTS, *AUDITED):
        with pytest.raises(L.StaleInventory, match=rf"{name} is stale: {len(named)} modules .*\({', '.join(named)}\)"):
            L.inventory_path(name, root)
        assert L.inventory_status(name, root) == (root / name, named)
    assert [L.inventory_path(name, root) for name in OTHERS] == [root / name for name in OTHERS]


def test_a_fresh_overlay_is_read_and_a_stale_one_is_an_error(tmp_path, monkeypatch):
    root = _tree(tmp_path)
    (root / "lean/A.lean").write_text("a2\n")
    _overlay(root, monkeypatch)
    assert [L.inventory_path(name, root) for name in LISTS] == [L.overlay_copy(name, root) for name in LISTS]
    with pytest.raises(L.StaleInventory, match=r"\(A\)"):  # the manifests' entry has no overlay
        L.inventory_path(AUDITED[0], root)
    (root / "lean/A.lean").write_text("a3\n")
    with pytest.raises(L.StaleInventory, match=r"1 modules .*\(A\)"):
        L.inventory_path(L.STATEMENTS, root)
    (root / "lean/A.lean").write_text("a\n")  # back to what the committed copy records
    assert L.inventory_path(L.STATEMENTS, root) == root / L.STATEMENTS


@pytest.mark.parametrize("spoil", [
    lambda root, mp: (root / "lean/A.lean").write_text("a3\n") and _overlay(root, mp, LISTS[:2]),  # one file left
    lambda root, mp: L.overlay_copy(L.DECLARATIONS, root).write_text("edited\n"),     # a file not as stamped
    lambda root, mp: L.overlay_copy(L.PREDICATES, root).unlink(),
    lambda root, mp: L._stamp_path(R.entry_named("lean-statements"), root).write_text("{"),
    lambda root, mp: L._stamp_path(R.entry_named("lean-statements"), root).unlink(),
])
def test_an_incomplete_or_altered_overlay_is_not_fresh(tmp_path, monkeypatch, spoil):
    root = _tree(tmp_path)
    (root / "lean/A.lean").write_text("a2\n")
    _overlay(root, monkeypatch)
    assert L.inventory_path(L.STATEMENTS, root) == L.overlay_copy(L.STATEMENTS, root)
    spoil(root, monkeypatch)
    with pytest.raises(L.StaleInventory, match=r"\(A\)"):
        L.inventory_path(L.STATEMENTS, root)


def test_the_pins_and_the_doc_cover_no_module_and_their_overlay_follows_the_committed_copy(tmp_path, monkeypatch):
    root = _tree(tmp_path)
    (root / "lean/A.lean").write_text("a2\n")
    _overlay(root, monkeypatch, OTHERS)
    assert [L.inventory_path(name, root) for name in OTHERS] == [L.overlay_copy(name, root) for name in OTHERS]
    (root / OTHERS[0]).write_text("main's new pins\n")  # a merge of main: the overlay was made from another lock
    assert [L.inventory_path(name, root) for name in OTHERS] == [root / OTHERS[0], L.overlay_copy(OTHERS[1], root)]


def test_the_service_client_reads_its_pins_through_the_accessor(tmp_path, monkeypatch):
    root = _tree(tmp_path)
    monkeypatch.setattr(lean_service, "ROOT", root)
    assert lean_service.build_lock() == root / OTHERS[0]
    _overlay(root, monkeypatch, OTHERS[:1])
    assert lean_service.build_lock() == L.overlay_copy(OTHERS[0], root)
    monkeypatch.setattr(lean_service, "BUILD_LOCK", tmp_path / "test.lock")
    assert lean_service.build_lock() == tmp_path / "test.lock"


@pytest.mark.parametrize("switch, target", [(None, "committed"), ("", "committed"), ("committed", "committed"),
                                            ("overlay", "overlay"), ("Overlay", None), ("1", None)])
def test_writers_write_the_committed_path_unless_the_overlay_is_asked_for(tmp_path, monkeypatch, switch, target):
    root = _tree(tmp_path)
    if switch is not None:
        monkeypatch.setenv(L.SWITCH, switch)
    if target is None:
        with pytest.raises(SystemExit, match="expected 'overlay' or 'committed'"):
            L.inventory_target(L.STATEMENTS, root)
    else:
        written = L.write_inventory(L.STATEMENTS, "new\n", root)
        assert written == (root / L.STATEMENTS if target == "committed" else L.overlay_copy(L.STATEMENTS, root))
        assert written.read_text() == "new\n"


def test_write_refuses_a_text_of_other_sources_and_the_accessor_refuses_other_files(tmp_path, monkeypatch):
    root = _tree(tmp_path)
    inputs = L.lean_inputs(root)
    assert set(inputs) == {"A", "B"}
    (root / "lean/A.lean").write_text("a2\n")
    monkeypatch.setenv(L.SWITCH, "overlay")
    with pytest.raises(SystemExit, match="a source changed"):
        L.write_inventory(L.STATEMENTS, "dump of the old tree\n", root, inputs)
    assert not L.overlay_copy(L.STATEMENTS, root).exists()
    for name in ("lean/A.lean", "tools/trust-classes.json", "lean/statements", "lean/*.txt"):
        with pytest.raises(ValueError, match="is not a train-only file"):
            L.inventory_path(name, root)


@pytest.mark.parametrize("count, tail", [(5, "M4)"), (6, "M4, and 1 more)")])
def test_the_stale_error_names_five_modules_and_counts_the_rest(count, tail):
    assert f"{count} modules" in str(L.StaleInventory("x", [f"M{i}" for i in range(count)], "c")) and \
        tail in str(L.StaleInventory("x", [f"M{i}" for i in range(count)], "c"))


def test_scan_tree_hashes_the_manifest_copy_the_accessor_gives(tmp_path, monkeypatch):
    root = _tree(tmp_path)
    (root / "lean/A.lean").write_text("a2\n")
    manifest = "-- the overlay's manifest\n"
    monkeypatch.setenv(L.SWITCH, "overlay")
    L.write_inventory(L.DECLARATIONS, "".join(f"module {m} {h}\n" for m, h in {
        **L.lean_inputs(root), "VE.Audit": L.hashlib.sha256(manifest.encode()).hexdigest(),
        "ResponseShapeAudit": L.source_hash(root / "lean/ResponseShapeAudit.lean")}.items()), root)
    for name in (*LISTS[:2], *AUDITED[1:]):
        L.write_inventory(name, (root / name).read_text(), root)
    L.write_inventory(AUDITED[0], manifest, root)
    assert trust_map.scan_tree(root)[3] == set()
    L.write_inventory(L.PREDICATES, "module A\nmodule B\nmodule VE.Audit\nmodule ResponseShapeAudit\nA.p@A\n", root)
    assert trust_map.read_tree(root)[2] == {("A", "A.p")}  # the overlay's list, not the committed one
    L.overlay_copy(AUDITED[0], root).write_text("-- not as stamped\n")  # now the committed manifest is hashed
    assert trust_map.scan_tree(root)[3] == {"VE/Audit.lean"}


# The guard (DRI condition 1(b)): a literal train-only path joined onto a path (tools/, lean/: any; tests/: the
# checkout's, so a fixture tree under tmp_path is not a read) or bound to a module-level name.
ALLOWED = {  # (file, train-only path): why it may still read the path itself
    **{(f, "lean/checkers.lock"): "a pin reader gi-2b merges into its one pin reader (DESIGN.md 4 step 5)"
       for f in ("tools/answer_cutoff.py", "tools/gate.py", "tools/gate_collection.py", "tools/lean_first_cache.py",
                 "tools/lean_output_diff.py", "tools/lean_share.py", "tools/rust_build.py")},
    ("tools/test_map_recorder.py", "lean/checkers.lock"): "records that a test read the file; reads no key",
}


def literal_reads(source: str, anywhere: bool) -> list[tuple[int, str]]:
    tree, roots, found = ast.parse(source), set(), []

    def rooted(node) -> bool:
        while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            node = node.left
        return isinstance(node, ast.Name) and node.id in roots or any(
            isinstance(n, ast.Name) and n.id == "__file__" for n in ast.walk(node))

    def named(node) -> list[str]:
        value = node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None
        return [p for p in R.train_only() if value and (value == p or value.endswith("/" + p) or p.endswith("/" + value))]
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
            if rooted(node.value):
                roots |= {t.id for t in (node.targets if isinstance(node, ast.Assign) else [node.target])
                          if isinstance(t, ast.Name)}
            found += [(node.lineno, p) for p in named(node.value)]
    found += [(node.lineno, p) for node in ast.walk(tree) if isinstance(node, ast.BinOp)
              and isinstance(node.op, ast.Div) and (anywhere or rooted(node.left)) for p in named(node.right)]
    return sorted(set(found))


@pytest.mark.parametrize("source, anywhere, reads", [
    ('ROOT = Path(__file__).parent\nx = ROOT / "lean/declarations.txt"\n', False, ["lean/declarations.txt"]),
    ('ROOT = Path(__file__).parent\nLEAN = ROOT / "lean"\nx = LEAN / "VE" / "Audit.lean"\n', False, ["lean/VE/Audit.lean"]),
    ('LOCK = "lean/checkers.lock"\n', False, ["lean/checkers.lock"]),
    ('def f(root):\n    return root / "lean/statements.txt"\n', True, ["lean/statements.txt"]),
    ('def f(tmp_path):\n    return tmp_path / "lean/statements.txt"\n', False, []),
    ('x = inventory_path("lean/axioms.txt")\n', False, []),
    ('"""Reads lean/axioms.txt."""\nx = ("lean/axioms.txt",)\n', True, []),
    ('ROOT = Path(__file__).parent\nx = ROOT / "lean/statements.txt.bak"\n', False, []),
])
def test_the_guard_sees_a_literal_read_and_nothing_else(source, anywhere, reads):
    assert [p for _, p in literal_reads(source, anywhere)] == reads


def test_no_train_only_path_is_read_outside_the_accessor():
    files = sorted({*ROOT.glob("tools/**/*.py"), *ROOT.glob("lean/**/*.py"), *ROOT.glob("tests/**/*.py")})
    found = {(path.relative_to(ROOT).as_posix(), p): line for path in files if ".lake" not in path.parts
             for line, p in literal_reads(path.read_text(), path.relative_to(ROOT).parts[0] != "tests")}
    assert sorted(set(found) - set(ALLOWED)) == []
    assert sorted(set(ALLOWED) - set(found)) == [], "an allow-list entry that no longer reads the path goes"
