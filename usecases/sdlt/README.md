# SDLT, FA 2003 s.55 + Sch 6ZA (statute corpus batch 2 law 1): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-sdlt (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus batch 2). Author, translator
and encoder: dri-statute-corpus-sdlt-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or lint
change; nothing merges.

- `translation.py`: the in-scope units (batch2/sdlt/units.jsonl) as RULE / PART / NOT entries, grounded per case;
  committed BEFORE the encoder's question file was opened; 6 planted errors (MUTANTS).
- `smoke_cases.py` + `test_smoke.py`: synthetic cases with hand-worked answers and a kill for every planted error.
- `encode.py` (+ `cases.py`, added after this commit): the encoder's facts from `questions-enc.jsonl` only; conventions C1-C4.
- `run.py`: staged proofs per derived fact and per derived amount, Lean replay of every certificate, one admitted
  documents@1 document per answer target (fork of usecases/tenant_fees/run.py).
- `grade.py`: compares a run file with the sealed answers (sha256 checked).

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    .venv/bin/python -B usecases/sdlt/test_smoke.py
    .venv/bin/python -B usecases/sdlt/run.py --mutants --out RUN.json
    python3 -I usecases/sdlt/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch2/sdlt
