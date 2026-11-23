# HMO England (statute corpus law 3): one translation pass. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-hmo (manage-agents reviews/spare/statute-corpus/SELECTION.md (b)); author, translator and encoder:
dri-statute-corpus-hmo-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or lint change; nothing merges.

- `source/hmo-england.txt`: the pinned source (sha256 29fd379a...f6e8481a7).
- `rows.py`: the formulas (relational FOL over person / place / amenity), readings J1-J7, each row linked to units.jsonl.
- `translation.py`: grounding over a case's names (unique names), the AtLeast abbreviation, 5 planted errors;
  `test_translation.py`: AtLeast = its FOL form on small domains; every atom fixed by one rule; mutants differ.
- `cases.py` + `encode.py`: the encoder's facts, from `questions-enc.jsonl` only; conventions C1-C8 and per-case judgement.
- `run.py`: staged proofs per derived atom (a true disjunct proved first as a witness step: search only), Lean replay of
  every certificate, one admitted documents@1 document per answer atom.
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    uv run python -B usecases/hmo/run.py --mutants --out RUN.json
    python3 -I usecases/hmo/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/hmo/sealed/answers.jsonl \
        <manage-agents>/reviews/spare/statute-corpus/hmo/questions.jsonl
