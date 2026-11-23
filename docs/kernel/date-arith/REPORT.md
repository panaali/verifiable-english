# date-arith-build: report

Branch `date-arith-build` from main `df25d3c3b3`. Ruling: manage-agents `reviews/dri-ruling-date-arith-20261123.md`.
Design: manage-agents `reviews/spare/date-arith/` (PROPOSAL.md frozen at sha256 8bff883f..., SIZING.md sections 0, 2, 3,
9; CHALLENGE.md C1-C13). Deltas and trust rows: [DELTA.md](DELTA.md). Spec: docs/spec/units-schema.md section 6.2a.

## 1. What was built

- **Calendar** (`lean/VE/Time/Calendar.lean`): `parseIsoFrom lo` (`parseIso = parseIsoFrom 1970`, old callers
  unchanged), `minGroundYear` (1900), `Civil.Ground`, a decidable `Civil.Before`, `MonthEnd` (`last`, `next`),
  `Civil.addMonths` and its spec `Civil.MonthsLater`, `Civil.weekday` (0 = Monday), `nthWeekday`.
- **Wire** (`lean/VE/Time/Wire.lean`): `elabCal` (nodes `date`, `plus_months`, `plus_days`, `month_first`, `month_last`,
  `nth_weekday`) and its spec relation `CalDenotes`; the day term `["cal", E]` (`calDay`: valid dates only); the formula
  `["cal_cmp", op, E1, E2]` (`elabCalCmp`: today's date node over both day numbers when both are from 1970, so `Q` shows
  them (C1 fix 1); decided `top`/`bottom` when a date is before 1970) with `CalOrder`; `calInputs`/`inputsField`: each
  `cal`/`cal_cmp` node's source, compressed, bound into the canonical meaning object (`statementIds`) and shown in the
  report claim (`Document.claimJson`) (C1 fix 2; widened from the date leaves to the whole expression by review B4).
- **Cardinality** refuses ground date expressions (review B3: it binds no inputs).
- **Shell** `ve/surface/dates.py`: the written form (PROPOSAL 2.1-2.4) lowered to these nodes; C2 (two rules that
  conclude one date name, in one item or across the items of a case, are refused unless written exclusive; a case date is
  never concluded) and C3 (a date the case may lack is an ordinary day constant with today's nodes, never ground, never
  in a `Let`, per role).
- No change to Syntax, Semantics, the guard, the schema version, a profile or a `refuses` pair.

## 2. Proofs (SIZING section 3 as corrected in section 9; all in `lean/axioms.txt`, no `sorryAx`)

| Group | Theorems |
|---|---|
| 1, 2 | `addMonths_spec` (a month offset computes `MonthsLater`: kept day, else `last`/`next`, else none), `addMonths_none_missing` |
| 3 | `addMonths_ground` |
| 4 | `addMonths_mono` (both inputs ground, both results present; additivity not claimed) |
| 5 | `monthLast_spec`, `monthFirst_proper` |
| 6 | `weekday_epoch` (1970-01-01 a Thursday), `weekday_succ` (needs `Proper`) |
| 7 | `nthWeekday_spec` (valid, the month asked, weekday `w`, `(day - 1) / 7 = n - 1`) |
| 9 | `parseIsoFrom_valid`, `parseIso_eq`, `parseIso_valid` |
| 10 | `elabCal_sound` (listed): every date `elabCal` returns is the one `CalDenotes` names, and is `Ground` |
| 11 | `calDay_sound` (listed): a `cal` term's date is `CalDenotes`' and `Valid` |
| 12 | `calCmp_sound` (listed): in every tagged structure the formula holds iff `CalOrder op x y` for the denoted dates; the plus-days equation is `CalDenotes.plusDays` (from `num_addDays`) |
| 13 | the five wire theorems and `extension_document_sound`, unchanged statements, rebuilt over the extended decoder |
| 14 | `calCmp_agrees` (C7: for valid dates `cal_cmp` is today's date node), `statementIds_inputs` (C1: the meaning id is over the object with the inputs) |
| review B6 | `calDenotes_unique` (listed; with `monthsLater_unique`, `same_week_day`): an expression denotes at most one date |

Listed on `quantity` (tools/kernel-paths.json): `elabCal_sound`, `calDay_sound`, `calCmp_sound`, `calDenotes_unique`,
`weekday_epoch`, `weekday_succ`, `parseIsoFrom_valid`.

## 3. Tests

- `lean/VE/Time/CalExamples.lean`: #guard checks of every new definition (Calendar values and refusals, each node, each
  operator, inputs, meaning ids, the whole report claim); `lean/ResponseShape/QuantityClaimExamples.lean` (the claim
  schema); `lean/VE/Cardinality/WireExamples.lean` (the refusal).
