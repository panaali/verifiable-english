# Full-language metatheory milestones

All statements below quantify universally over their displayed parameters.
These are the actual String printer and parser, not a substitute token codec.
`Document E` is nonempty and each formula is closed and well typed under `E`.
The previous theorem inventory remains in [README.md](README.md).

## Declaration names and the unbudgeted reference

`Surface.NamesValid E` requires every declared sort, predicate and constant name
to match `[a-z][a-z0-9_]*`, not be in the exact v0 reserved list, and not match
`x[0-9]+`. No cardinality, identifier-length, formula-size or binder-count bound
is imposed on the theorem. Signature arity/sort validity and cross-category
name distinctness are not needed by the round trip; the wire validator still
checks them. The unused `Environment.Valid` predicate was removed; individual
theorems state precisely their typing, lexical or model-admissibility premises.
These lexical conditions exclude malformed identifiers and prevent
both keyword ambiguity and collisions with generated binders.

The per-name condition is the decidable Boolean `Surface.declarationName`.
`Bridge.Vocabulary.namesValid` checks every entry in a finite inventory, and
`decodeEnvironment` explicitly requires this check. `vocabulary_namesValid`
proves that check supplies `NamesValid` for its lookup-based environment.
Arbitrary function-valued `Environment` fields cannot be exhaustively checked
without a finite inventory; the universal `NamesValid` proposition is the
interface premise, not a claimed decision procedure over arbitrary functions.

`readIdent` previously mixed in the runtime 64-character cap. It now implements
the unbounded reference identifier grammar; the bridge continues to limit wire
declarations, model IDs and source identifier runs to 64 ASCII bytes. This matters mathematically for
canonical binder indices with more than 63 digits. The spec explicitly separates
reference definitions from runtime caps. `Bridge.sourceIdentifierBudget` retains
the executable source-identifier cap before reference parsing. The pre-existing
whole-source size/work budget gaps remain.

## New theorem inventory: lexical foundations

Names in this table have prefix `VE.Surface.`.

| Theorem | Exact statement in plain words |
|---|---|
| `decimal_digit` | For each natural number below ten, `Nat.digitChar` is an ASCII decimal digit and subtracting 48 from its character code recovers that number. |
| `digitsCore_valid` | For any fuel, number and all-decimal accumulator, base-ten `Nat.toDigitsCore` returns only decimal digits. |
| `digitsCore_value` | If a number is smaller than the fuel, folding decimal decoding from zero over `toDigitsCore` equals folding over the original accumulator starting at that number. |
| `digitsCore_nonempty` | For positive fuel, base-ten `toDigitsCore` returns a nonempty list for any number and accumulator. |
| `canonicalName_generated` | For every natural number, `"x" ++ toString n` matches `x[0-9]+`. |
| `canonicalName_injective` | Equal canonical names imply equal natural-number indices. |
| `generated_identifier` | Every name matching `x[0-9]+` satisfies the identifier grammar. |
| `canonicalName_identifier` | Every canonical name satisfies the identifier grammar. |
| `generated_not_reserved` | No name matching `x[0-9]+` is in the v0 reserved list. |
| `span_ident_loop` | Given an all-identifier-character prefix and a boundary-starting suffix, the span loop returns the reversed accumulator followed by the prefix, and exactly the suffix. |
| `span_ident_append` | Under the same prefix/suffix premises and an empty accumulator, identifier spanning returns exactly that prefix and suffix. |
| `readIdent_append` | Reading any valid identifier followed by an empty or non-identifier-character-starting suffix returns precisely that identifier and suffix. |

## New theorem inventory: full round trip

Names in this table have prefix `VE.Surface.`. A `Scope names n` has distinct
active names, each the canonical name of an index strictly below `n`.

