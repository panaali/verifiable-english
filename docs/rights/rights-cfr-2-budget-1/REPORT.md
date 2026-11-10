# rights-cfr-2-budget-1: REPORT

**Status:** delivered on branch feature/rights-cfr-2-budget-1. Fix (A) is made under R1, the count is named under R3,
and both routes' `<j>` now comes from one owner. No DRI signature is reserved, because no printed count changes on any
existing fixture or test (step 1, and the soft probe below).
**What changed:** with no situation supplied, a `rights-conflict` CONFLICT-FREE answer no longer says a search hit its
budget. The line names what `<j>` counts, and rights.md 7.3 writes both forms. The soft route's `<j>` is now WP(T)
from the same owner (`Wire.openCoherence`) instead of a repeat of `<k>`. Every JSON field stays as it was.
**Open:** the full gate, which the chain runs on the final HEAD. The soft route's own no-search text is a follow-up
(Notes); it has been sent to the DRI.

## Step 1: measured before any edit (main f3f40d51dc)

Evidence: `evidence/step1_probe.py` and its saved output `evidence/step1-output.txt`. The fixture is `WEIGHED`
(tests/test_rights_report_parts.py), with no `situation`: an unranked default pair on `arrest_permitted` and
limitation 29 with a sufficient condition. Its default pair alone, no-arbitrary-arrest and may-detain (the probe's
`plain` case), ran once as a rights document and once as a soft-norms document. `WEIGHED` itself has a limitation, so
it cannot go through the soft route.

(a) The status line the rights route printed for `WEIGHED`:

```text
CONFLICT-FREE among rules on the same act, conditional on 1 coherence premises and 2 limitation premises (soft:coherence:may-detain,no-arbitrary-arrest, rights:limitation:l29:arrest_permitted:necessary:determined_by_law, rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity); 1 weighing points open; situation exhibited: UNKNOWN (budget 10000)
```

(b) The "weighing points open" counts: `WEIGHED` on the rights route gives 1. `plain` gives 1 on the rights route and
1 on the soft route (soft line: `conditional on 1 coherence premises; 1 weighing points open; coherent situation
exhibited: UNKNOWN (budget 10000)`). The probe's `disjoint` variant (disjoint guards) also gives 1 and 1.

The two definitions on the base:
- **Rights route:** `<j>` = `weighing.length`, where `weighing := VE.SoftNorms.Wire.openCoherence (correlate D)`
  (lean/VE/Rights/Run.lean:432). `openCoherence` (lean/VE/SoftNorms/Wire.lean:169-170) lists the colliding default
  pairs that are not `Comparable`, i.e. that no ranking resolves. That is WP(T) (docs/spec/soft-norms.md:577, "the
  WEIGHING POINT and UNKNOWN pairs") with no pair evidence; a rights-conflict request carries none.
- **Soft route:** `<j>` = `conditional.length` (lean/VE/SoftNorms/Run.lean:362), the same number it prints as `<k>`.
  `conditional := sufficientCoherence openLabels …` (:352) keeps only the open labels the certificates need.
  `openLabels` is WP(T) under the request's pair evidence (`openAfterClassification`, :115-120).

**Reading: the soft count was wrong.** soft-norms.md 7.3 (:704) has separate `<k>` and `<j>`, and :577 defines the
open weighing points as WP(T). The soft line printed `<k>` twice (commit 1961d91c91 gives no reason). The rights count
is WP(T). So the task's branch "make both routes take it from one Lean definition" applies. (A first draft of this
item read the difference as by design; the self-review's A finding corrected it.)

**No printed count changes.** Before making the change, a probe build of the soft route threw whenever a CONFLICT-FREE
answer had `openLabels.length != conditional.length`. Every soft-conflict user in the suite ran against it: 18 files,
893 tests, 0 hits (`evidence/soft-count-probe.txt`). So did five constructed cases meant to make the counts split
(`evidence/soft_count_edge_cases.py`: a default guarded by ⊥, two pairs, a contradictory guard, disjoint guards): 0
hits. Python's prover always used the coherence premise. The counts can differ only for a request whose certificates
leave an open pair's coherence premise unused, and none was found. The STOP condition (a changed count on an existing
fixture or test) is therefore not met.

## Delivered

