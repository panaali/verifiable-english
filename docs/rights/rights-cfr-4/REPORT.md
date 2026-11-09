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

`nodeOpen` is the only trusted definition changed; none is added. TRUST-NUMBERS-PENDING

In-flight branches: `git diff --name-only main...<b>` for every `lean-first/*`, `feature/*`, `infra/*` and
`foundation/*` branch lists none of lean/VE/Rights/Run.lean, lean/VE/Rights/OpenActExamples.lean or
tests/test_rights_open_act_is_open.py (the loop printed only `done`).

## Size

Hand-written lines: SIZE-PENDING

## Pilot bytes expected to move

An estimate only; nothing is claimed before a pilot audit. Expected: 0 bytes in the current pilots. No pilot
document declares an open term that is also a right's act. Future documents that declare an open act move that
unit's bytes from CHECKED to OPEN.

## Checks run

CHECKS-PENDING

## Next item

rights-cfr-2 (same file, lean/VE/Rights/Run.lean).
