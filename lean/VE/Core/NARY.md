# nary@0 Core theorem statement review

Core consequence means: for every structure admissible for the declared environment, if every premise is true under the empty valuation, the conclusion is true under that valuation. N-ary extensions are sets of ordered tuples; repeated arguments are permitted. Only user sorts occur in n-ary positions.

The inherited closure tableau rules are copied into `VE.Core`; the new relation atom and its positional congruence case are proved in the same recursive soundness argument. The v0, closure, and order checkers remain unchanged.

## Headline statements

The proof obligations that enable the route are stated here in plain words.

- `VE.Core.Tableau.checkCertificate_sound`: An accepted Core tableau certificate proves that its exact ordered premises entail its conclusion in every admissible structure.
- `VE.Core.Tableau.tokenListMatches_sound`: Equalities established on a branch may substitute arguments at every position of an n-ary atom.
- `VE.Core.check_iff_wellFormed`: The executable Core type check succeeds exactly when the independent well-formedness predicate holds, including positional sorts and the arity cap.
- `VE.Core.embedClosure_check`: Embedding a closure formula in Core preserves its executable type-check result.
- `VE.Core.embedClosure_denote`: Embedding a closure formula in Core preserves its truth in every structure and valuation.
- `VE.Core.entails_closure`: A Core entailment of embedded closure formulas yields the same closure consequence.
- `VE.Core.entails_v0`: A Core entailment of embedded v0 formulas yields the same v0 consequence.
- `VE.Core.eval_iff_denote`: Finite-table evaluation returns true exactly when the formula is true in the corresponding mathematical structure.
- `VE.Route.coreValid_certificateSound`: The new Core checker satisfies P0’s parameterized checker-soundness contract.
- `VE.Route.core_family_gate`: The declared closure plus n-ary profile list selects the Core checker family.
- `VE.Route.core_route_acceptance`: When the Core checker accepts a certificate on the identity statement route, its exact ordered premises entail its conclusion in every admissible structure.
- `VE.Core.Wire.run_certificate_acceptance`: If the Core wire runner accepts a certificate case and returns `valid: true`, the runner has checked the certificate's identity binding to the decoded environment, ordered user premises and regenerated literal premises, and the decoded conclusion follows in every admissible structure satisfying those generated premises and the user premises. The theorem is polymorphic over structure universes; its decoding hypotheses name the exact wire values returned by the decoders.

## Path and reachability helpers

These lemmas characterize finite paths, reflexive and transitive closure, and the finite Warshall computation; they relate each executable edge or pivot operation to the corresponding mathematical path relation.

- `VE.Core.Path.first`
- `VE.Core.Path.last`
- `VE.Core.Path.least`
- `VE.Core.Path.trans`
- `VE.Core.Path.unfold`
- `VE.Core.Tableau.mem_dedup`
- `VE.Core.Tableau.reachable_sound`
- `VE.Core.edge_inclusion`
- `VE.Core.endEdge_sound`
- `VE.Core.mem_bodyEdges`
- `VE.Core.mem_dedup`
- `VE.Core.mem_namedEdges`
- `VE.Core.mem_pivot`
- `VE.Core.pair_values`
- `VE.Core.path_iff`
- `VE.Core.pivot_closed`
- `VE.Core.pivot_preserves_closed`
- `VE.Core.reachEval_iff`
- `VE.Core.reach_compose`
- `VE.Core.reach_denote`
- `VE.Core.reachable_congr`
- `VE.Core.reachable_iff`
- `VE.Core.reachable_induction`
- `VE.Core.reachable_trans`
- `VE.Core.star_least`
- `VE.Core.warshall_closed`
- `VE.Core.warshall_extends`
- `VE.Core.warshall_iff_path`
- `VE.Core.warshall_preserves_closed`
- `VE.Core.warshall_sound`

## Tableau helpers

Each listed lemma establishes that the named tableau operation preserves a satisfiable branch, reflects a true ground literal, or closes only an impossible branch. Together they support the certificate-soundness theorem above.

- `VE.Core.Tableau.add_holds`
- `VE.Core.Tableau.bindings_extend`
- `VE.Core.Tableau.bindings_get`
- `VE.Core.Tableau.checkCertificate_sound_v0`
- `VE.Core.Tableau.checkChildren_member`
- `VE.Core.Tableau.closed_sound`
- `VE.Core.Tableau.closes_sound`
- `VE.Core.Tableau.closure_holds`
- `VE.Core.Tableau.complementary_sound`
- `VE.Core.Tableau.composeStep_sound`
- `VE.Core.Tableau.delta_witness`
- `VE.Core.Tableau.edgeStep_sound`
- `VE.Core.Tableau.endStep_sound`
- `VE.Core.Tableau.equalities_sound`
- `VE.Core.Tableau.equivalent_sound`
- `VE.Core.Tableau.extra_sound`
- `VE.Core.Tableau.gamma_holds`
- `VE.Core.Tableau.ground_denote`
- `VE.Core.Tableau.grow_sound`
- `VE.Core.Tableau.holds_extend`
- `VE.Core.Tableau.induct_sound`
- `VE.Core.Tableau.known_bindings`
- `VE.Core.Tableau.literals_hold`
- `VE.Core.Tableau.matches_sound`
- `VE.Core.Tableau.namedStep_sound`
- `VE.Core.Tableau.next_sound`
- `VE.Core.Tableau.one_holds`
- `VE.Core.Tableau.reachClosed_sound`
- `VE.Core.Tableau.replay_sound`
- `VE.Core.Tableau.rule_closure_formula`
- `VE.Core.Tableau.step_sound`
- `VE.Core.Tableau.termToken_denote`
- `VE.Core.Tableau.termTokens_denote`
- `VE.Core.Tableau.token_defined`
- `VE.Core.Tableau.two_holds`
- `VE.Core.Tableau.typed_extend`
- `VE.Core.Tableau.unfoldAt_sound`

## Surface, typing, and semantics helpers

These lemmas establish strict print/parse correspondence, substitution and embedding preservation, finite countermodel correctness, and denotation or typing equivalence for the named operation.

- `VE.Core.Surface.parseRaw_print_named`
- `VE.Core.Surface.parseStatements_nonempty`
- `VE.Core.Surface.parse_print_named`
- `VE.Core.Surface.print_injective_named`
- `VE.Core.closure_induction`
- `VE.Core.conservativity`
- `VE.Core.conservativity_without_reach`
- `VE.Core.countermodelCheck_iff`
- `VE.Core.countermodel_sound`
- `VE.Core.edge_at_denote`
- `VE.Core.edge_shift_denote`
- `VE.Core.edge_typed`
- `VE.Core.embed_of_erase`
- `VE.Core.erase_embed`
- `VE.Core.eval_false_iff_not_denote`
- `VE.Core.formula_matches_sound`
- `VE.Core.inductionStep_denote`
- `VE.Core.invariantAt_denote`
- `VE.Core.liftMatch_sound`
- `VE.Core.liftSub_denote`
- `VE.Core.liftTerm_denote`
- `VE.Core.named_body_denote`
- `VE.Core.substTerm_denote`
- `VE.Core.subst_denote`
- `VE.Core.termsMatch_sound`
- `VE.Core.unfold_denote`
- `VE.Core.unlift_denote`
- `VE.Route.core_entails_iff`

## Authoring status

Explicit n-ary English templates with three to six ordered, single-use placeholders round-trip under the all-derivations check. The generic `ve assist` offering is **strict only** until W8’s fidelity gate approves its suggestion and disambiguation hooks. Strict `p(t1, ..., tk)` is writable now. Integer-time n-ary arguments belong to stage 2.
