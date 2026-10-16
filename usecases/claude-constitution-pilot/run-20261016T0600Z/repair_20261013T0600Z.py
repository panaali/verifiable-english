#!/usr/bin/env python3
"""Run 20261013T0600Z: repair of the seven hard-constraint units the audit of run 20261012T1800Z rejected (AUDIT-20261012T1800Z-received.md).

    uv run python usecases/claude-constitution-pilot/run-20261013T0600Z/repair_20261013T0600Z.py
        # base/ -> translation-without-content.ve.md, readings/all-strict.ve.md
    uv run python usecases/claude-constitution-pilot/run-20261013T0600Z/nd.py all   # adds the content of the three "should" reading sets

* u0165.s01 to u0165.s07: the previous guard was the category's case atom AND the open term `restricted_action_knowing_or_quite_likely`. The audit
  (all seven UNFAITHFUL, "weaken applicability") points out that u0173.s01 has TWO alternatives: Claude "knowingly and intentionally engaging in an
  action of the relevant restricted category", OR Claude "thinks it quite likely that a given action would fall into such a category". The second
  is a belief that need not be correct, so it cannot be conjoined with actual membership. The guard of each rule is now the two alternatives, in the
  source's order, as one flat "either ... or ..." of two open terms of the rule's own category C (the words of the bullet):

      knowingly_<C>      Claude would be knowingly and intentionally doing what the bullet says (the first alternative; it includes the category)
      thought_likely_<C> Claude thinks it quite likely that the action would be a case of what the bullet says (the second alternative)

  A flat "or" of two atoms is the form VE's English export reads back (a nested "(case and K) or B" does not: IdentityMetadataMismatch, block count),
  and it is the source's own sentence. The category's former case atom `<C>` and the single term of the previous run are removed with every
  trace (vocabulary, open terms, stored relations, the regulated predicate's description); the category's open factors move into the two new terms.
  Where the guard does not hold the rule still says nothing (completion unspecified): unclear or unknowing cases are not decided by the constraint.
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

RUN_ID = "20261013T0600Z"
HC_UNITS = [f"u0165.s0{i}" for i in range(1, 8)]
OLD_KNOW = "restricted_action_knowing_or_quite_likely"
KNOWING = "knowingly_"
LIKELY = "thought_likely_"
PER_UNIT = {unit: (term, words) for unit, _rule, _pred, term, _act, words in nd.HARD}
OLD_DESC_TAIL = "The act phrase only points at the case; the source's own words for it are the case atom {term}, an open term."
NEW_DESC_TAIL = ("The act phrase only points at the category; the source's own words for it are in the open terms {x} and {b} (the two alternatives "
                 "of u0173.s01: Claude knowingly and intentionally doing it, or thinking it quite likely that the action falls into it).")


def knowing_text(words):
    assert words.startswith("Claude ")
    return "Claude knowingly and intentionally " + words[len("Claude "):]


def term_entry(name, factors):
    return {"name": name, "arguments": [nd.SITUATION], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [], "factors": factors,
            "precedents": [], "jurisdiction": "claude_constitution", "version": 1}


def drop_relation(x, name):
    if isinstance(x, dict):
        if isinstance(x.get("relations"), dict):
            x["relations"].pop(name, None)
        for v in x.values():
            drop_relation(v, name)
    elif isinstance(x, list):
        for v in x:
            drop_relation(v, name)


def repair(meta):
    meta = copy.deepcopy(meta)
    preds = meta["environment"]["vocabulary"]["predicates"]
    assert OLD_KNOW in preds
    del preds[OLD_KNOW]
    terms = [t for t in meta["open_terms"] if t["name"] != OLD_KNOW]
    assert len(terms) == len(meta["open_terms"]) - 1
    by_term = {t["name"]: t for t in terms}
    pred_of = {pred: unit for unit, _rule, pred, _t, _a, _w in nd.HARD}
    for unit in HC_UNITS:
        case, words = PER_UNIT[unit]
        x, b = KNOWING + case, LIKELY + case
        assert x not in preds and b not in preds and case in preds and len(x) <= 64 and len(b) <= 64
        old_factors = list(by_term[case]["factors"])
        del preds[case]
        terms = [t for t in terms if t["name"] != case]
        preds[x] = nd.base([nd.SITUATION], "{0} is a case of " + knowing_text(words),
                           f"u0173.s01, first alternative: the hard constraints are “centrally meant to apply to cases where Claude would either be knowingly and "
                           f"intentionally engaging in an action of the relevant restricted category, or …”: here the category of {words}. It is the knowing and "
                           f"intentional doing of what the bullet says (it includes the category). Which situations these are is the open term {x}.")
        preds[b] = nd.base([nd.SITUATION], "{0} is a case in which Claude thinks it quite likely that the action would be a case of " + words,
                           f"u0173.s01, second alternative: the hard constraints are “centrally meant to apply to cases where … Claude thinks it quite likely "
                           f"that a given action would fall into such a category”: here the category of {words}. It is Claude's belief, which need not be correct. "
                           f"Which situations these are is the open term {b}.")
        terms.append(term_entry(x, [*old_factors, "what counts as Claude knowingly engaging in it", "what counts as Claude intentionally engaging in it"]))
        terms.append(term_entry(b, [*old_factors, "what counts as Claude thinking it so", "how likely counts as quite likely"]))
        # the regulated predicate's description named the case atom
        pdata = preds[[p for p, u in pred_of.items() if u == unit][0]]
        assert OLD_DESC_TAIL.format(term=case) in pdata["description"], unit
        pdata["description"] = pdata["description"].replace(OLD_DESC_TAIL.format(term=case), NEW_DESC_TAIL.format(x=x, b=b))
    meta["open_terms"] = terms
    done = []
    for u in pilot._flat(meta["units"]):
        if u["id"] in HC_UNITS:
            case, _ = PER_UNIT[u["id"]]
            x, b = KNOWING + case, LIKELY + case
            guard = u["content"]["norm"]["guard"]
            assert guard == ["and", ["unary", case, ["var", 0]], ["unary", OLD_KNOW, ["var", 0]]], (u["id"], guard)
            assert u["content"]["norm"]["unless"] == []
            u["content"]["norm"]["guard"] = ["or", nd.un(x, 0), nd.un(b, 0)]
            assert u["meaning"]["open"] == [case, OLD_KNOW], u["meaning"]
            u["meaning"]["open"] = [x, b]
            done.append(u["id"])
    assert done == HC_UNITS, done
    drop_relation(meta["reading_sets"], OLD_KNOW)
    for unit in HC_UNITS:
        drop_relation(meta["reading_sets"], PER_UNIT[unit][0])
    return meta


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
