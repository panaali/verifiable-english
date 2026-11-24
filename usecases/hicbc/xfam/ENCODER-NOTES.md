# Encoder notes: cases_xfam.py

`python3 -I check.py out/cases_xfam.py` prints `OK: 25 cases, 7 probes`.

## Counts
- Households: 32
- In-scope records in CASES: 25 (H001-H025)
- PROBES: 7 (H026-H032, all scope "out"). No in-scope household was put in PROBES: the vocabulary can state every one of them.

## Conventions used
- The template's record format and helpers: `cb`, `lw`, `rel`, and the week ranges `S` and `S26`. Each range's first and last Monday appear verbatim in the facts that use it.
- ANI: every stated adjusted net income is recorded as a whole-pound string, including the children's stated £0.
- Child benefit: one `cb` record per stated entitlement period, with the stated weekly amount and its first and last Monday. Basis is "a" when the facts say the child lives with the claimant, "b" when they say the claimant contributes to the cost, and "145a" when they cite s.145A.
- s.13A elections: "all" when the facts say an election has effect for every amount (H017), and the stated week range when it covers only some weeks (H018).
- Lives-with: an `lw` record for every stated "lives with ... for the purposes of s.143(1)(a)" period. This includes the claimants on basis "a", even though the bridge adds them anyway.
- Weeks outside the tax year are transcribed when the facts state them: H020's 1 April 2024 and 7 April 2025, and the s.143(1)(a) weeks either side of the "b" periods in H023 and H024. The bridge only counts Mondays inside the year, and it uses the outside weeks for the s.681D(4) facts.
- Relationships: `married_or_cp` covers both marriage and civil partnership. `sep_court` and `sep_permanent` start on their stated dates. `as_if_married` is recorded only where the facts state it. The `to` date is left open (None) whenever the facts say the relationship still holds.
- Closed facts: anything stated as never holding, or as "no other", is left out.
- `unstated_dates_ok` is not used.

## Judgements
- H015: "until they stopped living together on 4 June 2025" is recorded as living together up to and including 4 June 2025, the stated end date.
- H019: the s.145A amounts after Ivy's death have is_child set to true, because the build gives every item that value. They are recorded with basis "145a" as stated.
