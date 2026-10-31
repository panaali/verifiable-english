import VE.Scope.Examples
import VE.Scope.Readings

/-! Scope spec 11.6's fixtures (sc-5r's statement stub, `docs/spec/scope/SpecStubs_sc5r.lean`, verbatim; sc-5rb):
    each value is computed by `#guard` over the hard-constraint document of `VE.Scope.Examples` (`hcDoc`, `parts`,
    `g1`), on `governSets` as `lean/VE/Scope/Readings.lean` defines it. -/

namespace VE.Scope.Examples
open Lean VE.Scope

def guardWide : Json := j "[\"and\", [\"or\", [\"unary\", \"creating_a_cyberweapon\", [\"var\", 1]], [\"unary\", \"creating_malicious_code\", [\"var\", 1]]], [\"unary\", \"could_cause_significant_damage_if_deployed\", [\"var\", 1]]]"
def guardNarrow : Json := j "[\"or\", [\"unary\", \"creating_a_cyberweapon\", [\"var\", 1]], [\"and\", [\"unary\", \"creating_malicious_code\", [\"var\", 1]], [\"unary\", \"could_cause_significant_damage_if_deployed\", [\"var\", 1]]]]"
def cyberPart (pred : String) (g : Json) (extra : List (String × Json) := []) : Json :=
  Json.mkObj [("part", Json.mkObj ([("name", Json.str "hc-cyberweapons"), ("predicate", Json.str pred), ("guard", g)] ++ extra))]
def reading (id : String) (content : Json) : Json :=
  Json.mkObj [("id", id), ("kind", "norm"), ("meaning_id", s!"m-{id}"), ("content", content),
    ("admission", Json.mkObj [("who", "translator"), ("why", "the clause attaches to both nouns or to one")])]
def rset (id unit : String) (rs : List Json) : Json :=
  Json.mkObj [("id", id), ("unit", unit), ("version", (1 : Nat)), ("status", "open"), ("readings", .arr rs.toArray)]
/-- u0165.s03's set as the pilot records it (two candidates, wide and narrow), each reading a part under the frame. -/
def s03set (wide narrow : Json) : Json := rset "scope-u0165-s03" "u0165.s03" [reading "wide" wide, reading "narrow" narrow]
def s03 : Json := s03set (cyberPart "cyberweapon_creation_permitted" guardWide) (cyberPart "cyberweapon_creation_permitted" guardNarrow)
/-- The hard-constraint document: the six other items' parts, u0165.s03 without content, and the given sets. -/
def setDoc (sets : List Json) (cs : List (String × Json) := without "u0165.s03" parts) : Json :=
  hcDoc cs [("reading_sets", .arr sets.toArray)]
def sets (doc : Json) (gs : List Governor) (ln : List (VE.Discourse.ContentName × String × String) := []) :
    Except String Json := do
  governSets (sdoc doc gs ln (← VE.Readings.Wire.decodeEnvironment envJ))
def readingContents (r : Except String Json) (u : String) : Option (List String) :=
  r.toOption.map fun o => (((setsJson o).find? (setUnit · == u)).map fun s =>
    (readingsJson s).map (·.getObjValD "content" |>.compress)).getD []
def wideNorm : String :=
  "{\"norm\":{\"guard\":[\"and\",[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"unary\",\"creating_malicious_code\",[\"var\",1]]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]],\"name\":\"hc-cyberweapons\",\"over\":[],\"predicate\":\"cyberweapon_creation_permitted\",\"sign\":false,\"unless\":[]}}"
def narrowNorm : String :=
  "{\"norm\":{\"guard\":[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"and\",[\"unary\",\"creating_malicious_code\",[\"var\",1]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]]],\"name\":\"hc-cyberweapons\",\"over\":[],\"predicate\":\"cyberweapon_creation_permitted\",\"sign\":false,\"unless\":[]}}"

