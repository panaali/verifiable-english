import VE.Route.Budget

/-! A document-level meter. The existing family evaluators own formula visits;
this module owns the shared document budget and the three-valued result. -/
namespace VE.Route.Metered
open Lean

structure Result where
  status : String
  value : Option Bool
  evaluations : Nat
  deriving Repr, DecidableEq

/-- The first false formula ends the document. `none` is exhaustion, never false.
The formula evaluator's charge function fails only when the budget is spent. -/
def scan {α : Type} (step : α → Nat → Option (Bool × Nat)) (limit : Nat) :
    List α → Nat → Result
  | [], work => ⟨"Satisfied", some true, work⟩
  | formula :: rest, work =>
    match step formula work with
    | none => ⟨"ResourceLimit", none, limit⟩
    | some (false, work') => ⟨"Violated", some false, work'⟩
    | some (true, work') => scan step limit rest work'

def evaluate {α : Type} (step : α → Nat → Option (Bool × Nat))
    (limit : Nat) (formulas : List α) : Result :=
  scan step limit formulas 0

/-- The closure families carry a cache as well as work between formulas. -/
def scanState {α σ : Type} (step : α → σ → Option (Bool × σ)) (work : σ → Nat)
    (limit : Nat) : List α → σ → Result
  | [], state => ⟨"Satisfied", some true, work state⟩
  | formula :: rest, state =>
    match step formula state with
    | none => ⟨"ResourceLimit", none, limit⟩
    | some (false, state') => ⟨"Violated", some false, work state'⟩
    | some (true, state') => scanState step work limit rest state'

/-- An exhausted document cannot be mistaken for a violation. -/
theorem scan_exhausted_unknown {α : Type} (step : α → Nat → Option (Bool × Nat))
    (limit : Nat) (formulas : List α) (work : Nat)
    (h : (scan step limit formulas work).status = "ResourceLimit") :
    (scan step limit formulas work).value = none := by
  induction formulas generalizing work with
  | nil => simp [scan] at h
  | cons f fs ih =>
    cases hs : step f work with
    | none => simp [scan, hs]
    | some r =>
      obtain ⟨b, work'⟩ := r
      cases b with
      | false => simp [scan, hs] at h
      | true =>
        simpa [scan, hs] using ih work' (by simpa [scan, hs] using h)

/-- Successful budgeted document answers agree with the unmetered owner. -/
theorem scan_sound {α : Type} (step : α → Nat → Option (Bool × Nat))
    (plain : α → Bool) (limit : Nat)
    (hstep : ∀ f w b w', step f w = some (b, w') → b = plain f) :
    ∀ (fs : List α) (work : Nat) (b : Bool),
      (scan step limit fs work).value = some b → b = fs.all plain := by
  intro fs
  induction fs with
  | nil => intro work b h; simp [scan] at h; cases h; rfl
  | cons f fs ih =>
    intro work b h
    cases hs : step f work with
    | none => simp [scan, hs] at h
    | some r =>
      obtain ⟨v, work'⟩ := r
      cases v with
      | false =>
        simp [scan, hs] at h
        cases h
        simp [List.all_cons, ← hstep f work false work' hs]
      | true =>
        have ht := hstep f work true work' hs
        have hi := ih work' b (by simpa [scan, hs] using h)
        simpa [List.all_cons, ← ht] using hi

/-- The stateful form also preserves an invariant such as closure-cache
correctness across every formula in the document. -/
theorem scanState_sound {α σ : Type} (step : α → σ → Option (Bool × σ))
    (work : σ → Nat) (limit : Nat) (plain : α → Bool) (P : σ → Prop)
    (hstep : ∀ f s b s', P s → step f s = some (b, s') → b = plain f ∧ P s') :
    ∀ (fs : List α) (state : σ) (b : Bool), P state →
      (scanState step work limit fs state).value = some b → b = fs.all plain := by
  intro fs
  induction fs with
  | nil => intro state b _ h; simp [scanState] at h; cases h; rfl
  | cons f fs ih =>
    intro state b hp h
    cases hs : step f state with
    | none => simp [scanState, hs] at h
    | some r =>
      obtain ⟨v, state'⟩ := r
      obtain ⟨hv, hp'⟩ := hstep f state v state' hp hs
      cases v with
      | false =>
        simp [scanState, hs] at h
        cases h
        simp [List.all_cons, ← hv]
      | true =>
        have hi := ih state' b hp' (by simpa [scanState, hs] using h)
        simpa [List.all_cons, ← hv] using hi

/-- Strict JSON budget fields. A missing field uses its documented default. -/
def budget (j : Json) (field : String) (default : Nat) : Except String Nat := do
  let n ← match j.getObjVal? field with
    | .ok v => v.getNat?
    | .error _ => pure default
  if n > VE.Time.maxEvaluations then
    throw "ResourceLimit: Evaluation budget exceeds the v0 limit of 1,000,000 nodes"
  pure n

def traceRequested (j : Json) : Except String Bool := do
  match j.getObjVal? "trace" with
  | .ok v => v.getBool?
  | .error _ => pure false

/-- Python uses the lesser of the work and trace-node budgets. -/
def limit (j : Json) : Except String Nat := do
  let work ← budget j "max_evaluations" VE.Time.maxEvaluations
  if ← traceRequested j then
    let nodes ← budget j "max_trace_nodes" 10000
    pure (min work nodes)
  else pure work

def resultFields (r : Result) : List (String × Json) :=
  [("status", .str r.status),
   ("value", r.value.map Json.bool |>.getD Json.null),
   ("evaluations", toJson r.evaluations)]

end VE.Route.Metered
