import VE.Discourse.Descriptions

/-! # Same-witness fusion (docs/spec/discourse.md 4.6, 9.3)

"A service is deployed. It is reviewed" licenses no fresh constant and no two unrelated
existentials: its same-witness reading is one group reading `∃x:σ (φ x ∧ ψ x)` bound to
both spans. `sharedWitness` decides syntactically that a content has one outermost
existential whose body is a conjunction every conjunct of which mentions the bound
variable; the group check requires it (`WitnessSplit` otherwise). -/
namespace VE.Discourse
universe u

def fused (σ : String) (φ ψ : VE.Formula) : VE.Formula := .ex σ (.and φ ψ)

def termMentions (k : Nat) : VE.Term → Bool
  | .var i => i == k
  | .const _ => false

/-- Whether de Bruijn variable `k` occurs free. -/
def mentionsVar : Nat → VE.Formula → Bool
  | _, .top | _, .bottom => false
  | k, .unary _ t => termMentions k t
  | k, .binary _ t w | k, .eq t w => termMentions k t || termMentions k w
  | k, .not a => mentionsVar k a
  | k, .and a b | k, .or a b | k, .implies a b => mentionsVar k a || mentionsVar k b
  | k, .all _ a | k, .ex _ a => mentionsVar (k + 1) a

/-- The conjuncts of a right- or left-nested conjunction. -/
def conjuncts : VE.Formula → List VE.Formula
  | .and a b => conjuncts a ++ conjuncts b
  | a => [a]

def isAnd : VE.Formula → Bool
  | .and _ _ => true
  | _ => false

def IsConjunctionMentioningZero (body : VE.Formula) : Prop :=
  isAnd body = true ∧ ∀ c ∈ conjuncts body, mentionsVar 0 c = true

def sharedWitness : VE.Formula → Bool
  | .ex _ body => isAnd body && (conjuncts body).all (mentionsVar 0)
  | _ => false

/-- Shared witness is decided syntactically and is what the group check requires. -/
theorem sharedWitness_spec (φ : VE.Formula) :
    sharedWitness φ = true ↔ ∃ σ body, φ = .ex σ body ∧ IsConjunctionMentioningZero body := by
  cases φ with
  | ex σ body =>
    simp only [sharedWitness, Bool.and_eq_true, List.all_eq_true, IsConjunctionMentioningZero,
      VE.Formula.ex.injEq]
    constructor
    · intro h; exact ⟨σ, body, ⟨rfl, rfl⟩, h⟩
    · rintro ⟨_, _, ⟨rfl, rfl⟩, h⟩; exact h
  | _ => simp [sharedWitness]

/-- The fused reading implies the split reading (the converse is refuted on a concrete
model, `split_not_fused_model`). -/
theorem fused_implies_split (E : VE.Environment) (σ : String) (hσ : σ ∈ E.sorts) (φ ψ : VE.Formula)
    (hφ : φ.WellFormed E [σ]) (hψ : ψ.WellFormed E [σ]) :
    VE.Entails E [fused σ φ ψ] (.and (.ex σ φ) (.ex σ ψ)) := by
  intro S _ hp
  obtain ⟨v, hv, h1, h2⟩ := hp _ (List.mem_singleton_self _)
  exact ⟨⟨v, hv, h1⟩, ⟨v, hv, h2⟩⟩

end VE.Discourse
