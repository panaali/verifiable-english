# ftr_per_diem: statute corpus batch 4, US regulation

Federal Travel Regulation, 41 CFR 301-11.1 to 301-11.23 (per diem and subsistence; US federal work), pinned in manage-agents
reviews/spare/statute-corpus/batch4/ftr-per-diem/ (source.txt, units.jsonl, ISOLATION.md). CROSS-FAMILY questions (Codex
writer, gpt-6-astra), Opus translator and encoder. translation.py (readings R1-R19, units, planted errors), encode.py (the
encoder's Sub), kit.py (transcription helpers), run.py (copied from usecases/gitlab_expenses; Lean checks every step and
answer document), smoke_cases.py / smoke_test.py (made-up cases worked by hand), cases.py (the encoder's cases from
questions-enc.jsonl), grade.py (committed before the headline run). Nothing here is a kernel line, profile, refuses pair or
lint change.

Fidelity: translation not independently checked against its source. A fidelity sweep (same model family, Opus) found six
latent departures (rows U8, U20, U24, U27, U33, T013; flags FL01, FL03, FL05, FL06, FL07, FL10); all six are fixed in
translation.py and pinned by tests/test_ftr_per_diem_fidfix.py (29 tests: on the frozen translation, commit 24d490f718,
10 row tests fail by behaviour, 9 mutant tests fail because the planted errors M27-M35 are not there yet, and the other 10
pass: 8 guards and the M10 and M11 kill tests). Replay of the Codex-written question set against the sealed key, graded by grade.py: 97/101, wrong 0, refused 4
(frozen: 98/101, wrong 0, refused 1, writer-ambiguous 2; the one answer that moved away from the key, T013-3, went from correct to refused,
not to wrong) [translation not independently checked against its source].