| Theorem | Exact statement in plain words |
|---|---|
| `scope_mono` | A valid scope remains valid if the next counter increases. |
| `scope_fresh` | The canonical name of the next counter is absent from its valid active scope. |
| `scope_cons` | Prepending that fresh name and incrementing the counter preserves scope validity. |
| `canonical_binderAllowed` | Under `NamesValid`, the parser accepts the next canonical name as a binder in any valid scope. |
| `printAux_counter` | Printing any raw formula never decreases the next-name counter. |
| `index_lookup` | If lookup at index `i` in a duplicate-free name list gives `name`, that name is a member and its first index is exactly `i`. |
| `parseTerm_print` | Under `NamesValid`, a valid scope of the same length as the typing context, a term with an inferred sort, and a boundary-starting suffix, parsing its printed form recovers the term and exactly that suffix. |
| `printTerm_head` | Under the same scope/typing premises, every printed term begins with `@` or `x`; declaration-name validity is not needed. |
| `parseRaw_term` | Under those scope/typing premises and positive fuel, formula parsing at a printed term followed by any suffix dispatches to atomic parsing. |
| `consume_sound` | Successful literal consumption implies the input is exactly the consumed prefix concatenated with the returned remainder. |
| `consume_keyword_ne` | For distinct valid identifiers `p` and `key`, consuming space+key+space from space+p+space+any suffix fails. |
| `declaration_identifier` | Every accepted declaration name satisfies the identifier grammar. |
| `declaration_not_reserved` | Every accepted declaration name is absent from the reserved list. |
| `depth_le_print_length` | Every raw formula's connective/quantifier depth is at most its printed character count, for any name stack and counter. |
| `parseRaw_print` | Under `NamesValid`, a valid scope matching the typing-context length, a well-formed formula, fuel strictly exceeding its depth and a boundary-starting suffix, parsing its canonical prefix recovers precisely that formula and suffix. All constructors are covered. |
| `document_length` | The number of formulas in any raw list is at most the character length of its printed statements. |
| `parseStatements_print` | Under `NamesValid`, for any list of closed typed formulas, fuel strictly exceeding the list length suffices to parse its concatenated statements back to exactly that list, including the empty list internally. |
| `parse_print` | **P4:** For every environment satisfying `NamesValid` and every `Document E`, parsing its printed String returns exactly its formula list. |
| `parse_wellFormed` | In any environment, successful public parsing returns a nonempty list of closed, well-formed formulas. No lexical-validity premise is needed. |
| `normalize_idempotent` | **P5:** Under `NamesValid`, for every String, binding normalization over its normalization result equals the first result; rejection is preserved as `none`. |

Names below have prefix `VE.Bridge.`.

| Theorem | Exact statement in plain words |
|---|---|
| `lookup_name` | If finite-table lookup succeeds for a key, some pair with that exact key belongs to the table. |
| `vocabulary_namesValid` | For every finite vocabulary, if its executable declaration-name check returns true, its induced environment satisfies `Surface.NamesValid`. |

## New theorem inventory: accepted text and uniqueness

Names in this table have prefix `VE.Surface.`.

| Theorem | Exact statement in plain words |
|---|---|
| `accepted_normalize` | For every environment and text parsed successfully to a formula list, normalization returns exactly `some` of that list's printed String. This is a definitional characterization, not evidence of grammar correspondence. |
| `accepted_reparse` | Under `NamesValid`, any successfully parsed list can be printed and reparsed to exactly the same list. |
| `print_injective` | Under `NamesValid`, any two `Document E` values with equal printed Strings are equal documents, including every term index, constructor and statement position. |
| `canonical_unique` | Under `NamesValid`, if two well-formed documents both print to a given String, they are equal. This is uniqueness for the canonical rendering relation. |
| `accepted_normalize_eq_iff` | Under `NamesValid`, for any two texts successfully parsed to lists `a` and `b`, their normalization results are equal if and only if `a = b`. |
| `normalize_print` | Under `NamesValid`, normalizing any well-formed document's printed String returns that exact String. |

The injectivity result is the requested P1-style corollary of P4. It does **not**
prove the verification contract's stronger P1 about *all derivations* of an
independently specified grammar. Acceptance typing and canonical reparse are
progress toward P2/P3; the equation for `normalize` alone is definitional.

