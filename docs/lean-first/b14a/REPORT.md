# Batch 14a build report

Plan row 14a (LEAN-FIRST-PLAN draft 3): the `definitions@0` surface sugar (`no S is P`,
`every S x that is P, (A)`, `(A) iff (B)`, `define p(x, …) as (A)`) is read and decided by Lean's `parse` mode,
and the Python fallback batch 13b retained for it is deleted in the same batch. One owner: Lean decides
acceptance, the diagnostic and the document; Python only constructs the document after Lean accepts, and must
agree with Lean or the parse is `CheckerUnavailable`.

## Size

* **Deleted:** 39 lines of `ve/parser.py` (8 added): the `definitions@0` branch of `_parse_lean`,
  `_parse_python_marked`, the `_Parser.sugar` mark and the `definitions_sugar` exception tag. Mapped site by site in
  [LEDGER.md](LEDGER.md).
* **Lean added:** 416 lines (122 deleted) in 9 product files (`Surface`, `Closure/Surface`, `Core/Surface`,
  `Service/ParseDiagnostic`, `Service/Standalone`, the round-trip and proof files that follow the signatures).
  Trusted lines V 37,154 → 37,451 (R6, `docs/trust-baseline.json`); 25 new declarations classified in
  `tools/trust-classes.json`.
* **Tests:** `tests/test_lean_first_b14a.py` (250 lines, new), `tests/test_stage2_parse.py` (+17/−8). Rust unchanged.

## Gate 5.1 evidence

All in [DELTA.md](DELTA.md) and `evidence/`: corpus A/B 65,772 records, 0 unlisted (base and head recordings
byte-identical); sugar corpus 760 records, 350 wording (W1, R1), 0 unlisted; difffuzz `--ci` + `--deep 1` over 14
seeds, 0 head-only signatures, baseline 250 entries on both sides (does not grow); latency within section 4's
budgets (C1, R4); relay mutation gate: the `parse` route has no failure, the 133 failures are identical at base
and head (`main`'s). Every DELTA row is signed by a standing ruling (R1, R4, R6, R7); none needs a DRI signature.

The full release gate runs once, as the last step, on the commit that adds this report; its result is kept as
`gate-result.json` in the worktree (no later commit, so the gate's commit is HEAD).

## Seeded bugs

`evidence/mutants.json`: M1 (Lean, `lean/VE/Service/Standalone.lean`), M2 (Lean,
`lean/VE/Service/ParseDiagnostic.lean`), M3 (Python, `ve/parser.py`), M4 (Lean, `lean/VE/Core/Surface.lean`); each
made its named test fail and was restored.

## Not run, recorded

* Base-side A/B of the UDHR whole-translation input exceeds 8 GB (U2, R7); not retried.
* The rights, discourse and quantity corpora were not recorded (no `definitions@0` surface text; DELTA.md item 2).
* Environments outside Lean's `parse` scope (statement layers, W6 units) keep the Python sugar reader: 13b's scope
  gap 5, FOLLOW-UP outside 14a.
