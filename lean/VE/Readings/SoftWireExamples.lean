import VE.Readings.SoftSupWireExamples

/-! sc-admit-cpu's fixtures (docs/rd-9/sc-admit-cpu/cpu.md; DRI 2026-11-11 sc-admit-cpu item 3): admission's charge
`sdAdmitWork N ≤ maxSdAdmitWork`, read before the per-choice texts of 4.1 step 5 (`sdTextsWithin`, `admitSDOf`).
Over it, 4.1 step 5 refuses with `ResourceLimit`; within it, its answer is the per-choice texts' as before the
charge; over 64 compatible choices no text runs and the charge is not read. The documents are SoftSupWireExamples'
(`NSDbig`, `NSDheavy`, `guarded`, `sized`). NSDheavy and heavyIn were admitted on main in 1.3-2.0 s of Lean CPU. -/
namespace VE.Readings.SoftWireExamples
open Lean VE.Readings VE.Readings.Wire
open VE.Readings.SoftSupWireExamples (envWith NSDbig NSDheavy guarded sized wideGuard767)
open VE.Readings.SoftSeparateExamples (D4)
open VE.Rights.Examples (strictNode)

/-- `NSDbig 6` and nine guarded fixed rules (sc-11w's `heavyIn`, docs/rd-9/sc-11w/cpu.md). -/
def heavyIn : NDoc := ⟨{ (NSDbig 6).D with items := (NSDbig 6).D.items ++ (List.range 9).map guarded }, ["y_permitted"]⟩
/-- `NSDbig 6` and thirteen fixed rules, twelve of two nodes and the first `r` of three: `32 * (63 + r)` per choice. -/
def NSDlimit (r : Nat) : NDoc := ⟨{ (NSDbig 6).D with items := (NSDbig 6).D.items ++ (List.range 13).map (fun k =>
  .fixed s!"g{k}" (.norm (strictNode s!"guarded-{k}" (["x_required", "x_permitted", "y_permitted"][k % 3]!) true
    (sized (if k < r then 3 else 2)))) []) }, ["y_permitted"]⟩
/-- At the limit: 64 choices of 2,048 units. -/
def atLimit : NDoc := NSDlimit 1
/-- One node more: 64 choices of 2,080 units, the next work this shape takes. -/
def overLimit : NDoc := NSDlimit 2

def texts (limit : Nat) (N : NDoc) : Option String :=
  match decodeEnvironment (envWith 0) with
  | .ok re => sdTextsWithin limit re N
  | .error e => some e

def refusal (limit : Nat) : Option String :=
  some s!"ResourceLimit: the per-reading checks of 64 readings exceed {limit} units"

-- NSDheavy and heavyIn: over the charge, refused before any per-choice text (the R5 regression rows)
#guard maxSdAdmitWork == 131072
#guard sdSizeCharge NSDheavy == 14703 && sdAdmitWork NSDheavy == 940992 && texts maxSdAdmitWork NSDheavy == refusal 131072
#guard sdSizeCharge heavyIn == 12880 && sdAdmitWork heavyIn == 824320 && texts maxSdAdmitWork heavyIn == refusal 131072
-- the same document under an adequate limit: its 64 per-choice texts run and pass, so it is admitted
#guard texts (sdAdmitWork heavyIn) heavyIn == none
-- at the limit admitted, one unit lower refused; the next work of the shape (133,120) refused
#guard sdAdmitWork atLimit == 131072 && texts maxSdAdmitWork atLimit == none &&
  texts (maxSdAdmitWork - 1) atLimit == refusal 131071
#guard sdAdmitWork overLimit == 133120 && texts maxSdAdmitWork overLimit == refusal 131072
-- the named NSDbig 6: within the charge, admitted
#guard sdAdmitWork (NSDbig 6) == 44992 && texts maxSdAdmitWork (NSDbig 6) == none
-- over 64 choices: no text runs and the charge is not read, although the work is over it (as before the charge)
#guard (choices wideGuard767.D).length == 65 && sdAdmitWork wideGuard767 > maxSdAdmitWork &&
  texts maxSdAdmitWork wideGuard767 == none
-- within the charge a failing choice's text is today's, byte for byte (`findSome?` of `sdChoiceText`)
#guard match decodeEnvironment (envWith 0) with
  | .ok re => let N : NDoc := ⟨D4, ["bogus"]⟩
    sdAdmitWork N ≤ maxSdAdmitWork && (sdTextsWithin maxSdAdmitWork re N).isSome &&
      sdTextsWithin maxSdAdmitWork re N == (choices N.D).findSome? (sdChoiceText re N)
  | .error _ => false

end VE.Readings.SoftWireExamples
