# VE authoring feasibility result — 2026-09-22

**0/12 DEV items replayed, initially or after one repair (0%).** The fixed-prompt
Gemini-only probe made 24 calls and spent **$1.145812**, below the authorized
**$3** cap. No pending reservations, infrastructure retries, judges, critics,
defenders, scored items or extra repair rounds. This is a genuine
**formalisation-cost finding under the fixed one-repair/4096-output-token
resource envelope**, not evidence that VE cannot be authored under other
budgets or that VE improves flaw detection.

The pre-inference [dated amendment](AUTHORING-FEASIBILITY-AMENDMENT.md),
[freeze](runs/ve-author-feasibility-v11/freeze.json),
[raw request/response and cost ledger](runs/ve-author-feasibility-v11/costs.jsonl),
[per-attempt checker replays](runs/ve-author-feasibility-v11/results.json), and
[summary](runs/ve-author-feasibility-v11/summary.json) are retained. The freeze
predates the first dispatch. All bound source files and retained v10 evidence,
ratings, materials, labels and paid ledger are unchanged. This probe does not
replace historical outcomes or renew the main study's execution freeze.

## Retained v10 failure taxonomy

First observed blocker in each original artifact, reproduced without rewriting
model content. Six additional artifacts fail JSON delivery before the checker.
The 30 checker failures are:

| Requested category | Count |
| --- | ---: |
| Syntax/parse error | 24 |
| Undeclared or misspelled predicate | 0 |
| Sort/type error | 1 |
| Wrong graph shape | 0 |
| Missing premise so the step does not entail | 0 |
| Certificate/format | 5 |
| Prover ResourceLimit | 0 |
| Other | 0 |

The parse category comprises nine sources containing multiple statements where
Claim requires exactly one, plus fifteen strict surface-syntax errors. The five
format failures omit required environment descriptions; no submitted proof
certificate was reached. The type/scope failure is an unbound variable. Zeroes
are **first-blocker counts**, not evidence that downstream checks would pass.

Three short examples:

- `id9eed1756a3842c2d7da8f08ce3b9290/author`: several separately terminated rules
  inside one claim → `A claim must contain exactly one closed statement`.
- `i910d7c5f209964573680cb7258301c2a/author`: predicate declaration omits
  `description` → environment schema rejection.
- `i11e21a96aa6260b7bafaaec82c8810b9/defender`: bare `unit3` instead of constant
  `@unit3` → `UnboundVariable`.

See the hash-bound [offline audit](runs/ve-author-feasibility-v11/offline-audit.json)
for all 36 retained artifacts and the actual claim/span diagnostics.

## Fixes evaluated

The old two-example guide did not explain the single-formula claim boundary,
exact binary conjunction nesting/no redundant parentheses, mandatory description
fields, complete graph/premise wiring, or certificate generation. Environment
objects already reached the checker correctly, so no transport fix was needed.

The replacement guide provides exact relational grammar, complete declaration
and graph contracts, nested-conjunction examples, and a full unrelated toy
artifact that replays with a locally generated certificate. It explains that
record text is not an implicit proof premise and that the harness creates
certificates. Repair receives the actual failing claim ID/span. No checker
relaxation, source rewriting, gold vocabulary, formalisation, flaw location,
answer or reference certificate is supplied. The author must still choose
all dossier-specific meanings and claims.

The author/repair system instructions, model configuration and 4096-token output
cap (thoughts included) stayed fixed. Only input capacity increased to hold the
guide and full prior response: 8192 author / 12288 repair. Existing exact-config
Vertex calibration remains applicable. The maximum scheduled reservation was
$1.671168; actual usage cost $1.145812 at the retained registered rates. Local
checker work is retained separately: about 0.669 CPU seconds / 2.787 elapsed
seconds across 17 delivered artifacts, with no additional paid inference.

## New probe outcomes

| Outcome | Count |
| --- | ---: |
| Initial replay success | 0/12 |
| Replay success with one repair | 0/12 |
| Delivered JSON | 17/24 artifacts |
| Valid environment schema | 17/17 delivered |
| All claims parse | 8/24 artifacts (5 initial, 3 repair) |
| Reached graph/certificate checking | 4/24 artifacts across 3 items |
| Initial + repair calls | 12 + 12 |
| Judges / scored calls | 0 / 0 |

The 24 artifact outcomes are nine syntax failures, four invalid alignment-ID
failures, seven JSON delivery failures (all `MAX_TOKENS`), and four graphs with
an unproved edge. No environment-description failures remain. The four checked
graphs each certify **15/16 edges**; each remaining edge returns `NotFound`
after 14 proof-search steps. None is a prover `ResourceLimit`, certificate
replay error, or graph-checker schema error. Offline proof-search details are
in [artifact-analysis.json](runs/ve-author-feasibility-v11/artifact-analysis.json).

An unproved edge can be a faithful encoding of a flawed original argument.
These four outputs therefore are not established semantic formalisation errors;
`NotFound` alone is not a refutation, and this no-judge probe does not establish
source fidelity. The requested completion endpoint still requires all edges
to replay, so they remain failures for the reported 0/12. Do not conceal this
distinction or reinterpret the three items as successful completed protocols.

## X decoder recheck and validation

Offline rechecking accepts all **19 original question texts across 12 retained
X critic responses**, including the nine formerly rejected annotated wrappers.
Each isolated request contains exactly the original packet, actual retained
commitment and unchanged question; wrapper annotations are not forwarded. The
truncated follow-up fence remains rejected. Actual historical X completion
remains **2/12**; no missing answers are invented and no paid X calls are made.

`UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run --offline pytest -q
tests/test_p5*.py`: **239 passed**, one third-party deprecation warning. This
includes malformed/ambiguous wrapper rejection, question-token-limit behavior,
synthetic isolated-copy execution using all nine observed wrappers, real toy
certificate replay, and DEV/author/repair-only budget/config boundaries.
The offline analysis also verifies raw response digests, unchanged prompt
systems, exact fixed-guide inclusion, original source/input hashes and freeze
before dispatch. Reproduce it without inference with:

```
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run --offline python -m experiments.p5_authoring_feasibility_analysis
```

## Recommendation

**Report VE authoring/completion infeasibility under this registered budget as
the VE arm result; do not proceed to scored VE execution or silently drop its
failed items.** The rate is below the requested 50% threshold even after
instruction fixes. Report the syntax/delivery burden, full authoring cost and
partial graph-checking progress alongside the 0/12 completion endpoint.

A future alternative may preregister a fixed **k** repair rounds and/or a larger
output allowance, charge all attempts and certificate work, retain all failures,
and compare within an explicit total-cost ceiling. It must also distinguish
valid source-faithful formalisation with an unsupported step from failure to
produce a usable artifact; otherwise additional repairs can merely pressure
the author to prove a flawed argument. That distinction needs an independently
specified source-fidelity assessment. Neither endpoint changes nor further
paid calls are applied here.
