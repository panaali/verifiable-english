"""The test selector: AST change units, map lookups, drift, the recorder, whole plans,
and the map-free `--impacted` fast path.

Synthetic graphs and maps keep most checks independent of the repository's
history; the whole-plan checks run on this checkout with a map built here.
Every cache write goes under tmp_path (XDG_CACHE_HOME).
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import textwrap
import types

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import change_units  # noqa: E402
from change_units import delta, summarize  # noqa: E402
import nested_pytest  # noqa: E402
import select_tests  # noqa: E402
import source_graph  # noqa: E402
import test_map  # noqa: E402
import test_map_recorder  # noqa: E402
import select_tests_seeds  # noqa: E402


@pytest.fixture(autouse=True)
def private_cache(tmp_path_factory, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path_factory.getbasetemp() / "cache"))
    monkeypatch.setenv("VE_TESTMAP_CACHE", str(tmp_path_factory.getbasetemp() / "maps"))
    monkeypatch.delenv("VE_TESTMAP", raising=False)
    # The synthetic library lives in `pkg/`; outside the known areas any file would change everything.
    monkeypatch.setattr(select_tests, "KNOWN_AREAS", select_tests.KNOWN_AREAS | {"pkg"})


def code_qualnames(source: str) -> set[str]:
    """Qualified names CPython gives the function code objects of `source`."""
    names, stack = set(), [compile(source, "m.py", "exec")]
    while stack:
        code = stack.pop()
        for constant in code.co_consts:
            if isinstance(constant, types.CodeType):
                stack.append(constant)
                if not constant.co_qualname.endswith(("<lambda>", "<genexpr>", "<listcomp>",
                                                      "<dictcomp>", "<setcomp>")) \
                        and constant.co_name not in ("__annotate__",) \
                        and "<generic parameters" not in constant.co_qualname \
                        and constant.co_flags & 0x2:  # CO_NEWLOCALS: a function, not a class body
                    names.add(constant.co_qualname)
    return names


QUALNAME_SOURCE = textwrap.dedent('''
    import functools

    def top(x=1):
        def inner():
            return lambda: x
        class Local:
            def method(self):
                def deep():
                    return 1
                return deep
        return inner, Local

    class Outer:
        attribute = 1
        class Nested:
            def method(self):
                return [y for y in range(3)]
        @property
        def value(self):
            return 1
        @value.setter
        def value(self, v):
            pass
        @staticmethod
        async def coroutine():
            pass

    if True:
        def conditional():
            pass
    try:
        def guarded():
            pass
    except ImportError:
        def guarded():
            pass
    try:
        pass
    except* OSError:
        def grouped():
            pass
    match 1:
        case 1:
            def matched():
                class Inside:
                    async def method(self):
                        pass
    for _ in ():
        async def looped():
            pass
    else:
        def after_loop():
            pass
''')


def test_unit_names_are_cpython_qualnames():
    assert set(summarize(QUALNAME_SOURCE, "m").units) == code_qualnames(QUALNAME_SOURCE)


def test_qualnames_of_the_repository_match_the_compiler():
    for path in ("ve/environment.py", "ve/surface/registry.py", "tools/select_tests.py",
                 "tests/conftest.py"):
        source = (ROOT / path).read_text()
        assert set(summarize(source, "m").units) == code_qualnames(source), path


def test_comments_and_docstrings_change_nothing():
    old = 'def f(x):\n    """Doc."""\n    return x  # one\n'
    new = 'def f(x):\n    """Other doc."""\n    # a comment\n    return x  # two\n'
    assert delta(summarize(old, "m"), summarize(new, "m")).empty


@pytest.mark.parametrize("old, new, expected", [
    ("def f():\n    return 1\n", "def f():\n    return 2\n", {"changed": {"f"}}),
    ("class C:\n    def m(self):\n        return 1\n",
     "class C:\n    def m(self):\n        return 2\n", {"changed": {"C.m"}}),
    ("def f():\n    def g():\n        return 1\n    return g\n",
     "def f():\n    def g():\n        return 2\n    return g\n", {"changed": {"f", "f.<locals>.g"}}),
    ("def f(x=1):\n    return x\n", "def f(x=2):\n    return x\n", {"changed": {"f"}}),
    ("X = 1\ndef f():\n    return X\n", "X = 2\ndef f():\n    return X\n", {"binds": {"X"}}),
    ("TABLE = {}\n", "TABLE = {}\nTABLE['k'] = 1\n", {"binds": {"TABLE"}}),
    ("class C:\n    a = 1\n", "class C:\n    a = 2\n", {"binds": {"C", "a"}}),
    ("X = 1\n", "X = 1\nregister(X)\n", {"effect": True}),
    ("def f():\n    pass\n", "@register\ndef f():\n    pass\n", {"decorated": {"f"}}),
    ("def f():\n    pass\n", "@functools.cache\ndef f():\n    pass\n", {"changed": {"f"}, "decorated": set()}),
    ("A = 1\nB = 2\n", "B = 2\nA = 1\n", {"effect": True}),
    ("def f():\n    pass\n", "def f():\n    pass\ndef g():\n    pass\n", {"added": {"g"}}),
    ("def f():\n    pass\ndef g():\n    pass\n", "def f():\n    pass\n", {"removed": {"g"}}),
])
def test_delta_classifies_each_kind_of_edit(old, new, expected):
    d = delta(summarize(old, "m"), summarize(new, "m"))
    for field, value in expected.items():
        assert getattr(d, field) == value, field


@pytest.mark.parametrize("old", [
    "def f():\n    return 1\n",
    "class C:\n    def f(self):\n        return 1\n",
    "def g():\n    def f():\n        return 1\n    return f\n",
    "class C:\n    @staticmethod\n    def f():\n        return 1\n",
])
def test_def_and_async_def_are_different_units(old):
    new = old.replace("def f(", "async def f(")
    d = delta(summarize(old, "m"), summarize(new, "m"))
    assert any(q.endswith("f") for q in d.changed), d
    assert not delta(summarize(new, "m"), summarize(new, "m")).changed


def test_making_a_repository_method_async_changes_it():
    # The reviewed case: `Environment._decode` turned into a coroutine selected no
    # conformance test, because both kinds of def were digested as `def`.
    source = real("ve/environment.py")
    assert "    def _decode(" in source
    changed = source.replace("    def _decode(", "    async def _decode(", 1)
    assert "Environment._decode" in delta(summarize(source, "ve.environment"),
                                          summarize(changed, "ve.environment")).changed


# One edit of each field of a def or class (named from the `ast` schema below).
DEF = "@deco\ndef f(a: int = 1) -> int:\n    '''Doc.'''\n    return a\n"
CLASS = "@deco\nclass C(Base, metaclass=M):\n    x = 1\n"
FIELD_EDITS = {
    ("def", "name"): DEF.replace("def f", "def g"),
    ("def", "args"): DEF.replace("a: int = 1", "a: int = 2"),
    ("def", "body"): DEF.replace("return a", "return -a"),
    ("def", "decorator_list"): DEF.replace("@deco", "@other"),
    ("def", "returns"): DEF.replace("-> int", "-> str"),
    ("def", "type_params"): DEF.replace("def f(", "def f[T]("),
    ("class", "name"): CLASS.replace("class C", "class D"),
    ("class", "bases"): CLASS.replace("Base,", "Other,"),
    ("class", "keywords"): CLASS.replace("metaclass=M", "metaclass=N"),
    ("class", "body"): CLASS.replace("x = 1", "x = 2"),
    ("class", "decorator_list"): CLASS.replace("@deco", "@other"),
    ("class", "type_params"): CLASS.replace("class C(", "class C[T]("),
}
# Not semantic: a type comment is a comment (and `ast.parse` drops it by default).
NOT_SEMANTIC = {"type_comment"}


def test_every_field_of_a_def_or_class_is_part_of_its_digest():
    for kind, cls in (("def", ast.FunctionDef), ("def", ast.AsyncFunctionDef), ("class", ast.ClassDef)):
        assert set(cls._fields) - NOT_SEMANTIC == {f for k, f in FIELD_EDITS if k == kind}, cls
    for (kind, field), edited in FIELD_EDITS.items():
        for prefix in ("", "async "):
            old = (DEF if kind == "def" else CLASS).replace("def f", prefix + "def f")
            new = edited.replace("def ", prefix + "def ")
            d = delta(summarize(old, "m"), summarize(new, "m"))
            assert not d.empty, (prefix, kind, field)
            # Nested in a class, the edit still shows (as a changed unit or statement).
            nest = lambda text: "class Holder:\n" + textwrap.indent(text, "    ")  # noqa: E731
            assert not delta(summarize(nest(old), "m"), summarize(nest(new), "m")).empty, (prefix, kind, field)


def compound_statements() -> set[type]:
    """Statement kinds that hold other statements, read from the `ast` schema."""
    def holds(annotation) -> bool:
        return any(name in str(annotation) for name in ("ast.stmt", "stmt", "excepthandler", "match_case"))
    return {cls for cls in ast.stmt.__subclasses__()
            if cls not in (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            and any(holds(t) for t in ast_field_types(cls).values())}


def ast_field_types(cls: type) -> dict[str, object]:
    """Compiler-provided AST field schema on both Python 3.12 and 3.13+.

    Python 3.12 exposes field types in each constructor's generated docstring;
    Python 3.13+ also provides ``_field_types``. Keep the schema as the oracle.
    """
    if hasattr(cls, "_field_types"):
        return cls._field_types
    signature = (cls.__doc__ or "").partition("(")[2].rpartition(")")[0]
    return {name: kind for field in signature.split(",")
            if len(parts := field.strip().split()) == 2
            for kind, name in [parts] if name in cls._fields}


# A def in every block of every compound statement; {body} marks each def.
COMPOUND_TEMPLATES = {
    ast.For: "for _ in x:\n{a}\nelse:\n{b}\n",
    ast.AsyncFor: "async def outer():\n    async for _ in x:\n{a2}\n    else:\n{b2}\n",
    ast.While: "while x:\n{a}\nelse:\n{b}\n",
    ast.If: "if x:\n{a}\nelse:\n{b}\n",
    ast.With: "with x:\n{a}\n",
    ast.AsyncWith: "async def outer():\n    async with x:\n{a2}\n",
    ast.Match: "match x:\n    case 1:\n{a2}\n    case _:\n{b2}\n",
    ast.Try: "try:\n{a}\nexcept E:\n{b}\nelse:\n{c}\nfinally:\n{d}\n",
    ast.TryStar: "try:\n{a}\nexcept* E:\n{b}\nelse:\n{c}\nfinally:\n{d}\n",
}


def test_defs_in_every_compound_statement_are_units():
    assert set(COMPOUND_TEMPLATES) == compound_statements()
    for kind, template in COMPOUND_TEMPLATES.items():
        def render(value):
            blocks = {}
            for slot in "abcd":
                body = f"def unit_{slot}():\n    return {value}\n"
                blocks[slot] = textwrap.indent(body, "    ")
                blocks[slot + "2"] = textwrap.indent(body, "        ")
            return template.format(**blocks)
        old, new = summarize(render(1), "m"), summarize(render(2), "m")
        slots = [s for s in "abcd" if "{" + s in template]
        prefix = "outer.<locals>." if template.startswith("async def outer") else ""
        expected = {f"{prefix}unit_{s}" for s in slots}
        assert expected <= set(old.units), kind
        assert set(old.units) == code_qualnames(render(1)), kind
        assert expected <= delta(old, new).changed, kind


def test_every_identifier_field_of_the_ast_is_classified():
    # A name-holding field the binder does not know would let a rebinding go unseen.
    found = {(cls.__name__, name) for cls in vars(ast).values()
             if isinstance(cls, type) and issubclass(cls, ast.AST)
             for name, annotation in ast_field_types(cls).items()
             if ("str" in str(annotation) if hasattr(cls, "_field_types")
                 else str(annotation).rstrip("?*") in ("identifier", "string"))}
    assert found == set(change_units.IDENTIFIER_FIELDS)
    for old, new, name in (
            ("try:\n    pass\nexcept E as e:\n    pass\n", "try:\n    pass\nexcept F as e:\n    pass\n", "e"),
            ("match x:\n    case [a]:\n        pass\n", "match x:\n    case [1, a]:\n        pass\n", "a"),
            ("match x:\n    case [*rest]:\n        pass\n", "match x:\n    case [1, *rest]:\n        pass\n", "rest"),
            ("match x:\n    case {1: a, **rest}:\n        pass\n", "match x:\n    case {2: a, **rest}:\n        pass\n",
             "rest")):
        binds = delta(summarize(old, "m"), summarize(new, "m")).binds
        assert name in binds and not {"E", "F", "x"} & binds, binds


def make_graph(root: Path, files: dict[str, str], lean: dict[str, str] | None = None) -> source_graph.Graph:
    for path, text in {**files, **(lean or {})}.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text)
    (root / "lean").mkdir(exist_ok=True)
    (root / "lean/lakefile.toml").write_text(
        '[[lean_exe]]\nname = "ve_demo"\nroot = "DemoMain"\n\n[[lean_exe]]\nname = "ve_other"\nroot = "OtherMain"\n')
    summaries = {}
    for path, text in files.items():
        if path.endswith(".py"):
            module, package = source_graph.module_name(path)
            summaries[path] = summarize(text, module, package=package)
    graph = source_graph.Graph(root, sorted([*files, *(lean or {})]), summaries)
    for path, text in (lean or {}).items():
        module = ".".join(Path(path).with_suffix("").parts[1:])
        graph.lean_modules[module] = path
        graph.lean_imports[module] = source_graph.lean_imports(text)
    graph.prepare_names()
    graph.build()
    return graph


def make_map(edges: dict[str, dict], commit: str = "0" * 40, failed: tuple[str, ...] = ()) -> dict:
    """A map as the recorder would write it; each unit ran at least its own module."""
    results = {test: {"f": {(test, "<module>"), *map(tuple, e.get("f", ()))}, "r": set(e.get("r", ())),
                      "d": set(e.get("d", ())), "x": set(e.get("x", ())), "m": set(e.get("m", ())),
                      "p": set(e.get("p", ())),
                      "opaque": [],
                      "exit": 1 if test in failed else 0, "seconds": 1.0}
               for test, e in edges.items()}
    return test_map.build_map(results, commit)


LIBRARY = {
    "pkg/__init__.py": "",
    "pkg/core.py": textwrap.dedent('''
        LIMIT = 3
        DERIVED = LIMIT * 2

        def bounded(x):
            return min(x, LIMIT)

        def doubled():
            return DERIVED

        def unrelated():
            return 0

        def dispatch(kind):
            return globals()["handle_" + kind]()

        def handle_a():
            return "a"
    '''),
    "pkg/user.py": "from pkg.core import LIMIT, unrelated\n\ndef reads_limit():\n    return LIMIT\n\n"
                   "def calls():\n    return unrelated()\n",
    "pkg/attr.py": "from pkg import core\n\ndef via_attribute():\n    return core.DERIVED\n",
}
EDGES = {
    "tests/test_bounded.py": {"f": [("pkg/core.py", "<module>"), ("pkg/core.py", "bounded")]},
    "tests/test_doubled.py": {"f": [("pkg/core.py", "<module>"), ("pkg/core.py", "doubled")]},
    "tests/test_unrelated.py": {"f": [("pkg/core.py", "<module>"), ("pkg/user.py", "calls"),
                                      ("pkg/core.py", "unrelated")]},
    "tests/test_user.py": {"f": [("pkg/core.py", "<module>"), ("pkg/user.py", "reads_limit")]},
    "tests/test_attr.py": {"f": [("pkg/core.py", "<module>"), ("pkg/attr.py", "via_attribute")]},
    "tests/test_dispatch.py": {"f": [("pkg/core.py", "<module>"), ("pkg/core.py", "dispatch"),
                                     ("pkg/core.py", "handle_a")]},
}


def impact(tmp_path, path: str, new_text: str, edges=EDGES, called=None) -> dict[str, set[str]]:
    graph = make_graph(tmp_path, LIBRARY)
    coverage = select_tests.Coverage(make_map(edges))
    old = summarize(LIBRARY[path], source_graph.module_name(path)[0])
    new = summarize(new_text, source_graph.module_name(path)[0])
    found: dict[str, set[str]] = {}

    def add(tests, reason=""):
        for test in tests:
            found.setdefault(test, set()).add(reason)

    d = select_tests.delta(old, new)
    select_tests.python_impact(coverage, graph, set(edges), add, path, old, new, d,
                               called if called is not None else d.references)
    return found


def test_a_changed_function_selects_the_tests_that_ran_it(tmp_path):
    new = LIBRARY["pkg/core.py"].replace("min(x, LIMIT)", "max(x, LIMIT)")
    assert set(impact(tmp_path, "pkg/core.py", new)) == {"tests/test_bounded.py"}


def test_a_changed_constant_selects_its_readers_here_and_in_importers(tmp_path):
    new = LIBRARY["pkg/core.py"].replace("LIMIT = 3", "LIMIT = 4")
    # bounded reads LIMIT, doubled reads DERIVED (computed from LIMIT), user imports LIMIT,
    # attr reads core.DERIVED; unrelated and dispatch read neither.
    assert set(impact(tmp_path, "pkg/core.py", new)) == {
        "tests/test_bounded.py", "tests/test_doubled.py", "tests/test_user.py", "tests/test_attr.py"}


def test_a_top_level_call_selects_every_importer(tmp_path):
    new = LIBRARY["pkg/core.py"] + "\nprint('loaded')\n"
    assert set(impact(tmp_path, "pkg/core.py", new)) == set(EDGES)


def test_a_new_function_nothing_calls_by_name_selects_the_whole_file(tmp_path):
    new = LIBRARY["pkg/core.py"] + "\ndef handle_b():\n    return 'b'\n"
    found = impact(tmp_path, "pkg/core.py", new)
    assert "tests/test_dispatch.py" in found and "tests/test_bounded.py" in found


def test_a_new_function_called_by_changed_code_adds_nothing_else(tmp_path):
    new = LIBRARY["pkg/core.py"].replace(
        "def bounded(x):\n    return min(x, LIMIT)",
        "def helper(x):\n    return x\n\ndef bounded(x):\n    return min(helper(x), LIMIT)")
    assert set(impact(tmp_path, "pkg/core.py", new)) == {"tests/test_bounded.py"}


def test_lookups_match_nested_code_but_not_name_prefixes():
    coverage = select_tests.Coverage(make_map({
        "t1": {"f": [("a.py", "f.<locals>.<lambda>")]}, "t2": {"f": [("a.py", "f2")]}}))
    assert coverage.tests_of("a.py", "f") == {"t1"}
    assert coverage.tests_of("a.py", "f2") == {"t2"}


def test_map_round_trips_through_its_edges():
    edges = {"t1": {"f": [("a.py", "f")], "r": ["d.json"], "d": ["data"], "x": ["lake"],
                    "m": ["parse"], "p": ["typing"]},
             "t2": {"f": [("a.py", "g"), ("b.py", "<module>")]}}
    data = make_map(edges)
    back = test_map.unit_edges(json.loads(json.dumps(data)))
    assert back == {test: {"f": {(test, "<module>"), *map(tuple, e.get("f", ()))}, "r": set(e.get("r", ())),
                           "d": set(e.get("d", ())), "x": set(e.get("x", ())),
                           "m": set(e.get("m", ())), "p": set(e.get("p", ()))}
                    for test, e in edges.items()}


def test_operation_map_rejects_missing_and_bool_indices():
    data = make_map({"t1": {"m": ["parse"], "p": ["typing"]}})
    test_map.validate(data)
    for field in ("operations", "presence"):
        missing = json.loads(json.dumps(data))
        del missing[field]
        with pytest.raises(ValueError):
            test_map.validate(missing)
        retyped = json.loads(json.dumps(data))
        retyped[field][next(iter(retyped[field]))] = [True]
        with pytest.raises(ValueError):
            test_map.validate(retyped)


def _read_fields(op: dict) -> tuple:
    """What `ve` reads of an operation at run time: its authority (the guard), each Lean binding's
    executable, mode, kinds, response and counts (`require_lean_binding`, `row_problem`) and its
    Lean call sites (`require_lean_call_site`)."""
    bindings = sorted(json.dumps({key: binding.get(key) for key in ("executable", "mode", "kinds", "response",
                                                                     "counts")}, sort_keys=True)
                      for binding in (op.get("lean") or {}).get("bindings", ()))
    return op["authority"], bindings, sorted(op.get("lean_call_sites", ()))


MANIFEST_SEEDS = [row for row in select_tests_seeds.seeds() if row["kind"] == "manifest"]


@pytest.mark.parametrize("seed", MANIFEST_SEEDS, ids=[row["operation"] for row in MANIFEST_SEEDS])
def test_seeded_manifest_edits_change_a_field_ve_reads(seed):
    """The gate's seeds (tools/select_tests_seeds.py) must be edits a test can observe, not a field nobody reads."""
    old = (ROOT / select_tests.MANIFEST).read_text()
    new = seed["files"][select_tests.MANIFEST]
    assert select_tests_seeds.manifest_text(json.loads(old)) == old  # the seed keeps the file's layout
    assert select_tests.changed_manifest_operations(old, new) == {seed["operation"]}
    before = next(op for op in json.loads(old)["operations"] if op["id"] == seed["operation"])
    after = next(op for op in json.loads(new)["operations"] if op["id"] == seed["operation"])
    assert _read_fields(before) != _read_fields(after)


