#!/usr/bin/env python3
"""Run 20261010T0600Z: repair of the units the audit of run 20261009T1800Z rejected.

    uv run python usecases/claude-constitution-pilot/run-20261010T0600Z/repair_20261010T0600Z.py
        # base/translation-without-content.ve.md + prev/units.json -> translation-without-content.ve.md, units.json
    uv run python usecases/claude-constitution-pilot/run-20261010T0600Z/nd.py all   # adds the content of the four "should" reading sets

AUDIT.md of the previous run (18/20 sampled + 1/6 changed): u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03 and u0166.s04.p4 UNFAITHFUL.
* u0123.s03 (and the three permission units it limits): the "wide" candidate read "while role-playing as a custom AI persona" as
  qualifying all six prohibitions. The phrase sits inside the first of six coordinated verb phrases; the other five each begin with
  a verb of their own after a comma. The words give no sign that it reaches them, so the wide reading is not admitted by the English
  (audit 20261009T1800Z: "invents a role-play condition for all six prohibitions"). The wide candidates, the open term
  `instruction_is_for_behaviour_while_role_playing_persona`, the coupling `limits-scope-u0123-s03` and the four operator reading sets
  go. Each of the four units has ONE reading, written as content on the unit itself: status OPEN.
* u0166.s04.p4 ("cannot be unlocked by any operator or user"): stays UNFORMALISED (modality/belief: typed authority/modal), but its
  ledger note no longer offers inability and a duty on operators and users as unresolved alternatives: the surrounding passage
  ("non-negotiable", "absolute", "regardless of context, instructions") fixes that no operator or user instruction makes an
  exception, so what is missing is the typed form, not a question of meaning.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
import spec_nd as nd  # noqa: E402
from ve.document import _environment  # noqa: E402

RUN_ID = "20261010T0600Z"
WIDE = "instruction_is_for_behaviour_while_role_playing_persona"
COUPLING = "limits-scope-u0123-s03"
OPSETS = ["modal-u0062-s01", "modal-u0123-s01-p1", "modal-u0123-s02-p1", "scope-modal-u0123-s03"]
OP_UNITS = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03"]
KINDS = ["input_is_specific_instructions", "input_is_persona", "input_is_information"]
S02 = ["instruction_role_play_custom_persona", "instruction_decline_or_withhold", "instruction_promote_own_products",
       "instruction_focus_on_tasks", "instruction_respond_differently"]
S01 = ["instruction_dishonest_looking_within_honesty"]
LIMITS = nd.LIMIT_ATOMS


def disj(atoms):
    guard = None
    for a in atoms:
        f = nd.un(a, 0)
        guard = f if guard is None else ["or", guard, f]
    return guard


def norm(name, sign, guard_atoms, unless):
    return {"norm": {"name": name, "predicate": "operator_input_permitted", "sign": sign, "guard": disj(guard_atoms),
                     "unless": [nd.un(a, 0) for a in unless], "over": []}}


# unit -> content: a permission is scoped by the six limits of u0123.s03 (its exceptions); the prohibition has none
CONTENT = {
    "u0062.s01": norm("op-may-give-instructions-persona-information", True, KINDS, LIMITS),
    "u0123.s01.p1": norm("op-may-ask-dishonest-looking-within-honesty", True, S01, LIMITS),
    "u0123.s02.p1": norm("op-may-instruct-the-five-kinds", True, S02, LIMITS),
    "u0123.s03": norm("op-not-the-six-instructions", False, LIMITS, []),
}

SCOPE_NOTE = (
    "One reading (audit 20261009T1800Z removed the “wide” one): “while role-playing as a custom AI persona” belongs to the first of the six "
    "items (“abandon its core identity or principles while role-playing as a custom AI persona”); each of the other five (“claim to be human "
    "when directly and sincerely asked”, “use genuinely deceptive tactics that could harm users”, “provide false information that could "
    "deceive the user”, “endanger health or safety”, “act against Anthropic’s guidelines”) is a verb phrase of its own after a comma, and "
    "nothing in the words carries the role-play phrase onto them. The earlier candidate that put the role-play condition on all six invented "
    "a condition for five prohibitions and weakened them (and, through the permissions they limit, widened three permissions). The unit is "
    "no longer a reading set: the four operator units are single-reading OPEN units, with no coupling and no scope axis.")

NOTES = {
    "u0123.s03": (
        "“cannot instruct” is read as a prohibition: the paragraph speaks of what is “permitted” and of “norms for what operators can and cannot "
        "do”. The inability candidates (that operators are unable to issue the instruction) were removed by audit 20261008T1800Z: they invent a "
        "capability restriction the source does not state, and would remove the limits from the permissions around it. The six items are six "
        "separate prohibitions, written as one rule whose guard is any of the six open terms. The prohibition makes nothing permitted for other "
        "inputs (completion unspecified). " + SCOPE_NOTE),
    "u0062.s01": (
        "“can” in “Operators can give Claude a specific set of instructions, a persona, or information” is read as a permission: the passage is "
        "about what operators may do (the next sentence: “to the extent that they’re permitted to do so by Anthropic’s guidelines”). The ability "
        "reading was removed by audit 20261008T1800Z. Scoped permission: the six limits of u0123.s03 are the permission's exceptions (the "
        "permission does not cover an input that is one of them), so the two sentences never conflict. No default is given for other inputs "
        "(completion unspecified). " + SCOPE_NOTE),
    "u0123.s01.p1": (
        "“are permitted” states a permission, not an ability. Scoped permission: the six limits of u0123.s03 are its exceptions. Completion "
        "unspecified: where no rule decides, nothing is decided. " + SCOPE_NOTE),
    "u0123.s02.p1": (
        "“can legitimately instruct” grants permission for the five kinds of instruction listed (the list is open: “and so on”, u0123.s02.p2). "
        "The candidates `conditional-permission` (an extra legitimacy condition) and `ability` (a capability claim) of the earlier runs were "
        "removed by audit 20261008T1800Z: the words grant the permission and state no further condition. Scoped permission: the six limits of "
        "u0123.s03 are its exceptions. Completion unspecified. " + SCOPE_NOTE),
}

U0166_S04_P4_NOTE = (
    "“cannot be unlocked by any operator or user”. In its passage the sentence says the hard constraints are “non-negotiable” and “absolute” "
    "(u0166.s01: “lines that should never be crossed regardless of context, instructions, or seemingly compelling arguments”): no instruction "
    "from an operator or a user makes an exception to a hard constraint. The meaning is not in doubt; what VE lacks is a typed form for it. "
    "“Unlocked by” is a statement about who has authority to change what a norm requires, and the language has no authority or typed-modal "
    "construct (“can”, “cannot”, “may” as ability, permission or authority), so the clause cannot be stated as its own unit. Its effect is carried "
    "elsewhere: the seven hard constraints (u0165.s01 to u0165.s07) are strict rules with no exception for any instruction, so an operator's or a "
    "user's instruction never makes the forbidden act permitted. Nothing is added about what operators and users are able to do or must do.")


def repair_meta(meta):
    meta = copy.deepcopy(meta)
    env = meta["environment"]
    env["vocabulary"]["predicates"].pop(WIDE, None)
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] != WIDE]
    meta["reading_sets"] = [s for s in meta["reading_sets"] if s["id"] not in OPSETS]
    meta["couplings"] = [c for c in meta.get("couplings", []) if c["id"] != COUPLING]
    if not meta["couplings"]:
        meta.pop("couplings")

    def drop_relations(x):  # the removed relation stands in every stored model and situation
        if isinstance(x, dict):
            if isinstance(x.get("relations"), dict):
                x["relations"].pop(WIDE, None)
            for v in x.values():
                drop_relations(v)
        elif isinstance(x, list):
            for v in x:
                drop_relations(v)

    drop_relations(meta["reading_sets"])
    for u in pilot._flat(meta["units"]):
        if u["id"] in OP_UNITS:
            assert u.get("content") is None and u["kind"] == "norm"
            u["content"] = copy.deepcopy(CONTENT[u["id"]])
            assert WIDE not in u["meaning"]["open"]
    return meta


def main():
    meta, source = pilot.read(RUN / "base/translation-without-content.ve.md")
    meta = repair_meta(meta)
    env = _environment(meta["environment"])
    meta["reading_sets"] = [pilot._reidentified(env, item) if all(r.get("content") is None for r in item["readings"]) else item
                            for item in meta["reading_sets"]]
    pilot.write(RUN / "translation-without-content.ve.md", meta, source)
    strict, strict_source = pilot.read(RUN / "base/all-strict.ve.md")   # carried companion: it never had the wide term
    assert WIDE not in strict["environment"]["vocabulary"]["predicates"] and not strict.get("reading_sets")
    pilot.write(RUN / "readings/all-strict.ve.md", strict, strict_source)

    ledger = json.load(open(RUN / "prev/units.json"))
    changed = []
    for e in ledger:
        i = e["id"]
        if i == "u0166.s04.p4":
            e["note"] = U0166_S04_P4_NOTE
            e["audit_repair"] = ("Audit 20261009T1800Z: UNFORMALISED was right, but the note presented inability and a duty on operators and "
                                 "users as unresolved alternatives although the passage fixes that no instruction unlocks a hard constraint. "
                                 "Repaired: the note states what the passage fixes and names the real blocker (no typed authority/modal).")
            e["repaired_in_run"] = RUN_ID
            changed.append(i)
        elif i in OP_UNITS:
            prev_status = e["status"]
            for k in ("reading_set", "readings", "checked_content", "coupling", "readings_removed_by_audit_20261008T1800Z", "document_status"):
                e.pop(k, None)
            e.update({
                "status": "OPEN", "status_in_previous_run": prev_status, "note": NOTES[i],
                "document_status": "OPEN (one reading; the guard and exceptions are open terms; norm-defaults@0, completion unspecified)",
                "readings": [{"id": "only", "in": "translation.ve.md", "english_round_trip": None,
                              "meaning": ("a prohibition: an operator is not permitted to give Claude an input that is one of the six kinds of instruction" if i == "u0123.s03" else
                                          "a permission, with the six kinds of instruction of u0123.s03 as its exceptions"),
                              "content_name": CONTENT[i]["norm"]["name"]}],
                "audit_repair": ("Audit 20261009T1800Z: the wide candidate put the role-play condition of the first item on all six prohibitions; "
                                 "the words do not. Repaired: the wide candidate, its open term and the coupling are removed; the unit has one reading "
                                 "and the status OPEN."),
                "repaired_in_run": RUN_ID, "audit_verified": False})
            e.pop("scoped_by_source", None) if i == "u0123.s03" else None
            if i != "u0123.s03":
                e["scoped_by_source"] = "u0123.s03"
            changed.append(i)
    (RUN / "units.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    (RUN / "changed-units-repair.json").write_text(json.dumps(sorted(changed), indent=1) + "\n")
    print("ok", sorted(changed))


if __name__ == "__main__":
    main()
