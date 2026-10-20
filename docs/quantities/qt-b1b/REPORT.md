# qt-b1b build report: the Lean core of `scales@0`, second part

No DRI signature is reserved. The one delta is trust S +9, SIGNED by standing ruling R16 (DELTA.md row 1). This item
finishes QT-B1. Next item: **qt-b2** (the `scales` pack, after et-4 in queue 4.2).

Item: feature item qt-b1b (rank 33 of the feature feed, acting DRI dri-featurefeed, 2026-10-18). This is the
model-construction half of QT-B1, split off by qt-b1's builder (`docs/quantities/qt-b1/REPORT.md`, "Next item: qt-b1b").
Plan: `docs/spec/quantities-PLAN.md` QT-B1 and 3.1–3.4. Spec: `docs/spec/quantities.md` 6.2 and 9.5. Both are on main,
unchanged since qt-b1. Branch `feature/qt-b1b` from main b1f7ca7ad.

## Statement gate

QT-0's ten corrections are verified (`manage-agents/quantities-p3ver1.final.md`, PASS). None of them changes a
qt-b1b statement: A3 and A2 touch qt-b1's statements and fixtures, and A4 belongs to QT-B2. Spec change C12 (no
`envScales`) is applied, so `scales_conservative` and `grade_open` read `E` itself, as in spec 6.2.
DRI-DECISIONS-PHASE2 QT1–QT3 change nothing here. Under SYNTHESIS 2.3 and 4.2 the item touches no shared hand-written file.

