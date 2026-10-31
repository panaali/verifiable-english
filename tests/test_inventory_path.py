"""gi-2a: the train-only files and their one accessor (docs/infra/gen-inv-design/DESIGN.md section 4, steps 1-2).

`regen_generated.train_only()` lists the train-only files; `inventory_path` gives the copy that describes the tree:
the overlay's when it is fresh, the committed one when no module its entry covers differs from the committed
declaration list's record, and otherwise a StaleInventory naming the modules, never a silent fallback (DRI
condition 1(b)). The guard below fails on a literal read of a train-only path anywhere else.
"""
from __future__ import annotations

import ast
from collections import Counter
import functools
import json
from pathlib import Path
import re
import subprocess
import sys
import textwrap

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


# (file, function or "" for module level, train-only path): why it may still name or read the path itself. Keyed by
# function, so a new read of an allowed path elsewhere in the same file still fails.
PIN_READERS = {"tools/answer_cutoff.py": ("", "pinned"), "tools/gate.py": ("main",),
               "tools/gate_collection.py": ("build_rust",), "tools/lean_first_cache.py": ("pinned_checkers",),
               "tools/lean_output_diff.py": ("", "save_baseline"), "tools/lean_share.py": ("", "pinned", "_read_pins"),
               "tools/rust_build.py": ("", "pinned_digests"), "ve/backends/rust_jsonl.py": ("", "run"),
               "research/defeasible/baseline.py": ("main",)}
INVENTORY_NAMES = ("lean/statements.txt", "lean/predicates.txt", "lean/declarations.txt", "lean/axioms.txt")
ALLOWED = {
    **{(f, where, "lean/checkers.lock"): "a pin reader gi-2b merges into its one pin reader (DESIGN.md 4 step 5)"
       for f, functions in PIN_READERS.items() for where in functions},
    ("tools/test_map_recorder.py", "", "lean/checkers.lock"): "records that a test read the file; reads no key",
    ("ve/backends/lean_service.py", "_spawn", "lean/checkers.lock"):
        "names the lock in its refusal when the accessor fails; reads the pins through `build_lock` (the accessor)",
    ("tools/lean_first_oracle.py", "", "lean/checkers.lock"):
        "hashes a revision's frozen files (git ls-tree); reads no key",
    ("tools/lean_share.py", "lean_tree", "lean/checkers.lock"): "leaves the pins out of HEAD's tree hash; reads no key",
    **{("tools/regen_generated.py", "", path): "the registry: the one list of train-only files"
       for path in R.train_only()},
    **{("lean/audit.py", "", path): "the manifests' writer names its outputs; it reads them through inventory_path"
       for path in ("lean/VE/Audit.lean", "lean/ResponseShapeAudit.lean")},
    **{("tools/trust_mutants.py", "", path): "names the inventories a check-only change regenerates; reads none"
       for path in INVENTORY_NAMES},
    **{("tools/architecture_numbers.py", "", path):
       "counts the lines of a revision's blobs (`read_tree`), not the checkout's"
       for path in INVENTORY_NAMES},
    ("tools/assurance_manifest.py", "document", "docs/spec/assurance-manifest.md"):
        "the hand-written template of the document; --check compares the accessor's copy with it",
    ("tools/repo_map.py", "lean_dispatch", "lean/statements.txt"):
        "asks whether the tree has a list at all; reads it through inventory_path",
    ("tools/trust_map.py", "rev_paths", "lean/statements.txt"): "a revision's archive (`extract_rev`): its own list",
    **{("tests/test_regen_generated.py", "test_gitattributes_is_generated_from_the_registry", path):
       "asks git for the path's merge attribute; reads no copy" for path in ("lean/VE/Audit.lean", "lean/axioms.txt",
                                                                            "lean/checkers.lock")},
    ("tests/test_regen_generated.py", "", "lean/checkers.lock"): "FAKE_USER reads the pins of the tmp tree it is given",
    ("tests/test_answer_cutoff.py", "test_timeouts_and_data_reads_of_the_pins_are_recorded", "lean/checkers.lock"):
        "its child reads the pins outside the client to show the recorder files that read as data",
}
SITES = {("tools/gate.py", "main", "lean/checkers.lock"): 2,  # an allowed function's lines, when more than one
         ("ve/backends/lean_service.py", "_spawn", "lean/checkers.lock"): 2}
GUARD = "tests/test_inventory_path.py"  # its cases are sources that read the paths


# The guard (DRI condition 1(b)) fails on a literal read of a train-only path, whatever its spelling (review F1). It
# parses every tracked Python file but docs/ and folds each expression to its possible spellings: strings, f-strings,
# `+`, `/`, `%`, `.format`, `Path`, `joinpath`, `os.path.join`, `str.join`, `glob`, `dict`/`zip`, comprehensions,
# subscripts and dict literals (a key, a value or both, as the read takes them: `_held`), through local and module
# names, tuple unpacking, loop variables, attributes the file sets (`self.LOCK`, `C.LOCK`), calls, constructors and
# fixtures of the same file, pytest's `parametrize` (`_parametrized`), the registry (`entry_named(...).paths`,
# `train_only()`, the registry modules' own names by value) and the constants other modules export (`exported`,
# `module.NAME` through the file's imports). So `ROOT / "lean/x"`, `open("lean/x")`, a path in a local variable, a
# module tuple, a dict or a parametrize list and `audit.ROOT / LOCK` are one case. Outside tests a path may be spelled
# only for the accessor (its calls and its own body), in a docstring or in prose: the guard fails where a path is first
# spelled. In tests it fails on a read (a join, `open`, `Path`, `.read_text`; not `.name` nor a comparison) onto a tree
# the test did not make; `tmp_path` and what is made from it are the test's own. What the guard cannot fold (a parameter
# nothing passes, an attribute the file never sets) is unknown, so a read of a path onto it fails: never the test's own
# tree (review F7). A string that parses as Python is a child script and is scanned too; a command's words are scanned
# as paths. A file name split inside its stem is not a literal (`can_spell`). Folds are memoised per scope and every set
# of spellings is cut short as it is made (`_short`, `_joined`), and each file's tree is dropped once scanned, so the
# scan of the whole tree stays within a fixed memory bound (DRI note 2026-10-31: under 2 GB).
HOLE, OWN_TREE = "\0", "\1"  # in a spelling: a part the file does not say; a tree the test made
ACCESSORS = {"inventory_path", "inventory_status", "overlay_copy", "inventory_target", "write_inventory"}
TREES = {"tmp_path", "tmp_path_factory", "tmpdir", "mkdtemp", "mktemp", "TemporaryDirectory"}
JOINS = {"Path", "PurePath", "PosixPath", "joinpath", "glob", "rglob", "join"}  # the receiver, then each argument
SAME = {"str", "resolve", "absolute", "fspath", "abspath", "normpath", "realpath", "expanduser", "as_posix", "sorted",
        "list", "tuple", "set", "reversed"}
