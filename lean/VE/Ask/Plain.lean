import VE.Ask.Sound

/-! The plain adapter's rows (docs/spec/question-answering.md 5.2; plan 4.7, R13): a `relational-fol@0` document has
no layers and no gaps, so its one row reads `VE.Entails` and a finite model, with the same five leads and no split.
-/

namespace VE.Ask
open VE.Readings
universe u

structure PlainRow where
  premise : ChoiceResult
  query : ChoiceResult
  negation : ChoiceResult
  deriving DecidableEq, Repr

def PlainRow.lead (r : PlainRow) : Lead := Row.lead ⟨[], .free, r.premise, r.query, r.negation, false⟩

def Consistent (E : VE.Environment) (Γ : List VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0}, S.Admissible E ∧ ∀ a ∈ Γ, a.denote S []

def LeadHoldsPlain (E : VE.Environment) (Γ : List VE.Formula) (ψ : VE.Formula) (r : PlainRow) : Prop :=
  match r.lead with
  | .yes => Consistent E Γ ∧ VE.Entails.{u} E Γ ψ
  | .no => Consistent E Γ ∧ VE.Entails.{u} E Γ (.not ψ)
  | .notNecessarily => ¬ VE.Entails.{0} E Γ ψ
  | .notSettled => False
  | .unknown => True

def PlainRowOk (E : VE.Environment) (Γ : List VE.Formula) (ψ : VE.Formula) (r : PlainRow) : Prop :=
  (r.premise = .model → Consistent E Γ) ∧ (r.premise = .inconsistent → VE.Entails.{u} E Γ .bottom) ∧
  (r.query = .proved → VE.Entails.{u} E Γ ψ) ∧ (r.query = .refuted → ¬ VE.Entails.{0} E Γ ψ) ∧
  (r.negation = .proved → VE.Entails.{u} E Γ (.not ψ))

theorem plain_never_split : ∀ r : PlainRow, r.lead ≠ .notSettled := by
  intro r h
  have := (lead_notSettled h).2.2.2
  cases this

theorem plain_lead_sound : ∀ (E : VE.Environment) (Γ : List VE.Formula) (ψ : VE.Formula) (r : PlainRow),
    PlainRowOk.{u} E Γ ψ r → LeadHoldsPlain.{u} E Γ ψ r := by
  intro E Γ ψ r h
  obtain ⟨hm, _, hq, hr, hn⟩ := h
  unfold LeadHoldsPlain
  cases hl : r.lead with
  | yes =>
    obtain ⟨_, h2, h3⟩ := lead_yes hl
    exact ⟨hm h3, hq h2⟩
  | no =>
    obtain ⟨_, _, h3, h4⟩ := lead_no hl
    exact ⟨hm h4, hn h3⟩
  | notSettled => exact plain_never_split r hl
  | notNecessarily => exact hr (lead_notNecessarily hl).2.1
  | unknown => trivial

end VE.Ask
