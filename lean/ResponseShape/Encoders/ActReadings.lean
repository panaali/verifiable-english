import ResponseShape.Encoders.Common
import VE.Acts.Run

/-! The `act-readings` mode (`VE.Acts.Run.actReadingsReported`) against `act-readings.json#/row`: a listed row's
spans, readings and acts, and a refused or limited row's diagnostic, typed to the leaves. -/
namespace ResponseShape.Encoders.ActReadings
open Lean ResponseShape ResponseShape.Skeletons VE.Acts VE.Acts.Run

variable {req : Json}

theorem actJson_fits (fx : List String) (op : Op) (f : Option Lexical.Form) (plain : Bool) (ps : List Lexical.Tok)
    (x : Simple) : OkFits req (skel% "act-readings.json#/$defs/act") (actJson fx op f plain ps x) := by
  unfold actJson
  okfits
  all_goals fits

theorem readingJson_fits (fx : List String) (op : Op) (f : Option Lexical.Form) (plain : Bool)
    (ps : List Lexical.Tok) (x : List Simple × String) :
    OkFits req (skel% "act-readings.json#/$defs/reading") (readingJson fx op f plain ps x) := by
  unfold readingJson
  okfits
  rename_i acts hacts
  have h := OkP.mapM (fun y _ => actJson_fits (req := req) fx op f plain ps y) _ hacts
  fits
  exact h _ ‹_›

theorem listReadings_fits (id : String) (fx : List String) (V : Vocab) (op : Op) (f : Option Lexical.Form)
    (plain : Bool) (phrase : String) :
    OkFits req (skel% "act-readings.json#/$defs/result") (listReadings id fx V op f plain phrase) := by
  unfold listReadings
  okfits
  all_goals simp only [VE.Route.Wire.ok, List.cons_append, List.nil_append]
  all_goals fits
  rename_i rows hrows _ _
  exact OkP.mapM (fun x _ => readingJson_fits (req := req) fx op f plain _ x) _ hrows _ ‹_›

theorem refusedRow_fits (id d : String) : Fits req (skel% "act-readings.json#/$defs/result") (refusedRow id d) := by
  have hv : verdictOf d = "LIMIT" ∨ verdictOf d = "REFUSED" := by unfold verdictOf; split <;> simp
  unfold refusedRow VE.Route.Wire.ok
  simp only [List.cons_append, List.nil_append]
  refine Fits.mkObjAlt 1 rfl (by rcases hv with h | h <;> rw [h] <;> rfl) ?_
  intro p hp
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl
  all_goals simp only [Skel.field, List.lookup, Option.getD]
  all_goals first
    | exact Fits.any _
    | (rcases hv with h | h <;> rw [h] <;> exact Fits.strIn (by simp))
    | exact Fits.strIn (by simp)
    | exact Fits.arrOf (by simp)

theorem listed_fits (j : Json) (id phrase : String) (fx : List String) (role : VE.Norms.Role) (sign : Bool)
    (f : Option Lexical.Form) : OkFits req (skel% "act-readings.json#/$defs/result") (listed j id phrase fx role sign f) := by
  intro v hv
  unfold listed at hv
  obtain ⟨V, _, h⟩ := VE.Kit.Except.bind_ok hv
  split at h
  · exact listReadings_fits _ _ _ _ _ _ _ v h
  · cases h

theorem runActReadings_fits (j : Json) : OkFits j Skeletons.actReadings (runActReadings j) := by
  intro v hv
  obtain ⟨⟨id, phrase, fx, role, sign, f⟩, _, h⟩ := VE.Kit.Except.bind_ok hv
  cases h
  split
  · fits_from listed_fits j id phrase fx role sign f _ ‹_›
  · fits_from refusedRow_fits id _

theorem actReadingsReported_fits (j : Json) : Fits j Skeletons.actReadings (actReadingsReported j) := by
  unfold actReadingsReported
  split
  · exact runActReadings_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.ActReadings
