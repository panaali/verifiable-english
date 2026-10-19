#!/usr/bin/env python3
"""The operator ("can") sets as content-bearing reading sets on the soft chain, added to the S1 document by s1.py.

The main translation keeps u0062.s01, u0123.s02.p1 and u0123.s03 as reading sets without content (their permission
rules need norm-defaults@0, which readings@1 content cannot join). Here the three sets carry content (composition S1). u0123.s01.p1
is a reading set in the main document (run 20261005T0600Z, audit 20261004T1800Z: the reach of the limits of u0123.s03 is a
choice the sentence does not fix), but this soft-chain companion has no candidates for it, so here it has no content:

* a candidate is ONE content, so the several permission rules of the main document become one rule with a disjunctive guard and the
  six limits of u0123.s03 as exceptions; u0123.s03's prohibitions are one rule per candidate, the guard a disjunction of the six items;
* an ability candidate is an assertion over a base predicate `operator_can_supply` (an open term: the operator is able to give
  Claude the input; run 20261005T0600Z: for u0123.s03 the ability candidates say the operator is unable to *issue* an instruction of
  the six kinds, nothing about whether Claude would comply);
* the permission predicate needs a completion on the soft chain (`deny`): not the source's, an invention of this companion, named in
  the ledger. Where a pair is told apart by an outcome probe, the completion is what the other reading falls back on.
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

import spec_nd as nd  # noqa: E402
from ve.ast import formula_from_data  # noqa: E402
from ve.document import _environment  # noqa: E402
from ve.identity import meaning_id  # noqa: E402
from ve.readings import s1_content_meaning_id  # noqa: E402

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)

KINDS = ["input_is_specific_instructions", "input_is_persona", "input_is_information"]
S02 = ["instruction_role_play_custom_persona", "instruction_decline_or_withhold", "instruction_promote_own_products",
       "instruction_focus_on_tasks", "instruction_respond_differently"]
S01 = ["instruction_dishonest_looking_within_honesty"]
LEGIT = ["instruction_is_legitimate"]
WIDE = ["instruction_given_while_role_playing_persona"]
LIMITS = nd.LIMIT_ATOMS
# (set id, unit, [(candidate id, form, (guard atoms, extra conjuncts, exceptions))])
SETS = [
    ("modal-u0062-s01", "u0062.s01", [("permission", "perm", (KINDS, [], LIMITS)), ("ability", "able", (KINDS, [], []))]),
    ("modal-u0123-s02-p1", "u0123.s02.p1", [("permission", "perm", (S02, [], LIMITS)),
                                            ("conditional-permission", "perm", (S02, LEGIT, LIMITS)),
                                            ("ability", "able", (S02, LEGIT, []))]),
    ("scope-modal-u0123-s03", "u0123.s03", [("narrow-permission", "forbid", (LIMITS, [], [])),
                                            ("wide-permission", "forbid", (LIMITS, WIDE, [])),
                                            ("narrow-ability", "unable", (LIMITS, [], [])),
                                            ("wide-ability", "unable", (LIMITS, WIDE, []))]),
]


def disj(atoms):
    guard = None
    for a in atoms:
        f = nd.un(a, 0)
        guard = f if guard is None else ["or", guard, f]
    return guard


def ability(guard):
    return ["exists", nd.OPERATOR, ["exists", nd.OPERATOR_INPUT,
                                    ["and", ["binary", "operator_can_supply", ["var", 1], ["var", 0]], guard]]]


def content(form, spec, name):
    atoms, extra, unless = spec
    guard = disj(atoms)
    for a in extra:
        guard = ["and", guard, nd.un(a, 0)]
    if form in ("perm", "forbid"):
        return {"norm": {"name": name, "predicate": "operator_input_permitted", "sign": form == "perm", "guard": guard,
                         "unless": [nd.un(a, 0) for a in unless], "over": []}}, "norm"
    return (ability(guard) if form == "able" else ["not", ability(guard)]), "asserted"


def add(meta, main_meta):
    """Add the operator vocabulary, units and sets to the S1 document `meta` (in place); `main_meta` supplies the unit pieces."""
    vocab = meta["environment"]["vocabulary"]
    vocab["sorts"][nd.OPERATOR] = nd.SORTS[nd.OPERATOR]
    vocab["sorts"][nd.OPERATOR_INPUT] = nd.SORTS[nd.OPERATOR_INPUT]
    atoms = KINDS + S02 + S01 + LEGIT + LIMITS
    for name in atoms:
        vocab["predicates"][name] = copy.deepcopy(nd.PREDICATES[name])
    vocab["predicates"][WIDE[0]] = nd.base(
        [nd.OPERATOR_INPUT], "{0} is given while role-playing as a custom AI persona",
        "The operator input is given while role-playing as a custom AI persona; the wide reading of u0123.s03 puts this condition on "
        "every item of its list; open term.")
    vocab["predicates"]["operator_input_permitted"] = {
        "arguments": [nd.OPERATOR, nd.OPERATOR_INPUT],
        "description": "An operator is permitted to give Claude the input. Companion only: the soft chain needs a completion, `deny`; "
                       "the source states none.",
        "regulated": {"role": "permission", "default": "deny", "act": "{0} give Claude {1}"}}
    # not "is able …": a binary wording starting "is" makes unrelated English fail to parse (a finding of run 20261003T0600Z)
    vocab["predicates"]["operator_can_supply"] = nd.base(
        [nd.OPERATOR, nd.OPERATOR_INPUT], "{0} can supply {1}", "The operator is able to give Claude the input; open term.")
    terms = meta["open_terms"]
    have = {t["name"] for t in terms}
    for name in atoms + WIDE + ["operator_can_supply"]:
        if name not in have:
            terms.append({"name": name, "arguments": nd.OPEN_TERM_ARGS.get(name, [nd.OPERATOR, nd.OPERATOR_INPUT]),
                          "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
                          "factors": nd.OPEN_TERM_FACTORS.get(name, ["what counts as being able to"]),
                          "precedents": [], "jurisdiction": "claude_constitution", "version": 1})
    env = _environment(meta["environment"])

    # the environment grew, so every identity is recomputed and the old situations are searched again
    for old in meta["reading_sets"]:
        old.pop("situations", None)
        for r in old["readings"]:
            r["meaning_id"] = s1_content_meaning_id(env, old["id"], r)
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in old["readings"] if o["id"] != r["id"]}

    # the unit pieces of the main document replace the whole sentences of the soft companion
    main_units = {u["id"]: u for u in main_meta["units"]}
    wholes = ("u0062.s01", "u0123.s01", "u0123.s02", "u0123.s03")
    units = []
    for u in meta["units"]:
        pieces = [copy.deepcopy(x) for i, x in main_units.items() if i == u["id"] or i.rsplit(".p", 1)[0] == u["id"]] \
            if u["id"] in wholes else None
        units.extend(pieces or [u])
    meta["units"] = units
    for u in meta["units"]:
        if u["id"] in {s[1] for s in SETS} | {"u0123.s01.p1"}:
            u["content"] = None
    for sid, uid, cands in SETS:
        readings = []
        for cid, form, spec in cands:
            body, kind = content(form, spec, f"{sid}-{cid}")
            if kind == "norm":
                r = pilot.candidate(env, sid, cid, body, f"{cid} reading")
            else:
                r = {"id": cid, "kind": kind, "content": body, "meaning_id": meaning_id(env, formula_from_data(env, body)),
                     "admission": {"who": "translator", "why": f"{cid} reading", "distinguishing_models": {}}}
            readings.append(r)
        for r in readings:
            r["admission"]["distinguishing_models"] = {o["id"]: "pending" for o in readings if o["id"] != r["id"]}
        meta["reading_sets"].append({"id": sid, "unit": uid, "version": 1, "status": "open", "readings": readings})
    return meta


