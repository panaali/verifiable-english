import VE.Core.Conservativity
import VE.Route.Checker
import VE.Route.Gate
import VE.Route.Route

namespace VE.Route
universe u

/-- Core uses the same structures as closure, with n-ary relation tables. -/
def core : Semantics.{u} where
  Env := VE.Environment
  Formula := VE.Core.Formula
  Model := VE.Structure.{u}
  Admissible E S := S.Admissible E
  WellFormed E a := a.WellFormed E []
  Holds S a := a.denote S []

theorem core_entails_iff (E : VE.Environment) (ps : List VE.Core.Formula)
    (c : VE.Core.Formula) :
    core.{u}.Entails E ps c ↔ VE.Core.Entails.{u} E ps c := Iff.rfl

def coreValid (E : VE.Environment) (c : VE.Core.Tableau.Certificate)
    (ps : List VE.Core.Formula) (r : VE.Core.Formula) : Prop :=
  VE.Core.Tableau.checkCertificate E ps r c = true

/-- The Core instance of P0's frozen checker contract. -/
theorem coreValid_certificateSound (E : VE.Environment) :
    CertificateSound core.{u} id E (coreValid E) := by
  intro c ps r h
  simpa using VE.Core.Tableau.checkCertificate_sound E ps r c h

def Checker.core (E : VE.Environment) : Checker core.{u} E where
  Stmt := VE.Core.Formula
  Cert := VE.Core.Tableau.Certificate
  formula := id
  valid := coreValid E
  decidable _ _ _ := inferInstanceAs (Decidable (_ = true))
  sound := coreValid_certificateSound E

theorem core_family_gate :
    Gate.classify ["closure@0", "nary@0", "relational-fol@0"] =
      .ok .closureNary := by rfl

/-- The Core checker is sound when installed in P0's identity route: an
accepted certificate proves the statement in every admissible model. -/
theorem core_route_acceptance (E : VE.Environment) (ps : List VE.Core.Formula)
    (r : VE.Core.Formula) (c : VE.Core.Tableau.Certificate)
    (h : VE.Core.Tableau.checkCertificate E ps r c = true) :
    core.{u}.Entails E ps r := by
  let R : Layer core.{u} Unit := Layer.id E (fun S => S.Admissible E) (fun _ hS => hS)
  have hbg : BackgroundSound R [] := by
    intro _ _ _ _ _ ha
    cases ha
  have hps : ps.map (Checker.core E).formula = checkedPremises R [] () ps := by
    simp [Checker.core, checkedPremises, R, Layer.id]
  exact (route_acceptance R [] hbg (Checker.core E) () ps r c ps r h hps rfl).1

end VE.Route
