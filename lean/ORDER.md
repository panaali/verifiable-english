# Order: Lean foundation, Farkas certificate checker and wire route

`VE.Order` is the Lean side of opt-in `order@0`. Stage 1 (syntax, typing,
semantics, finite evaluation, conservativity), the finite-model gate and the
general profile gate, and the Farkas certificate checker (`Tableau.lean`,
`checkCertificate_sound`) are implemented. Order envelopes are accepted **only**
on the separate `ve_conformance order` route (`Wire.lean`); the pre-existing
certificate and evaluation routes are unchanged and still reject every envelope
that declares `order@0`. The Python stage, the frozen canonical forms and the
differential corpus are described in
[order-implementation.md](../docs/spec/order-implementation.md).

Round 2 adds `Surface.parse` on a separate `kind: "surface"` case in the order
route. It returns a checked indexed AST from strict order text. The dispatcher
is covered by `surface_route_gate`; the certificate checker and its soundness
proof are unchanged. No order parser/printer round-trip theorem is claimed.

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
The order wire adapter (`Wire.decodeEnvironment`) maps the reserved spelling
`$int` to `SortName.int`, accepts no user sort spelled `$int` (it is not an
identifier), lists no integer domain, and type-checks every formula against the
decoded environment before use.

Order and closure remain **incompatible**. No mixed formula, mixed evaluation,
or closure-to-order embedding is claimed. The existing closure implementation
and its theorems remain intact; an envelope declaring both closure@0 and
order@0 fails on every route (`combined_profiles_rejected` and
`combined_profiles_surface_rejected`). General
composition in design D remains future work.

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
| `validModel_iff` | For every finite order vocabulary (declaration lists) and every finite model table set over any object type with decidable equality, `validModel?` returns true exactly when the tables' finite presentation is admissible (`FiniteModel.Valid`) for the vocabulary's environment. No uniqueness, lexical or `$int` assumption is needed. |
| `checkCountermodel_iff` | The end-to-end countermodel gate returns true exactly when the tables are admissible, every premise denotes true and the conclusion denotes false. |
| `checkCountermodel_sound` | If the end-to-end gate accepts finite tables, the premises do not entail the conclusion over all admissible structures in the tables' universe. There is no validity hypothesis. |
| `domainCheck_iff`, `tupleCheck_iff`, `lookup_mem`, `lookup_isSome` | Helper lemmas: executable sort and signature membership agree with `Structure.domain` and `TupleTyped`; first-entry lookup agrees with list membership. |
| `closure_decode_profiles` | For every JSON value, if the closure environment decoder succeeds, its `language` is `ve.core@0.1`, its declared `profiles` decode to exactly `["closure@0", "relational-fol@0"]`, and it has no singular `profile` field. |
| `v0_decode_profiles` | For every JSON value, if the v0 environment decoder succeeds, its `language` is `ve.core@0`, its singular `profile` is `relational-fol@0`, and it has no `profiles` field (also for raw objects with repeated keys). |
| `decode_profiles_accepted`, `v0_runCase_profiles`, `closure_runCase_profiles`, `certificate_runCase_profiles` | Success of either decoder, of each evaluation `runCase`, and of the certificate `runCase` (both branches of its `language` dispatch) implies `ProfilesAccepted` for the case's environment. |
| `profile_gate` | For every JSON case, if the certificate route or the evaluation route (`runEvaluationCase`, the `language` dispatch used by `ve_conformance`) succeeds, the case's environment satisfies `ProfilesAccepted`: exactly the closure profile list, or v0 without a `profiles` field. |
| `order_not_accepted`, `order_profile_gate` | An environment whose declared `profiles` contain `order@0` never satisfies `ProfilesAccepted`; hence every case declaring `order@0` fails on both routes, whatever its other fields. |
| `singular_order_not_accepted`, `singular_order_profile_gate` | The same for a singular `"profile": "order@0"` field, under any `language`. |
| `order_decode_profiles`, `order_route_gate` | The order route (`Wire.runCase`) succeeds only if the case's environment has `language` `ve.core@0.1` and `profiles` exactly `["order@0", "relational-fol@0"]`. |
| `surface_route_gate` | The executable order dispatcher, including the surface parser case, has the same exact profile gate. |
| `combined_profiles_rejected` | An environment whose declared profiles contain both closure@0 and order@0 fails on the certificate route, the evaluation route and `Wire.runCase`. Its original statement is preserved. |
| `combined_profiles_surface_rejected` | The same profile combination also fails through the executable `Surface.runCase` dispatcher. |
| `Tableau.checkCertificate_sound` | If the order checker accepts a certificate (checker `ve-order-farkas-checker@1`) for premises and a conclusion, the premises entail the conclusion over every admissible order structure, at every universe, with standard unbounded integers. There is no certificate-soundness premise. |
| `Wire.Query.accepts_sound` | The JSON-facing form of the same result, at universe zero. |
| `Tableau.replay_sound`, `next_sound`, `closed_sound`, `farkas_sound`, `neqSplit_sound` | A satisfiable branch has a satisfiable child under every rule; closing rules (complementary formulas, argument congruence, Farkas with cuts) never close a satisfiable branch. |
| `Tableau.constraint_sound`, `addLiterals_sound`, `addCuts_sound`, `comboLin_sound`, `runCuts_sound` | Every usable literal gives `0 ≤ p` (`t < u` read as `t + 1 ≤ u`; a negated `≤`/`<` as the opposite strict/weak bound; an equality as `0 = p`), and nonnegative combinations and Chvatal-Gomory cuts preserve `0 ≤ p`. |
| `Tableau.sameValue_sound`, `objectEq_sound`, `hasLe_sound`, `closed_denote`, `termToken_denote`, `bindings_get`, `known_defined` | Argument equality evidence (same resolved token, one positive object equality, identical linear term, or `t ≤ u` and `u ≤ t` on the branch) implies equal denotations. |
| `Tableau.token_defined`, `bindings_extend`, `holds_extend`, `typed_extend`, `add_holds`, `one_holds`, `two_holds`, `gamma_holds`, `delta_witness`, `object_of_domain`, `compare_ints`, `checkChildren_member` | Tableau helper lemmas, as in the v0 checker, for user-sort binders over `Sum Carrier Int`. |
| `linearize_denote` | For every admissible structure and valuation, a term that linearizes to a form denotes the integer value of that form (integer constants read through the structure). |
| `tighten_sound`, `floor_bound`, `sumTerms_divide` | If `0 ≤ b + Σ kᵢxᵢ`, `g > 0` and `g` divides every collected coefficient, then `0 ≤ ⌊b/g⌋ + Σ (kᵢ/g)xᵢ` over the integers. |
| `Lin.eval_*`, `sumTerms_*` | Evaluation of linear forms commutes with addition, scaling, subtraction, shifting, collection of repeated names, and vanishes on zero coefficients. |
| `runEvaluationCaseReported_eq` | The binary's evaluation route through `runEvaluationCaseReported` equals the previous inline `language` dispatch. |
| `ProfileGate.bind_ok`, `ProfileGate.exactFields_keys`, `ProfileGate.getObjVal_mem`, `ProfileGate.impl_get_mem`, `ProfileGate.nodup_length_le` | Helper lemmas for the gate: `Except` bind inversion; `exactFields` admits no unexpected key; any key found by `getObjVal?` is listed by `fields`, for arbitrary (not necessarily well-formed) JSON object trees. |

