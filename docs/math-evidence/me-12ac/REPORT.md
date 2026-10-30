# me-12ac report: the deciding value and M-6

Status: done, ready for review. Lean only, new files only. Trust +0, DELTA has no row, and no DRI signature is reserved.
`decidingValue` (spec 12.5) and its three theorems are proved. Each theorem equals 12.5's text. M-6 is a `#guard`:
401 values agree and 78 are prime. 3 seeded bugs and 4 definition mutants, 7 of 7 killed.
Open: one finding for me-12b (F1, an unbounded row with a deciding value). Next: me-12b.

Base `62d8329d4` (`git merge-base HEAD main`); commits `git log --oneline --no-merges main..HEAD`. There is no Python,
Rust, mode, route or public output. This item implements no edit of the synthesis round 2 file
(`debates/plan-synthesis-2/edits-math-evidence.md`): its edits 1–5 are plan wording for me-2nb, me-12b and ME-11.
Its closing note names this item's scope (parts (3) and (4) of me-12ab), and that is what this item delivers.

**Statement gate.** ME-S passed (manage-agents math-evidence-p3ver1.final.md, then math-evidence-p3ver2.final.md:
PASS). A scratch script took each theorem from `theorem` to its `:=` and collapsed whitespace, in both the spec and
`Deciding.lean`. `decidingValue_all`, `decidingValue_ex` and `decidingValue_of_fails` each printed EQUAL against
spec 12.5 (`docs/spec/math-evidence.md:2701`, `:2707`, `:2713`). So did `decidingValue`'s signature (`:2677`).
`uv run python tools/lean_statements.py --check`: "added: 0, removed: 0, changed: 0 … PASS". No statement is false.

## Delivered (task order)

| Task row | Delivered | Proof or test |
|---|---|---|
| (1) `decidingValue`, the first decisive value of the outermost bounded quantifier, as a loop shaped like `quantLoop` that returns the index where it stops early | yes. `decidingLoop` is `quantLoop` with `some (i, w')` where `quantLoop` returns `some (!universal, w')`, and none where it completes. `decidingAt` is `Formula.evalB`'s visit of an `allFromTo` or `exFromTo` node at the top of a statement, with `decidingLoop` in place of `quantLoop`. `decidingValue` is it on those two nodes, else none | `Deciding.lean:13-35` |
| (2) `decidingValue_all`, `decidingValue_ex` through `Formula.evalB_sound` and `agrees_env` | yes. `decidingLoop_sound` covers the loop: the value lies in the range, its step disagrees with `universal`, and every earlier step agrees. `decidingAt_sound` joins it to the meaning through `agrees_env`, `Term.evalB_sound` (the range's ends), `stepB_sound` and `Formula.evalB_sound` (the body). The two theorems specialise it. `hD` and `hφ` are unused, as in `decideBounded_sound` | `Deciding.lean:38-122`; `lake build` PASS; `DecidingExamples.lean:87-91` applies `decidingValue_all` to M-5 |
| (2) `decidingValue_of_fails` from `quantLoop` returning false exactly when that loop stops | yes. `decidingLoop_iff`: `decidingLoop` returns some value with units w' exactly when `quantLoop` returns `(!u, w')`. Both directions are proved | `Deciding.lean:64-77, 124-148` |
| (3) M-6: VE's `prime` against `IsPrime` on 0 … 400 (78 primes), with a `Decidable` instance for `IsPrime` proved equal to it | yes. `isPrimeB` (`isPrimeB_iff : isPrimeB p = true ↔ IsPrime p`) and `instance decIsPrime := decidable_of_iff _ (isPrimeB_iff p)`. `#guard agreeCount primeDefs 401 = (401, 78)` checks VE's `prime` by the evaluator (`decideBounded`, default budget) at every value. The refusing side: a body that also tries p itself disagrees at each of the 78 primes, `(323, 78)` | `DecidingExamples.lean:10-35` |
| (4) seeded bugs: last decisive value, off-by-one start, M-6's range cut to 0 … 399; one mutant per new trusted definition | yes, 7 of 7 killed (below) | [`mutants.json`](mutants.json) |
| Fixtures on both sides of each check, at and around each boundary | yes (next table) | `DecidingExamples.lean` |
| `lean/VE.lean`, `lean/ARITH.md` | two imports; the two files and the three theorems in plain words | — |

Fixtures (`DecidingExamples.lean`; `lake build` checks them; each line was checked in one `lake env lean` run):

