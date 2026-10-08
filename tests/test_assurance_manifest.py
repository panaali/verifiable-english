"""The operation assurance manifest is bound to the code it describes.

docs/spec/assurance-manifest.md specifies the manifest. These tests check it
against the actual code paths (entry points, Lean call sites, Lean modes and
case kinds, audited theorems, Rust commands, backing tests, decoder line
ranges) and exercise the two runtime obligations: operational failure is
`CheckerUnavailable`, never a verdict, UNKNOWN, `ResourceLimit` or
`InvalidInput`; and a migrated operation's verdict can only come from Lean.
"""
import ast
from dataclasses import replace
import importlib
import json
import os
from pathlib import Path
import re
import stat
import sys

import pytest

from subprocesses import HANG_TIMEOUT, expired_waits
from ve import assurance
from ve.backends import lean as lean_backend
from ve.errors import AuthorityViolation, CheckerUnavailable, ResourceLimit, VEError

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = assurance.manifest()
OPS = MANIFEST["operations"]
LEAN_BIN = ROOT / "lean/.lake/build/bin"


def _modules():
    for path in sorted((ROOT / "ve").rglob("*.py")):
        rel = path.relative_to(ROOT)
        yield ".".join(rel.with_suffix("").parts).removesuffix(".__init__"), rel, ast.parse(path.read_text())


def _qualified(tree):
    """Yield (qualname, node) for every function, including methods."""
    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + child.name
                if not isinstance(child, ast.ClassDef):
                    yield name, child
                yield from walk(child, name + ".")
    yield from walk(tree, "")


def _resolve(entry):
    module, qualname = entry.split(":")
    value = importlib.import_module(module)
    for part in qualname.split("."):
        value = getattr(value, part)
    return value.fget if isinstance(value, property) else value


def _manifest_entries():
    return {(entry, op["id"]) for op in OPS for entry in op["python"]}


# --- schema -----------------------------------------------------------------

def test_schema_and_vocabulary():
    assert MANIFEST["version"] == assurance.MANIFEST_VERSION
    assert set(MANIFEST) == {"version", "spec", "migration_plan", "outcome_classes", "authorities", "trusted",
                             "reviewed_broad_handlers", "lean_decoders", "plan_operations", "non_verdict_api",
                             "operations"}
    assert (ROOT / MANIFEST["spec"]).exists() and (ROOT / MANIFEST["migration_plan"]).exists()
    assert set(MANIFEST["authorities"]) == set(assurance.AUTHORITIES)
    ids = [op["id"] for op in OPS]
    assert len(ids) == len(set(ids))
    required = {"id", "summary", "class", "authority", "target", "assurance", "python", "outcomes",
                "lean", "rust", "lean_call_sites", "tests", "trusted", "notes"}
    for op in OPS:
        assert set(op) == required, op["id"]
        assert op["class"] in ("leaf", "combination", "search", "surface")
        assert op["authority"] in assurance.AUTHORITIES
        assert op["target"] in ("lean", "rust", "python")
        assert op["assurance"]["current"] == "experimental"
        assert op["assurance"]["at_switch"] in ("experimental", "reference-theorems-checked")
        assert op["assurance"]["reason"]
        assert set(op["trusted"]) <= set(MANIFEST["trusted"]), op["id"]
        assert op["tests"], op["id"]


def test_operational_failure_is_its_own_outcome_class_everywhere():
    for op in OPS:
        outcomes = op["outcomes"]
        assert set(outcomes) == {"verdict", "unknown", "rejection", "budget", "operational"}
        assert outcomes["operational"] == ["CheckerUnavailable"], op["id"]
        for key in ("verdict", "unknown", "rejection", "budget"):
            assert "CheckerUnavailable" not in outcomes[key], (op["id"], key)
        assert set(outcomes["budget"]) <= {"ResourceLimit"}
        assert not any("UNKNOWN" in value for value in outcomes["verdict"] + outcomes["rejection"])
    assert not issubclass(CheckerUnavailable, (VEError, ValueError, OSError))
    assert issubclass(AuthorityViolation, CheckerUnavailable)


def test_trusted_components_are_all_referenced():
    used = {item for op in OPS for item in op["trusted"]}
    assert used == set(MANIFEST["trusted"])


# --- executable bindings: Python ----------------------------------------------

def test_python_entries_are_exactly_the_marked_functions():
    marked = set()
    for module, _, tree in _modules():
        for qualname, node in _qualified(tree):
            for decorator in node.decorator_list:
                if (isinstance(decorator, ast.Call) and getattr(decorator.func, "id", None) == "semantic_entry"):
                    marked.add((f"{module}:{qualname}", decorator.args[0].value))
    assert marked == _manifest_entries()


def test_python_entries_resolve_to_guarded_callables():
    for entry, op_id in _manifest_entries():
        fn = _resolve(entry)
        assert getattr(fn, "__ve_operation__", None) == op_id, entry
        expected_engine = "lean" if next(op for op in OPS if op["id"] == op_id)["authority"] == "migrated" else "python"
        assert fn.__ve_engine__ == expected_engine
    for op_id, rows in assurance.ENTRIES.items():
        assert {(name, op_id) for name, _ in rows} <= _manifest_entries()


BACKEND = "ve.backends.lean"


def _absolute(module, node):
    """The absolute module named by an ImportFrom in `module`."""
    if not node.level:
        return node.module or ""
    package = module.split(".")
    package = package[:len(package) - node.level] if not module.endswith("__init__") else package
    return ".".join(package + ([node.module] if node.module else []))


def _backend_calls(module, tree, is_package=False):
    """(qualname, operation) for every call of ve.backends.lean.run in `tree`, however imported,
    and every other reference to that function (which the test forbids)."""
    context = module if not is_package else module + ".__init__"
    modules, functions = {}, set()   # local name -> dotted module; local names of `run`
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    modules[alias.asname] = alias.name
                else:
                    modules[alias.name.split(".")[0]] = alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            base = _absolute(context, node)
            for alias in node.names:
                name = alias.asname or alias.name
                if base == BACKEND and alias.name == "run":
                    functions.add(name)
                elif base == BACKEND and alias.name == "*":
                    functions.add("run")
                else:
                    modules[name] = f"{base}.{alias.name}"

    def dotted(expr):
        if isinstance(expr, ast.Name):
            return modules.get(expr.id)
        if isinstance(expr, ast.Attribute):
            head = dotted(expr.value)
            return head and f"{head}.{expr.attr}"
        return None

    def is_run(expr):
        return ((isinstance(expr, ast.Name) and expr.id in functions)
                or (isinstance(expr, ast.Attribute) and expr.attr == "run" and dotted(expr.value) == BACKEND))

    calls, references = set(), set()

    def visit(node, qualname):
        # Each use is attributed to its innermost enclosing function (or "<module>").
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            qualname = node.name if qualname == "<module>" else f"{qualname}.{node.name}"
        children = list(ast.iter_child_nodes(node))
        if isinstance(node, ast.Call) and is_run(node.func):
            operation = node.args[0] if node.args else None
            calls.add((qualname, operation.value if isinstance(operation, ast.Constant) else None))
            children.remove(node.func)
        elif is_run(node):
            references.add(qualname)
            return
        for child in children:
            visit(child, qualname)

    visit(tree, "<module>")
    return calls, references


