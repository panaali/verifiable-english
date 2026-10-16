# Lean service response schemas

The shapes of `ve_service` responses (`docs/spec/lean-service.md`, stage 1 of
`docs/spec/SEMANTICS-MIGRATION-PLAN.md`), **generated from Lean; never edit them by hand**.

**One source** (lf-1 recheck B). The shapes are written once, as Lean data beside the service:
`lean/ResponseShape/Schemas/<File>.lean` (one module per file here) in the dialect of
`lean/ResponseShape.lean`. From that source

* `python tools/response_schemas.py --write` renders every `*.json` here (through
  `ve_response_decode`, check `schemas`), and `--check` fails on a file that differs from its
  rendering, a missing one, or a file the Lean source does not render
  (`tests/test_response_schemas.py`);
* `ve_response_decode` decides responses by checking the same shapes (`ResponseShape.check`),
  so the client and the Lean side read one description;
* every value domain of a Lean decoder carries the decoder (`decidedBy`: `Bridge.decodeFormula`,
  `Order.Wire.decodeFormula`, `Route.Admission.decodeKind`, `parseLabel`, `token`, `decodeInt`,
  `atomicKind`, `EnglishRun.decodeTok`), and every route's path selector the runner's dispatch
  test (`usesSoftPath`, `usesRightsPath`, ..., `usesNormsPath`): Lean decides each value with both
  and fails (`broken`) when they disagree, so a schema cannot drift from the decoder or dispatch it
  names;
* enumerations with a Lean list are that list (`Service.rejectionCodes`, `Service.modes`, the
  limits, `Route.Admission.acts`/`modalities`/`relations`, `Route.Background.generators`,
  `Norms.Plain.statementLayers`).

To change a shape, edit the Lean module, `lake build ve_response_decode`, then
`python tools/response_schemas.py --write`.

* `envelope.json`: the response line; its context is the request
  `{"id": nonce, "mode", "cases": [...], "digests": [...], "bytes": trimmed cases size}`,
  where `digests[i]` is the SHA-256 of the text of case `i` as sent (`null` when the cases
  text does not split into cases). Result `i` is bound:
  `{"digest": digests[i], "index": i, "result"}`. A request error is bound too: it echoes
  the nonce, the mode and `digests`.
* `<mode>.json` for every mode: `row` is the schema of one `result`; its context is
  the request case at the same position.
* Every rejection carries `code`, the public diagnostic code the service derives from its
  message (`Service.Protocol.rejectionCode`): a request error in its own line, a result whose
  `status` is `error` beside it in its bound entry (`{"index", "digest", "result", "code"}`,
  with `generator` when the message names an `InvalidModel(generator)`), so the runners' rows
  are unchanged. The handshake's `codes` is that code domain; a service with another list is
  refused at its start.
* `common.json`: shared value domains, each the domain of the Lean decoder named in
  its `$comment` (formulas, terms, kinds, labels, ...).

**What the schemas check** (threat model, `docs/spec/lean-service.md`): binding to the
request and well-formedness. The binding is the nonce, the mode, each
result's position and case digest (a request error: every case digest), and the identity
fields a runner echoes from its case, graph claims, and the bounds of certificate counts.
The well-formedness is the Lean decoders' domains. A rule belongs here only if its
expected value can be read directly off the request. Values the runners compute belong
to the service, which the tests check on its outputs (`ve_response_decode`'s
`invariants`); the client never predicts them (architecture decision D1). Examples are
certificate Background counts (bound here only by `x-background-bound`), graph unfoldings,
dependency orders, target lists and their sorts, and the relations between result fields.

**Every answer is closed** (lf-1 review B). A mode's `ok` rows list each field its Lean
encoder writes, required (or conditional, with the condition the encoder uses), typed to
its leaves, with `additionalProperties: false`; nested objects are closed too, except maps
keyed by request names (`additionalProperties` is then a schema). A statement-layer route
(the batch 1 modes) answers a case on its own path with its own rows and delegates every
other case unchanged: the `x-select` on the request is the route's dispatch test
(`usesSoftPath`, `usesRightsPath`, ...) and the delegate's row is `$ref`'d. No caller reads a
field the schema did not check, so a dropped, emptied or retyped field is
`CheckerUnavailable`, never a `KeyError` in the caller. `tests/test_route_row_schemas.py`
checks the route modes on genuine answers (`tests/data/route-cases.jsonl`) and on every drop,
empty and retype of every field, against `ve_response_decode`.

