# fsf-r1 REPORT: the Frontier Safety Framework v3.1 use case re-measured on main

**No DRI signature is reserved, and no DELTA row is needed: no product code changed.** There are two questions for
the DRI. Neither is a signature. Both come from the independent fidelity check, and both are for the next item:
(1) whether this document's own contrast of "should" and "must" narrows soft-norms.md 2.2's `{strict, default}` rule
for its three force sets; (2) whether RS9 = same and RS6 = same are readings the words allow.

- Item: fsf-r1, rank 8 of the feature feed (plan `manage-agents/reviews/feature-plan-20261018.md`, row 8 and
  milestone M4). Normal lane. Branch `feature/fsf-r1`, based on main at 93131f96.
- Plan row: "Safety framework re-measured on main (first since Oct 1), with units whose blocker has merged (soft
  'should'/'must' reading sets) re-expressed". Its spec column is "none", so no statement review applies. The
  statement gate has nothing to accept and was not blocking.
- Commits (`git log --oneline main..HEAD --no-merges`, saved at the time of writing): 3ab864b4, 26816b88, 07fce3e3,
  94804781, 984cdc4d, fdecc7db, and this report's commit.

## Deliverables

| Task line | Delivered | Where | Test |
|---|---|---|---|
| (1) The same translation re-checked on main with the same rules: per unit, its status today and the answer-key agreement | Yes. `run.py --check` and `build_document.py --check` both pass on main unchanged, before any fsf-r1 edit: results.json and coverage.json are byte-identical, and 257 of 262 answers agree. No unit changed status: 28 CHECKED, 197 LABELLED, 34 OPEN, 31 UNFORMALISED, the same bytes as Oct 1. Each unit's status (Oct 1 and today), blockers and answer-key items are in [units.json](units.json). The items a unit's rules decide add up, with the 104 items no unit's rule decides (silences and whole-document answers), to 257 of 262. | `measure_r1.py`, [units.json](units.json), [gaps.json](gaps.json), [oct1/](oct1/) | `test_rerun_equals_committed_results`, `test_span_accounting_is_complete`, `test_every_unit_and_item_is_measured_once` |
| (2) Units whose blocker is now a merged feature, re-expressed with it, each change with before/after VE text, checked by a second model, conflicts through R14 | Yes, for every set the merged feature can carry. 7 of 18 reading sets (7 units, 1,436 B) now carry content under `readings@1`. On its part document VE separates and checks each one itself. The other 11 sets each have a reading with no rule or with several rules, which a candidate cannot hold yet. The independent check on Sonnet 5.5 is in [fidelity-check.md](fidelity-check.md). Under R14 it classified C1 and C3 as translation artefacts, and the README now says so. | `build_document.py`, `readings_r1.py`, `readings/results.json`, this report's "Changes" | `test_a_set_carries_content_exactly_when_each_reading_is_one_rule_and_that_rule_is_its_content`, `test_ve_decides_every_content_bearing_set_and_keeps_its_unit_open`, `test_readings_rerun_equals_committed_readings` |
| (3) New coverage.json and README numbers, Oct 1 figures kept as history; the remaining gaps by feature with bytes | Yes. coverage.json's byte statuses are unchanged. Its residual gains `separations` 7, `readings_findings` 5, `pending_candidates` 0 and `couplings` 0, so `residual_total` goes from 35 to 47. The README has an Oct 1 / Oct 18 table and a gaps-by-feature table. The Oct 1 coverage.json and spans.json are saved in [oct1/](oct1/). | `usecases/safety-framework/README.md`, [gaps.json](gaps.json) | `test_span_accounting_is_complete` |
| Product code: none; a VE bug gets a minimal repro, not a fix | No product file changed. No VE bug was found (see "VE findings"). | | |
| Evidence under `docs/usecases/safety-framework/fsf-r1/` | Yes: this directory | | |

## Today on main, in numbers

