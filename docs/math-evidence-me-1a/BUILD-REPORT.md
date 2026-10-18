# me-1a build report: the `VE.Numbers` core

No DRI signature is needed: the trust growth (K +0, S +76, V +27 = 103 lines) is signed by standing rulings
R16 (88 lines, cap 150) and R6 (15 lines), recorded in `docs/trust-baseline.json`; see [DELTA.md](DELTA.md).

## Scope and evidence

- Branch `infra/me-1a`, fresh from `main` at `b5248038e` (`git merge-base HEAD main`; main has not moved). It does
  not merge foundation/me-1; its content is carried over with `git show 7b93539a4:<path>`.
- Item: the first of three that replace foundation/me-1 (acting DRI dri-apply1017b, after
  reviews/dri-decisions-20261017b.md #6: "Cut it, or split it into items of 150 lines or fewer"). me-1b (Calc
  Syntax, Eval, Decls) and me-1c (Render) follow.
- Commits (`git log main..HEAD --no-merges`): `8f473c930` spec and plan; `60b5afe66` Numbers core, generated
  table, Python reader, regenerated files; `7d0392ace` trust allowance; `e3648f975` generator test, seeded bugs;
  `a94913df8` spec-table guard, DELTA; `2123eafd2` consolidation ledger; `c11362c45` seeded-bug records.
- Acceptance: AGENT for all of it. EXTERNAL: the full release gate on the final HEAD is the chain's (the task
  replaces checklist 22's full-gate step); it was not run here. HUMAN: none.

## Directive ledger

