"""Lean soft-norms route (docs/spec/soft-norms.md 9.4, item 4) against the item-1 fixtures.

The Lean executable regenerates E′ and T′ from raw soft norm objects. Its layer
premises are evaluated here by the Python evaluator on one-element situations with
every decision table supplied, which reads off W1's value on T′ (Lean proves it is
ValueSoft, `soften_faithful`) and is compared with the hand-written fixture results.
Diagnostics, witness replay and the pair classification are checked on the same
inputs. The Python soft profile (item 2) is not needed: environments are raw JSON.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ve.ast import formula_from_data
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.wire import digest
from tests.test_norms import environment, obligation, permission

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_soft_norms_route"
DECIDER = {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}


@pytest.fixture(scope="module")
def lean():
    if not LEAN.exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("lake is required for the soft-norms Lean route")
        built = subprocess.run([lake, "build"], cwd=ROOT / "lean", capture_output=True,
                               text=True, timeout=600)
        assert built.returncode == 0, built.stdout + built.stderr
    return LEAN


def run(executable, cases):
    result = subprocess.run([str(executable), "-"], input=json.dumps(cases), text=True,
                            capture_output=True, timeout=180)
    assert result.returncode in (0, 1), result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    return rows


def env(soft=None, *, perm="allow", req="deny", extra=None, profiles=("norms@0", "soft-norms@0")):
    """Act X: x_required (obligation, dual x_permitted) and x_permitted, over one sort."""
    raw = environment({"x_required": obligation(req, "x_permitted", act="{0} do x", args=("assistant",)),
                       "x_permitted": permission(perm, act="{0} do x", args=("assistant",)),
                       **(extra or {})}, sorts=("assistant", "user")).to_dict()
    raw["profiles"] = sorted({"relational-fol@0"} | set(profiles))
    if soft is not None:
        raw["vocabulary"]["soft"] = soft
    return raw


def norm(name, pred, sign, *, guard=("top",), unless=(), over=(), **soft):
    return {"norm": {"name": name, "predicate": pred, "sign": sign, "guard": list(guard),
                     "unless": [list(u) for u in unless], "over": list(over), **soft}}


def should(name, pred, sign, **soft):
    return norm(name, pred, sign, **{"mode": "default", "exception": dict(DECIDER), **soft})


def ranks(order, mode="strict", parties=()):
    edges = [[a, b] for a, b in zip(order, order[1:])]
    block = {"ranks": list(order), "outranks": edges, "outranking": {"mode": mode}}
    if mode == "holistic":
        block["outranking"]["decided_by"] = "assistant"
    if parties:
        block["parties"] = list(parties)
    return block


def elaborate(lean, environment_json, norms):
    row = run(lean, [{"id": "e", "kind": "soft-elaborate", "environment": environment_json,
                      "norms": norms}])[0]
    assert row["status"] == "ok", row
    return row


def python_env(row):
    """E′ as a Python environment (the soft block is metadata the evaluator does not read)."""
    data = json.loads(json.dumps(row["environment_prime"]))
    data["profiles"] = [p for p in data["profiles"] if p != "soft-norms@0"]
    data["vocabulary"].pop("soft", None)
    for entry in data["vocabulary"]["predicates"].values():
        entry.pop("instruction_of", None)
    return Environment(data)


def values(row, predicate, decisions):
    """The values of `predicate` at the one-element situation that its elaboration admits:
    [True] or [False] is ValueSoft; [] is a conflict (no value)."""
    penv = python_env(row)
    premise = next(p["ast"] for p in row["premises"] if p["label"] == f"layer:norms:{predicate}")
    out = []
    for value in (True, False):
        relations = {p: [] for p in penv.predicates if p not in ("x_required", "x_permitted")}
        relations.update({p: [["a"]] for p in decisions})
        relations[predicate] = [["a"]] if value else []
        # the other member of the pair, chosen to satisfy the profile premise r ⊆ m (the
        # elaboration of `predicate` never reads it)
        if predicate == "x_required":
            relations["x_permitted"] = [["a"]]
        else:
            relations["x_required"] = []
        model = FiniteModel.from_dict(penv, {"complete": True,
                                             "domains": {"assistant": ["a"], "user": []},
                                             "constants": {}, "relations": relations})
        if evaluate(penv, formula_from_data(penv, premise), model, trace=False).value:
            out.append(value)
    return out


def test_alpha_holistic_override_one_winner(lean):
    row = elaborate(lean, env(ranks(["a", "b"], "holistic")),
                    [should("h", "x_required", True, rank="a"), should("l", "x_required", False, rank="b")])
    assert [d["name"] for d in row["decisions"]] == [
        "soft__excepted__h", "soft__excepted__l", "soft__outweighs__b__a__x_permitted"]
    assert values(row, "x_required", ["soft__outweighs__b__a__x_permitted"]) == [False]
    assert values(row, "x_required", []) == [True]
    assert [(p["pair"], p["comparable"]) for p in row["colliding_pairs"]] == [(["h", "l"], True)]
    assert row["conditional_on"] == []


def test_epsilon_alternating_cycle_d_alone_effective(lean):
    names = ["ra", "rb", "rc", "rd"]
    rules = [should("a", "x_required", True, rank="ra"), should("b", "x_required", False, rank="rb"),
             should("c", "x_required", True, rank="rc"), should("d", "x_required", False, rank="rd")]
    row = elaborate(lean, env(ranks(names, "holistic")), rules)
    found = ["soft__outweighs__rb__ra__x_permitted", "soft__outweighs__rc__rb__x_permitted",
             "soft__outweighs__rd__rc__x_permitted"]
    assert values(row, "x_required", found) == [False]
    assert {tuple(p["pair"]) for p in row["colliding_pairs"]} == {("a", "b"), ("a", "d"), ("b", "c"), ("c", "d")}
    assert all(p["comparable"] for p in row["colliding_pairs"])


def test_kappa_defeated_higher_rule_does_not_dominate(lean):
    rules = [should("a", "x_required", True, rank="ra"), should("b", "x_permitted", False, rank="rb"),
             should("c", "x_permitted", True, rank="rc")]
    row = elaborate(lean, env(ranks(["ra", "rb", "rc"]), perm="deny"), rules)
    assert values(row, "x_required", []) == [True]
    assert values(row, "x_permitted", []) == [True]


def test_lambda_blocked_dominator(lean):
    rules = [norm("s", "x_required", False), should("hi", "x_required", True, rank="high"),
             should("lo", "x_permitted", False, rank="low")]
    row = elaborate(lean, env(ranks(["high", "low"]), perm="allow"), rules)
    assert values(row, "x_required", []) == [False]
    assert values(row, "x_permitted", []) == [False]


def test_mu_switchable_strict_exception_changes_hard_parent(lean):
    rules = [norm("h", "x_required", True), norm("e", "x_required", False, over=["h"], alterable=["user"])]
    row = elaborate(lean, env({"parties": ["user"], "outranking": {"mode": "strict"}}), rules)
    assert [d["name"] for d in row["decisions"]] == ["soft__off__e__user"]
    assert values(row, "x_required", []) == [False]
    assert values(row, "x_required", ["soft__off__e__user"]) == [True]
    derived = {d["rule"]: d["ast"] for d in row["derived"]}
    assert derived["h"] is None and derived["e"] is not None


def test_upsilon_yield_through_dominated_rule(lean):
    rules = [should("m", "x_required", True, rank="high"), should("n", "x_required", False, rank="low", over=["m"]),
             should("k", "x_required", False, over=["n"])]
    row = elaborate(lean, env(ranks(["high", "low"])), rules)
    assert values(row, "x_required", []) == [False]
    assert "RankAgainstPrecedence: rule n over m" in row["warnings"]
    rules[1]["norm"]["over"] = []
    row = elaborate(lean, env(ranks(["high", "low"])), rules)
    assert values(row, "x_required", []) == []


def test_eta_default_rule_with_unless_and_exception(lean):
    u = {"u": {"arguments": ["assistant"], "description": "u"}}
    rules = [should("r", "x_required", True, unless=[("unary", "u", ["var", 0])])]
    row = elaborate(lean, env(extra=u), rules)
    assert values(row, "x_required", []) == [True]
    assert values(row, "x_required", ["u"]) == [False]
    assert values(row, "x_required", ["soft__excepted__r"]) == [False]


def test_xi_all_hard_documents_elaborate_to_themselves(lean):
    row = elaborate(lean, env(), [norm("m", "x_required", True), norm("p", "x_permitted", True)])
    assert row["decisions"] == [] and row["colliding_pairs"] == []
    assert all(d["ast"] is None for d in row["derived"])
    assert not any(b["generator"] == "soft" for b in row["background"])


def test_nu_outweighs_indexed_by_act_and_sorts(lean):
    extra = {"y_required": obligation("deny", "y_permitted", act="{0} do y to {1}", args=("assistant", "user")),
             "y_permitted": permission("allow", act="{0} do y to {1}", args=("assistant", "user"))}
    rules = [should("xh", "x_required", True, rank="h"), should("xl", "x_required", False, rank="l"),
             should("yh", "y_required", True, rank="h"), should("yl", "y_required", False, rank="l")]
    row = elaborate(lean, env(ranks(["h", "l"], "holistic"), extra=extra), rules)
    outweighs = {d["name"]: d["arguments"] for d in row["decisions"] if "outweighs" in d["name"]}
    assert outweighs == {"soft__outweighs__l__h__x_permitted": ["assistant"],
                         "soft__outweighs__l__h__y_permitted": ["assistant", "user"]}


@pytest.mark.parametrize("environment_json,norms,expected", [
    (env(ranks(["a", "b"]) | {"ties": [["a", "b"]]}), [], "TieAgainstOrder: a, b"),
    (env({"ranks": ["a", "b", "c"], "outranks": [["a", "b"], ["b", "c"], ["c", "a"]],
          "outranking": {"mode": "strict"}}), [], "DependencyCycle: a, b, c"),
    (env(), [norm("m", "x_required", True), should("d", "x_required", False, over=["m"])],
     "SoftOverHard: rule d over m"),
    (env({"parties": ["user"], "outranking": {"mode": "strict"}}),
     [norm("m", "x_required", True, alterable=["user"], hard=True)], "HardConstraintAltered: rule m"),
    # `decided_by: null` (inherit) is sent as an absent key: the frozen restricted JSON
    # parser of the Lean executables admits no null
    (env(), [norm("m", "x_required", True, mode="default", exception={})],
     "MissingExceptionDecider: rule m"),
    (env({"ranks": [], "outranking": {"mode": "holistic"}}), [], "MissingExceptionDecider: outranking"),
    (env(), [should("m", "x_required", True, exception={**DECIDER, "sufficient": [["unary", "x_permitted", ["var", 0]]]})],
     "InvalidInput: exception condition of rule m mentions x_permitted"),
    (env(), [should("m", "x_required", True, rank="nope")], "UnknownRank: rule m, nope"),
    (env(profiles=("soft-norms@0",)), [], "UnsupportedProfile: soft-norms@0 requires norms@0"),
    (env(ranks(["a"]), profiles=()), [], "UnsupportedProfile: soft-norms@0 is required"),
])
def test_theta_sigma_pi_rho_diagnostics(lean, environment_json, norms, expected):
    row = run(lean, [{"id": "d", "kind": "soft-elaborate", "environment": environment_json, "norms": norms}])[0]
    assert row["status"] == "error" and row["error"] == expected


def model(relations):
    return {"complete": True, "domains": {"assistant": ["a"], "user": []}, "constants": {},
            "relations": relations}


def test_gamma_completion_conflict_and_delta_weighing_point(lean):
    gamma = [should("s", "x_required", True)]
    witness = {"target": "x_required->x_permitted", "model": model({"soft__excepted__s": []}), "tuple": ["a"]}
    delta = [should("a", "x_required", True), should("b", "x_permitted", False)]
    both_false = model({"soft__excepted__a": [], "soft__excepted__b": []})
    rows = run(lean, [
        {"id": "g", "kind": "soft-conflict", "environment": env(perm="deny"), "norms": gamma, "witness": witness},
        {"id": "g2", "kind": "soft-conflict", "environment": env(perm="allow"), "norms": gamma, "witness": witness},
        {"id": "d", "kind": "soft-pairs", "environment": env(), "norms": delta,
         "pairs": {"soft:coherence:a,b": {"witness": {"model": both_false, "tuple": ["a"]}}}},
        {"id": "d2", "kind": "soft-conflict", "environment": env(), "norms": delta,
         "witness": {"target": "x_required->x_permitted", "model": both_false, "tuple": ["a"]}},
        {"id": "d3", "kind": "soft-pairs", "environment": env(ranks(["hi", "lo"])),
         "norms": [should("a", "x_required", True, rank="hi"), should("b", "x_permitted", False, rank="lo")],
         "pairs": {}},
    ])
    assert rows[0]["verdict"] == "CONFLICT"
    assert rows[0]["witness_kind"] == "pair conflict on x_required->x_permitted"
    assert rows[1]["verdict"] == "UNKNOWN"
    assert rows[2]["pairs"][0]["status"] == "WEIGHING POINT"
    assert rows[2]["weighing_points"] == ["soft:coherence:a,b"]
    # the same witness violates Coh_T, so it is no countermodel to the conditional claim
    assert rows[3]["status"] == "error" and rows[3]["error"].startswith("InvalidModel(soft background)")
    assert rows[4]["pairs"][0]["status"] == "RANK-RESOLVED" and rows[4]["weighing_points"] == []


def test_w1_inputs_delegate_unchanged(lean):
    raw = env(profiles=())
    raw["profiles"] = ["norms@0", "relational-fol@0"]
    case = {"id": "w1", "kind": "norms-elaborate", "environment": raw, "norms": [norm("m", "x_required", True)]}
    soft = run(lean, [case])[0]
    w1 = run(ROOT / "lean/.lake/build/bin/ve_norms_route", [case])[0]
    assert soft == w1


# End-to-end CONFLICT-FREE replay: certificates found by Python's unchanged prover over the
# Lean-regenerated E′_base and Background_base′, packaged with the bindings of 3.4.

def identity(profiles):
    return "v0.2:" + ",".join(profiles)


def canonical_norm(n):
    defaults = {"mode": "strict", "alterable": [], "hard": False}
    return {"norm": {k: v for k, v in n["norm"].items() if defaults.get(k, object()) != v}}


def base_prime(row):
    data = json.loads(json.dumps(row["environment_prime"]))
    data["profiles"] = [p for p in data["profiles"] if p not in ("norms@0", "soft-norms@0")]
    vocab = data["vocabulary"]
    vocab.pop("soft", None)
    vocab["predicates"] = {n: {k: v for k, v in e.items() if k != "instruction_of"}
                           for n, e in vocab["predicates"].items() if "regulated" not in e}
    return Environment(data)


def packages(environment_json, norms, row, *, soft=True):
    profiles = environment_json["profiles"]
    env_id = digest(f"ve-environment-{identity(profiles)}\n", environment_json)
    doc_hash = digest(f"ve-soft-norms-{identity(profiles)}\n",
                      {"environment_id": env_id, "document": [canonical_norm(n) for n in norms]})
    base = base_prime(row)
    premises = [formula_from_data(base, b["ast"]) for b in row["background"] if soft and b["generator"] == "soft"]
    out = {}
    for t in row["conflict_targets"]:
        closed = ["not", t["ast"]]
        for sort in reversed(t["sorts"]):
            closed = ["forall", sort, closed]
        conclusion = formula_from_data(base, closed)
        result = prove_entailment(base, premises, conclusion)
        if result.status == "Found":
            out[t["target"]] = {"environment_id": env_id, "document_hash": doc_hash,
                                "target": t["target"], "certificate": result.certificate}
    return out


def test_delta_conflict_free_conditional_on_coherence(lean):
    environment_json = env()
    delta = [should("a", "x_required", True), should("b", "x_permitted", False)]
    row = elaborate(lean, environment_json, delta)
    certified = packages(environment_json, delta, row)
    assert set(certified) == {t["target"] for t in row["conflict_targets"]}
    verdict = run(lean, [{"id": "c", "kind": "soft-conflict", "environment": environment_json,
                          "norms": delta, "packages": certified}])[0]
    assert verdict["verdict"] == "CONFLICT-FREE", verdict
    assert verdict["conditional_on"] == ["soft:coherence:a,b"]
    # without Coh_T the pair target has no certificate, and no other certificate binds
    bare = packages(environment_json, delta, row, soft=False)
    assert "x_required->x_permitted" not in bare
    verdict = run(lean, [{"id": "c", "kind": "soft-conflict", "environment": environment_json,
                          "norms": delta, "packages": {**certified, **bare}}])[0]
    assert verdict["verdict"] == "UNKNOWN"


def test_alpha_rank_resolved_conflict_free_unconditionally(lean):
    environment_json = env(ranks(["a", "b"], "holistic"))
    alpha = [should("h", "x_required", True, rank="a"), should("l", "x_required", False, rank="b")]
    row = elaborate(lean, environment_json, alpha)
    certified = packages(environment_json, alpha, row)
    verdict = run(lean, [{"id": "c", "kind": "soft-conflict", "environment": environment_json,
                          "norms": alpha, "packages": certified}])[0]
    assert verdict["verdict"] == "CONFLICT-FREE" and verdict["conditional_on"] == []


def test_theta_dual_guard_cycle_on_t_prime(lean):
    not_required = ("not", ["unary", "x_required", ["var", 0]])
    not_permitted = ("not", ["unary", "x_permitted", ["var", 0]])
    rows = run(lean, [
        {"id": "1", "kind": "soft-elaborate", "environment": env(),
         "norms": [norm("s", "x_permitted", False, guard=not_required), should("d", "x_required", True)]},
        {"id": "2", "kind": "soft-elaborate", "environment": env(),
         "norms": [norm("s", "x_required", True, guard=not_permitted), should("d", "x_permitted", False)]},
        {"id": "3", "kind": "soft-elaborate", "environment": env(),
         "norms": [norm("s", "x_permitted", True, guard=not_required), should("d", "x_required", True)]},
        {"id": "4", "kind": "soft-elaborate", "environment": env(),
         "norms": [norm("s", "x_permitted", False, guard=not_required), norm("d", "x_required", True)]},
    ])
    # the shared dependencyOrder diagnostic names every node that cannot be placed: the
    # self-edge is on the defaulted predicate, and the strict rule's predicate depends on it
    # (spec fixture θ writes only the first name; see lean/SOFT-NORMS.md)
    assert rows[0]["error"] == "DependencyCycle: x_permitted, x_required"
    assert rows[1]["error"] == "DependencyCycle: x_permitted, x_required"
    assert rows[2]["status"] == "ok" and rows[3]["status"] == "ok"
