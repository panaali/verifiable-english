"""Genuine requests for every service mode and result kind (schema and differential tests).

Small, deterministic slices of the committed fixtures and generators the parity tool
uses (`tools/lean_service_parity.py`), plus norms cases built as in
`tests/test_norms_three_way.py`. Every result kind of every mode occurs, as do line
errors, case errors and runner errors.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text())


ADVERSARIAL = [{"id": "deep", "x": json.loads("[" * 300 + "]" * 300)}, {}, {"id": "no-environment"},
               {"id": 7, "environment": {}}, {"id": {"nested": [0, False]}, "kind": "certificate"},
               {"id": "list-env", "environment": []}, [], "text"]


def evaluate_cases():
    evaluation = load("conformance/evaluation.json")
    countermodels = load("conformance/countermodels.json")
    closure = load("conformance/closure.json")
    return evaluation[:24] + countermodels[:8] + closure[:8] + [
        {**evaluation[0], "kind": "other"}, {**evaluation[0], "ast": []}] + ADVERSARIAL


def certificate_cases():
    rows = load("conformance/v0-replay-baseline.json")["rows"]
    queries = [json.loads(p.read_text()) for p in
               sorted((ROOT / "usecases/closure-induction").glob("*/query.json"))[:3]]
    return [r["case"] for r in rows[:12]] + queries + ADVERSARIAL


def order_cases():
    from conformance import order
    from ve import Environment, print_document
    from ve.ast import document_from_data
    from ve.entailment import prove_entailment
    generated = order.evaluation_cases(24)
    generated = [c for c, _ in generated] if generated and isinstance(generated[0], tuple) else generated
    surface, countermodel = [], []
    for case in generated:
        env = Environment(case["environment"])
        source = print_document(env, document_from_data(env, case["ast"]))
        surface.append({"id": case["id"] + "-s", "kind": "surface", "environment": case["environment"],
                        "source": source})
        if case["ast"]:
            countermodel.append({"id": case["id"] + "-c", "kind": "countermodel",
                                 "environment": case["environment"], "model": case["model"],
                                 "premises": case["ast"][:-1], "conclusion": case["ast"][-1]})
    certificates = []
    rng = random.Random(42)
    for i in range(4):
        premises, goal = order.gen_farkas(rng)
        env = order.environment(i)
        proof = prove_entailment(env, premises, goal, max_steps=4000)
        if proof.certificate:
            certificates.append(order.envelope(f"farkas{i}", env, premises, goal, proof.certificate))
    empty = {"id": "empty-surface", "kind": "surface", "environment": generated[0]["environment"],
             "source": ""}
    return generated + surface + countermodel + certificates + [empty] + ADVERSARIAL


def route_cases():
    route = load("lean/VE/Route/examples/route-cases.json")
    by_kind = {}
    for case in route:
        by_kind.setdefault(case.get("kind", "evaluate"), []).append(case)
    cases = [c for kind in sorted(by_kind) for c in by_kind[kind][:16]]
    bundle = load("usecases/math-mini-paper/t7-definitions-bundle.json")
    cases.append({"id": "t7", "kind": "bundle", "environment": bundle["environment"],
                  "lemmas": bundle["lemmas"]})
    stale = deepcopy(cases[-1])
    stale["id"] = "t7-stale"
    stale["lemmas"][0]["meaning_id"] = "0" * 64
    cases.append(stale)
    from tests.test_definitions_differential import generate, probes
    for index in range(6):
        env, model, _ = generate(index)
        try:
            ast = probes(env)
        except Exception:  # noqa: BLE001  (an invalid environment: Lean reports it)
            ast = []
        cases.append({"id": f"bg{index}", "kind": "background", "environment": env})
        cases.append({"id": f"ev{index}", "kind": "evaluate", "environment": env, "model": model,
                      "ast": ast})
    certificate = by_kind["certificate"][0]
    cases.append({**certificate, "id": "invalid-model", "kind": "evaluate",
                  "model": {"domains": {}, "constants": {}, "relations": {}}, "ast": [["top"]]})
    return cases + ADVERSARIAL


def norms_cases():
    from tests.test_norms import environment, model, obligation, permission, rule
    from tests.test_norms_three_way import corpus, lean_case
    from tests.test_norm_admission import source
    from ve.ast import Not, Top, formula_to_data
    from ve.entailment import prove_entailment
    from ve.norms import NormDocument, _bind, check_conflict, prove_norm_entailment
    cases = [lean_case(i, d) for i, d in zip(range(8), corpus())]
    env = environment({"permitted": permission()},
                      base={"condition": {"arguments": ["act"], "description": "condition"}})
    pair = environment({"permitted": permission(), "required": obligation()})
    documents = [NormDocument(env, [rule("yes", "permitted", True), rule("no", "permitted", False)]),
                 NormDocument(env, [rule("no", "permitted", False),
                                    rule("exception", "permitted", True, over=("no",))]),
                 NormDocument(pair, [rule("must", "required", True), rule("may", "permitted", True)])]
    for i, doc in enumerate(documents):
        report = check_conflict(doc, model=model(doc))
        if report.status == "CONFLICT":
            cases.append({**lean_case(f"w{i}", doc), "kind": "norms-conflict",
                          "witness": {"target": report.target, "model": model(doc).to_dict(),
                                      "tuple": list(report.tuple)}})
        packages = {}
        for target, sorts, formula in doc.conflict_targets():
            proof = prove_entailment(doc.base_environment(), (), _bind(Not(formula), sorts))
            if proof.certificate:
                packages[target] = {"environment_id": doc.env.environment_id,
                                    "document_hash": doc.document_hash, "target": target,
                                    "certificate": proof.certificate}
        cases.append({**lean_case(f"c{i}", doc), "kind": "norms-conflict", "packages": packages})
    doc = NormDocument(environment({"permitted": permission()}), [rule("allow", "permitted", True)])
    conclusion = doc.elaborate("permitted")
    proof = prove_norm_entailment(doc, (Top(),), conclusion)
    cases.append({"id": "certificate", "kind": "norms-certificate", "environment": doc.env.to_dict(),
                  "norms": [r.to_dict() for r in doc.rules], "premises": [["top"]],
                  "conclusion": formula_to_data(doc.env, conclusion), "certificate": proof.certificate})
    raw, document = source()
    cases.append({"id": "admission", "kind": "admission", "environment": raw.to_dict(),
                  "document": document})
    quoted = deepcopy(document)
    quoted["units"][0]["kind"] = ["attributed", "alice", "says", "norm"]
    quoted["units"].append({"id": "u2", "span": [20, 30], "kind": "asserted", "content": ["top"]})
    quoted["graph"] = {"root": "asserted", "nodes": [{"name": "asserted", "ast": ["top"], "unit": "u2"}]}
    cases.append({"id": "quoted", "kind": "admission", "environment": raw.to_dict(), "document": quoted})
    cases.append({"id": "unsupported", "kind": "evaluate", "norms": []})
    return cases + route_cases()


def english_cases():
    import warnings
    from conformance import english_lean as E
    from ve import ast, render
    from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning
    warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
    payloads = []
    for offset, (name, env, options) in enumerate(E.configurations()):
        if len(payloads) == 4:
            break
        words = EnglishVocabulary(env, **options)
        try:
            lex = E.lexicon(env, words)
        except E.Untokenizable:
            continue
        letters = tuple(words.letters.values())
        cases = []
        for formula in E.corpus(env, words, name, 6, offset):
            if not E.v0_only(formula):
                continue
            text = render(ast.Document((formula,)), env, "ve_english", **options)
            cases.append({"tokens": E.tokenize(E.lower_sentence_starts(text), letters),
                          "formulas": [E.wire(formula)]})
        cases += [{"tokens": tokens, "formulas": [E.wire(ast.Top())]} for _, tokens, _ in E.fixtures(lex)][:4]
        cases.append({"tokens": ["no", "such", "words"], "formulas": []})
        payloads.append({"environment": E.environment(env), "lexicon": lex, "cases": cases})
    return payloads + [{"environment": {}}, {"lexicon": {}}]


def corpus():
    """{mode: [case, ...]} with every result kind of every mode."""
    return {"evaluate": evaluate_cases(), "check-certificate": certificate_cases(),
            "order": order_cases(), "route": route_cases(), "norms": norms_cases(),
            "english": english_cases()}
