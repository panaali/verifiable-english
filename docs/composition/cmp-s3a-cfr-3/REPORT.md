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
with no entry.

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
  not constrained. Spec 6 sums "over its lines' elided spans", and so does `unitElided`.
- **Candidates.** This route refuses `readings@1`, so reading candidates are not counted. When cmp-s3-cfr-1c admits
  them, `entryElided` must read the candidates' lines too.

## Cost and limit (the evaluator rule)

`entryElided` reads each decoded elided span once, when Run.lean binds `es`. `elidedTotal` and `unitElided` read only
those numbers. `unitElided` does (named line objects) × (entries) key comparisons. That is the bound `plainLineJson`
already has, and the rights limits cap both counts (256 rules, the generated norm layer's size). Spans per line are
bounded only by the request size, and the head's `checkSpans` is already quadratic in them. Spec 10 adds no new limit,
and neither does this item: the stated limit is the request size, together with `decodeClauseDoc`'s 1,024 units and
rights' rule and layer limits. Fixture: `test_right_clauses_elided_bytes_large_request` uses 32 units (right r21 and 31
`right_lines` units of it), each with one line eliding 500 one-byte spans, which is 16,000 spans. It answers 16,000,
with 500 for each unit, in 0.13 s locally, within `HANG_TIMEOUT`. With more lines on one predicate, rights refuses
`ResourceLimit: generated norm layer`. A probe before this fixture hit that refusal at 200 lines, and `ResourceLimit:
rights` at 1,024 rights.

## Seeded bugs

Each bug was planted, built, pinned (`checker-pins`) and run against the named tests, then restored, and the lock was
reset. All of them are in Lean. The item changes no Python or Rust product code: its Python changes are tests and
the manifest's classification.

| # | File | Bug | Fails |
|---|---|---|---|
| S1 | lean/VE/RightClauses/ElidedBytes.lean (`lineElided`) | off by one: `n + (s.2 - s.1 + 1)` | Lean `#guard`s Examples.lean:93-94 (K4 gives 11) and RunExamples.lean:121, 123, 124; `test_right_clauses_k4_product_elided_bytes` (`elided_bytes` 11, not 10); `test_right_clauses_existing_answers_unchanged` (K4's added field) |
| S2 | lean/VE/RightClauses/Plain.lean (`checkSpans`) | the disjointness test is dropped, so overlapping elided spans are counted twice | Examples.lean:121-123 and 127 (K6 `#guard`s); `test_right_clauses_k4_product_elided_bytes`: `[[30, 40], [35, 45]]` is answered `elided_bytes` 20 instead of refused |
| S3 | lean/VE/RightClauses/ElidedBytes.lean (`unitElided`) | each line adds the document total, not its own entry | RunExamples.lean:124-125 (two units; the last lines of the build log); `test_right_clauses_k4_product_elided_bytes` (two units: 36 for each) |
| S4 | lean/VE/RightClauses/Run.lean (`elaborateCase`) | `plained` carries the request document's bytes, which changes an existing field | `test_right_clauses_existing_answers_unchanged`, the DELTA row's negative test |

## Trust

TBD (measured on the final HEAD).

## Pilot bytes

No verdict moves. Each `ok` answer of the mode gains two fields. When cmp-s3-cfr-1b's relay sends UDHR units, each
unit under the profile will report its `elided_bytes`, and the seven audited units (u035, u039, u041, u046, u054,
u077, u033b) will report their counts. Nothing is claimed before a pilot audit.

## Next item

None. The relay that binds these fields in Python, and the Python differential, are cmp-s3-cfr-1b's, which already
exists.
