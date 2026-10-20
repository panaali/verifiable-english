# qt-b1 build report: the Lean core of `scales@0`, first part

No DRI signature is reserved: the one delta (trust S +78) is SIGNED by standing ruling R16 (DELTA.md row 1). The
rest of QT-B1 (the theorems that need a model construction, and `Degrees.lean`) is named as the next item
**qt-b1b** (below), as the feed's size rule asks.

Item: feature item qt-b1 (rank 18 of the feature feed, acting DRI dri-featurefeed, 2026-10-18). Plan:
`docs/spec/quantities-PLAN.md` batch QT-B1 and sections 3.1 to 3.4; spec `docs/spec/quantities.md` 6.1, 6.2, 9.3 to
9.5. Both files are on `main` and identical to `research/quantities-p1` at e3697d8c7 and to main cf73592b4. Branch
`feature/qt-b1` from main aeedb8ad2, synced with main cb033316a (qt-a1 and pk-1 merged) in e3bf6c78d.

## Statement gate

QT-0 is QT-B1's statement review. Its verdict (Astra and Fable, debate `manage-agents/debates/quantities-spec`) was
**FIX** with ten corrections; the correction check `manage-agents/quantities-p3ver1.final.md` is **PASS** ("all ten
agreed corrections … are in both documents and are correct").

| QT-0 correction | Applied in | Touches QT-B1's statements? |
|---|---|---|
| A2: FB2's endpoint premise; the countermodel without it stays a fixture | plan QT-B1 FB2; spec 2.2, 9.3 FB2 | yes: FB2 (`Examples.lean`, counts 3/1 and 1/0 without it, 1/0 with it) |
| A3: `WellFormed` rejects duplicate premise labels; `scalePremises_labels_nodup` | plan QT-B1 (`WellFormed`'s comment, the theorem, FB8); spec 2.2, 6.1, 6.2, FB8 | yes: `WellFormed`'s label conjunct, `scalePremises_labels_nodup` (proved), FB8's 6/4 and 6/5 label fixtures |
| A4: `scales_conflictFree_iff`'s actual guarantee at `envAt (fill U) 0` | plan 3.4; spec 6.3, FB9, FB10 | no: QT-B2 |
| A1, E1–E5, E6a | track A, English and QT-A3 | no |

Both corrections that touch QT-B1 are applied in the pinned plan and spec; none is missing. Spec change C12
(`envScales` dropped, decision b) is applied: every statement uses `E` itself. DRI-DECISIONS-PHASE2 "Quantities" QT1
(QX-2's forms), QT2 (the premise-scale item) and QT3 (the 0600Z audit finding) change nothing in QT-B1. SYNTHESIS
2.3: QS-1 is on main and used (`gradeOrder` is a `VE.Closure.Order`, its caps `Order.admit`; acyclicity stays
`VE.Route.kahn`); 4.1 puts QT-B1 among the parallel Lean cores; 4.2 gives it no shared hand-written file.

**Built declarations against the approved text** (`evidence/statements.json`, made by `evidence/statements-diff.py.txt`
with the repository's `declarations` reader of `tools/check_readings_defaults_statements.py`): **16 exact**, 1
differing, 6 not built. `WellFormed` differs only by core's `decide (…).Nodup` for the `firstUse` length test and
core's `Except.isOk` for the spec's `okB` (same accepted blocks; `lean/SCALES.md`). Not built: `Fresh`, `okB`,
`StrictLinear`, `scales_conservative`, `grade_open`, `intended_iff_degrees` (qt-b1b; `okB` is replaced). No approved
statement changed: `premises_iff_intended`, `premises_wellTyped`, `scalePremises_labels_nodup`, `Intended` and
`premises` are exact.

## Plan rows

| Plan row (QT-B1) | Delivered | Where |
|---|---|---|
| `Syntax.lean` | yes: `Direction`, `Grade`, `Dimension`, `ScaleDoc`, `symbols`, `rel1`, `rel2` | 1949a0452 |
| `Premises.lean` | yes: `premises`, `scalePremises`, `gradeOrder`, `gradeCaps`, `aboveNodes`, `WellFormed` | 1949a0452 |
| `Intended.lean` | `Intended`; `Fresh` moves to qt-b1b with its only theorem | 1949a0452, 804e4fe54 |
| `Theorems.lean` | `premises_iff_intended`, `premises_wellTyped`, `scalePremises_labels_nodup` proved; **not** `scales_conservative`, `grade_open` (qt-b1b) | 1949a0452 |
| `Degrees.lean` | **not built** (qt-b1b): `StrictLinear`, `intended_iff_degrees` | — |
| `Examples.lean` | FB1 (and its lower twin), FB2 (with its refutation, `fb2_refuted`), FB3, FB4, FB8 (with one role per predicate, position pair by position pair); 9.5's `premises_iff_intended` rows (`trust_intended`, `trust_not_intended`); **not** FB6 (`grade_open`'s witnesses, qt-b1b) | f4bd46d72, 804e4fe54, 18b639851 |
| `lean/SCALES.md` | yes | b8da5c83b |
| Generated (as QT-A1) | `lean/VE.lean` (one import, union list), `VE/Audit.lean`, `axioms.txt`, `statements.txt`, `predicates.txt`, `declarations.txt` by `uv run python tools/regen_generated.py --write --skip route-cases` (no route changed; route-cases needs the Rust binary); trust tables signed | 804e4fe54, 18b639851 |
| "Hand-written shared: none" | none touched (`lean/VE.lean` is the union-merged root list) | — |
| Seeded bug: the lower closure with the comparative reversed; FB1's lower twin's `#guard` fails | yes: `B1-lower-reversed` stops at `dim_iff`; its guard twin stops at the lower twin's `#guard` (0 models becomes 1) | `mutants.json` |
| Bytes: 0 | 0: no route reads the files | — |

FB2's certificate fixture (spec 9.3: the refutation of "a disposition more autonomous than fully autonomous") is
`fb2_refuted`: `Entails disp.environment (endpoint :: between :: premises) (.not aboveTop)`, proved over every
admissible structure from `premises_iff_intended`, so it is stronger than replaying one certificate; spec 8's "not
computable here" was about the stub's opaque `checkCertificate`. FB2's finite counts stay. FB2's endpoint premise must
still be justified from u0226's words by QT-B4 (HUMAN, an audit: spec 9.3).

## Next item: qt-b1b

`lean/VE/Scales/Degrees.lean` (`StrictLinear`, `intended_iff_degrees`, 9.5's degree-map counts), `Fresh` with
`scales_conservative`, `grade_open`, FB6 and 9.5's `scales_conservative` rows, all as spec 6.2 states them. The two
model constructions they need (a structure that interprets the scale symbols, fresh formulas unchanged; a one-object
model for `grade_open`) need one-role-per-predicate from `WellFormed`'s symbol conjunct, which this item checks and
fixtures position pair by position pair of `Dimension.symbols` (the role-pair `#guard`s; a mutant dropping any part
of the conjunct fails them). `WellFormed`'s equivalence to the approved text is argued in `lean/SCALES.md`, not
proved (review F4, a C item); qt-b1b proves the one-role-per-predicate consequence it uses. Then qt-b2 (after pk-1 and et-4, queue 4.2).

## Size

Measured at the midpoint (`git diff --numstat` against the merge base) at **541** lines, all Lean; cut there: the
model-construction theorems and `Degrees.lean` went to qt-b1b. Final hand-written lines: Lean product 339 (Syntax
42, Premises 69, Intended 30, Theorems 198), fixtures 304 (`Examples.lean`, including 36 lines added so each seeded
bug has a fixture that stops it, and 70 for the review's F1 to F3), `lean/SCALES.md` 55,
`tests/test_scales_exercised.py` 43, side tables 112 (`tools/trust-classes.json` 105, the fixtures' T entries written
by hand, as `--seed` needs a TRUST-MAP.md the repository does not carry; `docs/trust-baseline.json` 7, written by
`--allow` and then put in main's order by hand in 5a5e3485e (review F5): it equals main's file plus the `--allow`
entry and passes `--check`), `mutants.json` 70,
evidence script 25, DELTA and this report. Tool output (`evidence/mutants-run.json`, `evidence/statements.json`) and
generated files are not counted. The item is over the ~600 guide by its fixtures, side tables and documents; its
scope did not grow after the cut.

## Overlap

Hand-written files: `lean/VE/Scales/*.lean` and `lean/SCALES.md` (new directory), `tests/test_scales_exercised.py`
(new), `lean/VE.lean` (one import line). Against every branch in flight (`git branch --list 'lean-first/*'
'feature/*' 'infra/*' 'foundation/*'`, 123 branches): none touches `lean/VE/Scales` or `SCALES.md`; `lean/VE.lean` and
`lean/VE/Audit.lean` are also edited by ap-2, pk-1, qt-a1, me-1, b18 and arch-AR-1, and are a union-merged root list
and a generated inventory (R12).

## Seeded bugs (Lean, the only language whose product code changed)

All in `docs/quantities/qt-b1/mutants.json`, run with `uv run python tools/mutants.py docs/quantities/qt-b1/mutants.json
--no-baseline --evidence docs/quantities/qt-b1/evidence/mutants-run.json`: **64/64 killed**. Each claim names where
the build stops. The 17 `-guard` twins rebuild only `Premises` with the bug and elaborate `Examples.lean` over the
built `Theorems`, so a fixture, not a proof, must stop them.

| Behaviour claimed | Mutants (file) | Stops at |
|---|---|---|
| the generated premises mean the intended meaning (`premises_iff_intended`) | B1-lower-reversed (the plan's seeded bug), B1-upper-reversed, B1-irreflexive-dropped, B1-same-left-swapped, B1-above-reversed (`Premises.lean`); I-irrefl … I-aboveImp, 13 fields (`Intended.lean`) | `dim_iff`, `intended_iff_and`; guard twins: FB1's and its lower twin's `#guard`s, FB2's counts, `trust_intended`, the `graveOnly` `#guard` |
| one premise per label (A3) | B1-label-merged, W-labels | FB8's `#guard`, `scalePremises_labels_nodup`; twin: the duplicate-label `#guard` |
| one role per predicate, each part of the conjunct (review F1) | W-symbols-grades, W-symbols-same, W-symbols-more, W-symbols-within (`Premises.lean`), H-dim-symbols-grades, H-dim-symbols-more, H-dim-symbols-one-grade (`Syntax.lean`), W-dims-first | the role-pair `#guard`s, the positions `#guard`, FB8's shared-symbol and predicate-in-two-dimensions `#guard`s, `symbols_cases`, `dim_ok`; twins: the role-pair, FB8 and every-position `#guard`s |
| `WellFormed` refuses each hostile block (FB8) | W-symbols, W-sort, W-more, W-same, W-comparable, W-grade-sig, W-open-term, W-direction, W-caps, W-acyclic | FB8's `#guard`s, or `dim_ok`; twins: the ghost-sort, undeclared-comparative, one-place-equative, two-place-grade and open-term `#guard`s |
| the helpers `WellFormed` reads | H-caps, H-gradeOrder, H-aboveNodes (`Premises.lean`), H-dim-symbols, H-doc-symbols (`Syntax.lean`) | `order_cases`, `symbols_cases`, FB8's `#guard`s |
| the data types | D-direction, D-grade, D-dimension, D-scaledoc (`Syntax.lean`) | `premises`' match; the fixtures' grades; the fixture dimensions' `WellFormed` `#guard`s (name and sort swapped); `ScaleDoc.symbols`. A data type has no cases: three of these four are shape changes that elaboration stops |

Every trusted definition (`tools/trust_map.py` lists 11) has at least one mutant: Direction, Grade, Dimension,
ScaleDoc (D-*), Dimension.symbols, ScaleDoc.symbols (H-*-symbols), gradeOrder, gradeCaps, aboveNodes (H-*),
WellFormed (W-*), Intended (I-*). Two conjuncts of `WellFormed` have no mutant because none can survive alone:
`p.1 != p.2` (kahn refuses a self-loop) and "both ends of an `above` pair are grades" (`Order.admit` refuses a pair
outside the grades); `lean/SCALES.md` says so.

## Trust

`uv run python tools/trust_map.py --check`: PASS, K +0, **S +78**, V +0 against cb033316a (DELTA row 1, per
declaration). Allowance recorded with `--allow` and signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), qt-b1,
2026-10-18". R16's conditions: at most 150 lines, no K; every trusted definition stated about by a theorem
(`tests/test_scales_exercised.py`, and PROBE `trust_map.unexercised(...)` over the five files prints `[]`); every
trusted definition carries a killed mutant (above); FOLLOW-UPS row "## qt-b1" in `manage-agents/FOLLOW-UPS.md` (copy:
`evidence/follow-ups-row.md`).

## Tests

- `lake build` of the new modules (the merge's `regen_generated.py --resolve` builds and checks everything); the
  Examples build takes about 5 s.
- Selected tests on the Mac runner (`mac-pytest.sh --select`, HEAD b8da5c83, clean): 121/441 units, exit 0, 0 failed.
  After the sync with main and these documents (HEAD c2d37e53, clean): exit 0, 0 failed, 1,434 s (the runner
  recorded 359 units for the merged tree).
- `tests/test_scales_exercised.py`: 3 passed. `tools/gate_collection.py --check --prebuilt`: 3 added, 0 removed, 0
  refused, 0 stale, 0 malformed. `tools/regen_generated.py --check --skip route-cases`: 30 entries checked.
- Review fixes (HEAD 11d5bade9 with these documents uncommitted): `lake build` (1016 jobs) and `python3 lean/audit.py`
  PASS; `tools/mutants.py` 64/64 killed (`evidence/mutants-run.json`); PROBE F1 and PROBE F2 fail before the fix and
  pass after it; selected tests on the Mac runner (`mac-pytest.sh --select`): 74 units, exit 0, 0 failed, 990 s;
  `tests/test_scales_exercised.py` 3 passed; `tools/trust_map.py --check` PASS (S +78, K +0, V +0);
  `tools/regen_generated.py --check --only lean-statements` and `--only lean-audit-manifests` PASS after `--write`.
- Not run here: the full gate (the chain runs it on the final HEAD); `route-cases` regeneration (needs the Rust
  binary; no route changed). No test of `main-known-red.txt` is touched.

Commits (`main..HEAD --no-merges` before this report): 1949a0452, f4bd46d72, 804e4fe54, b8da5c83b, 18b639851,
44cd54883, c2d37e531 (DELTA and this report), 5a5e3485e (the trust history's order), 02f0c4285 (this list). Review
fixes: 11d5bade9 (F1 to F3 in Lean, the mutants, the generated inventories and the fixtures' trust classes) and the
commit with the mutant evidence and these documents.

## Review fixes (`manage-agents/qt-b1-review.final.md`)

| Finding | Class | Fix | Regression test |
|---|---|---|---|
| F1 (B): a graded word or an equative shared by two dimensions passed every fixture, so a weakened symbol conjunct survived | a check whose parts no fixture separates: only whole-conjunct mutants were planted | `Examples.lean`'s role-pair `#guard`s: every pair of positions of `Dimension.symbols` of one arity, across two dimensions and within one, refused when shared and accepted when renamed apart; a `#guard` ties the positions to `Dimension.symbols`, so a new symbol field fails it until the table covers it; a `#guard` that each dimension's own conjuncts are checked in every position | the role-pair `#guard`s (`lake build VE.Scales.Examples`); mutants W-symbols-grades and H-dim-symbols-grades (review F1's two) and the 12 others of the class above, 14/14 killed; PROBE F1 passes |
| F2 (B): FB2's refutation not built | a certificate fixture the spec asks for, left to a later batch | `fb2_refuted` (`Entails` over every admissible structure) | `VE.Scales.Examples.fb2_refuted` (built, in `VE/Audit.lean`, `lean/audit.py` PASS); PROBE F2 passes |
| F3 (C) | a fixture helper that answers the passing value on a miss | `bodyAt` is `true` when the label or shape misses | the single-instance `#guard` |
| F4 (C) | — | not changed: `WellFormed`'s equivalence to the approved text stays argued in `lean/SCALES.md`; named in the qt-b1b paragraph | — |
| F5 (C) | — | not changed: the size overrun stays reported (Size); the hand ordering of `docs/trust-baseline.json` is stated in Size | — |

## Pilot bytes

0, as the plan says: no route reads these files. UDHR u094 (FB4) and the constitution's u0043.s01 (FB3) move only
once QT-B2 puts the premises in the `scales` pack and QT-B3 adds the wordings; nothing is claimed before a pilot
audit.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no route or relay reads these files.
2. Deliverables: PASS, the plan-row table above (each row with its commit or the qt-b1b cut); diff grep: no Python
   copy of a Lean decision, no report test, no authority switch.
3. Tests can fail: PASS, `mutants.json` 64/64 killed (`evidence/mutants-run.json`);
   `tests/test_scales_exercised.py::test_a_definition_no_theorem_uses_is_reported`.
4. Python, Lean and Rust agree: N.A., a Lean-only core with no other implementation.
5. R8 binding: N.A., no relayed answer.
6. Gate evidence: PASS, synced with main (e3bf6c78d), commit list from `main..HEAD --no-merges`; the chain gates the
   final HEAD.
7. No unsigned item: PASS, DELTA row 1 cites R16 with its evidence.
8. Every user-visible change in DELTA: PASS, the only delta is the trust budget (DELTA.md).
9. Test selection: PASS, 121/441 units including `tests/test_scales_exercised.py`, `lake build` and `lean/audit.py`,
   which build `VE.Scales.Examples` where every mutant fails.
10. Lean statements say what is claimed: PASS, `evidence/statements.json` (16 exact, `WellFormed` differing as
    documented); the Intended mutants break `premises_iff_intended`'s proof.
11. Budgets fail closed: N.A., no public operation or budget.
12. CPU or memory: N.A., no route; the fixtures enumerate at most 512 models and build in about 5 s.
13. `Test-removed` trailers: PASS, `tools/gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale, 0
    malformed.
