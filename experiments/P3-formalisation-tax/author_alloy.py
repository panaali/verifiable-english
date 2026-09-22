"""Author's convenience writer for Alloy item formalisations (part of authoring cost)."""
import json
from author_cedar import AND, OR, NOT, EX, ALL, IMP, EQ
HDR = {"language": "ve.core@0.1", "profiles": ["closure@0", "relational-fol@0"], "spec_revision": "ve-v0.1-closure-2026-09-21"}
def P(args, d): return {"arguments": args, "description": d}
BIN = lambda d: P(["atom", "atom"], d)
UN = lambda d: P(["atom"], d)
TUP = lambda d: P(["tuple", "atom"], d)
def IFF(a, b): return AND(IMP(a, b), IMP(b, a))
def write(item, statements, preds, consts=(), tuples=False, extra_bindings=None):
    sorts = {"atom": {"description": "An Alloy atom of the instance (one universe)."}}
    if tuples:
        sorts["tuple"] = {"description": "A reified tuple of a ternary field."}
    env = {**HDR, "vocabulary": {"sorts": sorts, "predicates": preds,
           "constants": {c: {"sort": "atom", "description": d} for c, d in consts}}}
    d = f"items/{item}/"
    open(d + "environment.json", "w").write(json.dumps(env, indent=1) + "\n")
    open(d + "bindings.json", "w").write(json.dumps(extra_bindings or {}, indent=1) + "\n")
    open(d + "formalisation.ve", "w").write("".join(s + ".\n" for s in statements))
