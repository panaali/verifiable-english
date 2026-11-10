import json, sys
sys.path.insert(0, "/home/seyran/code/ve-rights-cfr-2-budget-1"); sys.path.insert(0, "/home/seyran/code/ve-rights-cfr-2-budget-1/tests")
from tests import test_rights_lean as R, test_soft_norms_lean as S
DEC = dict(S.DECIDER)
def dflt(name, pred, sign, **kw): return R.norm(name, pred, sign, mode="default", exception=dict(DEC), **kw)
environment_json = R.env(R.ARREST)
soft_env = json.loads(json.dumps(environment_json)); soft_env["profiles"] = [x for x in soft_env["profiles"] if x != "rights@0"]; soft_env["vocabulary"].pop("rights")
cases = {"bottom": [dflt("no-arbitrary-arrest", "arrest_permitted", False, guard=("bottom",)), dflt("may-detain", "arrest_permitted", True)],
         "two-acts-bottom": [dflt("no-arbitrary-arrest", "arrest_permitted", False, guard=("bottom",)), dflt("may-detain", "arrest_permitted", True), dflt("may-hold", "arrest_permitted", True)],
         "contra": [dflt("no-arbitrary-arrest", "arrest_permitted", False, guard=("and", R.ARBITRARY, ["not", R.ARBITRARY])), dflt("may-detain", "arrest_permitted", True)]}
for tag, norms in cases.items():
    soft_doc = [{"norm": n} for n in norms]
    try:
        srow = S.elaborate(R.SOFT, soft_env, soft_doc)
    except AssertionError as e:
        print(tag, "elab", e); continue
    sp = S.packages(soft_env, soft_doc, srow)
    soft = S.run(R.SOFT, [{"id": "s", "kind": "soft-conflict", "environment": soft_env, "norms": soft_doc, "packages": sp}])[0]
    print(tag, "colliding", [p.get("label") for p in srow.get("colliding_pairs", [])], "SOFT:", soft.get("error") or soft.get("status_text"))
