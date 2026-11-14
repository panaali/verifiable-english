import VE.Readings.Wire
/-! kb-2a-b, for build_rsp_mixed.py: the id the readings route gives a situation entry over a written environment
(`VE.Readings.Wire.decodeSituation`'s `computed`), which Python cannot compute for an environment that lists
`judgments@0`. Usage: `lake env lean --run situation_id.lean ENVIRONMENT.json ENTRY.json`. -/
open Lean

def main (args : List String) : IO Unit := do
  let env ← IO.FS.readFile args[0]!
  let entry ← IO.FS.readFile args[1]!
  let result : Except String String := do
    let e ← Json.parse env
    let s ← Json.parse entry
    let re ← VE.Readings.Wire.decodeEnvironment e
    let envId ← VE.Route.Wire.environmentId re.profiles (← VE.Norms.Wire.canonicalEnvironmentJson re.json)
    VE.CertificateWire.digest s!"ve-situation-{VE.Route.Wire.identityVersion re.profiles}\n"
      (Json.mkObj [("environment_id", .str envId), ("situation", s)])
  match result with
  | .ok d => IO.println d
  | .error e => throw (IO.userError e)
