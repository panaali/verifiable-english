# qt-a1b build report: soundness of erasure for `cardinality@0` (spec 3.6)

No DRI signature is reserved and there is no DELTA row: trust is +0 on every class (K, S, untied [V], unclassified) and
no route reaches the new proofs. The rest of the task (spec 3.7's four `count_*_agree` and 3.9's `refutesC_sound`) is
named as the next item **qt-a1c** (below), by the feed's size rule.

Item: feature item qt-a1b (rank 19, acting DRI dri-featurefeed, 2026-10-18), branch `feature/qt-a1b` from main
3cc70f557. Plan and spec on main, identical to cf73592b4 and to `research/quantities-p1` e3697d8c7 (`git diff --quiet`).

## Statement gate

QT-0 accepted QT-A1's statements (FIX, ten corrections; `manage-agents/quantities-p3ver1.final.md`: **PASS**); qt-a1's
report maps each correction (E5 = `erasedProblem_admitted`). The proved statements are the spec's, unchanged: the
statement diff of qt-a1 (`docs/quantities/qt-a1/evidence/statements-diff.py.txt`, rerun, output saved as
`evidence/statements.json`) gives **59 exact** (qt-a1's 54 and this item's five), the same 4 differences (the ratio cases
QT-A2 adds) and 14 not built (QT-A2's ratio definitions; qt-a1c's five theorems; `roundsTo_ratio_agree`). QT-A2 has not
merged, so the theorems cover the constructors on main; their inductions are over `Admitted`, so QT-A2 adds one case
per ratio constructor. DRI-DECISIONS-PHASE2 QT1–QT3 and ME3 and SYNTHESIS 2.3/2.4 change nothing here.

## Plan rows

| Row (QT-A1 / spec 3.6) | Delivered | Where |
|---|---|---|
| `withRegions_admissible`, `bridge_hold`, `erase_iff`, `cardinality_elab_sound`, `erasedProblem_admitted` | yes, statements unchanged | `Theorems.lean`, f93a44fb7 |
| "Admission is preserved … FA1's erased problem" (spec 3.6, 9.1) | yes: `fa1_entails` proves `CEntails fomc fa1 fa1Conclusion` from the replayed certificate, through `erasedProblem_admitted`, `checkCertificate_sound`, `tentails_of_entails` and `cardinality_elab_sound`; FA4c is QT-A2's | `Examples.lean` |
| `erase_iff` both directions on a model | `erase_two`: a proportion that holds and one that fails, each carried to its erasure | `Examples.lean` |
| `count_atLeast_agree` … `count_nOfM_agree` (3.7), `refutesC_sound` (3.9) | **no**: qt-a1c | — |

How the proofs go is in `lean/CARDINALITY.md` ("qt-a1b"). Lemmas not in the spec (all P): the string facts
`startsWith_of_data` (reusing `VE.Readings`' `unfold_substrEq_loop` for `String.startsWith`'s private loop, not a copy),
`regionConst_startsWith`, `regionConst_inj`; the partition `regionSize_sum`; `regionSum_denote`; `admitted_elab`;
`denote_congr` (a core formula reads only declared constants); `bodyOfQ_spec`; `erase_iff_of`, `erase_admitted`.

## Seeded bugs (Lean only; `uv run python tools/mutants.py docs/quantities/qt-a1b/mutants.json --no-baseline`)

11 mutants, 11 killed (`evidence/mutants-run.json`). The harness keeps only the build log's tail, so each mutant was
also rebuilt with its full log; the theorems that fail are listed.

| id | File | Bug | Fails at |
|---|---|---|---|
| erase-cmp | `Erase.lean` | `Cmp.erase .gt` as `≤` | `erase_iff_of` |
| bridge | `Erase.lean` | a bridge sums the regions inside the body, not outside | `bridge_hold`, `erasedProblem_admitted` |
| elab-tag | `Regions.lean` | region constants declared `day` | `withRegions_admissible`, `regionSum_typed`, `erasedProblem_admitted` |
| admitted-tag | `Regions.lean` | region sums tagged `day` (meaning unchanged) | `sumTerms_typed`, `erase_admitted`, `erasedProblem_admitted` only |
| sound-fs | `Erase.lean` | regions from the premises only | `cardinality_elab_sound`, `erasedProblem_admitted` |
| name-sep | `Regions.lean` | region name without `__` | `regionConst_startsWith`, `regionConst_inj` |
| name-prefix | `Regions.lean` | sort before the prefix | `regionConst_startsWith` |
| region-body | `Regions.lean` | a region's body negates its bits | `regionBody_holds` |
| withRegions-size | `Erase.lean` | a region constant read as the sort's size | `nonneg_hold`, `withRegions_const`, `withRegions_admissible` |
| fa1-premises | `Examples.lean` (changed) | FA1 stated without the exclusion premise | `fa1_entails` (the certificate no longer replays) |
| partition-statement | `Theorems.lean` (changed) | `regionSize_sum` summing every region | `regionSize_sum`, `regionSum_denote` |

R16's mutant-per-trusted-definition rule: N.A., no trusted definition is added. Python and Rust: no product code
changed (`tools/trust-classes.json` is a data table: one P entry, below).

## Trust

