# qt-a1c build report: agreement with W6a and finite countermodels for `cardinality@0` (spec 3.7, 3.9)

No DRI signature is reserved and there is no DELTA row. Trust is +0 on every class (K, S, D, G, tied, unclassified),
and no route reaches the new proofs. Every theorem of spec 3.6 to 3.9 is now proved, for every constructor, including
QT-A2's ratio statements.

Item: feature item qt-a1c (rank 34, acting DRI dri-featurefeed, 2026-10-18), branch `feature/qt-a1c` from main
e14d56df9. The plan and spec on main are identical to e010fb6aa (`git diff --quiet`), and so to `research/quantities-p1`
e3697d8c7.

## Statement gate

QT-0 accepted QT-A1's statements: the verdict was FIX with ten corrections, all verified
(`manage-agents/quantities-p3ver1.final.md`: **PASS**). I reran qt-a1's statement diff
(`docs/quantities/qt-a1/evidence/statements-diff.py.txt`), which compares spec 3.2 to 3.9 with the Lean files after
whitespace normalisation. Its output is saved as `evidence/statements.json`: **76 exact**, 1 spelled differently, 0 not
built.
- The five statements of this item are among the exact ones: `count_atLeast_agree`, `count_atMost_agree`,
  `count_exactly_agree`, `count_nOfM_agree` and `refutesC_sound`.
- The one spelling is QT-A2's known `CTerm.tagOf`, which writes `VE.Time.dimensionless` for `dl`
  (`lean/CARDINALITY.md`).

No statement changed. `lean/statements.txt` only gains lines. DRI-DECISIONS-PHASE2 QT1–QT3 and ME3, and SYNTHESIS 2.3
and 2.4, change nothing here: the agreement is with W6a's existing sugar, the countermodel check is the frozen
`VE.Order.countermodelCheck`, and Lean computes the region sizes.

## Plan rows

| Row (QT-A1 / spec 3.7, 3.9) | Delivered | Where |
|---|---|---|
| `count_atLeast_agree`, `count_atMost_agree`, `count_exactly_agree` | yes, statements unchanged | `Theorems.lean`, eb56e6527 |
| `count_nOfM_agree` ("follows from `count_exactly_agree`") | yes: it applies `count_exactly_agree` twice | same |
| `refutesC_sound` | yes, statement unchanged; it covers every admitted `CFormula`, ratios included, through `erase_iff` and `erase_admitted` | same |
| FA2 (agreement on models of 6, 7 and 8 objects) | the `#guard`s were qt-a1's. This item adds a `#guard` with a body using `not`, `and` and `or`, and `fa2_agree`, which uses each agreement theorem in both directions (`.mp` for the true cases, `.mpr` for the false ones) | `Examples.lean`, a503e3138 |
| FA1b (the countermodel refutes FA1 without the exclusion premise) | `fa1b_not_entails`: `¬ CEntails` through `refutesC_sound`. With qt-a1b's `fa1_entails`, the exclusion premise is what makes FA1 hold | `Examples.lean` |
| QT-A2's ratio constructors | `fa4d_not_entails`: a ratio claim refuted on a four-decision model. The two readings of "out of" give 0.500 and 1.000 | `Examples.lean`, 9139f4943 |

The proof route is in `lean/CARDINALITY.md` ("qt-a1c"). The lemmas below are not in the spec. All are proofs (P).

Agreement lemmas:
- `lower_unary`: a unary relation survives the units-only restriction.
- `toFormula_denote`: a body means what its formula means.
- `atLeast_iff_le`: W6a's "at least n" holds exactly when the count is at least n. Its proof reuses this file's
  `nodup_length_eq`, because core has no `subperm_of_subset`.

Countermodel lemmas:
- `firstUse_nodup`.
- `evalFin_iff`.
- `countFin_eq`: on a valid finite model, `countFin` is the count in the model's `VE.Time.lift`.
- `withRegionsFinite_denote`: `withRegions` of the lift and `withRegionsFinite` agree on every well-formed formula,
  through qt-a1b's `denote_congr`.

Fixture lemmas: `rowsModel_valid` and `count_lift`.

## Seeded bugs (Lean only; `uv run python tools/mutants.py docs/quantities/qt-a1c/mutants.json --no-baseline`)

14 mutants, 14 killed (`evidence/mutants-run.json`, run on the final product code). Each command is
`lake build VE.Cardinality.Examples`. The harness keeps only the tail of the log, so I rebuilt each mutant with its full
log. The table names the declaration where each build fails.

