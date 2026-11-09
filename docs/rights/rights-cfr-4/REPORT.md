# rights-cfr-4 report: a right whose act is a declared open term is OPEN

Status: built; final checks in "Checks run". HEAD: the branch head this file is committed in.
Changed: `nodeOpen` (lean/VE/Rights/Run.lean) now reads the act through `opensIn`, and `nodeOpen_eq` is restated and
proved. A unit whose act is a declared open term is now OPEN (spec 7.2).
Open items: none. Signatures: none needed. The CHECKED -> OPEN row is signed ahead (lp0801 item 1), and the trust
growth falls under R16.

Item rights-cfr-4 (DRI 2026-11-09; reviews/dri-decisions-20261109-lp0801.md item 1; regrade #5 in
reviews/l1-c-regrade-rights-20261109.md). The plan is docs/spec/rights.md 7.2 and 7.3 on main. Base: merge base
268829b1a. No signature is reserved.

## Defect

`VE.Rights.Run.nodeOpen` read the default mode, the switches, the guard and the carve-outs, but not the act
`N.pred`. So a specified strict right whose act predicate is a declared open term was CHECKED. Spec 7.2 says it is
OPEN ("an open standard in a guard, act, limitation or condition"). lean/VE/Service/Document.lean does not compute
the status itself. `rightsDoc` (`opens`) stores `Rights.Run.unitOpen` per rights source unit, and the unit loop turns
CHECKED into OPEN from that table. So Document.lean is unchanged.

## Plan rows delivered

| Deliverable | Delivered |
|---|---|
| (1) `nodeOpen` reads the act through the same `VE.Judgments.opensIn` scan | Yes. The scan reads `.unary N.pred (.var 0) :: N.guard :: N.carveOuts`; only the atom's name is read. The other places spec 7.2 lists are already read, and existing tests show it:
- Guard: `nodeOpen`, and a line's own guard through `nodeOf`'s `ownGuard` (tests/test_rights.py::test_holder_guard_opens_correlated_incident; `#guard` OpenActExamples.lean:34).
- Limitation and condition: a line's limitation pack is in its carve-outs (`nodeOf`'s `limPackList`), `unitOpen` makes a line with any `scopeLimits` OPEN, and a `limitation` unit, with its conditions, is always OPEN (tests/test_rights.py::test_generated_condition_opens_unscoped_right_and_accepts_open_meaning, ::test_generated_limitation_names_open_outside_norms). |
| (2) `nodeOpen_eq` restated to the new body and proved; docstring honest | Yes. It adds the disjunct `openNames.contains N.pred`, proved by `simp` from `opensIn_isEmpty`. The docstring says the theorem is no longer byte-neutral for open acts. |
| (3) condition test, fails on main first | tests/test_rights_open_act_is_open.py::test_rights_open_act_is_open, through `ve document check` (`ve.__main__.main`) on a two-unit part document and through the service (`rights-elaborate`'s `unit_open`, relayed by `RightsDocument`, and the per-unit statuses of Lean's `document` answer). It also includes a two-rights fixture, a norm-unit case and the controls. |
| (4) fixtures that move CHECKED -> OPEN listed | None move (see below). |

The status of judgment-terms' `Content.rule` (lean/VE/Judgments/Status.lean) also reads only the guard and the
carve-outs, as judgment-terms spec 3 states. It is outside this item's spec and files. A rights unit under
`judgments@0` should still get the rights overlay, because Document.lean's `unit_open` step (lean/VE/Service/Document.lean,
the `R.opens.lookup` step after `Judgments.status`) runs on every unit. This is read from the code; UNVERIFIED by a
test in this item.

## The condition test fails on main

Run on main's `lean/VE/Rights/Run.lean` (the rest of the branch unchanged), `lake build ve_service`, then
`uv run pytest -q tests/test_rights_open_act_is_open.py` (the norm-unit test was added after this run, so this run does
not include it):

