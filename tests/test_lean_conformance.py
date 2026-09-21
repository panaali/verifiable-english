"""Portable JSON differential tests. No files under ve/ are modified by Lean."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from ve import Environment, FiniteModel, evaluate, parse, print_document
from ve.ast import document_from_data
from ve.errors import VEError
from ve.search import check_countermodel

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "conformance/evaluation.json").read_text())
COUNTERMODELS = json.loads((ROOT / "conformance/countermodels.json").read_text())


@pytest.fixture(scope="session")
def lean_executable():
    lake = shutil.which("lake")
    if lake is None:
        pytest.skip("lake is not available")
    if not os.environ.get("VE_LEAN_PREBUILT"):
        build = subprocess.run([lake, "build"], cwd=ROOT / "lean", capture_output=True, text=True, timeout=180)
        assert build.returncode == 0, build.stdout + build.stderr
    assert (ROOT / "lean/.lake/build/bin/ve_conformance").exists()
    return ROOT / "lean/.lake/build/bin/ve_conformance"


def invoke(executable, cases, expected_code=0):
    result = subprocess.run([str(executable)], input=json.dumps(cases), capture_output=True, text=True, timeout=60)
    assert result.returncode == expected_code, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_shared_fixture_python_golden_values():
    for case in CASES:
        env = Environment.from_dict(case["environment"])
        model = FiniteModel.from_dict(env, case["model"])
        doc = document_from_data(env, case["ast"])
        assert parse(env, case["source"]) == doc, case["id"]
        assert print_document(env, doc) == case["source"], case["id"]
        assert [evaluate(env, f, model).value for f in doc.formulas] == case["expected"], case["id"]


def test_lean_agrees_on_every_shared_case(lean_executable):
    results = invoke(lean_executable, CASES)
    assert len(results) == len(CASES)
    for case, result in zip(CASES, results, strict=True):
        env = Environment.from_dict(case["environment"])
        doc = document_from_data(env, case["ast"])
        model = FiniteModel.from_dict(env, case["model"])
        expected = [evaluate(env, f, model).value for f in doc.formulas]
        assert result == {"id": case["id"], "status": "ok", "values": expected, "value": all(expected), "canonical": case["source"]}


def countermodel_python(case):
    env = Environment.from_dict(case["environment"])
    model = FiniteModel.from_dict(env, case["model"])
    doc = document_from_data(env, case["premises"] + [case["conclusion"]])
    checked = check_countermodel(env, doc.formulas[:-1], doc.formulas[-1], model)
    assert checked.status in ("Valid", "NotCountermodel"), case["id"]
    return checked.valid


def test_countermodel_python_golden_values():
    for case in COUNTERMODELS:
        assert countermodel_python(case) == case["expected_refutes"], case["id"]


def test_lean_countermodels_agree_on_every_shared_case(lean_executable):
    results = invoke(lean_executable, COUNTERMODELS)
    assert len(results) == len(COUNTERMODELS)
    for case, result in zip(COUNTERMODELS, results, strict=True):
        assert result == {"id": case["id"], "status": "ok", "refutes": countermodel_python(case)}, case["id"]


def test_corpus_coverage_and_stable_evaluation_envelope():
    assert len(CASES) >= 600
    assert len({c["id"] for c in CASES}) == len(CASES)
    assert all(set(c) == {"id", "environment", "model", "ast", "source", "expected"} for c in CASES)
    extended = [c for c in CASES if c["id"].startswith("extended_")]
    assert {(len(c["model"]["domains"]["item"]), len(c["model"]["domains"]["person"]))
            for c in extended} == {(i, p) for i in range(5) for p in range(5)}
    for case in extended:
        node = case["ast"][3]
        kinds = []
        for _ in range(6):
            assert node[0] in ("forall", "exists")
            kinds.append(node[0])
            node = node[2]
        assert all(a != b for a, b in zip(kinds, kinds[1:]))
    assert {c["expected_refutes"] for c in COUNTERMODELS} == {False, True}
    aliases = [c for c in extended if c["model"]["domains"]["item"]]
    assert {c["expected"][-2] for c in aliases} == {False, True}


@pytest.mark.parametrize("field, value", [
    ("premises", [["bottom"], ["eq", ["const", "nope"], ["const", "nope"]]]),
    ("conclusion", ["not", ["eq", ["const", "nope"], ["const", "nope"]]]),
    ("conclusion", ["eq", ["var", 0], ["var", 0]]),
    ("conclusion", ["forall", "person", ["exists", "service", ["eq", ["var", 0], ["var", 1]]]]),
    ("premises", [["unary", "deployed", ["const", "nope"]]]),
    ("conclusion", ["unary", "owns", ["const", "nope"]]),
])
def test_countermodel_rejects_ill_typed_formulas_before_evaluation(lean_executable, field, value):
    case = copy.deepcopy(COUNTERMODELS[-1])
    case[field] = value
    with pytest.raises(VEError):
        countermodel_python(case)
    assert invoke(lean_executable, case, 1)[0]["status"] == "error"


def test_countermodel_rejects_inadmissible_model(lean_executable):
    case = copy.deepcopy(next(c for c in COUNTERMODELS if c["model"]["constants"]))
    name = next(iter(case["model"]["constants"]))
    case["model"]["constants"][name] = "missing"
    with pytest.raises(VEError):
        countermodel_python(case)
    assert invoke(lean_executable, case, 1)[0]["status"] == "error"


def test_countermodel_expected_is_ignored_and_kind_is_checked(lean_executable):
    case = copy.deepcopy(COUNTERMODELS[-1])
    expected = countermodel_python(case)
    case["expected_refutes"] = not expected
    assert invoke(lean_executable, case)[0]["refutes"] == expected
    case["kind"] = "unknown"
    assert invoke(lean_executable, case, 1)[0]["error"] == "unknown case kind"


def malformed_cases():
    base = CASES[0]
    mutations = [
        lambda c: c["environment"].update(language="unknown"),
        lambda c: c["environment"].update(extra="unknown"),
        lambda c: c["environment"]["vocabulary"]["sorts"]["person"].update(description=""),
        lambda c: c["environment"]["vocabulary"]["predicates"]["owns"].update(arguments=["unknown", "service"]),
        lambda c: c["environment"]["vocabulary"]["predicates"]["owns"].update(arguments=[]),
        lambda c: c["model"].update(complete=False),
        lambda c: c["model"].update(complete=1),
        lambda c: c["model"].update(extra=[]),
        lambda c: c["model"]["relations"].pop("owns"),
        lambda c: c["model"]["domains"].pop("person"),
        lambda c: c["model"]["domains"]["person"].append("alice"),
        lambda c: c["model"]["domains"]["person"].append("Bad"),
        lambda c: c["model"]["relations"]["owns"].append(["alice", "api"]),
        lambda c: c["model"]["relations"].update(owns=[["missing", "api"]]),
        lambda c: c["model"]["relations"].update(owns=[["api", "alice"]]),
        lambda c: c["model"]["relations"].update(owns=[["alice"]]),
        lambda c: c.update(ast=[]),
        lambda c: c.update(ast=[["top", "extra"]]),
        lambda c: c.update(ast=[["unknown"]]),
        lambda c: c.update(ast=[["eq", ["var", 0], ["var", 0]]]),
        lambda c: c.update(ast=[["forall", "missing", ["top"]]]),
        lambda c: c.update(ast=[["forall", "person", ["unary", "deployed", ["var", 0]]]]),
        lambda c: c.update(ast=[["forall", "person", ["unary", "owns", ["var", 0]]]]),
        lambda c: c.update(ast=[["forall", "person", ["eq", ["var", True], ["var", 0]]]]),
        lambda c: c.update(ast=[["forall", "person", ["eq", ["var", -1], ["var", 0]]]]),
        lambda c: c.update(ast=[["forall", "person", ["exists", "service", ["eq", ["var", 0], ["var", 1]]]]]),
    ]
    cases = []
    for i, mutate in enumerate(mutations):
        case = copy.deepcopy(base)
        mutate(case)
        case["id"] = f"invalid_{i}"
        cases.append(case)
    return cases


def test_both_decoders_reject_malformed_cases(lean_executable):
    for case in malformed_cases():
        with pytest.raises(VEError):
            env = Environment.from_dict(case["environment"])
            model = FiniteModel.from_dict(env, case["model"])
            doc = document_from_data(env, case["ast"])
            evaluate(env, doc, model)
        result = subprocess.run([str(lean_executable)], input=json.dumps(case), capture_output=True, text=True, timeout=10)
        assert result.returncode != 0, case["id"]


@pytest.mark.parametrize("raw", [
    '{"a":1,"a":2}', '{"a":1,"\\u0061":2}', '{"a":{"b":1,"b":2}}',
    '{"a":"\\ud800"}', '{"a":"\\udfff"}', '{"a":"\\ud800x"}',
    '{"a":null}', '{"a":1.0}', '{"a":1e0}', '{"a":-1}', '{"a":9007199254740992}',
])
def test_lean_rejects_invalid_raw_json(lean_executable, raw):
    result = subprocess.run([str(lean_executable)], input=raw, capture_output=True, text=True, timeout=10)
    assert result.returncode == 2, result.stdout + result.stderr


def test_lean_source_resolution_and_canonical_binder_order(lean_executable):
    cases = []
    for original in CASES[:3] + CASES[-12:]:
        case = copy.deepcopy(original)
        case["source"] = case["source"].replace("x0", "trueish").replace("x1", "falsehood")
        case["source"] = case["source"].replace("x2", "notable").replace("x3", "therefore")
        cases.append(case)
    sibling = copy.deepcopy(CASES[0])
    sibling["id"] = "sibling_scopes"
    sibling["source"] = "(for every service s, (s is deployed)) and (for every service s, (s is reviewed)).\n"
    env = Environment.from_dict(sibling["environment"])
    doc = parse(env, sibling["source"])
    from ve.ast import document_to_data
    sibling["ast"] = document_to_data(env, doc)
    cases.append(sibling)
    results = invoke(lean_executable, cases)
    for case, result in zip(cases, results, strict=True):
        env = Environment.from_dict(case["environment"])
        doc = parse(env, case["source"])
        assert result["canonical"] == print_document(env, doc), case["id"]


@pytest.mark.parametrize("source", [
    "true.", "true.\r\n", "true.\n\n", " true.\n", "true .\n", "(true).\n",
    "true and false.\n", "True.\n", "true.\n#comment\n", "true.\t\n",
    "for every service s, (for every service s, (true)).\n",
    "for every service person, (true).\n", "for every service not, (true).\n",
    "for every service s, (s is deployed).\nthere exists service t, (s is reviewed).\n",
])
def test_lean_rejects_non_strict_or_unbound_source(lean_executable, source):
    case = copy.deepcopy(CASES[0])
    case["source"] = source
    env = Environment.from_dict(case["environment"])
    with pytest.raises(VEError):
        parse(env, source)
    assert invoke(lean_executable, case, 1)[0]["status"] == "error"


def test_lean_rejects_individually_valid_source_ast_substitution(lean_executable):
    case = copy.deepcopy(CASES[0])
    case["source"] = "true.\n"
    assert invoke(lean_executable, case, 1)[0]["error"] == "source/AST mismatch"


def test_lean_json_accepts_unicode_descriptions(lean_executable):
    case = copy.deepcopy(CASES[0])
    case["environment"]["vocabulary"]["sorts"]["person"]["description"] = "Person \U0001f600 \u20ac"
    for escaped in (True, False):
        result = subprocess.run([str(lean_executable)], input=json.dumps(case, ensure_ascii=escaped),
                                capture_output=True, text=True, timeout=10)
        assert result.returncode == 0, result.stderr + result.stdout


def test_lean_and_python_accept_identity_bound_display_metadata(lean_executable):
    case = copy.deepcopy(CASES[0])
    vocab = case["environment"]["vocabulary"]
    vocab["sorts"]["person"]["verbalisation"] = {"singular": "person", "plural": "people"}
    vocab["predicates"]["owns"].update(verbalisation="{0} owns {1}",
                                        negative_verbalisation="{0} does not own {1}")
    env = Environment(case["environment"])
    doc = document_from_data(env, case["ast"])
    model = FiniteModel.from_dict(env, case["model"])
    assert invoke(lean_executable, case)[0]["values"] == [evaluate(env, f, model).value for f in doc.formulas]
    # Rejected display templates remain inert data in both semantic decoders.
    vocab["predicates"]["owns"]["negative_verbalisation"] = "{0} owns {1}"
    Environment(case["environment"])
    assert invoke(lean_executable, case)[0]["values"] == case["expected"]


@pytest.mark.parametrize("field,bad", [
    ("verbalisation", []), ("verbalisation", ""), ("verbalisation", "x" * 257),
    ("negative_verbalisation", {}), ("negative_verbalisation", ""),
    ("negative_verbalisation", "x" * 257), ("unknown_verbalisation", "word"),
])
def test_lean_and_python_reject_malformed_display_metadata(lean_executable, field, bad):
    case = copy.deepcopy(CASES[0])
    case["environment"]["vocabulary"]["predicates"]["owns"][field] = bad
    with pytest.raises(VEError):
        Environment(case["environment"])
    assert invoke(lean_executable, case, 1)[0]["status"] == "error"


def test_lean_transitive_axiom_allowlist(lean_executable):
    import sys
    result = subprocess.run([sys.executable, str(ROOT / "lean/audit.py")], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS:" in result.stdout


@pytest.fixture(scope="module")
def source_audit():
    import importlib.util
    spec = importlib.util.spec_from_file_location("lean_source_audit", ROOT / "lean/audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("keyword", [
    "partial", "opaque", "extern", "implemented_by", "unsafe", "native_decide", "axiom", "sorry", "sorryAx", "admit",
])
@pytest.mark.parametrize("path", ["Main.lean", "VE/Nested/Policy.lean", "Extra.lean"])
def test_source_audit_rejects_escape_hatches_everywhere(source_audit, tmp_path, keyword, path):
    source = tmp_path / path
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(f"{keyword}\n")
    with pytest.raises(AssertionError, match=rf"{path}:1: forbidden {keyword}"):
        source_audit.scan_sources(tmp_path)


def test_source_audit_includes_root_and_dotted_theorems(source_audit, tmp_path):
    (tmp_path / "Main.lean").write_text(
        '/- comment /- nested -/ comment -/\n-- comment\ndef label := "ordinary"\n'
        'theorem root_result : True := by trivial\nnamespace Demo\n'
        '@[simp] theorem Nested.result : True := by trivial\nend Demo\n')
    actual, sources = source_audit.scan_sources(tmp_path)
    assert actual == {"root_result", "Demo.Nested.result"}
    assert [p.name for p in sources] == ["Main.lean"]


@pytest.mark.parametrize("text", [
    'def message := s!"{(by sorry : Nat)}"',
    'macro "bad" : term => `(by native_decide)',
    '/- opaque -/',
    'def message := "unsafe"',
])
def test_source_audit_scans_literal_tokens_in_quotations(source_audit, tmp_path, text):
    (tmp_path / "Main.lean").write_text(text)
    with pytest.raises(AssertionError, match="forbidden"):
        source_audit.scan_sources(tmp_path)


def test_oracle_witnesses_replay_in_lean(lean_executable):
    from ve import Document, Eq, Exists, Forall, Implies, Top, Unary, Var
    from ve.ast import document_to_data
    from ve.equivalence import compare, validate_reference
    from test_equivalence import ENV

    p, q = Unary('p', Var(0)), Unary('q', Var(0))
    pairs = (
        (Forall('item', Implies(p, q)), Top()),
        (Forall('item', p), Exists('item', p)),
        (Exists('item', p), Exists('item', q)),
        (Exists('item', Eq(Var(0), Var(0))), Top()),
    )
    cases = []
    for a, b in pairs:
        result = compare(ENV, a, b)
        for direction, model in result.models.items():
            doc = Document((a, b))
            cases.append({'id': str(len(cases)), 'environment': ENV.to_dict(),
                          'ast': document_to_data(ENV, doc), 'source': print_document(ENV, doc),
                          'model': model.to_dict(),
                          'expected': [direction == 'a_not_implies_b', direction == 'b_not_implies_a']})
    reference = validate_reference(ENV, Forall('item', Implies(p, q)))
    for model, value in ((reference.satisfying_model, True), (reference.falsifying_model, False)):
        doc = Document((Forall('item', Implies(p, q)),))
        cases.append({'id': str(len(cases)), 'environment': ENV.to_dict(),
                      'ast': document_to_data(ENV, doc), 'source': print_document(ENV, doc),
                      'model': model.to_dict(), 'expected': [value]})
    results = invoke(lean_executable, cases)
    for case, result in zip(cases, results, strict=True):
        assert result['status'] == 'ok' and result['values'] == case['expected']
