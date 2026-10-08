#!/usr/bin/env python3
"""Reading sets with checked content on the main chain (`norm-defaults@0`, completion unspecified), RD-2b.

    uv run python usecases/claude-constitution-pilot/run-20261008T1800Z/nd.py [force|op|s01p1|all]

At `ve-green-rd-6a` a reading set with content beside `norm-defaults@0` was refused (`readings/s1.ve.md` therefore
moved every duty to the soft chain and completed it with `deny`, which the source does not say). From RD-2b on such a
document loads, checks and renders, one compatible choice at a time (the enumerated route, at most 64 choices).
This script rebuilds the reading sets on the main translation's own chain, with no completion of mine:

* the strict candidate of each "should" set is the strict rule of `readings/all-strict.ve.md` (norm-defaults
  predicates, completion unspecified); the defeasible candidate stays a candidate WITHOUT content (it needs
  `soft-norms@0`, which is a different chain), which the language allows (a pending candidate, composition S1 1.2);
* the operator ("can") sets get one content per candidate where the candidate is one self-contained content:
  a permission rule (the six limits of u0123.s03 as its exceptions), a prohibition rule (u0123.s03), or an ability
  assertion over the base predicate `operator_can_supply` (an open term);
* the documents are SPLIT by hand into groups of sets whose choices multiply to at most 64, because the enumerated
  route refuses more ("UNKNOWN: more than 64 compatible readings") and the companion split (RD-4a) is not merged.

Not part of the translation (`translation.ve.md` keeps its sets as they were); these are measurement documents.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)

import spec_nd as nd  # noqa: E402
from ve.ast import formula_from_data  # noqa: E402
from ve.document import _environment, check_document, load_document  # noqa: E402
from ve.errors import VEError  # noqa: E402
from ve.identity import meaning_id  # noqa: E402
from ve.readings import s1_content_meaning_id  # noqa: E402

OUT = RUN / "readings"
FORCE = ["force-u0036-s05", "force-u0125-s04-p2", "force-u0156-s03", "force-u0263-s04-p2"]
OPSETS = ["modal-u0062-s01", "modal-u0123-s02-p1", "scope-modal-u0123-s03"]
S01P1 = ["modal-u0123-s01-p1"]
KINDS = ["input_is_specific_instructions", "input_is_persona", "input_is_information"]
S02 = ["instruction_role_play_custom_persona", "instruction_decline_or_withhold", "instruction_promote_own_products",
       "instruction_focus_on_tasks", "instruction_respond_differently"]
S01 = ["instruction_dishonest_looking_within_honesty"]
LEGIT = ["instruction_is_legitimate"]
WIDE = "instruction_given_while_role_playing_persona"
LIMITS = nd.LIMIT_ATOMS
GROUPS = {"force": FORCE, "op": OPSETS, "s01p1": S01P1, "all": FORCE + OPSETS + S01P1}


def disj(atoms):
    guard = None
    for a in atoms:
        f = nd.un(a, 0)
        guard = f if guard is None else ["or", guard, f]
    return guard


def ability(guard):
    return ["exists", nd.OPERATOR, ["exists", nd.OPERATOR_INPUT,
                                    ["and", ["binary", "operator_can_supply", ["var", 1], ["var", 0]], guard]]]


def op_content(form, atoms, extra, unless, name):
    guard = disj(atoms)
    for a in extra:
        guard = ["and", guard, nd.un(a, 0)]
    if form in ("perm", "forbid"):
        return {"norm": {"name": name, "predicate": "operator_input_permitted", "sign": form == "perm", "guard": guard,
                         "unless": unless, "over": []}}, "norm"
    return (ability(guard) if form == "able" else ["not", ability(guard)]), "asserted"


def narrow_unless():
    return [nd.un(a, 0) for a in LIMITS]


def wide_unless():
    return [["and", disj(LIMITS), nd.un(WIDE, 0)]]


# set id -> {candidate id: (form, guard atoms, extra conjuncts, exceptions)}. One content per candidate; where the
# main translation's note says "limited by whatever u0123.s03 forbids under its own reading", the content is the
# narrow-limits form (the one `readings/all-strict.ve.md` elaborated, audit 20261002T0620Z).
OPCONTENT = {
    "modal-u0062-s01": {"permission": ("perm", KINDS, [], narrow_unless()), "ability": ("able", KINDS, [], [])},
    "modal-u0123-s02-p1": {"permission": ("perm", S02, [], narrow_unless()),
                           "conditional-permission": ("perm", S02, LEGIT, narrow_unless()),
                           "ability": ("able", S02, LEGIT, [])},
    "scope-modal-u0123-s03": {"narrow-permission": ("forbid", LIMITS, [], []),
                              "wide-permission": ("forbid", LIMITS, [WIDE], []),
                              "narrow-ability": ("unable", LIMITS, [], []),
                              "wide-ability": ("unable", LIMITS, [WIDE], [])},
    "modal-u0123-s01-p1": {"permission-narrow-limits": ("perm", S01, [], narrow_unless()),
                           "permission-wide-limits": ("perm", S01, [], wide_unless()),
                           "permission-no-limits": ("perm", S01, [], [])},
}


# The defeasible candidate of a "should" set, on the main chain: the strict rule with ONE exception the text does not
# name (the soft chain's `exception: unstated`, here a base predicate that is an open term, so `norm-defaults@0` need
# not be left). set id -> (exception predicate, its sorts, its English, the exception's variable indexes in the guard)
EXCEPTIONS = {
    "force-u0036-s05": ("exception_to_asking_for_clarification", [nd.SITUATION],
                        "{0} is an exception to asking for clarification in cases of genuine ambiguity", [0]),
    "force-u0125-s04-p2": ("exception_to_never_denying_being_claude", [nd.CLAUDE],
                           "{0} has an exception to never directly denying being Claude", [0]),
    "force-u0156-s03": ("exception_to_not_deceiving_about_system_prompt", [nd.CLAUDE, nd.USER],
                        "{0} has an exception to not deceiving {1} about a system prompt", [1, 0]),
    "force-u0263-s04-p2": ("exception_to_complying_with_exploit_instruction", [nd.CLAUDE, nd.SITUATION],
                           "{0} has an exception to complying with an instruction against unintended exploits in {1}",
                           [1, 0]),
}


def with_exception(content, set_id):
    name, sorts, _, vars_ = EXCEPTIONS[set_id]
    atom = ["unary", name, ["var", vars_[0]]] if len(vars_) == 1 else ["binary", name, ["var", vars_[0]], ["var", vars_[1]]]
    out = copy.deepcopy(content)
    out["norm"]["unless"] = [atom]
    return out


def source_word(source, span):
    a, b = span
    text = source[a:b].decode("utf-8")
    m = re.search("shouldn’t|should not|should|must not|must|shall not|shall|always|never", text)
    start = a + len(text[:m.start()].encode("utf-8"))
    return [start, start + len(m.group(0).encode("utf-8"))]


def build(group, main_meta, source, strict_meta):
    sets_wanted = GROUPS[group]
    meta = copy.deepcopy(main_meta)
    env_data = meta["environment"]
    env_data["profiles"] = sorted({*env_data["profiles"], "readings@1"})
    vocab = env_data["vocabulary"]
    if any(s in sets_wanted for s in OPSETS + S01P1):
        vocab["predicates"][WIDE] = nd.base([nd.OPERATOR_INPUT], "{0} is given while role-playing as a custom AI persona",
                                            "The operator input is given while role-playing as a custom AI persona; the "
                                            "wide reading of u0123.s03 puts this condition on every item of its list; "
                                            "open term.")
        vocab["predicates"]["operator_can_supply"] = nd.base(
            [nd.OPERATOR, nd.OPERATOR_INPUT], "{0} can supply {1}",
            "The operator is able to give Claude the input; open term.")
        have = {t["name"] for t in meta["open_terms"]}
        for name, args in ((WIDE, [nd.OPERATOR_INPUT]), ("operator_can_supply", [nd.OPERATOR, nd.OPERATOR_INPUT])):
            if name not in have:
                meta["open_terms"].append({"name": name, "arguments": args, "decided_by": "unresolved_decider",
                                           "necessary": [], "sufficient": [],
                                           "factors": ["what counts as being able to" if name != WIDE else
                                                       "what counts as role-playing a custom AI persona"],
                                           "precedents": [], "jurisdiction": "claude_constitution", "version": 1})
    if any(s in sets_wanted for s in OPSETS + S01P1):
        # an assertion candidate is rendered over the whole lexicon, which Lean refuses when an act wording holds an
        # apostrophe ("system prompt's"): V3, found at ve-green-lf-15b; the wording is changed in these documents only
        acts = {"system_prompt_compliance_required": "{0} comply with the system prompt instructions in {1}",
                "system_prompt_deception_permitted": "{0} actively deceive {1} about system prompt existence-or-content"}
        for name, act in acts.items():
            vocab["predicates"][name]["regulated"]["act"] = act
    for set_id, (name, sorts, english, _) in EXCEPTIONS.items():
        if set_id in sets_wanted:
            vocab["predicates"][name] = nd.base(
                sorts, english, "An exception the source does not name, which the defeasible reading of its sentence "
                                "allows; open term, decided by nobody the source names.")
            meta["open_terms"].append({"name": name, "arguments": sorts, "decided_by": "unresolved_decider",
                                       "necessary": [], "sufficient": [],
                                       "factors": ["the source names no exception"], "precedents": [],
                                       "jurisdiction": "claude_constitution", "version": 1})
    env = _environment(env_data)
    strict_units = {u["id"]: u for u in pilot._flat(strict_meta["units"])}
    spans = {u["id"]: u["span"] for u in pilot._flat(meta["units"])}
    new_sets = []
    for item in main_meta["reading_sets"]:
        if item["id"] not in sets_wanted:
            continue
        item = copy.deepcopy(item)
        item.pop("models", None)
        readings = []
        for r in item["readings"]:
            if item["id"] in FORCE and r["id"] == "strict":
                content = strict_units[item["unit"]]["content"]
                r = {**r, "content": content}
                r["meaning_id"] = s1_content_meaning_id(env, item["id"], r)
            elif item["id"] in FORCE and r["id"] == "default":
                r = {**r, "content": with_exception(strict_units[item["unit"]]["content"], item["id"])}
                r["meaning_id"] = s1_content_meaning_id(env, item["id"], r)
            elif item["id"] in OPCONTENT and r["id"] in OPCONTENT[item["id"]]:
                form, atoms, extra, unless = OPCONTENT[item["id"]][r["id"]]
                body, kind = op_content(form, atoms, extra, unless, f"{item['id']}-{r['id']}")
                r = {**r, "kind": kind, "content": body}
                r["meaning_id"] = (s1_content_meaning_id(env, item["id"], r) if kind == "norm" else
                                   meaning_id(env, formula_from_data(env, body)))
            else:  # a candidate without content (the defeasible reading: it needs the soft chain)
                r = {**r, "content": None}
                r["meaning_id"] = _pending_id(env, item["id"], r)
            readings.append(r)
        for r in readings:
            r["admission"] = {**r["admission"], "distinguishing_models": {o["id"]: "pending" for o in readings
                                                                         if o["id"] != r["id"]}}
        if item["id"] in FORCE:
            item["source_word"] = source_word(source, spans[item["unit"]])
        item["readings"] = readings
        new_sets.append(item)
    meta["reading_sets"] = new_sets
    # units of the sets left out keep their place without a set (their content is null already)
    return meta


def _pending_id(env, set_id, reading):
    old = reading.get("meaning_id", "")
    return old


def find_situations(meta):
    """`tools/readings_s1_pilot.find_situations` under the completion: the frame is the filled document Lean's
    `readings-elaborate` answers before any situation is recorded (RD-2b)."""
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import Decoded, guard_base, record_situations, search
    units = [{"id": u["id"], "kind": u["kind"], "content": u.get("content")} for u in pilot._flat(meta["units"])]
    document = document_wire(units, meta["reading_sets"])
    [row] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": meta["environment"],
                       "document": document}])
    if row.get("status") != "ok" or "filled" not in row:
        raise VEError("elaborate refused: " + json.dumps(row)[:600])
    decoded = Decoded(meta["environment"], document, row["filled"], row.get("fill_premises"))
    missing, limits, sets = [], [], []
    for item in meta["reading_sets"]:
        R = decoded.doc.set_by_id(item["id"])
        if R is None or not Decoded.content_bearing(R):
            sets.append(item)
            continue
        with_content = [i for i, a in enumerate(R.candidates) if a.content is not None]
        if len(with_content) < 2:  # nothing to separate: a pending candidate needs no situation
            sets.append(item)
            continue
        hints = [guard_base(decoded, item["id"], i) for i in with_content]
        if item["id"] in OPCONTENT:  # the exceptions' atoms true as well: the situation that tells the limits apart
            rich = copy.deepcopy(hints[0])
            elem = rich["domains"][nd.OPERATOR_INPUT][0]
            for atom in (LIMITS[0], WIDE):
                if [elem] not in rich["relations"].get(atom, []):
                    rich["relations"].setdefault(atom, []).append([elem])
            hints.append(rich)
        try:
            found = search(meta["environment"], document, item["id"], max_size=1, hints=hints, decoded=decoded,
                           filled=row)
        except VEError as exc:
            limits.append((item["id"], str(exc)))
            sets.append(item)
            continue
        missing += [(item["id"], x, y) for (x, y), hit in found.items() if hit is None and x < y]
        sets.append(record_situations(item, {k: v for k, v in found.items() if v is not None}))
    return {**meta, "reading_sets": sets}, missing, limits


def main(argv):
    group = argv[1] if len(argv) > 1 else "force"
    main_meta, source = pilot.read(RUN / "translation.ve.md")
    strict_meta, _ = pilot.read(RUN / "readings/all-strict.ve.md")
    meta = build(group, main_meta, source, strict_meta)
    started = time.monotonic()
    meta, missing, limits = find_situations(meta)
    searched = round(time.monotonic() - started, 1)
    path = OUT / f"nd-{group}.ve.md"
    pilot.write(path, meta, source)
    result = {"document": str(path.relative_to(ROOT)), "group": group, "search_seconds": searched,
              "sets": [{"set": i["id"], "unit": i["unit"], "candidates": [
                  {"id": r["id"], "content": "none" if r["content"] is None else ("norm" if r["kind"] == "norm" else "assertion")}
                  for r in i["readings"]]} for i in meta["reading_sets"]],
              "pairs_without_situation": missing, "search_limits": limits}
    started = time.monotonic()
    try:
        load_document(path)
    except VEError as exc:
        result.update({"admitted": False, "rejection": getattr(exc, "message", str(exc))})
        (OUT / f"nd-{group}-result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps(result, indent=1, ensure_ascii=False))
        return 1
    result["load_seconds"] = round(time.monotonic() - started, 1)
    result["admitted"] = True
    started = time.monotonic()
    report = check_document(path)
    result["check_seconds"] = round(time.monotonic() - started, 1)
    (OUT / f"nd-{group}-check.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    result["readings"] = report.get("readings")
    result["premises"] = report.get("premises")
    result["bytes_by_status"] = report["coverage"]["bytes_by_status"]
    (OUT / f"nd-{group}-result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("readings",)}, indent=1, ensure_ascii=False)[:6000])
    r = report.get("readings") or {}
    print(json.dumps({k: v for k, v in r.items() if k != "sets"}, indent=1, ensure_ascii=False)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