| id | File | Bug | Fails at |
|---|---|---|---|
| atLeast-rel | `Theorems.lean` | `atLeastAtom` uses `<` | `count_atLeast_agree` |
| atMost-rel | `Theorems.lean` | `atMostAtom` uses `<` | `count_atMost_agree` |
| exactly-rel | `Theorems.lean` | `exactlyAtom` uses `≤` | `count_exactly_agree` |
| nOfM-body | `Theorems.lean` | "n of the m" counts `prop`, not `sel ∧ prop` | `count_nOfM_agree` |
| toFormula-not | `Theorems.lean` | `Body.toFormula` drops a negation | `toFormula_denote` |
| toFormula-var | `Theorems.lean` | an atom reads variable 1 | `toFormula_denote` |
| evalFin-not | `Erase.lean` | `Body.evalFin` drops a negation | `evalFin_iff` |
| countFin-dup | `Erase.lean` | `countFin` counts a twice-listed object twice | `countFin_eq` |
| withRegionsFinite-body | `Erase.lean` | every region constant is the sort's size | `withRegionsFinite_denote` |
| refutesC-regions | `Erase.lean` | the finite model's regions come from the premises only | `refutesC_sound` |
| refutesC-conclusion | `Erase.lean` | the check refutes `bottom`, not the conclusion | `refutesC_sound` |
| fa1b-premise | `Examples.lean` | FA1b stated with the exclusion premise | `fa1b_not_entails` (the check is false) |
| fa2-bound | `Examples.lean` | "at least 3" claimed false on the model with 3 | `fa2_agree` |
| fa4d-premise | `Examples.lean` | FA4d's premise is the other reading | `fa4d_not_entails` (the check is false) |

The fixtures fail as well as the theorems (`evidence/guards-under-mutants.txt`, script `guards-under-mutants.py.txt`).
For three of the mutants above I replaced the broken proof with `sorry`, so the build reaches `Examples.lean`:
- atLeast-rel fails the four FA2 `#guard`s, `fa2_agree` and qt-a1's `entails_cases`.
- toFormula-not fails only the new compound-body FA2 `#guard` (`Examples.lean:212`). That is the coverage this guard
  adds.
- withRegionsFinite-body fails `fa1b_not_entails` and twelve FA1, FA1b, FA1c, FA2, FA4c and FA10 `#guard`s.
  `fa4d_not_entails` survives this one mutant: with every region read as 3, its premise still holds (3/6).
  `refutesC_sound` kills it.

R16's mutant-per-trusted-definition rule is N.A.: no trusted definition is added. The only new definitions are the
fixtures `fa2Model` and `fa4dModel`, classified T. Python and Rust: no product code changed.
`tools/trust-classes.json` is a data table: two T entries.

## Trust

`uv run python tools/trust_map.py --check` on the final tree against e14d56df9: **K +0, S +0, D +0, G +0, tied +0,
unclassified +0, trusted +0**, PASS. There is no allowance and no FOLLOW-UPS row, because R16 is not used.
`python3 lean/audit.py`: PASS (594 files, 6743 theorems, only the standard axioms). The kernel `decide`s use
`decide +kernel`, as in `fa1_entails`, and no `native_decide`.

## Pilot bytes

This item moves 0 bytes, because no route changed. Once QT-A3 puts the mode `cardinality` on a route:
- `refutesC_sound` makes a refuted counting claim a proved non-entailment;
- the agreement theorems let W6a's "at least / at most / exactly / n of m" and the count atoms be read as one meaning.

Together with qt-a1b this covers counting in the Asimov extended case's P6 and in 31 constitution units (5,387 B,
research share). These are **estimates**; nothing is claimed before a pilot audit.

## Size

Hand-written lines (`git diff --numstat` against the merge base; generated inventories and run outputs excluded):

| File | Lines |
|---|---|
| `Theorems.lean` | +142 −1 |
| `Examples.lean` | +74 −2 |
| `CARDINALITY.md` | +27 −6 |
| `mutants.json` | 34 |
| `guards-under-mutants.py.txt` | 33 |
| `trust-classes.json` | 2 |
| this report | about 150 |

The total is 312 lines added and 9 changed before this report, about 460 with it, under the ~600 guide. No cut was needed.

## Next item

qt-a3: the wire and the service mode `cardinality`, after ar-10a. QT-A1 and QT-A2 are complete: spec 3.6 to 3.9 are
all proved.

