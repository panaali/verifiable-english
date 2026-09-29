import VE.Risk.Decl

/-! The severity order and the alternatives document of a risk policy
(docs/spec/risk.md 4.1 and 7.2). -/
namespace VE.Risk

/-- 4.1: the risk document is an alternatives document over `E_risk`. -/
theorem risk_wellFormed_alt (R : RiskDoc) (h : WellFormedRisk R = true) :
    VE.Alternatives.WellFormedAlt (toAlt R) = true :=
  (riskValid_of_wellFormed R h).alt

/-- 4.1(3): the closed order is irreflexive and transitive. -/
theorem severity_strict (R : RiskDoc) (h : WellFormedRisk R = true) :
    (∀ c, (c, c) ∉ closure R) ∧
    (∀ a b c, (a, b) ∈ closure R → (b, c) ∈ closure R → (a, c) ∈ closure R) := by
  have hv := riskValid_of_wellFormed R h
  exact ⟨fun c hc => hv.irrefl _ hc rfl, fun a b c h1 h2 => hv.trans _ h1 _ h2 rfl⟩

end VE.Risk
