import VE.Scope.Run
import VE.Scope.Examples
import VE.Scope.ReadingsExamples

/-! Acceptance fixtures of the explain route (docs/spec/scope.md 7.3, SC-1c) on the hard-constraint layout of
    `VE.Scope.Examples`, with u0173.s01 after it; the rows per choice (sc-1cb) on sc-5rb's fixtures of a reading set
    governed per choice (`VE.Scope.ReadingsExamples`, scope 11.6). -/

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

/-! sc-1cb: a reading set governed per choice (scope 11). -/

def sdOn (doc : Json) (gs : List Governor) : Except String SDoc := do
  pure (sdoc doc gs [] (← VE.Readings.Wire.decodeEnvironment envJ))
/-- The route's groups, each choice named by `choiceText`. -/
def groups (doc : Json) (gs : List Governor := [g1]) (limit : Nat := Run.cellLimit) :
    Except String (List (String × List Row)) := do
  let D ← sdOn doc gs
  pure ((← Run.explainSetsWithin limit D source).map fun (ch, rows) => (choiceText D ch, rows))
/-- Spec 5.3's rows of each choice's document (`explainRows (atChoice D ch)`), in lf-14d's order. -/
def perChoiceRows (doc : Json) (gs : List Governor := [g1]) : Except String (List (List Row)) := do
  let D ← sdOn doc gs
  (← setChoices D).mapM fun ch => @explainRows ⟨fun u => ((Run.quotesOf D source.toUTF8).lookup u).getD ""⟩ (atChoice D ch)
def twoDoc : Json := setDoc [s03, s05set] twoSets
def strOf (p : Json) (k : String) : String := (p.getObjValD k).getStr?.toOption.getD ""
def outcome {α} (r : Except String α) : String := match r with | .ok _ => "ok" | .error e => e

-- SR-1: two groups, labelled wide then narrow, each F-ex's seven rows under g1; the coupled sets: four, s03 first
#guard (groups (setDoc [s03])).toOption.map (·.map (·.1)) ==
  some ["u0165.s03 scope-u0165-s03@1:wide", "u0165.s03 scope-u0165-s03@1:narrow"]
#guard (groups (setDoc [s03])).toOption.map (·.map fun (_, rs) => rs.map fun r => (r.unit, r.governors.map (·.id), r.provenance)) ==
  some [seven.map fun u => (u, ["g1"], [fr]), seven.map fun u => (u, ["g1"], [fr])]
#guard (groups twoDoc).toOption.map (·.map (·.1)) == some ["u0165.s03 scope-u0165-s03@1:wide, u0165.s05 scope-u0165-s05@1:a",
  "u0165.s03 scope-u0165-s03@1:wide, u0165.s05 scope-u0165-s05@1:b", "u0165.s03 scope-u0165-s03@1:narrow, u0165.s05 scope-u0165-s05@1:a",
  "u0165.s03 scope-u0165-s03@1:narrow, u0165.s05 scope-u0165-s05@1:b"]
-- each group holds `explainRows (atChoice D ch)`, one per choice (u0166.s01's rule depends on the choice in SR-dep's
-- admitted form: hc-cyberweapons on one predicate)
#guard [(setDoc [s03], [g1]), (twoDoc, [g1]), (setDoc [s03] depParts, [g1, gPr]), (setDoc [s03], [g1, gR])].all fun (d, gs) =>
  (groups d gs).toOption.map (·.map (·.2)) == (perChoiceRows d gs).toOption && (perChoiceRows d gs).isOk
-- the label is `choiceText`'s, typed (`choiceJson`): its picks written as 11.5 writes them
#guard (do
    let D ← sdOn twoDoc [g1]
    let cs ← setChoices D
    pure (cs.all fun ch => match Run.choiceJson (governedSets D) ch with
      | .arr ps => ", ".intercalate (ps.toList.map fun p => strOf p "unit" ++ " " ++ strOf p "set" ++ "@" ++
          (p.getObjValD "version").compress ++ ":" ++ strOf p "reading") == choiceText D ch
      | _ => false)).toOption == some true
-- the gate is `governSets`': the same refusal text on 11.6's refused fixtures (SR-c, SR-c-nr, SR-g, SR-dep, SR-cap's
-- 72 and 65, a second version, a set without a reading) and admitted on SR-1, SR-u and the coupled sets
#guard [(setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
      (cyberPart "cyberweapon_creation_permitted" guardNarrow [("sign", .bool false)])], [g1]),
    (setDoc [s03set (j "[\"top\"]") (cyberPart "cyberweapon_creation_permitted" guardNarrow)], [g1]),
    (setDoc [rset "lead" "u0164.s02" [reading "a" .null], s03], [g1]),
    (setDoc [s03], [⟨"gX", "u0165.s03", carveT, .list "u0164.s02", seven⟩, g1]),
    (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide) (cyberPart "other_permitted" guardNarrow)]
      depParts, [g1, gPr]),
    (setDoc [wideSet "s3" "u0165.s03" 8, wideSet "s5" "u0165.s05" 9] twoSets, [g1]),
    (setDoc [wideSet "s3" "u0165.s03" 5, wideSet "s5" "u0165.s05" 13] twoSets, [g1]),
    (setDoc [s03, s03.setObjVal! "version" (2 : Nat)], [g1]), (setDoc [s03, u0166set], [g1]), (twoDoc, [g1])].all
  fun (d, gs) => outcome (groups d gs) == errorOf (sets d gs)
#guard outcome (groups (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
    (cyberPart "cyberweapon_creation_permitted" guardNarrow [("sign", .bool false)])])) ==
  "ScopeChoice: u0165.s03 scope-u0165-s03@1:narrow: ScopeConflict: u0165.s03: sign"
-- the cells are summed over the choices: SR-1's two groups hold 2 × 7 × (7 + 1); at 112 it answers, at 111 (above one
-- group's 56) it is UNKNOWN
#guard (groups (setDoc [s03]) [g1] 112).isOk && outcome (groups (setDoc [s03]) [g1] 111) == "ResourceLimit: scope explain answer cells"
-- 64 joint choices (8 by 8) are answered within the route's limit (64 × 7 × 8 cells); 65 (5 by 13) are UNKNOWN
#guard (groups (setDoc [wideSet "s3" "u0165.s03" 8, wideSet "s5" "u0165.s05" 8] twoSets)).toOption.map (·.length) == some 64 &&
  (do pure (decide (Run.cellBound (← sd [g1]) (64 * 7) ≤ Run.cellLimit))).toOption == some true
#guard outcome (groups (setDoc [wideSet "s3" "u0165.s03" 5, wideSet "s5" "u0165.s05" 13] twoSets)) == "ResourceLimit: scope choices"
-- a document with no governed set: today's answer, byte for byte (F-ex), never the choice loop
#guard (do
    let D ← sd [g1, g2]
    let rows ← Run.explainWithin Run.cellLimit D source
    pure ((Run.answerOf "x" D source).toOption.map Json.compress == some (Json.mkObj [("governed", Run.governedJson D rows),
      ("id", "x"), ("rows", .arr (rows.map Run.rowJson).toArray), ("status", "ok")]).compress && rows.length == 7)).toOption ==
  some true

end VE.Scope.RunExamples
