#!/usr/bin/env python3
"""Run 20261014T1800Z: AT-0p, the hard-constraint guards bound to the acting Claude instance (DRI AT2; docs/spec/attitudes-PLAN.md on research/attitudes-p1).

    uv run python usecases/claude-constitution-pilot/run-20261014T1800Z/repair_20261014T1800Z.py
        # base/ -> translation-without-content.ve.md, readings/all-strict.ve.md
    uv run python usecases/claude-constitution-pilot/run-20261014T1800Z/nd.py all   # adds the content of the three "should" reading sets

The audit of run 20261013T0600Z rejected u0165.s01 to u0165.s07: both guard terms (`knowingly_<C>`, `thought_likely_<C>`) took only the situation, so
they did not bind the regulated instance of Claude and one instance's knowledge or belief counted against every instance. For hard constraint
i = 1..7 (u0165.s0i, category case atom C_i from spec_nd.HARD) the guard is now

    ( C_i(s) and knowingly_engages_i(c, s) )  or  thinks_quite_likely_i(c, s)        c = var 1 (the instance), s = var 0 (the situation)

with fourteen binary open terms on (claude_instance, situation). C_i(s) is restored (it is the category; with untyped terms VE cannot know that
knowing implies the category), and the previous run's unary terms `knowingly_<C>` and `thought_likely_<C>` are removed with every trace.
Reference: `git show research/attitudes-p1:research/attitudes/at0p.py` (written for the shape of run 20261012T1800Z; the asserts here start from this run's shape).
"""
from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
import s03_scope as sc  # noqa: E402
import spec_nd as nd  # noqa: E402
from ve.document import _environment  # noqa: E402

RUN_ID = "20261014T1800Z"
HC_UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
OLD_KNOW = "knowingly_"          # the previous run's unary terms, prefix + the category's case atom
OLD_LIKELY = "thought_likely_"
CLAUDE, SITUATION = nd.CLAUDE, nd.SITUATION
PER_UNIT = {unit: (term, words) for unit, _rule, _pred, term, _act, words in nd.HARD}
PRED_OF = {unit: pred for unit, _rule, pred, _term, _act, _words in nd.HARD}
SOURCE_U0173 = ("u0173.s01: the hard constraints are “centrally meant to apply to cases where Claude would either be knowingly and intentionally "
                "engaging in an action of the relevant restricted category, or where Claude thinks it quite likely that a given action would fall "
                "into such a category”.")
# the previous run's tail of each regulated predicate's description (replaced) and this run's
PREV_TAIL = ("The act phrase only points at the category; the source's own words for it are in the open terms {x} and {b} (the two alternatives "
             "of u0173.s01: Claude knowingly and intentionally doing it, or thinking it quite likely that the action falls into it).")
NEW_TAIL = ("The act phrase only points at the case; the source's own words for it are the case atom {term}, an open term, and the guard adds "
            "u0173.s01's two alternatives on the acting instance of Claude: the open terms {x} (knowingly and intentionally engaging in the action as "
            "an action of the category) and {b} (thinking it quite likely that the action falls into the category).")


def knowing(i):
    return f"knowingly_engages_{i}"


def thinking(i):
    return f"thinks_quite_likely_{i}"


def category(words):
    assert words.startswith("Claude ")
    return words[len("Claude "):]


def term_record(name, factors):
    return {"name": name, "arguments": [CLAUDE, SITUATION], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [], "factors": factors,
            "precedents": [], "jurisdiction": "claude_constitution", "version": 1}


def case_record(term):
    return {"name": term, "arguments": [SITUATION], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
            "factors": list(nd.OPEN_TERM_FACTORS[term]), "precedents": [], "jurisdiction": "claude_constitution", "version": 1}


def bi(pred, i, j):
    return ["binary", pred, ["var", i], ["var", j]]


def guard(case, i):
    """( C_i(s) and knowingly_engages_i(c, s) ) or thinks_quite_likely_i(c, s); c = var 1, s = var 0."""
    return ["or", ["and", nd.un(case, 0), bi(knowing(i), 1, 0)], bi(thinking(i), 1, 0)]


def drop_relation(x, name):
    if isinstance(x, dict):
        if isinstance(x.get("relations"), dict):
            x["relations"].pop(name, None)
        for v in x.values():
            drop_relation(v, name)
    elif isinstance(x, list):
        for v in x:
            drop_relation(v, name)


