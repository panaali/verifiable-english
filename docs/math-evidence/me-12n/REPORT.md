# me-12n: the `arith@0` budget addendum (spec 12.2 and 13.3, draft 5)

This item reserves no DRI signature. There is no DELTA row, and trust is +0 because only documents and a stub changed.
**One point for the reviewers:** the charge goes further than the decision's rule (b), in the conservative direction
the decision chose:
- every value a term yields is charged its bit length, not only the results of `add`, `sub` and `mul`;
- so is every value a range step binds.

Rule (b) alone leaves B-4, a large value divided again and again, running for 29 s. Spec 12.2 gives the reason. Please
accept this extension by name, or name the edit.

## What this is

This item is the addendum the DRI decided on 2026-10-27 for me-12aa's N1 (`reviews/dri-decisions-20261027-me-12-n1.md`,
item 1). It contains documents and a type-checked stub, and no product code.
- `docs/spec/math-evidence.md`: draft 5 of 12.2 and 13.3, plus a change-log entry. Every statement outside those two
  sections keeps its text.
- `docs/spec/math-evidence/me-12n-budget-stub.lean`: the stub. Check it with
  `cd lean && lake env lean ../docs/spec/math-evidence/me-12n-budget-stub.lean`; it takes 50 s and gives 0 errors.

The stub imports `VE.Arith.Examples` (not `Bounded`, whose names it restates), and nothing imports it. Its independent
review is the ME-S bounded re-check of 12.2 and 13.3. The build, me-12nb, starts only after that check passes;
me-12ac and me-12b wait for it too.

## The task's parts

| Part | Where it is delivered | Evidence |
|---|---|---|
| (a) one unit per term-node visit; a function call is one visit plus its body's | 12.2 "Fuel accounting", `Term.evalB` (every clause starts with `charge`) | stub guards `:218` (`pos 3` = 10), B-1's recurrence |
| (b) `add`, `sub` and `mul` are charged their result's size; the unit is chosen | 12.2: **bit length** (`bits`), with three reasons. Extension: every yielded value, and every range step | stub `:224` (M-5's 33), B-3's closed form `:259-261` |
| (c) `decideBounded_work` restated if its form changes; a size bound | `_work` keeps its form. `Term.evalB_bits` is a **theorem**, proved in the stub, as are `bits_add_le`, `bits_sub_le` and `bits_mul_le` | stub `:152-168`, `:170-198` |
| (d) `_sound`, `_mono` and `_complete` checked against the new `charge` | 12.2 "The theorems under the new charge": no statement text changes, and none is named for restatement. me-12ab merged at 4a850162c, so its branch was not touched | stub `:134-147` (restated, `sorry`) |
| (e) 13.3 recomputed and marked *by hand*; N1's and F1's chains are UNKNOWN within seconds; the N1 pin is flipped | 13.3 rows M-1, M-1b, M-2, M-4, M-4b, M-4x and M-5; new rows B-1, B-2, B-2p, B-3 and B-4 | stub `:215-264` |
| (f) the build plan for me-12nb | below | — |

The DRI rejected "evaluate each zero-parameter definition once" as the fix. 12.2 allows it only as a later
optimisation that leaves every unit count unchanged, and B-2p is a chain it cannot shorten. `maxSteps` stays
1,000,000.

## Numbers (draft 4 → draft 5; every one is a `#guard` in the stub)

| Fixture | Draft 4 | Draft 5 |
|---|---|---|
| M-1 | 17,011 units | 337,735 (unknown at 337,734) |
| M-2 | 395 | 7,420 |
| M-5 | 2 | 33 (derived clause by clause in 13.3) |
| M-4 completing bound at 1,000,000 | 248 | 87 (973,791 units; 88 needs 1,004,183) |
| M-4b bounds: (1, 2), (3, 17), (4, 29), (5, 41) | ME-12's measurement | 87, 88, 89, 91 |
| B-1, N1's pin (`1024 = f10`) | (true, 1) at budget 1 | unknown at 1, 1,000 and 12,272; holds at 12,273 |
| B-2, N1's chain at k = 24 | 1 unit, 55.8 s | unknown, 0.7 s |
| B-3, F1's chain at 31 levels | 1 unit, 40 s, 1.8 GB | unknown, no measurable time; `0 < g_k` costs 8·2^k + 10k + 1 |
| B-4, a reused 65,537-bit value | holds in 999,001 units after 107 s | unknown within a second; under (a) and (b) alone, 29 s |

**How the numbers were measured.**
- Times are wall times of `lake env lean` (interpreted) on the VM, beyond the stub's 1.3 s load time. Draft 4's B-4
  time comes from a scratch file that imports `VE.Arith.BoundedExamples` and runs B-4's definitions on the merged
  evaluator.
- The "(a) and (b) alone" variant is the stub with five edits:
  - `var`, `num`, `call` and `count` yield without `chargeBits`;
  - `stepB` is `cond i w`.
- Each derivation in 13.3 matches the evaluator: M-5's 33, B-1's recurrence (12,273) and B-3's closed form (95,
  524,449, 1,048,747). So do `prime 7` = 85, the empty count = 9 and `f2(1)` = 55.
- The cost of the extension is that every count grows by about 20 times, because each read of a small value now costs
  1 plus its bits. As a result, M-4's bounded range shrinks from 248 to 87.

## Build plan for me-12nb (Lean only; no Python or Rust)

