"""The test selector: AST change units, map lookups, drift, the recorder, and whole plans.

Synthetic graphs and maps keep most checks independent of the repository's
history; the whole-plan checks run on this checkout with a map built here.
Every cache write goes under tmp_path (XDG_CACHE_HOME).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
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


@pytest.fixture(autouse=True)
def private_cache(tmp_path_factory, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path_factory.getbasetemp() / "cache"))
    monkeypatch.setenv("VE_TESTMAP_CACHE", str(tmp_path_factory.getbasetemp() / "maps"))
    monkeypatch.delenv("VE_TESTMAP", raising=False)


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
    results = {test: {"f": set(map(tuple, e.get("f", ()))), "r": set(e.get("r", ())),
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
    assert back == {test: {"f": set(map(tuple, e.get("f", ()))), "r": set(e.get("r", ())),
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


def recorder_run(tmp_path, program: str) -> dict:
    """Run `program` under the recorder (children start it as the .pth hook would) and fold the records."""
    root, out = tmp_path / "root", tmp_path / "out"
    root.mkdir()
    out.mkdir()
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
        "runpy.run_path(sys.argv[1], run_name='__main__')\n")
    env = {"PATH": os.environ["PATH"], "VE_TESTMAP_OUT": str(out), "VE_TESTMAP_ROOT": str(root)}
    subprocess.run([sys.executable, "start.py", "main.py"], cwd=root, env=env, check=True,
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
        subprocess.run([sys.executable, "-I", "-c", "pass"], check=True)
    '''))
    assert result["opaque"]


@pytest.fixture(scope="module")
def head():
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


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


SAFETY_CASES = (
    # (mutation of the selector, the check above that must then fail)
    ("tests_of matches only the exact name", test_lookups_match_nested_code_but_not_name_prefixes),
    ("module-level statements are ignored", test_a_changed_constant_selects_its_readers_here_and_in_importers),
    ("drift is ignored", test_tests_that_ran_no_drifted_code_keep_their_map_entry),
    ("new functions are trusted", test_a_new_function_nothing_calls_by_name_selects_the_whole_file),
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
    else:
        monkeypatch.setattr(select_tests.Coverage, "file_wide", lambda self, file, defs: set())
        arguments = (tmp_path,)
    with pytest.raises(AssertionError):
        check(*arguments)
