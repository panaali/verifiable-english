# Definitions statement review

What a definition means (`Layer.lean`): `Agrees S d` says that on every
well-typed argument tuple, the defined predicate holds exactly when its body
does. `Intended E ds lits S` (`Route.lean`) adds that `S` is admissible and the
declared `$string` literals are distinct. A definition list is admitted
(`Chain`, checked by `Elaborate.chainOk`) when each definition, in dependency
order, declares one fresh unary or binary predicate and its body is typed over
the symbols strictly below it (so no recursion, no free variable, no symbol
above it).

| Theorem | Statement in plain words |
|---|---|
| `faithful` | The generated biconditionals hold exactly when every defined predicate agrees with its body. |
| `conservative` | Every admissible structure of the base vocabulary has exactly one admissible expansion satisfying the definitions; forgetting the defined predicates gives it back. |
| `conservative_entails` | For statements that do not mention defined predicates, reasoning with the definitions proves exactly what reasoning without them proves. |
| `acceptance` | A checked certificate using the definitions (as Background, before the literals) proves its conclusion in every intended structure; for base-vocabulary statements, in every base structure; and for any statement, in the unique expansion of every base structure. |
| `closure_acceptance` | The same on the closure family. |
| `countermodel` | A finite model satisfying the regenerated Background is intended, so a checked countermodel refutes the statement. |
| `elaborate_chain` | The executable elaborator only returns admitted definition lists. |
| `Bundle.bundle_sound` | Every lemma of an accepted bundle is true in every intended structure in which its non-background transitive leaves hold. |
| `Alias.faithful`, `Alias.conservative`, `Alias.alias_acceptance` | The earlier worked example: one fresh unary predicate named by an existing unary predicate. |

The citation rule under review (`Bundle.checkLemma`, mirrored by
`ve/bundle.py`): a lemma may cite only lemmas strictly earlier in the same
bundle, under the same environment identity (hence the same definitions
version); reading choices must agree on every shared unit; the lemma must list
exactly Background's labelled leaves, its own labelled hypotheses and every
transitive leaf of what it cites, in that order without repeats; its
certificate is replayed by the unchanged checker on Background ++ own
hypotheses ++ cited conclusions.

English (`ve/surface/definitions.py`): "By definition, for every person, that
person is lead exactly when ...", "In this document, staff, employees and
personnel mean the same thing." (alias definitions of the first word) and
"By T7a and T7b, ..." (citations). Each reduces to ordinary closed English
statements that pass the complete all-derivations check. The strict input-only
sugar `define p(x) as (body).`, `(A) iff (B).`, `every point x that is prime,
(B).` and `no point is prime.` is unchanged.