`validModel?` and `checkCountermodel` (in `ModelCheck.lean`) close review
finding 1: `Environment` and `FiniteModel` hold functions, so validity is decided
over their finite wire form, `Vocabulary` and `ModelData`, as in v0's
`Bridge.ModelData`. `checkCountermodel_sound` is stated for `v.environment`,
which uses first-entry lookup and distinguishes a user sort spelled `$int` from
the built-in integer sort. A decoder therefore still has obligations before the
theorem says anything about the JSON it read: reject duplicate keys (or match
first-entry lookup), map `$int` to `SortName.int`, and type-check formulas against
that same environment. `Wire.decodeModel` meets them: the restricted JSON parser
rejects duplicate keys, `decodeSortName` maps `$int`, and `decodeFormulas` checks
against `v.environment`; the countermodel route calls `checkCountermodel` itself.
`ProfileGate.lean` closes review finding 2. Its theorems prove that decoding
*fails* on the stated inputs; unlike the two point theorems below (kept
unchanged), they do not fix the error message.

The `certificate_profile_gate` and `combined_profile_gate` theorems concern the exact decoder used by the existing v0.1
certificate route. Runtime regressions additionally exercise the complete
certificate entry point, with an accepted v0 certificate as control, both
profile lists, two revisions, and three checker-version tags. All order cases
must fail at the profile gate, before certificate replay or identity checking.
The order proof path is the separate `order` route below; these two routes have
no order proof path.

`Checks.lean` covers negative/large numerals, signed scaling, subtraction,
integer aliases, object/integer separation, undefined terms, rejected arithmetic
on objects, mixed predicate arguments, absent numeric tuples, empty user sorts,
user quantification and positive/negative countermodel checks. These are Lean
regressions, not the requested Python/Lean differential corpus.

`TableauChecks.lean` pins the Farkas checker on small certificates: a strict
bound, rejected negative multipliers, `2c = 1` closing only with gcd cuts (and
not with a wrong divisor), `t != u` by split, `P(c+1)` against `not P(1+c)`
closing only after certified `c+1 ≤ 1+c` and `1+c ≤ c+1`, rejected splits on
object comparisons, quantifier instantiation, the checker-version gate and the
order route's exact profile list.

The source/dependency audit scans every project Lean source and every named
theorem. Only the pre-existing standard allowlist (`propext`, `Classical.choice`,
`Quot.sound`) is permitted. The original v0 and closure theorem sources and both
existing certificate checkers are unchanged.
