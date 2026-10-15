#!/usr/bin/env python3
"""Run 20261009T0600Z: repair of the units the audit of run 20261008T1800Z rejected, from `prev/translation.ve.md` into `translation-without-content.ve.md` (the translation without content; nd.py adds content and writes readings/nd-all.ve.md, which is `translation.ve.md`).

    uv run python usecases/claude-constitution-pilot/run-20261009T0600Z/repair_20261009.py

AUDIT.md of the previous run: u0123.s02.p1, u0123.s03 and u0123.s01.p1 UNFAITHFUL.
* u0123.s02.p1 "Operators can legitimately instruct ...": the conditional-permission candidate added a legitimacy
  condition the words do not state (they grant the permission), and the ability candidate put a capability claim into a passage
  about what is permitted. Both candidates go; so does the open term `instruction_is_legitimate` that only they used.
* u0123.s03 "Operators cannot instruct ...": the two inability candidates invent a restriction on what an operator can do; the
  source prohibits those instructions. They go.
* u0123.s01.p1 "Operators are permitted ...": `permission-no-limits` rested on that inability reading. It goes.
* The same reasoning is applied to the neighbour u0062.s01 ("Operators can give Claude ..."), whose ability candidate has the same
  defect (the next sentence says "to the extent that they're permitted to do so"). It goes too.

What remains in all four sets is the ambiguity the words do carry: how far "while role-playing as a custom AI persona" reaches in
u0123.s03 (the first item only, or every item), and what that does to the permissions the limits attach to. Each set has the
narrow and the wide candidate; a coupling on the label axis `limits-scope` makes the four sets take the same scope, so the
sentences can no longer be read with different limits (they were free to differ before: 16 choices, now 2).
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import readings_s1_pilot as pilot  # noqa: E402
from ve.document import _environment  # noqa: E402

AXIS = "limits-scope"
COUPLING = {"id": "limits-scope-u0123-s03", "axis": AXIS, "by": "translator", "reason_spans": ["u0123.s03"],
            "sets": [{"set": s, "version": 1} for s in ("modal-u0062-s01", "modal-u0123-s01-p1", "modal-u0123-s02-p1",
                                                         "scope-modal-u0123-s03")]}

LIMITS_NARROW = "the six kinds of instruction u0123.s03 lists are each excluded from the permission"
LIMITS_WIDE = "each of the six kinds is excluded from the permission only while Claude is role-playing as a custom AI persona"
COMMON = ("Pending: a candidate norm carries no content in this document; the content that Lean checks is in readings/nd-op.ve.md "
          "and nd-all.ve.md. The permission is scoped by the limit the next sentences attach (u0123.s03); where no rule decides, "
          "nothing is decided (completion unspecified).")
SETS = {
    "modal-u0062-s01": ("u0062-s01", [
        ("permission-narrow-limits", "narrow", "“can give” read as a permission (the passage is about what operators may do: “to the extent that "
         "they’re permitted to do so by Anthropic’s guidelines”); " + LIMITS_NARROW),
        ("permission-wide-limits", "wide", "“can give” read as a permission; " + LIMITS_WIDE)]),
    "modal-u0123-s01-p1": ("u0123-s01-p1", [
        ("permission-narrow-limits", "narrow", "“are permitted” states a permission; " + LIMITS_NARROW),
        ("permission-wide-limits", "wide", "“are permitted” states a permission; " + LIMITS_WIDE)]),
    "modal-u0123-s02-p1": ("u0123-s02-p1", [
        ("permission-narrow-limits", "narrow", "“can legitimately instruct” grants the permission for the five listed kinds of "
         "instruction (and “so on”); “legitimately” adds no condition of its own; " + LIMITS_NARROW),
        ("permission-wide-limits", "wide", "“can legitimately instruct” grants the permission for the five listed kinds; "
         + LIMITS_WIDE)]),
    "scope-modal-u0123-s03": ("u0123-s03", [
        ("narrow-prohibition", "narrow", "“cannot instruct” is a prohibition (the passage speaks of what is permitted and of norms "
         "for what operators can and cannot do): the party is not permitted to give such an instruction; “while role-playing as a custom "
         "AI persona” qualifies the first item only (abandoning core identity or principles); the other five are prohibited whenever"),
        ("wide-prohibition", "wide", "“cannot instruct” is a prohibition; “while role-playing as a custom AI persona” qualifies every "
         "item of the list: each of the six is prohibited only while Claude is role-playing a custom persona")]),
}
NOTES = {
    "u0062.s01": (
        "“can” in “Operators can give Claude a specific set of instructions, a persona, or information” is read as a permission: the "
        "passage is about what operators may do (the next sentence: “to the extent that they’re permitted to do so by Anthropic’s "
        "guidelines”). The ability reading offered by the earlier runs is removed: it claims a capability the words of this "
        "normative passage do not (audit 20261008T1800Z, same defect as u0123.s02.p1). Scoped permission: the limits the source attaches "
        "(u0123.s03) restrict it. What the words leave open is how far those limits reach, so the set has the narrow-limits and the "
        "wide-limits candidate, coupled to the other three sets on the axis `limits-scope`. No default is given for inputs no rule decides "
        "(completion unspecified)."),
    "u0123.s01.p1": (
        "“are permitted” states a permission, not an ability. The candidate `permission-no-limits` is removed: it relied on the inability "
        "reading of u0123.s03 that the audit rejected (u0123.s03 prohibits those instructions; it does not say operators cannot issue "
        "them). Scoped permission: the limits u0123.s03 attaches restrict it; the two candidates are the permission under the narrow and the "
        "wide scope of “while role-playing as a custom AI persona” there, coupled to the other three sets on the axis `limits-scope`. "
        "Completion unspecified: where no rule decides, nothing is decided."),
    "u0123.s02.p1": (
        "“can legitimately instruct” grants permission for the five kinds of instruction listed (the list is open: “and so on”, u0123.s02.p2). "
        "The candidates `conditional-permission` (an extra legitimacy condition) and `ability` (a capability claim) of the earlier runs are "
        "removed (audit 20261008T1800Z): the words grant the permission and state no further condition, and the passage is about what is "
        "permitted. The open term `instruction_is_legitimate` that only they used is removed. Scoped permission: the limits of u0123.s03 "
        "restrict it; the set has the narrow-limits and the wide-limits candidate, coupled to the other three on the axis `limits-scope`. "
        "Completion unspecified."),
    "u0123.s03": (
        "“cannot instruct” is read as a prohibition: the paragraph speaks of what is “permitted” and of “norms for what operators can and "
        "cannot do”. The inability candidates (that operators are unable to issue the instruction) are removed: they invent a capability "
        "restriction the source does not state, and would remove the limits from the permissions around it (audit 20261008T1800Z). What the "
        "words leave open is the scope of “while role-playing as a custom AI persona”: the first item only (narrow) or every item (wide). "
        "The six items are six separate prohibitions. The set is coupled to the three permission sets on the axis `limits-scope`. Completion "
        "unspecified: the prohibition makes nothing permitted for other inputs."),
}


def repair_meta(meta):
    meta = copy.deepcopy(meta)
    # the open term and predicate only the removed candidates used
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] != "instruction_is_legitimate"]
    meta["environment"]["vocabulary"]["predicates"].pop("instruction_is_legitimate", None)

    def strip(units):
        for u in units:
            if "meaning" in u and isinstance(u["meaning"], dict) and "open" in u["meaning"]:
                u["meaning"]["open"] = [o for o in u["meaning"]["open"] if o != "instruction_is_legitimate"]
            for key in ("children", "subunits"):
                if key in u:
                    strip(u[key])
    strip(meta["units"])
    meta["environment"]["profiles"] = sorted({*meta["environment"]["profiles"], "readings@1"})
    sets = []
    for item in meta["reading_sets"]:
        for data in item.get("models", {}).values():
            data["relations"].pop("instruction_is_legitimate", None)
        if item["id"] in SETS:
            key, cands = SETS[item["id"]]
            model_id = next(iter(item["models"]))
            readings = []
            for cid, scope, why in cands:
                readings.append({"id": cid, "kind": "norm", "meaning_id": f"pending-{cid}-{key}", "content": None, "labels": {AXIS: scope},
                                 "admission": {"who": "translator", "why": why + ". " + COMMON,
                                               "distinguishing_models": {o[0]: model_id for o in cands if o[0] != cid}}})
            item = {**item, "readings": readings}
        sets.append(item)
    meta["reading_sets"] = sets
    meta["couplings"] = [COUPLING]
    return meta


def main():
    meta, source = pilot.read(RUN / "prev/translation.ve.md")
    meta = repair_meta(meta)
    env = _environment(meta["environment"])
    meta["reading_sets"] = [pilot._reidentified(env, item) if all(r.get("content") is None for r in item["readings"]) else item
                            for item in meta["reading_sets"]]
    pilot.write(RUN / "translation-without-content.ve.md", meta, source)
    ledger = json.load(open(RUN / "prev/units.json"))
    for e in ledger:
        if e["id"] in NOTES:
            e["note"] = NOTES[e["id"]]
            e["open_terms"] = [t for t in e.get("open_terms", []) if t != "instruction_is_legitimate"]
            e["repaired_in_run"] = "20261009T0600Z"
    (RUN / "units.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    print("ok")


if __name__ == "__main__":
    main()
