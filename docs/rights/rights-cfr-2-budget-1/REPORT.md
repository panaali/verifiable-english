# rights-cfr-2-budget-1: REPORT

**Status:** delivered on branch feature/rights-cfr-2-budget-1, with fix (A) under R1 and the count named under R3.
No DRI signature is reserved, because no printed count changes (step 1). Both rows are covered by standing rulings
(DELTA.md).
**What changed:** a `rights-conflict` CONFLICT-FREE answer with no situation supplied no longer says a search hit its
budget. Its line also names what its weighing-point count counts. Every JSON field and every count stays as it was.
**Open:** the full gate, which the chain runs on the final HEAD.

## Step 1: measured before any edit (main f3f40d51dc)

The fixture is `WEIGHED` (tests/test_rights_report_parts.py): an unranked default pair on `arrest_permitted` and
limitation 29 with a sufficient condition. The certificate packages are as in `_weighed()`, with no `situation`.
The probe also ran the same default pair (no-arbitrary-arrest, may-detain) once as a rights document and once as a
soft-norms document, through both routes.

(a) The status line the rights route printed for `WEIGHED`:

```text
CONFLICT-FREE among rules on the same act, conditional on 1 coherence premises and 2 limitation premises (soft:coherence:may-detain,no-arbitrary-arrest, rights:limitation:l29:arrest_permitted:necessary:determined_by_law, rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity); 1 weighing points open; situation exhibited: UNKNOWN (budget 10000)
```

(b) The "weighing points open" counts:

| Fixture | rights route `<j>` | soft route `<j>` |
|---|---|---|
| `WEIGHED` (rights only: it has a limitation) | 1 | n/a |
| the default pair alone, as a rights document and as a soft document | 1 | 1 (`coherent situation exhibited: UNKNOWN (budget 10000)`) |
| RightsChecks.lean `weighed` with only the limitation premises used (`conflict true false (·.startsWith "rights:")`) | 2 (with 0 coherence premises) | the soft definition would give 0 here |

The two definitions:
- **Rights route:** `<j>` = `weighing.length`, where `weighing := VE.SoftNorms.Wire.openCoherence (correlate D)`
  (lean/VE/Rights/Run.lean:432 on the base). `openCoherence` is at lean/VE/SoftNorms/Wire.lean:169-170: the
  colliding default pairs that are not `Comparable`, i.e. that no ranking resolves. That is WP(T)
  (docs/spec/soft-norms.md:577) with no pair classified. The rights-conflict case takes no pair evidence, so no pair
  can be discharged as DISJOINT.
- **Soft route:** `<j>` = `conditional.length` (lean/VE/SoftNorms/Run.lean:362). The same number is printed as `<k>`.
  `conditional := sufficientCoherence openLabels (conflictValidWithout res)` (:352), where `openLabels` holds the
  pairs that pair classification leaves open (`openAfterClassification`, :115-120). `sufficientCoherence` (:142-145)
  keeps only the open labels the certificates need. So the soft route counts the open weighing points its verdict
  rests on.

**Reading.** The two routes count different things by design. The rights count is the spec's WP(T) for a request that
carries no pair evidence. The soft count is the subset of WP(T) that its certificates use, after the request's pair
evidence. The counts differ when the soft request's pair evidence discharges a pair, or when no certificate uses an
open pair. Neither count is wrong for its route, so the task's branch "the rights text names what it counts" (R3)
applies. The count expression on both routes is unchanged, so no printed count moves on any fixture or test, and
nothing stops for the DRI.

## Delivered

