"""One accepted case per declared Lean binding of the assurance manifest.

`probes()` maps each (operation, executable, mode, kind) of
ve/assurance-manifest.json to a case that exercises that operation and that
the Lean executable accepts in that mode. tests/test_assurance_manifest.py runs
every probe through the real runner, so a binding whose mode or kind no longer
routes the operation's cases (or a manifest edit that changes a binding without
a matching probe) fails. Kind `None` is a mode whose cases carry no kind.
"""
from __future__ import annotations

from functools import cache
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _fixture(name):
    return json.loads((ROOT / f"conformance/{name}.json").read_text())


def _soft_wire_root():
    return json.loads((ROOT / "ve/wire_contract/examples/soft-norms@0/empty.json").read_text())


def _norm_wire_case(unit, kind):
    root = json.loads((ROOT / f"ve/wire_contract/examples/{unit}/empty.json").read_text())
    if kind == "admission":
        return {"id": f"wire-{unit}-admission", "kind": kind,
                "environment": root["environment"],
                "document": {"units": [], "graph": {"root": "leaf", "nodes": []}}}
    return {"id": f"wire-{unit}-{kind}", "kind": kind, **root}


def _python(env_json):
    from ve.environment import Environment
    return Environment(env_json)


def _certificate_case(env_json, id_, kind=None):
    """env ⊢ ⊤ with the certificate Python's prover finds and replays."""
    from ve.ast import Top
    from ve.entailment import prove_entailment
    proof = prove_entailment(_python(env_json), (), Top())
    assert proof.status == "Found"
    return {"id": id_, **({"kind": kind} if kind else {}), "environment": env_json,
            "premises": [], "conclusion": ["top"], "certificate": proof.certificate}


def _model(env_json):
    from ve.ast import Bottom
    from ve.search import find_countermodel
    found = find_countermodel(_python(env_json), (), Bottom(), max_domain_size=2)
    assert found.status == "Found"
    return found.model.to_dict()


def _countermodel_case(env_json, id_, kind="countermodel"):
    """A model refuting ⊢ ⊥."""
    return {"id": id_, "kind": kind, "environment": env_json, "premises": [], "conclusion": ["bottom"],
            "model": _model(env_json)}


def _evaluate_case(env_json, id_, kind=None, source=None):
    return {"id": id_, **({"kind": kind} if kind else {}), "environment": env_json, "model": _model(env_json),
            "ast": [["top"]], **({"source": source} if source is not None else {})}


def _legacy():
    return _fixture("evaluation")[0]["environment"]


def _route():
    from conformance.p0 import VOCAB, envelope
    return envelope(VOCAB)


def _order():
    from conformance.order import environment
    return environment(0).to_dict()


def _route_fixture(name, kind):
    from conformance.p0 import lean_case
    for case in _fixture(name):
        if case["kind"] == kind and case["expected"].get("status") == "ok":
            return {k: v for k, v in lean_case(case).items() if k != "expected"}
    raise LookupError(f"no accepted {kind} case in conformance/{name}.json")


def _norms():
    from tests.test_norms_three_way import environment, permission, rule
    from ve.norms import NormDocument
    return NormDocument(environment({"permitted": permission()}), [rule("allow", "permitted", True)])


def _norms_case(kind, **fields):
    doc = _norms()
    return {"id": kind, "kind": kind, "environment": doc.env.to_dict(),
            "norms": [r.to_dict() for r in doc.rules], **fields}


def _norms_certificate():
    from ve.ast import Top, formula_to_data
    from ve.norms import prove_norm_entailment
    doc = _norms()
    conclusion = doc.elaborate("permitted")
    proof = prove_norm_entailment(doc, (Top(),), conclusion)
    assert proof.status == "Found"
    return _norms_case("norms-certificate", premises=[["top"]],
                       conclusion=formula_to_data(doc.env, conclusion), certificate=proof.certificate)


def _norms_conflict():
    from ve.ast import Not
    from ve.entailment import prove_entailment
    from ve.norms import _bind
    doc = _norms()
    packages = {}
    for target, sorts, formula in doc.conflict_targets():
        proof = prove_entailment(doc.base_environment(), (), _bind(Not(formula), sorts))
        assert proof.status == "Found"
        packages[target] = {"environment_id": doc.env.environment_id, "document_hash": doc.document_hash,
                            "target": target, "certificate": proof.certificate}
    return _norms_case("norms-conflict", packages=packages)


def _norms_admission():
    from tests.test_norm_admission import source
    env, document = source()
    return {"id": "admission", "kind": "admission", "environment": env.to_dict(), "document": document}


