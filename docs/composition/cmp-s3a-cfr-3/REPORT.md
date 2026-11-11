# cmp-s3a-cfr-3: `elided_bytes` by product code

This item follows up regrade #10 of the rights family (reviews/l1-c-regrade-rights-20261109.md, grade B). Here "the
plan" is docs/spec/right-clauses.md on main: :207 (4.1 step 5, "compute `Rel_D` and `elided_bytes`"), K4 (:573,
`elided_bytes = 10`) and the report rule (:602: every unit under the profile reports `elided_bytes`; 6 :271 defines it
as the sum of `b - a` over the unit's lines' elided spans, with 0 printed, plus the document total). The prerequisite
cmp-s3-cfr-1 (the `clauses-elaborate` route) is on main; its REPORT left `elided_bytes` to this item.

The defect: Examples.lean:91 summed the fixture's literal `[(30, 40)]`, and no product code computed `elided_bytes`.

## Plan rows delivered

| Row | Delivered | Where |
|---|---|---|
| (1) `elided_bytes` computed by product Lean code from the elided spans of the decoded document, emitted by the route, per unit as :602 says | yes. `lineElided` (one line's sum), `entryElided` (each decoded line's key and bytes, every span read once), `elidedTotal` (the document total) and `unitElided` (one count per unit of the request's document, in order, 0 printed). The route answers `elided_bytes` (the total) and `unit_elided_bytes` | lean/VE/RightClauses/ElidedBytes.lean; lean/VE/RightClauses/Run.lean (it calls the module); schema lean/ResponseShape/Schemas/ClausesElaborate.lean, encoder theorem `runCaseReported_fits` unchanged and re-proved |
| (2) Examples.lean's K4 calls that code, with no literal | yes. `#guard elidedTotal (entryElided (cdoc k4)) == 10`, plus three spans (51) and none (0) | lean/VE/RightClauses/Examples.lean:92-95 |
| (3) `test_right_clauses_k4_product_elided_bytes`: K4 through the product route reports 10, and fails on main | yes. On main the answer has no `elided_bytes` field: the saved base answer of K4 (base-answers.json, `answers.K4.result`) has only `plained` and `clause_slot`, so the test fails on its first field read | tests/test_right_clauses.py |
| (4) The evaluator rule (reviews/dri-decisions-20261027-me-12-n1.md): spans read once, with a stated limit | yes; see "Cost and limit" | ElidedBytes.lean module doc; `test_right_clauses_elided_bytes_large_request` |

RunExamples.lean adds route-level `#guard`s: K4 gives `10` and `[10]`; no span gives `0` and `[0]`; two units give 36
and `[10, 26]`, and `[2, 0]` for a unit without spans; and `unitElided` on a unit without a line body, and on a line
with no entry. `test_right_clauses_power_line_elided_bytes` covers a power line. Spec 1.1 allows `elided` on one, and
its key is its liberty's name (`jsonLineName`). Eliding `[105, 112)` makes its unit report 7, beside the claim unit's
10 (17 in total). Without the elision, the power unit reports 0.

Where this differs from the task's Files line: the route's output is built in Run.lean (cmp-s3-cfr-1 put it there),
not in Wire.lean. So Run.lean calls ElidedBytes.lean, and Wire.lean is unchanged.

## Readings made here

- **Per unit.** The decoded document's lines (`ClauseDoc.lines`) do not record their unit. `unitElided` walks the
  request's units and finds each named line object's entry by (right, rule name). This is the key `plainLineJson`
  already uses to plain a line. It reads the bytes from `entryElided`, never a span from JSON. Rights refuses a
  repeated rule name (`DuplicateDeclaration: rule <n>`) before the answer, so each entry belongs to exactly one line
  object. A unit with no line body (a limitation, for example) or no named line reports 0.
- **Overlap.** Spec 1.1 (:55) makes the spans of one line pairwise disjoint, and `checkSpans` refuses an overlap
  (`ClauseSpan`, K6) before `elided_bytes` is computed. So the overlap fixture is a refusal fixture: two overlapping
  elisions of one line are answered `ClauseSpan: equal-access: [35, 45)`. Spans of different lines of one unit are
  not constrained. Spec 6 sums "over its lines' elided spans", and so does `unitElided`: two lines of one unit that
  each elide `[30, 40)` report 20 for the unit, with no union across lines. The DRI signed this reading
  (reviews/dri-decisions-20261110-cmp-s3a-cfr-3.md item 1). Its condition tests are the route test's cross-line case
  in `test_right_clauses_k4_product_elided_bytes`, the `#guard elided sameUnit` in RunExamples.lean, the within-line
  `ClauseSpan` refusal fixture, and seeded bug S5 below.
- **Candidates.** This route refuses `readings@1`, so reading candidates are not counted. When cmp-s3-cfr-1c admits
  them, `entryElided` must read the candidates' lines too.

## Cost and limit (the evaluator rule)

`entryElided` reads each decoded elided span once, when Run.lean binds `es`. `elidedTotal` and `unitElided` read only
those numbers. `unitElided` does (named line objects) × (entries) key comparisons. That is the bound `plainLineJson`
already has, and the rights limits cap both counts (256 rules, the generated norm layer's size). This item's work is
linear in the decoded spans. Spans per line are bounded only by the 16 MiB request. The head's `checkSpans` on main
(Plain.lean, since cmp-s3-cfr-1) is quadratic in one line's spans: measured at about 13 s for about 40k spans in one
line (one run, on this branch's base). It stays so until cmp-s3-cfr-1b merges, which makes it O(s log s) and owns that
fixture (test_right_clauses_w1_budget, 30,000 spans in one line). As of this HEAD, cfr-1b has not merged. This item
adds no span-count limit and does not touch `checkSpans` (reviews/dri-decisions-20261110-cmp-s3a-cfr-3.md item 2,
DRI 2026-11-10 23:42Z). Spec 10 adds no new limit, and neither does this item: the stated limit is the request size, together with `decodeClauseDoc`'s 1,024 units and
rights' rule and layer limits. Fixture: `test_right_clauses_elided_bytes_large_request` uses 32 units (right r21 and 31
`right_lines` units of it), each with one line eliding 500 one-byte spans, which is 16,000 spans. It answers 16,000,
with 500 for each unit, in 0.13 s locally, within `HANG_TIMEOUT`. With more lines on one predicate, rights refuses
`ResourceLimit: generated norm layer`. A probe before this fixture hit that refusal at 200 lines, and `ResourceLimit:
rights` at 1,024 rights. The fixture also grows the same request to 200 lines, past that limit, and checks that it is
answered `ResourceLimit: ...`, not with a count.

## Seeded bugs

Each bug was planted, built, pinned (`checker-pins`) and run against the named tests, then restored, and the lock was
reset. All of them are in Lean. mutants.json lists them with one mutant per new trusted definition (S1 `lineElided`, S5
`entryElided`, M6 `elidedTotal`, S3 `unitElided`); M6 was checked against the `#guard`s only. The item changes no Python or Rust product code: its Python changes are tests and
the manifest's classification.

| # | File | Bug | Fails |
|---|---|---|---|
| S1 | lean/VE/RightClauses/ElidedBytes.lean (`lineElided`) | off by one: `n + (s.2 - s.1 + 1)` | Lean `#guard`s Examples.lean:93-94 (K4 gives 11) and RunExamples.lean:121, 123, 124; `test_right_clauses_k4_product_elided_bytes` (`elided_bytes` 11, not 10); `test_right_clauses_existing_answers_unchanged` (K4's added field) |
| S2 | lean/VE/RightClauses/Plain.lean (`checkSpans`) | the disjointness test is dropped, so overlapping elided spans are counted twice | Examples.lean:121-123 and 127 (K6 `#guard`s); `test_right_clauses_k4_product_elided_bytes`: `[[30, 40], [35, 45]]` is answered `elided_bytes` 20 instead of refused |
| S3 | lean/VE/RightClauses/ElidedBytes.lean (`unitElided`) | each line adds the document total, not its own entry | RunExamples.lean:124-125 (two units; the last lines of the build log); `test_right_clauses_k4_product_elided_bytes` (two units: 36 for each) |
| S4 | lean/VE/RightClauses/Run.lean (`elaborateCase`) | `plained` carries the request document's bytes, which changes an existing field | `test_right_clauses_existing_answers_unchanged`, the DELTA row's negative test |
| S5 | lean/VE/RightClauses/ElidedBytes.lean (`entryElided`) | removes duplicates across lines: a line whose spans equal an earlier line's of the same right counts 0 | RunExamples.lean:132 (`#guard elided sameUnit`, the only `#guard` that fails); `test_right_clauses_k4_product_elided_bytes` (the cross-line case gives 10 and `[10]`, not 20 and `[20]`) |
| M6 | lean/VE/RightClauses/ElidedBytes.lean (`elidedTotal`) | `max n e.2` instead of `n + e.2`: the total is the largest line's count | RunExamples.lean:123 and 132 |

A sixth check, outside Lean: in `ve/backends/lean_service_schema/clauses-elaborate.json` (generated; the seed is
planted by hand and restored), `unit_elided_bytes`'s `x-length` is renamed, so the row count is no longer bound.
`test_right_clauses_elided_bytes_retyped_and_rebound` fails (`1 failed`). That test takes a genuine K4 answer, then
retypes both fields (-1, 1.5, "10", true, null, [], {}), retypes one row, removes a row, adds an extra row or a
duplicate, or deletes a field, and `check_response` must refuse every mutant.

Trust mutants (build checklist 13a; the light lane printed NOT): the last full run is on 38dbc5503 (`zsh mac-pytest.sh
--trustmut -- --max-mutants 1000 --json docs/composition/cmp-s3a-cfr-3/trust-mutants.json`). It gave 56 KILLED,
1 SURVIVOR, 10 INVALID. The survivor was `| none => 0` → `1` in `unitElided`, the branch for a line object with no
name. `#guard` RunExamples.lean:136 (an unnamed line beside a named one gives `[7]`) now kills it: planted by hand, the
build fails at :136. The rescore on that check-only change (`--rescore` the same JSON) gives 57 KILLED, 0 SURVIVOR,
0 UNKNOWN, 10 INVALID, exit 0 (docs/composition/cmp-s3a-cfr-3/trust-mutants.json). An earlier run on e16063ed6 had 3
survivors: they were equivalent mutants of a redundant `dropKeys ["span"]` (`unitBody` reads only `right` and
`right_lines`), and that call is removed. It also had 5 UNKNOWN: `[]` mutants that did not elaborate, because the fold
lambdas had no type ascription and the tool reads an `Option.map` as a list method. The lambdas now carry their types,
and the lookup is a `match`.

## Trust

Measured with `uv run python tools/trust_map.py --check` on this HEAD, against base 0295df174375: K +0, S +12, D +14,
G +5, tied +0, unclassified +0, trusted +29. By file: lean/VE/RightClauses/ElidedBytes.lean trusted +26 (S +12:
`lineElided`, `entryElided`, `elidedTotal`; D[V] +14: `unitElided`), lean/VE/RightClauses/Run.lean trusted +3. The
command prints `PASS: K, S and untied [V] within 0295df174375 and the allowances introduced since`. The total, 29, is
within R16's 150, with no K growth. The allowance is recorded in docs/trust-baseline.json, in two entries: S +11 V +14,
then S +1 V +3 after the typed `unitElided`. Each says "SIGNED by standing ruling R16 (DRI-RULINGS.md), cmp-s3a-cfr-3".
There is one mutant per new trusted definition (mutants.json), and the trust_mutants sweep above exits 0. The
FOLLOW-UPS.md row is under "## cmp-s3a-cfr-3".

SIZE: 69 product, 162 tests (pytest and Lean `#guard`s), 153 other hand-written lines (`git diff --numstat` against
0295df174375; REPORT, DELTA, the base-answer probe and mutants.json; generated files excluded).

## Pilot bytes

No verdict moves. Each `ok` answer of the mode gains two fields. When cmp-s3-cfr-1b's relay sends UDHR units, each
unit under the profile will report its `elided_bytes`, and the seven audited units (u035, u039, u041, u046, u054,
u077, u033b) will report their counts. Nothing is claimed before a pilot audit.

## Next item

None. The relay that binds these fields in Python, and the Python differential, are cmp-s3-cfr-1b's, which already
exists.

## Notes for the DRI

- Spec re-read: `elided_bytes` (4.1 step 5) against docs/spec/right-clauses.md:207; the per-unit sum of `b - a` over
  its lines' elided spans, with 0 printed, and their document total, against :271-272; K4's `elided_bytes = 10`
  against :573; "every unit under the profile reports `elided_bytes`" against :602; one line's spans pairwise
  disjoint (so the overlap fixture is a refusal) against :55.
- `unit_elided_bytes` has one entry per unit of the request's `document`, and a unit with no rights line body reports
  0. That is the narrower binding (`x-length: "/document"`), not a list of only the units that have lines.
- Main known-red: none of the tests this item touches is listed in main-known-red.txt.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `test_right_clauses_elided_bytes_retyped_and_rebound` (both fields retyped, or deleted
   from a genuine answer) and `test_random_malformed_responses_never_escape_schema` (the clauses-elaborate seed carries
   both fields).
2. Deliverables: PASS. The plan rows table above: (1) to (4), each with its test.
   `test_right_clauses_k4_product_elided_bytes` fails on main (saved base answer, base-answers.json).
3. Tests can fail: PASS. Seeded bugs S1 to S5 and M6, the schema seed, and trust-mutants.json (57 killed, 0
   survivor, exit 0).
4. Agreement, valid inputs still pass: PASS. `test_right_clauses_existing_answers_unchanged` compares 23 saved base
   answers. There is no Python or Rust copy of the count.
5. R8 binding: PASS. `test_right_clauses_elided_bytes_retyped_and_rebound` (a row missing, extra or duplicated, and
   an empty list, are refused). `x-length: "/document"` is in the generated schema.
6. Gate evidence on the final HEAD: PASS. main is merged (this branch's latest merge commit). The chain runs the gate
   on the final HEAD, and the final selected run is on committed code.
7. No unsigned item: PASS. The DELTA row cites R3. The trust growth is under R16 (docs/trust-baseline.json). No
   signature is reserved.
8. Every user-visible change is in DELTA: PASS. One row. `test_right_clauses_existing_answers_unchanged` shows that
   nothing else changes.
9. Test selection: PASS. `tools/select_tests.py --base <merge-base>` selects tests/test_right_clauses.py.
10. Lean statements: PASS. The encoder theorem `runCaseReported_fits` is re-proved over the schema with both fields,
    and `python3 lean/audit.py` prints PASS (846 files). No theorem statement is added or changed.
11. Budgets fail closed: PASS. `test_right_clauses_elided_bytes_large_request` checks that a request grown past the
    rights limit is answered `ResourceLimit`. The mode has no budget parameter of its own.
12. CPU and memory: PASS. The work is linear in the decoded spans (`test_right_clauses_elided_bytes_large_request`,
    16,000 spans). The route is on no pilot path yet, so no pilot timing applies.
13. Test-removed trailers: N.A. No test is removed. `tools/gate_collection.py --check --prebuilt`: 5 added,
    0 refused, 0 stale, 0 malformed.
14. Both directions, cited evidence: PASS. The overlap is refused within one line and summed across lines
    (`test_right_clauses_k4_product_elided_bytes`). A power line reports 7 with its elision and 0 without
    (`test_right_clauses_power_line_elided_bytes`).
15. Overclaim, silent cut, guards that can fail, limits charged: PASS. Nothing is cut (Next item: none). Every new
    `#guard` has a mutant that fails it (Seeded bugs, trust-mutants.json). The limit fixture is
    `test_right_clauses_elided_bytes_large_request`. The quadratic `checkSpans` is cfr-1b's, per DRI 2026-11-10
    item 2.
