import VE.NormDefaults.Run
import VE.Defaults.Examples
import VE.Service.DocumentChain

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

-- The charge counts every event, both roles of every state and every link: two of each at the boundary.
def counted (links : Nat) : String :=
  let rows := fun (n : Nat) (f : Nat → String) => ",".intercalate ((List.range n).map f)
  let b := parse ("{\"day\":\"day\",\"before\":\"before\",\"events\":[" ++
    rows 2 (fun i => "{\"sort\":\"e" ++ toString i ++ "\",\"on\":\"on" ++ toString i ++ "\"}") ++ "],\"states\":[" ++
    rows 2 (fun i => "{\"sort\":\"s" ++ toString i ++ "\",\"begins\":\"b" ++ toString i ++ "\",\"ends\":\"x" ++ toString i ++ "\"}") ++
    "],\"dates\":[],\"links\":[" ++ rows links (fun i => linkJ s!"l{i}") ++ "]}")
  match eventsHook (envOf b) terms with
  | .ok _ => "ok"
  | .error e => e
#guard counted 250 == "EventsSort: e0" && counted 251 == "ResourceLimit: events premises"

/-! ## The view a layered decoder reads, and the identities it does not -/

-- The author's constants stay beside the dates, every one of them.
def twoConstants : Json :=
  let e := envOf
  let v := e.getObjValD "vocabulary"
  e.setObjVal! "vocabulary" (v.setObjVal! "constants" (parse "{\"a1\":{\"sort\":\"act\",\"description\":\"a1\"},\"a2\":{\"sort\":\"act\",\"description\":\"a2\"}}"))
#guard (match eventsHook twoConstants terms with
  | .ok (some h) => ((VE.Bridge.fields ((h.view.getObjValD "vocabulary").getObjValD "constants")).toOption.map (·.map (·.1))) ==
      some ["a1", "a2", "date__2026_10_12", "date__2026_10_13", "date__2026_10_14"]
  | _ => false)

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
-- The profile read anywhere in the list, not first: `documents@1` sorts before it.
#guard pathOf "x" (plainEnv ["documents@1", "events@0", "norms@0", "relational-fol@0"])
#guard pathOf "x" (plainEnv ["data@0", "events@0"])

-- The answer is the block-less answer's, field by field, with the pack's rows beside it.
def fieldsOf (e : Json) : List String := ((VE.Bridge.fields (answer (caseOf "norm-defaults-elaborate" e))).toOption.getD []).map (·.1)
def fieldOf (e : Json) (k : String) : Json := (answer (caseOf "norm-defaults-elaborate" e)).getObjValD k
#guard (fieldsOf envOf).filter (· != "events_premises") == fieldsOf (envOf none) && (fieldsOf envOf).length > 8
#guard ["soft", "rights", "premises", "fill", "background"].all fun k => fieldOf envOf k == fieldOf (envOf none) k
-- The base environment, with the dates; the identity is the bytes as written.
#guard (((fieldOf envOf "base_environment").getObjValD "vocabulary").getObjValD "constants").getObjValD "date__2026_10_13" ==
  parse "{\"sort\":\"day\",\"description\":\"the date of this document\"}"
#guard fieldOf envOf "environment_id" == toJson ((VE.Route.Wire.environmentId listed envOf).toOption.getD "")

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
-- Every decision predicate of the rights document is charged too: two default norms, one more than one norm.
def dflt : String := ",\"mode\":\"default\",\"exception\":{\"decided_by\":\"the court\",\"sufficient\":[],\"necessary\":[],\"factors\":[]}"
def defaultDoc (two : Bool) : Json := parse ("[{\"right\":{\"name\":\"liberty\",\"holder\":\"person\",\"guard\":[\"top\"],\"lines\":[" ++
  ",".intercalate ((if two then ["art9", "art9b"] else ["art9"]).map fun n => "{\"kind\":\"claim\",\"cites\":{},\"norm\":{\"name\":\"" ++
    n ++ "\",\"predicate\":\"arrest_permitted\",\"sign\":false,\"guard\":[\"top\"],\"unless\":[],\"over\":[]" ++ dflt ++ "}}") ++ "]}}]")
