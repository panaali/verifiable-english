# qt-a2 build report: rounding and percent-of for `cardinality@0` (plan QT-A2, spec 3.8)

No DRI signature is reserved. The one DELTA row (trust S +35) cites R16. Size is over the ~600-line guide, at 877
hand-written lines added (36 changed); see "Size". With qt-a1 and qt-a1b, `erase_iff` and `cardinality_elab_sound` now cover every
constructor of spec 3.2.

Item: feature item qt-a2 (rank 20, acting DRI dri-featurefeed, 2026-10-18), branch `feature/qt-a2` from main 702ff7429.
The plan and spec on main are unchanged since cf73592b4.

## Statement gate

QT-0's verdict was FIX with ten corrections, all verified (`manage-agents/quantities-p3ver1.final.md`). The spec
applies its rounding decisions:
- decision d: `tiesUp` and `halfEven` are admitted; `down` and `up` decode and are refused (`admittedRules`);
- decision f: no closed-interval relation;
- C8: `erasedRounding` has a body for all four rules;
- C9: `roundHalfUp` is dropped.

No QT-A2 statement had to change. `evidence/statements.json` reruns qt-a1's statement diff (spec 3.2 to 3.9 against
the Lean files) and finds 71 exact. One declaration is spelled differently: `CTerm.tagOf` writes
`VE.Time.dimensionless` where the spec writes `dl`. `dl` lives in `Regions.lean`, which imports `Syntax.lean`, and is
defined as exactly that constant. Moving it would break qt-a1b's recorded mutant `admitted-tag`. Five declarations are
not built; they belong to qt-a1c. DRI-DECISIONS-PHASE2 QT1–QT3 and ME3 change nothing here. Meaning comes from
`VE.Numbers.RoundsTo` only (one owner, math-evidence).

## Plan rows

