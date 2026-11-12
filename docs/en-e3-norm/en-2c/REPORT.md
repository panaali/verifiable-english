# en-e3bb build report: the W1 shadow relay to `english.statement`, its binding, fuzz tests and the W1 delta report

**Summary.**
- **Status:** built and review-fixed (en-e3bb-review.final.md F1, F2); nothing is reserved for the DRI in this item.
- **What changed:** `parse_english`'s W1 path asks `english.statement` in shadow behind two env flags, schema-checked
  and bound (R8). The delta's suite corpus is now derived from coverage, and the REPORT's numbers and causes are
  checked against `delta.json` (section "Review fix").
- **Open:** the DRI's W1 decision gates en-e3, not this merge; the complete suite's new rows go to en-e3 (R9). Trust +0.

Scope: task-en-e3b.txt deliverables (1)-(4) without what en-e3b built (reviews/dri-decisions-20261110-en-e3b.md
item 1), under reviews/dri-decisions-20261102-en-e3-norm.md items 1-3.
SIZE: 216 product, 672 tests, about 700 other hand-written lines added: `git diff --numstat $(git merge-base HEAD main)`.
- Product is `ve/norm_english.py` 200 and `tools/relay_mutation_gate.py` 16.
- Tests are the six test files plus 1 fixture line.
- Other is `w1_delta.py` 373, `seed.py` 76, this report and `en-2c/DELTA.md`.
- Written by the scripts: `delta.json` 9,907 lines, the evidence DELTA.md 194 and `mutants.json` 118. Written by
  `tools/history_tests.py --write`: `tests/history-dependent.json` 19.

## Review fix (en-e3bb-review.final.md)

- **F1 (B): the suite corpus was a hand-kept list of 33 files.** 10 test files that call `parse_english` were
  missing, so their records were missing from the evidence, and the soft-rights corpus had the same gap. The class
  is a hand-kept corpus list that drifts. `w1_delta.py` now derives it: `derive_suite` takes the coverage map
  `select_tests` uses, every unit the map records running `parse_english`, and every unit it cannot rule out
  (unrecorded, failed, opaque, or changed since the map, `select_tests.uncertain_since`). With no map, the whole
  suite runs. `delta.json` saves the derivation and pytest's summary. The tagging plugin now tags only records written
  to the run's own log, so the shadow's own tests pass in the instrumented run. The run deselects the 5 tests that
  read its own output (`READS_OUTPUT`). `test_the_suite_run_deselects_exactly_the_tests_that_read_its_output` checks
  that set against the test file's source. The evidence was regenerated:
  suite 73 to 210 records, soft-rights 70 to 262, plus 23 records from `ve` subprocesses.
  Tests: `tests/test_w1_delta_suite.py` (the derivation over a map built in the test, and the plugin), and
  `check_suite` in `test_the_saved_delta_report_records_every_disagreement_with_its_class`. That check covers the 10
  files, the derivation's shape, a record from a test outside the suite, and a run that did not pass, and
  `test_the_suite_check_fails_on_a_hand_kept_or_incomplete_suite` is its other direction. Probe F1 passes.
- **F2 (A): the REPORT said Lean refuses soft-norms@0 environments, so no soft-rights W1 call is answered.** That was
  false: Lean answers them, and the 47 unavailable rows are `InvalidGrammar`. The class is prose claims about the
  evidence with no check. The note is corrected (Notes for the DRI, Soft environments). The cause list is now one line per corpus and class, and
  `test_the_report_s_delta_numbers_and_causes_are_the_saved_evidence` checks it against `delta.json`: the table, each
  line's count and cause, every group covered, and no "every <corpus> … `class`" sentence unless all its records have
  that class. `test_the_report_check_fails_on_review_f2_s_overclaim_and_on_a_wrong_number` is its other direction.
  DELTA.md's cause table now names the refusal behind each `unavailable` row, and `check_delta` requires this.
  Probe F2 passes.
- **Generated:** `tests/history-dependent.json` (by `tools/history_tests.py --write`), because the new test file
  imports `select_tests`.

## Deliverables

