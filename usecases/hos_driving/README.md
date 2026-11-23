# hos_driving: 49 CFR 395.3 + 395.2 (statute corpus batch 3, law 2). Evidence branch, SAME-FAMILY, not for merge.
translation.py (rules from the pinned source only), bridge/clock.py (+ test_clock.py: the one bridge script, time
arithmetic only), cases.py (parses questions-enc.jsonl; the activity readings), encode.py (pieces, closed-world facts,
bridge trail), run.py (the staged route; Lean replays every certificate and admits every answer document), grade.py.
Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):
    python3 -I usecases/hos_driving/bridge/test_clock.py
    .venv/bin/python -B usecases/hos_driving/run.py --mutants --out RUN.json
    python3 -I usecases/hos_driving/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/hos-driving
