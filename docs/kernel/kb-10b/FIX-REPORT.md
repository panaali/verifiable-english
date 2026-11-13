# kb-10b review fix

Status: F1 fixed in `33d8077a46`; saved evidence repaired in `3162f48995`; all required checks passed. No DRI signature is needed.
Open: none for this review fix; no product, Lean, or Rust code changed.
The three original full-run reports still record 180,587 comparisons and zero mismatches; this fix corrects identity attribution if a mismatch, refusal, or background-false call occurs.

## F1 — required mismatch identities

The recorder now captures the active choice and case on every call. It uses the current harness call rather than the first label attached to a shared document. Directly constructed probe documents receive their full choice, and N3 witness calls receive their rule and situation. Mismatch, refusal, and background-false rows include the recorded model digest, so distinct cases cannot collapse under one output key. `calls_by_family` still uses the original item context.

The executable F1 probe failed before the fix with `AssertionError: missing document choices for N2` and passed afterward. The regression `tests/test_kb10_shadow.py::test_query_only_probe_mismatch_keeps_its_actual_choice_and_case` checks N2 and the RSP G1 sibling against each harness's returned choice assignments. `::test_reused_document_keeps_choice_case_and_model_in_every_report_row` checks reuse across choices, cases, and models and checks all three output row kinds. A planted Python bug that reused the document's first choice failed that second test (`/tmp/kb10b-mutant.log`); it was restored before commit.

The two original reports had six empty choice lists each. `repair_shadow_choices.py` reran only the direct G1/G3 and N2 probes across baseline, m1–m6, and N1–N3 and filled those twelve lists by document digest. Both reports retain the original full-run `commit`, counts, and zero-mismatch result; `choice_label_correction` records the code commit and method. All three saved reports now have zero empty choice lists. No full harness replay was performed.

## Verification

- Targeted regressions: N2 and G1 passed; the reused-document regression passed after the planted bug was restored.
- `lake build`: passed, 1,438 jobs.
- `python3 lean/audit.py`: passed, 872 source files and 9,965 named theorem declarations.
- `uv run python tools/regen_generated.py --check`: passed, 41 entries.
- Selected tests: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` passed on code/evidence HEAD `3162f48995` (GitHub Actions run `kb-10b-3162f489-t602508`, 48 units across three shards: 16 + 18 + 14 passed, zero failed). The selector deferred eight weakly related slow files to the chain gate.
- Main's known red tests in `main-known-red.txt` were not edited: two sub-tick deadline variants and `test_review_fix_commit_chain_and_final_gate_target`. Any appearance in this selection is pre-existing.
- No full suite, release gate, or trust-mutant sweep was run. The change is confined to the Python shadow helper, its regression tests, and saved evidence.
