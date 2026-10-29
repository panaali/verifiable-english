Status: delivered the committed code map and advisory branch check; the selected run's one failure passed its targeted rerun.
HEAD: this report's commit is the final branch HEAD (`git log -1 --oneline`).
Open: the chain runs the full release gate on that committed HEAD; the DRI adds `codemap` to the merge train after merge.
DRI signature: none required; no trusted Lean, product decision path, or DELTA row changed.

# eff-codemap build report

## Delivered and evidence

| Acceptance | Owner | Delivery | Check |
|---|---|---|---|
| Working-tree-only `--write`, `--check`, `--missing`; sentence extraction and size caps | AGENT | `tools/code_map.py`, commit `1888fdc22` | `tests/test_code_map.py` (5 passed in focused run) |
| Generated ownership, merge attribute, advisory check | AGENT | `tools/regen_generated.py`, `.gitattributes`, commit `1888fdc22` | `tests/test_regen_generated.py::test_advisory_check_warns_without_failing_and_strict_check_still_fails`; registry checks (6 passed) |
| Short AGENTS pointer | AGENT | `AGENTS.md`, commit `1888fdc22` | `tests/test_repo_map.py::test_agents_md_is_short_and_claude_md_is_its_symlink`; path test |
| Committed map | AGENT | `docs/codemap/`, commit `1888fdc22` | `python3 tools/code_map.py --check` exited 0 |
| Candidate regeneration entry | HUMAN: DRI, after merge | Add the exact line `codemap` to `manage-agents/cand-regen-entries.txt` | VM timings below; candidate timing is the DRI's merge-train step |
| Final full gate | EXTERNAL: chain | Runs on committed final HEAD | Not run by this builder, as directed |

`/usr/bin/time -f 'codemap_write_seconds=%e' python3 tools/code_map.py --write` printed `codemap_write_seconds=6.52` on the VM. The matching `--check` command printed `codemap_check_seconds=6.13` and exited 0. `python3 tools/code_map.py --missing | wc -l` printed `165`; `--missing` is informational. The map size command (`Path('docs/codemap').glob('*.md')`, file byte sizes, approximate tokens as ceil(bytes/4)) printed `files bytes approximate_tokens index_bytes: 134 281495 70374 9958`. Sizes for every file are below.

`timeout 3000 env UV_CACHE_DIR=/tmp/eff-codemap-uv uv run python tools/regen_generated.py --write` exited 0 and ended `regen_generated: wrote 34 entries` (`/tmp/eff-codemap-regen.log`, final 50 lines inspected). No Lean source changed, so no separate Lean build, Lean audit, or trust mutants run was required. The full release gate is reserved for the chain.

The one selected-test run (`zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`) ran six GitHub Actions shards. Five shards passed; shard 2 had one failure, `tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry`, because the documented registry table lacked `codemap` (`/tmp/eff-codemap-selected.log`, lines 391-418, 611). I added the row to `docs/merge-tooling.md` and reran only that test ID through `mac-pytest.sh --`; it passed `1 passed in 1.63s` on ve-mac-1 (`/tmp/eff-codemap-failed-rerun.log`). No selected test remains failing.

Spec re-read: `docs/codemap/INDEX.md` and one area file per split, sorted first sentences, `--missing`, and the size caps against `prompts/eff-codemap-task.txt:4-14`; the committed branch map's lag and merge regeneration against `reviews/shared-cache-20261028.md:87-106`; the original index motivation against `reviews/transcript-review-20261028.md:217-225`. No schema or binding statement changed.

## Seeded bugs

Each mutant was planted in a changed Python file, run against one named test, and removed. Each produced a pytest assertion failure:

| File | Seeded bug | Failing test |
|---|---|---|
| `tools/code_map.py` | Prefix every extracted sentence with `BROKEN ` | `tests/test_code_map.py::test_synthetic_tree_extracts_first_sentences_and_is_deterministic` |
| `tools/code_map.py` | Return success immediately for `--check` | `tests/test_code_map.py::test_check_detects_stale_and_extra_files_then_accepts_write` |
| `tools/regen_generated.py` | Add advisory drift to fatal failures | `tests/test_regen_generated.py::test_advisory_check_warns_without_failing_and_strict_check_still_fails` |

