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
import lean_mode_deps  # noqa: E402
import select_tests_seeds  # noqa: E402


@pytest.fixture(autouse=True)
def private_cache(tmp_path_factory, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path_factory.getbasetemp() / "cache"))
    monkeypatch.setenv("VE_TESTMAP_CACHE", str(tmp_path_factory.getbasetemp() / "maps"))
    monkeypatch.setenv("VE_LEAN_BUILDS", str(tmp_path_factory.getbasetemp() / "lean-builds"))
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
                      "p": set(e.get("p", ())), "v": set(e.get("v", ())),
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


def test_light_tier_keeps_the_heavy_test_of_a_changed_function(tmp_path):
    new = LIBRARY["pkg/core.py"].replace("min(x, LIMIT)", "max(x, LIMIT)")
    selected = sorted(impact(tmp_path, "pkg/core.py", new))
    inventory = tmp_path / "heavy.json"
    inventory.write_text(json.dumps({"run": "fixture", "collected_count": 2,
                                     "heavy": [{"nodeid": "tests/test_bounded.py::test_bounded",
                                                "seconds": 30, "run": "fixture"},
                                               {"nodeid": "tests/test_unrelated.py::test_unrelated",
                                                "seconds": 30, "run": "fixture"}]}))
    plan = select_tests.light_tier({"selected": selected, "commands": []}, inventory, jobs=2)
    assert plan["tier"]["selected_heavy"] == ["tests/test_bounded.py::test_bounded"]


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
                    "m": ["parse"], "p": ["typing"], "v": ["rights"]},
             "t2": {"f": [("a.py", "g"), ("b.py", "<module>")]}}
    data = make_map(edges)
    back = test_map.unit_edges(json.loads(json.dumps(data)))
    assert back == {test: {"f": {(test, "<module>"), *map(tuple, e.get("f", ()))}, "r": set(e.get("r", ())),
                           "d": set(e.get("d", ())), "x": set(e.get("x", ())),
                           "m": set(e.get("m", ())), "p": set(e.get("p", ())), "v": set(e.get("v", ()))}
                    for test, e in edges.items()}


def test_resumed_unit_merges_every_edge_kind(tmp_path):
    """A checkpoint has JSON lists, but a live recording and merge use sets."""
    unit = "tests/test_example.py"
    name = unit.replace("/", "__")
    recorded = {"f": [["a.py", "new"]], "r": ["new.json"], "d": ["new-dir"],
                "x": ["new-program"], "m": ["new.operation"], "p": ["new.presence"], "v": ["rights"],
                "exit": 0, "opaque": [], "seconds": 1.0}
    (tmp_path / f"{name}.result.json").write_text(json.dumps(recorded))
    resumed = test_map.run_unit(unit, tmp_path, 1, set())
    assert all(isinstance(resumed[key], set) for key in test_map.EDGE_KEYS)
    earlier = {"f": {("a.py", "old")}, "r": {"old.json"}, "d": {"old-dir"},
               "x": {"old-program"}, "m": {"old.operation"}, "p": {"old.presence"}, "v": {"norms"},
               "exit": 0, "opaque": [], "seconds": 1.0}
    test_map.merge({unit: resumed}, test_map.build_map({unit: earlier}, "0" * 40))
    for key in test_map.EDGE_KEYS:
        assert resumed[key] == ({tuple(v) if key == "f" else v for v in recorded[key]}
                                | earlier[key]), key


def test_operation_map_rejects_missing_and_bool_indices():
    data = make_map({"t1": {"m": ["parse"], "p": ["typing"], "v": ["rights"]}})
    test_map.validate(data)
    for field in ("operations", "presence", "modes"):
        missing = json.loads(json.dumps(data))
        del missing[field]
        with pytest.raises(ValueError):
            test_map.validate(missing)
        retyped = json.loads(json.dumps(data))
        retyped[field][next(iter(retyped[field]))] = [True]
        with pytest.raises(ValueError):
            test_map.validate(retyped)


def test_service_modes_narrow_only_known_recorded_users(tmp_path, monkeypatch):
    graph = make_graph(tmp_path, {}, lean={
        "lean/VE/Common.lean": "def common := 1\n",
        "lean/VE/Rights/Run.lean": "import VE.Common\ndef rights := 1\n",
        "lean/VE/Norms/Run.lean": "import VE.Common\ndef norms := 1\n",
        "lean/VE/Service/Protocol.lean": "import VE.Rights.Run\nimport VE.Norms.Run\ndef protocol := 1\n",
        "lean/Serve.lean": "import VE.Service.Protocol\ndef serve := 1\n",
    })
    monkeypatch.setattr(select_tests.lean_mode_deps, "load", lambda: {
        "rights": ["VE.Rights.Run"], "norms": ["VE.Norms.Run"]})
    monkeypatch.setattr(source_graph, "lean_executables", lambda root: {"ve_service": "Serve"})
    service = "lean/.lake/build/bin/ve_service"
    coverage = select_tests.Coverage(make_map({
        "rights": {"x": [service], "v": ["rights"]},
        "norms": {"x": [service], "v": ["norms"]},
        "unknown": {"x": [service]},
        "future": {"x": [service], "v": ["future"]},
        "direct": {"x": ["lake"]},
    }))
    assert select_tests.proposed_service_impact(coverage, graph, "lean/VE/Rights/Run.lean") == {
        "rights", "unknown", "future"}
    assert select_tests.proposed_service_impact(coverage, graph, "lean/VE/Common.lean") == {
        "rights", "norms", "unknown", "future"}
    for path in ("lean/VE/Service/Protocol.lean", "lean/Serve.lean"):
        assert select_tests.proposed_service_impact(coverage, graph, path) == {
            "rights", "norms", "unknown", "future"}
    selected = set()
    select_tests.file_impact(coverage, graph, set(coverage.tests),
                             lambda names, _: selected.update(names), "lean/VE/Rights/Run.lean", False)
    assert selected == {"rights", "norms", "unknown", "future", "direct"}
    monkeypatch.setattr(select_tests.lean_mode_deps, "load", lambda: None)
    assert select_tests.proposed_service_impact(coverage, graph, "lean/VE/Rights/Run.lean") == {
        "rights", "norms", "unknown", "future"}
    assert select_tests.service_impact(coverage, graph, "lean/VE/Rights/Run.lean") == {
        "rights", "norms", "unknown", "future"}