def at0p(meta, keep_content):
    """AT-0p on one document's front matter; asserts the starting shape (run 20261013T0600Z)."""
    meta = copy.deepcopy(meta)
    preds = meta["environment"]["vocabulary"]["predicates"]
    terms = list(meta["open_terms"])
    gone = []
    for n, unit in enumerate(HC_UNITS, 1):
        case, words = PER_UNIT[unit]
        old_x, old_b = OLD_KNOW + case, OLD_LIKELY + case
        x, b = knowing(n), thinking(n)
        assert old_x in preds and old_b in preds and case not in preds and x not in preds and b not in preds, unit
        assert (case in nd.PREDICATES or unit == sc.UNIT) and len(x) <= 64
        # remove the unary terms of the previous run (vocabulary, open terms, stored relations)
        del preds[old_x], preds[old_b]
        terms = [t for t in terms if t["name"] not in (old_x, old_b)]
        gone += [old_x, old_b]
        # restore the category's case atom (spec_nd owns its words and factors); u0165.s03's category is three atoms combined by a reading set
        if unit == sc.UNIT:
            terms, new_atoms = s03_atoms(preds, terms)
        else:
            preds[case] = copy.deepcopy(nd.PREDICATES[case])
            terms.append(case_record(case))
        # the two binary terms on (claude_instance, situation)
        cat = category(words)
        case_words = ("case atoms " + ", ".join(sc.ATOMS)) if unit == sc.UNIT else ("case atom " + case)
        preds[x] = nd.base([CLAUDE, SITUATION], "{0} knowingly and intentionally engages in {1}, which is a case of " + cat,
                           f"{SOURCE_U0173} Hard constraint {unit}: the instance of Claude knowingly and intentionally engages in the action of the "
                           f"situation as an action of the restricted category of {cat}. Which pairs of an instance and a situation these are is the "
                           f"open term {x}. It is not typed: VE does not know that knowing and intentionally engaging in it implies that the situation "
                           f"is a case of the category, so the guard states the {case_words} beside it.")
        preds[b] = nd.base([CLAUDE, SITUATION], "{0} thinks it quite likely that {1} is a case of " + cat,
                           f"{SOURCE_U0173} Hard constraint {unit}: the instance of Claude thinks it quite likely that the action of the situation falls "
                           f"into the restricted category of {cat}. It is that instance's belief, which need not be correct, so it does not need the "
                           f"case atom. Which pairs of an instance and a situation these are is the open term {b}; it is not typed.")
        terms.append(term_record(x, ["what counts as knowingly and intentionally engaging in the action"]))
        terms.append(term_record(b, ["how likely counts as quite likely"]))
        # the regulated predicate's description
        pdata = preds[PRED_OF[unit]]
        old_tail = PREV_TAIL.format(x=old_x, b=old_b)
        assert old_tail in pdata["description"], unit
        tail = NEW_TAIL.format(term=case, x=x, b=b)
        if unit == sc.UNIT:
            tail = tail.replace("the case atom " + case + ", an open term,", "the case atoms " + ", ".join(sc.ATOMS) + " (open terms, combined in "
                                "two ways by the reading set " + sc.SET_ID + "),")
        pdata["description"] = pdata["description"].replace(old_tail, tail)
    meta["open_terms"] = terms
    done = []
    for u in pilot._flat(meta["units"]):
        if u["id"] in HC_UNITS:
            n = int(u["id"][-1])
            case, _ = PER_UNIT[u["id"]]
            assert u["content"]["norm"]["guard"] == ["or", nd.un(OLD_KNOW + case, 0), nd.un(OLD_LIKELY + case, 0)], (u["id"], u["content"]["norm"]["guard"])
            assert u["content"]["norm"]["unless"] == [] and preds[u["content"]["norm"]["predicate"]]["arguments"] == [CLAUDE, SITUATION]
            assert u["meaning"]["open"] == [OLD_KNOW + case, OLD_LIKELY + case], u["meaning"]
            if u["id"] == sc.UNIT:
                # the rule is a reading set of two candidates (the strict companion carries the wide one); the unit keeps its place without content
                u["content"] = sc.with_reading(u["content"], "wide") if keep_content else None
                if not keep_content:
                    del u["content"]
                u["meaning"]["open"] = [*sc.ATOMS, knowing(n), thinking(n)]
            else:
                u["content"]["norm"]["guard"] = guard(case, n)
                u["meaning"]["open"] = [case, knowing(n), thinking(n)]
            done.append(u["id"])
    assert done == HC_UNITS, done
    for name in gone:
        drop_relation(meta["reading_sets"], name)
    return meta


def s03_atoms(preds, terms):
    """The three case atoms of u0165.s03 (the old single atom `damaging_cyberweapon_or_malicious_code` is gone for good)."""
    words = {sc.CYBERWEAPON: ("{0} is a case of Claude creating a cyberweapon", "The situation is a case of Claude creating a cyberweapon",
                              ["what counts as a cyberweapon"]),
             sc.MALICIOUS_CODE: ("{0} is a case of Claude creating malicious code", "The situation is a case of Claude creating malicious code",
                                 ["what counts as malicious code"]),
             sc.DAMAGE: ("{0} is a case in which what Claude creates could cause significant damage if deployed",
                         "In the situation, what Claude creates could cause significant damage if deployed",
                         ["what counts as significant damage"])}
    for name, (verb, desc, factors) in words.items():
        assert name not in preds
        preds[name] = nd.base([SITUATION], verb, desc + f"; which situations these are is the open term {name}. u0165.s03 says “Create cyberweapons or malicious "
                               "code that could cause significant damage if deployed”: the clause “that could cause significant damage if deployed” can follow both "
                               f"nouns or only “malicious code”, which the two candidates of the reading set {sc.SET_ID} state.")
        terms.append(case_record_of(name, factors))
    return terms, list(words)


