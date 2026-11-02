import VE.NormDefaults.Run
import VE.Defaults.Examples

/-! et-4b's route fixtures (docs/spec/events-time-causation.md 1.1, 3, 4; plan ET-4): the profile row, `LinkNotOpen` in
its place, the charged limits, the view a layered decoder reads and the kinds a list with `events@0` is answered on,
each on both sides of its boundary. Certificates are `tests/test_events_route.py`'s, with the untrusted prover. -/
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

/-- A block's fault on the route's hook, or the labels of its pack. -/
def hook (e : Json) (t : Json := terms) : Except String (List String) := do
  match ← eventsHook e t with
  | some ⟨_, some d⟩ => pure (d.labelled.map (·.1))
  | _ => pure []
def fault (e : Json) (t : Json := terms) : String := match hook e t with
  | .ok _ => "ok"
  | .error m => m

-- The accepting fixture: the profile, the block and the open term on a soft document.
#guard elaborated envOf == "ok"

/-! ## Item 1: the row, before any events check -/

def bad : Json := blockJ "[\"nonsense\"]"

-- Each requirement in its order, then the admitted list; the block's own fault comes only after the row.
#guard fault (envOf bad ["events@0", "norm-defaults@0", "norms@0"]) == "UnsupportedProfile: events@0 requires relational-fol@0"
#guard fault (envOf bad ["events@0", "norm-defaults@0", "relational-fol@0"]) == "UnsupportedProfile: events@0 requires norms@0"
#guard fault (envOf bad ["events@0", "norms@0", "relational-fol@0"]) == "UnsupportedProfile: events@0 requires norm-defaults@0"
#guard fault (envOf bad) == "InvalidDate(nonsense)"
#guard fault (envOf none) == "ok"
-- Every refused profile by name, first in the sorted list, ahead of any other row's text.
#guard VE.Compose.eventsRefused.all fun p =>
  let ps := (listed ++ [p]).toArray.qsort (· < ·) |>.toList
  fault (envOf bad ps) == s!"UnsupportedProfile: events@0 with {p}"
#guard fault (envOf bad ["alternatives@0", "events@0", "norm-defaults@0", "norms@0", "relational-fol@0", "risk@0"]) ==
  "UnsupportedProfile: events@0 with alternatives@0"
-- Beside it: what the layered route admits, on the block's own check.
#guard ["documents@1", "rights@0", "readings@1", "definitions@0"].all fun p =>
  let ps := (listed ++ [p]).toArray.qsort (· < ·) |>.toList
  VE.Compose.eventsFault ps == none && fault (envOf bad ps) == "InvalidDate(nonsense)"
-- A list without the profile is read as before: no hook, and the route's own refusal of the key.
#guard (match eventsHook (envOf (some bad) ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]) terms with
  | .ok none => true | _ => false)
#guard elaborated (envOf (some blockJ) ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]) ==
  "InvalidInput: invalid environment envelope"
-- The row's text on a list the norm-defaults profile is missing from, through the service.
#guard elaborated (envOf bad ["events@0", "norms@0", "relational-fol@0"]) == "UnsupportedProfile: events@0 requires norm-defaults@0"
-- The modes that gate by `baseRows` hook no pack: the profile stays unknown to them.
#guard (match VE.Compose.gateOf VE.Compose.baseRows listed with
  | .error e => e | .ok _ => "ok") == "UnsupportedProfile: Unsupported profile events@0"

/-! ## Item 5: `LinkNotOpen`, after the link's own faults and before the dates -/

#guard fault envOf (parse "[]") == "LinkNotOpen: led_to"
#guard fault envOf (parse "[{\"name\":\"led_to\",\"decided_by\":\"the court\"}]") == "LinkNotOpen: led_to"
#guard fault envOf (parse "[{\"name\":\"needed\",\"decided_by\":\"the drafters\"}]") == "LinkNotOpen: led_to"
#guard fault envOf (parse "[{\"name\":\"led_to\"}]") == "LinkNotOpen: led_to"
#guard fault envOf (.num 7) == "LinkNotOpen: led_to"
#guard fault envOf == "ok"
-- Every link is read, and its form's wording and repeats come first.
def twoLinks : Json := blockJ (links := [linkJ "led_to", linkJ "needed" "necessary"])
def bothTerms : Json := parse "[{\"name\":\"led_to\",\"decided_by\":\"the drafters\"},{\"name\":\"needed\",\"decided_by\":\"the drafters\"}]"
#guard fault (envOf twoLinks) == "LinkNotOpen: needed"
#guard fault (envOf twoLinks) bothTerms == "ok"
#guard fault (envOf (blockJ (links := [linkJ "needed" "necessary", linkJ "led_to"]))) == "LinkNotOpen: needed"
#guard fault (envOf (blockJ (links := [linkJ "needed", linkJ "led_to"]))) (parse "[]") == "EventsVerbalisation: needed"
#guard fault (envOf (blockJ (links := [linkJ "led_to", linkJ "led_to"]))) (parse "[]") == "DuplicateDeclaration: link led_to"
-- `unstated` is the decider as written, the absence of one.
#guard fault (envOf (blockJ (links := [linkJ "led_to" "contributed" "unstated"]))) == "LinkNotOpen: led_to"
#guard fault (envOf (blockJ (links := [linkJ "led_to" "contributed" "unstated"])))
  (parse "[{\"name\":\"led_to\",\"decided_by\":\"unstated\"}]") == "ok"
-- Items 5 then 6: an open-term fault comes before a date's, and a date's is reached with the term.
#guard fault (envOf bad) (parse "[]") == "LinkNotOpen: led_to"
#guard fault (envOf bad) == "InvalidDate(nonsense)"
#guard (decodeEvents envOf).toOption.isSome && (decodeEventsWith (checkOpen []) envOf).toOption.isNone

