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


# Request errors of every kind: (mode, cases text, count, budget).
ERROR_REQUESTS = [
    ("evaluate", '[{"id":"a","ast":[]},{"id":"b","ast":[]}]', 2, {"cases": 1}),
    ("route", '[{"id":"a","kind":"evaluate"}]', 1, {"bytes": 3}),
    ("evaluate", '[{},{}]', 2, {"steps": 1}),
    ("order", '[{"id":1,}]', 1, None),
    ("check-certificate", '[{"id":null}, {"id":"b"}]', 2, None),
    ("english", '[{"cases":[],}]', 1, None),
    ("norms", '{}', 0, {"cases": 1}),
]


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
    # Background of every certificate environment: flags, definitions and literals on
    # the FOL, closure and order families.
    cases += [{"id": c["id"] + "-bg", "kind": "background", "environment": c["environment"]}
              for c in by_kind["certificate"]]
    cases.append(shared_admission())
    cases.append(deep_definition_background(route))
    cases += fol_projection_cases()
    return cases + ADVERSARIAL


def negations(depth, leaf):
    for _ in range(depth - 1):
        leaf = ["not", leaf]
    return leaf


def deep_definition_background(route, depth=64):
    """A binary definition whose body has depth `depth` (at most the decoder's 64): its
    Background premise, two binders and a biconditional around the body, is 4 deeper."""
    case = deepcopy(next(c for c in route if c.get("id") == "defs-background"))
    case["id"] = f"deep-definition-{depth}"
    case["environment"]["vocabulary"]["predicates"]["over"] = {
        "arguments": ["person", "person"], "description": "is over",
        "defined": {"arguments": ["person", "person"],
                    "body": negations(depth, ["binary", "supervises", ["var", 1], ["var", 0]])}}
    return case


FOL_FAMILIES = ("defined", "functional", "total")


def fol_projection_environment(family, arity, norms=False):
    """A `nary@0` environment whose predicate `p` has `arity` arguments and carries the
    Background family `family`; with `norms`, also a regulated obligation/permission pair."""
    from ve.profiles import SPEC_REVISION
    point = {"description": "point"}

    def declared(n, description):
        return {"arguments": ["point"] * n, "description": description}
    predicates = {"upper": declared(1, "upper"), "base1": declared(1, "base"),
                  "base2": declared(2, "base"), "base3": declared(3, "base")}
    bodies = {1: ["unary", "base1", ["var", 0]], 2: ["binary", "base2", ["var", 1], ["var", 0]],
              3: ["atom", "base3", [["var", 2], ["var", 1], ["var", 0]]]}
    extra = {"defined": {"arguments": ["point"] * arity, "body": bodies[arity]}} if family == "defined" else {
        family: True}
    predicates["p"] = {**declared(arity, "p"), **extra}
    profiles = ["closure@0", "data@0", "definitions@0", "nary@0", "relational-fol@0"]
    if norms:
        profiles.append("norms@0")
        predicates["permitted"] = {**declared(1, "permission"), "regulated": {
            "role": "permission", "default": "deny", "act": "{0} be done"}}
        predicates["required"] = {**declared(1, "obligation"), "regulated": {
            "role": "obligation", "default": "deny", "act": "{0} be done", "permission": "permitted"}}
    return {"language": "ve.core@0.2", "profiles": sorted(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {"point": point}, "predicates": predicates, "constants": {}}}


def fol_projection_cases(norms=False):
    """Certificates and Background cases over each Background family (`FOL_FAMILIES`) on a predicate of every
    arity 1-3 the environment admits. Every regenerated Background is built from the FOL
    projection (`VE.Core.Layers.folEntry`: at most two arguments), so a three-argument
    declaration adds no premise and the response's `background` count must not count it
    (lf-13b looprecheck1: a valid certificate was refused over a three-argument definition).
    With `norms`, the environments also declare a norm pair (the norms route refuses its
    `norms-certificate` over `nary@0`, so these are plain certificates)."""
    from ve import ast
    from ve.ast import formula_to_data
    from ve.entailment import prove_entailment
    from ve.environment import Environment
    from ve.errors import VEError
    cases = []
    for family in FOL_FAMILIES:
        for arity in (1, 2, 3):
            raw = fol_projection_environment(family, arity, norms)
            try:
                env = Environment(raw)
            except VEError:  # data flags on a unary predicate
                continue
            goal = ast.Forall("point", ast.Unary("upper", ast.Var(0)))
            proof = prove_entailment(env, [goal], goal)
            data = formula_to_data(env, goal)
            name = f"fol-{'norms-' if norms else ''}{family}-{arity}"
            cases.append({"id": name, "kind": "certificate", "environment": raw, "premises": [data],
                          "conclusion": data, "certificate": proof.certificate})
            cases.append({"id": name + "-bg", "kind": "background", "environment": raw})
    return cases


NORM_PAIR_ARITIES = (1, 2, 3, 4)


