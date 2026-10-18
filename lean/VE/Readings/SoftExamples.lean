import VE.Readings.SoftWire
import VE.Readings.Examples

/-! RD-9's F-SD1 admission boundary: the default twin adds one decision
predicate, yet contributes no soft premise when it has no exception formula. -/
namespace VE.Readings.SoftExamples
open VE.Readings VE.Readings.Wire

def N : NDoc := ⟨VE.Readings.Examples.K1, ["avoid_required"]⟩

#guard softShaped N.D
#guard WellFormedSD N
#guard !softShaped VE.Readings.Examples.K17
#guard !softShaped VE.Readings.Examples.K19
#guard decisionCount (free N.D).1 == 0
#guard decisionCount (one N.D "rs1" 0).1 == 0
#guard decisionCount (one N.D "rs1" 1).1 == 1
#guard choiceX N [("rs1", 1)] == []

end VE.Readings.SoftExamples
