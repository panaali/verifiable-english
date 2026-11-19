# defs-repair-math-mini-paper-1119 REPORT

DRI signature needed: none. Every DELTA row cites R3, and trust is +0.

- **Status:** both P1 rows KEPT and carried word for word. Ready for the chain gate.
- **Base:** rebased on main 9b72137abf. The audit was read at pin 3d6b459df4.
- **Changed:** the `sim` legend (environment.json) and the `r` legend (environment-closure.json). The derived files were regenerated with the project's tools. The new condition test is `tests/test_defs_repair_math_mini_paper_1119.py`.
- **Open:** `t7-definitions-bundle.json` was not regenerated, because its tool `verify_definitions.py` already fails on main (see "Not done").
- **Answers touched:** 11 of 19 keyed. Row 1: T6, T7, T7a, T7b, T7mono. Row 2: T9, T9a-T9e. Their verdict.json bytes are unchanged.

## 0. Verify first

The source is checked at main, in `usecases/math-mini-paper/paper.template.md`. There is no hash-pinned source (METHOD amendment 8). The frozen text is the live legends at main.

| row id | KEPT / DROPPED | reason |
|---|---|---|
| defs-math-mini-paper-1-1119 | KEPT | D3 is at paper.template.md:280 ("**Prose.** For a preorder *(X, ≤)* put *x ∼ y* iff *x ≤ y* and *y ≤ x*."). The `sim` legend at environment.json:81 (main) only names the predicate and does not hold it. T7 uses `sim` (theorems/T7/premises.ve:1-3, conclusion.ve:1), and its premises.ve has no definition axiom, so the verdict is ELSEWHERE. The audit quote equals the source span once `*` emphasis is left out. |
| defs-math-mini-paper-2-1119 | KEPT | The sentence is at paper.template.md:430-432. The `r` legend at environment-closure.json:24 (main) says only "The base edge relation whose transitive closure is discussed.", so the sentence is NOT CARRIED. `tc[r]` appears in the conclusion.ve of T9, T9a, T9b, T9c, T9d and T9e. The audit quote equals the source span. |

The condition test checks both rows' spans against the source file: `test_source_definition_is_carried_in_the_rules_legend` asserts sentence == audit quote, and `test_carrier_is_used_by_the_rules_it_serves` checks rule usage. P2 rows 3-7 were not taken, as the task says.

## 1. Carried (deliverable 1)

Each sentence is appended to the legend's `description` after the old text, which stays unchanged:
- `usecases/math-mini-paper/environment.json`, `sim`: "For a preorder (X, ≤) put x ∼ y iff x ≤ y and y ≤ x."
- `usecases/math-mini-paper/environment-closure.json`, `r`: "The closure profile adds `tc[r](a, b)` and `rtc[r](a, b)` — the transitive and reflexive-transitive closures of a named homogeneous binary relation — with a least-fixed-point semantics over arbitrary, possibly infinite structures."

The text is the source's own. Markdown emphasis `*` is left out (it is markup), and backticks are kept as in the source. Neither carrier is in a frozen or sealed run directory: `usecases/math-mini-paper/` has no frozen-run.json or seal file. The legends are hand-written inputs that `theory.py` reads (theory.py:18-19). No rule formula and no theorem statement changed: the premises.ve and conclusion.ve bytes are identical after `verify.py` rewrote them (git status shows no change).

## 2. Regenerated (deliverable 2), only with the project's tools

- `uv run python usecases/math-mini-paper/verify.py`, then `make_paper.py`. These are verify.sh's steps; the boundary probe was skipped because its inputs are unchanged. Results:
  - 15 certificates were re-pinned: C2, T1-T8, T7a, T7b and T9a-T9d. A field diff (/tmp/mmp_jsondiff.py against HEAD) shows changes only in `environment_id`, `conclusion_meaning_id` and `premise_meaning_ids` (the meaning ids hash the environment id), plus `checker_version` on T9a-T9d.
  - All 15 `trace` values are byte-identical to the committed ones (checked per file). Certified: Python 15/19 and Lean 15/19, the same as committed (report.md).
  - The countermodels, vocabulary-lint.json, premises.ve and conclusion.ve came out identical.
  - `results.json`, the 19 `verdict.json`, `report.md` and `paper.md` differed only in wall-clock seconds. A float-masked text compare and a field diff show only `prove_seconds`, `necessity[].seconds` and `refutation_seconds`. These four were kept at their committed bytes because nothing in them depends on the legends. This was the conservative choice: keyed answers stay untouched and no timing churn is added.