def test_compiled_mode_roots_cover_every_service_mode(monkeypatch):
    from ve.backends.service_schema import MODES
    roots = lean_mode_deps.load()
    assert roots is not None and set(roots) == set(MODES)
    assert all(root != "VE.Service.Protocol" for values in roots.values() for root in values)
    monkeypatch.setattr(lean_mode_deps, "digests", lambda: {"changed": "source"})
    assert lean_mode_deps.load() is None


def test_unverified_mode_activation_keeps_service_wide_selection(tmp_path, monkeypatch):
    graph = make_graph(tmp_path, {}, lean={
        "lean/VE/Rights/Run.lean": "def rights := 1\n",
        "lean/VE/Norms/Run.lean": "def norms := 1\n",
    })
    monkeypatch.setattr(select_tests.lean_mode_deps, "load", lambda: {
        "rights": ["VE.Rights.Run"], "norms": ["VE.Norms.Run"]})
    service = "lean/.lake/build/bin/ve_service"
    coverage = select_tests.Coverage(make_map({
        "rights": {"x": [service], "v": ["rights"]},
        "norms": {"x": [service], "v": ["norms"]},
    }))
    assert select_tests.proposed_service_impact(
        coverage, graph, "lean/VE/Rights/Run.lean") == {"rights"}
    assert select_tests.service_impact(
        coverage, graph, "lean/VE/Rights/Run.lean") == {"rights", "norms"}


def test_compiled_mode_roots_regenerate_from_lean():
    generated = lean_mode_deps.generate()
    assert generated["modes"] == json.loads(lean_mode_deps.OUTPUT.read_text())["modes"]


def test_shared_service_response_dependency_selects_every_mode():
    """`coding` calls Route's generator parser for every service answer."""
    root = Path(__file__).resolve().parents[1]
    graph = source_graph.Graph(root, [], {})
    graph.lean_modules = {"VE.Route.Run": "lean/VE/Route/Run.lean"}
    graph.lean_imports = {
        ".".join(file.relative_to(root / "lean").with_suffix("").parts):
        source_graph.lean_imports(file.read_text())
        for file in (root / "lean/VE").rglob("*.lean")
    }
    coverage = select_tests.Coverage(test_map.load(
        root / "docs/test-speed-b2/evidence/coverage-map.json.gz"))
    assert all("VE.Route.Run" in roots for roots in lean_mode_deps.load().values())
    assert coverage.service_users() <= select_tests.proposed_service_impact(
        coverage, graph, "lean/VE/Route/Run.lean")


def test_checker_pin_reader_still_selects_on_lock_change(tmp_path):
    graph = make_graph(tmp_path, {})
    coverage = select_tests.Coverage(make_map({
        "pin-test": {"r": ["lean/checkers.lock"]}, "other": {}}))
    selected = set()
    select_tests.file_impact(coverage, graph, set(coverage.tests),
                             lambda names, _: selected.update(names), "lean/checkers.lock", False)
    assert "pin-test" in selected


def test_recorder_tracks_each_service_request_mode(tmp_path):
    result = recorder_run(tmp_path, "import sys\nsys.audit('ve.service.mode', 'rights')\n"
                                    "sys.audit('ve.service.mode', 'norms')\n")
    assert result["v"] == {"rights", "norms"}


def test_lean_service_emits_mode_before_dispatch(monkeypatch):
    from ve.backends import lean_service
    events = []
    monkeypatch.setattr(lean_service.sys, "audit", lambda *event: events.append(event))
    monkeypatch.setattr(lean_service, "configured_seconds", lambda *args: (_ for _ in ()).throw(
        RuntimeError("dispatch stopped")))
    with pytest.raises(RuntimeError, match="dispatch stopped"):
        lean_service.LeanService().exchange("rights", "[]", 0)
    assert events == [("ve.service.mode", "rights")]


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


