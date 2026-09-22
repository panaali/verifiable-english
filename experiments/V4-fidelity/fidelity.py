"""Generate frozen items, score translations, or run exactly three CLI smoke items."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys

import ve
from ve_experiments.claude_cli import ClaudeCLI, Controls
from ve_experiments.llm import parse_final_json
from ve_experiments.ve_iface import StubBackend
from generator import atoms, evaluate, literal, sat, skeleton

HERE = Path(__file__).resolve().parent
SEED = 2026092204
BUDGET = ve.Budgets(max_proof_steps=3000, max_models=0)
SYSTEM = "You translate free English into precise Verifiable English and submit a claim graph. Return one JSON object."


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+"\n")


def environment(predicates):
    return {"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
            "vocabulary": {"sorts": {"person": {"description": "People in the story"}},
            "constants": {"ada": {"sort": "person", "description": "Ada"},
                          "ben": {"sort": "person", "description": "Ben"}}, "predicates": predicates}}


def english(f, atom_text):
    if isinstance(f, str): return atom_text[f]
    if f[0] == "¬": return "it is not the case that ("+english(f[1], atom_text)+")"
    a, b = (english(x, atom_text) for x in f[1:])
    return {"→": f"if ({a}), then ({b})", "∧": f"both ({a}) and ({b})",
            "∨": f"at least one of ({a}) and ({b}) is true, possibly both",
            "⊕": f"exactly one of ({a}) and ({b}) is true"}[f[0]]


def to_ast(f, mapping):
    if isinstance(f, str): return mapping[f]
    if f[0] == "¬": return ["not", to_ast(f[1], mapping)]
    a, b = (to_ast(x, mapping) for x in f[1:])
    if f[0] == "⊕": return ["and", ["or", a, b], ["not", ["and", a, b]]]
    return [{"→":"implies", "∧":"and", "∨":"or"}[f[0]], a, b]


def realize(sk, index, rng):
    names = sorted(set().union(*(atoms(f) for f in sk["premises"]+[sk["query"]])))
    rng.shuffle(names)
    preds, mapping, text, kinds = {}, {}, {}, {}
    colors = ["amber", "cobalt", "silver", "violet", "teal", "copper", "ivory", "scarlet"]
    objects = ["badge", "ribbon", "hat", "scarf", "coat", "pin", "belt", "card"]
    relations = ["trusts", "admires", "follows", "helps", "respects", "knows"]
    # Independent predicate per atom makes all propositional assignments realizable.
    for i, name in enumerate(names):
        pred = f"p{i}"
        kind = (i+index) % 4
        if kind == 0:
            phrase = f"has a {colors[i%8]} {objects[(i//8)%8]}"
            preds[pred] = {"arguments":["person"], "description":phrase}
            mapping[name] = ["unary", pred, ["const", "ada"]]
            text[name] = "Ada "+phrase
        else:
            phrase = f"{relations[i%6]} through club {i}"
            preds[pred] = {"arguments":["person", "person"], "description":phrase+" (first person to second person)"}
            if kind == 1:
                mapping[name] = ["binary", pred, ["const","ada"], ["const","ben"]]
                text[name] = f"Ada {relations[i%6]} Ben through club {i}"
            elif kind == 2:
                mapping[name] = ["forall", "person", ["exists", "person", ["binary",pred,["var",1],["var",0]]]]
                text[name] = f"every person {relations[i%6]} at least one person through club {i} (the person may differ for each individual)"
            else:
                mapping[name] = ["exists", "person", ["forall", "person", ["binary",pred,["var",0],["var",1]]]]
                text[name] = f"there is a person whom every person {relations[i%6]} through club {i}"
        kinds[name] = kind
    env_dict = environment(preds); env = ve.Environment.from_dict(env_dict)
    gold = [to_ast(f,mapping) for f in sk["premises"]]
    query = to_ast(sk["query"], mapping)
    # E0's existing mechanical FOL flags, followed by actual VE AST/type/parse checks.
    spec = importlib.util.spec_from_file_location("e0_fit", HERE.parent/"E0/survey_sample.py")
    e0 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e0)
    fit = []
    for f in gold+[query]:
        fol = StubBackend().render(f,"fol")
        flags, arity = e0.folio_formula_flags(fol)
        if flags & {"arity_gt2","nested_term","arith_or_cmp_symbol","numeric_constant","arity0"}:
            raise ValueError((flags,fol))
        formula = ve.formula_from_data(env,f)
        source = ve.print_formula(env,formula)+".\n"
        assert ve.parse(env,source.rstrip()+"\n").formulas == (formula,)
        fit.append({"flags":sorted(flags),"max_arity":arity})
    witnesses = {}
    for polarity in (True,False):
        witness = sat(sk["premises"]+[sk["query"] if polarity else ("¬",sk["query"])])
        if witness is None: continue
        model = {"complete": True, "domains":{"person":["a","b"]}, "constants":{"ada":"a","ben":"b"}, "relations":{}}
        for name, atom in mapping.items():
            pred = f"p{names.index(name)}"
            arity = len(preds[pred]["arguments"])
            model["relations"][pred] = ([["a"],["b"]] if arity == 1 else [[a,b] for a in ("a","b") for b in ("a","b")]) if witness[name] else []
        finite = ve.FiniteModel.from_dict(env,model)
        assert all(ve.evaluate(env,ve.formula_from_data(env,f),finite).value is True for f in gold)
        assert ve.evaluate(env,ve.formula_from_data(env,query),finite).value is polarity
        witnesses[str(polarity)] = model
    label = "Uncertain" if len(witnesses)==2 else "True" if "True" in witnesses else "False" if "False" in witnesses else "INCONSISTENT"
    assert label == sk["label"], (label,sk["label"])
    # Shuffle premises, preserving their English/gold alignment. No labels enter prompts.
    order=list(range(len(gold))); rng.shuffle(order)
    return {"id":f"v4-{index:03d}", "seed":SEED, "depth":sk["depth"],"label":label,
            "environment":env_dict, "premises":[{"id":f"p{i}","english":english(sk['premises'][j],text)+".","gold_ast":gold[j]} for i,j in enumerate(order)],
            "query":{"english":english(sk["query"],text)+".","gold_ast":query},
            "gold_witnesses":witnesses, "e0_fit":fit, "skeleton":sk,
            "atom_mapping":mapping, "atom_english":text}


def generate(seed=SEED, filename="items.jsonl", prefix="v4"):
    rng=random.Random(seed)
    labels=["True","False","Uncertain"]*20
    rows=[]
    for i,label in enumerate(labels):
        sk=skeleton(rng,label,rng.choice([6,7,8,9]))
        row=realize(sk,i,rng)
        row.update(id=f"{prefix}-{i:03d}", seed=seed)
        rows.append(row)
    path=HERE/filename
    path.write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in rows))
    dump(path.with_name(path.stem+"-manifest.json" if filename != "items.jsonl" else "manifest.json"), {"seed":seed,"items":60,"labels":dict(Counter(r['label'] for r in rows)),
         "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"e0_fit_pass":60,
         "satisfiable_items":60,"gold_validation":"Independent Tseitin/DPLL plus VE evaluation of all satisfying witnesses",
         "smoke_ids":[r["id"] for r in rows[:3]],
         "hand_audit_ids":[r["id"] for r in random.Random(seed+1).sample(rows,12)]})
    print("Generated and E0/VE validated 60 fresh items",flush=True)


def prompt(item):
    schema = (HERE/"PROMPT.md").read_text()
    public = {"environment":item["environment"],"premises":[{k:p[k] for k in ("id","english")} for p in item["premises"]],
              "query":item["query"]["english"]}
    return schema+"\nINPUT:\n"+json.dumps(public,ensure_ascii=False)


def features(ast):
    """Diagnostics retain binding/order/polarity, not just operator counts."""
    found=[]
    def walk(f,path):
        if f[0] in ("unary","binary"): found.append({"path":path,"predicate":f[1],"arguments":f[2:]})
        elif f[0] in ("forall","exists"):
            found.append({"path":path,"quantifier":f[0],"sort":f[1]}); walk(f[2],path+[f[0]])
        elif f[0] in ("not","and","or","implies"):
            found.append({"path":path,"operator":f[0]})
            for i,c in enumerate(f[1:]): walk(c,path+[f[0],i])
    walk(ast,[])
    return found


def compare_translation(env, source, gold):
    doc=ve.parse(env,source.rstrip()+"\n")
    if len(doc.formulas)!=1: raise ValueError("One formula required per translation")
    candidate=doc.formulas[0]; reference=ve.formula_from_data(env,gold)
    exact=candidate==reference
    relation="EQUIVALENT" if exact else ve.compare(env,reference,candidate,BUDGET).status
    data=ve.formula_to_data(env,candidate)
    return {"exact_structure":exact,"relation":relation,"faithful_mechanical":relation=="EQUIVALENT",
            "submitted_ast":data,
            "gold_structure":features(gold),"submitted_structure":features(data)}


def score(item,response):
    result={"id":item["id"],"faithful_mechanical":False,"certified_answer":False,"grounded_certificate":False}
    try:
        obj=parse_final_json(response) if isinstance(response,str) else response
        answer=obj.get("answer")
        result.update(answer=answer,answer_correct=answer==item["label"])
        env=ve.Environment.from_dict(item["environment"])
        translations=obj["translations"]
        expected={p["id"] for p in item["premises"]}
        if len(translations)!=len(expected) or {t["premise_id"] for t in translations}!=expected:
            raise ValueError("Translation table must cover each premise exactly once")
        by_id={p["id"]:p for p in item["premises"]}
        diagnostics={}
        for t in translations:
            pid=t["premise_id"]
            if t["english"]!=by_id[pid]["english"]: raise ValueError("English source substituted")
            diagnostics[pid]=compare_translation(env,t["ve"],by_id[pid]["gold_ast"])
        diagnostics["query"]=compare_translation(env,obj["query_ve"],item["query"]["gold_ast"])
        result["translations"]=diagnostics
        result["faithful_mechanical"]=all(d["faithful_mechanical"] for d in diagnostics.values())
        answer=obj["answer"]
        if answer not in ("True","False","Uncertain"): raise ValueError("Invalid answer")
        result.update(answer=answer,answer_correct=answer==item["label"])
        g=obj["graph"]
        claims=[ve.Claim.create(env,c["id"],c["ve"].rstrip()+"\n") for c in g["claims"]]
        deductions=[ve.Deduction(d["id"],tuple(d["premises"]),d["conclusion"]) for d in g["deductions"]]
        graph=ve.ArgumentGraph(env,tuple(claims),tuple(deductions),g["root"])
        checked=ve.check_argument(graph,max_proof_steps=3000,max_models=0)
        result["checker"]=checked.to_dict()
        cm={c.name:c for c in claims}
        q=ve.parse(env,obj["query_ve"].rstrip()+"\n").formulas[0]
        target=q if answer=="True" else ve.Not(q) if answer=="False" else None
        bound=target is not None and cm[g["root"]].ast==target
        # Every graph leaf must be a submitted premise, and each table row must bind
        # to the same-named claim. Never use gold premises in the deduction checker.
        table_bound=all(t["premise_id"] in cm and cm[t["premise_id"]].source==t["ve"].rstrip()+"\n" for t in translations)
        derived={d.conclusion for d in deductions}
        leaves={c.name for c in claims}-derived
        grounded=table_bound and leaves<=expected
        result.update(query_bound=bound,premise_bound=grounded,
                      certified_answer=bool(checked.composed and bound),
                      grounded_certificate=bool(checked.composed and bound and grounded and result["faithful_mechanical"]))
        # Non-entailment is certified by checked countermodels for BOTH polarities.
        if answer=="Uncertain":
            premises=[ve.parse(env,t["ve"].rstrip()+"\n").formulas[0] for t in translations]
            models=obj.get("countermodels",{})
            valid=True
            for key,polarity in (("query_true",True),("query_false",False)):
                model=ve.FiniteModel.from_dict(env,models[key])
                valid &= all(ve.evaluate(env,p,model).value is True for p in premises)
                valid &= ve.evaluate(env,q,model).value is polarity
            result["certified_answer"]=bool(valid)
            result["grounded_certificate"]=bool(valid and result["faithful_mechanical"])
    except Exception as exc:
        result["error"]=f"{type(exc).__name__}: {exc}"
    return result


def smoke():
    rows=[json.loads(x) for x in (HERE/"items.jsonl").read_text().splitlines()][:3]
    results=HERE/"results"; results.mkdir(exist_ok=True)
    client=ClaudeCLI(results/"smoke-ledger.jsonl", Controls(output_tokens=14000,timeout_s=300),max_calls=3)
    for item in rows:
        row=client.sample(item["id"],SYSTEM,prompt(item))
        scored=score(item,row["text"])
        dump(results/(item["id"]+"-score.json"),scored)
        print(json.dumps({k:v for k,v in scored.items() if k not in ("translations","checker")}),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("command",choices=("generate","smoke"))
    {"generate":generate,"smoke":smoke}[p.parse_args().command]()
