import Std

/-! The route contract of PLAN-EXPAND2 section 3.4: typed, environment-extending
layers over an abstract semantics. A layer extends an environment `E_in` to
`E_out`, generates premises over `E_out`, and proves two things about them:
`faithful` (the premises say exactly the reviewed `Intended` meaning on every
admissible output structure) and `expands` (every admissible structure of the
layer below has exactly one admissible expansion satisfying the premises). The
second is the model correspondence behind both proof and countermodel results.

Structures are not indexed by environments in this development (see
`VE.Structure.Admissible`), so a "structure of `E`" is a model together with an
admissibility predicate over it. Nothing here is checker code: the checker is a
parameter of the route (`VE.Route.Checker`). -/
namespace VE.Route
universe u

/-- An abstract logic presentation: environments, closed formulas, structures
at universe `u`, structural admissibility, closed well-formedness and closed
truth. The FOL, closure and order logics are instances (`VE.Route.Checker`). -/
structure Semantics where
  Env : Type
  Formula : Type
  Model : Type (u + 1)
  Admissible : Env → Model → Prop
  WellFormed : Env → Formula → Prop
  Holds : Model → Formula → Prop

/-- Exactly one element satisfies `P` (core Lean has no `∃!`). -/
def Unique {α : Sort _} (P : α → Prop) : Prop := ∃ x, P x ∧ ∀ y, P y → y = x

namespace Semantics
variable (L : Semantics.{u})

/-- Consequence over every admissible structure of the environment. For the
three instances this unfolds to the existing `Entails` relation. -/
def Entails (E : L.Env) (premises : List L.Formula) (conclusion : L.Formula) : Prop :=
  ∀ S, L.Admissible E S → (∀ a ∈ premises, L.Holds S a) → L.Holds S conclusion

/-- A structure satisfies every formula of a list. -/
def Sat (S : L.Model) (as : List L.Formula) : Prop := ∀ a ∈ as, L.Holds S a

theorem sat_append (S : L.Model) (as bs : List L.Formula) :
    L.Sat S (as ++ bs) ↔ L.Sat S as ∧ L.Sat S bs := by
  simp only [Sat, List.mem_append]
  constructor
  · intro h
    exact ⟨fun a ha => h a (Or.inl ha), fun a ha => h a (Or.inr ha)⟩
  · rintro ⟨h₁, h₂⟩ a (ha | ha)
    · exact h₁ a ha
    · exact h₂ a ha

end Semantics

/-- One statement-layer elaboration step, as frozen by PLAN-EXPAND2 3.4. The
fields beyond the plan's list (`extends_env`, `premises_wellFormed`,
`admissible_out`, `restrict_admissible`, `restrict_holds`) are the coherence
obligations that make layers composable and the route theorem provable; each is
a property the plan's prose already requires ("E_in ⊆ E_out", "premises over
E_out", "forget the new symbols", "every countermodel restricts to one"). -/
structure Layer (L : Semantics.{u}) (Doc : Type) where
  E_in : L.Env
  E_out : L.Env
  /-- `E_in ⊆ E_out`: every formula over the input vocabulary is one over the output. -/
  extends_env : ∀ a, L.WellFormed E_in a → L.WellFormed E_out a
  /-- Executable, over `E_out`; mirrored in Python; concatenated on the route. -/
  premises : Doc → List L.Formula
  premises_wellFormed : ∀ d, ∀ a ∈ premises d, L.WellFormed E_out a
  /-- Structures admissible for the layer below. -/
  Admissible_in : L.Model → Prop
  Admissible_out : L.Model → Prop
  admissible_out : ∀ S, Admissible_out S → L.Admissible E_out S
  /-- Forget the new symbols. -/
  restrict : L.Model → L.Model
  restrict_admissible : ∀ S, Admissible_out S → Admissible_in (restrict S)
  /-- Forgetting the new symbols does not change the truth of an old formula. -/
  restrict_holds : ∀ S a, Admissible_out S → L.WellFormed E_in a →
    (L.Holds (restrict S) a ↔ L.Holds S a)
  /-- The reviewed statement of meaning (statement review, rule 1b). -/
  Intended : Doc → L.Model → Prop
  faithful : ∀ d S, Admissible_out S →
    ((∀ a ∈ premises d, L.Holds S a) ↔ Intended d S)
  /-- Unique expansion: the model correspondence behind proof and countermodel results. -/
  expands : ∀ d S₀, Admissible_in S₀ →
    Unique fun S => restrict S = S₀ ∧ Admissible_out S ∧ ∀ a ∈ premises d, L.Holds S a