def git_line(rev: str) -> str:
    return subprocess.run(["git", "rev-parse", rev], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


# A format version no chain of converters reaches (tools/test_map.py CONVERTERS).
UNCONVERTIBLE = 1


def cached_map(directory: Path, commit: str, version: int | None = test_map.VERSION, mtime: int = 0) -> Path:
    """A map recorded at `commit` in the cache `directory`, written by map format `version`
    (None writes bytes that are not a gzip file)."""
    import gzip
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{commit}.json.gz"
    if version is None:
        path.write_bytes(b"not a map")
    else:
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            json.dump({**make_map({"t1": {"x": ["lake"]}}, commit), "version": version}, handle)
    os.utime(path, (mtime, mtime))
    return path


def test_find_map_names_each_nearer_map_it_skips(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("VE_TESTMAP_CACHE", str(tmp_path / "maps"))
    head, parent = (git_line(rev) for rev in ("HEAD", "HEAD~1"))
    old = cached_map(tmp_path / "maps", head, UNCONVERTIBLE)
    other_versions: list[Path] = []
    assert test_map.find_map(head, other_versions=other_versions) is None
    err = capsys.readouterr().err
    assert err == (f"test_map: skipped map {old} for {head[:10]}: recorded by map format version "
                   f"{UNCONVERTIBLE}, this checkout reads version {test_map.VERSION} "
                   "(record a new map: tools/test_map.py record)\n")
    assert other_versions == [old]
    # A current map farther down is returned; the nearer old one is still named, the current one not.
    current = cached_map(tmp_path / "maps", parent, mtime=1)
    assert test_map.find_map(head) == current
    captured = capsys.readouterr()
    assert str(old) in captured.err and str(current) not in captured.err and captured.out == ""
    # An old map farther than the chosen one would not have been used: nothing to say.
    old.unlink()
    farther = cached_map(tmp_path / "maps", parent, UNCONVERTIBLE)
    current = cached_map(tmp_path / "maps", head, mtime=1)
    assert test_map.find_map(head) == current and capsys.readouterr().err == ""
    farther.unlink()
    corrupt = cached_map(tmp_path / "maps", git_line("HEAD~2"), None, mtime=2)
    current.unlink()
    other_versions = []
    assert test_map.find_map(head, other_versions=other_versions) is None and other_versions == []
    err = capsys.readouterr().err
    assert err.startswith(f"test_map: skipped map {corrupt}: unreadable (") and err.count("\n") == 1


def test_select_tests_says_why_old_maps_left_it_without_one(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(select_tests, "time", types.SimpleNamespace(monotonic=lambda: 0.0))

    def main_output(cache: Path) -> tuple[str, str]:
        monkeypatch.setenv("VE_TESTMAP_CACHE", str(cache))
        monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "docs/TESTING.md"])
        assert select_tests.main() == 0
        captured = capsys.readouterr()
        return captured.out, captured.err

    cached_map(tmp_path / "old", git_line("HEAD"), UNCONVERTIBLE)
    cached_map(tmp_path / "old", git_line("HEAD~1"), UNCONVERTIBLE, mtime=1)
    out_without, err_without = main_output(tmp_path / "none")
    out_old, err_old = main_output(tmp_path / "old")
    assert out_old == out_without and "missing coverage map" in out_old.splitlines()[0]
    assert err_without == ""
    summary = [line for line in err_old.splitlines() if line.startswith("select_tests:")]
    assert summary == [f"select_tests: no map of format version {test_map.VERSION} for HEAD; skipped 2 "
                       "ancestor map(s) of other versions, so selection has no map "
                       "(record a new map: tools/test_map.py record)"]


def test_tree_maps_do_not_crowd_commit_maps_out_of_the_window(tmp_path, monkeypatch):
    """Draft 2, 2.3: `--run` saves a map per tree; 30 newer tree maps filled find_map's 30-newest
    window, so the main map below them was never looked at."""
    cache = tmp_path / "maps"
    monkeypatch.setenv("VE_TESTMAP_CACHE", str(cache))
    commit = cached_map(cache, git_line("HEAD~1"), mtime=1)
    for i in range(31):
        tree = cache / f"tree-{i:040x}.json.gz"
        tree.write_bytes(commit.read_bytes())
        os.utime(tree, (100 + i, 100 + i))
    assert test_map.find_map(git_line("HEAD")) == commit


def test_freshness_is_the_map_selection_would_use(tmp_path, monkeypatch, capsys):
    """`test_map.py fresh` (for verify.sh and fixloop.sh) accepts a map only if find_map gives it for the
    base and it is recent: neither an old-format map nor a tree map nor a stale one counts."""
    import datetime
    cache = tmp_path / "maps"
    monkeypatch.setenv("VE_TESTMAP_CACHE", str(cache))
    head = git_line("HEAD")
    assert test_map.fresh(head, 24) == 1 and capsys.readouterr().out == ""
    cached_map(cache, head, UNCONVERTIBLE)
    (cache / f"tree-{'0' * 40}.json.gz").write_bytes((cache / f"{head}.json.gz").read_bytes())
    assert test_map.fresh(head, 24) == 1 and capsys.readouterr().out == ""
    path = cached_map(cache, git_line("HEAD~1"))
    created = datetime.datetime.fromisoformat(test_map.load(path)["created"])
    assert test_map.fresh(head, 24, now=created + datetime.timedelta(hours=23)) == 0
    assert capsys.readouterr().out == f"{path}\n"
    assert test_map.fresh(head, 24, now=created + datetime.timedelta(hours=25)) == 1
    captured = capsys.readouterr()
    assert captured.out == "" and "25.0 h old, more than 24 h" in captured.err
    assert test_map.fresh(head, 24, max_behind=0, now=created) == 1
    assert "1 commits behind, more than 0" in capsys.readouterr().err


def test_each_map_format_version_ships_with_a_converter_or_a_recorded_map():
    """Astra re-check 6: ts-B2 raised the format to 7 and every cached map stopped counting, without
    a word. A new VERSION must name how maps of it exist from the start: a converter from the
    previous version, or the main commit whose map was recorded and published with the change."""
    assert test_map.VERSION in test_map.FORMAT_CHANGES, "name a converter or a recorded map in FORMAT_CHANGES"
    assert max(test_map.FORMAT_CHANGES) == test_map.VERSION
    for version, (how, what) in test_map.FORMAT_CHANGES.items():
        if how == "converter":
            assert what == version - 1 and version in test_map.CONVERTERS, version
        else:
            assert how == "recorded" and isinstance(what, str) and len(what) == 40 \
                and set(what) <= set("0123456789abcdef"), version
    assert all(test_map.FORMAT_CHANGES.get(version, ("",))[0] == "converter" for version in test_map.CONVERTERS)


def test_a_version_6_map_converts_and_keeps_every_service_user(tmp_path, monkeypatch):
    import gzip
    monkeypatch.setenv("VE_TESTMAP_CACHE", str(tmp_path / "maps"))
    data = make_map({"t_service": {"x": ["lean/.lake/build/bin/ve_service"]}, "t_other": {}})
    old = {key: value for key, value in data.items() if key != "modes"}
    path = tmp_path / "maps" / f"{git_line('HEAD')}.json.gz"
    path.parent.mkdir()
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump({**old, "version": 6}, handle)
    loaded = test_map.load(path)
    assert loaded["version"] == test_map.VERSION and loaded["converted_from"] == 6 and loaded["modes"] == {}
    assert select_tests.Coverage(loaded).service_users({"rights"}) == {"t_service"}
    assert test_map.find_map(git_line("HEAD")) == path


def test_recording_starts_the_longest_units_first():
    previous = make_map({"t_short": {}, "t_long": {}, "t_mid": {}})
    previous["status"]["t_long"]["seconds"], previous["status"]["t_mid"]["seconds"] = 900.0, 30.0
    assert test_map.by_length(["t_short", "t_mid", "t_long", "t_new"], previous) == \
        ["t_new", "t_long", "t_mid", "t_short"]
    assert test_map.by_length(["b", "a"], None) == ["a", "b"]


# Each program runs under the recorder (`recorder_run`) as if the site hook had started it, then starts
# a Python child that may or may not record. Whether the hook is installed in this environment's
# site-packages (it is while tools/test_map.py records this very file) changes nothing below.
HOOKED = "sys.modules['_ve_testmap'] = types.ModuleType('_ve_testmap')\n"
CHILDREN = {
    # This environment's interpreter with this recording's variables: if its record file is missing,
    # it died before any code under the root ran (here, it ran none, and the hook is not installed).
    "records here": (HOOKED + "subprocess.run([sys.executable, '-c', 'pass'], check=True)\n", False),
    # Another interpreter: the base one, outside this environment, never has the hook.
    "another interpreter": (HOOKED + "subprocess.run([sys._base_executable, '-c', 'pass'], check=True)\n", True),
    "site skipped": (HOOKED + "subprocess.run([sys.executable, '-IS', '-c', 'pass'], check=True)\n", True),
    "another recording": (HOOKED + "subprocess.run([sys.executable, '-c', 'pass'], check=True,\n"
                          "               env={**os.environ, 'VE_TESTMAP_OUT': os.getcwd()})\n", True),
}


@pytest.mark.parametrize("program, opaque", CHILDREN.values(), ids=CHILDREN)
def test_a_child_that_records_here_and_left_no_file_ran_nothing(tmp_path, program, opaque):
    result = recorder_run(tmp_path, "import os, subprocess, sys, types\n" + program)
    assert bool(result["opaque"]) is opaque, result["opaque"]


def test_a_child_records_here_only_if_the_hook_started_this_process(tmp_path, monkeypatch):
    """A process whose recorder was started by hand (as `recorder_run` does) has no hook in its
    interpreter's site-packages to vouch for: its children's missing records stay opaque."""
    monkeypatch.setitem(test_map_recorder._state, "out", str(tmp_path))
    monkeypatch.setenv("VE_TESTMAP_OUT", str(tmp_path))
    monkeypatch.setenv("VE_TESTMAP_ROOT", str(ROOT))
    child = [sys.executable, "-c", "pass"]
    monkeypatch.setitem(sys.modules, test_map_recorder.HOOK, types.ModuleType(test_map_recorder.HOOK))
    assert test_map_recorder._records_here(sys.executable, child, None)
    assert not test_map_recorder._records_here(sys.executable, child, {"VE_TESTMAP_OUT": "/elsewhere",
                                                                        "VE_TESTMAP_ROOT": str(ROOT)})
    monkeypatch.delitem(sys.modules, test_map_recorder.HOOK)
    assert not test_map_recorder._records_here(sys.executable, child, None)


def test_the_hook_test_map_installs_is_the_one_the_recorder_checks():
    assert test_map.HOOK == test_map_recorder.HOOK


def test_a_recording_inside_a_recorded_test_hands_over_its_records(tmp_path, monkeypatch):
    """The selector's own tests record units; their children wrote to the nested recording only, so
    test_select_tests and test_run_order were opaque in every map."""
    outer, inner = tmp_path / "outer", tmp_path / "inner"
    outer.mkdir()
    inner.mkdir()
    (outer / "100.jsonl").write_text(json.dumps(["c", 200, True, False]) + "\n")
    (inner / "200.jsonl").write_text(json.dumps(["f", "ve/x.py", "f"]) + "\n")
    root = str(test_map.ROOT.resolve())
    monkeypatch.setenv("VE_TESTMAP_OUT", str(outer))
    monkeypatch.setenv("VE_TESTMAP_ROOT", "/elsewhere")
    test_map.share_with_outer(inner, {"VE_TESTMAP_ROOT": root})
    assert test_map.read_unit(outer, set())["opaque"]  # another root: its paths mean other files
    monkeypatch.setenv("VE_TESTMAP_ROOT", root)
    test_map.share_with_outer(inner, {"VE_TESTMAP_ROOT": root})
    result = test_map.read_unit(outer, set())
    assert result["opaque"] == [] and ("ve/x.py", "f") in result["f"]


def test_added_and_removed_lean_modules_select_only_importing_executables(tmp_path):
    graph = make_graph(tmp_path, {}, lean={"lean/Shared.lean": "import Lean\n",
                                            "lean/Used.lean": "import Shared\n"})
    graph.lean_imports["Main"] = ["Used"]
    graph.lean_imports["OtherMain"] = []
    from unittest.mock import patch
    with patch.object(source_graph, "lean_executables", return_value={"first": "Main", "second": "OtherMain"}):
        assert select_tests.lean_programs(graph, "lean/Shared.lean") == {"first"}


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


def mapped_reasons(plan: dict) -> set[str]:
    """The units a plan selected through the map (not smoke, not the static graph)."""
    return {test for test, reasons in plan["reasons"].items()
            if any(r != "smoke" and not r.endswith("(static)") for r in reasons)}


EVIDENCE_FILE = "docs/arch/AR-1/evidence/checks.json"


def test_an_evidence_file_selects_its_readers_not_every_unmapped_unit(head):
    """Draft 2, 2.3: the conftest closure's product modules hold the word "evidence", which named all
    41 evidence/ directories, so an evidence file selected every unit the map did not cover."""
    edges = {test: {} for test in select_tests.units()}
    edges["tests/test_bundle.py"] = {"r": [EVIDENCE_FILE]}
    data = make_map(edges, commit=head, failed=("tests/test_english.py",))
    plan = plan_for([select_tests.Change(EVIDENCE_FILE, real(EVIDENCE_FILE), real(EVIDENCE_FILE) + " ")], data)
    assert not plan["full"]
    assert mapped_reasons(plan) == {"tests/test_bundle.py"}
    assert "tests/test_english.py" not in plan["selected"], plan["reasons"].get("tests/test_english.py")


PRODUCT_WORDS = {
    "ve/__init__.py": "",
    "ve/words.py": "KEY = 'evidence'\nDATA = 'packs'\n",
    "ve/packs/p.json": "{}",
    "docs/b/evidence/e.json": "{}",
    "tests/test_bundle.py": "import ve.words\n",          # a product user only
    "tests/test_closure.py": "PATH = 'evidence'\n",       # the test side names the directory
}


def test_a_product_word_names_only_product_directories(tmp_path, monkeypatch):
    graph = make_graph(tmp_path, PRODUCT_WORDS)
    monkeypatch.setattr(source_graph, "load", lambda root: graph)
    _, mentions = graph.closure("tests/test_bundle.py")
    assert "dir:ve/packs" in mentions and "dir:docs/b/evidence" not in mentions
    assert "dir:docs/b/evidence" in graph.closure("tests/test_closure.py")[1]
    plan = plan_for([select_tests.Change("docs/b/evidence/e.json", "{}", "[]")], None)
    named = {test for test, reasons in plan["reasons"].items() if "names docs/b/evidence/e.json (static)" in reasons}
    assert named == {"tests/test_closure.py"}
    plan = plan_for([select_tests.Change("ve/packs/p.json", "{}", "[]")], None)
    assert "names ve/packs/p.json (static)" in plan["reasons"].get("tests/test_bundle.py", [])


def swapped_merge_lines(text: str) -> str:
    """.gitattributes with its last two merge-driver lines swapped (as arch-20261010-1 reordered them)."""
    lines = text.splitlines(keepends=True)
    merge = [i for i, line in enumerate(lines) if line.rstrip().endswith("merge=ve-generated")]
    lines[merge[-1]], lines[merge[-2]] = lines[merge[-2]], lines[merge[-1]]
    return "".join(lines)


def test_a_merge_driver_edit_of_gitattributes_selects_its_readers_and_git_users(head):
    """Draft 2, 2.3 cause C: .gitattributes counted as a root file that changes everything, though the
    edits of the window only moved merge-driver lines, which only git commands read."""
    every = select_tests.units()
    edges = {test: {} for test in every}
    edges["tests/test_regen_generated.py"] = {"r": [".gitattributes"]}
    edges["tests/test_precommit_hook.py"] = {"x": ["git"]}
    data = make_map(edges, commit=head)
    old = real(".gitattributes")
    new = swapped_merge_lines(old)
    assert new != old and select_tests.kind_of(".gitattributes") == select_tests.DATA
    plan = plan_for([select_tests.Change(".gitattributes", old, new)], data)
    expected = {"tests/test_regen_generated.py", "tests/test_precommit_hook.py"}
    assert not plan["full"] and mapped_reasons(plan) == expected
    coverage, graph = select_tests.Coverage(data), source_graph.load(select_tests.ROOT)
    assert select_tests.uncertain_units(coverage, graph, set(every), {".gitattributes": "M"},
                                        {".gitattributes": (old, new)}) == expected
    # A line that sets a checkout attribute rewrites what a checkout holds: everything, in both.
    crlf = old + "*.json text eol=crlf\n"
    plan = plan_for([select_tests.Change(".gitattributes", old, crlf)], data)
    assert plan["full"] and plan["full_reasons"] == [".gitattributes: checkout attributes changed"]
    assert select_tests.uncertain_units(coverage, graph, set(every), {".gitattributes": "M"},
                                        {".gitattributes": (old, crlf)}) == set(every)
    assert select_tests.uncertain_units(coverage, graph, set(every), {".gitattributes": "M"}, {}) == set(every)


GITATTRIBUTES_EDITS = {
    # (old, new, whether the edit may change checked-out bytes)
    "merge line moved": ("a merge=x\nb merge=y\n", "b merge=y\na merge=x\n", False),
    "comment": ("a merge=x\n", "# note\na merge=x\n", False),
    "export rule": ("a merge=x\n", "a merge=x\ndocs/ export-ignore\n", False),
    "diff driver": ("", "*.lean diff=lean\n", False),
    "text set": ("", "*.ve text\n", True),
    "text unset": ("*.ve text\n", "*.ve -text\n", True),
    "eol": ("", "*.sh eol=lf\n", True),
    "filter": ("", "*.bin filter=lfs\n", True),
    "binary macro": ("", "*.png binary\n", True),
    "line order of eol": ("*.a eol=lf\n*.a eol=crlf\n", "*.a eol=crlf\n*.a eol=lf\n", True),
    "macro defined": ("", "[attr]gen merge=x\n", True),
    "macro used": ("[attr]gen text\n", "[attr]gen text\n*.j gen\n", True),
    "quoted pattern": ("", '"a b" merge=x\n', True),
    "unknown token": ("", "a merge=x b@c\n", True),
}


@pytest.mark.parametrize("old, new, changed", GITATTRIBUTES_EDITS.values(), ids=GITATTRIBUTES_EDITS)
def test_only_checkout_attribute_edits_of_gitattributes_change_everything(old, new, changed):
    assert select_tests.checkout_attributes_changed(old, new) is changed


SHARED_FIELD = "lean_decoders"


def manifest_units() -> dict[str, dict]:
    return {"tests/test_file_reader.py": {"r": [select_tests.MANIFEST]}, "tests/test_whole.py": {"m": ["*"]},
            "tests/test_entry.py": {"m": ["parse"]}, "tests/test_registrar.py": {"p": ["parse"]},
            "tests/test_none.py": {}, select_tests.MANIFEST_TEST: {}}


def manifest_selection(tmp_path, old: str, new: str) -> tuple[select_tests.Selection, set[str]]:
    edges = manifest_units()
    coverage = select_tests.Coverage(make_map(edges))
    selection = select_tests.Selection(make_graph(tmp_path, {}), coverage, set(), list(edges))
    select_tests.manifest_change(selection, select_tests.Change(select_tests.MANIFEST, old, new))
    drift = select_tests.uncertain_units(coverage, make_graph(tmp_path, {}), set(edges),
                                         {select_tests.MANIFEST: "M"}, {select_tests.MANIFEST: (old, new)})
    return selection, drift


def test_a_shared_manifest_field_selects_its_whole_manifest_readers(tmp_path):
    """Draft 2, 2.3: a shared field (lean_decoders, in lf-14d and lf-16d) selected everything. `ve`
    hands shared fields out only with the whole manifest, which the map records."""
    old = (ROOT / select_tests.MANIFEST).read_text()
    changed = json.loads(old)
    assert SHARED_FIELD in changed
    changed[SHARED_FIELD] = {**changed[SHARED_FIELD], "seeded": 1}
    selection, drift = manifest_selection(tmp_path, old, json.dumps(changed))
    expected = {"tests/test_file_reader.py", "tests/test_whole.py", select_tests.MANIFEST_TEST}
    assert not selection.full and set(selection.reasons) == expected
    assert drift == expected
    # The version is checked by every importer of ve.assurance: still everything.
    changed["version"] = "seeded"
    selection, drift = manifest_selection(tmp_path, old, json.dumps(changed))
    assert selection.full and drift == set(manifest_units())


def test_an_authority_change_selects_the_registrations_of_its_entries(tmp_path):
    """`ve.assurance` reads each operation's authority at import (`_migrated`); a call of a guarded
    entry records nothing while nothing is migrated, but its caller imported the registration."""
    old = (ROOT / select_tests.MANIFEST).read_text()
    changed = json.loads(old)
    entry = next(op for op in changed["operations"] if op["id"] == "parse")
    entry["authority"] = "migrated" if entry["authority"] != "migrated" else "python"
    selection, drift = manifest_selection(tmp_path, old, json.dumps(changed))
    expected = {"tests/test_file_reader.py", "tests/test_whole.py", "tests/test_entry.py",
                "tests/test_registrar.py", select_tests.MANIFEST_TEST}
    assert not selection.full and set(selection.reasons) == expected and drift == expected


BASE_TREE, HEAD_TREE = "b" * 40, "c" * 40
LEAN_UNITS = {"service": "tests/test_lean_service.py", "metered": "tests/test_cpu_bounds.py",
              "lake": "tests/test_lean_conformance.py", "reader": "tests/test_background.py"}


def write_build(tree: str, digests: dict[str, str]) -> None:
    path = test_map.build_record_path(tree)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"lean_tree": tree, "platform": test_map.platform_tag(), "digests": digests}))


