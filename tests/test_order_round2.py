"""The order surface and finite evaluation agree in Python, Rust and Lean.

Rust reads no source text (batch 15b): its order route takes Python's AST, so the surface
itself (parsing, source limits, strict rejections) is compared between Python and Lean."""
import copy
import json
from subprocesses import HANG_TIMEOUT
import subprocess

import pytest

from conformance.order import evaluation_cases
from test_lean_conformance import lean_executable  # noqa: F401
from test_rust_conformance import rust_executable  # noqa: F401
from ve import evaluate
from ve.ast import document_from_data, document_to_data
from ve.environment import Environment
from ve.errors import ResourceLimit, VEError
from ve.identity import meaning_id
from ve.model import FiniteModel
from ve.parser import parse
from ve.printer import print_document
from ve.wire import canonical_json


def invoke(executable, command, cases):
    result = subprocess.run([str(executable), command], input=json.dumps(cases),
                            capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert result.returncode in (0, 1), result.stderr
    return json.loads(result.stdout)


def test_order_surface_and_evaluation_three_way(rust_executable, lean_executable):
    generated = evaluation_cases(100)
    cases, surface = [], []
    for case, _ in generated:
        env = Environment(case["environment"])
        document = document_from_data(env, case["ast"])
        source = print_document(env, document)
        cases.append(case)
        surface.append({"id": case["id"], "kind": "surface", "environment": case["environment"],
                        "source": source})
    rust = invoke(rust_executable, "conformance", cases)
    lean_values = invoke(lean_executable, "order", [c for c, _ in generated])
    lean_surface = invoke(lean_executable, "order", surface)
    for (case, expected), r, lv, ls in zip(generated, rust, lean_values, lean_surface, strict=True):
        env = Environment(case["environment"])
        doc = document_from_data(env, case["ast"])
        model = FiniteModel.from_dict(env, case["model"])
        assert r["status"] == lv["status"] == ls["status"] == "ok", case["id"]
        assert r["values"] == lv["values"] == expected, case["id"]
        assert ls["ast"] == r["ast"] == case["ast"], case["id"]
        assert r["canonical"] == print_document(env, doc)
        assert r["environment_id"] == env.environment_id
        assert r["meaning_id"] == meaning_id(env, doc)
        assert r["model_id"] == model.model_id
        for key, data in (("canonical_environment", env.to_dict()),
                          ("canonical_ast", case["ast"]), ("canonical_model", model.to_dict())):
            assert r[key].encode() == canonical_json(data)


def test_order_new_routes_reject_malformed_input(rust_executable, lean_executable):
    base, _ = evaluation_cases(1)[0]
    bad = []
    for formula in (["lt", ["num", "01"], ["num", "2"]],
                    ["lt", ["const", "a"], ["num", "2"]],
                    ["forall", "$int", ["top"]]):
        case = copy.deepcopy(base)
        case["ast"] = [formula]
        bad.append(case)
    rows = invoke(rust_executable, "conformance", bad)
    assert all(r["status"] == "error" for r in rows)
    surface = [{"id": str(i), "kind": "surface", "environment": base["environment"],
                "source": source} for i, source in enumerate((
                    "-0 < 2.\n", "for every $int x0, (true).\n", "@n < [01 * @m].\n"))]
    rows = invoke(lean_executable, "order", surface)
    assert all(r["status"] == "error" for r in rows)
    proof = copy.deepcopy(base)
    proof["kind"] = "certificate"
    assert invoke(rust_executable, "conformance", [proof])[0]["status"] == "error"


def without_source(case):
    """The case Rust is sent: Python's AST, never the source text."""
    return {key: value for key, value in case.items() if key != "source"}


def _surface_case(env, source, index):
    return {"id": str(index), "kind": "surface", "environment": env, "source": source}


def test_order_large_integers_and_coefficient_families_three_way(rust_executable, lean_executable):
    base, _ = evaluation_cases(1)[0]
    env = Environment(base["environment"])
    numerals = ("0", "1", "-2", "-9", "-20", "-99", "-100",
                "9" * 40, "-" + "9" * 39)
    sources = [f"[{k} * @n] < {n}.\n" for k in numerals for n in ("0", "-99")]
    rust_cases = []
    for index, source in enumerate(sources):
        doc = parse(env, source)
        assert print_document(env, doc) == source
        rust_cases.append({"id": str(index), "environment": base["environment"],
                           "source": source, "ast": document_to_data(env, doc)})
    rust = invoke(rust_executable, "conformance", [without_source(case) for case in rust_cases])
    lean = invoke(lean_executable, "order", [
        _surface_case(base["environment"], source, i) for i, source in enumerate(sources)])
    for case, r, l in zip(rust_cases, rust, lean, strict=True):
        assert r["status"] == l["status"] == "ok", case["source"]
        assert r["ast"] == l["ast"] == case["ast"]
        assert r["canonical"] == case["source"]
    model = FiniteModel.from_dict(env, base["model"])
    evaluations = [{**case, "kind": "evaluate", "model": base["model"]}
                   for case in rust_cases]
    rust_values = invoke(rust_executable, "conformance", [without_source(case) for case in evaluations])
    lean_values = invoke(lean_executable, "order", evaluations)
    for case, r, l in zip(evaluations, rust_values, lean_values, strict=True):
        doc = document_from_data(env, case["ast"])
        expected = [evaluate(env, f, model, trace=False).value for f in doc.formulas]
        assert r["status"] == l["status"] == "ok", case["source"]
        assert r["values"] == l["values"] == expected


def test_order_source_limit_boundaries_two_way(lean_executable):
    base, _ = evaluation_cases(1)[0]
    env = Environment(base["environment"])
    term64 = "@n"
    for _ in range(63):
        term64 = f"[{term64} + 1]"
    formula64 = "not (" * 63 + "true" + ")" * 63
    name64 = "x" + "a" * 63
    numeric_name64 = "x" + "9" * 63
    sources = [
        (f"{term64} < 0.\n", True),
        (f"{formula64}.\n", True),
        (f"for every item {name64}, (true).\n", True),
        (f"for every item {numeric_name64}, (true).\n", True),
        (f"[{term64} + 1] < 0.\n", False),
        (f"not ({formula64}).\n", False),
        (f"for every item {name64}a, (true).\n", False),
        (f"for every item {numeric_name64}9, (true).\n", False),
        (f"{'9' * 41} < 0.\n", False),
        # past Python's lowest and default digit limits (english-lean looprecheck1, finding 1)
        (f"{'9' * 641} < 0.\n", False),
        (f"-{'9' * 4301} < 0.\n", False),
        (f"[{'9' * 4301} * @n] < 0.\n", False),
    ]
    lean = invoke(lean_executable, "order", [
        _surface_case(base["environment"], source, i)
        for i, (source, _) in enumerate(sources)])
    for (source, accepted), l in zip(sources, lean, strict=True):
        if accepted:
            doc = parse(env, source)
            assert l["status"] == "ok", source
            assert l["ast"] == document_to_data(env, doc)
        else:
            with pytest.raises(ResourceLimit):
                parse(env, source)
            assert l["status"] == "error", source
            assert "ResourceLimit" in l["error"], source


def test_order_strict_source_rejections_two_way(rust_executable, lean_executable):
    base, _ = evaluation_cases(1)[0]
    env = Environment(base["environment"])
    sources = (
        "-0 < 2.\n", "01 < 2.\n", "for every $int x0, (true).\n",
        "z < 2.\n", "for every item x0, (for every item x0, (true)).\n",
        "true.\ntrailing", "true.\r\n", "@n < [01 * @m].\n",
    )
    for source in sources:
        with pytest.raises(VEError):
            parse(env, source)
    lean = invoke(lean_executable, "order", [
        _surface_case(base["environment"], source, i) for i, source in enumerate(sources)])
    assert all(r["status"] == "error" for r in lean)
    # Rust's order route reads no source text: a case carrying one is refused, with or without its AST.
    source_only = {"id": "s", "environment": base["environment"], "source": "true.\n"}
    for case in (source_only, {**base, "source": print_document(env, document_from_data(env, base["ast"]))}):
        row = invoke(rust_executable, "conformance", [case])[0]
        assert row["status"] == "error", row
        assert row["error"] == {"code": "InvalidInput", "message": "Rust reads no source text; send the AST"}
