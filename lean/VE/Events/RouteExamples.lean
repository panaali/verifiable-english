import VE.NormDefaults.Run
import VE.Defaults.Examples

/-! et-4b's route fixtures (docs/spec/events-time-causation.md 3, 4; plan ET-4): the hook through the layered decoders
and the service, the identities, the date constants in the vocabulary limit and the kinds a list with `events@0` is
answered on, each on both sides of its boundary. The hook's own checks are `WireExamples.lean`'s; certificates are
`tests/test_events_route.py`'s, with the untrusted prover. -/
namespace VE.Events.RouteExamples
open Lean
open VE.Events
open VE.Defaults.Fixtures (xReq xPerm envJ strictSoft ruleJ dfltJ)
open VE.NormDefaults.Wire (LayeredU decodeLayered)

def parse (s : String) : Json := (Json.parse s).toOption.getD .null

def rolePred (name args wording : String) : String :=
  "\"" ++ name ++ "\":{\"arguments\":" ++ args ++ ",\"description\":\"" ++ name ++ "\",\"verbalisation\":\"" ++ wording ++ "\"}"

def eventPreds : List String :=
  [rolePred "before" "[\"day\",\"day\"]" "{0} is before {1}", rolePred "committed_on" "[\"act\",\"day\"]" "{0} happens on {1}",
   rolePred "led_to" "[\"act\",\"act\"]" "{0} contributed to {1}", rolePred "needed" "[\"act\",\"act\"]" "{0} was necessary for {1}"]

def linkJ (p : String) (form : String := "contributed") (by_ : String := "the drafters") : String :=
  "{\"predicate\":\"" ++ p ++ "\",\"form\":\"" ++ form ++ "\",\"decided_by\":\"" ++ by_ ++ "\"}"

def blockJ (dates : String := "[\"2026-10-14\",\"2026-10-12\"]") (links : List String := [linkJ "led_to"]) : Json :=
  parse ("{\"day\":\"day\",\"before\":\"before\",\"events\":[{\"sort\":\"act\",\"on\":\"committed_on\"}],\"states\":[]," ++
    "\"dates\":" ++ dates ++ ",\"anchor\":\"2026-10-13\",\"links\":[" ++ ",".intercalate links ++ "]}")

def withSorts (e : Json) : Json :=
  let v := e.getObjValD "vocabulary"
  let day := parse "{\"description\":\"d\"}"
  e.setObjVal! "vocabulary" (v.setObjVal! "sorts" (((v.getObjValD "sorts").setObjVal! "day" day).setObjVal! "act" day))

def listed : List String := ["events@0", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]

def envOf (b : Option Json := some (blockJ)) (ps : List String := listed) (extra : List String := []) : Json :=
  let e := (withSorts (envJ ([xReq, xPerm] ++ eventPreds ++ extra) strictSoft)).setObjVal! "profiles" (toJson ps)
  match b with
  | some b => e.setObjVal! "events" b
  | none => e

def norms : Json := parse ("[" ++ ruleJ "r" "x_required" true (dfltJ []) ++ "]")
def terms : Json := parse "[{\"name\":\"led_to\",\"decided_by\":\"the drafters\"}]"

def caseOf (kind : String) (e : Json) (t : Json := terms) (more : List (String × Json) := []) : Json :=
  Json.mkObj ([("id", .str "a"), ("kind", .str kind), ("environment", e), ("norms", norms), ("open_terms", t)] ++ more)

def answer (j : Json) : Json := VE.NormDefaults.Run.runCaseReported j
def status (j : Json) : String := if (answer j).getObjValD "status" == .str "ok" then "ok" else
  ((answer j).getObjValD "error").getStr?.toOption.getD "?"
def elaborated (e : Json) (t : Json := terms) : String := status (caseOf "norm-defaults-elaborate" e t)

/-- The labels of a block's pack on the route's hook. -/
def hook (e : Json) (t : Json := terms) : Except String (List String) := do
  match ← eventsHook e t with
  | some ⟨_, some d⟩ => pure (d.labelled.map (·.1))
  | _ => pure []

-- The accepting fixture: the profile, the block and the open term on a soft document.
#guard elaborated envOf == "ok"

/-! ## Item 1 through the service, and a block without the profile -/

def bad : Json := blockJ "[\"nonsense\"]"

