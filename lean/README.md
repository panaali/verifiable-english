# Lean 4 reference semantics for VE v0

This project uses Lean **4.24.0**, core Lean and `Std`, with no Mathlib or external
Lake dependencies. It formalizes the full function-free relational syntax and
Tarski semantics, proves finite evaluator equivalence (P6), semantic assumption
composition (P10), and finite countermodel soundness (P11). P4/P5 are proved for the full v0 syntax under the spec's declaration-name
restrictions, including arbitrarily many preorder-named binders and statements. These results do not
upgrade the complete Python acceptance path from `experimental`.

From this directory:

```sh
lake build
python3 audit.py
lake exe ve_conformance ../conformance/evaluation.json
```

From the repository root:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python -m pytest -q
python3 conformance/generate.py
```

`lake build` builds the semantic library, all proofs, direct executable regression
checks, and the JSON executable. `audit.py` checks that every named theorem has a
`#print axioms` entry, reruns those audits, and rejects any transitive dependency
outside `propext`, `Classical.choice`, and `Quot.sound`. All named theorems in the current [audit](axioms.txt) pass;
there are no `sorry`, new axioms, unsafe declarations, or native-evaluation
proofs. The source audit additionally prohibits those escape hatches. The
upstream toolchain and its standard logical dependencies remain trusted.

## Representations and scope

* `VE/Syntax.lean`: raw indexed `Term` and `Formula`, finite declared sort list,
  unary/binary predicate signatures, constant sorts, extrinsic well-formedness,
  executable type/scope checker, and nonempty closed typed `Document`.
* `VE/Semantics.lean`: a common carrier `Type u` with a domain predicate for each
  sort; constants and relations must satisfy `Structure.Admissible`. This is the
  usual extrinsic presentation of many-sorted semantics. Arbitrary separate
  carriers can be represented by their tagged union. Empty domains are allowed;
  constants inhabit their declared domains; constants need not be distinct.
  Cross-sort equality is rejected by typing. No carrier is assumed finite or
  inhabited. `Entails.{u}` ranges over **all admissible structures in universe
  u**, not just supplied inventories. Statements are uniform in that universe.
* `VE/Finite.lean`: finite domain lists and relation extensions, their embedding
  into `Structure`, and a structurally recursive Boolean evaluator. An infinite
  ambient ID type is permitted; quantifiers use only the enumerated domain.
  Evaluation and denotation agree even on raw formulas. Semantic claims use
  well-formed formulas, valid environments, and admissible structures. Invalid
  raw terms produce false atoms; `term_defined` excludes them on typed inputs.
* `VE/Consequence.lean`: finite acyclic proof trees whose steps carry actual
  entailment proofs, cut/composition, and finite countermodel soundness.
* `VE/ClaimGraph.lean`: executable named claim-graph checking, with explicit leaf
  nodes, ordered premise references and a checked topological order. Under the
  abstract sound-certificate predicate, acceptance proves acyclicity, unique
  aliases, exact root identity, typing, named leaf provenance, exact ordered
  leaf unfolding (including duplicates), and entailment of the root from those
  leaves. `VE/GraphChecks.lean` exercises positive/negative cases with a small
  proved-sound test certificate language. No Python graph/replay refinement,
  graph wire decoder, cryptographic identity layer or proof-artifact replay is
  proved.
* `VE/Surface.lean`: canonical preorder binder naming and a total strict parser
  for all constructors, with name-to-index resolution. Parser recursion decreases
  explicit fuel; the public parser supplies input length plus one. Full-language
  printer fuel adequacy is proved in `VE/RoundTrip.lean`.
  Reference identifier lexing is unbudgeted; the bridge retains its 64-byte
  declaration/local-ID/source-identifier runtime limit. Whitespace is literal, scopes
  do not shadow, statements end in period+LF, and typing is checked after parsing.
  Its failure result is `none`, not a source-location diagnostic.
