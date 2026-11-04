import VE.Defaults.ZoneWire
import Lean

open VE.Defaults.Wire Lean

/-- `ve/defaults_words.json`: the words of DE10 to DE13 (`zoneHeads`, `zoneLineWords`, `zoneJoins`), each row with
    the answer's fields that select it. -/
def main : IO Unit :=
  IO.println <| (Json.mkObj [
    ("heads", toJson (zoneHeads.map fun (z, f, r, w) =>
      Json.mkObj [("zone", .str z), ("form", .str f), ("row", .str r), ("words", .str w)])),
    ("lines", toJson (zoneLineWords.map fun (r, k, s, i) =>
      Json.mkObj [("row", .str r), ("kind", .str k), ("sentence", .str s), ("inline", .str i)])),
    ("joins", Json.mkObj (zoneJoins.map fun (k, w) => (k, .str w)))]).compress
