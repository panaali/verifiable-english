"""One submission compared with the spec record, Python and Lean engines."""

import json
import subprocess
from copy import deepcopy
from pathlib import Path

from conformance.soft_norms import multi_fault_base
from conformance.wire_contract_golden import reports as golden_reports
from tests.test_wire_contract_corpus import CONTRACTS, LIMITS, NAMES, _registry
from tests.test_wire_contract_lean import DEFER, DEMO
from tests.test_wire_contract_soft_lean import FIXTURES, INHERITED, p7_source, with_faults
from tests.test_soft_norms_lean import elaborate, env, should
from ve.softnorms_contract import REGISTRY
from ve.wire import canonical_json
from ve.wire_contract.engine import CLEAN, Deferred, Fault, load, run

from tests.test_wire_contract_lean import LEAN


def _lean(unit, roots, kind):
    assert LEAN.exists(), "build ve_diagnose before running three-way conformance"
    cases = [{"id": str(i), "kind": kind, **root} for i, root in enumerate(roots)]
    result = subprocess.run([str(LEAN), unit, "-"], input=json.dumps(cases),
                            text=True, capture_output=True, timeout=600)
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    assert all(row["status"] == "ok" for row in rows)
    return rows


def _record(outcome):
    return "clean" if outcome is CLEAN else canonical_json(outcome.record)


def test_spec_golden_reports_match_fixtures():
    root = Path(__file__).resolve().parents[1] / "conformance/wire-contract"
    for filename, expected in golden_reports().items():
        assert json.loads((root / filename).read_text()) == expected


def test_engine_corpus_spec_python_lean():
    """E1–E32: the hand-derived full records agree in all three columns."""
    labels = list(DEMO)
    roots = [DEMO[name][0] for name in labels]
    rows = _lean("demo@0", roots, "corpus")
    for name, root, row in zip(labels, roots, rows):
        outcome = run(CONTRACTS["demo@0"], root, registry=_registry(),
                      contracts=CONTRACTS, limits=LIMITS, names=NAMES)
        expected = DEMO[name][1]
        lean = "clean" if row["outcome"] == "clean" else canonical_json(row["diagnostic"])
        assert (_record(outcome), lean) == (expected, expected), name


def test_deferred_corpus_spec_python_lean():
    """E33–E36 include the specified Python deferral and Lean continuation."""
    labels = list(DEFER)
    rows = _lean("defer@0", [DEFER[name][0] for name in labels], "corpus")
    for name, row in zip(labels, rows):
        root, expected_lean = DEFER[name]
        python = run(CONTRACTS["defer@0"], root, registry=_registry(),
                     contracts=CONTRACTS, limits=LIMITS, names=NAMES)
        lean = "clean" if row["outcome"] == "clean" else canonical_json(row["diagnostic"])
        assert lean == expected_lean, name
        if name in ("E34", "E35", "E36"):
            assert python == Deferred("d2"), name
        else:
            assert _record(python) == expected_lean, name


def test_soft_pilot_spec_python_lean():
    """P1–P17: whole records, except inherited decoder text and its args."""
    contract = load("soft-norms@0")
    named = sorted(FIXTURES)
    sources = [multi_fault_base(), (env(), []), p7_source(), with_faults("malformed-predicate"),
               *[with_faults(*FIXTURES[name][0]) for name in named]]
    roots = [{"environment": env, "norms": rules} for env, rules in sources]
    rows = _lean("soft-norms@0", roots, "soft-elaborate")
    for root, row in zip(roots[:2], rows[:2]):
        assert row["outcome"] == "clean"
        assert run(contract, root, registry=REGISTRY) is CLEAN
    p7_python = run(contract, roots[2], registry=REGISTRY)
    assert (p7_python.record["check"], rows[2]["diagnostic"]["check"]) == ("4.14b", "4.14b")
    assert canonical_json(p7_python.record) == canonical_json(rows[2]["diagnostic"])
    p17_python = run(contract, roots[3], registry=REGISTRY)
    assert (p17_python.record["check"], rows[3]["diagnostic"]["check"]) == ("2.3", "2.3")
    for key in ("contract", "revision", "check", "phase", "code", "class", "path"):
        assert p17_python.record[key] == rows[3]["diagnostic"][key]
    for name, root, row in zip(named, roots[4:], rows[4:]):
        python = run(contract, root, registry=REGISTRY)
        assert isinstance(python, Fault), name
        assert row["outcome"] == "fault", name
        expected = deepcopy(FIXTURES[name][1])
        assert canonical_json(row["diagnostic"]) == canonical_json(expected), name
        if expected["check"] in INHERITED:
            for key in ("text", "args"):
                python.record.pop(key)
                expected.pop(key)
        assert canonical_json(python.record) == canonical_json(expected), name


def test_admission_adapter_uses_active_norm_units():
    environment = env()
    rules = [should("a", "x_required", True), should("b", "x_permitted", False)]
    elaborated = elaborate(Path(__file__).resolve().parents[1] /
                           "lean/.lake/build/bin/ve_soft_norms_route", environment, rules)
    coherence = next(b for b in elaborated["background"] if b.get("label") == "soft:coherence:a,b")
    document = {"units": [{"id": f"u{i}", "span": [i * 10, i * 10 + 5],
                           "kind": "norm", "content": rule} for i, rule in enumerate(rules)],
                "graph": {"root": "leaf", "nodes": [
                    {"name": "leaf", "ast": coherence["ast"], "label": coherence["label"]}]}}
    case = {"environment": environment, "document": document}
    [engine] = _lean("soft-norms@0", [case], "admission")
    assert engine["outcome"] == "clean"
    submitted = {"id": "admission", "kind": "admission", **case}
    legacy = subprocess.run([str(Path(__file__).resolve().parents[1] /
                                 "lean/.lake/build/bin/ve_soft_norms_route"), "-"],
                            input=json.dumps([submitted]), text=True, capture_output=True, timeout=180)
    assert json.loads(legacy.stdout)[0]["status"] == "ok"
    bad = deepcopy(case)
    bad["document"]["units"][0]["content"]["norm"]["mode"] = "invalid"
    [lean_bad] = _lean("soft-norms@0", [bad], "admission")
    python_root = REGISTRY.adapters["soft_source"]({"kind": "admission", **bad})
    python_bad = run(load("soft-norms@0"), python_root, registry=REGISTRY)
    assert isinstance(python_bad, Fault)
    assert canonical_json(python_bad.record) == canonical_json(lean_bad["diagnostic"])
    assert lean_bad["diagnostic"]["check"] == "4.3"