| Task directive | Delivery and check |
|---|---|
| `lean/VE/Numbers/{Decimal,Round,Phrases,PhrasesMain}.lean` from foundation/me-1 | `60b5afe66`, byte-for-byte `git show 7b93539a4:<path>`; `lake build`; `python3 lean/audit.py` PASS (528 files, 6,202 theorems, standard axioms only) |
| Generated comparison table: `tools/numbers_phrases.py`, `ve/numbers_phrases.json`, the `ve/english.py` reader, regen entry, `.gitattributes` line | `60b5afe66`; `_COMPARISONS` literal deleted, read from the generated file; regen entry `numbers-phrases` (and its `docs/merge-tooling.md` row); `.gitattributes` written by `regen_generated.py --write` (main generates it now); `tools/numbers_phrases.py --check` PASS |
| `tests/test_numbers_phrases.py` | carried over, plus `test_generator_writes_lean_output_and_check_refuses_any_other_file` (`e3648f975`) |
| Numbers part of `lean/VE.lean`, `lean/VE/Audit.lean`, `tools/trust-classes.json` | `VE.lean` imports `VE.Numbers.Phrases` and `VE.Numbers.Examples`; `Audit.lean` regenerated (`audit.py --write`); me-1's class entries for the four modules copied unchanged |
| `test_select_tests.py` / `select_tests.py` / assurance manifest / consolidation ledger only as far as needed | assurance manifest: the `other_json` reason for `PhrasesMain.lean` (`test_every_json_handling_lean_file_is_classified`). Consolidation ledger: step 7 names the seven top-level mains (me-1's change), because `*Main.lean` also counted `PhrasesMain.lean` and broke `test_committed_ledger_names_real_declarations`; new `test_the_skeleton_step_names_every_top_level_executable_main` keeps the list complete. `select_tests.py` and its test: not needed. Main now generates `.gitattributes` and classifies its edits itself, which made me-1's `ROOT_DATA` rule obsolete, and nothing here changes the manifest's operations. |
| Plan and spec verbatim | `8f473c930`; `git diff 7b93539a4 HEAD -- docs/spec/math-evidence.md docs/spec/math-evidence-PLAN.md` is empty |
| No Calc file | none in `git diff main...HEAD --stat` |
| `#guard` fixtures for every new trusted definition | `lean/VE/Numbers/Examples.lean` (new, 0 trusted lines): 59 guards; DELTA rows 1-5 map each trusted declaration to its guards |
| Keep me-1 review fixes that touch these files | F1 touched only `Calc/Render.lean`: not in this item. C7 (Phrases under R6): applied, DELTA row 5. C3 (the 4,096 text beside `maxDigits`): `maxDigits` arrives in me-1b, so this item has one owner; FOLLOW-UPS "## me-1a" row 2 asks me-1b to keep one owner |
| Trust re-measured, R6 + R16 recorded, DELTA itemised per file, FOLLOW-UPS ties row | `tools/trust_map.py --check` PASS at HEAD: K +0, S +76, untied V +27; `--allow` recorded S 76, V 27 with both rulings named; DELTA rows 1-5; manage-agents FOLLOW-UPS.md "## me-1a (2026-10-18)" row 1 (ties pass, infra item ties-me-1a) |
| Seeded bugs (a rounding mode, a decimal normalisation, a comparison row), restored | [mutants.json](mutants.json), rows 1, 2, 5, 6 among ten |
| Generated files only through `regen_generated.py` | `--write` (all 29 entries), then `--only` for lake-build, lean-statements, lean-audit-manifests and frozen-inventory after the Examples change; `regen_generated.py --check` PASS (29 entries) |
| No public output change | DELTA "Public output: none" |

## Trust

`uv run python tools/trust_map.py --check` at the final code, against `b5248038ee26`: K +0, S +76, D +0, G +44,
tied +0, unclassified +0, trusted +103 (Round.lean +54, Phrases.lean +26, PhrasesMain.lean +14, Decimal.lean +9).
Exactly the task's measured 103. R16 covers 88 lines, under its cap of 150 (no K). R6 covers 15. The task put all of
`Phrases.lean` under R6; DELTA rows 4 and 5 split it more strictly, as explained there.

## Seeded bugs

Ten mutants, each restored ([mutants.json](mutants.json)). There is at least one in each changed language:
- Lean: Round.lean ×4, Decimal.lean, Phrases.lean, PhrasesMain.lean.
- Python: `ve/english.py`, `tools/numbers_phrases.py`, `tools/consolidation-ledger.json`.
- Rust: none, because no Rust code changed.

Most Numbers definitions are pinned by proofs, so a mutant usually breaks a proof first. Proof breaks are not counted
as test failures, so three methods are used:
- Mutant 1 swaps "rounded down" and "rounded up" consistently, proofs included. Round.lean still compiles, so only
  the fixtures can catch it.
- Mutants 2 and 5 replace the pinning proofs with `sorry` for the mutant only. Without that, mutant 5 fails at
  `decValue_lower`.
- The other mutants touch definitions no proof pins.

| # | File | Mutation | Failing check |
|---|---|---|---|
| 1 | `lean/VE/Numbers/Round.lean` | down/up meanings swapped, proofs swapped too | Examples.lean:60, 61, 63, 64 |
| 2 | `lean/VE/Numbers/Round.lean` | half to even rounds a tie to the odd digit | Examples.lean:40, 47, 53, 55, 69 |
| 3 | `lean/VE/Numbers/Round.lean` | digits text says 4,069 | Examples.lean:74 |
| 4 | `lean/VE/Numbers/Round.lean` | witness-points text says 4,069 | Examples.lean:100 |
| 5 | `lean/VE/Numbers/Decimal.lean` | `decValue` drops the sign | Examples.lean:12 (and `decValue_lower` without `sorry`) |
| 6 | `lean/VE/Numbers/Phrases.lean` | "is more than" loses its swap | Examples.lean:94; `numbers_phrases.py --check`; 4 pytest cases incl. `test_english_lean_s3.py::test_the_comparison_actions_swap_more_and_at_least` |
| 7 | `lean/VE/Numbers/PhrasesMain.lean` | `.lt` written as "le" | `numbers_phrases.py --check`; `test_comparison_rows_match_generated_table` |
| 8 | `ve/english.py` | "lt" read as `ast.Le` | `test_comparison_rows_match_generated_table` + 3 `test_english_lean_s3.py` cases |
| 9 | `tools/numbers_phrases.py` | `--check` passes on any existing file | `test_generator_writes_lean_output_and_check_refuses_any_other_file` |
| 10 | `tools/consolidation-ledger.json` | a top-level main the step does not name | `test_the_skeleton_step_names_every_top_level_executable_main` |

## Verification

- Selected tests: `mac-pytest.sh --select -- --base b5248038e --run`.
  - It ran on ve-mac-1 (aarch64) at HEAD `c11362c45` (clean): 226/430 units, exit 0, 0 failed ids, no known Mac-only
    failures, 2,609 s. That is the final code; only this report was added after it.
  - An earlier attempt at `e3648f975` fell back to the VM and was stopped. I had edited the worktree while it ran.
    It had failed `tests/test_consolidation_tools.py`, and `2123eafd2` fixed that. The whole file then passed
    locally: 288 passed.
- `regen_generated.py --check`: PASS, 29 entries, including `numbers-phrases`, `trust-tables` and
  `lean-audit-manifests`.
- `gate_collection.py --check --prebuilt`: 17,113 collected; 2 added; 0 removed, refused, stale or malformed.
- Spec statements:
  - No `tools/check_*_statements.py` exists for this spec. A one-off mechanical diff compared the Lean code blocks
    of spec §1.1-1.5 with the Numbers files: 33 items (definitions, theorems, the instance), 0 differences.
  - A planted `≤`→`<` in `RoundsTo` showed 1 difference.
  - The spec's §1.5 text table is pinned by guard 100.
- `git diff --check main...HEAD`: clean.
- Disk: 69 GB free.
- Not run: the full release gate (the chain runs it on the final HEAD) and the relay mutation gate (this branch
  changes no relay, schema or route).
- Pre-existing failures on main (main-known-red.txt) were neither touched nor seen in the selected run.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean service answer, route or request decoder is added. `PhrasesMain` is a build-time generator whose
   output is checked byte for byte (`numbers_phrases.py --check`).
2. PASS: directive ledger above; `git diff main...HEAD` holds no Calc file, no new report test and no Python copy of
   a Lean decision (the Python literal is deleted; `test_comparison_rows_match_generated_table`).
3. PASS: ten seeded bugs in mutants.json. Each makes a `#guard` or a named test fail; mutant 1 does so with every
   proof still checking.
4. PASS: the Python rows equal the Lean rows (`test_comparison_rows_match_generated_table`). The parser's
   comparison behaviour is unchanged (`test_english_lean_s3.py::test_the_comparison_actions_swap_more_and_at_least`,
   `::test_ev5_python_agrees_with_every_fixture_in_its_own_selections`). No Rust code is involved.
5. N.A.: no relayed answer and no new request input.
6. PASS: main has not moved (merge base = main = `b5248038e`). The commit list is from `main..HEAD --no-merges`. The
   final-HEAD gate is the chain's.
7. PASS: DELTA rows 1-5 cite R16 or R6 with their tests. `trust_map.py --check` passes. FOLLOW-UPS "## me-1a" has the
   ties-pass row.
8. PASS: DELTA "Public output: none", because no route or command is added and the phrase rows are byte-identical
   (`test_comparison_rows_match_generated_table`).
9. PASS: `select_tests.py --base b5248038e` picks 226/430 units. The size comes from `ve/english.py`'s import-time
   table, which every English-reader test imports. The selection contains every test the seeded bugs fail
   (`test_numbers_phrases.py`, `test_english_lean_s3.py`, `test_consolidation_tools.py`).
10. PASS: no new theorem. The carried-over statements match the spec (33/33, mechanical diff). Mutants 2 and 5 show
    the proofs pin the definitions (they break without `sorry`).
11. N.A.: no budget, limit or deadline is enforced in this item. The limit texts are fixed strings, pinned by
    guards 73-84 and 100.
12. PASS: no service module imports `VE.Numbers` (checker pins unchanged under `regen_generated.py --check`). The
    Python cost is reading one 4-row JSON file at import.
13. PASS: no test removed or renamed. `gate_collection.py --check --prebuilt` reports 0 refused, stale or malformed.