| Task line | Where | Test |
|---|---|---|
| (1) The W1 path sends `{id, environment, lexicon, kind: "blocks", source}` through `ve/backends/relay.py` only with both flags set. It keeps its own reading as the answer and logs the comparison with en-e3b's comparator. | `ve/norm_english.py` `parse_english` (dispatch, then the shadow around `_parse_w1`, the unchanged body), `statement_request`, `read_statement`, `_shadow` | `test_the_shadow_asks_lean_and_keeps_python_s_answer`, `test_the_shadow_needs_both_flags` |
| (1) The schema check | `statement_answer` runs `service_schema.check_row` (the generated `english.statement.json`), then the binding | `test_every_retyped_dropped_or_duplicated_member_is_unavailable` |
| (1) The binding: every rule number and span exists in the request; no block row is empty or extra; each rule row has exactly one span, inside the source, on UTF-8 boundaries, increasing and non-overlapping; no layout check | `statement_problem`, `_rule_problem` | `test_every_named_mutant_is_unavailable` (17-21 faults per `one` answer, singly and in pairs: 747 mutants), `test_p2_*`, `test_p3_*`, `test_an_extra_rule_row_over_a_precedence_line_is_unavailable` |
| (1) `SERVICE_READERS` | `_statement_reader` in `tools/relay_mutation_gate.py` | `test_english_statement_is_read_as_the_w1_shadow_reads_it` |
| (1) `tools/relay-gate-allow.json` | unchanged: the gate allows no mutant of the route. `relay_mutation_gate.py --route service:english.statement` gives "8 fixtures, 1533 mutants, 1533 refused, 0 allowed". | the gate |
| (1) A relay-gate `one` fixture with its reader | one row appended to `tests/data/relay-gate-cases.jsonl` (id `one`; main's rows kept, as en-e3b did) | the gate; `test_english_statement_is_read_as_the_w1_shadow_reads_it` |
| (1) Binding inventory rows (D9) | `tests/test_relay_binding_inventory.py`: `ROUTES`, `INVENTORY["english.statement"]`, `_statement_relays`, one `UNEXERCISED` row | `test_every_schema_field_is_classified[english.statement]`, `test_every_bound_field_mutant_is_unavailable[english.statement]`, `test_another_requests_genuine_answer_is_unavailable[english.statement]` |
| (2) Fuzz tests over genuine recorded answers, each rule row's `span` included, and P2, P3 | `tests/test_english_statement_answer.py` (12 tests) | itself |
| (3) The delta report, its suite derived from coverage | `docs/en-e3-norm/en-2/DELTA.md` and `delta.json`, written by `w1_delta.py` | `test_the_saved_delta_report_records_every_disagreement_with_its_class`, `tests/test_w1_delta_suite.py` (2 tests), `test_the_report_s_delta_numbers_and_causes_are_the_saved_evidence` |
| (4) The shadow test reads the saved delta; with the flag set and no `VE_SHADOW_LOG`, Lean is not called and no file is written; en-e3b's 16 tests kept | `tests/test_english_statement_shadow.py` (22 tests; 19 before review F1, F2) | `test_the_saved_delta_report_*`, `test_the_delta_check_fails_on_an_unlisted_or_misclassed_disagreement`, `test_the_shadow_needs_both_flags` |
| Stop-point message | `msg.sh dri en-e3bb "W1 delta decision for EN-3 …"`: "sent to dri: …/20261111T190003Z-en-e3bb-3935271.md" | — |

The commits are `main..HEAD --no-merges` on feature/en-e3bb.

## The delta report (saved evidence; `delta.json` at the commit DELTA.md names)

The command was `uv run python docs/en-e3-norm/en-2/w1_delta.py --workers 12 --scratch /tmp/e3bb-w1-scratch3`, on a
clean tree. The suite corpus is derived from coverage (review F1): every test unit that may call `parse_english`,
the ones the coverage map at the merge base `f4d52f1eb` records calling it and the ones it cannot rule out
(unrecorded, or changed since the map). `delta.json`'s `suite` saves the derivation and pytest's summary, and
DELTA.md quotes both counts and the summary.

| corpus | records | lean-unavailable | agree | lean-stricter | lean-looser | both-refuse |
|---|---|---|---|---|---|---|
| pinned (120 blocks) | 120 | 0 | 120 | 0 | 0 | 0 |
| suite (100 test units, derived from coverage) | 210 | 1 | 144 | 18 | 3 | 44 |
| suite-subprocess (`ve` processes the suite starts) | 23 | 0 | 16 | 0 | 1 | 6 |
| soft-rights (`_w1=True` calls) | 262 | 47 | 211 | 0 | 4 | 0 |
| udhr (norm units and readings, one at a time) | 47 | 1 | 0 | 37 | 0 | 9 |
| constitution (the probe translation's) | 14 | 14 | 0 | 0 | 0 | 0 |
| known (english-lean-s6.md section 5) | 15 | 0 | 3 | 2 | 9 | 1 |

`lean-unknown` and `different-node` are 0 in every corpus. No block is answered `NodeRefused` or `NodeLimit`
(DELTA.md, "Blocks Lean answers …: 0"). The causes, one line per corpus and class, as DELTA.md's "Rows by Lean's
answer" gives them (`test_the_report_s_delta_numbers_and_causes_are_the_saved_evidence` checks each line and the
table against `delta.json`):
- `suite` `lean-stricter` (17): `NoDerivation`, where Python admits (alternatives, asimov, risk, question fixtures).
- `suite` `lean-stricter` (1): `EmptyDocument`, a text `test_english_statement_answer.py`'s fuzz test reads.
- `suite` `lean-looser` (3): `one`: `test_four_wordings_and_identity_manifest` (Python's `IdentityMetadataMismatch`)
  and 2 texts of `test_english_statement_answer.py`'s fuzz test that Python refuses as layout.
- `suite` `lean-unavailable` (1): `CheckerUnavailable: Lean refused the request: UnsupportedProfile: alternatives@0 with norm-defaults@0`,
  in `test_et8_completion.py`.
- `suite-subprocess` `lean-looser` (1): `one`, where Python's `ve` process refuses a stale English export
  (`IdentityMetadataMismatch`).
- `soft-rights` `lean-unavailable` (47): `InvalidGrammar`, Lean's refusal of the request's lexicon (45 from
  `test_rights.py`, 2 from `test_english_unambiguity.py`).
- `soft-rights` `lean-looser` (4): `one`, rights lines with two carve-outs that Python refuses.
- `udhr` `lean-stricter` (37): `NoDerivation`, where Python admits.
- `udhr` `lean-unavailable` (1): `InvalidGrammar`.
- `constitution` `lean-unavailable` (14): `CheckerUnavailable: Lean refused the request: UnsupportedProfile: Unsupported profile soft-norms@0`.
  Lean refuses `soft-norms@0` only beside `norm-defaults@0`, which the constitution's environment has.
- `known` `lean-looser` (9): `one`: the layout rows (blocks sharing a line, a block over two lines, a blank line, a
  trailing line), lowercase `rule` and `except when`, double spacing, a tab and a self-precedence line.
- `known` `lean-stricter` (1): `NoDerivation`, `, except When`.
- `known` `lean-stricter` (1): `EmptyDocument`, the empty text.

The complete suite adds rows to the ones the DRI decided on 2026-11-11
(reviews/dri-decisions-20261111-en-e3bb-w1-delta.md): more `NoDerivation` rows of the item 6 groups, the
`EmptyDocument` and fuzz rows of `test_english_statement_answer.py`, and the `alternatives@0 with norm-defaults@0`
refusal. Item 7 already rejects every `lean-unavailable` row until en-e3-delta-close, and item 8b has en-e3 re-run this
script on its base and bring any row outside items 1-4 back to the DRI. So these rows are that later row's (R9). Python's
answer stays the answer here: the shadow changes nothing a user sees, and `en-2c/DELTA.md` has no row.

Two known differences, a predicate with a sort three times and one with no argument, have no text: their
environment is refused by `Environment` itself ("invalid signature"), so they are listed as
`known_not_constructible`.

## Seeded bugs (Python; each planted alone, shown failing, restored)

Each was run by `docs/en-e3-norm/en-2c/seed.py`, and the record is `mutants.json` (file, tests, failed): 10 of 10 caught.
Bugs 1-7 are in `ve/norm_english.py`, 8 and 9 (review F1) in `docs/en-e3-norm/en-2/w1_delta.py`, and 10 in
`tools/relay_mutation_gate.py`:
1. **An answer with one rule row more than the request's numbering allows is accepted** (the header binding gone;
   spec 9): `test_an_extra_rule_row_over_a_precedence_line_is_unavailable` fails.
2. **The span binding's overlap check dropped** (spec 9): `test_p2_…[overlap]` and `test_every_named_mutant_is_unavailable`
   fail.
3. **The shadow calls Lean with `VE_SHADOW_LOG` unset** (spec 9, P5): `test_the_shadow_needs_both_flags` fails.
4. **The binding accepts a span that ends inside a multi-byte character** (spec 9): `test_p2_…[off a UTF-8 boundary]`
   and `test_every_named_mutant_is_unavailable` fail.
5. **`over` not tied to the row's `exception_to` and precedence rows:**
   `test_every_retyped_dropped_or_duplicated_member_is_unavailable` fails.
6. **The spans not all bound before nodes are read:** `test_the_spans_bound_the_rule_rows_before_any_node_is_read`
   fails.
7. **A rule node's formulas may name an undeclared predicate or constant, or an unbound variable:**
   `test_every_named_mutant_is_unavailable` and `test_every_retyped_dropped_or_duplicated_member_is_unavailable` fail.
8. **The delta's suite is only the units the map records calling `parse_english`** (none it cannot rule out):
   `test_the_delta_suite_is_every_unit_the_coverage_map_cannot_rule_out` fails.
9. **The suite's tagging plugin tags every record** (a test's own record and log changed):
   `test_the_plugin_tags_only_the_records_of_its_own_log` fails.
