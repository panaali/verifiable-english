# Feature review: what `ve-green-arch-AR-8` adds over `ve-green-arch-AR-6`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261010T1800Z` (`prev/`), whose audit found all 31 sampled and changed units faithful. Two first-parent merges since `ve-green-arch-AR-6`.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `readings-defaults/rd6b` (RD-6b) | the superposed route under the unspecified completion: a document whose reading sets carry `norm-defaults@0` content is checked as one superposed document (conflict, certificate, model) instead of one choice at a time | No (repackages the check; the meaning of every reading is the same) |
| `infra/arch-AR-8` | Rust crate-boundary check, facade `lib.rs` rules, gate collection | No |

Result: **no unit changes status because of a feature, and no unit is newly expressible.** I changed no unit, so `changed_units` is empty. Claimed coverage does not move (2,951 bytes, 1.60%).

## What the measurement shows
* **Same verdicts, new route.** `ve document check` of the unchanged translation: premises `model`, 16 choices, conflict-free, field for field the previous run's except the route. At `ve-green-arch-AR-6` VE said “ReadingsNotSuperposable … the unspecified completion” and checked the 16 choices one at a time; now it checks all 16 together (route `superposed`, 199 nodes, 69 predicates, within the limits 10,000 / 256 / 32) and lists each choice's status (16 × CONFLICT-FREE). Its English drops “checked one way at a time” and adds “This does not depend on how sentence N is read.” for each of the four sets. The premises answer is now one model for one choice with the gaps listed (`premises.gaps`, empty), not a status per choice.
* **Reproduced.** `nd.py all` rebuilt the translation from `translation-without-content.ve.md`: byte-identical to `translation.ve.md`. Same two outcome and two selects separations, found by Lean. `ve document check`: 35 s here (55 s at AR-6; one run each, not a controlled comparison; RD-6b's own evidence says three documents of this pilot got more than 20% slower in its 29-record re-recording).
* **Conclusion queries.** Same four verdicts: denial across readings UNKNOWN, under the strict reading ALL, under the defeasible reading UNKNOWN, claim-to-be-human ALL. All four now run on the `superposed` route (before, `enumerated`), including the two `--under` queries; the ALL answers gain “This does not depend on how sentence N is read.” lines. Regression: the two UNKNOWN answers no longer carry an English line (“Read sentence 132 as … VE could not check whether the conclusion follows”); `docs/spec/readings-defaults.md` records that the superposed route emits no English plan for a gated UNKNOWN (follow-up work).
* **Probes.** The seven carried probes re-run; all seven byte-identical. The companion probe (four sets as companion sets, without `source_word`) gives the same result: 19 decided units, 2,602 bytes, 1.41%; the four companion queries are byte-identical. The `source_word` defect is still there (`CheckerUnavailable: ReadingsConstruction … KeyError`). The translation itself still has 0.00% Lean-decided units (no `decided_units` on the plain or superposed route).
* **Question reader (Q1).** `ve ask --reading` on five questions (text saved in `probes/ask/q*.question.txt`): none read (“Unknown English phrase 'must not'”, “'must seek clarification in each situation'”, …). Unchanged.

## Costs and limits (unchanged unless said)
* A defeasible rule beside norm-defaults@0 is still refused (probe c, byte-identical): defeasible candidates are the strict rule with an `unless` over an open term the translator names (four `exception_to_*` terms).
* The budget of 64 choices stopped no unit: none of the 1,074 UNFORMALISED units names it. The superposed route's limit is 1,024 choices, so more reading sets would be possible, but the words give no more “should” sets than the four, so none was added.
* Open terms 33, reading sets 4 (16 choices), unchanged.

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged).
Next, in order of unlock: typed modals and authority (“cannot”, “can”, “may”, “unlocked by”); graded quantities (“serious uplift”, “vast majority”); context-sensitive defeasible obligations beside norm-defaults@0; decided units reported for documents without companion sets (and the `source_word` fix); English for a gated UNKNOWN on the superposed route.
