import VE.Readings.Separate

/-! A separating situation built from simple acts (docs/spec/act-phrases.md 7; plan AP-4).

Two candidates of a reading set built from a source differ in a simple act: one regulates an act the other does not.
`atomSituation` builds the situation that shows it: a base with one element in every sort, every relation and every
generated table empty, and the probe asking whether a rule selects the act of witness `i`'s rule that `j`'s rule does
not regulate. It is checked by the existing `VE.Readings.separates`, whose `separates_separated` gives `Separated`;
no new soundness theorem is needed. When there is no such act the probe is `holds`, which `separates` refuses
whenever the two documents hold the same assertions.
-/

namespace VE.Acts

/-- The predicate of candidate `i`'s rule, if its content is a rule. -/
def rulePreds (D : VE.Readings.Doc) (s : String) (i : Nat) : List String :=
  match (VE.Readings.candidate D s i).bind (·.content) with
  | some (.norm N) => [N.pred]
  | _ => []

/-- A separating situation built from simple acts: the status of an act in one reading and not the other holds,
    every other generated status is false. It is checked by `VE.Readings.separates` (no new soundness theorem). -/
def atomSituation (D : VE.Readings.Doc) (s : String) (i j : Nat) : VE.Readings.Situation Nat :=
  let probe := match (rulePreds D s i).find? (fun p => !(rulePreds D s j).contains p) with
    | some p => .selects "norm" p ((VE.SoftNorms.sortsIn D.frame.soft.T.regulated p).map (fun _ => 0))
    | none => .holds
  ⟨⟨fun _ => [0], fun _ => some 0, fun _ => []⟩, [], [], probe, true⟩

end VE.Acts