10. **`tools/relay_mutation_gate.py`: the gate without the english.statement reader:**
   `test_english_statement_is_read_as_the_w1_shadow_reads_it` fails.

The spec's other two Python EN-2 bugs (the comparator's) were en-e3b's (`docs/en-e3-norm/en-2b/seeded-bugs.json`).
No Lean or Rust product code changed.

## Trust

- `uv run python tools/trust_map.py --check` gives "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0",
  PASS.
- `tools/trust_mutants.py --plan` gives `{"definitions": 0, "mutants": 0}` (no Lean file changed).
- The light lane prints NOT, because it counts the 6,893-line `delta.json` and the generated DELTA.md. The sweep
  would select nothing, so none was run.
- No FOLLOW-UPS row is needed (no R16 growth).

## Spec re-read

- The request against docs/spec/en-e3-norm.md:523-524.
- The identities against :526-527, as `english.read`'s binding builds them, with no overlay sent.
- Members and codes against :528-529, read from `codes.json` by `statement_codes()`.
- `one` numbering and ranges against :530-533.
- The spans against :534-538, with no layout check.
- `partial` (named `unformalised` since en-e3a item 2) against :539.
- The rejection's `sentence`/`span` against :540-541, and `class` against :542.
- The shadow's flags, record and partition against :569-594.
- The fuzz list against :560-566.
- The delta report against :596-611 and the tests against :613-621.
- P2, P3 and P5 against :1361-1371, and the seeded bugs against :1440-1446.

