# copilot_ext_policy: GitHub Copilot Extension Developer Policy (statute corpus batch 4, NON-STATUTE (c), STAND-IN). Evidence branch, CROSS-FAMILY questions (Codex writer), Opus translator; not for merge.

Row statute-corpus-github-copilot-ext (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus batch 4).
Translator and encoder: dri-statute-corpus-github-copilot-ext-w-1124 (Opus 5.5). The questions were written and sealed by one
Codex session (gpt-6-astra) before this translation (manage-agents reviews/spare/statute-corpus/batch4/github-copilot-ext/
ISOLATION.md). Nothing here is a Lean kernel line, profile, refuses pair or lint change; nothing merges.

- `translation.py`: the 38 in-scope units as RULE / PART entries (yes/no classifications of the case's items, Lean dates);
  readings R1-R12 in its docstring; 13 planted errors (MUTANTS).
- `encode.py`: a case spec -> items and facts; conventions C1-C4 (encoder judgement where they decide anything).
- `run.py`: the staged route (oas_canada runner), Lean replay of every certificate, one admitted document chain per answer.
- `smoke_cases.py`, `smoke_test.py`: made-up cases, hand-worked from the readings (51/51; 13 of 13 planted errors killed).
- After the translation commit: `cases.py` (the encoder's cases from questions-enc.jsonl), `grade.py`.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    .venv/bin/python -B usecases/copilot_ext_policy/smoke_test.py
    .venv/bin/python -B usecases/copilot_ext_policy/run.py --mutants --out RUN.json
    python3 -I usecases/copilot_ext_policy/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/github-copilot-ext
