# usecases/uc_award: statute corpus batch 2, law 4 (Universal Credit award). EVIDENCE BRANCH, SAME-FAMILY, NOT FOR MERGE

WRA 2012 s.8 + UC Regulations 2013 regs 3(2)-(6), 4, 22, 24, 36 (2026-27 amounts), translated in one pass with today's
language (translation.py), written from the pinned source only before the encoder's question file was opened.
No Lean kernel line, profile, refuses pair or lint change; nothing outside this folder changes.

- translation.py: UNITS (RULE / PART / NOT per unit of batch2/uc-award/units.jsonl), grounding over one award's persons,
  the environment, planted errors M1-M6.
- encode.py: the encoder's facts (closed world, conventions C1-C5).
- cases.py: the encoder's transcription of questions-enc.jsonl (one record per award), probes, unsupported.
- run.py: the staged runner (tenant_fees' protocol): steps proved in Python, every certificate and answer document
  replayed and admitted by Lean. grade.py: strict comparison with the sealed answers (sha256-checked).

Reproduce (after `cd lean && lake build`):
    .venv/bin/python -B usecases/uc_award/run.py --mutants --out RUN.json
    python3 -I usecases/uc_award/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch2/uc-award
