# HICBC (ITEPA 2003 ss. 681B-681H): statute corpus law 2. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-hicbc (manage-agents reviews/spare/statute-corpus/SELECTION.md, kind (a) tax or charge threshold).
Translator, encoder and runner author: dri-statute-corpus-hicbc-1123 (Opus 5.5). Nothing here is a Lean kernel line, a
profile, a refuses pair or a lint change; nothing merges; no gate-train.

- `rules.py`: the translation (vocabulary, one row per in-scope provision: RULE / NAME / FACT / BRIDGED), grounding over a
  household's persons, child-benefit items, pairs and day-types, 5 planted errors (MUTANTS). First committed (b2bf8ee2de)
  before the encoder's question file was opened.
- `cases.py`: the encoder's transcription of `questions-enc.jsonl` only (stated dates, amounts, bases, relationship facts),
  with encoder judgement listed per household. `encode.py`: mechanical facts (closed).
- `bridge/bridges.py` -> `bridge/bridges.jsonl`: the only source of weeks, segments, "throughout the week" day-types, the
  681D(4) period facts, the percentage and the rounded totals/charges. Tests: `python3 -I bridge/test_bridges.py`
  (31 tests, 7 planted errors caught).
- `run.py`: staged proofs per derived atom, Lean replay of every certificate, one admitted document per answer (Q3: one per
  person). `grade.py`: compares a run file with the sealed answers (sha256 checked).

Reproduce (repository root, after `cd lean && lake build`):
    python3 -I usecases/hicbc/bridge/bridges.py usecases/hicbc/questions-enc.jsonl | cmp - usecases/hicbc/bridge/bridges.jsonl
    uv run python -B usecases/hicbc/run.py --mutants --out RUN.json
    python3 -I usecases/hicbc/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/hicbc/sealed/answers.jsonl