## Notes for the DRI

- **Bindings beyond the spec's list:**
  - each rule row's span begins with `rule <number>` (case-folded), which is how "every rule number it names exists
    in the request" is checked;
  - a rule node's `over` equals its `exception_to` followed by the precedence rows that name it (`Elab.overOf`);
  - the node's predicate is a regulated predicate of the request; every predicate and constant its formulas name is
    declared there, and every variable is in scope of the rule's arguments and quantifiers. These are names only:
    typing them is Lean's, and `tools/inventory_lint.py` bars new code from `ve.ast._Checker`, a class-A body.

  All of these refuse more; none accepts more. A Lean refusal of the request (an error row) is `lean-unavailable`.
- **What the binding cannot see:** a dropped last rule row that no precedence row names. The binding cannot count the
  text's blocks without reading it (R8). EN-3's manifest block count binds it. The fuzz test lists it as Lean's
  (`LEAN`), and the inventory classes `result.statements` as Lean's count.
- **The span end:** where a block ends inside the source is Lean's (`statementSpans`). The span is bound inside the
  source, on boundaries, at its header and in order.
- **Soft environments:** Lean answers W1 text in a `soft-norms@0` environment: 211 soft-rights records `agree` and
  4 are `lean-looser`. The 47 soft-rights `lean-unavailable` rows are Lean's `InvalidGrammar` refusal of the request's
  lexicon (review F2's probe: V6, predicate `rights__lim__1`), not a profile refusal. Lean refuses `soft-norms@0` with
  `UnsupportedProfile` only when `norm-defaults@0` is also in the environment, as in the constitution's, so the 14
  constitution units are `lean-unavailable` (probed again for this fix: `one` with `soft-norms@0` alone,
  `UnsupportedProfile` with both).
- **The `should` blocks:** the 17 "should" pinned blocks agree because the soft reader's `_w1=True` call reads the
  strict text it derives.
- **One test edited outside the Files list:** `tests/test_english_e2_ledger_sites.py`. Its ledger site moves from
  `parse_english` to `_parse_w1` with the reader call; the text is unchanged.
- **The shadow's own failures never change the answer.** A request Python cannot form, or a log it cannot write
  (`VEError`, `OSError`), is passed over, as `ve/english.py`'s comparator does. Python's refusal (`VEError`, or
  `CheckerUnavailable` from its own relays) is recorded and re-raised as it stands. Both handlers are narrow, so
  `test_broad_exception_handlers_are_reviewed` needs no new entry.
- **Overlaps with branches in flight:**
  - ci-3 and et-5b: `tests/test_relay_binding_inventory.py`, different definitions;
  - cmp-s3-cfr-1c and 1d: `tests/data/relay-gate-cases.jsonl`, plus `tools/relay_mutation_gate.py` next to
    `SERVICE_READERS["english.command"]`.

  Whichever merges second resolves them. cmp-s3-cfr-1c reached main first, so this branch merged main
  (`2902e3fc05`). `tools/relay_mutation_gate.py` conflicted, and the resolution keeps both readers
  (`clauses-elaborate`, `english.statement`). The `.jsonl` rows merged cleanly. `regen_generated.py --check`
  checked 40 entries and found none stale.
- **Pilot bytes moved:** 0 (shadow only).

## Final selected run

The run was `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on the committed review-fix HEAD
`7334403810`, with a clean tree. It ran on GitHub Actions (run `en-e3bb-73344038-t449919`) in 5 shards: 102 units, 102
passed, exit 0. It included `tests/test_w1_delta_suite.py`, `tests/test_english_statement_shadow.py` and
`tests/test_history_tests.py`. `lake build` succeeded (1419 jobs). `python3 lean/audit.py` passed (856 files, 9590
theorems). `regen_generated.py --check` checked 40 entries and found none stale. Both review probes pass. After the
run, only this section of this report changed. Not run: the full gate (the chain runs it).

## Next

en-e3a-cutback, then en-e3 (EN-3) after the DRI's W1 delta decision.

## Self-review against BUILDER-CHECKLIST

1. **Typed and contained:** PASS. `test_every_retyped_dropped_or_duplicated_member_is_unavailable` covers 7, true,
   null, [], {}, 1.5, "\ud800" and 10k-deep at every position; the gate refuses 1533 of 1533.
2. **Deliverables:** PASS. The table above; `git diff main...HEAD` holds no new Python copy of a Lean decision and no
   new report test of git.
3. **Tests can fail:** PASS. `mutants.json`: 10 of 10 caught; `test_the_delta_check_fails_on_an_unlisted_or_misclassed_disagreement`.
4. **Agreement:** PASS. `delta.json`: pinned 120 of 120 agree; the rest are listed for the DRI.
5. **R8 binding:** PASS. `test_every_named_mutant_is_unavailable` (undeclared predicate, shifted number, extra and
   duplicated rows); `test_relay_binding_inventory.py[english.statement]`.
6. **Gate evidence on final HEAD:** N.A. The chain runs the gate. The final selected run is below.
7. **No unsigned item:** PASS. `en-2c/DELTA.md` has no row; the evidence DELTA.md has no Ruling column.
8. **Every user-visible change in DELTA:** PASS. There is none: `test_the_shadow_asks_lean_and_keeps_python_s_answer`.
9. **Selection:** PASS. `tools/select_tests.py --base …` selects 99 test files (not every unit), including the five
   changed tests and `test_english_statement_blocks.py`.
10. **Lean statements:** N.A. No Lean changed.
11. **Budgets:** PASS. `test_the_spans_bound_the_rule_rows_before_any_node_is_read`: a step count, no timing.
12. **CPU:** N.A. The shadow runs only behind two flags; one Lean call per W1 parse.
13. **Test-removed:** N.A. No test removed or renamed.
14. **Both directions:** PASS. The genuine-answer tests (`test_every_genuine_answer_is_accepted`, P2's accepted
    spans, P3); the delta check's broken copies.
15. **Overclaim, cuts, failing checks, limits:** PASS. No deliverable cut. Each check has its seeded bug. Spans are
    charged before node work.
