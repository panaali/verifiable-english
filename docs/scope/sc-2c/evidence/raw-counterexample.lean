import VE.Scope.Examples
open Lean VE.Scope VE.Scope.Examples
open Std.DTreeMap.Internal (Impl)
-- a raw rule tree no parser builds: `guard` at the root (lookup finds it) and again in the right subtree
def cxRule : Json := rawJ (nd "guard" (j "[\"top\"]")
  (nd "name" "r" (nd "over" (.arr #[])) (nd "predicate" "p"))
  (nd "sign" (.bool false) (nd "guard" (j "[\"top\"]")) (nd "unless" (.arr #[]))))
-- reguard_applies: prints N.guard, N'.guard, G', the first conjunct, jsonWF?
def cxC : Json := j "[\"not\", \"own\"]"
#eval do
  let re ← VE.Readings.Wire.decodeEnvironment softEnv
  let o' ← applyEffect "u" (.reguard cxC) cxRule
  let N ← VE.Readings.Wire.decodeNorm re cxRule
  let N' ← VE.Readings.Wire.decodeNorm re o'
  let G' ← VE.Norms.Wire.decodeBudgeted (substOwn (cxRule.getObjValD "guard") depthLimit cxC)
  pure (repr N.guard, repr N'.guard, repr G', N' == { N with guard := G' }, jsonWF? cxRule)
-- carveOut_applies: `unless` at the root (lookup finds it) and again later in traversal
def cxRule3 : Json := rawJ (nd "unless" (.arr #[])
  (nd "guard" (j "[\"top\"]") (nd "name" "r") (nd "over" (.arr #[])))
  (nd "sign" (.bool false) (nd "predicate" "p") (nd "unless" (.arr #[]))))
#eval do
  let re ← VE.Readings.Wire.decodeEnvironment softEnv
  let c := j "[\"bottom\"]"
  let o' ← applyEffect "u" (.carveOut c) cxRule3
  let N ← VE.Readings.Wire.decodeNorm re cxRule3
  let N' ← VE.Readings.Wire.decodeNorm re o'
  let C ← VE.Norms.Wire.decodeBudgeted (substOwn (cxRule3.getObjValD "guard") depthLimit c)
  pure (N.carveOuts.length, N'.carveOuts.length, N' == { N with carveOuts := N.carveOuts ++ [C] })
-- restrict_applies: the same tree as reguard_applies
#eval do
  let re ← VE.Readings.Wire.decodeEnvironment softEnv
  let C := j "[\"bottom\"]"
  let o' ← applyEffect "u" (.reguard (Json.arr #[.str "and", .str "own", C])) cxRule
  let N ← VE.Readings.Wire.decodeNorm re cxRule
  let N' ← VE.Readings.Wire.decodeNorm re o'
  let C' ← VE.Norms.Wire.decodeBudgeted C
  pure (hasOwn depthLimit C, N' == { N with guard := .and N.guard C' })
