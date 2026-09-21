# Experimental Python VE v0 core

The implementation supports exactly `ve.core@0`, `relational-fol@0`, and
`ve-v0-draft-2026-09-20`. It implements the draft semantics; it does not establish
the pending theorems in [the verification contract](spec/verification-contract.md).
`uv.lock` pins the test/build dependencies. There are no third-party runtime
dependencies. Use Python 3.14 and `uv sync`; run `uv run python -m pytest`.

## Python API

```python
from pathlib import Path
from ve import Environment, FiniteModel, parse, print_document, evaluate
from ve import check, find_countermodel, check_countermodel

env = Environment.from_json(Path("examples/environment.json").read_bytes())
source = Path("examples/requirements.ve").read_bytes()
document = parse(env, source)
model = FiniteModel.from_json(env, Path("examples/model.json").read_bytes())
assert evaluate(env, document, model).status == "Satisfied"
print(print_document(env, document))
record = check(env, source, model, candidate_ast=document)

premises = parse(env, Path("examples/premise.ve").read_bytes()).formulas
conclusion = parse(env, Path("examples/conclusion.ve").read_bytes()).formulas[0]
search = find_countermodel(env, premises, conclusion, max_domain_size=2)
if search.status == "Found":
    assert check_countermodel(env, premises, conclusion, search.model).valid
```

`ve.ast` exposes frozen raw constructors: `Var(index)`, `Const(name)`, `Top`,
`Bottom`, `Unary(predicate, term)`, `Binary(predicate, left, right)`, `Eq`, `Not`,
`And`, `Or`, `Implies`, `Forall(sort, body)`, and `Exists(sort, body)`.
`Document(formulas)` defensively copies its ordered, nonempty formula sequence
(nonemptiness is checked at validation). Variables use nearest-first de Bruijn
indices. The runtime uses **extrinsic typing**: constructors are convenient raw
syntax, and `check_formula`/`check_document` establish closure, scope, sort and
arity correctness under the supplied environment. Public semantic consumers
validate inputs themselves. Python annotations alone are not evidence of typing.
The Python interpreter and in-process code are trusted; arbitrary malicious
Python execution is outside this data-only interface's threat model.

Environment and model factories validate all required fields and make defensive,
immutable copies. Empty sorts are permitted unless a constant inhabits them.
Constants may alias. Equal local identifiers in different sorts are distinct
entities. Model membership is closed-world only inside the explicitly complete
supplied inventory; this makes no assertion about real-world completeness.

`parse_with_metadata` retains original source names and spans separately from
semantic nodes. Its metadata documents its ordering. `canonicalize` changes only
binder names and grammar serialization; `is_canonical` compares exact bytes.
There is no source normalization before checking: CRLF, tabs, comments, missing
final LF, implicit grouping and unsupported operators fail.

## Interchange and identity

Use the [specified wire shapes](spec/v0-language.md) for environments and models.
Use `ve.ast.document_from_data`, `document_to_data`, and `doc_from_json` for the
indexed AST. Documents are arrays of formula arrays; single formulas are tagged
arrays. Invalid tags, arities, Boolean/negative indices, free indices and sort
mismatches fail. Source remains separate from AST; `check(..., candidate_ast=...)`
rejects an individually valid AST that does not match the parsed source.

`ve.wire.loads_json` rejects duplicate object keys before overwrite, lone
surrogates, floats, null, excessive size/depth, and integers outside `[0, 2^53-1]`.
`canonical_json` implements the restricted RFC 8785 subset: UTF-16 key order,
minimal JSON string escaping, integer serialization, no insignificant whitespace.
Model domain and relation sets are sorted before identity; duplicates are errors.
Formula order, tuple argument order, and predicate signatures are never sorted.