def test_backend_call_scanner_sees_through_aliases():
    source = """
from .backends import lean as lb
from ve.backends.lean import run as go
import ve.backends.lean as vbl
import ve.backends.lean
from . import backends

def a():
    lb.run("bundle.check", 1)
def b():
    go("bundle.check", 1)
def c():
    vbl.run("graph.compose", 1)
def d():
    ve.backends.lean.run("graph.compose", 1)
def e():
    backends.lean.run("bundle.check", 1)
def f():
    table = {"x": lb.run}
def g(op):
    lb.run(op, 1)
"""
    calls, references = _backend_calls("ve.sample", ast.parse(source))
    assert {(q, o) for q, o in calls if q in "abcdeg"} == {
        ("a", "bundle.check"), ("b", "bundle.check"), ("c", "graph.compose"), ("d", "graph.compose"),
        ("e", "bundle.check"), ("g", None)}
    assert references == {"f"}


def test_lean_call_sites_are_exactly_the_backend_calls():
    sites, references = set(), set()
    for module, rel, tree in _modules():
        if rel.as_posix() == "ve/backends/lean.py":
            continue
        calls, refs = _backend_calls(module, tree, rel.name == "__init__.py")
        sites |= {(f"{module}:{qualname}", op) for qualname, op in calls}
        references |= {f"{module}:{qualname}" for qualname in refs}
    assert not references, f"ve.backends.lean.run used other than as a direct call: {sorted(references)}"
    assert all(op is not None for _, op in sites), "the operation of a Lean call must be a literal"
    declared = {(site, op["id"]) for op in OPS for site in op["lean_call_sites"]}
    assert sites == declared
    for site, op_id in declared:
        binding = next(op for op in OPS if op["id"] == op_id)["lean"]["bindings"]
        assert binding, site
        _resolve(site)


def test_only_the_backend_starts_processes():
    starters = set()
    for module, rel, tree in _modules():
        for node in ast.walk(tree):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import) else
                     [node.module] if isinstance(node, ast.ImportFrom) and node.level == 0 else [])
            if any(name in ("subprocess", "multiprocessing") or name.startswith("subprocess.") for name in names):
                starters.add(rel.as_posix())
    assert starters == {"ve/backends/lean.py", "ve/backends/lean_service.py",
                        "ve/backends/rust_jsonl.py"}


def test_broad_exception_handlers_are_reviewed():
    """A handler broad enough to catch CheckerUnavailable could turn it into a result."""
    broad = ("Exception", "BaseException", "RuntimeError")
    found = set()
    def own(node):
        # The node's own body, not nested functions (reported under their own name).
        pending = list(ast.iter_child_nodes(node))
        while pending:
            child = pending.pop()
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                yield child
                pending.extend(ast.iter_child_nodes(child))

    for _, rel, tree in _modules():
        for qualname, node in [("<module>", tree), *_qualified(tree)]:
            for handler in own(node):
                if not isinstance(handler, ast.ExceptHandler):
                    continue
                caught = (handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type])
                if handler.type is None or any(getattr(t, "id", None) in broad for t in caught):
                    found.add(f"{rel.as_posix()}:{qualname}")
    reviewed = MANIFEST["reviewed_broad_handlers"]
    assert found == set(reviewed), "\n".join(sorted(found ^ set(reviewed)))
    assert all(reason for reason in reviewed.values())


def test_english_admission_is_python_authoritative():
    assert {op["authority"] for op in OPS} <= {"python", "migrated", "lean-only"}
    assert assurance.enforced_operations() == frozenset()


# --- completeness: omissions that no decorator comparison can see ----------------

def _plan_section(heading):
    text = (ROOT / MANIFEST["migration_plan"]).read_text()
    return text.split(heading, 1)[1].split("\n### ", 1)[0]


def test_every_plan_operation_has_a_manifest_operation():
    """Review reproducer: environment and model validation (plan 2.3) had no operation entry."""
    section = _plan_section("### 2.3 ")
    listed = re.search(r"^- \*\*Operations:\*\* (.*?)\n- \*\*", section, re.S | re.M).group(1)
    listed = " ".join(listed.split()).rstrip(".")
    names = [name.strip() for name in re.split(r",\s*(?![^()]*\))", listed)]
    mapping = MANIFEST["plan_operations"]["operations"]
    assert names == list(mapping), set(names) ^ set(mapping)
    ids = {op["id"] for op in OPS}
    for name, ops in mapping.items():
        assert ops and set(ops) <= ids, name


def test_every_planned_lean_mode_is_carried_by_an_operation():
    """Review reproducer: the plan's `identity` mode (2.1) was named in the spec but carried by no operation."""
    section = _plan_section("### 2.1 ")
    rows = re.findall(r"^\| `([^`]+)`[^|]*\|.*\| (new [^|]*)\|$", section, re.M)
    assert rows
    planned = {mode for op in OPS for mode in (op["lean"] or {}).get("planned_modes", ())}
    bound = {(b["mode"], kind) for op in OPS for b in (op["lean"] or {}).get("bindings", ())
             for kind in b["kinds"]}
    for mode, _ in rows:
        if "/" in mode:   # an extension of an existing route kind, e.g. route/evaluate
            assert tuple(mode.split("/", 1)) in bound, mode
        else:
            assert mode in planned, mode


def _public_api():
    import types
    import ve
    return {name: getattr(ve, name) for name in dir(ve)
            if not name.startswith("_") and not isinstance(getattr(ve, name), types.ModuleType)}


def _is_entry(value):
    if hasattr(value, "__ve_operation__"):
        return True
    if isinstance(value, type):
        for attribute in vars(value).values():
            attribute = attribute.fget if isinstance(attribute, property) else attribute
            attribute = getattr(attribute, "__func__", attribute)
            if hasattr(attribute, "__ve_operation__"):
                return True
    return False


def test_every_public_api_name_is_an_entry_or_classified():
    """An unmarked public verdict producer (validate_reference was one) fails here."""
    api = _public_api()
    entries = {name for name, value in api.items() if _is_entry(value)}
    classified = [name for group in MANIFEST["non_verdict_api"] for name in group["names"]]
    assert len(classified) == len(set(classified))
    assert all(group["reason"] for group in MANIFEST["non_verdict_api"])
    assert not entries & set(classified), entries & set(classified)
    assert set(api) == entries | set(classified), "\n".join(sorted(set(api) ^ (entries | set(classified))))
    assert {"Environment", "FiniteModel", "Claim", "meaning_id", "source_id", "validate_reference",
            "formula_from_data", "formula_to_data"} <= entries


def test_lean_only_operations_have_no_python_verdict_path():
    """A lean-only operation has no Python verdict entry. Its only Python code is a relay of Lean's answer:
    a declared call site of `ve.backends.lean.run` under one of its bindings (senses.read), never a
    semantic entry."""
    for op in OPS:
        if op["authority"] == "lean-only":
            assert op["python"] == [], op["id"]
            assert op["id"] not in assurance.ENTRIES
            assert not op["lean_call_sites"] or op["lean"]["bindings"], op["id"]
            for site in op["lean_call_sites"]:
                assert not hasattr(_resolve(site), "__ve_operation__"), (op["id"], site)


# --- executable bindings: Lean and Rust ---------------------------------------

AUDITED = set(re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",
                         (ROOT / "lean/axioms.txt").read_text(), re.M))


def test_lean_theorems_are_audited_and_planned_ones_absent():
    for op in OPS:
        lean = op["lean"] or {}
        missing = set(lean.get("theorems", ())) - AUDITED
        assert not missing, (op["id"], missing)
        landed = set(lean.get("planned_theorems", ())) & AUDITED
        assert not landed, f"{op['id']}: move {landed} from planned_theorems to theorems"


def _lean_executables():
    text = (ROOT / "lean/lakefile.toml").read_text()
    return dict(re.findall(r'\[\[lean_exe\]\]\s*name = "([^"]+)"\s*root = "([^"]+)"', text))


