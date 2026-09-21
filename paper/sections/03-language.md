# Language, checking, and assurance engineering

VE's base profile is function-free, many-sorted first-order logic with equality,
unary/binary predicates, constants, Boolean connectives, and quantifiers.
Sorts may be empty unless constants or assumptions require inhabitants.
Typed, closed formulas have classical semantics. Vocabulary declarations carry
ordered argument signatures and human descriptions; descriptions are trusted
assertions, not semantic proofs. Canonical identities bind the environment,
formula, and finite interpretation, under a hash-collision assumption. An
identity establishes neither truth nor equivalence to an informal source.

Five deterministic displays share the same logical candidate: symbolic FOL
(S), keyword FOL (K), strict VE (V), explicit natural VE (N), and fluent VE (F).
Only strict VE is accepted as source syntax. The other views are displays;
fluent rendering contracts selected patterns and falls back when a pattern is
unavailable. A compact common legend exposes predicate identity and argument
order. Lexical lint checks reject several dangerous wording patterns, but
cannot prove that a description is honest.

For example, the requirement that each deployed service has some owner permits
different owners for different services:

$$\forall s:\mathrm{service},\quad \mathrm{deployed}(s)\to
\exists p:\mathrm{person},\quad \mathrm{owns}(p,s).$$

The generated fluent view says, "for every service S that is deployed, there is
a person P such that P owns S." Moving the existential before the universal
would require one owner for all deployed services. The renderer exposes a
quantifier dependency; whether a reader notices it is an empirical question.
The complete five-view example is retained in the artifact.

Finite evaluation checks a formula in a fully specified interpretation. A
countermodel to a submitted consequence makes every premise true and the
conclusion false. Bounded search can propose such a model or a tableau
certificate, but search failure is UNKNOWN, never evidence of validity or
non-entailment. Replay checks the proposed object against exact formulas.
Claim graphs preserve the assumptions needed by the root rather than hiding
them behind a "proved" badge. Empirical truth and applicability of those
assumptions remain separate obligations.

The opt-in closure profile adds positive and reflexive-transitive finite-path
relations, including named edges and filtered Body edges with explicit local
scope. It recomputes reachability from base edges; an uninterpreted predicate
named `reachable` is not an implementation. The language still lacks interpreted
arithmetic, unrestricted counting, regex, probability, causality, obligations,
beliefs, and general temporal operators. Reifying an event or tuple may expose
its participants without supplying those missing meanings.

## Exact assurance scope

The Lean work supplies engineering assurance about the definitions below.
It is not a proof of the implemented oversight workflow or its novelty.

| Reference component | What is established | Boundary |
|---|---|---|
| `eval_iff_denote` | Finite Boolean evaluation agrees with Tarski denotation in the embedded structure | Accepted VE claims additionally require typing and closure checks |
| `Surface.parse_print`, `print_injective` | Canonical strict printer/parser round trip; equal printed strings imply equal indexed documents, under declaration-name conditions | No independent grammar-unambiguity theorem; no property of the fluent renderer |
| `Tableau.checkCertificate_sound` | Acceptance entails the exact conclusion from the exact ordered premises over admissible common-carrier structures, including empty sorts and infinite structures | Soundness, not search completeness; generic theorem is universe-polymorphic |
| `Graph.check_sound`, `check_entails` | Lean base-profile graph checking preserves provenance and establishes root entailment from reported assumptions | No refinement of Python's graph representation or extended closure graph theorem |
| `Bridge.decodeModel_valid`, `CountermodelQuery.refutes_sound` | Decoded models are admissible; an accepted typed finite countermodel refutes the exact universe-zero consequence | Full byte/wire correspondence is not proved |
| Closure checker and evaluator | Finite-path semantics, conservativity, evaluator correctness, and extended certificate soundness | Named singleton surface round trip only; no arbitrary Body/document round trip, completeness, or general induction |

Closure rules cover edge inclusion, mixed positive/reflexive path composition,
first/last-edge existence, and Named-to-Body conversion. The original base
certificate theorem remains unchanged; a closure corollary follows by
conservativity. These are scoped reference results, not a completeness claim
for first-order logic with reachability.

Lean's logic and kernel and the correctness of the theorem statements remain
trusted. The axiom audit permits `propext`, `Classical.choice`, and `Quot.sound`.
Executable use additionally trusts compilation, runtime, decoding, serialization,
IO, hashing, and display. Lean's common carrier allows overlapping sort domains;
the documented sort-tagging argument to independent disjoint domains is not
mechanized. Python graph display deduplicates assumptions that Lean records as
ordered lists, and that correspondence is unproved. Natural/fluent rendering,
lexical linting, Python replay, and Rust execution are outside the reference
soundness theorems. E4 artifacts were replayed in Python, not Lean.

Differential certificate and evaluator corpora are useful integration evidence,
not production-refinement proofs. In particular, successful replay of generated
fixtures cannot establish that source requirements were faithfully formalized.
Implementation benchmarks and the full conformance inventory are in the
appendices; the assurance label remains experimental.
<!-- src: lean/METATHEORY.md; lean/CLOSURE.md; lean/README.md;
docs/rendering-views.md; docs/implementation.md; paper/sources/review-lean.md. -->
