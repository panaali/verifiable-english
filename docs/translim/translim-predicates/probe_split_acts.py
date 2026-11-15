"""PART 1a/3 probe: the post-split limit through `norms`, and the soft route's refusal of an acts@0 vocabulary (REPORT 3)."""
import json
from tests.test_acts_joined_route import environment, NORM_PROFILES
from ve.backends import lean_service
L = "abcdefghijklmnopqrstuvwxyz"
def split_env(split, lexical):
    env = environment(NORM_PROFILES)
    preds = {}
    for i in range(split):
        t = L[i // 26] + L[i % 26]
        preds[f"p{i}"] = {"arguments": ["person"], "description": "d", "regulated": {"role": "permission", "default": "deny", "act": f"{{0}} be subjected to x{t} or to y{t}"}}
    for i in range(lexical):
        preds[f"h{i}"] = {"arguments": ["person"], "description": "d", "regulated": {"role": "permission", "default": "deny", "act": f"{{0}} be held{L[i]}"}}
    env["vocabulary"]["predicates"] = preds
    rules = [{"norm": {"name": f"r{p}", "predicate": p, "sign": False, "guard": ["top"], "unless": [], "over": []}} for p in preds]
    return env, rules
for split, lex in ((31, 2), (32, 1), (32, 0), (33, 0)):
    env, rules = split_env(split, lex)
    with lean_service.LeanService(lean_service.DEFAULT_EXECUTABLE) as s:
        _, r = s.exchange("norms", json.dumps([{"id": "c", "kind": "norms-elaborate", "environment": env, "norms": rules}]), 1)
    row = r["results"][0]["result"]
    print(split, lex, len(env["vocabulary"]["predicates"]), row.get("error") or (row.get("status"), len(row.get("conflict_targets", []))))
print("soft")
for split, lex in ((31, 2), (32, 1)):
    env, rules = split_env(split, lex)
    env["profiles"] = sorted(env["profiles"] + ["soft-norms@0"])
    rules = [{"norm": {**r["norm"], "mode": "default", "exception": {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}}} for r in rules]
    with lean_service.LeanService(lean_service.DEFAULT_EXECUTABLE) as s:
        _, r = s.exchange("soft-norms", json.dumps([{"id": "c", "kind": "soft-elaborate", "environment": env, "norms": rules}]), 1)
    row = r["results"][0]["result"]
    print(split, lex, row.get("error") or (row.get("status"), len(row.get("conflict_targets", []))))
