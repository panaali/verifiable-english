# Lean service response schemas

The single source of truth for the shapes of `ve_service` responses
(`docs/spec/lean-service.md`, stage 1 of `docs/spec/SEMANTICS-MIGRATION-PLAN.md`).

* `envelope.json`: the response line; its context is the request
  `{"id": nonce, "mode", "cases": [...], "bytes": trimmed cases size}`.
* `<mode>.json` for the nine modes: `row` is the schema of one result; its context is
  the request case at the same position.
* `common.json`: shared value domains, each the domain of the Lean decoder named in
  its `$comment` (formulas, terms, kinds, labels, ...).

`ve/backends/service_schema.py` compiles these files; `ve/backends/lean_service.py`
has no other shape checks. `lean/ResponseDecode.lean` (`ve_response_decode`) decodes
the same responses with the Lean decoders, and `tests/test_lean_service_schema.py`
requires the two to agree on genuine service responses and on every mutation of them.

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
| `x-fuel: {counter, limit}` | at most `limit` nested entries into schemas with this counter (Lean decoder fuel) |
| `x-echo: p` | equals the context value at `p`, or `null` if it is absent (`Json.getObjValD`) |
| `x-equals: p` | equals the context value at `p`, which must exist |
| `x-length: p` | an array as long as the context array at `p` |
| `x-count: p` | the integer length of the context array at `p` |
| `x-index: true` | the position of the result in the response |
| `x-member: {of: p, keys, where}` | the instance's `keys` equal those of some context element at `p` (absent keys stay absent) valid under `where` (default `true`) |
| `x-dependency-order: p` | `Route.verifyOrder` accepts the instance for the dependency nodes at `p` |
| `x-zip: {of: p, items: s}` | an array with element `i` valid under `s` with context element `i` of the context array at `p` |
| `x-case: s` | the context is valid under `s` |
| `x-select: [{when, then}, ...]` | the first `when` valid for the context selects `then`; none fails |
| `x-same: [[p, q], ...]` | instance values at `p` and `q` are equal |
| `x-same-length: [[p, q], ...]` | instance arrays at `p` and `q` have the same length |
| `x-in: [[p, q], ...]` | the instance value at `p` is an element of the instance array at `q` |
| `x-capture: {source, pattern, target}` | `pattern` matches a prefix of `source`; group 1 equals `target` |
| `x-count-where: {array, where, equals}` | the number of elements of `array` valid under `where` equals `equals` |
| `x-rows: true` | element `i` is valid under the mode's `row` with context `cases[i]` |
