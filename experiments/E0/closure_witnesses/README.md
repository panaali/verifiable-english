# Checked E0 closure witnesses

This directory contains **10 Cedar items and 5 Alloy items**, all exact sampled
IDs from `docs/spec/v0.1-coverage.md`. Each item has a `.ve` canonical strict
formula and a `.json` bundle containing the v0.1 environment, indexed AST,
source provenance, adapter conditions, and one true and one false finite model.
`manifest.json` lists the files. `report.json` records all 30 Python/Lean truth
comparisons, independent graph checks, and environment-bound artifact identities.

The source text is copied exactly from sampled records at git revision
`46be9e1bafc85e37456cbf56e9dc92b6c8178666`, with its SHA-256 recorded per item.
The validator checks the source against that immutable git object and checks
membership in the design's sampled closure ID set. The two identical Chord
predicate texts retain their distinct sampled IDs.

| File prefix | Sampled item suffix | Main translation |
|---|---|---|
| `cedar_01` | `sales_orgs/templated/policies.cedar#3` | Action-group RTC and present owner equality |
| `cedar_02` | `github_example/policies.cedar#5` | RTC into the writers **group entity**, not set membership |
| `cedar_03` | `sales_orgs/static/policies.cedar#5` | Action RTC and RTC into a member of the reified viewerMarkets set |
| `cedar_04` | `github-templates/cedar/policies.cedar#0` | Principal slot RTC, action equality and resource slot equality |
| `cedar_05` | `PhotoApp/photoapp.cedar#4` | Family and album RTC |
| `cedar_06` | `gdrive-templates/cedar/policies.cedar#0` | Principal and resource slot RTC |
| `cedar_07` | `policies_3c.cedar#0` | Principal equality, arbitrary action, album RTC |
| `cedar_08` | `policies_2a.cedar#0` | Friends-group RTC, exact action/photo |
| `cedar_09` | `cedar-java-partial-evaluation/app/src/main/resources/policies.cedar#0` | Principal, action and resource hierarchy RTC |
| `cedar_10` | `policies_3a.cedar#0` | Exact view action and album RTC |
| `alloy_01_chord2` | `chord2.als@81` | Positive filtered successor paths with a fixed origin parameter |
| `alloy_02_chord` | `chord.als@80` | Separate sampled copy of the same predicate |
| `alloy_03_connected` | `iolus.als@5190` | RTC of parent or its converse |
| `alloy_04_dag` | `javatypes_soundness.als@282` | No positive diagonal xtends path |
| `alloy_05_one_node` | `chord2.als@4943` | Exactly one Node, expanded NextCorrect, and the union State.active |

Cedar formulas define each policy's per-request **permit contribution** by a
biconditional; they do not claim to be the final authorization decision.
Requests are reified with total principal/action/resource projections. All
entity types share a UID carrier with separate unary type tags. The adapter
checks unique UIDs, a partition by type tags, acyclic immediate parent edges,
functional entity attributes, and explicit set-value objects. An absent field
has no field row; a present empty set has a collection object with no members.
Only positive field-access conditions occur in these selected policies, so
absence/error contributes no permit. Slots are explicitly bound constants.

The false Cedar models retain the proposed permit output but remove an edge
needed by the matching condition, making its defining equivalence false.
The Alloy contrasts exercise filtering **into** an outer origin, graph
connectivity, positive cycles, and empty states versus the union of active
nodes. No numeric scope is added. Alloy field multiplicities and State.data
reification are checked separately from truth of the sampled formula. The
`ShowMe1Node` false model keeps one Node and an Id cycle but has no State, so
`State.active = Node` fails; its quantified NextCorrect is vacuous. Its formula
still expands both NextCorrect clauses and filtered less_than, without using
opaque helper predicates.

The validator includes handwritten independent graph interpretations of the
sampled conditions; these do not call the VE evaluator. Both model results are
then checked with the proved Lean finite evaluator. Labels and expected values
are not sent to Lean. These checks establish finite witness validity in the
recorded representation. They do **not** prove source-to-VE translation
equivalence, validate entire Cedar schemas or Alloy modules, or run Cedar/Alloy
engines. Unrelated module facts and fields are outside the sampled formula;
relevant representation constraints are listed in each bundle. These are
synthetic development witnesses, not a revised E0 coverage score.

Reproduce from the repository root, sequentially:

```sh
(cd lean && lake build)
UV_CACHE_DIR=/private/tmp/ve-uv-cache .venv/bin/python experiments/E0/closure_witnesses/generate.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache .venv/bin/python experiments/E0/closure_witnesses/validate.py
VE_LEAN_PREBUILT=1 UV_CACHE_DIR=/private/tmp/ve-uv-cache .venv/bin/python -m pytest -q tests/test_closure_witnesses.py
```