`source_id` binds exact submitted bytes. `Environment.environment_id` binds the
complete vocabulary including descriptions. `meaning_id(env, document)` binds
the entire document array; `meaning_id(env, formula)` binds one formula array.
These are deliberately different preimages. The argument layer should use the
single-formula variant consistently for claims and must require one statement.
`FiniteModel.model_id` binds the normalized inventory and its environment.
All hashes use the specified domain-separated SHA-256 preimages. Hashes identify
artifacts; they do not certify semantic equivalence or truth.
Diagnostic result records use ordinary JSON, including `null` for an unavailable
Boolean or absent search witness. They are not semantic input packages or new
certificate encodings; the argument-layer wire contract remains a separate task.

## Four views and FOL interchange

`render(ast, env, view)` returns a deterministic string for a closed formula or
`Document`. The views are `fol_symbols`, `fol_keywords`, `ve_strict`, and
`ve_natural`. They share one traversal, preorder binder names, and formula
parenthesisation. Natural vocabulary templates, fallback rules, and the full
read-only grammar are documented in [rendering views](rendering-views.md).
`print_document` preserves the existing strict canonical serialization.

`render_fol(env, value, view=...)` accepts these four names and returns text.
The legacy `canonical` default returns strict text; `natural` returns a
`NaturalView` record. This adapter accepts a `Document`, an
indexed document array, or the following explicit named-FOL object. This is an
AST API, not an arbitrary FOL string parser. Adapters must handle dataset syntax
and declare all sorts, constants, and predicates themselves; unsupported items
must remain visible in coverage accounting.

```python
from ve import render_fol

named = {"formulas": [{
    "op": "forall", "sort": "service", "variable": "s", "body": {
        "op": "exists", "sort": "person", "variable": "p", "body": {
            "op": "binary", "predicate": "owns",
            "left": {"var": "p"}, "right": {"var": "s"}
        }
    }
}]}
strict_text = render_fol(env, named)
natural_view = render_fol(env, named, view="natural")
print(natural_view.text)
```

Named formulas use the same tags as indexed formulas in an `op` field:
`top`/`bottom`; `unary` with `predicate, term`; `binary` with `predicate, left,
right`; `eq` with `left, right`; `not` with `body`; binary connectives with
`left, right`; quantifiers with `sort, variable, body`. Terms have exactly one
`var` or `const` field. Unknown fields and missing operands fail. Imported
variable declarations and references must obey the strict ASCII identifier and
length rules, avoid reserved/schema names, and obey scope without shadowing.
`document_to_named_fol(env, document)` exports this same object shape with
canonical preorder binder names; importing that export recovers the exact AST.

The natural view is a conservative ACE-style experimental display, **not an ACE
parser or an independently verified ACE translation**. It returns text, renderer
name/version, environment ID and meaning ID. Every constructor is rendered with
explicit scope; existential witnesses remain nested under their dependencies,
disjunction explicitly permits both, and no statement or antecedent is omitted.
No LLM paraphrasing, vocabulary definitions, inference, quantifier reordering,
or implicit existence assumptions occur. Read-only natural text is not accepted
as strict VE. Its readability and semantic fidelity still require review and
formal correspondence evidence before higher assurance is claimed.

## Evaluation and finite search

`evaluate` returns `Satisfied`, `Violated`, or `ResourceLimit`, a Boolean or no
result, work count, and explanatory bindings. Explanations explicitly distinguish
empty-domain universal satisfaction, lack of existential witnesses, and material
implication with a false antecedent. Binding records contain de Bruijn index,
sort, and local ID rather than ambiguous untyped names. Evaluation short-circuits;
an unvisited branch is not evidence about that branch. Work exhaustion is never
reported as a false claim. A separate `max_trace_nodes` budget defaults to 10,000;
exhausting it also returns `ResourceLimit`, even when formula-work budget remains.
Use `evaluate(..., trace=False)` or `check(..., trace=False)` to omit explanatory
trees (`explanation: null`) and use the full 1,000,000-node evaluation envelope.
`max_evaluations` is exposed by `evaluate`, `check`, `check_countermodel`,
`find_countermodel`, and `find_distinguishing_model`; work exhaustion is never a
logical negative. Countermodel checks and search use no-trace evaluation.
Search uses private validated evaluation paths after validating each generated
model once; public witness checks still independently validate submitted models.