namespace Layer
variable {L : Semantics.{u}} {Doc : Type}

/-- The empty layer: no new symbols, no premises, meaning `True`. It is the
route of a document whose profiles generate no statement layer. -/
def id (E : L.Env) (A : L.Model → Prop) (hA : ∀ S, A S → L.Admissible E S) : Layer L Doc where
  E_in := E
  E_out := E
  extends_env _ h := h
  premises _ := []
  premises_wellFormed _ _ h := nomatch h
  Admissible_in := A
  Admissible_out := A
  admissible_out := hA
  restrict S := S
  restrict_admissible _ h := h
  restrict_holds _ _ _ _ := Iff.rfl
  Intended _ _ := True
  faithful _ _ _ := ⟨fun _ => trivial, fun _ _ h => nomatch h⟩
  expands _ S₀ h := ⟨S₀, ⟨rfl, h, fun _ h => nomatch h⟩, fun _ hS => hS.1⟩

/-- Restriction preserves a whole list of old formulas. -/
theorem sat_restrict (l : Layer L Doc) (S : L.Model) (h : l.Admissible_out S)
    (as : List L.Formula) (hw : ∀ a ∈ as, L.WellFormed l.E_in a) :
    L.Sat (l.restrict S) as ↔ L.Sat S as :=
  ⟨fun hs a ha => (l.restrict_holds S a h (hw a ha)).mp (hs a ha),
   fun hs a ha => (l.restrict_holds S a h (hw a ha)).mpr (hs a ha)⟩

section Comp
variable (l₁ l₂ : Layer L Doc) (hE : l₂.E_in = l₁.E_out)
  (hA : ∀ S, l₂.Admissible_in S ↔ l₁.Admissible_out S)
include hE hA
-- Every composition lemma takes both compatibility facts, so `comp` passes them uniformly.
set_option linter.unusedSectionVars false

theorem comp_extends (a : L.Formula) (h : L.WellFormed l₁.E_in a) : L.WellFormed l₂.E_out a :=
  l₂.extends_env a (hE ▸ l₁.extends_env a h)

theorem comp_premises_wellFormed (d : Doc) :
    ∀ a ∈ l₁.premises d ++ l₂.premises d, L.WellFormed l₂.E_out a := by
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact l₂.extends_env a (hE ▸ l₁.premises_wellFormed d a ha)
  · exact l₂.premises_wellFormed d a ha

theorem comp_restrict_admissible (S : L.Model) (h : l₂.Admissible_out S) :
    l₁.Admissible_in (l₁.restrict (l₂.restrict S)) :=
  l₁.restrict_admissible _ ((hA _).mp (l₂.restrict_admissible S h))

theorem comp_restrict_holds (S : L.Model) (a : L.Formula) (h : l₂.Admissible_out S)
    (ha : L.WellFormed l₁.E_in a) :
    L.Holds (l₁.restrict (l₂.restrict S)) a ↔ L.Holds S a :=
  (l₁.restrict_holds _ a ((hA _).mp (l₂.restrict_admissible S h)) ha).trans
    (l₂.restrict_holds S a h (hE ▸ l₁.extends_env a ha))

/-- Composition theorem, faithfulness half: on an admissible output structure
the concatenated premises hold iff the lower layer's meaning holds of the
restriction and the upper layer's meaning holds of the structure. -/
theorem comp_faithful (d : Doc) (S : L.Model) (h : l₂.Admissible_out S) :
    (∀ a ∈ l₁.premises d ++ l₂.premises d, L.Holds S a) ↔
      (l₁.Intended d (l₂.restrict S) ∧ l₂.Intended d S) := by
  have h₁ : l₁.Admissible_out (l₂.restrict S) := (hA _).mp (l₂.restrict_admissible S h)
  have hlow : L.Sat S (l₁.premises d) ↔ l₁.Intended d (l₂.restrict S) := by
    rw [← l₁.faithful d _ h₁]
    exact (l₂.sat_restrict S h (l₁.premises d)
      (fun a ha => hE ▸ l₁.premises_wellFormed d a ha)).symm
  have hs := L.sat_append S (l₁.premises d) (l₂.premises d)
  unfold Semantics.Sat at hs hlow
  rw [hs, hlow, l₂.faithful d S h]

