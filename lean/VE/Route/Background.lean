import VE.Route.Gate
import VE.ModelProofs
import VE.Closure.Finite

/-! Background premises on the Lean route (PLAN-EXPAND2 3.1). Background is
regenerated here from the decoded declarations, never read from the wire. P0
implements the `literals` generator (one `¬(l1 = l2)` per pair of declared
`$string` constants); the `flags` (W5), `definitions` (W3) and `profile` (W1)
generators contribute nothing until their workstreams land.

The reviewed stage-1 meaning of strings is `StringAdmissible`: an admissible
structure in which distinct declared literals denote distinct elements. The
route instances below take it as the admissibility of the base layer, so each
enabled route has its end-to-end acceptance theorem: an accepted certificate
for `Background ++ Γ ⊢ φ` means `φ` holds in every string-admissible structure
satisfying `Γ`, and a checked finite countermodel refutes it. -/
namespace VE.Route.Background
universe u

def stringSort : String := "$string"

/-- The generators, in Background order. -/
def generators : List String := ["flags", "definitions", "literals", "profile"]

/-- Pairs `(xᵢ, xⱼ)` with `i < j`, in list order. -/
def pairs : List String → List (String × String)
  | [] => []
  | x :: xs => xs.map (fun y => (x, y)) ++ pairs xs

def literalPremise (p : String × String) : VE.Formula := .not (.eq (.const p.1) (.const p.2))

/-- The `literals` generator: the sorted declared literals, one distinctness
premise per pair. -/
def literals (lits : List String) : List VE.Formula := (pairs (sortStrings lits)).map literalPremise

/-- Background(env) with each premise's generator. Only `literals` is non-empty in P0. -/
def background (lits : List String) : List (VE.Formula × String) :=
  (literals lits).map (fun a => (a, "literals"))

/-- The stage-1 meaning of `$string` literals (statement review, rule 1b). -/
def LiteralsDistinct (S : VE.Structure.{u}) (lits : List String) : Prop :=
  ∀ a ∈ lits, ∀ b ∈ lits, a ≠ b → ∀ v, S.constant a = some v → S.constant b ≠ some v

def StringAdmissible (E : VE.Environment) (lits : List String) (S : VE.Structure.{u}) : Prop :=
  S.Admissible E ∧ LiteralsDistinct S lits

theorem mem_pairs {l : List String} {a b : String} (h : (a, b) ∈ pairs l) :
    a ∈ l ∧ b ∈ l ∧ (l.Nodup → a ≠ b) := by
  induction l with
  | nil => simp [pairs] at h
  | cons x xs ih =>
    simp only [pairs, List.mem_append, List.mem_map, Prod.mk.injEq] at h
    rcases h with ⟨y, hy, rfl, rfl⟩ | h
    · exact ⟨List.mem_cons_self, List.mem_cons_of_mem _ hy,
        fun hn he => (List.nodup_cons.mp hn).1 (he ▸ hy)⟩
    · obtain ⟨ha, hb, hn⟩ := ih h
      exact ⟨List.mem_cons_of_mem _ ha, List.mem_cons_of_mem _ hb,
        fun hn' => hn (List.nodup_cons.mp hn').2⟩

