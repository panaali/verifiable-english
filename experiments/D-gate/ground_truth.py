"""D-gate ground truth from named reference verifiers (no model calls, no network).

    CEDAR=/path/to/cedar CVC5=/path/to/cvc5 UV_CACHE_DIR=/private/tmp/ve-uv-cache-dgate \
        uv run --project solvers --locked python ground_truth.py

Cedar items: Cedar SymCC, source-native (`cedar symcc ... implies`, cedar-policy-cli 4.13.0 built
with `--features analyze`, cvc5 1.4.0). SymCC is a sound and complete encoding of Cedar semantics
(including errors, extension types, entity hierarchy) for one request environment (principal type,
action, resource type) over all schema-valid entity stores; the script runs one query per
environment the item lists. `only_if`: implies(artefact, property); `if`: implies(property,
artefact). YES iff every query HOLDS. Any query that errors (e.g. an ill-typed property) or times
out makes the item UNDECIDED; nothing is guessed.

K8s items: Z3 (z3-solver 5.1.0, strings) over a direct encoding of the RBAC authorizer written for
this script (it does not import P3's encoding or VE). YES iff the property's negation is unsat.
Every K8s counterexample is replayed through P3's independent reference authorizer
(experiments/P3-formalisation-tax/reference_rbac.py) as a cross-check.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CEDAR = os.environ.get("CEDAR", "cedar")
TIMEOUT_S = 120


def cedar_version():
    return subprocess.run([CEDAR, "--version"], capture_output=True, text=True).stdout.strip()


def cvc5_version():
    cv = os.environ.get("CVC5")
    if not cv:
        return None
    return subprocess.run([cv, "--version"], capture_output=True, text=True).stdout.splitlines()[0]


def symcc_implies(schema, env, p1, p2):
    principal, action, resource = env
    cmd = [CEDAR, "symcc", "--principal-type", principal, "--action", action, "--resource-type", resource,
           "-s", str(schema), "--counterexample", "implies", "--policies1", str(p1), "--policies2", str(p2)]
    t = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return dict(env=env, result="timeout", seconds=TIMEOUT_S)
    out = (r.stdout + r.stderr).strip()
    first = out.splitlines()[0] if out else ""
    if "DOES NOT HOLD" in first:
        res = "does_not_hold"
    elif first.startswith("✓") and "VERIFIED" in first:
        res = "holds"
    else:
        res = "error"
    row = dict(env=env, result=res, seconds=round(time.time() - t, 2))
    if res != "holds":
        row["output"] = out[:4000]
    return row


def cedar_item(it, scratch):
    v = it["verifier"]
    art = HERE / v["policies"]
    schema = HERE / "artefacts" / it["artefact"] / "schema.cedarschema"
    prop = scratch / f"{it['id']}.property.cedar"
    prop.write_text(v["property_policy"] + "\n")
    rows = []
    for env in v["environments"]:
        p1, p2 = (art, prop) if v["kind"] == "only_if" else (prop, art)
        rows.append(symcc_implies(schema, env, p1, p2))
    results = {r["result"] for r in rows}
    if results - {"holds", "does_not_hold"}:
        answer = "UNDECIDED"
    elif "does_not_hold" in results:
        answer = "NO"
    else:
        answer = "YES"
    cex = next((r["output"] for r in rows if r["result"] == "does_not_hold"), None)
    return dict(answer=answer, queries=rows, counterexample=cex)


# ------------------------------------------------------------------------------------------------
# Kubernetes RBAC encoding for Z3
# ------------------------------------------------------------------------------------------------

def selector_matches(sel, labels):
    for k, v in (sel.get("matchLabels") or {}).items():
        if labels.get(k) != v:
            return False
    assert not sel.get("matchExpressions"), "matchExpressions not used in these artefacts"
    return True


def aggregated_rules(objects):
    crs = {o["metadata"]["name"]: o for o in objects if o["kind"] == "ClusterRole"}
    rules = {n: ([] if o.get("aggregationRule") else list(o.get("rules") or [])) for n, o in crs.items()}
    while True:
        changed = False
        for n, o in crs.items():
            agg = o.get("aggregationRule")
            if not agg:
                continue
            acc = []
            for sel in agg.get("clusterRoleSelectors") or []:
                for m, mo in crs.items():
                    if m != n and selector_matches(sel, mo["metadata"].get("labels") or {}):
                        acc += [r for r in rules[m] if r not in acc]
            if acc != rules[n]:
                rules[n], changed = acc, True
        if not changed:
            return rules


def k8s_encode(z3, objects, V):
    user, verb, api, res, sub, ns, name, grp = (V[k] for k in ("user", "verb", "api", "res", "sub", "ns", "name", "grp"))
    S = z3.StringVal
    cr = aggregated_rules(objects)
    roles = {(o["metadata"]["namespace"], o["metadata"]["name"]): o.get("rules") or []
             for o in objects if o["kind"] == "Role"}
    combined = z3.If(sub == S(""), res, z3.Concat(res, S("/"), sub))

    def rule(r):
        vm = z3.Or([z3.BoolVal(True) if v == "*" else verb == S(v) for v in r.get("verbs") or []] or [z3.BoolVal(False)])
        gm = z3.Or([z3.BoolVal(True) if g == "*" else api == S(g) for g in r.get("apiGroups") or []] or [z3.BoolVal(False)])
        rms = []
        for rr in r.get("resources") or []:
            if rr == "*":
                rms.append(z3.BoolVal(True))
            elif rr.startswith("*/"):
                rms.append(z3.And(sub != S(""), sub == S(rr[2:])))
            else:
                rms.append(combined == S(rr))
        rm = z3.Or(rms or [z3.BoolVal(False)])
        names = r.get("resourceNames") or []
        nm = z3.Or([name == S(n) for n in names]) if names else z3.BoolVal(True)
        return z3.And(vm, gm, rm, nm)

    alts = []
    for o in objects:
        if o["kind"] not in ("RoleBinding", "ClusterRoleBinding"):
            continue
        bns = o["metadata"].get("namespace", "") if o["kind"] == "RoleBinding" else ""
        subj = []
        for s in o.get("subjects") or []:
            if s["kind"] == "User":
                subj.append(user == S(s["name"]))
            elif s["kind"] == "Group":
                subj.append(grp(S(s["name"])))
            elif s["kind"] == "ServiceAccount":
                sns = s.get("namespace") or bns
                subj.append(user == S(f"system:serviceaccount:{sns}:{s['name']}"))
        ref = o["roleRef"]
        rs = cr.get(ref["name"], []) if ref["kind"] == "ClusterRole" else roles.get((bns, ref["name"]), [])
        scope = [ns == S(bns)] if o["kind"] == "RoleBinding" else []
        alts.append(z3.And(*scope, z3.Or(subj or [z3.BoolVal(False)]), z3.Or([rule(r) for r in rs] or [z3.BoolVal(False)])))
    return z3.Or(alts or [z3.BoolVal(False)])


def k8s_item(it, reference_rbac):
    import z3
    world = json.loads((HERE / it["verifier"]["policies"]).read_text())
    objects = world["objects"]
    V = {k: z3.String(k) for k in ("user", "verb", "api", "res", "sub", "ns", "name")}
    V["grp"] = z3.Function("grp", z3.StringSort(), z3.BoolSort())
    allowed = k8s_encode(z3, objects, V)
    env = dict(V, allowed=allowed, And=z3.And, Or=z3.Or, Not=z3.Not, Implies=z3.Implies,
               grp=lambda g: V["grp"](z3.StringVal(g)))
    # string literals in the property are auto-lifted by z3's == on String sorts
    prop = eval(it["verifier"]["property"], {"__builtins__": {}}, env)
    s = z3.Solver()
    s.set("timeout", TIMEOUT_S * 1000)
    s.add(z3.Not(z3.Contains(V["res"], z3.StringVal("/"))), z3.Not(z3.Contains(V["sub"], z3.StringVal("/"))))
    s.add(z3.Not(prop))
    t = time.time()
    r = s.check()
    row = dict(solver_result=str(r), solver_seconds=round(time.time() - t, 2))
    if r == z3.unsat:
        row["answer"] = "YES"
    elif r == z3.sat:
        m = s.model()
        req = {k: m.eval(V[k], model_completion=True).as_string() for k in ("user", "verb", "res", "sub", "ns", "name")}
        req["apiGroup"] = m.eval(V["api"], model_completion=True).as_string()
        req["subresource"], req["resource"], req["namespace"] = req.pop("sub"), req.pop("res"), req.pop("ns")
        # groups the model puts the user in, among the group names the world mentions
        gnames = sorted({s_["name"] for o in objects for s_ in (o.get("subjects") or []) if s_["kind"] == "Group"} | {"manager"})
        req["groups"] = [g for g in gnames if z3.is_true(m.eval(V["grp"](z3.StringVal(g)), model_completion=True))]
        z3_allowed = z3.is_true(m.eval(allowed, model_completion=True))
        ref_allowed = reference_rbac.k8s_authorize(objects, req)
        row.update(answer="NO", counterexample=dict(request=req, allowed_z3=z3_allowed, allowed_reference=ref_allowed),
                   crosscheck="agree" if z3_allowed == ref_allowed else "DISAGREE")
        if z3_allowed != ref_allowed:
            row["answer"] = "UNDECIDED"
    else:
        row["answer"] = "UNDECIDED"
    row["grid_crosscheck"] = k8s_grid_crosscheck(z3, it, objects, V, prop, reference_rbac)
    if row["grid_crosscheck"]["violations_found"] and row["answer"] == "YES":
        row["answer"] = "UNDECIDED"
    return row


def k8s_grid_crosscheck(z3, it, objects, V, prop, reference_rbac, n=3000, seed=0):
    """Sample requests over the strings the world and property mention (plus a fresh value and "")
    and evaluate the property with P3's reference authorizer in place of the Z3 encoding."""
    import random
    rnd = random.Random(seed)
    lits = set(re.findall(r"'([^']*)'", it["verifier"]["property"]))

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                yield from walk(v)
        elif isinstance(x, list):
            for v in x:
                yield from walk(v)
        elif isinstance(x, str):
            yield x
    for sv in walk(objects):
        lits.add(sv)
        if "/" in sv:
            lits.update(sv.split("/"))
    pool = sorted(l for l in lits | {"", "fresh"} if "/" not in l and "*" not in l)
    groups_pool = sorted({s["name"] for o in objects for s in (o.get("subjects") or []) if s["kind"] == "Group"} | {"manager", "fresh"})
    bindings = [o for o in objects if o["kind"] in ("RoleBinding", "ClusterRoleBinding")]
    all_rules = aggregated_rules(objects)
    role_rules = {(o["metadata"]["namespace"], o["metadata"]["name"]): o.get("rules") or []
                  for o in objects if o["kind"] == "Role"}
    pick = lambda xs: rnd.choice(pool) if not xs or xs == ["*"] else rnd.choice(xs)
    fields = ("user", "verb", "apiGroup", "resource", "subresource", "namespace", "name")
    viol = 0
    allowed_n = 0
    for _ in range(n):
        req = {k: rnd.choice(pool) for k in fields}
        req["groups"] = [g for g in groups_pool if rnd.random() < 0.3]
        if bindings and rnd.random() < 0.7:
            # steer towards a binding/rule pair, then perturb fields
            b = rnd.choice(bindings)
            bns = b["metadata"].get("namespace", "")
            rs = (all_rules.get(b["roleRef"]["name"], []) if b["roleRef"]["kind"] == "ClusterRole"
                  else role_rules.get((bns, b["roleRef"]["name"]), []))
            s_ = rnd.choice(b["subjects"])
            if s_["kind"] == "User":
                req["user"] = s_["name"]
            else:
                req["groups"] = sorted(set(req["groups"]) | {s_["name"]})
            if bns:
                req["namespace"] = bns
            if rs:
                r = rnd.choice(rs)
                req["verb"], req["apiGroup"] = pick(r.get("verbs")), pick(r.get("apiGroups"))
                res = pick(r.get("resources"))
                req["resource"], req["subresource"] = (res.split("/", 1) + [""])[:2] if "/" in res else (res, "")
                if r.get("resourceNames"):
                    req["name"] = rnd.choice(r["resourceNames"])
            for k in fields:
                if rnd.random() < 0.15:
                    req[k] = rnd.choice(pool)
        ref = reference_rbac.k8s_authorize(objects, req)
        allowed_n += ref
        sub = [(V["user"], z3.StringVal(req["user"])), (V["verb"], z3.StringVal(req["verb"])),
               (V["api"], z3.StringVal(req["apiGroup"])), (V["res"], z3.StringVal(req["resource"])),
               (V["sub"], z3.StringVal(req["subresource"])), (V["ns"], z3.StringVal(req["namespace"])),
               (V["name"], z3.StringVal(req["name"]))]
        ev = eval(it["verifier"]["property"], {"__builtins__": {}},
                  dict(V, allowed=z3.BoolVal(ref), And=z3.And, Or=z3.Or, Not=z3.Not, Implies=z3.Implies,
                       grp=lambda g: z3.BoolVal(g in req["groups"])))
        if not z3.is_true(z3.simplify(z3.substitute(ev, *sub))):
            viol += 1
    return dict(samples=n, seed=seed, allowed_by_reference=allowed_n, violations_found=viol)


