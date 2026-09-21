# Independent second-rater working record

Read only `../survey_samples/_drawn/<dataset>.json` for sampled items. Do not read
`../survey_samples/<dataset>.jsonl`, which contains the first rater's labels, or
`../SURVEY.md`, which contains the first rater's aggregate conclusions. Dataset
agents receive no first-rater labels. Their outputs are frozen before comparison.

Checker source: `ve-integration` at `12538d8d418b3eeec59e58d74c3886786e5139da`,
exported to `/private/tmp/ve-e0-integration`. Run Python with
`UV_CACHE_DIR=/private/tmp/ve-uv-cache-grammar` and
`PYTHONPATH=/private/tmp/ve-e0-integration`.

Each dataset output is an array of 30 JSONL records with fields `dataset`, `id`,
`label`, `construct_needed` (list), `rationale`, `formalization` (v0 document or
null), `environment` (complete v0 environment or null), `parse_result` (checker
record or a status dictionary), and `reification` (explanation or null). Preserve
sample IDs verbatim. Auxiliary fields are allowed. Do not commit independently.

The item unit is the sampled source: FOLIO sentence (consult gold but rate the
sentence's meaning), ProofWriter theory plus question, Cedar policy, Gatekeeper
constraint's violation condition including helpers/exemptions (diagnostic message
formatting is excluded), Alloy paragraph with referenced definitions expanded,
FRET requirement, and Clover program's functional specification (contracts,
supporting predicates, and invariants; algorithm implementation itself excluded).

Use DIRECT for unary/binary function-free FOL, REIFIED for explicit mechanical
meaning-preserving relational encodings. No invented finite bounds, unconstrained
"arithmetic" or "reachable" predicates, or deletion of qualifications. Fixed
finite cardinalities can be expressed using equality; general counting cannot.
OPAQUE means an otherwise useful relational skeleton depends on named interpreted
checks that v0 cannot implement. NO means the essential claim requires an excluded
construct, with no useful independent relational content. These two categories
require judgment; state exactly what is hidden or unavailable. Predicate inputs
must not be mislabeled direct merely because their names hide difficult content.

Actually write and check at least min(10, number of DIRECT+REIFIED items) per
dataset; checking every claimed fit is preferred. Use `ve.check(Environment(...),
source)` from the pinned source and preserve results. A failing DIRECT witness
must be repaired or downgraded. Parser acceptance verifies syntax/types only,
not semantic correspondence with the source.