#guard elaborated (envOf bad ["events@0", "norms@0", "relational-fol@0"]) == "UnsupportedProfile: events@0 requires norm-defaults@0"
#guard elaborated (envOf bad) == "InvalidDate(nonsense)"
#guard elaborated (envOf (some blockJ) ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]) ==
  "InvalidInput: invalid environment envelope"

/-! ## The view a layered decoder reads, and the identities it does not -/

def decoded (e : Json) (t : Json := terms) : Except String LayeredU := decodeLayered (caseOf "k" e t)
-- The pack is last, the date constants reach the regenerated environment, and identity reads the bytes as written.
#guard ((decoded envOf).toOption.map fun L => L.packs.map (·.id)) == some ["soft", "events"]
#guard ((decoded (envOf none)).toOption.map fun L => L.packs.map (·.id)) == some ["soft"]
#guard ((decoded envOf).toOption.map fun L =>
  ((L.baseEnv.getObjValD "vocabulary").getObjValD "constants").getObjValD "date__2026_10_13" != .null &&
    !(L.baseEnv.getObjVal? "events").toBool) == some true
#guard ((decoded envOf).toOption.map fun L => some L.envId ==
  (VE.Route.Wire.environmentId listed envOf).toOption) == some true
#guard ((decoded envOf).toOption.map (·.envId)) != ((decoded (envOf (blockJ "[\"2026-10-15\"]"))).toOption.map (·.envId))
#guard ((decoded envOf).toOption.map (·.docHash)) != ((decoded (envOf (blockJ "[\"2026-10-15\"]"))).toOption.map (·.docHash))
-- The date constants are charged to the vocabulary: the same document fits with one date and not with three.
def filled (k : Nat) (b : Option Json) : String := match decoded (envOf b listed
    ((List.range k).map fun i => rolePred s!"f{i}" "[\"act\",\"day\"]" "d")) with
  | .ok _ => "ok"
  | .error e => e
#guard filled 245 blockJ == "ok"
#guard filled 246 blockJ == "ResourceLimit: vocabulary size"
#guard filled 247 (blockJ "[]") == "ok"
#guard filled 248 (blockJ "[]") == "ResourceLimit: vocabulary size"

/-! ## The kinds: what reads no situation is answered, the rest refused by name -/

def refusedKind (k : String) : String := s!"CheckerUnavailable: events@0 with {k} needs its composed Lean route"

#guard ["norm-defaults-status", "norm-defaults-report", "norm-defaults-gaps", "admission", "defaults-conflict"].all
  fun k => status (caseOf k envOf) == refusedKind k
#guard status (caseOf "norm-defaults-conflict" envOf terms [("witness", parse "{}")]) == refusedKind "norm-defaults-conflict"
#guard status (caseOf "norm-defaults-conflict" envOf) == "ok"
#guard status (caseOf "norm-defaults-elaborate" envOf) == "ok"
-- The row comes before the kind, and a list without the profile never meets this gate.
#guard status (caseOf "norm-defaults-status" (envOf bad ["events@0", "norm-defaults@0", "norms@0"])) ==
  "UnsupportedProfile: events@0 requires relational-fol@0"
#guard VE.NormDefaults.Run.pendingEvents (caseOf "norm-defaults-status" (envOf none (listed.filter (· != "events@0")))) == none
-- The plain norm-defaults route has no hook yet, and a rights source no certificate kind.
#guard status (caseOf "norm-defaults-elaborate" (envOf none ["events@0", "norm-defaults@0", "norms@0", "relational-fol@0"])) ==
  refusedKind "norm-defaults-elaborate"
#guard status (caseOf "norm-defaults-certificate" (envOf none (listed ++ ["rights@0"] |>.toArray.qsort (· < ·) |>.toList))) ==
  refusedKind "norm-defaults-certificate"

-- `events_premises`: the pack's rows in `eventsLabelled`'s order, only on a document with the block.
def premiseLabels (e : Json) : List String :=
  match (answer (caseOf "norm-defaults-elaborate" e)).getObjValD "events_premises" with
  | .arr rs => rs.toList.map fun r => (r.getObjValD "label").getStr?.toOption.getD "?"
  | _ => []
#guard premiseLabels envOf == (hook envOf).toOption.getD []
#guard (premiseLabels envOf).take 3 == ["events:irreflexive", "events:transitive", "events:linear"]
#guard premiseLabels envOf != [] && premiseLabels (envOf none) == []
#guard !((answer (caseOf "norm-defaults-elaborate" (envOf none))).getObjVal? "events_premises").toBool

