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


def at0p(meta):
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
        assert case in nd.PREDICATES and len(x) <= 64
        # remove the unary terms of the previous run (vocabulary, open terms, stored relations)
        del preds[old_x], preds[old_b]
        terms = [t for t in terms if t["name"] not in (old_x, old_b)]
        gone += [old_x, old_b]
        # restore the category's case atom (spec_nd owns its words and factors)
        preds[case] = copy.deepcopy(nd.PREDICATES[case])
        terms.append(case_record(case))
        # the two binary terms on (claude_instance, situation)
        cat = category(words)
        preds[x] = nd.base([CLAUDE, SITUATION], "{0} knowingly and intentionally engages in {1}, which is a case of " + cat,
                           f"{SOURCE_U0173} Hard constraint {unit}: the instance of Claude knowingly and intentionally engages in the action of the "
                           f"situation as an action of the restricted category of {cat}. Which pairs of an instance and a situation these are is the "
                           f"open term {x}. It is not typed: VE does not know that knowing and intentionally engaging in it implies that the situation "
                           f"is a case of the category, so the guard states the case atom {case} beside it.")
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
        pdata["description"] = pdata["description"].replace(old_tail, NEW_TAIL.format(term=case, x=x, b=b))
    meta["open_terms"] = terms
    done = []
    for u in pilot._flat(meta["units"]):
        if u["id"] in HC_UNITS:
            n = int(u["id"][-1])
            case, _ = PER_UNIT[u["id"]]
            assert u["content"]["norm"]["guard"] == ["or", nd.un(OLD_KNOW + case, 0), nd.un(OLD_LIKELY + case, 0)], (u["id"], u["content"]["norm"]["guard"])
            assert u["content"]["norm"]["unless"] == [] and preds[u["content"]["norm"]["predicate"]]["arguments"] == [CLAUDE, SITUATION]
            u["content"]["norm"]["guard"] = guard(case, n)
            assert u["meaning"]["open"] == [OLD_KNOW + case, OLD_LIKELY + case], u["meaning"]
            u["meaning"]["open"] = [case, knowing(n), thinking(n)]
            done.append(u["id"])
    assert done == HC_UNITS, done
    for name in gone:
        drop_relation(meta["reading_sets"], name)
    return meta


def repair(meta):
    return at0p(meta)


def main():
    strict, strict_source = pilot.read(RUN / "base/all-strict.ve.md")
    meta, source = pilot.read(RUN / "base/translation-without-content.ve.md")
    meta = repair(meta)
    env = _environment(meta["environment"])
    meta["reading_sets"] = [pilot._reidentified(env, item) if all(r.get("content") is None for r in item["readings"]) else item
                            for item in meta["reading_sets"]]
    assert len(meta["reading_sets"]) == 3
    pilot.write(RUN / "translation-without-content.ve.md", meta, source)
    strict2 = repair(strict)
    (RUN / "readings").mkdir(exist_ok=True)
    pilot.write(RUN / "readings/all-strict.ve.md", strict2, strict_source)
    print("ok", len(meta["open_terms"]), [s["id"] for s in meta["reading_sets"]])


if __name__ == "__main__":
    main()
