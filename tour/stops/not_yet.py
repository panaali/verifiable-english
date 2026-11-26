"""Tour stop 10: what VE cannot do yet, shown on three ways to write a late fee. Runs from branch after-release until
it reaches main.

VE's English for amounts has sums (stop 5) but no multiplication and no percentages, so VE refuses to read the second
and third rules rather than guess at them.
Run from the after-release checkout: python tour/stops/not_yet.py (tour/stops/10-not-yet.sh does this).
"""
from ve.environment import Environment
from ve.errors import VEError
from ve.surface import time as amounts

GBP = "gbp_penny"
RULES = ("The late fee equals the daily fee plus the daily fee.",
         "The late fee equals the daily fee times the number of days late.",
         "The late fee equals 10 percent of the price of the book.")
READ = amounts.parse_w6_sentence  # VE's reader of one sentence about amounts


def main():
    amount = lambda phrase, unit=GBP: {"sort": "$int", "unit": unit, "description": phrase,  # noqa: E731
                                       "verbalisation": phrase}
    env = Environment({
        "language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"item": {"description": "an item"}}, "predicates": {},
                       "constants": {"fee": amount("the late fee"), "rate": amount("the daily fee"),
                                     "price": amount("the price of the book"),
                                     "days": {"sort": "$int", "description": "the number of days late",
                                              "verbalisation": "the number of days late"}}},
        "unit_schema": "ve-units@1", "units": {GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP"}}}})
    for rule in RULES:
        print("The rule:", rule)
        try:
            READ(env, rule)
            print("  VE reads it (one reading).")
        except VEError as error:
            print(f"  VE refuses to read it ({type(error).__name__}): it has no reading of this sentence.")


if __name__ == "__main__":
    main()