-- The open terms are the case's, or its document's on the route that reads a document; the case's come first.
#guard VE.NormDefaults.Wire.caseOpenTerms (Json.mkObj [("open_terms", terms), ("document", parse "{\"open_terms\":[]}")]) == terms
#guard VE.NormDefaults.Wire.caseOpenTerms (Json.mkObj [("document", Json.mkObj [("open_terms", terms)])]) == terms
#guard VE.NormDefaults.Wire.caseOpenTerms (Json.mkObj []) == .null

-- Each way onto the route: the profile, an `unspecified` default, a route kind, `events@0` alone; and none of them.
def pathOf (kind : String) (e : Json) : Bool := VE.NormDefaults.Run.usesNormDefaultsPath (caseOf kind e)
def plainEnv (ps : List String) : Json := (envJ [xPerm] strictSoft).setObjVal! "profiles" (toJson ps)
#guard pathOf "x" (plainEnv ["norm-defaults@0", "norms@0", "relational-fol@0"])
#guard pathOf "x" (envOf none ["norms@0", "relational-fol@0"])
#guard pathOf "norm-defaults-x" (plainEnv ["norms@0", "relational-fol@0"])
#guard pathOf "x" (plainEnv ["events@0", "norms@0", "relational-fol@0"])
#guard !pathOf "x" (plainEnv ["norms@0", "relational-fol@0"])

-- The answer is the block-less answer's, field by field, with the pack's rows beside it.
def fieldsOf (e : Json) : List String := ((VE.Bridge.fields (answer (caseOf "norm-defaults-elaborate" e))).toOption.getD []).map (·.1)
def fieldOf (e : Json) (k : String) : Json := (answer (caseOf "norm-defaults-elaborate" e)).getObjValD k
#guard (fieldsOf envOf).filter (· != "events_premises") == fieldsOf (envOf none) && (fieldsOf envOf).length > 8
#guard ["soft", "rights", "premises", "fill", "background"].all fun k => fieldOf envOf k == fieldOf (envOf none) k

-- Every decision predicate is charged with the dates: two default rules move the boundary by one more.
def twoRules : Json := parse ("[" ++ ruleJ "r" "x_required" true (dfltJ []) ++ "," ++ ruleJ "s" "x_permitted" true (dfltJ []) ++ "]")
def filled2 (k : Nat) : String := match decodeLayered ((caseOf "k" (envOf (some blockJ) listed
    ((List.range k).map fun i => rolePred s!"f{i}" "[\"act\",\"day\"]" "d"))).setObjVal! "norms" twoRules) with
  | .ok _ => "ok"
  | .error e => e
#guard filled2 244 == "ok" && filled2 245 == "ResourceLimit: vocabulary size" && filled 245 blockJ == "ok"
-- A block-less document with the profile has no date to charge.
#guard filled 248 none == "ok"
#guard filled 249 none == "ResourceLimit: vocabulary size"

/-! ## The rights branch: the pack after soft's and rights' -/

def rightsEnv (b : Option Json) (ps : List String) (extra : List String := []) : Json :=
  let e := parse ("{\"language\":\"ve.core@0.2\",\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{" ++
    "\"state\":{\"description\":\"state\"},\"person\":{\"description\":\"person\"},\"day\":{\"description\":\"day\"}}," ++
    "\"predicates\":{" ++ ",".intercalate ([rolePred "before" "[\"day\",\"day\"]" "{0} is before {1}",
      "\"arrest_permitted\":{\"arguments\":[\"state\",\"person\"],\"description\":\"permission\",\"regulated\":{\"role\":" ++
      "\"permission\",\"default\":\"unspecified\",\"act\":\"{0} arrest {1}\"}}",
      "\"arbitrary\":{\"arguments\":[\"state\",\"person\"],\"description\":\"arbitrary\",\"verbalisation\":\"{0} arrests {1} arbitrarily\"}"] ++
      extra) ++ "},\"constants\":{},\"rights\":{\"holders\":[\"person\"],\"bearers\":[\"state\"],\"protected\":[],\"alters\":{}}}}")
  let e := e.setObjVal! "profiles" (toJson ps)
  match b with
  | some b => e.setObjVal! "events" b
  | none => e

