import ResponseShape.Encoders.Common
import VE.Route.MeteredRun

/-! The `metered` mode (`Route.MeteredRun.runCaseReported`) against `metered.json#/row`: a document
result has one of the three statuses, every explanation row is one node object, and a non-vacuity
answer has its three fields. -/

namespace ResponseShape.Encoders.Metered
open Lean ResponseShape ResponseShape.Skeletons
open VE.Route VE.Route.MeteredRun

variable {req : Json}

/-- The three metered document results: satisfied and true, violated and false, or exhausted with no
value. -/
def Statused (r : Metered.Result) : Prop :=
  (r.status = "Satisfied" ∧ r.value = some true) ∨ (r.status = "Violated" ∧ r.value = some false) ∨
    (r.status = "ResourceLimit" ∧ r.value = none)

theorem scan_statused {α : Type} (step : α → Nat → Option (Bool × Nat)) (limit : Nat) :
    ∀ (fs : List α) (work : Nat), Statused (Metered.scan step limit fs work)
  | [], _ => Or.inl ⟨rfl, rfl⟩
  | f :: fs, work => by
    unfold Metered.scan
    split
    · exact Or.inr (Or.inr ⟨rfl, rfl⟩)
    · exact Or.inr (Or.inl ⟨rfl, rfl⟩)
    · exact scan_statused step limit fs _

theorem scanState_statused {α σ : Type} (step : α → σ → Option (Bool × σ)) (work : σ → Nat) (limit : Nat) :
    ∀ (fs : List α) (state : σ), Statused (Metered.scanState step work limit fs state)
  | [], _ => Or.inl ⟨rfl, rfl⟩
  | f :: fs, state => by
    unfold Metered.scanState
    split
    · exact Or.inr (Or.inr ⟨rfl, rfl⟩)
    · exact Or.inr (Or.inl ⟨rfl, rfl⟩)
    · exact scanState_statused step work limit fs _

theorem binding_fits (index : Nat) (b : String × String) :
    Fits req (skel% "metered.json#/$defs/binding") (MeteredTrace.bindingJson index b) := by
  unfold MeteredTrace.bindingJson
  fits

theorem row_fits (r : MeteredTrace.Row) : Fits req (skel% "metered.json#/$defs/node") r.json := by
  unfold MeteredTrace.Row.json MeteredTrace.bindingsJson
  fits

theorem trace_fits (t : MeteredTrace.Trace) :
    Fits req (.arr [] (skel% "metered.json#/$defs/node")) t.json := by
  unfold MeteredTrace.Trace.json
  apply Fits.arrOf
  elems_split
  intro r _
  exact row_fits r

theorem answer_fits {α ρ σ entity : Type} (q : Query) (s : Session α ρ σ entity)
    (hs : ∀ fs, Statused (s.document fs)) (r : Request α) :
    Fits req Skeletons.metered (answer q s r) := by
  cases r with
  | nonVacuity f =>
    simp only [answer, nonVacuityResult, Wire.ok]
    split <;> fits
  | evaluate fs =>
    simp only [answer, Wire.ok, Metered.resultFields]
    rcases hs fs with ⟨h, hv⟩ | ⟨h, hv⟩ | ⟨h, hv⟩ <;> rw [h, hv] <;> split <;> fits using trace_fits

/-- Every row fits whatever environment decoding the case is answered with: its own (`runCase`) or
the one the service keeps with its handle (`VE.Service.caseResultWith`). -/
theorem runWith_fits (p : Except String Prepared) (j : Json) :
    OkFits req Skeletons.metered (runWith p j) := by
  unfold runWith run
  okfits
  all_goals first
    | exact answer_fits _ _ (fun fs => scan_statused _ _ fs 0) _
    | exact answer_fits _ _ (fun fs => scanState_statused _ _ _ fs _) _

theorem runCase_fits (j : Json) : OkFits req Skeletons.metered (runCase j) :=
  runWith_fits _ j

theorem reportedWith_fits (p : Except String Prepared) (j : Json) :
    Fits j Skeletons.metered (reportedWith p j) := by
  unfold reportedWith
  split
  · exact runWith_fits p j _ ‹_›
  · fits

theorem runCaseReported_fits (j : Json) : Fits j Skeletons.metered (runCaseReported j) :=
  reportedWith_fits _ j

end ResponseShape.Encoders.Metered