`find_countermodel` enumerates finite domains, constant denotations (including
aliases), and relation subsets within explicit size/model/work bounds. Only
predicates occurring in the premises/conclusion or `a`/`b`, plus
`nonvacuous_for`, have their relations enumerated. Every other declared predicate
is fixed to the empty relation in the complete returned model. This reduction
is sound for finding distinguishing/countermodels: changing an unused predicate
cannot affect any checked formula's truth or guard satisfaction. Bounded
`NotFound` exhausts representatives modulo unused relations, not every complete
interpretation of the vocabulary. Domain vectors are streamed by total entity
count then lexical size vector. Within each vector, used relation interpretations
are streamed by total tuple count across all relations then sorted predicate
names and generated domain order; each is paired with all constant denotations.
Sparse small witnesses come first without materializing the exponential set of interpretations. It is a
small exponential search tool intended for mechanism examples, not a scalable
general-purpose solver. `Found` supplies a witness; `NotFound` means only that
the bounded enumeration finished; `ResourceLimit` means the search stopped
early. None supplies positive entailment evidence. The language has invalid
inferences with no finite countermodels at all.

`min_domain_size=0` preserves the default empty-sort semantics;
`nonempty_domains=True` raises the minimum to at least 1 for **all** sorts.
Constants continue to require an inhabitant of their sorts. These are search
filters, not extra logical axioms. Use `find_distinguishing_model(env, a, b, ...)`
with the same options to obtain a `CountermodelResult` whose `Found` model makes
the two closed formulas differ. Evaluate both formulas to determine direction.
`NotFound` covers only the requested finite bounds and filters.

`nonvacuous_for=formula` further requires nonempty domains at all of that
formula's quantifiers and at least one true antecedent for each syntactic
implication occurrence, over all bindings of its enclosing quantifiers. It
inspects both branches regardless of evaluation short-circuiting; it does not
require the formula itself to be true. Different occurrences of a shared AST
node are checked independently. The inspection and antecedent evaluations share
the request's work budget. The condition is conservative: an impossible
antecedent disqualifies a candidate; there is no silent logical-feasibility
exemption. Such a request may return `NotFound` even when ordinary distinguishing
models exist. This legacy default is syntactic: `not dep(s) or rev(s)` is not an
`Implies` node, so its empty antecedent relation is not detected in this mode.

Set `semantic_nonvacuity=True` together with `nonvacuous_for=formula` to also
check clause guards semantically in each candidate model. Precisely:

- Retain every legacy quantifier-domain and implication-antecedent check.
- For each maximal tree of `Or` nodes beneath at least one enclosing `Forall`,
  flatten its disjuncts in order. Each disjunct of the form `Not(G)` contributes
  `G` to the guard. Non-negated disjuncts do not contribute. For example,
  `not dep(s) or rev(s)` has guard `dep(s)`; `not A or not B or C` has joint
  guard `A and B`, independent of left/right association or disjunct order.
- If there is at least one such negated disjunct, require **one assignment** of
  the occurrence's enclosing universal/existential binders on which **all** its
  guard bodies evaluate true simultaneously. Each occurrence is independent;
  individual guard satisfaction on different assignments is insufficient.
- Inspect all branches, even under negation or a short-circuiting connective.
  This conservative occurrence check does not require the whole formula, its
  consequent, or its enclosing conditions to be true. Witnesses may differ
  between occurrences; this is not a per-outer-assignment witness requirement.

