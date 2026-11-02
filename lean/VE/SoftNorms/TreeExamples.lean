import VE.Defaults.MeaningExamples
import VE.Defaults.WireExamples
import VE.Rights.Examples

/-! Fixture F6.1b (docs/spec/profile-composition.md 1.10, PC-6a): the staged decision key changes nothing.
No decoder sets `splitFrom`, so on every rule of today's soft documents `decisionRule N = N.name`: the
documents the norm-defaults layered route decodes (`decodeSoftU`, DF-1a's fixtures and their siblings), the
literal DF-π and the rights examples after `correlate`. A document that does not decode, or has no rule,
fails its claim. -/
namespace VE.SoftNorms.TreeFixtures
open VE.SoftNorms (SoftDoc SoftNode decisionRule decisionRule_unsplit)
open VE.NormDefaults.Wire (LayeredU)
open VE.Defaults.Fixtures
open VE.Defaults.MeaningFixtures (dTwo dSw dπ Dπ nπ)
open VE.Defaults.WireFixtures (dγb)

/-- Every rule of `D` reads its own name as its decision key, and `D` has a rule. -/
def unsplitKeys (D : SoftDoc) : Bool :=
  !D.T.nodes.isEmpty && D.T.nodes.all (fun N => N.splitFrom == none && decisionRule N == N.name)

/-- The soft documents the layered route decodes in the fixtures on main. -/
def layeredDocs : List (Except String LayeredU) :=
  [dα, dβ, dγ, dγ', dδ, dδs, dδo, dε, dζ, dζ0, dσ, dTwo, dSw, dπ, dγb]

#guard layeredDocs.length == 15
#guard layeredDocs.all fun e => holds e fun L => unsplitKeys L.D
#guard unsplitKeys Dπ
#guard [VE.Rights.Examples.alpha, VE.Rights.Examples.gamma, VE.Rights.Examples.gamma7, VE.Rights.Examples.rho,
  VE.Rights.Examples.epsilon].all fun R => unsplitKeys (VE.Rights.correlate R)

/-- `decisionRule_unsplit` on the literal rule; the anonymous constructor's `none` is the default. -/
example : decisionRule nπ = nπ.name := decisionRule_unsplit nπ rfl
#guard nπ.splitFrom == none && decisionRule nπ == "r1"

-- The other direction: a part split from `r0` reads `r0`'s decisions, not its own.
#guard decisionRule { nπ with splitFrom := some "r0" } == "r0"

end VE.SoftNorms.TreeFixtures
