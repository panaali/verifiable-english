# Lean 4 reference semantics for VE v0

This project uses Lean **4.24.0**, core Lean and `Std`, with no Mathlib or external
Lake dependencies. It formalizes the full function-free relational syntax and
Tarski semantics and proves finite evaluator equivalence (P6). **P9/P10 now use
proved tableau replay:** `Tableau.checkCertificate_sound` proves that every
accepted data-only certificate entails its exact supplied conclusion from its
ordered premises, over all admissible structures. `Graph.check_entails` uses
this theorem without a caller-supplied `CertificateSound` hypothesis. All
propositional, quantifier and equality rules are supported, including empty
sorts. Python graph/refinement and the JSON boundary are not verified.
**P11 requires admissible models:** `decodeModel_valid` now proves that every
successful executable model decode supplies this premise; typed countermodel
queries refute precisely `Entails.{0}`. JSON/wire-spec correspondence, Python
refinement and compiler/IO correctness remain outside the proof.
P4/P5 are proved for the full v0 syntax under the spec's declaration-name
restrictions, including arbitrarily many preorder-named binders and statements. These results do not
upgrade the complete Python acceptance path from `experimental`.

From this directory:

```sh
lake build
python3 audit.py
lake exe ve_conformance ../conformance/evaluation.json
lake exe ve_conformance ../conformance/countermodels.json
lake exe ve_conformance check-certificate certificate-query.json
```

From the repository root:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run --frozen python -m pytest -q
python3 conformance/generate.py
.venv/bin/python conformance/certificates.py --report conformance/certificates-report.json
```

The current inventory contains **11 headline results and 99 supporting lemmas or
corollaries**, not 110 independent milestones. The headline results are
`eval_iff_denote`, `composition_sound`, `Graph.check_sound`,
`Tableau.checkCertificate_sound`, `CertificateWire.Query.accepts_sound`,
`Bridge.decodeModel_valid`, `Bridge.CountermodelQuery.refutes_sound`,
`Surface.parse_print`, `Surface.normalize_idempotent`, `Surface.print_injective`,
and `Surface.accepted_normalize_eq_iff`. [METATHEORY.md](METATHEORY.md) gives exact
plain-word statements and the remaining premises.

`lake build` builds the semantic library, all proofs, direct executable regression
checks, and the JSON executable. `audit.py` checks that every named theorem has a
`#print axioms` entry, reruns those audits, and rejects any transitive dependency
outside `propext`, `Classical.choice`, and `Quot.sound`. All named theorems in the current [audit](axioms.txt) pass;
there are no `sorry`, new axioms, unsafe declarations, or native-evaluation
proofs. The source audit scans every project `.lean` file, including `Main.lean`,
root modules and nested directories (excluding the `.lake` dependency/build
cache). It prohibits `partial`, `opaque`, `extern`, `implemented_by`, `unsafe`,
`native_decide`, `axiom`, `sorry`, `sorryAx` and `admit` as literal source tokens,
conservatively including comments and quoted text. The
upstream toolchain and its standard logical dependencies remain trusted.

## Representations and scope

* `VE/Syntax.lean`: raw indexed `Term` and `Formula`, finite declared sort list,
  unary/binary predicate signatures, constant sorts, extrinsic well-formedness,
  executable type/scope checker, and nonempty closed typed `Document`.
* `VE/Semantics.lean`: a common carrier `Type u` with a domain predicate for each
  sort; constants and relations must satisfy `Structure.Admissible`. Domains may
  overlap. Equivalence with separate disjoint carriers for typed formulas is
  an explicit unproved interpretation assumption, explained below. Empty domains are allowed;
  constants inhabit their declared domains; constants need not be distinct.
  Cross-sort equality is rejected by typing. No carrier is assumed finite or
  inhabited. `Entails.{u}` ranges over **all admissible structures in universe
  u**, not just supplied inventories. Generic semantic statements are uniform in
  that universe. JSON entities are `String × String : Type 0`, and JSON-backed
  consequence uses `Bridge.JsonEntails`, an alias of **`Entails.{0}`**.
* `VE/Finite.lean`: finite domain lists and relation extensions, their embedding
  into `Structure`, and a structurally recursive Boolean evaluator. An infinite
  ambient ID type is permitted; quantifiers use only the enumerated domain.
  Evaluation and denotation agree even on raw formulas. Semantic claims use
  closed well-formed formulas and admissible structures. A raw term whose
  interpretation is `none` produces false atoms; `term_defined` excludes this
  behavior for typed terms under typed valuations in admissible structures.
* `VE/Consequence.lean`: finite acyclic proof trees whose steps carry actual
  entailment proofs, cut/composition, and finite countermodel soundness.
* `VE/ClaimGraph.lean`: executable named claim-graph checking, with explicit leaf
  nodes, ordered premise references and a checked topological order. The concrete
  `checkTableau` predicate has proved soundness, so acceptance proves acyclicity, unique
  aliases, exact root identity, typing, named leaf provenance, exact ordered
  leaf unfolding (including duplicates), and entailment of the root from those
  leaves. `VE/GraphChecks.lean` exercises positive/negative cases with a small
  proved-sound test certificate language; `VE/TableauChecks.lean` tests the actual
  tableau-backed graph path. No Python graph refinement, graph wire decoder or
  cryptographic identity correctness theorem is supplied.
