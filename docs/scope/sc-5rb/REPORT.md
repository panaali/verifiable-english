# sc-5rb: scope 11, a per-choice GOVERN over a reading set inside a governed list. Build report

**DELTA rows 1 and 2 are SIGNED by the DRI** (reviews/dri-decisions-20261027-sc-5rb.md item 1,
reviews/dri-decisions-20261028-sc-5rb.md item 1), and the size is taken (reviews/dri-decisions-20261028-sc-5rb-size.md). No signature is reserved, and trust is under R16 (+136, K +0).
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

## Seeded bugs

[mutants.json](mutants.json) lists 21 seeded bugs, each planted alone on the committed tree and then restored. Each
makes its named test or `#guard` fail.
- **Lean, `lean/VE/Scope/Readings.lean` (15).** Each is checked by `lake build` of the fixtures and theorems.
  - The 11.7 build plan's seeded bugs, each with its fixture: `governedSetUnits` without the governor-unit test
    (SR-g); `atChoiceOn` keeping the governed sets (SR-1, SR-dep, SR-lim); `faultOf` always naming a choice (SR-c,
    F-mm); `choiceFault` naming a limit (SR-lim); `assemble` without the agreement check (SR-dep); `setChoices` with
    `≥` (SR-cap at 64); `readingIn` returning the written reading (SR-1).
  - One per further definition or clause: no one-entry test; no non-empty test; written content allowed;
    `layoutReach` true on a fixed reach; `choiceText` without the reading id; `shapeOf` with one reading;
    `pickOf` ignoring the version; `governSetsWith` skipping faults.
- **Lean, `lean/VE/Service/Document.lean` (5).** Each is checked with the service rebuilt and pinned, and its test
  run with `VE_NATIVE_PREBUILT=1`. Each test passes unmutated.
  - From the build plan: `withGoverned` without `reading_sets` (`test_sr1_…`); `withGoverned` copying
    `reading_sets` when no set is governed (`test_sr0_…`, which gives `reading_sets must be a list`).
  - Also: `withUnits` keeping a case's own `reading_sets` (`test_a_cases_own_reading_sets_member_is_no_input`);
    `check` ignoring GOVERN's reading sets (`test_sr1_…`); `checkDocSets` running GOVERN alone (`test_sr1_…`). Three
    of the five also break `checkDocSets_no_sets` or `scope_admission_sets`.
- **Python, `ve/document/render.py` (1).** With render's refusal removed, render shows the authored part, and
  `test_render_refuses_a_set_composed_per_choice_naming_its_unit` fails (`SyntaxError: AST nodes must be nonempty
  tagged JSON arrays`).
- **No Rust** product code changed.
- The build plan's Python bug ("the relay binding a governed reading by content equality") has nothing to plant: the
  relay binds no reading (11.7 item 7 is sc-5rc).
- **Statement gate.** A changed hypothesis in a proved statement fails
  `tests/test_scope_sc5r_stub.py::test_each_statement_sc5rb_proves_is_the_stubs_text`; that is what it compares.

**R16 mutants per trusted definition:** `mac-pytest.sh --trustmut -- --max-mutants 400 --jobs 6 --allow
docs/scope/sc-5rb/trust-mutants-allow.json` at `118e33b5`, run on ve-mac-1. Result: **220 KILLED, 0 SURVIVOR,
0 UNKNOWN, 68 INVALID, 50 ALLOWED, 0 NOT RUN**, exit 0 ([trust-mutants.json](trust-mutants.json)). The first run
left 38 survivors and 36 unknowns. New fixtures killed 24 of the survivors: two governed sets, governor order, a
dependent rule on the first and the last unit, 65 choices, a set with no version, a lead-in set listed first, and
the governed units kept as written. The 14 allowed survivors are each argued in
[trust-mutants-allow.json](trust-mutants-allow.json):
- equivalent: `Option.any`/`all` on a found set; `layoutReach ||` beside a reach that never covers; `contains` over
  unit ids a covering reach already implies; `isEmpty` of a list cut to one element;
- defensive: `readingIn`'s agreement check, as sc-5r's review F2(d) found;
- `Pinned.withGoverned`'s four list cuts, which break `scope_admission_sets`'s proof (checked by hand), a proof
  trust_mutants does not count.

The 36 unknowns are mutants that do not elaborate (type errors at the mutated site).

## Trust, size, bytes

- **Trust:** `uv run python tools/trust_map.py --check` on the final HEAD, against main `c0a80d23a`, gives **K +0, S
  +6, V +130 (trusted +136)**:
  - `VE/Scope/Readings.lean` +118 (G[V], untied, as 11.7 plans);
  - `VE/Service/Document.lean` +12 (`withSets` D[V] and `check`'s reading-set case; `checkDocSets` is tied to its
    three theorems);
  - `VE/Service/ScopeAdmission.lean` +6 (S, `Pinned.withGoverned`, the case the statements name).

  It is recorded with `trust_map.py --allow` as "SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-5rb,
  2026-10-28". The FOLLOW-UPS row "## sc-5rb" asks for the ties pass. R6 does not apply: no decision path is
  deleted, and `admitBlock`'s readings check stays.
- **Size:** about 1,020 hand-written lines (`git diff --numstat` against main, generated files excluded). About 237
  of them are the stub's definitions and fixtures copied verbatim, and about 110 are guards and allow entries for
  R16's mutants. This is over the ~600 rule. The DRI took the item at this size: see "Size decision" below.
- **Bytes:** 0 claimed (estimate). The constitution's M13 number (u0164.s02, +22 B: the lead-in OPEN by its items
  instead of UNFORMALISED) waits for the pilot's rewrite of the hard-constraint block (scope queue 4.4 step 2).
