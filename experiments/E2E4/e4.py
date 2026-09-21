"""Twelve held-out quantified/relational inference templates, certified by oracle."""
from dataclasses import replace, asdict
from functools import lru_cache
import hashlib
import json

from ve import ast, ArgumentGraph, Claim, Deduction, FiniteModel, check_argument
from ve.argument import deduction_identity
from ve.equivalence import compare, Budgets
from ve.search import check_countermodel
from .common import fresh, source, conjunct, ast_environment, instruction

CELLS = ("checked_countermodel", "prose_critique", "dishonest_critic")
VOCABS = {**{f"dev_{s}": "dev" for s in ("aster", "brindle")},
          **{f"score_{s}": "scored" for s in ("cobalt", "dovetail", "elm", "flint", "garnet")}}
TEMPLATES = ("quantifier_order", "witness_sharing", "relation_subject", "relation_range",
             "witness_direction", "transitive_path", "negative_instantiation", "guarded_transport",
             "relation_inclusion", "quantifier_negation", "existential_disjunction", "universal_disjunction",
             "dev_instantiation", "dev_existential", "dev_relation", "dev_transport")


def inference(template, family):
    names = {s: fresh(family, s) for s in "pqrstu"}
    def P(t): return ast.Unary(names["p"], t)
    def Q(t): return ast.Unary(names["q"], t)
    def R(x, y): return ast.Binary(names["r"], x, y)
    def S(x, y): return ast.Binary(names["s"], x, y)
    def T(x, y): return ast.Binary(names["t"], x, y)
    A, O, I, N = ast.And, ast.Or, ast.Implies, ast.Not
    def F(body): return ast.Forall("object", body)
    def E(body): return ast.Exists("object", body)
    x, y, z = ast.Var(0), ast.Var(1), ast.Var(2)
    a, b, c = ast.Const("a"), ast.Const("b"), ast.Const("c")
    cases = {
        # tuple(premises), valid conclusion, invalid conclusion
        "quantifier_order": ((E(F(R(y, x))),), F(E(R(x, y))), F(E(R(y, x)))),
        "witness_sharing": ((E(P(x)), E(Q(x))), E(E(A(P(y), Q(x)))), E(A(P(x), Q(x)))),
        "relation_subject": ((F(F(I(R(y, x), P(y)))), R(a, b)), P(a), P(b)),
        "relation_range": ((F(F(I(R(y, x), Q(x)))), E(E(R(y, x)))), E(Q(x)), F(Q(x))),
        "witness_direction": ((F(I(P(x), E(R(y, x)))), P(a)), E(R(a, x)), E(R(x, a))),
        "transitive_path": ((F(F(F(I(A(R(z, y), R(y, x)), R(z, x))))), R(a, b), R(b, c)), R(a, c), R(c, a)),
        "negative_instantiation": ((F(I(P(x), N(Q(x)))), Q(a)), N(P(a)), N(P(b))),
        "guarded_transport": ((F(I(P(x), Q(x))), E(A(P(x), R(x, a)))), E(A(Q(x), R(x, a))), E(A(Q(x), R(a, x)))),
        "relation_inclusion": ((F(F(I(R(y, x), S(y, x)))), F(F(I(S(y, x), T(y, x))))), F(F(I(R(y, x), T(y, x)))), F(F(I(T(y, x), R(y, x))))),
        "quantifier_negation": ((N(E(A(P(x), Q(x)))),), F(I(P(x), N(Q(x)))), F(I(P(x), Q(x)))),
        "existential_disjunction": ((E(O(P(x), Q(x))),), O(E(P(x)), E(Q(x))), A(E(P(x)), E(Q(x)))),
        "universal_disjunction": ((F(O(P(x), Q(x))),), F(O(Q(x), P(x))), O(F(P(x)), F(Q(x)))),
        "dev_instantiation": ((F(I(P(x), Q(x))), P(a)), Q(a), Q(b)),
        "dev_existential": ((E(A(P(x), Q(x))),), E(P(x)), F(P(x))),
        "dev_relation": ((F(F(I(R(y, x), S(y, x)))), R(a, b)), S(a, b), S(b, a)),
        "dev_transport": ((F(I(P(x), Q(x))), E(P(x))), E(Q(x)), F(Q(x))),
    }
    return cases[template]


def certified(env, premise, conclusion, oracle):
    leaf, root = Claim.create(env, "assumptions", source(premise)), Claim.create(env, "root", source(conclusion))
    edge = Deduction("step", ("assumptions",), "root")
    graph = ArgumentGraph(env, (leaf, root), (edge,), "root")
    finding = oracle.a_implies_b
    if finding.status == "ENTAILED":
        edge = replace(edge, certificates=({"edge_id": deduction_identity(graph, edge),
            "direction": "follows", "proof": finding.certificate},))
    elif finding.status == "COUNTERMODEL":
        edge = replace(edge, countermodels=(finding.model,))
    else:
        raise AssertionError("Undecided inference; never label from failed search")
    graph = replace(graph, deductions=(edge,))
    result = check_argument(graph, search=False)
    assert result.findings["step"] == (("follows",) if finding.status == "ENTAILED" else ("gap",))
    return {"graph": graph.to_dict(), "result": result.to_dict()}


