import VE.Numbers.Phrases
import Lean

open VE.Numbers Lean

private def relName : Rel → String
  | .eq => "eq"
  | .lt => "lt"
  | .le => "le"

private def phraseJson (entry : String × Comparison) : Json :=
  Json.mkObj [
    ("text", toJson entry.1),
    ("rel", toJson (relName entry.2.rel)),
    ("swap", toJson entry.2.swap)
  ]

def main : IO Unit :=
  IO.println <| (toJson (orderPhrases.map phraseJson)).compress
