# VE authoring feasibility amendment — 2026-09-22

Authorized by the user's 2026-09-22 instruction to Worker X on `codex/p5`, before
any new inference. This is a separate DEV-only authoring probe, not another
scored duel, replacement of v10 outcomes, or authorization to start scored
execution. Its ledger is separate and all previous spending stays charged.

## Retained evidence and first-failure taxonomy

Replay all 36 retained v10 author/repair/defender outputs unchanged. Six fail
JSON delivery; 30 reach the checker. Categorize by the **first observed blocker**,
not by speculation about errors hidden behind it:

| Category | Count |
| --- | ---: |
| Syntax/parse error | 24 |
| Undeclared or misspelled predicate | 0 |
| Sort/type error (unbound variable) | 1 |
| Wrong graph shape | 0 |
| Missing premise so step does not entail | 0 |
| Certificate/format (environment schema) | 5 |
| Prover ResourceLimit | 0 |
| Other | 0 |

The 24 parse failures include nine multi-statement sources rejected by Claim's
one-closed-statement contract and fifteen surface syntax errors. These counts
do not establish that later graph, vocabulary, or entailment checks would pass.
Three short examples (exact artifact identity can be joined through the offline
report's item ID, stage and response digest):

1. `id9eed1756a3842c2d7da8f08ce3b9290`, author: several period-terminated rules
   inside a single claim; `A claim must contain exactly one closed statement`.
2. `i910d7c5f209964573680cb7258301c2a`, author: predicate declarations omit
   `description`; `Incorrect fields (missing=['description'], unknown=[])`.
3. `i11e21a96aa6260b7bafaaec82c8810b9`, defender: bare `unit3` where a constant
   requires `@unit3`; `UnboundVariable: unbound variable 'unit3'`.

## Instruction/harness diagnosis and fixed prompt

The v10 environment **is already passed as an object**. No evidence supports
another environment-transport fix. All 30 are genuine rejections under the
current checker, not rejected valid proofs. However, the prompt only gave two
syntax examples and an environment example. It did not specify the one-formula
Claim boundary, binary connective grammar/no redundant parentheses, explicitly
mandatory declaration descriptions, complete graph/edge contract, or that the
harness constructs certificates. It had no complete replayed artifact example.
These are correctable instruction omissions, so 0/36 cannot by itself establish
irreducible formalisation cost.

The fixed, separately versioned guide documents the exact relational grammar,
one nested conjunction for a group of facts/rules, scope/sort/declaration rules,
all mandatory fields, coverage and acyclicity, and rule-group premises on edges.
It clarifies that source records do not become implicit logical premises. A
three-claim toy artifact using unrelated pebble/marked/round/inspected symbols
is checked by the actual prover and certificate checker before dispatch.
The existing graph checker and proof search are unchanged. Repair feedback adds
the failing claim ID and parser span, never rewritten source or a suggested
interpretation. The author chooses every dossier-specific symbol, sense,
formula, source association, and edge premise. No gold environment, hidden
labels, canonical formalisation, split location, root answer, or reference
certificate enters either request. No postprocessing fixes model artifacts.
The original v10 guide and trial records remain immutable; this replacement
guide is applied only by the feasibility runner pending future preregistration.

## Prespecified probe and budget

- Exactly the 12 existing DEV items in their retained order, separate contexts.
- Gemini `gemini-3.1-pro-preview` author, then **at most one repair if replay
  fails**, as in the registered author/repair branch. No critic, defender,
  queries, splits, judge, rating call, scored item or extra repair round.
- Existing temperature 0, LOW thinking, seed 20260921, 4096 total output-token
  ceiling including thoughts. No structured-output/schema intervention. The
  author and repair system instructions/generation configs stay unchanged;
  only the user guide and located diagnostics change.
- Raise only input capacity to 8192 (author) / 12288 (repair) for documentation
  and the full previous artifact. Existing config-specific Vertex token
  calibration still applies because the system/generation configs are exact.
- Maximum 24 completed scientific generation calls. At the retained registered rates ($2/M input,
  $12/M output), worst-case reservation is **$1.671168**. Hard run cap **$3**.
  Durable per-call reservations, provider usage (thoughts included), raw
  requests/replies and checks are retained in the new ledger. Unknown billing
  remains reserved. Existing paid-client infrastructure handling remains within
  the dollar cap; no retry of a completed scientific failure.
- The probe freeze binds code, amendment, generic example, DEV input hashes,
  exact author requests, config keys and prior immutable ledgers **before**
  dispatch. This local dated freeze is sufficient for the user-authorized
  feasibility probe; it does not renew or waive the main study's external
  timestamp/review/scored gates.
- Success means unchanged `author_graph` reports `ok`: all submitted edges
  have locally generated certificates accepted by `check_argument`. Report
  initial and after-one-repair successes over **all 12 items**, spend and
  delivery/checker failures. Mechanical replay alone is not source fidelity.
  A faithful formalisation of a flawed argument may remain unprovable; report
  parser/graph progress separately rather than calling all failed proofs
  author incompetence. Do not relax the original root/completion endpoint.
- If fewer than 6/12 replay after fixes, report that as a genuine
  formalisation-cost/feasibility finding **for this fixed resource envelope**.
  Recommend reporting VE authoring infeasibility as the arm result; any future
  k-repair arm must be separately preregistered and all calls/costs charged.

## Offline X decoder recheck

Use every retained v10 X critic response, extract unchanged question text with
the patched decoder, and build isolated requests with the actual retained
commitment. Verify exact context equality and preservation of raw wrappers.
Retain rejection of the truncated follow-up fence; do not invent missing
answers or relabel historical completions. Run the existing adversarial decoder,
visible-token-limit and isolated-copy regression tests as well. No X paid calls.

Results are recorded separately in `AUTHORING-FEASIBILITY-RESULTS.md` and
`runs/ve-author-feasibility-v11/summary.json`. This amendment is fixed before
those results and does not change in response to them.
