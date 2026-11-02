import VE.NormDefaults.Layered

/-!
# Weighing's zone interface (weighing-PLAN 3.4)

The six shared definitions the zone is stated over: the decision atoms of a finite
situation, the open predicate names of a layered document, an admissible completion, the
outcome in a completion, settledness and the reasons for `unknown`. The zone answers and
their theorems are WG-6's and extend this file.
-/

namespace VE.Weighing
universe u
open VE.Norms VE.NormDefaults
open VE.SoftNorms (SoftDoc decisions decisionNames)

variable {α : Type u}

/-- The decision atoms of a finite situation: every decision predicate of `D` at every typed tuple. -/
def decisionAtoms (D : SoftDoc) (M : VE.FiniteModel α) : List (String × List α) :=
  (decisions D).flatMap fun (p, ss) => (allTuples M ss).map (p, ·)
def openNames (L : VE.NormDefaults.Wire.LayeredU) : List String := decisionNames L.D ++ unsaidNames L.U

/-- A completion of `M`: relations that agree with `M` off the open names and with the record on its atoms, and
    satisfy PK-1's whole assembled X and `Fill_T`. -/
def AdmissibleCompletion (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (R : String → List α → Prop) : Prop :=
  (∀ n vs, n ∉ opens → (R n vs ↔ vs ∈ M.relations n)) ∧
  (∀ a b, (a, b) ∈ record → (R a.1 a.2 ↔ b = true)) ∧
  Wire.BaseAdmissibleX U X { M.asStructure with relation := R }

def OutcomeIn (U : UDoc) (M : VE.FiniteModel α) (R : String → List α → Prop) (r : Regulated) (vs : List α) : Prop :=
  (outcomeBase (fill U) r.name).denote { M.asStructure with relation := R } (tupleVal vs)

/-- Settled, and not vacuously: some admissible completion exists. -/
def SettledZ (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α) (b : Bool) : Prop :=
  (∃ R, AdmissibleCompletion U X M opens record R) ∧
  ∀ R, AdmissibleCompletion U X M opens record R → (OutcomeIn U M R r vs ↔ b = true)

/-- Why an answer is `unknown`; each reason is one Lean checked. -/
inductive ZoneUnknown (α : Type u)
  | budget (opens limit : Nat)
      -- the enumeration was not completed: the cone has `opens` open atoms not fixed by the record, over `limit`;
      -- never given after a complete enumeration
  | branch (assignment : List ((String × List α) × Bool)) (why : String)
      -- a complete enumeration left this assignment, which Kleene evaluation does not refute against X ++ Fill_T
      -- and no completion checked by `modelCheckX` confirms as a witness (`why`: none checked, or events' `NotCalendar`)

end VE.Weighing