def cutoff_plan(head, tmp_path, monkeypatch, base: dict | None, now: dict | None) -> dict:
    """A plan for an edit of a Lean module every executable imports, with these build records of the
    base and head `lean/` trees (None: not recorded)."""
    monkeypatch.setenv("VE_LEAN_BUILDS", str(tmp_path / "builds"))
    monkeypatch.setattr(test_map, "lean_tree", lambda rev=None, root=None: BASE_TREE if rev == "HEAD" else HEAD_TREE)
    for tree, digests in ((BASE_TREE, base), (HEAD_TREE, now)):
        if digests is not None:
            write_build(tree, digests)
    edges = {test: {} for test in select_tests.units()}
    path = "lean/VE/Json.lean"
    edges[LEAN_UNITS["service"]] = {"x": ["lean/.lake/build/bin/ve_service"]}
    edges[LEAN_UNITS["metered"]] = {"x": ["lean/.lake/build/bin/ve_metered"]}
    edges[LEAN_UNITS["lake"]] = {"x": ["lake"]}
    edges[LEAN_UNITS["reader"]] = {"r": [path]}
    graph = source_graph.load(select_tests.ROOT)
    assert {"ve_service", "ve_metered"} <= select_tests.lean_programs(graph, path)
    return plan_for([select_tests.Change(path, real(path), real(path) + "\n-- c\n")], make_map(edges, commit=head))