READS = {"open", "read_text", "read_bytes"}
NAMES_OF = {"name", "stem", "suffix"}  # a path's file name: not a read
MERGES = {"dict", "zip", "items", "keys", "values", "get", "copy", "pop", "setdefault", "enumerate", "chain",
          "param"}  # what they give holds what they are given
SHELLS = {"run", "check_output", "check_call", "call", "Popen", "system", "popen", "getoutput"}
DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
SHORT = 64
SPACE = re.compile(r"\s")  # a text with one is prose or a command, not a path
EXPORTED = {f"{module.__name__}.{name}": frozenset({value}) for module in (L, R) for name, value in vars(module).items()
            if isinstance(value, str) and value in R.train_only()}  # {module.NAME: its spellings}: the registry's names


class _Item(ast.expr):
    """The `at`th item of what `value` gives, bound by `a, b = value`."""
    _fields = ("value",)

    def __init__(self, value, at: int):
        super().__init__(value=value)
        self.at = at


def _called(node: ast.Call) -> str:
    return node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")


@functools.cache
def _returns(function) -> list:
    """The values `function` itself returns or yields (a lambda: its body), not those of a function inside it."""
    if isinstance(function, ast.Lambda):
        return [function.body]
    found, todo = [], list(ast.iter_child_nodes(function))
    while todo:
        node = todo.pop()
        if isinstance(node, (ast.Return, ast.Yield)) and node.value is not None:
            found.append(node.value)
        if not isinstance(node, DEFS):
            todo.extend(ast.iter_child_nodes(node))
    return found


def _registry(node) -> tuple[str, ...] | None:
    """`entry_named("name").paths`: the registry's own list."""
    if isinstance(node, ast.Attribute) and node.attr == "paths" and isinstance(node.value, ast.Call) and \
            _called(node.value) == "entry_named" and node.value.args and isinstance(node.value.args[0], ast.Constant):
        return R.entry_named(node.value.args[0].value).paths
    return None


def _joined(parts: list[set[str]], separator: str = "") -> set[str]:
    """Each way to join one spelling of each part, cut short (`_short`) after each part: never the product of all."""
    spellings = {""}
    for part in parts:
        spellings = _short({left + (separator if left else "") + right for left in spellings for right in part})
    return spellings


def _short(spellings: set[str]) -> set[str]:
    """`spellings` cut to what `spelled` and the own-tree test read, so a fold stays small: whether a tree the test made
    is in it, and the text after the last hole, its last four path components at most (a cut prefix is a hole). Over
    SHORT spellings, each keeps only the train-only paths its last word spells (after a hole), and the rest are one
    hole: unknown, never the test's own tree, though some of them were (DRI note 2026-10-31: refused, never safe)."""
    if spellings == {HOLE}:
        return spellings
    short = set()
    for text in spellings:
        own, rest = OWN_TREE * (OWN_TREE in text), text.rsplit(OWN_TREE, 1)[-1]
        if not SPACE.search(rest):
            hole, parts = HOLE in rest or rest.count("/") > 3, rest.rsplit(HOLE, 1)[-1].split("/")
            rest = HOLE * hole + "/".join(parts[-4:])
        short.add(own + rest)
    if len(short) > SHORT:
        short = {OWN_TREE * (OWN_TREE in text) + HOLE + path for text in short
                 for path in spelled(([""] + text.rsplit(OWN_TREE, 1)[-1].split())[-1])} | {HOLE}
    return short