def test_lean_bindings_name_real_executables_modes_and_kinds():
    executables = _lean_executables()
    for op in OPS:
        for binding in (op["lean"] or {}).get("bindings", ()):
            if binding["executable"] == "ve_service":
                # The service's modes are its handshake's (lean/VE/Service/Protocol.lean `modes`).
                from ve.backends.service_schema import MODES
                assert binding["mode"] in MODES, (op["id"], binding)
            elif binding["mode"]:
                root = ROOT / "lean" / (executables[binding["executable"]] + ".lean")
                assert f'"{binding["mode"]}"' in root.read_text(), (op["id"], binding)
            sources = [ROOT / path for path in binding["dispatch"]]
            assert sources and all(path.exists() for path in sources), (op["id"], binding)
            text = "".join(path.read_text() for path in sources)
            for kind in binding["kinds"]:
                assert f'"{kind}"' in text, (op["id"], kind)
        for path in (op["lean"] or {}).get("decoders", ()):
            assert path in {f["file"] for f in MANIFEST["lean_decoders"]["files"]}, (op["id"], path)


def _binding_keys(ops):
    return {(op["id"], b["executable"], b["mode"], kind) for op in ops
            for b in (op["lean"] or {}).get("bindings", ()) for kind in (b["kinds"] or [None])}


def test_every_lean_binding_has_a_probe():
    """conformance/binding_probes.py holds one accepted case per (operation, executable, mode, kind)."""
    from conformance.binding_probes import BUILDERS
    assert _binding_keys(OPS) == set(BUILDERS), _binding_keys(OPS) ^ set(BUILDERS)
    for op in OPS:
        for binding in (op["lean"] or {}).get("bindings", ()):
            response, counts = binding["response"], binding.get("counts", {})
            assert type(response) is dict and response, (op["id"], binding)
            assert all(type(f) is str and lean_backend.valid_type(t) for f, t in response.items()), response
            assert set(binding) <= {"executable", "mode", "kinds", "response", "counts", "uncounted", "dispatch", "note"}
            # Every size-carrying field (array or nat) is counted, or says why its size is Lean's to choose
            # (review reproducer: evaluation `values: []` for a one-formula case was `ok`).
            uncounted = binding.get("uncounted", {})
            sized = {name for name, spec in response.items() if spec.startswith("array<") or spec == "nat"}
            assert set(counts) | set(uncounted) == sized and not set(counts) & set(uncounted), (op["id"], binding)
            assert all(type(reason) is str and reason for reason in uncounted.values()), (op["id"], binding)
            for name, reference in counts.items():
                # A counted field is a declared nat or array; it counts a case array or a declared array.
                assert response.get(name, "").startswith("array<") or response.get(name) == "nat", name
                source, _, field = reference.partition(".")
                assert source in ("case", "row") and field, reference
                assert source == "case" or response.get(field, "").startswith("array<"), reference


def test_binding_drift_is_detected_without_lean():
    """Review reproducer: moving evaluate's `order` binding to check-certificate passed every test."""
    import copy
    from conformance.binding_probes import BUILDERS
    for index in range(3):
        mutated = copy.deepcopy(OPS)
        evaluate = next(op for op in mutated if op["id"] == "evaluate")
        evaluate["lean"]["bindings"][index]["mode"] = "check-certificate"
        assert _binding_keys(mutated) != set(BUILDERS), index


@pytest.fixture(scope="module")
def lean_bin():
    import shutil
    import subprocess
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    if not os.environ.get("VE_LEAN_PREBUILT"):
        build = subprocess.run([lake, "build"], cwd=ROOT / "lean", capture_output=True, text=True, timeout=3600)
        assert build.returncode == 0, build.stdout + build.stderr
    return LEAN_BIN


def test_every_lean_binding_routes_its_operation(lean_bin):
    """Each probe is accepted in its declared mode, through the backend (binding, response and row schema)."""
    from conformance.binding_probes import probes
    for (op_id, executable, mode, kind), case in probes().items():
        rows = lean_backend.run(op_id, lean_bin / executable, [case], runner=executable, mode=mode,
                                timeout=HANG_TIMEOUT)
        assert rows[0]["status"] == "ok", (op_id, executable, mode, kind, rows)


def _declared_binding(op_id, executable, mode, kind):
    op = next(op for op in OPS if op["id"] == op_id)
    return next(b for b in op["lean"]["bindings"] if (b["executable"], b["mode"]) == (executable, mode)
                and (kind in b["kinds"] if kind else not b["kinds"]))


def _miscounted(row, binding):
    """`row` with one counted field made one short or one long, for every counted field."""
    for name in binding.get("counts", {}):
        value = row[name]
        if type(value) is int:
            yield from ({**row, name: n} for n in (value - 1, value + 1) if n >= 0)
        else:
            extra = value[:1] or [_conforming(binding["response"][name][len("array<"):-1])]
            yield from ({**row, name: v} for v in ([value[:-1]] if value else []) + [value + extra])


def test_every_real_answer_is_counted_and_indexed(lean_bin, tmp_path):
    """Review reproducers: the real evaluation answer with `values: []` for a one-formula case was `ok` in
    every mode, and `case_index: false` on the real bundle answer was accepted. For every binding, its real
    answer miscounted in any counted field, or naming its case with a non-integer index, is unavailable."""
    from conformance.binding_probes import probes
    for (op_id, executable, mode, kind), case in probes().items():
        binding = _declared_binding(op_id, executable, mode, kind)
        [row] = lean_backend.run(op_id, lean_bin / executable, [case], runner=executable, mode=mode,
                                 timeout=HANG_TIMEOUT)
        assert lean_backend.row_problem(case, row, 0, binding["response"], binding.get("counts")) is None
        # lf-0 review B2: a row naming its case both by id and by position is no answer.
        assert lean_backend.row_problem(case, {**row, "case_index": 0}, 0, binding["response"],
                                        binding.get("counts"))
        forged = [*_miscounted(row, binding), *({**row, "case_index": i} for i in (False, 0.0, "0"))]
        assert len(forged) > 3 or not binding.get("counts"), (op_id, mode, kind)
        for index, bad in enumerate(forged):
            if executable == "ve_service":
                # The service's rows are bound by its schemas before `run` reads them; the binding's own
                # check still refuses each forged row.
                assert lean_backend.row_problem(case, bad, 0, binding["response"], binding.get("counts")), bad
                continue
            answer = tmp_path / f"forged_{index}.json"
            answer.write_text(json.dumps([bad]))
            fake = _fake_lean(tmp_path, f"print(open({str(answer)!r}).read())", f"forged_{index}")
            with pytest.raises(CheckerUnavailable, match="count|case indices|JSON result"):
                lean_backend.run(op_id, fake, [case], runner=executable, mode=mode, timeout=HANG_TIMEOUT)


def test_no_other_mode_accepts_an_operations_probe(lean_bin):
    """The declared mode is what routes the case: every other mode of the executable rejects it."""
    import subprocess
    from conformance.binding_probes import probes
    modes = {}
    for _, executable, mode, _ in _binding_keys(OPS):
        modes.setdefault(executable, set()).add(mode)
    for (op_id, executable, mode, kind), case in probes().items():
        if executable == "ve_service":
            # Each service mode is one runner, pinned by `runMode_*`; the norm-defaults and quantity
            # runners delegate the cases they do not own (to the norms route), as their one-shot
            # executables did, so a mode of another former executable may accept a probe.
            continue
        for other in sorted(modes[executable] - {mode}):
            if (op_id, executable, other, kind) in probes():
                # A shared kind such as admission has a declared binding in both modes.
                continue
            proc = subprocess.run([str(lean_bin / executable), *([other] if other else [])],
                                  input=json.dumps([case]), capture_output=True, text=True, timeout=HANG_TIMEOUT)
            row = json.loads(proc.stdout)[0]
            assert row["status"] == "error", (op_id, mode, kind, "accepted by", other or "(default)")


