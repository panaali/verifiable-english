# Batch 13a fix report

Base: `7345e3ed`. Branch: `lean-first/b13a`. Scope: Lean parse diagnostics with
spans, the order-family printer, and certificate binding prechecks and step
budgets. The [deletion ledger](LEDGER.md) names the owner and caller for every
removed decision site. Source diff (excluding generated inventories and schema
snapshots): 594 Lean lines added, 90 Lean lines deleted, 106 Python lines
deleted. The gross source deletion count is 196 lines (`git diff --numstat
7345e3ed`, limited to `.lean` and the four changed Python modules).

## Gate evidence

| Item | Status and evidence |
|---|---|
| AGENT — conformance and public A/B | [`evidence/corpus-ab.json`](evidence/corpus-ab.json) has 94,489 records: 94,440 identical and 49 listed wording changes; zero unlisted. All 294 pilot records match. The exact text block is in [`DELTA.json`](DELTA.json) and classified in [`DELTA.md`](DELTA.md). |
| AGENT — differential fuzz | [`evidence/difffuzz-ab.json`](evidence/difffuzz-ab.json): 15 paired runs, including CI and 14 date seeds; identical finding maps, zero head-only signatures; reviewed baseline 357 before and after. |
| AGENT — latency | [`evidence/latency-ab.json`](evidence/latency-ab.json): five paired 100-call samples per changed path, matching request hashes. All median Lean CPU changes are at most 20%; all head median CPU values are below 2 ms and all head p95 wall values below 10 ms. |
| AGENT — focused tests | `VE_AUTHORITY=lean` focused parser and response-schema suites: 142 passed. The source inventory, producer schema, frozen inventory, wire contract, Lean import graph, and full clean-head gate are checked at handoff. |
| HUMAN — wording block | DRI, exact review of the 16 before/after text pairs in `DELTA.json`. DRI answer 3 (2026-10-04) already approves Lean as canonical text owner; exact pair signoff is deferred to that owner. |
| HUMAN — theorem statements | DRI, approval of two changed dispatch statements, `VE.Service.runMode_parse` and `VE.Service.runMode_checkCertificate`, two added helpers, `VE.Route.WireSound.valid_field_steps` and `VE.Norms.RunSound.valid_field_steps`, and the changed response-shape theorem `ResponseShape.Encoders.Conformance.checkCertificate_fits`. `tools/lean_statements.py --diff` against the base reports two added, zero removed, two changed among audited VE statements. Their proofs build. |
| HUMAN — trust budget | DRI, signed allowance for the growth reported by `tools/trust_map.py --check`. Declaration classification has zero problems; the baseline check reports S +960 and untied V +703 across this tree, including pre-existing senses work and the 13a diagnostic. No allowance was invented in this batch. |
| EXTERNAL — operational soak | Owner: DRI after batch 13b, per DRI answer 1. This batch does not begin that soak. |

## Final review fixes

The B parse diagnostic finding is closed by adding `no` to the Lean surface
reserved vocabulary (also used by the diagnostic scanner), mirroring the Python
and Rust lists. The lexical proof now enumerates the Lean list by decision
instead of a hand-counted disjunction. Regression tests compare every reserved
word in term and binder position, including malformed `no@`, against Python's
code, message and span.

The B replay budget finding is closed at `CertificateWire.limit`: only an absent
`max_steps` uses the default. Present values must be nonnegative integers; the
shared `Except` result reaches FOL, closure, order, core and norms replay
runners. Regressions cover `false`, `"0"`, `[]`, `{}`, `null`, negative and
fractional values. The exact previously unlisted effects are recorded in
`DELTA.md` and `DELTA.json`.

## Mutation proof

Three seeded changes were run and removed. Raw failing and restored outputs are
in [`evidence/mutant-python.txt`](evidence/mutant-python.txt) and
[`evidence/mutant-order.txt`](evidence/mutant-order.txt).

1. Make Python parse before Lean on a rejected source: `test_public_lean_parse_uses_lean_rejection` fails.
2. Print order `<=` as `<`: the permanent `#guard` in `VE.Order.Surface` fails its Lean build.
3. Drop `max_steps` from the public Lean certificate request: `test_public_certificate_budget_is_sent_to_lean` fails.

All three were removed and the focused tests or build passed again. No model
calls, push, or external writes were made. Default Python authority replay and
definitions surface sugar remain scheduled for batch 13b; the prover-internal
replay remains under batch 15's measurement gate. The full gate command at
handoff is `tools/gate.py --workers 8 --output /tmp/b13a-gate-final.json` on
the clean committed HEAD.
