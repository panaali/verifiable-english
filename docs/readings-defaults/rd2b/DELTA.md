# RD-2b: relay and generators under the completion (Python)

Batch RD-2b of [readings-defaults-PLAN.md](../../spec/readings-defaults-PLAN.md) (its RD-2b section and table row), on
the wire of [readings-defaults.md](../../spec/readings-defaults.md) 3, 4.2 and 4.3, on branch
`readings-defaults/rd2b` from `main` at `51853586`. Built by one worker session on 2026-10-08; no model was called.
The section lists no Lean statement (spec 6 has none for RD-2b): no statement was added, changed or removed, and RD-1's,
RD-2a's and RD-6a's still check exact. Every number below is in [evidence/gate.json](evidence/gate.json) or the
evidence files it names, and `tests/test_readings_defaults_rd2b_report.py` checks this file against them.

## What changed

- **Relay** (`ve/readings_route.py`). Under `norm-defaults@0`, `readings-elaborate` is relayed: Lean's text verbatim,
  else its row bound to the request (the route, the finding naming every open set, each choice a reading with content
  of every open set, no choice twice, the count the list's own). RD-2a's refusal by name (`UNDER_COMPLETION`) is gone.
  `fill_premises` and `filled` are bound to the request on `readings-validate` and `readings-elaborate`
  (`_bind_completion`): present exactly under the completion beside a content-bearing set, one `Fill_T` per reading
  with content in admission order, each label naming a declared obligation and its permission, the filled
  environment keeping the request's sorts, constants and predicates and adding base predicates only, the filled units
  the request's in source order and then Lean's generated units, each a rule named by its unit whose guard reads an
  added table. Python regenerates none of it: no search, count, limit or name-prefix classification.
- **English** (`Wording`, `ve/readings_s2_wording.py`). The documents behind the English are Lean's filled ones; the
  `<reading>` slot shows what the author wrote (`Candidate.authored`). A filled table is no fact of a shown situation:
  after the situation, each of its points gets norm-defaults 3.2's sentence, "Here the text does not say whether …;
  this situation answers 'yes'." (spec 2.2, reused verbatim), on S1's pair sentences (E19, E21) and on S2a's
  results (R3 to R5 inside E12).
- **Generators** (`ve/readings_s1.py`). Under the profile the S1 frame is Lean's `filled.environment`
  (`S1Environment(data, filled)`; without it there is no frame, `CheckerUnavailable`), and each reading's document is
  built from Lean's filled units (`decode_filled`). The search's witness filter evaluates Lean's `fill_premises` on the
  base (`Decoded.fill_holds`, the generator-internal evaluator of rule 3). `_placeholder_frame` is deleted
  ([LEDGER.md](LEDGER.md)).
- **Each choice** (`ve/readings_verdicts.py`). Under the completion the compatible choices are Lean's (the elaborate
  row), and each choice's evidence is generated over Lean's `norm-defaults-elaborate` row for it
  (`_FilledChoiceDocument`): conflict packages proved from `Fill_T` over `E‴_base` and bound to the choice's own
  environment id and document hash, filled witnesses, certificates bound to the source environment
  (`norm_defaults_route.filled_certificate`, split out of `prove_filled_entailment`), base models with a separate
  filling. Every piece goes back to `readings-choice`. No `UnspecifiedDocument` is built for a readings document.
  Python's fold over the choices is unchanged (RD-3 moves it to Lean).
- **Lean** (one addition, below): `readings-elaborate` under the completion also answers `fill_premises` and `filled`
  (`runElaborateNDFilled` through `runElaborateNDWith`; `runElaborateND` is the same runner with nothing after the
  route's fields, so `elaborateND_fits` keeps its statement), with `elaborateNDFilled_fits`.
- **Inventories**: `readings-route.json` regenerated, frozen hashes, axioms, declarations, trust classes, the
  assurance pin of `UnspecifiedWire.lean`, `checkers.lock` (`ve_service`), the gate collection.
- **Tests** (`tests/test_readings_nd_document.py`, 61): F-ND1 and F-ND2 through `ve document load`, `check`, `render`
  and `readings --conclusion`; F-ND5's reserved name as Lean's text; the generator on F-ND1; the relay's binding under
  mutated genuine rows. RD-2a's refusal tests became relay tests (`test_rd2b_completion_document_is_checked_not_refused`,
  `test_rd2a_review_b3_route_table_is_lean_s`); the placeholder test reads Lean's filled frame; the readings
  differential's search reads Lean's filled document under the profile.