class Spellings:
    """What one file's expressions can spell: `scope` holds each function's names, each with its values."""

    def __init__(self, tree: ast.Module, exported: dict[str, frozenset[str]], module: str = ""):
        self.module, self.tree, self.exported, self.scope = module, tree, exported, {tree: {}}
        self.defs, self.calls, self.functions = {}, {}, []
        self.attributes, self.classes, self.members = {}, set(), {}  # `x.NAME = ...` and class bodies; `D[k](...)`
        self.inits: dict[int, str] = {}  # each `__init__`: its class's name
        self.folded: dict[tuple[int, ...], set[str]] = {}
        self.imports = {alias.asname or alias.name.split(".")[0]: f"{node.module.rsplit('.', 1)[-1]}.{alias.name}"
                        if isinstance(node, ast.ImportFrom) and node.module else alias.name.rsplit(".", 1)[-1]
                        for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                        for alias in node.names}
        self._bind_names(tree, (self.scope[tree],))
        self.decorated = {id(d): owner for owner in ast.walk(tree) for d in getattr(owner, "decorator_list", ())}
        for node, chain in self.functions:
            self._bind_parameters(node, chain)

    def use(self, exported: dict[str, frozenset[str]]) -> Spellings:
        """The same file, folded again with the names other modules export."""
        self.exported, self.folded = {**EXPORTED, **exported}, {}
        return self

    def _bind(self, env, target, value, chain) -> None:
        if isinstance(target, ast.Name):
            env.setdefault(target.id, []).append((value, chain))
        elif isinstance(target, (ast.Tuple, ast.List)):
            same = isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(target.elts)
            for at, item in enumerate(target.elts):
                item_value = value.elts[at] if same else _Item(value, at) if value is not None else None
                self._bind(env, item, item_value, chain)
        elif isinstance(target, ast.Attribute):  # `self.LOCK = ...`: what any `.LOCK` of the file may give
            self.attributes.setdefault(target.attr, []).append((value, chain))

    def _bind_names(self, node, chain) -> None:
        env = chain[-1]
        if isinstance(node, ast.ClassDef):
            self.classes.add(node.name)
        for child in ast.iter_child_nodes(node):
            inner = chain
            if isinstance(child, DEFS) and getattr(child, "name", "") in ACCESSORS:
                continue  # the accessor itself
            if isinstance(child, DEFS):
                inner = (*chain, self.scope.setdefault(child, {}))
                self.functions.append((child, inner))
                if isinstance(node, ast.ClassDef) and child.name == "__init__":
                    self.inits[id(child)] = node.name  # `C(...)` passes its parameters
                if not isinstance(child, ast.Lambda):
                    self.defs[child.name] = child, inner
            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    self._bind(env, target, child.value, chain)
                    if isinstance(node, ast.ClassDef):  # a class attribute: also `self.NAME`, `cls.NAME`, `C.NAME`
                        self._bind(self.attributes, target, child.value, chain)
                    if isinstance(child.value, ast.Lambda) and isinstance(target, ast.Name):
                        self.defs[target.id] = child.value, (*chain, self.scope.setdefault(child.value, {}))
                    if isinstance(child.value, (ast.Dict, ast.List, ast.Tuple)) and isinstance(target, ast.Name):
                        held = child.value.values if isinstance(child.value, ast.Dict) else child.value.elts
                        for member in (m for m in held if isinstance(m, (ast.Lambda, ast.Name))):  # `D[k](...)`
                            self.members.setdefault(id(member) if isinstance(member, ast.Lambda) else member.id,
                                                    set()).add(f"{target.id}[]")
            elif isinstance(child, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)) and child.value is not None:
                self._bind(env, child.target, child.value, chain)
                if isinstance(node, ast.ClassDef):
                    self._bind(self.attributes, child.target, child.value, chain)
            elif isinstance(child, (ast.For, ast.comprehension)):
                self._bind(env, child.target, ast.Starred(child.iter), chain)
            elif isinstance(child, ast.withitem) and child.optional_vars is not None:
                self._bind(env, child.optional_vars, child.context_expr, chain)
            elif isinstance(child, ast.Call):
                self.calls.setdefault(_called(child), []).append((child, chain))
                if isinstance(child.func, ast.Subscript) and isinstance(child.func.value, ast.Name):
                    self.calls.setdefault(f"{child.func.value.id}[]", []).append((child, chain))
            self._bind_names(child, inner)

    def _parametrized(self, node, chain) -> dict[str, list]:
        """{parameter: [(value, scope)]} that pytest passes `node`: each `parametrize` on it, on its class, in
        `pytestmark` or `metafunc.parametrize` naming the parameter (the last three for every function of the file
        with a parameter of that name), and a fixture's `params` as its `request.param`. An `indirect` name goes to
        its fixture's `request.param` when the file defines that fixture."""
        own = [d for d in getattr(node, "decorator_list", ()) if isinstance(d, ast.Call)]
        found: dict[str, list] = {}
        for decorator in own:
            params = [k.value for k in decorator.keywords if k.arg == "params"]
            if _called(decorator) == "fixture" and params:
                for name in (a.arg for a in node.args.args):
                    found.setdefault(f"{name}.param", []).append((ast.Starred(params[0]), chain[:-1]))
        for call, caller in self.calls.get("parametrize", []):
            if call not in own and not self._shared(call, node):
                continue
            names = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg == "argnames"), None)
            names = [n.strip() for n in names.value.split(",")] if isinstance(names, ast.Constant) and isinstance(
                names.value, str) else [getattr(n, "value", None) for n in getattr(names, "elts", ())]
            given = call.args[1] if len(call.args) > 1 else next(
                (k.value for k in call.keywords if k.arg == "argvalues"), None)
            indirect = next((k.value for k in call.keywords if k.arg == "indirect"), None)
            indirect = {getattr(n, "value", None) for n in getattr(indirect, "elts", ())} | (
                set(names) if getattr(indirect, "value", False) is True else set())
            rows = [(row, inner) for source, inner in (self._sources(given, caller) if given is not None else [])
                    for row in (source.elts if isinstance(source, (ast.List, ast.Tuple)) else [ast.Starred(source)])]
            for at, name in enumerate(names):
                values = [(row if len(names) == 1 else _Item(row, at), inner) for row, inner in (
                    (ast.Tuple(row.args) if isinstance(row, ast.Call) and _called(row) == "param" else row, inner)
                    for row, inner in rows)]
                if name in indirect and name in self.defs:
                    fixture, inner = self.defs[name]
                    for request in (a.arg for a in fixture.args.args):
                        inner[-1].setdefault(f"{request}.param", []).extend(values)
                elif name is not None:
                    found.setdefault(name, []).extend(values)
        return found

    def _shared(self, call, node) -> bool:
        """Whether `parametrize` `call` reaches `node` though not its decorator: on its class, in `pytestmark` or
        through `metafunc` (each binds by parameter name)."""
        owner = self.decorated.get(id(call))
        return owner is None or isinstance(owner, ast.ClassDef) and node in owner.body

    def _bind_parameters(self, node, chain) -> None:
        """Each parameter takes what pytest's `parametrize` passes it (`_parametrized`), what the file's calls pass it
        (by name, or through a dict or list of callables: `D[k](...)`) and its default; with none, a function of this
        file of its name (a pytest fixture) gives its value, and otherwise it is unknown: a hole, never the test's own
        tree (review F7). A test's own tree is only one it makes (`TREES`)."""
        args = node.args
        names = [a.arg for a in (*args.posonlyargs, *args.args)]
        defaults = dict(zip(reversed(names), reversed(args.defaults)))
        names = names[1:] if names[:1] in (["self"], ["cls"]) else names
        defaults |= {a.arg: d for a, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None}
        calls = [c for name, (fn, _) in self.defs.items() if fn is node for c in self.calls.get(name, [])]
        calls += [c for key in (id(node), getattr(node, "name", None)) for held in self.members.get(key, ())
                  for c in self.calls.get(held, [])]
        calls += self.calls.get(self.inits[id(node)], []) if id(node) in self.inits else []
        given = self._parametrized(node, chain)
        for name, values in given.items():
            if "." in name:  # `request.param`
                chain[-1].setdefault(name, []).extend(values)
        for at, name in enumerate((*names, *(a.arg for a in args.kwonlyargs))):
            values = [(defaults[name], chain[:-1])] if name in defaults else []
            values += given.get(name, [])
            for call, caller in calls:
                values += [(call.args[at], caller)] if at < min(len(names), len(call.args)) else [
                    (keyword.value, caller) for keyword in call.keywords if keyword.arg == name]
            if not values and name in self.defs:
                fixture, inner = self.defs[name]
                values = [(value, inner) for value in _returns(fixture)]
            chain[-1].setdefault(name, []).extend(values or [(ast.Constant(HOLE), chain)])

    def fold(self, node, chain) -> set[str]:
        """The spellings of `node`, each folded once per scope and kept short (`_short`); a name or call met again
        inside its own folding is a hole."""
        key = (id(node), *map(id, chain))
        if key not in self.folded:
            self.folded[key] = {HOLE}
            self.folded[key] = _short(self._fold(node, chain))
        return self.folded[key]

    def _sources(self, node, chain, seen=None) -> list:
        """What a name, a call or a key of a dict literal of this file gives, as written: [(expression, its scope)].
        Each is followed once (one `seen` for the whole walk), so a name bound from many names stays linear."""
        found, seen, todo = [], set() if seen is None else seen, [(node, chain)]
        while todo:
            node, chain = todo.pop()
            if id(node) in seen:
                continue
            seen.add(id(node))
            bound = next((env[node.id] for env in reversed(chain) if node.id in env), None) if isinstance(
                node, ast.Name) and node.id not in TREES else None
            if bound is not None:
                todo += [(value, inner) for value, inner in bound if value is not None]
            elif isinstance(node, ast.Call) and _called(node) in self.defs:
                function, inner = self.defs[_called(node)]
                todo += [(value, inner) for value in _returns(function)]
            elif isinstance(node, ast.Subscript) and any(held := self._held(node.value, chain, node.slice, seen=seen)):
                todo, found = todo + held[0], found + held[1]
            else:
                found.append((node, chain))
        return found

    def _held(self, node, chain, key=None, keys=False, seen=None) -> tuple[list, list]:
        """An item of what `node` gives: ([(expression, scope)] taken out of dict literals, [(expression, scope)] of
        the rest, each its own item). Out of a dict literal: its keys (`keys`: iterating, `.keys()`), else its value
        at constant `key` (every value when `key` or one of its keys is not a constant, `**other` included)."""
        key = key.value if isinstance(key, ast.Constant) and key.value is not None else None
        taken, rest = [], []
        for source, inner in self._sources(node, chain, seen):
            if isinstance(source, ast.Dict):
                exact = not keys and key is not None and all(isinstance(k, ast.Constant) for k in source.keys)
                taken += [(value if k is None or not keys else k, inner) for k, value in zip(source.keys, source.values)
                          if not exact or k.value == key]
            elif isinstance(source, ast.DictComp):
                taken.append((source.key if keys else source.value, inner))
            else:
                rest.append((source, inner))
        return taken, rest

    def _sequence(self, node, chain, seen=None) -> bool:
        """Whether `node` gives a tuple or a list as written: a display, a comprehension, `tuple(...)`, `list(...)`,
        `sorted(...)` or a `+` of one (each `+` looked at once: `x = x + ...`)."""
        seen = set() if seen is None else seen
        return any(isinstance(source, (ast.Tuple, ast.List, ast.ListComp)) or isinstance(source, ast.Call) and _called(
            source) in ("tuple", "list", "sorted") or isinstance(source, ast.BinOp) and isinstance(source.op, ast.Add)
            and id(source) not in seen and not seen.add(id(source))
            and (self._sequence(source.left, inner, seen) or self._sequence(source.right, inner, seen))
            for source, inner in self._sources(node, chain))

    def _fold(self, node, chain) -> set[str]:
        fold = lambda item: self.fold(item, chain)  # noqa: E731
        if isinstance(node, _Item):
            return set().union(*[self.fold(value.elts[node.at], inner) if isinstance(value, (ast.Tuple, ast.List))
                                 and node.at < len(value.elts) else {_registry(value)[node.at]}
                                 if node.at < len(_registry(value) or ()) else self.fold(value, inner)
                                 for value, inner in self._sources(node.value, chain)]) or {HOLE}
        union = lambda items: set().union(*map(fold, items)) if items else {HOLE}  # noqa: E731
        if isinstance(node, ast.Starred):  # what iterating gives: a dict literal's keys (`_held`)
            taken, rest = self._held(node.value, chain, keys=True)
            return set().union(*[self.fold(*item) for item in taken + rest]) or {HOLE} if taken else fold(node.value)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {node.value}
        if isinstance(node, ast.JoinedStr):
            return _joined([fold(value) for value in node.values])
        if isinstance(node, ast.FormattedValue):
            return fold(node.value)
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Mod):
                return {re.sub(r"%[sr]", HOLE, left) for left in fold(node.left)}
            if isinstance(node.op, ast.Add) and any(self._sequence(side, chain) for side in (node.left, node.right)):
                return fold(node.left) | fold(node.right)  # two tuples or lists: their items, not one text
            if isinstance(node.op, (ast.Add, ast.Div)):
                return _joined([fold(node.left), fold(node.right)], "/" if isinstance(node.op, ast.Div) else "")
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            return union(node.elts)
        if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            return fold(node.elt)
        if isinstance(node, ast.Subscript):  # a dict literal's value at the key it names (`_sources`), never a key
            sources = self._sources(node, chain)
            if len(sources) == 1 and sources[0][0] is node:
                return fold(node.value)
            return set().union(*[self.fold(source, inner) for source, inner in sources]) or {HOLE}
        if isinstance(node, ast.Dict):  # its keys and values (`P.items()`, `dict(P)`); a key and iterating: above
            return union([*(key for key in node.keys if key is not None), *node.values])
        if isinstance(node, ast.DictComp):
            return union([node.key, node.value])
        if isinstance(node, ast.IfExp):
            return union([node.body, node.orelse])
        if isinstance(node, ast.BoolOp):
            return union(node.values)
        if isinstance(node, ast.Name):
            if node.id in TREES:
                return {OWN_TREE}
            for env in reversed(chain):
                if node.id in env:  # a module name of the registry's own modules: also its value (`EXPORTED`)
                    return set().union(*[self.fold(value, inner) for value, inner in env[node.id]],
                                       self.exported.get(f"{self.module}.{node.id}", set()) if env is chain[0] else ())
            return set(self.exported.get(self.imports.get(node.id, ""), {HOLE}))
        if _registry(node):
            return set(_registry(node))
        if isinstance(node, ast.Attribute):
            owner = node.value.id if isinstance(node.value, ast.Name) else ""
            module = self.imports.get(owner, "").rsplit(".", 1)[-1]
            if f"{module}.{node.attr}" in self.exported:
                return set(self.exported[f"{module}.{node.attr}"])
            keyed = [pair for env in chain for pair in env.get(f"{owner}.{node.attr}", ())]  # a fixture's request.param
            held = self.attributes.get(node.attr, [])  # `self.LOCK`, `C.LOCK`: what the file sets it to
            given = set().union(*[self.fold(value, inner) for value, inner in keyed + held if value is not None])
            if keyed or held and (owner in ("self", "cls") or owner in self.classes):
                return given or {HOLE}
            return given | {OWN_TREE if OWN_TREE in part else HOLE for part in fold(node.value)}
        if isinstance(node, ast.Call):
            return self._fold_call(node, chain, fold)
        return {HOLE}

    def _fold_call(self, node, chain, fold) -> set[str]:
        name, receiver = _called(node), node.func.value if isinstance(node.func, ast.Attribute) else None
        if name in TREES:
            return {OWN_TREE}
        if name in ACCESSORS:
            return {HOLE}  # the accessor's copy
        if name == "train_only":
            return set(R.train_only())
        if name == "join" and isinstance(receiver, ast.Constant) and isinstance(receiver.value, str) and node.args:
            return _joined([fold(part) for part in getattr(node.args[0], "elts", node.args)], receiver.value)
        if name in JOINS and (name != "join" or getattr(receiver, "attr", "") == "path"):
            parts = ([receiver] if name in ("joinpath", "glob", "rglob") else []) + node.args
            return _joined([fold(part) for part in parts], "/") if parts else {HOLE}
        if name in ("keys", "values", "get", "pop", "setdefault") and receiver is not None:
            taken, rest = self._held(receiver, chain, node.args[0] if node.args else None, keys=name == "keys")
            if taken:  # a dict literal's keys or values, and a default
                return set().union(*[self.fold(*item) for item in taken + rest], *map(fold, node.args[1:])) or {HOLE}
        if name in MERGES:
            return set().union(*map(fold, [*node.args, *(k.value for k in node.keywords),
                                           *([receiver] if receiver else [])])) or {HOLE}
        if name in SAME or name in READS:
            first = name in ("open", "str", "fspath") or receiver is None
            return fold(node.args[0] if first and node.args else receiver)
        if name == "removeprefix" and receiver is not None and node.args and isinstance(node.args[0], ast.Constant):
            return {text.removeprefix(node.args[0].value) for text in fold(receiver)}
        if name == "format" and receiver is not None:
            return {re.sub(r"\{[^}]*\}", HOLE, text) for text in fold(receiver)}
        passed = [*node.args, *(keyword.value for keyword in node.keywords), *([receiver] if receiver else [])]
        if any(OWN_TREE in text for part in passed for text in fold(part)):
            return {OWN_TREE}
        if name in self.defs:
            function, inner = self.defs[name]
            values = _returns(function)
            return set().union(*[self.fold(v, inner) for v in values]) if values else {HOLE}
        return {HOLE}


