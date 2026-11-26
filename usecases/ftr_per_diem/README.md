# ftr_per_diem: statute corpus batch 4, US regulation (evidence branch, not for merge)

Federal Travel Regulation, 41 CFR 301-11.1 to 301-11.23 (per diem and subsistence; US federal work), pinned in manage-agents
reviews/spare/statute-corpus/batch4/ftr-per-diem/ (source.txt, units.jsonl, ISOLATION.md). CROSS-FAMILY questions (Codex
writer, gpt-6-astra), Opus translator and encoder. translation.py (readings R1-R19, units, planted errors), encode.py (the
encoder's Sub), kit.py (transcription helpers), run.py (copied from usecases/gitlab_expenses; Lean checks every step and
answer document), smoke_cases.py / smoke_test.py (made-up cases worked by hand), cases.py (the encoder's cases from
questions-enc.jsonl), grade.py (committed before the headline run). Nothing here is a kernel line, profile, refuses pair or
lint change.
