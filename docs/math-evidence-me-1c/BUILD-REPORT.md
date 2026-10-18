No DRI signature is needed: the trust growth (K +0, S +0, V +113, all `lean/VE/Calc/Render.lean`) is within standing ruling R16 and recorded under it; no DELTA row reserves a signature. With this item ME-1 is complete. The full release gate is left to the chain's run on the committed final HEAD, as the task directs.

# me-1c build report: the `VE.Calc` English lines, and ME-1 as a whole

## Scope and evidence

- Base: `main` at merge base `c2b1a7d44` (me-1b merged); branch `infra/me-1c`, fresh from main. foundation/me-1 is
  not merged; its files are carried over from `7b93539a4`.
- Item: the last of three that replace foundation/me-1 (acting DRI dri-apply1017b, after
  reviews/dri-decisions-20261017b.md #6: "Cut it, or split it into items of 150 lines or fewer, each signed under
  R16 with a ties pass"). me-1a (`VE.Numbers`, merged `05b85b631`) and me-1b (`VE.Calc` meaning and checker,
  merged `c2b1a7d44`) are on main.
- Commits (`git log --oneline --no-merges main..HEAD`, before this report's commit): `3197cef96` Render.lean, its
  fixtures, the trust classes, the generated inventories; `229a8c19a` the R16 allowance; `dc20f6f24` the seeded
  bugs; `8a52edb47` `lean/CALC.md`; `f2e7fd9d5` DELTA.
- `lean/VE/Calc/Render.lean` is byte-identical to `7b93539a4` (`git diff --quiet 7b93539a4 HEAD -- <file>`),
  which includes me-1's review fix F1 (`9183df324`).
- Acceptance: **AGENT** for all code, fixtures, generated files, the trust allowance (R16) and the FOLLOW-UPS
  row; **EXTERNAL** for the final full gate (the chain's run on the test runner) and the ties pass (infra item
  ties-me-1c). No **HUMAN** item. No pilot bytes.

## Task ledger (me-1c)

| Directive | Delivery and check |
|---|---|
| `lean/VE/Calc/Render.lean` from foundation/me-1, with review fix F1 (`renderClaim` writes a line only when 11.2 has one reading, else `none`) | `3197cef96`; byte-identical to `7b93539a4`; F1's guards at `Examples.lean` 340-352 and the depth-3 read-back at 446 |
| The rest of `lean/VE/Calc/Examples.lean` (the Render fixtures and any left by me-1b) | `3197cef96`: me-1's lines 92-221 (every English-line `#guard`) carried unchanged at 318-447; nothing else was left by me-1b (its review confirmed it kept every check of me-1's lines 19-90 that does not need Render). Added: 452-495 (every phrase, rounding rule, places word, numeral bound and value-word rule) |
| The rest of `lean/CALC.md` | `8a52edb47`: Render's row in the file table, the section "The English lines", ME-1 complete |
| `tools/trust-classes.json` entries | `3197cef96`: me-1's thirteen G[V] Render entries unchanged; the seventeen new Examples helpers are T; `trust_map.py` reports 0 unclassified |
| Generated inventories through regen | `tools/regen_generated.py --write` (lake build, `declarations.txt`, `predicates.txt`), then `--check`: 31 entries pass. `lean/VE/Audit.lean` and `statements.txt` do not change: Render has no theorem |
| Every new trusted definition exercised by a check that can fail | DELTA row 1 maps all thirteen; seeded bugs 1-13 (one or more per declaration group) each fail an `Examples.lean` guard |
| Trust re-measured on the final HEAD, recorded under R16 if at most 150 and K +0 | `trust_map.py --check`: K +0, S +0, V +113 (Render.lean +113) against `c2b1a7d442b4`; `--allow --reason "me-1c Calc display lines: VE/Calc/Render.lean +113 ..." --signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), me-1c, 2026-10-17"` (`229a8c19a`); `--check` PASS at HEAD |
| DELTA rows per file, each Ruling cell citing its ruling | `docs/math-evidence-me-1c/DELTA.md` row 1, R16; `review-ready.py --delta-dri-needed`: "no DELTA row reserved for the DRI" |
| FOLLOW-UPS.md "## me-1c" ties-pass row | manage-agents FOLLOW-UPS.md, section "## me-1c (2026-10-18)": the ties row per declaration (infra item ties-me-1c, with candidate theorems), me-1b review F1/F2 closed, ME-1 complete |
| ME-1 complete: say so in DELTA and report | DELTA's opening paragraph; this report's first line; `lean/CALC.md` |
| Seeded bugs, one per new trusted file | Render.lean: 13 (bugs 1-13); see Seeded bugs |
| Generated files only through `tools/regen_generated.py` | none hand-edited; `trust-classes.json` and `trust-baseline.json` are the trust ledgers (`--allow` wrote the latter) |
| No public output changes | DELTA "Public output: none": no mode, command, route, Python or Rust change |
| `docs/math-evidence-me-1c/BUILD-REPORT.md` summarising ME-1 across me-1a/b/c | this file, "ME-1 plan ledger" below |

