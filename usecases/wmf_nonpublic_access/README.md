# wmf_nonpublic_access: Wikimedia Foundation Access to Nonpublic Personal Data Policy (oldid 556416; statute corpus batch 4, NON-STATUTE (e)). Evidence branch, not for merge.

Row statute-corpus-wmf-nonpublic-access (manage-agents reviews/spare/statute-corpus/batch4/wmf-nonpublic-access). Questions:
CROSS-FAMILY (one Codex writer session, gpt-6-astra, sealed in ISOLATION.md). Translator and encoder:
dri-statute-corpus-wmf-nonpublic-access-w-1124 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or lint
change; nothing merges.

- `translation.py`: the 40 in-scope units as RULE / PART / NOT entries, grounded per case; readings R1-R14; planted errors.
- `bridge/wmf_bridge.py` (+ `test_bridge.py`): the ONE bridge: the days a member attains 16 and 18; the tenth business day
  counting back from a disclosure day.
- `encode.py`: a case record (stated facts) -> facts; conventions C1-C5.
- `run.py`: the staged route (fmla_eligibility runner, adapted), Lean replay of every certificate, one admitted document
  chain per answer target.
- `smoke_test.py`: made-up cases, hand-worked; every planted error must change one.
- After the translation commit: `cases.py` (the encoder's cases from questions-enc.jsonl), `grade.py`.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/wmf_nonpublic_access/bridge/test_bridge.py
    .venv/bin/python -B usecases/wmf_nonpublic_access/smoke_test.py
    .venv/bin/python -B usecases/wmf_nonpublic_access/run.py --mutants --out RUN.json
    python3 -I usecases/wmf_nonpublic_access/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/wmf-nonpublic-access
