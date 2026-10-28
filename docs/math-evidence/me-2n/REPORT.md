# me-2n: the `calc@0` work addendum (spec 3.2, draft 6)

This item reserves no DRI signature. It has no DELTA row, and trust is +0. The three classes of deltas that me-2nb and
me-2nc will make that no standing ruling covers (rows B1/C1, C2 and C3 below) are SIGNED by the DRI in
`reviews/dri-decisions-20261027-me-2n.md`, items 1 to 3. Fix round 1 (spec draft 7) answers the review's F1 to F4 and
adds no class beyond those three ("Fix round 1" below).

## What this is

This is the `calc@0` sibling of the DRI's me-12aa N1 decision (`reviews/dri-decisions-20261027-me-12-n1.md`), written
for me-2b's review F1. It contains documents and a stub, and no product code:
- the spec: draft 6 of 3.2, one clause each in 5, 13.1 and 14, nine rows in 13.3, and the change log;
- the stub: `cd lean && lake env lean ../docs/spec/math-evidence/me-2n-calc-work-stub.lean` gives 0 errors and 17
  `sorry` warnings, with every guard passing, in about 15 s. Nothing imports it.

| Part | Where | Evidence |
|---|---|---|
| (a) each declaration evaluated once, in order, read from a table; the theorem that the table means 2.4's values | 3.2 (a): `valueTable`, `valueTable_read` (**proved**); a claim's sides are evaluated once and its outcome, `sides`, `display` and `tie` read them | F1-511: 512 values in 396,545 units, where re-reading would cost 2^511 |
| (b) size charge in me-12n's unit (bits), a per-request limit in 3.2's order, `ResourceLimit` | 3.2 limit 10 (2^33 units), (b), and the bound that no claim case reaches it (≤ 163,290,000) | `runC`, `Expr.evalC`, `Expr.linearC`; H-1 at 107,837,424 |
| (c) the answers that change, with fixtures | 3.2 (c), 13.3 F1-24 to C-1 | stub guards `:473-627` |
| (d) the build plan | below | — |

## What the review should know: growths beyond F1 (measured on `ve_service`, d9cff5345)

Evaluating once fixes F1 alone. 3.2's "Why limit 10" gives three more growths, each fixed in draft 6:
- G-1, 18.7 s for one power: the guard's digit list;
- L-3, 12.7 s: unguarded lowered constants;
- P-1, 29 s: re-lowering at each mention.

A fourth is FM's search. Its rows' coefficients double with each elimination: one dense 5-premise derivation with
40-digit coefficients takes 1.14 s, and 40 copies of it take 64.7 s, past the deadline. Draft 6 charges each row and
holds it to the digit limit.

Not charged:
- `inlineTable` and `nodesWithin`: linear in the case, and the walk stops at 10,000 nodes;
- counted values and statistics: ME-4 and ME-7 are not on the wire yet, and ME-4 has its own budget.

Draft 6 also left the Farkas replay and the counterexample point uncharged, because "they read rows already charged".
The review (F1) showed that this was wrong: `pick` checks each bound against every row, and `Farkas.check` calls
`coeffOf` per name. Draft 7 charges them per entry and makes them one pass ("Fix round 1").

## Fix round 1 (`manage-agents/me-2n-review.final.md`; spec draft 7)

