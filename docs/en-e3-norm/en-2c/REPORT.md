# en-e3bb build report: the W1 shadow relay to `english.statement`, its binding, fuzz tests and the W1 delta report

**Summary.**
- **Status:** built; nothing is reserved for the DRI in this item.
- **What changed:** `parse_english`'s W1 path asks `english.statement` in shadow behind two env flags, and the
  answer is schema-checked and bound (R8). New fuzz tests, gate and inventory rows, and the saved delta report
  (`docs/en-e3-norm/en-2/`).
- **Open:** the DRI's W1 delta decision, which gates en-e3, not this merge. The stop-point message was sent
  (`inbox/dri/20261111T190003Z-en-e3bb-3935271.md`).
- **Trust:** +0.
- **Size:** 213 product, 470 tests, 536 other hand-written lines.

Scope: task-en-e3b.txt deliverables (1)-(4) without what en-e3b built (reviews/dri-decisions-20261110-en-e3b.md
item 1), under reviews/dri-decisions-20261102-en-e3-norm.md items 1-3.
SIZE: 213 product, 470 tests, 536 other hand-written lines: `git diff --numstat $(git merge-base HEAD main)`.
- Product is `ve/norm_english.py` 197 and `tools/relay_mutation_gate.py` 16.
- Tests are the five test files plus 1 fixture line.
- Other is `w1_delta.py` 289, `seed.py` 68, this report and DELTA.md.
- Written by the scripts: `delta.json` 6,893 lines, the evidence DELTA.md 181 and `mutants.json` 83.

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
| (3) The delta report | `docs/en-e3-norm/en-2/DELTA.md` and `delta.json`, written by `w1_delta.py` | `test_the_saved_delta_report_records_every_disagreement_with_its_class` |
| (4) The shadow test reads the saved delta; with the flag set and no `VE_SHADOW_LOG`, Lean is not called and no file is written; en-e3b's 16 tests kept | `tests/test_english_statement_shadow.py` (19 tests) | `test_the_saved_delta_report_*`, `test_the_delta_check_fails_on_an_unlisted_or_misclassed_disagreement`, `test_the_shadow_needs_both_flags` |
| Stop-point message | `msg.sh dri en-e3bb "W1 delta decision for EN-3 …"`: "sent to dri: …/20261111T190003Z-en-e3bb-3935271.md" | — |

The commits are `main..HEAD --no-merges` on feature/en-e3bb.

## The delta report (saved evidence; `delta.json` at `c54938c37`, the final product code)

The command was `uv run python docs/en-e3-norm/en-2/w1_delta.py --workers 8 --scratch /tmp/e3bb-w1-scratch`. Its
suite part was "4693 passed".

| corpus | records | lean-unavailable | agree | lean-stricter | lean-looser | both-refuse |
|---|---|---|---|---|---|---|
| pinned (120 blocks) | 120 | 0 | 120 | 0 | 0 | 0 |
| suite (33 test files) | 73 | 0 | 16 | 15 | 1 | 41 |
| soft-rights (`_w1=True` calls) | 70 | 47 | 19 | 0 | 4 | 0 |
| udhr (norm units and readings, one at a time) | 47 | 1 | 0 | 37 | 0 | 9 |
| constitution (the probe translation's) | 14 | 14 | 0 | 0 | 0 | 0 |
| known (english-lean-s6.md section 5) | 15 | 0 | 3 | 2 | 9 | 1 |

`lean-unknown` and `different-node` are 0 in every corpus. No block is answered `NodeRefused` or `NodeLimit`
(DELTA.md, "Blocks Lean answers …: 0"). The causes, from DELTA.md's "Rows by Lean's answer":
- all 15 suite and 37 UDHR `lean-stricter` rows are `NoDerivation`;
- the 47 soft-rights and 1 UDHR `lean-unavailable` rows are `InvalidGrammar`;
- the 14 constitution rows are the request refusal "UnsupportedProfile: Unsupported profile soft-norms@0";
- the layout rows (blocks sharing a line, a block over two lines, a blank line, a trailing line) are `lean-looser`,
  and so are lowercase `rule`, double spacing, a tab and a self-precedence line.

Two known differences, a predicate with a sort three times and one with no argument, have no text: their
environment is refused by `Environment` itself ("invalid signature"), so they are listed as
`known_not_constructible`.

## Seeded bugs (Python; each planted alone, shown failing, restored)

Each was run by `docs/en-e3-norm/en-2c/seed.py`, and the record is `mutants.json` (file, tests, failed). All are in
`ve/norm_english.py` except bug 8:
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
7. **A rule node's formulas may name an undeclared constant or an unbound variable:**
   `test_every_named_mutant_is_unavailable` and `test_every_retyped_dropped_or_duplicated_member_is_unavailable` fail.
8. **`tools/relay_mutation_gate.py`: the gate without the english.statement reader:**
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
- **Soft environments:** Lean's `english.statement` refuses `soft-norms@0` environments, and so does its grammar for
  the soft frames. So every soft-rights W1 call and every constitution unit is `lean-unavailable` (61 rows).
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

  Whichever merges second resolves them.
- **Pilot bytes moved:** 0 (shadow only).

## Next

en-e3a-cutback, then en-e3 (EN-3) after the DRI's W1 delta decision.

## Self-review against BUILDER-CHECKLIST

1. **Typed and contained:** PASS. `test_every_retyped_dropped_or_duplicated_member_is_unavailable` covers 7, true,
   null, [], {}, 1.5, "\ud800" and 10k-deep at every position; the gate refuses 1533 of 1533.
2. **Deliverables:** PASS. The table above; `git diff main...HEAD` holds no new Python copy of a Lean decision and no
   new report test of git.
3. **Tests can fail:** PASS. `mutants.json`: 8 of 8 caught; `test_the_delta_check_fails_on_an_unlisted_or_misclassed_disagreement`.
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
