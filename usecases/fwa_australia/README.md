# Notice of termination and redundancy pay, Fair Work Act 2009 (Cth) ss. 117, 119, 121(1), 123 (statute corpus batch 3, fwa-australia): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-fwa-australia (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author,
translator and encoder: dri-statute-corpus-fwa-australia-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile,
refuses pair or lint change; nothing merges.

- `translation.py`: the in-scope units (stock/fwa-australia/units.jsonl, 26) as RULE / PART / NOT entries for one
  employee; 10 planted errors (MUTANTS).
- `cases.py` + `encode.py`: the encoder's facts from `questions-enc.jsonl` only; conventions C1-C4 and per-case judgement.
- `bridge/`: the one tested bridge script (the age on the notice day as years and days; the comparison with 45 stays
  in the translation) and its output `bridges.jsonl`.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target
  (a certified sentinel value = premises with no model = refused). Adapted from usecases/council_tax/run.py.
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/fwa_australia/bridge/test_age.py
    python3 -I usecases/fwa_australia/bridge/age.py
    .venv/bin/python -B usecases/fwa_australia/run.py --mutants --out RUN.json
    python3 -I usecases/fwa_australia/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/fwa-australia
