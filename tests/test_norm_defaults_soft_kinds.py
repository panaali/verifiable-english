"""RD-9 SC-6: the soft branch's `admission` and `norm-defaults-certificate` under norm-defaults@0
(docs/spec/rd-9-soft-chain.md 1.13, 4.5, 6.10 and 8.3's SC-6 row; lean/VE/NormDefaults/LayeredAdmission.lean).

`layeredCase` has no admission and no certificate kind; `NormDefaults.Admission.softCase` answers both for a soft
source, and `Run.runCase` calls it first. Certificates are bound by the one binder `bindCertX` to the source
environment, the regenerated `premisesX L.U L.X []` (Lean's own encodings, read from its elaborate row) and the
case's premises and conclusion as written. Claim graphs admit, beside W2 provenance, the filled tree's layer, pair,
soft and `Fill_T` premises under their labels. Python here only proposes evidence (the frozen oracle and the prover
are untrusted generators); every verdict is Lean's.
"""
from __future__ import annotations

from copy import deepcopy

import pytest

from conformance import norm_defaults_layered as layered
from tests.test_norm_defaults_three_way import lean_executable  # noqa: F401  (the route fixture)
from ve import norm_defaults_route as route
from ve.ast import Binary, Forall, Implies, Not, Unary, Var, formula_from_data, formula_to_data
from ve.entailment import prove_entailment
from ve.identity import meaning_id
from ve.wire import digest

STALE = "certificate is stale or bound to different inputs"


def _fixture(name):
    return next((kind, env, source) for n, kind, env, source, _ in layered.fixtures() if n == name)


def _elaborate(kind, env, source):
    (row,) = route.run_cases([layered.case(kind, env, source, "norm-defaults-elaborate")])
    assert row["status"] == "ok", row
    return row


def _source_meaning(doc, ast):
    """A meaning id under the source environment, as `bindCertX` computes it (`Route.Wire.bindingOk`)."""
    env = doc.env
    return digest(f"ve-meaning-{env.identity_version}\n", {"environment_id": env.environment_id, "ast": ast})


def _regenerated_asts(row):
    """`premisesX L.U L.X []` as Lean encodes it: `background (fill U) ++ X ++ Fill_T ++ elaborate (fill U).T`."""
    return ([b["ast"] for b in row["background"]] + [s["ast"] for s in row["soft"]] +
            [f["ast"] for f in row["fill"]] + [p["ast"] for p in row["premises"]])


def _certificate_case(name, conclusion):
    """A `norm-defaults-certificate` case on the soft source `name` with a certificate the untrusted prover finds
    over `Background(E‴) ++ X ++ Fill_T ++ T‴`, bound to the source as `bindCertX` binds it."""
    kind, env, source = _fixture(name)
    row = _elaborate(kind, env, source)
    doc = layered.document(kind, env, source)
    filled = doc.filled.env
    regenerated = [formula_from_data(filled, s["ast"], _generated=True) for s in row["soft"]]
    regenerated += [f for _, f in doc.fill_premises] + [f for _, f in doc.filled.premises()]
    proof = prove_entailment(filled, tuple(regenerated), conclusion)
    assert proof.status == "Found", proof.status
    conclusion_ast = formula_to_data(filled, conclusion)
    certificate = {**proof.certificate, "environment_id": doc.env.environment_id,
                   "premise_meaning_ids": [_source_meaning(doc, a) for a in _regenerated_asts(row)],
                   "conclusion_meaning_id": _source_meaning(doc, conclusion_ast)}
    case = layered.case(kind, env, source, "norm-defaults-certificate", premises=[], conclusion=conclusion_ast,
                        certificate=certificate)
    return case, doc, row


def _u2_unexcepted():
    """u2: where the rule's exception does not apply, the act is not permitted."""
    permitted = Binary("system_prompt_deception_permitted", Var(1), Var(0))
    excepted = Binary("soft__excepted__no_system_prompt_deception", Var(1), Var(0))
    return (Forall("claude_instance", Forall("user", Implies(Not(excepted), Not(permitted))))), \
        Forall("claude_instance", Forall("user", Not(permitted)))