Guard recognition is structural; guard **satisfaction** uses the evaluator and
shares the search work budget, including inspection. There is no arbitrary CNF
normalization, English interpretation, or invariance under every logically
equivalent rewrite. A disjunction with no negated disjunct, or with no enclosing
universal, adds no clause guard. An impossible joint guard rejects the model.
The result records `semantic_nonvacuity` and `nonvacuous_for_meaning_id` so that
filtered `NotFound` is not mistaken for unconstrained exhaustion.

```python
from ve import find_distinguishing_model

witness = find_distinguishing_model(
    env, faithful, candidate, min_domain_size=1, max_domain_size=2,
    nonvacuous_for=faithful, semantic_nonvacuity=True, max_evaluations=1_000_000,
)
if witness.status == "Found":
    assert evaluate(env, faithful, witness.model, trace=False).value != evaluate(
        env, candidate, witness.model, trace=False).value
```

`check_countermodel` is the independent trusted witness-checking entry point.
It checks every premise and the exact conclusion and binds the result to the
environment, model, ordered premise meaning IDs and conclusion meaning ID.
This supplies the argument layer's `gap` finding; a gap does not make the conclusion
false in reality. Neither search exhaustion nor finite satisfaction is positive
entailment evidence.

## Entailment evidence and trust boundary

`prove_entailment(env, premises, conclusion, max_steps=10000)` searches for a
closed signed semantic tableau and returns `Found`, `NotFound`, or `ResourceLimit`,
with a data-only `certificate` on success. `NotFound` is inconclusive. The search
is deliberately incomplete, has a recursion bound, and may exhaust resources
even on simple valid formulas. It has no authority to assert validity; generated
traces are replayed before `Found` is returned.

`check_entailment_certificate(env, premises, conclusion, certificate,
max_steps=10000)` is the separate trusted replay entry point. Its result has
`valid`, `status` (`Valid`, `InvalidCertificate`, or `ResourceLimit`), `steps`,
and `detail`. It accepts restricted JSON data only. It constructs the initial
branch from **the supplied expected formulas**, with every premise true and the
conclusion false. A certificate contains exactly `checker_version`,
`environment_id`, ordered `premise_meaning_ids`, `conclusion_meaning_id`, and
`trace`; bindings are checked before replay. No executable code, imports,
theorem names, solver unsat labels, or hidden axioms are accepted.

Trace nodes are `{"rule":"close"}` or
`{"rule":"expand","at":n,"children":[...]}`, with `parameter` additionally
specified for universal-style instantiation. The checker reconstructs every
child branch. The certificate cannot supply formulas or premises for a branch.
The rules are standard classical signed-tableau rules:

| Signed formula | Checked expansion |
|---|---|
| true/false negation | Reverse the body's sign |
| true conjunction, false disjunction, false implication | Both signed components on one branch |
| false conjunction, true disjunction, true implication | Both alternative branches must close |
| true existential or false universal | Fresh checker-generated parameter of the quantified sort |
| true universal or false existential | Instantiate with an already present parameter of that sort |

For implication the antecedent sign is reversed. Declared constants supply
initial parameters; constants are not assumed distinct. No parameter is added
merely because a sort is declared. A witness is introduced only by a signed
quantifier that requires an inhabitant, so empty sorts remain admissible.
Bindings are nearest-first and each branch retains dependent witnesses.
Closure checks true `false`, false `true`, a false equality whose terms coincide
after positive-equality union, or opposite relation atoms modulo those equality
classes. Well-typed inputs and sorted instantiation prevent cross-sort equality.
Fresh parameters may denote equal elements; freshness never implies inequality.

The small replay rules, equality closure, expected-input bindings, and input
validators are trusted Python. The search strategy is untrusted, although it
calls these same logical rule helpers to construct candidate traces. Replay
does not invoke search and reconstructs branch state independently of submitted
search output. The rest of the existing parser/evaluator/display trust boundary
still applies. This is **experimental Python tableau checking**, not Lean kernel
checking or a discharge of P9–P11. The draft Lean replay design in the specs is
not implemented by this path. No third-party solver or runtime dependency is
needed. A future verified checker must establish soundness of these rules and
their correspondence to the independent semantics; finite property tests cannot
replace that proof.

