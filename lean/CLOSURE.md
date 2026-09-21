# closure@0 Lean reference

The new language is `VE.Closure.Formula`. The existing `VE.Formula` and its
certificate, graph, parser and evaluator theorems are unchanged. `Formula.reach`
accepts `Kind.plus | star` and `Edge.named r | body s formula`; the two recursive
edge alternatives lower injectively to `reachNamed` and `reachBody` constructors.
The wire representation has the design's single `reach` tag and two edge tags.

The new envelope is exactly `language: ve.core@0.1`,
`profiles: ["closure@0", "relational-fol@0"]`,
`spec_revision: ve-v0.1-closure-2026-09-21`, and the unchanged `vocabulary`.
The bridge shares the v0 vocabulary and finite-model validators. New profiles,
unknown revisions, and the singular v0 `profile` field in this envelope fail.

Exact headline theorem statements in plain words:

- `Path.least`: a positive finite R-path from a to c exists if and only if every
  relation X containing R and closed under prepending an R-edge contains (a,c).
  `Path.unfold` proves the corresponding fixed-point equation. These quantify
  over arbitrary carriers, including infinite ones.
- `star_least`: a equals c or there is a positive finite R-path from a to c if
  and only if every reflexive relation closed under prepending an R-edge
  contains (a,c). Thus star is the least fixed point of Id union R;X.
- `warshall_iff_path`: for every finite edge table and endpoints a,b, the
  iteratively closed table contains (a,b) exactly when a positive finite path
  through the original table exists. Repeated edges and cycles are permitted.
- `eval_iff_denote`: for every finite model over any decidable-equality carrier,
  every valuation and every raw extended formula, evaluation returns true
  exactly when that formula's denotation in the induced structure holds.
  No inhabitation, acyclicity, typing, or model-validity premise is needed.
- `check_iff_wellFormed`: for every environment, sort context and extended
  formula, the executable checker returns true exactly when the independent
  typing predicate holds. Body locals have destination at 0 and source at 1;
  endpoints use the outer context.
- `conservativity`: for every old formula, structure and valuation, its embedded
  new denotation is equivalent to its original v0 denotation.
  `conservativity_without_reach` states this for every extended formula whose
  structural Reach-free erasure succeeds.
- `countermodel_sound`: if a valid finite model passes the extended countermodel
  check, the requested entailment over all admissible structures is false.
- `Surface.parseRaw_print_named`: for either closure kind, a well-typed Named
  atom, a lexically valid environment, canonical outer binder scope and matching
  sort context, parsing its printed form with any positive fuel and any suffix
  returns that same atom and untouched suffix.
- `Surface.parse_print_named`: for a lexically valid environment and any closed,
  well-typed Named closure atom, public parsing of its printed singleton document
  returns precisely that singleton document, including period/newline framing.
- `Surface.print_injective_named`: in a lexically valid environment, any two
  closed well-typed Named closure atoms whose printed documents are equal are
  the same AST.

Both Named and Body strict syntax are executable, including nested bodies and
fixed outer parameters. The **new round-trip proof is currently for Named atoms**;
full extended-document round trip, Body round trip, and general extended printer
injectivity are not proved. Named singleton documents and Named-atom printer
injectivity are covered. The old full v0 round-trip theorems still build.

The reference uses finite materialized edge lists and deduplication at each
Warshall pivot. Its correctness is proved; an O(n^3) matrix implementation and
complexity bound are not. Body relations are evaluated for all domain pairs
per outer valuation. The reference bridge has no evaluation work-budget theorem.

The Lean certificate checker contains no Reach unfolding rules. Its JSON adapter explicitly
rejects every v0.1 environment with a profile-gate message. The path unfolding
lemma alone is not a soundness extension of tableau replay: substitution,
branch-preservation and closure certificate theorems remain outstanding.
The integration merge retains its single v0 version-2 exact complementary-formula
close proof, `VE.Tableau.complementary_sound`: identical formulas with identical
parameter bindings and opposite signs cannot both hold. This is equivalent in
generality to the removed `compoundClosed_sound` proof. All four `Tableau*.lean`
files match integration: version 1 retains literal-only closes; version 2 also
allows complementary compounds. Both retain the 124-expansion limit and the exact
`checkCertificate_sound` statement. Closure environments are rejected even when
their formulas contain no Reach or their certificates claim a v0 checker version.

JSON correspondence, IO/compiler/runtime correctness and Python refinement
remain outside the proofs, as in v0. No project axioms or proof placeholders
are introduced; audit.py covers every new named theorem.
