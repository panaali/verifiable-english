# srccov-rl-bluedot-grant-1121: translation omissions of bluedot-grant (REPORT)

Result: **0 of 3 in-scope units KEPT, 3 DROPPED.** No VE file outside this directory changes: there is no new
rule or fact line, no regenerated file, no condition test and no seeded bug. No DRI signature is reserved.
There are no DELTA rows.

## 0. Verify table

The scope is the units of srccov-bluedot-grant-s5-2/-4/-6-1119 that the map tags `none: translation omission`:
S0011 (row -2), S0019 (row -4) and S0059 (row -6) (`part-bluedot-grant-s5.tsv` lines 14, 22, 62). Every other
unit in those rows is out of scope and stays as it is.

| unit id | row id | KEPT / DROPPED | one-line reason with file:line |
|---|---|---|---|
| S0011 (u020) | srccov-bluedot-grant-s5-2-1119 | DROPPED | This is a NEW Milestone 2 plan step (kind `new_text says applicant intends`, `usecases/bluedot-grant/semantic_readings.py:368`). The use case decided that milestone items are plans and are not formalised (`usecases/bluedot-grant/README.md:88-89`, `:102`), and its test forbids a body: "Milestones are plans: never checked" (`tests/test_bluedot_grant.py:312-315`). A body here would delete that check, which only the DRI can decide (DRI-RULINGS "Never covered": deleting a check). It also needs the applicant's intention (attitude content, which waits for srccov-design-attributed-1119) and the milestone's deadline "By 25 October, week 4" (`usecases/bluedot-grant/source.md:19`, which waits for srccov-design-deadline-cadence-1119). |
| S0019 (u033) | srccov-bluedot-grant-s5-4-1119 | DROPPED | "should help ... even if VE provides no advantage" is an expectation that the OLD text attributes to the applicant (kind `old_text says applicant expects`, `usecases/bluedot-grant/semantic_readings.py:383`; source `usecases/bluedot-grant/source.md:32`). That is attitude content ("we expect" is in the scope of srccov-design-attributed-1119, its task file line 6), so it waits for that design. No CHECKED unit of this document has an expectation kind: the "should" case of the modal test has never been met (`tests/test_bluedot_grant.py:437`, `:444` `seen == {"would", "may", "will"}`). |
| S0059 (u081) | srccov-bluedot-grant-s5-6-1119 | DROPPED | This is the PASTE copy of S0011 (kind `paste_text says applicant intends`, `usecases/bluedot-grant/semantic_readings.py:479`; source `usecases/bluedot-grant/source.md:56`). It is dropped for the same three reasons: the milestone check at `tests/test_bluedot_grant.py:312-315` (it covers u078-u082), the intention attitude, and the milestone deadline. |

Checks behind the table (command run in the worktree at `cebf4fd24f`):

- **Source unchanged since the map's pin.** `git diff --stat e53db4e8fc HEAD -- usecases/bluedot-grant/` lists
  only causal.ve.md, document.ve.md and semantic_readings.py (the defs-repair-bluedot-grant-1119 legends).
  source.md is not in the list.
- **Not carried at main.** The probe below loads both carriers with `ve.document.front_matter` and slices
  source.md at the map's offsets. It printed:
  ```
  document.ve.md u020 LABELLED ["attributed", "new_text", "says", ["attributed", "applicant", "intends", "asserted"]] [1609, 1681] False
  document.ve.md u033 LABELLED ["attributed", "old_text", "says", ["attributed", "applicant", "expects", "asserted"]] [2633, 2757] False
  document.ve.md u081 LABELLED ["attributed", "paste_text", "says", ["attributed", "applicant", "intends", "asserted"]] [6585, 6657] False
  causal.ve.md units 4 ['u029', 'u035', 'u047', 'u086']
  1609 1680 test authentic versus forged checker findings under sustained pushback.
  2633 2755 The open benchmark, harness and failure analysis should help other oversight researchers even if VE provides no advantage.
  6585 6656 test authentic versus forged checker findings under sustained pushback.
  ```
  (`False` means the unit has no `content`, so it has no VE body.) The source text matches the map's units
  byte for byte. A grep of the document.ve.md front matter and of causal.ve.md and semantic_readings.py for
  `pushback|forged|authentic|researchers` found no legend. The only `advantage` hit was the unrelated
  constant `cost_advantage`. So no earlier row (srccov-bluedot-grant-1119, defs-repair) carried these units.

**Why "a plain line" does not hold here.** The map's amendment 14 tags a unit `none: translation omission`
whenever a predicate line could carry the clause, with the attitude left in the front-matter kind. In this
document that is not enough:

- **S0011 and S0059.** The kind would still have to sit on a CHECKED milestone unit, and the document's own
  check refuses one.
- **S0019.** Its content is the attitude itself ("should" = expects). This task tells us to drop
  attributed/attitude content until that design lands.

