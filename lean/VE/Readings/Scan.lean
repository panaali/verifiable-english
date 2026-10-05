import VE.Readings.Separate

/-! The other reading's side of a pair, scanned lazily (lean-first plan F5b; batch 3b review B1). `separates` asks
whether some completion of the other reading over the base is admissible and gives the probe the recorded value,
and the route also reports whether some completion is admissible. `otherScan` answers both in one pass over the
completions, evaluating each one's admissibility only when the scan reaches it and its value only when it is
admissible and the witness shows the value, and stopping as soon as both answers are decided; `otherScan_id` is
the pair of answers as `separates` and `other_admissible` state them. Its evaluations are actions of a monad, so
`RunExamples.lean` counts them. -/
namespace VE.Readings
open VE.Rights (RightsDoc)

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

/-- The other reading's completions `Gs` over M with the shared tables `Tj`, through `scanOthers`: `tickValid` runs
    each time a completion's admissibility is evaluated and `tickValue` each time its value is. The route runs it in
    `Id` with no ticks (`otherScan_id`); `RunExamples.lean` counts the evaluations. -/
def otherScan {m : Type → Type} [Monad m] {α : Type} [DecidableEq α] (tickValid tickValue : m Unit)
    (Xj : RightsDoc × List VE.Formula) (M : VE.FiniteModel α) (Tj : List (GenKey × List (List α))) (q : Probe α)
    (v want : Bool) (Gs : List (List (GenKey × List (List α)))) : m (Bool × Bool) :=
  scanOthers (fun G => do tickValid; pure (sideValidOf Xj.1 M (Tj ++ G)))
    (fun G => do tickValue; pure (sideValueOf Xj M (Tj ++ G) q == some v)) want Gs false

theorem otherScan_id {α : Type} [DecidableEq α] (Xj : RightsDoc × List VE.Formula) (M : VE.FiniteModel α)
    (Tj : List (GenKey × List (List α))) (q : Probe α) (v want : Bool) (Gs : List (List (GenKey × List (List α)))) :
    otherScan (m := Id) (pure ()) (pure ()) Xj M Tj q v want Gs =
      (want && Gs.any (fun G => sideValidOf Xj.1 M (Tj ++ G) && sideValueOf Xj M (Tj ++ G) q == some v),
        Gs.any (fun G => sideValidOf Xj.1 M (Tj ++ G))) := by
  have h := scanOthers_eq (fun G => sideValidOf Xj.1 M (Tj ++ G)) (fun G => sideValueOf Xj M (Tj ++ G) q == some v)
    want Gs false
  rw [Bool.false_or] at h
  exact h

theorem and_not_and_any {β : Type} (w : Bool) (l : List β) (p : β → Bool) :
    (w && !(w && l.any p)) = (w && l.all (fun x => !p x)) := by
  cases w <;> simp [List.all_eq_not_any_not]

end VE.Readings
