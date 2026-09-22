"""Does the differential test catch realistic mistranslations? Runs each
items/<id>/naive_variants.json statement through the same test cases as
mutation.py. Writes naive_results.json."""
import json
import re
import sys

import harness as H
import mutation as M
from ve import Environment, evaluate, parse

SIG = {"bt_": ["entity"], "bf_": ["entity"], "has_": ["entity"], "ea_": ["entity", "entity"],
       "es_": ["entity", "entity"], "sa_": ["entity", "value"], "ss_": ["entity", "value"]}


def extended_env(d, variants):
    """The item environment plus any convention-named Cedar predicate a naive variant uses."""
    wire = json.loads((d / "environment.json").read_text())
    preds = wire["vocabulary"]["predicates"]
    for v in variants:
        for name in set(re.findall(r"\b((?:bt|bf|has|ea|es|sa|ss)_[a-z0-9_]+)\b", v["ve"])):
            if name not in preds:
                sig = next(SIG[k] for k in SIG if name.startswith(k))
                preds[name] = {"arguments": sig, "description": "Added for a naive variant."}
    return Environment.from_json(json.dumps(wire).encode())


out = []
for d in sorted(H.ITEMS.iterdir()):
    f = d / "naive_variants.json"
    if not f.exists() or (sys.argv[1:] and d.name not in sys.argv[1:]):
        continue
    item = H.load_item(d.name)
    env, doc, bindings = H.load_formalisation(item)
    variants = json.loads(f.read_text())
    env = extended_env(d, variants)
    cases = M.test_cases(item, env, doc, bindings, H.N_PERTURB)
    for v in variants:
        stmt = parse(env, v["ve"].encode()).formulas[0]
        wrong_item = sum(evaluate(env, stmt, m, trace=False).value != ref for k, m, q, ref in cases if k == "item")
        wrong_pert = sum(evaluate(env, stmt, m, trace=False).value != ref for k, m, q, ref in cases if k == "perturbed")
        row = {"item": d.name, "variant": v["name"], "description": v["description"],
               "item_questions_wrong": wrong_item, "perturbations_wrong": wrong_pert,
               "perturbations": sum(k == "perturbed" for k, *_ in cases),
               "caught": wrong_item + wrong_pert > 0, "caught_by_item_questions_alone": wrong_item > 0}
        out.append(row)
        print(json.dumps({k: row[k] for k in row if k != "description"}), flush=True)
if not sys.argv[1:]:
    (H.HERE / "naive_results.json").write_text(json.dumps(out, indent=1) + "\n")
