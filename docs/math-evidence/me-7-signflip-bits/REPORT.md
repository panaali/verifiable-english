# me-7-signflip-bits: the sign flip charged its value bits (12.2's unit)

`signFlipWork` counted only the list's length (`n + 2ⁿ (n + 1)`), so large values ran far over `Work.maxWork`
(me-7-review-ov F1). It now takes the list and charges 12.2's unit (one per value plus its bits), never less than the run.
`signFlipC` charges it before it evaluates. Sixteen 2,000-bit integers and twelve 1,000-bit numerators over 2,000-bit
denominators, which the length-only charge admitted, are now refused (UNKNOWN). Sixteen 1s still end within `maxWork`.
Trust growth is 0 (the charge is class C). No route reads `signFlipC`, so no CLI verdict changes. Bytes 0.

Task: `prompts/task-me-7-signflip-bits.txt` (rank 3; exposure ruling reviews/dri-decisions-20261105-adv0031-apply.md
item 2; regrade reviews/dri-decisions-20261105-cfr2.md #21). The governing statement is
docs/spec/math-evidence.md 12.2's unit (accepted), restored by syn2-math-evidence edit 4 (budgets).

## Delivered

| Task row | Done | Where |
|---|---|---|
| (1) A conservative bits-aware charge, charged before evaluation | yes | `lean/VE/Calc/Stats.lean:146-158` (`signFlipWork d`), `:161-162` (`signFlipC` checks it first) |
| (2) `signFlipC_sound` / `signFlipC_complete` re-proved | yes | `Stats.lean:164-170`; same proofs, only the work term changes |
| (3) #guards: a large-rational case that is refused, d16 at the new numbers, the boundary | yes | `lean/VE/Calc/StatsExamples.lean:56-58` (d16, the empty list), `:65-67` (big16, big12, the boundary of big12) |
| (3) The same cases in tests/test_calc_stats.py | yes | `sign-flip-16`, `sign-flip-short`, `sign-flip-empty`, `sign-flip-big16`, `sign-flip-big12`; `test_sign_flip_charge_covers_work` (5 cases) |
| (4) Correct docs/math-evidence/me-7/REPORT.md:31 | yes | the row now reads "no (corrected by me-7-signflip-bits)" and says the old charge under-charged |

## The charge

`signFlipWork d = (2ⁿ + 2) · (4n + 8) · (A + 2 · bits L + 2n + 3)`. Here `n` is the length, `A` the largest
numerator's `bits`, and `L` the least common multiple of the denominators. `bits` is `VE.Numbers.bits`, the same
`bits` that `Work.qbits` reads.

- **Rows.** There are 2ⁿ sign vectors, plus one row for the observed mean and one for the values read and the final
  share.
- **Values per row.** At most `4n + 8`: per value a sign, its entry in the vector, a product and a running sum, then
  the length, the mean, its absolute value, the comparison and the filter's decision. One row of the run takes
  `3n + 6`.
- **Size per value.** One visit plus at most `A + 2 · bits L + 2n + 2` bits:
  - a running sum's denominator divides `L`;
  - its numerator is `Σ aᵢ · (L / bᵢ)`, below `n · 2^A · L`, so it has at most `A + bits L + n` bits;
  - dividing by `n` adds `bits n ≤ n + 1` bits to the denominator;
  - a product `±xᵢ` has `qbits xᵢ ≤ A + bits L` bits.
- **Why the lcm.** The lcm, not the sum of the denominators' bits, keeps plain decimals cheap: thousandths cost
  10 bits, not 10 per value. Coprime denominators still cost all their bits (big12: about 24,000).

**Checked against a run.** `test_sign_flip_charge_covers_work` runs the sign flip in Python with exact fractions. It
charges every value computed one plus its `qbits`, and asserts that Lean's charge is at least that count and at most
16 times it. Measured ratios: d12 12.4, v6 6.9, the 12 synthetic values 8.3, six coprime 2,000-bit denominators 5.9,
eight prime denominators 6.0.

| Case | Old charge | New charge | `maxWork` = 8,589,934,592 |
|---|---|---|---|
| sixteen 1s (`d16`) | 1,114,128 | 179,311,968 | within; 179,311,967 refuses |
| `[]` | 1 | 120 | 119 refuses; budget 0 refuses `d16` (`:58`) |
| sixteen 2,000-bit integers (`big16`) | 1,114,128 | 9,612,065,232 | refused (was admitted) |
| twelve 1,000-bit numerators over 2,000-bit odd denominators (`big12`) | 53,260 | 11,241,469,680 | refused (was admitted); 11,241,469,680 admits, one less refuses |

## Changed statements (before → after)

- `signFlipWork (n : Nat) : Nat` → `signFlipWork (d : List Rat) : Nat` (a definition, class C).
- `signFlipC_sound`: `… → q = signFlipP d ∧ w = signFlipWork d.length ∧ w ≤ limit` →
  `… → q = signFlipP d ∧ w = signFlipWork d ∧ w ≤ limit`.
- `signFlipC_complete`: `(h : signFlipWork d.length ≤ limit) : signFlipC limit d = some (signFlipP d, signFlipWork
  d.length)` → `(h : signFlipWork d ≤ limit) : signFlipC limit d = some (signFlipP d, signFlipWork d)`.

The task names these two theorems as changing. No other approved statement changes; `lean/statements.txt` changes in
these two only (regenerated).

## Seeded bugs (docs/math-evidence/me-7-signflip-bits/mutants.json)

All are Lean, in `lean/VE/Calc/Stats.lean`, the only product file changed. No Python or Rust product code changed.
Guard lines are `lean/VE/Calc/StatsExamples.lean`'s.

| Id | Bug | Caught by |
|---|---|---|
| M1 | charge reverted to the length only | #guards `:56`, `:57`, `:58`, `:65`, `:66` (large-rational, refused), `:67`; with those guards commented out, `test_fixture[sign-flip-16/-short/-empty/-big16/-big12]` and `test_sign_flip_charge_covers_work[d12/v6/synthetic/coprime/primes]` fail (10 failed) |
| M2 | denominator bits dropped (`0 * bits L`) | #guard `:66` (big12, large denominators) and `:67`, with `:56`-`:58`, `:65` |
| M3 | numerator bits dropped (`0 * A`) | #guard `:65` (big16), with `:56`, `:57`, `:66`, `:67` |
| M4 | the limit check made strict in `signFlipC` | `signFlipC_sound` and `signFlipC_complete` no longer prove (unsolved goals at `Stats.lean:165`, `:169`) |
| M5 | denominators' maximum instead of their lcm | #guards `:66`, `:67` (big12) |

## Trust, DELTA, size

- **Trust.** `tools/trust_map.py --check` on the final tree: K +0, S +0, D +0, G +0, unclassified +0, trusted +0.
  `signFlipWork` and `signFlipC` are class C (checked executables), and the new fixtures `big12`/`big16` are T
  (`tools/trust-classes.json`). No S line changed, so no R16 allowance and no FOLLOW-UPS ties row were needed.
- **DELTA.** None. `signFlipC` is read by no route or CLI mode (`Expr` has no `.stat` arm until me-7b), so no CLI
  verdict changes; no DELTA.md.
- **Size.** `git diff --numstat e9a6ec8d5`, hand-written: Stats.lean +18 −6, StatsExamples.lean +14 −4,
  tests/test_calc_stats.py +55 −5, me-7 REPORT +1 −1, trust-classes.json +2. That is 90 added and 16 removed outside
  this report and mutants.json. Generated: `lean/statements.txt`, `lean/declarations.txt`, docs/codemap (main's lag,
  regenerated).

## Tests run (final code)

- `lake build`: all 1,311 jobs passed, which includes every StatsExamples #guard.
- `python3 lean/audit.py`: PASS, 780 source files, 8,635 theorems audited.
- `uv run pytest -q tests/test_calc_stats.py`: 34 passed.
- `uv run python tools/regen_generated.py --check`: rc 0, 35 entries.
- `uv run python tools/gate_collection.py --check --prebuilt`: 8 added, 0 removed, 0 refused, 0 stale.
- `mac-pytest.sh --select -- --base e9a6ec8d5 --run` on HEAD 34bdfad7, ve-mac-1:
  - exit 0; 105 of 547 test units selected, 0 failed ids, test_calc_stats.py among them;
  - two heavy files were deferred to the chain gate (test_safety_framework.py, test_test_chunks.py).
- The only later change is the budget-0 conjunct on `:58` and its `sign-flip-empty` entry, rerun with the two
  file-level checks above.
- Known-red on main (main-known-red.txt): none touch these files.

## Pilot bytes and next item

Pilot bytes: 0 (the charge only refuses oversized sign flips; no pilot document states one).
Next: ME-8 (consistency of printed numbers) uses the corrected charge.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained answers: N.A. No route, relay or schema changes; `signFlipC` is read by no service mode.
2. Deliverables: PASS. Every task row is in "Delivered" with its file and test. No Python copy of a Lean decision:
   `counted_work` in the test is an oracle that runs the sign flip, not the charge. No in-flight branch edits these
   files (checked with `git diff --name-only main...<branch>` for every lean-first/feature/infra/foundation branch).
3. Tests can fail: PASS. M1-M5 in mutants.json, each with its failing #guard or theorem; M1 is also caught by 10
   pytest ids alone. No R16 growth, so trust_mutants are not required.
4. Python, Lean and Rust agree: N.A. No Python or Rust product code changed. The Python oracle agrees with Lean in
   `test_sign_flip_charge_covers_work`.
5. R8 binding: N.A. No relayed field is added.
6. Gate evidence: PASS. The chain runs the gate on the final HEAD; this report reads no live git.
7. Unsigned items: PASS. There is no DELTA row and no trust growth (`trust_map.py --check`: K, S, D, G +0).
8. DELTA: PASS (none). No CLI mode reaches `signFlipC` (grep: only Stats, StatsExamples, Audit and the test).
9. Test selection: PASS. The selection run listed `tests/test_calc_stats.py` as changed and ran it.
10. Statements: PASS. The two changed statements are listed before and after. M4 shows the proofs break when
    `signFlipC` changes. Spec re-read: 12.2's unit against docs/spec/math-evidence.md:836-838 (one per node plus
    each value's bits, a rational's numerator and denominator bits), and `signFlipC` charges before evaluation
    (:839).
11. Budgets fail closed: PASS. The charge is tested both ways:
    - refusals: budget 0 refuses `d16` (`:58`, `sign-flip-empty`); one unit short refuses (`:57`, `:58`, `:67`);
    - acceptances: the exact charge admits (`:57`, `:58`, `:67`);
    - oversized cases end at once as UNKNOWN, because the charge comes before the 2ⁿ enumeration (`:65`, `:66`).
12. CPU and memory: PASS. The charge is computed in one pass before the enumeration, and refuses the large cases
    without enumerating them. StatsExamples builds in about 4 s.
13. Test-removed trailers: N.A. No test is removed (`gate_collection.py --check --prebuilt`: 0 removed, 0 stale).
14. Both directions and cited evidence: PASS. Every refusal case has its admitted twin (`:57`/`:58`/`:67`). Each
    claim above names its command.
15. Overclaim, silent cut, every check can fail, limits charged first: PASS.
    - "never below its work" is checked on five cases by `test_sign_flip_charge_covers_work`. It is argued, not
      proved in Lean.
    - Nothing is cut.
    - Every new #guard (`:56`-`:58`, `:65`-`:67`) breaks under M1, M2 or M3.
    - `signFlipC` charges before it evaluates (M4, `:65`).
