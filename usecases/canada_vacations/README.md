# canada_vacations: Canada Labour Code ss.183-189 (annual vacations), statute corpus batch 4 (evidence branch, not for merge)

CROSS-FAMILY questions (Codex writer, sealed in manage-agents reviews/spare/statute-corpus/batch4/canada-vacations/ISOLATION.md),
Opus translator/encoder (dri-statute-corpus-canada-vacations-w-1124).

- translation.py: the units (17 in scope; unit 16 = s.189(1.5) out: unapplied amendment), readings R1-R10, planted errors.
- bridge/bridge.py (+ test_bridge.py): the ONE bridge: years-of-employment counts, the ten months, s.189(1.4)'s left-out gap.
- encode.py: the encoder conventions C1-C5; cases.py: the encoder's cases (from questions-enc.jsonl only, written after the
  translation commit).
- run.py: the staged Lean route (step certificates + documents@1 answer documents); grade.py: compare with the seal.
- smoke_cases.py / smoke_test.py: made-up cases with hand-worked answers; every planted error must change one.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/canada_vacations/bridge/test_bridge.py
    .venv/bin/python -B usecases/canada_vacations/smoke_test.py
    .venv/bin/python -B usecases/canada_vacations/run.py --smoke --out SMOKE.json
    .venv/bin/python -B usecases/canada_vacations/run.py --mutants --out RUN.json
    python3 -I usecases/canada_vacations/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch4/canada-vacations
Nothing here is a Lean kernel line, a profile, a refuses pair or a lint change.