def _u8_unexcepted():
    """u8: where the rule's exception does not apply, the act is required."""
    return Forall("assistant", Implies(Not(Unary("soft__excepted__s", Var(0))), Unary("x_required", Var(0)))), \
        Forall("assistant", Unary("x_required", Var(0)))


@pytest.mark.parametrize("name, formulas", [("u2-unspecified-default", _u2_unexcepted),
                                            ("u8-unspecified", _u8_unexcepted)])
def test_layered_certificates_bind_the_regenerated_premises(lean_executable, name, formulas):
    """8.3 SC-6 certificates: the certificate is `valid`; replayed against the conclusion without the condition it is
    diagnostic 11 (`bindingOk` compares the conclusion's meaning id before any check); rebound to that conclusion
    its proof does not close (`valid: false`); with one regenerated premise missing from its binding, diagnostic
    11."""
    conclusion, weaker = formulas()
    case, doc, row = _certificate_case(name, conclusion)
    (answer,) = route.run_cases([case])
    assert answer["status"] == "ok", answer
    assert answer["valid"] is True
    assert answer["premises"] == len(_regenerated_asts(row))
    weaker_ast = formula_to_data(doc.filled.env, weaker)
    replayed = deepcopy(case)
    replayed["conclusion"] = weaker_ast
    rebound = deepcopy(replayed)
    rebound["certificate"]["conclusion_meaning_id"] = _source_meaning(doc, weaker_ast)
    missing = deepcopy(case)
    missing["certificate"]["premise_meaning_ids"].pop(len(row["background"]))
    rows = route.run_cases([replayed, rebound, missing])
    assert rows[0] == {"id": case["id"], "status": "error", "error": STALE}
    assert (rows[1]["status"], rows[1]["valid"]) == ("ok", False)
    assert rows[2] == {"id": case["id"], "status": "error", "error": STALE}


def test_the_soft_premises_are_part_of_the_binding(lean_executable):
    """`coherent` has `X ≠ []`: a binding over the norms route's premise list (without `X`) is refused."""
    kind, env, source = _fixture("coherent")
    row = _elaborate(kind, env, source)
    assert [s["label"] for s in row["soft"]] == ["soft:exception:must-x:sufficient:0",
                                                 "soft:coherence:must-x,need-not-x"]
    doc = layered.document(kind, env, source)
    conclusion = Forall("assistant", Implies(Unary("x_required", Var(0)), Unary("x_permitted", Var(0))))
    filled = doc.filled.env
    regenerated = [formula_from_data(filled, s["ast"], _generated=True) for s in row["soft"]]
    regenerated += [f for _, f in doc.fill_premises] + [f for _, f in doc.filled.premises()]
    proof = prove_entailment(filled, tuple(regenerated), conclusion)
    assert proof.status == "Found"
    conclusion_ast = formula_to_data(filled, conclusion)
    asts = _regenerated_asts(row)
    without_x = [a for a in asts if a not in [s["ast"] for s in row["soft"]]]
    cases = [layered.case(kind, env, source, "norm-defaults-certificate", premises=[], conclusion=conclusion_ast,
                          certificate={**proof.certificate, "environment_id": doc.env.environment_id,
                                       "premise_meaning_ids": [_source_meaning(doc, a) for a in ids],
                                       "conclusion_meaning_id": _source_meaning(doc, conclusion_ast)})
             for ids in (asts, without_x)]
    rows = route.run_cases(cases)
    assert (rows[0]["status"], rows[0]["valid"]) == ("ok", True)
    assert rows[1]["error"] == STALE


def _coherent_document(row, nodes, root):
    kind, env, source = _fixture("coherent")
    units = [{"id": f"u{i}", "span": [10 * i, 10 * i + 5], "kind": "norm", "content": n}
             for i, n in enumerate(layered._wire(source))]
    return env, {"units": units, "graph": {"root": root, "nodes": nodes}}


def _admission(env, document):
    return {"id": "a", "kind": "admission", "environment": env, "document": document}


