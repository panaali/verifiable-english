# sc-5r: scope spec addendum, per choice over a reading set a governed unit owns. Build report

**No DRI signature is reserved; no DELTA (no behaviour changes).** This item is docs and a statement stub only. Its
independent review is the scope statement review for spec section 11; the build, **sc-5rb**, starts after a PASS.
**Size: about 655 hand-written lines, over the ~600 the common rules allow.** The stub holds 360 of them; it is the
only home of the Lean text (the spec cites it, as pk-1s's spec cites its stub). It was not cut, because what remains
is the six fixtures the task requires plus the three fixtures that caught real design faults (below).

- Branch `feature/sc-5r`, worktree `/home/seyran/code/ve-sc-5r`, merge base `4a850162c` (main). Spec and plan on main
  (spec draft 4 = `ab010c3f0`'s text). Read first: the DRI decision (`reviews/dri-decisions-20261027-scope-readings.md`
  item 1), spec 1.1, 1.7, 4.2, 5.1, 5.2, 5.7, 6, 7.1, 7.7, 8.1, 9.4; plan "SC-5" and 8; docs/scope/sc-1b/REPORT.md
  and sc-1ad's (F-raw); the pilot final (finding 1) and its `s03_scope.py` (the set's two readings); lf-14d's
  `VE/Discourse/Joint.lean`; the DRI's fix (a) for F-raw (`reviews/dri-decisions-20261027-featureplan-gates.md`
  item 2).
