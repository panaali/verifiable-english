import VE.Cardinality.Wire
import VE.Compose.Dispatch

/-! The `cardinality@0` row of AR-10's profile table (SYNTHESIS 2.2; quantities 4.2, E2). The batch that adds a row
proves the composition theorem for every list the row newly admits: the table admits a list with `cardinality@0`
exactly when the cardinality decoder's E2 does (one of W6a's two lists beside it, or the chain list). -/
namespace VE.Cardinality
open VE.Compose

/-- A strictly increasing list whose members a strictly increasing list holds is a sublist of it. -/
theorem sublist_of_sorted : ∀ {l m : List String}, l.Pairwise (· < ·) → m.Pairwise (· < ·) →
    (∀ x ∈ l, x ∈ m) → l.Sublist m
  | [], _, _, _, _ => List.nil_sublist _
  | a :: _, [], _, _, h => absurd (h a (List.mem_cons_self ..)) List.not_mem_nil
  | a :: l, b :: m, hl, hm, h => by
    have hl' := List.pairwise_cons.mp hl
    have hm' := List.pairwise_cons.mp hm
    by_cases hab : a = b
    · subst hab
      refine (sublist_of_sorted hl'.2 hm'.2 fun x hx => ?_).cons₂ a
      rcases List.mem_cons.mp (h x (List.mem_cons_of_mem _ hx)) with e | hx'
      · exact absurd (e ▸ hl'.1 x hx) (String.lt_irrefl _)
      · exact hx'
    · have hba : b < a := hm'.1 a ((List.mem_cons.mp (h a (List.mem_cons_self ..))).resolve_left hab)
      refine (sublist_of_sorted hl hm'.2 fun x hx => ?_).cons b
      rcases List.mem_cons.mp (h x hx) with e | hx'
      · subst e
        rcases List.mem_cons.mp hx with e | hx''
        · exact absurd e.symm hab
        · exact absurd (String.lt_trans hba (hl'.1 _ hx'')) (String.lt_irrefl _)
      · exact hx'

/-- The gate admits a list with `cardinality@0` exactly when E2 does (`Wire.profileLists`), on the route `routeOf` names:
the frozen one under W6a's lists, whose checker no list with `cardinality@0` reaches (the `cardinality` mode decodes
those environments itself), and the readings wrapper's under the chain list, which the document mode reads by two
projections (quantities 4.1; DRI 2026-11-05, reviews/dri-decisions-20261105-qt-a4b.md item 1). A list that also has the
document layer `judgments@0` is admitted exactly as the same list without it (`gate_judgments`), which this theorem then
decides. -/
theorem gate_cardinality (ps : List String) (h : "cardinality@0" ∈ ps) (hj : "judgments@0" ∉ ps) (r : Route) :
    gateOf profileTable ps = .ok r ↔
      ps ∈ Wire.profileLists ∧ r = (if ps = Wire.chainProfiles then .readings else .frozen) := by
  have hlists : ∀ qs ∈ Wire.profileLists,
      gateOf profileTable qs = .ok (if qs = Wire.chainProfiles then .readings else .frozen) := by
    intro qs hq
    simp only [Wire.profileLists, VE.Time.Wire.w6Profiles, List.map_cons, List.map_nil, List.cons_append,
      List.nil_append, List.mem_cons, List.not_mem_nil, or_false] at hq
    rcases hq with rfl | rfl | rfl <;> rfl
  constructor
  · intro hg
    have hp : ps ∈ Wire.profileLists := by
      have hl := ((gateOf_iff _ _ _).mp hg).1.2.2.2 h
      rwa [List.erase_of_not_mem hj] at hl
    have he := hg.symm.trans (hlists ps hp)
    exact ⟨hp, Except.ok.inj he⟩
  · rintro ⟨hp, rfl⟩
    exact hlists ps hp

end VE.Cardinality
