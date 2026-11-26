# gitlab_relocation: statute corpus batch 5, NON-STATUTE (a) company staff policy (evidence branch, not for merge)

GitLab handbook "Relocation / Address Change" (CC BY-SA 4.0, page commit 03f49b80), pinned in manage-agents
reviews/spare/statute-corpus/batch5/gitlab-relocation/ (source.txt, units.jsonl, ISOLATION.md). CROSS-FAMILY questions
(Codex writer, to run later on source.txt alone), Opus translator. The translation was written and frozen BEFORE any question
existed (orchestrator order 2026-11-25T10:25Z). translation.py (readings R1-R16, units, planted errors), encode.py (the
encoder's Sub, conventions E1-E4), bridge/ (the ONE bridge script: the start date's first anniversary, with its tests),
run.py (copied from usecases/gitlab_expenses; Lean checks every step and answer document), smoke_cases.py / smoke_test.py
(made-up cases worked by hand). cases.py and grade.py come later, from questions-enc.jsonl once the questions are sealed.
Nothing here is a kernel line, profile, refuses pair or lint change.

## After the frozen run: the R035 fix (branch relocation-r035-preapproval-1125, target after-release)
The frozen build (1847cd06dc, translation 8b113741bd; measured 79/98, WRONG 1: R035-2) is unchanged on its own branch. This
branch adds: translation R17 (unit 4's written VP/PBP pre-approval is acceptance condition (i); not stated -> acceptance never
YES), encode.py E5 (a stated fact with no predicate that a unit the answer turns on depends on -> REFUSED), the planted error
M17 (the frozen R10; flips R035-2 back to YES), smoke cases S4c-S4g, r035-enc/ (the fresh encoder's two new fields) and
tests/test_gitlab_relocation_r035.py. E5 narrowed after the review (written clauses, item scope, the answer must not still follow). Result: manage-agents reviews/spare/statute-corpus/batch5/gitlab-relocation/fix-r035/.
