import VE.Readings.VerdictsWire

/-! The answer core of question answering (docs/spec/question-answering.md 5.2; plan 4.1, 4.2, Q2.1).

A question VE reads with formula `ψ` is answered from RD-3's checked rows, one per compatible choice: its conflict row,
its premise row, its query row for `ψ`, a negation row (a certificate for `¬ψ`) and a split flag (one base model with
two checked fillings, `ψ` true under one and false under the other). The lead of a row is a function of these alone
(`Row.lead`), in the priority yes, no, not settled, not necessarily, unknown; an unknown lead has its reason
(`Row.reason`, X1 to X4 and X6). `LeadHolds` and `ReasonHolds` say what each claims of its choice; `Sound.lean` proves
them from `RowOk`, the rows' own `Holds`. -/

namespace VE.Ask
open VE.Readings VE.NormDefaults
open VE.Norms (Sat restrictAll DocumentExpansion)
universe u

inductive Lead | yes | no | notSettled | notNecessarily | unknown
  deriving DecidableEq, Repr

/-- What Lean checked for the question's formula under one compatible choice (plan 4.2). -/
structure Row where
  choice   : Choice
  conflict : ChoiceResult   -- RD-3's conflict row: `.free`, `.conflict` or `.unknown`
  premise  : ChoiceResult   -- RD-3's premise row: `.model`, `.inconsistent` or `.unknown`
  query    : ChoiceResult   -- RD-3's query row for ψ: `.proved`, `.refuted` or `.unknown`
  negation : ChoiceResult   -- `.proved` (a certificate for ¬ψ, `ndCertOk`) or `.unknown`
  split    : Bool           -- one base model, two fillings, both `ndModelOk`, ψ true and false
  deriving DecidableEq, Repr

def Row.lead (r : Row) : Lead :=
  if r.conflict != .free then .unknown
  else if r.query == .proved then (if r.premise == .model then .yes else .unknown)
  else if r.negation == .proved then (if r.premise == .model then .no else .unknown)
  else if r.split then .notSettled
  else if r.query == .refuted then .notNecessarily
  else .unknown

/-- The reason sentence after A5: X1 `conflict`, X2 `conflictUnchecked`, X3 `inconsistent`, X4 `noResult`,
    X5 `tooMany` (no rows), X6 `unchecked` (R9). -/
inductive Reason | conflict | conflictUnchecked | inconsistent | noResult | tooMany | unchecked
  deriving DecidableEq, Repr

def Row.reason (r : Row) : Option Reason :=
  if r.lead != .unknown then none
  else if r.conflict == .conflict then some .conflict
  else if r.conflict != .free then some .conflictUnchecked
  else if r.premise == .inconsistent then some .inconsistent
  else if r.query == .proved || r.negation == .proved then some .unchecked
  else some .noResult

/-- One base situation, two admissible fillings of its gaps, the premises true in both expansions, ψ true in the
    first and false in the second. -/
def SplitU (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula) : Prop :=
  ∃ (B : VE.Structure.{0}) (F₁ F₂ : FillTables U B) (S₁ S₂ : VE.Structure.{0}),
    restrictAll (fill U).T S₁ = withFill U B F₁ ∧ restrictAll (fill U).T S₂ = withFill U B F₂ ∧
    BaseAdmissibleU U (withFill U B F₁) ∧ BaseAdmissibleU U (withFill U B F₂) ∧
    DocumentExpansion (fill U) (withFill U B F₁) S₁ ∧ DocumentExpansion (fill U) (withFill U B F₂) S₂ ∧
    Sat S₁ Γ ∧ Sat S₂ Γ ∧ ψ.denote S₁ [] ∧ ¬ ψ.denote S₂ []

def LeadHolds (N : NDoc) (ψ : VE.Formula) (r : Row) : Prop :=
  let U := choiceU N r.choice
  let Γ := (choiceDoc N.D r.choice).2
  match r.lead with
  | .yes => ConflictFreeU.{u} U ∧ ConsistentU U Γ ∧ EntailsU.{u} U Γ ψ
  | .no => ConflictFreeU.{u} U ∧ ConsistentU U Γ ∧ EntailsU.{u} U Γ (.not ψ)
  | .notSettled => ConflictFreeU.{u} U ∧ SplitU U Γ ψ
  | .notNecessarily => ConflictFreeU.{u} U ∧ CounterU U Γ ψ
  | .unknown => True

def ReasonHolds (N : NDoc) (ψ : VE.Formula) (r : Row) : Reason → Prop
  | .conflict => ¬ ConflictFreeU.{0} (choiceU N r.choice)
  | .inconsistent => ConflictFreeU.{u} (choiceU N r.choice) ∧
      EntailsU.{u} (choiceU N r.choice) (choiceDoc N.D r.choice).2 .bottom
  | .unchecked => ConflictFreeU.{u} (choiceU N r.choice) ∧
      (EntailsU.{u} (choiceU N r.choice) (choiceDoc N.D r.choice).2 ψ ∨
        EntailsU.{u} (choiceU N r.choice) (choiceDoc N.D r.choice).2 (.not ψ))
  | _ => True

/-- The row's hypotheses: each component holds of its choice, as RD-3's rows do (`nd*Row_holds`). -/
def RowOk (N : NDoc) (ψ : VE.Formula) (r : Row) : Prop :=
  Holds.{u} N [] .bottom r.choice r.conflict ∧ Holds.{u} N [] .bottom r.choice r.premise ∧
  Holds.{u} N [] ψ r.choice r.query ∧ Holds.{u} N [] (.not ψ) r.choice r.negation ∧
  (r.split = true → SplitU (choiceU N r.choice) (choiceDoc N.D r.choice).2 ψ)

/-! ## Agreement with RD-3's fold (plan 4.2) -/

def conflictRows (rs : List Row) : List (Choice × ChoiceResult) := rs.map fun r => (r.choice, r.conflict)
def queryRows (rs : List Row) : List (Choice × ChoiceResult) := rs.map fun r => (r.choice, r.query)

end VE.Ask
