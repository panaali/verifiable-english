import ResponseShape.Encoders.Common

/-! The `english` mode (`Service.englishReported`, the English runner) against `english.json#/row`,
and the `diagnose` mode (`Service.Diagnose.diagnoseCase`) against `diagnose.json#/row`. -/

namespace ResponseShape.Encoders.English
open Lean ResponseShape ResponseShape.Skeletons
open VE.English.ServiceRun

variable {req : Json}

theorem runCase_fits (E : VE.Environment) (L : VE.English.Lexicon) (j : Json) :
    OkFits req (skel% "english.json#/$defs/item") (runCase E L j) := by
  unfold runCase
  okfits
  fits

theorem run_fits (input : String) : OkFits req Skeletons.english (run input) := by
  unfold run
  okfits
  fits
  exact Fits.arrOf (OkP.arrayMapM (fun c _ => runCase_fits _ _ c) _ ‹_›)

theorem reported_fits (raw : String) : Fits req Skeletons.english (match run raw with
    | .ok result => result
    | .error message => Json.mkObj [("status", .str "error"), ("error", .str message)]) := by
  split
  · exact run_fits _ _ ‹_›
  · fits

theorem english_fits (j : Json) : Fits j Skeletons.english (VE.Service.englishReported j) :=
  reported_fits _

end ResponseShape.Encoders.English

/-! ## The class of a diagnose record

A finding's class (`Finding.cls`) is one a table names: a check's, a classifier member's or an
include's `as` (`entryClasses`). Every registered table names public rejection codes only, so the
`class` of every record is one (`common.json#/$defs/code`). -/

namespace ResponseShape.Encoders.English
open VE.WireContract

mutual
/-- The classes an entry names: its check's and classifier members', each include's `as`. -/
def entryClasses : Entry → List String
  | .check c => c.cls :: match c.kind with
    | .classifier _ emits => emits.map (·.cls)
    | _ => []
  | .each _ _ _ entries => entriesClasses entries
  | .scope _ _ _ recode entries => recode.toList.map (·.2) ++ entriesClasses entries
def entriesClasses : List Entry → List String
  | [] => []
  | e :: es => entryClasses e ++ entriesClasses es
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace; closing and
-- reopening the namespace here keeps its reading and Lean's the same.
end ResponseShape.Encoders.English

namespace ResponseShape.Encoders.English
open Lean ResponseShape ResponseShape.Skeletons VE.WireContract

def tableClasses (t : Table) : List String := t.phases.flatMap fun p => entriesClasses p.entries

/-- An instance whose check, classifier members and enclosing `as` name classes of `S`. -/
def ClassesIn (S : List String) (i : Instance) : Prop :=
  i.check.cls ∈ S ∧ (∀ n emits, i.check.kind = .classifier n emits → ∀ m ∈ emits, m.cls ∈ S) ∧
    ∀ r, i.frame.recode = some r → r.2 ∈ S

mutual
theorem expand_classes (S : List String) (h : Hooks) (phase : String) (root : Json) (items earlier : List Pointer)
    (frame : Frame) (hf : ∀ r, frame.recode = some r → r.2 ∈ S) :
    (e : Entry) → (∀ x ∈ entryClasses e, x ∈ S) → ∀ i ∈ expand h phase root items earlier frame e, ClassesIn S i
  | .check c, hS, i, hi => by
    unfold expand at hi
    split at hi
    · simp only [List.mem_cons, List.not_mem_nil, or_false] at hi
      subst hi
      refine ⟨hS _ (by simp [entryClasses]), fun n emits hk m hm => hS _ ?_, hf⟩
      simp only [entryClasses, List.mem_cons]
      right
      rw [show c.kind = .classifier n emits from hk]
      exact List.mem_map.mpr ⟨m, hm, rfl⟩
    · cases hi
  | .each _ _ _ entries, hS, i, hi => by
    unfold expand at hi
    split at hi
    · obtain ⟨_, _, hi⟩ := List.mem_flatMap.mp hi
      exact expandAll_classes S h phase root _ _ frame hf entries (by simpa [entryClasses] using hS) i hi
    · cases hi
  | .scope id _ view recode entries, hS, i, hi => by
    unfold expand at hi
    split at hi
    · cases hi
    · refine expandAll_classes S h phase _ _ _ _ (fun r hr => ?_) entries
        (fun x hx => hS x (by simp [entryClasses, hx])) i hi
      simp only [Frame.enter, Option.or_eq_some_iff] at hr
      rcases hr with hr | ⟨_, hr⟩
      · exact hf r hr
      · exact hS _ (by simp [entryClasses, hr])