def test_the_lean_seed_adds_a_module_to_one_executable():
    (seed,) = [row for row in select_tests_seeds.seeds() if row["kind"] == "lean"]
    assert not (ROOT / select_tests_seeds.SEED_MODULE).exists()
    assert set(seed["files"]) == {select_tests_seeds.SEED_MODULE, select_tests_seeds.SEED_ROOT}
    assert "import VE.SeedProbe" in seed["files"][select_tests_seeds.SEED_ROOT]


@pytest.mark.parametrize("seed", MANIFEST_SEEDS, ids=[row["operation"] for row in MANIFEST_SEEDS])
def test_seeded_manifest_edits_select_their_readers(seed, tmp_path):
    op_id = seed["operation"]
    old, new = (ROOT / select_tests.MANIFEST).read_text(), seed["files"][select_tests.MANIFEST]
    reader, other = "tests/test_reader.py", "tests/test_other.py"
    edges = {reader: {"m": [op_id]}, other: {"p": [op_id]},
             select_tests.MANIFEST_TEST: {"m": ["*"]}}
    coverage = select_tests.Coverage(make_map(edges))
    graph = make_graph(tmp_path, {"tests/test_reader.py": "", "tests/test_other.py": ""})
    selection = select_tests.Selection(graph, coverage, set(), list(edges))
    select_tests.manifest_change(selection, select_tests.Change(select_tests.MANIFEST, old, new))
    assert reader in selection.reasons
    assert select_tests.MANIFEST_TEST in selection.reasons
    assert other not in selection.reasons
    assert not selection.full