| Check | Deciding side | Undecided side |
|---|---|---|
| first witness (∃) | 8 … 20 gives 11, not 19 (`:54`); at lo, 2 … 20 gives 2; at hi, 14 … 17 gives 17; 7 … 7 gives 7; ends given by terms, (3 + 1) … (2 · 4) gives 5 | 8 … 8 and 8 … 10 (no prime) give none |
| first counterexample (∀) | 1 … 10 at most 6 gives 7, not 10 (`:60`); at hi, 10; at lo, 3 (`:62`); negatives, −3 … 3 at most −2 gives −1, and ∃ −3 … 3 below 0 gives −3 (`:63`) | 1 … 9 at most 9 gives none |
| range ends | the one-value ranges above | the empty range 5 … 4 of either quantifier gives none (`:67`) |
| outermost node | `allFromTo` and `exFromTo` at the top | `not`, `and` around M-5, a call and `allNat` give none (`:67`) |
| budget | M-5: none at 32 units, 1 at 33, 34 and 1,000,000 (`:50`). At every budget from 0 up to past each statement's work, there is a deciding value exactly when the evaluator stops early (`agreesUpTo`, `:73`, each sweep past its work: M-5 33 units, 8 … 20 322, 1 … 10 84, M-1 to 4 324 (true), 8 … 10 165 (false)) | as before |
| `decidingValue_of_fails` | M-5 fails at 33 and has its value (`:78`) | M-5 unknown at 32 and M-1 holding at 161 have none (`:79-80`) |
| M-6 | VE's `prime` agrees at 401 values, 78 prime (`:33`); `IsPrime` at 0, 1, 2, 3, 4, 397, 399, 400 (`:21`) | the off-by-one body disagrees at all 78 primes (`:34`) |

## Findings

- **F1, for me-12b.** `decidingValue` does not read boundedness, and neither does spec 12.5's definition. A statement
  whose evaluation stops early before it reaches an unbounded part therefore has a deciding value, though
  `arithOutcome` calls it "stated, not decided". The fixture is
  `∀ n from 1 through 3, n ≤ 0 and (for every whole number m, 0 ≤ m)`: deciding value 1, and the row is
  `unknown .unboundedStatement` (`DecidingExamples.lean:84`). The theorems still hold, since they speak of the meaning.
  The row should show `deciding` only on a decided outcome. Spec 12.5's rows text implies this ("with the deciding
  value, M-5's row says 'fails at n = 1'"). Neither the relay check nor `Run.deciding_sound` states it, so me-12b
  should state it in its runner.
- **M-6 and π(399).** π(399) = π(400) = 78, so a count of primes alone cannot catch the range cut to 0 … 399. The guard
  also counts the values that agree (401), and S3 breaks that count.

## Trust

`uv run python tools/trust_map.py --check --since 62d8329d4`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0,
trusted +0 … PASS". New executables are C (`tools/trust-classes.json`); fixtures are T; theorems are P. No allowance,
so no R16 row and no FOLLOW-UPS ties-pass row (sibling lesson me-5e F1 checked: no R16 signature is claimed). `mac-pytest.sh
--trustmut -- --max-mutants 1000 --json docs/math-evidence/me-12ac/trust-mutants.json` (run in the cloud pool):
"0 definitions, 0 mutants … 0 KILLED, 0 SURVIVOR", exit 0. It was rerun with `--rescore` after the last fixture edit
("check-only change: lean/VE/Arith/DecidingExamples.lean"), again 0 definitions, exit 0.

## Seeded bugs and mutants (Lean; [`mutants.json`](mutants.json))

Each was planted alone in a copy of `Deciding.lean` joined with `DecidingExamples.lean`, and checked by one
`lake env lean` run on that file. The control has no error. **7 of 7 are killed.**

- **S1** `decidingLoop` returns the last decisive value: breaks `decidingLoop_sound` and `decidingLoop_iff`; fails
  `DecidingExamples.lean:54` (19 for 11), `:60`, `:63`, `:84`.
- **S2** `decidingAt` starts at lo + 1: breaks `decidingAt_sound` and `decidingValue_of_fails`; fails `:50` (M-5),
  `:54`, `:60`, `:62`, `:63`, `:67`, `:73`, `:78`, `:84` and the `decide` at `:90`.
