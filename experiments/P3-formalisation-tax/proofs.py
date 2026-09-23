"""Prove/countermodel arm: property-level questions a reviewer would ask about an
artefact, answered with VE's entailment checker (certificate replayed) or its
finite countermodel search, and cross-checked against the reference.

Each task: premises and conclusion in VE strict syntax over the item's
environment (optionally extended with extra constants/predicates), the
expected verdict from the reference, and how the reference verdict was obtained:
  * Cedar/K8s: the property is an implication about the authorizer's decision;
    the reference samples perturbed worlds (harness.perturbations) and looks for
    a counterexample (sampling can refute, never prove), or reads a recorded decision.
  * Alloy: exhaustive enumeration of all graphs on <= 3 nodes with the Alloy
    reference evaluator (a bounded check, as the Alloy Analyzer would do).

Writes proof_results.json.
"""
from __future__ import annotations

import itertools
import json
import time

import harness as H
from ve import Environment, find_countermodel, parse, prove_entailment
from ve.entailment import check_entailment_certificate


def env_with(item_id, constants=None, predicates=None):
    wire = json.loads((H.ITEMS / item_id / "environment.json").read_text())
    for k, s in (constants or {}).items():
        wire["vocabulary"]["constants"][k] = {"sort": s, "description": "Added for a proof task."}
    for k, a in (predicates or {}).items():
        wire["vocabulary"]["predicates"][k] = {"arguments": a, "description": "Added for a proof task."}
    return Environment.from_json(json.dumps(wire).encode())


def formalisation(item_id):
    return (H.ITEMS / item_id / "formalisation.ve").read_text().splitlines()[0].rstrip(".")


# ------------------------------------------------------------- reference sides

def cedar_sampled(item_id, antecedent, consequent, n=300):
    """Search sampled worlds for: reference allows, antecedent(world, req) holds, consequent fails."""
    import reference
    item = H.load_item(item_id)
    hits = 0
    for p in H.perturbations(item, n):
        if reference.answer(item, {}, p["world"], p["request"]) and antecedent(p["world"], p["request"]):
            hits += 1
            if not consequent(p["world"], p["request"]):
                return {"verdict": False, "method": f"sampled {n} perturbed worlds: counterexample found", "support": hits}
    return {"verdict": True, "method": f"sampled {n} perturbed worlds: no counterexample ({hits} allowed worlds met the antecedent)",
            "support": hits}


def c13_private_view(schema_valid: bool, n=400):
    """Force the antecedent (action ViewDocument on a document with isPrivate = true) on
    perturbed worlds; schema_valid keeps the schema's guarantees (documents have an owner,
    actions have no parents)."""
    import random
    import reference
    item = H.load_item("c13_document_cloud")
    rng = random.Random("c13-private")
    hits = 0
    for p in H.perturbations(item, n):
        w, r = p["world"], dict(p["request"])
        docs = [e for e in w["entities"] if e["uid"].startswith("Document::")]
        if not docs:
            continue
        d = rng.choice(docs)
        d["attrs"]["isPrivate"] = True
        r["action"], r["resource"] = 'Action::"ViewDocument"', d["uid"]
        if schema_valid:
            if not isinstance(d["attrs"].get("owner"), dict):
                d["attrs"]["owner"] = {"__entity": 'User::"alice"'}
            for e in w["entities"]:
                if e["uid"].startswith("Action::"):
                    e["parents"] = []
        if reference.answer(item, {}, w, r):
            hits += 1
            if not probe("permit(principal, action, resource) when { resource.owner == principal };")(w, r):
                return {"verdict": False, "method": f"{n} perturbed worlds forced to the antecedent"
                        f"{' (schema-valid)' if schema_valid else ' (arbitrary stores)'}: counterexample found", "support": hits}
    return {"verdict": True, "method": f"{n} perturbed worlds forced to the antecedent"
            f"{' (schema-valid)' if schema_valid else ' (arbitrary stores)'}: no counterexample", "support": hits}


