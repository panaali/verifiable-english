# Order foundation: Stage 1 checkpoint

`VE.Order` is the Lean foundation for opt-in `order@0`. It is **not yet an
accepted Python or JSON profile**. Stage 1 is implemented; Stages 2 and 3 remain
unimplemented. The implementation boundary and continuation requirements are in
[order-implementation.md](../docs/spec/order-implementation.md).

Terms add arbitrary-precision `Int` numerals, addition and multiplication by an
`Int` coefficient. Unary minus is scale by -1; subtraction is addition of a
negated term. Equality retains ordinary equality, with new `<` and `≤` atoms.
Terms can occur in unary/binary relations with integer argument sorts. No
variable product, division, modulo, real arithmetic or implicit coercion exists.

`SortName.int` is distinct from `SortName.user s` for every string `s`.
Structures use `Sum Carrier Int`. Every standard integer is in the integer
sort, and no object is in that sort. Numerals denote their literal integer;
constants may alias. User sorts retain arbitrary, possibly empty or infinite,
domains in denotation. Finite presentations enumerate only user objects and
predicate rows; a row absent from a table is false even when it contains an
integer absent from every other row. Integer cells and constants store `Int`,
not object identifiers or indices into a numeric domain.

Integer quantification is **disallowed in this implementation**, an explicitly
permitted narrowing of design B. Quantifier constructors bind user objects;
the checker rejects a binder spelled `$int` even if an adversarial environment
lists that name as a user sort. The integer sort remains infinite regardless
of the fragment's inability to quantify it. This makes evaluation total without
an unproved integer quantifier-elimination procedure. Raw ill-typed formulas have
total denotation/evaluation but are not accepted claims. In particular an invalid
raw binder named `$int` is a user binder, never an integer-domain enumeration.
A future wire adapter must reject `$int` declarations and finite enumerations,
and reject integer quantifiers before constructing an accepted document.

Order and closure are **incompatible at this checkpoint**. No mixed formula,
mixed evaluation, or closure-to-order embedding is claimed. The existing closure
implementation and its theorems remain intact; the combined certificate envelope
is rejected. General composition in design D remains future work.

All named results below are audited. Quantification over structures and object
carriers is universe-polymorphic; there is no finite-domain restriction in the
consequence relation.

| Theorem in `VE.Order` | Exact statement in plain words |
|---|---|
| `check_iff_wellFormed` | For every environment, context and raw formula, the executable checker returns true exactly when the independent well-formedness predicate holds. |
| `integer_of_domain` | Any value in a structure's integer domain is the integer injection of some standard integer. |
| `term_defined` | In any admissible structure and typed valuation, a term assigned a sort by `sortOf` denotes a value in that sort. |
| `numerals_distinct` | In every structure and valuation, equality of the numerals for x and y holds exactly when the standard integers x and y are equal. |
| `compareEval_iff` | If a Boolean integer comparison agrees with a propositional integer relation for all integer pairs, its lifted evaluation on any two optional object/integer values agrees exactly with `Compare` for that relation. |
| `eval_iff_denote` | For every object type with decidable equality, every finite presentation, every valuation and every raw order formula, evaluation returns true exactly when the formula denotes true in that presentation's structure. No model-validity or typing assumption is needed for this equivalence. |
| `eval_false_iff_not_denote` | Under the same quantification, evaluation returns false exactly when denotation does not hold. |
| `countermodelCheck_iff` | For every finite presentation, list of premises and conclusion, the countermodel checker returns true exactly when all premises denote true and the conclusion denotes false in that presentation. |
| `countermodel_sound` | If a finite presentation is admissible for an environment and the countermodel checker returns true, the premises do not entail the conclusion over all admissible structures in that universe. |
| `embedTerm_denote` | For every v0 structure, valuation and term, denotation of the embedded term in the expanded structure and object-injected valuation is precisely the object injection mapped over the old optional denotation. |
| `expand_relation_unary` | The expanded structure's relation on the injection of one old object holds exactly when the old unary relation holds on that object. |
| `expand_relation_binary` | The expanded structure's relation on the injections of two old objects holds exactly when the old binary relation holds on those objects. |
| `conservativity` | For every v0 structure, valuation and raw formula, the embedded formula in the expanded structure and object-injected valuation has exactly the old denotation. |
| `tupleTyped_expand` | A tuple of object injections has the corresponding user-sort signature in the expansion exactly when the old tuple has the original signature. |
| `expansion_admissible` | Every v0 structure admissible for a v0 environment expands to an order structure admissible for the expanded environment. |
| `entails_v0` | If the mapped v0 premises entail the embedded v0 conclusion in the expanded order environment, the original premises entail the original conclusion in v0. Thus this expansion creates no new entailments between old claims. |
| `certificate_profile_gate` | For every JSON vocabulary, the unchanged closure environment decoder returns the unsupported-version/profiles error on the proposed order-only envelope. |
| `combined_profile_gate` | For every JSON vocabulary, that same decoder returns that error on the proposed closure-plus-order envelope. |

The last two theorems concern the exact decoder used by the existing v0.1
certificate route. Runtime regressions additionally exercise the complete
certificate entry point, with an accepted v0 certificate as control, both
profile lists, two revisions, and three checker-version tags. All order cases
must fail at the profile gate, before certificate replay or identity checking.
There is no order certificate-soundness theorem and no enabled order proof path.

`Checks.lean` covers negative/large numerals, signed scaling, subtraction,
integer aliases, object/integer separation, undefined terms, rejected arithmetic
on objects, mixed predicate arguments, absent numeric tuples, empty user sorts,
user quantification and positive/negative countermodel checks. These are Lean
regressions, not the requested Python/Lean differential corpus.

The source/dependency audit scans every project Lean source and every named
theorem. Only the pre-existing standard allowlist (`propext`, `Classical.choice`,
`Quot.sound`) is permitted. The original v0 and closure theorem sources and both
certificate checkers are byte-for-byte unchanged from the branch base.
