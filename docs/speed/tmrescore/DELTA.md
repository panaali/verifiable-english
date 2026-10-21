# speed-tmrescore: DELTA

No user-visible delta, so this file has no rows. The item changes builder and reviewer tooling only
(`tools/trust_mutants.py`, its test, the step-1 measurement script and the seeded-bug evidence). It changes no file
under `ve/`, `lean/`, `rust/` or `conformance/`, so no VE output, diagnostic, verdict, limit or fault order can
change. Trust budget: +0 (no Lean change).

What the tooling does, none of it a VE output:

- `tools/trust_mutants.py` gains `--rescore PREV.json`. Every `--json` it writes gains `inputs` (digests of the
  bytes its verdicts are computed from) and, on each mutant, `raw_status` (its status before `--allow`); a reused
  mutant gains `reused_from`, and a rescored run gains `rescore`. A mutant that runs keeps today's verdict rules,
  and the exit codes are unchanged. Without `--rescore` the tool runs exactly as before.
- No gate, merge train (R2) or nightly (R3) runs or reads the tool or its evidence; both stay complete and
  unchanged.