def test_rust_commands_exist():
    main = (ROOT / "rust/ve/src/main.rs").read_text()
    for op in OPS:
        for command in (op["rust"] or {}).get("commands", ()):
            assert f'"{command}"' in main, (op["id"], command)


def test_backing_tests_exist():
    for op in OPS:
        for node in op["tests"]:
            path, name = node.split("::")
            assert re.search(rf"^def {name}\(", (ROOT / path).read_text(), re.M), node


DECLARATION = re.compile(r"^(?:private |protected )?(?:def|abbrev|structure|inductive) ")


def test_trusted_decoder_line_ranges_are_pinned():
    total = 0
    for entry in MANIFEST["lean_decoders"]["files"]:
        lines = (ROOT / entry["file"]).read_text().split("\n")
        if lines[-1] == "":
            lines.pop()
        previous = 0
        for start, end in entry["ranges"]:
            assert previous < start <= end <= len(lines), entry["file"]
            assert start == 1 or DECLARATION.match(lines[start - 1]), (entry["file"], start)
            after = lines[end] if end < len(lines) else ""
            assert (after == "" or DECLARATION.match(after) or after.startswith(("theorem ", "end ", "/-"))), \
                (entry["file"], end, after)
            total += end - start + 1
            previous = end
        for name in entry["declarations"]:
            starts = [i + 1 for i, line in enumerate(lines)
                      if re.match(rf"^(?:private |protected )?(?:def|abbrev|structure) {re.escape(name)}\b", line)]
            assert any(a <= s <= b for s in starts for a, b in entry["ranges"]), (entry["file"], name)
    assert total == MANIFEST["lean_decoders"]["total_lines"]


def _pin_problems(root, entries):
    import hashlib
    problems = []
    for entry in entries:
        data = (root / entry["file"]).read_bytes()
        lines = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
        digest = hashlib.sha256(data).hexdigest()
        if (lines, digest) != (entry["lines"], entry["sha256"]):
            problems.append(f'{entry["file"]}: review the ranges, then pin "lines": {lines}, "sha256": "{digest}"')
    return problems


def test_decoder_files_are_pinned_whole():
    """Range-boundary checks accept a new declaration right after a range; the file pin does not."""
    problems = _pin_problems(ROOT, MANIFEST["lean_decoders"]["files"])
    assert not problems, "\n".join(problems)


def test_decoder_pin_detects_code_appended_after_a_range(tmp_path):
    """Review reproducer: a def appended right after a range passed the boundary checks."""
    entry = next(e for e in MANIFEST["lean_decoders"]["files"] if e["file"] == "lean/VE/Route/Wire.lean")
    lines = (ROOT / entry["file"]).read_text().split("\n")
    end = entry["ranges"][-1][1]
    appended = "def decodeExtra (j : Json) : Except String Json := pure j"
    assert DECLARATION.match(appended)   # the boundary check alone accepts it
    copy = tmp_path / entry["file"]
    copy.parent.mkdir(parents=True)
    copy.write_text("\n".join(lines[:end] + [appended, ""] + lines[end:]))
    assert _pin_problems(tmp_path, [entry])


JSON_USE = re.compile(r"getObjVal\?|getObjValD|getObjValAs\?|setObjVal!|Json\.mkObj|getArr\?|getStr\?")


def test_every_json_handling_lean_file_is_classified():
    """A Lean file that reads or builds JSON is a pinned decoder or has a recorded reason under other_json."""
    lean = ROOT / "lean"
    found = {path.relative_to(ROOT).as_posix() for path in lean.rglob("*.lean")
             if ".lake" not in path.parts and JSON_USE.search(path.read_text())}
    decoders = {entry["file"] for entry in MANIFEST["lean_decoders"]["files"]}
    other = MANIFEST["lean_decoders"]["other_json"]
    assert not decoders & set(other)
    assert found == decoders | set(other), "\n".join(sorted(found ^ (decoders | set(other))))
    assert all(reason for reason in other.values())


# --- the authority guard ------------------------------------------------------

def test_guard_blocks_every_python_entry_once_migrated():
    for op in OPS:
        for entry in op["python"]:
            fn = _resolve(entry)
            if fn.__ve_engine__ == "lean":
                assurance.require_authority(op["id"], "lean")
                continue
            with assurance.simulate_migration(op["id"]):
                assert op["id"] in assurance.enforced_operations()
                with pytest.raises(AuthorityViolation) as caught:
                    fn()
            assert caught.value.to_dict()["code"] == "CheckerUnavailable"
            assert caught.value.operation == op["id"]
    assert assurance.enforced_operations() == frozenset()


def test_guard_allows_the_lean_engine():
    with assurance.simulate_migration("evaluate"):
        assurance.require_authority("evaluate", "lean")
        with pytest.raises(AuthorityViolation):
            assurance.require_authority("evaluate", "rust")


# --- operational failure never becomes UNKNOWN or a verdict -------------------

@pytest.fixture
def p0():
    from conformance.p0 import VOCAB, envelope
    from ve.environment import Environment
    return Environment(envelope(VOCAB))


LEAVES = ("certificate.check", "countermodel.check")


def test_combinations_propagate_unavailability_instead_of_unknown(p0):
    from ve.ast import Bottom, Const, Not, Top, Unary
    from ve.equivalence import compare, validate_reference
    from ve.readings import check_readings
    from ve.vacuity import premise_status
    senior = Unary("senior", Const("alice"))
    raw = ["unary", "senior", ["const", "alice"]]
    sets = [{"id": "s", "version": 1, "readings": [{"kind": "asserted", "content": raw},
                                                   {"kind": "asserted", "content": ["not", raw]}]}]
    # Without migration these are ordinary verdicts and UNKNOWNs.
    assert premise_status(p0, (senior,))["status"] == "model"
    assert check_readings(p0, sets, raw)["verdict"] == "SOME"
    with assurance.simulate_migration(*LEAVES):
        for premises in ((senior,), (senior, Not(senior)), (Bottom(),)):
            with pytest.raises(CheckerUnavailable):
                premise_status(p0, premises)
        with pytest.raises(CheckerUnavailable):
            compare(p0, senior, Top())
        with pytest.raises(CheckerUnavailable):
            check_readings(p0, sets, raw)
        with pytest.raises(CheckerUnavailable):
            check_readings(p0, sets, ["top"])
        for formula in (senior, Top(), Bottom()):
            with pytest.raises(CheckerUnavailable):
                validate_reference(p0, formula)


def test_search_reports_found_only_through_the_countermodel_check(p0, monkeypatch):
    """Review reproducer: both searches returned Found with countermodel.check migrated."""
    from ve import search
    from ve.ast import Const, Not, Unary
    senior = Unary("senior", Const("alice"))
    assert search.find_countermodel(p0, (), senior).status == "Found"
    assert search.find_distinguishing_model(p0, senior, Not(senior)).status == "Found"
    assert search.find_distinguishing_model(p0, Not(senior), senior).status == "Found"
    with assurance.simulate_migration("countermodel.check"):
        for run in (lambda: search.find_countermodel(p0, (), senior),
                    lambda: search.find_distinguishing_model(p0, senior, Not(senior)),
                    lambda: search.find_distinguishing_model(p0, Not(senior), senior)):
            with pytest.raises(CheckerUnavailable):
                run()
        # NotFound publishes no witness and needs no check.
        assert search.find_countermodel(p0, (senior,), senior).status == "NotFound"
    # A candidate the check does not accept is never published.
    calls = []
    real = search.check_countermodel

    def refuse(env, premises, conclusion, model, **kwargs):
        calls.append((tuple(premises), conclusion))
        return replace(real(env, premises, conclusion, model, **kwargs), valid=False, status="NotCountermodel")
    monkeypatch.setattr(search, "check_countermodel", refuse)
    if os.environ.get("VE_AUTHORITY", "python") != "python":
        # A backend search returns one witness; a refused witness is a
        # disagreement between generator and check, never NotFound.
        with pytest.raises(CheckerUnavailable):
            search.find_countermodel(p0, (), senior)
        assert set(calls) == {((), senior)}
        calls.clear()
        with pytest.raises(CheckerUnavailable):
            search.find_distinguishing_model(p0, senior, Not(senior))
        assert set(calls) == {((senior,), Not(senior)), ((Not(senior),), senior)}
        calls.clear()
    # Python's generator keeps searching past a refused candidate.
    monkeypatch.setenv("VE_AUTHORITY", "python")
    assert search.find_countermodel(p0, (), senior).status == "NotFound"
    assert set(calls) == {((), senior)}
    calls.clear()
    assert search.find_distinguishing_model(p0, senior, Not(senior)).status == "NotFound"
    # Each direction of a distinguishing model is checked as a countermodel to it.
    assert set(calls) == {((senior,), Not(senior)), ((Not(senior),), senior)}


