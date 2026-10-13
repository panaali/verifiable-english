"""QX-1, QX-2, QX-3: the part of each pre-registered experiment that needs no model call (quantities plan, section 5).

All three experiments are executed by models (QX-1 and QX-3: 40 Sonnet 5.5 proxy-reader sessions; QX-2: a blind
audit by the reviewer pair), so their execution is DEFERRED. This script audits each pre-registration against the
plan's own text and the pinned pilot inputs, and computes what the plan fixes without readers:

- QX-1: the item count the plan lists against the count it budgets; for every item the plan specifies completely
  (numbers given), each reading's answer and whether the item separates the readings; the seeded order of those items.
- QX-2: the six units (bytes and status from the pinned ledger), the graded words in each, which units the plan gives
  a decomposed form (a QT-B1 fixture), and the latest audit verdict of the current form.
- QX-3: the four example items the plan states, with their labels re-derived under counting semantics by exhaustive
  enumeration of region sizes (every population up to N_MAX objects), and the premise each label silently needs.

Writes docs/research/evidence/quantities/qx/prereg-audit.json. No `ve` run, no model call.
"""
from __future__ import annotations

import itertools
import json
import random
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONSTITUTION_RUN, EVIDENCE, REPO, sha256, write_json

PLAN = REPO / "docs" / "spec" / "quantities-PLAN.md"
N_MAX = 12  # populations up to 12 objects in QX-3's enumeration

# ---------------------------------------------------------------- QX-1

# The plan's item list (section 5, QX-1), word by word: (word, contexts the plan names).
QX1_LISTED = [("most", 6), ("many", 6), ("few", 6), ("several", 6), ("multiple", 6), ("bare n of the m", 6),
              ("bare 105 percent of", 6)]
QX1_BUDGET_ITEMS = 36  # "40 sessions x 36 items = 1,440 short calls"


def qx1_items() -> list[dict]:
    """Items whose numbers the plan fixes, with each reading's answer (None: the reading gives no answer)."""
    items = []
    # "most": the plan names five points for six contexts.
    for k, n in ((50, 100), (51, 100), (60, 100), (95, 100), (3, 5)):
        more_than_half = 2 * k > n
        items.append({"word": "most", "context": f"Of the {n} members, {k} voted yes. Is it true that most members "
                                                    f"voted yes?",
                      "readings": {"more than half": more_than_half, "open proportion grade": None}})
    # "multiple": contexts at 1 and 2 ("at least two").
    for k in (1, 2):
        items.append({"word": "multiple", "context": f"{k} copies are running. Are multiple copies running?",
                      "readings": {"at least two": k >= 2}})
    # bare "16 of the 18 ... expect X": is 17 compatible?
    items.append({"word": "bare n of the m", "context": "16 of the 18 policymakers expect X. Is it compatible with "
                                                        "this that 17 of the 18 expect X?",
                  "readings": {"exactly": 17 == 16, "at least": 17 >= 16}})
    # bare "105 percent of": is 105.4 percent compatible?
    value = Fraction(1054, 10)
    nearest = {rule: _rounds_to_percent(value, 105, rule) for rule in ("tiesUp", "halfEven")}
    items.append({"word": "bare 105 percent of", "context": "The September estimate is 105 percent of the June "
                                                            "estimate. Is a value of 105.4 percent compatible?",
                  "readings": {"exact": value == 105, **{f"to the nearest percent ({r})": v
                                                          for r, v in nearest.items()}}})
    for item in items:
        answers = [v for v in item["readings"].values() if v is not None]
        item["separates_readings"] = len(set(answers)) > 1 or (None in item["readings"].values() and len(answers) > 0)
    return items


def _rounds_to_percent(x: Fraction, d: int, rule: str) -> bool:
    """`VE.Numbers.RoundsTo` at zero places, as the synthesis reference states it (tiesUp: 2D-1 <= 2x < 2D+1;
    halfEven: the end points count only when D is even)."""
    lo, hi = Fraction(2 * d - 1, 2), Fraction(2 * d + 1, 2)
    if rule == "tiesUp":
        return lo <= x < hi
    if d % 2 == 0:
        return lo <= x <= hi
    return lo < x < hi


