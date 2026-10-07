# Batch 13a fix report

Base: `7345e3ed`. Branch: `lean-first/b13a`. Scope: Lean parse diagnostics with
spans, the order-family printer, and certificate binding prechecks and step
budgets. The [deletion ledger](LEDGER.md) names the owner and caller for every
removed decision site. Source diff (excluding generated inventories and schema
snapshots): 568 Lean lines added, 82 Lean lines deleted, 106 Python lines
deleted. The gross source deletion count is 188 lines (`git diff --numstat
7345e3ed`, limited to `.lean` and the four changed Python modules).

## Gate evidence

| Item | Status and evidence |
|---|---|
| AGENT — conformance and public A/B | [`evidence/corpus-ab.json`](evidence/corpus-ab.json) has 94,489 records: 94,440 identical and 49 listed wording changes; zero unlisted. All 294 pilot records match. The exact text block is in [`DELTA.json`](DELTA.json) and classified in [`DELTA.md`](DELTA.md). |
| AGENT — differential fuzz | [`evidence/difffuzz-ab.json`](evidence/difffuzz-ab.json): 15 paired runs, including CI and 14 date seeds; identical finding maps, zero head-only signatures; reviewed baseline 357 before and after. |
| AGENT — latency | [`evidence/latency-ab.json`](evidence/latency-ab.json): five paired 100-call samples per changed path, matching request hashes. All median Lean CPU changes are at most 20%; all head median CPU values are below 2 ms and all head p95 wall values below 10 ms. |
| AGENT — focused tests | `VE_AUTHORITY=lean` focused parser and response-schema suites: 142 passed. The source inventory, producer schema, frozen inventory, wire contract, Lean import graph, and full clean-head gate are checked at handoff. |
| HUMAN — wording block | DRI, exact review of the 16 before/after text pairs in `DELTA.json`. DRI answer 3 (2026-10-04) already approves Lean as canonical text owner; exact pair signoff is deferred to that owner. |
| HUMAN — theorem statement | DRI, approval of the one changed audited statement, `VE.Service.runMode_parse`. `tools/lean_statements.py --diff` against the base reports zero added, zero removed, one changed. This states the new parse dispatch; its `rfl` proof builds. |
| EXTERNAL — operational soak | Owner: DRI after batch 13b, per DRI answer 1. This batch does not begin that soak. |

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
