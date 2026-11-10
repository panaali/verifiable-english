import VE.Events.RouteExamples
import VE.Service.DocumentChainExamples

/-! et-5b's document-route fixtures (docs/spec/events-time-causation.md 1.3, 2.3, 2.9, 4 and 8.1 T15-T17; DRI
2026-11-10 item 1): an `events@0` document read by `Document.check`, one document per item of 2.9 with its diagnostic,
the open anchor term and its two checks, and T15-T17's shapes. Entailment answers (T15's NOT ENTAILED) need the prover
and are not checked here. -/

namespace VE.Service.EventsDocumentExamples
open Lean
open VE.Events.RouteExamples (parse rolePred withSorts envOf eventPreds linkJ blockJ)
open VE.Service.DocumentChain.Examples (document textOf checkError)

def rule : Json := parse (VE.Defaults.Fixtures.ruleJ "r" "x_required" true (VE.Defaults.Fixtures.dfltJ []))
def term (p : String) (args : List String := ["x", "y"]) (by_ : String := "drafters") : Json :=
  Json.mkObj [("name", .str p), ("arguments", toJson args), ("decided_by", .str by_), ("necessary", Json.arr #[]),
    ("sufficient", Json.arr #[]), ("factors", Json.arr #[]), ("precedents", Json.arr #[]),
    ("jurisdiction", .str "drafting"), ("version", toJson (1 : Nat))]
def opens : List (String × Json) := [("open_terms", Json.arr #[term "led_to"])]
def doc (e : Json) (members : List (String × Json) := opens) : Json := document e rule members
def outcome (e : Json) (members : List (String × Json) := opens) : String :=
  (checkError (doc e members)).getD "ok"

def blockD (dates : String := "[\"2026-10-12\"]") (anchor : String := "") : Json :=
  let b := blockJ dates [linkJ "led_to" "contributed" "drafters"]
  if anchor.isEmpty then b.setObjVal! "anchor" .null |> fun b => Json.mkObj (((VE.Bridge.fields b).toOption.getD []).filter (·.1 != "anchor"))
  else b.setObjVal! "anchor" (.str anchor)
def anchorConst (sort : String := "day") (wording : String := "the date of this document") : Json :=
  Json.mkObj [("sort", .str sort), ("description", .str wording)]
def withAnchor (e : Json) (c : Json := anchorConst) : Json :=
  let v := e.getObjValD "vocabulary"
  e.setObjVal! "vocabulary" (v.setObjVal! "constants" ((v.getObjValD "constants").setObjVal! "date_of_this_document" c))
def readingSet (rid : String) : Json := Json.mkObj [("id", .str "rs"), ("unit", .str "u1"), ("version", toJson (1 : Nat)),
  ("status", .str "authored"), ("signature", .str "author"), ("readings", Json.arr #[Json.mkObj [("id", .str rid),
    ("kind", .str "asserted"), ("meaning_id", .str "pending"), ("content", .null), ("admission", Json.mkObj
      [("who", .str "translator"), ("why", .str "the source word"), ("distinguishing_models", Json.mkObj [])])]])]
def openEnv : Json := withAnchor (envOf (some (blockD "[]")))
def statePreds : List String := [rolePred "thinking_forms" "[\"thinking\",\"day\"]" "{0} forms on {1}",
  rolePred "thinking_lapses" "[\"thinking\",\"day\"]" "{0} lapses on {1}",
  rolePred "standing_arises" "[\"standing\",\"day\"]" "{0} arises on {1}",
  rolePred "standing_ceases" "[\"standing\",\"day\"]" "{0} ceases on {1}"]
/-- T15's block (u0022.s02's shape): two state sorts, no events, no links, no `anchor`; `dates` as given. -/
def t15Block (dates : String := "[]") : Json := parse ("{\"day\":\"day\",\"before\":\"before\",\"events\":[],\"states\":[" ++
  "{\"sort\":\"thinking\",\"begins\":\"thinking_forms\",\"ends\":\"thinking_lapses\"}," ++
  "{\"sort\":\"standing\",\"begins\":\"standing_arises\",\"ends\":\"standing_ceases\"}],\"dates\":" ++ dates ++ ",\"links\":[]}")
def t15Env (dates : String := "[]") (ps : List String := VE.Events.RouteExamples.listed) : Json :=
  let e := envOf (some (t15Block dates)) ps statePreds
  let v := e.getObjValD "vocabulary"
  let sort := Json.mkObj [("description", .str "s")]
  withAnchor (e.setObjVal! "vocabulary" (v.setObjVal! "sorts" (((v.getObjValD "sorts").setObjVal! "thinking" sort).setObjVal!
    "standing" sort)))
def ex (s : String) (f : Json) : Json := Json.arr #[.str "exists", .str s, f]
def bin (p : String) (a b : Json) : Json := Json.arr #[.str "binary", .str p, a, b]
def v (n : Nat) : Json := Json.arr #[.str "var", toJson n]
def anchorJ : Json := Json.arr #[.str "const", .str "date_of_this_document"]
/-- T15's two assertions: a thinking formed no later than the date of this document (the begun half of "in progress"),
and "there is a day such that that day is after the date of this document and that standing begins on that day". -/
def t15Claims : List Json := [
  ex "day" (ex "thinking" (Json.arr #[.str "and", bin "thinking_forms" (v 0) (v 1),
    Json.arr #[.str "not", bin "before" anchorJ (v 1)]])),
  ex "day" (ex "standing" (Json.arr #[.str "and", bin "before" anchorJ (v 1), bin "standing_arises" (v 0) (v 1)]))]
/-- A document of the norm unit and asserted units, one source byte each. -/
def assertedDoc (e : Json) (claims : List Json) (members : List (String × Json) := []) : String :=
  let unit (i : Nat) (c : Json) := Json.mkObj [("id", .str s!"a{i}"), ("span", toJson [i + 1, i + 2]),
    ("kind", .str "asserted"), ("meaning", .str "specified"), ("support", .str "assumption"),
    ("content", Json.mkObj [("ast", c)])]
  let front := doc e members
  let units := ((front.getObjValD "units").getArr?.toOption.getD #[]) ++ (claims.zipIdx.map fun (c, i) => unit i c).toArray
  "---\n" ++ (front.setObjVal! "units" (Json.arr units)).compress ++ "\n---\n" ++ "".pushn 'x' (claims.length + 1)
def statuses (text : String) : Option (List String) :=
  (VE.Service.Document.check text).toOption.map (·.units.map (·.status))
/-- The block `environmentOf` decoded once, and the layered document `check` reads (`eventsLayeredOf`). -/
def decodedOf (e : Json) : Option VE.Events.EventsDecoded :=
  match VE.Service.Document.environmentOf e with
  | .ok E => E.events.bind (·.2)
  | .error _ => none
def labels (e : Json) : List String := ((decodedOf e).map fun d => d.labelled.map (·.1)).getD []
def layered (e : Json) : Except String VE.NormDefaults.Wire.LayeredU := do
  let front := doc e
  let c ← VE.Service.Document.check (textOf front)
  let E ← VE.Service.Document.environmentOf e (c.front.getObjValD "units")
  match E.events with
  | some (w, d) => VE.Service.DocumentChain.eventsLayeredOf E c.front c.units w d
  | none => throw "no events"
def packs (e : Json) : Option (List String) := (layered e).toOption.map (·.packs.map (·.id))

/-! ## The route admits `events@0` (DRI 2026-11-10 item 1): checked, with the block's pack, bound to the bytes -/

#guard outcome (envOf (some (blockD))) == "ok" && packs (envOf (some (blockD))) == some ["soft", "events"]
#guard outcome (envOf none) == "ok" && packs (envOf none) == some ["soft"]
-- Identities read the environment as written: its profiles and bytes, the block included.
#guard (match VE.Service.Document.environmentOf (envOf (some (blockD))) with
  | .ok E => E.profiles == VE.Events.RouteExamples.listed &&
      some E.envId == (VE.Service.Standalone.environmentIdOf E.profiles (envOf (some (blockD)))).toOption &&
      E.envId != ((VE.Service.Document.environmentOf (envOf (some (blockD "[\"2026-10-15\"]")))).toOption.map (·.envId)).getD ""
  | .error _ => false)
#guard (layered (envOf (some (blockD)))).toOption.map (·.envId) ==
  ((VE.Service.Document.environmentOf (envOf (some (blockD)))).toOption.map (·.envId))
-- Another list with `events@0` is still unavailable on this mode; `layeredOf` stays the soft branch alone.
#guard outcome (envOf none ["events@0", "norm-defaults@0", "norms@0", "relational-fol@0"]) ==
  "CheckerUnavailable: events@0 outside the soft chain under norm-defaults@0 needs its composed Lean route"

/-! ## Spec 2.9, one document per item, each with its diagnostic on the document route -/

def withBlock (f : String → String) : Json := envOf (some (parse (f (blockD).compress)))
-- 1: the row, its requirement and its refusal.
#guard outcome (envOf (some (blockD)) ["events@0", "norms@0", "relational-fol@0", "soft-norms@0"]) ==
  "UnsupportedProfile: events@0 requires norm-defaults@0"
#guard outcome (envOf (some (blockD)) (VE.Events.RouteExamples.listed ++ ["time@0"])) == "UnsupportedProfile: events@0 with time@0"
-- 2 to 6: the block's shape, the day sort, an event sort twice, an unopened link, a date.
#guard outcome (withBlock (·.replace "\"links\"" "\"extra\":1,\"links\"")) == "InvalidInput: events.extra"
#guard outcome (withBlock (·.replace "\"day\":\"day\"" "\"day\":\"days\"")) == "EventsSort: days"
#guard outcome (withBlock (·.replace "\"events\":[" "\"events\":[{\"sort\":\"act\",\"on\":\"committed_on\"},")) ==
  "DuplicateDeclaration: event sort act"
#guard outcome (envOf (some (blockD))) [] == "LinkNotOpen: led_to"
#guard outcome (envOf (some (blockD "[\"nonsense\"]"))) == "InvalidDate(nonsense)"
-- 7: the pack's charge.
def counted (links : Nat) : String :=
  let rows := fun (n : Nat) (f : Nat → String) => ",".intercalate ((List.range n).map f)
  outcome (envOf (some (parse ("{\"day\":\"day\",\"before\":\"before\",\"events\":[],\"states\":[],\"dates\":[],\"links\":[" ++
    rows links (fun i => linkJ s!"l{i}" "contributed" "drafters") ++ "]}"))))
#guard counted 256 == "EventsSort: l0" && counted 257 == "ResourceLimit: events premises"
-- 8: the open anchor term: its sort, its wording, no `anchor` beside it; then no A2 or E2 reading.
#guard outcome openEnv == "ok"
#guard outcome (withAnchor (envOf (some (blockD "[]"))) (anchorConst "act")) == "AnchorNotOpen: date_of_this_document"
#guard outcome (withAnchor (envOf (some (blockD "[]"))) (anchorConst "day" "today")) == "AnchorNotOpen: date_of_this_document"
#guard outcome (withAnchor (envOf (some (blockD "[]" "2026-10-13")))) == "AnchorNotOpen: date_of_this_document"
#guard outcome (withAnchor (envOf none)) == "AnchorNotOpen: date_of_this_document"
#guard outcome openEnv (opens ++ [("reading_sets", Json.arr #[readingSet "A2"])]) == "AnchorOpen: A2"
#guard outcome openEnv (opens ++ [("reading_sets", Json.arr #[readingSet "E2"])]) == "AnchorOpen: E2"
-- The other direction: A1 and E1 stay; without the constant an A2 reading is the author's to name.
#guard outcome openEnv (opens ++ [("reading_sets", Json.arr #[readingSet "A1"])]) == "ok"
#guard outcome openEnv (opens ++ [("reading_sets", Json.arr #[readingSet "E1"])]) == "ok"
#guard outcome (envOf (some (blockD "[]"))) (opens ++ [("reading_sets", Json.arr #[readingSet "A2"])]) == "ok"

/-! ## T15: the open anchor term, u0022.s02's shape -/

def judged : List String := ["documents@1", "events@0", "judgments@0", "norm-defaults@0", "norms@0", "relational-fol@0",
  "soft-norms@0"]
def dated : Json := Json.arr #[.str "const", .str "date__2030_01_01"]
-- Both assertions load with no GAP, and so with `judgments@0` listed (no W2 record, so no `JudgmentUnbound`).
#guard statuses (assertedDoc t15Env t15Claims) == some ["CHECKED", "CHECKED", "CHECKED"]
#guard statuses (assertedDoc (t15Env "[]" judged) t15Claims) == some ["CHECKED", "CHECKED", "CHECKED"]
-- 3 calendar premises and no `date` premise; the term is no named date, so the one named date is 2030-01-01.
def calendar : List String := ["events:irreflexive", "events:transitive", "events:linear"]
#guard [t15Env, t15Env "[\"2030-01-01\"]"].all fun e =>
  (labels e).take 3 == calendar && !(labels e).any (·.startsWith "events:date:") && (labels e).length == 9
#guard ((decodedOf t15Env).map (·.V.dates.length)) == some 0
#guard ((decodedOf (t15Env "[\"2030-01-01\"]")).map (·.V.dates.map (·.iso))) == some ["2030-01-01"]
-- The claim against the named date and its negation each load (their answers are the prover's: et-6's runs).
#guard statuses (assertedDoc (t15Env "[\"2030-01-01\"]") [bin "before" anchorJ dated,
  Json.arr #[.str "not", bin "before" anchorJ dated]]) == some ["CHECKED", "CHECKED", "CHECKED"]
-- The legend has 2.3's open-anchor line, last; a dated document's has none.
def legendOf (e : Json) : List String :=
  ((decodedOf e).map fun d => VE.Events.legend d.V ((VE.Events.openAnchor e (some d.V)).toOption.join.isSome)).getD []
#guard (legendOf t15Env).getLast? == some "This document states no date of its own, so \"the date of this document\" is left open."
#guard (legendOf t15Env).length == 2 + 1
#guard (legendOf (envOf (some (blockD)))).length == 3 &&
  !(legendOf (envOf (some (blockD)))).any (·.startsWith "This document states no date")

/-! ## T16: links between states under the open anchor, u0117.s01's shape -/

def t16Env : Json :=
  let b := parse ("{\"day\":\"day\",\"before\":\"before\",\"events\":[],\"states\":[" ++
    "{\"sort\":\"situation\",\"begins\":\"situation_begins\",\"ends\":\"situation_ends\"}," ++
    "{\"sort\":\"held_value\",\"begins\":\"value_held\",\"ends\":\"value_dropped\"}," ++
    "{\"sort\":\"felt_pressure\",\"begins\":\"pressure_felt\",\"ends\":\"pressure_eased\"}],\"dates\":[],\"links\":[" ++
    linkJ "value_contributed" "contributed" "drafters" ++ "," ++ linkJ "value_necessary" "necessary" "drafters" ++ "]}")
  let preds := [("situation", "situation_begins", "situation_ends"), ("held_value", "value_held", "value_dropped"),
    ("felt_pressure", "pressure_felt", "pressure_eased")].flatMap fun (s, p, q) =>
      [rolePred p s!"[\"{s}\",\"day\"]" "{0} begins on {1}", rolePred q s!"[\"{s}\",\"day\"]" "{0} ends on {1}"]
  let links := [rolePred "value_contributed" "[\"held_value\",\"felt_pressure\"]" "{0} contributed to {1}",
    rolePred "value_necessary" "[\"held_value\",\"felt_pressure\"]" "{0} was necessary for {1}"]
  let e := envOf (some b) VE.Events.RouteExamples.listed (preds ++ links)
  let v := e.getObjValD "vocabulary"
  let sort := Json.mkObj [("description", .str "s")]
  withAnchor (e.setObjVal! "vocabulary" (v.setObjVal! "sorts" ((((v.getObjValD "sorts").setObjVal! "situation" sort).setObjVal!
    "held_value" sort).setObjVal! "felt_pressure" sort)))
def t16Opens : List (String × Json) := [("open_terms", Json.arr #[term "value_contributed", term "value_necessary"])]
/-- "There will be situations where held values cause felt pressure", with a situation that begins after the date of
this document. -/
def t16Claim : Json := ex "day" (ex "situation" (Json.arr #[.str "and", bin "before" anchorJ (v 1),
  bin "situation_begins" (v 0) (v 1)]))
#guard statuses (assertedDoc t16Env [t16Claim] t16Opens) == some ["CHECKED", "CHECKED"]
#guard (labels t16Env).contains "events:link_weaker:value_necessary:value_contributed"
#guard outcome t16Env t16Opens == "ok" && outcome t16Env == "LinkNotOpen: value_contributed"

/-! ## T17: A2 and E2 against the document's anchor -/

open VE.EnglishGrammar (sourceReadings RuleContext AnchorState)

/-- `sourceReadings` as its candidates, or its reason with none. -/
def rd (word : String) (ctx : RuleContext) (a : AnchorState) : String × List String :=
  match sourceReadings word ctx a with
  | .ok xs => ("ok", xs)
  | .error e => (e, [])

/-- The anchor a document's reading sets are read against: its ISO anchor, its open term, or neither. -/
def anchorOf (e : Json) : AnchorState :=
  match decodedOf e with
  | some d => if d.V.anchor.isSome then .iso
      else if (VE.Events.openAnchor e (some d.V)).toOption.join.isSome then .openTerm else .none
  | none => .none
def isoEnv : Json := envOf (some (blockD "[]" "2026-10-13"))
#guard anchorOf t15Env == .openTerm && anchorOf isoEnv == .iso && anchorOf (envOf (some (blockD))) == .none
-- "always" and "eventually" in T15's document: {A1} and {E1}; with an ISO anchor: {A1, A2} and {E1, E2}.
#guard rd "always" .outside (anchorOf t15Env) == ("ok", ["<clause> on each day."])
#guard rd "eventually" .outside (anchorOf t15Env) == ("ok", ["There is a day such that <clause> on that day."])
#guard rd "always" .outside (anchorOf isoEnv) == ("ok", ["<clause> on each day.",
  "<clause> on each day, if that day is on or after the date of this document."])
#guard rd "eventually" .outside (anchorOf isoEnv) == ("ok", ["There is a day such that <clause> on that day.",
  "There is a day such that that day is after the date of this document and <clause> on that day."])
-- A reading set there with an A2 candidate (above: `AnchorOpen: A2`), and `AnchorNotOpen` twice: an ISO anchor beside
-- the constant, and the constant of another sort.
#guard outcome t15Env [("reading_sets", Json.arr #[readingSet "A2"])] == "AnchorOpen: A2"
#guard outcome (withAnchor isoEnv) == "AnchorNotOpen: date_of_this_document"
#guard outcome (withAnchor t15Env (anchorConst "thinking")) [] == "AnchorNotOpen: date_of_this_document"