def probe(policy_text):
    """A consequent evaluated by the Cedar reference: does this one-policy set allow the request?"""
    import reference_cedar
    return lambda w, r: reference_cedar.authorize(policy_text, [], w["entities"], r)


def attr(uid_key, name):
    def get(w, r):
        e = next((e for e in w["entities"] if e["uid"] == r[uid_key]), None)
        return None if e is None else e["attrs"].get(name)
    return get


def alloy_enumerated(src_item, pred_a, pred_b, max_nodes=3):
    """All graphs on 0..max_nodes nodes: does pred_a imply pred_b (reference_alloy)?"""
    import reference_alloy
    item = H.load_item(src_item)
    src = {k: v for k, v in item["sources"].items() if k.endswith(".als")}
    count = 0
    for n in range(max_nodes + 1):
        nodes = [f"n{i}" for i in range(n)]
        pairs = [[x, y] for x in nodes for y in nodes]
        for bits in itertools.product([0, 1], repeat=len(pairs)):
            inst = {"sigs": {"node": nodes}, "fields": {"edges": [p for p, b in zip(pairs, bits) if b]}, "bindings": {"r": "edges"}}
            count += 1
            a = reference_alloy.evaluate(src, {"kind": "pred", "name": pred_a, "args": ["r"]}, inst)
            if a and not reference_alloy.evaluate(src, {"kind": "pred", "name": pred_b, "args": ["r"]}, inst):
                return {"verdict": False, "method": f"exhaustive, graphs with <= {max_nodes} nodes: counterexample {inst['fields']['edges']}"}
    return {"verdict": True, "method": f"exhaustive, all {count} graphs with <= {max_nodes} nodes"}


# -------------------------------------------------------------------- tasks