def defaultFilled (k : Nat) (two : Bool) : String :=
  match decodeLayered ((rightsCase (rightsEnv (some (dayBlock threeDates)) rightsListed
      ((List.range k).map fun i => rolePred s!"f{i}" "[\"state\",\"day\"]" "d"))).setObjVal! "document" (defaultDoc two)) with
  | .ok _ => "ok"
  | .error e => e
#guard defaultFilled 248 false == "ok" && defaultFilled 249 false == "ResourceLimit: vocabulary size"
#guard defaultFilled 247 true == "ok" && defaultFilled 248 true == "ResourceLimit: vocabulary size"
#guard rightsFilled 247 threeDates == "ok" && rightsFilled 248 threeDates == "ResourceLimit: vocabulary size"
#guard rightsFilled 250 "[]" == "ok" && rightsFilled 251 "[]" == "ResourceLimit: vocabulary size"

/-! ## The replay: a one-node proof of a pack premise, bound by Lean's own identities -/

def before (a b : String) : VE.Formula := .binary "before" (.const a) (.const b)
def inPack : VE.Formula := before "date__2026_10_12" "date__2026_10_13"
def notInPack : VE.Formula := before "date__2026_10_13" "date__2026_10_12"

/-- A certificate as `bindCertX` binds it to `e`: its ids from Lean's own functions, its trace one `close`. -/
def boundProof (e : Json) (c : VE.Formula) (ps : List String := listed) : Json := Id.run do
  let .ok L := decoded e | return .null
  let .ok canonical := VE.NormDefaults.Wire.canonicalEnvironmentJsonU e | return .null
  let .ok id := VE.Route.Wire.environmentId ps canonical | return .null
  let meaning := fun (a : VE.Formula) => (VE.Route.Wire.meaningId ps id (VE.NormDefaults.Wire.enc a)).toOption.getD ""
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
def excEnv : Json := envOf (some blockJ) listed [VE.Defaults.Fixtures.baseJ "s", VE.Defaults.Fixtures.baseJ "t"]
def excNorms : Json := parse ("[" ++ ruleJ "r" "x_required" true (dfltJ [VE.Defaults.Fixtures.un "s"]) ++ "," ++
  ruleJ "q" "x_permitted" true (dfltJ [VE.Defaults.Fixtures.un "t"]) ++ "]")
def excElaborated : Json := answer ((caseOf "norm-defaults-elaborate" excEnv).setObjVal! "norms" excNorms)
-- The other packs' arrays stay in the answer, with their rows: soft's two exception premises, rights' limitation.
#guard ((excElaborated.getObjValD "soft").getArr?.toOption.map (·.size)) == some 2
-- Every regenerated field of the route is in the answer.
#guard ((decodeLayered ((caseOf "k" excEnv).setObjVal! "norms" excNorms)).toOption.map fun L =>
  (VE.NormDefaults.Wire.regeneratedU L.U).all fun (k, _) => excElaborated.getObjValD k != .null) == some true
#guard ((excElaborated.getObjValD "rights").getArr?.toOption.map (·.size)) == some 0
#guard ((((answer (rightsCase (rightsEnv (some dayBlock) rightsListed))).getObjValD "rights").getArr?).toOption.map (·.size)) ==
  ((((answer (rightsCase (rightsEnv none rightsListed))).getObjValD "rights").getArr?).toOption.map (·.size)) &&
  ((((answer (rightsCase (rightsEnv (some dayBlock) rightsListed))).getObjValD "rights").getArr?).toOption.map (·.size) |>.getD 0) > 0
def excCase (c : VE.Formula) (e : Json := excEnv) : Json :=
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
#guard (answer (excCase inPack)).getObjValD "premises" == toJson excCount && excCount == premiseCount + 2
#guard (match VE.Events.replayEventsEntailment (excCase inPack) with
  | .ok r => r.X.length == 2 | .error _ => false)

-- The replay reads the profile anywhere in the list: with `documents@1` before it, the same proof replays.
def docListed : List String := ["documents@1", "events@0", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]
#guard (answer (replayCase (envOf (some blockJ) docListed) (boundProof (envOf (some blockJ) docListed) inPack docListed) inPack)).getObjValD
  "valid" == .bool true