| Status | Oct 1 bytes | Oct 18 bytes | Units |
|---|---|---|---|
| CHECKED | 4,595 (8.5%) | 4,595 (8.5%) | 28 |
| OPEN | 7,356 (13.5%) | 7,356 (13.5%) | 34 |
| LABELLED | 35,557 (65.4%) | 35,557 (65.4%) | 197 |
| UNFORMALISED | 6,865 (12.6%) | 6,865 (12.6%) | 31 |

- Answer key: 257 of 262 agree, as on Oct 1. The five disagreements are the same recorded findings: A-L5/6/7-INT/DM
  and C1, C-doc.
- Of the 18 reading sets, 7 now carry content; on Oct 1, none did. VE's verdict on each of those 7 part documents
  is CONFLICT-FREE, with a checked model of its premises. On the whole D1 document the verdict stays UNKNOWN
  (route `pending`): Lean found 7 separations (3 decision-only, 2 act-only), and 11 sets are still pending.
- Pilot bytes this item moves: 0 B to CHECKED, because every content-bearing unit stays OPEN by design. 1,436 B of
  OPEN text now has VE's own per-reading verdict instead of the harness's alone.

## Changes (before and after, from readings/results.json and rules.d1.ve)

Each candidate's content is the reading's rule of `rules.d1.ve` from Oct 1, under one rule name shared by the set's
readings, so that VE sees when two twins differ only in force. The Oct 1 text of each rule is unchanged.

#### rs2_misuse (unit `s212-step2`, 246 B, RS2)

- **Before (Oct 1):** readings `p`, `u`, each `"content": null, "meaning_id": "pending"`; VE's readings query UNKNOWN (W2); unit OPEN.
- **After (fsf-r1):** each reading carries its rule as content:
  - `p` (f12-p): *Rule 1. Every proposal must not proceed, if all of the following hold: (a) that proposal is external; (b) there is a level such that both that proposal has reached that level and that level is misuse, unless that proposal is classified as "governance_found_acceptable".*
  - `u` (f12-u): *Rule 1. Every proposal must not proceed, if that proposal is external, unless that proposal is classified as "governance_found_acceptable".*
- **VE's answer on the part document:** route `superposed`, conflict CONFLICT-FREE, premises `model`, unit OPEN; findings {"SeparatedByActOnly": 0, "SeparatedByDecisionOnly": 0}; separation line E24.

#### rs2_ml_rd (unit `s312-step2`, 281 B, RS2)

- **Before (Oct 1):** readings `p`, `u`, each `"content": null, "meaning_id": "pending"`; VE's readings query UNKNOWN (W2); unit OPEN.
- **After (fsf-r1):** each reading carries its rule as content:
  - `p` (f13-p): *Rule 1. Every proposal must not proceed, if all of the following hold: (a) either that proposal is external or that proposal is classified as "high_risk", or both; (b) there is a level such that both that proposal has reached that level and that level is classified as "ml_rd_and_misalignment", unless that proposal is classified as "governance_found_acceptable".*
  - `u` (f13-u): *Rule 1. Every proposal must not proceed, if either that proposal is external or that proposal is classified as "high_risk", or both, unless that proposal is classified as "governance_found_acceptable".*
- **VE's answer on the part document:** route `superposed`, conflict CONFLICT-FREE, premises `model`, unit OPEN; findings {"SeparatedByActOnly": 0, "SeparatedByDecisionOnly": 0}; separation line E24.

#### rs4_elicitation (unit `note-ml-rd-must`, 252 B, RS4elicitation)

- **Before (Oct 1):** readings `default`, `strict`, each `"content": null, "meaning_id": "pending"`; VE's readings query UNKNOWN (W2); unit OPEN.
- **After (fsf-r1):** each reading carries its rule as content:
  - `default` (f20-elicitation-default): *Rule 1. Every proposal should have its risk assessment consider greater elicitation effort by others.*
  - `strict` (f20-elicitation-strict): *Rule 1. Every proposal must have its risk assessment consider greater elicitation effort by others.*
- **VE's answer on the part document:** route `superposed`, conflict CONFLICT-FREE, premises `model`, unit OPEN; findings {"SeparatedByActOnly": 0, "SeparatedByDecisionOnly": 1}; separation line E14.