theorem pairs_complete {l : List String} {a b : String} (ha : a ∈ l) (hb : b ∈ l) (hne : a ≠ b) :
    (a, b) ∈ pairs l ∨ (b, a) ∈ pairs l := by
  induction l with
  | nil => simp at ha
  | cons x xs ih =>
    simp only [pairs, List.mem_append, List.mem_map, Prod.mk.injEq]
    rcases List.mem_cons.mp ha with rfl | ha' <;> rcases List.mem_cons.mp hb with rfl | hb'
    · exact absurd rfl hne
    · exact Or.inl (Or.inl ⟨b, hb', rfl, rfl⟩)
    · exact Or.inr (Or.inl ⟨a, ha', rfl, rfl⟩)
    · rcases ih ha' hb' with h | h
      · exact Or.inl (Or.inr h)
      · exact Or.inr (Or.inr h)

theorem mem_sortStrings (l : List String) (x : String) : x ∈ sortStrings l ↔ x ∈ l := by
  simp [sortStrings, List.mem_mergeSort]

theorem literalPremise_denote (S : VE.Structure.{u}) (p : String × String) :
    (literalPremise p).denote S [] ↔
      ∀ v, S.constant p.1 = some v → S.constant p.2 ≠ some v := by
  simp [literalPremise, VE.Formula.denote, VE.Term.denote]

/-- The generated premises say exactly the stage-1 meaning of strings, for any
duplicate-free list of literals (vocabulary names are unique). -/
theorem literals_sat_iff (S : VE.Structure.{u}) (lits : List String) (hn : lits.Nodup) :
    (∀ a ∈ literals lits, a.denote S []) ↔ LiteralsDistinct S lits := by
  have hsn : (sortStrings lits).Nodup :=
    (List.mergeSort_perm lits _).symm.nodup_iff.mp hn
  constructor
  · intro h a ha b hb hne v hv hv'
    rcases pairs_complete ((mem_sortStrings lits a).mpr ha) ((mem_sortStrings lits b).mpr hb) hne
      with hp | hp
    · exact (literalPremise_denote S _).mp (h _ (List.mem_map.mpr ⟨_, hp, rfl⟩)) v hv hv'
    · exact (literalPremise_denote S _).mp (h _ (List.mem_map.mpr ⟨_, hp, rfl⟩)) v hv' hv
  · intro h f hf
    obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hf
    obtain ⟨ha, hb, hne⟩ := mem_pairs hp
    exact (literalPremise_denote S p).mpr (h p.1 ((mem_sortStrings lits _).mp ha)
      p.2 ((mem_sortStrings lits _).mp hb) (hne hsn))

/-- Finite-model validity for `literals`: the executable check evaluates the
regenerated Background in the supplied model; `true` means the model satisfies
the stage-1 meaning of strings. -/
def literalsValid {α : Type u} [DecidableEq α] (M : VE.FiniteModel α) (lits : List String) : Bool :=
  (literals lits).all (fun a => a.eval M [])

theorem literalsValid_sound {α : Type u} [DecidableEq α] (M : VE.FiniteModel α)
    (lits : List String) (hn : lits.Nodup) (h : literalsValid M lits = true) :
    LiteralsDistinct M.asStructure lits := by
  apply (literals_sat_iff M.asStructure lits hn).mp
  intro a ha
  exact (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp h a ha)

/-- A model that fails the check aliases two declared literals, so rejecting it
as `InvalidModel("literals")` rejects exactly the invalid models. -/
theorem literalsValid_complete {α : Type u} [DecidableEq α] (M : VE.FiniteModel α)
    (lits : List String) (hn : lits.Nodup) (h : LiteralsDistinct M.asStructure lits) :
    literalsValid M lits = true := by
  apply List.all_eq_true.mpr
  intro a ha
  exact (VE.eval_iff_denote M [] a).mpr ((literals_sat_iff M.asStructure lits hn).mpr h a ha)

/-! ## Route instances for the three compiled checker families -/

/-- The FOL route of P0: no statement layer yet, base admissibility is
`StringAdmissible`, Background is `literals`. -/
def folLayer (E : VE.Environment) (lits : List String) : Layer fol.{u} Unit :=
  Layer.id E (StringAdmissible E lits) (fun _ h => h.1)

theorem fol_background_sound (E : VE.Environment) (lits : List String) (hn : lits.Nodup) :
    BackgroundSound (folLayer.{u} E lits) (literals lits) :=
  fun _ S hS _ => (literals_sat_iff S lits hn).mpr hS.2

theorem fol_background_complete (E : VE.Environment) (lits : List String) (hn : lits.Nodup) :
    BackgroundComplete (folLayer.{u} E lits) (literals lits) :=
  fun _ S hS hb _ => ⟨hS, (literals_sat_iff S lits hn).mp hb⟩

/-- Consequence over string-admissible structures. -/
def EntailsString (E : VE.Environment) (lits : List String) (Γ : List VE.Formula)
    (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, StringAdmissible E lits S → (∀ a ∈ Γ, a.denote S []) → φ.denote S []

/-- The FOL route's acceptance theorem: an accepted tableau certificate for
`literals ++ Γ ⊢ φ` proves `φ` over every string-admissible structure. -/
theorem fol_route_acceptance (E : VE.Environment) (lits : List String) (hn : lits.Nodup)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate E (literals lits ++ Γ) φ c = true) :
    VE.Entails.{u} E (literals lits ++ Γ) φ ∧ EntailsString.{u} E lits Γ φ := by
  have he : VE.Entails.{u} E (literals lits ++ Γ) φ :=
    VE.Tableau.checkCertificate_sound E _ φ c accepted
  refine ⟨he, fun S hS hΓ => ?_⟩
  have h := route_intended (folLayer.{u} E lits) (literals lits) (fol_background_sound E lits hn)
    () Γ φ (by simpa [checkedPremises, folLayer, Layer.id] using he) S hS trivial hΓ
  exact h

/-- Model correspondence on the FOL route: the checked entailment is exactly
consequence over string-admissible structures. -/
theorem fol_route_entails_iff (E : VE.Environment) (lits : List String) (hn : lits.Nodup)
    (Γ : List VE.Formula) (φ : VE.Formula) :
    VE.Entails.{u} E (literals lits ++ Γ) φ ↔ EntailsString.{u} E lits Γ φ := by
  have := route_entails_iff (folLayer.{u} E lits) (literals lits) (fol_background_sound E lits hn)
    (fol_background_complete E lits hn) () Γ φ
  constructor
  · intro h S hS hΓ
    apply route_intended (folLayer.{u} E lits) (literals lits) (fol_background_sound E lits hn)
      () Γ φ (by simpa [checkedPremises, folLayer, Layer.id] using h) S hS trivial hΓ
  · intro h S hS hs
    have hs' : ∀ a ∈ literals lits ++ Γ, a.denote S [] := hs
    have hb : ∀ a ∈ literals lits, a.denote S [] := fun a ha => hs' a (List.mem_append_left _ ha)
    exact h S ⟨hS, (literals_sat_iff S lits hn).mp hb⟩ (fun a ha => hs' a (List.mem_append_right _ ha))

/-- A checked finite countermodel that passes the literal check refutes the
string-admissible statement: NO survives on the route. -/
theorem fol_route_countermodel {α : Type u} [DecidableEq α] (E : VE.Environment) (lits : List String)
    (hn : lits.Nodup) (M : VE.FiniteModel α) (valid : M.Valid E) (hl : literalsValid M lits = true)
    (Γ : List VE.Formula) (φ : VE.Formula) (checked : VE.countermodelCheck M Γ φ = true) :
    ¬ EntailsString.{u} E lits Γ φ ∧ ¬ VE.Entails.{u} E (literals lits ++ Γ) φ := by
  obtain ⟨hp, hc⟩ := (VE.countermodelCheck_iff M Γ φ).mp checked
  have hs : ¬ EntailsString.{u} E lits Γ φ :=
    fun h => hc (h M.asStructure ⟨valid, literalsValid_sound M lits hn hl⟩ hp)
  exact ⟨hs, fun h => hs ((fol_route_entails_iff E lits hn Γ φ).mp h)⟩

/-- The closure route: closure formulas, Background embedded unchanged. -/
theorem closure_route_acceptance (E : VE.Environment) (lits : List String) (hn : lits.Nodup)
    (Γ : List VE.Closure.Formula) (φ : VE.Closure.Formula) (c : VE.Closure.Tableau.Certificate)
    (accepted : VE.Closure.Tableau.checkCertificate E ((literals lits).map VE.Closure.embed ++ Γ) φ c = true) :
    ∀ S : VE.Structure.{u}, StringAdmissible E lits S → (∀ a ∈ Γ, a.denote S []) → φ.denote S [] := by
  intro S hS hΓ
  apply VE.Closure.Tableau.checkCertificate_sound E _ φ c accepted S hS.1
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · obtain ⟨b, hb, rfl⟩ := List.mem_map.mp ha
    exact (VE.Closure.conservativity S [] b).mpr ((literals_sat_iff S lits hn).mpr hS.2 b hb)
  · exact hΓ a ha

/-- The order route without declared literals: Background is empty and the
route is the order checker itself (the `lits = []` case of
`order_string_route_acceptance` below). -/
theorem order_route_acceptance (E : VE.Order.Environment) (Γ : List VE.Order.Formula)
    (φ : VE.Order.Formula) (c : VE.Order.Tableau.Certificate)
    (accepted : VE.Order.Tableau.checkCertificate E ([] ++ Γ) φ c = true) :
    VE.Order.Entails.{u} E Γ φ := by
  simpa using VE.Order.Tableau.checkCertificate_sound E _ φ c accepted

/-! ## The order route with `$string` literals

`$string` literals are available on every checker family (PLAN-EXPAND2 3.1: the
`literals` generator depends on the environment only). On order@0 a literal is
a constant of the user sort `$string`, which is never in the environment's
`sorts`, so it is never quantified over; Background is the same distinctness
premises, over order formulas. -/

def orderLiteralPremise (p : String × String) : VE.Order.Formula := .not (.eq (.const p.1) (.const p.2))

/-- The `literals` generator on the order route: the same sorted pairs. -/
def orderLiterals (lits : List String) : List VE.Order.Formula :=
  (pairs (sortStrings lits)).map orderLiteralPremise

/-- The stage-1 meaning of `$string` literals over order structures. -/
def OrderLiteralsDistinct (S : VE.Order.Structure.{u}) (lits : List String) : Prop :=
  ∀ a ∈ lits, ∀ b ∈ lits, a ≠ b → ∀ v, S.constant a = some v → S.constant b ≠ some v

def OrderStringAdmissible (E : VE.Order.Environment) (lits : List String) (S : VE.Order.Structure.{u}) :
    Prop :=
  S.Admissible E ∧ OrderLiteralsDistinct S lits

theorem orderLiteralPremise_denote (S : VE.Order.Structure.{u}) (p : String × String) :
    (orderLiteralPremise p).denote S [] ↔
      ∀ v, S.constant p.1 = some v → S.constant p.2 ≠ some v := by
  simp [orderLiteralPremise, VE.Order.Formula.denote, VE.Order.Term.denote]

/-- The generated order premises say exactly the stage-1 meaning of strings. -/
theorem orderLiterals_sat_iff (S : VE.Order.Structure.{u}) (lits : List String) (hn : lits.Nodup) :
    (∀ a ∈ orderLiterals lits, a.denote S []) ↔ OrderLiteralsDistinct S lits := by
  have hsn : (sortStrings lits).Nodup :=
    (List.mergeSort_perm lits _).symm.nodup_iff.mp hn
  constructor
  · intro h a ha b hb hne v hv hv'
    rcases pairs_complete ((mem_sortStrings lits a).mpr ha) ((mem_sortStrings lits b).mpr hb) hne
      with hp | hp
    · exact (orderLiteralPremise_denote S _).mp (h _ (List.mem_map.mpr ⟨_, hp, rfl⟩)) v hv hv'
    · exact (orderLiteralPremise_denote S _).mp (h _ (List.mem_map.mpr ⟨_, hp, rfl⟩)) v hv' hv
  · intro h f hf
    obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hf
    obtain ⟨ha, hb, hne⟩ := mem_pairs hp
    exact (orderLiteralPremise_denote S p).mpr (h p.1 ((mem_sortStrings lits _).mp ha)
      p.2 ((mem_sortStrings lits _).mp hb) (hne hsn))

/-- Finite-model validity for `literals` on the order route. -/
def orderLiteralsValid {α : Type u} [DecidableEq α] (M : VE.Order.FiniteModel α) (lits : List String) :
    Bool :=
  (orderLiterals lits).all (fun a => a.eval M [])

theorem orderLiteralsValid_sound {α : Type u} [DecidableEq α] (M : VE.Order.FiniteModel α)
    (lits : List String) (hn : lits.Nodup) (h : orderLiteralsValid M lits = true) :
    OrderLiteralsDistinct M.asStructure lits := by
  apply (orderLiterals_sat_iff M.asStructure lits hn).mp
  intro a ha
  exact (VE.Order.eval_iff_denote M [] a).mp (List.all_eq_true.mp h a ha)

/-- Consequence over string-admissible order structures. -/
def EntailsOrderString (E : VE.Order.Environment) (lits : List String) (Γ : List VE.Order.Formula)
    (φ : VE.Order.Formula) : Prop :=
  ∀ S : VE.Order.Structure.{u}, OrderStringAdmissible E lits S → (∀ a ∈ Γ, a.denote S []) → φ.denote S []

/-- Model correspondence on the order route: the checked entailment over
`literals ++ Γ` is exactly consequence over string-admissible order structures. -/
theorem order_string_route_entails_iff (E : VE.Order.Environment) (lits : List String) (hn : lits.Nodup)
    (Γ : List VE.Order.Formula) (φ : VE.Order.Formula) :
    VE.Order.Entails.{u} E (orderLiterals lits ++ Γ) φ ↔ EntailsOrderString.{u} E lits Γ φ := by
  constructor
  · intro h S hS hΓ
    apply h S hS.1
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact (orderLiterals_sat_iff S lits hn).mpr hS.2 a ha
    · exact hΓ a ha
  · intro h S hS hs
    exact h S ⟨hS, (orderLiterals_sat_iff S lits hn).mp
      (fun a ha => hs a (List.mem_append_left _ ha))⟩ (fun a ha => hs a (List.mem_append_right _ ha))

/-- The order route's acceptance theorem with literals: an accepted order
certificate for `literals ++ Γ ⊢ φ` proves `φ` over every string-admissible
order structure satisfying `Γ`. -/
theorem order_string_route_acceptance (E : VE.Order.Environment) (lits : List String) (hn : lits.Nodup)
    (Γ : List VE.Order.Formula) (φ : VE.Order.Formula) (c : VE.Order.Tableau.Certificate)
    (accepted : VE.Order.Tableau.checkCertificate E (orderLiterals lits ++ Γ) φ c = true) :
    VE.Order.Entails.{u} E (orderLiterals lits ++ Γ) φ ∧ EntailsOrderString.{u} E lits Γ φ := by
  have he : VE.Order.Entails.{u} E (orderLiterals lits ++ Γ) φ :=
    VE.Order.Tableau.checkCertificate_sound E _ φ c accepted
  exact ⟨he, (order_string_route_entails_iff E lits hn Γ φ).mp he⟩

/-- A checked finite order countermodel that passes the literal check refutes
the string-admissible statement. -/
theorem order_string_route_countermodel {α : Type u} [DecidableEq α] (E : VE.Order.Environment)
    (lits : List String) (hn : lits.Nodup) (M : VE.Order.FiniteModel α) (valid : M.Valid E)
    (hl : orderLiteralsValid M lits = true) (Γ : List VE.Order.Formula) (φ : VE.Order.Formula)
    (checked : VE.Order.countermodelCheck M Γ φ = true) :
    ¬ EntailsOrderString.{u} E lits Γ φ ∧ ¬ VE.Order.Entails.{u} E (orderLiterals lits ++ Γ) φ := by
  obtain ⟨hp, hc⟩ := (VE.Order.countermodelCheck_iff M Γ φ).mp checked
  have hs : ¬ EntailsOrderString.{u} E lits Γ φ :=
    fun h => hc (h M.asStructure ⟨valid, orderLiteralsValid_sound M lits hn hl⟩ hp)
  exact ⟨hs, fun h => hs ((order_string_route_entails_iff E lits hn Γ φ).mp h)⟩

end VE.Route.Background
