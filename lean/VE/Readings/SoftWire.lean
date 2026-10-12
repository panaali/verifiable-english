import VE.Readings.UnspecifiedWire

/-! Admission of a readings document under the soft completion. The public route is
enabled only after separation and per-choice replay use this admitted value. -/
namespace VE.Readings.Wire
open Lean
open VE.Readings

def underSoftCompletion (re : ReadingsEnvironment) (D : Doc) : Bool :=
  re.lower.contains normDefaultsProfile && re.chain == .soft && D.sets.any contentBearing

/-- The source choice is checked before its completion and generated decisions. -/
def sdChoiceText (re : ReadingsEnvironment) (N : NDoc) (c : Choice) : Option String :=
  (choiceChainText N.D c).or
    ((ndDocTextG re (decisionCount (choiceDoc N.D c).1) (choiceU N c)).map
      (· ++ " under " ++ choiceText N.D c))

structure AdmittedSD where
  b : Admitted2
  N : NDoc
  hN : N.D = b.D
  wf : WellFormedSD N = true
  side : ∀ s i, b.a.side s i = one N.D s i

/-- Continue S2 admission using the common fill checks and the soft shape. -/
def admitSDOf (b : Admitted2) : Except String AdmittedSD :=
  let re := b.a.re
  let N : NDoc := ⟨b.D, unspecOf re b.D⟩
  if hsd : b.D.chain = b.a.D.chain ∧ b.D.items = b.a.D.items then
    have hside : ∀ s i, b.a.side s i = one N.D s i := fun s i => by
      rw [b.a.side_eq]
      exact one_congr hsd.1.symm (by rw [b.frame]; rfl) hsd.2.symm s i
    match hT : ndTextWith re N b.a.side with
    | some e => .error e
    | none =>
      have hT' : ndText re N = none := (ndTextWith_eq hside) ▸ hT
      if hs : softShaped N.D = true then
        match hc : if (choices N.D).length ≤ maxChoices then
            (choices N.D).findSome? (sdChoiceText re N) else none with
        | some e => .error e
        | none =>
          .ok ⟨b, N, rfl, by
            simpa [wellFormedSD_eq, hs, fillRest_of_ndText hT'] using b.wf, hside⟩
      else .error "InvalidInput: norm-defaults document is not well formed"
  else .error "InvalidInput: readings document is not well-formed"

def admitSD (environment document : Json) : Except String AdmittedSD := do
  let b ← admitS2 environment document
  unless underSoftCompletion b.a.re b.D do
    throw "UnsupportedProfile: the document is not under the unspecified completion"
  admitSDOf b

end VE.Readings.Wire
