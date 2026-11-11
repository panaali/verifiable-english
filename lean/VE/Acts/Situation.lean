import VE.Readings.Separate

/-! A separating situation built from simple acts (docs/spec/act-phrases.md 7; plan AP-4).

Two candidates of a reading set built from a source differ in a simple act: one regulates an act the other does not.
`atomSituation` builds the situation that shows it: a base with one element in every sort (every constant names it),
every relation and every generated table empty, and the probe asking whether a rule selects the act of witness `i`'s rule that `j`'s rule does
not regulate. It is checked by the existing `VE.Readings.separates`, whose `separates_separated` gives `Separated`
(`atomSituation_separated`: the base is always valid); no new soundness theorem is needed. When there is no such act the probe is `holds`, which `separates` refuses
whenever the two documents hold the same assertions.
-/

namespace VE.Acts

/-- The predicate of candidate `i`'s rule, if its content is a rule. -/
def rulePred (D : VE.Readings.Doc) (s : String) (i : Nat) : Option String :=
  match (VE.Readings.candidate D s i).bind (·.content) with
  | some (.norm N) => some N.pred
  | _ => none

/-- A separating situation built from simple acts: the status of an act in one reading and not the other holds,
    every other generated status is false. It is checked by `VE.Readings.separates` (no new soundness theorem). -/
def atomSituation (D : VE.Readings.Doc) (s : String) (i j : Nat) : VE.Readings.Situation Nat :=
  let probe := match rulePred D s i with
    | some p => if rulePred D s j == some p then .holds
      else .selects "norm" p ((VE.SoftNorms.sortsIn D.frame.soft.T.regulated p).map (fun _ => 0))
    | none => .holds
  ⟨⟨fun _ => [0], fun _ => some 0, fun _ => []⟩, [], [], probe, true⟩

/-! ### Ties (R16 ties pass, ap-4bb)

`rulePred` reads candidate `i`'s rule; `atomSituation` probes the act `i`'s rule regulates and `j`'s does not, else
`holds`; its base is valid over every environment, so `separates` accepting it gives `Separated` through
`separates_separated`, with no premise on the base. -/

theorem rulePred_eq_some (D : VE.Readings.Doc) (s : String) (i : Nat) (p : String) : rulePred D s i = some p ↔
    ∃ N : VE.SoftNorms.SoftNode, (VE.Readings.candidate D s i).bind (·.content) = some (.norm N) ∧ N.pred = p := by
  unfold rulePred
  constructor
  · intro h
    split at h
    · rename_i N hN
      exact ⟨N, hN, Option.some.inj h⟩
    · cases h
  · rintro ⟨N, hN, rfl⟩
    rw [hN]

theorem atomSituation_probe (D : VE.Readings.Doc) (s : String) (i j : Nat) (p : String) (hi : rulePred D s i = some p)
    (hj : rulePred D s j ≠ some p) : (atomSituation D s i j).probe =
      .selects "norm" p ((VE.SoftNorms.sortsIn D.frame.soft.T.regulated p).map (fun _ => 0)) := by
  simp [atomSituation, hi, hj]

theorem atomSituation_holds (D : VE.Readings.Doc) (s : String) (i j : Nat)
    (h : ∀ p, rulePred D s i = some p → rulePred D s j = some p) : (atomSituation D s i j).probe = .holds := by
  cases hi : rulePred D s i with
  | none => simp [atomSituation, hi]
  | some p => simp [atomSituation, hi, h p hi]

/-- Every constant names the one element, which is in every sort, and no relation holds. -/
theorem atomSituation_valid (D : VE.Readings.Doc) (s : String) (i j : Nat) :
    (atomSituation D s i j).base.Valid (VE.Readings.authorEnv D) :=
  ⟨fun _ _ _ => ⟨(0 : Nat), rfl, List.mem_singleton_self 0⟩, fun _ _ h => absurd h List.not_mem_nil⟩

theorem atomSituation_separated (D : VE.Readings.Doc) (hD : VE.Readings.WellFormedDoc D = true) (s : String) (i j : Nat)
    (hi : (VE.Readings.candidate D s i).bind (·.content) ≠ none) (hj : (VE.Readings.candidate D s j).bind (·.content) ≠ none)
    (h : VE.Readings.separates D s i j (atomSituation D s i j) = true) : VE.Readings.Separated.{0} D s i j :=
  VE.Readings.separates_separated D hD s i j hi hj _ (atomSituation_valid D s i j) h

end VE.Acts
