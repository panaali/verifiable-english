# hipaa_breach_notice: HIPAA breach notification, 45 CFR 164.402-164.414 (eCFR 2026-11-20; statute corpus batch 4, regulation, US data security). Evidence branch, not for merge.

Row statute-corpus-hipaa-breach-notice (manage-agents reviews/spare/statute-corpus/batch4/hipaa-breach-notice). Questions:
CROSS-FAMILY (one Codex writer session, gpt-6-astra, sealed in ISOLATION.md). Translator and encoder:
dri-statute-corpus-hipaa-breach-notice-w-1124 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or lint
change; nothing merges.

- `translation.py`: the 30 in-scope units as RULE / PART / NOT entries, grounded per case; readings R1-R11; 14 planted errors.
  No bridge: every day and count step (60 / 30 days, the earliest qualifying discovery day, 31 December of the year of
  discovery from a calendar table, the sum of the per-State residents) is in Lean.
- `encode.py`: a case record (stated facts) -> facts; conventions C1-C5.
- `run.py`: the staged route (wmf_nonpublic_access runner, adapted), Lean replay of every certificate, one admitted document
  chain per answer target; Q2 recipients composed from Lean-admitted atoms.
- `smoke_test.py`: made-up cases, hand-worked; every planted error must change one.
- `grade.py`: the grader (sealed hashes checked), written with the translation.
- After the translation commit: `cases.py` (the encoder's cases from questions-enc.jsonl).

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    .venv/bin/python -B usecases/hipaa_breach_notice/smoke_test.py
    .venv/bin/python -B usecases/hipaa_breach_notice/run.py --mutants --out RUN.json
    python3 -I usecases/hipaa_breach_notice/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/hipaa-breach-notice
