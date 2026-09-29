import VE.Attribution.Content

/-! The independent semantics of `reports@0` (spec 4.2): source models `(S, J, A)`
with arbitrary typed attitude and assessment relations, satisfaction of a
statement by recursion on the statement grammar, the intended meaning of a
document, and the two directions of the typed model correspondence with
`E_reports` structures (`interp`, `restrictJ`, spec 4.3). -/
namespace VE.Reports
open VE.Route (fol Layer)
open VE.Definitions (forget hide)
universe u

/-- 4.2: the independent semantics, typed by the key's sort. -/
structure Source (D : ReportDoc) where
  S : VE.Structure.{u}
  /-- act, holder sort, context id, complement id -/
  J : Act → String → String → String → S.Carrier → Prop
  /-- judgment, assessment id, content id -/
  A : Judgment → String → String → S.Carrier → Prop
  J_typed : ∀ a s c q v, J a s c q v → S.domain s v
  A_typed : ∀ j a q v, A j a q v → S.domain D.evidence v

/-- 4.2: satisfaction of a statement, by recursion on the statement grammar.
Nested nodes are contents: the recursion stops at a report or assessment node
and never visits its body. -/
def Sat (D : ReportDoc) (M : Source.{u} D) : Content → Prop
  | .report h act c b lit =>
      ∀ s, holderSort D h = some s → ∀ v, M.S.constant h = some v → M.J act s c (complementId D b lit) v
  | .assessment j a b =>
      ∀ r, recordOf D a = some r → ∀ v, M.S.constant r.context = some v → M.A j a (contentId D b) v
  | .negated n => ¬ Sat D M n
  | _ => True

def IntendedReports (D : ReportDoc) (M : Source.{u} D) : Prop := ∀ u ∈ D.units, Sat D M u.content

/-- The structure over E_reports that agrees with S on E and interprets each
generated predicate by its relation. -/
def interp (D : ReportDoc) (M : Source.{u} D) : VE.Structure.{u} :=
  { M.S with relation := fun r vs =>
      match keyOf D r, vs with
      | some (.inl k), [v] => M.J k.act k.sort k.ctx k.content v
      | some (.inr k), [v] => M.A k.j k.a k.content v
      | some _, _ => False
      | none, _ => M.S.relation r vs }

/-- The domain guards discharge the typing fields for every S'; forget keeps
carrier, domains and constants. -/
def restrictJ (D : ReportDoc) (S' : VE.Structure.{u}) : Source.{u} D where
  S := forget (names D) S'
  J := fun act s c q v =>
    ⟨act, s, c, q⟩ ∈ keys D ∧ S'.domain s v ∧ S'.relation (reportName D ⟨act, s, c, q⟩) [v]
  A := fun j a q v =>
    ⟨j, a, q⟩ ∈ akeys D ∧ S'.domain D.evidence v ∧ S'.relation (assessName D ⟨j, a, q⟩) [v]
  J_typed := fun _ _ _ _ _ hv => hv.2.1
  A_typed := fun _ _ _ _ hv => hv.2.1

/-- Two source models agree on D: one structure and, transported along that
equality, one relation on every key of D. -/
def AgreeOn (D : ReportDoc) (M N : Source.{u} D) : Prop :=
  ∃ e : M.S = N.S,
    (∀ k ∈ keys D, ∀ v, M.J k.act k.sort k.ctx k.content v ↔
       N.J k.act k.sort k.ctx k.content (congrArg VE.Structure.Carrier e ▸ v)) ∧
    (∀ k ∈ akeys D, ∀ v, M.A k.j k.a k.content v ↔ N.A k.j k.a k.content (congrArg VE.Structure.Carrier e ▸ v))

/-- The model-existence hypothesis of every theorem that builds a model of D:
trivial for a positive D. -/
def Expandable (D : ReportDoc) (S₀ : VE.Structure.{u}) : Prop := fol.Sat S₀ (neqs (premises D))

/-- 4.4: P0's FOL route at E_reports (folLayer E lits is Layer.id E (StringAdmissible E lits) _). -/
def reportsRoute (D : ReportDoc) : Layer fol.{u} _root_.Unit :=
  VE.Route.Background.folLayer (envReports D) D.lits

def checkedList (D : ReportDoc) (Γ : List VE.Formula) : List VE.Formula :=
  VE.Route.Background.literals D.lits ++ premises D ++ Γ

/-- `D` has positive top-level belief units of holder `hd` in context `c` with
formula contents `P` and `R`. -/
def beliefsIn (D : ReportDoc) (hd c : String) (P R : VE.Formula) : Prop :=
  (∃ u ∈ D.units, ∃ l, u.content = .report hd .believes c (.formula P) l) ∧
  (∃ u ∈ D.units, ∃ l, u.content = .report hd .believes c (.formula R) l)

end VE.Reports