def test_removed_manifest_operation_selects_registration(tmp_path):
    manifest = json.loads((ROOT / select_tests.MANIFEST).read_text())
    changed = json.loads(json.dumps(manifest))
    changed["operations"] = [row for row in changed["operations"] if row["id"] != "parse"]
    old, new = json.dumps(manifest), json.dumps(changed)
    reader = "tests/test_register.py"
    edges = {reader: {"p": ["parse"]}, select_tests.MANIFEST_TEST: {"m": ["*"]}}
    selection = select_tests.Selection(make_graph(tmp_path, {}), select_tests.Coverage(make_map(edges)),
                                       set(), list(edges))
    select_tests.manifest_change(selection, select_tests.Change(select_tests.MANIFEST, old, new))
    assert reader in selection.reasons


def test_semantic_registration_reads_only_presence(monkeypatch):
    from ve import assurance
    events = []
    monkeypatch.setattr(assurance.sys, "audit", lambda *args: events.append(args))
    assurance.semantic_entry("parse")
    assert events == [("ve.manifest.presence", "parse")]


MANIFEST_EVENTS = {"ve.manifest.all", "ve.manifest.operation", "ve.manifest.presence"}


def _mapping_reads() -> list[str]:
    """Every way to read a Mapping: its public methods and the dunders `in`, `[]`, `len`, `==`, iteration."""
    from collections.abc import Mapping
    return sorted({name for name in dir(Mapping) if not name.startswith("_")}
                  | {"__contains__", "__eq__", "__getitem__", "__iter__", "__len__", "__ne__"})


@pytest.mark.parametrize("method", _mapping_reads())
def test_every_read_of_the_operation_table_is_an_audit_event(method, monkeypatch):
    """However code reads `ve.assurance.OPERATIONS`, the recorder sees an operation, presence or whole-table event."""
    from ve import assurance
    events = []
    monkeypatch.setattr(assurance.sys, "audit", lambda *args: events.append(args))
    table = assurance.OPERATIONS
    call = {"get": lambda: table.get("parse"), "__getitem__": lambda: table["parse"],
            "__contains__": lambda: "parse" in table, "__eq__": lambda: table == {},
            "__ne__": lambda: table != {}, "__iter__": lambda: list(table), "__len__": lambda: len(table),
            "keys": lambda: list(table.keys()), "values": lambda: list(table.values()),
            "items": lambda: list(table.items())}[method]
    call()
    assert events and {event[0] for event in events} <= MANIFEST_EVENTS
    if method in ("get", "__getitem__"):
        assert events == [("ve.manifest.operation", "parse")]
    elif method == "__contains__":
        assert events == [("ve.manifest.presence", "parse")]
    else:
        assert ("ve.manifest.all",) in events


def test_difffuzz_binding_lookup_is_a_recorded_manifest_read():
    """The review's bypass: `tools/difffuzz.py` scanned every binding without an audit event."""
    import difffuzz
    from ve import assurance
    events = []
    original = assurance.sys.audit

    def hook(*args):
        if args[0] in MANIFEST_EVENTS:
            events.append(args)
        return original(*args)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(assurance.sys, "audit", hook)
        difffuzz.manifest_bindings("ve_conformance", "check-certificate", [])
    assert ("ve.manifest.all",) in events


def test_no_module_reads_assurance_state_around_the_audited_api():
    """`ve.assurance`'s private state (the raw manifest, the id table, the migrated set) is read only
    inside the module, so every read elsewhere goes through an audited accessor. Checked on the
    parsed source of every tracked Python file."""
    offenders = []
    for path in subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True,
                               check=True).stdout.split():
        if path == "ve/assurance.py":
            continue
        source = (ROOT / path).read_text(encoding="utf-8", errors="replace")
        if "assurance" not in source:
            continue
        for node in ast.walk(ast.parse(source, path)):
            if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[-1] == "assurance":
                offenders += [f"{path}:{node.lineno} imports {alias.name}" for alias in node.names
                              if alias.name.startswith("_")]
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                    and node.value.id == "assurance" and node.attr.startswith("_") \
                    and not node.attr.startswith("__"):
                offenders.append(f"{path}:{node.lineno} reads assurance.{node.attr}")
    assert offenders == []


def test_manifest_shared_field_or_missing_map_selects_full(tmp_path):
    old = (ROOT / select_tests.MANIFEST).read_text()
    changed = json.loads(old)
    changed["version"] = "seeded"
    graph = make_graph(tmp_path, {})
    selection = select_tests.Selection(graph, None, set(), [])
    select_tests.manifest_change(selection, select_tests.Change(select_tests.MANIFEST, old, json.dumps(changed)))
    assert selection.full


def test_automatic_selection_without_a_map_runs_full_suite(monkeypatch):
    monkeypatch.setattr(select_tests, "resolve_map", lambda base, coverage: None)
    plan = select_tests.select(changes=[select_tests.Change("docs/example.md", "before", "after")],
                               coverage="auto")
    assert plan["full"] and plan["full_reasons"] == ["missing coverage map"]
    assert set(plan["selected"]) == set(select_tests.units())


def test_added_and_removed_lean_modules_select_only_importing_executables(tmp_path):
    graph = make_graph(tmp_path, {}, lean={"lean/Shared.lean": "import Lean\n",
                                            "lean/Used.lean": "import Shared\n"})
    graph.lean_imports["Main"] = ["Used"]
    graph.lean_imports["OtherMain"] = []
    from unittest.mock import patch
    with patch.object(source_graph, "lean_executables", return_value={"first": "Main", "second": "OtherMain"}):
        assert select_tests.lean_programs(graph, "lean/Shared.lean", True) == {"first"}


def test_tests_that_ran_no_drifted_code_keep_their_map_entry(tmp_path):
    graph = make_graph(tmp_path, LIBRARY)
    coverage = select_tests.Coverage(make_map(EDGES))
    changed = LIBRARY["pkg/core.py"].replace("return 0", "return 1")
    uncertain = select_tests.uncertain_units(
        coverage, graph, set(EDGES), {"pkg/core.py": "M", "tests/test_user.py": "M"},
        {"pkg/core.py": (LIBRARY["pkg/core.py"], changed), "tests/test_user.py": ("", "x = 1\n")})
    assert uncertain == {"tests/test_unrelated.py", "tests/test_user.py"}


def test_drifted_data_and_programs_make_their_users_uncertain(tmp_path):
    graph = make_graph(tmp_path, LIBRARY, {"lean/DemoMain.lean": "import Demo.Core\n",
                                           "lean/Demo/Core.lean": "", "lean/OtherMain.lean": ""})
    edges = {"t_read": {"r": ["data/a.json"]}, "t_list": {"d": ["data"]},
             "t_demo": {"x": ["lean/.lake/build/bin/ve_demo"]},
             "t_other": {"x": ["lean/.lake/build/bin/ve_other"]}, "t_rust": {"x": ["rust/target/release/ve"]},
             "t_none": {}}
    coverage = select_tests.Coverage(make_map(edges))
    every = set(edges)
    assert select_tests.uncertain_units(coverage, graph, every, {"data/a.json": "M"}, {}) == {"t_read"}
    assert select_tests.uncertain_units(coverage, graph, every, {"data/b.json": "A"}, {}) == {"t_list"}
    assert select_tests.uncertain_units(coverage, graph, every, {"lean/Demo/Core.lean": "M"}, {}) == {"t_demo"}
    assert select_tests.uncertain_units(coverage, graph, every, {"rust/ve-core/src/a.rs": "M"}, {}) == {"t_rust"}


