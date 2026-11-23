# Canada Employment Insurance Act ss.7, 12, 14 + Sch I (statute corpus batch 2, law 3): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-ei-canada (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus batch 2). Author,
translator and encoder: dri-statute-corpus-ei-canada-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile,
refuses pair or lint change; nothing merges.

- `translation.py`: the Act's in-scope units (batch2/ei-canada/units.jsonl, 68 units, 59 table rows) as RULE / PART / NOT
  entries, grounded per case; committed before the encoder's question file was opened; 7 planted errors (MUTANTS).
- `encode.py` + `cases.py`: the encoder's facts from `questions-enc.jsonl` only.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target.
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.
No bridge script: amounts are never bridged (batch 2 criterion 10); weeks are given as a list (no date arithmetic).

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    .venv/bin/python -B usecases/ei_canada/run.py --mutants --out RUN.json
    python3 -I usecases/ei_canada/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch2/ei-canada
