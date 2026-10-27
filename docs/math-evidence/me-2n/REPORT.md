# me-2n: the `calc@0` work addendum (spec 3.2, draft 6)

This item reserves no DRI signature. It has no DELTA row, and trust is +0. **For the DRI, before me-2nb and me-2nc
build:** three classes of deltas those builds will make fit no standing ruling. They are rows B1, C2 and C3 below; I
asked for a ruling with `msg.sh dri me-2n`.

## What this is

This is the `calc@0` sibling of the DRI's me-12aa N1 decision (`reviews/dri-decisions-20261027-me-12-n1.md`), written
for me-2b's review F1. It contains documents and a stub, and no product code:
- the spec: draft 6 of 3.2, one clause each in 5, 13.1 and 14, nine rows in 13.3, and the change log;
- the stub: `cd lean && lake env lean ../docs/spec/math-evidence/me-2n-calc-work-stub.lean` gives 0 errors and 11
  `sorry` warnings, with every guard passing, in about 5 s. Nothing imports it.

| Part | Where | Evidence |
|---|---|---|
| (a) each declaration evaluated once, in order, read from a table; the theorem that the table means 2.4's values | 3.2 (a): `valueTable`, `valueTable_read` (**proved**); a claim's sides are evaluated once and its outcome, `sides`, `display` and `tie` read them | F1-511: 512 values in 396,545 units, where re-reading would cost 2^511 |
| (b) size charge in me-12n's unit (bits), a per-request limit in 3.2's order, `ResourceLimit` | 3.2 limit 10 (2^33 units), (b), and the bound that no claim case reaches it (≤ 163,290,000) | `runC`, `Expr.evalC`, `Expr.linearC`; H-1 at 107,837,424 |
| (c) the answers that change, with fixtures | 3.2 (c), 13.3 F1-24 to P-2 | stub guards `:269-334` |
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
- the Farkas replay and the counterexample point: they read rows already charged;
- counted values and statistics: ME-4 and ME-7 are not on the wire yet, and ME-4 has its own budget.

## The changes the builds will make (3.2 (c)) and their rulings

| Row | Build | Change | Ruling |
|---|---|---|---|
| B1 | me-2nb | requests today's runner does not finish (`CheckerUnavailable`) get 2.4's outcomes: F1-28 `holds`, G-1x512 `unknown (limit .digits)` | **none fits**: R7 covers only unavailable on both sides, and R5 only yes or no becoming unknown. Ruling requested |
| B2 | me-2nb | trusted Lean growth, about +80 to +120 V in `Decls.lean` and `Run.lean` | R16 (per-file DELTA row, a test per new trusted definition, FOLLOW-UPS ties row) |
| C1 | me-2nc | unavailable → answered: P-1 (same rows), L-4 (`derivationInconclusive`) | as B1 |
| C2 | me-2nc | decided → `unknown derivationInconclusive` when a lowering or search meets a value beyond 4,096 digits: L-2 (holds in 0.07 s today), L-3 | **R5 by analogy only**: a fixed limit forbids the confirming step, but there is no request budget for R5's "adequate budget" test. Ruling requested |
| C3 | me-2nc | answered → `ResourceLimit` for the whole case past 2^33 units: P-2 with 73 premises (about 5 s today); its other rows are lost | **none fits** (a loss of information). Ruling requested: sign it, or answer such a derivation per row instead |
| C4 | me-2nc | trusted Lean growth (`Lower.lean`, the lowering table) | R16 |

No answer of a claim case that finishes today changes (`runC_sound`, and the 163,290,000 bound in 3.2), and no claim
case can end `ResourceLimit`.

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
- `Lower.lean`: `Lowered` and `Expr.linearC`.
- `Wire.lean`: `derivations` reads one lowering table and charges limit 10 in 3.2's order; only `.nonlinear` is
  `NonlinearPremise`.
- `Run.lean`: premise facts once per case, and the case's units threaded through the claims.
- `FourierMotzkin.lean` and `Derive.lean` (untrusted): each row charged `1 + rowSize` and held to the digit limit,
  ending the search `derivationInconclusive`.
- Fixtures: L-1 to L-5, P-1, and P-2 at 72 and 73 premises, with exact case units. S7 and S8 below are its seeded
  bugs.

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

Each claimed behaviour has a bug that a named guard or proof catches. No product code changed, so there is no
product seeded bug in any language.

## Trust, tests, size, overlap

- **Trust.** `uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0, trusted +0, PASS. There is no R16 row
  and no FOLLOW-UPS row. `repo_map.py --check` passes.
- **Tests.** The selected tests are in "Final checks" below. The full gate was not run here: the chain runs it on the
  final HEAD.
- **Size.**
  - Spec: 140 lines added and 6 changed.
  - Stub: 336 lines, its guards counted as evidence.
  - This report: 135 lines.
  - In all: 617, a little over the ~600 guide. The fixtures for the growths beyond F1 (G, L and P) are the excess.
- **Overlap.** The hand-written files are the spec, the stub and this report. No branch in flight (`feature/*`,
  `lean-first/*`, `infra/*`, `foundation/*`) changes them, `lean/VE/Calc/` or `ve/backends/lean_service.py`.
- **Bytes.** 0 (the use-case ceiling); no pilot movement is claimed.

**Next:** me-2nb, after the ME-S re-check of 3.2 passes; then me-2nc, after the DRI rules on B1, C2 and C3.

## Final checks

(filled in below after the selected-test run)

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
10. PASS: `valueTable_read` and `Val.check_eq` are proved, and the restated theorems are `sorry` only in the stub.
11. PASS: limit 10 fails closed (`ResourceLimit`, never `CheckerUnavailable`), refused before it is passed (S4), and
    tested under, at and over (F1-24, P-2 at 72 and 73).
12. PASS: F1-511, G-1x512, H-1, L-4 and P-2 are the step and size fixtures for the CPU and memory class.
13. N.A.: no test was removed or renamed.