```text
FAILED tests/test_rights_open_act_is_open.py::test_rights_open_act_is_open - ...
FAILED tests/test_rights_open_act_is_open.py::test_rights_open_act_reads_each_rights_own_act
2 failed, 1 passed in 0.66s
E       AssertionError: assert {'CHECKED': 8, 'LABELLED': 17} == {'OPEN': 8, 'LABELLED': 17}
E           assert {'u1': 'CHECK...2': 'CHECKED'} == {'u1': 'OPEN'...2': 'CHECKED'}
```

On the branch all 4 tests pass.

## Fixtures that move CHECKED -> OPEN

None. Only a unit whose act predicate is a declared open term can move (DELTA.md, "Who can move": a generated name
can never be an authored act).

- `uv run python docs/rights/rights-cfr-4/scan_open_acts.py tests conformance usecases docs examples experiments`
  scans every rights@0 document file with declared `open_terms` and prints:

  ```text
  docs with rights@0 and open_terms: 2
    usecases/question-answering/udhr-part07.ve.md
    usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md
  units whose act is a declared open term: 0
  ```

  Fixtures written inline in Python (tests/test_rights.py, tests/test_b16e_rights_document.py,
  tests/test_judgments_*.py) are not scanned. The selected test run below covers them.
- The UDHR fixtures of lean/VE/Judgments/ChainExamples.lean declare `general_welfare`, `just_requirements`,
  `morality` and `public_order`. These are limitation predicates, not acts, and their `#guard`s still pass in the
  full build.
- The selected tests (below) found no other status change.

## Seeded bugs (Lean; Python and Rust product code unchanged)

All are in lean/VE/Rights/Run.lean, and each was restored after its run. Where the mutant breaks `nodeOpen_eq`, the
proof was cut to `sorry` so the service could be built. The pytest runs use the rebuilt `ve_service`, pinned only for
that run. Details are in [mutants.json](mutants.json).

| # | Behaviour | Mutation | Fails |
|---|---|---|---|
| m1 | the act scan (the condition) | the act removed from the scan: `(N.guard :: N.carveOuts)` | test_rights_open_act_is_open, test_rights_open_act_reads_each_rights_own_act, test_rights_document_norm_unit_with_open_act_is_open (rerun after that test was added: `3 failed, 1 passed`); `#guard`s OpenActExamples.lean:31, 39, 40; `nodeOpen_eq` (`error: VE/Rights/Run.lean:247:81: unsolved goals`) |
| m2 | each unit reads its own line's act | `unitOpen` reads the act of the first line of the document: `{ nodeOf D line with pred := ((linesOf D).head?.map (·.2.node.pred)).getD "" }` | test_rights_open_act_reads_each_rights_own_act (the two-rights fixture); `#guard`s OpenActExamples.lean:39, 40 |
| m3 | no other rule opens (claims no more) | any open name opens: `.unary (openNames.headD N.pred) (.var 0)` | test_rights_closed_act_stays_checked, test_rights_open_act_reads_each_rights_own_act; `#guard`s OpenActExamples.lean:32, 39, 40; `nodeOpen_eq` (`2 failed, 1 passed`, before the norm-unit test) |
| m4 | the negative direction: no act opens by itself | every rule opens: `true \|\| N.mode == .default \|\| ...` | test_rights_closed_act_stays_checked, test_rights_open_act_reads_each_rights_own_act, test_rights_document_norm_unit_with_open_act_is_open (`3 failed, 1 passed`); `nodeOpen_eq` |

## Trust

`nodeOpen` is the only trusted definition changed; none is added.

- `uv run python tools/trust_map.py --check` on the final code prints "against 268829b1ac9d: K +0, S +0, D +0, G +4,
  tied +0, unclassified +0, trusted +4 / VE/Rights/Run.lean: trusted +4" and "PASS: K, S and untied [V] within
  268829b1ac9d and the allowances introduced since". This is within R16 (at most 150, no K).