def test_static_closure_follows_imports_facade_and_named_programs(tmp_path):
    graph = make_graph(tmp_path, {
        "ve/__init__.py": "from .core import parse\n",
        "ve/core.py": "from .low import helper\n\ndef parse():\n    return helper()\n",
        "ve/low.py": "def helper():\n    return 1\n",
        "ve/other.py": "",
        "tests/test_a.py": "from ve import parse\nBIN = ROOT / 'lean' / '.lake' / 'build' / 'bin' / 've_demo'\n"
                           "DATA = 'fixtures.json'\n",
        "tests/data/fixtures.json": "{}",
    })
    files, mentions = graph.closure("tests/test_a.py")
    assert {"ve/core.py", "ve/low.py"} <= files and "ve/other.py" not in files
    assert {"lean-exe:ve_demo", "tests/data/fixtures.json"} <= mentions


def test_static_closure_holds_what_each_conftest_above_the_test_reaches(tmp_path):
    """pytest imports every conftest.py from the root down to a test's directory (the
    --impacted review finding, which holds for the static graph too). Their native
    mentions stay theirs: the conftest builds the checkers and starts none."""
    graph = make_graph(tmp_path, {
        "conftest.py": "import helpers.top\n",
        "helpers/__init__.py": "",
        "helpers/top.py": "",
        "tests/conftest.py": "import tests.subprocesses\nBIN = 'rust/target/release/ve'\n"
                             "LEAN = ROOT / 'lean' / '.lake' / 'build' / 'bin' / 've_demo'\n"
                             "DATA = 'fixtures.json'\n",
        "tests/subprocesses.py": "",
        "tests/deep/conftest.py": "import ve.deep\n",
        "ve/__init__.py": "",
        "ve/deep.py": "",
        "tests/test_a.py": "",
        "tests/deep/test_b.py": "",
        "tests/data/fixtures.json": "{}",
    })
    files, mentions = graph.closure("tests/test_a.py")
    assert {"helpers/top.py", "tests/subprocesses.py"} <= files and "ve/deep.py" not in files
    assert "tests/data/fixtures.json" in mentions
    assert not {"rust", "lean-exe:ve_demo"} & mentions
    assert {"helpers/top.py", "tests/subprocesses.py", "ve/deep.py"} <= graph.closure("tests/deep/test_b.py")[0]


AFTER_DELETION = {
    "ve/__init__.py": "from .core import parse\n",
    "ve/core.py": "def parse():\n    return 1\n",
    "tests/test_importer.py": "import ve.gone\nfrom ve import parse\n",
    "tests/test_dropped.py": "from ve.core import parse\n",          # imported ve.low before
    "tests/test_fixture.py": "DATA = 'tests/data/gone.json'\n",
    "tests/test_facade.py": "from ve import vanished\n",              # ve exported it before
}
BEFORE_DELETION = {
    "ve/gone.py": "def used():\n    return 1\n",
    "tests/data/gone.json": "{}",
    "tests/test_dropped.py": "from ve.core import parse\nfrom ve.low import helper\n",
    "ve/low.py": "def helper():\n    return 1\n",
    "ve/__init__.py": "from .core import parse\nfrom .low import helper as vanished\n",
}


def test_a_deleted_file_keeps_the_tests_that_used_it(tmp_path):
    # Built from the tree after the change, the graph has no node for a deleted
    # module, so its importer's test was not selected; the overlay keeps each
    # changed file as it was before as well.
    graph = make_graph(tmp_path, AFTER_DELETION).overlay(BEFORE_DELETION)
    assert "ve/gone.py" not in make_graph(tmp_path, AFTER_DELETION).closure("tests/test_importer.py")[0]
    assert "ve/gone.py" in graph.closure("tests/test_importer.py")[0]
    assert "ve/low.py" in graph.closure("tests/test_dropped.py")[0]
    assert "ve/low.py" in graph.closure("tests/test_facade.py")[0]
    assert "tests/data/gone.json" in graph.closure("tests/test_fixture.py")[1]
    assert graph.reverse["ve/gone.py"] == {"tests/test_importer.py"}


def test_without_a_map_deleting_a_module_selects_its_importers(monkeypatch):
    path = "ve/authoring.py"  # imported only by tests/test_authoring.py
    tree = source_graph.load(select_tests.ROOT)
    # The graph of the tree after the deletion (the file itself stays on disk here).
    deleted = source_graph.Graph(tree.root, [f for f in tree.files if f != path],
                                 {f: s for f, s in tree.summaries.items() if f != path},
                                 lean_modules=tree.lean_modules, lean_imports=tree.lean_imports,
                                 lean_unreadable=tree.lean_unreadable)
    deleted.prepare_names()
    deleted.build()
    assert "tests/test_authoring.py" not in deleted.reverse.get(path, set())
    monkeypatch.setattr(source_graph, "load", lambda root: deleted)
    plan = plan_for([select_tests.Change(path, real(path), None)], None)
    assert "tests/test_authoring.py" in plan["selected"], plan["reasons"]


def test_with_a_map_deleting_a_module_selects_every_test_that_imported_it(tmp_path):
    # A module of constants only: no unit was removed and no reader of a name runs
    # in the importer's functions, yet every test that imported it now fails.
    library = {**LIBRARY, "pkg/consts.py": "VALUE = 1\n"}
    graph = make_graph(tmp_path, {k: v for k, v in library.items() if k != "pkg/consts.py"})
    edges = {"tests/test_consts.py": {"f": [("pkg/consts.py", "<module>")]}, "tests/test_other.py": {}}
    coverage = select_tests.Coverage(make_map(edges))
    found = select_tests.uncertain_units(coverage, graph, set(edges), {"pkg/consts.py": "D"},
                                         {"pkg/consts.py": (library["pkg/consts.py"], None)})
    assert found == {"tests/test_consts.py"}
    found = set()
    old = summarize(library["pkg/consts.py"], "pkg.consts")
    select_tests.python_impact(coverage, graph, set(edges), lambda tests, _="": found.update(tests),
                               "pkg/consts.py", old, None, delta(old, None), {})
    assert found == {"tests/test_consts.py"}


def recorder_run(tmp_path, program: str, argv=("main.py",), files: dict[str, str] | None = None) -> dict:
    """Run `program` (or `-m module ...`) under the recorder, children starting it as the
    .pth hook would, and fold the records."""
    root, out = tmp_path / "root", tmp_path / "out"
    root.mkdir()
    out.mkdir()
    for path, text in (files or {}).items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text)
    (root / "lib.py").write_text("import warnings\n\ndef used():\n    return 1\n\ndef in_child():\n    return 2\n\n"
                                 "def in_fork():\n    return 3\n\ndef never():\n    return 4\n\n"
                                 "def noisy():\n    warnings.warn('shown with a source line')\n    raise ValueError\n")
    (root / "data.json").write_text("{}")
    (root / "main.py").write_text(program)
    (root / "child.py").write_text("import lib\nlib.in_child()\n")
    (root / "fixtures").mkdir()
    (root / "fixtures/case.json").write_text("{}")
    (root / "start.py").write_text(
        f"import runpy, sys\nsys.path.insert(0, {str(ROOT / 'tools')!r})\nimport test_map_recorder\n"
        "test_map_recorder.start()\nsys.path.pop(0)\nsys.path.insert(0, '.')\n"
        "if sys.argv[1] == '-m':\n"
        "    sys.argv = sys.argv[2:]\n"
        "    runpy.run_module(sys.argv[0], run_name='__main__', alter_sys=True)\n"
        "else:\n"
        "    runpy.run_path(sys.argv[1], run_name='__main__')\n")
    env = nested_pytest.environment({"PATH": os.environ["PATH"], "VE_TESTMAP_OUT": str(out), "VE_TESTMAP_ROOT": str(root),
                                     "PYTHONDONTWRITEBYTECODE": "1"})
    subprocess.run([sys.executable, "start.py", *argv], cwd=root, env=env, check=True,
                   timeout=HANG_TIMEOUT)
    return test_map.read_unit(out, {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()})


def test_recorder_sees_functions_reads_and_children(tmp_path):
    result = recorder_run(tmp_path, textwrap.dedent('''
        import json, os, subprocess, sys, traceback, warnings
        import lib
        lib.used()
        json.load(open("data.json"))
        os.listdir("fixtures")
        try:
            lib.noisy()
        except ValueError:
            traceback.format_exc()
        # An explicit environment without the recording variables: the recorder adds them.
        subprocess.run([sys.executable, "start.py", "child.py"], env={"PATH": os.environ["PATH"]},
                       check=True)
        pid = os.fork()
        if pid == 0:
            lib.in_fork()
            os._exit(0)
        os.waitpid(pid, 0)
    '''))
    functions = {q for file, q in result["f"] if file == "lib.py"}
    assert functions == {"<module>", "used", "in_child", "in_fork", "noisy"}
    assert "data.json" in result["r"]
    assert "lib.py" not in result["r"]  # imports, tracebacks and warnings read source, not data
    assert result["d"] == {"fixtures"}  # the import system's listing of "." is not the test's
    assert result["opaque"] == []


def test_recorder_tracks_manifest_operations_without_import_read(tmp_path):
    assurance = textwrap.dedent('''
        import json, pathlib, sys
        def _load():
            return json.loads(pathlib.Path(__file__).with_name("assurance-manifest.json").read_text())
        DATA = _load()
        sys.audit("ve.manifest.presence", "typing")
        def operation(name):
            sys.audit("ve.manifest.operation", name)
            return DATA[name]
    ''')
    result = recorder_run(tmp_path, "from ve import assurance\nassurance.operation('parse')\n",
                          files={"ve/__init__.py": "", "ve/assurance.py": assurance,
                                 "ve/assurance-manifest.json": '{"parse": 1}'})
    assert result["m"] == {"parse"}
    assert result["p"] == {"typing"}
    assert "ve/assurance-manifest.json" not in result["r"]