def test_argument_record_reports_unavailability_not_incompleteness():
    from ve import check_argument
    from ve.argument_fixtures import merged_vocabulary_example
    graph = merged_vocabulary_example()
    assert check_argument(graph).status == "Checked"
    with assurance.simulate_migration(*LEAVES):
        result = check_argument(graph)
    assert result.status == "CheckerUnavailable" and not result.composed
    assert result.errors[0]["code"] == "CheckerUnavailable"
    assert result.to_dict()["proof"] == "not_checked"


def _fake_lean(tmp_path, body, name="fake_lean"):
    path = tmp_path / name
    path.write_text(f"#!{sys.executable}\nimport json, sys, time\ncases = json.loads(sys.stdin.read())\n{body}\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


CASE = [{"id": "bundle", "kind": "bundle"}]
FAULTS = {
    "crash": "sys.exit(3)",
    "signal": "import os, signal; os.kill(os.getpid(), signal.SIGKILL)",
    "usage": "sys.exit(2)",
    "garbage": "print('not json')",
    "empty": "pass",
    "row-count": "print(json.dumps([]))",
    "not-objects": "print(json.dumps([1]))",
    "wrong-id": "print(json.dumps([{'id': 'other', 'status': 'ok'}]))",
    "ok-rows-exit-1": "print(json.dumps([{'id': c['id'], 'status': 'ok'} for c in cases])); sys.exit(1)",
    "error-rows-exit-0": "print(json.dumps([{'id': c['id'], 'status': 'error'} for c in cases]))",
    # Never answers; a test injects its deadline as expired (tests/subprocesses.py: expired_waits).
    "hang": "import threading; threading.Event().wait()",
    # Rows that are JSON objects but not an answer (review reproducer: exit 0 with `[{}]`).
    "empty-row": "print(json.dumps([{}]))",
    "no-status": "print(json.dumps([{'id': c['id']} for c in cases]))",
    "unknown-status": "print(json.dumps([{'id': c['id'], 'status': 'maybe'} for c in cases]))",
    "ok-without-id": "print(json.dumps([{'status': 'ok', 'lemmas': []} for c in cases]))",
    "null-id": "print(json.dumps([{'id': None, 'status': 'error', 'error': 'x'} for c in cases])); sys.exit(1)",
    "error-without-message": "print(json.dumps([{'id': c['id'], 'status': 'error'} for c in cases])); sys.exit(1)",
    "wrong-case-index": "print(json.dumps([{'case_index': 7, 'status': 'error', 'error': 'x'} for c in cases]));"
                        " sys.exit(1)",
    # Python's `False == 0` and `0.0 == 0` are not JSON equalities (review reproducer: `case_index: false`).
    "bool-case-index": "print(json.dumps([{'case_index': False, 'status': 'error', 'error': 'x'} for c in cases]));"
                       " sys.exit(1)",
    "float-case-index": "print(json.dumps([{'case_index': 0.0, 'status': 'error', 'error': 'x'} for c in cases]));"
                        " sys.exit(1)",
    "ok-without-fields": "print(json.dumps([{'id': c['id'], 'status': 'ok'} for c in cases]))",
    "ill-typed-field": "print(json.dumps([{'id': c['id'], 'status': 'ok', 'lemmas': 'all'} for c in cases]))",
}


@pytest.mark.parametrize("fault", FAULTS)
def test_backend_faults_are_checker_unavailable(tmp_path, monkeypatch, fault):
    fake = _fake_lean(tmp_path, FAULTS[fault])
    waits = expired_waits(monkeypatch, lean_backend, expire=lambda argv: fault == "hang")
    with pytest.raises(CheckerUnavailable) as caught:
        lean_backend.run("bundle.check", fake, CASE, runner="ve_conformance", mode="route",
                         timeout=HANG_TIMEOUT)
    assert caught.value.backend == "lean" and caught.value.operation == "bundle.check"
    assert waits == ([HANG_TIMEOUT] if fault == "hang" else [])


def test_row_schema():
    case, problem = {"id": "c"}, lean_backend.row_problem
    assert problem(case, {"id": "c", "status": "ok", "valid": True}, 0, {"valid": "bool"}) is None
    assert problem(case, {"id": "c", "status": "error", "error": "no", "valid": False}, 0, {"valid": "bool"}) is None
    assert problem(case, {"case_index": 0, "status": "error", "error": "no"}, 0, {}) is None
    assert problem(case, {"case_index": 1, "status": "error", "error": "no"}, 1, {}) is None
    for index, forged in ((0, False), (1, True), (0, 0.0), (1, 1.0), (0, "0"), (0, None), (0, [0])):
        assert problem(case, {"case_index": forged, "status": "error", "error": "no"}, index, {}), forged
        assert problem(case, {"id": "c", "case_index": forged, "status": "ok"}, index, {}), forged
    for case_id, forged in (("c", ["c"]), ("c", None), (1, True), (0, False), (1, 1.0)):
        assert problem({"id": case_id}, {"id": forged, "status": "ok"}, 0, {}), (case_id, forged)
        assert problem({"id": case_id}, {"id": forged, "status": "error", "error": "no"}, 0, {}), (case_id, forged)
    assert problem(case, {"id": "c", "status": "ok", "valid": 1}, 0, {"valid": "bool"})
    assert problem(case, {"id": "c", "status": "ok", "background": True}, 0, {"background": "nat"})
    assert problem(case, {"id": "c", "status": "ok", "background": -1}, 0, {"background": "nat"})
    assert problem(case, {"id": "c", "status": "ok", "background": 2}, 0, {"background": "nat"}) is None
    assert problem(case, {"id": "c", "status": "ok", "valid": True}, 0, {"valid": "bool", "background": "nat"})
    assert problem(case, {"status": "ok"}, 0, {})
    assert problem(case, [], 0, {})
    # Element types and counts (review reproducers: `checked: {}` and `lemmas: [1]`).
    bundle, schema, counts = {"id": "c", "lemmas": [{}, {}]}, {"lemmas": "array<string>", "checked": "nat"}, \
        {"lemmas": "case.lemmas", "checked": "case.lemmas"}
    ok = {"id": "c", "status": "ok", "lemmas": ["a", "b"], "checked": 2}
    assert problem(bundle, ok, 0, schema, counts) is None
    for bad in ({"checked": {}}, {"lemmas": [1, "b"]}, {"lemmas": ["a"]}, {"checked": 3}, {"checked": True},
                {"lemmas": ["a", "b", "c"], "checked": 3}, {"lemmas": [["a"], "b"]}):
        assert problem(bundle, {**ok, **bad}, 0, schema, counts), bad
    assert problem({"id": "c"}, ok, 0, schema, counts), "a case without the counted array"
    assert problem(case, {"id": "c", "status": "ok", "g": ["x"], "p": []}, 0,
                   {"g": "array<string>", "p": "array<json>"}, {"g": "row.p"})


def _conforming(spec):
    if spec.startswith("array<"):
        return []
    return {"bool": True, "nat": 0, "string": "", "object": {}, "json": None}[spec]


def _ill_typed(spec):
    """Values that do not have type `spec` (none for `json`)."""
    values = [None, True, -1, 1, "x", {}, [], [None], [1], ["x"], [{}], [[]]]
    return [v for v in values if not lean_backend.conforms(v, spec)]


@pytest.mark.parametrize("op_id, binding", [(op["id"], b) for op in OPS
                                            for b in (op["lean"] or {}).get("bindings", ())],
                         ids=lambda value: value if type(value) is str else
                         f"{value['executable']}-{value['mode'] or 'default'}-{','.join(value['kinds'])}")
def test_every_declared_response_field_is_enforced(op_id, binding):
    """For every binding: a missing, ill-typed, ill-element-typed or miscounted field is not an answer."""
    response, counts = binding["response"], binding.get("counts", {})
    case = {"id": "c", **{ref.partition(".")[2]: [] for ref in counts.values() if ref.startswith("case.")}}
    row = {"id": "c", "status": "ok", **{name: _conforming(spec) for name, spec in response.items()}}
    problem = lean_backend.row_problem
    assert problem(case, row, 0, response, counts) is None, (op_id, row)
    for name, spec in response.items():
        assert problem(case, {k: v for k, v in row.items() if k != name}, 0, response, counts), (op_id, name)
        for bad in _ill_typed(spec):
            assert problem(case, {**row, name: bad}, 0, response, counts), (op_id, name, bad)
    for name in counts:
        extra = 1 if response[name] == "nat" else [row[name][0] if row[name] else _conforming(response[name][6:-1])]
        assert problem(case, {**row, name: extra}, 0, response, counts), (op_id, name)


def test_missing_backend_is_checker_unavailable(tmp_path):
    with pytest.raises(CheckerUnavailable, match="cannot start"):
        lean_backend.run("bundle.check", tmp_path / "absent", CASE, runner="ve_conformance",
                         mode="route", timeout=HANG_TIMEOUT)


def test_backend_rejection_is_returned_as_a_semantic_row(tmp_path):
    fake = _fake_lean(tmp_path, "print(json.dumps([{'id': c['id'], 'status': 'error', 'error': 'forged'} "
                                "for c in cases])); sys.exit(1)")
    rows = lean_backend.run("bundle.check", fake, CASE, runner="ve_conformance", mode="route",
                            timeout=HANG_TIMEOUT)
    assert rows == [{"id": "bundle", "status": "error", "error": "forged"}]


def test_undeclared_call_site_inside_ve_is_refused(tmp_path):
    """The runtime complement of the static scan: an alias the scan cannot see still fails."""
    namespace = {"__name__": "ve.rogue", "backend": lean_backend, "absent": tmp_path / "absent"}
    exec("def rogue():\n    run = getattr(backend, 'r' + 'un')\n"
         "    return run('bundle.check', absent, [{'id': 'b', 'kind': 'bundle'}], runner='ve_conformance',"
         " mode='route', timeout=1)\n", namespace)
    with pytest.raises(RuntimeError, match="not a declared Lean call site"):
        namespace["rogue"]()
    namespace["__name__"] = "tools.rogue"   # outside the package: no public verdict, not restricted
    exec("def rogue():\n    return backend.run('bundle.check', absent, [{'id': 'b', 'kind': 'bundle'}],"
         " runner='ve_conformance', mode='route', timeout=1)\n", namespace)
    with pytest.raises(CheckerUnavailable):
        namespace["rogue"]()


@pytest.mark.parametrize("op_id, runner, mode, case", [
    ("bundle.check", "ve_conformance", "check-certificate", {"id": "x"}),
    ("bundle.check", "ve_conformance", "route", {"id": "x", "kind": "admission"}),
    ("bundle.check", "ve_norms_route", "", {"id": "x", "kind": "bundle"}),
    ("readings", "ve_conformance", "route", {"id": "x"}),
    ("evaluate", "ve_conformance", "route", {"id": "x", "kind": "bundle"}),
])
def test_backend_calls_must_be_declared(tmp_path, op_id, runner, mode, case):
    # The binding is checked before any process starts.
    with pytest.raises(RuntimeError, match="not declared"):
        lean_backend.run(op_id, tmp_path / "absent", [case], runner=runner, mode=mode, timeout=HANG_TIMEOUT)


def _bundle():
    return json.loads((ROOT / "usecases/math-mini-paper/t7-definitions-bundle.json").read_text())


def test_bundle_separates_rejection_from_unavailability(tmp_path, monkeypatch):
    from ve.bundle import check_bundle
    hang = _fake_lean(tmp_path, FAULTS["hang"], name="hang")
    configured_wait = HANG_TIMEOUT + 123.5
    with monkeypatch.context() as setting:
        setting.setenv("VE_LEAN_TIMEOUT", str(configured_wait))
        waits = expired_waits(setting, lean_backend)
        with pytest.raises(CheckerUnavailable, match=rf"no answer within {configured_wait} s"):
            check_bundle(_bundle(), lean_executable=hang)
    assert waits == [configured_wait]
    assert check_bundle(_bundle())["lean_outcome"] == "not_requested"
    with pytest.raises(CheckerUnavailable):
        check_bundle(_bundle(), lean_executable=tmp_path / "absent")
    rejecting = _fake_lean(tmp_path, "print(json.dumps([{'id': c['id'], 'status': 'error', 'error': 'no'} "
                                     "for c in cases])); sys.exit(1)", name="rejecting")
    with pytest.raises(VEError, match="did not accept"):
        check_bundle(_bundle(), lean_executable=rejecting)
    if (LEAN_BIN / "ve_conformance").exists():
        assert check_bundle(_bundle(), lean_executable=LEAN_BIN / "ve_conformance")["lean_outcome"] == "accepted"


@pytest.mark.parametrize("fault", ["empty-row", "no-status", "ok-without-fields", "ill-typed-field",
                                   "error-without-message"])
def test_malformed_rows_never_become_a_rejection(tmp_path, fault):
    """Review reproducer: `[{}]` with exit 0 was InvalidInput for bundles and `rejected` for arguments."""
    from ve import check_argument
    from ve.argument_fixtures import merged_vocabulary_example
    from ve.bundle import check_bundle
    fake = _fake_lean(tmp_path, FAULTS[fault])
    with pytest.raises(CheckerUnavailable):
        check_bundle(_bundle(), lean_executable=fake)
    result = check_argument(merged_vocabulary_example(), lean_executable=fake)
    assert result.status == "Checked" and not result.lean_checked
    assert result.lean_outcome == "unavailable", result.lean_detail


# Mutations of a well-formed three-lemma bundle answer (`checked`, `lemmas` hold the real meaning ids).
BUNDLE_ROW_FAULTS = {
    "checked-object": "row['checked'] = {}",
    "checked-bool": "row['checked'] = True",
    "checked-negative": "row['checked'] = -1",
    "checked-miscount": "row['checked'] = 2",
    "checked-string": "row['checked'] = '3'",
    "lemma-not-string": "row['lemmas'] = [1] + row['lemmas'][1:]",
    "lemmas-one-int": "row['lemmas'] = [1]",
    "lemmas-object": "row['lemmas'] = {}",
    "lemmas-dropped": "row['lemmas'] = row['lemmas'][1:]",
    "lemmas-and-checked-dropped": "row['lemmas'] = row['lemmas'][1:]; row['checked'] = 2",
    "lemmas-extra": "row['lemmas'] = row['lemmas'] + row['lemmas'][:1]; row['checked'] = 4",
    "lemmas-empty": "row['lemmas'] = []; row['checked'] = 0",
    "checked-missing": "del row['checked']",
    # Review reproducer: `case_index: false` on the real answer gave Checked with lean_outcome accepted.
    "case-index-false": "row['case_index'] = False",
    "case-index-float": "row['case_index'] = 0.0",
    "case-index-string": "row['case_index'] = '0'",
}


def _bundle_answer(tmp_path, mutation, name="bundle_lean", lean=None):
    """A runner answering the bundle case with the well-formed `ok` row, then `mutation` applied to it.

    With `lean`, the row is the real Lean runner's answer; otherwise it is built from the Python ids.
    """
    from ve.bundle import check_bundle
    ids = [report["meaning_id"] for report in check_bundle(_bundle())["lemmas"]]
    if lean is None:
        answer = (f"row = {{'id': cases[0]['id'], 'status': 'ok', 'checked': {len(ids)}, 'lemmas': {ids!r}}}")
    else:
        answer = ("import subprocess\n"
                  f"proc = subprocess.run([{str(lean)!r}, *sys.argv[1:]], input=json.dumps(cases),"
                  " capture_output=True, text=True)\n"
                  f"row = json.loads(proc.stdout)[0]\nassert row['lemmas'] == {ids!r}, row")
    return _fake_lean(tmp_path, f"{answer}\n{mutation}\nprint(json.dumps([row]))", name)


@pytest.mark.parametrize("fault", BUNDLE_ROW_FAULTS)
def test_malformed_bundle_answers_are_unavailable(tmp_path, fault):
    """Review reproducer: `checked: {}` became a Checked, Lean-accepted bundle; `lemmas: [1]` InvalidInput."""
    from ve.bundle import check_bundle
    runners = [_bundle_answer(tmp_path, BUNDLE_ROW_FAULTS[fault])]
    if (LEAN_BIN / "ve_conformance").exists():
        runners.append(_bundle_answer(tmp_path, BUNDLE_ROW_FAULTS[fault], "real_lean", LEAN_BIN / "ve_conformance"))
    for runner in runners:
        with pytest.raises(CheckerUnavailable):
            check_bundle(_bundle(), lean_executable=runner)


def test_well_formed_bundle_answers_are_verdicts(tmp_path):
    """The controls: the unmutated answer is accepted; a well-formed answer naming other ids is a rejection."""
    from ve.bundle import check_bundle
    result = check_bundle(_bundle(), lean_executable=_bundle_answer(tmp_path, "pass"))
    assert result["lean_checked"] and result["lean_outcome"] == "accepted"
    # lf-0 review B2: the same answer naming its case by position too is no answer.
    indexed = _bundle_answer(tmp_path, "row['case_index'] = 0", "indexed")
    with pytest.raises(CheckerUnavailable, match="position"):
        check_bundle(_bundle(), lean_executable=indexed)
    other = _bundle_answer(tmp_path, "row['lemmas'] = row['lemmas'][::-1]", "reordered")
    with pytest.raises(VEError, match="did not accept") as caught:
        check_bundle(_bundle(), lean_executable=other)
    assert type(caught.value) is not CheckerUnavailable


ARGUMENT_ROW_FAULTS = {
    "valid-string": "row['valid'] = 'true'",
    "valid-int": "row['valid'] = 1",
    "background-bool": "row['background'] = True",
    "background-negative": "row['background'] = -1",
    "background-object": "row['background'] = {}",
    "background-missing": "del row['background']",
}


def _route_argument():
    """merged_vocabulary_example over ve.core@0.2, so Lean replays it on the `route` binding."""
    from ve.argument import ArgumentGraph, Claim
    from ve.argument_fixtures import merged_vocabulary_example
    from ve.environment import Environment
    from ve.profiles import SPEC_REVISION
    graph = merged_vocabulary_example()
    env = Environment({"language": "ve.core@0.2", "profiles": ["relational-fol@0"], "spec_revision": SPEC_REVISION,
                       "vocabulary": graph.env.to_dict()["vocabulary"]})
    claims = tuple(Claim.create(env, claim.name, claim.source) for claim in graph.claims)
    return ArgumentGraph(env, claims, graph.deductions, graph.root)


def test_route_argument_is_replayed_on_the_route_binding():
    from ve import check_argument
    assert check_argument(_route_argument()).status == "Checked"
    if (LEAN_BIN / "ve_conformance").exists():
        assert check_argument(_route_argument(), lean_executable=LEAN_BIN / "ve_conformance").lean_outcome == "accepted"


@pytest.mark.parametrize("fault", ARGUMENT_ROW_FAULTS)
def test_malformed_argument_answers_are_unavailable(tmp_path, fault):
    """The same class for graph.compose: an ill-typed `valid` or `background` is not a rejection."""
    from ve import check_argument
    graph = _route_argument()
    body = ("from ve.background import background\nfrom ve.environment import Environment\nrows = []\n"
            "for c in cases:\n"
            "    row = {'id': c['id'], 'status': 'ok', 'valid': True,"
            " 'background': len(background(Environment(c['environment'])))}\n"
            f"    {ARGUMENT_ROW_FAULTS[fault]}\n    rows.append(row)\nprint(json.dumps(rows))")
    fake = _fake_lean(tmp_path, f"sys.path.insert(0, {str(ROOT)!r})\n{body}")
    control = _fake_lean(tmp_path, f"sys.path.insert(0, {str(ROOT)!r})\n{body.replace(ARGUMENT_ROW_FAULTS[fault], 'pass')}",
                         "control")
    assert check_argument(graph, lean_executable=control).lean_outcome == "accepted"
    result = check_argument(graph, lean_executable=fake)
    assert result.status == "Checked" and not result.lean_checked
    assert result.lean_outcome == "unavailable", result.lean_detail


def test_argument_separates_lean_rejection_from_unavailability(tmp_path, monkeypatch):
    from ve import check_argument, outstanding_obligations
    from ve.argument_fixtures import merged_vocabulary_example
    configured_wait = HANG_TIMEOUT + 123.5
    monkeypatch.setenv("VE_LEAN_TIMEOUT", str(configured_wait))
    waits = expired_waits(monkeypatch, lean_backend, expire=lambda argv: Path(argv[0]).name == "hang")
    graph = merged_vocabulary_example()
    outcomes = {}
    for name, body in (("absent", None), ("crash", FAULTS["crash"]), ("hang", FAULTS["hang"]),
                       ("rejecting", "print(json.dumps([{'id': c['id'], 'status': 'ok', 'valid': False} "
                                     "for c in cases]))")):
        executable = tmp_path / name if body is None else _fake_lean(tmp_path, body, name)
        result = check_argument(graph, lean_executable=executable)
        assert result.status == "Checked" and result.composed and not result.lean_checked
        outcomes[name] = (result.lean_outcome, result.to_dict()["lean_status"],
                          outstanding_obligations(graph, result)["lean_outcome"])
    assert outcomes["rejecting"] == ("rejected", "Lean-checked: no", "rejected")
    for name in ("absent", "crash", "hang"):
        assert outcomes[name] == ("unavailable", "Lean-checked: unavailable", "unavailable"), name
    assert waits and set(waits) == {configured_wait}
    assert check_argument(graph).lean_outcome == "not_requested"


# ve-argument-tableau@1 record ids of worked_examples() at df874bd (before P0-3), with checker_build
# (a digest of the checker sources, which changes with any code change) fixed to 64 zeros.
V1_RECORD_IDS = {
    None: {"g1": "05e8935ca20c23cf17b6216d685492006ca2da220c9cd61a5fe33717917a9acf",
           "g2": "2fa0892d7f53f1ebeb06e9741768e3e42d73ccc1cb633eb16f758385d99e7ece",
           "g3": "c822b6c8608a1d6a56d66cb864d3f54920aabf049476af56d297749c15542cdf"},
    "lean": {"g1": "05e8935ca20c23cf17b6216d685492006ca2da220c9cd61a5fe33717917a9acf",
             "g2": "ed1144ee5c21cd71564fcb702ffc62ad25d6684cdbe1f08d026162b6726ed45c",
             "g3": "d887e4db1243355c94ec8652f0b1ca3c9fcc54ba405a3953b3c70edf1871f2bf"},
    "rejecting": {"g1": "05e8935ca20c23cf17b6216d685492006ca2da220c9cd61a5fe33717917a9acf",
                  "g2": "f68c049213cec9920cc72e592bdcc5b75032f93cef770a70aba46ccbe282f16e",
                  "g3": "9ae3c6a9bfb48b706fb7a8fe0dc8200610156d7f0e568a6a92c1c3ea341f6722"},
}


def test_argument_record_identity_is_unchanged_except_for_unavailability(tmp_path, monkeypatch):
    """lean_outcome must not change the id of any record a v1 checker could already produce."""
    from ve import argument, check_argument
    monkeypatch.setattr(argument, "_checker_build", lambda: "0" * 64)
    from ve.argument_fixtures import worked_examples
    rejecting = _fake_lean(tmp_path, "print(json.dumps([{'id': c['id'], 'status': 'ok', 'valid': False} "
                                     "for c in cases]))", "rejecting")
    executables = {None: None, "rejecting": rejecting}
    if (LEAN_BIN / "ve_conformance").exists():
        executables["lean"] = LEAN_BIN / "ve_conformance"
    for key, executable in executables.items():
        for name, graph in worked_examples().items():
            record = check_argument(graph, lean_executable=executable).to_dict()
            assert "lean_outcome" not in record, (key, name)
            assert record["record_id"] == V1_RECORD_IDS[key][name], (key, name)
    unavailable = check_argument(worked_examples()["g2"], lean_executable=tmp_path / "absent").to_dict()
    assert unavailable["lean_outcome"] == "unavailable"
    assert unavailable["lean_status"] == "Lean-checked: unavailable"


def test_cli_reports_checker_unavailable_with_its_own_exit_code(tmp_path, capsys):
    from ve.__main__ import EXIT_CHECKER_UNAVAILABLE, main
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(_bundle()))
    assert main(["bundle", "check", str(path), "--lean", str(tmp_path / "absent")]) == EXIT_CHECKER_UNAVAILABLE == 5
    record = json.loads(capsys.readouterr().out)
    assert record["status"] == "CheckerUnavailable" and record["error"]["code"] == "CheckerUnavailable"


