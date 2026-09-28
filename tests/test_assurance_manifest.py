"""The operation assurance manifest is bound to the code it describes.

docs/spec/assurance-manifest.md specifies the manifest. These tests check it
against the actual code paths (entry points, Lean call sites, Lean modes and
case kinds, audited theorems, Rust commands, backing tests, decoder line
ranges) and exercise the two runtime obligations: operational failure is
`CheckerUnavailable`, never a verdict, UNKNOWN, `ResourceLimit` or
`InvalidInput`; and a migrated operation's verdict can only come from Lean.
"""
import ast
import importlib
import json
import os
from pathlib import Path
import re
import stat
import sys

import pytest

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
    return value


def _manifest_entries():
    return {(entry, op["id"]) for op in OPS for entry in op["python"]}


# --- schema -----------------------------------------------------------------

def test_schema_and_vocabulary():
    assert MANIFEST["version"] == assurance.MANIFEST_VERSION
    assert set(MANIFEST) == {"version", "spec", "migration_plan", "outcome_classes", "authorities", "trusted",
                             "reviewed_broad_handlers", "lean_decoders", "operations"}
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
        assert fn.__ve_engine__ == "python"
    for op_id, rows in assurance.ENTRIES.items():
        assert {(name, op_id) for name, _ in rows} <= _manifest_entries()


def test_lean_call_sites_are_exactly_the_backend_calls():
    sites = set()
    for module, _, tree in _modules():
        for qualname, node in _qualified(tree):
            for call in ast.walk(node):
                if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                        and call.func.attr == "run" and getattr(call.func.value, "id", None) == "lean_backend"):
                    sites.add((f"{module}:{qualname}", call.args[0].value))
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
    assert starters == {"ve/backends/lean.py"}


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


def test_nothing_is_migrated_yet():
    """P0-3 adds the hooks only; switching authority is stage 4's decision."""
    assert {op["authority"] for op in OPS} <= {"python", "lean-only"}
    assert assurance.enforced_operations() == frozenset()


def test_lean_only_operations_have_no_python_verdict_path():
    for op in OPS:
        if op["authority"] == "lean-only":
            assert op["python"] == [] and op["lean_call_sites"] == [], op["id"]
            assert op["id"] not in assurance.ENTRIES


# --- executable bindings: Lean and Rust ---------------------------------------

AUDITED = set(re.findall(r"^'([^']+)' depends on axioms", (ROOT / "lean/axioms.txt").read_text(), re.M))


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
            root = ROOT / "lean" / (executables[binding["executable"]] + ".lean")
            if binding["mode"]:
                assert f'"{binding["mode"]}"' in root.read_text(), (op["id"], binding)
            sources = [ROOT / path for path in binding["dispatch"]]
            assert sources and all(path.exists() for path in sources), (op["id"], binding)
            text = "".join(path.read_text() for path in sources)
            for kind in binding["kinds"]:
                assert f'"{kind}"' in text, (op["id"], kind)
        for path in (op["lean"] or {}).get("decoders", ()):
            assert path in {f["file"] for f in MANIFEST["lean_decoders"]["files"]}, (op["id"], path)


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


# --- the authority guard ------------------------------------------------------

def test_guard_blocks_every_python_entry_once_migrated():
    for op in OPS:
        for entry in op["python"]:
            fn = _resolve(entry)
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
    from ve.equivalence import compare
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
    "hang": "time.sleep(30)",
}


@pytest.mark.parametrize("fault", FAULTS)
def test_backend_faults_are_checker_unavailable(tmp_path, fault):
    fake = _fake_lean(tmp_path, FAULTS[fault])
    with pytest.raises(CheckerUnavailable) as caught:
        lean_backend.run("bundle.check", fake, CASE, runner="ve_conformance", mode="route", timeout=2)
    assert caught.value.backend == "lean" and caught.value.operation == "bundle.check"


def test_missing_backend_is_checker_unavailable(tmp_path):
    with pytest.raises(CheckerUnavailable, match="cannot start"):
        lean_backend.run("bundle.check", tmp_path / "absent", CASE, runner="ve_conformance",
                         mode="route", timeout=2)


def test_backend_rejection_is_returned_as_a_semantic_row(tmp_path):
    fake = _fake_lean(tmp_path, "print(json.dumps([{'id': c['id'], 'status': 'error', 'error': 'forged'} "
                                "for c in cases])); sys.exit(1)")
    rows = lean_backend.run("bundle.check", fake, CASE, runner="ve_conformance", mode="route", timeout=5)
    assert rows == [{"id": "bundle", "status": "error", "error": "forged"}]


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
        lean_backend.run(op_id, tmp_path / "absent", [case], runner=runner, mode=mode, timeout=1)


def _bundle():
    return json.loads((ROOT / "usecases/math-mini-paper/t7-definitions-bundle.json").read_text())


def test_bundle_separates_rejection_from_unavailability(tmp_path, monkeypatch):
    from ve import bundle
    from ve.bundle import check_bundle
    hang = _fake_lean(tmp_path, FAULTS["hang"], name="hang")
    with monkeypatch.context() as short:
        short.setattr(bundle, "LEAN_REPLAY_TIMEOUT", 1)
        with pytest.raises(CheckerUnavailable, match="no answer"):
            check_bundle(_bundle(), lean_executable=hang)
    assert check_bundle(_bundle())["lean_outcome"] == "not_requested"
    with pytest.raises(CheckerUnavailable):
        check_bundle(_bundle(), lean_executable=tmp_path / "absent")
    rejecting = _fake_lean(tmp_path, "print(json.dumps([{'id': c['id'], 'status': 'error', 'error': 'no'} "
                                     "for c in cases])); sys.exit(1)", name="rejecting")
    with pytest.raises(VEError, match="did not accept"):
        check_bundle(_bundle(), lean_executable=rejecting)
    if (LEAN_BIN / "ve_conformance").exists():
        assert check_bundle(_bundle(), lean_executable=LEAN_BIN / "ve_conformance")["lean_outcome"] == "accepted"


def test_argument_separates_lean_rejection_from_unavailability(tmp_path, monkeypatch):
    from ve import argument, check_argument, outstanding_obligations
    from ve.argument_fixtures import merged_vocabulary_example
    monkeypatch.setattr(argument, "LEAN_REPLAY_TIMEOUT", 1)
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
    assert check_argument(graph).to_dict()["lean_outcome"] == "not_requested"


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

def test_spec_table_is_generated_from_the_manifest():
    text = (ROOT / "docs/spec/assurance-manifest.md").read_text()
    begin, end = "<!-- BEGIN GENERATED: python tools/assurance_manifest.py --write -->\n", "<!-- END GENERATED -->"
    assert begin in text and end in text
    assert text.split(begin, 1)[1].split(end, 1)[0] == assurance.render_markdown()