def test_direct_manifest_read_remains_a_whole_file_edge(tmp_path):
    result = recorder_run(tmp_path, "from pathlib import Path\nPath('ve/assurance-manifest.json').read_text()\n",
                          files={"ve/assurance-manifest.json": "{}"})
    assert "ve/assurance-manifest.json" in result["r"]


def test_a_python_child_that_leaves_no_record_makes_the_unit_opaque(tmp_path):
    result = recorder_run(tmp_path, textwrap.dedent('''
        import subprocess, sys
        subprocess.run([sys.executable, "-S", "-c", "pass"], check=True)
    '''))
    assert result["opaque"]


def test_a_test_run_by_pytest_keeps_its_own_reads_and_listings(tmp_path):
    # The reviewed case: every frame of a test has pytest further out, and the
    # recorder dropped any read of a Python source and any listing made with a
    # pytest frame anywhere on the stack, so editing lib.py or adding a fixture
    # did not select this test although either made it fail.
    test = textwrap.dedent('''
        import ast, glob, os
        from pathlib import Path
        import helper
        ROOT = Path(__file__).resolve().parent.parent

        def test_uses_files():
            assert ast.parse((ROOT / "lib.py").read_text()).body
            assert sorted(p.name for p in (ROOT / "fixtures").iterdir()) == ["case.json"]
            assert os.listdir(ROOT / "more") == ["x.txt"]
            assert glob.glob(str(ROOT / "globbed" / "*.txt"))
            assert helper.value() == 1
    ''')
    result = recorder_run(tmp_path, "", nested_pytest.command(["-q", "-p", "no:cacheprovider", "--rootdir", ".",
                                                               "--confcutdir", ".", "tests/test_uses.py"], python=[]),
                          {"tests/test_uses.py": test, "helper.py": "def value():\n    return 1\n",
                           "more/x.txt": "", "globbed/y.txt": ""})
    assert "lib.py" in result["r"]  # read as data by the test
    assert {"fixtures", "more", "globbed"} <= result["d"]
    # Imports and pytest's assertion rewriting read sources; collection lists directories.
    assert not {"helper.py", "tests/test_uses.py"} & result["r"]
    assert not {".", "tests"} & result["d"]
    assert ("helper.py", "value") in result["f"] and result["opaque"] == []


ROOT_DIR, PYTEST = "/r", "/venv/site-packages/_pytest/python.py"
PLUGGY, LIBRARY_CODE = "/venv/site-packages/pluggy/_callers.py", "/venv/site-packages/lark/load_grammar.py"
STDLIB = "/usr/lib/python3.14/{}.py".format
TEST_FILE, PROJECT = "/r/tests/test_x.py", "/r/ve/lib.py"
ORIGINS = [
    # (stack of code filenames, innermost first; who the open or listing is for)
    ([STDLIB("pathlib/_local"), TEST_FILE, PYTEST, PLUGGY], test_map_recorder.TEST),
    ([STDLIB("glob"), PROJECT, TEST_FILE, PYTEST], test_map_recorder.TEST),
    ([LIBRARY_CODE, PROJECT, TEST_FILE, PYTEST], test_map_recorder.TEST),
    ([STDLIB("pkgutil"), PROJECT, PYTEST], test_map_recorder.TEST),
    (["/r/tools/test_map_recorder.py", STDLIB("os"), TEST_FILE, PYTEST], test_map_recorder.TEST),
    (["<string>"], test_map_recorder.TEST),
    ([STDLIB("linecache"), STDLIB("inspect"), TEST_FILE, PYTEST], test_map_recorder.TEST),
    ([STDLIB("linecache"), STDLIB("traceback"), TEST_FILE, PYTEST], test_map_recorder.DISPLAY),
    ([STDLIB("linecache"), STDLIB("warnings"), PROJECT, TEST_FILE], test_map_recorder.DISPLAY),
    ([STDLIB("linecache"), PYTEST, PLUGGY], test_map_recorder.INFRASTRUCTURE),
    ([PYTEST, PLUGGY, STDLIB("runpy")], test_map_recorder.INFRASTRUCTURE),
    (["<frozen importlib._bootstrap_external>", "<frozen importlib._bootstrap>", TEST_FILE, PYTEST],
     test_map_recorder.INFRASTRUCTURE),
    (["<frozen site>"], test_map_recorder.INFRASTRUCTURE),
    (["/venv/lib/python3.14/importlib/metadata/__init__.py", TEST_FILE], test_map_recorder.INFRASTRUCTURE),
]


def test_reads_and_listings_belong_to_the_innermost_owner():
    for stack, expected in ORIGINS:
        assert test_map_recorder.origin(iter(stack), ROOT_DIR, {"/r/tools/test_map_recorder.py"}) == expected, stack


def head_commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


@pytest.fixture(scope="module")
def head():
    return head_commit()


def plan_for(changes, coverage):
    return select_tests.select(changes=changes, coverage=coverage, base="HEAD")


def real(path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout


def test_whole_plans_on_this_checkout(head):
    every = select_tests.units()
    edges = {test: {} for test in every}
    edges["tests/test_background.py"] = {"f": [("ve/definitions.py", "<module>")]}
    edges["tests/test_bundle.py"] = {"r": ["docs/english-surface.md"]}
    # Recorded as failed, so the static graph answers for it.
    data = make_map(edges, commit=head, failed=("tests/test_english.py",))
    smoke = set(select_tests.SMOKE)

    docs = plan_for([select_tests.Change("docs/english-surface.md", "a", "b")], data)
    assert "tests/test_bundle.py" in docs["selected"]
    assert set(docs["selected"]) <= {"tests/test_bundle.py", "tests/test_english.py"}
    assert docs["commands"] == [[*select_tests.PYTEST, "-q", *docs["selected"]]]

    definitions = real("ve/definitions.py")
    comment = plan_for([select_tests.Change("ve/definitions.py", definitions, "# c\n" + definitions)], data)
    assert not smoke & set(comment["selected"]) and not comment["full"]

    added = definitions + "\n\ndef _uncalled_marker():\n    return 0\n"
    new_function = plan_for([select_tests.Change("ve/definitions.py", definitions, added)], data)
    assert smoke <= set(new_function["selected"])
    assert "tests/test_english.py" in new_function["selected"]
    assert "tests/test_background.py" not in new_function["selected"]  # it ran no function there

    unknown = plan_for([select_tests.Change("mystery.cfg", None, "x")], data)
    assert unknown["full"] and unknown["selected_count"] == len(every)
    assert ["lake", "build"] in unknown["commands"]

    conftest = plan_for([select_tests.Change("tests/conftest.py", real("tests/conftest.py"), "x = 1\n")], data)
    assert conftest["full"]

    vacuity = real("tests/test_vacuity.py")
    test_change = plan_for([select_tests.Change("tests/test_vacuity.py", vacuity, vacuity + "\nX = 1\n")], data)
    assert "tests/test_vacuity.py" in test_change["selected"]


def test_native_changes_schedule_builds_and_their_runners(head):
    every = select_tests.units()
    edges = {test: {} for test in every}
    edges["tests/test_lean_conformance.py"] = {"x": ["lean/.lake/build/bin/ve_conformance"]}
    edges["tests/test_rust_conformance.py"] = {"x": ["rust/target/release/ve"]}
    data = make_map(edges, commit=head)
    lean_path = "lean/Main.lean"
    lean = plan_for([select_tests.Change(lean_path, real(lean_path), real(lean_path) + "\n-- c\n")], data)
    assert "tests/test_lean_conformance.py" in lean["selected"]
    assert "tests/test_rust_conformance.py" not in lean["selected"]
    assert ["lake", "build"] in lean["commands"] and list(select_tests.AUDIT) in lean["commands"]
    rust_path = "rust/ve/src/main.rs"
    rust = plan_for([select_tests.Change(rust_path, real(rust_path), real(rust_path) + "\n")], data)
    assert "tests/test_rust_conformance.py" in rust["selected"]
    assert any(c[:3] == [*select_tests.CARGO, "test"] for c in rust["commands"])
    assert list(select_tests.AUDIT) not in rust["commands"]


def graph_without(path: str) -> source_graph.Graph:
    """The checkout's graph as if `path` were deleted (the file itself stays on disk here)."""
    tree = source_graph.load(select_tests.ROOT)
    deleted = source_graph.Graph(tree.root, [f for f in tree.files if f != path],
                                 {f: s for f, s in tree.summaries.items() if f != path},
                                 lean_modules=tree.lean_modules, lean_imports=tree.lean_imports,
                                 lean_unreadable=tree.lean_unreadable)
    deleted.prepare_names()
    deleted.build()
    return deleted


# Modules that bind nothing: no unit, no statement, so their semantic delta is empty.
BINDS_NOTHING = {"empty": "", "docstring": '"""Only a docstring."""\n', "pass": "pass\n",
                 "comment": "# only a comment\n"}


@pytest.mark.parametrize("content", BINDS_NOTHING.values(), ids=BINDS_NOTHING)
def test_deleting_a_module_that_binds_nothing_selects_its_importers(content, head, monkeypatch):
    # Review B1: the empty delta returned before the deletion was looked at, so
    # neither the static graph nor a fresh map selected the importer that now
    # fails to collect, and the drift check kept the importer's map entry.
    path = "ve/authoring.py"  # imported only by tests/test_authoring.py
    importer = "tests/test_authoring.py"
    static = graph_without(path)
    monkeypatch.setattr(source_graph, "load", lambda root: static)
    plan = plan_for([select_tests.Change(path, content, None)], None)
    assert importer in plan["selected"], plan["reasons"]
    edges = {test: {} for test in select_tests.units()}
    edges[importer] = {"f": [(path, "<module>")]}
    plan = plan_for([select_tests.Change(path, content, None)], make_map(edges, commit=head))
    assert f"{path}: import-time change" in plan["reasons"].get(importer, []), plan["reasons"]
    coverage = select_tests.Coverage(make_map(edges, commit=head))
    every = set(edges)
    assert importer in select_tests.uncertain_units(coverage, static, every, {path: "D"}, {path: (content, None)})
    assert importer not in select_tests.uncertain_units(coverage, static, every, {path: "M"},
                                                        {path: (content, content + "\n")})


def test_adding_a_python_fixture_selects_the_tests_that_listed_its_directory(head):
    # Review B2: a test that listed tests/fixtures failed once b.py appeared there;
    # the plan applied directory listings to data files only.
    edges = {test: {} for test in select_tests.units()}
    edges["tests/test_bundle.py"] = {"d": ["tests/fixtures"]}
    data = make_map(edges, commit=head)
    for name in ("b.py", "b.json", "b.lean", "b.rs"):
        plan = plan_for([select_tests.Change(f"tests/fixtures/{name}", None, "X = 1\n")], data)
        assert f"lists the directory of tests/fixtures/{name}" in plan["reasons"].get("tests/test_bundle.py", []), \
            (name, plan["reasons"])


# Recorded listers (looprecheck2): each test lists one directory, run by pytest from the root.
LISTING_TREE = {"README.md": "x\n", "tests/fixtures/case.json": "{}", "tests/fixtures/sub/last.json": "{}"}
LISTING_TESTS = {  # unit name in this checkout -> (its test file in the scratch tree, the directory it lists)
    "tests/test_bundle.py": ("tests/test_root.py", ".",
                             "assert [p.name for p in Path('.').glob('*.md')] == ['README.md']"),
    "tests/test_closure.py": ("tests/test_parent.py", "tests/fixtures",
                              "assert sorted(p.name for p in Path('tests/fixtures').iterdir()) == "
                              "['case.json', 'sub']"),
    "tests/test_argument.py": ("tests/test_child.py", "tests/fixtures/sub",
                               "assert [p.name for p in Path('tests/fixtures/sub').iterdir()] == ['last.json']"),
}
LISTING_FILES = {**LISTING_TREE, **{file: f"from pathlib import Path\n\ndef test_listing():\n    {body}\n"
                                    for file, _, body in LISTING_TESTS.values()}}


def pytest_exit(root: Path, test_file: str) -> int:
    return subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", "--rootdir", ".",
                                                "--confcutdir", ".", test_file]), cwd=root, capture_output=True,
                          env=nested_pytest.environment({"PATH": os.environ["PATH"], "PYTHONDONTWRITEBYTECODE": "1"}),
                          timeout=HANG_TIMEOUT).returncode


