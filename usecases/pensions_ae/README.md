# Pensions Act 2008 ss. 1, 3, 5, 13 (statute corpus batch 4, pensions-auto-enrolment): translation, encoding, run and grading. Evidence branch, NOT a merge candidate.

Row statute-corpus-pensions-auto-enrolment (manage-agents reviews/spare/statute-corpus/batch4/pensions-auto-enrolment).
CROSS-FAMILY questions (Codex writer, gpt-6-astra, sealed before translation), Opus 5.5 translator and encoder
(dri-statute-corpus-pensions-auto-enrolment-w-1124). Nothing here is a Lean kernel line, profile, refuses pair or lint
change; nothing merges.

- `translation.py`: the 23 in-scope units as RULE / PART / NOT entries, grounded per employment; readings R1-R12 in its
  docstring; committed before the encoder's question file was read; 17 planted errors (MUTANTS).
- `encode.py` (+ `cases.py`, written after the commit): the encoder's facts from `questions-enc.jsonl` only; conventions C1-C6.
- `bridge/`: the one tested bridge script (age on a day; the first day of the 12 months ending with the day before a day;
  the days of a window); `python3 -I bridge/test_bridge.py`.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target
  (from usecases/posthog_leave/run.py).
- `smoke_test.py` + `smoke_cases.py`: made-up cases written with the translation (not from the question file).

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/pensions_ae/bridge/test_bridge.py
    .venv/bin/python -B usecases/pensions_ae/smoke_test.py
    .venv/bin/python -B usecases/pensions_ae/run.py --mutants --out RUN.json
    python3 -I usecases/pensions_ae/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/pensions-auto-enrolment