def _assist_session(tmp_path, capsys):
    from ve.assist.cli import main as assist_main
    from tests.test_assist import ENV, TEXT
    (tmp_path / "env.json").write_text(json.dumps(ENV))
    (tmp_path / "arg.txt").write_text(TEXT)
    session = tmp_path / "s.json"
    assert assist_main(["new", str(session), "--env", str(tmp_path / "env.json"), "--text",
                        str(tmp_path / "arg.txt"), "--target", "p2.1"]) == 0
    capsys.readouterr()
    return assist_main, str(session)


def test_assist_cli_exits_5_when_a_result_reports_checker_unavailable(tmp_path, capsys):
    """Session actions return CheckerUnavailable as a result; the exit code must still be 5."""
    assist_main, session = _assist_session(tmp_path, capsys)
    arguments = json.dumps({"target": "t_p2_1", "text": "@api is safe."})
    with assurance.simulate_migration("parse"):
        assert assist_main(["freeze", session, "t_p2_1", "@api is safe."]) == 5
        assert "CheckerUnavailable" in capsys.readouterr().out
        assert assist_main(["call", session, "freeze_target", arguments]) == 5
        assert json.loads(capsys.readouterr().out)["error"]["code"] == "CheckerUnavailable"
    # Rejections keep exit 2 and success exit 0.
    assert assist_main(["freeze", session, "t_p2_1", "@api is not a sentence"]) == 2
    assert assist_main(["call", session, "freeze_target", arguments]) == 0