def spelled(text: str) -> list[str]:
    """The train-only paths `text` spells; a hole or `*` may stand for directories, never for part of the file name."""
    text = re.sub(r"/+", "/", text.replace("*", HOLE)).removeprefix("./").replace(HOLE + "/", HOLE)
    found = []
    for path in (path for path in R.train_only() if path.rsplit("/", 1)[1] in text):  # each case needs the name
        if HOLE not in text:
            found += [path] * (text == path or text.endswith("/" + path) or path.endswith("/" + text))
        else:
            tail, name = text.rsplit(HOLE, 1)[1], path.rsplit("/", 1)[1]
            found += [path] * ((tail == name or tail.endswith("/" + name)) and (tail.endswith("/" + path) or bool(
                re.fullmatch("(.*/)?" + ".*".join(map(re.escape, text.split(HOLE))), path))))
    return found


def _is_read(node, text: str, parent) -> bool:
    """A read: `/` onto a tree, `+` or an f-string onto a root, or `open`, `Path(...)`, a path join or `.read_text()`;
    not the file name of one (`.name`, `.stem`, `.suffix`) nor a comparison with one."""
    if isinstance(parent, ast.Compare) or isinstance(parent, ast.Attribute) and parent.attr in NAMES_OF:
        return False  # its file name, or a comparison with it
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):  # a root string and a literal: not two tuples
        return text.startswith(HOLE) and isinstance(node.right, (ast.Constant, ast.JoinedStr))
    if isinstance(node, ast.JoinedStr):
        return text.startswith(HOLE)
    if isinstance(node, ast.Call) and _called(node) == "join":
        receiver = node.func.value if isinstance(node.func, ast.Attribute) else None
        return getattr(receiver, "attr", "") == "path" or getattr(receiver, "value", "") == "/"
    return isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) or isinstance(node, ast.Call) \
        and _called(node) in JOINS | READS


