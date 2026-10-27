# me-2c report: the `calc` rows' fields (math-evidence ME-2, third part)

No DRI signature is reserved. DELTA rows 1-3 cite R3 and row 4 R16. Delivered: (1) `line`, `display`, `sides`,
`tie` and `finding`. Not delivered: (2) `rests_on` stops on a spec gap, and (3) the words checks become **me-2d**,
because they change answers on main. Both are below, under "Not delivered".

## Statement gate

ME-S passed its bounded re-checks (manage-agents `math-evidence-p3ver1.final.md`, then `math-evidence-p3ver2.final.md`:
PASS). Spec 3.4 has no theorem about the row fields, and this item proves none of the spec's statements anew.
`runMode_calc` (`lean/VE/Service/Protocol.lean`, not edited) and `runCaseReported_fits`
(`lean/ResponseShape/Encoders/Calc.lean`, re-proved) keep their reviewed text unchanged. Statement review J1 holds:
an exact value is written with Lean's `Int` printing, an optional "-" and no leading zero ("0" for zero). The `-`
sign is `toString` of the numerator, and the identity encoder is not touched.

## Plan rows delivered (task order)

| Row | Delivered | Where, checked by |
|---|---|---|
| (1) `sides`: each expression's exact value as a reduced fraction, `"n/d"` or `"n"`, or `null` | yes | `VE.Calc.Run.sides`, `exact`, `claimFields`. Uses the same bounded evaluation as `Claim.run`: `Expr.evalL (valuesL ds)`, computed once per case |
| (1) `display`: 2.5's truncated decimal at the printed places | yes. Truncated toward zero two places beyond the printed ones, "…" when a nonzero remainder was dropped, and the sign kept. Only for rounding claims with a value | `VE.Calc.Run.truncated`, `display` |
| (1) `tie`: 2.2's flag | yes. `tieAt` at the printed places for `rounds` under either rule. `false` for an undefined value, as `Claim.tieSensitive` says. `null` for a `rounds` claim beyond a limit. `false` for every other claim | `VE.Calc.Run.tie` |
| (1) `line`: Lean's English (11.1) | yes. `English.renderClaim` / `renderFollows` (unchanged), with the request's value words. `null` where 11.2's rule or the words refuse a rendering | `VE.Calc.Run.line`, `wordsIn` |
| (1) `finding` | yes: always `null`. A standalone case is no translated document (2.5; 13.6 writes `null` in every row). The `{"kind", "text"}` finding belongs to ME-10's `calculation` content | `VE.Calc.Run.rowJson` |
| (1) shape and encoder | yes. `calc.json#/$defs/claim_row` has five alternatives: claim rows that hold or fail, are undefined, or are unknown, and follows rows that are decided or unknown. A holds/fails row has every side, a rounding claim's display and a `rounds` claim's tie. An undefined or unknown row has a side without a value, and an unknown row has no display. The number of sides is bound to the request claim's form, and a follows row has none of a claim row's members. `runCaseReported_fits` is re-proved, with `rowJson_fits`, `rowJson_fits_software` and `tie_fits` | `lake build`. Schema via `regen_generated.py --write` |
| (1) R3 for the new fields | DELTA rows 1-3 | the tests named there |
| (2) `rests_on` | **no: spec gap** (below) | |
| (3) `VerbalisationCollision`, `ValueWordsForm`, `ReservedWord` | **no: answers change → me-2d** (below) | |
| Do not edit `Protocol.lean`, `service_schema.py`. Keep `Run.lean`/`Wire.lean` edits to the row fields | kept. `Wire.lean` is not edited. `Run.lean` gains only the row-field section, `rowJson`'s new members and `outcome_sound`'s two field lemmas over the new `rowJson` | `git diff main...HEAD --stat` |
| Each check on both sides of each boundary | yes. `RunExamples.lean` `rowFieldCases` covers: display at, beyond and below the printed places; negative values; places 0, −2 and −7; exact and inexact; tie under each rule, at and next to a tie; printed bounds at a tie; undefined values and values beyond the digit limit; ranges and comparisons; follows rows. It also has the line guards (rendered, nested, words not in form, derivation), `wordsIn` (first and last value, absent name) and zero displays. Route case 23 of `tests/data/route-cases.jsonl` covers the same groups through the service | `test_row_fields_at_their_boundaries` |

## Not delivered

**(2) `rests_on`: the spec gap.** A row's `rests_on` lists each stated, counted or free value it reads, with its
source kind, its `support` and whether its span was checked. Spec 3.4's `Case` has only `decls`, `claims` and
`software`, and a `Decl` has only a name and a source, so no decoded case carries a value's `support` or `span`.
As the task directs, no field is added to the case. Two ways to close the gap, for the DRI: the spec adds `support`
and `span` to `Decl` (with a `decodeCase_keep`-style statement), or it lets the runner read them from the request,
as `line` reads the value words (`Run.wordsIn`). FOLLOW-UPS "## me-2c".

**(3) The words checks → me-2d.** I measured them with a temporary check in `Wire.value` and `Wire.decode`:
`valueWordsOk`, plus W6a's `checkVerbalisations` over the values' words. The check was reverted, and none of it is
in the branch.

