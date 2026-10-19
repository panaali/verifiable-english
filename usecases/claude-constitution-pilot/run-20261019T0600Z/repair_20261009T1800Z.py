#!/usr/bin/env python3
"""Run 20261009T1800Z: repair of the units the audit of run 20261009T0600Z rejected.

    uv run python usecases/claude-constitution-pilot/run-20261009T1800Z/repair_20261009T1800Z.py
        # base/translation-without-content.ve.md + prev/units.json -> translation-without-content.ve.md, units.json
    uv run python usecases/claude-constitution-pilot/run-20261009T1800Z/nd.py all   # adds the content of the eight reading sets

AUDIT.md of the previous run (15/20): u0166.s04.p4, u0165.s03, u0123.s01.p1, u0123.s03 and u0062.s01 UNFAITHFUL.
* u0165.s03 (hard constraint on cyberweapons): the open term listed "how likely deployment must be" as an unsettled question; the words
  say "could cause significant damage if deployed" and raise no probability threshold. The factor goes. The same invented question
  stood in two operator terms (`instruction_deceptive_tactics_harming_users`, `instruction_false_information_deceiving_user`:
  "how likely harm / deception must be"); those factors go too (the lead's rule: never list unsettled questions the text does not raise).
* u0166.s04.p4 ("cannot be unlocked by any operator or user"): the unit stated an ability ("no operator and no user is able to unlock").
  The words do not say whether "cannot" is ability, permission or authority to override, and the one candidate that stays
  within the lead's rule (no duty on operators and users) is the ability statement the audit rejects. The unit is UNFORMALISED
  (missing feature: modality/belief). The fenced statement, the two relations (`operator_unlocks`, `user_unlocks`) and their
  open terms are removed.
* u0123.s03, u0123.s01.p1, u0062.s01 (and u0123.s02.p1, the same set of four): the wide candidate put the role-play condition on
  the time the instruction is given (`instruction_given_while_role_playing_persona`); an instruction issued beforehand to
  abandon principles during later role-play would escape the prohibition. The wide reading puts the condition on the behaviour
  the instruction asks for: `instruction_is_for_behaviour_while_role_playing_persona` (the instructed behaviour is to be carried
  out while Claude role-plays a custom AI persona). nd.py defines the term; here the candidates' admission texts change.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import readings_s1_pilot as pilot  # noqa: E402
from ve.document import _environment  # noqa: E402

RUN_ID = "20261009T1800Z"
REMOVED_PREDICATES = ["operator_unlocks", "user_unlocks"]
FACTORS_REMOVED = {
    "damaging_cyberweapon_or_malicious_code": "how likely deployment must be for the damage to count as one that could happen",
    "instruction_deceptive_tactics_harming_users": "how likely harm must be for the tactics to be ones that could harm users",
    "instruction_false_information_deceiving_user": "how likely deception must be for the information to be information that could deceive",
}
OLD_WIDE_PERMISSION = "each of the six kinds is excluded from the permission only while Claude is role-playing as a custom AI persona"
NEW_WIDE_PERMISSION = ("each of the six kinds is excluded from the permission only for behaviour Claude is to carry out while role-playing as "
                       "a custom AI persona (the role-play condition is on the behaviour the instruction asks for, not on when the "
                       "instruction is given)")
OLD_WIDE_PROHIBITION = ("“while role-playing as a custom AI persona” qualifies every item of the list: each of the six is prohibited "
                        "only while Claude is role-playing a custom persona")
NEW_WIDE_PROHIBITION = ("“while role-playing as a custom AI persona” qualifies every item of the list: each of the six is prohibited "
                        "only for behaviour Claude is to carry out while role-playing a custom persona (the condition is on the behaviour "
                        "the instruction asks for, not on when the instruction is given)")
NOTE_ADD = {
    "u0165.s03": (" Repair (audit 20261009T0600Z): the open term no longer lists “how likely deployment must be”; the words say “could cause "
                  "significant damage if deployed” and raise no probability threshold."),
    "u0123.s03": (" Repair (audit 20261009T0600Z): in the wide candidate the role-play condition is on the behaviour the instruction asks for "
                  "(the open term `instruction_is_for_behaviour_while_role_playing_persona`), not on when the instruction is given, so an "
                  "instruction issued beforehand for later role-play is not outside the prohibition."),
    "u0123.s01.p1": (" Repair (audit 20261009T0600Z): the wide candidate's exception takes the role-play condition from the behaviour the "
                     "instruction asks for, not from the time it is given (see u0123.s03)."),
    "u0123.s02.p1": (" Repair (the same set of four as u0123.s03): the wide candidate's exception takes the role-play condition from the "
                     "behaviour the instruction asks for, not from the time it is given."),
    "u0062.s01": (" Repair (audit 20261009T0600Z): the wide candidate's exception takes the role-play condition from the behaviour the "
                  "instruction asks for, not from the time it is given (see u0123.s03)."),
}
U0166_S04_P4_NOTE = ("“cannot be unlocked by any operator or user”: “cannot” can be an inability (no operator and no user is able to "
                     "unlock), a prohibition (none is permitted to) or a denial of authority to override. The words do not say which. A "
                     "prohibition would put a duty on operators and users that the source does not state; the ability statement the earlier "
                     "runs wrote adds a capability claim the audit rejected (audit 20261009T0600Z). VE has no typed modality to keep the "
                     "ambiguity, so the clause is not formalised. What the passage does fix is carried elsewhere: the seven hard constraints "
                     "(u0165.s01 to u0165.s07) are written as strict rules with no exception for any instruction.")


def repair_meta(meta, source):
    meta = copy.deepcopy(meta)
    env = meta["environment"]
    for name in REMOVED_PREDICATES:
        env["vocabulary"]["predicates"].pop(name, None)
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] not in REMOVED_PREDICATES]
    for t in meta["open_terms"]:
        if t["name"] in FACTORS_REMOVED:
            t["factors"] = [f for f in t["factors"] if f != FACTORS_REMOVED[t["name"]]]
            assert len(t["factors"]) >= 1
    # u0166.s04.p4: unformalised (modality/belief); its fenced statement leaves the body
    for u in pilot._flat(meta["units"]):
        if u["id"] == "u0166.s04.p4":
            for k in ("content", "surface"):
                u.pop(k, None)
            u.update({"support": "none", "kind": ["unformalised", "modality_belief"], "meaning": {"unformalised": "modality_belief"}})
        elif "open" in u.get("meaning", {}):
            u["meaning"]["open"] = [o for o in u["meaning"]["open"] if o not in REMOVED_PREDICATES]
    block = re.compile(rb"```ve u0166\.s04\.p4\n.*?\n```\n", re.S)
    assert len(block.findall(source)) == 1
    source = block.sub(b"", source)
    def drop_relations(x):  # the removed relations stand in every stored model and situation
        if isinstance(x, dict):
            if isinstance(x.get("relations"), dict):
                for name in REMOVED_PREDICATES:
                    x["relations"].pop(name, None)
            for v in x.values():
                drop_relations(v)
        elif isinstance(x, list):
            for v in x:
                drop_relations(v)

    drop_relations(meta["reading_sets"])
    for item in meta["reading_sets"]:
        for r in item["readings"]:
            why = r["admission"]["why"]
            why = why.replace(OLD_WIDE_PERMISSION, NEW_WIDE_PERMISSION).replace(OLD_WIDE_PROHIBITION, NEW_WIDE_PROHIBITION)
            r["admission"] = {**r["admission"], "why": why}
    return meta, source


def main():
    meta, source = pilot.read(RUN / "base/translation-without-content.ve.md")
    meta, source = repair_meta(meta, source)
    env = _environment(meta["environment"])
    meta["reading_sets"] = [pilot._reidentified(env, item) if all(r.get("content") is None for r in item["readings"]) else item
                            for item in meta["reading_sets"]]
    pilot.write(RUN / "translation-without-content.ve.md", meta, source)
    # the carried strict companion (source of the strict content of the four "should" sets): same repairs
    strict, strict_source = pilot.read(RUN / "base/all-strict.ve.md")
    strict, strict_source = repair_meta(strict, strict_source)
    pilot.write(RUN / "readings/all-strict.ve.md", strict, strict_source)
    ledger = json.load(open(RUN / "prev/units.json"))
    changed = []
    for e in ledger:
        i = e["id"]
        if i == "u0166.s04.p4":
            keep = {k: e[k] for k in ("id", "span", "source_excerpt", "parent_unit", "old_unit") if k in e}
            e.clear()
            e.update(keep)
            e.update({"status": "UNFORMALISED", "missing_feature": "modality/belief", "other_blockers": [], "note": U0166_S04_P4_NOTE,
                      "status_in_previous_run": "OPEN", "audit_repair": "Rejected by audit 20261009T0600Z (an ability statement adds a "
                      "capability guarantee to a normative restriction). The permission reading is excluded by the lead's rule (no duty on "
                      "operators and users), the ability reading by the audit, and the words do not choose, so the unit is not formalised."})
            changed.append(i)
        elif i in NOTE_ADD:
            e["note"] = e["note"] + NOTE_ADD[i]
            e["repaired_in_run"] = RUN_ID
            changed.append(i)
        if i in ("u0123.s03", "u0123.s01.p1", "u0123.s02.p1", "u0062.s01") and i not in changed:
            changed.append(i)
        if i in ("u0123.s03", "u0123.s01.p1", "u0123.s02.p1", "u0062.s01"):
            for r in e.get("readings", []):
                if r.get("labels", {}).get("limits-scope") == "wide":
                    r["meaning"] = (r["meaning"].replace("only while Claude is role-playing as a custom AI persona",
                                                         "only for behaviour Claude is to carry out while role-playing as a custom AI persona"))
        if i == "u0165.s03":
            changed.append(i)
        if i in ("u0165.s03", "u0123.s03", "u0123.s01.p1", "u0123.s02.p1", "u0062.s01"):
            e["audit_verified"] = False
    for e in ledger:
        if e["id"] in ("u0165.s03",):
            e["repaired_in_run"] = RUN_ID
    (RUN / "units.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    (RUN / "changed-units-repair.json").write_text(json.dumps(sorted(set(changed)), indent=1) + "\n")
    print("ok", sorted(set(changed)))


if __name__ == "__main__":
    main()
