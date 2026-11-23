"""relb-f3-phrases: how many eligibility rules and yes/no facts read in plain phrases.

A rule or fact COUNTS when (a) its generated controlled-English wording (render_w6_sentence, as the
eligibility harness and the relb-f1f2-eligibility rule row use) parses back (parse_w6_sentence) to
exactly one reading, equal to the statement, and (b) [plain] the wording uses no fallback phrase for a yes/no
predicate: neither 'is classified as "<name>"' nor 'has the recorded relation "<name>" to'.
[declared] (the headline): (a) and every yes/no predicate in it reads with the wording the environment
declares for it (its `verbalisation`), accepted by the checker; a predicate read from its bare name
("applicant is claimed") does not count. Facts = the distinct profile facts (run.py english_facts) whose formula holds a yes/no predicate.

usage: python -B measure.py <ve checkout> [--wordings <json name->template>] [--out <json>]
--wordings declares the templates as `verbalisation`s in an in-memory copy of the environment
(nothing on disk changes). Read-only on the checkout.
"""
import argparse, collections, json, sys

ap = argparse.ArgumentParser()
ap.add_argument("repo")
ap.add_argument("--wordings")
ap.add_argument("--out")
ap.add_argument("--idioms-python-only", action="store_true",
                help="spike only: also add the wordings to the Python idiom list in memory (Lean's is unchanged, "
                     "so reading sentences fails; use with --legend-only)")
ap.add_argument("--legend-only", action="store_true")
ap.add_argument("--show", type=int, default=3)
a = ap.parse_args()
sys.path.insert(0, a.repo); sys.path.insert(0, a.repo + "/usecases/eligibility")
import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.english import english_legend  # noqa: E402
from ve.surface.time import parse_w6_sentence, render_w6_sentence  # noqa: E402
from ve.units import elaborate_quantity, erased_environment  # noqa: E402

raw = T.environment()
wordings = json.load(open(a.wordings)) if a.wordings else {}
for n, t in wordings.items():
    raw["vocabulary"]["predicates"][n]["verbalisation"] = t
if a.idioms_python_only:
    import ve.english_vocabulary as EV
    for t in wordings.values():
        EV.IDIOMS[t.count("{")].add(t)
env = Environment(raw)
leg = json.loads(english_legend(erased_environment(env), style="json"))
used = {n: p["template"] for n, p in leg["predicates"].items()}
declared_ok = {n for n, d in env.predicates.items() if d.verbalisation and used.get(n) == d.verbalisation}
fallback = {n for n, t in used.items() if "classified as" in t or "recorded relation" in t}
lint = collections.defaultdict(list)
for i in leg.get("lint", []):
    parts = i["path"].split("/")
    if len(parts) > 3 and parts[2] == "predicates":
        lint[parts[3]].append(i["code"])
preds_by = {}


def preds(f, acc):
    if isinstance(f, list):
        if f and f[0] in ("unary", "binary", "pred", "atom") and len(f) > 1 and isinstance(f[1], str):
            acc.add(f[1])
        for x in f:
            preds(x, acc)
    return acc


def q(formula):
    return T.q(formula)


def row(rid, formula):
    can, _ = elaborate_quantity(env, q(formula))
    ps = preds(formula, set()) & set(used)
    r = {"id": rid, "predicates": sorted(ps), "fallback": sorted(ps & fallback)}
    try:
        r["sentence"] = render_w6_sentence(env, can)
        r["round_trip"] = parse_w6_sentence(env, r["sentence"]) == can
        if not r["round_trip"]:
            r["why"] = "one reading, not the statement"
    except VEError as exc:
        r["round_trip"] = False
        r["why"] = f"{type(exc).__name__}: {str(exc)[:200]}"
    r["declared"] = r["round_trip"] and all(n in declared_ok for n in ps)
    r["plain"] = r["round_trip"] and not r["fallback"] and "classified as" not in r.get("sentence", "") \
        and "recorded relation" not in r.get("sentence", "")
    return r


if a.legend_only:
    print(json.dumps({"declared": len(wordings), "declared_used": sum(1 for n, t in wordings.items() if used.get(n) == t)}))
    for n, t in sorted(wordings.items()):
        if used.get(n) != t:
            print("REFUSED WORDING", n, json.dumps({"declared": t, "used": used[n], "lint": lint.get(n, [])}))
    sys.exit(0)
rules = [row(r["id"], r["formula"]) for r in T.rules()]
data = json.load(open(a.repo + "/usecases/eligibility/cases.json"))
cases = data["cases"] if isinstance(data, dict) and "cases" in data else data
defaults = data.get("defaults") if isinstance(data, dict) else None
seen, facts = set(), []
for case in cases:
    for f in T.profile_facts(case, defaults):
        k = T.key(f["formula"])
        if k in seen:
            continue
        seen.add(k)
        if preds(f["formula"], set()) & set(used):
            facts.append(row(f["id"], f["formula"]))

out = {
    "predicates": len(used), "predicates_plain": len(used) - len(fallback),
    "rules": len(rules), "rules_round_trip": sum(r["round_trip"] for r in rules),
    "rules_plain": sum(r["plain"] for r in rules), "rules_declared": sum(r["declared"] for r in rules),
    "facts": len(facts), "facts_round_trip": sum(r["round_trip"] for r in facts),
    "facts_plain": sum(r["plain"] for r in facts), "facts_declared": sum(r["declared"] for r in facts),
    "declared": len(wordings),
    "declared_used": sum(1 for n, t in wordings.items() if used.get(n) == t),
}
print(json.dumps(out))
refused = {n: {"declared": t, "used": used[n], "lint": lint.get(n, [])}
           for n, t in wordings.items() if used.get(n) != t}
for n, v in sorted(refused.items()):
    print("REFUSED WORDING", n, json.dumps(v))
c = collections.Counter(r.get("why", "")[:60] for r in rules + facts if not r["round_trip"])
for k, v in c.most_common():
    print("NO ROUND TRIP", v, k)
for kind, rows in (("rule", rules), ("fact", facts)):
    for r in [r for r in rows if r["plain"]][:a.show]:
        print("PLAIN", kind, r["id"], r["sentence"][:300])
    for r in [r for r in rows if not r["plain"] and r["round_trip"]][:a.show]:
        print("FALLBACK", kind, r["id"], r["sentence"][:300])
if a.out:
    json.dump({"summary": out, "refused": refused, "rules": rules, "facts": facts}, open(a.out, "w"), indent=1)