/-- SR-1 with `g2`: the wide reading's rule, re-guarded by u0173.s01's condition (the F3 shape of 7.4). -/
def wideG2 : String :=
  "{\"norm\":{\"guard\":[\"or\",[\"and\",[\"and\",[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"unary\",\"creating_malicious_code\",[\"var\",1]]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]],{\"attitude\":{\"content\":[\"and\",[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"unary\",\"creating_malicious_code\",[\"var\",1]]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]],\"holder\":[\"var\",0],\"mode\":\"knows\"}}],{\"attitude\":{\"content\":[\"and\",[\"or\",[\"unary\",\"creating_a_cyberweapon\",[\"var\",1]],[\"unary\",\"creating_malicious_code\",[\"var\",1]]],[\"unary\",\"could_cause_significant_damage_if_deployed\",[\"var\",1]]],\"degree\":\"quite likely\",\"holder\":[\"var\",0],\"mode\":\"thinks\"}}],\"name\":\"hc-cyberweapons\",\"over\":[],\"predicate\":\"cyberweapon_creation_permitted\",\"sign\":false,\"unless\":[]}}"
/-- The narrow reading's rule is the one `govern` gives u0165.s03 when its part is written in place of the set. -/
def narrowG2 : Option String :=
  contentStr (gov (hcDoc ((without "u0165.s03" parts) ++ [("u0165.s03", cyberPart "cyberweapon_creation_permitted" guardNarrow)])) [g1, g2] hcNames) "u0165.s03"

-- SR-1: u0165.s03's set inside the hard-constraint list. Two choices, each conflict-free: the list is admitted; each
-- reading is composed as the unit would be; u0165.s03 stays as written; the other items are F1-g's
#guard (do pure (governedSetUnits (sdoc (setDoc [s03]) [g1] [] (← VE.Readings.Wire.decodeEnvironment envJ))) :
  Except String (List String)).toOption == some ["u0165.s03"]
#guard (do setChoices (sdoc (setDoc [s03]) [g1] [] (← VE.Readings.Wire.decodeEnvironment envJ))).toOption ==
  some [[("scope-u0165-s03", 1, 0)], [("scope-u0165-s03", 1, 1)]]
#guard readingContents (sets (setDoc [s03]) [g1]) "u0165.s03" == some [wideNorm, narrowNorm]
#guard contentStr (sets (setDoc [s03]) [g1]) "u0165.s03" == some "null"
#guard contentStr (sets (setDoc [s03]) [g1]) "u0165.s01" == contentStr (gov (hcDoc parts) [g1]) "u0165.s01" &&
  (contentStr (sets (setDoc [s03]) [g1]) "u0165.s01").isSome
-- the per-choice statement on SR-1: each choice read off the answer is `govern` of that choice
def perChoice (doc : Json) (gs : List Governor) : Except String Bool := do
  let D := sdoc doc gs [] (← VE.Readings.Wire.decodeEnvironment envJ)
  let out ← governSets D
  let cs ← setChoices D
  cs.allM fun ch => do pure (VE.Readings.Wire.jeq (atChoiceOn (governedSetUnits D) out ch) (← governChoice D ch))
#guard (perChoice (setDoc [s03]) [g1]).toOption == some true
-- with g2 (the re-guard over the list name) too: every reading is re-guarded, as the items are
#guard (readingContents (sets (setDoc [s03]) [g1, g2] hcNames) "u0165.s03") == (narrowG2.map fun n => [wideG2, n]) && narrowG2.isSome &&
  contentStr (sets (setDoc [s03]) [g1, g2] hcNames) "u0165.s01" == contentStr (gov (hcDoc parts) [g1, g2] hcNames) "u0165.s01"

-- SR-c: one choice conflicts (its reading writes `sign`, which the frame writes): refused, naming the unit and choice
#guard errorOf (sets (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
    (cyberPart "cyberweapon_creation_permitted" guardNarrow [("sign", .bool false)])]) [g1]) ==
  "ScopeChoice: u0165.s03 scope-u0165-s03@1:narrow: ScopeConflict: u0165.s03: sign"