## Argument API and interchange

```python
from ve import check_argument, outstanding_obligations, predicate_use_panel
from ve.argument_fixtures import worked_examples

graphs = worked_examples()
result = check_argument(graphs["merged"])
assert result.findings["merged_review"] == ("follows",)
assert result.remaining_assumptions == ("operations_review", "security_policy")
print(result.to_json())
obligations = outstanding_obligations(graphs["merged"], result)
uses = predicate_use_panel(graphs["merged"], result)
```

The stable construction API is:

```python
Claim.create(env, name, source, candidate_ast=None, evidence_ids=())
Deduction(name, premises, conclusion, certificates=(), countermodels=())
ArgumentGraph(env, claims, deductions, root, evidence=(), target_scope="unspecified")
Evidence(evidence_id, claim_id, snapshot_id, passage, reviewer, target_scope,
         judgment="unassessed", kind="empirical")
check_argument(graph, search=True, max_proof_steps=10000, max_domain_size=1,
               max_models=1000, max_evaluations=100000)
```

Optional arguments to `Claim.create` and `check_argument` are keyword-only.
Sequences are ordered lists or tuples. The argument checker reparses each exact
source, requires one statement including final LF, checks source/AST agreement,
and checks every environment and claim identity. Duplicate aliases, missing
references, multiple deductions for one conclusion, cycles (including outside
the root component), stale evidence, and extra certificate assumptions fail.
Limits are 256 claims, 512 premise references, and a 16 MiB input package;
existing source, AST, model and JSON bounds also apply. Search and replay budgets
are per edge/direction; host cancellation propagates as a process interruption.

An edge certificate has the exact envelope
`{"edge_id": ..., "direction": "follows" | "refuted", "proof": ...}`.
Use `deduction_identity(graph, deduction)` for `edge_id`. That digest includes
the environment, deduction name, ordered premise aliases and exact claim IDs,
and conclusion alias and exact claim ID. Each claim ID binds environment,
exact-source ID, and single-formula meaning ID. The nested proof is separately
checked against the expected ASTs, targeting `Not(conclusion)` for `refuted`.
Binder renaming therefore invalidates an old envelope even when meanings match.
Changing premises or moving a bridge out of view cannot preserve a certificate.
Changing evidence invalidates the complete graph record, while an unchanged
conditional edge theorem can still be replayed against a new factual assessment.

`ArgumentGraph.to_dict()/to_json()` and `from_dict()/from_json()` define the
versioned `ve-argument-tableau@1` package. Required fields are `version`,
`environment`, `claims`, `deductions`, `root`, `evidence`, and `target_scope`;
unknown fields and duplicate JSON keys are rejected. Claims include their source,
indexed `ast`, name, three identity fields, `claim_id`, and `evidence_ids`.
Deductions contain `name`, `premises`, `conclusion`, `certificates`, and
`countermodels` (the ordinary finite-model wire format). Evidence includes the
constructor fields plus an `assessment_binding` digest of all those fields.
The binding must be retained on interchange; changing snapshot, passage,
reviewer, scope, or judgment requires a fresh reported assessment. A mutable URL
alone is rejected as a snapshot ID. Snapshot contents and reviewer authority are
**not authenticated or fact-checked**; these records expose reported support.

`check_argument` searches by default; `search=False` checks submitted artifacts
only. Its result exposes `findings` (edge name to tuple), `remaining_assumptions`
(root-reachable premise-leaf names), `unresolved_obligations` (uncertified
intermediate/root names), `composed`, `edges`, `errors`, and JSON output.
All findings are retained:

| Finding | Evidence |
|---|---|
| `follows` | Replayed proof of the exact conclusion under the displayed premises |
| `refuted` | Replayed proof of its negation under the same premises |
| `gap` | Separately validated model satisfying all premises and falsifying the conclusion |
| empty tuple, edge `status: unresolved` | No logical finding established |