## Named claim graphs and P10

`Graph.ClaimGraph Certificate` contains a list of named AST claims and a root
name. Each node is explicitly either an assumption or a deduction with an
ordered list of premise names and a certificate. Nodes must be supplied in
topological order, with every premise before its conclusion. The checker
validates this order by ranks, checks unique names and typing, resolves every
premise from earlier checked nodes, checks every submitted edge (even outside
the root's dependency closure), and finally resolves the root. Unknown names,
cycles, forward references, conflicting aliases, and invalid certificates cause
`none`; there is no fallback that turns a failed deduction into an assumption.
A valid DAG submitted in another order is rejected. Sorting completeness is
not proved or claimed.

The returned report contains the exact named root and ordered named assumption
list. Child lists are concatenated in premise order; shared children and repeated
premise references repeat their leaves. An empty-premise certified edge contributes
no leaves. The independent `Unfolds` inductive relation specifies this computation.
Acyclicity is specified independently as absence of a nonempty dependency path
from any name to itself, not merely as success of the checker.

`Graph.checkTableau E` instantiates the generic graph checker with
`Tableau.checkCertificate` on the exact ordered formulas resolved for each edge.
`tableau_certificateSound` discharges the old `CertificateSound` premise with
the proved checker theorem. The public `Graph.check_sound`, `check_entails` and
`check_unfolds` now require only successful `checkTableau` execution. There is no
caller-supplied certificate-soundness assumption. The generic versions remain
available with the suffix `_of_certificateSound`; the small `GraphChecks`
certificate language remains a separate regression fixture.

Names in the following table have prefix `VE.Graph.` unless otherwise shown.

| Theorem | Exact statement in plain words |
|---|---|
| `acyclicCheck_dependency` | If the rank checker accepts a graph, every edge in its independent dependency relation strictly decreases rank from parent to child. |
| `path_rank` | Under the same acceptance premise, every nonempty dependency path strictly decreases rank. |
| `acyclicCheck_sound` | Every graph accepted by the rank checker has no nonempty dependency path from a name back to itself. |
| `lookup_sound` | Successful lookup returns an actual member of the stored report list whose root name is exactly the requested name. |
| `resolve_sound` | Successful ordered premise resolution returns only reports in the supplied store, and their root-name list is exactly the requested name list, preserving order and multiplicity. |
| `checkNode_sound` | Given a sound certificate predicate, stored reports satisfying `SoundReport` and a node belonging to the graph, a successful local check produces a `SoundReport`: typed root, exact submitted root provenance, typed explicit-assumption provenance for every leaf, entailment from reported leaves, and an `Unfolds` derivation for precisely the reported ordered leaf list. |
| `checkNodes_sound` | Given the same certificate contract and valid initial reports, successfully checking a node list whose nodes all belong to the graph yields only `SoundReport` entries. |
| `check_sound` | **Unconditional graph P10:** For every environment, tableau-carrying graph and report, if `checkTableau E g = some r`, the graph is acyclic, all submitted claim names are unique, the reported root has exactly the requested name, and the report satisfies all five `SoundReport` properties above. |
| `check_entails` | Under the same parameters and acceptance premise, the reported root formula is entailed by the formulas of exactly the reported named assumption list, over all admissible structures in the selected universe. |
| `check_unfolds` | Under the same parameters and acceptance premise, the exact reported root and assumption list satisfy the independent ordered graph-unfolding relation. |
| `tableau_certificateSound` | The concrete tableau predicate meets `CertificateSound` for every environment and universe, by `Tableau.checkCertificate_sound`. |
| `check_sound_of_certificateSound`, `check_entails_of_certificateSound`, `check_unfolds_of_certificateSound` | Generic counterparts of the three results above, retaining the explicit soundness premise for other certificate languages. |
| `VE.GraphChecks.testCertificate_sound` | For every environment, the regression-only predicate binding exact named inputs and accepting only truth introduction or direct premise reuse satisfies `CertificateSound`. |

Certificates are replayed against the supplied environment and resolved ASTs;
there is no certificate-supplied proposition, theorem name or executable proof
code. The core graph theorem binds names and AST provenance through the graph;
artifact hashes and descriptions are additional wire-level checks, not the
semantic definition of identity. The certificate wire adapter checks hashes.
There is still no graph JSON decoder or refinement theorem for Python's
`check_argument`, whose default execution still uses Python replay. Its
composition record is not automatically a result of the Lean graph checker.

For JSON-backed claims the expected proposition is `Bridge.JsonEntails`, exactly
`Entails.{0}`. `CertificateWire.Query.accepts_sound` proves this target for the
same decoded ordered premises and conclusion used by replay. Instantiate graph
entailment at universe 0 when pairing it with the JSON countermodel theorem.

The checker terminates structurally over the finite node list and each ordered
premise list, given a terminating certificate decision procedure. It does not
prove graph completeness, proof-search completeness or production resource
bounds. Repeated shared leaves can make explicit output large; there is no
claim of polynomial output size, deduplication, or a verified runtime budget.

## Verified tableau certificates: P9 and the discharged P10 premise

`VE/Tableau.lean`, `TableauClosure.lean` and `TableauChecker.lean` implement the
full Python calculus. The data type has the five exact certificate fields:
`checker_version`, `environment_id`, ordered `premise_meaning_ids`,
`conclusion_meaning_id`, and `trace`. Trace nodes are `close` or `expand` with a
natural-number `at`, optional String `parameter`, and ordered child list. The
logical rule is inferred from the indexed signed formula. All alpha/beta cases,
negation, gamma/delta cases and equality closure are supported. There is no
unsupported-rule subset in this milestone.

Replay starts with every supplied premise positive and the supplied conclusion
negative, with empty binder stacks. It checks closure/typing of every input.
Constants are `c:name`; a branch's delta witnesses are `w:0`, `w:1`, etc. Each
witness records its quantified sort. Gamma accepts only a declared constant or
an existing witness of the exact requested sort. A numeric-looking token such
as `w:00` does not alias `w:0`. Delta accepts no supplied parameter, allocates the
next unused index and requires every older witness reference to be below it.
Each branch tracks one-shot expansion indices and gamma (index, token) pairs,
rejecting duplicates. Child counts and order match the inferred rule exactly.

The invariant is satisfiability under a parameter assignment in an arbitrary
admissible structure. Assignments return optional values, so neither the common
carrier nor any sort needs an inhabitant. Gamma obtains its element from
constant admissibility or a previously introduced sorted witness. Delta obtains
an element from a true existential or a false universal, extends the assignment
at a fresh index, and preserves every old formula's binder valuation. A beta
step preserves at least one satisfiable child; an alpha step preserves its
single child. A successful replay closes all children, contradicting this
invariant if the initial branch had been satisfiable.

Closure grounds only literals, keeping de Bruijn binder stacks explicit. Positive
equalities generate undirected edges; bounded reachability supplies reflexivity,
symmetry and transitivity. Related tokens denote the same optional value.
Unary and binary predicates preserve truth when arguments have equal values.
A negative equality closes only when its related terms are also known to denote;
positive bottom and negative top close directly. Thus equality reflexivity never
manufactures an inhabitant. No unique-name assumption is made.

Names below have prefix `VE.Tableau.` except the last row.

| Theorem | Exact statement in plain words |
|---|---|
| `token_defined` | In an admissible structure under a sorted witness assignment, a token with inferred sort `s` denotes an element of that domain. |
| `bindings_extend` | Extending at index `n` preserves any binder stack whose witness references are strictly below `n`. |
| `holds_extend` | Such an extension preserves all signed truths on a scoped branch. |
| `typed_extend` | Adding an element of sort `s` at the next witness index preserves sorted assignment validity for the appended witness inventory. |
| `add_holds` | Appending signed formulas that hold preserves branch satisfaction. |
| `one_holds` | A true signed one-child rule supplies every one of its additions. |
| `two_holds` | A true signed two-child rule supplies at least one alternative. |
| `gamma_holds` | A gamma formula supplies its signed body when instantiated by a token denoting an element of the requested sort. |
| `delta_witness` | A delta formula supplies an element of its quantified sort and its signed body under the extended binder valuation. |
| `bindings_get` | If every binder token denotes, indexing its interpreted list agrees with indexing the tokens then interpreting the selected token. |
| `termToken_denote` | Under that defined-binder premise, grounding a term preserves its optional denotation. |
| `ground_denote` | Grounding a literal under that premise preserves its truth. |
| `literals_hold` | On an admissible, satisfied branch with known binder tokens and a sorted assignment, every extracted signed literal holds. |
| `mem_dedup` | Token deduplication preserves membership in both directions. |
| `equalities_sound` | Every extracted positive equality has endpoints with equal optional denotations. |
| `grow_sound`, `reachable_sound` | If all equality edges preserve a value and every initial reachable token has that value, one expansion and any finite number of expansions preserve that fact. |
| `equivalent_sound` | Accepted token reachability under satisfied positive equalities implies equal optional denotations. |
| `matches_sound` | Accepted unary/binary atom matching under those equalities implies equivalent atom truth. |
| `closes_sound`, `closed_sound` | No satisfied admissible branch under a sorted assignment and known bindings can pass literal closure. |
| `next_sound` | Any accepted expansion of a scoped satisfiable branch has a satisfiable child, under a possibly extended sorted assignment. |
| `checkChildren_member` | Successful child replay supplies a successful trace for every generated branch; none can be omitted. |
| `replay_sound` | For every fuel, successful replay contradicts branch satisfaction in every admissible structure under every sorted assignment. |
| `checkCertificate_sound` | **P9:** For every `E`, ordered premise list, conclusion and certificate, `checkCertificate E premises conclusion c = true` implies `Entails.{u} E premises conclusion`, for every universe `u`. No certificate-validity soundness hypothesis occurs. |
| `VE.CertificateWire.Query.accepts_sound` | For every decoded typed query with `accepts = true`, its exact ordered premises entail its exact conclusion at universe 0. |

All recursive checking is structural or fuel recursive. Public replay has 500
levels of fuel; exhaustion returns false. It is not proof search and is not
claimed complete. Equality reachability uses one expansion round per positive
equality edge; its soundness is proved, but equivalence with Python union-find
and general acceptance completeness are not proved. The wire boundary retains
the 16 MiB batch and 256-level JSON caps, 64-level formula cap and 10,000-node
aggregate AST cap. These differ from a complete production work-budget policy.

`ve_conformance check-certificate [file|-]` decodes the environment, typed
premises/conclusion and certificate, recomputes the Python domain-separated
SHA-256 bindings (including order, duplicates and descriptions), then invokes
the very proved checker. Lean's standalone logical checker deliberately does
not use hash metadata as evidence: it replays against actual ASTs. The wire
adapter rejects stale bindings even if a trace could prove another true query.
Its total SHA-256/canonical-JSON code is tested against Python identities and
standard digest vectors, but neither cryptographic correctness nor JSON
correspondence is formally proved.

The committed [report](../conformance/certificates-report.json) records **721/721
Python-produced certificates accepted (100%) and 150/150 forgeries rejected**.
There are no Python-accepted/Lean-rejected cases to classify in this corpus.
Two seeded cohorts each contain 320 randomly instantiated valid inference
schemas: the unrestricted cohort yields 317 certificates and 3 `ResourceLimit`
outcomes; the bounded cohort yields all 320. Among 160 unconditioned random
queries, 82 yield certificates, 74 yield `NotFound`, and 4 hit `ResourceLimit`.
The bridge-repair and merged-vocabulary worked examples yield accepted proofs;
the separated-vocabulary example yields `NotFound` and its forged close is
rejected. Every produced certificate is checked, and all search outcomes remain
in the denominator. This is development conformance evidence, not a workload
acceptance estimate or completeness proof. Reproduce with:

```sh
.venv/bin/python conformance/certificates.py --report conformance/certificates-report.json
.venv/bin/python -m pytest -q tests/test_lean_certificates.py
```

The remaining trust base for executable acceptance is Lean's kernel and standard
logical foundations (`propext`, `Classical.choice`, `Quot.sound`), the pinned Lean
compiler/runtime and standard library, UTF-8/JSON/environment/formula/certificate
decoding, canonical serialization/hash binding, IO and faithful display of the
actual checked query. The Python prover and its replay checker are **untrusted
search/filtering** when their outputs go through this Lean path. Python's default
API has not been switched to Lean, and no Python refinement theorem is claimed.
Human interpretation, empirical premises and evidence authenticity remain
outside logical entailment. The assurance label remains `experimental`.

## Model-output admissibility and executable P11

Names below have prefix `VE.Bridge.`. These are six audited declarations:
two headline results (`decodeModel_valid`, `CountermodelQuery.refutes_sound`)
and four supporting lemmas/corollaries. The complete project inventory is 11
headline results plus 99 supporting declarations; see [README.md](README.md).

| Theorem | Exact statement in plain words |
|---|---|
| `lookup_mem` | A successful finite-table lookup returns a key/value pair present in the table, even if keys repeat. |
| `tupleCheck_iff` | For any finite model and signature/tuple lists, the recursive Boolean tuple check equals the semantic `TupleTyped` predicate. |
| `modelData_valid` | For every finite table and vocabulary, success of the final Boolean admissibility gate implies its embedded model is admissible for that vocabulary's environment. All declared constants and all stored true relation tuples are covered. No earlier wire-check success is assumed. |
| `decodeModel_valid` | For every vocabulary, JSON value and finite model, `decodeModel v j = .ok M` implies `M.Valid v.environment`. The final semantic gate is mandatory. |
| `decoded_countermodel_sound` | For every successfully decoded model, raw premise list and raw conclusion, a true Boolean countermodel check refutes `Entails.{0}` for the same environment/formulas. This extends to raw formulas under their explicitly defined total semantics; it does not prove typing. |
| `CountermodelQuery.refutes_sound` | For every successfully decoded model and `CountermodelQuery` whose executable `refutes` check returns true, all premises and the conclusion are closed and well typed, and `Bridge.JsonEntails` (exactly `Entails.{0}`) is false. |

The executable `decodeCountermodel` constructs `CountermodelQuery` only after
checking closure and typing, including every premise even when an earlier
premise would evaluate false. It permits zero premises. `runCase` exposes the
same `CountermodelQuery.refutes`/`countermodelCheck` functions in its opt-in
countermodel response. The theorem is about the decoded model and typed query,
not JSON serialization, IO, or generated machine code. Python is compared on
the committed corpus; that empirical comparison is not a refinement proof.

The independent disjoint-carrier interpretation is an **unproved external
assumption for typed formulas**, with its intended construction explained in
[README.md](README.md#typing-universes-and-the-carrier-interpretation-assumption).
It introduces no Lean assumption and is not used by these proofs.

## Remaining obligations

No independent `ParseSpec` or general grammar soundness/completeness/uniqueness
(P1/P2/P3) is proved by this milestone. P4/P5 do not prove that parser and printer
avoid shared grammar errors. The lexical validator theorem and model-output
admissibility theorem do not prove JSON decoding matches the wire spec.
Python parsing/evaluation/graph refinement, P7 source-to-proposition correspondence,
JSON-to-checked-AST correspondence, compiler/runtime and IO correctness,
cryptographic identities and human interpretation remain outside these theorems.
P9 now binds replay directly to the exact decoded query; it does not prove the
JSON boundary or correspondence to a separate proposition generator. The assurance label remains `experimental`.
