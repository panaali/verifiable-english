# Batch AR-7 report: one architecture map, a stale-document sweep, the binding ADR

Plan: `docs/ARCHITECTURE-REVIEW-2026-10.md` on branch `design/arch-review`, section 4.3, AR-7; DRI decisions in
`manage-agents/arch-dri-decisions.md`. Branch `infra/arch-AR-7` from `main` at `c24aeab2`.

## Delivered

- `docs/ARCHITECTURE.md`: the map, from section 1 of the review. Its sizes, counts and trust tables are rendered
  from `docs/architecture/numbers.json`, which `tools/architecture_numbers.py --write` measures from a commit's
  tree (git blobs, Python's `ast`, `tomllib`, the JSON inventories; no regular expression over source). Section 6
  is the stale-document sweep, section 7 the re-measuring commands.
- `docs/adr/0001-response-binding.md`: the binding definition of T1(a), recorded as signed by the DRI (D1,
  2026-10-10; R8, R11). It quotes D1 as signed and states T1(a) and T1(b): the "only by" rule (a field that
  names a request item is bound only by `references` or `equals`; a format check is not a binding), the four
  leaf classes including `derived (guarantee)`, the preference for an encoder theorem over a test-time
  `ResponseDecode` invariant, and the census's limit (classified, not correctly classified). The relation table
  names the schema dialect's keywords for each relation (review fix B1).
- Corrections, each marked "Superseded" with a link to the map: `docs/architecture-and-design.md` (status),
  `docs/implementation.md` (header), `docs/INTEGRATION-GAPS.md` (four paragraphs), `docs/spec/lean-service.md`
  (status; the threat model now points to the ADR), `docs/CONSOLIDATION-PLAN.md` (the decoder total, after rd4b
  merged).
- `tests/test_architecture_docs.py` (32 tests): the map against the saved numbers only (never a live measurement,
  so it holds after syncs and the merge), every saved number shown, the tool on a fixture tree and failing closed,
  each of the 11 sweep rows (every row quotes each passage it covers), links, and the ADR: D1's clauses, each
  relation's keywords and each leaf class's shapes held in the test, the Decision section pinned by hash, and
  Lean's `Shape` constructors, the dialect README's keywords and the ADR's tables checked to name one set.

## Outcome

The map's section 6 holds the review's 11 stale statements: 5 corrected in their files (rows 1, 2, 7, 8, 10; row 7
covers four paragraphs and quotes each), 5 waiting for a named reason (rows 3–6: `ARCHITECTURE-LAYERS.md` is edited
by `infra/ts-B1` and `lean-first/b16d`; row 9: `docs/trust-baseline.json` is edited by `lean-first/b13b`,
`lean-first/b16d`, `question-answering/q2` and `readings-defaults/rd6b`, and AR-4 drops `section11`), and 1 recorded
in the map (row 11: the lean-first plan is not on `main`). Every checked row quotes the passages it covers, and the
test checks that each quote of a waiting row is still in its file (for row 9, a key of `section11`), so the row must
be flipped when its file is fixed.

## Not done, and why

- `docs/ARCHITECTURE-LAYERS.md` does not yet point to the map, and rows 3–6 are not applied: the start-of-batch
  overlap check (plan 4.2) found `readings-defaults/rd4b` editing it, and after rd4b merged (`cc534bfc`)
  `infra/ts-B1` and `lean-first/b16d` edit it; the task says to avoid an overlapping file. Follow-up for the first
  batch after those merge: apply rows 3–6 from the map's "Today" column, add the pointer at the top of
  `ARCHITECTURE-LAYERS.md`, and set the rows to "corrected". Row 10 was applied in the review fixes, since no
  running branch edits `CONSOLIDATION-PLAN.md` any more.
- Row 9 waits for AR-4.

## Start-of-batch overlap check

Files touched: `docs/ARCHITECTURE.md`, `docs/adr/0001-response-binding.md`, `docs/architecture/*`,
`docs/architecture-and-design.md`, `docs/implementation.md`, `docs/INTEGRATION-GAPS.md`,
`docs/spec/lean-service.md`, `tools/architecture_numbers.py`, `tests/test_architecture_docs.py`,
`tools/gate-collection.json`. Against `git diff --name-only main...<branch>` for every branch matching
`lean-first/*`, `readings-defaults/*`, `question-answering/*` and `infra/*`: no overlap except the shared inventory
`tools/gate-collection.json`. Avoided because they overlap: `docs/ARCHITECTURE-LAYERS.md` and
`docs/CONSOLIDATION-PLAN.md` (rd4b), `docs/trust-baseline.json` (b13b, b16d, question-answering/integrate).

**Collision rules for the merge train.**
- Conflict in `tools/gate-collection.json` (a generated inventory, never an overlap and never hand-edited; R12):
  resolve it with `uv run python tools/regen_generated.py --resolve` after the merge (or `--write`), which runs
  `tools/gate_collection.py --write`.
- Conflict in `docs/architecture/numbers.json` or a numbers table of `docs/ARCHITECTURE.md`: take either side and
  run `python3 tools/architecture_numbers.py --write` on the merged commit.

## Behaviour and deltas

No change to `ve/`, `lean/` or Rust; no user-visible delta, so no standing ruling (DRI-RULINGS R1–R10) applies and
there is no `DELTA.md`. The ADR records D1, which the DRI signed on 2026-10-10 (R11). The plan's 4.1 items 2 and 3
(A/B corpora, Lean statements and trust map) do not apply to a docs-only batch; `lake build` was run only to
regenerate the gate collection.

## Seeded bugs (each planted, shown failing, then removed)

| # | Bug planted | Behaviour claimed | Failing tests |
|---|---|---|---|
| M1 | `render` shows only the two largest `ve/` files | every saved number is in the map | `test_map_tables_are_rendered_from_the_saved_numbers`, `test_every_saved_number_is_shown` |
| M2 | `**/` in a glob never matches zero directories | the tool's globs | `test_glob[ve/a.py-…]`, `test_measure_on_a_small_tree`, `test_measure_fails_closed` |
| M3 | a glob with no committed file counts as 0 lines | the tool fails closed | `test_measure_fails_closed` |
| M4 | "Nothing in `ve` calls the service yet" restored in `lean-service.md` | the sweep holds | `test_stale_statement[8]` |
| M5 | the ADR drops `x-zip-or-empty` | the ADR lists every binding keyword of the dialect | `test_adr_relation_keywords`, `test_adr_decision_is_pinned` |
| M6 | the ADR drops "Python never recomputes it to check it" | the ADR records D1 as signed | `test_adr_records_d1_as_signed`, `test_adr_decision_is_pinned` |
| M7 | the ADR adds "A format check counts as binding." | the same | `test_adr_decision_is_pinned` |
| M8 | `x-references` moved into relation 1 | each relation's keywords | `test_adr_relation_keywords`, `test_adr_decision_is_pinned` |
| M9 | `pattern` added to the closed-domain shapes | the four leaf classes | `test_adr_leaf_classes`, `test_adr_decision_is_pinned` |
| M10 | the alternatives or quantity note of `INTEGRATION-GAPS.md` loses its "Superseded" marker | row 7 covers four passages | `test_stale_statement[7]` |
| M11 | `NormsMain` removed from `ARCHITECTURE-LAYERS.md` | a waiting row's quote is still in its file | `test_stale_statement[4]` |

## Tests run

Selected tests (`tools/select_tests.py --base c24aeab2 --run`): the new module and the selected set; the only
failures were `test_gate_collection.py` and `test_gate.py::test_the_collection_baseline_is_what_the_gate_collects`,
for the 28 new IDs, which pass after `gate_collection.py --write` (28 IDs added, none removed). The full gate's
result on the final head is in the hand-off report; it is not restated here, because it runs on the commit that
holds this file.
