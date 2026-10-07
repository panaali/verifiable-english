import VE.Readings.SupExtra
import VE.Readings.Examples

/-! The fixtures of RD-6a (docs/spec/readings-defaults-PLAN.md RD-6a), each a `#guard` on S2a's M1 document `K1`.

X1 is the counterexample that made `superpose_all_extra` take `hQw` (the approved statement has no typing of `Q`).
`noAvoid` is `∀agent ∀user. ¬avoid_required`. It is over the shared vocabulary and over each choice's complete
vocabulary, and the name map fixes `avoid_required`. A base admissible for `sup K1` gives `avoid_required`, a layer
symbol and so not in its base vocabulary, no tuple, and the pulled base gives it the same relation. So
`Q = Q' c = [noAvoid]` holds of every such base, and `Transfers K1 [noAvoid] (fun _ => [noAvoid])` holds, and so
does the conflict-freedom hypothesis, since K1 is CONFLICT-FREE (S2a M1, one rule per reading) and `Q` excludes no
base. The certificate `closeCert` (one closing step) is accepted with `Q` in the slot. Yet the bare base, admissible
for both readings' documents and satisfying `noAvoid` as a base, has `avoid_required (a, u)` on both readings'
expansions, so `noAvoid` is false there: the approved conclusion fails. `hQw` excludes `Q` (X1.3). X2 checks that the
`_extra` checks at `Q = []` are the S2a checks on M2's bases. -/
namespace VE.Readings.SupExtraExamples
open VE.Readings
open VE.Readings.Examples (K1 baseM)
open VE.Rights (correlate)
open VE.Norms (envAt)
open VE.SoftNorms (soften circ)

def noAvoid : VE.Formula := .all "agent" (.all "user" (.not (.binary "avoid_required" (.var 1) (.var 0))))
def closeCert : VE.Tableau.Certificate := ⟨"ve-tableau-checker@2", "", [], "", .close⟩
/-- One agent, one user, no constant and no tuple. -/
def bare : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => ["u"] | _ => []
  constants _ := none
  relations _ := []

/-! ## X1: `superpose_all_extra` without `hQw` -/

-- X1.1: `φ = noAvoid` is over the shared vocabulary (`hφ`)
#guard noAvoid.check (sharedEnv K1) []
-- X1.2: `Q' c = [noAvoid]` is over each choice's complete vocabulary (`Transfers`' first conjunct), and the name map
-- fixes `avoid_required`, so the pulled base reads it as the base does
#guard choices K1 == [[("rs1", 0)], [("rs1", 1)]]
#guard (choices K1).all (fun c => noAvoid.check (choiceEnvFull K1 c) [] && nameMap K1 c "avoid_required" == "avoid_required")
-- X1.3: `noAvoid` is not over `sup K1`'s base vocabulary (`hQw` fails), while the slot is
#guard !VE.Compose.slotCheck (correlate (sup K1).1) [noAvoid]
#guard VE.Compose.slotCheck (correlate (sup K1).1) (slotUnder K1 [])
-- X1.4: the certificate is accepted with `Q` in the slot, and not without it
#guard supCertificateCheckExtra K1 [] [noAvoid] [] noAvoid closeCert
#guard !supCertificateCheck K1 [] [] noAvoid closeCert
-- X1.5: the bare base satisfies each reading's background with `Q' c`, and `noAvoid` as a base sentence, and K1's
-- readings assert nothing
#guard (choices K1).all (fun c => VE.Compose.backgroundValidP (correlate (choiceDoc K1 c).1)
  (VE.Rights.limPremises (choiceDoc K1 c).1 ++ [noAvoid]) bare && (choiceDoc K1 c).2.isEmpty)
#guard noAvoid.eval bare []
-- X1.6: on each reading's expansion of the bare base `noAvoid` is false (`circ_canon`)
#guard (choices K1).all (fun c => !(circ (correlate (choiceDoc K1 c).1) noAvoid).eval bare [])

/-! ## X2: at `Q = []` the checks are S2a's (`supCertificateCheckExtra_nil`, `supModelCheckExtra_nil`) -/

#guard [baseM true true, baseM false false, baseM false true].all (fun M =>
  supModelCheckExtra K1 [] [] [] M == supModelCheck K1 [] [] M &&
  supModelCheckExtra K1 [("rs1", 1)] [] [] M == supModelCheck K1 [("rs1", 1)] [] M)
#guard supCertificateCheckExtra K1 [] [] [noAvoid] noAvoid closeCert == supCertificateCheck K1 [] [noAvoid] noAvoid closeCert
#guard supCertificateCheck K1 [] [noAvoid] noAvoid closeCert
-- with `Q` the model check reads `Q` on the base: `baseM true true` satisfies `noAvoid` and not `¬noAvoid`
#guard supModelCheckExtra K1 [] [noAvoid] [] (baseM true true)
#guard !supModelCheckExtra K1 [] [.not noAvoid] [] (baseM true true)

end VE.Readings.SupExtraExamples
