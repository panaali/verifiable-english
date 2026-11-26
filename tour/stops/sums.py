"""Tour stop 5: a sum of amounts. Runs from branch after-release (the sums feature) until it reaches main.

A travel policy's refund rule, written in VE's English, and one trip's three receipts. VE turns the rule into one
addition over exactly the receipts the case lists, prints its own reading of that addition, and asks Lean to check
the refund. Run from the after-release checkout: python tour/stops/sums.py (tour/stops/05-sum.sh does this).
"""
from ve.environment import Environment
from ve.surface.sums import lower_sum_item
from ve.units import check_quantity_certificate, elaborate_quantity, prove_quantity

GBP = "gbp_penny"
RULE = "The refund equals the sum, over each receipt that is approved, of the amount of the receipt."
RECEIPTS = (("r1", "train ticket", "84.50", True), ("r2", "hotel night", "212.00", True),
            ("r3", "hotel minibar", "18.75", False))


def main():
    constants = {"refund": {"sort": "$int", "unit": GBP, "description": "the refund", "verbalisation": "the refund"}}
    for rid, _, _, _ in RECEIPTS:
        constants[rid] = {"sort": "item", "description": rid}
        phrase = f"the amount of the receipt ({rid})"
        constants["a_" + rid] = {"sort": "$int", "unit": GBP, "description": phrase, "verbalisation": phrase}
    env = Environment({
        "language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"item": {"description": "an item of the case"}},
                       "predicates": {"approved": {"arguments": ["item"], "description": "the receipt is approved"}},
                       "constants": constants},
        "unit_schema": "ve-units@1",
        "units": {GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP"}}}})
    approved = {rid: ["unary", "approved", ["const", rid]] for rid, _, _, _ in RECEIPTS}
    facts = {f"the receipt ({rid}) is approved": f for rid, f in approved.items()}
    stated = [approved[rid] if ok else ["not", approved[rid]] for rid, _, _, ok in RECEIPTS]
    amounts = [["eq", ["const", GBP, "a_" + rid], ["decimal", GBP, value]] for rid, _, value, _ in RECEIPTS]
    case = {"items": {"receipt": [rid for rid, _, _, _ in RECEIPTS]}, "facts": stated}

    print("The rule:", RULE)
    print("The trip's receipts:")
    for rid, what, value, ok in RECEIPTS:
        print(f"  {rid}: {what}, £{value}, {'approved' if ok else 'not approved'}")
    lowered = lower_sum_item(env, RULE, case, facts=facts)
    print("VE's reading of the rule for this trip:")
    for line in lowered["readback"]:
        print("  " + line)
    env2 = lowered["environment"]
    premises = [elaborate_quantity(env2, {"format": "ve-quantity@1", "formula": f})[0] if "format" not in f
                else elaborate_quantity(env2, f)[0]
                for f in lowered["premises"] + stated + amounts]
    for claim in ("296.50", "315.25"):
        goal = elaborate_quantity(env2, {"format": "ve-quantity@1",
                                         "formula": ["eq", ["const", GBP, "refund"], ["decimal", GBP, claim]]})[0]
        certificate = prove_quantity(env2, premises, goal)
        checked = certificate is not None and check_quantity_certificate(env2, premises, goal, certificate)
        print(f"Is the refund £{claim}? " + ("Yes: Lean checked the addition." if checked
                                            else "VE has no proof that Lean accepts, so it does not say so."))


if __name__ == "__main__":
    main()