def recorded_listers(tmp_path: Path, head: str, tests: dict[str, tuple[str, str, str]], files: dict[str, str]) -> dict:
    """A map of every unit, where each unit of `tests` has the listings its scratch
    test made under the real recorder (in its own tree, `tmp_path/<unit>/root`)."""
    results = {test: {"f": {(test, "<module>")}, "r": set(), "d": set(), "x": set(), "opaque": [],
                      "exit": 0, "seconds": 1.0} for test in select_tests.units()}
    for unit, (test_file, directory, _) in tests.items():
        (tmp_path / unit).mkdir(parents=True)
        recorded = recorder_run(tmp_path / unit, "", nested_pytest.command(
            ["-q", "-p", "no:cacheprovider", "--rootdir", ".", "--confcutdir", ".", test_file], python=[]), files)
        assert recorded["d"] == {directory}, recorded["d"]
        results[unit]["d"] = recorded["d"]
    return test_map.build_map(results, head)


def assert_plan_and_drift_select(data: dict, change, letter: str, failing: set[str]) -> None:
    """The plan selects each failing unit as a lister, and the drift check drops its entry."""
    plan = plan_for([change], data)
    assert {test for test in failing
            if f"lists the directory of {change.path}" in plan["reasons"].get(test, [])} == failing, plan["reasons"]
    drift = select_tests.uncertain_units(select_tests.Coverage(data), source_graph.load(select_tests.ROOT),
                                         set(data["tests"]), {change.path: letter}, {})
    assert failing <= drift, drift


def test_an_added_or_deleted_file_selects_the_listers_of_every_directory_above_it(tmp_path, head):
    # Looprecheck2 B1: a test listing the root "." failed once a root Markdown file
    # appeared, but the lookup never reached ".". B2: with tests/fixtures/sub also
    # recorded, deleting its last file failed the tests/fixtures lister too, but the
    # lookup stopped at the nearest recorded directory. Recorded, not hand-written, edges.
    data = recorded_listers(tmp_path, head, LISTING_TESTS, LISTING_FILES)
    root_md, last = "NOTES.md", "tests/fixtures/sub/last.json"

    # Each change really fails the tests that listed a directory above it.
    added = tmp_path / "tests/test_bundle.py/root"
    (added / root_md).write_text("x\n")
    deleted = tmp_path / "tests/test_closure.py/root"
    (deleted / last).unlink()
    (deleted / last).parent.rmdir()
    assert pytest_exit(added, "tests/test_root.py") == 1
    assert [pytest_exit(deleted, LISTING_TESTS[unit][0]) for unit in LISTING_TESTS] == [0, 1, 1]

    assert_plan_and_drift_select(data, select_tests.Change(root_md, None, "x\n"), "A", {"tests/test_bundle.py"})
    assert_plan_and_drift_select(data, select_tests.Change(last, "{}", None), "D",
                                 {"tests/test_closure.py", "tests/test_argument.py"})


# Recorded listers (looprecheck3): a listing of the root that a new top-level directory
# changes, and a listing of a directory that does not exist yet.
NEW_DIRECTORY_TESTS = {
    "tests/test_bundle.py": ("tests/test_root.py", ".",
                             "assert sorted(p.name for p in Path('.').iterdir() if p.is_dir()) == "
                             "['fixtures', 'tests']"),
    "tests/test_closure.py": ("tests/test_new.py", "tests/fixtures/new",
                              "assert list(Path('tests/fixtures/new').glob('*.md')) == []"),
}
NEW_DIRECTORY_FILES = {"tests/fixtures/case.json": "{}",
                       **{file: f"from pathlib import Path\n\ndef test_listing():\n    {body}\n"
                          for file, _, body in NEW_DIRECTORY_TESTS.values()}}


def test_a_file_in_a_new_directory_selects_the_listers_of_the_root(tmp_path, head):
    # Rule 1: an added file selects the listers of every directory above it, the root
    # included, even when only the root was listed: its new top-level directory
    # changes the root's listing.
    tests = {unit: NEW_DIRECTORY_TESTS[unit] for unit in ("tests/test_bundle.py",)}
    data = recorded_listers(tmp_path, head, tests, NEW_DIRECTORY_FILES)
    added = "docs/new/notes.md"
    root = tmp_path / "tests/test_bundle.py/root"
    assert pytest_exit(root, "tests/test_root.py") == 0
    (root / added).parent.mkdir(parents=True)
    (root / added).write_text("x\n")
    assert pytest_exit(root, "tests/test_root.py") == 1
    assert_plan_and_drift_select(data, select_tests.Change(added, None, "x\n"), "A", {"tests/test_bundle.py"})


def test_a_listing_of_a_directory_that_does_not_exist_yet_is_kept(tmp_path, head):
    # Looprecheck3 B2 (rule 3): a passing test listed tests/fixtures/new, which did not
    # exist; the map dropped the listing (only directories holding a tracked file were
    # kept), so adding tests/fixtures/new/a.md failed the test but selected nothing, and
    # the drift check kept its entry.
    tests = {unit: NEW_DIRECTORY_TESTS[unit] for unit in ("tests/test_closure.py",)}
    data = recorded_listers(tmp_path, head, tests, NEW_DIRECTORY_FILES)
    assert data["dirs"] == {"tests/fixtures/new": [data["tests"].index("tests/test_closure.py")]}
    added = "tests/fixtures/new/a.md"
    root = tmp_path / "tests/test_closure.py/root"
    assert pytest_exit(root, "tests/test_new.py") == 0
    (root / added).parent.mkdir()
    (root / added).write_text("x\n")
    assert pytest_exit(root, "tests/test_new.py") == 1
    assert_plan_and_drift_select(data, select_tests.Change(added, None, "x\n"), "A", {"tests/test_closure.py"})


# Static fallback (looprecheck3 B1, rule 2): which spellings of "." name the root.
ROOT_NAMERS = {
    "tests/test_bundle.py": "from pathlib import Path\n\ndef test_md():\n    assert list(Path('.').glob('*.md'))\n",
    "tests/test_cli.py": "import os\n\ndef test_ls():\n    assert os.listdir('./')\n",
    "tests/test_assist.py": "import os\n\ndef test_join():\n    assert os.listdir(os.path.join('.', 'docs'))\n",
}
NOT_ROOT_NAMERS = {  # "." as text, or as the English full stop in a product module
    "tests/test_closure.py": "def test_text():\n    assert '.'.join(['a', 'b']).split('.') and 'a' + '.' != f'{1}.'\n",
    "tests/test_argument.py": "import ve.punctuation\n\ndef test_stop():\n    assert ve.punctuation.STOP\n",
    "ve/punctuation.py": "STOP = '.'\nMARKS = {',', '.'}\n",
}


def test_without_a_map_an_added_file_selects_the_tests_that_name_the_root(tmp_path, monkeypatch):
    # Looprecheck3 B1: the static graph never named the root ".", so its `dir:.` lookup
    # could not match: adding NOTES.md failed a test that listed `Path('.').glob('*.md')`,
    # but selection without a map returned no tests.
    graph = make_graph(tmp_path, {**ROOT_NAMERS, **NOT_ROOT_NAMERS})
    monkeypatch.setattr(source_graph, "load", lambda root: graph)
    for change in (select_tests.Change("NOTES.md", None, "x\n"), select_tests.Change("docs/new/a.md", None, "x\n"),
                   select_tests.Change("README.md", "x\n", None)):
        plan = plan_for([change], None)
        named = {test for test, reasons in plan["reasons"].items() if f"names {change.path} (static)" in reasons}
        assert named == set(ROOT_NAMERS), (change.path, plan["reasons"])


