import VE.Bridge

namespace VE.Bridge

theorem lookup_mem (xs : List (String × α)) (key : String) (value : α)
    (h : lookup xs key = some value) : (key, value) ∈ xs := by
  induction xs with
  | nil => simp [lookup] at h
  | cons x xs ih =>
    by_cases he : x.1 = key
    · simp [lookup, he] at h
      exact List.mem_cons.mpr (Or.inl (Prod.ext he.symm h.symm))
    · have hb : (x.1 == key) = false := beq_eq_false_iff_ne.mpr he
      exact List.mem_cons.mpr (Or.inr (ih (by simpa [lookup, List.find?_cons, hb] using h)))

theorem tupleCheck_iff (M : FiniteModel Entity) (ss : List String) (xs : List Entity) :
    tupleCheck M ss xs = true ↔ TupleTyped M.asStructure ss xs := by
  induction ss generalizing xs with
  | nil => cases xs <;> simp [tupleCheck, TupleTyped]
  | cons s ss ih => cases xs <;> simp [tupleCheck, TupleTyped, FiniteModel.asStructure, ih]

/-- The executable semantic gate implies admissibility, including every declared
constant and every true relation tuple, with no uniqueness-of-names premise. -/
theorem modelData_valid (d : ModelData) (v : Vocabulary) (h : d.valid v = true) :
    d.toModel.Valid v.environment := by
  simp only [ModelData.valid, Bool.and_eq_true, List.all_eq_true] at h
  constructor
  · intro c s hc
    have hm := h.1 (c, s) (lookup_mem v.constants c s hc)
    cases hx : d.toModel.constants c with
    | none => simp [hx] at hm
    | some x =>
      exact ⟨x, hx, by simpa [hx, FiniteModel.asStructure] using hm⟩
  · intro p xs hxs
    change xs ∈ (lookup d.relations p).getD [] at hxs
    cases hr : lookup d.relations p with
    | none => simp [hr] at hxs
    | some rows =>
      have hm := h.2 (p, rows) (lookup_mem d.relations p rows hr)
      cases hp : v.environment.predicates p with
      | none => simp [hp] at hm
      | some ss =>
        refine ⟨ss, rfl, (tupleCheck_iff d.toModel ss xs).mp ?_⟩
        exact (List.all_eq_true.mp (by simpa [hp] using hm)) xs (by simpa [hr] using hxs)

/-- Successful decoding entails the exact validity premise used by P11. No
assumption about earlier JSON decoding or vocabulary validation is required. -/
theorem decodeModel_valid (v : Vocabulary) (j : Lean.Json) (M : FiniteModel Entity)
    (h : decodeModel v j = .ok M) : M.Valid v.environment := by
  unfold decodeModel at h
  cases hd : decodeModelData v j with
  | error e => simp [hd, Except.bind, bind] at h
  | ok d =>
    simp only [hd, bind, Except.bind] at h
    split at h
    · cases h
      exact modelData_valid d v (by assumption)
    · contradiction

/-- JSON entities live in Type 0. This refutes precisely Entails.{0}, including
infinite admissible Type 0 structures; it is not a bounded-search assertion. -/
theorem decoded_countermodel_sound (v : Vocabulary) (j : Lean.Json)
    (M : FiniteModel Entity) (decoded : decodeModel v j = .ok M)
    (premises : List Formula) (conclusion : Formula)
    (checked : countermodelCheck M premises conclusion = true) :
    ¬ Entails.{0} v.environment premises conclusion :=
  countermodel_sound M (decodeModel_valid v j M decoded) premises conclusion checked

/-- The executable query type makes closure and typing explicit. Every decoded
model passing this query check refutes the universe-0 certificate target. -/
theorem CountermodelQuery.refutes_sound (v : Vocabulary) (j : Lean.Json)
    (M : FiniteModel Entity) (decoded : decodeModel v j = .ok M)
    (q : CountermodelQuery v.environment) (checked : q.refutes M = true) :
    (∀ a ∈ q.premises, a.WellFormed v.environment []) ∧
    q.conclusion.WellFormed v.environment [] ∧
    ¬ JsonEntails v.environment q.premises q.conclusion :=
  ⟨q.premises_typed, q.conclusion_typed,
    decoded_countermodel_sound v j M decoded q.premises q.conclusion checked⟩

end VE.Bridge