- **CPU:** `governSets` runs `governFast` once per joint choice: twice for u0165.s03, at most 64 times. `ve document check` takes 0.84 s wall
  (0.66 s user) on the part document, against 0.86 s (0.70 s) on F1 without a set, on the VM at load about 42 (a spot
  check, not a benchmark). No benchmark row is added. sc-5r's review F4 asks for a B1 variant with a governed set, and that is in the FOLLOW-UPS for the
  ties pass.
- **Next item:** **sc-5rc**: the four `Pinned.JsonWF` statements after sc-1ae, and Lean's answer carrying the
  composed readings for render (11.7 item 7). After that comes the pilot's rewrite of the hard-constraint block.
- Acceptance: AGENT for the build, fixtures, tests and seeded bugs. HUMAN (DRI): rows 1 and 2 (signed) and the size.
  EXTERNAL: none.

## Size decision

The DRI took sc-5rb at about 1,020 hand-written lines (option (a); split (b) rejected) in
`reviews/dri-decisions-20261028-sc-5rb-size.md` item 1. Counted without the ~237 lines copied verbatim from the
reviewed stub, the item is about 780. The decision's conditions hold on this HEAD:
- `tests/test_scope_sc5r_stub.py::test_the_definitions_are_the_stubs_verbatim` and
  `::test_each_statement_sc5rb_proves_is_the_stubs_text` pass and are selected;
- the trust_mutants evidence has 0 SURVIVOR and 0 UNKNOWN (above);
- nothing was added after the decision, and further work goes to sc-5rc.

## Selected tests

`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` (base `c0a80d23a`), on ve-mac-1 (aarch64), 6
jobs, 3,541 s: **395 units recorded, 0 failed, exit 0**. The runner's summary reads "HEAD 26e555c3 (clean)". Among
the units: `tests/test_scope_readings_document.py`, `tests/test_scope_document.py`, `tests/test_scope_lean.py`,
`tests/test_scope_sc5r_stub.py`, `tests/test_trust_mutants.py`, and the run's `lake build` and `lean/audit.py`, which
build F-rs's and `readings_refused`'s checks (the DRI's condition). After `26e555c3` only these changed:
`tools/trust-classes.json`, put back in main's module order (the same table, checked by `trust_map.py --check` and
`regen_generated.py --check`); this report; and `mutants.json`. Main's known-red tests were not selected.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: PASS. The answer keeps the document shape, and `checkDocSets_fits`
   (`lean/ResponseShape/Encoders/Document.lean`) proves every row fits `Skeletons.document`. The one-fault structural
   fuzz over SR-1's genuine answer is refused (`tests/test_scope_readings_document.py::test_every_structural_mutant_of_the_sr1_answer_is_refused`).
2. Every deliverable built, no rule broken: PASS. Task rows above; what is not built is in sc-5rc (spec 11.7's split,
   and DRI decision 20261028 item 1). The diff has no Python copy of a Lean decision: render's refusal tests only for
   a part, and that refusal is signed (row 2). No report test was added. Shared files are an import union and
   generated files only (R12).
3. Tests can fail: PASS. 21 seeded bugs (`mutants.json`), and `trust_mutants` exit 0 with 0 SURVIVOR and 0 UNKNOWN
   (`trust-mutants.json`, `trust-mutants-allow.json`).
4. Python, Lean and Rust agree: PASS. No Rust or Python verdict path reads scope@0. Main and this branch were run
   side by side on the part document (DELTA rows 1-2). F1 and documents without a governed set are unchanged:
   `checkDocSets_no_sets` (proved), `test_sr0_…`, and `tests/test_scope_document.py`.
5. R8 binding: PASS. The answer names nothing new. The rebind mutants (`absent`, span +1, an extra row, `source_id`)
   are run over SR-1's answer (`test_every_structural_mutant_of_the_sr1_answer_is_refused`). A case's own
   `reading_sets` is no input (`test_a_cases_own_reading_sets_member_is_no_input`).
6. Gate evidence matches the final HEAD: PASS by procedure. The branch is synced with main `c0a80d23a`, and the chain
   runs the gate on the final HEAD.
7. No unsigned item: PASS. DELTA rows 1 and 2 are SIGNED by the DRI (decision files cited), and trust is recorded
   under R16 with its FOLLOW-UPS row. Size: see "Size decision".
8. Every user-visible change in DELTA: PASS. Rows 1 (check) and 2 (render). No other answer changes, by proof and by
   `test_sr0_…`.
9. Test selection: PASS. `select_tests.py --base $(git merge-base HEAD main)` selects
   `tests/test_scope_readings_document.py` and the scope tests (see "Selected tests").
10. Lean statements say what is claimed: PASS. Each proved statement is the reviewed stub's text
    (`tests/test_scope_sc5r_stub.py::test_each_statement_sc5rb_proves_is_the_stubs_text`). Three Document seeded
    bugs break the service theorems, and the definitions are verbatim (`::test_the_definitions_are_the_stubs_verbatim`).
11. Budgets and limits fail closed: PASS. More than 64 choices gives `ResourceLimit: scope choices`, proved by
    `governSets_limit` and checked at 65 and 72 (`#guard`s). A limit under a choice passes on unchanged
    (`choiceFault_limit`, SR-lim).
12. No CPU or memory regression: PASS for the part document (the spot check above). The work is bounded:
    `governFast` runs at most 64 times, the limit is checked before any choice is governed, and the product is
    never built over the limit. The B1 benchmark variant is in FOLLOW-UPS.
13. `Test-removed` trailers: PASS. No test was removed or renamed. `tools/gate_collection.py --check --prebuilt`:
    19,855 collected, 15 added, 0 refused, 0 stale, 0 malformed.
