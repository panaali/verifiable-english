# VE JSON authoring interface amendment — 2026-09-22

Authorized by Worker X's user instruction on `codex/p5`, before dispatch.
This is an **authoring INTERFACE change**, with the same content requirements
and no supplied answers. It supersedes neither the immutable v10 results nor
the v11 surface-authoring probe (0/12). The earlier v10 first-blocker audit had
24 surface-syntax/parse failures among 30 checker-reaching artifacts.

## Interface and information boundary

Author and one optional repair emit the claim graph as JSON under a per-item
JSON Schema, sent through Gemini's **`response_schema`** with
`response_mime_type=application/json`. There is no JSON-mode-only fallback.
The provider wire uses the existing `VertexBackend.wire` implementation.
[Google's structured-output documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/control-generated-output)
describes this mechanism; local validation remains mandatory.

The schema derives its constructor fields from `ve/fol.py`'s named-FOL import
format and `ve/ast.py`. A flat, dependency-ordered `expressions` array replaces
nested formula operands with earlier-expression indices. Expansion is purely
structural, bounded by the existing 64-depth/10,000-node limits. This avoids
recursive provider schemas and repeated formula serialization. The ground
fragment includes unary/binary atoms, equality, negation, conjunction,
disjunction, implication and top/bottom. These dossiers contain named entities
and ground rules; no quantifier inference is permitted or required.

Predicate enums come from the **public glossary**, using its existing R-number
as an ASCII `pNN` identifier and retaining its full sense description. Every
public sense, including distractors, remains available. Constants are the
public `unitN` names. The public `supplied` relation is available when it occurs
in the dossier. This is a vocabulary inventory only: it supplies no atom,
clause, per-use sense, node-to-record association, supporting-rule assignment,
answer, hidden label, reference environment, reference graph or certificate.
The only sort is the generic public entity sort.

Claim IDs are enums of the exact dossier premise/paragraph IDs, with exact
coverage validated locally. The original root is a singleton enum. The
`support` object's keys are exactly the paragraph IDs; values select additional
declared-premise IDs from an enum of all six declared premises. The harness
copies each dossier paragraph's public parent edges and adds only the model's
selected declared premises, deduplicating IDs. It supplies no rule-group
choice. Every claim has model-selected, nonempty public record associations.

The model must preserve every declared premise, grouped rule, conditional
alternative, entity and original root. Unassumed checks remain unassumed.
No invented bridge, dropped content, merged distinct meaning, true placeholder
or weakened root is allowed to obtain replay. Mechanical success does not
certify this fidelity; no fidelity judge is included in this probe.

The harness validates the JSON, expands references without logical rewriting,
then calls `document_from_named_fol`, **the existing `python -m ve import-fol`
path**, and `print_document` to obtain canonical VE. It passes that artifact to
the unchanged `author_graph`: one 10,000-step proof search per edge followed
by `check_argument(search=False)`. Failed outputs remain failures; there is
no automatic content correction. Repair receives the original output and
located schema/import or edge/checker diagnostics, never a suggested solution.

## Prespecified run and accounting

- New identity: `ve-json-author-feasibility-v12`; exactly the existing 12 DEV
  items in retained order. One author and at most one repair on failure.
- Gemini `gemini-3.1-pro-preview`, temperature 0, LOW thinking, seed 20260921.
  No critics, defenders, judges, ratings, scored items, calibration generations
  or extra scientific attempts. No full DEV cell rerun is authorized here.
- Up to 5,000 total output tokens per call, including thoughts (v11 used 4,096).
  This explicit serialization allowance accommodates the complete JSON graph;
  it is a resource-envelope change as well as an interface change, so this is
  not claimed to be an isolated, equal-token causal comparison with v11.
  Input reservation ceilings: 16,384 author / 20,480 repair.
- At retained rates ($2/M input, $12/M output), all 24 maximum reservations cost
  **$2.324736**. Hard cap **$2.50**, a separate durable ledger. Prior spending
  remains charged in its original ledger and is not refunded or overwritten.
- Schema/system changes invalidate the old exact-config token calibration.
  Do not transfer those residuals. Instead perform a conservative admission
  guard using full-config native countTokens **plus the complete schema's UTF-8
  byte length plus 512**, intentionally double-covering schema overhead. This
  is not presented as exact billing calibration. Reserve the complete input
  and output ceilings before dispatch; reconcile provider prompt, candidate
  and thought usage and halt on any ceiling/revision/billing mismatch. Unknown
  billing stays reserved. No separate paid calibration calls are made.
- Freeze code, tests, schema-bearing author requests, model/rates, guide, DEV
  material hashes and prior ledgers/results before inference. Store raw
  requests/replies, imported FOL, canonical VE, checker results and costs.
- Success is `author_graph.ok` after author or at most one repair, denominator
  **all 12**. Report initial and final success, final-item and all-attempt
  failure categories, spend and outstanding reservations. Unproved edges are
  not refutations; offline proof-status inspection may distinguish NotFound
  from ResourceLimit, without additional model calls or new repairs.
- If at least 6/12 replay, prepare the VE-only DEV cell rerun under a new run
  identity and print its command, **without running it**. Otherwise state the
  below-50% result and recommend reporting remaining feasibility limitations.
  Neither branch authorizes scored execution or retroactive relabeling.

## Addendum (2026-09-22, before v13 inference): wire-schema fix and new identity

The v12 identity dispatched exactly one call (DEV item 0 author). Vertex
rejected it with `400 INVALID_ARGUMENT` before generation. The v12 ledger is
settled with an `interrupted` event at the full reserved ceiling
($0.092768; actual billing unknown, never refunded) and v12 is closed.

A first smoke that moved the same schema to `response_json_schema` was also
rejected (charged at its $0.038912 ceiling). A capped
`gemini-2.5-flash-lite` bisection (`experiments/p5_json_schema_bisect.py`,
log `runs/ve-json-author-schema-bisect-v13.jsonl`, 9 calls, 16 output tokens,
charged as a rounded-up $0.001 allowance) returned the specific reason:
"The specified schema produces a constraint that has too many states for
serving". The cause is the array-length bounds (exact claim count,
`maxItems` 512/16). Removing only `minItems`/`maxItems`, except `minItems: 1`,
is accepted through both schema fields. A second `gemini-3.1-pro-preview`
smoke on DEV item 0's schema with a content-free instruction and a 64-token
cap was accepted (`runs/ve-json-author-schema-smoke2-v13`; its reply is not
used).

**v13 therefore changes only the provider copy of the schema**
(`wire_schema`): array length bounds are dropped; the wire field remains
`response_schema` via the unchanged `VertexBackend.wire`. The full schema,
with exact coverage and length bounds, is enforced locally by `validate`;
violations are located interface failures sent to the one repair. The
guide, messages (byte-identical to the v12 author request), models, token
envelopes, sampling and success definition are unchanged.

- New identity: `ve-json-author-feasibility-v13`, same 12 DEV items.
- Task cap remains **$2.50 in total**. Prior charges (v12 $0.092768, smoke 1
  $0.038912, smoke 2 actual, bisection $0.001) are subtracted; the v13 ledger
  cap is the remainder (about $2.36), which covers the unchanged $2.324736
  worst case for all 24 calls.
