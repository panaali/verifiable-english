# Portable VE v0 evaluation cases

`evaluation.json` contains 177 valid environment/model/document cases (776
formulas). Every case has `id`, `environment`, `model`, `ast`, canonical `source`,
and the per-formula Boolean array `expected`. The whole-document value is the
conjunction of that array. The AST, environment, and model use the formats in
`docs/spec/v0-language.md`; the outer case envelope is a testing convention.

Cases cover the worked examples, all constructors, empty domains, vacuity,
constant aliases, ordered binary arguments, nearest-first binding, mixed sorts
sharing local IDs, and 160 seeded generated documents. The examples and explicit
corner cases mirror `tests/test_evaluate_search.py` and `tests/test_properties.py`.
These are development fixtures, not an independently frozen evaluation corpus.
Golden truth values are produced by Python, so the Lean comparison is a
cross-implementation differential check, not an independent oracle for decoding.

Regenerate with `python conformance/generate.py`. Run `python -m pytest
 tests/test_lean_conformance.py` (without the line break). When `lake` is available,
the test builds the pinned Lean project and compares every shared formula. With
no `lake`, the Python golden-value check runs and the Lean checks are skipped.

From `lean/`, `lake exe ve_conformance ../conformance/evaluation.json` emits a JSON
array of `{id, status, values, value}` records. A single case or array can also be
supplied on stdin. Exit 0 means all cases were evaluated; 1 means a case was
rejected; 2 means malformed restricted JSON or incorrect invocation. Logical
false is a successful result, not a decoder failure. The executable never reads
`expected`; the surface `source` is currently metadata for this AST bridge.

The bridge validates vocabulary declarations, typed ASTs, and model inventories,
and rejects duplicate JSON keys, unpaired surrogates, unsupported JSON numbers,
missing entries, duplicates, arity mismatches and dangling entities. Decoding,
limits, IO, Lean's compiler, and native runtime remain trusted and unproved. The
reference evaluator itself has no work-budget outcome. The bridge is intended
for bounded conformance inputs, not hostile workloads or certificate replay.
