#!/usr/bin/env python3
"""Run 20261015T0600Z: the repairs the audit of run 20261014T1800Z asked for.

    uv run python usecases/claude-constitution-pilot/run-20261015T0600Z/repair_20261015T0600Z.py
        # base/ -> translation-without-content.ve.md, readings/all-strict.ve.md, readings/all-strict-narrow.ve.md
    uv run python usecases/claude-constitution-pilot/run-20261015T0600Z/nd.py all   # adds the content of the four reading sets

1. u0165.s03 (UNFAITHFUL, audit 20261014T1800Z): the reading set split the case atoms into wide and narrow but not the attitude terms, so `thinks_quite_likely_3`
   was the same belief in both candidates and its record, like that of `knowingly_engages_3`, described the category with the unsplit phrase. Each candidate now has
   its own pair of binary open terms on (claude_instance, situation): knowingly_engages_3_wide / thinks_quite_likely_3_wide and knowingly_engages_3_narrow /
   thinks_quite_likely_3_narrow (s03_scope.py owns their wording and the guards). The two terms of the previous run are removed with every trace.
2. The record of `good_judgment` (u0052.s01) named argument sorts `action` and `context` that the document does not declare; it is now a pair of an instance of
   Claude and a situation (both declared).
3. DRI 2026-10-14 15:30Z (1): the carried sort `entity` gets the noun “thing” (plural “things”) instead of the reserved word “entity” (thing_noun).
4. The ledger entry of u0126 listed the removed open term `ethical_harm` (done in finish_20261015T0600Z.py: the ledger is not written here).

The AT-0p guards of u0165.s01 to s07 are the shape of the previous run (asserted below), which already is the plan's form
`( C_i(s) and knowingly_engages_i(c, s) ) or thinks_quite_likely_i(c, s)`; nothing is changed for them.
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

RUN_ID = "20261015T0600Z"
CLAUDE, SITUATION = nd.CLAUDE, nd.SITUATION
S03_PRED = "cyberweapon_creation_permitted"
GOOD_JUDGMENT = "good_judgment"
PREV_TAIL = ("the open terms knowingly_engages_3 (knowingly and intentionally engaging in the action as an action of the category) and thinks_quite_likely_3 "
             "(thinking it quite likely that the action falls into the category).")
NEW_TAIL = ("the open terms knowingly_engages_3_wide and thinks_quite_likely_3_wide for the wide candidate, and knowingly_engages_3_narrow and "
            "thinks_quite_likely_3_narrow for the narrow candidate (each pair: knowingly and intentionally engaging in the action as an action of that candidate's "
            "category, and thinking it quite likely that the action falls into it).")


def term_record(name, factors):
    return {"name": name, "arguments": [CLAUDE, SITUATION], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [], "factors": factors,
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


def replaced(items, old_names, new_items, key):
    """`items` with the entries named in old_names (in order) replaced, at the place of the first, by new_items."""
    out, placed = [], False
    for it in items:
        if key(it) in old_names:
            if not placed:
                out += new_items
                placed = True
            continue
        out.append(it)
    assert placed
    return out


def split_attitudes(meta, reading=None, keep_content=False):
    """u0165.s03's two attitude terms become one pair per candidate. `reading`: the candidate a companion document carries (None: no content)."""
    meta = copy.deepcopy(meta)
    old = [sc.OLD_KNOWING, sc.OLD_THINKING]
    vocab = meta["environment"]["vocabulary"]
    preds = vocab["predicates"]
    assert all(n in preds for n in old) and not any(n in preds for n in sc.ATTITUDES)
    # vocabulary: the four binary terms, at the place of the two
    new_preds = {}
    for r in sc.READINGS:
        (kw, kd), (tw, td) = sc.wording(r)
        new_preds[sc.KNOWING[r]] = nd.base([CLAUDE, SITUATION], kw, kd)
        new_preds[sc.THINKING[r]] = nd.base([CLAUDE, SITUATION], tw, td)
    ordered = {}
    for k, v in preds.items():
        if k == sc.OLD_KNOWING:
            ordered.update(new_preds)
        elif k != sc.OLD_THINKING:
            ordered[k] = v
    vocab["predicates"] = ordered
    # the regulated predicate's description names the open terms
    pdata = ordered[S03_PRED]
    assert PREV_TAIL in pdata["description"]
    pdata["description"] = pdata["description"].replace(PREV_TAIL, NEW_TAIL)
    # open terms
    terms = [t for t in meta["open_terms"] if t["name"] in old]
    assert [t["name"] for t in terms] == old and terms[0]["arguments"] == [CLAUDE, SITUATION] and terms[1]["arguments"] == [CLAUDE, SITUATION]
    k_factors, t_factors = terms[0]["factors"], terms[1]["factors"]
    assert k_factors == ["what counts as knowingly and intentionally engaging in the action"] and t_factors == ["how likely counts as quite likely"]
    new_terms = []
    for r in sc.READINGS:
        new_terms += [term_record(sc.KNOWING[r], list(k_factors)), term_record(sc.THINKING[r], list(t_factors))]
    meta["open_terms"] = replaced(meta["open_terms"], old, new_terms, lambda t: t["name"])
    # the unit and the stored models of the reading sets
    done = 0
    for u in pilot._flat(meta["units"]):
        if u["id"] != sc.UNIT:
            continue
        assert u["meaning"]["open"] == [*sc.ATOMS, *old], u["meaning"]
        u["meaning"]["open"] = [*sc.ATOMS, *sc.ATTITUDES]
        if keep_content:
            assert u["content"]["norm"]["guard"] == guard_before(reading), u["content"]["norm"]["guard"]
            u["content"] = sc.with_reading(u["content"], reading)
        else:
            assert "content" not in u or u["content"] is None
        done += 1
    assert done == 1
    for n in old:
        drop_relation(meta["reading_sets"], n)
    return meta


