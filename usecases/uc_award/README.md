# usecases/uc_award: statute corpus batch 2, law 4 (Universal Credit award). SAME-FAMILY

WRA 2012 s.8 + UC Regulations 2013 regs 3(2)-(6), 4, 22, 24, 36 (2026-27 amounts), translated in one pass with today's
language (translation.py), written from the pinned source only before the encoder's question file was opened.
No Lean kernel line, profile, refuses pair or lint change; nothing outside this folder changes except its test,
tests/test_uc_award_reg36.py.

- translation.py: UNITS (RULE / PART / NOT per unit of batch2/uc-award/units.jsonl), grounding over one award's persons,
  the environment, planted errors M1-M8. reg. 3(6) is read from both sides of a pair (row statute-xfam-wrong-uc-award-1:
  either member absent over 6 months from the other's household ends the couple, whichever anchors the award; a member
  of two couples needs absent_from, else refused); a claimant holds at most one partner (two standing couple links:
  refused). Tests: tests/test_uc_award_reg36.py. M7 one-sided reg. 3(6); M8 the 9517f4dcd2 reading.
- encode.py: the encoder's facts (closed world, conventions C1-C5).
- cases.py: the encoder's transcription of questions-enc.jsonl (one record per award), probes, unsupported.
- run.py: the staged runner (tenant_fees' protocol): steps proved in Python, every certificate and answer document
  replayed and admitted by Lean. grade.py: strict comparison with the sealed answers (sha256-checked).

Reproduce (after `cd lean && lake build`):
    .venv/bin/python -B usecases/uc_award/run.py --mutants --out RUN.json
    python3 -I usecases/uc_award/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch2/uc-award
