# Lean-first batch 2: deletion ledger

Plan: `docs/LEAN-FIRST-PLAN.md` (draft 3), section 5.1 item 3 and section 5.2 row 2 ("Service throughput, and the
rule-3 measurement"). Base `24ea9e45` (the head of batch 1). The row lists one deletion: "per-call environment
re-encoding in the adapters". The batch decides nothing new: every answer is the answer of the same Lean
per-case function as before (`runMode`), read from a case whose environment is named by handle
(`VE.Service.Handles.expand`, theorems `expand_hit`, `expand_plain`, `runRequest_ok`).

## Deleted

| # | Deleted (base) | What it did | Owner now |
|---|---|---|---|
| R1 | the environment re-sent and re-decoded by the service with every case (`LeanService._texts` wrote each case's environment into the request; `VE.JsonInput.parseCases` split, digested and parsed it per case) | 1.1 ms of the 2.2 ms Lean CPU of a typing call on the agent-policy environment, 542 MB of request JSON in one agent-policy run | the service's handle table (`VE.Service.Handles`, `register`, `registerOne`): an environment is sent and parsed once per process, cases name it by its SHA-256; the client sends a case's environment object once per request (`lean_service._encode`, one encoding per object per request) |
| R2 | `rust_jsonl._run_checker`'s process per call (`Popen.communicate` of one line) | one `ve jsonl` process per evaluation or search: 22,533 in one agent-policy run, 5.6 ms wall per typing call on a quiet host | one persistent `ve jsonl -` process per caller (`rust_jsonl._Checker`, `_run_checker`); `ve jsonl` flushes each record (`rust/ve/src/main.rs`) |
| R3 | `rust_jsonl.run`'s SHA-256 of the 2.6 MB Rust binary on every call (`hashlib.sha256(binary.read_bytes())`) | the build check, recomputed per call | `lean_service.executable_sha256`, the one owner of executable hashing (cached by file identity, with its sidecar); a process is reused only while its executable keeps that identity (`_Checker.usable`) |
| R4 | `rust_jsonl.run`'s exit-status check of each record | a one-shot process's exit status agreeing with its record | none needed: a persistent process has no per-record exit status. A process that times out, ends its output, writes anything but one record or has output pending is killed and never reused (`_answer`, `exchange`, `usable`) |
| R5 | `background.background`'s Lean request on every call | 12,199 Background requests for the same few environments in one agent-policy run | `relay.decide_once`: one request per distinct request text per service pool (a pool runs one pinned build); a rejection is raised each time and kept nowhere |
| R6 | the handle member and bounds as numbers in Python (an intermediate state of this batch) | the client's mirror of the service's table | the service's handshake (`handles`), pinned by the schema rendered from the Lean shapes (`envelope.json`); `lean_service.HANDLE_KEY`, `MAX_HANDLES`, `MAX_HANDLE_BYTES` are read from it |

No decision site is deleted: R1-R6 are transport. `relay_lint` passes. No consumer of a deleted symbol remains
(`git grep` finds no `hashlib` in `rust_jsonl.py` and no caller of the removed exit-status path).

## Retained, named

| Site | Why it stays | Removed by |
|---|---|---|
| The adapters' per-call construction of the environment object (`Environment.to_dict`, `lean_runner.route_environment`, `rust_jsonl.rust_environment`) and its one JSON encoding per request | measured at 10 µs (`to_dict`) plus 29 µs (encoding) per call on the agent-policy environment, about 2 s of a 263 s harness run; the expensive half of "re-encoding" (sending and decoding it in Lean, R1) is gone | a later batch, if a measurement makes it worth an environment-text cache on `Environment` |
| Lean's per-call decoding of the registered environment into each mode's own structure | about 0.8 ms of the 0.94 ms Lean CPU of a typing call with a handle (section "Latency" of `DELTA.md`); each mode decodes the environment with its own decoder, so a decoded cache needs per-mode work | open item O2 of `DELTA.md` |
| `rust_jsonl.rust_environment` and `lean_runner.route_environment`, which both strip the `speech-acts@0` scope and the `rights@0` block from an environment object | Python-internal duplication of a transport projection, not a semantic decision; not listed for this batch | batch 15b (Rust's environment) |
| The two rule-3 duplicates (`eval.rs` with the order evaluator, the provers' Python replay) | retained pending question 10; this batch measures them (`rule3.json`) | batch 15b on its condition |

## Lines

`git diff --numstat 24ea9e45..HEAD`, product code only (tests, generated records and evidence excluded):

| Language | Added | Deleted |
|---|---:|---:|
| Python (`ve/`) | 406 | 51 |
| Lean (`lean/VE`, `lean/Serve.lean`, `lean/ResponseShape`) | 209 | 31 |
| Rust | 6 | 0 |

The Python growth is the handle client (`_Sent`, `_encode`, `_handle_request`, the mirror), the persistent Rust
process (`_Checker`, the idle pool, fork and exit handling) and `decide_once`: transport, which rule 5 of the plan
keeps per language. The batch deletes no semantic Python; its row lists none.