## Self-review against BUILDER-CHECKLIST

1. N.A. No Lean answer or request decoder changed.
2. PASS — acceptance table above; `tests/test_code_map.py`, `tests/test_regen_generated.py`, `tests/test_repo_map.py`.
3. PASS — three seeded failures listed above.
4. N.A. No product Python, Lean, or Rust semantics changed.
5. N.A. No relayed answer or R8 binding changed.
6. N.A. The chain runs the final-HEAD gate, as required by this task.
7. PASS — no DELTA or trust growth; `git diff main...HEAD --stat` self-review.
8. PASS — no product output delta; `git diff main...HEAD --stat` shows only tooling, tests, documentation, and merge attributes.
9. PASS — selected-test run and targeted rerun recorded above; `tests/test_code_map.py::test_check_detects_stale_and_extra_files_then_accepts_write` covers a source edit.
10. N.A. No Lean statement or proof changed.
11. N.A. No budget or deadline logic changed.
12. PASS — VM `--write`/`--check` timings above; `tests/test_code_map.py::test_body_edit_does_not_change_output` prevents needless drift.
13. N.A. No test removed or renamed.
14. PASS — opposite directions in `test_check_detects_stale_and_extra_files_then_accepts_write` and `test_advisory_check_warns_without_failing_and_strict_check_still_fails`; source reread above.

## Generated sizes

Approximate tokens are ceil(bytes/4), a sizing estimate rather than a tokenizer count. Generated by reading every `docs/codemap/*.md` with `Path.stat().st_size` after `--write`.