-- The view keeps every other listed profile, the one before `events@0` too.
#guard (match eventsHook (envOf (some blockJ) docListed) terms with
  | .ok (some h) => VE.Compose.listedProfiles h.view == docListed.filter (· != "events@0")
  | _ => false)

-- Without a block the profile neither widens nor narrows the route (spec 1.1) and adds no pack (1.11): every kind
-- `eventsServed` answers is answered, on both branches, as on the list without `events@0`; every other is refused by name.
def unlisted (ps : List String) : List String := ps.filter (· != "events@0")
def onBranch (rights : Bool) (k : String) (ps : List String) : Json :=
  if rights then (rightsCase (rightsEnv none (if ps == listed then rightsListed else unlisted rightsListed))).setObjVal! "kind" (.str k)
  else caseOf k (envOf none ps)
def everyKind : List String :=
  VE.NormDefaults.Wire.legacyKinds ++ ["norm-defaults-certificate", "norm-defaults-gaps", "admission", "defaults-conflict"]
#guard [false, true].all fun r => everyKind.all fun k =>
  if VE.NormDefaults.Run.eventsServed (onBranch r k listed) k then status (onBranch r k listed) == status (onBranch r k (unlisted listed))
  else status (onBranch r k listed) == refusedKind k
#guard ([false, true].map fun r => everyKind.filter fun k => VE.NormDefaults.Run.eventsServed (onBranch r k listed) k) ==
  [["norm-defaults-elaborate", "norm-defaults-conflict", "norm-defaults-certificate"], ["norm-defaults-elaborate", "norm-defaults-conflict"]]
-- The certificate without a block replays over soft's premises alone, bound to the list as written.
#guard status (caseOf "norm-defaults-certificate" (envOf none)) == "property not found: premises"
#guard [(.top, true), (.bottom, false)].all fun ((c : VE.Formula), v) =>
  answer (replayCase (envOf none) (boundProof (envOf none) c) c) == Json.mkObj [("id", .str "a"), ("status", .str "ok"),
    ("valid", .bool v), ("premises", toJson ((decoded (envOf none)).toOption.map fun L => (VE.NormDefaults.Wire.premisesX L.U L.X []).length))]
#guard (answer (replayCase (envOf none) (boundProof (envOf none) .top) .top)) ==
  (answer (replayCase (envOf none (unlisted listed)) (boundProof (envOf none (unlisted listed)) .top (unlisted listed)) .top))
#guard status (replayCase (envOf none) (boundProof (envOf none (unlisted listed)) .top (unlisted listed)) .top) ==
  "certificate is stale or bound to different inputs"
#guard status (replayCase (envOf none) (boundProof envOf .top) .top) == "certificate is stale or bound to different inputs"
def excBare : Json := envOf none listed [VE.Defaults.Fixtures.baseJ "s", VE.Defaults.Fixtures.baseJ "t"]
#guard (match VE.Events.replayUnblockedEntailment (excCase .top excBare) with
  | .ok r => r.valid && r.L.packs.map (·.id) == ["soft"] &&
      r.L.X == (VE.NormDefaults.Wire.softLabelledU r.L.U r.L.D).map (·.2) && r.L.X.length == 2
  | .error _ => false)
-- With the block the replay is `replayEventsEntailment`'s, never this one.
#guard (match VE.Events.replayUnblockedEntailment (caseOf "norm-defaults-certificate" envOf) with
  | .error e => e == "InvalidInput: events" | .ok _ => false)
#guard status (caseOf "norm-defaults-certificate" envOf) == "property not found: premises"

/-! ## requestOf refuses events@0 (et-4b trust-mutant barrier, DRI 2026-11-08) -/

/-- An environment over `profiles`, with no predicate (the shape of `DocumentChainExamples.environmentOver`). -/
def chainEnv (profiles : List String) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [("constants", Json.mkObj []), ("predicates", Json.mkObj []),
      ("sorts", Json.mkObj [("claude_instance", Json.mkObj [("description", .str "Claude")])])])]

