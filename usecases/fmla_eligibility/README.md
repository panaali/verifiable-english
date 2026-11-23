# FMLA eligible employee, 29 CFR 825.110 (statute corpus batch 3, law 1): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-fmla-eligibility (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author,
translator and encoder: dri-statute-corpus-fmla-eligibility-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile,
refuses pair or lint change; nothing merges.

- `translation.py`: the regulation's 14 in-scope units (stock/fmla-eligibility/units.jsonl) as RULE / PART / NOT entries,
  grounded per case; readings R1-R5 in its docstring; committed (92e36c119b) before the encoder's question file was read,
  unchanged after; 9 planted errors (MUTANTS).
- `cases.py` + `encode.py`: the encoder's facts from `questions-enc.jsonl` only; conventions C1-C5 and per-case judgement.
- `bridge/`: the one tested bridge script (dates to the 12-month period's first day, to whole months + days, to Monday-Sunday
  weeks) and its output `bridges.jsonl`; `python3 -I bridge/test_bridge.py`.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target.
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.
- `smoke_test.py`: six made-up cases written with the translation (not from the question file).

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/fmla_eligibility/bridge/test_bridge.py
    .venv/bin/python -B usecases/fmla_eligibility/run.py --mutants --out RUN.json
    python3 -I usecases/fmla_eligibility/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/fmla-eligibility