def _carries(node) -> bool:
    """A name, an attribute or a call only carries a value that was spelled where it was made."""
    return isinstance(node, (ast.Name, ast.Attribute, ast.Call)) and not (
        isinstance(node, ast.Call) and _called(node) in JOINS | {"format"})


def _value(part: ast.FormattedValue, spellings: set[str]) -> str:
    """What an f-string part puts in a child script: its one spelling (quoted for `!r`, holes as `_`), `tmp_path` for
    a tree the test made, `_` when it has several."""
    if len(spellings) != 1:
        return "_"
    [text] = spellings
    if OWN_TREE in text:
        return "tmp_path"
    text = text.replace(HOLE, "_")
    return repr(text) if part.conversion == ord("r") else text


def literal_reads(source: str | Spellings, anywhere: bool, exported: dict[str, frozenset[str]] | None = None
                    ) -> list[tuple[int, str, str]]:
    """(line, train-only path, the function it is in or "") for each place `source` spells a path outside the
    accessor: where a path is first spelled (`anywhere`: tools and the like) and each read of one (in tests, onto
    a tree the test did not make), each command argument and each child script."""
    spellings = (source if isinstance(source, Spellings) else Spellings(ast.parse(source), {})).use(exported or {})
    tree, found = spellings.tree, []
    parents = {id(child): node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}

    known: dict[tuple[int, bool], set[str]] = {}

    def paths(node, chain, read=False) -> set[str]:
        if (id(node), read) not in known:
            known[id(node), read] = {
                path for text in spellings.fold(node, chain)
                if not SPACE.search(text) and (anywhere or OWN_TREE not in text)
                and (not read or _is_read(node, text, parents.get(id(node)))) for path in spelled(text)}
        return known[id(node), read]

    def child_script(node, chain, where) -> None:
        """A string that parses as Python, whole: an f-string's value is its one spelling (a made tree: `tmp_path`),
        or `_` when it has several or none (not the shortened fold, which drops what comes before a made tree)."""
        if isinstance(node, ast.JoinedStr):
            text = "".join(part.value if isinstance(part, ast.Constant) else _value(part, spellings.fold(part, chain))
                           for part in node.values)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
        else:
            return
        if ("\n" in text or "(" in text) and any(path.rsplit("/", 1)[1] in text for path in R.train_only()):
            try:
                inner = literal_reads(textwrap.dedent(text), False, exported)
            except (SyntaxError, ValueError):
                return
            found.extend((node.lineno + line - 1, path, where) for line, path, _ in inner)

    def visit(node, chain, where) -> None:
        if node in spellings.scope and node is not tree:
            chain = (*chain, spellings.scope[node])
        where = getattr(node, "name", where) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else where
        if isinstance(node, ast.Call) and _called(node) in ACCESSORS or getattr(node, "name", "") in ACCESSORS:
            return  # the accessor, a call of it or its definition
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            return  # a docstring
        if isinstance(node, ast.expr):
            child_script(node, chain, where)
            if isinstance(node, ast.Call) and _called(node) in SHELLS and (not any(
                    OWN_TREE in text for keyword in node.keywords if keyword.arg == "cwd"
                    for text in spellings.fold(keyword.value, chain)) or anywhere):
                found.extend((node.lineno, path, where) for argument in node.args
                             for text in spellings.fold(argument, chain)
                             for word in text.split() for path in spelled(word))
            if anywhere and not _carries(node):
                inner = set().union(*[paths(child, chain) for child in ast.iter_child_nodes(node)
                                      if isinstance(child, ast.expr)])
                found.extend((node.lineno, path, where) for path in paths(node, chain) - inner)
            found.extend((node.lineno, path, where) for path in paths(node, chain, read=True))
        for child in ast.iter_child_nodes(node):
            visit(child, chain, where)

    visit(tree, (spellings.scope[tree],), "")
    return sorted(set(found))


