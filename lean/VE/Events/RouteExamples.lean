import VE.NormDefaults.Run
import VE.Defaults.Examples

/-! et-4b's route fixtures (docs/spec/events-time-causation.md 3, 4; plan ET-4): the hook through the layered decoders
and the service, the identities, the date constants in the vocabulary limit and the kinds a list with `events@0` is
answered on, each on both sides of its boundary. The hook's own checks are `WireExamples.lean`'s; certificates are
`tests/test_events_route.py`'s, with the untrusted prover. -/
namespace VE.Events.RouteExamples
open Lean
open VE.Events
open VE.Defaults.Fixtures (regJ xReq xPerm envJ strictSoft ruleJ dfltJ)
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
def filled (k : Nat) (b : Json) : String := match decoded (envOf b listed
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

-- A replay needs the block: with the profile alone there is no pack to replay against.
#guard status (caseOf "norm-defaults-certificate" (envOf none)) == "InvalidInput: events"
#guard status (caseOf "norm-defaults-certificate" envOf) == "property not found: premises"

end VE.Events.RouteExamples
