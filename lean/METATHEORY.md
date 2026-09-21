# Full-language metatheory milestones

All statements below quantify universally over their displayed parameters.
These are the actual String printer and parser, not a substitute token codec.
`Document E` is nonempty and each formula is closed and well typed under `E`.
The previous theorem inventory remains in [README.md](README.md).

## Declaration names and the unbudgeted reference

`Surface.NamesValid E` requires every declared sort, predicate and constant name
to match `[a-z][a-z0-9_]*`, not be in the exact v0 reserved list, and not match
`x[0-9]+`. No cardinality, identifier-length, formula-size or binder-count bound
is imposed on the theorem. Semantic `Environment.Valid` and cross-category
name distinctness are not needed by the round trip; the wire validator still
checks them. These lexical conditions exclude malformed identifiers and prevent
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
declarations and model IDs to 64 ASCII bytes. This matters mathematically for
canonical binder indices with more than 63 digits. The spec explicitly separates
reference definitions from runtime caps. The bridge still lacks a separately
budgeted source-identifier scan (along with the pre-existing source budget gap).

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

The checker is parameterized by a **decidable certificate-validity predicate**.
The semantic theorem explicitly assumes `CertificateSound E valid`: whenever
that predicate accepts a certificate with an exact list of named premises and
an exact named conclusion, the premises' formulas entail the conclusion's
formula over all admissible structures in the chosen universe, under this `E`.
This is a theorem parameter, not a new global logical assumption. The small
`GraphChecks` predicate is proved sound and executable, but is only a regression
fixture, not the production certificate interface.

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
| `check_sound` | **Graph P10:** For every environment, certificate predicate with a decision procedure and an explicit `CertificateSound` proof, graph and returned report, if the executable checker returns that report, the graph is acyclic, all submitted claim names are unique, the reported root has exactly the requested name, and the report satisfies all five `SoundReport` properties above. |
| `check_entails` | Under the same parameters and acceptance premise, the reported root formula is entailed by the formulas of exactly the reported named assumption list, over all admissible structures in the selected universe. |
| `check_unfolds` | Under the same parameters and acceptance premise, the exact reported root and assumption list satisfy the independent ordered graph-unfolding relation. |
| `VE.GraphChecks.testCertificate_sound` | For every environment, the regression-only predicate binding exact named inputs and accepting only truth introduction or direct premise reuse satisfies `CertificateSound`. |

Python remains trusted to implement the certificate predicate soundly: it must
construct the expected entailment proposition from this exact environment and
the resolved ordered premise/conclusion ASTs, replay the submitted artifact
against that proposition in the pinned Lean environment, audit the permitted
logical dependencies, and isolate untrusted proof generation. A worker build,
theorem name, certificate-supplied proposition, stale environment, or subset of
the premise list does not establish this contract. No code or proof here supplies
Python replay, P9 proposition generation/expected-type binding, the graph wire
decoder, certificate decoding, hash/identity checks, or faithful assumption display.
There is no theorem refining a Python graph validator to this Lean checker.
In this base checkout there is no Python argument graph/replay module to connect.

The checker terminates structurally over the finite node list and each ordered
premise list, given a terminating certificate decision procedure. It does not
prove graph completeness, proof-search completeness or production resource
bounds. Repeated shared leaves can make explicit output large; there is no
claim of polynomial output size, deduplication, or a verified runtime budget.

## Remaining obligations

No independent `ParseSpec` or general grammar soundness/completeness/uniqueness
(P1/P2/P3) is proved by this milestone. P4/P5 do not prove that parser and printer
avoid shared grammar errors. The lexical validator theorem is not a refinement
of all JSON decoding or model validation. Python parsing/evaluation refinement,
P7 proposition generation, P9 exact certificate expected-type binding, compiler,
runtime, IO, cryptographic identities and human interpretation remain outside
these theorems. The assurance label remains `experimental`.