-- a reading that is an assertion under the frame: refused under its choice, never skipped
#guard errorOf (sets (setDoc [s03set (j "[\"top\"]") (cyberPart "cyberweapon_creation_permitted" guardNarrow)]) [g1]) ==
  "ScopeChoice: u0165.s03 scope-u0165-s03@1:wide: ScopeNotARule: u0165.s03"

-- SR-cap: two governed sets of 8 and 9 readings (72 joint choices): ResourceLimit, UNKNOWN; 8 and 8 (64) are checked
def wideSet (id unit : String) (n : Nat) : Json :=
  rset id unit ((List.range n).map fun i => reading s!"r{i}" (cyberPart "cyberweapon_creation_permitted" guardWide))
#guard errorOf (sets (setDoc [wideSet "s3" "u0165.s03" 8, wideSet "s5" "u0165.s05" 9] ((without "u0165.s05" parts).filter (·.1 != "u0165.s03"))) [g1]) ==
  "ResourceLimit: scope choices"
#guard errorOf (sets (setDoc [wideSet "s3" "u0165.s03" 8, wideSet "s5" "u0165.s05" 8] ((without "u0165.s05" parts).filter (·.1 != "u0165.s03"))) [g1]) ==
  "ok"

-- SR-u: a reading set on a unit no governor covers (u0166.s01) is returned unchanged, beside a governed set and alone
def u0166set : Json := rset "u0166-set" "u0166.s01" [reading "a" .null, reading "b" .null]
#guard (sets (setDoc [s03, u0166set]) [g1]).toOption.map (fun o =>
  ((setsJson o).find? (setUnit · == "u0166.s01")).map (VE.Readings.Wire.jeq u0166set)) == some (some true)
#guard (sets (hcDoc parts [("reading_sets", .arr #[u0166set])]) [g1]).toOption.map (VE.Readings.Wire.jeq ·
  ((gov (hcDoc parts [("reading_sets", .arr #[u0166set])]) [g1]).toOption.getD .null)) == some true

-- SR-0: no reading set: the answer is `govern`'s, as a value (F1-g's document, and F-id's)
#guard (sets (hcDoc parts) [g1]).toOption.map (VE.Readings.Wire.jeq · ((gov (hcDoc parts) [g1]).toOption.getD .null)) ==
  some true
#guard same (sets (hcDoc fourNorms [("title", "x")]) []) (hcDoc fourNorms [("title", "x")])

-- SR-g: still refused (F-rs's governor half): a set on the governor's own unit; a set on a governed unit that has content
#guard errorOf (sets (setDoc [s03, rset "lead" "u0164.s02" [reading "a" .null]]) [g1]) == "ScopeReadings: u0164.s02"
-- a carve-out written on u0165.s03 itself: the governor's own unit, though the frame covers it
#guard errorOf (sets (setDoc [s03]) [g1, ⟨"gX", "u0165.s03", carveT, .list "u0164.s02", seven⟩]) == "ScopeReadings: u0165.s03"
-- a fault every choice has is named with no choice: a frame recording six of the seven units (F-mm)
#guard errorOf (sets (setDoc [s03]) [{g1 with units := seven.take 6}]) == "ManifestMismatch: scope.governors.g1.units"
#guard errorOf (sets (hcDoc parts [("reading_sets", .arr #[s03])]) [g1]) == "ScopeReadings: u0165.s03"
-- F-rs itself is unchanged: `govern` refuses the set it governs per choice
#guard errorOf (gov (setDoc [s03]) [g1]) == "ScopeReadings: u0165.s03"

-- SR-dep: another unit's rule depends on the choice. r9 on u0166.s01 takes precedence over the rules named hc-2 and
-- hc-cyberweapons on its predicate; the narrow reading has another predicate, so r9's `over` differs: refused
def r9 : Json := j "{\"norm\": {\"name\": \"r9\", \"predicate\": \"cyberweapon_creation_permitted\", \"sign\": true, \"guard\": [\"top\"], \"unless\": [], \"over\": []}}"
def gPr : Governor := ⟨"gPr", "u0166.s01", .precedes, .rules ["hc-2", "hc-cyberweapons"], ["u0165.s02", "u0165.s03"]⟩
def depParts : List (String × Json) :=
  ((without "u0165.s03" parts).filter (·.1 != "u0165.s02")) ++
    [("u0165.s02", part "hc-2" "cyberweapon_creation_permitted" "a2"), ("u0166.s01", r9)]
#guard errorOf (sets (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
    (cyberPart "other_permitted" guardNarrow)] depParts) [g1, gPr]) ==
  "ScopeReadings: u0166.s01: differs between choices u0165.s03 scope-u0165-s03@1:wide and u0165.s03 scope-u0165-s03@1:narrow"
-- with one predicate in both readings, r9's `over` is the same under both choices: admitted
#guard (sets (setDoc [s03] depParts) [g1, gPr]).toOption.map (fun o => contentOf o "u0166.s01" |>.compress) ==
  some "{\"norm\":{\"guard\":[\"top\"],\"name\":\"r9\",\"over\":[\"hc-2\",\"hc-cyberweapons\"],\"predicate\":\"cyberweapon_creation_permitted\",\"sign\":true,\"unless\":[]}}"

-- SR-lim: a decoder limit met under one choice is passed on unchanged: UNKNOWN, not a refusal of that choice. The
-- narrow reading's guard is 63 levels deep (it decodes, so its name is found); `gN`'s narrowing makes the composed
-- guard 64 deep, which the graph step's decoding of the composed rule meets
def notN : Nat → Json | 0 => j "[\"top\"]" | n + 1 => .arr #[.str "not", notN n]
#guard errorOf (sets (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
    (cyberPart "cyberweapon_creation_permitted" (notN 63))] depParts) [g1, gN, gPr] hcNames) ==
  "ResourceLimit: formula depth exceeds 64"
