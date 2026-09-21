import VE.TableauChecker
import VE.TableauClosure
import VE.Tableau
import VE.Consequence
import VE.SurfaceProofs
import VE.EnvironmentProofs
import VE.ParserContracts
import VE.GraphChecks
import VE.ModelProofs

#print axioms VE.term_defined
#print axioms VE.typed_empty
#print axioms VE.typed_cons
#print axioms VE.check_iff_wellFormed

#print axioms VE.eval_iff_denote
#print axioms VE.eval_false_iff_not_denote
#print axioms VE.document_eval_iff_denote

#print axioms VE.composition_sound
#print axioms VE.entails_cut
#print axioms VE.countermodelCheck_iff
#print axioms VE.countermodel_sound
#print axioms VE.no_certificate_countermodel_conflict

#print axioms VE.Surface.propositional_printAux
#print axioms VE.Surface.propositional_check
#print axioms VE.Surface.consume_append
#print axioms VE.Surface.propositional_depth_le_length
#print axioms VE.Surface.parseRaw_propositional
#print axioms VE.Surface.propositional_code_nonempty
#print axioms VE.Surface.parseStatements_nonempty
#print axioms VE.Surface.parseStatements_propositional
#print axioms VE.Surface.propositional_document_length
#print axioms VE.Surface.parse_print_propositional
#print axioms VE.Surface.normalize_idempotent_propositional

#print axioms VE.Surface.decimal_digit
#print axioms VE.Surface.digitsCore_valid
#print axioms VE.Surface.digitsCore_value
#print axioms VE.Surface.digitsCore_nonempty
#print axioms VE.Surface.canonicalName_generated
#print axioms VE.Surface.canonicalName_injective
#print axioms VE.Surface.generated_identifier
#print axioms VE.Surface.canonicalName_identifier
#print axioms VE.Surface.generated_not_reserved
#print axioms VE.Surface.span_ident_loop
#print axioms VE.Surface.span_ident_append
#print axioms VE.Surface.readIdent_append

#print axioms VE.Surface.scope_mono
#print axioms VE.Surface.scope_fresh
#print axioms VE.Surface.scope_cons
#print axioms VE.Surface.canonical_binderAllowed
#print axioms VE.Surface.printAux_counter
#print axioms VE.Surface.index_lookup
#print axioms VE.Surface.parseTerm_print
#print axioms VE.Surface.printTerm_head
#print axioms VE.Surface.parseRaw_term
#print axioms VE.Surface.consume_sound
#print axioms VE.Surface.consume_keyword_ne
#print axioms VE.Surface.declaration_identifier
#print axioms VE.Surface.declaration_not_reserved
#print axioms VE.Surface.depth_le_print_length
#print axioms VE.Surface.parseRaw_print
#print axioms VE.Surface.document_length
#print axioms VE.Surface.parseStatements_print
#print axioms VE.Surface.parse_print
#print axioms VE.Surface.parse_wellFormed
#print axioms VE.Surface.normalize_idempotent

#print axioms VE.Bridge.lookup_name
#print axioms VE.Bridge.vocabulary_namesValid

#print axioms VE.Surface.accepted_normalize
#print axioms VE.Surface.accepted_reparse
#print axioms VE.Surface.print_injective
#print axioms VE.Surface.canonical_unique
#print axioms VE.Surface.accepted_normalize_eq_iff
#print axioms VE.Surface.normalize_print

#print axioms VE.Graph.acyclicCheck_dependency
#print axioms VE.Graph.path_rank
#print axioms VE.Graph.acyclicCheck_sound
#print axioms VE.Graph.lookup_sound
#print axioms VE.Graph.resolve_sound
#print axioms VE.Graph.checkNode_sound
#print axioms VE.Graph.checkNodes_sound
#print axioms VE.Graph.check_sound
#print axioms VE.Graph.check_entails
#print axioms VE.Graph.check_unfolds

#print axioms VE.GraphChecks.testCertificate_sound

#print axioms VE.Bridge.lookup_mem
#print axioms VE.Bridge.tupleCheck_iff
#print axioms VE.Bridge.modelData_valid
#print axioms VE.Bridge.decodeModel_valid
#print axioms VE.Bridge.decoded_countermodel_sound
#print axioms VE.Bridge.CountermodelQuery.refutes_sound

#print axioms VE.Tableau.token_defined
#print axioms VE.Tableau.bindings_extend
#print axioms VE.Tableau.holds_extend
#print axioms VE.Tableau.typed_extend
#print axioms VE.Tableau.add_holds
#print axioms VE.Tableau.one_holds
#print axioms VE.Tableau.two_holds
#print axioms VE.Tableau.gamma_holds
#print axioms VE.Tableau.delta_witness

#print axioms VE.Tableau.bindings_get
#print axioms VE.Tableau.termToken_denote
#print axioms VE.Tableau.ground_denote
#print axioms VE.Tableau.literals_hold
#print axioms VE.Tableau.mem_dedup
#print axioms VE.Tableau.equalities_sound
#print axioms VE.Tableau.grow_sound
#print axioms VE.Tableau.reachable_sound
#print axioms VE.Tableau.equivalent_sound
#print axioms VE.Tableau.matches_sound
#print axioms VE.Tableau.closes_sound
#print axioms VE.Tableau.closed_sound

#print axioms VE.Tableau.next_sound
#print axioms VE.Tableau.checkChildren_member
#print axioms VE.Tableau.replay_sound
#print axioms VE.Tableau.checkCertificate_sound