- Route cases (`tests/data/route-cases.jsonl`, the `calc` rows run on main and with the check): case 18 changes
  from `DuplicateName: x` to `VerbalisationCollision(x, x)`. The other 21 are unchanged.
- me-2's fixtures (`lean/VE/Calc/RunExamples.lean`): 9 guards change.
  - `identityFaults` (:243).
  - The accepted-edge cases with words "w" (:279, :282).
  - The exact-digest cases with words "w" (:287, :291).
  - The 64-byte `words` case (:414).
  - The hostile set (:495).
  - Spec 3.3's derivation identity classes (:780).
  - me-2c's own `line-words` fixture (:848).

Each is an answer that becomes a refusal, or a refusal that becomes another one. No standing ruling covers that
verdict change, so (3) is cut to me-2d with this list, and no signature is reserved.

## Deviations

- A line that 11.2's rule refuses is `null`. Spec 9 says the display "then names the intermediate values", and 13.6
  writes `"<display>"`, but no Lean renderer builds that display yet.
- `ME2C-1` (`tools/relay-gate-allow.json`, by design): a `null` line retyped to a string is accepted. The line is
  Lean's text, and whether there is one is Lean's answer (R8).
- `binding_census.py` reports `/rows/*/sides` with no length binding, because it reads only `x-length`/`x-zip`. The
  length is bound by `x-case` alternatives, which Python checks.

All three are in FOLLOW-UPS "## me-2c".

## Trust (R16)

`tools/trust_map.py --check` on the final HEAD: K +0, S +0, untied V +50, PASS with the allowance in
`docs/trust-baseline.json`. All 50 lines are in `lean/VE/Calc/Run.lean`: the D[V] `wordsIn`, `line`, `exact`,
`truncated`, `sides`, `display`, `tie` and `claimFields`, plus the new lines of `rowJson` and `runCaseReported`. The
shape's new declarations are G[R], the `row_fits` proof tactic is P, and the `RunExamples` helpers are T
(`tools/trust-classes.json`). FOLLOW-UPS "## me-2c" asks for the ties pass.

`ve/assurance-manifest.json` pins `Run.lean` whole: 318 lines, with `wordsIn` and `claimFields` added to its
declarations, and the decoder total goes from 38,166 to 38,225. These are by-hand decoder pins, as the plan says.

## Seeded bugs and mutants

- [`mutants.json`](mutants.json): 10 seeded bugs, each applied alone and restored. All 10 were caught. All are Lean;
  no Python or Rust product code changed (`calc.json` is generated).
  - Runner bugs in `lean/VE/Calc/Run.lean`, one per field:
    - `line`: rendered without words.
    - `exact`: integers written as "n/1".
    - `display`: one place too few.
    - `tie`: an undefined value gives `null`.
    - `sides`: written in reverse.
    - `finding`: a string.

    Each breaks named `RunExamples` guards. The display bug was also run through `ve_service`, with the checker pin
    rewritten for that run, and fails `test_rows_carry_leans_sides_display_tie_and_line` and
    `test_row_fields_at_their_boundaries`.
  - Shape bugs in `lean/ResponseShape/Schemas/Calc.lean`:
    - A known tie typed `null`, and a rounding claim given two sides: four `tests/test_calc_service.py` tests refuse
      the genuine answers.
    - Follows rows required to carry the claim members: `rowJson_fits` fails to build.
- [`trust-mutants.json`](trust-mutants.json) with [`trust-mutants-allow.json`](trust-mutants-allow.json): a full run of
  `tools/trust_mutants.py --max-mutants 1000` on the final Lean change (a72685cc, ve-mac-1) over the 8 trusted
  definitions gives 58 KILLED, 0 SURVIVOR, 0 UNKNOWN, 8 INVALID, 9 ALLOWED, exit 0.
  - The first run had 7 survivors and 4 UNKNOWN. Two `wordsIn` survivors (the first value dropped) are now killed
    by a direct guard, and one by a zero-display guard. `truncated` was rewritten as one expression, so its `0 ≤ k`
    branch no longer exists.
  - The allowed mutants are:
    - equivalents: `den ≤ 1` for `den = 1`, a natural `≤ 0` for `= 0`, and `"-".take 1`;
    - mutants that do not elaborate: an inner match's default arm, a list literal for a `String` or for
      `vs.toList`.

## Tests

- New and changed:
  - `tests/test_calc_service.py`:
    - `test_rows_carry_leans_sides_display_tie_and_line`: spec 13.6's R-1, R-2 and R-3 rows.
    - `test_row_fields_at_their_boundaries`.
    - `test_sides_display_and_tie_are_bound_to_the_claims_form` (5 cases).
    - `test_a_follows_row_has_no_claim_members`.
    - 18 more row mutants in `test_answers_are_bound_to_their_request`.
  - Route case 23 in `tests/data/route-cases.jsonl`, with its expected rows.
  - `RunExamples.lean`: R-1 to R-4 in full, `rowFieldCases`, and the line, `wordsIn` and zero-display guards.