def every_executable(digest: str = "0" * 64) -> dict[str, str]:
    return {name: digest for name in select_tests.lean_executables()}


def test_an_identical_rebuild_selects_no_runner(head, tmp_path, monkeypatch):
    """Draft 2, 2.3: in 2 of 5 Lean merges the rebuilt ve_service was byte-identical. A test that only
    runs an executable built the same is not selected; Lean source readers and lake users still are."""
    plan = cutoff_plan(head, tmp_path, monkeypatch, every_executable(), every_executable())
    assert plan["lean_cutoff"]["state"] == "applied" and plan["lean_cutoff"]["rebuilt"] == []
    assert mapped_reasons(plan) == {LEAN_UNITS["lake"], LEAN_UNITS["reader"]}
    assert ["lake", "build"] in plan["commands"] and list(select_tests.AUDIT) in plan["commands"]


def test_a_changed_binary_selects_all_its_runners(head, tmp_path, monkeypatch):
    plan = cutoff_plan(head, tmp_path, monkeypatch, every_executable(),
                       {**every_executable(), "ve_service": "1" * 64})
    assert plan["lean_cutoff"]["rebuilt"] == ["ve_service"]
    assert mapped_reasons(plan) == {LEAN_UNITS["service"], LEAN_UNITS["lake"], LEAN_UNITS["reader"]}
    # An executable the base build lacks counts as rebuilt.
    plan = cutoff_plan(head, tmp_path, monkeypatch, {k: v for k, v in every_executable().items() if k != "ve_metered"},
                       every_executable())
    assert plan["lean_cutoff"]["rebuilt"] == ["ve_metered"]
    assert LEAN_UNITS["metered"] in mapped_reasons(plan) and LEAN_UNITS["service"] not in mapped_reasons(plan)


