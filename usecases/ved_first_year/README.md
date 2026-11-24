# Vehicle excise duty, light passenger vehicles from 1 April 2017, VERA 1994 Sch 1 Part 1AA (statute corpus batch 3, ved-first-year): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-ved-first-year (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author,
translator and encoder: dri-statute-corpus-ved-first-year-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile,
refuses pair or lint change; nothing merges.

- `translation.py`: the in-scope units (stock/ved-first-year/units.jsonl, 41; 25 table rows) as RULE / PART / NOT entries;
  readings R1-R6; 13 planted errors (MUTANTS).
- `encode.py` (conventions C1-C5) + `cases.py` (the encoder's facts from `questions-enc.jsonl` only, written after the
  translation commit).
- `bridge/`: the one tested bridge script (whole years and days from the first registration to a licence's date; the
  comparison with six years stays in the translation) and its output `bridges.jsonl`.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target.
  Adapted from usecases/fwa_australia/run.py. `smoke.py`: five made-up cases (never graded) checking the pieces fit.
- `flips.py`, `grade.py`: written after the cases, committed before the headline run.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/ved_first_year/bridge/test_years.py
    python3 -I usecases/ved_first_year/bridge/years.py
    .venv/bin/python -B usecases/ved_first_year/run.py --mutants --out RUN.json
    python3 -I usecases/ved_first_year/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/ved-first-year
