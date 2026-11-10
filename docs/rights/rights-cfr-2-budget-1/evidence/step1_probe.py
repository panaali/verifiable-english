"""Step 1 probe (rights-cfr-2-budget-1): one CONFLICT-FREE fixture, no situation, through both routes."""
import json, sys
sys.path.insert(0, "/home/seyran/code/ve-rights-cfr-2-budget-1")
sys.path.insert(0, "/home/seyran/code/ve-rights-cfr-2-budget-1/tests")
from tests import test_rights_lean as R, test_soft_norms_lean as S
from tests.test_rights_report_parts import WEIGHED, _weighed
from ve import rights_route

DEC = dict(S.DECIDER)
NOT_ARB = ["not", R.ARBITRARY]
def dflt(name, pred, sign, **kw):
    return R.norm(name, pred, sign, mode="default", exception=dict(DEC), **kw)

environment_json = R.env(R.ARREST)
soft_env = json.loads(json.dumps(environment_json)); soft_env["profiles"] = [x for x in soft_env["profiles"] if x != "rights@0"]; soft_env["vocabulary"].pop("rights")
cases = {
    # the soft part of WEIGHED: an unranked default pair on arrest_permitted
    "plain": [dflt("no-arbitrary-arrest", "arrest_permitted", False, guard=R.ARBITRARY),
              dflt("may-detain", "arrest_permitted", True)],
    # the same pair with disjoint guards: the pair target holds without its coherence premise
    "disjoint": [dflt("no-arbitrary-arrest", "arrest_permitted", False, guard=R.ARBITRARY),
                 dflt("may-detain", "arrest_permitted", True, guard=NOT_ARB)],
}
for tag, norms in cases.items():
    soft_doc = [{"norm": n} for n in norms]
    rights_doc = [R.right("r9", [R.line("claim", norms[0])]), {"norm": norms[1]}]
    srow = S.elaborate(R.SOFT, soft_env, soft_doc)
    sp = S.packages(soft_env, soft_doc, srow)
    soft = S.run(R.SOFT, [{"id": "s", "kind": "soft-conflict", "environment": soft_env,
                           "norms": soft_doc, "packages": sp}])[0]
    rrow = R.elaborate(R.LEAN, environment_json, rights_doc)
    rp = R.packages(environment_json, rights_doc, rrow)
    rights = R.run(R.LEAN, [{"id": "r", "kind": "rights-conflict", "environment": environment_json,
                             "document": rights_doc, "packages": rp}])[0]
    print(tag, "SOFT  :", soft.get("verdict"), "|", soft.get("status_text"), "| conditional_on", soft.get("conditional_on"))
    print(tag, "RIGHTS:", rights.get("verdict"), "|", rights.get("status_text"), "| weighing_points", rights.get("weighing_points"))
env_, certified, _ = _weighed()
row = rights_route.run_rights_case(env_, WEIGHED, "rights-conflict", packages=certified)
print("WEIGHED RIGHTS (relayed):", row["status_text"])

# disjoint guards, certificates proved without the soft (coherence) background
from tests.test_rights_lean import base_prime as rbase, canonical_unit, identity, digest, formula_from_data, prove_entailment
def rights_packages_nosoft(environment_json, document, row):
    profiles = environment_json["profiles"]
    env_id = digest(f"ve-environment-{identity(profiles)}\n", environment_json)
    doc_hash = digest(f"ve-rights-{identity(profiles)}\n",
                      {"environment_id": env_id, "document": [canonical_unit(u) for u in document]})
    base_env = rbase(row)
    premises = [formula_from_data(base_env, b["ast"]) for b in row["rights_background"]]
    out = {}
    for t in row["conflict_targets"]:
        closed = ["not", t["ast"]]
        for sort in reversed(t["sorts"]):
            closed = ["forall", sort, closed]
        result = prove_entailment(base_env, premises, formula_from_data(base_env, closed))
        if result.status == "Found":
            out[t["target"]] = {"environment_id": env_id, "document_hash": doc_hash,
                                "target": t["target"], "certificate": result.certificate}
    return out
norms = cases["disjoint"]
soft_doc = [{"norm": n} for n in norms]
rights_doc = [R.right("r9", [R.line("claim", norms[0])]), {"norm": norms[1]}]
srow = S.elaborate(R.SOFT, soft_env, soft_doc)
sp = S.packages(soft_env, soft_doc, srow, soft=False)
soft = S.run(R.SOFT, [{"id": "s", "kind": "soft-conflict", "environment": soft_env, "norms": soft_doc, "packages": sp}])[0]
rrow = R.elaborate(R.LEAN, environment_json, rights_doc)
rp = rights_packages_nosoft(environment_json, rights_doc, rrow)
rights = R.run(R.LEAN, [{"id": "r", "kind": "rights-conflict", "environment": environment_json, "document": rights_doc, "packages": rp}])[0]
print("nosoft SOFT  :", soft.get("verdict"), "|", soft.get("status_text"), "|", soft.get("conditional_on"), sorted(sp))
print("nosoft RIGHTS:", rights.get("verdict"), "|", rights.get("status_text"), "|", rights.get("weighing_points"), sorted(rp))
