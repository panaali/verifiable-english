import VE.Readings.DefaultVerdicts
import VE.Readings.Examples

/-! DF-3's computed fixtures (docs/spec/defeasible.md 8.3, plan 4.3 F-DF2): each choice's soft document, its no-exception
premises and its colliding pairs, on RD-9's K1 (DF-ν), K1 with a colliding second set (DF-ρ), and S1's and S2a's
documents (F-DF2). The rows that need evidence are `tests/test_defaults_readings.py`'s, through the service. -/
namespace VE.Readings.DefaultExamples
open VE.Readings VE.Readings.Examples VE.Defaults

def S2 : VE.SoftNorms.SoftNode := VE.Rights.Examples.strictNode "help" "help_required" true
def D2 : VE.SoftNorms.SoftNode := VE.Rights.Examples.defaultNode "permit-deception" "avoid_required" false
def rs2 : ReadingSet := ⟨"rs2", "u2", 1, [cand "help" S2, cand "permit" D2]⟩
def Nν : NDoc := ⟨K1, ["avoid_required"]⟩
def Nρ : NDoc := ⟨docK [.set rs1, .set rs2], ["avoid_required"]⟩

def labels (N : NDoc) : List (Choice × List String) :=
  (choices N.D).map fun c => (c, dfltLabels (choiceSoft N c))
def pairs (N : NDoc) : List (Choice × List (String × String × List String)) :=
  (choices N.D).map fun c => (c, (VE.SoftNorms.collidingPairs (choiceSoft N c)).map fun (P, Q) =>
    (P.name, Q.name, giveWayDeciders (choiceSoft N c) P Q))

-- DF-ν: only the default reading has a no-exception premise, and no choice has a colliding pair.
#guard labels Nν == [([("rs1", 0)], []), ([("rs1", 1)], ["default:exception:no-deception"])]
#guard (pairs Nν).all (·.2.isEmpty)

-- DF-ρ: only `(rs1, 1), (rs2, 1)` collides, both rules' exceptions decided by `unstated` (DE7a·u).
#guard pairs Nρ == [([("rs1", 0), ("rs2", 0)], []), ([("rs1", 0), ("rs2", 1)], []), ([("rs1", 1), ("rs2", 0)], []),
  ([("rs1", 1), ("rs2", 1)], [("no-deception", "permit-deception", ["unstated"])])]
#guard (labels Nρ).map (·.2.length) == [0, 1, 1, 2]

/-- F-DF2: on S1's and S2a's documents a choice without a no-exception premise has no colliding pair (its gate holds
    with no certificate, and its default rows are its strict ones), and the member is shown (`hasDefaults`) exactly on
    the documents some of whose choices have a no-exception premise. -/
def corpus : List (String × Doc) :=
  [("K1", K1), ("K2", K2), ("K3", K3), ("K4", K4), ("K5", K5), ("K6", K6), ("K9", K9), ("K11", K11), ("K12", K12),
   ("K13", K13), ("K14", K14), ("K16", K16), ("K17", K17), ("K19", K19), ("M5", M5), ("M6", M6), ("M7", M7),
   ("M8", M8), ("M9", M9), ("M10", M10), ("M16", M16), ("M18", M18), ("M20", M20)]

#guard corpus.all fun (_, D) => (choices D).all fun c =>
  !(dfltLabelled (choiceSoft ⟨D, []⟩ c)).isEmpty || (VE.SoftNorms.collidingPairs (choiceSoft ⟨D, []⟩ c)).isEmpty
#guard (corpus.filter fun (_, D) => (choices D).any fun c => !(dfltLabelled (choiceSoft ⟨D, []⟩ c)).isEmpty).map (·.1)
  == ["K1", "K2", "K5", "K6", "K9", "K11", "K14", "K19", "M6", "M7", "M10", "M16", "M20"]

end VE.Readings.DefaultExamples
