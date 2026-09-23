import VE.Order.Consequence

/-! Executable admissibility for finite order presentations.

`Environment` and `FiniteModel` use functions for declarations, constants and
relations, so validity over them quantifies over every string and is not
decidable as stated. Wire data is finite: a vocabulary is a declaration list
and a model is a set of finite tables, exactly as in v0's `Bridge.ModelData`.
`validModel?` decides `FiniteModel.Valid` for the presentations these tables
denote, in both directions and with no side conditions (duplicate keys, sort
names and `$int` spellings are all allowed; lookup takes the first entry). -/
namespace VE.Order
universe u

/-- First-entry lookup, as `Bridge.lookup`, at every universe. -/
def lookup {β : Type u} (xs : List (String × β)) (k : String) : Option β :=
  (xs.find? (fun x => x.1 == k)).map Prod.snd

theorem lookup_mem {β : Type u} (xs : List (String × β)) (key : String) (value : β)
    (h : lookup xs key = some value) : (key, value) ∈ xs := by
  induction xs with
  | nil => simp [lookup] at h
  | cons x xs ih =>
    by_cases he : x.1 = key
    · simp [lookup, he] at h
      exact List.mem_cons.mpr (Or.inl (Prod.ext he.symm h.symm))
    · have hb : (x.1 == key) = false := beq_eq_false_iff_ne.mpr he
      exact List.mem_cons.mpr (Or.inr (ih (by simpa [lookup, List.find?_cons, hb] using h)))

/-- A finite order declaration inventory. -/
structure Vocabulary where
  sorts : List String
  predicates : List (String × List SortName)
  constants : List (String × SortName)

def Vocabulary.environment (v : Vocabulary) : Environment :=
  ⟨v.sorts, lookup v.predicates, lookup v.constants⟩

/-- Finite tables for an order countermodel. Integers occur only as actual
`Int` values in constants and relation rows; no integer domain is listed. -/
structure ModelData (α : Type u) where
  domains : List (String × List α)
  constants : List (String × Value α)
  relations : List (String × List (List (Value α)))

def ModelData.toModel {α : Type u} (d : ModelData α) : FiniteModel α where
  domains s := (lookup d.domains s).getD []
  constants := lookup d.constants
  relations p := (lookup d.relations p).getD []

def domainCheck {α : Type u} [DecidableEq α] (M : FiniteModel α) :
    SortName → Value α → Bool
  | .user s, .inl x => decide (x ∈ M.domains s)
  | .int, .inr _ => true
  | _, _ => false

def tupleCheck {α : Type u} [DecidableEq α] (M : FiniteModel α) :
    List SortName → List (Value α) → Bool
  | [], [] => true
  | s :: ss, x :: xs => domainCheck M s x && tupleCheck M ss xs
  | _, _ => false

/-- Every declared constant is interpreted in its sort, and every stored row of
every relation table is typed by that predicate's declared signature. -/
def validModel? {α : Type u} [DecidableEq α] (v : Vocabulary) (d : ModelData α) : Bool :=
  v.constants.all (fun (c, _) =>
    match v.environment.constants c, d.toModel.constants c with
    | some s, some x => domainCheck d.toModel s x
    | _, _ => false) &&
  d.relations.all (fun (p, _) => (d.toModel.relations p).all (fun xs =>
    match v.environment.predicates p with
    | some ss => tupleCheck d.toModel ss xs
    | none => false))

/-- The complete end-to-end countermodel gate for finite wire tables. -/
def checkCountermodel {α : Type u} [DecidableEq α] (v : Vocabulary) (d : ModelData α)
    (premises : List Formula) (conclusion : Formula) : Bool :=
  validModel? v d && countermodelCheck d.toModel premises conclusion

theorem lookup_isSome {β : Type u} {xs : List (String × β)} {k : String} {x : β}
    (h : (k, x) ∈ xs) : ∃ y, lookup xs k = some y := by
  induction xs with
  | nil => cases h
  | cons e xs ih =>
    by_cases he : e.1 = k
    · exact ⟨e.2, by simp [lookup, he]⟩
    · have hb : (e.1 == k) = false := beq_eq_false_iff_ne.mpr he
      rcases List.mem_cons.mp h with h | h
      · subst h; exact absurd rfl he
      · obtain ⟨y, hy⟩ := ih h
        exact ⟨y, by simpa [lookup, List.find?_cons, hb] using hy⟩

