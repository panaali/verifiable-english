# sick_pay: statutory sick pay, SSCBA 1992 ss. 151-155, 157 (statute corpus batch 3, law 8). Evidence branch, SAME-FAMILY, not for merge.

Row statute-corpus-sick-pay (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author, translator and
encoder: dri-statute-corpus-sick-pay-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or lint
change; nothing merges.

- `translation.py`: the 19 in-scope units (stock/sick-pay/units.jsonl) as RULE / PART entries, grounded per sub-case
  (one employee and one employer) over a chain of pieces of days; readings R1-R10 in its docstring; committed before the
  encoder's question file was read; planted errors (MUTANTS).
- `encode.py`: a sub-case spec (stated facts) -> pieces, weeks and facts; conventions C1-C6 (encoder judgement).
- `run.py`: the staged route (council_tax / pawhp runner, generalised), Lean replay of every certificate, one admitted
  document per answer target.
- `smoke_cases.py`, `smoke_test.py`: made-up cases written with the translation (not from the question file), hand-worked.
- After the questions are read: `cases.py` (the encoder's sub-cases from questions-enc.jsonl), `grade.py`.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    .venv/bin/python -B usecases/sick_pay/smoke_test.py
    .venv/bin/python -B usecases/sick_pay/run.py --mutants --out RUN.json
    python3 -I usecases/sick_pay/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/sick-pay