def tasks():
    T = []
    f = formalisation
    T.append(dict(id="c02-only-group-members", item="c02_cit_2a",
        question="Can anyone outside UserGroup jane_friends (transitively) be allowed?",
        premises=[f("c02_cit_2a")], conclusion="rtc[parent](@principal, @jane_friends)",
        reference=lambda: cedar_sampled("c02_cit_2a", lambda w, r: True,
                                        probe('permit(principal in UserGroup::"jane_friends", action, resource);'))))
    T.append(dict(id="c03-only-photo94", item="c03_cit_2b",
        question="Is VacationPhoto94.jpg the only resource Alice may view? (expected: no)",
        premises=[f("c03_cit_2b")], conclusion="@resource equals @photo94", env_constants={"photo94": "entity"},
        reference=lambda: cedar_sampled("c03_cit_2b", lambda w, r: True,
                                        probe('permit(principal, action, resource == Photo::"VacationPhoto94.jpg");'))))
    c13_q = "Is a private document viewable only by its owner?"
    c13_prem = [f("c13_document_cloud"), "@action equals @view_document", "@resource is bt_isprivate"]
    T.append(dict(id="c13-private-owner-only-raw", item="c13_document_cloud", question=c13_q + " (no background axioms)",
        premises=c13_prem, conclusion="@resource ea_owner @principal",
        reference=lambda: c13_private_view(schema_valid=False)))
    acts = ["create_document", "modify_document", "edit_is_private", "add_to_share_acl", "edit_public_access",
            "create_group", "modify_group", "delete_group", "delete_document"]
    schema_axioms = ["for every entity x, (not ((x is bt_isprivate) and (x is bf_isprivate)))",
                     "for every entity x, (not (@view_document parent x))",
                     "there exists entity o, (@resource ea_owner o)",
                     "for every entity x, (for every entity y, (if ((@resource ea_owner x) and (@resource ea_owner y)), then (x equals y)))",
                     *[f"not (@view_document equals @{x})" for x in acts]]
    T.append(dict(id="c13-private-owner-only-schema-axioms", item="c13_document_cloud",
        question=c13_q + " (with schema axioms: distinct action UIDs, actions have no parents, owner present and unique, Boolean exclusivity)",
        premises=c13_prem + schema_axioms, conclusion="@resource ea_owner @principal",
        reference=lambda: c13_private_view(schema_valid=True)))
    # bob push secret: bob -> tiny_corp_owners -> secret_admins -> secret_maintainers -> secret_writers = secret.writers
    chain = ["@principal parent @g1", "@g1 parent @g2", "@g2 parent @g3", "@g3 parent @g4",
             "@resource ea_writers @g4", "@action equals @push"]
    T.append(dict(id="c14-bob-push-by-chain", item="c14_github",
        question="From the recorded group chain (4 parent edges), is the push allowed? (open-world proof, not evaluation)",
        premises=chain, conclusion=f("c14_github"), env_constants={"g1": "entity", "g2": "entity", "g3": "entity", "g4": "entity"},
        reference=lambda: {"verdict": True, "method": "recorded Cedar decision ALLOW/query_bob_push_secret.json and the reference on the item store"}))
    # k05: ana bound to admin in team-a gets crontabs through view -> edit -> admin aggregation (3 levels)
    k = ["@bind0 is is_rolebinding", "@bind0 binding_ns @ns0", "@bind0 subject_user @user", "@bind0 is ref_clusterrole", "@bind0 ref_name @n_admin",
         "@admin is is_clusterrole", "@admin role_name @n_admin", "@admin is has_aggregation", "@admin role_selector @q_admin",
         "for every str l, (if (@q_admin sel_label l), then (l equals @l_admin))",
         "@edit is is_clusterrole", "@edit is has_aggregation", "@edit role_label @l_admin", "@edit role_selector @q_edit",
         "for every str l, (if (@q_edit sel_label l), then (l equals @l_edit))",
         "@view is is_clusterrole", "@view is has_aggregation", "@view role_label @l_edit", "@view role_selector @q_view",
         "for every str l, (if (@q_view sel_label l), then (l equals @l_view))",
         "@cron is is_clusterrole", "@cron role_label @l_view", "not (@cron is has_aggregation)", "@cron role_rule @rule0",
         "@rule0 rule_verb @verb", "@rule0 rule_group @apigroup", "@rule0 rule_resource @path", "not (there exists str k, (@rule0 rule_resname k))",
         "@namespace equals @ns0"]
    T.append(dict(id="k05-admin-gets-view-rule-3-levels", item="k05_crontab_default_roles",
        question="Does a user bound to admin get a rule aggregated only into view (view -> edit -> admin)?",
        premises=k, conclusion=f("k05_crontab_default_roles"),
        env_constants={"bind0": "binding", "ns0": "str", "n_admin": "str", "admin": "role", "edit": "role", "view": "role", "cron": "role",
                       "q_admin": "sel", "q_edit": "sel", "q_view": "sel", "l_admin": "str", "l_edit": "str", "l_view": "str", "rule0": "rule"},
        reference=lambda: {"verdict": True, "method": "reference_rbac on the item world with cron-tabs-edit's aggregate-to-admin/edit labels removed (view-only path)",
                           **k05_view_only()}))
    T.append(dict(id="l03-noselfgrandpa", item="l03_grandpa1_noselfgrandpa",
        question="check NoSelfGrandpa (grandpa1.als): do the facts entail the assertion?",
        premises=[(H.ITEMS / "l03_grandpa1_noselfgrandpa" / "formalisation.ve").read_text().splitlines()[1].rstrip(".")],
        conclusion=(H.ITEMS / "l03_grandpa1_noselfgrandpa" / "formalisation.ve").read_text().splitlines()[0].rstrip("."),
        reference=lambda: {"verdict": __import__("reference_alloy").evaluate(
            {"source.als": H.load_item("l03_grandpa1_noselfgrandpa")["sources"]["source.als"]},
            {"kind": "check", "name": "NoSelfGrandpa", "scope": 3}, None), "method": "reference bounded check, scope 3"}))
    ring, weak, tree = f("l05_graph_ring"), f("l04_graph_weakly_connected"), f("l06_graph_tree")
    T.append(dict(id="l-ring-implies-weakly-connected", item="l05_graph_ring",
        question="util/graph: does ring[r] imply weaklyConnected[r]? (valid in all structures; needs closure monotonicity)",
        premises=[ring], conclusion=weak, reference=lambda: alloy_enumerated("l05_graph_ring", "ring", "weaklyConnected")))
    T.append(dict(id="l-tree-implies-weakly-connected", item="l06_graph_tree",
        question="util/graph: does tree[r] imply weaklyConnected[r]? (true for finite graphs only)",
        premises=[tree], conclusion=weak, reference=lambda: alloy_enumerated("l06_graph_tree", "tree", "weaklyConnected")))
    typing = "for every atom x, (for every atom y, (if (x f_edges y), then ((x is sig_node) and (y is sig_node))))"
    T.append(dict(id="l-tree-implies-weakly-connected-typed", item="l06_graph_tree",
        question="Same, adding the Alloy typing r: node->node as a premise",
        premises=[tree, typing], conclusion=weak, reference_same_as="l-tree-implies-weakly-connected"))
    T.append(dict(id="l-ring-implies-weakly-connected-typed", item="l05_graph_ring",
        question="ring => weaklyConnected with the typing premise",
        premises=[ring, typing], conclusion=weak, reference_same_as="l-ring-implies-weakly-connected"))
    T.append(dict(id="l-weakly-connected-implies-ring", item="l04_graph_weakly_connected",
        question="util/graph: does weaklyConnected[r] imply ring[r]? (expected: no)",
        premises=[weak], conclusion=ring, reference=lambda: alloy_enumerated("l04_graph_weakly_connected", "weaklyConnected", "ring")))
    return T


