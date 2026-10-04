"""The test selector: AST change units, map lookups, drift, the recorder, and whole plans.

Synthetic graphs and maps keep most checks independent of the repository's
history; the whole-plan checks run on this checkout with a map built here.
Every cache write goes under tmp_path (XDG_CACHE_HOME).
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import posixpath
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
import select_tests  # noqa: E402
import source_graph  # noqa: E402
import test_map  # noqa: E402
import test_map_recorder  # noqa: E402


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
        return any(name in str(annotation) for name in ("ast.stmt", "excepthandler", "match_case"))
    return {cls for cls in ast.stmt.__subclasses__()
            if cls not in (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            and any(holds(t) for t in cls._field_types.values())}


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
             for name, annotation in getattr(cls, "_field_types", {}).items() if "str" in str(annotation)}
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
                      "d": set(e.get("d", ())), "x": set(e.get("x", ())), "opaque": [],
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
    edges = {"t1": {"f": [("a.py", "f")], "r": ["d.json"], "d": ["data"], "x": ["lake"]},
             "t2": {"f": [("a.py", "g"), ("b.py", "<module>")]}}
    data = make_map(edges)
    back = test_map.unit_edges(json.loads(json.dumps(data)))
    assert back == {test: {"f": {(test, "<module>"), *map(tuple, e.get("f", ()))}, "r": set(e.get("r", ())),
                           "d": set(e.get("d", ())), "x": set(e.get("x", ()))}
                    for test, e in edges.items()}


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
    env = {"PATH": os.environ["PATH"], "VE_TESTMAP_OUT": str(out), "VE_TESTMAP_ROOT": str(root),
           "PYTHONDONTWRITEBYTECODE": "1"}
    subprocess.run([sys.executable, "start.py", *argv], cwd=root, env=env, check=True,
                   timeout=HANG_TIMEOUT)
    tracked = ({p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()},
               {".", *(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_dir())})
    return test_map.read_unit(out, tracked)


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
    result = recorder_run(tmp_path, "", ("-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", ".",
                                         "--confcutdir", ".", "tests/test_uses.py"),
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
    assert docs["commands"] == [[*docs["commands"][-1][:9], *docs["selected"]]]

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
    "data": ("tests/fixtures/_presence_probe.json", "docs/_presence_probe.md"),
    "everything": ("pyproject.toml", "_presence_probe.cfg"),
}
PRESENCE_UNITS = {"reader": "tests/test_background.py", "lister": "tests/test_bundle.py",
                  "importer": "tests/test_authoring.py", "runner": "tests/test_english.py",
                  "bystander": "tests/test_vacuity.py"}


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
    """Adding or deleting any kind of file selects its readers, the listers of its
    directory, and (a module) its importers, in the plan and the drift check alike."""
    assert not set(PRESENCE_UNITS.values()) & set(select_tests.SMOKE)
    edges = {test: {} for test in select_tests.units()}
    edges[PRESENCE_UNITS["reader"]] = {"r": [path]}
    edges[PRESENCE_UNITS["lister"]] = {"d": [posixpath.dirname(path) or "."]}
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
        expected = {PRESENCE_UNITS["reader"], PRESENCE_UNITS["lister"]}
        expected |= {"python": {PRESENCE_UNITS["importer"]}, "lean": {PRESENCE_UNITS["runner"]},
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