#guard errorOf (sets (setDoc [s03set (cyberPart "cyberweapon_creation_permitted" guardWide)
    (cyberPart "cyberweapon_creation_permitted" (notN 62))] depParts) [g1, gN, gPr] hcNames) == "ok"

-- sc-5rb, both sides of 11.1's clauses that sc-5r's review (F2) found without a fixture: one entry (two versions of
-- the set are refused), at least one reading (none is refused, never `ResourceLimit`; one is governed), and neither a
-- frontier nor a fixed reach
#guard errorOf (sets (setDoc [s03, s03.setObjVal! "version" (2 : Nat)]) [g1]) == "ScopeReadings: u0165.s03"
#guard errorOf (sets (setDoc [rset "scope-u0165-s03" "u0165.s03" []]) [g1]) == "ScopeReadings: u0165.s03"
#guard readingContents (sets (setDoc [rset "scope-u0165-s03" "u0165.s03"
  [reading "wide" (cyberPart "cyberweapon_creation_permitted" guardWide)]]) [g1]) "u0165.s03" == some [wideNorm]
#guard !layoutReach .frontier && !layoutReach (.fixed ["u0165.s03"]) && layoutReach (.list "u0164.s02") &&
  layoutReach (.rules ["hc-2"])
-- a choice names each set by its id and its version (`pickOf`): another version of the same id is another set
#guard pickOf [("scope-u0165-s03", 2, 1), ("scope-u0165-s03", 1, 0)] s03 == some 0 &&
  pickOf [("scope-u0165-s03", 2, 1)] s03 == none

