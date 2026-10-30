import VE.Scope.Run
import VE.Scope.Examples

/-! Acceptance fixtures of the explain route (docs/spec/scope.md 7.3, SC-1c) on the hard-constraint layout of
    `VE.Scope.Examples`, with u0173.s01 after it. -/

namespace VE.Scope.RunExamples
open Lean VE.Scope VE.Scope.Examples

def source : String := (mk govPieces).1

def sd (gs : List Governor) : Except String SDoc := do
  pure (sdoc (hcDoc parts) gs hcNames (← VE.Readings.Wire.decodeEnvironment envJ))

def rowsOf (gs : List Governor) (limit : Nat := Run.cellLimit) : Except String (List Row) := do
  Run.explainWithin limit (← sd gs) source

def gP : Governor := ⟨"gP", "u0165.s02", .precedes, .rules ["hc-cbrn-uplift"], ["u0165.s01"]⟩
def gY : Governor := ⟨"gY", "u0165.s02", .yields, .rules ["hc-cbrn-uplift"], ["u0165.s01"]⟩

def fr : String := "The start of this rule comes from the line above the list, \"Claude should never:\"."
def g2s : String := "Its condition comes from a later sentence, \"Hard constraints are centrally meant to apply to cases where " ++
  "Claude would …\", which covers all 7 items of this list."
def item2 : String := "\"* Provide serious uplift to attacks on critical infrastructure (power grids, water …\""
def shown (r : Except String (List Row)) : Option (List (String × List String × List String)) :=
  r.toOption.map (·.map fun r => (r.unit, r.governors.map (·.id), r.provenance))

-- F-ex: seven rows, u0165.s01–s07, each with governors [g1, g2]; no row for u0164.s02, u0166.s01, u0173.s01
#guard shown (rowsOf [g1, g2]) == some (seven.map fun u => (u, ["g1", "g2"], [fr, g2s]))
#guard (rowsOf [g1, g2]).toOption.map (·.map (·.governors.map fun x => (x.unit, x.effect, x.reach))) ==
  some (seven.map fun _ => [("u0164.s02", "frame", seven), ("u0173.s01", "reguard", seven)])
-- the run path answers as spec 5.3's `explainRows` (`explainFast_eq`), and a refusal of `govern` is the answer
#guard (do let D ← sd [g1, g2, gR]; pure ((@explainFast ⟨fun _ => "q"⟩ D).toOption == (@explainRows ⟨fun _ => "q"⟩ D).toOption)).toOption == some true
#guard (rowsOf [{g1 with units := seven.take 6}]) matches .error "ManifestMismatch: scope.governors.g1.units"
-- each contributor's sentence: a carve-out by rule name from an earlier sentence, `precedes` on its own rule,
-- `yields` on the reached rule (naming the governor's rule)
#guard (shown (rowsOf [g1, gR])).map (·.getLast?) == some (some ("u0165.s07", ["g1", "gR"], [fr,
  "Its exception comes from an earlier sentence, \"The current hard constraints on Claude’s behavior are as follows.\", " ++
  "which covers 1 rule."]))
#guard (shown (rowsOf [g1, gP])).map (·.lookup "u0165.s02") == some (some (["g1", "gP"], [fr,
  "It takes precedence over hc-cbrn-uplift; this comes from " ++ item2 ++ "."]))
#guard (shown (rowsOf [g1, gY])).map (·.lookup "u0165.s01") == some (some (["g1", "gY"], [fr,
  "hc-2 takes precedence over it; this comes from a later sentence, " ++ item2 ++ "."]))
#guard (shown (rowsOf [g1, gY])).map (·.lookup "u0165.s02") == some (some (["g1"], [fr]))
-- the answer's index of its rows: each governor in the block's order with the units whose rows list it
#guard (do let D ← sd [g1, gR]; pure (Run.governedJson D (← rowsOf [g1, gR])).compress).toOption ==
  some ("[{\"id\":\"g1\",\"units\":" ++ (Json.arr (seven.map Json.str).toArray).compress ++
    "},{\"id\":\"gR\",\"units\":[\"u0165.s07\"]}]")
-- spec 5.3's effect words
#guard effectWords == ["frame", "reguard", "carve-out", "precedes", "yields", "title"]
-- 2.3's `<where>` and `<cover>` on each reach kind; `<text>` at and around 12 words
#guard (do let D ← sd [g1, g2]; pure [whereOf D g1 "u0165.s01", whereOf D g2 "u0165.s01",
  whereOf D {g2 with unit := "u0164.s02"} "u0165.s01", whereOf D {g2 with reach := .label "u0165.s01"} "u0165.s01",
  whereOf D {g2 with reach := .anchor "a"} "u0165.s01", whereOf D {g2 with reach := .rules [], unit := "u0164.s01"} "u0165.s01"]).toOption ==
  some ["the line above the list", "a later sentence", "the line above the list", "the label of this item",
    "the heading of this section", "an earlier sentence"]
#guard [coverOf g2 7, coverOf gR 1, coverOf gR 2, coverOf {gR with reach := .list "x"} 3] ==
  ["all 7 items of this list", "1 rule", "2 rules", "all 3 items of this list"]
#guard [quote "a b c d e f g h i j k l", quote " a b c d e f g h i j k l m", quote "a\n b"] ==
  ["a b c d e f g h i j k l", "a b c d e f g h i j k l …", "a b"]
-- the answer's cells: [g1, g2] has 7 rows of (7 + 1) + (7 + 1) cells; at the bound it answers, one below it is UNKNOWN
#guard (do pure (Run.cellBound (← sd [g1, g2]) 7)).toOption == some 112
#guard (rowsOf [g1, g2] 112).isOk && (rowsOf [g1, g2] 111) matches .error "ResourceLimit: scope explain answer cells"
#guard (rowsOf [g1, g2] 0) matches .error "ResourceLimit: scope explain answer cells"

end VE.Scope.RunExamples