def test_claim_graph_with_a_soft_coherence_leaf_is_admitted(lean_executable):
    """8.3 SC-6 claim graphs: a `soft:coherence` leaf of the filled tree is admitted, with `conditional_on` naming it
    (it is open: the colliding pair has no rank); a leaf with no regenerated premise is refused with W1's text."""
    kind, env, source = _fixture("coherent")
    row = _elaborate(kind, env, source)
    coherence = next(s for s in row["soft"] if s["label"].startswith("soft:coherence:"))
    exception = next(s for s in row["soft"] if s["label"].startswith("soft:exception:"))
    good = [{"name": "leaf", "ast": coherence["ast"], "label": coherence["label"]}]
    env, document = _coherent_document(row, good, "leaf")
    _, exc_document = _coherent_document(row, [{"name": "leaf", "ast": exception["ast"],
                                               "label": exception["label"]}], "leaf")
    wrong = [{"name": "leaf", "ast": ["top"], "label": coherence["label"]}]
    _, wrong_document = _coherent_document(row, wrong, "leaf")
    unknown = [{"name": "leaf", "ast": coherence["ast"], "label": "soft:coherence:need-not-x,must-x"}]
    _, unknown_document = _coherent_document(row, unknown, "leaf")
    rows = route.run_cases([_admission(env, d) for d in (document, exc_document, wrong_document, unknown_document)])
    assert rows[0]["status"] == "ok" and rows[0]["admitted"] is True, rows[0]
    assert rows[0]["conditional_on"] == [coherence["label"]]
    assert [a["label"] for a in rows[0]["report"]["assumptions"]] == [coherence["label"]]
    assert rows[0]["kinds"] == ["norm", "norm"]
    assert rows[1]["status"] == "ok" and rows[1]["conditional_on"] == []
    assert rows[2]["error"] == f"AdmissionError: invalid label {coherence['label']}"
    assert rows[3]["error"] == "AdmissionError: invalid label soft:coherence:need-not-x,must-x"


def _filled_json(env, row):
    """`filledJsonX`: the placeholder environment (each `unspecified` default read as `deny`, `norm-defaults@0` set
    aside) with soft's decision predicates and every `unsaid__p` added, the entries as Lean writes them in the
    layered row's `base_environment`."""
    placeholder = deepcopy(env)
    for entry in placeholder["vocabulary"]["predicates"].values():
        regulated = entry.get("regulated")
        if regulated is not None and regulated.get("default") == "unspecified":
            regulated["default"] = "deny"
    placeholder["profiles"] = [p for p in placeholder["profiles"] if p != "norm-defaults@0"]
    added = {name: entry for name, entry in row["base_environment"]["vocabulary"]["predicates"].items()
             if name.startswith(("soft__", "unsaid__"))}
    placeholder["vocabulary"]["predicates"] = {**placeholder["vocabulary"]["predicates"], **added}
    return placeholder


def _bound(filled_json, certificate, premise_asts, conclusion_ast):
    """A node certificate bound as admission binds it (`nodeBinding`): the filled environment under its profiles,
    the premise nodes' ASTs and the node's own."""
    version = "v0.2:" + ",".join(filled_json["profiles"])
    env_id = digest(f"ve-environment-{version}\n", filled_json)

    def meaning(ast):
        return digest(f"ve-meaning-{version}\n", {"environment_id": env_id, "ast": ast})
    return {**certificate, "environment_id": env_id, "premise_meaning_ids": [meaning(a) for a in premise_asts],
            "conclusion_meaning_id": meaning(conclusion_ast)}


def _deduction(row, env_json):
    """A graph whose root is a deduction from the coherence leaf, its certificate bound as admission binds it: to the
    regenerated soft `E‴` (`filledJsonX`) under the source profiles without `norm-defaults@0`, the premise node's AST
    and its own."""
    kind, env, source = _fixture("coherent")
    doc = layered.document(kind, env, source)
    filled = doc.filled.env
    coherence = next(s for s in row["soft"] if s["label"].startswith("soft:coherence:"))
    leaf = formula_from_data(filled, coherence["ast"], _generated=True)
    conclusion = leaf
    proof = prove_entailment(filled, (leaf,), conclusion)
    assert proof.status == "Found"
    conclusion_ast = formula_to_data(filled, conclusion)
    nodes = [{"name": "leaf", "ast": coherence["ast"], "label": coherence["label"]},
             {"name": "same", "ast": conclusion_ast, "premises": ["leaf"],
              "certificate": _bound(_filled_json(env_json, row), proof.certificate, [coherence["ast"]],
                                    conclusion_ast)}]
    return doc, filled, nodes