* `VE/SurfaceProofs.lean`: P4/P5 for any nonempty document of arbitrarily nested
  **`true`, `false`, `not`, `and`, `or`, and `implies`**, with no terms, predicates,
  equality or quantifiers. This is an exact syntactic round trip through the
  actual full String printer and parser, including punctuation and final LFs.
  It preserves syntax, not merely equivalent truth values.
* `VE/LexicalProofs.lean` and `VE/RoundTrip.lean`: full-language P4/P5, decimal
  binder-name injectivity, fresh scope allocation, term lookup, lexical boundary
  preservation and input-length fuel adequacy. `parse_wellFormed` proves that all
  accepted documents are nonempty, closed and typed. There is still no independent
  grammar relation or proof of grammar P1/P2/P3.
* `VE/ParserContracts.lean`: accepted-text normalization, canonical reparse,
  printer injectivity and uniqueness of canonical representations. Equal normal
  forms of accepted texts are equivalent to exact indexed AST equality. These
  results do not imply the contract's independent-grammar P1.
* `VE/EnvironmentProofs.lean`: the executable finite vocabulary name validator
  implies precisely the declaration-name premise used by P4/P5. The entire JSON
  decoder and semantic environment/model validators remain unproved.
* `VE/Json.lean` and `VE/Bridge.lean`: executable, unproved restricted JSON decoder
  and validators. Model entities are `(sort, local_id)` pairs. The bridge invokes
  the very `Formula.eval`/`Document.eval` covered by P6, not a separate evaluator.
  A decoded document carries a proof of well-formedness from the proved checker.
  Environment validation and model admissibility are **tested, not proved**.

The bridge reads a case or array of cases from a path or stdin. A case contains
`id`, `environment`, `model`, and indexed document `ast`; optional `source` must
parse to that AST. Every case also exercises canonical printing/parsing. It
returns `id`, `status`, `values`, whole-document `value`, and `canonical`.
`expected` in fixtures is ignored. Exit 0 is successful evaluation (including
false), 1 is case rejection, and 2 is JSON or invocation failure. See
[`../conformance/README.md`](../conformance/README.md) for the shared corpus.

The decoder rejects duplicate keys before map insertion, invalid surrogate
escapes, null, fractions/exponents, out-of-range integers, invalid names,
unsupported versions, missing fields, duplicate inventory entries, wrong arity,
dangling/wrong-sort entities and ill-typed/free AST indices. It implements
formula depth/node, vocabulary, domain, tuple, and overall input-byte limits.
It does not implement Python's evaluation-work or trace budgets, source-size
budget, diagnostics, explanations, JCS hashes or assurance records. Its 16 MiB
input cap applies to the entire batch envelope. It is a conformance tool, not
an adversarial-input service, proof-certificate worker, or replacement Python CLI.

The new full-language theorem inventory and precise lexical conditions are in
[METATHEORY.md](METATHEORY.md). The table below records the original milestone.

## Original theorem inventory in plain words

All variables below are universally quantified unless the statement explicitly
says otherwise. “Finite model” in P6 may be any finite-list data; admissibility is
an explicit additional premise in P11. `depth` counts connective levels above
leaves. All surface-fragment statements refer to `Propositional` as defined above.

