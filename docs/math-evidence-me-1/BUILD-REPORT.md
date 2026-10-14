DRI signature needed: ME-1 introduces S +183 and V +106 trusted Lean lines; no standing ruling signs new core lines. See DELTA.md. The full release gate is reserved for the chain's committed-HEAD run, as the task explicitly directs.

# ME-1 build report

## Scope and evidence

- Base: `main` at merge base `f98183bf5`; branch `foundation/me-1`.
- The reviewed plan and spec were copied verbatim from `research/math-evidence-p1` in `92bfcc54c`.
- `fafaf7e5e` owns exact numbers, rounding and one Lean comparison phrase table; Python reads only its generated JSON. `0aeb5248f` implements the Calc meaning, checker, limits, rendering, fixtures, and generated inventories. `2a25e5620` adds tie guards and classifies the new Lean declarations. `bb7269293` records the generator's assurance/merge ownership, narrows the consolidation ledger to top-level mains, refreshes the frozen hash, and scopes test selection. `3eb40824b` scopes `other_json` selection. `3dc31cb97` makes two existing tests stable across this batch.
- Acceptance: **AGENT** for all ME-1 code, proofs, fixtures and generated files; **HUMAN** for the trust allowance signature; **EXTERNAL** for the final full gate on the chain's test runner. No pilot bytes are in ME-1.

## ME-1 plan ledger

| Plan directive | Delivery and check |
|---|---|
| New `VE.Numbers` decimal and round files, `VE.Calc` Syntax/Eval/Decls/Render/Examples, `lean/CALC.md`; Calc imports Numbers before QT-A2 | `fafaf7e5e`, `0aeb5248f`; `lake build VE.Calc.Examples VE.Calc.Render`; `python3 lean/audit.py --check` |
| Prove §3.1 and final `Counted`, `Val.exhausted`, `NameExhausted`; display-only English lines with named tie rule | `fafaf7e5e`, `0aeb5248f`; `Expr.eval_iff`, `Claim.decide_*`, `Claim.run_decided`, `Claim.run_unknown`, `Claim.run_complete` compiled; `VE.Calc.Examples` guards |
| Move W6 `_COMPARISONS` to one Lean table and generate the Python file | `fafaf7e5e`; `tests/test_numbers_phrases.py::test_comparison_rows_match_generated_table`, `tools/numbers_phrases.py --check` |
| `#guard` fixtures V-1, V-1n, V-2, V-4, V-9, V-10, V-11, D-1, H-4, H-5, H-5b, H-9 noon/negative, DL-1, DL-2, DL-4 | `0aeb5248f`, `2a25e5620`; `lake build VE.Calc.Examples` |
| Shared hand-written: none; regenerate roots, audit, frozen inventory, axioms, statements, predicates, declarations, trust table | `0aeb5248f`, `2a25e5620`; `tools/regen_generated.py --check` and trust check after signature |
| Seed subtraction reversal: V-2 must reject | The `Eval.lean` mutant broke `Expr.eval_sound` and `Denotes.eval_complete` before the guard could run; independent proof protection. Additional runtime guard mutants below supply test-failure evidence. |
| Bytes: 0 | No pilot or recorded source bytes. |

## Seeded bugs

All mutants were restored before the final build.

