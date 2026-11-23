# Sea and inland waterway passenger compensation, Reg (EU) 1177/2010 Arts 2, 3, 19, 20 (statute corpus batch 3, eu-sea-passengers): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-eu-sea-passengers (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author,
translator and encoder: dri-statute-corpus-eu-sea-passengers-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile,
refuses pair or lint change; nothing merges.

- `translation.py`: the in-scope units (stock/eu-sea-passengers/units.jsonl, 22) as RULE / PART / NOT entries over the
  passenger p, the carrier party c and the two ports e, d; translator readings R1-R6 (refusals where the text gives two
  readings); 13 planted errors (MUTANTS). Committed before the encoder's question file was opened.
- `smoke.py`: eleven made-up cases, run before any question was read.
- `cases.py` + `encode.py`: the encoder's facts from `questions-enc.jsonl` only; conventions C1-C4 and per-case judgement.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target
  (a certified sentinel value = premises with no model = refused). Adapted from usecases/fwa_australia/run.py.
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    .venv/bin/python -B usecases/eu_sea_passengers/run.py --mutants --out RUN.json
    python3 -I usecases/eu_sea_passengers/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/eu-sea-passengers