- `uv run python usecases/closure-induction/verify.py`: the T9_induction and T9e_induction `query.json` files were regenerated. They embed the `r` legend and the new environment id.
- `uv run python -m conformance.english_lean_lexicon`: `lexicon-report.json` changed only in the two math-mini-paper `lexicon_id`s. The selected run found this as the failure of `tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon`; after regeneration it passes.
- `uv run python -m conformance.english_lean_seal`: `corpus-seal.json` was resealed, first at f5553bc894 and again after the rebase onto 9b72137abf. The tool has no per-file mode, so the reseal also renews the 55 entries that were already stale at main (`--check` at f5553bc894 printed 55 differences, /tmp/mmp-seal-main.txt). After the reseal, `--check` prints 0 differences.
- `uv run python tools/regen_generated.py --check` exits 0 after the rebase. None of the files above are registered there.

### Not done (real seam)
`usecases/math-mini-paper/t7-definitions-bundle.json` embeds a copy of `environment.json`, so it holds the old `sim` legend. Its tool, `verify_definitions.py`, exits 1 on unmodified main with `VEError: Citation hypothesis is absent from the citing branch`, raised from `ve/bundle.py:146` (`check_bundle`), before it writes anything. This was run with main's environment.json; log /tmp/mmp-vdef-main.log. It cannot be regenerated with the project's tool until that is fixed, and a hand edit is not allowed. The bundle is a self-contained fixture of `tests/test_bundle.py`, not the rules' carrier, so neither row's carry depends on it.

## 3. Condition test (deliverable 3)

`tests/test_defs_repair_math_mini_paper_1119.py` has 4 tests. Each sentence is read from paper.template.md, with emphasis stripped, then normalised by `tests/omission_rule.py:omit_norm`.
- On the pre-change tree (the test commit alone on f5553bc894; main 9b72137abf has the same usecases/math-mini-paper and closure-induction bytes): 2 failed (both carry asserts), 2 passed (/tmp/mmp-t1.log).
- After the change: 4 passed (/tmp/mmp-t2.log). On the rebased HEAD, 6 passed together with the lexicon and seal tests (/tmp/mmp-t4.log).
- The file's path matches the selector (`changed` list in /tmp/mmp-select.log).

## Seeded bugs

No Lean, Python or Rust product code changed. `tools/trust_mutants.py --plan` lists 0 definitions and 0 mutants; it is saved as `trust-mutants-plan.json`. Light lane printed NOT: 362 lines, because certificates and the seal are not registered generated files. With an empty plan there is nothing to sweep, so no sweep was queued.

Five seeded bugs were planted, one per claimed behaviour. Each was restored afterwards; the tree was clean. Record: `mutants.json`.

| bug | file | failing test |
|---|---|---|
| sim legend drops "and y ≤ x" | usecases/math-mini-paper/environment.json | `test_source_definition_is_carried_in_the_rules_legend[defs-math-mini-paper-1-1119]` |
| r legend "possibly infinite" -> "finite" | usecases/math-mini-paper/environment-closure.json | `test_source_definition_is_carried_in_the_rules_legend[defs-math-mini-paper-2-1119]` |
| T6 certificate keeps the old environment_id | usecases/math-mini-paper/theorems/T6/certificate.json | `test_certificates_pin_the_carrier_environments` |
| T9_induction query keeps a different r legend | usecases/closure-induction/T9_induction/query.json | `test_certificates_pin_the_carrier_environments` |
| source D3 "preorder" -> "partial order" | usecases/math-mini-paper/paper.template.md | `test_source_definition_is_carried_in_the_rules_legend[defs-math-mini-paper-1-1119]` |

## Trust, size, tests

