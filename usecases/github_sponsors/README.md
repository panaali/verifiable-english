# github_sponsors: GitHub Sponsors Additional Terms, 'Terms For Sponsored Developer' 1.1-3.7 less 3.2.2 (statute corpus batch 5, NON-STATUTE (e)). Evidence branch, CROSS-FAMILY questions (Codex writer), Opus translator; not for merge.

Row statute-corpus-github-sponsors-developer-1125 (manage-agents reviews/spare/statute-corpus/batch5/github-sponsors-developer/).
Translator: dri-statute-corpus-github-sponsors-developer-tr-1125 (Opus 5.5). This translation was written and frozen BEFORE
any question existed (orchestrator order 2026-11-25T10:25Z): the Codex writer reads only source.txt, so the questions stay
independent of it. Nothing here is a Lean kernel line, profile, refuses pair or lint change; nothing merges.

- `translation.py`: the 45 units as RULE / PART / NOT entries (classifications, USD sums and the $5,000 cap in Lean, Lean
  dates with shift_days 30 / 60 / 90); readings R1-R13 in its docstring; 18 planted errors (MUTANTS).
- `bridge/bridge.py` (+ `bridge/test_bridge.py`, 29 tests): the ONE bridge: month ends, a month's 22nd and third Thursday,
  the same date 12 months later, whole years of age. Never an amount.
- `encode.py`: a case spec -> items and facts; conventions E1-E6 (encoder judgement where they decide anything).
- `run.py`: the staged route (opm_fegli_premiums runner), Lean replay of every certificate, one admitted document chain
  per answer.
- `smoke_cases.py`, `smoke_test.py`: made-up cases, hand-worked from the readings (96/96 with Lean since the s028 fix, 89/89 frozen; 19 of 19 planted
  errors killed; 333/333 certificates, 133/133 documents).
- `cases.py` (encoder, from `questions-enc.jsonl` only, sha256 checked; written by dri-statute-corpus-github-sponsors-developer-cw-1125 after the questions were sealed) and `grade.py` (against the sealed answers; committed before the headline run).
- FIX (row statute-corpus-github-sponsors-wrong-s028, branch sponsors-s028-carry-1125, after the frozen 60d692157a): R6 / unit 38 compares the Stripe Connect cross-border minimum with `sbal`, "the balance accrued since the last payout" (the month's Sponsored Developer Payment + the unpaid balance carried from the month before; reset by a payout or the chain's start; unknown carry -> OPEN), not the month's own payment. Planted error M19 (the frozen reading); smoke cases N-2 and P; tests/test_github_sponsors_s028_carry.py. The ACH / wire $100 path (unit 39, `bal`) is unchanged.
- `run.py` answer layer (added with cases.py, no rule changed): forms `nyn` (the negation of one Lean-checked atom: "May <act>?") and `payout` ("how much is paid out on D": paid, pdy and bal of one month, each a Lean-admitted document; used only where the case has no matching money).

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):

    python3 -I usecases/github_sponsors/bridge/test_bridge.py
    .venv/bin/python -B usecases/github_sponsors/smoke_test.py
    .venv/bin/python -B usecases/github_sponsors/run.py --cases-module smoke_cases --mutants --workers 4 --out SMOKE.json
