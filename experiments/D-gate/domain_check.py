"""D-gate: check the Cedar domain's entity-existence clause against native Cedar (no model calls).

    CEDAR=/path/to/cedar CVC5=/path/to/cvc5 python3 domain_check.py

Review finding: SymCC treats every referenced entity as present, while the first domain text allowed
dangling references. Real `cedar authorize` accepts a store with dangling references, and there an
attribute access on a missing entity errors, so a forbid can be skipped. This script

1. replays the reviewers' concrete counterexamples for D29, D22 (reference YES, `only_if`) and D11,
   D23 (reference YES, `if`) through native `cedar authorize` with the schema: each one violates the
   item's property;
2. shows that each is out of domain under the current text (build_items.CEDAR_DOMAIN: every entity
   referenced by the request, its context, or a stored entity's attribute or parent edge exists);
3. completes each store with the missing entity (fixed, schema-valid attributes) and shows the
   violation disappears;
4. confirms with SymCC that it assumes existence: a probe that accesses an attribute of the
   dangling entity (`x.a == x.a`) is VERIFIED for every allowed request, which is only possible if
   the access never errors.

Writes domain_check.json. Exit status 1 if any expectation fails.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CEDAR = os.environ.get("CEDAR", "cedar")


def E(t, i):
    return {"__entity": {"type": t, "id": i}}


def ent(t, i, attrs, parents=()):
    return {"uid": {"type": t, "id": i}, "attrs": attrs, "parents": list(parents)}


TP = "Taxpreparer::"
CASES = [
    dict(item="D29", missing=[f'{TP}Document::"DEF"'],
         request=dict(principal=f'{TP}Professional::"Alice"', action=f'{TP}Action::"viewDocument"',
                      resource=f'{TP}Document::"DEF"',
                      context={"consent": {"client": E(f"{TP}Client", "X"), "team_region_list": []}}),
         entities=[ent(f"{TP}Professional", "Alice", {"assigned_orgs": [], "location": "L"}),
                   ent(f"{TP}Client", "X", {"organization": "O"})],
         completion=[ent(f"{TP}Document", "DEF", {"serviceline": "S", "location": "L", "owner": E(f"{TP}Client", "X")})]),
    dict(item="D22", missing=['User::"ghost"'],
         request=dict(principal='User::"ghost"', action='Action::"grantViewAccessToPresentation"',
                      resource='Presentation::"r"', context={"target": E("User", "t")}),
         entities=[ent("Presentation", "r", {"owner": E("User", "ghost"), "viewers": [], "editors": []}),
                   ent("User", "t", {"job": E("Job", "customer"), "customerId": "C1"}),
                   ent("Job", "customer", {}), ent("Job", "other", {})],
         completion=[ent("User", "ghost", {"job": E("Job", "other"), "customerId": "C1"})]),
    dict(item="D11", missing=['User::"u"'],
         request=dict(principal='User::"u"', action='Action::"view"', resource='Photo::"p"',
                      context={"authenticated": True}),
         entities=[ent("Account", "a", {"admins": [], "owner": E("User", "u"), "private": False}),
                   ent("Photo", "p", {"account": E("Account", "a"), "admins": [], "private": False})],
         completion=[ent("User", "u", {"department": "D", "jobLevel": 1})]),
    dict(item="D23", missing=['User::"Bob"'],
         request=dict(principal='User::"Bob"', action='Action::"viewPresentation"',
                      resource='Presentation::"proposal"', context={}),
         entities=[ent("Presentation", "proposal", {"owner": E("User", "Carol")}),
                   ent("User", "Carol", {"job": E("Job", "other"), "customerId": ""}),
                   ent("Job", "other", {}), ent("Job", "internal", {})],
         completion=[ent("User", "Bob", {"job": E("Job", "other"), "customerId": ""})]),
]
# SymCC probes: (item, environment action, probe condition that dereferences the dangling entity)
PROBES = [
    ("D29", "resource.owner == resource.owner"),
    ("D22", "resource.owner.job == resource.owner.job"),
    ("D11", "principal.department == principal.department"),
    ("D23", "principal.job == principal.job"),
]


def uid_str(u):
    return f'{u["type"]}::{json.dumps(u["id"])}'


def refs(value):
    """Entity uids referenced anywhere inside a JSON value (entity escapes)."""
    if isinstance(value, dict):
        if set(value) == {"__entity"}:
            yield uid_str(value["__entity"])
            return
        for v in value.values():
            yield from refs(v)
    elif isinstance(value, list):
        for v in value:
            yield from refs(v)


def dangling(request, entities):
    """Referenced entities missing from the store (the domain requires none). Action entities come
    from the schema and are not store entities."""
    stored = {uid_str(e["uid"]) for e in entities}
    wanted = {request["principal"], request["resource"], *refs(request["context"])}
    for e in entities:
        wanted |= set(refs(e["attrs"]))
        wanted |= {uid_str(p) for p in e["parents"]}
    return sorted(w for w in wanted - stored if "Action::" not in w)


def authorize(policies, schema, request, entities):
    with tempfile.TemporaryDirectory() as d:
        ef, cf = Path(d) / "e.json", Path(d) / "c.json"
        ef.write_text(json.dumps(entities))
        cf.write_text(json.dumps(request["context"]))
        r = subprocess.run([CEDAR, "authorize", "-p", str(policies), "-s", str(schema), "--entities", str(ef),
                            "-l", request["principal"], "-a", request["action"], "-r", request["resource"],
                            "-c", str(cf)], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    first = out.splitlines()[0] if out else ""
    if first not in ("ALLOW", "DENY"):
        raise RuntimeError(f"cedar authorize failed: {out[:500]}")
    return first == "ALLOW"


def violates(item, request, entities, prop_file):
    v = item["verifier"]
    schema = HERE / "artefacts" / item["artefact"] / "schema.cedarschema"
    art = authorize(HERE / v["policies"], schema, request, entities)
    prop = authorize(prop_file, schema, request, entities)
    # only_if: allowed must imply the property; if: the property must imply allowed
    bad = (art and not prop) if v["kind"] == "only_if" else (prop and not art)
    return bad, dict(artefact_allows=art, property_holds=prop)


def symcc_probe(item, cond, scratch):
    v = item["verifier"]
    schema = HERE / "artefacts" / item["artefact"] / "schema.cedarschema"
    p1, p2 = scratch / "all.cedar", scratch / "probe.cedar"
    p1.write_text("permit (principal, action, resource);\n")
    p2.write_text(f"permit (principal, action, resource) when {{ {cond} }};\n")
    res = []
    for env in v["environments"]:
        r = subprocess.run([CEDAR, "symcc", "--principal-type", env[0], "--action", env[1], "--resource-type",
                            env[2], "-s", str(schema), "implies", "--policies1", str(p1), "--policies2", str(p2)],
                           capture_output=True, text=True)
        first = ((r.stdout + r.stderr).strip().splitlines() or [""])[0]
        res.append("holds" if "VERIFIED" in first and "DOES NOT HOLD" not in first else first[:200])
    return res


def main():
    items = {i["id"]: i for i in json.loads((HERE / "items.json").read_text())}
    gt = {r["id"]: r["answer"] for r in json.loads((HERE / "ground_truth.json").read_text())["items"]}
    ok = True
    out = dict(cedar=subprocess.run([CEDAR, "--version"], capture_output=True, text=True).stdout.strip(),
               domain_clause="Every referenced entity exists in the entity store", cases=[], symcc_probes=[])
    with tempfile.TemporaryDirectory() as d:
        scratch = Path(d)
        for c in CASES:
            it = items[c["item"]]
            pf = scratch / f"{c['item']}.property.cedar"
            pf.write_text(it["verifier"]["property_policy"] + "\n")
            bad, detail = violates(it, c["request"], c["entities"], pf)
            miss = dangling(c["request"], c["entities"])
            full = c["entities"] + c["completion"]
            bad_full, detail_full = violates(it, c["request"], full, pf)
            row = dict(item=c["item"], reference=gt[c["item"]], kind=it["verifier"]["kind"], request=c["request"],
                       entities=c["entities"], native_cedar=detail, violates_property=bad, dangling=miss,
                       out_of_domain=bool(miss), completed_store_violates=bad_full, completed=detail_full,
                       completion=c["completion"], dangling_after_completion=dangling(c["request"], full))
            good = (bad and miss == c["missing"] and not bad_full and not row["dangling_after_completion"]
                    and gt[c["item"]] == "YES")
            ok &= good
            out["cases"].append(row)
            print(c["item"], "violates" if bad else "no-violation", "dangling", miss,
                  "| completed:", "violates" if bad_full else "no-violation", "OK" if good else "UNEXPECTED")
        for item_id, cond in PROBES:
            res = symcc_probe(items[item_id], cond, scratch)
            good = all(r == "holds" for r in res)
            ok &= good
            out["symcc_probes"].append(dict(item=item_id, probe=cond, results=res))
            print("symcc probe", item_id, cond, res, "OK" if good else "UNEXPECTED")
    out["all_expectations_met"] = ok
    (HERE / "domain_check.json").write_text(json.dumps(out, indent=1) + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
