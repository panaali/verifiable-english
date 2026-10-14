#!/usr/bin/env python3
"""PS-0p step 7 (D5): trigger occurrences in rule acts and the distinct goals they project, from the pinned ledger.

Definitions: docs/research/presupposition-phase1.md 1.3 ("Distinct goals (D5)"). Population: the constitution's norm
units with rule content in the pinned translation (a unit's `content.norm`, or a reading of its reading set). An
occurrence is a G1 or G2 match (ps0p_census) in such a unit's text; its position (rule act or guard) is my reading of
the sentence, recorded in POSITION below so a reviewer can redo it. A goal key is (row, restriction noun, guard,
unless), the rule's wire formulas with their de Bruijn indices. For the units that are not formalised the ledger has no
guard, so their goal count is unknown; the occurrence count and the distinct (group, noun) pairs bound it.

Writes docs/research/evidence/presupposition/goals.json.

    python3 research/presupposition/ps0p_goals.py
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ps0p_census", HERE / "ps0p_census.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

# (unit, matched words) -> (position, row, restriction noun, why). My reading of each sentence.
POSITION = {
    ("u0123.s02.p1", "the operator"): ("guard", "definite", "operator",
        "in 'promote the operator’s own products', a kind of instruction the guard names; packed into the guard atom "
        "instruction_promote_own_products…, so no formula position exists for it"),
    ("u0123.s03", "the user"): ("guard", "definite", "user",
        "in 'provide false information that could deceive the user', a kind of instruction the guard names; packed "
        "into the guard atom instruction_false_information_deceiving_user"),
    ("u0156.s03", "the user"): ("rule_act", "definite", "user",
        "the act 'deceive the user'; the user is the regulated predicate's second argument (bound by the rule)"),
    ("u0156.s03", "its content"): ("rule_act", "plural", "content of a system prompt",
        "the act 'deceive … about … its content'; plan P6"),
}


def main() -> int:
    run, src = c.CONST_RUN, c.CONST_SRC.read_bytes()
    meta = json.loads((run / "translation.ve.md").read_text().split("\n")[1])
    units = {u["id"]: u for u in c.load(run)}
    rules: dict[str, list] = {}
    for u in meta["units"]:
        if isinstance(u.get("content"), dict) and "norm" in u["content"]:
            rules.setdefault(u["id"], []).append(("unit", u["content"]["norm"]))
    for rs in meta["reading_sets"]:
        for r in rs["readings"]:
            if isinstance(r.get("content"), dict) and "norm" in r["content"]:
                rules.setdefault(rs["unit"], []).append((r["id"], r["content"]["norm"]))

    occurrences, obligations = [], []
    for uid, rl in rules.items():
        text = c.text_of(src, units[uid])
        for g in ("G1", "G2"):
            for m in c.matches(g, text):
                pos = POSITION.get((uid, m.group(0)))
                if pos is None:
                    raise SystemExit(f"no recorded position for {uid}: {m.group(0)!r}")
                occurrences.append({"unit": uid, "words": m.group(0), "group": g, "position": pos[0], "row": pos[1],
                                    "restriction": pos[2], "why": pos[3], "readings": [r for r, _ in rl]})
                if pos[0] == "rule_act":
                    for reading, n in rl:
                        obligations.append({"unit": uid, "reading": reading, "words": m.group(0), "rule": n["name"],
                                            "key": [pos[1], pos[2], n["guard"], n["unless"]]})
    keys = {json.dumps(o["key"]) for o in obligations}
    per_alternative = {}
    for o in obligations:
        per_alternative.setdefault((o["unit"], o["reading"]), []).append(o)
    alt = {f"{u}/{r}": {"obligations": len(v), "distinct_goals": len({json.dumps(o["key"]) for o in v}),
                        "share_applicability": len({json.dumps(o["key"][2:]) for o in v}) == 1}
           for (u, r), v in per_alternative.items()}

    # The units that are not formalised: occurrences and (group, noun) pairs only.
    crow = c.ledger(c.load(run), src)
    formal = set(rules)
    rest = [r for r in crow if r["id"] not in formal]
    def noun(e):
        w = e["words"].lower().replace("’", "'")
        if e["group"] == "G1":
            return re.sub(r"s$", "", w.split()[1])
        return w
    g1 = [(r["id"], e) for r in rest for e in r["presupposition_triggers"] if e["group"] == "G1"]
    g2 = [(r["id"], e) for r in rest for e in r["presupposition_triggers"] if e["group"] == "G2"]
    by_role = {}
    for uid, e in g1:
        k = noun(e)
        s = by_role.setdefault(k, {"occurrences": 0, "units": set(), "units_by_status": {}})
        s["occurrences"] += 1
        s["units"].add(uid)
    for k, s in by_role.items():
        for uid in s["units"]:
            st = units[uid]["status"]
            s["units_by_status"][st] = s["units_by_status"].get(st, 0) + 1
        s["units"] = len(s["units"])
    both = {u for u, e in g1 if noun(e) == "user"} & {u for u, e in g1 if noun(e) == "operator"}
    g2_pairs = sorted({" ".join(e["words"].lower().replace("’", "'").split()) for _, e in g2})
    result = {
        "run": "20261012T1800Z", "definitions": "docs/research/presupposition-phase1.md 1.3 (Distinct goals (D5))",
        "formalised_rule_units": sorted(rules), "occurrences_in_formalised_units": occurrences,
        "rule_act_obligations": obligations, "distinct_goal_keys": len(keys),
        "per_reading_alternative": alt,
        "not_formalised": {
            "G1_by_role": by_role, "G1_units_with_both_roles": len(both),
            "G1_occurrences": len(g1), "G1_distinct_role_nouns": sorted(by_role),
            "G2_occurrences": len(g2), "G2_units": len({u for u, _ in g2}), "G2_distinct_owner_object_pairs": g2_pairs,
            "goals": "unknown: the ledger records no guard for an unformalised unit",
            "identical_applicability": "unknown, for the same reason",
            "upper_bound_distinct_goals_G1": len(g1),
            "source_identity_choices_G1": len(by_role),
        },
        "joint_budget": 64,
    }
    out = c.OUT / "goals.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("occurrences_in_formalised_units", "rule_act_obligations")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