- **S3** M-6's range cut to 0 … 399: fails `:33` ((400, 78) for (401, 78)).
- **D1** `decidingValue` reads an existential as a universal: breaks `decidingValue_ex`; fails `:54`, `:63`, `:67`, `:73`.
- **D2** `isPrimeB` starts its divisors at 3: breaks `isPrimeB_iff`; fails `:21`, `:33`, `:34`.
- **D3** `decIsPrime` says 2 is not prime (this needs a `sorry`, because the instance's type is its own proof):
  fails `:21`, `:33`, `:34`.
- **D4** `vePrime` (T) within 1,000 units: fails `:33`.

## Tests and checks

- **Selected tests:** `mac-pytest.sh --select -- --base 62d8329d4 --run` on HEAD a4bafc808 (clean) ran on GitHub Actions
  (run me-12ac-a4bafc80-t346792, 6 shards). It ran 427 units (79 + 70 + 71 + 72 + 69 + 66), 427 passed and 0 failed,
  exit 0, in 2,857 s. The item adds no pytest file. Its tests are the Lean guards and proofs that `lake build` checks.
- **Checks on the final code:** `lake build` of the whole library passes (1,163 jobs). `python3 lean/audit.py`
  passes ("672 source files; 7503 named theorem declarations"), and so do `lean_statements.py --check`,
  `repo_map.py --check` ("39 modes") and `trust_map.py --check`. `regen_generated.py --write --skip route-cases`
  wrote 33 entries; `route-cases` needs the Rust release binary, and no route changed. It also refreshed codemap
  pages that main had left stale. `gate_collection.py --check --prebuilt` reports 0 added, 0 removed, 0 refused,
  0 stale and 0 malformed.
- **Not run:** the full gate. The chain runs it on the final HEAD.

Shared files: `lean/VE.lean` (two imports, union) and `tools/trust-classes.json` (two new file keys). In-flight
branches that touch them: `feature/rd9-docroute`, `foundation/me-1` and `infra/scale-lean-memo` (both files);
`feature/qt-a3d` and `infra/usecase-safetyfw-b` (`trust-classes.json`). `feature/me-2nb` edits `Bounded.lean`, which
this item does not edit. No in-flight branch touches `Deciding*.lean` or `lean/ARITH.md`.

**Size:** 270 hand-written lines of Lean, ARITH.md and side table (`git diff --numstat`), plus this report, DELTA and
`mutants.json`. **Bytes:** 0 expected (use-case ceiling, ME-P4); nothing is claimed before a pilot audit.

## Next item

- **me-12b** (protocol queue after AP-4, only after me-12nc merges, DRI 2026-10-27): the wire, runner, rows, encoder
  and mode. `Run.deciding_sound` reads `decidingValue` as delivered here. Its runner shows `deciding` only on a
  decided outcome (F1). No me-12ad is needed: all of me-12ac's scope fits.

## Spec re-read

- `decidingValue` against `docs/spec/math-evidence.md:2674-2677` ("for `allFromTo`, the first value where its body
  fails; for `exFromTo`, the first where it holds; none otherwise"; 12.2's order = the evaluator's).
- `decidingValue_all`, `decidingValue_ex` and `decidingValue_of_fails` against `:2700-2716` (word for word, by the
  script above).
- M-6 against `:2889` ("VE's `prime` against `IsPrime` on 0 through 400") and `:2966` ("agree on 0…400 | 78 primes");
  `IsPrime` against `:2534`.
- M-5's deciding value 1 against `:2965` ("`decidingValue` is 1, the first n").

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; there is no mode or schema (me-12b).
2. PASS: each task row is in the table above with its proof or guard. `git diff main...HEAD` has no Python copy of a
   Lean decision, no report test, and no edit of `Bounded.lean`. Shared files are listed above.
3. PASS: S1–S3 and D1–D4 are each killed by a named proof or guard (`mutants.json`), and the control is clean.
   `trust_mutants.py` exits 0 with 0 definitions (`trust-mutants.json`).
4. N.A.: `arith@0` has no Python or Rust counterpart.
5. N.A.: there is no relayed field to bind.
6. PASS: the base comes from `git merge-base`; the full gate runs on the final HEAD by the chain.
7. PASS: DELTA has no row; trust +0 (`trust_map.py --check --since 62d8329d4`); no allowance and no signature.
8. PASS: DELTA says "Public output: none": no mode, command, route, or Python or Rust product file.
9. PASS: `select_tests.py --base 62d8329d4` lists the Lean build, `lean/audit.py` and the pytest files that read the
   Lean tree. This item's fixtures are Lean guards that `lake build` checks, and S1–S3 break them.
10. PASS: the statements equal spec 12.5 (script above, `lean_statements.py --check`). S1, S2 and D1 break the proofs as
    written. The theorems are about `decidingValue` itself, which reuses `charge`, `Term.evalB`, `stepB` and
    `Formula.evalB` and copies none of them.
11. PASS: budget 0 to 32 gives no deciding value for M-5 (`agreesUpTo`, `:73`; `:50` at 32). An unknown outcome has
    none (`:79`). S2 shows these guards can fail.
12. PASS: no runtime path changes; `decidingValue` has no caller yet.
13. PASS: no test is removed. `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
14. PASS: each check is tested on both sides (fixture table). Each claim cites its command. The spec re-read is above.