def exported_paths(files: dict[str, Spellings]) -> dict[str, frozenset[str]]:
    """{module.NAME: the spellings of train-only paths a module-level constant holds}, for the files that import it."""
    found = {}
    for name, spellings in files.items():
        tree = spellings.use({}).tree
        for target, values in spellings.scope[tree].items():
            texts = {text for value, chain in values for text in spellings.fold(value, chain) if spelled(text)}
            found.update({f"{Path(name).stem}.{target}": frozenset(texts)} if target.isupper() and texts else {})
    return found


def can_spell(source: str, exported: dict[str, str]) -> bool:
    """Whether `source` holds what a spelling of a train-only path is folded from: a file name's stem (a name split
    inside its stem is not a literal), `train_only` or a name that exports a path. Files without any are not parsed."""
    words = {path.rsplit("/", 1)[1].split(".")[0] for path in R.train_only()} | {"train_only"}
    return any(word in source for word in words) or bool(
        re.search(r"\b(%s)\b" % "|".join(re.escape(key.rsplit(".", 1)[1]) for key in {**EXPORTED, **exported}), source))


# F1 (gi-2a review): each spelling the first guard missed, in tools/ and lean/ (True) and in tests/ (False).
@pytest.mark.parametrize("source, anywhere, reads", [
    ('ROOT = Path(__file__).parent\nx = ROOT / "lean/declarations.txt"\n', False, ["lean/declarations.txt"]),
    ('ROOT = Path(__file__).parent\nLEAN = ROOT / "lean"\nx = LEAN / "VE" / "Audit.lean"\n', False, ["lean/VE/Audit.lean"]),
    ('LOCK = "lean/checkers.lock"\n', True, ["lean/checkers.lock"]),
    ('LOCK = "lean/checkers.lock"\ndef test_f():\n    return (ROOT / LOCK).read_text()\n', False, ["lean/checkers.lock"]),
    ('import audit\ndef test_f():\n    return [(ROOT / "lean" / m).read_text() for m in audit.MANIFESTS]\n', False,
     ["lean/ResponseShapeAudit.lean", "lean/VE/Audit.lean"]),
    ('def f():\n    return tuple(f"lean/{n}.txt" for n in ("statements", "axioms"))\n', True,
     ["lean/axioms.txt", "lean/statements.txt"]),
    ('def test_f():\n    assert Path(L.STATEMENTS).name in ", ".join(["lean/statements.txt"])\n', False, []),
    ('@pytest.fixture\ndef tree(tmp_path):\n    return tmp_path / "lean", 1\n'
     'def test_f(tree):\n    lean, _ = tree\n    return (lean / "axioms.txt").read_text()\n', False, []),
    ('def f(root):\n    return root / "lean/statements.txt"\n', True, ["lean/statements.txt"]),
    ('def f():\n    return open("lean/checkers.lock").read()\n', True, ["lean/checkers.lock"]),
    ('def f():\n    return Path("lean/statements.txt").read_text()\n', True, ["lean/statements.txt"]),
    ('def f(root):\n    return root.joinpath("lean", "axioms.txt").read_text()\n', True, ["lean/axioms.txt"]),
    ('import os\ndef f(root):\n    return open(os.path.join(root, "lean", "checkers.lock"))\n', True,
     ["lean/checkers.lock"]),
    ('def f(root):\n    return open(f"{root}/lean/predicates.txt")\n', True, ["lean/predicates.txt"]),
    ('def f(root):\n    name = "lean/declarations.txt"\n    return (root / name).read_text()\n', True,
     ["lean/declarations.txt"]),
    ('FILES = ("lean/axioms.txt", "lean/ResponseShapeAudit.lean")\n', True,
     ["lean/ResponseShapeAudit.lean", "lean/axioms.txt"]),
    ('def f(root):\n    return open("{}/docs/spec/{}".format(root, "assurance-manifest.md"))\n', True,
     ["docs/spec/assurance-manifest.md"]),
    ('from x import ROOT\ndef test_f():\n    return (ROOT / "lean/statements.txt").read_text()\n', False,
     ["lean/statements.txt"]),
    ('def test_f():\n    root = Path(__file__).parents[1]\n    return (root / "lean/statements.txt").read_text()\n',
     False, ["lean/statements.txt"]),
    ('import audit\ndef test_f():\n    return (audit.ROOT / "lean/axioms.txt").read_text()\n', False, ["lean/axioms.txt"]),
    ('def g(root):\n    return (root / "lean/statements.txt").read_text()\ndef test_f():\n    g(ROOT)\n', False,
     ["lean/statements.txt"]),
    ('from tools import lean_statements as L\ndef test_f():\n    return (ROOT / L.STATEMENTS).read_text()\n', False,
     ["lean/statements.txt"]),
    ('SCRIPT = """\nfrom pathlib import Path\nPath("lean/checkers.lock").read_text()\n"""\n', False, ["lean/checkers.lock"]),
    ('import lean_statements as L\ndef f():\n    fresh = dict(zip((L.STATEMENTS, L.DECLARATIONS), dump()))\n'
     '    return {name: (ROOT / name).read_text() for name in fresh}\n', True, ["lean/declarations.txt", "lean/statements.txt"]),
    ('import lean_statements as L\ndef f(path):\n    return path != ROOT / L.STATEMENTS\n', True, []),
    ('def f(tmp_path):\n    return tmp_path / "lean/statements.txt"\n', False, []),
    ('def g(root):\n    return root / "lean/statements.txt"\ndef test_f(tmp_path):\n    g(tmp_path / "t")\n', False, []),
    ('def test_f():\n    assert R.train_only()[0] == "lean/statements.txt"\n', False, []),
    ('x = inventory_path("lean/axioms.txt")\n', False, []),
    ('"""Reads lean/axioms.txt."""\nraise SystemExit("run lean/audit.py to rebuild lean/axioms.txt")\n', True, []),
    ('ROOT = Path(__file__).parent\nx = ROOT / "lean/statements.txt.bak"\n', False, []),
])
def test_the_guard_sees_a_literal_read_and_nothing_else(source, anywhere, reads):
    exported = exported_paths({"lean/audit.py": Spellings(ast.parse((ROOT / "lean/audit.py").read_text()), {})})
    assert sorted({p for _, p, _ in literal_reads(source, anywhere, exported)}) == reads


