import VE.Route.Layer
import VE.ClaimGraph
import VE.TableauExtendedChecker
import VE.Order.Tableau
import VE.Order.Consequence
import VE.Closure.Consequence

/-! The checker parameter of the route (PLAN-EXPAND2 3.4). `CertificateSound`
generalises `VE.Graph.CertificateSound` (lean/VE/ClaimGraph.lean) over the
statement type (the syntax the certificate predicate reads), its formula and the
formula's denotation (the semantics). The FOL, closure and order checkers are
instances, each proved by its existing soundness theorem; none of them is
rewritten. W4's Core checker is a later instance. -/
namespace VE.Route
universe u

/-- A certificate predicate is sound for an environment when every accepted
certificate proves consequence of its exact ordered premises. -/
def CertificateSound (L : Semantics.{u}) {Stmt Cert : Type} (formula : Stmt → L.Formula)
    (E : L.Env) (valid : Cert → List Stmt → Stmt → Prop) : Prop :=
  ∀ c ps r, valid c ps r → L.Entails E (ps.map formula) (formula r)

/-- A checker for one environment: syntax, a decidable certificate predicate
and its soundness contract. -/
structure Checker (L : Semantics.{u}) (E : L.Env) where
  Stmt : Type
  Cert : Type
  formula : Stmt → L.Formula
  valid : Cert → List Stmt → Stmt → Prop
  decidable : ∀ c ps r, Decidable (valid c ps r)
  sound : CertificateSound L formula E valid

/-- The v0 relational first-order logic. -/
def fol : Semantics.{u} where
  Env := VE.Environment
  Formula := VE.Formula
  Model := VE.Structure.{u}
  Admissible E S := S.Admissible E
  WellFormed E a := a.WellFormed E []
  Holds S a := a.denote S []

/-- The closure@0 logic: v0 structures, closure formulas. -/
def closure : Semantics.{u} where
  Env := VE.Environment
  Formula := VE.Closure.Formula
  Model := VE.Structure.{u}
  Admissible E S := S.Admissible E
  WellFormed E a := a.WellFormed E []
  Holds S a := a.denote S []

/-- The order@0 logic: user sorts plus standard integers. -/
def order : Semantics.{u} where
  Env := VE.Order.Environment
  Formula := VE.Order.Formula
  Model := VE.Order.Structure.{u}
  Admissible E S := S.Admissible E
  WellFormed E a := a.WellFormed E []
  Holds S a := a.denote S []

theorem fol_entails_iff (E : VE.Environment) (ps : List VE.Formula) (c : VE.Formula) :
    fol.{u}.Entails E ps c ↔ VE.Entails.{u} E ps c := Iff.rfl

theorem closure_entails_iff (E : VE.Environment) (ps : List VE.Closure.Formula)
    (c : VE.Closure.Formula) : closure.{u}.Entails E ps c ↔ VE.Closure.Entails.{u} E ps c := Iff.rfl

theorem order_entails_iff (E : VE.Order.Environment) (ps : List VE.Order.Formula)
    (c : VE.Order.Formula) : order.{u}.Entails E ps c ↔ VE.Order.Entails.{u} E ps c := Iff.rfl

/-- The claim-graph contract is literally the parametric one at FOL with
`Claim.formula` as the syntax projection. -/
theorem graph_certificateSound_iff {Cert : Type} (E : VE.Environment)
    (valid : VE.Graph.CertificatePredicate Cert) :
    VE.Graph.CertificateSound.{u} E valid ↔ CertificateSound fol.{u} VE.Graph.Claim.formula E valid :=
  Iff.rfl

/-- Instance 1 (FOL, claims): the production `tableauValid`, by the existing
`VE.Graph.tableau_certificateSound`. -/
theorem tableauValid_certificateSound (E : VE.Environment) :
    CertificateSound fol.{u} VE.Graph.Claim.formula E (VE.Graph.tableauValid E) :=
  (graph_certificateSound_iff E _).mp (VE.Graph.tableau_certificateSound E)

/-- FOL tableau validity on bare formulas, as the route checks elaborated premises. -/
def folValid (E : VE.Environment) (c : VE.Tableau.Certificate) (ps : List VE.Formula)
    (r : VE.Formula) : Prop :=
  VE.Tableau.checkCertificate E ps r c = true

/-- Instance 1' (FOL, formulas), by the existing `VE.Tableau.checkCertificate_sound`. -/
theorem folValid_certificateSound (E : VE.Environment) :
    CertificateSound fol.{u} id E (folValid E) := by
  intro c ps r h
  simpa using VE.Tableau.checkCertificate_sound E ps r c h

/-- The closure checker's certificate predicate. -/
def closureValid (E : VE.Environment) (c : VE.Closure.Tableau.Certificate)
    (ps : List VE.Closure.Formula) (r : VE.Closure.Formula) : Prop :=
  VE.Closure.Tableau.checkCertificate E ps r c = true

/-- Instance 2 (closure), by the existing `VE.Closure.Tableau.checkCertificate_sound`. -/
theorem closureValid_certificateSound (E : VE.Environment) :
    CertificateSound closure.{u} id E (closureValid E) := by
  intro c ps r h
  simpa using VE.Closure.Tableau.checkCertificate_sound E ps r c h

/-- The order checker's certificate predicate. -/
def orderValid (E : VE.Order.Environment) (c : VE.Order.Tableau.Certificate)
    (ps : List VE.Order.Formula) (r : VE.Order.Formula) : Prop :=
  VE.Order.Tableau.checkCertificate E ps r c = true

/-- Instance 3 (order), by the existing `VE.Order.Tableau.checkCertificate_sound`. -/
theorem orderValid_certificateSound (E : VE.Order.Environment) :
    CertificateSound order.{u} id E (orderValid E) := by
  intro c ps r h
  simpa using VE.Order.Tableau.checkCertificate_sound E ps r c h

/-- The three compiled checker instances. -/
def Checker.tableauClaims (E : VE.Environment) : Checker fol.{u} E where
  Stmt := VE.Graph.Claim
  Cert := VE.Tableau.Certificate
  formula := VE.Graph.Claim.formula
  valid := VE.Graph.tableauValid E
  decidable c ps r := inferInstanceAs (Decidable (VE.Graph.tableauValid E c ps r))
  sound := tableauValid_certificateSound E

def Checker.tableau (E : VE.Environment) : Checker fol.{u} E where
  Stmt := VE.Formula
  Cert := VE.Tableau.Certificate
  formula := id
  valid := folValid E
  decidable _ _ _ := inferInstanceAs (Decidable (_ = true))
  sound := folValid_certificateSound E

def Checker.closure (E : VE.Environment) : Checker closure.{u} E where
  Stmt := VE.Closure.Formula
  Cert := VE.Closure.Tableau.Certificate
  formula := id
  valid := closureValid E
  decidable _ _ _ := inferInstanceAs (Decidable (_ = true))
  sound := closureValid_certificateSound E

def Checker.order (E : VE.Order.Environment) : Checker order.{u} E where
  Stmt := VE.Order.Formula
  Cert := VE.Order.Tableau.Certificate
  formula := id
  valid := orderValid E
  decidable _ _ _ := inferInstanceAs (Decidable (_ = true))
  sound := orderValid_certificateSound E

end VE.Route
