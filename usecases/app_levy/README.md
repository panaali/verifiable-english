# Apprenticeship levy, FA 2016 ss. 99-101 (statute corpus batch 3, app-levy): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-app-levy (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author, translator and
encoder: dri-statute-corpus-app-levy-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or lint
change; nothing merges.

- `translation.py`: the in-scope units (stock/app-levy/units.jsonl, 28) as RULE / PART / NOT entries over persons,
  earnings items and connected groups; translator readings R1-R10 (refusals where the text gives two outcomes or none);
  11 planted errors (MUTANTS). Committed before the encoder's question file was opened.
- `smoke.py`: nine made-up cases, run before any question was read.
- `cases.py` + `encode.py`: the encoder's facts from `questions-enc.jsonl` only; conventions C1-C7 and per-case judgement.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target
  (a certified sentinel value = premises with no model = refused). Adapted from usecases/council_tax/run.py.
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    .venv/bin/python -B usecases/app_levy/run.py --mutants --out RUN.json
    python3 -I usecases/app_levy/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/app-levy
