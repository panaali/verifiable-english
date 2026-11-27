# Tenant Fees Act 2019 (statute corpus law 5): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-tenant-fees (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus). Author, translator
and encoder: dri-statute-corpus-tenant-fees-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or
lint change; nothing merges.

- `translation.py`: the Act's in-scope units (tenant-fees/units.jsonl) as RULE / PART / NOT entries, grounded per case;
  committed (783f91882c) before the encoder's question file was opened; 5 planted errors (MUTANTS).
- `cases.py` + `encode.py`: the encoder's facts from `questions-enc.jsonl` only; conventions C1-C4 and per-case judgement.
- `bridge/`: the one tested bridge script (Sch. 1 para. 4(5) late-rent cap) and its output `bridges.jsonl`.
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target.
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/tenant_fees/bridge/test_bridges.py
    .venv/bin/python -B usecases/tenant_fees/run.py --mutants --out RUN.json
    python3 -I usecases/tenant_fees/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/tenant-fees