| Theorem | Exact statement in plain words |
|---|---|
| `VE.term_defined` | In an admissible structure, if a valuation is typed for a context and a term's inferred sort is `s`, the term denotes some element of domain `s`. |
| `VE.typed_empty` | The empty valuation is typed for the empty context in every structure. |
| `VE.typed_cons` | If a valuation is typed for a context and an element belongs to sort `s`, prepending that element and `s` preserves valuation typing. |
| `VE.check_iff_wellFormed` | For every environment, context and raw formula, the executable checker returns true exactly when the independent recursive well-formedness predicate holds. |
| `VE.eval_iff_denote` | For every finite model over any type with decidable equality, valuation and raw formula, evaluation returns true exactly when Tarski denotation in the model's embedded structure holds. |
| `VE.eval_false_iff_not_denote` | Under the same parameters, evaluation returns false exactly when that denotation does not hold. |
| `VE.document_eval_iff_denote` | For every typed nonempty closed document and finite model with decidable entity equality, document evaluation returns true exactly when every statement denotes true in the embedded structure at the empty valuation. |
| `VE.composition_sound` | For every `Derivation E leaves root`, the root is entailed by its computed undischarged leaf list over all admissible structures in the derivation's universe. Each step already carries the exact premise-to-conclusion entailment proof; leaves are concatenated without removal or deduplication. |
| `VE.entails_cut` | If premises entail a conclusion and every premise is itself entailed by a fixed leaf list, then that leaf list entails the conclusion, in the same environment and universe. |
| `VE.countermodelCheck_iff` | For any finite model with decidable entity equality, premise list and conclusion, the Boolean check returns true exactly when every premise denotes true and the conclusion does not denote true in its embedded structure. |
| `VE.countermodel_sound` | If that finite model is admissible for the environment and the Boolean countermodel check returns true, then the premises do not entail the conclusion over all admissible structures in that universe. |
| `VE.no_certificate_countermodel_conflict` | If a finite model is admissible and the premises entail the conclusion, the countermodel check on those same premises and conclusion returns false. |
| `VE.Surface.propositional_printAux` | Printing an embedded fragment formula under any binder-name stack and counter emits its fragment character encoding and leaves the counter unchanged. |
| `VE.Surface.propositional_check` | Every embedded fragment formula passes typing in every environment and context. |
| `VE.Surface.consume_append` | Consuming any literal character-list prefix from that prefix concatenated with any suffix returns exactly the suffix. |
| `VE.Surface.propositional_depth_le_length` | Each fragment formula's connective depth is at most its printed character count. |
| `VE.Surface.parseRaw_propositional` | In every environment and binder-name stack, with fuel strictly greater than a fragment formula's depth and a suffix that is empty or begins with a non-identifier character, parsing the formula's encoding followed by that suffix returns its embedded AST and precisely that suffix. |
| `VE.Surface.propositional_code_nonempty` | Every fragment formula's character encoding is nonempty. |
| `VE.Surface.parseStatements_nonempty` | On nonempty input and positive fuel, the statement parser equals the explicit sequence of prefix-formula parsing using input length plus one, consumption of period+LF, recursive statement parsing with one less fuel, and prepending the parsed formula. |
| `VE.Surface.parseStatements_propositional` | For any list of fragment formulas and fuel strictly greater than its list length, parsing the concatenated fragment statements returns exactly the list of embedded ASTs. This internal statement includes the empty list. |
| `VE.Surface.propositional_document_length` | The number of fragment statements is at most the character count of their concatenated statement encodings. |
| `VE.Surface.parse_print_propositional` | For every environment and nonempty list of fragment formulas, the public String parser applied to the public canonical String printer returns exactly the original embedded AST list. |
| `VE.Surface.normalize_idempotent_propositional` | If parsing text returns a nonempty embedded fragment document, normalizing that text and then normalizing the successful result equals the first normalization result. |

## Remaining obligations and trust boundary

Grammar P1–P3, P7 proposition generation, P8 production refinement, and P9
certificate expected-type binding are not proved. P10 now also covers the Lean
named graph checker, conditional on the explicit
certificate-validity soundness premise. It does not verify the Python argument
graph or certificate replay implementation. P11 requires an admissible model;
the JSON decoder's successful
validation has no proved refinement to that premise. There is no combined
finite-evaluation acceptance theorem, cryptographic identity theorem, model
search completeness theorem, or claim of a complete entailment procedure.

Tests cover all 177 shared cases / 776 formulas, full-constructor canonical
print/parse agreement, ordinary binder names, sibling scopes, source/AST
substitution, malformed models/ASTs/JSON, Unicode descriptions, and explicit
negative surface cases. They are empirical correspondence evidence only.
They do not prove grammar uniqueness, arbitrary decoder behavior, or Python/Lean
refinement. IO/UTF-8 decoding, generated binaries, compiler/runtime correctness,
resource behavior, interpretation of declarations and all empirical premises
remain outside the proved scope. The project does not consume arbitrary
agent-produced Lean code or claim to implement a safe certificate replay path.