| Deliverable | Where | Test |
|---|---|---|
| (1) Situation text, fix (A): with no situation supplied the line ends `situation exhibited: none supplied (not searched; budget 10000 unused)`. A supplied one still says `yes`, and the JSON fields are unchanged. | `Run.lean` `exhibitedText`, used by `conflictAnswerOf`; relay binding `ve/rights_route.py` `_bind_conflict`; docs/spec/rights.md 7.3 names the form and when it applies | `test_rights_conflict_free_without_a_situation_names_no_search` (condition test; it fails on main, whose line contains `UNKNOWN (budget`), RightsChecks.lean :61-:62 |
| (2a) Count named (R3): `<j> weighing points open (colliding default pairs no ranking resolves)` | `Run.lean` `weighingGloss`; the relay binding; rights.md 7.3 | `test_rights_weighing_points_name_what_they_count` (condition test: count 1 and wording pinned on step 1's fixture), RightsChecks.lean :58 (0 coherence premises, 2 weighing points), :66 |
| (2b) One owner of the count: WP(T) is `Wire.openCoherence`. The soft route's `openAfterClassification` is rebuilt on it (minus the pairs its evidence discharges as DISJOINT), and the soft line's `<j>` is that list's length; the duplicate `conditional.length` is gone. | `SoftNorms/Run.lean` `openAfterClassification`, `conflictFreeText` | `test_rights_and_soft_routes_count_the_same_weighing_points` (step 1's `plain` pair on both routes, from Lean's raw answers), SoftNorms/Run.lean :127 (`#guard`, `<k>` 1 and `<j>` 2) |
| (3) The R1 delta test over saved evidence | `delta.json` (base and head lines, both forms) | `test_rights_no_search_delta_keeps_every_quoted_value` |
| (3) Binding fuzz for the new words | the relay refuses the old line restored, the gloss dropped and the budget shifted | `test_a_mutated_no_search_line_is_refused` (3 cases) |
| (4) Correction of rights-cfr-2's REPORT | docs/rights/rights-cfr-2/REPORT.md, its "Readings of 7.3" bullets on `<j>` and the budget, citing this item; its DELTA row 1 is annotated as amended | n/a |

Fix (A) meets R1, so (B), running a bounded situation search, was not needed. (A) keeps the quoted value `budget 10000`
and the path `status_text`, and it is more specific: it says no situation was supplied or searched. The spec-template
test (`test_rights_conflict_free_report_evidence`, the condition of rights-cfr-2's DRI-signed row 1) still reads the
7.3 template from docs/spec/rights.md. 7.3 now writes the gloss and the third alternative `none supplied (not searched;
<budget> unused)`, with a paragraph saying when each one applies. The test picks the alternative from the spec and
compares Lean's raw `ve_service` line and the relayed line with it byte for byte.

## Seeded bugs (mutants.json)

| id | language | file | mutation | caught by |
|---|---|---|---|---|
| S1 | Lean | lean/VE/Rights/Run.lean | put back the old `exhibited` text (`UNKNOWN (budget {conflictBudget})`) | RightsChecks.lean :62, the no-situation guard (also :56, :58): `lake build ResponseShape.Schemas.RightsChecks` failed |
| S2 | Lean | lean/VE/Rights/Run.lean | drop ` ({weighingGloss})` from the line | RightsChecks.lean :55, :56, :58, :62: build failed |
| S3 | Lean | lean/VE/Rights/Run.lean | point the rights count at the used premises (`coherence.length`) | RightsChecks.lean :58: build failed |
| S4 | Python | ve/rights_route.py | the binder expects the old `UNKNOWN (budget …)` text | `test_rights_conflict_free_without_a_situation_names_no_search`: 1 failed |
| S5 | Python | ve/rights_route.py | the binder drops the gloss | `test_rights_weighing_points_name_what_they_count`: 1 failed |
| S6 | Lean | lean/VE/SoftNorms/Run.lean | the soft line's `<j>` back to `conditional.length` (the old duplicate) | SoftNorms/Run.lean :127 (`#guard`): `lake build VE.SoftNorms.Run` failed |

Each one was restored after its run.

## Trust (R16)

`uv run python tools/trust_map.py --check` against f3f40d51dc6d gives K +0, S +0 and V +14: lean/VE/Rights/Run.lean +9
(`exhibitedText`, `weighingGloss`, docstrings) and lean/VE/SoftNorms/Run.lean +5 (`conflictFreeText`,
`openAfterClassification`). That is trusted +14, under 150. The three new definitions are classed D[V] in
tools/trust-classes.json. The growth is recorded with `--allow` as "SIGNED by standing ruling R16 (DRI-RULINGS.md),
rights-cfr-2-budget-1, 2026-11-10" (docs/trust-baseline.json). Each new definition is exercised by a `#guard` that its
seeded bug fails: `exhibitedText` RightsChecks :61-:62 (S1), `weighingGloss` :62 and :66 (S2), `conflictFreeText`
SoftNorms/Run.lean :127 (S6). The FOLLOW-UPS row asking for the ties pass is in `evidence/follow-ups-row.md`, and it
is appended to FOLLOW-UPS.md.

## Notes

- **Python binding (F1 debt):** the relay still rebuilds the whole rights line to bind it, so the two new phrases also
  live in `ve/rights_route.py`. Row rights-cfr-2-text-1 (F1) owns moving that to one Lean template.
- **Follow-up, soft route (sent to the DRI on 2026-11-10, inbox/dri/20261110T192504Z-rights-cfr-2-budget-1-3006072.md):**
  the soft route's CONFLICT-FREE line (`conflictFreeText`) still prints `coherent situation exhibited: UNKNOWN (budget
  N)` when the request sends no `coherent_model`, and it runs no search either. The fix is soft-route text and belongs
  to its own row.
- **The UNKNOWN line** keeps its literal `budget 10000`: `ResponseShape/Encoders/Rights.lean` states that literal.
- **No k ≠ j fixture from real certificates:** the RightsChecks guard at :58 uses a synthetic `uses` to get
  0 coherence premises with 2 weighing points. No real certificate that leaves an open pair unused was found (step 1).
- **Size:** about 45 product lines (Run.lean +14/-7, SoftNorms/Run.lean +12/-5, rights_route.py +6/-3), 11 lines of
  Lean checks, 3 lines of trust classes, about 100 lines of tests and 6 lines of spec. The rest is docs and evidence.

## Spec re-read

- The CONFLICT-FREE line against docs/spec/rights.md 7.3 (:765-766, as amended), and the reading paragraph after the block.
- `<j>` = WP(T) against docs/spec/soft-norms.md:577 and the soft 7.3 line (:704-705).
- The budget value against rights.md 7.3 `UNKNOWN: <target>, <budget>` (the UNKNOWN line is unchanged).

## Self-review against BUILDER-CHECKLIST

(filled in after the checks; see the end of this file)