-- sc-5rb (R16's mutants): two governed sets under the frame, each reading composed as its unit would be, the
-- units in order, and a choice named by both sets
def a5 : Json := part "hc-5" "restricted_act_permitted" "a5"
def s05set (b : Json := part "hc-5" "restricted_act_permitted" "a6") : Json :=
  rset "scope-u0165-s05" "u0165.s05" [reading "a" a5, reading "b" b]
def twoSets : List (String × Json) := without "u0165.s05" (without "u0165.s03" parts)
def asWritten (u : String) (c : Json) : Option String := contentStr (gov (hcDoc ((without u parts) ++ [(u, c)])) [g1]) u
#guard readingContents (sets (setDoc [s03, s05set] twoSets) [g1]) "u0165.s05" ==
    (do pure [← asWritten "u0165.s05" a5, ← asWritten "u0165.s05" (part "hc-5" "restricted_act_permitted" "a6")]) &&
  asWritten "u0165.s05" a5 != asWritten "u0165.s05" (part "hc-5" "restricted_act_permitted" "a6") &&
  readingContents (sets (setDoc [s03, s05set] twoSets) [g1]) "u0165.s03" == some [wideNorm, narrowNorm] &&
  (sets (setDoc [s03, s05set] twoSets) [g1]).toOption.map unitIds == some (unitIds (setDoc [s03, s05set] twoSets)) &&
  ["u0165.s03", "u0165.s05"].all (contentStr (sets (setDoc [s03, s05set] twoSets) [g1]) · == some "null")
#guard errorOf (sets (setDoc [s03, s05set (cyberPart "restricted_act_permitted" (j "[\"unary\", \"a5\", [\"var\", 1]]")
    [("sign", .bool false)])] twoSets) [g1]) ==
  "ScopeChoice: u0165.s03 scope-u0165-s03@1:wide, u0165.s05 scope-u0165-s05@1:b: ScopeConflict: u0165.s05: sign"
-- a set on the lead-in listed before the governed one: still refused under every choice
#guard errorOf (sets (setDoc [rset "lead" "u0164.s02" [reading "a" .null], s03]) [g1]) == "ScopeReadings: u0164.s02"
-- a governor that covers no governed unit, listed first, governs nothing; one on u0165.s03 itself, listed first,
-- still refuses
#guard errorOf (sets (setDoc [s03]) [gR, g1]) == "ok"
#guard errorOf (sets (setDoc [s03]) [⟨"gX", "u0165.s03", carveT, .list "u0164.s02", seven⟩, g1]) == "ScopeReadings: u0165.s03"
-- SR-dep's dependent rule on the document's first unit and on its last: still compared
def depAt (u : String) : List (String × Json) := (depParts.filter (·.1 != "u0166.s01")) ++ [(u, r9)]
#guard [("u0164.s01"), ("u0173.s01")].all fun u => errorOf (sets (setDoc [s03set (cyberPart "cyberweapon_creation_permitted"
    guardWide) (cyberPart "other_permitted" guardNarrow)] (depAt u)) [g1, {gPr with unit := u}]) ==
  s!"ScopeReadings: {u}: differs between choices u0165.s03 scope-u0165-s03@1:wide and u0165.s03 scope-u0165-s03@1:narrow"
-- 65 joint choices (5 by 13): over the limit; a set with no version is version 0
#guard errorOf (sets (setDoc [wideSet "s3" "u0165.s03" 5, wideSet "s5" "u0165.s05" 13] twoSets) [g1]) ==
  "ResourceLimit: scope choices"
#guard errorOf (sets (setDoc [Json.mkObj [("id", "scope-u0165-s03"), ("unit", "u0165.s03"), ("status", "open"),
    ("readings", .arr #[reading "wide" (cyberPart "cyberweapon_creation_permitted" guardWide), reading "narrow"
      (cyberPart "cyberweapon_creation_permitted" guardNarrow [("sign", .bool false)])])]]) [g1]) ==
  "ScopeChoice: u0165.s03 scope-u0165-s03@0:narrow: ScopeConflict: u0165.s03: sign"

/-! sc-5rd: the proved statements (`ReadingsTheorems.lean`) on spec 11.6's instances. -/

def optEq : Option Json → Option Json → Bool
  | some a, some b => VE.Readings.Wire.jeq a b
  | none, none => true
  | _, _ => false
