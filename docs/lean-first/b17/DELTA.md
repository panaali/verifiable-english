# Batch 17 public outcome comparison

The original saved A/B comparison covers 96,627 cases at base `7550e08a` and
code head `533dd290`. Those records agree on 96,623 available outcomes; four
constitution pilot readings documents returned the same Lean `invalidGrammar`
lexicon V3 `CheckerUnavailable` diagnostic on both sides. Their cases and full
responses are in `evidence/ab.json`.

The batch 17 path comparison adds 18 assist and 2 Cedar cases at the same base
and head `2766b7d5`. It records `_decide` and `_entails` with positive, negative,
quantified, zero-budget, and adequate-budget inputs, plus Cedar permit and
forbid policies over allow and deny requests. The paired raw records and strict
comparison are `evidence/base-paths.json`, `evidence/head-paths.json`, and
`evidence/path-ab.json`; `tools/b17_ab.py` regenerates and checks the matrix.
All Cedar outcomes and 16 assist outcomes match. The two changed assist outcomes
are signed in `DELTA.json` under `verdict`:

- `decide/top/proof_zero`: `yes → unknown`. With no proof steps, Lean cannot
  replay a proof, so `yes` is unavailable.
- `decide/forall/models_zero`: `no → unknown`. The saturated search has no
  countermodel budget, so Lean cannot confirm a negative witness.

These two conservative changes were approved by the DRI on 2026-10-09. The
same queries return `yes` and `no` with adequate budgets. The zero-budget and
adequate-budget regressions are `test_assist_zero_proof_budget_cannot_confirm_yes`
and `test_assist_zero_model_budget_cannot_confirm_saturated_no`.

The first head pilot recording had one five-second Rust subprocess timeout for
`pilot/cc-20261002T0600Z:usecases/bluedot-grant/document.ve.md`. A quiet-host
rerun of that exact case succeeded twice and matched the base result. The
second successful outcome is saved in `evidence/bluedot-rerun.json`; the final
head recording uses it in place of the transient timeout. The unmodified
recording and comparison are saved as `evidence/head-pilots-timeout.jsonl.gz`
and `evidence/ab-initial.json`.

The lead's 2026-10-08 rule-3 decision applies: search-internal accelerators
may stay as untrusted proposal mechanisms. Every result reported by the
batch-17 assist and Cedar paths is checked by Lean. Batch 17 introduces no
other retained decision owner and no plan theorem change.