def case_record_of(name, factors):
    return {"name": name, "arguments": [SITUATION], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [], "factors": factors,
            "precedents": [], "jurisdiction": "claude_constitution", "version": 1}


# ---- u0123.s02.p1: the operator's own products (audit 20261013T0600Z: the term took only the input, so every operator was permitted)
PROMOTE = "instruction_promote_own_products"


def bind_promote(meta):
    """`instruction_promote_own_products` becomes binary on (operator, operator_input): {1} promotes {0}'s own products. Its uses in the rules'
    guards become binary atoms (operator = var 1, input = var 0)."""
    meta = copy.deepcopy(meta)
    preds = meta["environment"]["vocabulary"]["predicates"]
    old = preds[PROMOTE]
    assert old["arguments"] == [nd.OPERATOR_INPUT], old
    preds[PROMOTE] = nd.base([nd.OPERATOR, nd.OPERATOR_INPUT], "{0} gives {1}, which is an instruction to promote its own products and services rather than those of competitors",
                             "The operator gives an input that is an instruction to promote the operator’s own products and services (u0123.s02: “the operator’s own”), "
                             "rather than those of competitors; which pairs of an operator and an input these are is the open term " + PROMOTE + ".")
    term = [t for t in meta["open_terms"] if t["name"] == PROMOTE]
    assert len(term) == 1 and term[0]["arguments"] == [nd.OPERATOR_INPUT], term
    term[0]["arguments"] = [nd.OPERATOR, nd.OPERATOR_INPUT]
    term[0]["factors"] = ["what counts as the operator’s own products and services", "what counts as a competitor"]
    count = [0]

    def walk(x):
        if isinstance(x, list):
            if x == ["unary", PROMOTE, ["var", 0]]:
                count[0] += 1
                return ["binary", PROMOTE, ["var", 1], ["var", 0]]
            return [walk(v) for v in x]
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items()}
        return x
    meta["units"] = walk(meta["units"])
    meta["reading_sets"] = walk(meta["reading_sets"])
    for item in meta["reading_sets"]:
        drop_relation(item, PROMOTE)  # the stored models are re-identified over the new arity
    return meta, count[0]


def scope_set(meta):
    """The reading set of u0165.s03, pending like the three "should" sets (nd.py gives it content)."""
    meta = copy.deepcopy(meta)
    template = copy.deepcopy(meta["reading_sets"][0])
    why = {"wide": "“Create cyberweapons or malicious code that could cause significant damage if deployed”: the relative clause follows both nouns, so a "
                   "cyberweapon too must be one that could cause significant damage if deployed.",
           "narrow": "“Create cyberweapons or malicious code that could cause significant damage if deployed”: the relative clause follows only “malicious code”, so "
                     "every cyberweapon is covered and only malicious code must be one that could cause significant damage if deployed."}
    item = {"id": sc.SET_ID, "unit": sc.UNIT, "version": 1, "status": "open", "models": template["models"], "readings": []}
    for r in sc.READINGS:
        item["readings"].append({"id": r, "kind": "norm", "meaning_id": f"pending-{r}-u0165-s03", "content": None,
                                 "admission": {"who": "translator", "why": why[r] + " Both attachments are possible in the English words; "
                                               "no reading comes from outside the sentence.", "distinguishing_models": {}}})
    for r in item["readings"]:
        r["admission"]["distinguishing_models"] = {o["id"]: next(iter(template["models"])) for o in item["readings"] if o["id"] != r["id"]}
    meta["reading_sets"].append(item)
    return meta


def repair(meta, keep_content=False):
    meta = at0p(meta, keep_content)
    meta, uses = bind_promote(meta)
    assert uses >= 1, uses
    return meta


def main():
    strict, strict_source = pilot.read(RUN / "base/all-strict.ve.md")
    meta, source = pilot.read(RUN / "base/translation-without-content.ve.md")
    meta = scope_set(repair(meta))
    env = _environment(meta["environment"])
    meta["reading_sets"] = [pilot._reidentified(env, item) if all(r.get("content") is None for r in item["readings"]) else item
                            for item in meta["reading_sets"]]
    assert len(meta["reading_sets"]) == 4
    pilot.write(RUN / "translation-without-content.ve.md", meta, source)
    strict2 = repair(strict, keep_content=True)
    (RUN / "readings").mkdir(exist_ok=True)
    pilot.write(RUN / "readings/all-strict.ve.md", strict2, strict_source)
    # the companion with u0165.s03's narrow reading (the probes ask both attachments; the main translation keeps both as the set scope-u0165-s03)
    narrow = copy.deepcopy(strict2)
    for u in pilot._flat(narrow["units"]):
        if u["id"] == sc.UNIT:
            u["content"] = sc.with_reading(u["content"], "narrow")
    pilot.write(RUN / "readings/all-strict-narrow.ve.md", narrow, strict_source)
    print("ok", len(meta["open_terms"]), [s["id"] for s in meta["reading_sets"]])


if __name__ == "__main__":
    main()
