"""ET-0: rewrite UDHR u042 (and, for P2, u043) in a copy of part01 with an event sort and a day sort.

No product code and no events@0: today's profile list and wire. The pinned part is read only; the copy is
written to the given output path. Variants:
  u042       P1 only (plan 4.2)
  u042u043   P1 and P2 (u043 with a reified `applicability` and the open comparison `heavier`)
  vocab042   diagnostic: P1's vocabulary only, u042 left as it is
  u042lean   diagnostic: u042 regulated on the act, without the `finding` sort (one quantifier, over days)

Usage: python3 et0_build.py <pinned translation-part01.ve.md> <out.ve.md> <variant>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from situation_ids import extend  # noqa: E402


def v(i):
    return ["var", i]


def un(p, *a):
    return ["unary", p, *a] if len(a) == 1 else ["binary", p, *a]


def ex(sort, body):
    return ["exists", sort, body]


def fa(sort, body):
    return ["forall", sort, body]


def conj(*xs):
    out = xs[-1]
    for x in reversed(xs[:-1]):
        out = ["and", x, out]
    return out


SORTS_042 = {
    "finding": {"description": "one finding that one person is guilty of one penal offence",
                "verbalisation": {"plural": "findings of guilt", "singular": "finding of guilt"}},
    "act": {"description": "one act or omission of one person",
            "verbalisation": {"plural": "acts", "singular": "act"}},
    "day": {"description": "one civil day",
            "verbalisation": {"plural": "days", "singular": "day"}},
}

PREDICATES_042 = {
    "finding_of_guilt_permitted": {
        "arguments": ["finding"],
        "description": "The finding of guilt is permitted to take place",
        "regulated": {"act": "{0} take place", "default": "unspecified", "role": "permission"}},
    "on_account_of": {
        "arguments": ["finding", "act"],
        "description": "The finding of guilt is on account of the act or omission",
        "verbalisation": "{0} is on account of {1}"},
    "committed_on": {
        "arguments": ["act", "day"],
        "description": "The act or omission is committed on the day",
        "verbalisation": "{0} is committed on {1}"},
    "constitutes_penal_offence_on": {
        "arguments": ["act", "day"],
        "description": "The act or omission constitutes a penal offence, under national or international law, on the day",
        "verbalisation": "{0} constitutes a penal offence under national or international law on {1}"},
}

# Context inside a guard: the rule's subject is var 0; each quantifier pushes one variable.
# "No finding of guilt may take place, if there is an act such that that finding of guilt is on account of that
#  act and there is a day such that that act is committed on that day and it is not the case that that act
#  constitutes a penal offence under national or international law on that day."
GUARD_042 = ex("act", conj(
    un("on_account_of", v(1), v(0)),
    ex("day", conj(un("committed_on", v(1), v(0)),
                   ["not", un("constitutes_penal_offence_on", v(1), v(0))]))))

UNIT_042 = {"id": "u042", "kind": "norm", "meaning": "specified", "span": [4151, 4351], "support": "none",
            "content": {"norm": {"guard": GUARD_042, "name": "u042-prohibited", "over": [],
                                 "predicate": "finding_of_guilt_permitted", "sign": False, "unless": []}}}

# Diagnostic variant "u042lean" (no finding sort): the permission is regulated on the act itself.
# "No act may be the ground of a finding of guilt, if there is a day such that that act is committed on that day and
#  it is not the case that that act constitutes a penal offence under national or international law on that day."
SORTS_042_LEAN = {k: SORTS_042[k] for k in ("act", "day")}
PREDICATES_042_LEAN = {
    "guilt_on_account_of_act_permitted": {
        "arguments": ["act"],
        "description": "The act or omission is permitted to be the ground on which a person is held guilty of a penal offence",
        "regulated": {"act": "{0} be the ground of a finding of guilt", "default": "unspecified", "role": "permission"}},
    **{k: PREDICATES_042[k] for k in ("committed_on", "constitutes_penal_offence_on")},
}
GUARD_042_LEAN = ex("day", conj(un("committed_on", v(1), v(0)),
                                ["not", un("constitutes_penal_offence_on", v(1), v(0))]))
UNIT_042_LEAN = {"id": "u042", "kind": "norm", "meaning": "specified", "span": [4151, 4351], "support": "none",
                 "content": {"norm": {"guard": GUARD_042_LEAN, "name": "u042-prohibited", "over": [],
                                      "predicate": "guilt_on_account_of_act_permitted", "sign": False,
                                      "unless": []}}}

SORTS_043 = {
    "imposition": {"description": "one imposition of one penalty on one person for one act or omission",
                   "verbalisation": {"plural": "impositions", "singular": "imposition"}},
    "penalty": {"description": "one penalty",
                "verbalisation": {"plural": "penalties", "singular": "penalty"}},
    "applicability": {"description": "one applicability of one penalty to one act or omission on one day",
                      "verbalisation": {"plural": "applicabilities", "singular": "applicability"}},
}

PREDICATES_043 = {
    "imposition_permitted": {
        "arguments": ["imposition"],
        "description": "The imposition of the penalty is permitted to take place",
        "regulated": {"act": "{0} take place", "default": "unspecified", "role": "permission"}},
    "imposes": {"arguments": ["imposition", "penalty"], "description": "The imposition imposes the penalty",
                "verbalisation": "{0} imposes {1}"},
    "imposed_for": {"arguments": ["imposition", "act"],
                    "description": "The imposition is for the act or omission",
                    "verbalisation": "{0} is for {1}"},
    "applicability_of": {"arguments": ["applicability", "penalty"],
                         "description": "The applicability is the applicability of the penalty",
                         "verbalisation": "{0} is of {1}"},
    "applicability_to": {"arguments": ["applicability", "act"],
                         "description": "The applicability is to the act or omission",
                         "verbalisation": "{0} is to {1}"},
    "applicable_on": {"arguments": ["applicability", "day"],
                      "description": "The applicability holds on the day",
                      "verbalisation": "{0} holds on {1}"},
    "heavier_than": {"arguments": ["penalty", "penalty"],
                     "description": "The first penalty is heavier than the second (the open term heavier)",
                     "verbalisation": "{0} is heavier than {1}"},
}

OPEN_043 = {"arguments": [], "decided_by": "unstated",
            "factors": ["which of two penalties is heavier"], "jurisdiction": "universal", "name": "heavier",
            "necessary": [], "precedents": [], "sufficient": [], "version": 1}

# "No imposition may take place, if there is a penalty such that that imposition imposes that penalty and there is
#  an act such that that imposition is for that act and there is a day such that that act is committed on that day
#  and there is an applicability such that that applicability is to that act and that applicability holds on that
#  day, and for each applicability, if that applicability is to that act and that applicability holds on that day,
#  then there is a penalty such that that applicability is of that penalty and the first penalty is heavier than it."
# Context at the innermost body: imposition, penalty p, act a, day d, then the inner variables.
_inner_every = fa("applicability", ["implies",
                                    conj(un("applicability_to", v(0), v(2)), un("applicable_on", v(0), v(1))),
                                    ex("penalty", conj(un("applicability_of", v(1), v(0)),
                                                       un("heavier_than", v(4), v(0))))])
_some_applicable = ex("applicability", conj(un("applicability_to", v(0), v(2)), un("applicable_on", v(0), v(1))))
GUARD_043 = ex("penalty", conj(
    un("imposes", v(1), v(0)),
    ex("act", conj(
        un("imposed_for", v(2), v(0)),
        ex("day", conj(un("committed_on", v(1), v(0)), _some_applicable, _inner_every))))))

UNIT_043 = {"id": "u043", "kind": "norm", "meaning": {"open": ["heavier"]}, "span": [4351, 4469],
            "support": "none",
            "content": {"norm": {"guard": GUARD_043, "name": "u043-prohibited", "over": [],
                                 "predicate": "imposition_permitted", "sign": False, "unless": []}}}


def main(src, out, variant):
    lines = Path(src).read_text().split("\n")
    assert lines[0] == "---" and lines[2] == "---", "front matter is one JSON line"
    fm = json.loads(lines[1])
    assert lines[1] == json.dumps(fm), "front matter round-trips"
    voc = fm["environment"]["vocabulary"]
    units = {u["id"]: i for i, u in enumerate(fm["units"])}
    sorts, preds, unit = ((SORTS_042_LEAN, PREDICATES_042_LEAN, UNIT_042_LEAN) if variant == "u042lean"
                          else (SORTS_042, PREDICATES_042, UNIT_042))
    for name in list(sorts) + list(preds):
        assert name not in voc["sorts"] and name not in voc["predicates"], name
    voc["sorts"].update(sorts)
    voc["predicates"].update(preds)
    if variant != "vocab042":          # diagnostic: the vocabulary alone, u042 left UNFORMALISED
        fm["units"][units["u042"]] = unit
    if variant == "u042u043":
        voc["sorts"].update(SORTS_043)
        voc["predicates"].update(PREDICATES_043)
        fm["open_terms"].append(OPEN_043)
        fm["units"][units["u043"]] = UNIT_043
    elif variant not in ("u042", "u042lean", "vocab042"):
        raise SystemExit(f"unknown variant {variant}")
    new_sorts = [s for s in voc["sorts"] if s not in json.loads(lines[1])["environment"]["vocabulary"]["sorts"]]
    # Each new base predicate, and `unsaid__<p>` for each new regulated predicate whose default is unspecified
    # (the situations list them as the existing ones do), gets an empty relation.
    added = [p for p in voc["predicates"] if p not in json.loads(lines[1])["environment"]["vocabulary"]["predicates"]]
    new_preds = [p for p in added if "regulated" not in voc["predicates"][p]] + [
        "unsaid__" + p for p in added if voc["predicates"][p].get("regulated", {}).get("default") == "unspecified"]
    renames = extend(fm, new_sorts, new_preds)
    print("situations renamed:", renames)
    lines[1] = json.dumps(fm)
    Path(out).write_text("\n".join(lines))


if __name__ == "__main__":
    main(*sys.argv[1:])