def _norm_defaults_admission():
    from conformance.norm_defaults import sources
    from conformance.norm_defaults_three_way import admission_document
    document = next(d for name, d, _ in sources() if name == "u5a")
    return {"id": "admission", "kind": "admission", "environment": document.env.to_dict(),
            "document": admission_document(document)}


def _quantity_admission():
    from tests.test_w6a_documents import base_document, doc_env
    raw = doc_env()
    return {"id": "admission", "kind": "document", "environment": raw,
            "document": base_document(_python(raw))}


def _bundle():
    data = json.loads((ROOT / "usecases/math-mini-paper/t7-definitions-bundle.json").read_text())
    return {"id": "bundle", "kind": "bundle", "environment": data["environment"], "lemmas": data["lemmas"],
            **({"document": data["document"]} if "document" in data else {})}


def _surface():
    from conformance.order import evaluation_cases
    from ve.ast import document_from_data
    from ve.printer import print_document
    case, _ = evaluation_cases(1)[0]
    env = _python(case["environment"])
    return {"id": "surface", "kind": "surface", "environment": case["environment"],
            "source": print_document(env, document_from_data(env, case["ast"]))}


C, S = "ve_conformance", "ve_service"
BUILDERS = {
    ("wire.diagnose", S, "diagnose", "soft-elaborate"):
        lambda: {"id": "wire-soft", "kind": "soft-elaborate", "unit": "soft-norms@0",
                 "environment": _soft_wire_root()["environment"], "norms": []},
    ("wire.diagnose", S, "diagnose", "admission"):
        lambda: {"id": "wire-admission", "kind": "admission", "unit": "soft-norms@0",
                 "environment": _soft_wire_root()["environment"],
                 "document": {"units": [], "graph": {"root": "leaf", "nodes": []}}},
    # The norm units' kinds through the same `diagnose` binding (its `admission` probe is the pilot's).
    **{("wire.diagnose", S, "diagnose", kind): (lambda unit=unit, kind=kind: {**_norm_wire_case(unit, kind), "unit": unit})
       for unit, prefix in (("norms@0", "norms"), ("norm-defaults@0", "norm-defaults"))
       for kind in (f"{prefix}-elaborate", f"{prefix}-conflict", f"{prefix}-certificate")},
    ("parse", C, "", None): lambda: _evaluate_case(_legacy(), "parse", source="true.\n"),
    ("parse", C, "order", "surface"): _surface,
    ("evaluate", C, "", None): lambda: _evaluate_case(_legacy(), "evaluate"),
    ("evaluate", C, "route", "evaluate"): lambda: _evaluate_case(_route(), "evaluate", "evaluate"),
    ("evaluate", C, "order", "evaluate"): lambda: _evaluate_case(_order(), "evaluate", "evaluate"),
    ("countermodel.check", C, "", "countermodel"): lambda: _countermodel_case(_legacy(), "countermodel"),
    ("countermodel.check", C, "route", "countermodel"): lambda: _countermodel_case(_route(), "countermodel"),
    ("countermodel.check", C, "order", "countermodel"): lambda: _countermodel_case(_order(), "countermodel"),
    ("certificate.check", C, "check-certificate", None): lambda: _certificate_case(_legacy(), "certificate"),
    ("certificate.check", C, "route", "certificate"):
        lambda: _certificate_case(_route(), "certificate", "certificate"),
    ("certificate.check", C, "order", "certificate"):
        lambda: _certificate_case(_order(), "certificate", "certificate"),
    ("definitions.elaborate", C, "route", "background"): lambda: _route_fixture("elaborated-document", "background"),
    ("definitions.elaborate", C, "route", "dependency-order"):
        lambda: _route_fixture("dependency-order", "dependency-order"),
    ("norms.elaborate", S, "norms", "norms-elaborate"): lambda: _norms_case("norms-elaborate"),
    ("norms.conflict", S, "norms", "norms-conflict"): _norms_conflict,
    ("norms.certificate", S, "norms", "norms-certificate"): _norms_certificate,
    ("admission", C, "route", "admission"): lambda: _route_fixture("admission", "admission"),
    ("admission", S, "norms", "admission"): _norms_admission,
    ("admission", S, "norm-defaults", "admission"): _norm_defaults_admission,
    ("admission", S, "quantity", "document"): _quantity_admission,
    ("label", C, "route", "label"): lambda: _route_fixture("labels", "label"),
    ("graph.compose", C, "route", "certificate"): lambda: _certificate_case(_route(), "edge", "certificate"),
    ("graph.compose", C, "check-certificate", None): lambda: _certificate_case(_legacy(), "edge"),
    ("bundle.check", C, "route", "bundle"): _bundle,
}


@cache
def probes() -> dict:
    return {key: build() for key, build in BUILDERS.items()}