@pytest.mark.parametrize("base, now, state", [
    (False, True, "no record of the base build"), (True, False, "no record of the head build"),
    (False, False, "no record of the base and head build")], ids=["base", "head", "both"])
def test_without_both_build_records_every_runner_is_selected(head, tmp_path, monkeypatch, base, now, state):
    plan = cutoff_plan(head, tmp_path, monkeypatch, every_executable() if base else None,
                       every_executable() if now else None)
    assert plan["lean_cutoff"]["state"] == state and plan["lean_cutoff"]["rebuilt"] is None
    assert set(LEAN_UNITS.values()) <= mapped_reasons(plan)


def test_no_cutoff_when_the_trees_cannot_show_the_change(head, tmp_path, monkeypatch):
    """A Lean change named without an edit (`--paths`), or one the working tree does not hold (the
    plan's base is its head), says nothing a build record could confirm: every runner stays."""
    monkeypatch.setenv("VE_LEAN_BUILDS", str(tmp_path / "builds"))
    write_build(test_map.lean_tree("HEAD"), every_executable())
    path = "lean/VE/Json.lean"
    edges = {test: {} for test in select_tests.units()}
    edges[LEAN_UNITS["service"]] = {"x": ["lean/.lake/build/bin/ve_service"]}
    data = make_map(edges, commit=head)
    for change in (select_tests.Change(path, real(path), real(path) + "\n-- c\n"),
                   select_tests.Change(path, real(path), real(path), known=False)):
        plan = plan_for([change], data)
        assert plan["lean_cutoff"]["rebuilt"] is None, plan["lean_cutoff"]
        assert LEAN_UNITS["service"] in mapped_reasons(plan)