| Row (plan QT-A2 / spec 3.8) | Delivered | Where |
|---|---|---|
| New file `Ratio.lean`: `erasedRounding`, `roundsTo_ratio_agree` (all four rules) | yes, statements as spec 3.8 | `Ratio.lean`; also `roundingQ`, `roundingQ_iff`, `roundingQ_admitted` |
| Erasure cases of `roundsTo`, `percentOf`, `percentRoundsTo` | yes (spec 3.5's bodies) | the three `CFormula.erase` cases are in `Erase.lean`, because Lean needs one recursive function; their linear forms (`roundingQ`) are in `Ratio.lean` |
| The ratio constructors, `CTerm`, admission, meaning (spec 3.2–3.4, on main only as text) | yes | `Syntax.lean`, `Semantics.lean`, `Regions.lean` (`countBodies`) |
| `erase_iff`, `cardinality_elab_sound` (and `erasedProblem_admitted`) extended to them | yes, statements unchanged | `Theorems.lean`: `cterm_erase`, `cterm_typed`, `tdenote_withRegions`, `roundsTo_holds_iff`, `percentOf_holds_iff`, `percentRoundsTo_holds_iff` |
| `roundHalfUp` only as a helper, if it stays | not defined (spec C9) | — |
| FA4 (paper; 0.296/0.297, 52, 31, 21 of 243; "0.3" vs "0.30") | yes | `Examples.lean:269–271` |
| Tie fixture, one per rule (1/8 to 0.13/0.12; 1/2 and 3/2) | yes | `:273–276` |
| FA4c, FA4d (counts as operands; the two readings of "out of") | yes; FA4c's erased problem is admitted (5 formulas) | `:288–314` |
| FA4e (−1/2, ratio and percent) | yes | `:278–280` |
| FA5 (1.028 under both rules, 103 % rounded and exact, 102.7778 %) | yes | `:316–336` |
| FA5b (exactly 105 percent against 5 percentage points at 370, 378, 860) | yes | `:337–338` |
| "About 103 percent" refused | English, QT-A6 (spec 7.3); no `CFormula` has "about" | — |
| FA9e (admission of ratios: rules, dates, tags) | yes | `:339–345`, `admitted_ratio_cases` |
| Seeded bug: upper bound erased with `≤`, the `tiesUp` tie fixture fails | yes | below |

A grid also checks meaning against erasure: every rule, a ratio, a rounded percentage and an exact percentage, with
a from −3 to 3, b from 0 to 3, D from −4 to 4, and k of 0 or 1 (`:282`). The oracle `holdsFin` decides
`VE.Numbers.RoundsTo` directly; the erased side evaluates `roundingQ` on the finite model.

## Seeded bugs (Lean only; `uv run python tools/mutants.py docs/quantities/qt-a2/mutants.json --no-baseline`)

36 mutants, 36 killed (`evidence/mutants-run.json`, rerun on the final product code). Each command is
`lake build VE.Cardinality.Examples`. The table names where each build fails first.

| Mutants (file) | Fail at |
|---|---|
| **plan-tiesUp-upper-le** (`Ratio.lean`, `roundingQ` tiesUp upper `.lt` → `.le`) | `roundingQ_iff`. With that proof stubbed, the build reaches the fixtures and fails the tiesUp tie `#guard` (1/8 to 0.12 becomes true, `Examples.lean:273`), FA4e (`:279`) and the grid (`:282`); see `evidence/plan-seeded-guard.txt` |
| erasedRounding-tiesUp-upper-le, -halfEven-parity, -down-lower, -up-upper (`Ratio.lean`) | `roundsTo_ratio_agree` |
| roundingQ-halfEven-parity (`Ratio.lean`) | `roundingQ_iff` |
| S-rules-down, S-rules-no-halfEven (`admittedRules`) | the FA4, FA5 and FA9e `#guard`s (`:269`, `:335`, `:343`), `admittedRules_cases`, `admitted_ratio_cases` |
| S-cterm-no-count (`CTerm` without `count`) | every use of the constructor; `CTerm` is a data type, and this is its only mutant |
| S-ctermTyped-count-finite, -count-body, -quantity-tag (`CTermTyped`); C-tagOf-count-body | `tagOf_iff` |
| S-admitted-roundsTo-rule, -day, -den, -percentOf-whole, -percentOf-day, -percentRoundsTo-rule (`Admitted`) | `admits_iff` |
| C-ratioTyped-day | `ratioTyped_iff` |
| M-denotes-count, M-denotes-quantity (`CTerm.Denotes`) | `cterm_erase` |
| M-roundsTo-positive, -swap, -rule, -places; M-percentOf-scale, -positive; M-percentRoundsTo-100, -rule (`CFormula.holds`) | `roundsTo_holds_iff`, `percentOf_holds_iff`, `percentRoundsTo_holds_iff` |
| E-roundsTo-positive, E-roundsTo-tag, E-percentOf-scale, E-percentRoundsTo-100, E-cterm-count (`Erase.lean`); G-countBodies-den (`Regions.lean`) | `erase_iff_of`, `erase_admitted` or `cterm_erase` |

R16's rule of a mutant in each new trusted definition is met: `CTerm`, `CTermTyped`, `admittedRules` and
`CTerm.Denotes`, plus each ratio case of `CFormula`, `Admitted` and `CFormula.holds`. Python and Rust: no product code
changed. `tools/trust-classes.json` and `docs/trust-baseline.json` are data tables.

## Trust

`uv run python tools/trust_map.py --check` on the final tree against 702ff7429 gives **K +0, S +35, D +0, G +0, V +0,
unclassified +0** and PASSes with the allowance. The growth:
- `Syntax.lean` +25: CTerm 6, CTermTyped 6, admittedRules 3, CFormula +4, Admitted +6;
- `Semantics.lean` +10: CTerm.Denotes 5, CFormula.holds +5.

The allowance is signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), qt-a2, 2026-10-18". The FOLLOW-UPS row is
"## qt-a2 (2026-10-19)" (`evidence/follow-ups-row.md`). `tests/test_cardinality_exercised.py` passes: no trusted
definition is left out of every theorem statement. `python3 lean/audit.py`: PASS (571 files, 6512 theorems, standard
axioms only).

## Pilot bytes

This item moves 0 bytes on the pilots: no route changes. Once QT-A3 puts erasure on a route, rounding and percentage
claims become checkable: VE's paper (FA4) and the news fixtures (FA5). Unmeasured; these are estimates, and nothing
is claimed before a pilot audit.

## Size

Hand-written lines (`git diff --numstat` against the merge base, generated inventories and run outputs excluded):

