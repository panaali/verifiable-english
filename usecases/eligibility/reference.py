"""Independent reference reading of the Winter Fuel Payment rules for winter 2026 to 2027.

Written from the pinned source text in source/ (SI 2025/969 as made; SI 2005/3360
reg. 2(5); Pensions Act 1995 Sch. 4 para. 1; the GOV.UK guide for the income charge),
not from any VE translation. It imports nothing from `ve`. It computes the answer
for each profile in cases.json and compares it with the hand-derived key there.

Usage: python reference.py [cases.json]   (exit status 1 on any mismatch)
"""

import json
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

YEAR = 2026
RELEVANT_BENEFITS = {  # SI 2025/969 reg. 1(3), "relevant benefit" (a) to (e)
    "income_support", "income_based_jsa", "pension_credit", "income_related_esa", "universal_credit",
}
INCOME_THRESHOLD = Decimal("35000.00")  # GOV.UK guide, "If your income is over £35,000"


def qualifying_week(year):
    """Reg. 1(3): the week beginning on the third Monday in the September of that year."""
    first = date(year, 9, 1)
    first_monday = first + timedelta(days=(0 - first.weekday()) % 7)
    start = first_monday + timedelta(days=14)
    return start, start + timedelta(days=6)


QW_START, QW_END = qualifying_week(YEAR)


