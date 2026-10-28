# sc-5rb: scope 11, a per-choice GOVERN over a reading set inside a governed list. Build report

**DELTA rows 1 and 2 are SIGNED by the DRI** (reviews/dri-decisions-20261027-sc-5rb.md item 1,
reviews/dri-decisions-20261028-sc-5rb.md item 1). No signature is reserved, and trust is under R16 (+136, K +0).
The four `Pinned.JsonWF` statements and the render of a set composed per choice go to **sc-5rc**.

- Branch `feature/sc-5rb`, worktree `/home/seyran/code/ve-sc-5rb`, merge base `d9cff5345` (main, sc-5r merged).
- Read first: the DRI route (`reviews/dri-decisions-20261027-scope-readings.md` item 1); spec `docs/spec/scope.md` 11
  (with 1.7, 5.1, 5.7, 7.1, 7.7); plan `docs/spec/scope-PLAN.md` "SC-5"; sc-5r's REPORT, review and recheck.
- **Statement gate: PASS.** sc-5r's review is this section's statement review, and its recheck ended **MERGE**
  (`manage-agents/sc-5r-looprecheck1.final.md`). Every statement proved here equals the stub's
  (`docs/spec/scope/SpecStubs_sc5r.lean`) after whitespace normalisation, and the definitions are the stub's verbatim:
  `tests/test_scope_sc5r_stub.py::test_each_statement_sc5rb_proves_is_the_stubs_text` and
  `::test_the_definitions_are_the_stubs_verbatim`. No approved statement changes: `scope_admission`,
  `scope_absent_unchanged`, `readings_refused` and F-rs stay, proved and selected (the DRI's condition).
- Overlap: `lean/VE.lean` and `lean/VE/Audit.lean` are also touched by feature/ap-2b, ap-3c, df-2b, qt-a3b,
  foundation/me-1 and infra/arch-AR-1. Those are an import union and a generated audit (R12), not overlaps. No live
  branch touches the other hand-written files.

## Task rows

| Row | Delivered | Where |
|---|---|---|
| (1) the definitions and theorems in lean/VE/Scope/, calling lf-14d's joint choices | 11.2 verbatim in `lean/VE/Scope/Readings.lean` (`VE.Discourse.allChoices`, `productSize` called, never edited). Proved: `governSets_no_sets`, `governSetsFast_eq`, `scope_set_choices`, `governSets_choice_refused`, `faultOf_every`, `choiceFault_limit`, `governSets_limit` (`lean/VE/Scope/ReadingsTheorems.lean`); `scope_admission_sets`, `checkDocSets_no_sets`, `checkDocSets_absent_unchanged` (`lean/VE/Service/ScopeAdmission.lean`). All in `lean/VE/Audit.lean`, no `sorry` | spec 11.2, 11.3 |
| (1) not delivered | `governSets_preserves`, `governSets_every_choice`, `governSets_strings`, `governSets_readings_refused` take `Pinned.JsonWF`, whose parser lemma is sc-1ae's (not merged): **sc-5rc**, as spec 11.7 plans | spec 11.7 |
| (2) the replacement of `readings_refused` and F-rs, as 11.4 says | The document mode's entry is `checkDocSets` (`lean/VE/Service/Document.lean`), which calls `governSetsWith governFast` and hands `check` GOVERN's reading sets through `withSets` when a set is governed per choice. `runCaseReported` calls it, and the encoder theorem `checkDocSets_fits` replaces `checkDoc_fits` there. `checkDoc` stays as the no-set statement's reference (`checkDocSets_no_sets`). `readings_refused`, F-rs's `#guard`s and `scope_admission` are unchanged and still built | spec 11.4 |
| (3) the 11.6 fixtures as `#guard`s | `lean/VE/Scope/ReadingsExamples.lean`: the stub's fixtures verbatim (SR-1, SR-1-pc, SR-1-g2, SR-c, SR-c-nr, SR-cap at 72 and 64, SR-u, SR-0, SR-g, F-rs, SR-dep, SR-lim). Added: both sides of the 11.1 clauses that sc-5r's review F2 found without a fixture (two versions refused, no reading refused, one reading governed, `layoutReach` on each reach kind), and `pickOf` by id and version | spec 11.6 |
| (3) part-document tests (u0165.s03's set in a governed list, never the whole constitution) | `tests/test_scope_readings_document.py`, 13 tests on F1 with the set built in the test (no copy of F1): SR-1 admitted (u0164.s02 OPEN, two choices, coverage OPEN 896 / UNFORMALISED 472); SR-c on each reading; the refusing side of each 11.1 clause; SR-0; a case's own `reading_sets` is no input; `meaning_id` read as in the written-in-full document; render's refusal (row 2); the R8 structural fuzz over the new answer | 11.7 item 6 |
| (4) seeded bugs from the build plan, plus a mutant per new trusted definition | below, and `mutants.json`; R16's `trust_mutants` run: `trust-mutants.json` | 11.7 |
| 11.7 item 7 (`ve/document/lean.py` binds governed readings) | not needed for check: the answer names no reading. Render shows readings, so it now refuses a set composed per choice (`CheckerUnavailable`, naming the unit; DELTA row 2, SIGNED). The relayed, bound readings are **sc-5rc** | `ve/document/render.py` |

Spec deviation: 11.7 item 6 names a data file `tests/data/scope/hard-constraints-readings.scope.md`. The test builds
that document from F1 instead, so F1 keeps one owner. The distinguishing situation is computed for F1's environment,
because the pilot's model id names the pilot's environment.

## Found while building

- **A case's own `reading_sets` would have been an input.** Once `check` reads GOVERN's reading sets from the case,
  a caller's `reading_sets` member would replace the document's under `scope@0`. `withUnits` now drops it, and only
  `withSets` sets it (`test_a_cases_own_reading_sets_member_is_no_input`, seeded bug below).
- **No check reads a norm reading's `meaning_id`** in the document mode, with or without scope@0: a stale id changes
  no answer. 11.7 item 3 asks that the governed answer be read as today's. The test pins that both documents read it
  alike (FOLLOW-UPS "## sc-5rb").
- **Render** shows each reading from the authored meta, which here is a part only Lean composes (row 2).
