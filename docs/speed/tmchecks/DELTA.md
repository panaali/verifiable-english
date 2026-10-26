# speed-tmchecks: DELTA

No user-visible delta, so this file has no rows. The item changes builder and reviewer tooling only
(`tools/trust_mutants.py`, its test, the step-1 measurement and replay scripts and the seeded-bug evidence). It
changes no file under `ve/`, `lean/`, `rust/` or `conformance/`, so no VE output, diagnostic, verdict, limit or
fault order can change. Trust budget: +0 (no Lean change).

What the tooling does, none of it a VE output:

- `tools/trust_mutants.py --rescore PREV.json` gains a second reuse mode, "checks": after a change that touches
  only check modules outside every selected declaration's file and import closure, outside --test files and
  generated inventories, it carries PREV's KILLED and INVALID verdicts whose reads read the same (`reused_from`,
  `carried: "checks"`) and runs every other mutant. Every `--json` gains `inputs.files` (per-file digests) and, on
  each KILLED or INVALID mutant, `reads` and `killed_at`; `rescore` gains `mode` and `changed`. `__pycache__` is no
  longer part of the `lean` digest (speed-tmrescore review F1). A mutant that runs keeps today's verdict rules, and
  the exit codes are unchanged. Without `--rescore` every verdict is computed as before.
- No gate, merge train (R2) or nightly (R3) runs or reads the tool or its evidence; both stay complete and
  unchanged.
