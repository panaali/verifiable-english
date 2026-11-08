import VE.Presupposition.Rows
import VE.Data.Background
import VE.SpeechActs.Answer

/-! # Agreement with the profiles that already take something for granted (docs/spec/presupposition.md 4.6)

`definite 0` is discourse's description; a functional and total `data@0` flag proves the
uniqueness of the attribute it names, at the top of a unit; a speech-acts question's
presupposition is its own goal at the top. -/
namespace VE.Presupposition
universe u

theorem discourse_definite_is_row (σ : String) (D P : VE.Formula) :
    (definite 0 σ D P).pre = VE.Discourse.uniqueD σ D ∧
    (definite 0 σ D P).strong = VE.Discourse.assertive σ D P ∧
    (definite 0 σ D P).weak = VE.Discourse.presupposed σ D P :=
  ⟨VE.Discourse.uniqueOpen_zero σ D, VE.Discourse.assertiveOpen_zero σ D P, rfl⟩

theorem data_attribute_proved (E : VE.Environment) (f : VE.Data.Background.Flag) (c : String)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hc : E.constants c = some f.source)
    (hfun : (VE.Data.Background.functionalPremise f).denote S [])
    (htot : (VE.Data.Background.totalPremise f).denote S []) :
    (Frame.hole.goal (VE.Discourse.uniqueD f.target (.binary f.name (.const c) (.var 0)))).denote S [] := by
  obtain ⟨v, hv, hdom⟩ := hS.1 c f.source hc
  obtain ⟨y, hy, hrel⟩ := (VE.Data.Background.totalPremise_iff S f).mp htot v hdom
  refine ⟨y, hy, ⟨v, y, hv, rfl, hrel⟩, fun z hz ⟨v', w, hv', hw, hr⟩ => ?_⟩
  obtain rfl : v' = v := Option.some.inj (hv'.symm.trans hv)
  obtain rfl : z = w := Option.some.inj hw
  obtain rfl : z = y := (VE.Data.Background.functionalPremise_iff S f).mp hfun v' hdom z hz y hy hr hrel
  exact ⟨z, rfl, rfl⟩

theorem speech_question_top (D : VE.SpeechActs.SpeechDoc) (q : VE.SpeechActs.Question) :
    Frame.hole.goal (VE.SpeechActs.presupposition D q) = VE.SpeechActs.presupposition D q :=
  rfl

end VE.Presupposition
