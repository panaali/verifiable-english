# me-8 delta: consistency of printed numbers, the Lean meaning, checkers and runner

Base `287d5dc60` (`git merge-base HEAD main`). **Public output: none.** me-8 adds Lean modules
(`lean/VE/Calc/Interval.lean`, `Consistency.lean`, `ConsistencyExamples.lean`) and `tests/test_calc_consistency.py`.
No service mode, command, route, wire form, schema, Python product code or Rust file changes, so no verdict,
diagnostic, fault order or line a user can see changes: an existing `ve-calc@0` request answers as on main, field for
field (`test_an_existing_request_answers_as_before`, its answer recorded at the base), and a `consistent` claim is
still refused as before (`test_a_consistency_claim_is_not_on_the_wire_yet`: `InvalidInput: claims.0.claim must be a
claim`); the wire form is me-8b's. No approved statement changes: `tools/lean_statements.py --check` reports 0
removed and 0 changed, and spec 8.1's 15 declarations appear verbatim (`evidence/check_statements.txt`). The runner's
limits (the outputs' 10,000 nodes together, each pass charged by input and node, the digit hold on enclosures) are not on
the wire either: nothing a user sees changes, and me-8b adds them to the spec's limit table with the wire form.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trusted base: K +0, S +8, untied V +0, trusted +8 (`uv run python tools/trust_map.py --check`: PASS with the allowance in `docs/trust-baseline.json`): `lean/VE/Calc/Interval.lean` S +4 (`InBox`), `lean/VE/Calc/Consistency.lean` S +4 (`Consistent`), both spec 8.1's text. Every checker is C, tied by its theorem (`enclose_sound`, `consistent_of_witness`, `inconsistent_of_refutation`, `grain_sound`, `consistencyRun_holds`, `consistencyRun_fails`); the decoder's refusals and the point limit are G[R]. | Every new trusted definition is exercised by a check that can fail: [`trust-mutants.json`](trust-mutants.json) (15 ALLOWED, 0 KILLED, 0 SURVIVOR, 0 UNKNOWN, exit 0; reasons in [`trust-mutants-allow.json`](trust-mutants-allow.json): `InBox`'s two fail the `#guard`s at `ConsistencyExamples.lean:23-24`, read through its rebuilt `Decidable` instance; `Consistent`'s 13 break `consistent_of_witness` and `inconsistent_of_refutation`, as me-9b's `IsIdentity`); seeded bugs S1 to S18 in [`mutants.json`](mutants.json); FOLLOW-UPS.md "## me-8" asks for the ties pass. | R16 |
| 2 | `refuteByGrain` is the constant `false` on today's `Claim` (no `.stat` constructor until me-7b), so the second disjunct of `inconsistent_of_refutation` and `refuteByGrain_sound` are vacuous until me-8b; the granularity check is delivered as library theorems (`grain_sound`, `signFlip_grain_refutes`, `mean_grain_refutes`) with V-7, V-7b and V-8 as `grainRefutes` guards. | `ConsistencyExamples.lean`'s V-7, V-7b, V-8 `#guard`s and `v8_tiesUp`; test ids `v7-ties-up`, `v7-half-even`, `v7b`; the five theorems proved, no `sorry` (`python3 lean/audit.py`: PASS). | SIGNED by the DRI 2026-11-02 (reviews/dri-decisions-20261102-me-8.md item 1) |