- Recorded with `trust_map.py --allow --reason "rights-cfr-4: lean/VE/Rights/Run.lean +4 (G[V]: nodeOpen reads the
  act)" --signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), rights-cfr-4, 2026-10-18"`, which reported
  "allowed V +4". The R16 ties-pass row is in manage-agents FOLLOW-UPS.md under "## rights-cfr-4".
- The fixture helpers of lean/VE/Rights/OpenActExamples.lean (`adult`, `twoRights`, `unitOf`, `opens`) are classed T
  in tools/trust-classes.json. Before that they counted as 17 unclassified lines.
- Trust mutants: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/rights/rights-cfr-4/trust-mutants.json
  --test lean/VE/Rights/OpenActExamples.lean`.
  - The first run gave 8 KILLED and 8 SURVIVOR. The two real gaps were the default mode alone (`or-and`) and a single
    switch party (`list-drop-last`, `list-drop-first` on `N.alterable`). They are now killed by the `#guard`s at
    OpenActExamples.lean:36-37.
  - Three operators are allowed as equivalent ([trust-mutants-allow.json](trust-mutants-allow.json)). `lit-plus`
    changes `.var 0` to `.var 1`, and the atom's term is never read. `list-first` and `list-last` add `take 1` and
    `reverse.take 1` before `isEmpty`, which does not change the result.
  - Rerun with `--allow ... --rescore`: exit 0, "11 KILLED, 0 SURVIVOR, 0 UNKNOWN, 2 INVALID, 5 ALLOWED, 0 NOT RUN"
    ([trust-mutants.json](trust-mutants.json)).

In-flight branches: `git diff --name-only main...<b>` for every `lean-first/*`, `feature/*`, `infra/*` and
`foundation/*` branch lists none of lean/VE/Rights/Run.lean, lean/VE/Rights/OpenActExamples.lean or
tests/test_rights_open_act_is_open.py (the loop printed only `done`).

## Size

`git diff --numstat $(git merge-base HEAD main)` without the generated files (codemap, declarations, statements,
predicates, checkers.lock, trust-mutants.json) gives about 480 hand-written lines. That is under the 600 cap but over
the task's expected 60-200.
- Product and test code is about 190 lines: Run.lean 11+/4-, OpenActExamples.lean 43, the test file 116, and
  layer_policy, VE.lean and JUDGMENTS.md.
- The rest is evidence and docs: this report, DELTA, mutants.json, scan_open_acts.py and the allow file.

## Pilot bytes expected to move

An estimate only; nothing is claimed before a pilot audit. Expected: 0 bytes in the current pilots. No pilot
document declares an open term that is also a right's act. Future documents that declare an open act move that
unit's bytes from CHECKED to OPEN.

## Checks run

- `lake build VE.Rights.Run`, `lake build VE.Rights.OpenActExamples`, and the full `lake build` after the regen:
  "Build completed successfully (1320 jobs)".
- `python3 lean/audit.py`: "PASS: 790 source files; 8711 named theorem declarations audited ...; only the declared
  standard axiom allowlist".
- `uv run python tools/regen_generated.py --write`: exit 0, "wrote 37 entries". `lean/VE.lean` (lean-roots, which
  has no writer) got the new import by hand.
- `uv run python tools/check_lean_imports.py`: "Lean layer graph kept". `uv run python tools/assurance_manifest.py
  --check`: rc 0.
- `uv run python tools/gate_collection.py --check --prebuilt`: "4 added, 0 removed by a trailer, 0 refused, 0 stale
  and 0 malformed trailers".
- `uv run pytest -q tests/test_rights_open_act_is_open.py`: 4 passed.
- Selected tests, `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base 268829b1a --run`, 450/557 units, on
  ve-cloud-3:
  - The first run stopped at the import lint: "new outward Lean import: VE.Rights.OpenActExamples -> VE.Rights.Run".
    Fixed in tools/layer_policy.py: a runner-boundary fixture is layer 4, as for `VE.Scope.RunExamples`.
  - The second run gave "1 failed" of 450 units: tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified,
    because the new file builds JSON. Fixed with an `other_json` reason in ve/assurance-manifest.json. That id alone
    was rerun with `zsh mac-pytest.sh -- <id>`: "1 passed". It is not in main-known-red.txt.
