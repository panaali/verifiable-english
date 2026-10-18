# qt-a1 build report: the Lean core of `cardinality@0`, first part

No DRI signature is reserved: the one delta (trust S +137) is SIGNED by standing ruling R16 (DELTA.md row 1). The
rest of QT-A1 (the soundness proofs) is named as the next item **qt-a1b** (below), as the feed's size rule asks.

Item: feature item qt-a1 (rank 16 of the feature feed, acting DRI dri-featurefeed, 2026-10-18). Plan:
`docs/spec/quantities-PLAN.md` batch QT-A1 and sections 2.1 to 2.4; spec `docs/spec/quantities.md` 3.1 to 3.10, 4.2
(P1, P2) and 9.1. Both files are on `main` and identical to `research/quantities-p1` at e3697d8c7 (`git diff --quiet
e3697d8c7 HEAD -- <file>` for each). Branch `feature/qt-a1` from main c7fc6acac.

## Statement gate

QT-0 is QT-A1's statement review. Its verdict (Astra and Fable, debate `manage-agents/debates/quantities-spec`,
converged in round 3) was **FIX** with ten corrections; the correction check `manage-agents/quantities-p3ver1.final.md`
is **PASS** ("all ten agreed corrections … are in both documents and are correct"). The phase-2 round
(`quantities-ph2.final.md`) changed no Lean statement; its check (`quantities-ph2-check.final.md`, FIX) found one
overstated sentence in the plan about the premise check, fixed in e3697d8c (`quantities-ph2-fix.final.md`, plan text
only, "the Lean blocks and the spec stub are unchanged"). Every QT-0 correction, and where it stands:

| QT-0 correction | Applied in | Bears on QT-A1's statements? |
|---|---|---|
| A1: E4 decodes the projection `projectW6`; the two identities are bound separately | spec 2.2, 4.1, 4.2, 4.3; FA11 | no: QT-A3's wire |
| A2: FB2's endpoint premise | spec 2.2, 9.3 FB2 | no: track B |
| A3: `WellFormed` of scales rejects duplicate premise labels; `scalePremises_labels_nodup` | spec 2.2, 6.1–6.3, FB8 | no: track B |
| A4: `scales_conflictFree_iff`'s actual guarantee, `envAt (fill U) 0` in both theorems | plan 3.4; spec 6.3, FB9, FB10, 9.5 | no: track B |
| E1: "divided by" wordings; "out of" refused with both rewrites; FA4d | spec 7.2, 7.3, FA4d | no: English (QT-A6) and rounding (QT-A2) |
| E2: "N percent more than" refused on `display: percent` operands; FA5b | spec 7.2–7.4, FA5b | no: English and QT-A2 |
| E3: the declaration sentence "There are finitely many …", English-only dispatch to W6a's sugar, the wire still `CardinalityNotFinite` | plan 2.1; spec 7.1, 7.3, FA12 | yes, at the core: admission refuses a count over a sort not declared finite (`Admitted.count`, `CFormula.admits`; FA8's first guard). The wire text is QT-A3's |
| E4: tie-up paraphrases say "to the larger number"; FA4e | spec 7.2, FA4e | no: English and QT-A2 |
| E5: `erasedProblem_admitted`, an admission-preservation obligation | plan QT-A1 fixtures; spec 3.6, 8, FA1, FA4c | yes: stated in spec 3.6; its proof is qt-a1b's. FA1's 11 erased formulas are built here (`erasedProblem`, guards on its length) |
| E6a: S1 and S2 first, then one depth-first pass of S3–S10; FA13 | spec 4.2, FA13 | no: QT-A3's decoder. P1 and P2 (`problemLimits`) are the problem-level checks after every statement, in 4.2's order (sorts, then predicates per sort in first-use order) |