def test_a_build_record_needs_a_current_build_of_one_tree(tmp_path, monkeypatch):
    monkeypatch.setenv("VE_LEAN_BUILDS", str(tmp_path / "builds"))
    trees = iter([BASE_TREE, BASE_TREE, BASE_TREE, BASE_TREE, HEAD_TREE])
    monkeypatch.setattr(test_map, "lean_tree", lambda rev=None, root=None: next(trees))
    monkeypatch.setattr(test_map, "executable_digests", lambda root=None: {"ve_service": "1" * 64})
    monkeypatch.setattr(test_map, "current_build", lambda root=None: False)
    assert test_map.record_build() is None and test_map.load_build(BASE_TREE) is None
    monkeypatch.setattr(test_map, "current_build", lambda root=None: True)
    assert test_map.record_build() == test_map.build_record_path(BASE_TREE)
    assert test_map.load_build(BASE_TREE) == {"ve_service": "1" * 64}
    test_map.build_record_path(BASE_TREE).unlink()
    assert test_map.record_build() is None  # the tree changed while the build was hashed
    for record in ({"lean_tree": HEAD_TREE, "platform": test_map.platform_tag(), "digests": {}},
                   {"lean_tree": BASE_TREE, "platform": "other-arch", "digests": {}},
                   {"lean_tree": BASE_TREE, "platform": test_map.platform_tag(), "digests": {"a": 1}}, []):
        test_map.build_record_path(BASE_TREE).write_text(json.dumps(record))
        assert test_map.load_build(BASE_TREE) is None, record


def test_a_current_build_is_up_to_date_and_traced(tmp_path, monkeypatch):
    (tmp_path / "lean/.lake/build/bin").mkdir(parents=True)
    (tmp_path / "lean/lakefile.toml").write_text('[[lean_exe]]\nname = "ve_a"\nroot = "A"\n')
    monkeypatch.setattr(test_map.lake_outputs, "stale", lambda lean, env=None: [])
    calls = []

    def lake(command, **options):
        calls.append(command)
        return subprocess.CompletedProcess(command, returncode)
    monkeypatch.setattr(test_map.subprocess, "run", lake)
    returncode = 0
    assert not test_map.current_build(tmp_path) and calls == []  # not built
    (tmp_path / "lean/.lake/build/bin/ve_a").write_bytes(b"binary")
    assert test_map.current_build(tmp_path) and calls == [["lake", "build", "--no-build", "ve_a"]]
    returncode = 3
    assert not test_map.current_build(tmp_path)
    returncode = 0
    monkeypatch.setattr(test_map.lake_outputs, "stale", lambda lean, env=None: [lean / ".lake/build/bin/ve_a"])
    assert not test_map.current_build(tmp_path)


