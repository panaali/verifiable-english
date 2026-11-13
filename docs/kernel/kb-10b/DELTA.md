# kb-10b: user-visible delta (round 1: step (1), the shadow)

This round adds a test-only script (`usecases/safetyfw_shadow.py`), its self-test (`tests/test_kb10_shadow.py`) and
three saved evidence files. No product file changed (`git diff --stat $(git merge-base HEAD main) HEAD -- ve tools
conformance lean rust` is empty), so no answer, diagnostic, verdict or limit changed. The three safety-framework
harnesses, run with `--check` under the shadow, each exited 0 (`harness_outcome` in each kb10-shadow.json), and no
`results.json` changed.

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | Generated files only: the code map (`docs/codemap/INDEX.md`, `usecases.md`, `tests--part-4.md` to `tests--part-8.md`, and `lean__VE__Route.md`, which gains main's `lean/VE/Route/CodecRoundTrip.lean` line that main's map lacked) and `tests/history-dependent.json` (the new test, since the shadow records `git rev-parse HEAD` in its report), through `uv run python tools/regen_generated.py --write` | `uv run python tools/regen_generated.py --check` | R12 |
| 2 | Shadow evidence rows now carry the recorded model digest and exact per-call choice and case, including direct probe documents and N3 witness identities; the original full-run comparison counts and commit stay intact. Twelve empty saved choice inventories were filled from targeted harness probes, with the correction commit recorded in each report. | `tests/test_kb10_shadow.py::test_query_only_probe_mismatch_keeps_its_actual_choice_and_case`, `::test_reused_document_keeps_choice_case_and_model_in_every_report_row`; the saved inventories have zero empty entries. | R3 |
