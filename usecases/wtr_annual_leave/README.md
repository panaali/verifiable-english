# Working Time Regulations 1998 regs 13, 13A, 14, 15: statute corpus batch 4 (wtr-annual-leave)

Evidence branch (statute-wtr-annual-leave-1124), not for merge. CROSS-FAMILY questions (Codex writer gpt-6-astra, sealed in
manage-agents reviews/spare/statute-corpus/batch4/wtr-annual-leave/ISOLATION.md), Opus translator and encoder.

- translation.py: the units (readings R1-R11), the case split over days worked in a week and days of a year, planted errors.
- bridge/wtr_bridge.py: dates and calendar-day counts only (D6); tests: `python3 -I usecases/wtr_annual_leave/bridge/test_bridge.py`.
- encode.py: encoder conventions C1-C5; cases.py: the encoder's cases from questions-enc.jsonl only.
- run.py: the staged route (Python search, Lean certificates and documents); grade.py: against the sealed answers.
- smoke: `.venv/bin/python -B usecases/wtr_annual_leave/smoke_test.py` (made-up cases, hand-worked; every planted error killed).