def test_substitutions_in_the_admitted_document(lean_executable):
    """8.3 SC-6 substitutions against `SourceDecodedX` (debate A1): a substituted root roots the report at that node
    with another `report_id`; a substituted node AST with its certificate kept is diagnostic 11; a substituted unit
    leaves a leaf citing it unadmitted (W2's `node <n> is not admitted under label <l>`)."""
    kind, env, source = _fixture("coherent")
    row = _elaborate(kind, env, source)
    doc, filled, nodes = _deduction(row, env)
    env, document = _coherent_document(row, nodes, "same")
    _, rooted = _coherent_document(row, nodes, "leaf")
    swapped = deepcopy(document)
    swapped["graph"]["nodes"][1]["ast"] = ["top"]
    rows = route.run_cases([_admission(env, d) for d in (document, rooted, swapped)])
    assert rows[0]["status"] == "ok", rows[0]
    assert rows[0]["report"]["root"]["name"] == "same"
    assert rows[1]["status"] == "ok" and rows[1]["report"]["root"]["name"] == "leaf"
    assert rows[1]["report_id"] != rows[0]["report_id"]
    assert rows[2] == {"id": "a", "status": "error", "error": STALE}


def test_a_substituted_unit_leaves_its_citing_leaf_unadmitted(lean_executable):
    """A leaf citing a unit whose content was replaced is W2's admission refusal, as on every route."""
    kind, env, source = _fixture("coherent")
    row = _elaborate(kind, env, source)
    asserted = {"id": "u2", "span": [30, 35], "kind": "asserted", "content": ["top"]}
    env, document = _coherent_document(row, [{"name": "fact", "ast": ["top"], "unit": "u2"}], "fact")
    document["units"].append(asserted)
    replaced = deepcopy(document)
    replaced["units"][-1]["content"] = ["bottom"]
    rows = route.run_cases([_admission(env, d) for d in (document, replaced)])
    assert rows[0]["status"] == "ok", rows[0]
    assert rows[1]["error"] == "AdmissionError: node fact is not admitted under label asserted", rows[1]


def test_rights_sources_keep_todays_answers(lean_executable):
    """8.3 SC-6 rights source: the certificate kind gives `runLayered`'s refusal (no layered certificate kind on the
    rights branch) and `admission` today's `runAdmission` answer, not the soft branch's."""
    kind, env, source = _fixture("u9-unspecified")
    (row,) = route.run_cases([layered.case(kind, env, source, "norm-defaults-certificate")])
    assert row["error"] == ("UnsupportedProfile: case kind norm-defaults-certificate is not available on the "
                            "rights@0 norm-defaults branch")
    (admission,) = route.run_cases([_admission(env, {"units": [], "graph": {"root": "x", "nodes": []}})])
    assert admission["status"] == "error"
    assert "conditional_on" not in admission


def test_soft_certificate_kind_is_answered_where_it_was_refused(lean_executable):
    """The availability change (spec 4.6, 1.1): before SC-6 a soft source's `norm-defaults-certificate` was
    `UnsupportedProfile`; now the soft branch answers it, and a case with no premises is the replay's own refusal."""
    kind, env, source = _fixture("u8-unspecified")
    (row,) = route.run_cases([layered.case(kind, env, source, "norm-defaults-certificate")])
    assert row == {"id": "norm-defaults-certificate", "status": "error", "error": "property not found: premises"}


def test_missing_certificate_premises_has_the_norms_branch_text(lean_executable):
    """B2: the soft branch uses the existing replay decoder's missing-field text."""
    from tests.test_readings_nd_lean import env1
    kind, env, source = _fixture("u8-unspecified")
    norms = env1(profiles=("norm-defaults@0", "norms@0", "relational-fol@0"))
    rows = route.run_cases([
        layered.case(kind, env, source, "norm-defaults-certificate"),
        {"id": "norm-defaults-certificate", "kind": "norm-defaults-certificate",
         "environment": norms, "norms": []},
    ])
    assert rows[0]["error"] == rows[1]["error"] == "property not found: premises"