/-- Composition theorem, expansion half: unique expansion composes. -/
theorem comp_expands (d : Doc) (S₀ : L.Model) (h : l₁.Admissible_in S₀) :
    Unique fun S => l₁.restrict (l₂.restrict S) = S₀ ∧ l₂.Admissible_out S ∧
      ∀ a ∈ l₁.premises d ++ l₂.premises d, L.Holds S a := by
  obtain ⟨S₁, ⟨hr₁, ha₁, hp₁⟩, hu₁⟩ := l₁.expands d S₀ h
  obtain ⟨S₂, ⟨hr₂, ha₂, hp₂⟩, hu₂⟩ := l₂.expands d S₁ ((hA S₁).mpr ha₁)
  have hw : ∀ a ∈ l₁.premises d, L.WellFormed l₂.E_in a :=
    fun a ha => hE ▸ l₁.premises_wellFormed d a ha
  refine ⟨S₂, ⟨by rw [hr₂, hr₁], ha₂, ?_⟩, ?_⟩
  · refine (L.sat_append S₂ _ _).mpr ⟨?_, hp₂⟩
    exact (l₂.sat_restrict S₂ ha₂ _ hw).mp (hr₂ ▸ hp₁)
  · rintro S ⟨hr, ha, hp⟩
    obtain ⟨hp₁', hp₂'⟩ := (L.sat_append S _ _).mp hp
    have hS₁ : l₂.restrict S = S₁ := by
      apply hu₁
      exact ⟨hr, (hA _).mp (l₂.restrict_admissible S ha),
        (l₂.sat_restrict S ha _ hw).mpr hp₁'⟩
    exact hu₂ S ⟨hS₁, ha, hp₂'⟩

/-- Sequential composition of two layers, innermost (`l₁`) first. The output
environment and admissibility of `l₁` must be exactly the input of `l₂`. -/
def comp : Layer L Doc where
  E_in := l₁.E_in
  E_out := l₂.E_out
  extends_env := comp_extends l₁ l₂ hE hA
  premises d := l₁.premises d ++ l₂.premises d
  premises_wellFormed := comp_premises_wellFormed l₁ l₂ hE hA
  Admissible_in := l₁.Admissible_in
  Admissible_out := l₂.Admissible_out
  admissible_out := l₂.admissible_out
  restrict S := l₁.restrict (l₂.restrict S)
  restrict_admissible := comp_restrict_admissible l₁ l₂ hE hA
  restrict_holds := comp_restrict_holds l₁ l₂ hE hA
  Intended d S := l₁.Intended d (l₂.restrict S) ∧ l₂.Intended d S
  faithful := comp_faithful l₁ l₂ hE hA
  expands := comp_expands l₁ l₂ hE hA

end Comp

/-- Consecutive layers agree on the environment and admissibility they share. -/
def Compatible : List (Layer L Doc) → Prop
  | [] | [_] => True
  | l₁ :: l₂ :: ls => l₂.E_in = l₁.E_out ∧ (∀ S, l₂.Admissible_in S ↔ l₁.Admissible_out S) ∧
      Compatible (l₂ :: ls)

/-- Fold a compatible chain into one layer, carrying the facts the next
composition step needs. -/
def composeAux : (l : Layer L Doc) → (ls : List (Layer L Doc)) → Compatible (l :: ls) →
    {r : Layer L Doc // r.E_in = l.E_in ∧ r.Admissible_in = l.Admissible_in}
  | l, [], _ => ⟨l, rfl, rfl⟩
  | l₁, l₂ :: ls, h =>
    let r := composeAux l₂ ls h.2.2
    ⟨comp l₁ r.1 (r.2.1.trans h.1) (fun S => by rw [r.2.2]; exact h.2.1 S), rfl, rfl⟩

/-- The route's layer: the chain composed innermost first. -/
def compose (l : Layer L Doc) (ls : List (Layer L Doc)) (h : Compatible (l :: ls)) : Layer L Doc :=
  (composeAux l ls h).1

/-- The composed premises are the concatenation of every layer's premises, in
route order. -/
theorem compose_premises (l : Layer L Doc) (ls : List (Layer L Doc)) (h : Compatible (l :: ls))
    (d : Doc) : (compose l ls h).premises d = (l :: ls).flatMap (fun x => x.premises d) := by
  induction ls generalizing l with
  | nil => simp [compose, composeAux]
  | cons l₂ ls ih =>
    have := ih l₂ h.2.2
    simp only [compose] at this
    simp [compose, composeAux, comp, this]

end Layer
end VE.Route