/-- The soft-norms@0 environment that `environmentOf` decodes, with `listed` as its profiles. `environmentOf` already
refuses an events@0 list by `ownedProfiles` (below), so the list goes on the decoded `Env`. That leaves `requestOf`'s
own test of events@0 as the only thing that can refuse it (`DocumentChainExamples.plainCase`'s style, no `check`). -/
def requestCase (listed : List String) : Except String Json := do
  let E ← VE.Service.Document.environmentOf (chainEnv ["norms@0", "relational-fol@0", "soft-norms@0"])
  pure (VE.Service.DocumentChain.requestOf
    { E with json := E.json.setObjVal! "profiles" (toJson listed), profiles := listed } (Json.mkObj []) [])

def requestIsNull (listed : List String) : Bool :=
  match requestCase listed with
  | .ok j => j == .null
  | .error _ => false

def requestIsCase (listed : List String) : Bool :=
  match requestCase listed with
  | .ok j => j != .null && j.getObjValD "norms" == Json.arr #[]
  | .error _ => false

-- The decoder refuses events@0 by itself, and accepts the list without it.
#guard (VE.Service.Document.environmentOf (chainEnv ["events@0", "norms@0", "soft-norms@0"])).toOption.isNone
#guard (VE.Service.Document.environmentOf (chainEnv ["norms@0", "relational-fol@0", "soft-norms@0"])).toOption.isSome
-- (a) events@0 the only profile beside soft-norms@0, (b) first of three, (c) last of three: no case.
#guard requestIsNull ["events@0", "soft-norms@0"]
#guard requestIsNull ["events@0", "norms@0", "soft-norms@0"]
#guard requestIsNull ["norms@0", "soft-norms@0", "events@0"]
-- The same lists without events@0 make a case, so no guard above passes because of an earlier refusal.
#guard requestIsCase ["soft-norms@0"]
#guard requestIsCase ["norms@0", "soft-norms@0"]

/-! ## events@0 owned: a refusal, never a silent empty result (pk-1-conditions-b, DRI 2026-11-08, adv1416 item 4)

`events@0` is not in `ownedProfiles`, so today `check` refuses a soft document listing it by name, before
`requestOf`. The owned case is built the way `requestCase` builds it: the `Env` decoded without events@0, then
listing it, so `check`'s soft branch reaches `layeredOf` through `requestOf`'s `null`. That case must be refused,
never a layered source with no pack; the control without events@0 is a case with the soft pack. -/

def ndListed : List String := ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]

/-- The `Env` decoded over `ndListed`, then listing `listed`: the owned case when `listed` holds events@0. -/
def ownedEnv (listed : List String) : Except String VE.Service.Document.Env := do
  let E ← VE.Service.Document.environmentOf (chainEnv ndListed)
  pure { E with json := E.json.setObjVal! "profiles" (toJson listed), profiles := listed }

def layeredCase (listed : List String) : Except String VE.NormDefaults.Wire.LayeredU := do
  VE.Service.DocumentChain.layeredOf (← ownedEnv listed) (Json.mkObj []) []

/-- `requestOf` on the same `Env` as `layeredCase`. -/
def ownedRequestIsNull (listed : List String) : Bool :=
  match ownedEnv listed with
  | .ok E => VE.Service.DocumentChain.requestOf E (Json.mkObj []) [] == .null
  | .error _ => false

def ownedLists : List (List String) := ["events@0" :: ndListed, ndListed ++ ["events@0"]]

-- Today: refused by name, before the layered route.
#guard (match VE.Service.Document.environmentOf (chainEnv ("events@0" :: ndListed)) with
  | .ok _ => "ok" | .error e => e) ==
  "CheckerUnavailable: document checks under events@0 need its Lean profile route"
-- Owned, events@0 first or last: `layeredOf` refuses it, never `.ok`; `requestOf` on that `Env` is `null`.
#guard ownedLists.all fun ps => (layeredCase ps).toOption.isNone
#guard ownedLists.all ownedRequestIsNull
-- Its text is the decoder's on `null`; it does not name events@0 (reported to the DRI, 2026-11-09).
#guard (match layeredCase ("events@0" :: ndListed) with | .ok _ => "ok" | .error e => e) == "object expected"
-- The control: without events@0 the same `Env` is a case whose one pack is soft's.
#guard (match layeredCase ndListed with | .ok L => L.packs.map (·.id) == ["soft"] | .error _ => false)
#guard !ownedRequestIsNull ndListed

end VE.Events.RouteExamples