Both choices are the conservative option (no new exposure; the narrower reading). Standing override 2 says
to take that option, so we did not ask the DRI.

## 1. Units carried

None. `usecases/bluedot-grant/` is unchanged.

## 2. Derived files

None regenerated: no source of a derived file changed. conformance/english-lean/corpus-seal.json,
tests/data/fidmech/ and tools/fidmech/manifests.py are untouched (`git diff --stat main...HEAD` lists only this
REPORT).

## 3. Answers touched

None. No unit's status, kind or content changes (probe above). No CHECKED answer or question of bluedot-grant
moves. No sealed, answers/, reports/ or diagnostic file of FSF/RSP/PF was opened.

## 4. Condition test and seeded bug

N.A. Deliverable 4 asks for an assertion per KEPT unit, and none is kept. A test that pinned the three dropped
units as LABELLED would already pass on main, so it could not meet the "fails on main" condition. It would
also stand in the way of the design rows that will carry them, so we did not add one. No product code changed
in any language, so there is no seeded bug to plant (review-ready [mutants]: no changed language).

## Merge commit and freeze

The branch is based on VE main `cebf4fd24f` and adds only this REPORT. Whatever commit it merges at, it
changes no answer, so no later read needs to re-pin for it. The Monday 2026-11-23 FSF freeze does not involve
this item.

SIZE: 0 product, 0 tests, 131 other hand-written lines (this REPORT).

## Tests

- **Selected run.** One run on the committed HEAD `7e1cb3e637`:
  `zsh mac-pytest.sh --select -- --base cebf4fd24f --run`. It ran on ve-cloud-2 and exited 0 in 1469 s. The log
  ends "recorded 267 units for tree 55d6607930; ... 0 failed". The selector left 24 slow, weakly selected
  files to the chain gate.
- **Light lane.** `light-lane.py check` printed "LIGHT 125 changed lines outside generated files <= 150
  (1 files), no trusted-core file", so no trust_mutants sweep was needed.
- **Known red.** No bluedot test is in main-known-red.txt.

## Notes for the DRI

- In this document the map's `none: translation omission` label held for 0 of the 3 units (an upper figure,
  as the task says).
- **Carrying S0019 later, under srccov-design-attributed-1119.** If that design accepts an expectation kind
  on a CHECKED unit (the precedent is the `promised` kind on u032/u042/u093), the carry is:
  - a new predicate and constant whose legends quote "should help other oversight researchers";
  - the reading `even if` = unconditional, as for u042 (`semantic_readings.py:347`);
  - updates to the document's own test at `tests/test_bluedot_grant.py:444` and to its coverage figures at
    `:519`/`:525`. That test is outside this item's path list.
- **Carrying S0011/S0059.** This first needs the DRI to reverse the use case's "milestones are not formalised"
  decision (`README.md:88-89`, `tests/test_bluedot_grant.py:312-315`). It also needs the attributed and
  deadline designs.
- No FOLLOW-UP is filed. Every deliverable is done or vacuous with 0 kept units, and no verdict or binding is
  wrong. The dropped units belong to the existing design rows named above.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relay or Lean change.
2. Every required deliverable built: PASS. Deliverable 0 is the verify table above. Deliverables 1-4 apply per
   KEPT unit and none is kept (section 4 says why there is no test). The REPORT is at the required path.
   Evidence: `git diff --stat main...HEAD`.
3. Tests and gates can fail: N.A., no new check or test (section 4).
4. Python/Lean/Rust agree: N.A., no product code changed.
5. R8 binding: N.A., no relay.
6. Gate evidence matches the final HEAD: PASS. The chain runs the full gate on the final HEAD. The selected run
   below is on the committed HEAD.
7. No unsigned item left: PASS. There are no DELTA rows and no reserved signature (this REPORT).
8. Every user-visible change in DELTA: N.A., no user-visible change (`git diff --stat main...HEAD`).
9. Test selection still finds the tests: N.A., no code or test changed.
10. Lean statements: N.A., no Lean change.
11. Budgets and limits fail closed: N.A., no limit touched.
12. No CPU or memory regression: N.A., no code changed.
13. Test-removed trailer: N.A., no test removed or renamed.
14. Pre-review self-check: PASS. Each claim cites a command (the probe output, `git diff --stat`). Spec
    re-read: the task's VERIFY drop list (attributed/attitude, deadlines) against the task text, and the scope
    of srccov-design-attributed-1119 against `prompts/dri-task-srccov-design-attributed-1119.txt:6`.
15. Four classes: no overclaim PASS ("None"/"no" claims cite the probe and `git diff --stat`). No silent cut
    PASS (nothing cut; the drops are the task's own VERIFY step). Every new check can fail N.A. (no new check).
    Limits charged before work N.A.
