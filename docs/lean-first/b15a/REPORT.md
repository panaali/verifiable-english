# Batch 15a fix report

Base `29773091`; implementation commits `97e175d9`, `1c439488`, `37105503`, `767d3506`, `2e831d80` on `lean-first/b15a`. The immutable [change snapshot](evidence/change-metrics.json) was captured at `2e831d80` from the original `main` branch point with `--no-merges`, before this report commit. Lean lines added: **781**. Total lines deleted: **6** (metadata and test edits). Python decision lines deleted: **0**; Rust decision lines deleted: **0**. The [owner ledger](LEDGER.md) records why 15a has no listed duplicate deletion.

## Work

Lean now exposes one metered evaluator for the four formula families. Its document scan shares the work budget, stops on the first violation, and returns `ResourceLimit` on exhaustion. `VE.Route.MeteredProofs` proves that every completed result has the existing finite-model meaning for FOL, closure, core and order. The new `ve_metered` executable also emits traces and checks non-vacuity of proposed witnesses. Traces are display data after the metered result. The route uses the existing Lean environment, model and formula decoders. Its caller is in Lean for this batch; Python and Rust caller rewiring belongs to 15b.

## Gate evidence

| Acceptance item | Status and saved evidence |
|---|---|
| AGENT — value, work, trace and non-vacuity | `tests/test_metered_lean.py`: 17 tests across FOL, closure, core and order; budget zero and boundaries, shared document counts, short circuits, traces, empty quantifier domains, malformed budgets, and semantic guards. Three seeded source mutations each made this suite fail; [mutant record](evidence/mutants.txt) lists the exact mutations and failures. |
| AGENT — corpus and pilots | [Base/head comparison](evidence/ab-compare.json) and [raw recording hashes](evidence/ab-recordings.json): 58,776/58,776 public results identical, including 39,612 conformance rows, 18,870 probe rows and all 294 historical pilot rows. Zero unlisted differences, so no `DELTA.md` signature is needed. Both raw recordings are [saved](evidence/base-ab.jsonl.gz) ([head](evidence/head-ab.jsonl.gz)) and have the same SHA-256. |
| AGENT — differential fuzz | [CI report](evidence/difffuzz-head-ci.json) has no new signature. The [14-seed A/B comparison](evidence/difffuzz-ab.json) records CI and 14 date seeds at base and head; the baseline does not grow. |
| AGENT — latency | The base and head `ve_service` executables both have SHA-256 `ea09d2acda207109238e222c3851fc11cb05bf44543da6728ce07cb9dbb23588`. The implementation snapshot has no `ve/` or `rust/` decision-source change. No existing public operation calls the new executable yet; existing service CPU and wire behavior are unchanged. The new one-shot route has no base counterpart for an A/B latency ratio. |
| AGENT — full clean-head gate | [Gate result](evidence/full-gate.json): 11858 passed, 7 skipped, 0 failed; 37 Rust tests passed. |
| HUMAN — theorem statements | DRI approval is deferred for 7 added statements in `lean/statements.txt`; the saved [statement diff](evidence/statement-diff.txt) found zero removed or changed existing statements. Owner: DRI. |
| HUMAN — trust budget | DRI signed allowance is deferred. `tools/trust_map.py --check` reports S +45 (inherited readings), V +631 (including this batch's display/route/non-vacuity code); declaration classification has zero unclassified. Owner: DRI. |
| EXTERNAL — operational soak | Deferred to DRI after 13b, under DRI answer 1. This batch does not start the soak. |

`python3 lean/audit.py --write`, `python3 tools/lean_statements.py`, `python3 VE/Route/frozen.py`, `python3 tools/check_lean_imports.py`, `python3 tools/relay_lint.py`, and the gate collection refresh passed. For checklist items 1–5, the new route reuses Lean's environment, model and formula decoders, keeps the existing evaluation and trace limits, tests malformed budget fields, and the saved three-way fuzzer comparison covers the unchanged public contract. Text normalization, English, identity, certificates and state machines (items 3, 9–12, 15, 18–19) have no new decision site in 15a. Items 6–8 are exercised by metered family dispatch and zero-budget tests; 13 by the seeded mutants; 14 by the gate's hermetic toolchain and shared `HANG_TIMEOUT`; 16–17 by the inventories and statement diff; and 20–22 by saved-evidence tests, acceptance labels and the clean-head gate. The project-wide generated limits table remains assigned to batch 19.

Not run: a batch-15a candidate-batch interface, because batch 2's recorded Rust-enumerator attempt missed its deadline; a 15b caller switch and duplicate removal; an A/B latency ratio for the new one-shot route, which did not exist at base.