#### rs4_holistic (unit `s135-holistic`, 189 B, RS4holistic)

- **Before (Oct 1):** readings `default`, `strict`, each `"content": null, "meaning_id": "pending"`; VE's readings query UNKNOWN (W2); unit OPEN.
- **After (fsf-r1):** each reading carries its rule as content:
  - `default` (f20-holistic-default): *Rule 1. Every proposal should have its mitigations assessed holistically in proportion to expected impact.*
  - `strict` (f20-holistic-strict): *Rule 1. Every proposal must have its mitigations assessed holistically in proportion to expected impact.*
- **VE's answer on the part document:** route `superposed`, conflict CONFLICT-FREE, premises `model`, unit OPEN; findings {"SeparatedByActOnly": 0, "SeparatedByDecisionOnly": 1}; separation line E14.

#### rs4_within (unit `g-within`, 107 B, RS4within)

- **Before (Oct 1):** readings `default`, `strict`, each `"content": null, "meaning_id": "pending"`; VE's readings query UNKNOWN (W2); unit OPEN.
- **After (fsf-r1):** each reading carries its rule as content:
  - `default` (f20-within-default): *Rule 1. Every proposal should have its residual risk brought within the acceptable levels, if there is a level such that that proposal has reached that level.*
  - `strict` (f20-within-strict): *Rule 1. Every proposal must have its residual risk brought within the acceptable levels, if there is a level such that that proposal has reached that level.*
- **VE's answer on the part document:** route `superposed`, conflict CONFLICT-FREE, premises `model`, unit OPEN; findings {"SeparatedByActOnly": 0, "SeparatedByDecisionOnly": 1}; separation line E14.

#### rs6_insider (unit `s22-insider-not-required`, 92 B, RS6)

- **Before (Oct 1):** readings `different`, `same`, each `"content": null, "meaning_id": "pending"`; VE's readings query UNKNOWN (W2); unit OPEN.
- **After (fsf-r1):** each reading carries its rule as content:
  - `different` (f15-diff): *Rule 1. Every proposal need not add mitigations against insider misuse beyond the baseline controls, if there is a level such that both that proposal has reached that level and that level is misuse.*
  - `same` (f15-same): *Rule 1. Every proposal need not apply each measure to the model weights, if all of the following hold: (a) there is a level such that both that proposal has reached that level and that level is misuse; (b) that measure addresses insiders.*
- **VE's answer on the part document:** route `superposed`, conflict CONFLICT-FREE, premises `model`, unit OPEN; findings {"SeparatedByActOnly": 1, "SeparatedByDecisionOnly": 0}; separation line E24.

#### rs9_bullet3 (unit `s135-bullet3-dm`, 269 B, RS9)

- **Before (Oct 1):** readings `different`, `same`, each `"content": null, "meaning_id": "pending"`; VE's readings query UNKNOWN (W2); unit OPEN.
- **After (fsf-r1):** each reading carries its rule as content:
  - `different` (f10-dm-diff): *Rule 1. Every proposal must have mitigations make the residual risk of severe harm acceptable, if all of the following hold: (a) either that proposal is external or that proposal is classified as "high_risk", or both; (b) there is a level such that all of the following hold: (i) that proposal has reached that level; (ii) both that level is critical and that level is classified as "ml_rd_and_misalignment".*
  - `same` (f10-dm-same): *Rule 1. Every proposal must have mitigations make the residual risk of harm acceptable, if all of the following hold: (a) either that proposal is external or that proposal is classified as "high_risk", or both; (b) there is a level such that all of the following hold: (i) that proposal has reached that level; (ii) both that level is critical and that level is classified as "ml_rd_and_misalignment".*
- **VE's answer on the part document:** route `superposed`, conflict CONFLICT-FREE, premises `model`, unit OPEN; findings {"SeparatedByActOnly": 1, "SeparatedByDecisionOnly": 0}; separation line E19.

## The independent fidelity check, and what it changed