| File | Bytes | Approx. tokens |
|---|---:|---:|
| `docs/codemap/INDEX.md` | 9958 | 2490 |
| `docs/codemap/bench.md` | 409 | 103 |
| `docs/codemap/conformance.md` | 7903 | 1976 |
| `docs/codemap/docs__act-phrases.md` | 3748 | 937 |
| `docs/codemap/docs__arch.md` | 3866 | 967 |
| `docs/codemap/docs__architecture.md` | 156 | 39 |
| `docs/codemap/docs__defeasible.md` | 1535 | 384 |
| `docs/codemap/docs__devtime.md` | 150 | 38 |
| `docs/codemap/docs__eff-tests.md` | 142 | 36 |
| `docs/codemap/docs__events-time-causation.md` | 148 | 37 |
| `docs/codemap/docs__infra.md` | 1723 | 431 |
| `docs/codemap/docs__judgment-terms.md` | 306 | 77 |
| `docs/codemap/docs__lean-first__b0.md` | 131 | 33 |
| `docs/codemap/docs__lean-first__b1.md` | 277 | 70 |
| `docs/codemap/docs__lean-first__b10a.md` | 487 | 122 |
| `docs/codemap/docs__lean-first__b10b.md` | 363 | 91 |
| `docs/codemap/docs__lean-first__b11b.md` | 356 | 89 |
| `docs/codemap/docs__lean-first__b12.md` | 670 | 168 |
| `docs/codemap/docs__lean-first__b13a.md` | 119 | 30 |
| `docs/codemap/docs__lean-first__b13b.md` | 836 | 209 |
| `docs/codemap/docs__lean-first__b14a.md` | 862 | 216 |
| `docs/codemap/docs__lean-first__b14b.md` | 1435 | 359 |
| `docs/codemap/docs__lean-first__b14c.md` | 572 | 143 |
| `docs/codemap/docs__lean-first__b15a.md` | 272 | 68 |
| `docs/codemap/docs__lean-first__b15b.md` | 691 | 173 |
| `docs/codemap/docs__lean-first__b16b.md` | 1089 | 273 |
| `docs/codemap/docs__lean-first__b16c.md` | 228 | 57 |
| `docs/codemap/docs__lean-first__b16d.md` | 595 | 149 |
| `docs/codemap/docs__lean-first__b16e.md` | 741 | 186 |
| `docs/codemap/docs__lean-first__b16f.md` | 931 | 233 |
| `docs/codemap/docs__lean-first__b16g.md` | 153 | 39 |
| `docs/codemap/docs__lean-first__b17.md` | 111 | 28 |
| `docs/codemap/docs__lean-first__b18.md` | 504 | 126 |
| `docs/codemap/docs__lean-first__b2.md` | 934 | 234 |
| `docs/codemap/docs__lean-first__b3.md` | 139 | 35 |
| `docs/codemap/docs__lean-first__b3b.md` | 395 | 99 |
| `docs/codemap/docs__lean-first__b3d.md` | 397 | 100 |
| `docs/codemap/docs__lean-first__b4.md` | 277 | 70 |
| `docs/codemap/docs__lean-first__b5.md` | 230 | 58 |
| `docs/codemap/docs__lean-first__b6.md` | 405 | 102 |
| `docs/codemap/docs__lean-first__b7.md` | 313 | 79 |
| `docs/codemap/docs__lean-first__b8.md` | 462 | 116 |
| `docs/codemap/docs__lean-first__b9.md` | 679 | 170 |
| `docs/codemap/docs__lean-first__e2.md` | 226 | 57 |
| `docs/codemap/docs__math-evidence-me-1c.md` | 312 | 78 |
| `docs/codemap/docs__math-evidence.md` | 587 | 147 |
| `docs/codemap/docs__merge-tooling.md` | 140 | 35 |
| `docs/codemap/docs__oom-rootcause.md` | 300 | 75 |
| `docs/codemap/docs__premise-scale.md` | 593 | 149 |
| `docs/codemap/docs__question-answering.md` | 347 | 87 |
| `docs/codemap/docs__readings-defaults.md` | 1028 | 257 |
| `docs/codemap/docs__scale-choice-batch.md` | 124 | 31 |
| `docs/codemap/docs__scope.md` | 1042 | 261 |
| `docs/codemap/docs__spec.md` | 1279 | 320 |
| `docs/codemap/docs__speed.md` | 1636 | 409 |
| `docs/codemap/docs__test-architecture.md` | 2891 | 723 |
| `docs/codemap/docs__test-speed-b1.md` | 158 | 40 |
| `docs/codemap/docs__test-speed-b2.md` | 506 | 127 |
| `docs/codemap/docs__test-speed-b3.md` | 403 | 101 |
| `docs/codemap/docs__test-speed-b5.md` | 340 | 85 |
| `docs/codemap/docs__test-tail.md` | 138 | 35 |
| `docs/codemap/examples.md` | 110 | 28 |
| `docs/codemap/experiments.md` | 9493 | 2374 |
| `docs/codemap/lean.md` | 1202 | 301 |
| `docs/codemap/lean__ResponseShape.md` | 11969 | 2993 |
| `docs/codemap/lean__VE.md` | 2360 | 590 |
| `docs/codemap/lean__VE__Acts.md` | 2927 | 732 |
| `docs/codemap/lean__VE__Alternatives.md` | 2233 | 559 |
| `docs/codemap/lean__VE__Arith.md` | 1461 | 366 |
| `docs/codemap/lean__VE__Ask.md` | 2510 | 628 |
| `docs/codemap/lean__VE__Attribution.md` | 2675 | 669 |
| `docs/codemap/lean__VE__Calc.md` | 3946 | 987 |
| `docs/codemap/lean__VE__Cardinality.md` | 2380 | 595 |
| `docs/codemap/lean__VE__Closure.md` | 981 | 246 |
| `docs/codemap/lean__VE__Compose.md` | 834 | 209 |
| `docs/codemap/lean__VE__Core.md` | 1613 | 404 |
| `docs/codemap/lean__VE__Data.md` | 67 | 17 |
| `docs/codemap/lean__VE__Defaults.md` | 1514 | 379 |
| `docs/codemap/lean__VE__Definitions.md` | 847 | 212 |
| `docs/codemap/lean__VE__Discourse.md` | 3335 | 834 |
| `docs/codemap/lean__VE__English.md` | 2207 | 552 |
| `docs/codemap/lean__VE__EnglishGrammar.md` | 4745 | 1187 |
| `docs/codemap/lean__VE__Events.md` | 1723 | 431 |
| `docs/codemap/lean__VE__Grammar.md` | 985 | 247 |
| `docs/codemap/lean__VE__Judgments.md` | 560 | 140 |
| `docs/codemap/lean__VE__Kit.md` | 110 | 28 |
| `docs/codemap/lean__VE__Layout.md` | 464 | 116 |
| `docs/codemap/lean__VE__NormDefaults.md` | 4562 | 1141 |
| `docs/codemap/lean__VE__Norms.md` | 3827 | 957 |
| `docs/codemap/lean__VE__Numbers.md` | 328 | 82 |
| `docs/codemap/lean__VE__Order.md` | 1188 | 297 |
| `docs/codemap/lean__VE__Question.md` | 1368 | 342 |
| `docs/codemap/lean__VE__Readings.md` | 11323 | 2831 |
| `docs/codemap/lean__VE__Rights.md` | 1654 | 414 |
| `docs/codemap/lean__VE__Risk.md` | 1844 | 461 |
| `docs/codemap/lean__VE__Route.md` | 3434 | 859 |
| `docs/codemap/lean__VE__Scales.md` | 1087 | 272 |
| `docs/codemap/lean__VE__Scope.md` | 1598 | 400 |
| `docs/codemap/lean__VE__SearchBudget.md` | 791 | 198 |
| `docs/codemap/lean__VE__Senses.md` | 1702 | 426 |
| `docs/codemap/lean__VE__Service.md` | 3446 | 862 |
| `docs/codemap/lean__VE__SoftNorms.md` | 1621 | 406 |
| `docs/codemap/lean__VE__SpeechActs.md` | 1479 | 370 |
| `docs/codemap/lean__VE__Time.md` | 988 | 247 |
| `docs/codemap/lean__VE__WireContract.md` | 1473 | 369 |
| `docs/codemap/lean__VE__Words.md` | 382 | 96 |
| `docs/codemap/paper.md` | 1033 | 259 |
| `docs/codemap/research.md` | 310 | 78 |
| `docs/codemap/rust.md` | 2685 | 672 |
| `docs/codemap/tests--part-1.md` | 11982 | 2996 |
| `docs/codemap/tests--part-2.md` | 11983 | 2996 |
| `docs/codemap/tests--part-3.md` | 11838 | 2960 |
| `docs/codemap/tests--part-4.md` | 11954 | 2989 |
| `docs/codemap/tests--part-5.md` | 11900 | 2975 |
| `docs/codemap/tests--part-6.md` | 10943 | 2736 |
| `docs/codemap/tests__frozen_speech.md` | 281 | 71 |
| `docs/codemap/tools--part-1.md` | 11990 | 2998 |
| `docs/codemap/tools--part-2.md` | 189 | 48 |
| `docs/codemap/tools__bench.md` | 887 | 222 |
| `docs/codemap/tools__evidence.md` | 1034 | 259 |
| `docs/codemap/tools__hooks.md` | 109 | 28 |
| `docs/codemap/usecases.md` | 6895 | 1724 |
| `docs/codemap/ve.md` | 7982 | 1996 |
| `docs/codemap/ve__adapters.md` | 554 | 139 |
| `docs/codemap/ve__assist.md` | 1873 | 469 |
| `docs/codemap/ve__backends.md` | 1650 | 413 |
| `docs/codemap/ve__document.md` | 1355 | 339 |
| `docs/codemap/ve__english_grammar.md` | 139 | 35 |
| `docs/codemap/ve__lexicon.md` | 103 | 26 |
| `docs/codemap/ve__readings_verdicts.md` | 1080 | 270 |
| `docs/codemap/ve__senses.md` | 74 | 19 |
| `docs/codemap/ve__surface.md` | 1171 | 293 |
| `docs/codemap/ve__wire_contract.md` | 174 | 44 |
| `docs/codemap/ve_experiments.md` | 4233 | 1059 |