theorem expandAll_classes (S : List String) (h : Hooks) (phase : String) (root : Json) (items earlier : List Pointer)
    (frame : Frame) (hf : ∀ r, frame.recode = some r → r.2 ∈ S) :
    (es : List Entry) → (∀ x ∈ entriesClasses es, x ∈ S) →
      ∀ i ∈ expandAll h phase root items earlier frame es, ClassesIn S i
  | [], _, i, hi => by simp [expandAll] at hi
  | e :: es, hS, i, hi => by
    unfold expandAll at hi
    rcases List.mem_append.mp hi with hi | hi
    · exact expand_classes S h phase root items earlier frame hf e
        (fun x hx => hS x (by simp [entriesClasses, hx])) i hi
    · exact expandAll_classes S h phase root items earlier frame hf es
        (fun x hx => hS x (by simp [entriesClasses, hx])) i hi
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace; closing and
-- reopening the namespace here keeps its reading and Lean's the same.
end ResponseShape.Encoders.English

namespace ResponseShape.Encoders.English
open Lean ResponseShape ResponseShape.Skeletons VE.WireContract

theorem finding_class {S : List String} {i : Instance} {id code cls : String} {text : List Piece} {p : Pointer}
    {target : Option Json} {extra args : List (String × Json)} (hc : cls ∈ S)
    (hr : ∀ r, i.frame.recode = some r → r.2 ∈ S) : (finding i id code cls text p target extra args).cls ∈ S := by
  unfold finding
  cases hrc : i.frame.recode with
  | none => simpa [hrc] using hc
  | some r => simpa [hrc] using hr r hrc

theorem eval_class {S : List String} {h : Hooks} {i : Instance} {f : Finding} (hi : ClassesIn S i)
    (he : eval h i = some f) : f.cls ∈ S := by
  obtain ⟨hc, hm, hr⟩ := hi
  unfold eval at he
  dsimp only at he
  split at he
  · split at he
    · cases he
    · cases he; exact finding_class hc hr
  · split at he
    · cases he
    · obtain ⟨m, hm', hf⟩ := Option.map_eq_some_iff.mp he
      subst hf
      exact finding_class (hm _ _ ‹_› m (List.mem_of_find?_eq_some hm')) hr
  · split at he
    · cases he; exact finding_class hc hr
    · cases he
  · split at he
    · cases he
    · obtain ⟨_, _, hf⟩ := Option.map_eq_some_iff.mp he
      subst hf
      exact finding_class hc hr

/-- The class of every finding of the engine is one its table names. -/
theorem run_class {t : Table} {h : Hooks} {j : Json} {f : Finding} (hrun : run t h j = some f) :
    f.cls ∈ tableClasses t := by
  obtain ⟨i, hi, he⟩ := List.exists_of_findSome?_eq_some hrun
  obtain ⟨p, hp, hi⟩ := List.mem_flatMap.mp hi
  refine eval_class (expandAll_classes _ h p.name j [] [] Frame.top (fun _ h => by cases h) p.entries
    (fun x hx => List.mem_flatMap.mpr ⟨p, hp, hx⟩) i hi) he

/-- Every registered table names public rejection codes only. -/
theorem units_classes : (VE.WireContract.Diagnose.units.all fun u =>
    (tableClasses u.2.table).all VE.Service.rejectionCodes.contains) = true := by
  decide +kernel

theorem lookup_mem {l : List (String × α)} {k : String} {v : α} (h : l.lookup k = some v) : v ∈ l.map (·.2) := by
  induction l with
  | nil => cases h
  | cons p l ih =>
    simp only [List.lookup] at h
    split at h
    · cases h; exact List.mem_cons_self
    · exact List.mem_cons_of_mem _ (ih h)

/-- The class of a registered unit's finding is a public rejection code. -/
theorem unit_class {unit : String} {u : VE.WireContract.Diagnose.Registered} {root : Json} {f : Finding}
    (hu : VE.WireContract.Diagnose.units.lookup unit = some u) (hrun : run u.table u.hooks root = some f) :
    f.cls ∈ VE.Service.rejectionCodes := by
  obtain ⟨⟨k, u'⟩, hm, rfl⟩ := List.mem_map.mp (lookup_mem hu)
  have hall := List.all_eq_true.mp units_classes _ hm
  exact List.contains_iff_mem.mp (List.all_eq_true.mp hall _ (run_class hrun))

theorem diagnose_fits (j : Json) : Fits j Skeletons.diagnose (VE.Service.Diagnose.diagnoseCase j) := by
  unfold VE.Service.Diagnose.diagnoseCase VE.WireContract.Diagnose.diagnoseCase VE.WireContract.record
  simp only []
  fits
  exact Fits.strIn (unit_class ‹_› ‹_›)

end ResponseShape.Encoders.English
