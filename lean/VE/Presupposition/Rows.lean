import VE.Presupposition.Reading
import VE.Discourse.Descriptions

/-! # Trigger rows (docs/spec/presupposition.md 4.4)

The three rows of presupposition@0: a definite description (discourse's builders, opened over
the hole's context), a plural description (`∃x:σ D`) and a generic trigger whose `pre` is
given. Each is defined (`strong ↔ pre ∧ weak`) at every typed valuation. `buildReading` and
`buildPre` take the row's arguments from the wire as one tuple, and an error names the field. -/
namespace VE.Presupposition
universe u

def definite (n : Nat) (σ : String) (D P : VE.Formula) : Reading :=
  { pre := VE.Discourse.uniqueOpen n σ D, strong := VE.Discourse.assertiveOpen n σ D P,
    weak := VE.Discourse.presupposed σ D P }

def plural (σ : String) (D P : VE.Formula) : Reading :=
  { pre := .ex σ D, strong := .and (.ex σ D) (.all σ (.implies D P)), weak := .all σ (.implies D P) }

def generic (pre body : VE.Formula) : Reading :=
  { pre := pre, strong := .and pre body, weak := .implies pre body }

/-- `raise1` at the hole's context: the weakened restriction at `b :: a :: τ` reads `D` at `b :: τ`. -/
theorem raise1_denote (E : VE.Environment) (Δ : List String) (σ : String) (D : VE.Formula)
    (hD : D.WellFormed E (σ :: Δ)) (S : VE.Structure.{u}) (τ : VE.Valuation S)
    (hτ : VE.Valuation.Typed S Δ τ) (a b : S.Carrier) :
    (VE.Discourse.raise1 Δ.length D).denote S (b :: a :: τ) ↔ D.denote S (b :: τ) := by
  have hlen : Δ.length ≤ τ.length := Nat.le_of_not_lt fun h => by
    obtain ⟨v, hv, _⟩ := hτ τ.length Δ[τ.length] (List.getElem?_eq_getElem h)
    simp at hv
  have hden : VE.Norms.Denotes S (b :: a :: τ)
      (.var 0 :: (List.range Δ.length).map (fun i => .var (i + 2))) (b :: τ.take Δ.length) := by
    refine ⟨by simp [hlen], fun i h₁ h₂ => ?_⟩
    cases i with
    | zero => rfl
    | succ i =>
      simp only [List.length_cons, List.length_take, List.length_map, List.length_range] at h₁ h₂
      simp [VE.Term.denote, List.getElem_take, List.getElem?_eq_getElem (show i < τ.length by omega)]
  rw [VE.Discourse.raise1, VE.Norms.inst_denote S E D (σ :: Δ) _ _ _ hD (by simp [hlen]) hden]
  exact VE.Discourse.denote_prefix D (σ :: Δ) _ _ hD fun i hi => by
    cases i with
    | zero => rfl
    | succ i =>
      simp only [List.length_cons] at hi
      simp [show i < Δ.length by omega]

/-- Generalises `VE.Discourse.description_definedness` (the case `Δ = []`, `τ = []`). -/
theorem definite_defined (E : VE.Environment) (Δ : List String) (σ : String) (hσ : σ ∈ E.sorts)
    (D P : VE.Formula) (hD : D.WellFormed E (σ :: Δ)) (hP : P.WellFormed E (σ :: Δ))
    (S : VE.Structure.{u}) (hS : S.Admissible E) (τ : VE.Valuation S) (hτ : VE.Valuation.Typed S Δ τ) :
    (definite Δ.length σ D P).DefinedAt S τ := by
  simp only [Reading.DefinedAt, definite, VE.Discourse.uniqueOpen, VE.Discourse.assertiveOpen,
    VE.Discourse.uniqueAt, VE.Discourse.assertiveAt, VE.Discourse.presupposed, VE.Formula.denote,
    VE.Term.denote, List.getElem?_cons_zero, List.getElem?_cons_succ, Option.some.injEq,
    raise1_denote E Δ σ D hD S τ hτ]
  constructor
  · rintro ⟨a, ha, hDa, hu, hPa⟩
    refine ⟨⟨a, ha, hDa, hu⟩, fun b hb hDb => ?_⟩
    obtain ⟨v, rfl, rfl⟩ := hu b hb hDb
    exact hPa
  · rintro ⟨⟨a, ha, hDa, hu⟩, hp⟩
    exact ⟨a, ha, hDa, hu, hp a ha hDa⟩

theorem plural_defined (σ : String) (D P : VE.Formula) (S : VE.Structure.{u}) (τ : VE.Valuation S) :
    (plural σ D P).DefinedAt S τ :=
  Iff.rfl

theorem generic_defined (pre body : VE.Formula) (S : VE.Structure.{u}) (τ : VE.Valuation S) :
    (generic pre body).DefinedAt S τ :=
  ⟨fun ⟨hp, hb⟩ => ⟨hp, fun _ => hb⟩, fun ⟨hp, hb⟩ => ⟨hp, hb hp⟩⟩

/-- The arguments as one tuple: `(sort, restriction, body, pre)`. Errors name the field. -/
def buildReading (row : String) (n : Nat) (a : Option String × Option VE.Formula × Option VE.Formula ×
    Option VE.Formula) : Except String Reading :=
  match row, a with
  | "definite", (some σ, some D, some P, none) => .ok (definite n σ D P)
  | "plural", (some σ, some D, some P, none) => .ok (plural σ D P)
  | "generic", (none, none, some b, some p) => .ok (generic p b)
  | "definite", _ | "plural", _ | "generic", _ => .error "arguments"
  | _, _ => .error "row"

/-- What a trigger in a rule's act takes for granted; a rule's act has no `body`. -/
def buildPre (row : String) (n : Nat) (a : Option String × Option VE.Formula × Option VE.Formula ×
    Option VE.Formula) : Except String VE.Formula :=
  match row, a with
  | "definite", (some σ, some D, none, none) => .ok (VE.Discourse.uniqueOpen n σ D)
  | "plural", (some σ, some D, none, none) => .ok (.ex σ D)
  | "generic", (none, none, none, some p) => .ok p
  | "definite", (_, _, some _, _) | "plural", (_, _, some _, _) | "generic", (_, _, some _, _) => .error "body"
  | "definite", _ | "plural", _ | "generic", _ => .error "arguments"
  | _, _ => .error "row"

end VE.Presupposition