/-- `x` and `y` agree on every member outside `ks` (the members `getObjVal?` finds). -/
def sameBut (ks : List String) (x y : Json) : Bool :=
  (keysOf x ++ keysOf y).all fun k => ks.contains k || optEq (x.getObjVal? k).toOption (y.getObjVal? k).toOption
/-- `governSets_preserves`' conclusion, computed for an answer `out` of the document `doc` with governed units `su`. -/
def preserved (su : List String) (out doc : Json) : Bool :=
  sameBut ["units", "reading_sets"] out doc && (unitsOf out).map idOf == (unitsOf doc).map idOf &&
  ((unitsOf out).zip (unitsOf doc)).all (fun (x, y) => sameBut ["content"] x y && (!su.contains (idOf y) ||
    VE.Readings.Wire.jeq x y)) && (setsJson out).length == (setsJson doc).length &&
  ((setsJson out).zip (setsJson doc)).all fun (x, y) => (su.contains (setUnit y) || VE.Readings.Wire.jeq x y) &&
    sameBut ["readings"] x y && (readingsJson x).length == (readingsJson y).length &&
    ((readingsJson x).zip (readingsJson y)).all fun (r, r') => sameBut ["content"] r r'
/-- `preserved` on `governSets`' answer, and on the document with one member it must keep changed (`bad`). -/
def preservesOn (doc : Json) (gs : List Governor) (bad : Json → Json) : Except String (Bool × Bool) := do
  let D := sdoc doc gs [] (← VE.Readings.Wire.decodeEnvironment envJ)
  let out ← governSets D
  pure (preserved (governedSetUnits D) out D.doc, preserved (governedSetUnits D) out (bad D.doc))
-- SR-1 and SR-u: kept, and the check fails once a member outside `units` and `reading_sets`, a governed set unit,
-- a set's `id` or a reading's `id` differs
def setAt (k : String) (f : Json → Json) (doc : Json) : Json := match doc.getObjValD k with
  | .arr xs => doc.setObjVal! k (.arr (xs.modify 0 f))
  | _ => doc
#guard (preservesOn (setDoc [s03]) [g1] (·.setObjVal! "title" "x")).toOption == some (true, false)
#guard (preservesOn (setDoc [s03, u0166set]) [g1] (·.setObjVal! "title" "x")).toOption == some (true, false)
#guard (preservesOn (setDoc [s03]) [g1] (setAt "units" (·.setObjVal! "kind" "x"))).toOption == some (true, false)
#guard (preservesOn (setDoc [s03]) [g1] (setAt "reading_sets" (·.setObjVal! "id" "x"))).toOption == some (true, false)
#guard (preservesOn (setDoc [s03]) [g1] (setAt "reading_sets" (setAt "readings" (·.setObjVal! "id" "x")))).toOption ==
  some (true, false)
-- `governSets_readings_refused` (SR-g's case): u0165.s03's part is written, so its set, which g1 reaches, is not
-- governed per choice and the document is refused; with the unit unwritten (SR-1) the set is governed and admitted
def refusedOn (doc : Json) (g : Governor) (u : String) : Except String (Bool × Bool × Bool × Bool) := do
  let D := sdoc doc [g] [] (← VE.Readings.Wire.decodeEnvironment envJ)
  let us ← covered D g.reach
  pure (us.contains u, (setUnits D.doc).contains u, (governedSetUnits D).contains u, (governSets D).isOk)
#guard (refusedOn (hcDoc parts [("reading_sets", .arr #[s03])]) g1 "u0165.s03").toOption == some (true, true, false, false)
#guard (refusedOn (setDoc [s03]) g1 "u0165.s03").toOption == some (true, true, true, true)
-- on the governor's own unit (`u = g.unit`): refused, though the set holds a reading
#guard (refusedOn (setDoc [s03, rset "lead" "u0164.s02" [reading "a" .null]]) g1 "u0164.s02").toOption ==
  some (false, true, false, false)

end VE.Scope.Examples