- `tools/relay_mutation_gate.py --route service:calc`: 1,451 mutants, 1,446 refused, 5 allowed (`ME2B-1`, and
  `ME2C-1` four times), 0 failures. Its first run on the row fields found three accepted retypes to `null`; the
  per-outcome alternatives above refuse them.
- Selected tests (`mac-pytest.sh --select`, ve-mac-1):
  - 606cc0e3: 2 failing tests in `test_enum_domains.py` (the new `tie` constants' skeleton admitted "BOGUS"). Fixed
    by the `flag` enumeration and `tie_fits`.
  - 12233511: `test_assurance_manifest.py`, 2 tests (the `Run.lean` pin). Fixed by the manifest entry. That file
    then passed (137) in the worktree, as did `test_enum_domains.py` with `test_calc_service.py` (50).
  - Every other selected unit passed. The final selected run is under "Final checks".
- No test is removed. No test in `main-known-red.txt` is touched.

## Size

Hand-written lines over the merge base (`git diff --numstat`):

- Lean: 303 (`Run.lean` 81, `RunExamples.lean` 74, `Schemas/Calc.lean` 83, `Encoders/Calc.lean` 65).
- Tests and fixtures: 95 (`test_calc_service.py` 94, route case 1).
- Side tables: 55 (`trust-classes.json` 38, allow entry 10, trust allowance 7).
- Manifest: 12.
- Evidence and docs: about 220 (this report 183, DELTA 12, `mutants.json` 15, the allow file 11).

That is about 685, over the ~600 guide by about 85. The product code and tests are about 400. The excess is
evidence, and three fixes made here rather than left to a later item: the per-outcome typing (the relay gate's
retype-null findings), the tie enumeration (`test_enum_domains`) and the manifest pin. Generated: `calc.json`, the
inventories, the binding census and answers, `trust-mutants.json`, the assurance doc and the pins.

## Pilot bytes and next item

0 expected (plan "Bytes: 0"); nothing is claimed. Next: qt-a3 (the protocol queue), me-5c, me-4, me-6c and ME-P2.
ME-3 (the Python relay) can read these rows. **me-2d** takes the words checks for the DRI, with the list above. The
`rests_on` gap waits for the DRI's spec choice.

## Final checks

- `lake build` (whole library), `regen_generated.py --write` then `--check` (33 entries), `trust_map.py --check`
  (K +0, S +0, V +50: PASS), `relay_mutation_gate.py --route service:calc` (0 failures), `trust_mutants`
  (exit 0, above).
- Selected tests on 0393af80 (`mac-pytest.sh --select`, ve-mac-1): all 382 units passed, exit 0.
  `gate_collection.py --check --prebuilt`: 8 added, 0 refused, 0 stale, 0 malformed.
- Not run: the full gate (the chain runs it on the final HEAD).

## Self-review against BUILDER-CHECKLIST

1. PASS: every field of genuine `calc` answers is dropped, retyped and mutated (`tools/relay_mutation_gate.py --route
   service:calc`: 1,451 mutants, 0 failures; `tests/test_route_row_schemas.py`), plus the 18 new row mutants of
   `test_answers_are_bound_to_their_request`.
2. PASS: the plan-row table above, with (2) and (3) not delivered and why. There is no Python copy of a Lean value:
   Python only checks the schema and the binding. There is no permanent report test. On overlap, only
   `foundation/me-1`, a stale branch, edits `Render.lean`, which I did not edit.
3. PASS: `mutants.json` (10 of 10 caught) and `trust-mutants.json` (exit 0).
4. PASS: `test_route_cases_answer_their_rows`: the 22 earlier route cases' outcomes are unchanged, plus case 23. The
   R-1 to R-4 goldens give the same ids and outcomes as main. No Rust changed.
5. PASS: `test_sides_display_and_tie_are_bound_to_the_claims_form`, `test_a_follows_row_has_no_claim_members`, and
   the side added, dropped and empty mutants in `test_answers_are_bound_to_their_request`.
6. PASS: no merge was needed (main is the merge base). The selected tests ran, and the gate is the chain's.
7. PASS: DELTA rows 1-3 cite R3 with its tests, and row 4 cites R16. No row is reserved.
8. PASS: DELTA lists every new member. No outcome, reason, refusal or id changes
   (`test_route_cases_answer_their_rows`; the `meaning_id`s and `claim_id`s of the RunExamples goldens are main's).
9. PASS: the selected plan ran `test_enum_domains.py` and `test_assurance_manifest.py`, and each caught a missing
   entry (above).
10. PASS: `runCaseReported_fits` is re-proved over the new `rowJson`. The `seed-schema-follows` seed breaks it.
11. PASS: no limit, budget or deadline changes. A value beyond the digit limit gives `null` sides, display and tie
    (`rowFieldCases` "digits"). The tests have no timing, only `HANG_TIMEOUT`.
12. PASS: no other mode's path changes. Each claim's expressions are evaluated once more for the sides (the same
    bounded `evalL`, `valuesL` built once per case), so the work grows by a constant factor, not exponentially.
13. PASS: no test is removed or renamed (`gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed).
