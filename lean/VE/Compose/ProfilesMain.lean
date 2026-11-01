import VE.Compose.Dispatch
import Lean

/-! Prints `ve/profile_table.json` (tools/profile_table.py): the profiles an environment lists and the rows of
`VE.Compose.profileTable`, which Python reads and never writes. -/
open VE.Compose Lean

private def rowJson (r : ProfileRow) : Json :=
  Json.mkObj [("profile", toJson r.profile), ("requires", toJson r.requires),
    ("refuses", toJson (r.refuses.map fun (q, text) => [q, text])), ("slot", toJson r.slot)]

def main : IO Unit :=
  IO.println <| (Json.mkObj [("environment", toJson environmentProfiles), ("document_layers", toJson documentLayers),
    ("rows", toJson (profileTable.map rowJson))]).pretty
