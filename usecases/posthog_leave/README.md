# PostHog handbook "Time off" (statute corpus batch 4, posthog-leave): translation, encoding, run and grading. Evidence branch, NOT a merge candidate.

Row statute-corpus-posthog-leave (manage-agents reviews/spare/statute-corpus/batch4/posthog-leave). CROSS-FAMILY questions
(Codex writer, gpt-6-astra, sealed before translation), Opus 5.5 translator and encoder (dri-statute-corpus-posthog-leave-w-1124).
Nothing here is a Lean kernel line, profile, refuses pair or lint change; nothing merges.

- `translation.py`: the policy's 46 in-scope units as RULE / PART / NOT entries, grounded per case; readings R1-R12 in its
  docstring; committed before the encoder's question file was read; 15 planted errors (MUTANTS).
- `encode.py` (+ `cases.py`, written after the commit): the encoder's facts from `questions-enc.jsonl` only; conventions C1-C5.
- `bridge/`: the one tested bridge script (the day 4 months before; calendar quarters; the prior two full quarters);
  `python3 -I bridge/test_bridge.py`.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target
  (from usecases/fmla_eligibility/run.py).
- `smoke_test.py` + `smoke_cases.py`: made-up cases written with the translation (not from the question file).

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/posthog_leave/bridge/test_bridge.py
    .venv/bin/python -B usecases/posthog_leave/smoke_test.py
    .venv/bin/python -B usecases/posthog_leave/run.py --mutants --out RUN.json
    python3 -I usecases/posthog_leave/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/posthog-leave