## Overlap with branches in flight

Touched by hand:
- `lean/VE/Cardinality/{Theorems,Examples}.lean`, `lean/CARDINALITY.md` and `docs/quantities/qt-a1c/*`. No branch of
  `lean-first/*`, `feature/*`, `infra/*` or `foundation/*` touches these (`git diff --name-only main...<branch>`, at the
  start).
- `tools/trust-classes.json`, a module-keyed ledger with the `ve-generated` merge driver. `feature/ap-1b`,
  `feature/ar-10b`, `feature/df-1ab`, `feature/jt-2`, `feature/me-9` and `foundation/me-1` also touch it, in other
  modules.

## Tests

- Selected tests on the Mac runner (`mac-pytest.sh --select -- --base e14d56df9 --run`), HEAD 4a160c27: 79 units,
  0 failed, exit 0. They include `lake build`, `lean/audit.py`, `test_cardinality_exercised.py`,
  `test_trust_budget.py`, `test_frozen_sources.py` and `test_relay_mutation_gate.py`. After that run, FA4d, its mutant,
  two T entries and the docs changed; the rerun on the final code is recorded under "Final checks".
- `regen_generated.py --write --skip route-cases`. `route-cases` needs the Rust binary, and no route case changed. After
  the last Lean edit I ran `--only lean-statements` and `--only lean-audit-manifests` again. Statements: additions only.
- `tools/gate_collection.py --check --prebuilt`: 18,411 collected, 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Main-known-red tests: none selected. The chain runs the full gate on the final HEAD.

## Final checks

These were run on bf2723c6b, where all code is final; only this section changes after it.
- Selected tests on the Mac runner (`mac-pytest.sh --select -- --base e14d56df9 --run`): 79 units, 0 failed, exit 0.
- `regen_generated.py --check --skip route-cases`: 31 entries checked, all fresh.
- `trust_map.py --check`: +0 on every class, PASS.
- `lean/audit.py`: PASS.

## Acceptance items

All AGENT.

## Sibling lessons (qt-b1b review)

- F1 (a report claiming both directions when the fixtures used one): `fa2_agree` uses `.mp` and `.mpr` of each of the
  four agreement theorems (`Examples.lean:229–253`). `refutesC_sound` is not an iff.
- F2 (a case of a definition no fixture tests): toFormula-not showed that the qt-a1 FA2 grid did not reach
  `Body.toFormula`'s `not`, `and` and `or` cases. The new compound-body `#guard` does, and it is the only fixture that
  fails under that mutant.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no mode, relay or schema.
2. Deliverables built, no rule broken: PASS, "Plan rows" (each with its commit). No Python copy, no report test.
   Overlap checked.
3. Tests can fail: PASS, 14 mutants killed (`evidence/mutants-run.json`). The fixtures also fail under stubbed mutants
   (`evidence/guards-under-mutants.txt`).
4. Python, Lean, Rust agree: N.A., Lean only. Inside Lean, `fa2_agree` and the FA2 `#guard`s tie the count atoms to
   W6a's sugar.
5. R8 binding: N.A., no relay.
6. Gate evidence matches the final HEAD: PASS. No gate evidence is committed; the chain gates the final HEAD.
7. No unsigned item: PASS, no DELTA row; `trust_map.py --check` PASS at +0.
8. User-visible changes in DELTA: PASS, none: no route reaches the module.
9. Test selection finds the tests: PASS, 79 units selected, including `lake build`, which fails on every mutant.
10. Lean statements say what is claimed: PASS, `evidence/statements.json` (76 exact). Each mutant breaks the theorem
    it claims; refutesC-conclusion shows that `refutesC_sound` depends on the conclusion actually being refuted.
11. Budgets and limits fail closed: N.A., no budget or limit added.
12. No CPU or memory regression: PASS, no route changed. The new kernel `decide`s take about 0.4 s
    (`fa4d_not_entails`, profiled). On an idle machine, `Examples.lean` takes about 38 s, as before, mostly qt-a2's
    FA4c/FA4d `#guard`s.
13. Test-removed trailers: N.A., no test removed or renamed (`gate_collection.py --check --prebuilt`: 0 refused, 0 stale,
    0 malformed).

## Commits

`git log --oneline main..HEAD --no-merges` at the time of writing: eb56e6527, a503e3138, aeef10f39, a0a53185f,
95c2a0eb7, 4a160c270, 9139f4943, dd14f86d8, and this report's commit.