def test_a_new_module_selects_the_tests_that_now_import_it(tmp_path):
    # Nobody can have imported it when the map was recorded: those who import it now
    # ran without it (an optional import, or a failure), so the static graph answers.
    graph = make_graph(tmp_path, {**LIBRARY, "pkg/fresh.py": "",
                                  "tests/test_fresh.py": "try:\n    import pkg.fresh\nexcept ImportError:\n    pass\n"})
    edges = {"tests/test_fresh.py": {}, "tests/test_bounded.py": EDGES["tests/test_bounded.py"]}
    coverage = select_tests.Coverage(make_map(edges))
    assert select_tests.uncertain_units(coverage, graph, set(edges), {"pkg/fresh.py": "A"},
                                        {"pkg/fresh.py": (None, "")}) == {"tests/test_fresh.py"}


def test_a_named_but_unedited_path_may_have_appeared_or_vanished():
    change = select_tests.Change("tests/fixtures/b.py", None, None)
    assert not change.presence_changed
    change.presence_known = False
    assert change.presence_changed


# One example path of every kind of file the selector knows (generated from its table below).
KIND_EXAMPLES = {
    "python": ("ve/_presence_probe.py", "tests/fixtures/_presence_probe.py"),
    "lean": ("lean/VE/_PresenceProbe.lean",),
    "rust": ("rust/ve-core/src/_presence_probe.rs",),
    "data": ("tests/fixtures/_presence_probe.json", "docs/_presence_probe.md", "_presence_probe.md"),
    "everything": ("pyproject.toml", "_presence_probe.cfg"),
}
PRESENCE_UNITS = {"reader": "tests/test_background.py", "importer": "tests/test_authoring.py",
                  "runner": "tests/test_english.py", "bystander": "tests/test_vacuity.py",
                  "sibling lister": "tests/test_cli.py"}
# One unit per directory above the deepest example, nearest first: each listed only that directory.
LISTER_UNITS = ("tests/test_bundle.py", "tests/test_closure.py", "tests/test_argument.py", "tests/test_assist.py")
SIBLING_DIRECTORY = "paper"  # holds no example: listing it is unaffected


def presence_cases():
    for kind, paths in KIND_EXAMPLES.items():
        for path in paths:
            contents = BINDS_NOTHING | {"code": "X = 1\n"} if kind == "python" else {"text": "x\n"}
            for letter in ("A", "D"):
                for name, content in contents.items():
                    yield pytest.param(kind, path, letter, content, id=f"{path}-{letter}-{name}")


def test_every_kind_of_file_has_a_presence_example():
    assert set(KIND_EXAMPLES) == set(select_tests.KINDS)
    for kind, paths in KIND_EXAMPLES.items():
        assert {select_tests.kind_of(path) for path in paths} == {kind}, kind


@pytest.mark.parametrize("kind, path, letter, content", list(presence_cases()))
def test_the_plan_and_the_drift_check_treat_presence_alike(kind, path, letter, content, head):
    """Adding or deleting any kind of file selects its readers, the listers of every
    directory above it (the root "." included: the file may have been the first or
    last one there), and (a module) its importers, in the plan and the drift check alike."""
    assert not {*PRESENCE_UNITS.values(), *LISTER_UNITS} & set(select_tests.SMOKE)
    above = [str(directory) for directory in PurePosixPath(path).parents]
    assert len(above) <= len(LISTER_UNITS) and SIBLING_DIRECTORY not in above
    listers = dict(zip(LISTER_UNITS, above))
    edges = {test: {} for test in select_tests.units()}
    edges[PRESENCE_UNITS["reader"]] = {"r": [path]}
    for unit, directory in listers.items():
        edges[unit] = {"d": [directory]}
    edges[PRESENCE_UNITS["sibling lister"]] = {"d": [SIBLING_DIRECTORY]}
    edges[PRESENCE_UNITS["importer"]] = {"f": [(path, "<module>")]}
    edges[PRESENCE_UNITS["runner"]] = {"x": ["lean/.lake/build/bin/ve_conformance", "rust/target/release/ve"]}
    data = make_map(edges, commit=head)
    old, new = (None, content) if letter == "A" else (content, None)
    plan = plan_for([select_tests.Change(path, old, new)], data)
    every = set(edges)
    if kind == "everything":
        assert plan["full"]
        expected = every
    else:
        expected = {PRESENCE_UNITS["reader"], *listers}
        expected |= {"python": {PRESENCE_UNITS["importer"]}, "lean": set(),
                     "rust": {PRESENCE_UNITS["runner"]}, "data": set()}[kind]
        mapped = {test for test, reasons in plan["reasons"].items()
                  if any(r != "smoke" and not r.endswith("(static)") for r in reasons)}
        assert mapped == expected, plan["reasons"]
    versions = {path: (old, new)} if path.endswith(".py") else {}
    drift = select_tests.uncertain_units(select_tests.Coverage(data), source_graph.load(select_tests.ROOT),
                                         every, {path: letter}, versions)
    assert drift == expected


SAFETY_CASES = (
    # (mutation of the selector, the check above that must then fail)
    ("tests_of matches only the exact name", test_lookups_match_nested_code_but_not_name_prefixes),
    ("module-level statements are ignored", test_a_changed_constant_selects_its_readers_here_and_in_importers),
    ("drift is ignored", test_tests_that_ran_no_drifted_code_keep_their_map_entry),
    ("new functions are trusted", test_a_new_function_nothing_calls_by_name_selects_the_whole_file),
    ("any pytest frame on the stack makes a read infrastructure",
     test_reads_and_listings_belong_to_the_innermost_owner),
    ("def and async def are digested alike", test_making_a_repository_method_async_changes_it),
    ("the graph forgets deleted files", test_a_deleted_file_keeps_the_tests_that_used_it),
    ("the plan's graph forgets deleted files", test_without_a_map_deleting_a_module_selects_its_importers),
    ("a vanished module is not an import-time change",
     test_with_a_map_deleting_a_module_selects_every_test_that_imported_it),
    ("an empty delta hides an added or deleted module",
     test_deleting_a_module_that_binds_nothing_selects_its_importers),
    ("directory listings count for data files only",
     test_adding_a_python_fixture_selects_the_tests_that_listed_its_directory),
    ("listers of the root are ignored",
     test_an_added_or_deleted_file_selects_the_listers_of_every_directory_above_it),
    ("only the nearest recorded directory's listers count",
     test_an_added_or_deleted_file_selects_the_listers_of_every_directory_above_it),
    ("listers of the root are ignored for a new directory", test_a_file_in_a_new_directory_selects_the_listers_of_the_root),
    ("listings of directories without a tracked file are dropped",
     test_a_listing_of_a_directory_that_does_not_exist_yet_is_kept),
    ("the static graph never names the root", test_without_a_map_an_added_file_selects_the_tests_that_name_the_root),
    ("every '.' literal names the root", test_without_a_map_an_added_file_selects_the_tests_that_name_the_root),
    ("product modules name the root too", test_without_a_map_an_added_file_selects_the_tests_that_name_the_root),
)


@pytest.mark.parametrize("name, check", SAFETY_CASES, ids=[c[0] for c in SAFETY_CASES])
def test_selector_mutants_fail_the_checks(name, check, tmp_path, monkeypatch):
    if name == "tests_of matches only the exact name":
        monkeypatch.setattr(select_tests.Coverage, "tests_of",
                            lambda self, file, q: self._names(self.functions.get(file, {}).get(q, ())))
        arguments = ()
    elif name == "module-level statements are ignored":
        real_delta = change_units.delta

        def no_statements(old, new):
            d = real_delta(old, new)
            d.binds, d.effect = set(), False
            return d
        monkeypatch.setattr(select_tests, "delta", no_statements)
        arguments = (tmp_path,)
    elif name == "drift is ignored":
        monkeypatch.setattr(select_tests, "python_impact", lambda *args, **kwargs: None)
        arguments = (tmp_path,)
    elif name == "any pytest frame on the stack makes a read infrastructure":
        real_origin = test_map_recorder.origin

        def any_ancestor(filenames, root, own=frozenset()):
            filenames = list(filenames)
            if any("/_pytest/" in f or "/pluggy/" in f for f in filenames):
                return test_map_recorder.INFRASTRUCTURE
            return real_origin(filenames, root, own)
        monkeypatch.setattr(test_map_recorder, "origin", any_ancestor)
        arguments = ()
    elif name == "def and async def are digested alike":
        monkeypatch.setattr(change_units, "_unit_node", lambda node: ast.FunctionDef(
            name=node.name, args=node.args, body=node.body, decorator_list=[], returns=node.returns,
            type_params=node.type_params))
        arguments = ()
    elif name in ("the graph forgets deleted files", "the plan's graph forgets deleted files"):
        monkeypatch.setattr(source_graph.Graph, "overlay", lambda self, earlier: self)
        arguments = (tmp_path,) if name == "the graph forgets deleted files" else (monkeypatch,)
    elif name == "a vanished module is not an import-time change":
        real_impact = select_tests.python_impact
        monkeypatch.setattr(select_tests, "python_impact", lambda coverage, graph, all_units, add, path, old, new, d,
                            called: real_impact(coverage, graph, all_units, add, path, old or new, new or old,
                                                d, called))
        arguments = (tmp_path,)
    elif name == "an empty delta hides an added or deleted module":
        real_file_impact = select_tests.file_impact

        def empty_hides(coverage, graph, all_units, add, path, presence_changed, python=None, called=None):
            if python is not None and python[2] is not None and python[2].empty:
                presence_changed = False
            real_file_impact(coverage, graph, all_units, add, path, presence_changed, python, called)
        monkeypatch.setattr(select_tests, "file_impact", empty_hides)
        arguments = ("", head_commit(), monkeypatch)
    elif name == "directory listings count for data files only":
        real_listers = select_tests.Coverage.listers
        monkeypatch.setattr(select_tests.Coverage, "listers", lambda self, path: set() if select_tests.kind_of(
            path) != select_tests.DATA else real_listers(self, path))
        arguments = (head_commit(),)
    elif name == "listings of directories without a tracked file are dropped":
        real_read_unit = test_map.read_unit

        def tracked_directories_only(directory, files):
            result = real_read_unit(directory, files)
            result["d"] &= {".", *(str(parent) for file in files for parent in PurePosixPath(file).parents)}
            return result
        monkeypatch.setattr(test_map, "read_unit", tracked_directories_only)
        arguments = (tmp_path, head_commit())
    elif name == "the static graph never names the root":
        real_prepare = source_graph.Graph.prepare_names

        def without_root(self):
            real_prepare(self)
            self._directories.discard(".")
        monkeypatch.setattr(source_graph.Graph, "prepare_names", without_root)
        arguments = (tmp_path, monkeypatch)
    elif name == "every '.' literal names the root":
        monkeypatch.setattr(change_units, "_text_operands", lambda tree: set())
        arguments = (tmp_path, monkeypatch)
    elif name == "product modules name the root too":
        monkeypatch.setattr(source_graph, "PRODUCT", ())
        arguments = (tmp_path, monkeypatch)
    elif name.startswith("listers of the root are ignored"):
        real_listers = select_tests.Coverage.listers
        monkeypatch.setattr(select_tests.Coverage, "listers", lambda self, path: real_listers(self, path)
                            - self._names(self.dirs.get(".", ())))
        arguments = (tmp_path, head_commit())
    elif name == "only the nearest recorded directory's listers count":
        def nearest(self, path):
            for directory in select_tests.directories_above(path):
                if directory in self.dirs:
                    return self._names(self.dirs[directory])
            return set()
        monkeypatch.setattr(select_tests.Coverage, "listers", nearest)
        arguments = (tmp_path, head_commit())
    else:
        monkeypatch.setattr(select_tests.Coverage, "file_wide", lambda self, file, defs: set())
        arguments = (tmp_path,)
    with pytest.raises(AssertionError):
        check(*arguments)