- Not run: the full gate (the chain runs it on the final HEAD) and pilot timings. There are no whole-UDHR runs (L70).
  The extra cost is one atom per rule scanned, and no step-count test was added.

## Spec re-read

- spec re-read: "one with an open standard in a guard, act, limitation or condition is OPEN" against
  docs/spec/rights.md:759-760. Act: `nodeOpen` (this item). Guard: `nodeOpen` and `ownGuard`. Limitation and
  condition: the carve-outs (`limPackList`), `scopeLimits` and `limitation` units in `unitOpen`.
- spec re-read: "A right whose active lines are strict rules over declared vocabulary with no open term is CHECKED"
  against docs/spec/rights.md:758-759. The negative test is test_rights_closed_act_stays_checked, with no open term
  and with an open term the right does not read.
- spec re-read: "No new status" against docs/spec/rights.md:761. Only CHECKED -> OPEN, and no new value.
- spec re-read: the 7.3 status texts against docs/spec/rights.md:763-776. Unchanged: this item touches no status
  text; `unit_open` is a Boolean per unit.
- spec re-read: the DELTA row against reviews/dri-decisions-20261109-lp0801.md:21 ("rights-cfr-4: CHECKED to OPEN,
  only for units whose act is a declared open term"). For "Who can move", see DELTA.md.
- spec re-read: judgment-terms spec 3 (docs/spec/judgment-terms.md:256-273) shows the pre-change `nodeOpen` body and
  calls `nodeOpen_eq` byte-neutral. That is a deviation by this item, under the DRI's task (deliverable 2). The
  approved spec is not edited; lean/JUDGMENTS.md is updated.

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 0 A, 5 B, 8 C; fixed 12. All 5 B are fixed. 7 of the 8 C are fixed. The `judgments@0` claim is marked
UNVERIFIED rather than tested.

1. PASS. No new relayed field: `unit_open` was already typed and bound. tests/test_b16e_rights_document.py (selected,
   passed) keeps its fuzz of the rights answers.
2. PASS. Deliverables 1-4 are in the table above, with their tests. Grep of the diff: no Python copy of a Lean
   decision, no report test, no file shared with an in-flight branch.
3. PASS. 4 seeded bugs, all Lean (mutants.json). Trust mutants exit 0 (trust-mutants.json).
4. PASS. Base and HEAD were run on the new fixtures: the main-run output above shows 2 failed on main, and all pass on
   HEAD. The corpus scan found 0 units that can move.
5. N.A. No new field is read from a Lean answer.
6. PASS. Tests ran on the committed HEAD. The gate is the chain's.
7. PASS. DELTA row 1 is SIGNED by the DRI (lp0801 item 1), with the condition and negative tests. Row 2 is R16.
8. PASS. DELTA rows 1-2. No fixture moved: scan_open_acts.py and the selected run.
9. PASS. `tools/select_tests.py --base 268829b1a` selects tests/test_rights_open_act_is_open.py (450/557 units).
10. PASS. `nodeOpen_eq` is about the returned `nodeOpen`. Seeded m1, m3 and m4 break its proof ("unsolved goals").
11. N.A. No budget, limit or deadline changes.
12. N.A. One more atom per rule in an existing scan. Not timed (see "Not run").
13. PASS. No test removed (gate_collection: 0 removed).
14. PASS. Both directions: test_rights_open_act_is_open and test_rights_closed_act_stays_checked; the commands are
    cited above; see "Spec re-read".
15. PASS. Overclaim grep done: the "Who can move" claim cites Correlate.lean:372 and Soften.lean:620, and the
    `judgments@0` overlay claim is marked UNVERIFIED. No cut. Every new `#guard` can fail (m1-m3 and trust mutants).
    Limits: N.A.

## Next item

rights-cfr-2 (same file, lean/VE/Rights/Run.lean).
