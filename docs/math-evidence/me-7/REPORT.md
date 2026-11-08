# me-7 report: exact statistics (ME-7, first part)

- **Status:** ready for review. Evidence HEAD `123e24e12` (trust mutants, selected tests); later commits change only
  `docs/math-evidence/me-7/` and the generated codemap.
- **What changed:** `lean/VE/Calc/Stats.lean` has spec 7's statistics with every theorem of spec 7 proved and a
  charged sign flip; ME-4's `Agg` gains `variance` and `populationVariance`; fixtures as `#guard`s and a test.
- **Open:** me-7b (the `Expr`/`Claim` constructors, their meaning clauses and the domains that live in `Denotes`).
  A DRI question on `signFlipC` (statement gate, below) is in `inbox/dri/20261102T112838Z-me-7-1637463.md`.
- **Signatures:** none reserved. Trust S +84, K +0, under R16 (DELTA row 1).

## Plan rows and task deliverables

Plan `docs/spec/math-evidence-PLAN.md` "ME-7. Exact statistics"; spec `docs/spec/math-evidence.md` section 7 (the
task's "3.6") and 2.1, 2.2, 4.2. The synthesis-2 edits implement none of their five items here; edit 4 (budgets) holds:
`signFlipC`'s limit is Lean work units, separate from the Rust 5 s wall limit and `VE.SearchBudget`.

| Plan row or task line | Delivered | Where |
|---|---|---|
| New files `lean/VE/Calc/Stats.lean`, `tests/test_calc_stats.py` | yes | `6a47d9056`, `29b5ac8ff` |
| Proves 3.6 (spec 7) | yes | `sqrtRoundsTo_of_square`, `signs_length`, `mem_signs`, `signFlipP_grain`, `choose_succ_succ`, `binomialTail_zero`, `binomialTail_unit`, `Stat.run_isSome`; 25 of 25 declarations verbatim (`evidence/check_statements.py`, output in `check_statements.txt`) |
| (1) meanings: mean, sample and population variance, SD by squared bounds (`SqrtRoundsTo`), sign flip by 2ⁿ signs charged against a stated limit, binomial tail, kappa of a 2 × 2 table, `choose` with `choose_succ_succ`, `signFlipP_grain` for ME-8 | yes | `Stats.lean`; the limit: `maxSignFlip` = 16 (spec 7's decode limit), `signFlipWork n = n + 2ⁿ(n + 1)`, `signFlipC` (none, UNKNOWN, past the limit), `signFlipC_sound`, `signFlipC_complete` |
| Domains in the meaning, undefined outside them (J5) | partly | `Stat.run` (`Stat.run_isSome`), `kappa?`'s none, `SqrtRoundsTo`'s `0 ≤ v`; binomial's 0 ≤ p ≤ 1 and the root's v ≥ 0 as undefined, not false, are `Denotes.binom` and `Claim.Defined` clauses: **me-7b** |
| (2) `stat`, `binom`, `kappa`, `sqrtRounds` in ME-1's `Expr`/`Claim`, meaning clauses, ME-1's theorems re-proved | **no: me-7b** | size: they force arms in 12 `lean/VE/Calc/` files (Decls' 224-line `evalL_causes` among them) |
| Assumption leaves per procedure (2.8) | **no: me-7b** | the residual lines hang on the claim constructors and the runner |
| (3) `variance`, `populationVariance` in ME-4's `Agg` | yes | `Table.lean`, `Data.lean` (`Agg.columns`); `mean?` moved to `Stats.lean` so that me-7b's `Syntax.lean` can import it |
| (4) V-6 (holds × 3), V-6r (fails, 0.103 only) | yes | `StatsExamples.lean:19-23`; test ids `v6-*`, `v6r-*` |
| S-5, both sides of each domain | partly | `Stat.run` of 0, 1, 2 values, `kappa?` empty and pe = 1, unguarded `binomialTail 10 8 2` = 7,424, `binomialTail 1 1 2` = 2, `signFlipP []` = 1 (`:61-62`, `:72-77`); the wire forms' undefined verdicts are me-7b |
| Sign-flip p over 12 synthetic differences against a hand enumeration | yes | nine +1, three −1: 2 · (1 + 12 + 66 + 220) = 598 of 4,096 (`:44-47`); `sign-flip-synthetic` and `sign-flip-v6` against an exhaustive enumeration in the test |
| A binomial tail; a kappa of a 2 × 2 table | yes | 7/128 (`:60`), κ = 2/5 (`:66`); `binomial-third` against `math.comb` |
| Seeded bug: the sample variance divides by n | yes | S1 below |
| Evaluator rule (2026-10-27): each value read once, size charged against a stated limit, a large request within it | no (corrected by me-7-signflip-bits) | `signFlipC` charged before it runs, but `signFlipWork` counted the list's length only (`n + 2ⁿ (n + 1)`, 1,114,128 units for 16 values), not 12.2's unit with each value's bits, so it under-charged: large values were admitted far over `maxWork` (me-7-review-ov F1). me-7-signflip-bits charges the bits (`docs/math-evidence/me-7-signflip-bits/REPORT.md`). The binomial and kappa charges come with the `evalC` arms (me-7b) |

**Statement gate.** Spec 7 is the accepted 3.6 (ME-S statement review, cited in me-5e's REPORT). Every meaning is
spec 7's text. `maxSignFlip`, `signFlipWork`, `signFlipC` and the two `signFlipC_*` theorems are not in spec 7; they
are untrusted (G[R], C) and tie `signFlipC` to `signFlipP`. The task asks for the charge, so I asked the DRI decider
whether they stay here or move to me-7b (message above); nothing else waits on it.

## Seeded bugs (Lean; no Python or Rust product code changed)

Each was planted, shown to fail, and restored; `mutants.json` has the same list.

| # | File, definition | Bug | Fails |
|---|---|---|---|
| S1 | `Stats.lean`, `sampleVariance?` | divides by n (plan's) | `#guard StatsExamples.lean:20`, `:21` (SD rounds to 0.103) |
| S2 | `Stats.lean`, `signFlipP` | observed vector not counted (`<`) | `:47`, `:48` |
| S3 | `Stats.lean`, `binomialTail` | sums i > k | proofs break; cut to `sorry`, `:60`, `:62` fail |
| S4 | `Stats.lean`, `kappa?` | divides by 1 + pe | `:66`, `:69` |
| S5 | `Table.lean`, `Agg.run` | variance runs the population variance | `:82` |
| S6 | `Stats.lean`, `signFlipWork` | charge 2ⁿ, not 2ⁿ(n + 1) | `:55`, `:56` |
| S7 | `Stats.lean`, `SqrtRoundsTo` | ties up admits the upper tie | proof breaks; cut to `sorry`, `:27`, `:31`, `:35` fail |

**Trust mutants** (`mac-pytest.sh --trustmut -- --max-mutants 1000 --allow ... --json ...`, cloud run of
`123e24e12`, exit 0): 389 mutants over 19 definitions: 212 KILLED, 145 ALLOWED, 32 INVALID. The allowed ones are of
three kinds, each line's reason in `trust-mutants-allow.json`: refuted by the guard the UNKNOWN names, but read through
a `Decidable` instance Lean rebuilds from the mutated body (`SqrtRoundsTo`, the five root bounds; as in ap-1d, df-2,
sc-2d); 8 equivalent survivors (e.g. `xs ≤ []` is `xs = []`, `n + 2` adds a 0 term); and mutants that do not
elaborate. The first run (before the root bounds' instances unfolded their body) had 15 more UNKNOWN there.

## Tests

- `uv run pytest -q tests/test_calc_stats.py`: 26 passed.
- Selected tests, once, on the finished code (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`):
  422 of 529 units, exit 0, 0 failed, at `123e24e1` (`evidence/selected-tests.txt`). Nothing from
  `main-known-red.txt` was hit.
- `lake build` (1,233 jobs) and `python3 lean/audit.py` (PASS, 726 files): once, after the regeneration.
- The full gate: not run here (the chain runs it on the final HEAD).

## Trust, size, bytes

- `uv run python tools/trust_map.py --check`: K +0, S +84, untied V +0; PASS with the R16 allowance (DELTA row 1).
- Size (`git diff --numstat $(git merge-base HEAD main)`, hand-written): Lean 391 (`Stats.lean` 297, of which about
  150 are proofs; `StatsExamples.lean` 86; Table, Data and the import list 8), test 130, `tools/trust-classes.json` 51,
  trust baseline 7, allow file 66, statement check 30, DELTA 11, this report about 100: about 790, over the ~600
  guide (`mutants.json` and the trust-mutant JSON are evidence data, not counted). The cut is the constructors
  (me-7b); what remains is one part that passes its own fixtures, mutants and seeded bugs.
- Pilot bytes expected: 0 (plan "Bytes: 0"). Nothing is claimed.

## Spec re-read

- `Stat`, `Stat.minLength`, `Stat.run` against `docs/spec/math-evidence.md:331-333`, `:1744-1754`.
- `SqrtRoundsTo`, the root bounds, `signFlipP`, `binomialTail`, `kappa?` against `:1661-1757` (script above).
- `Agg` and `Agg.run` against `:1273-1284` (4.2, "from ME-7").
- The 16-value limit against `:1766-1767` and `:3379`.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed (no route or schema).
2. PASS: plan rows above, each with its commit or me-7b; no Python copy of a Lean decision (`git diff --stat` shows
   no `ve/` file); no report test; no file of an in-flight branch but the union-merged `lean/VE.lean`.
3. PASS: S1 to S7 and the trust mutants (exit 0); the statement check fails on a changed `Stat.minLength` (exit 1).
4. N.A.: no Python or Rust path changes; Lean answers are new and read by no other language yet.
5. N.A.: no relayed field.
6. PASS: selected tests at `123e24e1`; the chain gates the final HEAD.
7. PASS: DELTA row 1 cites R16 with its evidence; no other unsigned item.
8. PASS: no public output changes (DELTA "none" beyond trust).
9. PASS: the selection holds `tests/test_calc_stats.py` (`tools/select_tests.py --base ...`, 422 units).
10. PASS: `check_statements.py` 25 of 25; S3 and S7 break `binomialTail_zero`, `binomialTail_unit`,
    `sqrtRoundsTo_of_square`.
11. PASS: `signFlipC 0 [] = none` and one unit short of 16 values is none (`:56-57`).
12. PASS: no service path changes; the 2ⁿ enumeration is charged and capped (S6 catches a smaller charge).
13. N.A.: no test removed or renamed.
14. PASS: both directions in every guard (in and out of each domain, each side of each bound); claims cite commands.

Next: me-7b, then ME-8 (it uses `signFlipP_grain`), then ME-P3.