def anniversaries(birth, years, months=0):
    """Dates on which an age of `years` and `months` is attained (Family Law Reform Act
    1969 s. 9: at the commencement of the anniversary). A day missing from the target
    month (29 February, 31st) has two candidate readings; both are returned so a
    caller can check that its answer does not depend on the choice."""
    total = birth.month - 1 + months
    year, month = birth.year + years + total // 12, total % 12 + 1
    try:
        return [date(year, month, birth.day)]
    except ValueError:
        last = (date(year + month // 12, month % 12 + 1, 1) - timedelta(days=1))
        return [last, last + timedelta(days=1)]


TABLE3 = [  # Sch. 4 para. 1(7), table 3: births from 6 April 1960 to 5 March 1961
    (date(1960, 4, 6), date(1960, 5, 5), 1), (date(1960, 5, 6), date(1960, 6, 5), 2),
    (date(1960, 6, 6), date(1960, 7, 5), 3), (date(1960, 7, 6), date(1960, 8, 5), 4),
    (date(1960, 8, 6), date(1960, 9, 5), 5), (date(1960, 9, 6), date(1960, 10, 5), 6),
    (date(1960, 10, 6), date(1960, 11, 5), 7), (date(1960, 11, 6), date(1960, 12, 5), 8),
    (date(1960, 12, 6), date(1961, 1, 5), 9), (date(1961, 1, 6), date(1961, 2, 5), 10),
    (date(1961, 2, 6), date(1961, 3, 5), 11),
]
TABLE3_7A = {date(1960, 7, 31): date(2026, 11, 30), date(1960, 12, 31): date(2027, 9, 30),
             date(1961, 1, 31): date(2027, 11, 30)}


def pensionable_age_dates(birth):
    """Candidate dates of reaching pensionable age (Pensions Act 1995 Sch. 4 para. 1)."""
    if birth < date(1953, 12, 6):
        # Paras (1) to (4): a man at 65 (by 5 December 2018 at the latest); a woman at 60
        # or on the table 1 day (6 November 2018 at the latest). Only the latest possible
        # day matters for "in or before the qualifying week".
        return [date(2018, 12, 5)]
    if birth <= date(1954, 10, 5):
        raise NotImplementedError("Sch. 4 table 2 is not needed by any profile")
    if birth < date(1960, 4, 6):
        return anniversaries(birth, 66)  # para. (6)
    if birth <= date(1961, 3, 5):
        if birth in TABLE3_7A:
            return [TABLE3_7A[birth]]
        months = next(m for lo, hi, m in TABLE3 if lo <= birth <= hi)
        return anniversaries(birth, 66, months)  # para. (7)
    if birth < date(1977, 4, 6):
        return anniversaries(birth, 67)  # para. (8)
    raise NotImplementedError("births from 6 April 1977 are not needed by any profile")


def one_answer(values, what):
    if len(set(values)) != 1:
        raise ValueError(f"{what} depends on the reading of a missing anniversary day")
    return values[0]


def reached_pensionable_age(p):
    """Reg. 2(a): in or before the qualifying week, P has reached pensionable age."""
    return one_answer([d <= QW_END for d in pensionable_age_dates(p["birth"])], "pensionable age")


def reached_80(p):
    """Reg. 3: P has reached the age of 80 in or before the qualifying week."""
    return one_answer([d <= QW_END for d in anniversaries(p["birth"], 80)], "age 80")


def resident_in_qw(p):
    """Reg. 2(b): ordinarily resident in England or Wales on any day within the week."""
    if p["ew_from"] is None:
        return False
    return p["ew_from"] <= QW_END and (p["ew_last_day"] is None or p["ew_last_day"] >= QW_START)


def relevant_benefit(p):
    """A relevant benefit has been, or falls to be, paid to P for the qualifying week."""
    return any(b in RELEVANT_BENEFITS for b in p["benefits"])


def in_residential_care(p):
    """Reg. 1(4)(a): resides in a care home throughout the qualifying week and the period
    of at least 12 weeks (84 days) ending immediately before it."""
    care = p["care"]
    if care is None:
        return False
    until = care.get("until")
    return (QW_START - care["from"]).days >= 84 and (until is None or until >= QW_END)


def excluded_hospital(p):
    """Reg. 4(2)(b), with SI 2005/3360 reg. 2(5): a period of free in-patient treatment
    begins the day after admission and ends on the day of leaving."""
    h = p["hospital"]
    if h is None:
        return False
    start, end = h["admitted"] + timedelta(days=1), h["discharged"]
    throughout = start <= QW_START and end >= QW_END
    before = (QW_START - start).days  # days in [start, QW_START - 1]
    return throughout and before > 52 * 7


def excluded_custody(p):
    """Reg. 4(2)(c): throughout the week, detained in custody under a sentence. Adopted
    reading: in custody before the week began and not released until after it ended."""
    c = p["custody"]
    return (c is not None and c["sentenced"]
            and c["from"] < QW_START and c["release"] > QW_END)


def excluded_move(p):
    """Reg. 4(4): having been resident in England or Wales in the week, becomes ordinarily
    resident in Scotland or Northern Ireland on or before its last day."""
    return resident_in_qw(p) and p["scot_ni_from"] is not None and p["scot_ni_from"] <= QW_END


def excluded_no_claim(p):
    """Reg. 4(5)-(6) with reg. 5(1): no claim by 31 March following the week, unless paid
    without a claim. Reg. 5(2) is outside every profile."""
    claim = p["claim"]
    if claim["automatic"]:
        return False
    return claim.get("claimed_on") is None or claim["claimed_on"] > date(YEAR + 1, 3, 31)


def entitled(p, other):
    """Reg. 2 subject to reg. 4. `other` is the one person P lives with, or None."""
    if not (reached_pensionable_age(p) and resident_in_qw(p)):
        return False
    partner_benefit = (other is not None and other["partner"] and lives_with(p, other)
                       and reached_pensionable_age(other) and relevant_benefit(other))
    return not (partner_benefit or excluded_hospital(p) or excluded_custody(p)
                or (in_residential_care(p) and relevant_benefit(p))
                or excluded_move(p) or excluded_no_claim(p))


def lives_with(p, other):
    """Reg. 1(4)(b); every housemate in cases.json shares P's home in the week."""
    return other is not None and not in_residential_care(p) and not in_residential_care(other)


def amount(p, other):
    """Reg. 3, with each 'subject to' paragraph taking precedence."""
    rb = relevant_benefit(p)
    with_entitled = lives_with(p, other) and entitled(other, p)
    care = in_residential_care(p)
    if not reached_80(p):
        if not rb and (with_entitled or care):
            return Decimal("100.00")  # 3(2)
        if rb and other is not None and other["partner"] and lives_with(p, other) and reached_80(other):
            return Decimal("300.00")  # 3(3)
        return Decimal("200.00")  # 3(1)
    if not rb and ((with_entitled and reached_80(other)) or care):
        return Decimal("150.00")  # 3(6)
    if not rb and with_entitled and not reached_80(other):
        return Decimal("200.00")  # 3(5)
    return Decimal("300.00")  # 3(4)


def person(raw, defaults):
    p = {**defaults, **raw}
    for field in ("birth", "ew_from", "ew_last_day", "scot_ni_from"):
        if p.get(field) is not None:
            p[field] = date.fromisoformat(p[field])
    for field in ("care", "hospital", "custody", "claim"):
        if p.get(field) is not None:
            p[field] = {k: date.fromisoformat(v) if isinstance(v, str) else v for k, v in p[field].items()}
    p.setdefault("partner", False)
    p["income"] = Decimal(p["income"])
    return p


def answer(case, defaults):
    p = person(case["applicant"], defaults)
    other = person(case["housemate"], defaults) if case["housemate"] else None
    if not entitled(p, other):
        return {"entitled": False}
    paid = amount(p, other)
    recovered = p["income"] > INCOME_THRESHOLD
    kept = Decimal("0.00") if recovered else paid
    return {"entitled": True, "amount": f"{paid:.2f}", "recovered": recovered, "kept": f"{kept:.2f}"}


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("cases.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    print(f"qualifying week {QW_START} to {QW_END}")
    mismatches = 0
    for case in data["cases"]:
        got = answer(case, data["defaults"])
        ok = got == case["key"]
        mismatches += not ok
        print(f"{case['id']} {'ok ' if ok else 'MISMATCH'} {got}" + ("" if ok else f" key={case['key']}"))
    print(f"{len(data['cases']) - mismatches}/{len(data['cases'])} agree with the hand key")
    sys.exit(1 if mismatches else 0)


if __name__ == "__main__":
    main()
