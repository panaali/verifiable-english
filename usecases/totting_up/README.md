# Disqualification for repeated offences, RTOA 1988 s.35 (statute corpus batch 3, law 6): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-totting-up (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author, translator and
encoder: dri-statute-corpus-totting-up-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or lint
change; nothing merges.

- `translation.py`: the section's 8 in-scope units (stock/totting-up/units.jsonl) as RULE / PART entries, grounded per case;
  readings R1-R7 in its docstring; committed before the encoder's question file was read; 11 planted errors (MUTANTS).
- `encode.py` (+ `cases.py`, written after the questions were read): the encoder's facts from `questions-enc.jsonl` only;
  conventions C1-C5 and per-case judgement.
- `bridge/`: the one tested bridge script (a pair of dates to whole calendar months + days) and its output `bridges.jsonl`;
  `python3 -I bridge/test_bridge.py`.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target
  (the fmla_eligibility runner with this law's answer forms and units).
- `smoke_test.py`: twelve made-up cases written with the translation (not from the question file).

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/totting_up/bridge/test_bridge.py
    .venv/bin/python -B usecases/totting_up/smoke_test.py
    .venv/bin/python -B usecases/totting_up/run.py --mutants --out RUN.json
    python3 -I usecases/totting_up/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/totting-up
