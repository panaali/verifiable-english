# Batch 15b changes for signature

The corpus A/B ([`ab-compare.json`](evidence/ab-compare.json), with [`DELTA.json`](DELTA.json)) has no
unlisted difference. Every difference is listed here; the latency item is section 4's.

| Id | Class | Change | Records | Signature |
|---|---|---|---:|---|
| V1 | `verdict` (count only) | `evaluate` under `VE_AUTHORITY=lean` on closure@0 documents now reports Lean's metered count, which is the Python authority's count exactly; Rust's evaluator charged 3 to 42 fewer units on these documents (for example `closure_cycle`: Rust 753, Lean and Python 777). Values, statuses and traces are unchanged. Rule 3 asks for exactly this: counts reported to Python come from Lean's metered evaluator. | 9 (`conformance/lean evaluate closure/*`) | DRI: pending |
| W1 | `wording` (recorder artefact) | The 7 senses probe documents of `pilot/cc-20261008T0600Z` fail at base and head alike because they name a sense pack outside the pilot branch; the message names the recorder's scratch directory, which is named after the output file (`base-ab.pilots` against `head-ab.pilots`). No product text changed. | 7 | DRI: pending (one block) |
| U1 | `unavailable` on both sides | The constitution pilot's `readings/s1.ve.md` is `CheckerUnavailable` at base and head (readings budget, F5; untouched here). | 4 | none needed (listed with its reason) |
| A1 | `availability` (not in the corpora) | Python has no search of its own: under the default authority, `find_countermodel` and `find_distinguishing_model` need the Rust binary (and Lean's `ve_metered` when a witness must be non-vacuous). A checkout without the native builds gets `CheckerUnavailable` where the Python search answered. Every corpus record is unchanged. | 0 | DRI: pending |
| L1 | latency (section 4: more than 20% more Lean CPU) | `evaluate` under `VE_AUTHORITY=lean` runs `ve_metered`, a one-shot process: 10 conformance evaluations take 445.7 ms against 45.9 ms at base (p50 wall, [`latency.json`](evidence/latency.json)). The fix is F1's: `evaluate-budgeted` and `non-vacuity` as `ve_service` modes (15a follow-up C2). Default-authority search on the 28 search fixtures: 19.0 ms against 9.9 ms (Rust's search with its witness checked, against Python's in-process search); the plan promises no search speed. | — | DRI: pending |