| Finding | Fix | Regression |
|---|---|---|
| F1 (A): work not charged grows faster than the charge (`FM.pick`, `QLin.norm`/`coeffOf`, `nonlinearAt`; sweep `Farkas.check`, κ, `isConst`) | 3.2 (b): every derivation step pays `entryUnits` = 2^11 per entry it visits (`rowCost`, `passCost`, `chargeL`). The quadratic steps become one pass, each equal to 5's (`normOnce`, `isConstOnce`, `pickOnce`, `Farkas.checkOnce`, `nonlinearAtC`), and the point's values are held to the digit limit. "Why 2^33" is redone from measured times per unit (sizes 0.51 to 0.58 ns, entries 0.42 ns a unit, visits bounded by their count). 13.3 adds N-1, K-1 and C-1, and P-2 is retuned to keep 72/73 | stub `:576` (norm, isConst), `:599`/`:601` (pick, K-1's stages), `:603` (Farkas), `:620` (decoder paths), `:583` (N-1 units), `:610` (K-1 units); PROBE F1 is none (docs only) |
| F2 (B): `both` and `.pow` gave `tooLarge` before the side's shape was known, so S-1 and S-2 were accepted | `Lowered.tooLarge` carries its `Shape`. A product, quotient or power decides 5's linearity from its operands' shapes, and where they leave it open the node is lowered exactly, charged its bound first (`exactC`). `Expr.linearC_tooLarge`: `tooLarge` is always linear in 5. Swept: add, sub, mul and div through `binL`, and pow | PROBE F2 passes; stub `:562`, `:563` (S-1 to S-10 against `Expr.linear`), `:565`, `:566` |
| F3 (C): ruling cells said "Ruling requested" | B1, C1, C2 and C3 cite `reviews/dri-decisions-20261027-me-2n.md` items 1 to 3 | — |
| F4 (C): `Val.check_eq` called proved | Self-review 10: proved only relative to `digitCount_le_iff` (`sorry`; me-2nb proves it) | — |

The measurements, on today's `ve_service` (the VM, 2026-10-28). The review's scripts are in
`/tmp/me2n-review-probe/`; P-2 and C-1 are in `/tmp/me2n-fix-probe/`.
- K-1: 6.54 s for one increasing derivation and 13.05 s for two; 0.16 s for one decreasing.
- N-1 (400 free values): 0.14 s with 1 mention and 10 premises; 0.50 s with 2 and 10; 4.46 s with 8 and 10; 9.10 s
  with 16 and 10.
- P-2 (c^20): 0.73 s with 10 premises, 4.37 s with 72, 4.67 s with 73.
- C-1: 0.27 s with 64 premises; 0.98 to 1.50 s with 256.

No DRI signature is reserved. The new answer changes fall in the classes the DRI signed: K-1 increasing (unavailable
→ answered) under item 1, a point beyond the limit under item 2, and K-1 decreasing and N-1 under item 3. F2 removes a
widening instead of adding one. P-2 keeps item 3's condition (72 answered, 73 `ResourceLimit`) with 800-digit
coefficients. L-1 to L-4 keep item 2's units (8,642 to 8,645), because a constant pays no entry charge.

## The changes the builds will make (3.2 (c)) and their rulings

| Row | Build | Change | Ruling |
|---|---|---|---|
| B1 | me-2nb | requests today's runner does not finish (`CheckerUnavailable`) get 2.4's outcomes: F1-28 `holds`, G-1x512 `unknown (limit .digits)` | SIGNED by the DRI 2026-10-27 (`reviews/dri-decisions-20261027-me-2n.md` item 1) |
| B2 | me-2nb | trusted Lean growth, about +80 to +120 V in `Decls.lean` and `Run.lean` | R16 (per-file DELTA row, a test per new trusted definition, FOLLOW-UPS ties row) |
| C1 | me-2nc | unavailable → answered: P-1 (same rows), L-4 (`derivationInconclusive`), K-1 with 12 derivations (draft 7) | SIGNED by the DRI 2026-10-27 (`reviews/dri-decisions-20261027-me-2n.md` item 1) |
| C2 | me-2nc | decided → `unknown derivationInconclusive` when a lowering or search (draft 7: or its point) meets a value beyond 4,096 digits: L-2 (holds in 0.07 s today), L-3 | SIGNED by the DRI 2026-10-27 (`reviews/dri-decisions-20261027-me-2n.md` item 2) |
| C3 | me-2nc | answered → `ResourceLimit` for the whole case past 2^33 units: P-2 with 73 premises (4.7 s today); draft 7 adds K-1 decreasing with 39 or more derivations and N-1 with 122 to about 130 premises; its other rows are lost | SIGNED by the DRI 2026-10-27 (`reviews/dri-decisions-20261027-me-2n.md` item 3) |
| C4 | me-2nc | trusted Lean growth (`Lower.lean`, the lowering table) | R16 |

No answer of a claim case that finishes today changes (`runC_sound`, and the 163,290,000 bound in 3.2), and no claim
case can end `ResourceLimit`. No case refused today is accepted (draft 7, `Expr.linearC_tooLarge`: S-1 to S-3, S-9
and S-10 stay `NonlinearPremise`).

## Build plan

**me-2nb (claims; Lean and one Python comment).**
- `bits`: a single owner, in `lean/VE/Numbers/`. Whichever of me-12nb and me-2nb merges second reads it from there.
- `lean/VE/Calc/Decls.lean`:
  - `qbits`, `powTooLarge` and its soundness, `Table`, `valueTable` (copy the stub's proof), `Expr.evalC`,
    `Decl.valC`, `valueTableC`, `Claim.decideSides`, `Claim.ofSides` and its `_eq`;
  - `Small`'s `Decidable` instance by `digitCount_le_iff`. This changes no definition: it makes every `Val.guard` a
    comparison, the inlining's included.
- `lean/VE/Calc/Run.lean`:
  - `runCaseReported` runs `runC maxWork`, so the rows' `sides`, `display` and `tie` read each claim's evaluated
    values;
  - limit 10's text, in one place with 3.2's other limit texts (`Wire.limit`);
  - re-prove `outcome_sound` through `runC_sound` and `runC_mono`.
- `lean/VE/Calc/RunExamples.lean`: F1-24, F1-28, F1-511, G-1, G-1x512, V-11s and H-1 as guards, with their units.
- `ve/backends/lean_service.py:146`: the comment says what bounds the mode (the value table and limit 10). There is no
  `DEADLINES` change.
- Service route cases (`tests/data/route-cases.jsonl`, `tests/test_calc_service.py`): F1-28 and G-1. The bench row is
  F1-511 and H-1 in `tools/bench/` (not in the suite).
- Then `tools/trust-classes.json`, `regen_generated.py --write`, and trust mutants (13a).
- Seeded bugs, in product Lean: S1 to S6 below, planted in `Decls.lean`, must each fail a `RunExamples.lean` guard.
  The Python comment is not behaviour.

**me-2nc (derivations; Lean).**
- `Lower.lean`: `Shape`, `Lowered`, `Expr.linearC` with its shape rules, `Expr.exactBound` and `exactC`, and
  `Expr.linearC_form`, `_nonlinear` and `_tooLarge`. `QLin.isConst` becomes `isConstOnce`.
- `FourierMotzkin.lean`: `QLin.norm` and `FM.firstAppearance` become one pass, with a map from names to sums
  (`QLin.normOnce_eq`), and so does `FM.pick` (`pickOnce_eq`). `Linear.lean`: `Farkas.check` normalises its
  combination once (`Farkas.checkOnce_eq`). Each `_eq` is proved, so no answer changes.
- `Wire.lean`: `derivations` lowers each side once, bottom-up (`nonlinearAtC`, `nonlinearAtC_eq`), reads one lowering
  table and charges limit 10 in 3.2's order; only `.nonlinear` is `NonlinearPremise`.
- `Run.lean`: premise facts once per case, and the case's units threaded through the claims.
- `FourierMotzkin.lean` and `Derive.lean` (untrusted): each row charged `rowCost` and each pass over a stage
  `passCost`, with `entryUnits` = 2^11; rows and the point's values held to the digit limit, ending the search
  `derivationInconclusive`.
- Fixtures: L-1 to L-5, P-1, P-2 at 72 and 73 premises, S-1 to S-10, N-1 at 121 and 122 premises, and K-1, with
  exact case units. `tools/bench/`: K-1, N-1 and C-1 at the limit, and `entryUnits` re-measured against the one-pass
  steps. S7 to S16 below are its seeded bugs.

## Seeded bugs (this item: each planted alone in a copy of the stub, run with `lake env lean`, then removed)

| Bug | Edit in the stub | What fails |
|---|---|---|
| S1 | `valueTableC` does not store a value for later reads | guards `:269` to `:274`, `:280`, `:281`, `:287` and `:295` |
| S2 | a value read (`chargeV`) is not charged its size | `:269`, `:270`, `:272`, `:274`, `:280`, `:281`, `:287`, `:295` |
| S3 | a computed value (`chargeQ`) is not charged its size | the same eight guards |
| S4 | `chargeQ` refuses at the limit, not past it | `:274` (F1-24 at 1,124, 1,125, 1,126) |
| S5 | a claim's power is computed when `powTooLarge` rules it out | `:280`, `:281` (G-1), `:287` (V-11s) |
| S6 | 2.4's comparison lets 10^4,096 pass | `Val.check_eq`'s proof (`:36`), guard `:40` |
| S7 | lowered forms are not held to the digit limit | `:310` (L-5) |
| S8 | a lowered constant's power is computed when ruled out | `:306` (L-1 to L-4 units) |
| S9 | (fix 1) an operand beyond the limit makes the node `tooLarge` whatever the other side (draft 6's `both`) | `:562`, `:563`, `:565`, `:566` (S-1 to S-10), `:620` (decoder paths) |
| S10 | (fix 1) two sides that are not constant add to one that is not constant (cancellation ignored) | the same five guards |
| S11 | (fix 1) `pickOnce`'s tightest bound drops an equal bound's strictness | `:599` (K-1's stages), `:601` (mixed rows) |
| S12 | (fix 1) `normOnce` keeps names whose coefficients cancel | `:566`, `:576` (forms), `:603` (`Farkas.checkOnce`) |
| S13 | (fix 1) the decoder judges a node beyond `maxPolyTerms` | `:620` |
| S14 | (fix 1) a form's coefficients are not charged `entryUnits` | `:535` (P-1), `:544` (P-2), `:565` (S-1), `:583` (N-1) |
| S15 | (fix 1) a power ruled out by `powTooLarge` loses its shape (constant, nonzero) | `:515` (L-1 to L-4), `:565` |
| S16 | (fix 1) the decoder does not judge a power node | `:620` |

Each claimed behaviour has a bug that a named guard or proof catches. No product code changed, so there is no
product seeded bug in any language.

## Trust, tests, size, overlap

- **Trust.** `uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0, trusted +0, PASS. There is no R16 row
  and no FOLLOW-UPS row. `repo_map.py --check` passes.
- **Tests.** The selected tests are in "Final checks" below. The full gate was not run here: the chain runs it on the
  final HEAD.
- **Size.**
  - Spec: 140 lines added and 6 changed at draft 6; fix round 1 adds 118 and changes 27 (231 added against
    `d9cff5345`).
  - Stub: 336 lines at draft 6, 627 after fix round 1, its guards counted as evidence.
  - This report: 135 lines at draft 6, 190 after fix round 1.
  - Fix round 1 adds about 520 lines, mostly the stub's one-pass steps, shapes and guards, which the review's F1 and
    F2 ask for.
- **Overlap.** The hand-written files are the spec, the stub and this report. No branch in flight (`feature/*`,
  `lean-first/*`, `infra/*`, `foundation/*`) changes them, `lean/VE/Calc/` or `ve/backends/lean_service.py`.
- **Bytes.** 0 (the use-case ceiling); no pilot movement is claimed.

**Next:** me-2nb, after the ME-S re-check of 3.2 passes; then me-2nc. The DRI signed B1, C2 and C3
(`reviews/dri-decisions-20261027-me-2n.md`).

## Final checks

- **Selected tests.** `mac-pytest.sh --select -- --base d9cff5345 --run` ran on ve-mac-1 at aa686efc, with a clean tree,
  in 1,575 s. The summary: exit 0, 0 failed or error ids, no known Mac-only failures. No test in `main-known-red.txt`
  is touched.
- **Stub.** Fix round 1: 0 errors and 17 `sorry` warnings, with every guard passing (about 15 s). The seeded bugs S9
  to S16 were checked on it; S1 to S8 at draft 6.
- **Static.** `trust_map.py --check`: +0, PASS. `repo_map.py --check`: PASS, 38 modes.
- **DRI.** The rulings for B1, C2 and C3 were asked with `msg.sh dri me-2n`
  (`inbox/dri/20261027T232359Z-me-2n-2033442.md`).
- **Not run.** The full gate (the chain runs it), and no product build, because no product file changed.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or relay changed.
2. PASS: parts (a) to (d) are delivered (table above), and there is no Python copy of a Lean decision and no new
   permanent report test.
3. PASS: S1 to S8 each fail a stub guard or proof.
4. N.A.: no Python, Lean or Rust behaviour changed. The stub's agreement guards compare it with product code (`:273`,
   `:287`, `:305`, `:325`).
5. N.A.: no relay field.
6. PASS: the gate's evidence is the chain's run on the final HEAD; no evidence number comes from `git diff`.
7. PASS: no DELTA row and trust +0. The rulings the builds need are asked for now (B1, C2, C3).
8. N.A.: no user-visible change until me-2nb; 3.2 (c) lists every change the builds make.
9. PASS: `select_tests.py` selects for the two changed documents (Final checks).
10. PASS: `valueTable_read` is proved. `Val.check_eq`'s proof rests on `digitCount_le_iff`, which is `sorry` in the
    stub (me-2nb proves it), so `Val.check_eq` is proved only relative to it. The other restated theorems are
    `sorry` only in the stub.
11. PASS: limit 10 fails closed (`ResourceLimit`, never `CheckerUnavailable`), refused before it is passed (S4), and
    tested under, at and over (F1-24, P-2 at 72 and 73).
12. PASS: F1-511, G-1x512, H-1, L-4 and P-2 are the step and size fixtures for the CPU and memory class.
13. N.A.: no test was removed or renamed.