def test_assist_exit_code_reads_the_error_code():
    from ve.assist.cli import exit_code
    assert exit_code({"ok": True}) == exit_code({"tools": []}) == 0
    assert exit_code({"ok": False, "error": {"code": "CheckerUnavailable", "message": "m"}}) == 5
    assert exit_code({"ok": False, "error": {"code": "InvalidInput", "message": "m"}}) == 2
    assert exit_code({"ok": False, "error": {"code": "BackendError", "message": "m"}}) == 2


def test_assist_status_reports_unavailability_not_a_failed_replay():
    from tests.test_assist import build_success, new_session
    session = new_session()
    build_success(session)
    assert session.apply("status", {})["ok"]
    with assurance.simulate_migration(*LEAVES):
        result = session.apply("status", {})
    assert not result["ok"] and result["error"]["code"] == "CheckerUnavailable", result


def test_english_marked_conclusion_unavailability_is_not_a_syntax_error():
    from ve.english import parse_english_argument
    from ve.environment import Environment
    example = ROOT / "examples/assist"
    env = Environment.from_json((example / "environment.json").read_bytes())
    options = {"vocabulary": json.loads((example / "environment.english.json").read_text())}
    text = "Every reviewed service is safe. The API is reviewed. Therefore the API is safe."
    assert parse_english_argument(env, text, **options).deductions
    with assurance.simulate_migration("certificate.check"):
        with pytest.raises(CheckerUnavailable):
            parse_english_argument(env, text, **options)