def test_a_run_builds_the_head_for_the_cutoff_when_the_base_build_is_recorded(monkeypatch):
    plans = [{"full": False, "lean_cutoff": {"state": "no record of the head build"}},
             {"full": False, "lean_cutoff": {"state": "applied"}, "marker": "second"}]
    events = []
    monkeypatch.setattr(select_tests, "select", lambda *args, **kwargs: (events.append("select"), plans.pop(0))[1])
    monkeypatch.setattr(select_tests.test_map, "build_lean", lambda: events.append("build"))
    monkeypatch.setattr(select_tests, "run", lambda plan, **options: (events.append(plan.get("marker")), 0)[1])
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "lean/VE/Json.lean", "--run", "--json"])
    monkeypatch.setattr(select_tests, "light_tier", lambda plan, **options: plan)
    assert select_tests.main() == 0
    assert events == ["select", "build", "select", "second"]


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
    # tarch-select (draft 2 section 3.5, items 2-6; Astra re-check 6)
    ("tree maps fill find_map's window", test_tree_maps_do_not_crowd_commit_maps_out_of_the_window),
    ("a new map format needs no converter or map", test_each_map_format_version_ships_with_a_converter_or_a_recorded_map),
    ("the version 6 converter drops service users", test_a_version_6_map_converts_and_keeps_every_service_user),
    ("units record in name order", test_recording_starts_the_longest_units_first),
    ("a child without the hook counts as recorded", test_a_child_that_records_here_and_left_no_file_ran_nothing),
    ("a nested recording keeps its records", test_a_recording_inside_a_recorded_test_hands_over_its_records),
    ("product words name every directory of the name", test_a_product_word_names_only_product_directories),
    (".gitattributes changes everything", test_a_merge_driver_edit_of_gitattributes_selects_its_readers_and_git_users),
    ("checkout attributes are ignored", test_a_merge_driver_edit_of_gitattributes_selects_its_readers_and_git_users),
    ("shared manifest fields have no readers", test_a_shared_manifest_field_selects_its_whole_manifest_readers),
    ("an authority change selects only entry readers", test_an_authority_change_selects_the_registrations_of_its_entries),
    ("the cutoff ignores the digests", test_a_changed_binary_selects_all_its_runners),
    ("a missing build record counts as identical", test_without_both_build_records_every_runner_is_selected),
    ("equal trees are an identical build", test_no_cutoff_when_the_trees_cannot_show_the_change),
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

        def empty_hides(coverage, graph, all_units, add, path, presence_changed, python=None, called=None,
                        rebuilt=None):
            if python is not None and python[2] is not None and python[2].empty:
                presence_changed = False
            real_file_impact(coverage, graph, all_units, add, path, presence_changed, python, called, rebuilt)
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
    elif name == "tree maps fill find_map's window":
        monkeypatch.setattr(test_map, "commit_maps", lambda directory: list(directory.glob("*.json.gz")))
        arguments = (tmp_path, monkeypatch)
    elif name == "a new map format needs no converter or map":
        monkeypatch.setattr(test_map, "VERSION", test_map.VERSION + 1)
        arguments = ()
    elif name == "the version 6 converter drops service users":
        # The converter invents a mode for every unit: the service user seems to need another mode only.
        monkeypatch.setitem(test_map.CONVERTERS, 7, lambda data: {
            **data, "modes": {"norms": list(range(len(data["tests"])))}})
        arguments = (tmp_path, monkeypatch)
    elif name == "units record in name order":
        monkeypatch.setattr(test_map, "by_length", lambda selected, previous: sorted(selected))
        arguments = ()
    elif name == "a child without the hook counts as recorded":
        real_read_unit = test_map.read_unit

        def missing_children_ran_nothing(directory, files):
            result = real_read_unit(directory, files)
            result["opaque"] = [reason for reason in result["opaque"] if not reason.endswith("left no record")]
            return result
        monkeypatch.setattr(test_map, "read_unit", missing_children_ran_nothing)
        arguments = (tmp_path, *CHILDREN["another interpreter"])
    elif name == "a nested recording keeps its records":
        monkeypatch.setattr(test_map, "share_with_outer", lambda out, env: None)
        arguments = (tmp_path, monkeypatch)
    elif name == "product words name every directory of the name":
        real_mentions = source_graph.Graph._mentions
        monkeypatch.setattr(source_graph.Graph, "_mentions", lambda self, path, summary: real_mentions(
            self, "tests/as_if.py" if path.startswith(source_graph.PRODUCT) else path, summary))
        arguments = (tmp_path, monkeypatch)
    elif name == ".gitattributes changes everything":
        monkeypatch.setattr(select_tests, "GIT_ATTRIBUTES", "-")
        arguments = (head_commit(),)
    elif name == "checkout attributes are ignored":
        monkeypatch.setattr(select_tests, "checkout_attributes_changed", lambda old, new: False)
        arguments = (head_commit(),)
    elif name == "shared manifest fields have no readers":
        monkeypatch.setattr(select_tests.Coverage, "whole_manifest_readers", lambda self: set())
        arguments = (tmp_path,)
    elif name == "an authority change selects only entry readers":
        real_delta = select_tests.manifest_delta

        def no_authority(old, new):
            found = real_delta(old, new)
            if found is not None:
                found.authority = set()
            return found
        monkeypatch.setattr(select_tests, "manifest_delta", no_authority)
        arguments = (tmp_path,)
    elif name == "the cutoff ignores the digests":
        real_cutoff = select_tests.lean_cutoff
        monkeypatch.setattr(select_tests, "lean_cutoff", lambda base, after, known=True: {
            **real_cutoff(base, after, known), "state": "applied", "rebuilt": []})
        arguments = (head_commit(), tmp_path, monkeypatch)
    elif name == "equal trees are an identical build":
        real_tree = test_map.lean_tree
        monkeypatch.setattr(select_tests, "lean_cutoff", lambda base, after, known=True: {
            "state": "applied", "rebuilt": [], "same": [], "base_tree": real_tree(base), "head_tree": real_tree(after)})
        arguments = (head_commit(), tmp_path, monkeypatch)
    elif name == "a missing build record counts as identical":
        real_load = test_map.load_build
        monkeypatch.setattr(test_map, "load_build", lambda tree: real_load(tree) or {
            name: "0" * 64 for name in select_tests.lean_executables()})
        arguments = (head_commit(), tmp_path, monkeypatch, False, True, "no record of the base build")
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
