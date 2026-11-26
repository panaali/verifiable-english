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

## After the fidelity check: a planned stay's length (branch fidfix-tour-gitlab-relocation-1126, target after-release)
Row statute-latent-tour-gitlab-relocation-U15 (manage-agents fidelity-check/sweep/tour-gitlab-relocation.md FL02): the frozen
R7-R9 counted a place's stated stays only, so a place whose only child is a planned stay had 0 days and got a definite
"not long-term" / "short-term" / "no compensation change". Translation R18: a place with a planned stay gets no R7 NO, no R8
short-term YES and no R9 NO (refused; unit 15: "plan on staying ... more than 6 months" is long-term, and a planned stay's
length is never stated); the YES side is unchanged. Planted errors M18-M20 (the frozen R7 / R8 / R9), smoke cases S7-S7c,
tests/test_gitlab_relocation_planned_stay.py. Result: manage-agents reviews/spare/statute-corpus/fidelity-check/sweep/
tour-gitlab-relocation/FIX.md.

## After the fidelity check: compensation and mail (branch fidfix-tour-gitlab-relocation-u11-1126, target after-release)
Row statute-latent-tour-gitlab-relocation-U11-mail (fidelity step FL01 on the U15 fix): the frozen R9 gave "no change to
compensation" on the days and chg alone, while R7's long-term NO also requires that the mail will not go to an address in the
place (unit 11: "temporary locations for 183 days or less (short term relocation)"; unit 19: mail delivered there ->
"request a long-term relocation"). Translation R19: comp's NO also requires not mail (mail there, or not stated: refused);
the YES side is unchanged. The comp sub-cases R012-2 / R014-2 / R015-2 now enter mail from a fresh Opus encoder seat
(u11-enc/). Planted error M21 (the frozen R9), smoke cases S8-S8c, tests/test_gitlab_relocation_comp_mail.py. Result:
manage-agents reviews/spare/statute-corpus/fidelity-check/sweep/tour-gitlab-relocation/u11/FIX.md.