def test_english_graph_replay_unavailability_is_not_a_syntax_error(monkeypatch):
    """The claim-graph replay's CheckerUnavailable status is re-raised, not read as a failed replay."""
    from ve import argument
    from ve.english import parse_english_argument
    from ve.environment import Environment
    example = ROOT / "examples/assist"
    env = Environment.from_json((example / "environment.json").read_bytes())
    options = {"vocabulary": json.loads((example / "environment.english.json").read_text())}
    unavailable = argument.ArgumentResult("CheckerUnavailable", errors=(
        CheckerUnavailable("no Lean", operation="certificate.check", backend="lean").to_dict(),))
    monkeypatch.setattr(argument, "check_argument", lambda *args, **kwargs: unavailable)
    with pytest.raises(CheckerUnavailable, match="no Lean"):
        parse_english_argument(env, "Every reviewed service is safe. The API is reviewed. "
                                    "Therefore the API is safe.", **options)


def test_argument_require_available():
    from ve.argument import ArgumentResult
    with pytest.raises(CheckerUnavailable, match="gone") as caught:
        ArgumentResult("CheckerUnavailable", errors=({"code": "CheckerUnavailable", "message": "gone",
                                                      "operation": "certificate.check"},)).require_available()
    assert caught.value.operation == "certificate.check"
    checked = ArgumentResult("Incomplete")
    assert checked.require_available() is checked


# --- documentation ------------------------------------------------------------

def test_spec_tables_are_generated_from_the_manifest():
    text = (ROOT / "docs/spec/assurance-manifest.md").read_text()
    end = "<!-- END GENERATED -->"
    for begin, render in (
            ("<!-- BEGIN GENERATED DECODERS: python tools/assurance_manifest.py --write -->\n",
             assurance.render_decoders_markdown),
            ("<!-- BEGIN GENERATED: python tools/assurance_manifest.py --write -->\n", assurance.render_markdown)):
        assert begin in text and end in text
        assert text.split(begin, 1)[1].split(end, 1)[0] == render()
