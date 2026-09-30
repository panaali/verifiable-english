"""Reading-set candidates for the right units: complete right blocks, one per admissible reading.

A candidate is a `right` block (holder, lines). The axes a candidate is labelled on are the ones the
source leaves open: incident (claim or liberty), bearer (state or everyone), polarity (refrain or secure).
Force is strict for every candidate; the report says why (SUMMARY.md, metrics.json).
"""
from __future__ import annotations

from table import RIGHT_UNITS


def _slots(act: str, bearer: str) -> str:
    return act.replace("{0}", f"the {bearer}").replace("{1}", "the person")


def predicates_for(uid: str, entry: dict) -> dict:
    """Regulated predicates the unit's candidates need (obligation role, completion 'deny' = not required).

    One predicate per polarity over (bearer, holder); the bearer sort holds states, groups and persons, and the
    'state' reading is the same duty guarded by is_state, so the two bearer readings share their predicates.
    """
    key = entry["key"]
    holder = entry.get("holder", "person")
    out = {}
    for polarity, act in (("avoid", entry["neg"]), ("secure", entry["pos"])):
        out[f"{polarity}_{key}_required"] = {
            "arguments": ["bearer", holder],
            "description": ("The bearer is required to " + _slots(act[len("{0} "):], "bearer")
                            + f". Source clause: {entry['full']}."),
            "regulated": {"role": "obligation", "default": "deny", "act": act}}
    if "lib" in entry:
        out[f"person_may_{key}"] = {
            "arguments": ["person"],
            "description": ("The person is permitted to " + entry["lib"][len("{0} "):]
                            + f". Source clause: {entry['full']}."),
            "regulated": {"role": "permission", "default": "deny", "act": entry["lib"]}}
    return out


def _norm(name, predicate, sign=True):
    return {"name": name, "predicate": predicate, "sign": sign, "guard": ["top"], "unless": [], "over": []}


IS_STATE = ["unary", "is_state", ["var", 1]]


def candidates(uid: str, entry: dict) -> list[dict]:
    """[{id, labels, content, why}] for one right unit."""
    key, right, holder = entry["key"], entry["right"], entry.get("holder", "person")
    bearers, bearer_reason = entry.get("bearers", (["state", "anyone"], None))
    result = []
    for bearer_axis in ("state", "anyone"):
        if bearer_axis not in bearers:
            continue
        for polarity, verb in (("negative", "avoid"), ("positive", "secure")):
            norm = _norm(f"{verb}-{right}-by-{bearer_axis}", f"{verb}_{key}_required")
            if bearer_axis == "state":
                norm["guard"] = IS_STATE
            line = {"kind": "claim", "holder_slot": None, "cites": {}, "norm": norm}
            act = entry["neg"] if polarity == "negative" else entry["pos"]
            who = "every state" if bearer_axis == "state" else "every state, group and person"
            why = (f"Claim reading: {who} must {act[len('{0} '):].replace('{1}', 'each holder')} "
                   f"({'the duty is to avoid harming the right' if polarity == 'negative' else 'the duty is to secure the right'}; "
                   f"the source names no bearer and no polarity, so this is the translator's candidate"
                   f"{'; ' + bearer_reason if bearer_reason else ''}).")
            result.append({"id": f"{bearer_axis}_{polarity}",
                           "content": {"right": {"name": right, "holder": holder, "guard": ["top"], "lines": [line]}},
                           "labels": {"incident": "claim", "bearer": bearer_axis, "polarity": polarity, "force": "strict"},
                           "why": why})
    if "lib" in entry:
        line = {"kind": "liberty", "holder_slot": None, "cites": {}, "norm": _norm(f"person-may-{right}", f"person_may_{key}")}
        result.append({"id": "liberty", "content": {"right": {"name": right, "holder": "person", "guard": ["top"],
                                                              "lines": [line]}},
                       "labels": {"incident": "liberty", "force": "strict"},
                       "why": "Liberty reading: every person may " + entry["lib"][len("{0} "):].replace("{0}", "the person")
                              + " (the holder is permitted; no duty on anyone follows from this line)."})
    return result