* `VE/Tableau.lean`, `VE/TableauClosure.lean`, `VE/TableauChecker.lean`: the full
  signed-tableau calculus and sound executable certificate checking. Sorted
  parameter assignments preserve branch satisfiability; fresh delta extensions
  preserve older valuations; gamma requires a known element. Equality closure
  supports reflexivity, symmetry, transitivity and unary/binary substitution.
  Version 2 also checks exact complementary formulas with identical bindings,
  matching the existing Python rule; version 1 retains literal-only closure.
  Replay is total with depth fuel 125 (124 expansions plus a close). Its entailment theorem is universe
  polymorphic and permits infinite structures, empty sorts and empty carriers.
* `VE/CertificateWire.lean`: exact certificate JSON decoding, canonical JSON and
  SHA-256 identity checks, plus the `check-certificate` mode. Its query acceptance
  theorem pins the expected target to `Entails.{0}`. Decoder/serializer/hash
  correspondence and machine execution remain tested boundary code.
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
  decoder and semantic environment validation remain unproved.
* `VE/ModelProofs.lean`: the final executable finite-table admissibility gate
  implies `M.Valid E`; successful `decodeModel` necessarily passes that gate.
  The decoded-countermodel theorem discharges P11's validity premise, and
  `CountermodelQuery.refutes_sound` includes closed typing and universe 0.
  This proves decoder-output admissibility, not correspondence with the wire spec.
* `VE/Json.lean` and `VE/Bridge.lean`: restricted JSON decoding and validators.
  Model entities are `(sort, local_id)` pairs. The bridge invokes
  the very `Formula.eval`/`Document.eval` covered by P6, not a separate evaluator.
  A decoded document carries a proof of well-formedness from the proved checker.
  Environment wire validation is tested; model-output admissibility is proved.

The bridge reads a case or array of cases from a path or stdin. An evaluation case contains
`id`, `environment`, `model`, and indexed document `ast`; optional `source` must
parse to that AST. Every case also exercises canonical printing/parsing. It
returns `id`, `status`, `values`, whole-document `value`, and `canonical`.
An opt-in `kind: "countermodel"` case instead supplies an ordered `premises` AST
array (possibly empty) and one `conclusion` AST. Its response contains `id`,
`status`, and Boolean `refutes`, computed by `countermodelCheck`. Both premises
and conclusion must be closed and typed. `expected` and `expected_refutes` in
fixtures are ignored. Exit 0 is successful evaluation (including
false), 1 is case rejection, and 2 is JSON or invocation failure. See
[`../conformance/README.md`](../conformance/README.md) for the shared corpus.

The separate `check-certificate` mode takes one query or a batch of
`{id, environment, premises, conclusion, certificate}` objects and returns
`{id, status: "ok", valid: boolean}`. `premises` is an ordered AST list;
`conclusion` is a single formula AST. A stale/malformed package returns
`{id, status: "error", valid: false, error}` and exit 1. A well-formed trace that
fails replay returns `valid: false` with exit 0; invalid JSON/invocation is exit 2.
**Acceptance is `valid: true`, never the process exit code alone.**

The decoder rejects duplicate keys before map insertion, invalid surrogate
escapes, null, fractions/exponents, out-of-range integers, invalid names,
unsupported versions, missing fields, duplicate inventory entries, wrong arity,
dangling/wrong-sort entities and ill-typed/free AST indices. It implements
formula depth/node, vocabulary, domain, tuple, and overall input-byte limits.
It accepts Python's optional sort and predicate `verbalisation` metadata and
predicate `negative_verbalisation`, checking their field shapes and string
bounds. These are inert display data; lexical linting and negative-template
selection belong to the Python renderer and are outside the Lean proofs.
It does not implement Python's evaluation-work or trace budgets, source-size
budget, diagnostics, explanations or assurance records. Its 16 MiB input cap
applies to the entire batch envelope. The certificate mode does check JCS/SHA-256
bindings. It is a conformance tool with verified logical replay, not a resource
isolation service or replacement Python CLI.

The new full-language theorem inventory and precise lexical conditions are in
[METATHEORY.md](METATHEORY.md). The table below records the original milestone.

## Typing, universes and the carrier interpretation assumption

`Entails` and the generic P6/P11 lemmas deliberately extend to raw formulas;
they contain no hidden typing premise. Raw denotation is total: if `nope` has no
interpretation, `not (@nope equals @nope)` evaluates true because its equality
atom is false. Raw cross-sort equality can also observe overlapping domains.
Neither is a typed VE claim. `Formula.WellFormed E []` supplies closure and typing;
`Document E`, `Derivation`, accepted graph reports and `CountermodelQuery E`
carry that evidence. For open terms, `term_defined` additionally needs an
admissible structure and `Valuation.Typed S Γ ρ`. Typed equality is same-sort;
there is no unique-names assumption. Executable inputs reject undeclared
constants, free indices and cross-sort equality before evaluating them.