I compared each built declaration with spec 6.1–6.2 after whitespace normalisation, using qt-b1's script
(`uv run python docs/quantities/qt-b1/evidence/statements-diff.py.txt .`, output in `evidence/statements.json`): **21
exact**. All five new statements are exact: `Fresh`, `StrictLinear`, `intended_iff_degrees`, `scales_conservative` and
`grade_open`. `WellFormed` differs as qt-b1 documented (core's `Nodup` and `Except.isOk`), and `okB` stays replaced.
No statement had to change.

## Plan rows

| Row (qt-b1's "Next item", QT-B1) | Delivered | Where |
|---|---|---|
| `Degrees.lean`: `StrictLinear`, `intended_iff_degrees` | yes. The degrees are the classes of "as much as" over the sort, with every object outside the sort in one lowest class (`Quotient`, a classical case split), as spec 6.2's note says | 14514f13a |
| 9.5's degree-map counts | yes. Two levels: exactly (1, 1, 0) into two degrees, and 3 maps into three degrees. Three levels: 1. "As much as" not transitive: 0 of the 27 maps (and irreflexivity broken: 0). The `degreeMaps` `#guard`s are in `Examples.lean`, next to the trust models they read (FB3), not in `Degrees.lean`: they are fixtures (T) | 14514f13a |
| `Fresh` with `scales_conservative` | yes. `Fresh` is in `Intended.lean`, as the plan's file list says | 14514f13a |
| `grade_open` | yes | 14514f13a |
| the two model constructions | `reread D S grade`: the block's symbols reread by their roles, every other predicate as in `S`, so fresh formulas mean the same (`reread_denote`). `point`: the one-object structure; `reread D point True` and `reread D point False` are `grade_open`'s two models. Both satisfy the premises through `premises_iff_intended` (`reread_intended`) | 14514f13a |
| one role per predicate, from `WellFormed`'s symbol conjunct | `more_ne_same`: no comparative is an equative, in one dimension or across two. This is the only role fact the constructions need. Graded words are unary and the other symbols binary, so the reread reads them on different argument lists, and signatures settle the sorts. qt-b1's role-pair `#guard`s stay unchanged | 14514f13a |
| FB6 (u0165.s05) | `share_of_humanity_targeted` on `attempt`, grade `vast_majority` (upper, an open term). Over one attempt, 2 of the 4 models satisfy the premises: one with the grade, one without (`#guard`). `fb6_open` is `grade_open`'s two witnesses | 14514f13a |
| 9.5's `scales_conservative` rows | `conservative_true`: "r1 is flagged" follows from {r1 is flagged} with the FB1 block and without it. `conservative_false`: "r1 is reviewed" follows from neither, because `flaggedOnly` satisfies {r1 is flagged} and the premises but not φ. The rows go through the theorem in both directions | 14514f13a |
| `lean/SCALES.md` in plain words | yes: the files, the four new theorems, the two constructions, the new fixtures | 897d3e312 |
| seeded bugs for each new definition; R16 row | `mutants.json` (12/12 killed); DELTA row 1 | 897d3e312, 09160dfae |
| `python3 lean/audit.py`, `tools/regen_generated.py --check` | PASS (592 files, 6703 theorems); 31 entries checked (`--skip route-cases`: no route changed, and that entry needs the Rust binary) | 09160dfae |

Not changed: `WellFormed`'s full equivalence to the approved text is still argued in `lean/SCALES.md`, not proved
(qt-b1 review F4, a C item). This item proves the one consequence the constructions use.

## Seeded bugs (Lean, the only language whose product code changed)

All 12 are in `docs/quantities/qt-b1b/mutants.json`. They were run with `uv run python tools/mutants.py
docs/quantities/qt-b1b/mutants.json --no-baseline --evidence docs/quantities/qt-b1b/evidence/mutants-run.json`:
**12/12 killed**. Each run's output tail shows the first `error:` lines.

| Behaviour or definition | Mutant (file) | Stops at |
|---|---|---|
| `Fresh` (trusted, S) | Fresh-comparatives-only, Fresh-first-predicate-skipped (`Intended.lean`) | `reread_denote`'s atom cases (`scales_conservative`'s proof) |
| `StrictLinear` (trusted, S) | StrictLinear-connex-vacuous, StrictLinear-irrefl-vacuous (`Degrees.lean`) | `intended_iff_degrees`, both directions |
| degrees: the classes and their order | Degrees-outside-highest (`Degrees.lean`) | `below_of` (the order is not well defined on the classes) |
| one role per predicate | OneRole-symbol-conjunct-dropped (`Premises.lean`) | `more_ne_same` |
| conservative: the reread structure | Reread-comparative-as-equative, Reread-keeps-fresh-only (`Theorems.lean`) | `reread_rel2`, `reread_rel1`, `reread_admissible` |
| no threshold (`grade_open`) | Point-empty-sorts (`Theorems.lean`); Threshold and Threshold-guard (`Premises.lean`: every object given each graded word) | `grade_open`; `dim_iff`; guard level: FB6's `#guard` (two models become one) |
| conservative, at fixture level | NotConservative-guard (`Premises.lean`: the irreflexivity premise also says every response is reviewed) | guard level: every fixture whose models lack `reviewed`, among them the `scales_conservative` row's `#guard` and `conservative_false` |

The two `-guard` mutants rebuild only `VE.Scales.Premises` and elaborate `Examples.lean` against the Theorems olean
that is already built. So a fixture, not a proof, must stop them. `tools/trust_map.py` lists two new trusted
definitions, `Fresh` and `StrictLinear`, and each has two killed mutants.

## Trust

`uv run python tools/trust_map.py --check`: PASS. Against b1f7ca7ad: **K +0, S +9, V +0** (`Degrees.lean` +6
StrictLinear, `Intended.lean` +3 Fresh). The allowance is recorded with `--allow` and signed "SIGNED by standing ruling
R16 (DRI-RULINGS.md), qt-b1b, 2026-10-18". R16's conditions:
- at most 150 lines, none in K;
- every trusted definition is stated about by a theorem (`tests/test_scales_exercised.py`, 4 passed, including the new
  `test_fresh_is_stated_about_by_scales_conservative`);
- every trusted definition carries killed mutants (above);
- the FOLLOW-UPS row "## qt-b1b" is in `manage-agents/FOLLOW-UPS.md` (copy: `evidence/follow-ups-row.md`).

Classified as proof helpers (P): `reread`, `point`, `asMuch`, `below`, `degreeSetoid`. The new fixtures are T.

## Tests

- `lake build` (1046 jobs) and `python3 lean/audit.py`: PASS. No warnings in the changed files (`lake env lean`).
- Selected tests on the Mac runner (`mac-pytest.sh --select`, HEAD 897d3e31, clean): exit 0, 0 failed, 397 units, 2215 s.
- `tests/test_scales_exercised.py`: 4 passed.
- `tools/gate_collection.py --check --prebuilt`: 1 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- `tools/check_lean_imports.py`: kept.
- `tools/regen_generated.py --check --skip route-cases`: 31 entries.
- Not run here: the full gate (the chain runs it on the final HEAD). No test in `main-known-red.txt` is touched.

## Size

At the midpoint I measured 420 lines (Lean only), so the item was not cut. Final hand-written lines:

| Part | Lines |
|---|---|
| Lean product | 349 (`Theorems.lean` 186, `Degrees.lean` 157, `Intended.lean` 6) |
| Fixtures (`Examples.lean`) | 72 |
| `lean/SCALES.md` | 41 |
| `tests/test_scales_exercised.py` | 24 |
| `tools/trust-classes.json` | 29 |
| `mutants.json` | 18 |
| DELTA, FOLLOW-UPS row and this report | the rest |

That is about 533 before the documents. Not counted: generated files, tool output (`evidence/mutants-run.json`,
`evidence/statements.json`) and `docs/trust-baseline.json` (written by `--allow`).

## Overlap

Hand-written files touched: `lean/VE/Scales/{Intended,Theorems,Degrees,Examples}.lean`, `lean/SCALES.md`,
`tests/test_scales_exercised.py` and `tools/trust-classes.json` (one block per file). I checked every branch in flight
(`git branch --list 'lean-first/*' 'feature/*' 'infra/*' 'foundation/*'`): none touches `lean/VE/Scales`, `SCALES.md`
or the test. `lean/VE.lean` is not changed, because `VE.Scales.Examples` imports `Degrees`.

## Pilot bytes

Expected: 0. No route reads these files. These theorems are what qt-b2 (the `scales` pack) and the UDHR comparison
(163 B, u094) rely on. Nothing is claimed before a pilot audit.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no route or relay reads these files.
2. Deliverables: PASS. The plan-row table above gives a commit for each row. Diff grep: no Python copy of a Lean
   decision, no report test, no authority switch, no file shared with an in-flight branch.
3. Tests can fail: PASS. `mutants.json` 12/12 killed (`evidence/mutants-run.json`), including the guard-level FB6 and
   conservative-row kills; `tests/test_scales_exercised.py::test_fresh_is_stated_about_by_scales_conservative`.
4. Python, Lean and Rust agree: N.A., a Lean-only core with no other implementation.
5. R8 binding: N.A., no relayed answer.
6. Gate evidence: PASS. Branched from current main b1f7ca7ad; commit list from `main..HEAD --no-merges`; the chain
   gates the final HEAD.
7. No unsigned item: PASS. DELTA row 1 cites R16 with its evidence.
8. Every user-visible change in DELTA: PASS. The only delta is the trust budget (DELTA.md).
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects 397/457 units, including
   `lake build`, `lean/audit.py` and `tests/test_scales_exercised.py`; the Lean build is where every mutant fails.
10. Lean statements say what is claimed: PASS. `evidence/statements.json` (21 exact, the five new ones among them). The
    StrictLinear and Fresh mutants break `intended_iff_degrees` and `scales_conservative`.
11. Budgets fail closed: N.A., no public operation or budget.
12. CPU or memory: N.A., no route. The new fixtures enumerate at most 27 maps and 4 models, and `Examples.lean`
    elaborates in a few seconds.
13. `Test-removed` trailers: PASS, nothing removed. `tools/gate_collection.py --check --prebuilt`: 0 removed, 0 refused,
    0 stale, 0 malformed.

Commits (`main..HEAD --no-merges`): 14514f13a, 09160dfae, 897d3e312, and the commit with this report.