| Changed product file and mutation | Failing test |
|---|---|
| `lean/VE/Calc/Eval.lean`: `Claim.tieSensitive` returns false for an exact tie | `lake build VE.Calc.Examples`: `#guard` at the tie fixture failed (`/tmp/ve-me1-mutant-tie.log`) |
| `lean/VE/Calc/Render.lean`: ties-up English says “going down” | `lake build VE.Calc.Examples`: rounding-line `#guard` failed (`/tmp/ve-me1-mutant-render.log`) |
| `lean/VE/Calc/Decls.lean`: digit limit 4096 → 8192 | `lake build VE.Calc.Examples`: V-11 `#guard` failed (`/tmp/ve-me1-mutant-limit.log`) |
| `ve/english.py`: `<` phrases mapped to `ast.Le` | `tests/test_numbers_phrases.py::test_comparison_rows_match_generated_table` failed on the Mac runner (`/tmp/ve-me1-mutant-python.log`) |
| `tools/select_tests.py`: treat generated `.gitattributes` as a whole-repository change | `tests/test_select_tests.py::test_generated_merge_attributes_select_scoped_tests` failed on the Mac runner (`/tmp/ve-me1-mutant-selector.log`) |
| `tools/select_tests.py`: remove the `other_json` metadata-only classification | `tests/test_select_tests.py::test_manifest_other_json_classification_selects_manifest_contract` failed locally (`/tmp/ve-me1-mutant-manifest-selector-local.log`) |
| `lean/VE/Calc/Eval.lean`: subtraction computes `y - x` | `lake build VE.Calc.Examples` failed at the independent soundness/completeness theorems before V-2's guard (`/tmp/ve-me1-mutant-sub.log`); proof break, not counted as a test mutant |

## Build checklist directives

| # | Application to ME-1 |
|---|---|
| 1 single generated contract | PASS: `VE.Numbers` owns rounding/phrases; `ve/numbers_phrases.json` generated and checked. |
| 2 differential Py/Lean/Rust faults | N.A.: ME-1 has no route or Rust code; ME-2/3 own differential route tests. |
| 3 normalize text once | N.A.: no new parser; existing English phrases moved without change. |
| 4 validate untrusted output | N.A.: no new relay answer; ME-2/3 own schemas and binding. |
| 5 malformed input | N.A.: no new public input decoder. |
| 6 three-valued verdict | PASS: `Claim.run_unknown` and V-11 guard; undefined and exhaustion stay distinct. |
| 7 whole-operation deadline | N.A.: no public operation or deadline added. |
| 8 exhaustive kind/owner fold | N.A.: no status fold or profile gate in ME-1. |
| 9 English render/parse | PASS for ME-1's display-only render and explicit tie words in guards; parse-back is explicitly ME-11 in the plan. |
| 10 one admit entry point | N.A.: ME-1 registers no entry point. |
| 11 real-language parsing | PASS: Lean is compiled by Lake; Python reads generated JSON with `json.loads`. |
| 12 state machine/ledger | N.A.: no state machine or ledger. |
| 13 tests can fail | PASS: four runtime mutants above; subtraction proof mutant also broke the build. |
| 14 hermetic tests | PASS: Lean guards and phrase test use no network, sleeps or fixed timeouts. |
| 15 identity fields | N.A.: no wire identity yet (ME-2). |
| 16 inventory coverage | PASS: `regen_generated.py` inventory, Lean audit and statement scan. |
| 17 approved spec statements | PASS: approved spec copied verbatim; Lean proofs compiled; no ME-1-specific `check_*_statements.py` exists. |
| 18 spec-stage theorems/fixtures | PASS: statements and iff proofs compiled, boundary guards in `VE.Calc.Examples`. |
| 19 use-case formalisation | N.A.: ME-1 only installs core and arithmetic guards, with no source claims presented as findings. |
| 20 reports from gate JSON | N.A.: no pilot numbers or permanent report test; final gate is external. |
| 21 AGENT/HUMAN/EXTERNAL | PASS: scope and evidence section above. |
| 22 selected tests and final gate | Selected tests on Mac; chain runs full gate after final commit per user override. Initial 374-unit selected run exposed five inventory tests and was fixed. The scoped 163-unit run passed 161 units; the two failing tests were repaired and passed on the Mac. |
| 23 standing rulings and DELTA | `DELTA.md`; trust signature pending. |

## Verification and fixes from selected tests

