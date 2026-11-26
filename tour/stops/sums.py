"""Tour stop 5: a sum of amounts. Runs from branch after-release (the sums feature) until it reaches main.

A pizza shop's bill rule, written in VE's English, and one order of three pizzas. VE turns the rule into one addition
over exactly the pizzas the order lists, prints its own reading of that addition, and asks Lean to check the bill.
The shop's promise (a pizza is free if it arrives more than 30 minutes after the order) is not read by VE here: the
order itself states which pizzas are charged (p3 is free under the promise; p1 and p2 are charged as usual). Run from the after-release checkout: python tour/stops/sums.py (tour/stops/05-sum.sh does this).
"""
from ve.environment import Environment
from ve.surface.sums import lower_sum_item
from ve.units import check_quantity_certificate, elaborate_quantity, prove_quantity

GBP = "gbp_penny"
RULE = "The bill equals the sum, over each pizza that is charged, of the price of the pizza."
PROMISE = "A pizza is free if it arrives more than 30 minutes after the order."
# (id, pizza, price, minutes after the order it arrived, charged): the order's facts, as the shop's till states them
PIZZAS = (("p1", "margherita", "9.50", 22, True), ("p2", "pepperoni", "11.00", 22, True),
          ("p3", "four cheese", "10.50", 41, False))
CLAIMS = ("20.50", "31.00")


def main():
    charged = {pid: ok for pid, _, _, _, ok in PIZZAS}
    constants = {"bill": {"sort": "$int", "unit": GBP, "description": "the bill", "verbalisation": "the bill"}}
    for pid, _, _, _, _ in PIZZAS:
        constants[pid] = {"sort": "item", "description": pid}
        phrase = f"the price of the pizza ({pid})"
        constants["a_" + pid] = {"sort": "$int", "unit": GBP, "description": phrase, "verbalisation": phrase}
    env = Environment({
        "language": "ve.core@0.2", "profiles": ["order@0", "relational-fol@0", "time@0"],
        "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": {"sorts": {"item": {"description": "an item of the case"}},
                       "predicates": {"charged": {"arguments": ["item"], "description": "the pizza is charged"}},
                       "constants": constants},
        "unit_schema": "ve-units@1",
        "units": {GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP"}}}})
    atom = {pid: ["unary", "charged", ["const", pid]] for pid, _, _, _, _ in PIZZAS}
    facts = {f"the pizza ({pid}) is charged": f for pid, f in atom.items()}
    stated = [atom[pid] if charged[pid] else ["not", atom[pid]] for pid, _, _, _, _ in PIZZAS]
    amounts = [["eq", ["const", GBP, "a_" + pid], ["decimal", GBP, value]] for pid, _, value, _, _ in PIZZAS]
    case = {"items": {"pizza": [pid for pid, _, _, _, _ in PIZZAS]}, "facts": stated}

    print("The rule:", RULE)
    print("The order:")
    for pid, what, value, minutes, ok in PIZZAS:
        print(f"  {pid}: {what}, £{value}, arrived {minutes} minutes after the order, "
              + ("charged" if ok else "not charged (free: the 30-minute promise)"))
    lowered = lower_sum_item(env, RULE, case, facts=facts)
    print("VE's reading of the rule for this order:")
    for line in lowered["readback"]:
        print("  " + line)
    env2 = lowered["environment"]
    premises = [elaborate_quantity(env2, {"format": "ve-quantity@1", "formula": f})[0] if "format" not in f
                else elaborate_quantity(env2, f)[0]
                for f in lowered["premises"] + stated + amounts]
    for claim in CLAIMS:
        goal = elaborate_quantity(env2, {"format": "ve-quantity@1",
                                         "formula": ["eq", ["const", GBP, "bill"], ["decimal", GBP, claim]]})[0]
        proof = prove_quantity(env2, premises, goal)
        checked = proof is not None and check_quantity_certificate(env2, premises, goal, proof)
        print(f"Is the bill £{claim}? " + ("Yes: Lean checked the addition." if checked
                                            else "VE has no proof that Lean accepts, so it does not say so."))


if __name__ == "__main__":
    main()