## ME-1 plan ledger (all three items)

The plan rows of `docs/spec/math-evidence-PLAN.md` "ME-1. Lean core of `calc@0`" (the rows of me-1's
BUILD-REPORT), each with the item that delivered it.

| Plan directive | Delivered by | Check |
|---|---|---|
| New files `lean/VE/Numbers/{Decimal,Round}.lean` (`decValue`, `decValue_lower`, `tenPow`, `Printed`, `Rounding`, `RoundsTo` and its `Decidable` instance, `roundsTo_close`, `roundsTo_unique`) | me-1a (`60b5afe66`) | `lean/VE/Numbers/Examples.lean`; ties pass ties-me-1a (`802b8ff9b`) |
| `lean/VE/Calc/{Syntax,Eval,Decls}.lean`; `VE.Calc` imports `VE.Numbers` | me-1b (`44579fe61`) | `Examples.lean` 19-314 |
| `lean/VE/Calc/Render.lean`: the English line of each claim from `words` and the fixed phrases of 2.11, display only; every rounding line names its tie rule | me-1c (`3197cef96`) | `Examples.lean` 321-324, 461-468 (each rule named), 318-495 |
| `lean/VE/Calc/Examples.lean` | me-1b (meaning and checker), me-1c (English lines) | `lake build` (VE imports it) |
| `lean/CALC.md`, statement review notes as `lean/RISK.md` (me-1 review C5) | me-1b (`55f484b22`: files, theorems, choices and limits), me-1c (`8a52edb47`: the English lines) | review |
| Proves 3.1; the operational types in their final shape (`Val.exhausted`, `Counted`, `NameExhausted`) | me-1a (Numbers statements), me-1b (Calc statements) | `python3 lean/audit.py --check`; me-1's review diffed all 25 statements against the spec |
| Move W6's comparison phrases (`_COMPARISONS`) into one Lean table; Python reads a generated file | me-1a (`60b5afe66`, `11ddb4a2e`) | `tests/test_numbers_phrases.py`, `tools/numbers_phrases.py --check` |
| `#guard` fixtures V-1, V-1n, V-2, V-4, V-9, V-10, V-11, D-1, H-5, H-5b, H-4, H-9 noon and its negative control, DL-1, DL-2, DL-4 | me-1b | `Examples.lean` 19-122 |
| Generated: `lean/VE.lean`, `lean/VE/Audit.lean`, frozen inventory, axioms, statements, predicates, declarations, trust tables (signed) | each item through `regen_generated.py`; trust signed under R16 (me-1a also R6) | me-1a S +76 V +27 (R16 88, R6 15); me-1b S +107; me-1c V +113. Total 323, as measured on me-1 |
| Seeded bug (Lean): `eval` computes `sub a b` as `b - a`; V-2's third claim fails its `#guard` | me-1c (bug 16; me-1 hit only a proof break) | `Examples.lean` 37 and 40 fail with the proofs' sub cases replaced by `sorry` |
| Bytes: 0 | all three | no pilot or source bytes |

me-1's review: F1 (B) is in Render.lean, carried here (`9183df324`, byte-identical). C1 (memoize `values`) and C3
(one owner for the 4,096-digit limit) stay FOLLOW-UPS for ME-2 (FOLLOW-UPS "## me-1b"). C2 was closed by F1's fix
(negative numbers, "{1}" in value words, capitals; `Examples.lean` 359-367). C4 was closed by me-1b. C5 was closed
by me-1b and me-1c (`lean/CALC.md`). C7 (R6 for Phrases) was applied by me-1a. C6 (a load-sensitive deadline test) is outside Calc and not ME-1 code.
me-1b's review F1 and F2 (C, negative checks) are closed here (`Examples.lean` 138, 141, 304-314; bugs 14-15).

