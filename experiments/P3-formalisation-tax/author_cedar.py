"""Author's convenience writer for Cedar item formalisations (part of authoring cost)."""
import json
HDR = {"language": "ve.core@0.1", "profiles": ["closure@0", "relational-fol@0"], "spec_revision": "ve-v0.1-closure-2026-09-21"}
SORTS = {"entity": {"description": "A Cedar entity UID, record node, or the request context node."},
         "value": {"description": "A Cedar string, long or extension literal value."}}
REQ = {"principal": "The request principal.", "action": "The request action.", "resource": "The request resource.",
       "context": "The request context record node."}
def P(args, desc): return {"arguments": args, "description": desc}
STD = {"parent": P(["entity", "entity"], "Immediate hierarchy edge, child to parent.")}
def write(item, ve, ents={}, vals={}, preds={}, reqc=("principal", "action", "resource"), sorts=("entity",)):
    d = f"items/{item}/"
    c = {k: {"sort": "entity", "description": REQ[k]} for k in reqc}
    c.update({k: {"sort": "entity", "description": u} for k, u in ents.items()})
    c.update({k: {"sort": "value", "description": json.dumps(v)} for k, v in vals.items()})
    env = {**HDR, "vocabulary": {"sorts": {s: SORTS[s] for s in sorts}, "predicates": preds, "constants": c}}
    open(d + "environment.json", "w").write(json.dumps(env, indent=1) + "\n")
    b = {"constants": {**{k: {"entity": u} for k, u in ents.items()}, **{k: {"value": v} for k, v in vals.items()}}}
    open(d + "bindings.json", "w").write(json.dumps(b, indent=1) + "\n")
    open(d + "formalisation.ve", "w").write(ve)


# tiny surface-syntax builders (the strict grammar needs binary, fully parenthesised connectives)
def AND(*xs):
    xs = [x for x in xs if x]
    return xs[0] if len(xs) == 1 else f"({xs[0]}) and ({AND(*xs[1:])})"
def OR(*xs):
    return xs[0] if len(xs) == 1 else f"({xs[0]}) or ({OR(*xs[1:])})"
def NOT(x): return f"not ({x})"
def EX(sort, v, body): return f"there exists {sort} {v}, ({body})"
def ALL(sort, v, body): return f"for every {sort} {v}, ({body})"
def IMP(a, b): return f"if ({a}), then ({b})"
def IN(a, b): return f"rtc[parent]({a}, {b})"
def EQ(a, b): return f"{a} equals {b}"
def INANY(a, *bs): return OR(*[IN(a, b) for b in bs])


# `x in owner.<a>` where <a> should be an entity or a set of entities. Cedar raises a type
# error (policy skipped) if the value is a string/long/Boolean/record, or a set with any
# non-entity member; IN_OK says the operand evaluates without error, IN_TRUE that it is true.
def IN_OK(owner, a):
    return AND(f"{owner} is has_{a}", NOT(EX("value", "zv", f"{owner} sa_{a} zv")), NOT(f"{owner} is bt_{a}"),
               NOT(f"{owner} is bf_{a}"), NOT(EX("value", "zv", f"{owner} ss_{a} zv")),
               NOT(EX("entity", "zm", AND(OR(f"{owner} es_{a} zm", f"{owner} ea_{a} zm"), "zm is type_record"))))
def IN_TRUE(x, owner, a):
    return AND(IN_OK(owner, a), EX("entity", "zh", AND(OR(f"{owner} es_{a} zh", f"{owner} ea_{a} zh"), IN(x, "zh"))))
def IN_PREDS(*attrs):
    P_ = lambda args, d: {"arguments": args, "description": d}
    out = {"type_record": P_(["entity"], "Anonymous record node.")}
    for a in attrs:
        out.update({f"has_{a}": P_(["entity"], f"Attribute {a} present."), f"sa_{a}": P_(["entity", "value"], f"Scalar attribute {a}."),
                    f"bt_{a}": P_(["entity"], f"{a} is Boolean true."), f"bf_{a}": P_(["entity"], f"{a} is Boolean false."),
                    f"ss_{a}": P_(["entity", "value"], f"Scalar member of set attribute {a}."),
                    f"es_{a}": P_(["entity", "entity"], f"Entity/record member of set attribute {a}."),
                    f"ea_{a}": P_(["entity", "entity"], f"Entity/record-valued attribute {a}.")})
    return out