def norm_pair_environment(arity):
    """lf-13b looprecheck2: a `nary@0` environment whose obligation `required` and its
    permission dual `permitted` take `arity` arguments, beside a unary `upper`."""
    from ve.profiles import SPEC_REVISION
    act = " ".join(f"{{{i}}}" for i in range(arity)) + " be done"

    def regulated(description, **fields):
        return {"arguments": ["point"] * arity, "description": description,
                "regulated": {"default": "deny", "act": act, **fields}}
    return {"language": "ve.core@0.2", "spec_revision": SPEC_REVISION,
            "profiles": sorted(["closure@0", "nary@0", "norms@0", "relational-fol@0"]),
            "vocabulary": {"sorts": {"point": {"description": "point"}}, "constants": {}, "predicates": {
                "upper": {"arguments": ["point"], "description": "upper"},
                "permitted": regulated("permission", role="permission"),
                "required": regulated("obligation", role="obligation", permission="permitted")}}}


def norm_pair_cases():
    """A plain certificate proving `∀x upper(x) ⊢ ∀x upper(x)`, and a Background case, over a
    norm pair of each arity in `NORM_PAIR_ARITIES`. Lean's Background holds the pair's profile
    premise at every arity (`Norms.Plain.pairPremises`), so the certificate's `background` is 1;
    the client must not predict it (architecture decision D1)."""
    from ve import ast
    from ve.ast import formula_to_data
    from ve.entailment import prove_entailment
    from ve.environment import Environment
    cases = []
    for arity in NORM_PAIR_ARITIES:
        raw = norm_pair_environment(arity)
        env = Environment(raw)
        goal = ast.Forall("point", ast.Unary("upper", ast.Var(0)))
        proof = prove_entailment(env, [goal], goal)
        data = formula_to_data(env, goal)
        cases.append({"id": f"pair-{arity}", "kind": "certificate", "environment": raw, "premises": [data],
                      "conclusion": data, "certificate": proof.certificate})
        cases.append({"id": f"pair-{arity}-bg", "kind": "background", "environment": raw})
    return cases


def soft_premise_certificate():
    """A plain certificate on a `soft-norms@0` environment carrying two soft premises
    (`Norms.Plain.softPremises`): Lean's Background is the (empty) route Background followed
    by them, so its `background` is 2 though the vocabulary generates nothing."""
    from ve import ast
    from ve.ast import formula_to_data
    from ve.entailment import prove_entailment
    from ve.environment import Environment
    from ve.profiles import SPEC_REVISION
    raw = {"language": "ve.core@0.2", "spec_revision": SPEC_REVISION,
           "profiles": ["norms@0", "relational-fol@0", "soft-norms@0"],
           "vocabulary": {"sorts": {"point": {"description": "point"}}, "constants": {}, "predicates": {
               "upper": {"arguments": ["point"], "description": "upper"}}}}
    env = Environment(raw)
    goal = ast.Forall("point", ast.Unary("upper", ast.Var(0)))
    soft = [ast.Top(), ast.Top()]
    proof = prove_entailment(env, [*soft, goal], goal)
    data = formula_to_data(env, goal)
    return {"id": "soft-certificate", "kind": "certificate", "environment": raw, "premises": [data],
            "conclusion": data, "certificate": proof.certificate,
            "soft_premises": [formula_to_data(env, f) for f in soft]}


def deep_norms_elaboration():
    """70 rules on one predicate: the elaboration's disjunction of them is deeper than 64."""
    from tests.test_norms import environment, permission, rule
    env = environment({"permitted": permission()})
    return {"id": "deep-rules", "kind": "norms-elaborate", "environment": env.to_dict(),
            "norms": [rule(f"r{j}", "permitted", True).to_dict() for j in range(70)]}


def shared_admission():
    """An admitted graph whose unfolding repeats shared leaves:
    root <- [mid, b, mid], mid <- [a, b, a], so the report lists a b a b a b a."""
    from tests.test_data_flags import environment
    from ve.ast import Top
    from ve.entailment import prove_entailment
    from ve.identity import meaning_id
    env = environment()
    proof = prove_entailment(env, (), Top())
    assert proof.status == "Found"

    def deduce(name, premises):
        certificate = deepcopy(proof.certificate)
        certificate["premise_meaning_ids"] = [meaning_id(env, Top())] * len(premises)
        return {"name": name, "ast": ["top"], "premises": premises, "certificate": certificate}

    nodes = [{"name": "a", "ast": ["top"], "unit": "u"}, {"name": "b", "ast": ["top"], "unit": "u"},
             deduce("mid", ["a", "b", "a"]), deduce("root", ["mid", "b", "mid"])]
    document = {"units": [{"id": "u", "span": [0, 1], "kind": "asserted", "content": ["top"]}],
                "graph": {"root": "root", "nodes": nodes}}
    return {"id": "shared-leaves", "kind": "admission", "environment": env.to_dict(), "document": document}