`uv run python tools/trust_map.py --check` on the final tree against 3cc70f557: **K +0, S +0, D +0, G +0, tied +0,
unclassified +0, trusted +0**, PASS. The only declaration that is not a theorem is the proofs' `local notation "go"`
(`VE.Cardinality.termGo`), classified P. No allowance, no FOLLOW-UPS row (R16 is not used).
`trust_map.unexercised` over `Syntax`, `Semantics` and `Theorems` prints `[]`. `python3 lean/audit.py`: PASS (557
files, 6408 theorems, only the standard axioms).

## Pilot bytes

0 for this item (no route changed). Once QT-A3 puts erasure on a route, `cardinality_elab_sound` is what makes a
certificate mean the counting claim: the Asimov extended case's P6 and the 31 constitution units (5,387 B) where
counting is the primary blocker. **Estimates**; nothing is claimed before a pilot audit.

## Size and the cut

Hand-written lines (`git diff --numstat` against the merge base, generated inventories and the two evidence outputs
excluded): `Theorems.lean` +640 −6, `Examples.lean` +23, `CARDINALITY.md` +19 −9, `mutants.json` +28,
`trust-classes.json` +3, this report. That is over the ~600 guide. The size was measured once spec 3.6's proofs worked
(633 lines) and the item was cut there: 3.7 and 3.9 move to qt-a1c. A smaller coherent part does not exist, because
`cardinality_elab_sound` needs all of `erase_iff`, `bridge_hold` and `withRegions_admissible`, and these need the
region-name string facts (~110 lines) and the partition argument. Moving `erasedProblem_admitted` (~85 lines) out
would not bring the item under the guide either, and spec 3.6 would then be split across two items.

## qt-a1c (next item)

Spec 3.7's `count_atLeast_agree`, `count_atMost_agree`, `count_exactly_agree`, `count_nOfM_agree` (through
`VE.Time.expand_atLeast_iff`; `Body.toFormula` against `TStructure.lower`) and 3.9's `refutesC_sound`: lift the finite
model with `VE.Time.lift`, show `regionSize = countFin` on it, then `erase_iff`, `erase_admitted` and `units_faithful`,
with `denote_congr` to compare `withRegions`' lower structure with `withRegionsFinite`. Its fixture is FA1b's
countermodel giving `¬ CEntails`. Proofs only (P), so trust stays about +0. Then QT-A2 (ratio constructors, one case per
theorem here), then QT-A3.

## Overlap with branches in flight

Touched by hand: `lean/VE/Cardinality/{Theorems,Examples}.lean`, `lean/CARDINALITY.md`, `tools/trust-classes.json`
(module-keyed JSON ledger, `ve-generated` merge driver; `feature/ap-2`, `feature/pk-1`, `foundation/me-1`,
`lean-first/b18` also touch it, other modules), `docs/quantities/qt-a1b/*`. No branch of `lean-first/*`, `feature/*`,
`infra/*`, `foundation/*` touches the Cardinality files (`git diff --name-only main...<branch>`, at the start).

## Tests

- Selected tests on the Mac runner (`mac-pytest.sh --select -- --base 3cc70f557 --run`), HEAD 802bcc4a0: 120 units, 0
  failed, exit 0 (the `lake build`, `lean/audit.py`, `test_cardinality_exercised.py`, `test_trust_budget.py`,
  `test_frozen_sources.py`, …). Rerun on the final HEAD: see the last commit's message.
- `regen_generated.py --write --skip route-cases` (route-cases needs the Rust binary; no route case changed), then
  `--only lean-statements` and `--only lean-audit-manifests` after the last fixture. Frozen sources unchanged.
- Main-known-red tests: none selected. The full gate is the chain's, on the final HEAD.

## Acceptance items

All AGENT.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no mode, relay or schema.
2. Deliverables built, no rule broken: PASS, "Plan rows" (3.6 done, 3.7/3.9 named qt-a1c); no Python copy, no report test.
3. Tests can fail: PASS, 11 seeded bugs, 11 killed, each at the theorem it claims (table above).
4. Python, Lean, Rust agree: N.A., Lean only; `fa1_entails` ties the certificate route to the counting meaning in Lean.
5. R8 binding: N.A., no relay.
6. Gate evidence matches the final HEAD: PASS, no gate evidence committed; the chain gates the final HEAD.
7. No unsigned item: PASS, no DELTA row; `trust_map.py --check` PASS at +0.
8. User-visible changes in DELTA: PASS, none (no route reaches the module).
9. Test selection finds the tests: PASS, 120 units selected, including `lake build`, which fails on every seeded bug.
10. Lean statements say what is claimed: PASS, `evidence/statements.json` (five exact); `admitted-tag` breaks only
    the admission theorems, `erase-cmp` only the meaning.
11. Budgets and limits fail closed: N.A., no budget or limit added.
12. No CPU or memory regression: PASS, no route changed; `Theorems.lean` builds in about 7 s and `Examples.lean` in 8–15 s
    (`fa1_entails` replays the certificate in the kernel, `decide +kernel`, about 3 s).
13. Test-removed trailers: N.A., no test removed or renamed.

## Commits

`git log --oneline main..HEAD --no-merges` at the time of writing: f93a44fb7, 6a23cd2ec, 802bcc4a0, 064a7f47f,
cde232f33, and the report's commit.