The protocol uses `gap` for a countermodel; it reserves `refuted` for a proof of
negation. Proof search failure never produces either finding. Result statuses
are `Checked`, `Incomplete`, `InvalidInput`, `ResourceLimit`, and
`CheckerConflict`. Search exhaustion is retained in per-edge attempts, and
produces overall `ResourceLimit` when a required inference remains unsupported.
Exhausting the countermodel/negative search does not revoke a valid positive
proof. Submitted invalid artifacts withhold successful composition even when
other evidence was valid. A `follows`/`gap` conflict retains both artifacts and
withholds composition. `follows`/`refuted` records contradictory premises; a
validated model satisfying those premises instead triggers `CheckerConflict`.

Composition uses the acyclic graph's checked positive edges and lists **every**
root-reachable undischarged leaf, with full commitments in the composition record.
Shared leaves appear once; unused leaves remain outside this conditional theorem.
Unsupported intermediate nodes remain separate obligations, never promoted to
leaves. An assumption equal to the root stays an assumption. Composition does
not certify the truth, consistency, or adequacy of leaves and does not approve
the result. The checking record retains proof/model artifacts, graph identity,
and a checker-build digest over the relevant Python modules and runtime version;
its `record_id` hashes the full diagnostic JSON record. Diagnostic JSON may use
null and is separate from the restricted semantic-input encoding.

`outstanding_obligations(graph, result)` returns root interpretation status,
all remaining assumptions with reported assessments and cited snapshots,
literal target-scope agreement, unresolved deductions, and unassessed approval.
Accepted evidence never removes a logical assumption. Scope string agreement
is display metadata, not proof that grounding is adequate.
`predicate_use_panel(graph, result=None)` returns each predicate's declared
description/signature and every premise that uses it, including intermediate
premises, their cited evidence IDs and records, and root relevance. Both reject
a supplied result from a different package. These are JSON-ready E5 display
data; neither is an intent-recovery or factual-attestation mechanism.

`ve.argument_fixtures.worked_examples()` executes the separated-vocabulary
countermodel, explicit-bridge repair, and merged-vocabulary valid proof.
`UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python -m ve.argument_fixtures`
emits all three checking records and E5 displays as JSON.
`infinite_only_example()` encodes the language spec's satisfiable premises with
no finite model; bounded model absence cannot certify `false`. Since its root
is `false`, the independent `refuted` direction can prove `not(false)` even
without those premises. The merged example intentionally certifies the formal
substitution while exposing incompatible operations/security evidence scopes.

## CLI and operational outcomes

`python -m ve --help` lists `parse`, `format`, `render`, `evaluate`, `check`,
`import-fol`, and `countermodel`. Every command takes `--env`; source `-` reads
stdin where applicable. Text inputs are read as bytes so newline conversion
cannot conceal malformed input. The examples in the README are executable.

`parse` emits an acceptance record; `format` emits canonical source. `check`
optionally takes `--model` and `--candidate-ast`; `evaluate` requires a model.
Records explicitly retain `assurance: experimental`, `intent: unconfirmed`, and
`proof: not_checked`. Exit 0 means successful output or a found countermodel;
exit 1 means `Violated`; exit 2 means `InvalidInput`; exit 3 means
bounded/filtered `NotFound`; exit 4 means `ResourceLimit` (both returned budget
outcomes and raised resource exceptions). JSON statuses preserve these distinctions.
`evaluate`, `check`, and `countermodel` accept `--max-evaluations`.
`evaluate` and `check` accept `--no-trace`. Search always omits traces and accepts
`--min-domain-size`, `--nonempty-domains`, and `--nonvacuous-for FILE` (one strict
VE statement), plus `--semantic-nonvacuity` to enable the clause-guard check
(requires `--nonvacuous-for`). `render` and `import-fol` accept all four named
views as plain text; legacy `--view natural` emits the identity-bound JSON view record.

