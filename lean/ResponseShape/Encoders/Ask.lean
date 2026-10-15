import ResponseShape.Encoders.Common
import VE.Ask.Run

/-! The `ask` mode (`VE.Ask.Run.caseReported`) against `ask.json#/row`: every field of an answered question and of a
refused one, typed. -/
namespace ResponseShape.Encoders.Ask
open Lean ResponseShape ResponseShape.Skeletons VE.Ask VE.Ask.Run

variable {req : Json}

theorem source_fits (s : Source) : Fits req (skel% "ask.json#/$defs/source") (sourceJson s) := by
  cases s <;> simp only [sourceJson] <;> fits

theorem choice_fits (c : VE.Readings.Choice) : Fits req (skel% "ask.json#/$defs/choice") (VE.Readings.choiceJson c) := by
  unfold VE.Readings.choiceJson
  fits

/-- A line's source: null or a source (`ask.json` writes null as `const null`, so the skeleton keeps it). -/
theorem line_source_fits (s : Source) :
    Fits req (skel% "ask.json#/$defs/source_or_null") (sourceJson s) := by
  cases s <;> simp only [sourceJson] <;> fits

theorem reason_fits (x : Reason) : Fits req (skel% "ask.json#/$defs/reason") (Json.str (reasonName x)) := by
  cases x <;> simp only [reasonName, reasonFrame] <;> fits

theorem line_fits (l : Line) : Fits req (skel% "ask.json#/$defs/line") (lineJson l) := by
  unfold lineJson
  cases hs : l.source <;> cases hq : l.quote <;> cases hw : l.witness <;>
    simp only [Option.map_none, Option.map_some, Option.getD_none, Option.getD_some] <;>
    fits using line_source_fits, choice_fits

theorem row_fits (v : View) (r : Row) : Fits req (skel% "ask.json#/$defs/row") (rowJson v r) := by
  unfold rowJson
  cases hl : r.lead <;> cases hr : r.reason <;>
    simp only [leadKey, Option.map_none, Option.map_some, Option.getD_none, Option.getD_some] <;>
    fits using source_fits, choice_fits, reason_fits

theorem name_fits (nm : VE.Ask.Name) : Fits req (skel% "ask.json#/$defs/name") (nameJson nm) := by
  unfold nameJson
  fits

theorem identities_fits (text q : String) (lexicon : Json) (E : VE.EnglishGrammar.Env) :
    OkFits req (skel% "ask.json#/$defs/identities") (identitiesOf text q lexicon E) := by
  unfold identitiesOf
  okfits
  all_goals fits

theorem route_mem (text : String) : routeOfDocument text = "readings" ∨ routeOfDocument text = "plain" ∨
    routeOfDocument text = "norm-defaults" := by
  unfold routeOfDocument
  split
  · dsimp only
    split
    · exact Or.inl rfl
    · split
      · exact Or.inr (Or.inr rfl)
      · exact Or.inr (Or.inl rfl)
  · exact Or.inr (Or.inl rfl)

theorem answeredFields_fits (route q : String) (c : VE.Question.Candidate) (φ : VE.EnglishGrammar.EFormula)
    (ctx : Context) (v : View) (ids : Json)
    (hroute : route = "readings" ∨ route = "plain" ∨ route = "norm-defaults")
    (hids : Fits req (skel% "ask.json#/$defs/identities") ids) :
    Fits req (skel% "ask.json#/$defs/answered") (Json.mkObj (answeredFields route q c φ ctx v ++ [("identities", ids)])) := by
  unfold answeredFields answerLead VE.Question.Run.formName
  rcases hroute with rfl | rfl | rfl <;> cases hf : c.form <;> split <;>
    simp only [] <;> fits using line_fits, row_fits, name_fits
  all_goals (try exact hids)

theorem refused_fits (fs : List (String × Json)) (ids : Json)
    (hids : Fits req (skel% "ask.json#/$defs/identities") ids) :
    Fits req (skel% "ask.json#/$defs/refused") (Json.mkObj (refusedFields fs ++ [("identities", ids)])) := by
  unfold refusedFields
  fits
  exact hids

/-- The fields an answered question's result has. -/
theorem answered_ok (route : String) (j : Json) (q : String) (c : VE.Question.Candidate)
    (φ : VE.EnglishGrammar.EFormula) :
    OkP (fun fs => ∃ ctx v, fs = answeredFields route q c φ ctx v) (answered route j q c φ) := by
  unfold answered
  okfits
  all_goals exact ⟨_, _, rfl⟩

theorem askCase_fits (j : Json) : OkFits j Skeletons.ask (askCase j) := by
  unfold askCase VE.Route.Wire.ok
  okfits
  · have hi := identities_fits (req := j) _ _ _ _ _ ‹identitiesOf _ _ _ _ = .ok _›
    obtain ⟨ctx, v, hfs⟩ := answered_ok _ _ _ _ _ _ ‹answered _ _ _ _ _ = .ok _›
    subst hfs
    fits
    exact Fits.alt (by alt_mem) (answeredFields_fits _ _ _ _ ctx v _ (route_mem _) hi)
  · have hi := identities_fits (req := j) _ _ _ _ _ ‹identitiesOf _ _ _ _ = .ok _›
    fits
    exact Fits.alt (by alt_mem) (refused_fits _ _ hi)

theorem caseReported_fits (j : Json) : Fits j Skeletons.ask (caseReported j) := by
  unfold caseReported
  split
  · exact askCase_fits j _ ‹_›
  · fits

end ResponseShape.Encoders.Ask
