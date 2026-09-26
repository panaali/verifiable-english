import VE.Route.Examples
import VE.Route.Route

/-! A first concrete definition layer.  This file handles a fresh unary
predicate named by an existing unary predicate.  The general body decoder and
its identity-bound declaration remain outside this file. -/
namespace VE.Definitions
universe u

/-- Executable elaboration of a unary alias as a closed biconditional. -/
def expand (p q s : String) : List VE.Formula := [VE.Route.Examples.body p q s]

/-- The alias definition extends the vocabulary and uses the frozen Layer. -/
def aliasLayer (E : VE.Environment) (p q s : String)
    (hs : s ∈ E.sorts) (hp : E.predicates p = none)
    (hq : E.predicates q = some [s]) (hpq : q ≠ p) :
    VE.Route.Layer VE.Route.fol.{u} Unit :=
  VE.Route.Examples.copyLayer E p q s hs hp hq hpq

/-- The generated biconditional says exactly that the new predicate and its
body agree at every point of the declared sort. -/
theorem faithful (p q s : String) (S : VE.Structure.{u}) :
    (∀ a ∈ expand p q s, a.denote S []) ↔
      (∀ v, S.domain s v → (S.relation p [v] ↔ S.relation q [v])) := by
  simpa [expand] using VE.Route.Examples.body_holds_iff S (p := p) (q := q) (s := s)

/-- Every input structure has exactly one admissible expansion interpreting
the fresh predicate by its body. -/
theorem conservative (E : VE.Environment) (p q s : String)
    (hp : E.predicates p = none) (hpq : q ≠ p)
    (S₀ : VE.Structure.{u}) (hS₀ : S₀.Admissible E) :
    VE.Route.Unique fun S =>
      VE.Route.Examples.forget p S = S₀ ∧
      S.Admissible (VE.Route.Examples.extend E p s) ∧
      ∀ a ∈ expand p q s, a.denote S [] := by
  simpa [expand] using VE.Route.Examples.copy_expands hp hpq S₀ hS₀

/-- An accepted certificate using the elaborated definition proves every
old-vocabulary conclusion in every old structure satisfying the old premises. -/
theorem alias_acceptance (E : VE.Environment) (p q s : String)
    (hs : s ∈ E.sorts) (hp : E.predicates p = none)
    (hq : E.predicates q = some [s]) (hpq : q ≠ p)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed E []) (hφ : φ.WellFormed E [])
    (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (VE.Route.Examples.extend E p s)
      (expand p q s ++ Γ) φ c = true) :
    VE.Entails.{u} E Γ φ := by
  let R := aliasLayer E p q s hs hp hq hpq
  have he : VE.Route.fol.Entails R.E_out
      (VE.Route.checkedPremises R [] () Γ) φ := by
    have h := VE.Tableau.checkCertificate_sound
      (VE.Route.Examples.extend E p s) (expand p q s ++ Γ) φ c accepted
    simpa [R, aliasLayer, expand, VE.Route.checkedPremises, VE.Route.fol,
      VE.Route.Examples.copyLayer] using h
  intro S₀ hS₀ hPremises
  exact VE.Route.route_base R [] (fun _ _ _ _ _ h => nomatch h)
    () Γ φ hΓ hφ he S₀ hS₀ hPremises

end VE.Definitions
