"""The order surface and finite evaluation agree in Python, Rust and Lean."""
import copy
import json
import subprocess

from conformance.order import evaluation_cases
from test_lean_conformance import lean_executable  # noqa: F401
from test_rust_conformance import rust_executable  # noqa: F401
from ve.ast import document_from_data
from ve.environment import Environment
from ve.identity import meaning_id
from ve.model import FiniteModel
from ve.printer import print_document
from ve.wire import canonical_json


def invoke(executable, command, cases):
    result = subprocess.run([str(executable), command], input=json.dumps(cases),
                            capture_output=True, text=True, timeout=120)
    assert result.returncode in (0, 1), result.stderr
    return json.loads(result.stdout)


def test_order_surface_and_evaluation_three_way(rust_executable, lean_executable):
    generated = evaluation_cases(100)
    cases, surface = [], []
    for case, _ in generated:
        env = Environment(case["environment"])
        document = document_from_data(env, case["ast"])
        source = print_document(env, document)
        cases.append({**case, "source": source})
        surface.append({"id": case["id"], "kind": "surface", "environment": case["environment"],
                        "source": source})
    rust = invoke(rust_executable, "conformance", cases)
    rust_source = invoke(rust_executable, "conformance", [
        {key: value for key, value in case.items() if key != "ast"} for case in cases])
    lean_values = invoke(lean_executable, "order", [c for c, _ in generated])
    lean_surface = invoke(lean_executable, "order", surface)
    for (case, expected), r, rs, lv, ls in zip(generated, rust, rust_source, lean_values, lean_surface, strict=True):
        env = Environment(case["environment"])
        doc = document_from_data(env, case["ast"])
        model = FiniteModel.from_dict(env, case["model"])
        assert r["status"] == lv["status"] == ls["status"] == "ok", case["id"]
        assert r["values"] == lv["values"] == expected, case["id"]
        assert ls["ast"] == r["ast"] == case["ast"], case["id"]
        assert rs == r, case["id"]
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
