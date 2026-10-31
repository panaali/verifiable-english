import VE.Readings.SoftVerdicts
import VE.Readings.SupExtra

/-! SC-10's first part (docs/spec/rd-9-soft-chain.md 13.1, 13.3): superposition under the soft completion.

The superposed soft document is read as norm-defaults reads a soft document (`supU N`), and `fill` runs after
`soften`, on the superposed document (D1). `fill (supU N)` is not `soften` of any superposed document, so S2a's
simulation is applied to the author rules and `fill` is added on each side: a filled tree decides as its author rules
do, or by `F_p` where the gap says yes and the author rules are silent (`decidesD_fill`). The filled pull `pullF` is
S2a's `pull` onto the filled choice's vocabulary, which keeps the `unsaid__` tables (13.4 item 3). -/
namespace VE.Readings
open VE.Norms (Regulated Sat envAt size)
open VE.NormDefaults (fill)
universe u

/-- The superposed document's extra base premises under the soft completion (D2 on `sup`). -/
def supX (N : NDoc) : List VE.Formula := softX N (sup N.D).1

/-- S2a's `pull` onto the filled choice's full vocabulary: keeps the `unsaid__` tables. -/
def pullF (N : NDoc) (c : Choice) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun p vs =>
      (envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates p ≠ none ∧ S.relation (nameMap N.D c p) vs }

/-- The free document's filled full vocabulary: the queries' vocabulary on the superposed route (OPEN-SC10-1). -/
def sharedEnvSD (N : NDoc) : VE.Environment := envAt (fill (freeU N)) (size (fill (freeU N)))

/-- A certificate on the filled superposed document under `A`: slot, atoms, `supX`, then `Fill_T` (`premisesX`). -/
def supCertificateCheckSD (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (fill (supU N)) (size (fill (supU N))))
    (VE.NormDefaults.Wire.premisesX (supU N) (slotUnder N.D A ++ supX N) ((sup N.D).2 ++ Γ)) φ cert

end VE.Readings