def rightsDoc : Json := parse ("[{\"right\":{\"name\":\"liberty\",\"holder\":\"person\",\"guard\":[\"top\"],\"lines\":[{\"kind\":" ++
  "\"claim\",\"cites\":{},\"norm\":{\"name\":\"art9\",\"predicate\":\"arrest_permitted\",\"sign\":false,\"guard\":[\"binary\"," ++
  "\"arbitrary\",[\"var\",1],[\"var\",0]],\"unless\":[],\"over\":[]}}]}},{\"limitation\":{\"name\":\"l29\",\"scope\":[\"liberty\"]," ++
  "\"kinds\":[\"claim\"],\"decided_by\":\"unstated\",\"conditions\":[{\"name\":\"law\",\"role\":\"necessary\",\"verbalisation\":" ++
  "\"determined by law\"}],\"factors\":[]}}]")

def rightsListed : List String := ["events@0", "norm-defaults@0", "norms@0", "relational-fol@0", "rights@0", "soft-norms@0"]
def dayBlock (dates : String := "[\"2026-10-12\"]") : Json :=
  parse ("{\"day\":\"day\",\"before\":\"before\",\"events\":[],\"states\":[],\"dates\":" ++ dates ++ ",\"links\":[]}")
def rightsCase (e : Json) : Json :=
  Json.mkObj [("id", .str "a"), ("kind", .str "norm-defaults-elaborate"), ("environment", e), ("document", rightsDoc)]
def rightsPacks (e : Json) : Option (List String) := (decodeLayered (rightsCase e)).toOption.map (·.packs.map (·.id))

#guard rightsPacks (rightsEnv (some dayBlock) rightsListed) == some ["soft", "rights", "events"]
#guard rightsPacks (rightsEnv none rightsListed) == some ["soft", "rights"]
#guard (((answer (rightsCase (rightsEnv (some dayBlock) rightsListed))).getObjValD "events_premises").getArr?.toOption.map (·.size)) ==
  some 3
#guard (answer (rightsCase (rightsEnv (some dayBlock) rightsListed))).getObjValD "rights" ==
  (answer (rightsCase (rightsEnv none rightsListed))).getObjValD "rights"
-- The date constants are charged on this branch too.
def rightsFilled (k : Nat) (dates : String) : String :=
  match decodeLayered (rightsCase (rightsEnv (some (dayBlock dates)) rightsListed
      ((List.range k).map fun i => rolePred s!"f{i}" "[\"state\",\"day\"]" "d"))) with
  | .ok _ => "ok"
  | .error e => e
def threeDates : String := "[\"2026-10-12\",\"2026-10-13\",\"2026-10-14\"]"
#guard rightsFilled 247 threeDates == "ok" && rightsFilled 248 threeDates == "ResourceLimit: vocabulary size"
#guard rightsFilled 250 "[]" == "ok" && rightsFilled 251 "[]" == "ResourceLimit: vocabulary size"

/-! ## The replay: a one-node proof of a pack premise, bound by Lean's own identities -/

def before (a b : String) : VE.Formula := .binary "before" (.const a) (.const b)
def inPack : VE.Formula := before "date__2026_10_12" "date__2026_10_13"
def notInPack : VE.Formula := before "date__2026_10_13" "date__2026_10_12"

/-- A certificate as `bindCertX` binds it to `e`: its ids from Lean's own functions, its trace one `close`. -/
def boundProof (e : Json) (c : VE.Formula) : Json := Id.run do
  let .ok L := decoded e | return .null
  let .ok canonical := VE.NormDefaults.Wire.canonicalEnvironmentJsonU e | return .null
  let .ok id := VE.Route.Wire.environmentId listed canonical | return .null
  let meaning := fun (a : VE.Formula) => (VE.Route.Wire.meaningId listed id (VE.NormDefaults.Wire.enc a)).toOption.getD ""
  Json.mkObj [("checker_version", .str "ve-tableau-checker@2"), ("environment_id", .str id),
    ("premise_meaning_ids", toJson ((VE.NormDefaults.Wire.premisesX L.U L.X []).map meaning)),
    ("conclusion_meaning_id", .str (meaning c)), ("trace", parse "{\"rule\":\"close\"}")]

def replayCase (e bound : Json) (c : VE.Formula) : Json :=
  caseOf "norm-defaults-certificate" e terms
    [("premises", parse "[]"), ("conclusion", VE.NormDefaults.Wire.enc c), ("certificate", bound)]
def premiseCount : Nat := ((decoded envOf).toOption.map fun L => (VE.NormDefaults.Wire.premisesX L.U L.X []).length).getD 0

