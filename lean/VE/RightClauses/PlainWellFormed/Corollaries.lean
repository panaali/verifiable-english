import VE.RightClauses.Relation
import VE.RightClauses.PlainWellFormed

/-! The theorems of `Relation.lean` that assume `WellFormedRights (plain D)`, with that hypothesis discharged by
`plain_wellFormed` (8.3): it holds whenever the structured lines check (`WellFormedClauses D`), the rights document
is well formed and `validateRights (plain D)` does not fail with a `ResourceLimit: ` error (`hr`), the one outcome
8.3 leaves open. Relation.lean is unchanged (DRI adv0947 item 4). -/
namespace VE.RightClauses
open VE.Norms (Sat tupleVal)
open VE.Rights (RightsDoc Line linesOf holderSlot sortsOf dutyKind ownGuard narrowings NarrowsAt owes SelectsRN
  WellFormedRights validateRights limPremisesLabelled)
universe u

/-- `plain D` is well formed when `D.doc` is and its check reports no resource limit. -/
theorem plain_wellFormedRights (D : ClauseDoc) (h : WellFormedClauses D = true) (h0 : WellFormedRights D.doc = true)
    (hr : ¬ ∃ e, validateRights (plain D) = .error e ∧ "ResourceLimit: ".isPrefixOf e = true) :
    WellFormedRights (plain D) = true :=
  (plain_wellFormed D h h0).resolve_right hr

theorem clauseSlot_labelled_of_doc (D : ClauseDoc) (h : WellFormedClauses D = true)
    (h0 : WellFormedRights D.doc = true)
    (hr : ¬ ∃ e, validateRights (plain D) = .error e ∧ "ResourceLimit: ".isPrefixOf e = true)
    (hl : VE.Compose.Labelled.wellLabelled (limPremisesLabelled D.doc) = true) :
    VE.Compose.Labelled.wellLabelled (clauseSlotLabelled D) = true :=
  clauseSlot_labelled D h (plain_wellFormedRights D h h0 hr) hl

theorem clause_fails_not_selected_of_doc (D : ClauseDoc) (h : WellFormedClauses D = true)
    (h0 : WellFormedRights D.doc = true)
    (hr : ¬ ∃ e, validateRights (plain D) = .error e ∧ "ResourceLimit: ".isPrefixOf e = true)
    (R n : String) (L : CLine) (hL : (R, n, L) ∈ D.lines) (N : Line) (hN : (R, N) ∈ linesOf (plain D))
    (hn : N.node.name = n) (S : VE.Structure.{u}) (vs : List S.Carrier) (typed : VE.TupleTyped S (sortsOf (plain D) N) vs)
    (hf : (∃ c ∈ L.clauses, ¬ c.formula.denote S (tupleVal vs)) ∨
          (∃ rel, L.relation = some rel ∧ ¬ (relAtom (sortsOf (plain D) N).length rel).denote S (tupleVal vs))) :
    ¬ SelectsRN (plain D) S (tupleVal vs) N :=
  clause_fails_not_selected D h (plain_wellFormedRights D h h0 hr) R n L hL N hN hn S vs typed hf

theorem relation_some_bearer_of_doc (D : ClauseDoc) (h : WellFormedClauses D = true)
    (h0 : WellFormedRights D.doc = true)
    (hr : ¬ ∃ e, validateRights (plain D) = .error e ∧ "ResourceLimit: ".isPrefixOf e = true)
    (R n : String) (L : CLine) (hL : (R, n, L) ∈ D.lines) (N : Line) (hN : (R, N) ∈ linesOf (plain D))
    (hn : N.node.name = n) (hk : dutyKind N = true) (rel : Relation) (hrel : L.relation = some rel)
    (ht : rel.total = some (holderSlot (plain D) N)) (hs : rel.slots = (0, holderSlot (plain D) N))
    (S : VE.Structure.{u}) (hS : Sat S (relPremises D))
    (sh : String) (hsh : (sortsOf (plain D) N)[holderSlot (plain D) N]? = some sh)
    (hv : S.Carrier) (hd : S.domain sh hv) (hH : (holderGuardOf D R).denote S [hv]) :
    ∃ bv, (∃ sb, (sortsOf (plain D) N).head? = some sb ∧ S.domain sb bv) ∧ S.relation rel.pred [bv, hv] ∧
      ∀ vs, VE.TupleTyped S (sortsOf (plain D) N) vs → vs.head? = some bv →
        vs[holderSlot (plain D) N]? = some hv →
        (ownGuard (plain D) N).denote S (tupleVal vs) →
        (¬ ∃ m ∈ narrowings (plain D) N, NarrowsAt (plain D) S (tupleVal vs) N m) →
        owes (plain D) S N vs :=
  relation_some_bearer D h (plain_wellFormedRights D h h0 hr) R n L hL N hN hn hk rel hrel ht hs S hS sh hsh hv hd hH

end VE.RightClauses