These are the checker's verdicts. [fidelity-check.md](fidelity-check.md) gives each reason and its action, and
[fidelity-check-answer.md](fidelity-check-answer.md) has the full answer.

- **FAITHFUL WITH NOTE:** RS2 on both units, and RS6.
  - The notes for RS2: the safety-case parenthetical and the "only after" order are dropped.
  - The note for RS6: RS6 = same is overbroad, and "At this stage" is dropped.
- **UNFAITHFUL:** the three force sets and RS9.
  - RS4elicitation, RS4holistic, RS4within: "must" and "should" each have one reading, since the document uses both.
  - RS9: RS9 = same drops "severe".
- **C1 and C3: translation artefacts (R14).** The README no longer presents them as conflicts in the source.
  - C1 comes from RS6 = same together with the strict force of RS3 = Ds.
  - C3 comes from RS9 = same.

The force sets follow soft-norms.md 2.2 ("In translation any force word ... is a READINGS unit `{strict, default}`
unless a cited source unit narrows it"). The Oct 1 results review (finding B) required this, and
`test_every_should_keeps_its_strict_reading` pins it. So this item does not narrow them: that would change a
general translation rule on one checker's word. RS9 = same and RS6 = same are inputs to C3, C1 and C-doc, whose key
answers were frozen before VE ran. Withdrawing them would change those answers against the key. Both questions go
to the next item and the DRI.

## Remaining gaps by feature (gaps.json; bytes of the 54,373)

Each unit counts under every blocker it has. "Alone" means the unit has no other blocker, so its bytes would move
when that feature lands. A content-bearing open set is not a VE gap: the text has two readings.

| Feature | Units | Bytes | Alone: units, bytes | Where it is in the feature plan |
|---|---|---|---|---|
| judgment terms (16 open terms; "as appropriate", "where appropriate", "adequate", "uplift") | 36 | 7,976 (OPEN 6,621, UNFORMALISED 1,355) | 23, 5,114 | jt-1 merged (Lean core); jt-2 (document mode) and the JT-5 switch-on are needed first |
| modality ("may", "could") | 18 | 3,276 | 18, 3,276 | LABELLED hedged; attitudes (AT) |
| process and deadline wording | 11 | 2,212 | 11, 2,212 | events (ET-4 to ET-6) |
| readings with no rule or with several rules | 11 | 2,161 | 1, 95 | no plan yet: a `readings@1` candidate is one rule (below) |
| external references (RAND SL, SAIF) | 7 | 1,978 | 7, 1,978 | none: pointers, not content |
| attitudes: beliefs, expectations | 11 | 1,855 | 11, 1,855 | attitudes (AT) |
| two readings kept, each decided by VE | 7 | 1,436 | 4, 640 | done in fsf-r1; OPEN by design |
| causation | 3 | 807 | 3, 807 | alternatives@0 rejects "provides uplift to" |
| defeasible: "may be adjusted" | 2 | 551 | 2, 551 | defeasible (DF) |
| attitudes: aims without force | 2 | 486 | 2, 486 | attitudes (AT) |
| addressee: a recommendation to the field | 2 | 283 | 2, 283 | no plan yet |
| no claim to check (layout, exposition, definitions, examples) | 165 | 29,619 | 165, 29,619 | not a gap |

The 11 pending sets, and why each still has no content:

- **A reading that states no rule.** RS3 = F on two units: the recommendation is addressed to the field and puts no
  norm on the developer. This is F16's own "should" set, so its strict/default force (RS3force) cannot reach VE until
  F can be written. The same holds for RS4aim = intent ("we aim to" as an intention), RS7 = M ("may not" as "might
  not") and RS8 = scope (a scope sentence with no rule of its own) on three units.
- **A reading of several rules.** RS1 = G on three units is the classification together with its DM and SEC gates.
  RS5 = R is the determination together with the further assessment. RS8 = rel on bullet 3 is one of two rules,
  depending on RS9.

## VE findings (no VE bug; no product change)

1. **A candidate holds one rule.** A reading of no rule, or of several, can only stay pending. While one stays
   pending, VE's verdict on the whole D1 document is UNKNOWN (route `pending`, premises UNKNOWN) even though 7 sets
   are checked (`readings/results.json`, `whole_document`). This is the feature gap above, not a bug.
2. **E24 on act-only separations.** On RS2 (both units) and RS6 the separation line is E24: "These two readings
   differ in a checked situation that VE cannot yet show in words." The checker noted the line has no content. This
   is designed wording for a separation the English planner cannot render, not a bug.
3. **The default search misses RS9's pair.** With `max_size=2` and no hint, `ve.readings_s1.search` finds no
   separating situation for RS9 within its base budget. The document is then refused ("distinguishing model id does
   not match model"). The builder therefore tries D1's distinguishing case first (`hints`, the search's own
   parameter). Seeded bug 3 shows the refusal.
   - Minimal repro: run `build_document.record_situations` with `hints=[]` on the RS9 set.
   - The guard needs a reached ML R&D CCL with an external or high-risk proposal, so the smallest separating base is
     larger than the search's first bases. This is search reach, not a wrong answer.

## Seeded bugs (Python: the only language changed; each restored, `git status` clean after)

| # | Behaviour claimed | File | Mutation | Failing test |
|---|---|---|---|---|
| 1 | each candidate's content is its own reading's rule | `usecases/safety-framework/build_document.py` (`content_set`) | every reading takes the first reading's rule | `test_a_set_carries_content_exactly_when_each_reading_is_one_rule_and_that_rule_is_its_content` (norm mismatch) |
| 2 | twins share one rule name, and VE's saved answers are reproduced | `usecases/safety-framework/build_document.py` (`content_set`) | the shared name dropped (each rule keeps its own) | `test_readings_rerun_equals_committed_readings` ("readings/results.json is out of date") |
| 3 | every content-bearing set gets a checked separating situation | `usecases/safety-framework/build_document.py` (`record_situations`) | the D1 distinguishing case no longer tried first | `test_span_accounting_is_complete` (VEError: distinguishing model id does not match model) and `test_readings_rerun_equals_committed_readings` |
| 4 | every unit that is not CHECKED has a known blocker | `usecases/safety-framework/measure_r1.py` (`blockers`) | degree terms mapped to "unknown" | `test_every_unit_and_item_is_measured_once` (`s212-deem`) |
| 5 | per-unit agreement counts every item | `usecases/safety-framework/measure_r1.py` (`measure`) | an agreeing item (R2/ACCEPTABLE) left out of `items_agree` | `test_every_unit_and_item_is_measured_once` (`s135-bullet2`: 33 + 0 == 34). A first variant that left out C1 survived, because C1 disagrees and the count did not change; it was replaced. |

## Trust, DELTA, tests

- **Trust:** `uv run python tools/trust_map.py --check` on this branch against 93131f96: K +0, S +0, D +0, G +0,
  tied +0, trusted +0; PASS. No Lean file changed, so there is no R16 allowance and no FOLLOW-UPS row.
- **DELTA:** [DELTA.md](DELTA.md) has no user-visible VE delta, because no product code changed.
- **Collection:** `tools/gate_collection.py --check --prebuilt`: 4 added, 0 removed, 0 refused, 0 stale, 0
  malformed.
- **Selected tests:** `mac-pytest.sh --select` on the Mac runner selected 40 units. The first run had one failure,
  `tests/test_difffuzz.py::test_every_fixture_is_read_or_excluded_with_a_reason`: the new `readings.json` was neither
  read nor excluded. It was fixed in fdecc7db by moving the file to `readings/results.json`, which the corpus already
  excludes as a use case's recorded results. The rerun on the final HEAD is recorded below.
- **Not run:** the full gate (the chain runs it on the final HEAD); no reader evaluation, since no new English.
- **Main's known-red tests:** none is in this item's selection.

## Next items

- **fsf-r1b (DRI question first):** apply the fidelity check's two translation questions.
  - Does the document's own contrast of "should" and "must" narrow RS4holistic, RS4within and RS4elicitation (and
    RS3force) to one force each?
  - Should RS9 = same and RS6 = same be withdrawn?

  Either changes C1, C3 and C-doc against the frozen key, so the DRI decides before the build. Estimate: if both
  are applied, up to 640 B could reach CHECKED, because these four units have no other blocker:
  - note-ml-rd-must, 252 B;
  - s135-holistic, 189 B;
  - g-within, 107 B;
  - s22-insider-not-required, 92 B.

  RS9's unit (269 B) keeps its judgment term.
- **A readings feature for candidates with no rule or several rules** (no plan yet). This would let the 11 pending
  sets (2,161 B) carry content, so that VE's verdict on the whole D1 document could stop being UNKNOWN.
- **jt-2, then the JT-5 switch-on**, for the 7,976 B of judgment terms; 5,114 B have no other blocker.

## Build checklist lines that apply (prompts/build-checklist.txt)

- **19 (use-case formalisation).** Each rule's header in `rules.d1.ve` keeps its source quote and modal strength
  from Oct 1, and no rule text changed. The six M9 mutants still change the answers
  (`test_metrics`). No default, closure or uniqueness assumption was added. The one bridge is still marked
  `assumption`.
- **20 (reports).** Every number here comes from the saved files: `readings/results.json`, `units.json`,
  `gaps.json`, `coverage.json` and `results.json`. `test_every_unit_and_item_is_measured_once` recomputes the
  measure, and `measure_r1.py --check` reproduces both evidence files. What was not run is listed above.
- **21 (acceptance tags).** Deliverables (1) to (3) are AGENT. The second-model check is AGENT, done by a Claude
  Code subagent on another model. There is no HUMAN or EXTERNAL item.
- **22 (tests).** Selected tests and the added tests were run; the full gate is left to the chain (task rule).
- **23 (DRI rulings).** No delta. R14 is applied to C1 and C3, which are now translation artefacts.

## Self-review against BUILDER-CHECKLIST

1. **N.A.** No relay, schema or response field changed. VE is called only through `ve document check` and `load`.
2. **PASS.** Each task line is in the Deliverables table, with its commit and test.
   - `git diff main...HEAD` adds no Python copy of a Lean decision. `measure_r1.py` groups recorded statuses; it
     decides no status.
   - It adds no permanent test of batch numbers: the evidence in this directory has no test (D4).
   - It touches no file another in-flight branch edits: `git diff --name-only main...<branch>` was checked for every
     `lean-first/*`, `feature/*`, `infra/*` and `foundation/*` branch.
3. **PASS.** Seeded bugs 1 to 5 each fail a named test. The equivalent mutant was replaced.
4. **PASS.** Base and head give the same outputs: on main and on HEAD, `run.py --check` (results.json) and the
   byte statuses of `build_document.py` are identical (`test_rerun_equals_committed_results`,
   `test_span_accounting_is_complete`). The readings answers are new, not changed.
5. **N.A.** No relayed answer is read by new code. The part documents go through VE's own bound relays.
6. **PASS.** The branch is on main 93131f96, `merge-base` = main. The commit list is from `main..HEAD --no-merges`.
   The gate runs on the final HEAD in the chain.
7. **PASS.** DELTA has no rows, trust is +0, and no row is reserved (DELTA.md, `trust_map.py --check`).
8. **PASS.** No VE output changed. The use case's own output changes (coverage.json residual +12, spans.json
   `reading_content` on 7 units, the README sections) are listed in this report.
9. **PASS.** `select_tests.py --base $(git merge-base HEAD main)` selects 40 of 434 units, not all of them, and
   includes `tests/test_safety_framework.py`, where seeded bugs 1 to 5 fail.
10. **N.A.** No Lean statement or proof changed.
11. **N.A.** No budget, limit or deadline changed. The new tests use no sleep and no timeout.
12. **N.A. for VE.** For the use case: `build_document.py --check` takes about 19 s on the VM, against 3.7 s
    before, because it now searches 7 sets' situations and Lean replays them. `readings_r1.py --check` takes about
    36 s. There is no change to the pilot paths.
13. **PASS.** No test removed or renamed. `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0
    malformed.