theorem domainCheck_iff {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (s : SortName) (x : Value α) :
    domainCheck M s x = true ↔ M.asStructure.domain s x := by
  cases s <;> cases x <;> simp [domainCheck, Structure.domain]

theorem tupleCheck_iff {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ss : List SortName) (xs : List (Value α)) :
    tupleCheck M ss xs = true ↔ TupleTyped M.asStructure ss xs := by
  induction ss generalizing xs with
  | nil => cases xs <;> simp [tupleCheck, TupleTyped]
  | cons s ss ih => cases xs <;> simp [tupleCheck, TupleTyped, domainCheck_iff, ih]

/-- The executable check holds exactly when the finite tables denote a valid
presentation of the vocabulary's environment: both directions, all inputs. -/
theorem validModel_iff {α : Type u} [DecidableEq α] (v : Vocabulary) (d : ModelData α) :
    validModel? v d = true ↔ d.toModel.Valid v.environment := by
  simp only [validModel?, Bool.and_eq_true, List.all_eq_true]
  constructor
  · rintro ⟨hc, hr⟩
    constructor
    · intro c s hs
      have hm := hc (c, s) (lookup_mem v.constants c s hs)
      simp only [hs] at hm
      cases hx : d.toModel.constants c with
      | none => simp [hx] at hm
      | some x =>
        simp only [hx] at hm
        exact ⟨x, hx, (domainCheck_iff _ s x).mp hm⟩
    · intro p xs hxs
      change xs ∈ (lookup d.relations p).getD [] at hxs
      cases hl : lookup d.relations p with
      | none => simp [hl] at hxs
      | some rows =>
        have hm := hr (p, rows) (lookup_mem d.relations p rows hl) xs
          (by simpa [ModelData.toModel, hl] using hxs)
        cases hp : v.environment.predicates p with
        | none => simp [hp] at hm
        | some ss =>
          simp only [hp] at hm
          exact ⟨ss, rfl, (tupleCheck_iff _ ss xs).mp hm⟩
  · rintro ⟨hc, hr⟩
    constructor
    · rintro ⟨c, s'⟩ hmem
      obtain ⟨s, hs⟩ := lookup_isSome hmem
      obtain ⟨x, hx, hd⟩ := hc c s hs
      change (match v.environment.constants c, d.toModel.constants c with
        | some s, some x => domainCheck d.toModel s x
        | _, _ => false) = true
      rw [show v.environment.constants c = some s from hs,
        show d.toModel.constants c = some x from hx]
      exact (domainCheck_iff _ s x).mpr hd
    · rintro ⟨p, rows⟩ _ xs hxs
      obtain ⟨ss, hp, ht⟩ := hr p xs hxs
      rw [hp]
      exact (tupleCheck_iff _ ss xs).mpr ht

/-- The Boolean countermodel gate accepts exactly valid tables in which every
premise is true and the conclusion is false. -/
theorem checkCountermodel_iff {α : Type u} [DecidableEq α] (v : Vocabulary)
    (d : ModelData α) (premises : List Formula) (conclusion : Formula) :
    checkCountermodel v d premises conclusion = true ↔
      d.toModel.Valid v.environment ∧
      (∀ a ∈ premises, a.denote d.toModel.asStructure []) ∧
      ¬ conclusion.denote d.toModel.asStructure [] := by
  simp only [checkCountermodel, Bool.and_eq_true, validModel_iff, countermodelCheck_iff]

/-- End to end, with no validity premise: if the executable gate accepts finite
tables, the premises do not entail the conclusion over every admissible
structure (finite or infinite) in the tables' universe. -/
theorem checkCountermodel_sound {α : Type u} [DecidableEq α] (v : Vocabulary)
    (d : ModelData α) (premises : List Formula) (conclusion : Formula)
    (h : checkCountermodel v d premises conclusion = true) :
    ¬ Entails.{u} v.environment premises conclusion := by
  simp only [checkCountermodel, Bool.and_eq_true] at h
  exact countermodel_sound d.toModel v.environment premises conclusion
    ((validModel_iff v d).mp h.1) h.2

end VE.Order