def guard_before(reading):
    """u0165.s03's guard in the previous run's companions (one shared pair of attitude terms)."""
    case = sc.category(reading)
    return ["or", ["and", case, ["binary", sc.OLD_KNOWING, ["var", 1], ["var", 0]]], ["binary", sc.OLD_THINKING, ["var", 1], ["var", 0]]]


def fix_good_judgment(meta):
    """The record of good_judgment named the undeclared sorts `action` and `context`; it is a pair of an instance of Claude and a situation."""
    meta = copy.deepcopy(meta)
    declared = set(meta["environment"]["vocabulary"]["sorts"])
    rec = [t for t in meta["open_terms"] if t["name"] == GOOD_JUDGMENT]
    assert len(rec) == 1 and rec[0]["arguments"] == ["action", "context"] and not set(rec[0]["arguments"]) & declared, rec
    rec[0]["arguments"] = [CLAUDE, SITUATION]
    assert set(rec[0]["arguments"]) <= declared
    return meta


def thing_noun(meta):
    """DRI 2026-10-14 15:30Z (1): the sort `entity` is declared with the noun “thing” (plural “things”), never the reserved word “entity”. Only the noun changes:
    the sort's id, its place in the document, and every formula stay as they were."""
    meta = copy.deepcopy(meta)
    sort = meta["environment"]["vocabulary"]["sorts"]["entity"]
    assert sort["verbalisation"] == {"singular": "entity", "plural": "entities"}, sort["verbalisation"]
    sort["verbalisation"] = {"singular": "thing", "plural": "things"}
    return meta


def check_at0p_shape(meta):
    """The seven hard-constraint guards are the plan's form (AT-0p), c = var 1, s = var 0; u0165.s03 is checked by split_attitudes."""
    n = 0
    for u in pilot._flat(meta["units"]):
        if u["id"].startswith("u0165.s0") and u["id"] != sc.UNIT and len(u["id"]) == 9:
            i = int(u["id"][-1])
            case = nd.HARD[i - 1][3]
            g = u["content"]["norm"]["guard"]
            assert g == ["or", ["and", nd.un(case, 0), ["binary", f"knowingly_engages_{i}", ["var", 1], ["var", 0]]],
                         ["binary", f"thinks_quite_likely_{i}", ["var", 1], ["var", 0]]], (u["id"], g)
            n += 1
    return n


def main():
    strict, strict_source = pilot.read(RUN / "base/all-strict.ve.md")
    narrow, narrow_source = pilot.read(RUN / "base/all-strict-narrow.ve.md")
    meta, source = pilot.read(RUN / "base/translation-without-content.ve.md")
    assert check_at0p_shape(strict) == 6
    meta = thing_noun(fix_good_judgment(split_attitudes(meta)))
    env = _environment(meta["environment"])
    meta["reading_sets"] = [pilot._reidentified(env, item) if all(r.get("content") is None for r in item["readings"]) else item
                            for item in meta["reading_sets"]]
    assert len(meta["reading_sets"]) == 4
    pilot.write(RUN / "translation-without-content.ve.md", meta, source)
    (RUN / "readings").mkdir(exist_ok=True)
    pilot.write(RUN / "readings/all-strict.ve.md", thing_noun(fix_good_judgment(split_attitudes(strict, "wide", keep_content=True))), strict_source)
    pilot.write(RUN / "readings/all-strict-narrow.ve.md", thing_noun(fix_good_judgment(split_attitudes(narrow, "narrow", keep_content=True))), narrow_source)
    print("ok", len(meta["open_terms"]), [s["id"] for s in meta["reading_sets"]])


if __name__ == "__main__":
    main()