- `tests/test_date_arith.py` (12 tests, through the Lean service): `test_cal_nodes_are_worked_out_in_lean_and_bind_their_input_dates`,
  `test_comparison_with_a_date_before_1970_is_decided_and_bound`, `test_week_window_and_birthday_on_the_boundary`,
  `test_last_day_of_the_nth_month_after`, `test_29_february_age_is_refused_and_readings_settle_it`,
  `test_concluded_dates_and_per_role_copies`, `test_overlapping_rules_concluding_one_date_are_refused_unless_written_exclusive`,
  `test_a_date_the_case_may_lack_is_a_day_constant_with_todays_nodes`, `test_let_sentences_have_one_value_and_come_first`,
  `test_review_b1_a_conclusion_about_a_day_constant_always_meets_c2`, `test_review_b2_c2_compares_the_rules_of_every_item_of_a_case`,
  `test_review_b9_b10_a_date_the_case_may_lack_stays_a_constant`.
- Failing first: on main the nodes are refused ("Invalid quantity term", "Unknown quantity formula cal_cmp"),
  `ve.surface.dates` does not exist and `CalExamples` does not compile.

## 4. Planted off-by-one errors (ruling item 2d)

Each plant was applied to the tree, the check run, and the plant reverted; all six seeded bugs (these four, and the C2 and C3 rules of the shell) are in [mutants.json](mutants.json).

| Plant | Edit | Answer it changes | Caught by |
|---|---|---|---|
| a day | `plus_days`: `D.addDays (k.toNat + 1)` | the week beginning 21 Sep 2026 ends 28 Sep, not 27 | `CalExamples.lean` the `plus_days` guards (lines 124-131) |
| a month end | `addMonths`: `D.day < monthLen y m` | 31 Jan 2025 + 2 months -> refused/rolled, not 31 Mar | `CalExamples.lean` `Civil.addMonths ⟨2025, 1, 31⟩ 2 none == some ⟨2025, 3, 31⟩` (and five more) |
| a leap day | `addMonths`: month length of the start year | 29 Feb 1960 + 66 years (last) -> refused, not 28 Feb 2026 | `CalExamples.lean` the 29 February guards (lines 72-74, 114-116) |
| a birthday | shell age: `before` for `on_or_before` | born 18 May 1951: not 75 on 18 May 2026 | `test_week_window_and_birthday_on_the_boundary` (and `test_29_february_age_is_refused_and_readings_settle_it`) |

The two Calendar plants first break `addMonths_spec`; with that proof cut to `sorry` (as trust_mutants does) the guards fail.

## 5. Mutants

Final record [trust-mutants.json](trust-mutants.json) (the default selection, the trusted declarations the branch adds or
changes; `--test lean/VE/Time/WireSound.lean --test lean/ResponseShape/QuantityClaimExamples.lean --allow
trust-mutants-allow.json`; at 17775b3795, Lean unchanged since): **exit 0, KILLED 43, SURVIVOR 0, UNKNOWN 0, INVALID 1,
ALLOWED 135**.

| File | KILLED | ALLOWED | INVALID |
|---|---:|---:|---:|
| lean/VE/Time/Calendar.lean | 9 | 62 (`MonthsLater` 34, `Ground` 27, `weekday` 1) | 0 |
| lean/VE/Time/Wire.lean | 3 | 67 (`CalDenotes` 43, `CalOrder` 15, `elabTerm` 6, `decodeQuantity` 2, `calNode` 1) | 0 |
| lean/VE/Time/Document.lean | 10 | 2 (`claimJson`, equivalent) | 0 |
| lean/VE/Cardinality/Wire.lean | 2 | 4 (equivalent) | 1 |
| lean/ResponseShape/Schemas/Quantity.lean | 19 | 0 | 0 |

The allowed mutants of the spec Props (`CalDenotes`, `MonthsLater`, `Ground`) are caught by the proofs only (each breaks
`elabCal_sound`, `addMonths_spec`, `monthsLater_cases` or `addMonths_ground`, as R16 allows for a Prop no check can
evaluate); `CalOrder`'s are read through its decidable instance, which the `CalOrder` guards refute; the others are
mutants Lean refuses (read as UNKNOWN) or equivalent ones. Each entry of
[trust-mutants-allow.json](trust-mutants-allow.json) gives its reason.

A wider sweep at 42dd981936 selected every new definition, the tied decoders (`elabCal`, `elabCalCmp`, `calDay`,
`addMonths`, `nthWeekday`) and the check helpers too: KILLED 160, SURVIVOR 4, UNKNOWN 1, INVALID 42, ALLOWED 211. The
four survivors were on the cardinality refusal line (its fuel plus or minus one under the 64-deep source limit, and
`take 1` before `isEmpty`: equivalent) and the UNKNOWN a `weekday` mutant the weekday guards refute; all five are allowed
in the final run with those reasons. A first sweep (before the review) found 113 survivors; the new checks of the report
claim, `calInputs`, the claim schema and `--test WireSound` turned them into kills or reasoned allowances.

## 6. Reviews

One Opus 5.5 review of the statements and the two lowering rules (manage-agents
`reviews/spare/date-arith/BUILD-REVIEW-OPUS.md`): SOUND WITH CHANGES, no HIGH; B1-B7, B9, B10 fixed in 42dd981936, B8 and
B11 kept as stated limits. The Codex review is after the reset (row date-arith-codex-review).
