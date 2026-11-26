"""Tour stop 4: a date question. Runs from branch after-release (date arithmetic) until it reaches main.

A library's loan rule, written in VE's English. VE turns the date wording into date arithmetic that Lean itself
works out (the last day of the loan), then asks Lean to check whether each borrower was late.
Run from the after-release checkout: python tour/stops/dates.py (tour/stops/04-date.sh does this).
"""
from datetime import date, timedelta

from ve.environment import Environment
from ve.surface.dates import lower_date_item
from ve.units import check_quantity_certificate, elaborate_quantity, prove_quantity

RULE = ("If the return date is after the last day of the period of 21 days beginning with the borrowing date, "
        "then the person is late.")
BORROWED = "2026-11-03"
RETURNS = (("Ann", "2026-11-24"), ("Bo", "2026-11-23"))
EPOCH = date(1970, 1, 1)
FACTS = {"the person is late": ["unary", "late", ["const", "p"]]}


def environment():
    day = lambda phrase: {"sort": "$int", "unit": "day", "description": phrase, "verbalisation": phrase}  # noqa: E731
    return Environment({
        "language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"person": {"description": "a borrower"}},
                       "predicates": {"late": {"arguments": ["person"], "description": "the person is late"}},
                       "constants": {"p": {"sort": "person", "description": "the person"},
                                     "last_day": day("the last day of the loan")}},
        "unit_schema": "ve-units@1", "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}}}})


def shown(iso):
    return date.fromisoformat(iso).strftime("%A %d %B %Y").replace(" 0", " ")


def main():
    env = environment()
    print("The rule:", RULE)
    print("Borrowed on", shown(BORROWED) + ".")
    case = {"dates": {"the borrowing date": BORROWED, "the return date": RETURNS[0][1]}}
    [rule] = lower_date_item(env, RULE, case, facts=FACTS)["premises"]
    # VE's reading of "the last day of the period of 21 days beginning with the borrowing date": the term the rule's
    # date comparison ends with. Lean works it out to a day.
    term = rule["formula"][1][3]
    worked = elaborate_quantity(env, {"format": "ve-quantity@1", "formula": [
        "date_on", ["const", "day", "last_day"], ["cal", term]]})[0]
    last = (EPOCH + timedelta(days=int(worked["formula"][2][2]))).isoformat()
    print("Lean works out the last day of the loan:", shown(last) + ".")
    late = elaborate_quantity(env, {"format": "ve-quantity@1", "formula": ["unary", "late", ["const", "p"]]})[0]
    for name, returned in RETURNS:
        lowered = lower_date_item(env, RULE, {"dates": {"the borrowing date": BORROWED, "the return date": returned}},
                                  facts=FACTS)
        premises = [elaborate_quantity(env, p)[0] for p in lowered["premises"]]
        certificate = prove_quantity(env, premises, late)
        checked = certificate is not None and check_quantity_certificate(env, premises, late, certificate)
        print(f"{name} returned the book on {shown(returned)}. Is {name} late? "
              + ("Yes: Lean checked it." if checked else "Not shown: no proof that Lean accepts."))


if __name__ == "__main__":
    main()
