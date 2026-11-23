# 14 CFR 61.23 (medical certificates: requirement and duration): statute corpus law 4. SAME-FAMILY evidence branch, NOT a merge candidate.

Row statute-corpus-faa-medical (manage-agents reviews/spare/statute-corpus/SELECTION.md (c)). Author, translator and encoder:
dri-statute-corpus-faa-medical-1123 (Opus 5.5). Nothing here is a Lean kernel line, profile, refuses pair or lint change;
nothing merges; no gate-train.

- `rows.py`: the formulas, written from the pinned source text only, committed BEFORE the encoder's question file was opened
  (reading choices T1-T7 in its docstring).
- `translation.py`: mechanical grounding over a case's certificates and applications, splitting, "defines"; 6 planted errors.
- `bridge/`: the tested bridge script (ages, 60th birthday, month ends, 24/48 calendar-month windows, which date is later).
- `encode.py`: records -> VE facts (mechanical); `cases.py`: the encoder's records, from `questions-enc.jsonl` only.
- `run.py`: law 1's staged route (each derived atom one certified step; expiry, dl_last and last_day steps among the bridged
  dates), Lean replay of every certificate and admission of one document per answer.
- `smoke.py`: four made-up cases (not part of the number).
- `grade.py`: compares a run file with the sealed answers (sha256 checked); committed before the headline run.

Reproduce (repository root, after `cd lean && lake build`):
    uv run --frozen python -B usecases/faa-medical/run.py --mutants --out RUN.json
    python3 -I usecases/faa-medical/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/faa-medical/sealed/answers.jsonl