**Wave 2:** work that waited for foundation/me-1 (ME-2 first; ME-6, ME-12 and quantities' QT-A2 wait for ME-1 in
the plan's order) waits for this item's merge, and can start from main after it.

## Seeded bugs

All restored: `git status` was clean after each run, and the unmutated file builds. Each mutated file still
compiled (a proof a mutant breaks was given `sorry`, or for bug 15 adapted to the new constructor, for that mutant
only, so the fixtures catch it, not a proof).
Details and the failing lines are in [`mutants.json`](mutants.json). Only Lean product code changed (Render.lean);
no Python or Rust file changed.

| # | File and mutation | Failing check (`lake build VE.Calc.Examples`) |
|---|---|---|
| 1 | `Render.lean` `renderExpr`: a term, not an atom, on the left of "minus" (reverts F1) | `#guard` 350, sweep 446 |
| 2 | `Render.lean` `renderExpr`: depth bound 2 to 3 | `#guard` 352, sweep 446 |
| 3 | `Render.lean` `reservedWords`: drop "equals" | `#guard` 488 |
| 4 | `Render.lean` `valueWordsOk`: no leading "the" needed | `#guard` 488 |
| 5 | `Render.lean` `natWords`: "seventeen" to "seventy" | `#guard` 470 |
| 6 | `Render.lean` `placesPhrase`: "one decimal place" at 0, not 1 | `#guard`s 463, 470 |
| 7 | `Render.lean` `exactWords`: 41 places allowed | `#guard` 484 |
| 8 | `Render.lean` `printedWords`: the power's sign flipped | `#guard` 467 |
| 9 | `Render.lean` `renderClaim`: "rounded up" loses "up" | `#guard` 463 |
| 10 | `Render.lean` `fill`: filled text read again as a placeholder | `#guard`s 364, 366 |
| 11 | `Render.lean` `renderClaim`: no capital | 16 `#guard`s, 321-470 |
| 12 | `Render.lean` `renderAtom`: value words not checked | `#guard`s 361-363, sweep 446 |
| 13 | `Render.lean` `phraseWords`: drop "the sum of" | `#guard` 488 |
| 14 | `Decls.lean` `Small`: also needs `0 ≤ q` (me-1b review F1's mutant) | `#guard`s 138, 141 |
| 15 | `Decls.lean` `NameExhausted.here`: any counted result (me-1b review F2's mutant) | `example` 304-314 (unsolved goal at 312) |
| 16 | `Eval.lean` `Expr.eval`: `sub a b` as `b - a` (the plan's ME-1 seeded bug) | `#guard`s 37, 40 |

Equivalent mutants noted, not counted: dropping "twice" or "half of" from `phraseWords` changes no answer, because
value words must begin with "the" (DELTA row 1). An earlier version of bug 10 (re-filling the text recursively)
failed in Render.lean itself, on termination, so it was replaced by the version above.

## Build checklist directives

| # | Application to me-1c |
|---|---|
| 1 single generated contract | PASS: the phrases are read from `VE.Numbers.Phrases` (me-1a's one table, which Python reads from the generated `ve/numbers_phrases.json`); Render copies none of them |
| 2 differential Py/Lean/Rust | N.A.: no route; no Python or Rust renderer (ME-2/3) |
| 3 normalize text once | N.A.: no text input; value words are checked for 11.2's form (spacing included, `#guard` 488) |
| 4 untrusted output | N.A.: no relayed answer |
| 5 malformed input | N.A.: no public input decoder |
| 6 three-valued verdict | N.A.: Render writes no verdict; a line it cannot write is `none`, never a guessed line |
| 7 whole-operation deadline | N.A.: no public operation |
| 8 exhaustive kind fold | PASS: `renderClaim`, `renderTerm`, `renderExpr` match every `Claim`, `Expr` and `Rounding` constructor (Lean checks exhaustiveness); each rounding rule and each comparison has a `#guard` (452-468) |
| 9 English render/parse | PASS: `#guard` 446, render then an every-parse reader of 11.2 over every expression to depth 3 (unique derivation); a line is written only when 11.2 accepts the expression. The parse-back theorem is ME-11's, as the plan says |
| 10 one admit entry point | N.A.: no entry point |
| 11 real-language parsing | PASS: Lean is checked by `lake build`; no regex added |
| 12 state machine/ledger | N.A. |
| 13 tests can fail | PASS: 16 seeded bugs above |
| 14 hermetic | PASS: Lean fixtures only |
| 15 identity fields | N.A.: no wire identity (ME-2) |
| 16 inventory coverage | PASS: `regen_generated.py --check` (31 entries), `lean/audit.py --check`, `repo_map.py --check`, 0 unclassified declarations |
| 17 approved spec statements | PASS: Render has no theorem; the file is me-1's, reviewed against spec 9 and 11.2 (F1 fixed and rechecked, `me-1-loop.final.md`) |
| 18 spec-stage fixtures | PASS: boundary fixtures for each bound Render has: 40 and 41 places (483-484), depth 2 and 3 (446), twenty and 21 places (470), reserved words as whole words and inside words (488-495) |
| 19 use-case formalisation | N.A. |
| 20 reports from gate JSON | N.A.: no report numbers; the trust numbers are `trust_map.py --check` output |
| 21 AGENT/HUMAN/EXTERNAL | PASS: Scope and evidence |
| 22 selected tests, final gate | Selected tests on the Mac runner (below); the final gate is the chain's (task override) |
| 23 standing rulings, DELTA | PASS: DELTA row 1 under R16 |

## Verification

- Selected tests, `mac-pytest.sh --select -- --base c2b1a7d44 --run` at `f2e7fd9d5` (clean): 58 units (the Lean
  build, `lean/audit.py`, the layer policy, and 49 pytest files including `test_trust_budget.py`,
  `test_trust_ratchet.py`, `test_frozen_sources.py`, `test_regen_generated.py`, `test_numbers_phrases.py`), **0
  failed, exit 0**, 1,315 s on ve-mac-1. After it only `mutants.json` (bug 16) and this report changed.
- `lake build`: 978 jobs. `python3 lean/audit.py --check`: PASS, 539 files, 6,265 named theorems, standard axioms
  only. `tools/regen_generated.py --check`: 31 entries. `tools/repo_map.py --check`: 36 modes. `tools/trust_map.py
  --check`: PASS. `tools/gate_collection.py --check --prebuilt`: 17,318 collected, 0 added, 0 removed, 0 refused,
  0 stale, 0 malformed. `git diff --check main...HEAD`: clean. Free disk: 55 GB.
- No test in `main-known-red.txt` was selected or failed.
- Not run here: the full release gate (the chain's, on the final HEAD).

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean service answer or request decoder; ME-2/3 add them.
2. PASS — Task ledger and ME-1 plan ledger above; `git diff --check main...HEAD`; no Python copy of a Lean decision, no permanent report test, no file outside `lean/VE/Calc`, `lean/VE.lean`, `lean/CALC.md`, the generated inventories, the trust ledgers and `docs/math-evidence-me-1c`.
3. PASS — 16 seeded bugs (`mutants.json`), each failing `lake build VE.Calc.Examples` at a `#guard` or `example`, not at a proof or hash.
4. N.A. — no route, so no base/head output to compare; no Python or Rust counterpart.
5. N.A. — no relayed answer (R8 binding starts with ME-3).
6. N.A. — the final-HEAD full gate is the chain's (task override); selected tests on the Mac: 58 units, 0 failed at `f2e7fd9d5`.
7. PASS — `trust_map.py --check` PASS with the R16 allowance; DELTA row 1 cites R16; `review-ready.py --delta-dri-needed`: no reserved row; FOLLOW-UPS "## me-1c" ties row.
8. PASS — no public output change: no mode, command, Python or Rust change (DELTA "Public output: none").
9. PASS — `select_tests.py --base c2b1a7d44`: 49/434 pytest units plus the Lean build and audit; the build (where every seeded bug fails) and the trust tests are in the plan.
10. PASS — Render has no theorem; bug 16 broke `Expr.eval_sound`, `Denotes.eval_complete` and `Expr.evalL_agrees` (their sub cases were given `sorry` for the mutant), and bug 15 broke the `NameExhausted.here` term in `Decls.lean` 727 (adapted to the new constructor for the mutant); `lean/audit.py --check` PASS.
11. N.A. — Render has no budget or deadline; its bounds (40 places, depth 2) are tested at both sides (`Examples.lean` 446, 483-484).
12. PASS — `renderExpr` stops at depth 2 before rendering any operand (`exprDepth` first), and the read-back sweep at 446 runs every expression to depth 3 inside `lake build`'s time; no public path calls Render yet (ME-2), and the C1 cost item is ME-2's (FOLLOW-UPS).
13. PASS — no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.

## Sibling lessons (me-1b review F1, F2)

me-1b's review found definitions a weakened version of which still passed every check (negative-check gaps). For
me-1c: every Render declaration has a mutant that fails a guard (bugs 1-13), each rule of 11.2's value-word form
has its own negative case (488-492) and a positive case for whole-word matching (494-495), and each phrase and
rule is pinned to its exact text (452-478). The two me-1b gaps themselves are closed here (bugs 14-15).
