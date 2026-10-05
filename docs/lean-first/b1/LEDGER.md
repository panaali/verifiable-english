# Lean-first batch 1: deletion ledger

Plan: `docs/LEAN-FIRST-PLAN.md` (draft 3), section 5.1 item 3 and section 5.2 row 1 ("Every route in the
service"). Base `776a64d7` (the head of batch 0). Every deleted transport and runner is mapped to what now
does its work. The batch decides nothing new: each statement-layer route keeps its Lean per-case function
(`runCaseReported`), and the service mode that replaced its executable is pinned to that function by an `rfl`
theorem.

## Deleted

| # | Deleted (base) | What it did | Owner now |
|---|---|---|---|
| T1 | `ve/backends/lean.py` `run_soft_case` | one soft-norms or rights case through `ve_soft_norms_route` / `ve_rights_route`; error row → `VEError` with the row's soft code | `relay.decide("soft-norms" \| "rights", …)`: the service's public code chooses the class, the row's own soft-norms@0 code is kept as the error's `code` (`relay._raised`) |
| T2 | `lean.py` `run_alternatives_case` (also the risk route's transport) | one case through `ve_alternatives_route` / `ve_risk_route`, the row returned | `relay.rows("alternatives" \| "risk", …)` |
| T3 | `lean.py` `run_discourse_case` | the raw exit status, stdout and stderr of `ve_discourse_route` | `relay.rows("discourse", …)`; `discourse.lean_admission` keeps its well-formedness check of the row |
| T4 | `lean.py` `run_reports_case` | one case through `ve_reports_route` | `relay.decide("reports", …)` |
| T5 | `lean.py` `run_norm_defaults_cases` | cases through `ve_norm_defaults_route` | `relay.rows` / `relay.decide("norm-defaults", …)` |
| T6 | `lean.py` `run_readings_cases` | cases through `ve_readings_route` | `relay.rows("readings-route", …)` |
| T7 | the `ve_quantity` one-shot call of `admission._lean_quantity_admission` (through `lean.run`) and its `checker_error` text classification | W6 admission and its diagnostic class | `lean.run(…, runner="ve_service", mode="quantity")` → `relay.decide`: Lean's code, Lean's text |
| T8 | the 13 one-shot `lean_exe` targets (`ve_norms_route`, `ve_discourse_route`, `ve_speech_acts_route`, `ve_soft_norms_route`, `ve_rights_route`, `ve_quantity`, `ve_reports_route`, `ve_alternatives_route`, `ve_risk_route`, `ve_readings_route`, `ve_norm_defaults_route`, `ve_risk_eval`, `ve_diagnose`) and their 13 `*Main.lean` roots | 13 executables, 2.2 GiB of the 2.8 GiB `lean/.lake/build/bin` | the service's modes (`lean/VE/Service/Protocol.lean` `runMode`, theorems `runMode_*`); `bin` is 693 MiB |
| T9 | the `main` batch loops of `Norms`, `SoftNorms`, `Rights`, `SpeechActs`, `Attribution`, `Alternatives`, `Risk`, `NormDefaults`, `Discourse`, `Readings` `Run.lean`, `Time/Wire.lean`, `Time/Document.lean` and `WireContract/Diagnose.lean` (with `usage`) | 13 copies of the one-shot batch loop: read the case array, map the runner, print, exit 1 on a rejection | the service's one loop (`Protocol.runRequest`, `respond`, `Serve.lean`) |
| T10 | `RiskEvalMain.lean`'s `evalCondition` and `evalCase` | the risk differential harness | moved, unchanged, to `lean/VE/Risk/Eval.lean` (mode `risk-eval`) |
| T11 | the flat 5 s interactive and 60 s batch limits of `lean_service.py` and the callers' flat route limits (120, 60, 180, 300 s wall) | when a request is abandoned | per-operation CPU deadlines, `lean_service.DEADLINES` (F4): a base per case plus a share per MiB, CPU time where `/proc` reports it, a wall cap of 10 times; a request past its deadline is `CheckerUnavailable` naming its mode, not retried |

`relay_lint` passes. No consumer of a deleted symbol remains: `git grep` over `ve/`, `tests/`, `tools/`,
`conformance/` and `usecases/` finds no `run_soft_case`, `run_alternatives_case`, `run_discourse_case`,
`run_reports_case`, `run_norm_defaults_cases`, `run_readings_cases`, `LEAN_ROUTE`, `QUANTITY_ROUTE`,
`route_executable` or `VE_DISCOURSE_ROUTE`, and no path to a deleted executable outside the names
`tests/lean_routes.py` maps to modes and the docs that record history.

## Retained, named

| Site | Why it stays | Removed by |
|---|---|---|
| Python's regeneration compares (`soft_route.check_regenerated`, `rights_route.check_rights_regenerated`, `norm_defaults_route.check_regenerated`, `reports_route.checked_elaboration`, `readings_route.validate`'s byte comparison) | duplicates this batch does not list; only their transport changed | batches 3 (readings), 6 (soft norms), 7 (rights), 8 (reports), 10b (norm defaults) |
| `backends/diagnostics.py` `checker_error` | the Rust JSONL checker's rows still carry no code; no Lean row reaches it any more (its quantity use, kept by batch 0 for this batch, is gone) | batch 15b |
| `lean.py` `run` for `ve_conformance` (`argument.py`, `bundle.py`) | `ve_conformance` is not one of the 12 routes; its route mode already has a service mode | batch 13b with the core switch |
| `tests/lean_routes.py` `MODES` (executable name → mode) and `completed` | lets tests keep naming the route they test; the names are no executables | when the tests next change |

## Lines

`git diff --numstat 776a64d7 HEAD`. Python, `ve/*.py`: 320 deleted, 304 added. The transports are
`backends/lean.py` (137 out, 26 in); the nine callers lost 125 lines and gained 57; the additions are
`lean_service.py`'s deadlines, digest cache and two readers (149 in, 27 out) and `relay.py`'s `rows` and pools
(62 in, 22 out). Lean, `*.lean`: 349 deleted, 159 added: 12 of the 13 roots (55 lines), the 13 `main` loops (about
260) and the `RiskEvalMain` harness moved (54 out, 57 in as `VE/Risk/Eval.lean`); added are
`Service/Protocol.lean` (+71: twelve modes, their pins, `parseLeanCases`), `Service/Diagnose.lean` (+34) and
`Audit.lean` (+13); `lakefile.toml` lost 52 lines. Twelve response schemas (JSON) were added. Tests: 341
deleted, 668 added (`tests/lean_routes.py` 113, `tests/route_case_recorder.py` 48, 31 new test IDs).