What the fixtures show, all from evidence Lean checked: F-ND1 is CONFLICT-FREE under both readings, with a model;
the query "every agent must help each user" is SOME (a certificate under the first reading, accepted with its
choice's conflict packages; a base model and filling under the second, where the duty's gap is filled 'no'), ALL
under the first and NONE under the second. F-ND2 is CONFLICT under its first reading (a latent conflict: the filling
answers 'yes' to "may be tried") and CONFLICT-FREE under its second, and its query is gated (`UNKNOWN (conflict
status: CONFLICT)`).

## Deviations, each for the spec owner or the reviewers (EXTERNAL)

1. **`readings-elaborate` carries the filled document.** Spec 3 lists `fill_premises` and `filled` on
   `readings-validate` and `readings-separate`. A generator needs them before any separating situation is recorded,
   but `readings-validate` refuses a document whose separations are pending, and `readings-separate` (as RD-2a built
   it) neither carries them nor runs without a recorded situation. `readings-elaborate` admits without the situations,
   so its completion row now ends with the two fields (a Lean definition and response-shape addition; no statement).
   `readings-separate` still does not carry them (RD-2a's row; nothing here reads it).
2. **Every filled gap of a shown situation is shown.** Spec 2.2 shows "one sentence per filled gap the result depends
   on", which Lean's English plan selects (RD-3, `coneOf`). Until then every point of every filled table over the
   situation's elements is shown with its answer: a superset, never an omission, and no selection made in Python.
3. **The generator fixture.** Unaided, the search finds for F-ND1 a separation Lean admits that is not 3.3's: witness
   `asks`, every table empty, `help_required(a, u)` false (spec 8.1 row 1.7's situation); the 3.3 base with the
   permission filled 'no' is rejected for witness `every` by Lean's `Fill_T` (F-ND1′). With the 3.3 situation's base
   as a hint the search finds exactly the 3.3 situation.
4. **Finding for another owner.** A model of the choice's document from the generic model search names elements
   `e0` in every sort, so a shown countermodel reads "e0 is an agent; e0 is a user" (the S1 search names them `a`,
   `u`). Unchanged here; it is the model search's naming.

## Availability change (HUMAN: DRI to sign)

A `readings@1` document with content under `norm-defaults@0` on the norms chain, which RD-2a's `ve document` refused
by name (`UnsupportedProfile: … ve document relays their checks from readings-defaults RD-2b`), now loads, checks,
renders and answers queries across readings. Its English is new: S1's pair sentences and S2a's results, with the
filled-gap sentences after a shown situation. No other document changes: the corpus A/B below has none.

## Gate (HEAD `65760273`, this worktree with a clean status)

| Check | Result |
|---|---|
| `lake build` | 837 jobs, success |
| `python3 lean/audit.py` | PASS: 452 source files, 4802 theorems (base 4801), standard axioms only |
| `python3 VE/Route/frozen.py` | PASS |
| `tools/lean_statements.py --check` | PASS: 4422 statements (base 4422), 0 changed, 0 removed |
| `tools/check_readings_defaults_statements.py` | RD-1: 31 exact, 0 pending; RD-2a: 16 exact, 0 pending; RD-6a: 7 exact |
| `tools/relay_lint.py` | PASS (no readings module holds a reserved completion name) |
| `tools/response_schemas.py --check`, `tools/trust_map.py` | PASS; 0 unclassified |
| fixtures `tests/test_readings_nd_document.py` | 61 passed |
| full suite in 6 chunks of test files (`-n 16`, the gate's arguments and plugins, `VE_LEAN_PREBUILT=1`) | 1586, 4216, 1563, 1645, 1928 and 1473 passed; 1, 0, 3, 3, 0 and 0 skipped; 0, 0, 0, 2, 0 and 0 failed |
| corpus A/B (`tools/lean_first_diff.py`, base `51853586`, head `9baf53d3`, whose `ve/` and `lean/` are HEAD's) | 96608 records, 96604 the same, 4 unavailable on both sides, 0 changed |

The 2 failures are `tests/test_precommit_hook.py::test_wire_contract_checks_staged_generated_table` and
`::test_wire_contract_accepts_staged_equivalent_json`; both fail the same at the base `51853586` (the hook runs the
system Python, which cannot import `conformance.softnorms_legacy` from the staged copy): not RD-2b's. The 4 records
unavailable on both sides are the constitution pilot's `readings/s1.ve.md` of four runs, `CheckerUnavailable` from the
English reader's lexicon on both sides, so they are no evidence either way. The A/B covers the readings and
norm-defaults corpora (3157 records), the pilots, rights and discourse corpora (9243) and the probe, conformance and
quantity corpora (84208): [evidence/ab-*.json](evidence/). No corpus document is under the completion.

Not run: `tools/gate.py` in a fresh worktree (it does not fit one 60-minute foreground call; the chunks above are its
suite); the plan's latency budgets on a quiet host.

## Latency

`readings-elaborate` of a completion document, in CPU seconds per request of the `ve_service` process, the base build
(`3b424ee9`) and this one (`0cc52a47`) timed in turn on the same host (load about 22 on 32 cores),
`docs/readings-defaults/rd2b/latency.py` on RD-2a's documents; the two answers differ exactly by the two fields, which
equal `readings-validate`'s:

| `n` fixed units | first run, before | after | repeat, before | after |
|---|---|---|---|---|
| 10 | 2.72 | 7.57 | 2.03 | 3.73 |
| 20 | 6.05 | 9.06 | 4.15 | 5.52 |
| 30 | 18.13 | 13.49 | 7.13 | 8.75 |

The first run (3 calls) is dominated by the host's load (its 30-unit row inverts); the repeat (4 calls) shows the
filled document costing about 1.4 to 1.7 s per request at these sizes, paid at every load of a completion document
(`ve document` asks `readings-validate` and `readings-elaborate`, and both now build it). A request field asking for
it only when a generator needs it would remove the second build; not done here.

## Seeded bugs (each planted, its tests run, then removed; the Lean one rebuilt, its hash pinned for the run, and the build and pin restored)

| # | Bug | What failed |
|---|---|---|
| S1 | the relay no longer binds the readings' `Fill_T` lists to the request | 6 tests: `test_a_mutated_completion_answer_is_unavailable` |
| S2 | the completion's elaborate row relayed without binding its finding and choices | 7 tests: `test_a_mutated_elaborate_row_is_unavailable` |
| S3 | the S1 frame under the profile built by Python from the request instead of Lean's filled environment | 12 tests, among them `test_fnd1_load_relays_leans_route_and_filled_document` and `test_ruling4_lean_frame_reads_unspecified_as_deny` |
| S4 | the search's witness filter without Lean's `Fill_T` | 1 test: `test_generator_finds_separations_from_leans_filled_document` (Lean refuses the proposed situation) |
| S5 | the verdicts take only the first of Lean's compatible choices | 4 tests, among them `test_fnd1_check_every_choice_conflict_free_with_a_model` |
| S6 | a shown situation's filled gaps dropped from the S1 pair sentence | 2 tests: `test_fnd1_render_shows_the_situation_with_its_filled_gaps`, `test_fnd2_render` |
| S7 | conflict packages bound to the profile Background instead of `Fill_T` | 3 tests, among them `test_fnd1_check_every_choice_conflict_free_with_a_model` (Lean leaves the choice UNKNOWN) |
| S8 | the `<reading>` slot names Lean's filled content instead of the authored one | 5 tests, among them `test_fnd1_readings_conclusion_some` (first seeded at `candidate_sentence`, where it survived: for rule readings the batched rules decide the sentence; reseeded on the batch) |
| S9 | a filled table shown as a fact of the situation | 1 test: `test_fnd1_render_shows_the_situation_with_its_filled_gaps` |
| S10 | a choice's model sent with its filled tables in the base | 4 tests, among them `test_fnd2_query_is_gated_by_the_conflict` (Lean refuses the model: the tables are a filling) |
| S11 | S2a's situation shows filled tables as author facts | 1 test: `test_fnd2_check_conflict_under_one_reading_only` |
| S12 | Lean: the completion's elaborate row with an empty `fill_premises` | 18 tests, among them `test_genuine_completion_answers_are_relayed` and `test_rd2a_review_b3_route_table_is_lean_s` (dropping `filled` instead is refused at build time by `elaborateNDFilled_fits`) |
| S13 | a filled choice's conflict check falls back to CONFLICT-FREE when no package or witness is found (review B1) | 4 tests, among them `test_budget_zero_check_says_unknown_for_every_choice` (F-ND2, which has a real conflict, read CONFLICT-FREE at budget 0) |
| S14 | a lower-route choice's conflict check falls back to CONFLICT-FREE when no package or witness is found (B1's class) | 2 tests: `test_budget_zero_every_verdict_op_is_unknown` (M8 and M9) |

The report's own test fails on a wrong A/B total in this file, on a seeded bug naming a test that does not exist and
on a wrong latency cell (each tried once, then restored).

## Review fixes (rd-2b review)

**B1** (the UNKNOWN fallback of a choice's conflict check had no test): fixed as its class, budget handled fail-open.
`tests/test_readings_budget_zero.py` runs every public op of the superposed and enumerated routes and of both kinds of
choice document (`_FilledChoiceDocument`, `_ChoiceDocument`) with every budget at 0, on F-ND1, F-ND2, M6, M8 and M9,
and through `ve document check` and `readings --conclusion --under` on F-ND1 and F-ND2; a second pass certifies the
conflict status at the full budget first, so the entailment and premise fallbacks behind the gate of 14.8 are reached
too. Each answer that rests on evidence must be UNKNOWN (no certificate, no model). The op list is checked against the
classes: a new public op fails the test until it is swept or named as not budgeted. The finding's mutant (S13) and the
same fallback on the lower route (S14) are each caught; so were nine more fail-open mutants tried once (the superposed
witness fallback, the enumerated conflict and premise totals, the choice premise and entailment fallbacks, the
enumerated and superposed entailment fallbacks, a superposed candidate's fallback), each restored. No checker code
changed: HEAD already answered UNKNOWN on every path.

## Build checklist

| # | Status |
|---|---|
| 1 one contract | partly: every diagnostic and filled document is Lean's and relayed; the filled-gap sentence is norm-defaults' template; the relay's shape check of the two fields is hand-written beside the Lean-generated `readings-route.json`, as RD-2a's was |
| 2 differential fuzz | not applicable: the completion has no Python or Rust implementation; the relay's binding is fuzzed (item 4) |
| 3 normalization | not applicable: no text input |
| 4 untrusted output | done: genuine validate and elaborate rows with each new field dropped, emptied, duplicated, retyped (bool for int, null), reordered or rebound to another request are `CheckerUnavailable` (S1, S2, S12) |
| 5 malformed input | partly: the new fields' nodes are retyped in item 4; no 7/true/null/10k-deep sweep of the request |
| 6 three-valued verdicts | done: no package, certificate or model within the budget is UNKNOWN; evidence Lean refuses is `CheckerUnavailable`; the gate of 14.8 holds (F-ND2's query). Every public op of both routes and of both kinds of choice document runs at budget 0, before and after the conflict status is certified, on F-ND1, F-ND2, M6, M8 and M9 and through `ve document check` and `readings --conclusion` (`tests/test_readings_budget_zero.py`, which also fails when a new public op is neither swept nor named unbudgeted); S13, S14 |
| 7 deadlines | not applicable: the service's per-case deadline and the generators' existing budgets; no new loop |
| 8 exhaustive folds | not applicable: Python's fold is RD-3's |
| 9 English | partly: every line goes through its gate (E12's, S1's `s1_gated`); the reused filled-gap and pair sentences are not re-read here (their own gates) |
| 10 one admit() | done: `ve document` load, check, render and readings all relay Lean's one admission (`admitNDFull`) |
| 11 no regex of a real language | done: the relay reads Lean's labels and JSON structurally |
| 12 state machines | not applicable |
| 13 tests can fail | done: S1 to S14 |
| 14 hermetic | done: the new tests write under `tmp_path` only, read no environment variable, no sleep |
| 15 identity | done: packages bound to the choice's own environment id and document hash from Lean's row, certificates to the source environment; Lean checks both (S7) |
| 16 lists | done: gate collection, trust classes, assurance pin, frozen hashes, axioms, declarations, schema |
| 17 statement diff | done: no RD-2b statement; RD-1, RD-2a, RD-6a exact |
| 18 both directions | done: the witness filter on F-ND1′'s base and on 3.3's; ALL and NONE under each reading |
| 19 use-case formalisation | not applicable |
| 20 reports | done: `tests/test_readings_defaults_rd2b_report.py` checks this file against the saved evidence |
| 21 AGENT/HUMAN/EXTERNAL | done: the availability change is HUMAN (DRI); deviations 1 to 3 EXTERNAL (spec owner, reviewers); the rest AGENT |
| 22 hand-off | partly: all committed, the chunked suite on HEAD with a clean status, 74 GB free; `tools/gate.py` in a fresh worktree not run |
