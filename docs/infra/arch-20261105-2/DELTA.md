# arch-20261105-2: deltas

None user-visible. The batch changes test files, test-class Lean (`lean/VE/Senses/RunExamples.lean`: `#guard`s and
three helpers classed T), one evidence tool (`tools/ask_fixtures.py`), one report writer's hash seed
(`conformance/english_lean_s3_compare.py`) and the generated-file list (`tools/regen_generated.py`). It changes no
`ve/` module, no Lean product definition, no response schema and no Rust; `lean/checkers.lock` is not in
`git diff --stat main...HEAD`. Every Lean answer still carries `actions_version`.

The corpus A/B (`evidence/ab.json`, base `e433588f`, the merge base) found no record whose result differs: every
record that differed between the two recordings is either one of 7 whole-UDHR `document_check` records that hit
the recorder's 600 s timeout on the head side only while the machine's load average was above 100 on 32 cores
(re-run one at a time with the recorder's own `pilot_check`, `rerun_timeouts.py`; each then equals the base), or
is unavailable on both sides with identical outputs. The latter are listed with their reasons in
`evidence/ab-delta.json` and are the only rows here.

| # | Records | What both sides return | Ruling | Test |
|---|---|---|---|---|
| 1 | 17 `pilots/default` `document_check` records of `translation-companions-with_source_word.ve.md` (one per constitution pilot run) and 1 `et0-not-landed/translation-whole.et0.ve.md` | The same pre-existing unavailable outcome, byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/infra/arch-20261105-2/evidence/ab-delta.json` (0 unlisted) |
| 2 | 2 `discourse/default` records (`document_check`, `document_render`) of one generated discourse case | The same pre-existing `CheckerUnavailable` (a norm object the norms route refuses keeps its loader's diagnostic), byte for byte | R7 | as row 1 |
| 3 | 2 whole-UDHR `pilots/default` `document_check` records (runs 20261028T1800Z and 20261101T1800Z) | `{"timeout": 600}` on both sides | R7 | as row 1 |