- `mac-pytest.sh --select -- --base f98183bf5 --run` selected 163 units at `3eb40824b`: 161 passed. The RD-6b report test still compared its historical ledger to the moving current tree; it now compares the RD-6b baseline with its pinned commit. `tests/test_readings_defaults_rd6b_report.py::test_trust_growth_is_rd6b_entry_and_listed_for_signature` passed locally and on the Mac after the fix.
- `tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline` had a one-microsecond CPU limit that missed the Mac's CPU tick. The test now advances an injected CPU clock after the request write. It passed locally and on the Mac after the fix. `tests/test_hang_guards.py`: 61 passed locally.
- `python3 lean/audit.py --check`: 490 Lean source files and 5,840 named theorem declarations audited, standard axiom allowlist only. `tools/regen_generated.py --check --only lean-statements`: 5,390 statements unchanged; its checks of `gitattributes`, `numbers-phrases`, `frozen-inventory`, `checker-pins` and `assurance-doc` also passed. `tools/repo_map.py --check`: 32 modes have schemas. The approved plan and spec copies match `research/math-evidence-p1` byte-for-byte. `git diff --check main...HEAD` passed.
- The task reserves `tools/gate.py` for the chain's clean, committed final HEAD. No full release gate was run here.

## Pre-review continuation

- The chain's gate at `257ea1b28` completed its Lean, audit and Rust stages and failed one pytest case: `tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target`. Git now chooses a nine-character `%h` in this repository, while RD-8 saved eight-character IDs. Commit `77656c29d` compares each saved ID with the prefix of the full hash. The targeted pytest case passed locally; the 163-unit selected run on the Mac runner passed with zero failed units. `tools/gate.py --rerun-failed` would run the full gate because the repaired tree differs from the failed gate's tree; the task assigns that full run to the chain.
- The pre-review mutant scanner reads committed mutant JSON. Commit `77656c29d` records the previously planted and restored Lean and Python bugs in `mutants.json`, including each changed product file and its failing test. The scanner now finds `lean/VE/Calc/{Decls,Eval,Render}.lean` and `ve/english.py`.
- The readings relay schema already refuses seven paths the allow-list called untyped. The first all-route mutation run tested 109,195 mutants across 39 routes and found no unlisted accepted mutant. It found 121 unused allow-list paths, including the seven in the pre-review summary; the remaining findings were hidden by its 12-line tail. The five accepted mutations in that summary now have exact F10/F11 follow-up paths. Commit `4f3f3b2c9` removed exactly the 121 unused paths from `tools/relay-gate-allow.json` and dropped five entries left empty. `tests/test_relay_mutation_gate.py` passed (18 tests) after the prune; the final all-route run is recorded below.
- No ME-1 public output changed in this continuation. `DELTA.md` remains the public delta record. The chain will run the full release gate on the new committed HEAD, as the task directs.

Final all-route relay mutation run: **PASS**, 39 routes, 109,195 mutants, zero findings and zero failures (`uv run python tools/relay_mutation_gate.py --json /tmp/me1-relay-full-final.json`).

## Self-review against BUILDER-CHECKLIST

1. N.A. — ME-1 has no Lean service answer or request decoder; ME-2/3 add those.
2. PASS — this report's ME-1 plan ledger and build checklist directives; `git diff main...HEAD --check`.
3. PASS — `VE.Calc.Examples` guards and `tests/test_numbers_phrases.py` failed under the seeded mutations listed above and in `mutants.json`.
4. N.A. — no calc route exists yet, so no three-way response or new JSON order to compare.
5. N.A. — no relayed answer exists in ME-1; ME-3 adds R8 binding tests.
6. N.A. — the task assigns the final-HEAD full gate and its evidence to the chain.
7. PASS — `tools/trust_map.py --check` measures S +183 and V +106; `DELTA.md` lists the required DRI signature in its first lines.
8. PASS — `tests/test_numbers_phrases.py` pins every existing comparison row; Calc has no public route.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selects 163/374 units; `--paths .gitattributes --impacted` includes the generator and merge tests; the two selector tests above failed under their respective mutants.
10. PASS — subtraction mutant broke `Expr.eval_sound`/`Denotes.eval_complete`; `lake build VE.Calc.Examples`, `python3 lean/audit.py --check`.
11. PASS — V-11 `#guard` and digit-limit mutant; no deadline or public budget operation is added in ME-1.
12. N.A. — no calc service path or pilot measurement in ME-1; Calc becomes public in ME-2.