def main():
    items = json.loads((HERE / "items.json").read_text())
    spec = importlib.util.spec_from_file_location(
        "reference_rbac", HERE.parent / "P3-formalisation-tax" / "reference_rbac.py")
    reference_rbac = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference_rbac)
    scratch = HERE / ".scratch"
    scratch.mkdir(exist_ok=True)
    import z3
    out = dict(verifiers=dict(cedar=dict(name="Cedar SymCC via `cedar symcc implies`", cli=cedar_version(),
                                         cvc5=cvc5_version(), per_query_timeout_s=TIMEOUT_S),
                              k8s=dict(name="Z3 via Python encoding (ground_truth.py:k8s_encode)",
                                       z3=z3.get_version_string(), crosscheck="P3 reference_rbac.k8s_authorize replays every counterexample; 3,000 steered samples per item (seed 0) evaluate the property with that reference")),
               items=[])
    for it in items:
        t = time.time()
        r = cedar_item(it, scratch) if it["family"] == "cedar" else k8s_item(it, reference_rbac)
        row = dict(id=it["id"], artefact=it["artefact"], variant=it["variant"], answer=r.pop("answer"),
                   seconds=round(time.time() - t, 2), **r)
        out["items"].append(row)
        print(it["id"], it["artefact"], it["variant"], row["answer"], row["seconds"], flush=True)
    (HERE / "ground_truth.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    ans = [r["answer"] for r in out["items"]]
    print({a: ans.count(a) for a in sorted(set(ans))})


if __name__ == "__main__":
    main()
