# Council tax England, LGFA 1992 (statute corpus batch 2, law 5): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-council-tax (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author,
translator and encoder: dri-statute-corpus-council-tax-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile,
refuses pair or lint change; nothing merges.

- `translation.py`: the Act's in-scope units (batch2/council-tax/units.jsonl) as RULE / PART / NOT entries, grounded per
  case; committed (5488edc452) before the encoder's question file was opened; 7 planted errors (MUTANTS).
- `cases.py` + `encode.py`: the encoder's facts from `questions-enc.jsonl` only; conventions C1-C4 and per-case judgement.
- `bridge/`: the one tested bridge script (Sch. 1 para. 3(1)(a), attained the age of 18) and its output `bridges.jsonl`.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target
  (a certified sentinel value = premises with no model = refused).
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/council_tax/bridge/test_age.py
    .venv/bin/python -B usecases/council_tax/run.py --mutants --out RUN.json
    python3 -I usecases/council_tax/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch2/council-tax