`ve/backends/service_schema.py` compiles these files; `ve/backends/lean_service.py`
has no other shape checks. `lean/ResponseDecode.lean` (`ve_response_decode`, check `decode`)
checks the same responses with the Lean shapes and decoders, and `tests/test_lean_service_schema.py`
requires the two to agree on genuine service responses and on every mutation of them (the
Python and Lean readings of the dialect, and each decoder beside its grammar).

## Dialect

A subset of JSON Schema 2020-12: boolean schemas, `$ref` (local or `file.json#/...`),
`type` (`integer` excludes booleans; `number` is unused), `enum`, `const` (strict JSON
equality, so `false` is not `0`), `pattern` (whole-string match, `.` matches newlines),
`minLength`, `maxLength`, `minimum`, `properties`, `required`, `additionalProperties`,
`items`, `prefixItems`, `minItems`, `maxItems`, `contains`, `anyOf`, `allOf`, `not`,
`if`/`then`/`else`. As in JSON Schema, a keyword for one JSON type ignores other types.

Extensions. A pointer is a JSON pointer; `*` maps the rest of the pointer over every
element of an array (every element must resolve).

| Keyword | Meaning |
|---|---|
| `x-tagged: {tag: [s1, ..., sn]}` | an array `[tag, v1, ..., vn]` with each `vi` valid under `si` |
| `x-fuel: {counter, limit}` | at most `limit` nested entries into schemas with this counter (Lean decoder fuel); formulas the runners generate (`generated_formula`) have none, since generation is not bounded by the decoders' depth |
| `x-echo: p` | equals the context value at `p`, or `null` if it is absent (`Json.getObjValD`) |
| `x-equals: p` | equals the context value at `p`, which must exist |
| `x-length: p` | an array as long as the context array at `p` |
| `x-count: p` | the integer length of the context array at `p` |
| `x-same-length: [f, ...]` | sibling response fields are arrays with equal lengths (the generated Background, premises and generator rows) |
| `x-equal-fields: [a, b]` | two sibling response fields have the same JSON value (the two copies of generated Background) |
| `x-references: {array: a, field: f, in: p}` | every object in the response array at `a` has a string field `f` equal to one member of the context array at `p` |
| `x-claim-nodes: [p, ...]` | every claim at each response pointer (one claim or an array) matches a request graph node by name, AST and presence and value of the optional label |
| `x-max-steps: {default, cap}` | a certificate step count is at most the request's `max_steps`, or the generated default, capped at the generated maximum |
| `x-background-bound: true` | a certificate background count is an integer at most what the request could generate: four per predicate declaration (two flags, a definition, a norm pair), one per pair of constants, one per `soft_premises` element; the exact count is the service's (`ResponseShape.backgroundBound`) |
| `x-source-span: p` | a diagnostic object's start and end lie within the request source string at `p`, with line and column equal to its start position (Unicode code points, one-based line and column) |
| `x-index: true` | the position of the result in the response |
| `x-digest: true` | the digest of the result's case (`digests[i]` of the request) |
| `x-zip: {of: p, items: s}` | an array with element `i` valid under `s` with context element `i` of the context array at `p` |
| `x-zip-or-empty: {of: p, items: s}` | as `x-zip`, with a missing context array treated as empty; a present non-array is invalid |
| `x-case: s` | the context is valid under `s` |
| `x-select: [{when, then}, ...]` | the first `when` valid for the context selects `then`; none fails |
| `x-count-where: {array, where, equals}` | the number of elements of `array` valid under `where` equals `equals` |
| `x-count-presence: {value, equals}` | the integer at `equals` is 0 for a null `value`, and 1 otherwise; both paths must exist |
| `x-reading-plan: true` | every returned reading index is in its request set, coupling labels name request couplings, an over-budget count is bounded by the request's product, and open units name request units; Lean checks compatibility and completeness |
| `x-rows: s` | one element per case; element `i` is valid under `s` for result `i` (its case `cases[i]`, position `i` and digest `digests[i]`) |
| `x-row: true` | valid under the mode's `row` with the context of the enclosing result's case |
