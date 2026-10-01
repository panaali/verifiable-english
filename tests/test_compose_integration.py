"""S0 integration evidence for composition.md fixtures L2–L7.

Lean checks these models in VE.Compose.Examples during ``lake build``. This file
checks the same source through document admission and evaluates its regenerated
slot in Python and Rust. Rust receives the formulas as untrusted input.
"""

import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path

from conformance.rights_three_way import fixtures
from tests.test_rights import rights_document_file
from ve.ast import Binary, Bottom, Implies, Not, Top, Var, formula_from_data, formula_to_data
from ve.document import check_document, load_document
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.norms import _bind
from ve.rights import correlate
from ve.rights_route import check_rights_regenerated, run_rights_case


ROOT = Path(__file__).resolve().parents[1]


def gamma():
    raw, units = fixtures()["gamma"]
    rights = correlate(deepcopy(raw), deepcopy(units))
    return raw, units, rights


def test_gamma_document_admission_and_end_to_end(tmp_path):
    """The L2–L7 source loads, admits and checks on today's rights route."""
    raw, units, rights = gamma()
    lean = run_rights_case(rights.env, units, "rights-elaborate")
    check_rights_regenerated(rights, lean)
    premise = next(row for row in lean["premises"]
                   if row["label"] == "layer:norms:arrest_permitted")
    path = rights_document_file(tmp_path, units, env=raw)
    lines = path.read_text().splitlines(keepends=True)
    meta = json.loads(lines[1])
    meta["graph"] = {"root": "leaf", "nodes": [{"name": "leaf", "ast": premise["ast"],
                                                   "label": premise["label"]}]}
    path.write_text("---\n" + json.dumps(meta) + "\n---\n" + "".join(lines[3:]))
    loaded = load_document(path)
    assert [unit["kind"] for unit in loaded["units"]] == ["right", "limitation"]
    assert [unit["status"] for unit in loaded["units"]] == ["OPEN", "OPEN"]
    checked = check_document(path)
    assert checked["admission"]["admitted"] is True
    assert checked["document_id"] == loaded["document_id"]
    assert checked["admission"]["report"]["assumptions"][0]["label"] == premise["label"]
    assert [row["label"] for row in lean["limitations"]] == [
        label for label, _ in rights.limitation_premises
    ]


def test_gamma_slot_models_python_rust_and_lean_fixture():
    """L3–L5 and L7: Rust and Python agree with the Lean build guards."""
    _, units, rights = gamma()
    lean = run_rights_case(rights.env, units, "rights-elaborate")
    check_rights_regenerated(rights, lean)
    base_data = rights.soft_document.extended_env.to_dict()
    base_data["profiles"] = ["relational-fol@0"]
    for predicate in base_data["vocabulary"]["predicates"].values():
        predicate.pop("regulated", None)
    base = Environment(base_data)
    slot = [row["ast"] for row in lean["limitations"]]
    assert slot == [formula_to_data(rights.environment, formula, _generated=True)
                    for _, formula in rights.limitation_premises]
    extra = formula_to_data(base, _bind(Not(Binary("rights__lim__1", Var(1), Var(0))),
                                        ("state", "person")))
    gated_off = [formula_to_data(base, Implies(Bottom(), formula))
                 for _, formula in rights.limitation_premises]
    gated_on = [formula_to_data(base, Implies(Top(), formula))
                for _, formula in rights.limitation_premises]
    formulas = slot + [extra] + gated_off + gated_on
    relations = {name: [] for name in base.predicates}
    row = [["texas", "ann"]]
    expected = {
        "M1": (["arbitrary", "rights__lim__1", "rights__cond__1", "rights__cond__2"],
               [True, True, False, True, True, True, True]),
        "M2": (["arbitrary", "rights__lim__1", "rights__cond__1"],
               [True, False, False, True, True, True, False]),
        "M3": (["arbitrary"], [True, True, True, True, True, True, True]),
    }
    rust_binary = Path(os.environ.get("VE_RUST_BINARY", str(ROOT / "rust/target/release/ve")))
    assert rust_binary.is_file()
    for name, (present, values) in expected.items():
        model_data = {"complete": True, "domains": {"state": ["texas"],
                      "person": ["ann", "bob"]}, "constants": {},
                      "relations": {**relations, **{predicate: row for predicate in present}}}
        model = FiniteModel.from_dict(base, model_data)
        python = [evaluate(base, formula, model, trace=False).value
                  for formula in (formula_from_data(base, ast) for ast in formulas)]
        case = {"id": name, "kind": "evaluate", "environment": base_data,
                "ast": formulas, "model": model_data}
        run = subprocess.run([str(rust_binary), "conformance"], input=json.dumps(case),
                             text=True, capture_output=True, timeout=120)
        assert run.returncode == 0, run.stdout + run.stderr
        rust = json.loads(run.stdout)[0]
        assert rust["status"] == "ok", rust
        assert python == rust["values"] == values
