# Assurance

## What the Lean results establish

The theorem statements below concern the named Lean reference definitions.
They do not transfer automatically to Python, Rust, or a user-facing display.
We report semantic scope rather than a count of helper lemmas.

| Reference result | Plain-language statement and scope |
|---|---|
| `eval_iff_denote` | Finite Boolean evaluation agrees with Tarski denotation in the model's embedded structure. The generic lemma covers raw formulas; accepted VE claims additionally pass closure and typing checks. |
| `Surface.parse_print`; `normalize_idempotent` | For every closed typed base-profile document under the declaration-name conditions, the actual reference printer and parser round-trip; normalization is idempotent. |
| `Surface.print_injective` | Equal canonical strings imply equal indexed documents under those same name conditions. This is not independent grammar unambiguity. |
| `Tableau.checkCertificate_sound` | Boolean acceptance entails the exact supplied conclusion from the exact ordered premises over every admissible common-carrier structure in the chosen universe, including empty sorts and infinite structures. No assumed certificate-soundness premise remains. |
| `Graph.check_sound`; `check_entails` | Successful Lean tableau-backed checking of a topologically ordered named graph establishes acyclicity, unique names, exact claim provenance, and root entailment from its reported assumptions. |
| `Bridge.decodeModel_valid`; `CountermodelQuery.refutes_sound` | Successful model decoding supplies admissibility; an accepted typed finite countermodel refutes the exact universe-zero consequence relation. |

<!-- src: lean/METATHEORY.md; lean/VE/TableauChecker.lean;
lean/VE/ClaimGraph.lean; paper/sources/review-lean.md. -->

The Lean graph unfolds ordered assumption lists with repetitions. Python displays
shared leaves once. Their correspondence is unproved. Likewise, parser/printer
round trips can preserve a shared grammar error: the independent grammar
uniqueness and correspondence obligations remain open. No separate
source-to-generated-proposition theorem or production refinement theorem is
claimed.

For closure, Lean proves finite-path and least-fixed-point characterizations,
finite evaluator correctness, typing, reach-free conservativity, and conditional
countermodel soundness. The new surface proofs cover Named closure atoms,
including singleton-document round trip and injectivity. They do not cover
arbitrary extended documents or Body round trips. Closure substitution and
tableau branch-preservation proofs remain open at the pinned implementation base.
<!-- src: lean/CLOSURE.md; docs/spec/closure-implementation.md. -->

## Trust base

The metatheory assumes the formal definitions express the intended specification
and trusts Lean's logic and kernel. The project's axiom audit permits only
`propext`, `Classical.choice`, and `Quot.sound`. Executable acceptance additionally
trusts the compiler, runtime, standard library, UTF-8/JSON and AST decoding,
certificate decoding, canonical serialization and hash binding, file IO, and
faithful display. Decoder-output admissibility is proved; full correspondence
between submitted bytes and the wire specification is not.

Lean uses a common carrier with possibly overlapping sort domains. The documented
sort-tagging argument relating typed claims to independent disjoint-carrier
semantics is not mechanized. It is an external interpretation assumption, not a
hidden axiom in the proved theorems. JSON certificate and countermodel statements
pin the consequence relation to `Entails.{0}`; the generic certificate theorem is
universe-polymorphic. No result proves intended meaning, empirical premises,
proof-search completeness, hostile-input isolation, or correctness of a compiled
binary. The system's overall assurance label remains `experimental`.
<!-- src: lean/README.md; lean/METATHEORY.md; lean/audit.py. -->

## Conformance and Rust performance

The committed corpora provide the following development evidence. Overlapping
fixtures are not independent samples. Python generates the semantic golden
values; executable agreement is differential evidence, not a refinement proof.

<!-- INCLUDE generated/conformance-table.md -->

The certificate corpus includes schema-generated valid queries, unconditioned
queries, and regressions. All search attempts remain recorded, including failed
searches and resource outcomes. Many valid certificates share schemas, and many
forgeries mutate the same simple base. Acceptance and rejection counts cannot
be read as an error rate on independently sampled adversarial certificates.
<!-- src: conformance/certificates-report.json; conformance/certificates.py;
paper/sources/review-lean.md. -->

Rust is a separately implemented and differentially tested base-profile core.
Safe Rust restrictions do not prove logical correctness. This checkout does not
supply Rust closure support, certificate replay, or claim-graph composition.
The honest performance summary is about thirty times faster on the larger
measured finite-evaluation kernels, with the specific measurements below.
<!-- src: docs/rust.md; rust/benchmark-results.json; docs/spec/closure-implementation.md. -->

<!-- INCLUDE generated/rust-table.md -->

The benchmark evaluates already-validated inputs, excludes startup and JSON
setup, and disables traces in both implementations. Its nested universal workload
forces relation visits. Public API ratios additionally reflect Python's repeated
validation and hashing, so they are not kernel speedups. The run was serial on a
shared, loaded machine; the recorded samples are workload-specific observations,
not isolated estimates of general throughput or programming-language advantage.
<!-- src: rust/benchmark.py; rust/benchmark-results.json; docs/rust.md. -->
