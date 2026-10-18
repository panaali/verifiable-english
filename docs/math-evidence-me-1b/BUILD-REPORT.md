No DRI signature is needed: the trust growth (K +0, S +107, V +0) is within standing ruling R16 and recorded under it; no DELTA row reserves a signature. The full release gate is left to the chain's run on the committed final HEAD, as the task directs.

# me-1b build report: the `VE.Calc` meaning and checker

## Scope and evidence

- Base: `main` at merge base `05b85b631` (me-1a merged); branch `infra/me-1b`, fresh from main. foundation/me-1 is
  not merged; its files are carried over from `7b93539a4`.
- Commits (`git log --oneline --no-merges main..HEAD`, before this report's commit): `44579fe61` the three Calc
  files, their trust classes, the Render-free `Examples.lean`, the generated inventories; `55f484b22`
  `lean/CALC.md`; `ce2fe1d66` the `within` boundary examples; `51a7be551` the seeded bugs and regenerated
  declarations; `f8c1b3aaa` the R16 allowance; `7bd3d6aaa` the digit-limit tie (me-1 review C3); `9383031d0` DELTA.
- `lean/VE/Calc/Syntax.lean`, `Eval.lean` and `Decls.lean` are byte-identical to `7b93539a4`
  (`git diff --quiet 7b93539a4 HEAD -- <file>`). me-1's review fix F1 touched only `Render.lean`, which is me-1c's.
- Acceptance: **AGENT** for all code, fixtures, proofs, generated files, the trust allowance (R16) and the
  FOLLOW-UPS row; **EXTERNAL** for the final full gate (the chain's run on the test runner) and the ties pass
  (infra item ties-me-1b). No **HUMAN** item. No pilot bytes.

## Task ledger

| Directive | Delivery and check |
|---|---|
| `lean/VE/Calc/{Syntax,Eval,Decls}.lean` from foundation/me-1, no Render file | `44579fe61`; byte-identical to `7b93539a4`; `lake build` (976 jobs) |
| The Calc part of `lean/VE.lean` | `44579fe61`: `import VE.Calc.Examples` (which imports Decls, Eval, Syntax); no Render import |
| `lean/VE/Audit.lean`, axioms, statements, predicates, declarations, frozen sources through regen | `tools/regen_generated.py --write`, then `--check` passes all 29 entries; the frozen-source list does not change (no Calc file is frozen) |
| `lean/CALC.md`, the parts about these files | `55f484b22`: files, every theorem in plain words, choices and limits (fault order, the digit limit, review C1) |
| `tools/trust-classes.json` entries | `44579fe61`: me-1's classes for Syntax, Eval, Decls; the new Examples helpers are T; `trust_map.py` reports 0 unclassified |
| `#guard` fixtures V-1, V-2, V-4, V-9, V-10, V-11, D-1, H-4, H-5, H-9, DL-1, DL-2, DL-4 without Render, in an examples file that does not import Render | `lean/VE/Calc/Examples.lean` 19-122, carried from me-1's `Examples.lean` without the two `renderClaim` guards and the 11.2 read-back block (me-1c) |
| Proofs `Expr.eval_iff`, `Claim.decide_*`, `Claim.run_decided` / `run_unknown` / `run_complete` compile | `lake build`; `python3 lean/audit.py --check`: 537 files, 6,258 named theorems, standard axioms only |
| Every new trusted definition exercised by a check that can fail | DELTA rows 1-2 list the check for each of the 21 S declarations; review C4's gaps (free and counted sources through `run`, V-13, the 27/200 tie) are closed at `Examples.lean` 54-61, 148-184; ten seeded bugs below |
| Trust re-measured on the final HEAD, recorded under R16 if at most 150 and K +0 | `trust_map.py --check`: K +0, S +107, V +0 (Decls 70, Syntax 37, Eval 0); `--allow ... --signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), me-1b, 2026-10-17"` (`f8c1b3aaa`); `--check` PASS |
| DELTA rows per file, each citing its ruling | `docs/math-evidence-me-1b/DELTA.md` rows 1-2, R16; `review-ready.py --delta-dri-needed`: no row reserved |
| FOLLOW-UPS.md "## me-1b" ties-pass row | manage-agents FOLLOW-UPS.md, section "## me-1b": the ties row (per declaration, with the candidate theorems), C3 and C1 |
| Seeded bugs, one per new trusted file, each failing a check | ten, in `mutants.json`: Syntax 1-3, Eval 4, Decls 5-10 |
| Generated files only through `tools/regen_generated.py` | every generated file was written by `--write`; none is hand-edited |
| No public output changes | DELTA: no mode, command, route, Python or Rust change |

The FOLLOW-UPS note "me-1 review C3 for me-1b" asks that `maxDigits` and the "4,096 digits" text get one owner.
Both are approved spec text (2.4 `def maxDigits : Nat := 4096` in `VE.Calc`; 1.5's table in `VE.Numbers`), and
`VE.Numbers` cannot import `VE.Calc`, so one owner needs a spec change to 2.4, which is the DRI's. `7bd3d6aaa` ties
them instead: a `#guard` (`Examples.lean` 128-131) computes the text's number from `maxDigits` and fails the build
when they disagree (seeded bug 5 makes it fail). The owner move stays in FOLLOW-UPS.

## Seeded bugs

All restored; each mutated file still compiled (the proofs a mutant breaks were replaced by `sorry` for that mutant
only, so the fixtures, not a proof, catch it). Details and the failing lines are in `mutants.json`. Only Lean
product code changed; no Python or Rust file changed.

| # | File and mutation | Failing check |
|---|---|---|
| 1 | `Syntax.lean`: `Denotes.div` asks the dividend, not the divisor, to be nonzero | `Examples.lean` 194, 224 (a zero divisor has no meaning) |
| 2 | `Syntax.lean`: `Claim.Defined` skips the first expression | `Examples.lean` 217, 222 |
| 3 | `Syntax.lean`: `Claim.Holds` makes `within`'s lower end strict | `Examples.lean` 203 |
| 4 | `Eval.lean`: `Claim.tieSensitive` drops half to even | `#guard` 57 |
| 5 | `Decls.lean`: `maxDigits` 4096 to 4095 | `#guard`s 127-145, including the text tie at 129 |
| 6 | `Decls.lean`: `Decl.valueUnder` gives a counted value none | `#guard`s 162-171 |
| 7 | `Decls.lean`: `Decl.valL` makes an exhausted count undefined | `#guard`s 175-178 |
| 8 | `Decls.lean`: `Claim.run` reads the claim's expressions in reverse | `#guard`s 121-122, 177-178 |
| 9 | `Decls.lean`: `Expr.Overflows` drops the read-name cause | `example`s 262-286 |
| 10 | `Decls.lean`: `findingKind` accepts an empty check list as a source finding | `#guard` 183 |

## Build checklist directives

| # | Application to me-1b |
|---|---|
| 1 single generated contract | PASS: no new diagnostic, limit or decoder table outside Lean; the one limit text is tied to `maxDigits` (`Examples.lean` 128-131) |
| 2 differential Py/Lean/Rust | N.A.: no route and no Python or Rust counterpart (ME-2/3) |
| 3 normalize text once | N.A.: no parser or text input |
| 4 untrusted output | N.A.: no relayed answer |
| 5 malformed input | N.A.: no public input decoder |
| 6 three-valued verdict | PASS: `Verdict` has `undefined`; exhaustion and the digit limit are `unknown` (`Examples.lean` 103-108, 110-122, 136-145, 171-178; `Claim.run_unknown`) |
| 7 whole-operation deadline | N.A.: no public operation |
| 8 exhaustive kind fold | N.A.: no status fold; `Claim.decide` and `run` match every constructor (Lean checks exhaustiveness) |
| 9 English render/parse | N.A.: the renderer is me-1c's |
| 10 one admit entry point | N.A.: no entry point |
| 11 real-language parsing | PASS: Lean is checked by `lake build`; no regex over a language added |
| 12 state machine/ledger | N.A. |
| 13 tests can fail | PASS: ten seeded bugs above |
| 14 hermetic | PASS: Lean fixtures only; no sleeps, timeouts, network or caches |
| 15 identity fields | N.A.: no wire identity (ME-2) |
| 16 inventory coverage | PASS: `regen_generated.py --check` (29 entries), `lean/audit.py --check`, `repo_map.py --check`, 0 unclassified declarations |
| 17 approved spec statements | PASS: the carried files are me-1's, whose review diffed every ME-1 statement and definition against spec §§1-2.5; byte-identical here |
| 18 spec-stage fixtures | PASS: boundary fixtures for both directions of `decide_holds` / `decide_undefined` / `decide_fails` (holds, fails, undefined at 19-108) and of `findingKind_source_iff` (180-184) |
| 19 use-case formalisation | N.A. |
| 20 reports from gate JSON | N.A.: no report numbers; trust numbers are `trust_map.py --check` output |
| 21 AGENT/HUMAN/EXTERNAL | PASS: Scope and evidence |
| 22 selected tests, final gate | Selected tests on the Mac runner, final gate by the chain (task override) |
| 23 standing rulings, DELTA | PASS: DELTA rows 1-2 under R16 |

## Verification

- Selected tests, `mac-pytest.sh --select -- --base 05b85b631 --run`: first run at `55f484b2`, 370 units, two
  failed, both trust-budget tests (`tests/test_trust_budget.py::test_trust_map_check_passes_on_the_live_tree`,
  `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check`), as expected before the R16 allowance;
  second run at `9383031d` (after the allowance): **371 units, 0 failed, exit 0**.
- Selection picks 371 of 433 units because the coverage map is unreadable here ("44 passing units ran no recorded
  code"), so the static graph selects every test that runs Lean. With both builds on record the binary cutoff applies and
  reports no executable rebuilt. The changes that fail (the Lean `#guard`s, the trust budget) are in the selected
  plan (`lake build`, `tests/test_trust_budget.py`, `tests/test_trust_ratchet.py`); the trust tests failed in the
  first run before the allowance.
- `lake build`: 976 jobs. `python3 lean/audit.py --check`: PASS. `tools/regen_generated.py --check`: 29 entries.
  `tools/repo_map.py --check`: 36 modes. `tools/trust_map.py --check`: PASS. `tools/gate_collection.py --check
  --prebuilt`: 17,276 collected, 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- No test in `main-known-red.txt` was selected or failed. Free disk: 78 GB.

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean service answer or request decoder; ME-2/3 add them.
2. PASS — Task ledger above; `git diff --check main...HEAD`; no Python copy of a Lean decision, no permanent report test.
3. PASS — ten seeded bugs (`mutants.json`), each failing `lake build VE.Calc.Examples` at a `#guard` or `example`, not at a proof or hash.
4. N.A. — no route, so no base/head output to compare; no Python or Rust counterpart.
5. N.A. — no relayed answer (R8 binding starts with ME-3).
6. N.A. — the final-HEAD full gate is the chain's (task override); selected tests on the Mac: 371 units, 0 failed at `9383031d`.
7. PASS — `trust_map.py --check` PASS with the R16 allowance; DELTA rows 1-2 cite R16; `review-ready.py --delta-dri-needed`: no reserved row.
8. PASS — no public output changes: no mode, command, Python or Rust change (DELTA "Public output: none").
9. PASS — `select_tests.py --base 05b85b631`: 371/433 (static fallback, unreadable coverage map; binary cutoff applied, nothing rebuilt); the trust tests that failed before the allowance were in the selection.
10. PASS — seeded bugs 1-3 and 9 broke the proofs `Expr.eval_sound`, `Denotes.eval_complete`, `Claim.decide_undefined`, `Claim.decide_holds`, `Expr.evalL_causes` and `causes_step` before they were replaced by `sorry`; `lean/audit.py --check` PASS.
11. PASS — `Examples.lean` 127-145 test the digit limit at limit − 1, limit and limit + 1; an exhausted count is `unknown (limit .evaluations)` (171-178); no public budget or deadline is added.
12. N.A. — no public path calls Calc yet; review C1's per-link doubling in `values` is a FOLLOW-UP for ME-2 (step-count test before `calc` is registered).
13. PASS — no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.

## Sibling lesson (me-1a review F1)

me-1a's F1 was a generated table the product reads with no unmocked freshness check in the suite or gate. me-1b adds
no such table: its only generated files are the Lean inventories (`lean-statements`, `lean-audit-manifests`),
which `regen_generated.py --check` and `lean/audit.py` check, and every new trusted definition is pinned by
`Examples.lean`, which the gate's `lake build` compiles (it is imported by `lean/VE.lean`).