# F7 (gi-2a recheck 1): what pytest's parametrize, a dict literal or an attribute passes a read in tests, and what the
# guard cannot fold (refused); the cases after "precise" are reads the guard must not see.
PARAMETRIZE = 'import pytest\n@pytest.mark.parametrize("name", ["lean/statements.txt"])\n'


@pytest.mark.parametrize("source, reads", [
    (PARAMETRIZE + 'def test_f(name):\n    return (ROOT / name).read_text()\n', ["lean/statements.txt"]),  # PROBE F7
    ('@pytest.mark.parametrize("a, name", [(1, "lean/axioms.txt"), pytest.param(2, "lean/predicates.txt", id="p")])\n'
     'def test_f(a, name):\n    return (ROOT / name).read_text()\n', ["lean/axioms.txt", "lean/predicates.txt"]),
    ('NAMES = ["lean/declarations.txt"]\n@pytest.mark.parametrize("name", NAMES)\ndef test_f(name):\n'
     '    return open(ROOT / name)\n', ["lean/declarations.txt"]),
    ('@pytest.mark.parametrize(argnames="name", argvalues=["lean/axioms.txt"])\nclass TestX:\n'
     '    def test_f(self, name):\n        return (ROOT / name).read_text()\n', ["lean/axioms.txt"]),
    ('pytestmark = pytest.mark.parametrize("name", ["lean/axioms.txt"])\ndef test_f(name):\n'
     '    return (ROOT / name).read_text()\n', ["lean/axioms.txt"]),
    ('@pytest.fixture(params=["lean/checkers.lock"])\ndef name(request):\n    return request.param\n'
     'def test_f(name):\n    return (ROOT / name).read_text()\n', ["lean/checkers.lock"]),
    ('@pytest.fixture\ndef name(request):\n    return ROOT / request.param\n'
     '@pytest.mark.parametrize("name", ["lean/statements.txt"], indirect=True)\ndef test_f(name):\n    return name\n',
     ["lean/statements.txt"]),
    ('P = {"lock": "lean/checkers.lock", "doc": "README.md"}\ndef test_f():\n    return (ROOT / P["lock"]).read_text()\n',
     ["lean/checkers.lock"]),
    ('P = {"lock": "lean/checkers.lock"}\ndef test_f():\n    return (ROOT / P.get("lock")).read_text()\n',
     ["lean/checkers.lock"]),
    ('P = {"lean/axioms.txt": 1}\ndef test_f():\n    return [(ROOT / k).read_text() for k in P]\n', ["lean/axioms.txt"]),
    ('P = {"a": {"lock": "lean/checkers.lock"}}\ndef test_f():\n    q = P["a"]\n    return (ROOT / q["lock"]).read_text()\n',
     ["lean/checkers.lock"]),
    ('class TestX:\n    LOCK = "lean/checkers.lock"\n    def test_f(self):\n        return (ROOT / self.LOCK).read_text()\n',
     ["lean/checkers.lock"]),
    ('class TestX:\n    def setup_method(self):\n        self.name = "lean/axioms.txt"\n    def test_f(self):\n'
     '        return (ROOT / self.name).read_text()\n', ["lean/axioms.txt"]),
    ('class C:\n    LOCK = "lean/axioms.txt"\ndef test_f():\n    return (ROOT / C.LOCK).read_text()\n', ["lean/axioms.txt"]),
    ('class D:\n    def __init__(self, root):\n        self.root = root\ndef test_f():\n'
     '    return (D(ROOT).root / "lean/axioms.txt").read_text()\n', ["lean/axioms.txt"]),
    ('D = {"a": lambda root: (root / "lean/axioms.txt").read_text()}\ndef test_f():\n    D["a"](ROOT)\n',
     ["lean/axioms.txt"]),
    ('def test_f(repo):\n    return (repo / "lean/statements.txt").read_text()\n', ["lean/statements.txt"]),  # unknown
    ('def test_f(thing):\n    return (thing.root / "lean/axioms.txt").read_text()\n', ["lean/axioms.txt"]),
    ('class TestX:\n    def test_f(self):\n        return (self.root / "lean/axioms.txt").read_text()\n', ["lean/axioms.txt"]),
    ('def test_f(tmp_path):\n    run(f"""\nfrom pathlib import Path\nPath("lean/checkers.lock").read_text()\n'
     'print({tmp_path})\n""")\n', ["lean/checkers.lock"]),  # a child script's read before a made tree
    # precise
    ('P = {"lock": "lean/checkers.lock", "doc": "README.md"}\ndef test_f():\n    return (ROOT / P["doc"]).read_text()\n',
     []),
    ('P = {"lean/axioms.txt": "x.md"}\ndef test_f():\n    return [(ROOT / v).read_text() for v in P.values()]\n', []),
    ('class D:\n    def __init__(self, root):\n        self.root = root\ndef test_f(tmp_path):\n'
     '    return (D(tmp_path).root / "lean/axioms.txt").read_text()\n', []),
    ('D = {"a": lambda root: (root / "lean/axioms.txt").read_text()}\ndef test_f(tmp_path):\n    D["a"](tmp_path)\n', []),
    ('@pytest.mark.parametrize("name", ["README.md"])\ndef test_f(name):\n    return (ROOT / name).read_text()\n', []),
])
def test_the_guard_folds_what_pytest_a_dict_or_an_attribute_passes_and_refuses_the_rest(source, reads):
    assert sorted({p for _, p, _ in literal_reads(source, False)}) == reads