#guard (answer (replayCase envOf (boundProof envOf inPack) inPack)).getObjValD "valid" == .bool true
#guard (answer (replayCase envOf (boundProof envOf inPack) inPack)).getObjValD "premises" == toJson premiseCount
#guard premiseCount > (hook envOf |>.toOption.map (·.length) |>.getD 0)
-- The refusing sides: a proof that does not close, and a certificate of another block.
#guard (answer (replayCase envOf (boundProof envOf notInPack) notInPack)).getObjValD "valid" == .bool false
#guard status (replayCase envOf (boundProof envOf inPack) notInPack) == "certificate is stale or bound to different inputs"
#guard status (replayCase (envOf (blockJ "[\"2026-10-14\",\"2026-10-12\",\"2026-10-15\"]")) (boundProof envOf inPack) inPack) ==
  "certificate is stale or bound to different inputs"
-- What the theorem reads: this block, the other packs' `X` without the pack, this case's formulas.
#guard (match VE.Events.replayEventsEntailment (replayCase envOf (boundProof envOf inPack) inPack) with
  | .ok r => r.V.dates.length == 3 && r.valid && r.premises.isEmpty && r.conclusion == inPack &&
      r.X == ((decoded envOf).toOption.map fun L => (VE.NormDefaults.Wire.softLabelledU L.U L.D).map (·.2)).getD [.top]
  | .error _ => false)

-- With another pack's premise in `X`: the count is the whole of `premisesX`, the soft premise among it.
def excEnv : Json := envOf (some blockJ) listed [VE.Defaults.Fixtures.baseJ "s"]
def excNorms : Json := parse ("[" ++ ruleJ "r" "x_required" true (dfltJ [VE.Defaults.Fixtures.un "s"]) ++ "]")
def excElaborated : Json := answer ((caseOf "norm-defaults-elaborate" excEnv).setObjVal! "norms" excNorms)
-- The other packs' arrays stay in the answer, with their rows: soft's one exception premise, rights' limitation.
#guard ((excElaborated.getObjValD "soft").getArr?.toOption.map (·.size)) == some 1
#guard ((excElaborated.getObjValD "rights").getArr?.toOption.map (·.size)) == some 0
#guard ((((answer (rightsCase (rightsEnv (some dayBlock) rightsListed))).getObjValD "rights").getArr?).toOption.map (·.size)) ==
  ((((answer (rightsCase (rightsEnv none rightsListed))).getObjValD "rights").getArr?).toOption.map (·.size)) &&
  ((((answer (rightsCase (rightsEnv (some dayBlock) rightsListed))).getObjValD "rights").getArr?).toOption.map (·.size) |>.getD 0) > 0
def excCase (c : VE.Formula) : Json :=
  let e := excEnv
  let n := excNorms
  let bound : Json := Id.run do
    let .ok L := decodeLayered ((caseOf "k" e).setObjVal! "norms" n) | return .null
    let .ok canonical := VE.NormDefaults.Wire.canonicalEnvironmentJsonU e | return .null
    let .ok id := VE.Route.Wire.environmentId listed canonical | return .null
    let meaning := fun (a : VE.Formula) => (VE.Route.Wire.meaningId listed id (VE.NormDefaults.Wire.enc a)).toOption.getD ""
    Json.mkObj [("checker_version", .str "ve-tableau-checker@2"), ("environment_id", .str id),
      ("premise_meaning_ids", toJson ((VE.NormDefaults.Wire.premisesX L.U L.X []).map meaning)),
      ("conclusion_meaning_id", .str (meaning c)), ("trace", parse "{\"rule\":\"close\"}")]
  (replayCase e bound c).setObjVal! "norms" n
def excCount : Nat :=
  ((decodeLayered ((caseOf "k" excEnv).setObjVal! "norms" excNorms)).toOption.map fun L =>
    (VE.NormDefaults.Wire.premisesX L.U L.X []).length).getD 0
#guard (answer (excCase inPack)).getObjValD "valid" == .bool true
#guard (answer (excCase inPack)).getObjValD "premises" == toJson excCount && excCount == premiseCount + 1
#guard (match VE.Events.replayEventsEntailment (excCase inPack) with
  | .ok r => r.X.length == 1 | .error _ => false)

-- A replay needs the block: with the profile alone there is no pack to replay against.
#guard status (caseOf "norm-defaults-certificate" (envOf none)) == "InvalidInput: events"
#guard status (caseOf "norm-defaults-certificate" envOf) == "property not found: premises"

end VE.Events.RouteExamples