# ---------------------------------------------------------------- QX-2

QX2_UNITS = ["u0165.s01", "u0165.s02", "u0165.s03", "u0165.s04", "u0165.s05", "u0165.s06"]
GRADED = re.compile(r"\b(serious|significant|clearly|substantially|vast majority|unprecedented|absolute|mass)\b", re.I)
# The plan's decomposed forms: QT-B1's fixtures FB1 (u0165.s01, "serious uplift" on `uplift`) and FB6 (u0165.s05,
# "vast majority" on `share_of_humanity_targeted`). Section 4, QT-B1 fixtures; section 2.5 of the research.
PLAN_DECOMPOSITION = {"u0165.s01": "FB1 (dimension uplift on response, grade gives_serious_uplift)",
                      "u0165.s05": "FB6 (dimension share_of_humanity_targeted on attempt, grade vast_majority)"}


def qx2_units() -> list[dict]:
    units = {u["id"]: u for u in json.loads((CONSTITUTION_RUN / "units.json").read_text())}
    audit = (CONSTITUTION_RUN / "AUDIT.md").read_text()
    rows = []
    for uid in QX2_UNITS:
        u = units[uid]
        verdict = re.search(rf"^{re.escape(uid)} (\w+)$", audit, re.M)
        rows.append({"unit": uid, "bytes": u["span"][1] - u["span"][0], "status": u["status"],
                     "excerpt": u["source_excerpt"].strip(),
                     "graded_words": sorted({m.group(1).lower() for m in GRADED.finditer(u["source_excerpt"])}),
                     "open_terms": u.get("open_terms"),
                     "plan_decomposed_form": PLAN_DECOMPOSITION.get(uid),
                     "latest_audit_of_current_form": verdict.group(1) if verdict else None})
    return rows


# ---------------------------------------------------------------- QX-3

def _pops(n_preds: int):
    """Every assignment of sizes to the 2^n_preds regions with total at most N_MAX (the region sizes determine
    every count the items mention)."""
    regions = 2 ** n_preds
    for total in range(N_MAX + 1):
        for cut in itertools.combinations(range(total + regions - 1), regions - 1):
            sizes, prev = [], -1
            for c in (*cut, total + regions - 1):
                sizes.append(c - prev - 1)
                prev = c
            yield sizes


def _count(sizes, n_preds, test) -> int:
    return sum(s for r, s in enumerate(sizes) if test(tuple(bool(r >> i & 1) for i in range(n_preds))))


def most(a: int, b: int) -> bool:
    """"Most B are A" with b = #B and a = #(A and B): more than half, over a nonempty B."""
    return b > 0 and 2 * a > b