def test_a_fold_is_cut_as_it_is_made_and_an_overflow_is_unknown():
    """The guard ran out of memory (DRI note 2026-10-31): an f-string or a `+` chain of parts with many spellings each
    was joined into their whole product before it was cut. Each step is cut now, and a cut set is unknown, never the
    test's own tree, though one of its spellings was."""
    parts = [{f"p{at}/" for at in range(40)}] * 3 + [{"lean/statements.txt"}]
    joined = _joined(parts)
    assert len(joined) <= SHORT and {p for text in joined for p in spelled(text)} == {"lean/statements.txt"}
    many = {OWN_TREE + "/a"} | {f"d{at}/lean/statements.txt" for at in range(SHORT)}
    assert _short(many) == {HOLE, HOLE + "lean/statements.txt"}


def test_the_guard_reads_a_registry_modules_own_names_by_their_value():
    """A name the registry computes (`regen_generated.PIN_FILE`) is a path in its own module too (seeded S2)."""
    source = ('PIN_FILE = next(e for e in GENERATED if e.name == "checker-pins").paths[0]\n'
              'def _lock():\n    return json.loads((ROOT / PIN_FILE).read_text())\n')
    assert {p for _, p, _ in literal_reads(Spellings(ast.parse(source), {}, "regen_generated"), True)} == {
        "lean/checkers.lock"}
    assert literal_reads(Spellings(ast.parse(source), {}, "other"), True) == []


def test_the_file_filter_keeps_every_file_the_guard_finds_a_read_in():
    for source, anywhere, reads in [('x = open("lean/checkers.lock")\n', True, 1), ('x = open("README.md")\n', True, 0),
                                    ('import a\ny = open(a.PIN_FILE)\n', True, 1)]:
        assert can_spell(source, {"a.PIN_FILE": frozenset({"lean/checkers.lock"})}) == bool(reads)
        assert len(literal_reads(source, anywhere, {"a.PIN_FILE": frozenset({"lean/checkers.lock"})})) == reads


def test_no_train_only_path_is_read_outside_the_accessor():
    names = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    files = {name: source for name in names.split() if not name.startswith("docs/") and name != GUARD
             for source in [(ROOT / name).read_text()] if can_spell(source, {})}
    spellings = {name: Spellings(ast.parse(source), {}, Path(name).stem) for name, source in files.items()}
    exported, found = exported_paths(spellings), Counter()
    for name, source in files.items():  # each file's tree and folds are dropped once it is scanned (DRI note 10-31)
        file = spellings.pop(name)
        if can_spell(source, exported):
            found.update((name, where, p) for _, p, where in literal_reads(file, not name.startswith("tests/"), exported))
    allowed = {key: SITES.get(key, 1) for key in ALLOWED}
    assert sorted((key, sites) for key, sites in found.items() if allowed.get(key, 0) != sites) == [], \
        "a read outside the accessor, or another site in an allowed function"
    assert sorted(set(ALLOWED) - set(found)) == [], "an allow-list entry that no longer reads the path goes"