- **Trust:** `uv run python tools/trust_map.py --check` against f5553bc894 gives K +0, S +0, D +0, G +0, tied +0, trusted +0: PASS (/tmp/mmp-trust.log). No allowance and no R16 FOLLOW-UPS row.
- **SIZE:** 0 product, 118 tests, 173 other hand-written lines. The 173 are 2 legend lines, plus 171 lines of DELTA.md, REPORT.md and mutants.json. Regenerated files are not counted: the seal (+178/-28), 15 certificates, 2 query.json and the lexicon report (2 lines).
- **Selected run:** `mac-pytest.sh --select` on 35bba3b8 ran on the VM (no Mac slot). 42 units: 1 failed, the lexicon id fixed above, and the rest passed (/tmp/mmp-select.log). 8 heavy files were deferred to the chain gate.
- **After the fix:** the failed id plus the new test passed (/tmp/mmp-t3.log).
- **Collection:** `tools/gate_collection.py --check --prebuilt` reports 4 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- **Known red:** no test listed in main-known-red.txt was touched.
- **Gate:** the full gate was not run here; the chain runs it on the final HEAD.
- **Pilot bytes expected to move (estimate; nothing is claimed before a pilot audit):** the two carried sentences, 51 + 233 characters of legend text on the surface the audit counts. These are 2 P1 (term, carrier) pairs: `sim` for T6/T7/T7a/T7b/T7mono and `tc`/`rtc` via `r` for T9-T9e.

## Spec re-read
- D3 legend append, checked against paper.template.md:280 and rows-math-mini-paper.tsv row 1 `quote`: identical after emphasis removal.
- Closure-profile append, checked against paper.template.md:430-432 and rows-math-mini-paper.tsv row 2 `quote`: identical, line breaks joined by single spaces.
- DELTA rows, checked against DRI-RULINGS.md R3: information added, nothing removed or renamed; goldens updated; a test checks the field holds the true source text; nothing to bind.

## Notes for the DRI
- The audit says C1 and T7mono have no certificate.json. At main they are empty (0-byte) files, as are T9 and T9e, which did not certify. They stay empty.
- `checker_version` on T9a-T9d moves from `ve-tableau-closure-checker@0` to `@1`. This is because main's prover has emitted @1 since 441c236a4b. The trace bytes are identical, and Python and Lean both replay them (`tests/test_closure_induction.py`, in the selected run). It is not a verdict change, so there is no DELTA row.
- T9e also uses `tc[s]`. The audit names the `s` legend as a possible second carrier. It was not added, because it is not in the row.
- The seal reseal renews 55 stale entries from other changes (section 2). Siblings bluedot-grant and eligibility also regenerate this file. On a conflict, take main's version and rerun `python -m conformance.english_lean_seal`.

## Self-review against BUILDER-CHECKLIST
1. N.A.: no Lean answer, route or relay changed.
2. PASS: deliverables 0-3 are above, with commits 16f6067ecc and bf43185d64 and the condition test. The bundle seam is named with the reason. No Python copy of a decision; no report test; no overlap with in-flight branches (checked with `git diff --name-only main...<branch>` for every feature/infra/lean-first/foundation branch: none touch these files).
3. PASS: 5 seeded bugs, each failing a named test (mutants.json).
4. N.A.: no Python/Lean/Rust behaviour changed. Python and Lean replay of the regenerated certificates: `test_all_committed_mini_paper_certificates_still_replay_unchanged`.
5. N.A.: no relayed field.
6. PASS: rebased on main 9b72137abf, then the generated files were regenerated and their tests rerun (/tmp/mmp-t4.log). The gate runs in the chain on the final HEAD.
7. PASS: both DELTA rows cite R3 with its tests; no reserved signature.
8. PASS: DELTA rows 1-2 cover both legend changes. Verdict, rendered paper and lint are unchanged (git status after verify.py, section 2).
9. PASS: the selected run picked `tests/test_english_lean_lexicon.py`, which caught the lexicon drift, and the new test (/tmp/mmp-select.log).
10. N.A.: no Lean statement or proof.
11. N.A.: no budget, limit or deadline code.
12. N.A.: no code path changed. Prove steps are unchanged; traces are identical.
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 removed, 0 stale, 0 malformed.
14. PASS: opposite directions are covered. Pre-change main fails, the change passes, and mutants m1-m5 fail. Each claim above cites its command or log. The spec re-read is listed.
15. PASS:
    - Overclaim: "unchanged" claims cite git status, the field diff and the trace compare.
    - No silent cut: the bundle is a seam, not a size cut.
    - Every new check can fail: m1-m5.
    - Limits: N.A.

FOLLOW-UP: defs-repair-math-mini-paper-1119b regenerate usecases/math-mini-paper/t7-definitions-bundle.json with verify_definitions.py once its Lean bundle check passes on main