**Files.**
- `lean/VE/Arith/Bounded.lean` (about +120 lines):
  - add `bits`, `chargeBits` and `stepB`, and restate `Term.evalB` as in 12.2;
  - copy the stub's proofs of `Term.evalB_bits` and the `bits_*_le` lemmas;
  - re-prove `Term.evalB_sound`, `Formula.evalB_sound`, `_mono`, `_total`, `decideBounded_covered` and
    `decideBounded_complete`. Each term clause gains `charge_some` and a `chargeBits_some` lemma; `stepB` needs a
    small `stepB_some` lemma and a mono lemma, and `Total`'s W gains the bits;
  - update the module doc ("term nodes are free").
- `lean/VE/Arith/BoundedExamples.lean` (about ±70 lines):
  - recompute every units guard: `:14`, `:19-28`, `:35-69` and the clause fixtures `:75-124`;
  - flip the N1 pin `:125-130` to B-1;
  - add B-2, B-2p, B-3 and B-4 from the stub;
  - test M-2 and `big 3` one unit over their boundaries (me-12aa review F3).
- `lean/ARITH.md`: the budget paragraph and N1.
- `lean/VE/Audit.lean`: list `Term.evalB_bits`.
- `tools/trust-classes.json`: classes for the new names, then `regen_generated.py --write`.

**Seeded bugs (Lean).** S1 to S5 below, planted in `Bounded.lean`, must each fail a `BoundedExamples.lean` guard, or
`Term.evalB_bits`' proof for S4. A new trusted definition also gets a trust-mutants run.

**Expected trust under R16.**
- `Bounded.lean`: K +0, S +0. `bits`, `chargeBits` and `stepB` are C, tied to `decideBounded_sound`/`_work` and
  `Term.evalB_bits` as the evaluator is (me-12aa: the evaluator is C), so untied V +0. If `bits` is classed V, the
  growth is +1 to +3 lines, within 150.
- `BoundedExamples.lean`: T.
- me-12b then writes R-7's units, 337,735 and 33 (12.2).

## Seeded bugs (this item; each planted alone in a copy of the stub, then removed)

| Bug | Edit in `docs/spec/math-evidence/me-12n-budget-stub.lean` | What fails |
|---|---|---|
| S1 | `var` yields without `chargeBits` | `Term.evalB_bits` (`:168`); guards `:216` (`prime 7`), `:218`, `:221` (M-1) |
| S2 | `stepB` does not charge the bound value | guards `:216`, `:221`, `:223` (M-2), `:224` (M-5) |
| S3 | `mul` yields without `chargeBits` | `Term.evalB_bits` (`:168`); guards `:221`, `:223`, `:224` |
| S4 | `chargeBits` refuses only when `limit < w` | `chargeBits_some` (`:156`); guards `:221`, `:223`, `:224` |
| S5 | a function call costs no visit | guards `:227`, `:228` (M-4's instances), `:232` (bounds), `:237` |

Every claimed behaviour has a bug that a guard or proof catches: the visit charge (S5), the yield charge (S1, S3), the
step charge (S2) and the refusal before the budget is passed (S4). No product code changed, so there is no Python,
Rust or product-Lean seeded bug.

## Trust, tests, size and overlap

- **Trust.** `uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0, trusted +0, PASS. There is no R16 row
  and no FOLLOW-UPS row.
- **Tests.** `mac-pytest.sh --select` selected 146 of 471 units for the two changed documents. All 146 passed (0
  failed, exit 0); the run fell back to the VM and took 4,138 s. It ran on the tree of 5e5939d54; the later commits
  change only prose in 12.2 and this report. The stub check gives 0 errors and all guards pass, in 50 s. The full
  gate was not run here: the chain runs it on the final HEAD.
- **Size.** 133 + 28 lines in the spec, 266 in the stub (evidence) and this report: 544 + 28 lines in all, under
  600.
- **Overlap.**
  - Hand-written files: `docs/spec/math-evidence.md`, the stub and this report.
  - Of the in-flight branches, only `foundation/me-1` (last commit 2026-10-15, not merged) touches the spec: it adds
    draft 4's whole file, copied verbatim before main had it. That branch is stale, not a queue conflict.
  - No `lean/`, `ve/` or `tools/` file changed.
- **Bytes.** 0 (the use-case ceiling, ME-P4); this item claims no pilot movement.

**Next:** me-12nb (the build in `Bounded.lean`), then me-12ac and me-12b.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or relay changed.
2. PASS: parts (a) to (f) are in the table above with their places, and the diff contains no new Python copy of a
   Lean decision and no new permanent report test.
3. PASS: seeded bugs S1 to S5 each fail a stub guard or proof, as listed above. No trusted Lean was added
   (`trust_map.py --check`: +0).
4. N.A.: no Python, Lean or Rust behaviour changed.
5. N.A.: no relay field.
6. PASS: the gate's evidence is the chain's run on the final HEAD; this item writes no evidence numbers from
   `git diff`.
7. PASS: no DELTA row, and trust +0 (`trust_map.py --check`).
8. N.A.: there is no user-visible change until me-12nb; 12.2 names the text that me-12nb and me-12b reread.
9. PASS: `select_tests.py --base 6b5d6cbb6` selects 146 of 471 units, not every unit.
10. PASS: `Term.evalB_bits` and `chargeBits_some` fail under S1, S3 and S4; the restated theorems carry `sorry` only
    in the stub, as the task allows.
11. PASS: budget 0 and small budgets are UNKNOWN in the stub (B-1 at 1 and 1,000, M-4x, M-1b, M-5 at 32), and each
    boundary is tested under, at and over.
12. PASS: B-2, B-2p, B-3 and B-4 are the step-count fixtures for the CPU and memory class. Each is UNKNOWN at
    1,000,000 units (stub `:239-264`).
13. N.A.: no test was removed or renamed.