def k05_view_only():
    import copy
    import reference_rbac
    item = H.load_item("k05_crontab_default_roles")
    w = copy.deepcopy(item["world"])
    for o in w["objects"]:
        if o["metadata"]["name"] == "aggregate-cron-tabs-edit":
            o["metadata"]["labels"] = {}
    req = item["questions"][0]["request"]
    return {"reference_answer_view_only_world": reference_rbac.k8s_authorize(w["objects"], req)}


def run(task):
    item = task["item"]
    env = env_with(item, task.get("env_constants"), task.get("env_predicates"))
    prem = [parse(env, (p + ".\n").encode()).formulas[0] for p in task["premises"]]
    concl = parse(env, (task["conclusion"] + ".\n").encode()).formulas[0]
    t0 = time.time()
    pr = prove_entailment(env, prem, concl, max_steps=50000)
    out = {"prove": pr.status, "prove_steps": pr.steps, "prove_seconds": round(time.time() - t0, 2)}
    if pr.status == "Found":
        chk = check_entailment_certificate(env, prem, concl, pr.certificate, max_steps=50000)
        out["certificate_replayed"] = chk.valid
        out["ve_verdict"] = True
    else:
        t1 = time.time()
        cm = find_countermodel(env, prem, concl, max_domain_size=3, max_models=200000)
        out.update({"countermodel": cm.status, "countermodel_seconds": round(time.time() - t1, 2)})
        out["ve_verdict"] = False if cm.status == "Found" else None
        if cm.status == "Found":
            mdl = cm.model
            out["countermodel_model"] = {"domains": {k: list(v) for k, v in mdl.domains.items()},
                                         "constants": dict(mdl.constants),
                                         "relations": {k: sorted(map(list, v)) for k, v in mdl.relations.items() if v}}
    return out


if __name__ == "__main__":
    results, refs = [], {}
    for t in tasks():
        ref = refs[t["reference_same_as"]] if "reference_same_as" in t else t["reference"]()
        refs[t["id"]] = ref
        r = run(t)
        row = {"id": t["id"], "item": t["item"], "question": t["question"], **r, "reference": ref,
               "agrees": r["ve_verdict"] == ref.get("verdict") if r["ve_verdict"] is not None else None}
        results.append(row)
        print(json.dumps({k: row[k] for k in row if k not in ("countermodel_model", "question")})[:400], flush=True)
    (H.HERE / "proof_results.json").write_text(json.dumps(results, indent=1, default=str) + "\n")