| Deliverable | Where | Test |
|---|---|---|
| (1) Situation text, fix (A): with no situation supplied the line ends `situation exhibited: none supplied (not searched; budget 10000 unused)`. A supplied one still says `yes`. The JSON fields are unchanged. | `Run.lean` `exhibitedText`, used by `conflictAnswerOf`; the relay binding `ve/rights_route.py` `_bind_conflict` | `test_rights_conflict_free_without_a_situation_names_no_search` (condition test; on main it fails, because main's line contains `UNKNOWN (budget`), RightsChecks.lean :61-:62 |
| (2) Count named (R3): `<j> weighing points open (colliding default pairs no ranking resolves)` | `Run.lean` `weighingGloss`; the relay binding | `test_rights_weighing_points_name_what_they_count` (condition test: count 1 and wording pinned on step 1's fixture), RightsChecks.lean :58 (0 coherence premises, 2 weighing points), :66 |
| (3) The R1 delta test over saved evidence | docs/rights/rights-cfr-2-budget-1/delta.json (base and head lines, both forms) | `test_rights_no_search_delta_keeps_every_quoted_value` |
| (3) Binding fuzz for the new words | the relay refuses the old line restored, the gloss dropped and the budget shifted | `test_a_mutated_no_search_line_is_refused` (3 cases) |
| (4) Correction of rights-cfr-2's REPORT | docs/rights/rights-cfr-2/REPORT.md, its "Readings of 7.3" bullets on `<j>` and on the budget, citing this item | n/a |

Fix (A) meets R1, so (B) (running a bounded situation search) was not needed. (A) keeps the quoted value `budget 10000`
and the path `status_text`, and it is more specific: it says no situation was supplied or searched. The existing
spec-template test (`test_rights_conflict_free_report_evidence`, the condition of rights-cfr-2's DRI-signed row 1)
still reads the 7.3 template from docs/spec/rights.md. It fills the template with the two words this item adds (named
`GLOSS` and `NOT_SEARCHED` in the test) and compares Lean's raw `ve_service` line and the relayed line byte for byte.

## Seeded bugs (docs/rights/rights-cfr-2-budget-1/mutants.json)

| id | language | file | mutation | caught by |
|---|---|---|---|---|
| S1 | Lean | lean/VE/Rights/Run.lean | put back the old `exhibited` text (`UNKNOWN (budget {conflictBudget})`) | RightsChecks.lean :62, the no-situation guard (also :56, :58): `lake build ResponseShape.Schemas.RightsChecks` failed |
| S2 | Lean | lean/VE/Rights/Run.lean | drop ` ({weighingGloss})` from the line | RightsChecks.lean :55, :56, :58, :62: build failed |
| S3 | Lean | lean/VE/Rights/Run.lean | point the count at the soft route's (`coherence.length`, the used premises) | RightsChecks.lean :58: build failed |
| S4 | Python | ve/rights_route.py | the binder expects the old `UNKNOWN (budget …)` text | `test_rights_conflict_free_without_a_situation_names_no_search`: 1 failed |
| S5 | Python | ve/rights_route.py | the binder drops the gloss | `test_rights_weighing_points_name_what_they_count`: 1 failed |

Each was restored after its run.

## Notes

- **Python binding (F1 debt):** the relay still rebuilds the whole line to bind it, so the two new phrases also live in
  `ve/rights_route.py`. Row rights-cfr-2-text-1 (F1) owns moving that to one Lean template. This item adds no new kind
  of copy.
- **Follow-up, soft route, outside this item's files:** the soft route's CONFLICT-FREE line
  (lean/VE/SoftNorms/Run.lean:362) also prints `coherent situation exhibited: UNKNOWN (budget N)` when the request
  sends no `coherent_model`, and it runs no search either. Its `<j>` repeats `<k>` rather than giving the open
  WP(T) its own `soft-pairs` answer lists (`weighing_points`, :110-113). Changing either one changes soft-route
  text, and that change belongs to its own row.
- **Follow-up, spec:** docs/spec/rights.md 7.3 still writes `situation exhibited: yes | UNKNOWN (<budget>)` and
  `<j> weighing points open`. Naming the no-search form and the gloss there is a spec edit outside this item's files.
- **Size:** about 30 product lines (Run.lean +13/-5, rights_route.py +6/-3), 11 lines of Lean checks and 71 lines of
  tests. The rest is docs, evidence and the checker pin.
- **Trust:** this item adds `exhibitedText` and `weighingGloss` to V (Run.lean) and no K line. Both are exercised by
  `#guard`s that can fail (S1, S2).
