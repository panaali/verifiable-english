# Encoder notes: cases_xfam.py (hos_driving, 49 CFR 395.3 + 395.2)

`python3 -I check.py out/cases_xfam.py` prints: `OK: 35 cases, 7 probes, 25 activity keys` (no warnings that a stated duration differs from its clock times).

## Counts
- Cases (scope "in", all expressible in translation.FACTS): 35 (H001–H035), 107 questions.
- Probes: 7. These are the scope-"out" cases H036–H042, one question each. No in-scope case had to be made a probe.

## Conventions
- Records were copied from the facts text with a regex (the copying script itself is not kept). Log entries keep the stated clock times as `YYYY-MM-DDTHH:MM`. Durations are copied as `(0, hours, minutes)`. Questions use the template's `form()` and the clock time written in the question.
- `every_day` and `designated` come from Maple Transport's sentence, because Maple Transport is the employing carrier in every case.
- Activity key = the activity words as stated, with the driver's name replaced by "the driver". The two taxi rides in H024 get case-prefixed keys ("H024: …"), because reading them as testing depends on that case's stated carrier direction.
- "The truck" is the property-carrying commercial motor vehicle the driver drives (as stated).
- `head_work` is true for work done for a motor carrier and for stated readiness to work.
- Home, restaurant meal, parked-truck rest and sleeper rest are `relieved`, because the facts state a release by all employers. No work fact is true for them.
- Every fact not listed is false (closed world, encode.py C1).

## Judgements (one per key or case id)
- `resting in the parked truck`: in_on_cmv + rest_parked. The parked truck is the CMV, and 397.5 is stated not to apply.
- `resting in the sleeper berth`: in_on_cmv + rest_sleeper. The berth is in the truck.
- `driving the truck`: at_controls (the facts state every truck-driving activity is at the controls while in operation) + in_on_cmv.
- `riding in the passenger seat … with no task other than riding`: ride_passenger + in_on_cmv. No task or readiness is stated, so head_work is false, and so is relieved (not stated).
- `supervising other workers unloading the truck`: loading (limb (5), "supervising … the unloading").
- `giving receipts for the shipments just unloaded`: loading (limb (5)).
- `receiving receipts for the shipments just unloaded`: loading (limb (5)).
- `servicing the truck`: inspecting. The fact covers inspecting, servicing or conditioning (limb (2)).
- `filling in shipment paperwork at the terminal for Maple Transport`: carrier_work (limb (8)).
- `filling in payroll paperwork at the terminal for Maple Transport`: carrier_work (limb (8)).
- `waiting at a shipper's dock for dispatch; … requires immediate readiness …`: wait_dispatch (shipper's property) + head_work (required readiness). Not relieved.
- `waiting at the terminal for a future dispatch; … expressly released …`: wait_dispatch + relieved. No readiness is required, so head_work is false.
- `H024: traveling as a passenger in a taxi from the terminal to the collection site`: testing (limb (7) includes travel; H024 states the carrier's direction and part 382). A taxi is not a CMV, so in_on_cmv and ride_passenger are false.
- `H024: traveling as a passenger in a taxi from the collection site to the terminal`: read the same way as the trip to the site.
- `providing a urine specimen at the collection site`: testing. It occurs only in H024, where the carrier's direction and part 382 are stated.
- `working a paid shift stocking shelves at a store operated by Hazel, who is not a motor carrier`: paid_other (limb (9)). head_work is left false, reading the head as work for the carrier.
- `H027`: every_day and designated come from Maple Transport (stated to employ Dora at the queried time). Loading for Cedar Transport counts as on-duty loading ("regardless of the number of motor carriers").