All ten are applied; none is missing. DRI-DECISIONS-PHASE2 "Quantities" QT1 (QX-2's forms and timing), QT2 (the
premise-scale item), QT3 (the 0600Z audit finding) and ME3 ("around" in QT-A6's approximation row) change nothing in
QT-A1. SYNTHESIS 2.3 (QS-1) is merged and QT-A1 does not use it; 4.1 puts QT-A1 among the parallel Lean cores; 4.2
gives QT-A1 no shared hand-written file.

Built declarations against the approved text (`evidence/statements.json`, made with the repository's `declarations`
reader of `tools/check_readings_defaults_statements.py`, script `evidence/statements-diff.py.txt`): **54 exact**, 4
differing, 19 not built. The 4 differ only by the missing ratio cases (`CFormula.admits`, `CFormula.countBodies`,
`CFormula.erase`, `CFormula.holds`: the spec's text with the `roundsTo`, `percentOf` and `percentRoundsTo` lines
removed); the 19 not built are the ratio definitions (QT-A2) and the soundness theorems (qt-a1b). No approved
statement changed.

## Plan rows

| Plan row (QT-A1) | Delivered | Where |
|---|---|---|
| `lean/VE/Cardinality/Syntax.lean` | yes: 3.2's types, `regionPrefix`, `CEnv.WellFormed`; 3.4's `BodyTyped`, `Admitted`, `bodyCheck`, `CFormula.admits`; `admits_sound`, `admits_complete` proved | 5b073b3bb |
| `lean/VE/Cardinality/Semantics.lean` | yes: 3.3's meaning without erasure | 5b073b3bb |
| `lean/VE/Cardinality/Regions.lean` | yes: 3.5's regions, `predsOn`, `regionTable`, `CEnv.elab`, `regionBody`; 4.2's P1, P2 | 5b073b3bb |
| `lean/VE/Cardinality/Erase.lean` | yes: 3.5's erasure, `nonnegPremises`, `bridgePremises`, `erasedProblem`, `regionSize`, `withRegions`; 3.9's `Body.evalFin`, `countFin`, `withRegionsFinite`, `refutesC` | 5b073b3bb |
| `lean/VE/Cardinality/Theorems.lean` | `hasCount_exists_unique`, `nonneg_hold`, `proportion_holds_iff` (3.6) and 3.7's definitions; **not** `withRegions_admissible`, `bridge_hold`, `erase_iff`, `cardinality_elab_sound`, `erasedProblem_admitted`, the four `count_*_agree`, `refutesC_sound` (qt-a1b) | 5b073b3bb |
| `lean/VE/Cardinality/Examples.lean` | FA1, FA1b, FA1c, FA2, FA3, FA8, FA9a, FA9c, FA10 (below) | 5b073b3bb, 4ea2976c0, 5fef22e32 |
| `lean/CARDINALITY.md` | yes | 4ea2976c0 |
| generated: `lean/VE.lean`, `lean/VE/Audit.lean`, `frozen-sources.sha256`, `axioms.txt`, `statements.txt`, `predicates.txt`, `declarations.txt`, trust tables (signed) | regenerated with `uv run python tools/regen_generated.py --write` (`frozen-sources.sha256` unchanged: no frozen source changed; `lean/VE.lean` is the union-merged import list, one line); trust tables signed (DELTA.md) | 5b073b3bb, 4ea2976c0, 5fef22e32, a5b780b4e |
| "Hand-written shared: none" | none touched | — |
| FA1 "4 regions and a Farkas certificate"; "at least 16" still holds | yes: both certificates replay through the frozen order checker; found by `ve.entailment.prove_entailment` on Lean's erased problem (untrusted search, not committed) | `fa1Trace`, `fa1AtLeastTrace` |
| FA1b's countermodel | yes | `fa1bModel` |
| FA2 agreement on the units-schema 8 gate-4 models (six, seven and eight entities) | yes, for `atLeast`, `atMost`, `exactly`, `nOfM` with `n`, `m` up to 3 on every flag pattern up to 3, and at the bound 2 for every number flagged; the full 0-to-8 grid of the stub takes about 80 s in the interpreter and was cut to keep the build fast. "The evaluation counts of the pinned W6a fixtures are unchanged": no W6a file changed | `agreeOn` |
| FA3 | the cardinality half (admitted here); W6a's `CountingBound` refusal is W6a's unchanged code (`Wire.lean:739–749`), not re-run | `nOfMFormula pm 16 18` guard |
| FA8 | yes: every hostile admission, the 6/7-predicate and 8/9-sort limits, the universal statement with seven predicates and no count. "A vocabulary symbol beginning `cardinality__`" is `WellFormed`'s, shown as FA9a here; its diagnostic (E8) is QT-A3's decoder | FA8 guards |
| "Admission is preserved" (`erasedProblem_admitted`, with FA1's and FA4c's problems) | **no**: qt-a1b (FA4c is QT-A2's) | — |
| Seeded bug "`Body.inRegion` reads `not b` as `b`" | yes; the FA1 certificate guards fail, and FA1's model guard. **FA1b's countermodel guard does not fail** under it: on that model both bridges hold whichever way the region sums are read. The plan's sentence is wrong on that point; FA1's model (`fa1Model`) was added so a model guard fails too | mutant 1 |
| "Done when `lake build`, `lean/audit.py` and the `#guard`s pass and `lean/statements.txt` shows additions only" | yes: `lake build` passes, `lean/audit.py` PASS (553 files), `statements.txt` +82 −0 | — |

Differences from the spec, all in `lean/CARDINALITY.md`: the ratio constructors move to QT-A2 (below); P1 and P2 of
4.2 are `problemLimits` here so the core can be tested against them (P3 needs W6a's admissions: QT-A3); helper
theorems not in the spec: `bodyCheck_iff`, `admits_iff`, `hasCount_unique`, `exists_nodup_filter`, `nodup_length_eq`.

**The ratio constructors are QT-A2's.** `roundsTo`, `percentOf`, `percentRoundsTo`, `CTerm` with `CTermTyped`,
`CTerm.Denotes`, `CTerm.tagOf`, `CTerm.erase`, `CTerm.countBodies`, `ratioTyped`, `admittedRules` and `roundingQ` are
the spec's text and need only ME-1's `VE.Numbers` (on main). They were left out to keep this item inside R16's 150
trusted lines (with them S would be about +165) and inside the size rule; QT-A2 adds them, with their fixtures FA4,
FA4c to FA4e, FA5, FA5b, FA9e and `roundsTo_ratio_agree`, as one constructor block and one case per function, under its
own R16 allowance. The soundness theorems of qt-a1b are stated over `CFormula` and so cover whichever constructors
exist when they are proved; the plan's single milestone (QT-A1 with QT-A2) is unchanged.

## qt-a1b (next item)

The proofs of `withRegions_admissible`, `bridge_hold`, `erase_iff`, `cardinality_elab_sound`,
`erasedProblem_admitted` (with FA1's erased problem as its example), `count_atLeast_agree`, `count_atMost_agree`,
`count_exactly_agree`, `count_nOfM_agree` and `refutesC_sound`, exactly as spec 3.6, 3.7 and 3.9 state them. Almost
all of it is proof (P), so its trust growth is about 0 lines; it also ties erasure (C, untied here) and the count
meaning (FOLLOW-UPS "## qt-a1"). Until it lands no route uses erasure or `refutesC`, and an erased problem's W6a
certificate says only that the erased problem is entailed. Order: qt-a1b, then QT-A2 (or QT-A2 first: they touch
different declarations), then QT-A3.

## Seeded bugs (Lean; `uv run python tools/mutants.py docs/quantities/qt-a1/mutants.json --no-baseline`, results `evidence/mutants-run.json`)

Each mutation is applied alone to the committed tree, `lake build VE.Cardinality.Examples` is run, and the file is
restored (`tools/mutants.py`, after a passing build). 51 mutants, 51 killed: the first round's six, review F1's
fifteen, and one for every other case of each trusted definition of `Syntax.lean` and `Semantics.lean`. A mutant that
changes a specification and its check together (`Admitted` with `CFormula.admits`, `BodyTyped` with `bodyCheck`)
also adjusts `admits_iff` or `bodyCheck_iff`, so the build fails at a fixture rather than at that proof. Where each
fails is in `evidence/mutants-run.json` (`first_errors`): 48 at a fixture of `Examples.lean`, three first at a
theorem of `Theorems.lean` that restates the definition (`proportion_holds_iff`, `hasCount_exists_unique`); with that
proof replaced by `sorry` those three fail at fixtures too (each mutant's `note`).

| # | File | Mutant | Fails |
|---|---|---|---|
| 1 | `lean/VE/Cardinality/Regions.lean` | `Body.inRegion` reads `not b` as `b` (the plan's) | FA1's 91-node guard, both certificate replays (`replays fa1 …`, `replays fa1AtLeast …`), FA1's model guard (`agrees fomc … fa1Model`) |
| 2 | `lean/VE/Cardinality/Erase.lean` | a proportion's erasure drops its nonempty-population conjunct | FA9c/FA10's meaning-against-erasure guard on the empty model (`agrees users …`) |
| 3 | `lean/VE/Cardinality/Regions.lean` | the predicate limit fires at 6 instead of above 6 | FA8's "with six it passes" guard |
| 4 | `lean/VE/Cardinality/Syntax.lean` | a body atom needs only some declared predicate (specification `BodyTyped` and check `bodyCheck` changed together, so `admits_iff` still holds) | FA8's guards refusing a binary predicate and another sort's predicate; `admitted_cases` |
| 5 | `lean/VE/Cardinality/Semantics.lean` | `Cmp.holds .ge` compares the wrong way | `cmp_cases_two`, `population_cases`, `fa10_two` |
| 6 | `lean/VE/Cardinality/Erase.lean` | `countFin` counts a twice-listed object twice | FA2's duplicate-domain guard (`agreeOn dupModel`), added for this mutant, which survived the first fixture set |
| 7–22 | `Semantics.lean`, `Syntax.lean` | review F1's fifteen (`F1-*` in `mutants.json`): `Rel.holds .eq`, `.lt`; `Body.holds .not`, `.or`; `Cmp.holds .lt`, `.le`, `.eq`; `CFormula.holds .quantity`, `.not`, `.and`, `.or`, `.implies`; a proportion over a sort not declared finite; a W6a part unchecked; `.and` checking its left part; `WellFormed.fresh` reversed | `rel_cases_two`, `body_cases` and the body counts, `cmp_cases_two`, `quantity_cases`, `connective_cases`, `admitted_cases`, `wellFormed_cases` |
| 23–51 | `Semantics.lean`, `Syntax.lean` | every other case (`C-*`): `Rel.holds .le`; `Body.holds .and`, `.atom`, `.any`; `Cmp.holds .gt`, `.ge`; `Counts` on lists of the wrong length and on empty lists; the coefficients; the population; the whole; `.implies` as `∧`; both halves of `Admissible`; `CEntails` without premises or admissibility; `HasCount`'s sort; `finiteDeclared`; `BodyTyped` under `not`, `and`, `or`; a count's sort and bodies; a proportion's whole, part, denominator and fraction; `.not`, `.or`, `.implies` checking one part | the theorems above, `weighted_two`, `counts_two`, `admissible_cases`, `entails_cases`, FA8's guards |

Python and Rust: no product code changed (only `tools/trust-classes.json`, a data table, and docs), so no seeded bug
there.

## Trust

`uv run python tools/trust_map.py --check` on the final tree against merge base c7fc6acac: K +0, **S +137**, untied V
+0 (`VE/Cardinality/Syntax.lean` +81, `VE/Cardinality/Semantics.lean` +56), per declaration in DELTA.md row 1. Not
trusted: admission (`bodyCheck`, `CFormula.admits`: C, tied by `bodyCheck_iff`, `admits_iff`), regions and erasure
(C, untied until qt-a1b), the counting forms as count atoms (C, as `VE.Time.atLeast` is), the limits (G[R],
reject-only), `regionSize` and `withRegions` (P: the reading of region constants that the soundness proofs use; no
statement that the soundness theorem gives depends on them), the fixtures (T). SIGNED by standing ruling R16; allowance
recorded (a5b780b4e); FOLLOW-UPS row "## qt-a1" asks for the ties pass.

## Pilot bytes

0 for this item (infrastructure, reachable from no route). What QT-A1 opens, once QT-A2, QT-A3 and QT-A4 put it on a
route: the Asimov extended case's P6 (two deaths against one) and, as the feed's line says, 31 constitution units
(5,387 B) where counting is the primary blocker; the plan's own measured figure is QT-A5's news 0–194 B. All are
**estimates**; nothing is claimed before a pilot audit.

## Size

Hand-written Lean: 575 lines of product code (`Syntax` 152, `Semantics` 67, `Regions` 133, `Erase` 107, `Theorems`
116) and 456 lines of fixtures (`Examples`; 276 before fix round 1); `lean/CARDINALITY.md` 69; `lean/VE.lean` +1; `tools/trust-classes.json`
+155 (the side table); `docs/trust-baseline.json` +7 (the allowance). The product code is inside the ~600-line guide;
with the fixtures the item is about 850 lines, the smallest part that carries the plan's fixtures FA1 to FA3 and FA8
with their seeded bugs. The generated inventories (`declarations.txt`, `statements.txt`, `predicates.txt`,
`axioms.txt`, `VE/Audit.lean`) and this directory's docs and evidence are outside the count.

## Overlap with branches in flight

Files touched by hand: `lean/VE/Cardinality/*.lean` (new), `lean/CARDINALITY.md` (new), `docs/quantities/qt-a1/*`
(new), `lean/VE.lean` (one appended import, union merge), `tools/trust-classes.json` and `docs/trust-baseline.json`
(JSON ledgers with the `ve-generated` merge driver; `feature/ap-2`, `feature/et-7`, `feature/pk-1`, `foundation/me-1`
and `lean-first/b18` also touch `tools/trust-classes.json`, which merges by module key). No branch of `lean-first/*`,
`feature/*`, `infra/*`, `foundation/*` touches the new paths (`git diff --name-only main...<branch>` for each, at the
start). Outside the repository: one row appended to `manage-agents/FOLLOW-UPS.md` ("## qt-a1"). Recheck F7 found the
first append overwritten by another writer; fix round 2 re-appended it with `>>` and saved its text in
`evidence/follow-ups-row.md` (re-append verbatim if it goes missing; the probe is in that file).

## Tests

- Selected tests on the Mac runner: `zsh manage-agents/mac-pytest.sh --select -- --base c7fc6acac --run`, HEAD
  5fef22e32: 58 of 435 units (lake build, `lean/audit.py`, and 56 pytest files including `test_frozen_sources.py`,
  `test_lean_audit_record.py`, `test_regen_generated.py`, `test_p0_three_way.py`, `test_wire_gate_corpus.py`), all
  passing except `tests/test_trust_budget.py::test_trust_map_check_passes_on_the_live_tree` and
  `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check`, which failed because the allowance was not
  yet recorded; after a5b780b4e both files pass (`uv run pytest tests/test_trust_ratchet.py
  tests/test_trust_budget.py`: 110 passed).
- `uv run python tools/gate_collection.py --check --prebuilt`: 17322 collected, 0 added, 0 refused, 0 stale, 0
  malformed. `uv run python tools/repo_map.py --check`: PASS (36 modes; no mode added).
- `uv run python tools/regen_generated.py --write` ran with `--skip route-cases`: that entry needs the Rust binary,
  which this worktree has not built, and no route case changed (no route reaches the new modules); the final-HEAD gate
  checks it.
- The full gate is the chain's, on the final HEAD (not run here, as the task directs). Main-known-red tests: none
  selected.

## Acceptance items

All AGENT. None HUMAN or EXTERNAL.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A., no relayed answer, mode or schema is added (QT-A3, QT-A4).
2. Every deliverable built, no rule broken: PASS, "Plan rows" above lists each row with its commit or the item it
   moves to (qt-a1b, QT-A2); no Python copy of a Lean decision, no report test, no authority switch; overlap checked
   ("Overlap" above).
3. Tests and gates can fail: PASS, 51 seeded bugs, one per case of each trusted definition, each failing the build
   (`mutants.json`, `evidence/mutants-run.json`); the sixth survived the first fixtures and a fixture was added
   (`agreeOn dupModel`); review F1's fifteen survived the first round and the theorems of fix round 1 were added.
4. Python, Lean and Rust agree: PASS for the core's two internal routes: meaning (`holdsFin`) against erasure on
   finite models (`agrees` guards) and the count atoms against W6a's expansion (`agreeOn`); Python and Rust are not
   involved until QT-A3.
5. R8 binding: N.A., no relay.
6. Gate evidence matches the final HEAD: PASS, the chain runs the gate on the final HEAD; no gate evidence is
   committed here.
7. No unsigned item: PASS, DELTA.md row 1 cites R16 with its evidence; `uv run python tools/trust_map.py --check`
   exit 0.
8. Every user-visible change in DELTA: PASS, there is none besides the trust budget (no route reaches the new code;
   `tests/test_wire_gate_corpus.py` and `tests/test_p0_three_way.py` pass in the selected run).
9. Test selection finds the tests: PASS, 58 of 435 units selected, including `lake build`, which runs every `#guard`
   and fails for each seeded bug.
10. Lean statements say what is claimed: PASS, `evidence/statements.json` (54 exact; the 4 differences are the
    ratio cases moved to QT-A2); seeded bug 5 breaks a theorem about the meaning (`cmp_cases_two`).
11. Budgets and limits fail closed: PASS for the limits here: `problemLimits` refuses with `ResourceLimit` at 7
    predicates and 9 counted sorts and passes at 6 and 8 (FA8 guards); no search or budget exists in this item.
12. No CPU or memory regression: PASS, no route changed; the new module adds about 8 s to `lake build`
    (`lake env lean VE/Cardinality/Examples.lean`: 7.9 s), after FA2's grid was cut from about 80 s.
13. Test-removed trailers: N.A., no test removed or renamed (`gate_collection.py --check --prebuilt`: 0 removed).

## Fix round 1 (review `qt-a1-review.final.md`)

* **F1 (B), R16's "every new trusted definition is exercised by a test that can fail".** Fixed as a class: named
  theorems in `Examples.lean` state every case of every trusted definition of `Syntax.lean` and `Semantics.lean`,
  true cases beside false ones (the earlier `example`s became theorems, which `tools/trust_map.py` can see);
  `tests/test_cardinality_exercised.py` runs the R16 rule (`trust_map.unexercised`) over every file of
  `lean/VE/Cardinality/`, so a trusted definition a later item adds there fails until a theorem states it; the
  seeded bugs are now a `tools/mutants.py` file with one bug per case (51, all killed; the review's 15 are `F1-*`).
  The review's probe now prints `[]`. No trusted line changes: S +137 as before, the new fixtures are T.
* F2 to F6 (C) are notes for the plan and the orchestrator (QT-A2's prompt, FA2's range, FA8's predicates, QT-A3's
  order, size); no change here.

## Commits

`git log --oneline main..HEAD --no-merges` at the time of writing: 5b073b3bb, 4ea2976c0, 5fef22e32, a5b780b4e, b20a8e306
(the report), and fix round 1's commits after it.