/-! ## The charged limits: every value evaluated once, its size against a stated limit -/

def isos (n : Nat) : List String := (List.range n).filterMap fun i => (VE.Time.civilOf (20000 + i)).map (·.iso)
def datesJ (ds : List String) : String := (toJson ds).compress

/-- A growing chain of consecutive days: the premises grow by two a day, and the 65th date (the anchor is one) is
    refused by its limit, with the same fault at any size past it. -/
def chain (n : Nat) : Json := envOf (blockJ (datesJ (isos n)))
#guard [1, 10, 63].all fun n => ((hook (chain n)).toOption.map (·.length)) == some (2 * n + 4)
#guard fault (chain 63) == "ok"
#guard fault (chain 64) == "ResourceLimit: events dates"
#guard fault (chain 100000) == "ResourceLimit: events dates"
-- The largest list still reports its repeat (spec 4's order) and ends: the check is one pass, whatever the size.
#guard fault (envOf (blockJ (datesJ (isos 100000 ++ ["2024-10-05"])))) == "DuplicateDeclaration: date 2024-10-05"
#guard repeatOf [] ["a", "b", "a", "b"] == some "a" && repeatOf ["b"] ["a", "b"] == some "b" && repeatOf ["c"] ["a", "b"] == none
-- The roles and links are charged before they are read against each other; just inside, the next fault is theirs.
def manyLinks (n : Nat) : List String := (List.range n).map fun i => linkJ s!"l{i}"
#guard fault (envOf (blockJ (links := manyLinks 256))) == "ResourceLimit: events premises"
#guard fault (envOf (blockJ (links := manyLinks 255))) == "EventsSort: l0"
#guard fault (envOf (blockJ (links := manyLinks 100000))) == "ResourceLimit: events premises"
-- The whole pack against `maxNodes`, one premise at a time first: 60 necessary and 60 contributed links on one pair.
def linkPreds (p w : String) (n : Nat) : List String :=
  (List.range n).map fun i => rolePred s!"{p}{i}" "[\"act\",\"act\"]" w
def weaker (n : Nat) : Json :=
  let links := ((List.range n).map fun i => linkJ s!"c{i}") ++ (List.range n).map fun i => linkJ s!"n{i}" "necessary"
  let terms := Json.arr ((List.range (2 * n)).map fun i =>
    parse ("{\"name\":\"" ++ (if i < n then s!"c{i}" else s!"n{i - n}") ++ "\",\"decided_by\":\"the drafters\"}")).toArray
  Json.mkObj [("e", envOf (blockJ (links := links)) listed
    (linkPreds "c" "{0} contributed to {1}" n ++ linkPreds "n" "{0} was necessary for {1}" n)), ("t", terms)]
#guard fault ((weaker 60).getObjValD "e") ((weaker 60).getObjValD "t") == "ResourceLimit: events premises"
#guard fault ((weaker 30).getObjValD "e") ((weaker 30).getObjValD "t") == "ok"
-- One premise at its limit and one over, and the whole list at its limit and one over; the last premise is read too.
def pack : List (String × VE.Formula) := match eventsHook envOf terms with
  | .ok (some ⟨_, some d⟩) => d.labelled
  | _ => []
def sized (limit : Nat) (ls : List (String × VE.Formula)) : String := match checkPremiseSize limit ls with
  | .ok _ => "ok"
  | .error e => e
def nodes (i : Nat) : Nat := VE.Bridge.formulaNodes (pack.getD i ("", .top)).2
#guard nodes 0 < nodes 1
#guard sized (nodes 1) (pack.take 2 |>.drop 1) == "ok"
#guard sized (nodes 1 - 1) (pack.take 2) == "ResourceLimit: events premise events:transitive"
#guard sized (nodes 0 + nodes 1) (pack.take 2) == "ok"
#guard sized (nodes 0 + nodes 1 - 1) (pack.take 2) == "ResourceLimit: events premises"

/-! ## The view a layered decoder reads, and the identities it does not -/

def decoded (e : Json) (t : Json := terms) : Except String LayeredU := decodeLayered (caseOf "k" e t)
def viewOf (e : Json) : Json := match eventsHook e terms with
  | .ok (some h) => h.view
  | _ => .null

#guard (viewOf envOf).getObjVal? "events" |>.toBool |> not
#guard VE.Compose.listedProfiles (viewOf envOf) == ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]
-- One constant per named date, in the day sort, the anchor's with its fixed wording; the author's constants stay.
def viewConstants : Json := ((viewOf envOf).getObjValD "vocabulary").getObjValD "constants"
#guard viewConstants.getObjValD "date__2026_10_12" == parse "{\"sort\":\"day\",\"description\":\"2026-10-12\"}"
#guard viewConstants.getObjValD "date__2026_10_13" ==
  parse "{\"sort\":\"day\",\"description\":\"the date of this document\"}"
#guard viewConstants.getObjValD "date__2026_10_14" == parse "{\"sort\":\"day\",\"description\":\"2026-10-14\"}"
#guard (VE.Bridge.fields viewConstants).toOption.map (·.length) == some 3
-- No block, no constant: the view of a listed profile with an absent block only drops the profile.
#guard viewOf (envOf none) == (envOf none).setObjVal! "profiles" (toJson (listed.filter (· != "events@0")))
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

-- A replay needs the block: with the profile alone there is no pack to replay against.
#guard status (caseOf "norm-defaults-certificate" (envOf none)) == "InvalidInput: events"
#guard status (caseOf "norm-defaults-certificate" envOf) == "property not found: premises"

end VE.Events.RouteExamples