def prose_model(model):
    lines = ["Consider the following complete hypothetical interpretation."]
    for sort, entities in model["domains"].items():
        lines.append(f"The {sort} domain contains exactly " + (", ".join(entities) if entities else "no entities") + ".")
    for constant, entity in model["constants"].items():
        lines.append(f"The name {constant} denotes {entity}.")
    for predicate, tuples in model["relations"].items():
        if tuples:
            lines.append(f"The extension of {predicate} consists exactly of " + "; ".join("(" + ", ".join(t) + ")" for t in tuples) + ".")
        else:
            lines.append(f"The extension of {predicate} is empty.")
    lines.append("All tuples not listed are false. The critic claims every premise holds and the conclusion fails in this interpretation.")
    return " ".join(lines)


PADDING = ("The dossier refers throughout to the displayed finite interpretation. Read the object names and relations in their declared argument order. "
           "The listed assumptions and submitted conclusion are the statements under consideration. ").split()


def matched_critiques(check, asserted, model_check):
    status = "accepted" if model_check.valid else "rejected"
    formal = ("Checker replay of the critic's interpretation: " + status + ". "
              "Logical inference finding: " + ", ".join(check["result"]["findings"]["step"]) + ". "
              "Premise truth values: " + json.dumps(list(model_check.premise_values)) + ". "
              "Conclusion truth value: " + json.dumps(model_check.conclusion_value) + ". "
              "Complete interpretation: " + json.dumps(asserted, sort_keys=True, indent=1))
    prose = prose_model(asserted)
    dishonest = "Critic asserts this countermodel (unchecked): " + json.dumps(asserted, sort_keys=True, indent=1)
    versions = {"checked_countermodel": formal, "prose_critique": prose, "dishonest_critic": dishonest}
    # Exact whitespace-token length matching, including the checker status.
    # Neutral dossier text contains no inference-specific truth claims. This is
    # only a tokenizer proxy, not a promise of equality for every model tokenizer.
    target = max(len(v.split()) for v in versions.values()) + len(PADDING)
    return {k: v + "\n" + " ".join(PADDING[i % len(PADDING)] for i in range(target - len(v.split()))) for k, v in versions.items()}


def make_pair(template, family):
    premises, valid, invalid = inference(template, family)
    premise = conjunct(premises)
    env = ast_environment((*premises, valid, invalid))
    good = compare(env, premise, valid, Budgets(max_proof_steps=10000, max_models=10000))
    bad = compare(env, premise, invalid, Budgets(max_proof_steps=10000, max_models=10000))
    assert good.a_implies_b.status == "ENTAILED", (template, good.to_dict())
    assert bad.a_implies_b.status == "COUNTERMODEL", (template, bad.to_dict())
    asserted = bad.a_implies_b.model
    rows = []
    for conclusion, oracle, label in ((valid, good, "good"), (invalid, bad, "bad")):
        check = certified(env, premise, conclusion, oracle)
        model_check = check_countermodel(env, premises, conclusion, asserted)
        assert model_check.valid == (label == "bad")
        critiques = matched_critiques(check, asserted.to_dict(), model_check)
        p = {"experiment": "E4", "family": family, "template": template,
             "premises": [source(s).strip() for s in premises], "conclusion": source(conclusion).strip(),
             "check": check, "oracle": oracle.to_dict(), "asserted_model": asserted.to_dict(),
             "asserted_model_check": json.loads(json.dumps(asdict(model_check))), "critiques": critiques,
             "_audit": {"valid_inference": label == "good", "template": template,
                        "vocabulary_family": family, "critic_is_dishonest": label == "good"}}
        rows.append({"id": "e4-" + hashlib.sha256(f"{template}/{family}/{label}".encode()).hexdigest()[:18],
                     "label": label, "payload": p, "group": f"E4/{template}/{family}", "split": VOCABS[family]})
    return rows


@lru_cache(maxsize=1)
def items():
    rows = []
    for template in TEMPLATES:
        for family, split in VOCABS.items():
            if template.startswith("dev_") == (split == "dev"):
                rows.extend(make_pair(template, family))
    return sorted(rows, key=lambda r: r["id"])


def render(p, cell):
    if cell not in CELLS:
        raise ValueError(cell)
    return "\n".join(["Decide whether the inference is valid. The premises are assumptions for this logical task. Sorts may be empty unless the premises or named constants require inhabitants.",
        "Premises: " + " ".join(p["premises"]), "Conclusion: " + p["conclusion"], "Critic: " + p["critiques"][cell], instruction()])
