# kb-10b: user-visible delta (round 1: step (1), the shadow)

This round adds a test-only script (`usecases/safetyfw_shadow.py`), its self-test (`tests/test_kb10_shadow.py`) and
three saved evidence files. No product file changed (`git diff --stat $(git merge-base HEAD main) HEAD -- ve tools
conformance lean rust` is empty), so no answer, diagnostic, verdict or limit changed. The three safety-framework
harnesses, run with `--check` under the shadow, each exited 0 (`harness_outcome` in each kb10-shadow.json), and no
`results.json` changed.

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | Generated files only: the code map (`docs/codemap/INDEX.md`, `usecases.md`, `tests--part-4.md` to `tests--part-8.md`, and `lean__VE__Route.md`, which gains main's `lean/VE/Route/CodecRoundTrip.lean` line that main's map lacked) and `tests/history-dependent.json` (the new test, since the shadow records `git rev-parse HEAD` in its report), through `uv run python tools/regen_generated.py --write` | `uv run python tools/regen_generated.py --check` | R12 |
