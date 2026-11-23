# Child support maintenance calculation, CSA 1991 Sch. 1 Part I (statute corpus stock, batch 3 law 5). SAME-FAMILY. Evidence branch, not for merge.

Row statute-corpus-child-support (dri-statute-corpus-child-support-1123, Opus 5.5). Pinned source and the sealed question set live in
manage-agents reviews/spare/statute-corpus/stock/child-support/ (source.txt sha256 860a9df0...03c3; ISOLATION.md).
- translation.py: one translation pass from source.txt only, committed (a7f7140090, 20:21Z) before questions-enc.jsonl was opened;
  readings R1-R7 in its docstring; UNITS maps the 36 units to RULE / PART / NOT (the ledger).
- encode.py: the encoder's conventions C1-C6 (committed with the translation); cases.py: the 35 in-scope cases from questions-enc.jsonl
  only (encoder judgements listed per case) and the 10 probes (UNSUPPORTED).
- run.py: the staged route of usecases/council_tax/run.py; every answer only through Lean-replayed step certificates and Lean-admitted
  documents. Search aid added after the development run (no answer source): an exactly-k count atom whose first search fails gets a
  certified "hint" step (the one disjunct its known literals make true) and is then certified from it.
- smoke.py: 11 made-up cases (not the writer's), written before the questions were read.
- grade.py: compares a run file with the sealed answers (sha256 checked); reads the writer's tags at grading time.

Reproduce (repository root, after `cd lean && lake build` and `uv sync --locked --group dev`):

    .venv/bin/python -B usecases/child_support/smoke.py
    .venv/bin/python -B usecases/child_support/run.py --mutants --out RUN.json
    python3 -I usecases/child_support/grade.py RUN.json <manage-agents>/reviews/spare/statute-corpus/stock/child-support
