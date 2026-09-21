# The VE language

## Syntax, environments, and semantics

The base profile, `relational-fol@0`, is many-sorted, function-free first-order
logic with equality. An environment declares sorts, constants, unary predicates,
and binary predicates with ordered argument sorts. Each declaration has a
human-readable description. Profiles and specification revisions are explicit.
Unknown versions fail. Descriptions do not define predicate extensions, create
axioms, or establish facts.
<!-- src: docs/spec/v0-language.md. -->

Terms are bound variables or declared constants, written with `@`. Formulas
contain truth, falsity, predicate application, same-sort equality, negation,
conjunction, inclusive disjunction, material implication, and universal or
existential quantification. Strict VE has explicit grouping and binders. Each
statement ends in a period and line feed. It rejects implicit precedence,
undeclared symbols, free variables, shadowing, and ill-typed terms. The semantic
AST stores nearest-first de Bruijn indices; author-chosen names and source spans
are diagnostic metadata. A document is a nonempty ordered list of closed formulas.

For an environment $E$, an admissible structure $S$ gives each sort a domain,
each constant a correctly sorted element, and each predicate an appropriately
typed relation. Domains may be infinite or empty. A declared constant requires
an inhabitant, but different constants may denote the same element. Equality is
identity within a sort. The interpretation is classical Tarski semantics:

$$
\begin{aligned}
(S,\rho)\models\forall x:s.\,A
  &\iff \forall d\in D_s,\ (S,d::\rho)\models A,\\
(S,\rho)\models\exists x:s.\,A
  &\iff \exists d\in D_s,\ (S,d::\rho)\models A.
\end{aligned}
$$

An empty-sort universal is true; an empty-sort existential is false. A false
antecedent makes a material implication true. Existence and nonemptiness must be
stated when required. For closed premises $\Delta$ and conclusion $C$,

$$
E,\Delta\models C\quad\iff\quad
\forall\text{ admissible }S,\
\bigl(\forall A\in\Delta,\ S\models A\bigr)\Rightarrow S\models C.
$$

The finite-model interface uses sort-qualified local identifiers. The Lean
reference instead permits overlapping domains within a common carrier. The
transfer between these presentations for typed formulas is explained but not
proved in Lean; Section 5 states the resulting interpretation boundary.
<!-- src: docs/spec/v0-language.md; lean/README.md, carrier interpretation assumption. -->

## Canonical form and identities

Canonical printing assigns fresh names in binder preorder and resets at each
statement. It preserves constructor order and association. It does not sort
conjuncts, eliminate double negations, recognize synonyms, or compute a logical
equivalence class. Alpha-renaming preserves the indexed AST; a logically
equivalent rewrite can change it.

Domain-separated SHA-256 identifiers bind exact source bytes, the full
environment, the AST under that environment, and normalized finite models.
Descriptions and optional display metadata contribute to the environment
identity. Restricted canonical JSON fixes serialization; duplicate keys and
invalid values are rejected. Hashes index artifacts under a collision-resistance
assumption. They establish neither semantic equivalence nor factual truth.
Changes to evidence snapshots or review scope can invalidate an evidence
assessment without invalidating the unchanged conditional theorem.
<!-- src: docs/spec/v0-language.md, identity preimages; docs/implementation.md,
argument interchange. SHA-256 is the algorithm name, not an experimental count. -->

## Deterministic views and a worked example

The views range from symbolic FOL through keyword FOL and strict VE to explicit
natural and contracted fluent VE. The first four share a structural traversal.
The fluent renderer contracts specified patterns and has explicit fallback.
Only strict VE is accepted as source text. The others are read-only displays.
<!-- src: docs/rendering-views.md (five views, first four shared traversal). -->

Consider the requirement that every deployed service has an owner. The owner may
depend on the service. The following outputs are generated from one committed
AST and environment, not manually paraphrased. Line wrapping below is layout;
the generated artifact also preserves the exact strings.

<!-- INCLUDE generated/worked-example.md -->

A scenario with distinct deployed services and different sole owners satisfies
this formula but can falsify the alternative with an existential owner outside
the universal. The renderer makes the dependency visible; it does not guarantee
that a reader notices it. The shared legend records each raw identifier,
description, ordered signature, selected wording and fallback, renderer naming
policy, and lint diagnostics. The table below summarizes this example;
the complete API legend is saved with its generated strings.

The renderer now also provides `render_vocabulary(..., style="compact")`.
It retains vocabulary identity, ordered signatures, descriptions, selected
wording and lint information in a shorter display. E1 uses this compact legend,
byte-identical across all five views. Its earlier roughly 4,000-character JSON
legend (the final compact prompt is about 3,900 characters in total)
swamped the statement and moved every tested Qwen judge outside the
primary gate. Compact display is therefore part of the frozen prompt, not a
cosmetic implementation detail.
<!-- src: docs/rendering-views.md; paper/sources/e1-prereg-frozen.md;
paper/sources/process-log-v1.md. -->

<!-- INCLUDE generated/worked-legend.md -->

Natural and fluent templates are trusted vocabulary assertions. The linter
rejects many dangerous forms: reordered or repeated arguments, inserted logical
words, passive/converse patterns, lexical collisions, and unchecked negative
phrases. Rejected templates fall back to explicit atoms. These checks are
heuristics. A collision-free antonym or misleading sort noun can still pass.
The legend exposes raw identity and argument order in every cell; it cannot
ensure truthful vocabulary or attentive review. E1 freezes that
vocabulary before scored judging. Vocabulary-authored attacks need their own evaluation.
<!-- src: docs/rendering-views.md; paper/sources/review-views.md. -->

## The closure profile and exclusions

The opt-in `closure@0` profile adds positive and reflexive-transitive reachability.
Named edges refer to a homogeneous binary relation. Body edges define a relation
with source and destination locals while keeping outer parameters fixed. Strict
syntax includes `tc[parent](a, b)` and `rtc[parent](a, b)`. Positive closure means
a finite path of positive length. Reflexive closure also allows a zero-length
path. A cycle can make positive reachability hold from an element to itself.
<!-- src: docs/spec/closure-implementation.md; lean/CLOSURE.md. -->

Closure is interpreted by least finite-path relations even on infinite
structures. Evaluation recomputes closure from base edges; a supplied
`reachable` relation is not a substitute. Filtered Body edges can express paths
that exclude edges into a fixed outer endpoint. Direction, path kind, local
scope, and edge syntax remain explicit in the views. The old profile retains
its original identities and meaning; there is no silent migration.

The integer `order@0` profile remains a design proposal. Base VE has no
interpreted arithmetic, unrestricted counting, regex, functions, higher-order
quantification, probability, causality, obligation, belief, or general temporal
operators. Some bounded statements admit explicit relational encodings, with
adapter obligations. Giving a predicate the name of an unsupported computation
does not implement that computation. The motivating research-level mathematical
statements are outside this prototype's language.
<!-- src: docs/spec/v0.1-profiles.md; docs/spec/v0.1-coverage.md; FUTURE.md. -->