- Files: `docs/spec/scope.md` (draft 5: new section 11; added lines in the header, change log, 8.1, 9.4 and 10),
  `docs/spec/scope/SpecStubs_sc5r.lean` (the stub), this report, `mutants.json`. Overlap: only `design/scope` (the
  Oct 13 draft-3 design branch, superseded by main's draft 4) touches `docs/spec/scope.md`; no live branch does.
- Statement gate: not applicable in the usual sense. This item is the statement, and the DRI's decision routes it
  to the statement review. No approved statement's text changes. Section 11 restates statements beside the
  originals, and 11.4 says which ones sc-5rb replaces (`scope_admission`) or keeps (`readings_refused`, F-rs).

## Task rows

| Row | Delivered | Where |
|---|---|---|
| (1) which reading sets | yes: `governedSetUnits` | 11.1 |
| (2) the definition, `governAt` or a sibling | the sibling `governChoice D ch := govern (atChoice D ch)`, with `governSets`. Reason: 5.7's `pick` maps a governor id to a reach, and `fixAt` rewrites governors only, so it cannot carry a unit's content | 11.2 |
| (3) the three restated statements, one sentence each | `governSets_no_sets`, `governSets_preserves` + `governSets_every_choice`, `scope_set_choices`; also `governSets_strings`, `governSets_choice_refused`, `faultOf_every`, `choiceFault_limit`, `governSets_limit`, `governSets_readings_refused`, `scope_admission_sets`, `governSetsFast_eq` | 11.3, stub |
| (4) replacing `readings_refused` and F-rs; what stays refused; limits per choice | yes | 11.1, 11.4 |
| (5) diagnostics | `ScopeChoice: <unit> <set>@<v>:<reading>: <fault>`, `ResourceLimit: scope choices`, `ScopeReadings: <unit>: differs between choices …` | 11.5 |
| (6) fixtures, computed | SR-1 (u0165.s03 admitted, both choices), SR-c (one choice conflicts, named), SR-cap (72 refused, 64 checked), SR-u (unrelated set unchanged), SR-0 (no set: `govern`'s answer as a value); also SR-1-pc, SR-1-g2, SR-c-nr, SR-g, F-rs, SR-dep, SR-lim | 11.6, `#guard`s in the stub |
| (7) the build plan for sc-5rb | files, seeded bugs, trust about +114 under R16 (K +0), and the DRI signature its DELTA row needs | 11.7 |
| Stub, type-checked; change-log line | `cd lean && PATH=~/.elan/bin:$PATH lake env lean ../docs/spec/scope/SpecStubs_sc5r.lean`: no error, 12 `sorry` warnings (proofs only), every `#guard` true | stub; change log |

Design faults the fixtures found, all fixed in the spec before commit:
- Lean's `Json` `==` and `compress` are `partial`, so they cannot be used in a proved definition. The agreement check
  uses `VE.Readings.Wire.jeq` (proved sound).
- A fault every choice has, such as a set on the lead-in or a block fault, was at first named with the first choice.
  `faultOf` now reports it in `govern`'s own words (SR-g).
- `checkDoc` hands the chain GOVERN's `units` only (`withUnits`), which would drop the composed readings. 11.4 adds
  `withGoverned` and replaces `scope_admission`.
- The F-raw class in this section's own statements: `governSets_readings_refused` and `governSets_strings` would be
  false on malformed trees (a rebuilt `reading_sets`; a frame part read by traversal). Both take `Pinned.JsonWF`,
  the DRI's fix (a).
- SR-g's first governor-unit fixture never exercised the governor-unit clause (u0164.s02 is not covered). Seeded bug
  1 showed that; a fixture with a carve-out written on u0165.s03 itself now does.

Found, not changed (FOLLOW-UPS "## sc-5r"): `baseName` reads a decoder `ResourceLimit` as "no name", so a `rules`
reach can refuse with `ScopeUnknownRule` where 6.2 says UNKNOWN (spec 11.8 item 2; main's behaviour, approved text).

## Seeded bugs

[mutants.json](mutants.json): 8 seeded bugs, all in the stub's definitions (the only Lean this item writes; no product
code in any language). Each was run on a copy of the final stub, and each failed the `#guard`s listed there:
`governedSetUnits` without the governor-unit test (SR-g); `governedSetUnits` allowing written content (SR-g);
`atChoiceOn` keeping the governed sets (13 guards); `faultOf` always naming a choice (SR-g, F-mm); `choiceFault`
naming a limit (SR-lim); `assemble` without the agreement check (SR-dep); `setChoices` with `≥` (SR-cap at 64);
`readingIn` returning the written reading (SR-1, SR-1-pc, SR-1-g2). The stub itself was not edited.

## Trust, tests, bytes

- Trust: `uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0, trusted +0, PASS. Nothing is under
  `lean/`.
- Tests: the stub check above, and the selected tests
  (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`); see "Selected tests". The full gate is
  the chain's, on the final HEAD.
- Bytes: 0 (estimate) for this item and for sc-5rb. The M13 number (u0164.s02, +22 B) waits for the pilot's rewrite of
  the hard-constraint block.
- Next item: **sc-5rb** (spec 11.7), after this section's PASS. Its four `JsonWF` statements wait for sc-1ae
  (else **sc-5rc**).
- Acceptance: AGENT for the stub, its fixtures and seeded bugs. HUMAN (DRI) for the statement review's verdict and
  for sc-5rb's widening row. EXTERNAL none.

## Selected tests

SELECTED_TESTS_RESULT

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed answer changes (sc-5rb, 11.7 item 6 names its fuzz).
2. Every deliverable built, no rule broken: PASS. Task rows above; grep of the diff shows no Python copy of a Lean
   decision, no report test, and no live overlapping branch (`git diff --name-only main...<b>` over every live branch).
3. Tests can fail: PASS. 8 seeded bugs, each killed by a named `#guard` (`mutants.json`). R16 `trust_mutants`: N.A.,
   trust +0.
4. Python, Lean and Rust agree: N.A., no product code.
5. R8 binding: N.A., no relay changes (sc-5rb, 11.7 item 7).
6. Gate evidence matches the final HEAD: PASS by procedure. The chain runs the gate on the final HEAD; no evidence
   file is derived from it here.
7. No unsigned item: PASS. There is no DELTA row and no trust growth. The signature sc-5rb will need is named in
   spec 11.7.
8. Every user-visible change in DELTA: N.A., none (docs only).
9. Test selection: PASS. `select_tests.py --base $(git merge-base HEAD main)` ran (above). A docs-only diff has no
   product test to seed.
10. Lean statements say what is claimed: PASS for a statement stub. The `#guard`s compute every 11.6 value on the
    definitions as stated. The added hypothesis `Pinned.JsonWF` is the DRI's ruling (featureplan-gates item 2), with
    F-raw as its mechanised counterexample (`lean/VE/Scope/Examples.lean`).
11. Budgets and limits fail closed: PASS. SR-cap (72 refused with `ResourceLimit`, 64 checked) and SR-lim (a limit
    passed on unchanged, at 63 levels deep; admitted at 62) in the stub.
12. No CPU or memory regression: N.A., no product code. sc-5rb runs up to 64 × `governFast`, and 11.7 asks for
    a benchmark row, not a suite timing.
13. `Test-removed` trailers: N.A., no test removed or renamed.
