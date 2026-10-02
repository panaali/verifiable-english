import VE.Rights.Tree

/-! The candidate content type (docs/spec/composition.md 1.6, 9.4).

The content of a reading candidate under `readings@1` and of a unit whose references the stack resolves: one
of five existing unit contents. A bar and a quantity statement are not contents: the bar is the one enumerated
axis, fixed before a document is superposed, and quantity sets stay on W2's and W6's routes. A W1 rule under
`norms@0` without `soft-norms@0` is the `SoftNode` with mode strict and no alterable party. The wire decoder
of a content is S1's; S0 adds none. -/
namespace VE.Compose

/-- The content of a reading candidate (plan 2.2) and of a unit whose references are resolved (plan 2.8). -/
inductive Content
  | assertion (φ : VE.Formula)
  | norm (N : VE.SoftNorms.SoftNode)
  | right (R : VE.Rights.Right)
  | rightLines (right : String) (ls : List VE.Rights.SourceLine)
  | limitation (L : VE.Rights.Limitation)
  deriving DecidableEq, Repr

/-- The W2 kind word of a content. -/
def Content.kind : Content → String
  | .assertion _ => "asserted" | .norm _ => "norm" | .right _ => "right"
  | .rightLines _ _ => "right_lines" | .limitation _ => "limitation"

/-- The chain profile a content needs; none for a formula. -/
def Content.needs : Content → Option String
  | .assertion _ => none | .norm _ => some "norms@0" | _ => some "rights@0"

def lineRuleNames (S : VE.Rights.SourceLine) : List String :=
  (S.norm.toList ++ S.liberty.toList ++ S.recognition.toList).map (·.name)

/-- The names a content declares, each with its kind of name: "rule", "right" or "limitation" (1.6). -/
def Content.declared : Content → List (String × String)
  | .assertion _ => []
  | .norm N => [("rule", N.name)]
  | .right R => ("right", R.name) :: (R.lines.flatMap lineRuleNames).map (fun n => ("rule", n))
  | .rightLines _ ls => (ls.flatMap lineRuleNames).map (fun n => ("rule", n))
  | .limitation L => [("limitation", L.name)]

theorem needs_chain (c : Content) (p : String) (h : c.needs = some p) : p = "norms@0" ∨ p = "rights@0" := by
  cases c <;> simp only [Content.needs, Option.some.injEq, reduceCtorEq] at h <;> subst h <;> simp

theorem assertion_declares_nothing (φ : VE.Formula) : (Content.assertion φ).declared = [] := rfl

end VE.Compose
