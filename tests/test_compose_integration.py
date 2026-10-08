"""S0 integration evidence for composition.md 10.2 on a real document: L2's slot, L3–L5 and L7.

The source is Python's `gamma` (`conformance/rights_three_way.py`: predicate
`arbitrary`, elements `texas`/`ann`). What this file shows:

* Lean's rights route regenerates `Lim_D` for that document and its bytes equal
  Python's; the document loads, admits and checks on today's rights route.
* The slot, L5's extra premise and the slot gated by false and by true (L7) are
  evaluated on three models by Python, by Rust (the formulas as untrusted input)
  and by Lean's evaluator (service mode `route`): the same formulas on the same
  models, with hand-derived expected values that all three must meet.

What it does not show. The gated formulas are built here in Python, as Lean's
`gate χ P` is defined (`P.map (χ → ·)`); Lean's `gate` and `slotCheck` are not run
here. Lean's build guards in `VE.Compose.Examples` check L1–L9 on a separately
written `gamma` (`lean/VE/Rights/Examples.lean`: `arbitrary_arrest`, `journalist`,
`Texas`/`Ann`) of the same shape, not on this file's document; L6 is checked there
only.
"""

import json
import os
from copy import deepcopy
from pathlib import Path

from conformance.rights_three_way import fixtures
from conformance.three_way import run_rust_evaluations
from tests.test_rights import rights_document_file
from ve.ast import Binary, Bottom, Implies, Not, Top, Var, formula_from_data, formula_to_data
from ve.backends import lean_runner, relay
from ve.document import check_document, load_document
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.norms import _bind
from ve.rights import correlate
from ve.rights_route import run_rights_case


ROOT = Path(__file__).resolve().parents[1]


def gamma():
    raw, units = fixtures()["gamma"]
    rights = correlate(deepcopy(raw), deepcopy(units))
    return raw, units, rights


def test_gamma_document_admission_and_end_to_end(tmp_path):
    """The L2–L7 source loads, admits and checks on today's rights route."""
    raw, units, rights = gamma()
    lean = run_rights_case(rights.env, units, "rights-elaborate")
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


def test_gamma_slot_models_python_rust_and_lean_agree():
    """L3–L5 and L7 on this document: Python, Rust and Lean evaluate the same formulas on the same models."""
    _, units, rights = gamma()
    lean = run_rights_case(rights.env, units, "rights-elaborate")
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
        [rust] = run_rust_evaluations(rust_binary, [case])
        assert rust["status"] == "ok", rust
        mode, lean_case = lean_runner.evaluation_case(base, name, formulas, model_data)
        [lean_row] = relay.decide(mode, [lean_case])
        assert python == rust["values"] == lean_row["values"] == values
