# National Minimum Wage Regulations 2015 regs 4-16 (statute corpus batch 2, law 2): translation, encoding, run and grading. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-nmw (manage-agents reviews/SPARE-CAPACITY-TRACK-20261123.md, statute corpus batch 2). Author, translator
and encoder: dri-statute-corpus-nmw-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or lint
change; nothing merges.

- `translation.py`: the in-scope units (batch2/nmw/units.jsonl) as RULE / PART / NOT entries, grounded per case;
  committed before the encoder's question file was opened for question text; planted errors (MUTANTS).
- `cases.py` + `encode.py`: the encoder's facts from `questions-enc.jsonl` only; conventions and per-case judgement.
- `bridge/`: the one tested bridge script (ages and the 12-month test on the first day of the period; dates only).
- `run.py`: staged proofs per derived fact, Lean replay of every certificate, one admitted document per answer target
  (from usecases/tenant_fees/run.py).
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.
