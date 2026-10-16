import VE.SearchBudget.Demand

/-! # The premise check's search budget (premise-scale)

Lean owns the budget of the premise-consistency check (`ve/vacuity.py`, the readings route's
model search, the document mode): the proof-step, model and evaluation budgets, the domain bound
every sort is searched up to, and the per-sort bounds that raise it for the sorts whose premises
force more entities (`sortBounds`). A raised sort is searched at exactly its demand, so the
search starts where a model can be: by `demand_sound` no structure satisfying the premises has
fewer pairwise distinct elements of that sort, and a sort is raised only when its demand exceeds
the shared bound, so no model the shared bound admits is excluded. A sort whose demand exceeds
`sortCap` is not raised: its search stays at the shared bound (and finds no model there).

The budget steers an untrusted search: a model is reported only once Lean has checked it. -/
namespace VE.SearchBudget
open VE

/-- The premise check's budgets. -/
structure Budget where
  maxProofSteps : Nat
  domainSize : Nat
  maxModels : Nat
  maxEvaluations : Nat

def premiseBudget : Budget := ⟨10000, 2, 10000, 100000⟩

/-- The most entities a sort's search is raised to. -/
def sortCap : Nat := 8

/-- One sort's raised bounds: `(sort, least, most)`. -/
def sortBound (b : Budget) (cs : List (String × String)) (premises : List Formula) (s : String) :
    Option (String × Nat × Nat) :=
  let d := demand cs premises s
  if b.domainSize < d ∧ d ≤ sortCap then some (s, d, d) else none

/-- The sorts whose search is raised above the shared bound, each at its demand. -/
def sortBounds (b : Budget) (cs : List (String × String)) (premises : List Formula)
    (sorts : List String) : List (String × Nat × Nat) :=
  sorts.filterMap (sortBound b cs premises)

/-- Each raised sort is one of `sorts`, searched at exactly its demand, above the shared bound
and at most the cap. -/
theorem sortBounds_spec {b : Budget} {cs : List (String × String)} {premises : List Formula}
    {sorts : List String} {s : String} {least most : Nat}
    (h : (s, least, most) ∈ sortBounds b cs premises sorts) :
    s ∈ sorts ∧ least = demand cs premises s ∧ most = least ∧ b.domainSize < most ∧ most ≤ sortCap := by
  simp only [sortBounds, List.mem_filterMap, sortBound] at h
  obtain ⟨s', hs', he⟩ := h
  split at he
  · rename_i hc
    simp only [Option.some.injEq, Prod.mk.injEq] at he
    obtain ⟨rfl, rfl, rfl⟩ := he
    exact ⟨hs', rfl, rfl, hc.1, hc.2⟩
  · cases he

/-- A raised sort's least size is no more than any model of the premises has: every admissible
structure satisfying them has `least` pairwise distinct elements of the sort. -/
theorem sortBounds_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    {cs : List (String × String)} (hcs : ∀ c ∈ cs, E.constants c.1 = some c.2)
    {premises : List Formula} (hp : ∀ a ∈ premises, a.denote S [])
    {b : Budget} {sorts : List String} {s : String} {least most : Nat}
    (h : (s, least, most) ∈ sortBounds b cs premises sorts) :
    ∃ vs : List S.Carrier, vs.length = least ∧ vs.Nodup ∧ ∀ v ∈ vs, S.domain s v := by
  obtain ⟨_, hl, _⟩ := sortBounds_spec h
  exact hl ▸ demand_sound hS hcs hp s

/-- Distinct sorts give distinct raised rows. -/
theorem sortBounds_nodup {b : Budget} {cs : List (String × String)} {premises : List Formula}
    {sorts : List String} (h : sorts.Nodup) :
    ((sortBounds b cs premises sorts).map Prod.fst).Nodup := by
  unfold sortBounds
  induction sorts with
  | nil => exact List.Pairwise.nil
  | cons s ss ih =>
    rw [List.nodup_cons] at h
    simp only [List.filterMap_cons]
    cases hb : sortBound b cs premises s with
    | none => exact ih h.2
    | some r =>
      have hr : r.1 = s := by
        simp only [sortBound] at hb
        split at hb
        · cases hb; rfl
        · cases hb
      simp only [List.map_cons]
      refine List.nodup_cons.mpr ⟨fun hm => h.1 ?_, ih h.2⟩
      simp only [List.mem_map, List.mem_filterMap] at hm
      obtain ⟨⟨s', l, m⟩, ⟨x, hx, hxe⟩, rfl⟩ := hm
      have := sortBounds_spec (b := b) (cs := cs) (premises := premises) (sorts := ss)
        (List.mem_filterMap.mpr ⟨x, hx, hxe⟩)
      exact hr ▸ this.1

end VE.SearchBudget
