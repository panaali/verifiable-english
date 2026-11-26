"""Tour stop 10: what VE cannot do yet, shown on one rule. Runs from branch after-release until it reaches main.

A library's late fee is a daily fee multiplied by the number of days late. VE's English for amounts has sums
(stop 5) but no multiplication, so VE refuses to read the rule rather than guess at it.
Run from the after-release checkout: python tour/stops/not_yet.py (tour/stops/10-not-yet.sh does this).
"""
from ve.environment import Environment
from ve.errors import VEError
from ve.surface.time import parse_w6_sentence

GBP = "gbp_penny"
RULES = ("The late fee equals the daily fee plus the daily fee.",
         "The late fee equals the daily fee times the number of days late.")


def main():
    amount = lambda phrase, unit=GBP: {"sort": "$int", "unit": unit, "description": phrase,  # noqa: E731
                                       "verbalisation": phrase}
    env = Environment({
        "language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"item": {"description": "an item"}}, "predicates": {},
                       "constants": {"fee": amount("the late fee"), "rate": amount("the daily fee"),
                                     "days": {"sort": "$int", "description": "the number of days late",
                                              "verbalisation": "the number of days late"}}},
        "unit_schema": "ve-units@1", "units": {GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP"}}}})
    for rule in RULES:
        print("The rule:", rule)
        try:
            parse_w6_sentence(env, rule)
            print("  VE reads it (one reading).")
        except VEError as error:
            print(f"  VE refuses to read it ({type(error).__name__}): it has no reading of this sentence.")


if __name__ == "__main__":
    main()