| File | Lines |
|---|---|
| Lean product files | +345 −23 |
| `Examples.lean` | +183 −2 |
| `mutants.json` | 78 |
| `trust-classes.json` | +59 −5 |
| `CARDINALITY.md` | +23 −6 |
| `trust-baseline.json` | 7 |
| follow-ups row | 8 |
| DELTA and this report | +174 |

The total is 877 lines added and 36 changed. The size was measured at 344 lines once the core proofs worked, before the fixtures.
The rest could not be cut into a qt-a2b without leaving this item incoherent:
- The case theorems are R16's condition for the S lines, so they must ship with the constructors.
- The tie fixture is the plan's seeded bug.
- The plan names the other fixtures as this item's deliverables. They take about 95 lines, about 60 of them for
  FA4c/d and FA5/5b.

Padding was removed: `mutants.json` uses one mutant per two lines.

## Next item

qt-a3: the wire and the service mode `cardinality`, after ar-10a. qt-a1c (spec 3.7's agreement theorems and 3.9's
`refutesC_sound`) is still open and independent of this item.

## Overlap with branches in flight

Touched by hand: `lean/VE/Cardinality/*` and `lean/CARDINALITY.md`, which no other branch touches; `tools/trust-classes.json`,
a module-keyed ledger with the `ve-generated` merge driver, which `feature/et-7b`, `foundation/me-1` and `lean-first/b18`
also touch, in other modules; `docs/trust-baseline.json`, whose allowances merge through the same driver; and
`docs/quantities/qt-a2/*`.

## Tests

- Selected tests on the Mac runner (`mac-pytest.sh --select -- --base 702ff7429 --run`): 67 units, 0 failed, exit 0,
  on HEAD 64571cab and again on c0e81908, where all code is final; only this report changes after it. These include `lake build`, `lean/audit.py`, `test_cardinality_exercised.py`,
  `test_trust_budget.py` and `test_frozen_sources.py`.
- `regen_generated.py --write --skip route-cases`, then `--only lean-statements` and `--only lean-audit-manifests`
  after the last Lean edit. `route-cases` needs the Rust binary, and no route case changed. Statements: additions only.
- Main-known-red tests: none selected. The full gate is the chain's, on the final HEAD.

## Acceptance items

All AGENT.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no mode, relay or schema.
2. Deliverables built, no rule broken: PASS, "Plan rows" (each row with its place). No Python copy and no report test;
   overlap checked.
3. Tests can fail: PASS, 36 mutants killed (`evidence/mutants-run.json`). The plan's seeded bug fails the tie `#guard`
   (`evidence/plan-seeded-guard.txt`).
4. Python, Lean, Rust agree: N.A., Lean only. Inside Lean, meaning (`holdsFin` over `RoundsTo`) and erasure agree on
   the grid and on every fixture.
5. R8 binding: N.A., no relay.
6. Gate evidence matches the final HEAD: PASS, no gate evidence committed; the chain gates the final HEAD.
7. No unsigned item: PASS, DELTA row 1 cites R16 with its tests; `trust_map.py --check` PASS.
8. User-visible changes in DELTA: PASS, none besides the trust budget (no route reaches the module).
9. Test selection finds the tests: PASS, 67 units selected, including `lake build`, which fails on every mutant.
10. Lean statements say what is claimed: PASS, `evidence/statements.json` (71 exact, 1 spelling, 5 qt-a1c). Each
    mutant breaks the theorem it claims.
11. Budgets and limits fail closed: N.A., no budget or limit added.
12. No CPU or memory regression: PASS, no route changed. Rebuilding `Examples.lean` alone took 39 s on the loaded
    VM (`lake build`). The profiler puts about 24 s of that in FA4c/FA4d's two `#guard`s, which evaluate spec 9.1's
    602-decision model through `countFin` in the interpreter; each (model, claim) pair is evaluated once.
13. Test-removed trailers: N.A., no test removed or renamed.

## Commits

`git log --oneline main..HEAD --no-merges` at the time of writing: f641cf7f2, 93d97aed6, 3571ac592, 707605ba5,
c7032deab, 5309b6d05, 64571cabd, f6b3da1dc, c0e819080, and the commit of this report's last edit.