`Bridge.JsonEntails E premises conclusion` is exactly `Entails.{0} E premises
conclusion`, quantifying over all admissible common-carrier **Type 0** structures,
including infinite ones. JSON-backed P9 expected types must use this alias (or
explicit `Entails.{0}`); the corresponding generic graph certificate contract
must be instantiated at universe 0. The certificate query theorem proves exactly
this target; the underlying tableau and graph entailment theorems hold at every universe.
The finite JSON witness is not claimed here to refute an unspecified universe.

**Unproved external interpretation assumption — disjoint carriers.** We assume,
only when comparing this presentation with independent disjoint many-sorted
semantics, that satisfaction of typed formulas and typed valuations is preserved
by tagging each domain element with its sort. The intended carrier is
`Σ s : String, {x : S.Carrier // S.domain s x}`; the domain of sort `s` contains
only tags `s`. Declared constants receive their declared sort's tag, and each
relation tuple receives the tags of its declared signature. A valuation is tagged
according to its typing context. Within a fixed sort, tagging is injective, so
same-sort equality and aliased constants are preserved; quantifiers range over
bijective copies of their original domains, including empty ones. Formula
induction should establish satisfaction preservation. Conversely, disjoint
carriers embed in their tagged union with the same argument. For closed typed
premises/conclusions this would give equivalence of the two consequence notions.

That construction and induction are **not Lean-proved in this project**. They
are not valid for unrestricted raw formulas that compare distinct sorts. No
Lean declaration introduces this assumption, and none of the audited theorems
depends on it; all proved consequence statements refer to the explicitly defined
common-carrier semantics. Claims transferring them to a separate disjoint-carrier
formalization remain conditional on this interpretation assumption.

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

Grammar P1–P3, P7 source/proposition correspondence and P8 production refinement
remain unproved. P9 is now supplied by direct replay against the exact decoded
query, and P10 by `Graph.checkTableau`; neither needs an abstract certificate
soundness premise. These results do not verify Python's default argument/replay
implementation or prove JSON correspondence. P11 requires an admissible model;
successful `decodeModel` supplies that premise. The finite countermodel and
JSON certificate theorems share precisely `Entails.{0}`.

For Lean-accepted certificates, the Python prover and Python replay are
untrusted search/filtering. Remaining trusted executable components include
Lean's kernel, the standard logical foundations, compiler/runtime and standard
library, UTF-8/JSON/environment/AST/certificate decoding, canonical serialization
and hash identity checks, IO and faithful display of the checked query. The
SHA-256 implementation has standard-vector and Python-identity tests; it has
no cryptographic correctness proof. The existing Python `check_argument` API
still uses its own checker and is not automatically upgraded to the Lean path.
There is no graph wire/refinement theorem, completeness theorem, production
resource-bound proof, or verification of empirical evidence.

The certificate conformance run accepts **732/732** Python-produced certificates
and rejects **150/150** forgeries, including missing/wrong-sort/future parameters,
empty-sort inhabitation, illegal delta witnesses, stale identities and malformed
branches. The two positive worked examples pass; the separated example has no
proof and a forged close is rejected. All 811 search attempts and their outcomes
are retained in [the report](../conformance/certificates-report.json); 320 bounded
random valid queries all produce certificates, and another 320 broader valid
queries also all produce certificates. Eight existential weakening regressions
prove; 160 unconditioned queries give 82 certificates, 76 `NotFound` and two
resource-limit outcomes. These are seeded schema
and random-query tests, not an independently sampled workload or a completeness
claim. No produced certificate in this corpus was rejected by Lean.

Tests cover all 701 shared evaluation cases / 4,912 formulas and 708 countermodel
cases, full-constructor canonical
print/parse agreement, ordinary binder names, sibling scopes, source/AST
substitution, malformed models/ASTs/JSON, Unicode descriptions, and explicit
negative surface cases. They are empirical correspondence evidence only.
They do not prove grammar uniqueness, wire-decoder correspondence, or Python/Lean
refinement. IO/UTF-8 decoding, generated binaries, compiler/runtime correctness,
resource behavior, interpretation of declarations and all empirical premises
remain outside the proved scope. Certificates are data-only; the executable
does not consume agent-produced Lean code.

Tableau milestone validation (September 21, 2026): `lake build` passes;
`python3 lean/audit.py` audits 25 source files and 110 named theorems;
`.venv/bin/python -m pytest -q` passes **528 tests**, with **2 skips** for the
uninstalled optional `llguidance` and `xgrammar` backends. Dependencies were
synced with `UV_CACHE_DIR=/private/tmp/ve-uv-cache uv sync --frozen` before the full run.

## Opt-in closure profile

`VE.Closure` adds finite-path plus/star semantics, Named/Body edges, proved
finite evaluation and typing, Reach-free conservativity, and least-fixed-point
characterizations. Both edge forms have executable strict syntax; the new
round-trip theorem covers Named atoms. The JSON bridge dispatches the v0.1
closure envelope separately, and certificate replay explicitly rejects that
profile. Exact statements and remaining proof obligations are in
[`CLOSURE.md`](CLOSURE.md).
