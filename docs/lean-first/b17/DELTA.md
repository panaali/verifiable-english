# Batch 17 public outcome comparison

The saved A/B comparison covers 96,627 cases at base `7550e08a` and code head
`533dd290`. The base and head records agree on every outcome: 96,623 returned
the same available result and four returned the same `CheckerUnavailable`
result. The four unavailable cases are constitution pilot readings documents
with the same Lean `invalidGrammar` lexicon V3 diagnostic on both sides. Their
cases and full responses are in `evidence/ab.json`. There is no wording, order,
verdict or availability **change** to sign.

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
