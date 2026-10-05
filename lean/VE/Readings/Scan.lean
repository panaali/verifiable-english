import VE.Readings.Separate

/-! The other reading's side of a pair, scanned lazily (lean-first plan F5b; batch 3b review B1, batch 3d review
B). `separates` asks whether some completion of the other reading over the base is admissible and gives the probe
the recorded value, and the route also reports whether some completion is admissible. `scanOthers` answers both in
one pass over the completions, evaluating each one's admissibility only when the scan reaches it and its value only
when it is admissible and the witness shows the value, and stopping as soon as both answers are decided;
`scanOthers_eq` is the pair of answers as `separates` and `other_admissible` state them. `pairEval` is a pair's
facts with the other side scanned so (the route's `pairFactsIn` runs it), and `pairEval_id` states them as
specified. The evaluations are actions of a monad, so `RunExamples.lean` counts them. -/
namespace VE.Readings

/-- The other reading's completions in order, as `separates` and `other_admissible` read them: each one's
    admissibility is asked when the scan reaches it, its value only when it is admissible and `want` holds (the
    witness side shows the value), and the scan stops at the first admissible completion with the value, or
    without `want` at the first admissible one. The answer: whether `want` holds and such a completion exists, and
    whether some completion is admissible. The evaluations are actions of `m`, so a test can count them
    (`RunExamples.lean`); the route runs it in `Id`. -/
def scanOthers {m : Type → Type} [Monad m] {β : Type} (valid hits : β → m Bool) (want : Bool) :
    List β → Bool → m (Bool × Bool)
  | [], adm => pure (false, adm)
  | G :: Gs, adm => do
    if ← valid G then
      if want then
        if ← hits G then pure (true, true) else scanOthers valid hits want Gs true
      else pure (false, true)
    else scanOthers valid hits want Gs adm

theorem scanOthers_eq {β : Type} (valid hits : β → Bool) (want : Bool) :
    ∀ (Gs : List β) (adm : Bool), scanOthers (m := Id) (fun G => pure (valid G)) (fun G => pure (hits G)) want Gs adm =
      (want && Gs.any (fun G => valid G && hits G), adm || Gs.any valid)
  | [], adm => by simp only [scanOthers, List.any_nil, Bool.and_false, Bool.or_false]; rfl
  | G :: Gs, adm => by
    have ih := scanOthers_eq valid hits want Gs
    unfold scanOthers
    cases hv : valid G <;> cases hw : want <;> cases hh : hits G <;>
      simp only [hw] at ih <;> simp [hv, hh, ih] <;> rfl

/-- The other reading's completions `Gs` over M with the shared tables `Tj`, read from its side `P` (plan F5d),
    through `scanOthers`: `tickValid` runs each time a completion's admissibility is evaluated and `tickValue` each
    time its value is. The route runs it in `Id` with no ticks (`otherScanOn_id`); `RunExamples.lean` counts the
    evaluations. -/
def otherScanOn {m : Type → Type} [Monad m] {α : Type} [DecidableEq α] (tickValid tickValue : m Unit) (P : Side)
    (M : VE.FiniteModel α) (Tj : List (GenKey × List (List α))) (q : Probe α) (v want : Bool)
    (Gs : List (List (GenKey × List (List α)))) : m (Bool × Bool) :=
  scanOthers (fun G => do tickValid; pure (sideValidOn P M (Tj ++ G)))
    (fun G => do tickValue; pure (sideValueOn P M (Tj ++ G) q == some v)) want Gs false

theorem otherScanOn_id {α : Type} [DecidableEq α] (P : Side) (M : VE.FiniteModel α)
    (Tj : List (GenKey × List (List α))) (q : Probe α) (v want : Bool) (Gs : List (List (GenKey × List (List α)))) :
    otherScanOn (m := Id) (pure ()) (pure ()) P M Tj q v want Gs =
      (want && Gs.any (fun G => sideValidOn P M (Tj ++ G) && sideValueOn P M (Tj ++ G) q == some v),
        Gs.any (fun G => sideValidOn P M (Tj ++ G))) := by
  have h := scanOthers_eq (fun G => sideValidOn P M (Tj ++ G)) (fun G => sideValueOn P M (Tj ++ G) q == some v)
    want Gs false
  rw [Bool.false_or] at h
  exact h

theorem and_not_and_any {β : Type} (w : Bool) (l : List β) (p : β → Bool) :
    (w && !(w && l.any p)) = (w && l.all (fun x => !p x)) := by
  cases w <;> simp [List.all_eq_not_any_not]

theorem assignments_of_ownedKeys_nil {α : Type} [DecidableEq α] (D : Doc) (s : String) (j : Nat)
    (M : VE.FiniteModel α) (h : ownedKeys D s j = []) : assignments D s j M = [[]] := by
  unfold assignments
  rw [h]
  rfl

/-- The facts of the pair (witness i, other j) over σ, each side's layers given (plan F5d), in `m`: whether σ
    separates the two, the witness's admissibility and value, whether some completion of j is admissible, and j's
    value when it owns no key. The witness's completion is evaluated once. With no owned key, j's one completion is
    evaluated once; otherwise j's completions go through `otherScanOn`, each one's admissibility evaluated only when
    the scan reaches it and its value only when needed, so nothing builds or evaluates the `2 ^ cells` completions
    up front (batch 3b review B1, batch 3d review B). Each document is read from its side (`Pi.X`, `Pj.X`), so
    none is built here (batch 3b, the request's table). `tickValid` and `tickValue` run at each evaluation of j's
    admissibility and value: the route runs it in `Id` (`pairFactsIn`), `RunExamples.lean` counts them. The caller
    has checked j's cells against `maxCells`. -/
def pairEval {m : Type → Type} [Monad m] {α : Type} [DecidableEq α] (tickValid tickValue : m Unit) (D : Doc)
    (s : String) (i j : Nat) (Pi Pj : Side) (σ : Situation α) : m (Bool × Bool × Option Bool × Bool × Option Bool) := do
  let M := σ.base
  let Ti := tablesForOf Pi.X (σ.fixed ++ σ.decisions)
  let Tj := tablesForOf Pj.X σ.fixed
  let valid := sideValidOn Pi M Ti
  let value := sideValueOn Pi M Ti σ.probe
  let want := situationWFOf D s i j Pi.X Pj.X σ && valid && value == some σ.value
  if ownedKeysOn D s j Pj = [] then
    tickValid
    let ok := sideValidOn Pj M Tj
    tickValue
    let v := sideValueOn Pj M Tj σ.probe
    pure (want && !(ok && v == some σ.value), valid, value, ok, v)
  else
    let o ← otherScanOn tickValid tickValue Pj M Tj σ.probe σ.value want (assignmentsOn D s j Pj M)
    pure (want && !o.1, valid, value, o.2, none)

/-- With each candidate's own side and j's cells within the bound, `pairEval` is `separates` and the specified
    fields. -/
theorem pairEval_id {α : Type} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (σ : Situation α)
    (hc : cells D s j σ.base ≤ maxCells) :
    pairEval (m := Id) (pure ()) (pure ()) D s i j (sideOf D s i) (sideOf D s j) σ =
      (separates D s i j σ, sideValid D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)),
        sideValue D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) σ.probe,
        (assignments D s j σ.base).any (fun G => sideValid D s j σ.base (tablesFor D s j σ.fixed ++ G)),
        if ownedKeys D s j = [] then sideValue D s j σ.base (tablesFor D s j σ.fixed) σ.probe else none) := by
  have hc' : decide (cells D s j σ.base ≤ maxCells) = true := decide_eq_true hc
  unfold pairEval
  simp only [ownedKeysOn_sideOf, assignmentsOn_sideOf, sideValidOn_sideOf, sideValueOn_sideOf, tablesForOf_sideOf,
    situationWFOf_sideOf]
  by_cases ho : ownedKeys D s j = []
  · simp only [ho, if_true, separates, assignments_of_ownedKeys_nil _ _ _ _ ho, hc', List.all_cons, List.all_nil,
      List.any_cons, List.any_nil, List.append_nil, Bool.and_true, Bool.or_false]
    rfl
  · simp only [ho, if_false]
    rw [otherScanOn_id]
    simp only [sideValidOn_sideOf, sideValueOn_sideOf, separates, hc', Bool.and_true, bind, pure,
      and_not_and_any]

end VE.Readings