def test_testing_doc_tables_are_generated_from_the_evidence():
    import select_tests_evidence
    data = json.loads((ROOT / "docs/testselect-evidence.json").read_text())
    text = (ROOT / "docs/TESTING.md").read_text()
    start, end = "<!-- testselect-evidence:start -->\n", "\n<!-- testselect-evidence:end -->"
    shown = text[text.index(start) + len(start):text.index(end)]
    assert shown == select_tests_evidence.table(data)
    assert len(data["replay"]) == 50 and len(data["mutants"]) == 10
    # Every seeded bug was caught, and only after the same test passed without it.
    assert all(row["failure"] and not row.get("rest_exit") for row in data["mutants"])


def test_smoke_files_and_top_level_areas_match_the_tree():
    every = select_tests.units()
    assert set(select_tests.SMOKE) <= set(every)
    tracked = subprocess.run(["git", "ls-tree", "-d", "--name-only", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.split()
    # A top-level directory the selector does not know selects everything; list new ones on purpose.
    assert set(tracked) - select_tests.KNOWN_AREAS == set()


def corruptions(data: dict):
    """Each field dropped, emptied, retyped (including bool for int) or pointed out of range."""
    for key in data:
        yield f"drop {key}", {k: v for k, v in data.items() if k != key}
        for value in (None, 7, True, "x", [], {}):
            if value != data[key]:
                yield f"{key}={value!r}", {**data, key: value}
    yield "index out of range", {**data, "reads": {"a.json": [len(data["tests"])]}}
    yield "bool index", {**data, "reads": {"a.json": [True]}}
    yield "empty index list", {**data, "programs": {"lake": []}}
    yield "status missing a test", {**data, "status": {}}
    yield "bool exit", {**data, "status": {t: {**s, "exit": False} for t, s in data["status"].items()}}
    yield "duplicate test", {**data, "tests": data["tests"] * 2}


def test_a_malformed_map_is_rejected():
    data = make_map({"t1": {"f": [("a.py", "f")], "r": ["d.json"]}, "t2": {"x": ["lake"]}})
    test_map.validate(json.loads(json.dumps(data)))
    for name, corrupt in corruptions(data):
        if name.startswith(("drop created", "created=", "commit='x'")) or name in (
                "reads={}", "dirs={}", "programs={}"):
            continue  # informational, still a commit, or a table that may well be empty
        with pytest.raises(ValueError):
            test_map.validate(corrupt)
            pytest.fail(name)


# --- --impacted, the map-free fast path: every test file is reachable from a source path,
# so that the fast path can run it at all; unknown inputs select the full suite.


@pytest.fixture(scope="module")
def selector():
    with pytest.MonkeyPatch.context() as patch:
        import conftest
        patch.syspath_prepend(str(conftest.ROOT / "tools"))  # as the tool runs
        import select_tests
        yield select_tests


def tracked(selector):
    listed = subprocess.run(["git", "ls-files", "-z"], cwd=selector.ROOT, capture_output=True,
                            check=True, timeout=HANG_TIMEOUT).stdout.decode().split("\0")
    return [path for path in listed if path and not path.startswith("tests/test_")
            and (selector.ROOT / path).is_file()]


def test_every_test_file_is_reachable_from_a_source_path(selector):
    tests = [path.relative_to(selector.ROOT).as_posix() for path in selector.TESTS]
    sources, unreached = {}, []
    files = None
    for test in tests:
        imported = sorted(f for f in selector.closure(test) if f != test and not f.startswith("tests/test_"))
        if imported:
            sources[test] = imported[0]
            continue
        files = files if files is not None else tracked(selector)
        found = next((path for path in files if selector.reaches(test, path)), None)
        if found is None:
            unreached.append(test)
        else:
            sources[test] = found
    assert unreached == [], ("no source path selects these test files; name their sources in "
                             "tools/select_tests.py EXTRA_SOURCES")
    # The fast path itself selects each through its source, without the full fallback.
    for test in ("tests/test_evidence_bounds.py", "tests/test_precommit_hook.py",
                 "tests/test_agent_policy_rerun.py", "tests/test_coverage_dashboard.py"):
        plan = selector.impacted([sources[test]])
        assert not plan["fallback"] and test in plan["selected"], (test, sources[test])


@pytest.mark.parametrize("changed, expected", [
    # Native changes select their conformance tests.
    ("lean/VE/Norms/Wire.lean", {"tests/test_lean_conformance.py", "tests/test_soft_norms_lean.py"}),
    ("rust/ve/src/main.rs", {"tests/test_rust_conformance.py", "tests/test_p0_three_way.py",
                             "tests/test_nary_differential.py"}),
    # Data, tools and helpers select the tests that name or import them.
    ("usecases/asimov-laws/rules.ve", {"tests/test_asimov_laws.py"}),
    ("tools/hooks/precommit.py", {"tests/test_precommit_hook.py", "tests/test_hang_guards.py"}),
    ("tests/subprocesses.py", {"tests/test_cpu_bounds.py", "tests/test_hang_guards.py"}),
    ("tools/bench/baseline.py", {"tests/test_bench_baselines.py"}),
], ids=["lean", "rust", "use case", "hook", "test helper", "bench"])
def test_changes_select_the_tests_that_depend_on_them(selector, changed, expected):
    plan = selector.impacted([changed])
    assert not plan["fallback"]
    assert expected <= set(plan["selected"]), expected - set(plan["selected"])
    assert set(plan["always"]) <= set(plan["selected"])


@pytest.mark.parametrize("changed", ["tests/conftest.py", "tests/subprocesses.py", "tools/rust_build.py",
                                     "ve/surface/unambiguity.py"])
def test_what_the_conftest_loads_selects_every_test_below_it(selector, changed):
    """Review: a change to tests/conftest.py selected 18 of 214 files. pytest imports each
    conftest.py for every test below it, so a change to it, or to what it imports,
    selects them all."""
    assert changed in selector.closure("tests/conftest.py")
    plan = selector.impacted([changed])
    assert not plan["fallback"] and plan["selected_count"] == plan["full_count"]


def test_a_conftest_in_a_test_directory_joins_its_tests_closure(selector, tmp_path, monkeypatch):
    (tmp_path / "tests/deep").mkdir(parents=True)
    for conftest in ("conftest.py", "tests/conftest.py", "tests/deep/conftest.py"):
        (tmp_path / conftest).write_text("")
    (tmp_path / "tests/deep/test_x.py").write_text("")
    (tmp_path / "tests/test_y.py").write_text("")
    monkeypatch.setattr(selector, "ROOT", tmp_path)
    # Which conftest files join, each standing for its own (cached, real-tree) closure.
    monkeypatch.setattr(selector, "closure", lambda relative: frozenset({relative}))
    found = selector.test_closure.__wrapped__
    assert found("tests/deep/test_x.py") == {"tests/deep/test_x.py", "conftest.py", "tests/conftest.py",
                                             "tests/deep/conftest.py"}
    assert found("tests/test_y.py") == {"tests/test_y.py", "conftest.py", "tests/conftest.py"}


def test_narrow_changes_select_few_tests(selector):
    """The fast path is fast where the code is narrow (the product's modules import one
    another widely, so a kernel change still selects most of the suite)."""
    for changed in ("usecases/asimov-laws/rules.ve", "tools/hooks/precommit.py", "tools/bench/baseline.py"):
        assert selector.impacted([changed])["selected_count"] < 40, changed


def test_unknown_or_unreached_inputs_select_the_full_suite(selector):
    for paths in ([], ["new-unmapped-format.xyz"], ["ve/__init__.py"], ["ve/deleted_module.py"]):
        plan = selector.impacted(paths)
        assert plan["fallback"] and plan["selected_count"] == plan["full_count"], paths


def test_a_script_no_test_reaches_is_reported(selector, monkeypatch):
    monkeypatch.setattr(selector, "reaches", lambda test, changed: False)
    plan = selector.impacted(["tools/bench/baseline.py"])
    assert not plan["fallback"] and plan["scripts_without_tests"] == ["tools/bench/baseline.py"]
    assert plan["selected"] == sorted(plan["always"])
