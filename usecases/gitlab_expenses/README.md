# gitlab_expenses: statute corpus batch 4, NON-STATUTE (a) company expense policy

GitLab handbook "Global Travel and Expense Policy", s.4.1 Travel related expenses (CC BY-SA 4.0), pinned in manage-agents
reviews/spare/statute-corpus/batch4/gitlab-expenses/ (source.txt, units.jsonl, ISOLATION.md). CROSS-FAMILY questions
(Codex writer, gpt-6-astra), Opus translator and encoder. translation.py (readings R1-R16, units, planted errors),
encode.py (the encoder's Sub), run.py (copied from usecases/oas_canada; Lean checks every step and answer document),
smoke_cases.py / smoke_test.py (made-up cases worked by hand), cases.py (the encoder's cases from questions-enc.jsonl),
grade.py (committed before the headline run). Nothing here is a kernel line, profile, refuses pair or lint change.

Fidelity: translation not independently checked against its source. A fidelity sweep (same model family, Opus) found
twelve latent departures (flags FL01-FL18); all twelve are fixed in translation.py and run.py and pinned by
tests/test_gitlab_expenses_fidfix.py, each test failing on the frozen translation 24ed6a6481. Replay of the Codex-written
question set against the sealed key, graded by grade.py: 94/121, wrong 0, refused 19 (frozen: 94/121, wrong 0, refused 18)
[translation not independently checked against its source].
