# PAWHP (SSI 2024/351): statute corpus law 1, build half. SAME-FAMILY evidence branch, NOT a merge candidate.

Row spare-second-statute-build (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author, translator
and encoder: dri-spare-second-statute-build-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or
lint change; nothing merges.

- `rows_v2.py`: the formulas, a byte-for-byte copy of pass65.py v2 lines 37-348 (hash-checked at import).
- `translation.py`: mechanical grounding over a case's people, splitting, "defines"; 5 planted errors (MUTANTS).
- `cases.py` + `encode.py`: the encoder's facts, from `questions-enc.jsonl` only; conventions C1-C6 and per-case judgement.
- Free in-patient treatment (row statute-xfam-wrong-pawhp-1, 2026-11-24): the encoder states only a stay's dates (`"fipt"`);
  `translation.fipt_rules` derives the two reg. 9(a) facts in the checker (SI 2005/3360 reg. 2(5): from the day after
  entry); planted error M6 counts from the entry day; tests `test_fipt.py`; re-encoding provenance `fipt-enc/`.
- `bridge/`: the tested bridge script and its output `bridges.jsonl` (the only source of pensionable-age dates and 80th
  birthdays).
- `run.py`: staged proofs per derived fact, Lean replay of every certificate and admission of one document per answer.
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.

Reproduce (repository root, after `cd lean && lake build`):
    uv run python -B usecases/pawhp/run.py --mutants --out RUN.json
    python3 -I usecases/pawhp/grade.py RUN.json <manage-agents>/reviews/spare/spare-second-statute/sealed/answers.jsonl
