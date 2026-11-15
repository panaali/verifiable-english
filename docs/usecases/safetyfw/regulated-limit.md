# Carrying more than 64 regulated predicates: split into frames

Ruling: reviews/dri-decisions-20261115-translim-predicates.md. The answer is NO to raising the limit and
RESTRUCTURE instead. Each environment, or frame, keeps at most 64 regulated predicates
(docs/spec/soft-norms.md 11, docs/spec/readings-defaults.md 9). A keyed document that needs more splits into
frames.

Measurement, numbers and data: docs/translim/translim-predicates/REPORT.md.

## Why not raise the limit

Above 64 the cost is not bounded (REPORT 1b, MEASURED):
- At 96 and 128 the `norms` route overruns its 6 s CPU deadline.
- `norm-defaults` overruns 122 s.
- The soft document is refused by the AST limit (10,000 nodes) at 96 and by the 256-predicate vocabulary at 128.

PF's need can exceed 128 (REPORT 1c, ESTIMATE up to 171), so no single width carries every case.

## The recipe

1. **Link.** Join two regulated predicates when any of these holds:
   - a rule on one names the other in its guard or carve-outs;
   - one is the other's permission dual;
   - their rules stand in a precedence (`over`) pair;
   - their rules are checked in one document (a conflict cluster, an opposite-sign pair).

   The connected components are the units a split moves. RSP's 64 form 60 components: 56 single predicates and
   4 pairs.
2. **Split.** Every frame repeats the unregulated vocabulary (sorts, plain predicates, constants) and holds whole
   components, at most 64 regulated predicates each.
3. **Parse.** Parse each rule in its own frame's environment. A whole vocabulary of more than 64 is refused
   before any rule is read.
4. **Route.**
   - A question about predicate p is asked of p's frame.
   - A conflict pair is asked of the frame that holds both rules.
   - A probe that builds its own document builds it in one frame, with that frame's rules.
5. **Account for units.** A `ve-document@1` holds one environment. The units of a second frame go to a further
   document beside D1, as RSP's D2 and D3 and PF's d2 already are.

`closed_split` in docs/translim/translim-predicates/rsp_split.py refuses a split that breaks step 1. A frame that
misses a rule's guard predicate is refused by the route itself (`UnknownSymbol: Unknown predicate ...`), never
answered.

## Measured on RSP (scratch copy; data/rsp_split_runs.txt)

| split | `run.py --check` | answers |
|---|---|---|
| none | pass | 110 / 126 |
| 3 predicates to a second frame | pass, results.json byte-identical | 110 / 126 |
| 32 + 32 | pass, results.json byte-identical | 110 / 126 |
| `assessed_in_report` moved without `in_scope` (its rule's guard) | fail: `UnknownSymbol: Unknown predicate 'in_scope'` | n/a |

- **Cost.** No measurable time; the run took 5.6 to 6.2 min against 6.2 min unsplit.
- **What the split adds.** One environment per frame and the routing step 4 in the case's harness.

## Tests

`tests/test_regulated_limit.py`:
- **The limit.** Every limit site accepts 64 and refuses 65.
- **The recipe's links and refusals:** `test_split_recipe_*`.
- **End to end on a soft document:**
  - `test_a_split_into_component_frames_selects_the_same_rules`: each predicate's selected rules in its frame
    equal those of the unsplit document, over three models.
  - `test_a_frame_without_a_rules_guard_predicate_is_refused`.

## Adoption

Each case adopts the split in its next fix round. One backlog row per case: anthropic-rsp (needs 68) and
openai-preparedness (needs 62 to 171). FSF (27) needs none. Blind R2 (78) has no case directory; its R3 already
runs as a dependency-complete partition.