def qx3_items() -> list[dict]:
    out = []

    # 1. "The vast majority voted. Did a majority vote?" Plan: valid. "The vast majority" has no counting meaning in
    # the plan (a graded word, no threshold, grade_open); valid only with a threshold above one half, which is the
    # bridge the plan says is not offered. Checked over thresholds t (vast majority: share >= t) on a grid.
    thresholds = [Fraction(k, 100) for k in range(1, 100)]
    valid_by_t = {}
    for t in thresholds:
        ok = True
        for sizes in _pops(1):
            n, voted = sum(sizes), sizes[1]
            if n > 0 and Fraction(voted, n) >= t and not 2 * voted > n:
                ok = False
                break
        valid_by_t[t] = ok
    least_valid = min((t for t, ok in valid_by_t.items() if ok), default=None)
    out.append({"item": "The vast majority voted. Did a majority vote?", "plan_label": "valid",
                "counting_label": "depends on the grade's threshold: valid exactly when the threshold is above one "
                                  "half (smallest valid grid point: " + str(least_valid) + ")",
                "needs": "the bridge 'the vast majority implies more than half', which section 5 says is not "
                         "offered on any vote and waits for QX-4's proved bridge",
                "label_agrees": False})

    # 2. "A majority voted yes and a majority voted no." Plan: contradiction. Predicates yes (bit 0) and no (bit 1).
    sat_free = any(most(_count(s, 2, lambda r: r[0]), sum(s)) and most(_count(s, 2, lambda r: r[1]), sum(s))
                   for s in _pops(2))
    sat_excl = any(most(_count(s, 2, lambda r: r[0]), sum(s)) and most(_count(s, 2, lambda r: r[1]), sum(s))
                   and _count(s, 2, lambda r: r[0] and r[1]) == 0 for s in _pops(2))
    out.append({"item": "A majority voted yes and a majority voted no.", "plan_label": "contradiction",
                "counting_label": ("contradiction" if not sat_free else
                                   "satisfiable without the premise that no voter voted both; contradiction with it"
                                   if not sat_excl else "satisfiable"),
                "needs": "the exclusion premise 'no one voted both yes and no' (as FA1 needs 'no policymaker "
                         "expects both')",
                "label_agrees": not sat_free})

    # 3. "Most S are P; every P is Q. Are most S Q?" Plan: valid. Bits: S, P, Q.
    counter3 = None
    for s in _pops(3):
        S = _count(s, 3, lambda r: r[0])
        if (most(_count(s, 3, lambda r: r[0] and r[1]), S) and _count(s, 3, lambda r: r[1] and not r[2]) == 0
                and not most(_count(s, 3, lambda r: r[0] and r[2]), S)):
            counter3 = s
            break
    out.append({"item": "Most S are P; every P is Q. Are most S Q?", "plan_label": "valid",
                "counting_label": "valid (no countermodel up to N_MAX)" if counter3 is None else
                f"invalid: region sizes {counter3}", "needs": None, "label_agrees": counter3 is None})

    # 4. "Most S are P. Are most P S?" Plan: invalid. Bits: S, P.
    counter4 = None
    for s in _pops(2):
        if (most(_count(s, 2, lambda r: r[0] and r[1]), _count(s, 2, lambda r: r[0]))
                and not most(_count(s, 2, lambda r: r[0] and r[1]), _count(s, 2, lambda r: r[1]))):
            counter4 = s
            break
    out.append({"item": "Most S are P. Are most P S?", "plan_label": "invalid",
                "counting_label": "invalid: smallest countermodel region sizes (none, S only, P only, both) "
                                  f"= {counter4}" if counter4 else "valid up to N_MAX",
                "needs": None, "label_agrees": counter4 is not None})
    return out


# ---------------------------------------------------------------- driver

def main() -> None:
    items = qx1_items()
    order = list(range(len(items)))
    random.Random("quantities-QX1").shuffle(order)
    listed = sum(n for _, n in QX1_LISTED)
    report = {
        "plan": {"path": str(PLAN.relative_to(REPO)), "sha256": sha256(PLAN)},
        "ledger": {"path": str(CONSTITUTION_RUN / "units.json"), "sha256": sha256(CONSTITUTION_RUN / "units.json")},
        "qx1": {"listed_items": dict(QX1_LISTED), "listed_total": listed, "budgeted_total": QX1_BUDGET_ITEMS,
                "count_consistent": listed == QX1_BUDGET_ITEMS,
                "most_points_named": 5, "most_contexts_required": 6,
                "fully_specified_items": items,
                "seeded_order_of_fully_specified_items": order,
                "unspecified": ["the six contexts each for 'many', 'few' and 'several' (only their purpose, the "
                                "cardinal against the proportional reading, is given)",
                                "the sixth 'most' context", "four of the six 'multiple' contexts (two points given)",
                                "five of the six contexts each for bare 'n of the m' and bare '105 percent of' "
                                "(one question each)",
                                "the answer format and the analysis (the plan states no bar for QX-1)"]},
        "qx2": {"units": qx2_units()},
        "qx3": {"n_max": N_MAX, "items_stated": 4, "items_required": 20, "items": qx3_items()},
    }
    report["qx2"]["total_bytes"] = sum(r["bytes"] for r in report["qx2"]["units"])
    report["qx2"]["units_with_plan_decomposition"] = sum(r["plan_decomposed_form"] is not None
                                                         for r in report["qx2"]["units"])
    write_json(EVIDENCE / "qx" / "prereg-audit.json", report)
    print(json.dumps(report, indent=1, default=str)[:8000])


if __name__ == "__main__":
    main()