The v0 envelope bounds source bytes, JSON package size, AST depth/nodes,
vocabulary size, model entities/tuples, explanatory trace size, and formula-node evaluations. JSON
nesting additionally has a 256-level decoding guard. Search is separately
bounded; search also stops if a candidate domain vector requires more than
100,000 possible **used-predicate** relation atoms. Host cancellation remains
a process interruption, not a logical finding.

## Trust and tests

Trusted for the experimental acceptance/evaluation path: Python and its standard
library/runtime; strict byte and JSON decoding; environment/model validators;
parser and name resolver; AST type/scope checker; finite evaluator; canonical
serializer, SHA-256 binding and acceptance-record code; printer and displayed
rendering fidelity. FOL adapters additionally belong to the trust boundary when
dataset claims are about their source syntax. The CLI/file-I/O boundary is
trusted to supply and display the checked objects.

Search has no authority to assert validity: found models are checked separately.
There are no external solver or model calls in the core, no Lean proof replay, no
hidden domain nonemptiness or unique-name axioms, and no empirical evidence
verification. All metatheory obligations P1–P11 remain pending. Property tests
are empirical evidence, not proofs of grammar uniqueness or correspondence.

The tests include spec examples, malformed packages, scope/type errors, source
substitution and environment changes, all logical constructors, vacuity,
constant aliasing, countermodel subset enumeration, operational limits, and CLI
exit codes. Hypothesis tests compare parser/printer and wire round trips and a
separately written finite denotation for generated formulas. This is a development
suite, not the independently frozen 240-case corpus proposed in the roadmap,
and it is not evidence for any oversight or readability benefit.

Original core validation on September 21, 2026: `uv run --frozen python -m pytest -q` passed
90 tests; `uv build` produced both source and wheel distributions; importing the
built wheel in isolated Python and checking the worked inventory succeeded.
In the restricted worker environment these `uv` commands used
`UV_CACHE_DIR=/private/tmp/ve-uv-cache`. The ordinary `uv` cache is outside that
worker's writable paths; direct `.venv/bin/python -m pytest` also passed.

The rendering/search follow-up adds seeded cross-view injectivity and binder
checks, adversarial distinguishing pairs, verbalisation collision/fallback
checks, FOL-name rejection/export round trips, constrained model search,
trace-free evaluation and request-budget tests. Reproduce in the views worktree
with `UV_CACHE_DIR=/private/tmp/ve-uv-cache-views uv run --frozen python -m pytest -q`.

Views follow-up validation on September 21, 2026: the command above passed
158 tests. `UV_CACHE_DIR=/private/tmp/ve-uv-cache-views uv build --out-dir
/private/tmp/ve-views-dist` built the source and wheel distributions. An isolated
Python import from that wheel passed four-view rendering, no-trace inventory
checking, distinguishing-model search, and named-FOL export/import smoke checks.
The no-trace suite includes successful evaluation at exactly 1,000,000 nodes;
non-vacuity inspection itself is also charged to the search request budget.
The argument extension adds replay/forgery, empty-sort, aliasing/equality,
many-sort, dependent-witness, assumption-composition, stale-commitment,
inconsistent-premise, injected-checker-conflict, E5 display, and executable
fixture tests. Hypothesis generates small formulas and compares every certified
entailment to an independently written denotation over exhaustive finite models
through a small bound. These tests can expose implementation errors, but do not
establish soundness for arbitrary structures or satisfy the pending metatheory.

Argument-layer validation on September 21, 2026:
`UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python -m pytest -q`
passed **161 tests**. `UV_CACHE_DIR=/private/tmp/ve-uv-cache uv build` produced
both distributions. The executable fixtures returned `gap` for separated
vocabulary and `follows` for both explicit-bridge and merged-vocabulary cases.
