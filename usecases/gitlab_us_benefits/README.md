# gitlab_us_benefits: statute corpus batch 5, NON-STATUTE (f) benefit plan summary (evidence branch, not for merge)

GitLab handbook "GitLab Inc (US) Benefits" (CC BY-SA 4.0, page commit 747fa3f6), pinned in manage-agents
reviews/spare/statute-corpus/batch5/gitlab-us-benefits/ (source.txt 6e6e97e9...5050, units.jsonl a734ad0a...5282,
ISOLATION.md D1-D16). CROSS-FAMILY questions (Codex writer), Opus translator.

FROZEN BEFORE THE CODEX QUESTIONS (orchestrator order 2026-11-25T10:25Z): translation.py (readings R1-R18, 104 units +
the D3 lines 105-109, 26 planted errors), bridge.py (the one bridge script: dates only) with test_bridge.py, encode.py
(the encoder's Sub), run.py (copied from usecases/gitlab_expenses; Lean checks every step and answer document),
smoke_cases.py / smoke_test.py (made-up cases worked by hand, no writer case) were written and committed before any
question of this text existed. The questions' encoder file (questions-enc.jsonl), cases.py and grade.py come later, on
top of this commit, without changing a reading. Nothing here is a kernel line, profile, refuses pair or lint change.

    .venv/bin/python -B usecases/gitlab_us_benefits/test_bridge.py
    .venv/bin/python -B usecases/gitlab_us_benefits/smoke_test.py
    .venv/bin/python -B usecases/gitlab_us_benefits/run.py --cases-module smoke_cases --no-lean --mutants

AFTER THE SEAL (dri-statute-corpus-gitlab-us-benefits-cw-1125, 2026-11-25): the Codex questions were sealed 19:29Z
(gpt-6-astra; questions-enc.jsonl e56e87c2...); cases.py (the encoder's cases, from questions-enc.jsonl only) and
grade.py (copy of usecases/opm_fegli_premiums/grade.py with this text's seals) were added, and run.py got answer-layer
forms "all" / "any" / part "none" for a yes/no question that asks several things at once (no rule, reading or unit
changed; translation.py is byte-identical to the frozen f8309cf469). Headline:

    .venv/bin/python -B usecases/gitlab_us_benefits/run.py --mutants --workers 4 --out RUN.json
    python3 -I usecases/gitlab_us_benefits/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/batch5/gitlab-us-benefits