def norms_cases():
    from tests.test_norms import environment, model, obligation, permission, rule
    from tests.test_norms_three_way import corpus, lean_case
    from tests.test_norm_admission import source
    from ve.ast import Not, Top, formula_to_data
    from ve.entailment import prove_entailment
    from ve.environment import Environment
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
        cases.append({**lean_case(f"e{i}", doc), "kind": "norms-elaborate"})
    literals = pair.to_dict()
    literals["vocabulary"]["constants"].update({c: {"sort": "$string"} for c in ("alpha", "beta", "gamma")})
    cases.append({"id": "e-literals", "kind": "norms-elaborate", "environment": literals,
                  "norms": [r.to_dict() for r in documents[2].rules]})
    doc = NormDocument(environment({"permitted": permission()}), [rule("allow", "permitted", True)])
    conclusion = doc.elaborate("permitted")
    proof = prove_norm_entailment(doc, (Top(),), conclusion)
    cases.append({"id": "certificate", "kind": "norms-certificate", "environment": doc.env.to_dict(),
                  "norms": [r.to_dict() for r in doc.rules], "premises": [["top"]],
                  "conclusion": formula_to_data(doc.env, conclusion), "certificate": proof.certificate})
    # A norms certificate with a non-empty Background (one literal pair), so its count has a
    # natural neighbour on both sides.
    with_literals = doc.env.to_dict()
    with_literals["vocabulary"]["constants"].update({c: {"sort": "$string"} for c in ("alpha", "beta")})
    doc = NormDocument(Environment(with_literals), doc.rules)
    conclusion = doc.elaborate("permitted")
    proof = prove_norm_entailment(doc, (Top(),), conclusion)
    cases.append({"id": "certificate-literals", "kind": "norms-certificate", "environment": with_literals,
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
    cases.append(deep_norms_elaboration())
    cases += fol_projection_cases(norms=True)
    cases += norm_pair_cases()
    cases.append(soft_premise_certificate())
    return cases + route_cases()


def english_cases(negations=(64, 200)):
    """Four English payloads; the first also parses fixtures under each count of
    `negations` negations, deeper than the decoders' 64."""
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
        fixtures = [{"tokens": tokens, "formulas": [E.wire(ast.Top())]} for _, tokens, _ in E.fixtures(lex)][:4]
        cases += fixtures
        cases.append({"tokens": ["no", "such", "words"], "formulas": []})
        if not payloads:
            def tokens(formula):
                text = render(ast.Document((formula,)), env, "ve_english", **options)
                return E.tokenize(E.lower_sentence_starts(text), letters)
            once, twice = tokens(ast.Not(ast.Top())), tokens(ast.Not(ast.Not(ast.Top())))
            prefix = twice[:len(twice) - len(once)]  # one negation
            cases += [{**fixture, "tokens": prefix * k + fixture["tokens"]}
                      for fixture in fixtures[:2] for k in negations]
        payloads.append({"environment": E.environment(env), "lexicon": lex, "cases": cases})
    return payloads + [{"environment": {}}, {"lexicon": {}}]


def corpus():
    """{mode: [case, ...]} with every result kind of every mode."""
    from tests.probe_matrix import raw_environment, model_wire
    from ve import Environment, FiniteModel
    env = Environment(raw_environment(()))
    model = FiniteModel.from_dict(env, model_wire(env))
    standalone_env = [{"id": "ok", "environment": env.to_dict()},
                      {"id": "bad", "environment": {}}, *ADVERSARIAL]
    standalone_model = [{"id": "ok", "environment": env.to_dict(),
                         "model": model.to_dict()},
                        {"id": "bad", "environment": env.to_dict(), "model": {}},
                        *ADVERSARIAL]
    identities = [{"id": "source", "kind": "source", "source": "true.\n",
                   "environment": env.to_dict()},
                  {"id": "meaning", "kind": "meaning", "environment": env.to_dict(),
                   "ast": ["top"]},
                  {"id": "model", "kind": "model", "environment": env.to_dict(),
                   "model": model.to_dict()},
                  {"id": "bad", "kind": "unknown"}, *ADVERSARIAL]
    return {"evaluate": evaluate_cases(), "check-certificate": certificate_cases(),
            "order": order_cases(), "route": route_cases(), "norms": norms_cases(),
            "english": english_cases(), "environment": standalone_env,
            "model": standalone_model, "identity": identities, "document": document_cases()}


def document_cases():
    """The `document` mode's answers: the wrapper's generated seed documents (accepted, MIXED parts, reading
    sets, an admitted graph, a rejection and a refusal), the repository's accepted bluedot document, and
    malformed requests."""
    from conformance import document_wrapper as dw
    chosen = {"plain", "mixed", "reading-sets", "graph-bridge", "open-terms", "fence",
              "usecases/bluedot-grant/document.ve.md", "usecases/bluedot-grant/causal.ve.md"}
    cases = [{"id": name, "document": dw.text_of(doc)} for name, doc in dw.seeds() if name in chosen]
    return cases + [{"id": "empty", "document": ""}, {"id": "not-text", "document": 7}, *ADVERSARIAL]
