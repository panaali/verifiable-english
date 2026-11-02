import VE.Discourse.Run

/-! # Fixtures of the composed admission (docs/spec/discourse.md 14.8, item cmp-s4)

Synthetic documents over 10's α environment with the regulated `review_required : service` (14.8): `u1` asserts
`deployed(web_api)`, `u2` is the norm `review-it`. Each `#guard` names its fixture or the definition it pins. -/
namespace VE.Discourse.ComposeExamples
open Lean VE.Discourse

def src1 : String := "Web API is deployed.\n"
def src2 : String := "Every deployed service must be reviewed.\n"

/-- 10's α vocabulary; `regulated` adds the regulated predicate. -/
def vocabulary (regulated : Bool := true) : String :=
  r#"{"sorts": {"service": {"description": "Service"}, "person": {"description": "Person"}},
  "predicates": {"deployed": {"arguments": ["service"], "description": "Deployed"},
    "api": {"arguments": ["service"], "description": "API"},
    "owns": {"arguments": ["person", "service"], "description": "Owner"}"# ++
  (if regulated then r#", "review_required": {"arguments": ["service"], "description": "must be reviewed",
    "regulated": {"role": "obligation", "default": "allow", "act": "{0} be reviewed"}}"# else "") ++
  r#"}, "constants": {"web_api": {"sort": "service", "description": "Web API"},
    "alice": {"sort": "person", "description": "Alice"}}}"#

def normUnit (id : String) (a b : Nat) : String :=
  s!"\{\"id\": \"{id}\", \"span\": [{a}, {b}], \"kind\": \"norm\", \"meaning\": \"specified\", \"support\": \"none\", " ++
  s!"\"content\": \{\"norm\": \{\"name\": \"rule-{id}\", \"predicate\": \"review_required\", \"sign\": true, " ++
  "\"guard\": [\"unary\", \"deployed\", [\"var\", 0]], \"unless\": [], \"over\": []}}}"

def u1 : String :=
  s!"\{\"id\": \"u1\", \"span\": [0, {src1.utf8ByteSize}], \"kind\": \"asserted\", \"meaning\": \"specified\", " ++
  "\"support\": \"assumption\", \"content\": {\"ast\": [\"unary\", \"deployed\", [\"const\", \"web_api\"]]}}"

/-- The two units; `u2Content` replaces the norm content of `u2`. -/
def units (u2Content : Option String := none) : String :=
  "[" ++ u1 ++ ", " ++ (match u2Content with
    | none => normUnit "u2" src1.utf8ByteSize (src1 ++ src2).utf8ByteSize
    | some c => s!"\{\"id\": \"u2\", \"span\": [{src1.utf8ByteSize}, {(src1 ++ src2).utf8ByteSize}], \"kind\": " ++
        s!"\"norm\", \"meaning\": \"specified\", \"support\": \"none\", \"content\": {c}}") ++ "]"

def graph : String :=
  r#""graph": {"root": "n", "nodes": [{"name": "n", "ast": ["top"], "label": "open:t"}]}, "open_terms": [{"name": "t",
  "arguments": [], "decided_by": "reviewer", "necessary": [], "sufficient": [], "factors": [], "precedents": [],
  "jurisdiction": "policy", "version": 1}]"#

/-- A document text: format, profiles, units, the discourse block and the rest of the front matter. -/
def doc (profiles : String := r#""norms@0", "relational-fol@0", "ve.discourse@1""#) (format := "ve-document@2")
    (us : String := units) (discourse := r#", "discourse": {"version": "ve.discourse@1", "anchors": []}"#)
    (rest := ", " ++ graph) (regulated := true) (body := src1 ++ src2) : String :=
  s!"---\n\{\"format\": \"{format}\", \"environment\": \{\"language\": \"ve.core@0.2\", " ++
  s!"\"spec_revision\": \"ve-v0.2-expand2-2026-09-25\", \"vocabulary\": {vocabulary regulated}, " ++
  s!"\"profiles\": [{profiles}]}, \"units\": {us}{discourse}{rest}}\n---\n{body}"

def caseOf (text : String) : Json :=
  Json.mkObj [("id", .str "s4"), ("kind", .str "admission"), ("document", .str text)]

/-- The composed entry's answer: `chain` and the wrapper JSON, `today` and today's encoding, or the error. -/
def composed (text : String) : String :=
  match VE.Discourse.Run.loadCase (caseOf text) with
  | .error e => "load: " ++ e
  | .ok (d, env) => match VE.Route.Gate.profilesOf env >>= fun ps => admitComposed ps env d with
    | .ok (.chain c) => "chain " ++ (composedJson c).compress
    | .ok (.today r) => "today " ++ ((VE.Discourse.Run.encodeAdmission "s4" r).toOption.getD .null).compress
    | .error e => "error: " ++ e

/-- Today's discourse admission of the same case (`admitDiscourse` under `baseVocabulary`). -/
def today (text : String) : String :=
  match VE.Discourse.Run.loadCase (caseOf text) with
  | .error e => "load: " ++ e
  | .ok (d, env) => match (do
      let ps ← VE.Route.Gate.profilesOf env
      admitDiscourse ps env (← baseVocabulary env) d fuelBudget) with
    | .ok r => "today " ++ ((VE.Discourse.Run.encodeAdmission "s4" r).toOption.getD .null).compress
    | .error e => "error: " ++ e

def chainField (text key : String) : Json :=
  ((Json.parse ((composed text).drop 6)).toOption.getD .null).getObjValD key

/-! ## The composed path (14.5) -/

-- S4-1 (synthetic): the norms route admits the resolved document; `inner` is its answer, the wrapper binds it
#guard (composed doc).startsWith "chain "
#guard (chainField doc "inner").getObjValD "admitted" == .bool true
#guard (chainField doc "inner").getObjValD "kinds" == Json.arr #[.str "asserted", .str "norm"]
#guard chainField doc "inner_report_id" == (chainField doc "inner").getObjValD "report_id"
-- S4-1: `inner` is the norms route's answer on the document without the discourse block (`chainDocument`)
#guard match VE.Discourse.Run.loadCase (caseOf doc) with
  | .ok (d, env) => (chainDocument (baseEnvironment env) d >>= VE.Norms.Run.runAdmission "" (baseEnvironment env)).toOption ==
      some (chainField doc "inner")
  | .error _ => false
-- a large well-formed document: 200 norm units end within the chain document's byte limit
def large : String :=
  let n := 200
  let line := "Rule.\n"
  let us := (List.range n).map fun i => normUnit s!"r{i}" (i * line.utf8ByteSize) ((i + 1) * line.utf8ByteSize)
  doc (us := "[" ++ ", ".intercalate us ++ "]") (body := String.join (List.replicate n line))
#guard (composed large).startsWith "chain "

-- S4-16, S4-17, the soft and rights lists: in item cmp-s4 the wrapper's FOL-family check is the frozen gate, which
-- refuses them as today (their chain decoders and `dispatchAdmission`'s refusals are item cmp-s4c)
#guard composed (doc (profiles := r#""norms@0", "readings@1", "relational-fol@0", "ve.discourse@1""#)) ==
  today (doc (profiles := r#""norms@0", "readings@1", "relational-fol@0", "ve.discourse@1""#))
#guard composed (doc (profiles := r#""norms@0", "relational-fol@0", "speech-acts@0", "ve.discourse@1""#)) ==
  "error: UnsupportedProfile: Unsupported profile speech-acts@0"
#guard composed (doc (profiles := r#""norms@0", "relational-fol@0", "soft-norms@0", "ve.discourse@1""#)) ==
  today (doc (profiles := r#""norms@0", "relational-fol@0", "soft-norms@0", "ve.discourse@1""#))
-- S4-20: a `groups` entry (14.5 step 1, named abstention)
#guard composed (doc (discourse := r#", "discourse": {"version": "ve.discourse@1", "anchors": [], "groups": [{}]}"#)) ==
  "error: NotImplemented: groups on the chain"
#guard composed (doc (rest := ", " ++ graph ++ r#", "reading_sets": [{}]"#)) ==
  "error: NotImplemented: reading sets on the chain"
-- S4-21 (OPEN 2): no claim graph, as today
#guard composed (doc (rest := "")) == "error: NotImplemented: a document without a claim graph"
-- 14.5 step 3: `definitions_version` names the chain route's environment id
#guard composed (doc (discourse := r#", "discourse": {"version": "ve.discourse@1", "anchors": [],
  "definitions_version": "x"}"#)) == "error: StaleTarget: definitions@x"
-- 14.3 step 6: a recorded formula-producing mention on a JSON content
def mention (unit : String) : String :=
  s!", \"discourse\": \{\"version\": \"ve.discourse@1\", \"anchors\": [], \"mentions\": [\{\"id\": \"m1\", " ++
  s!"\"unit\": \"{unit}\", \"span\": [0, 3], \"form\": \"pronoun\", \"target\": \{\"kind\": \"entity\", \"name\": \"web_api\"}}]}"
#guard composed (doc (discourse := mention "u2")) == "error: MentionNotSlot: m1"
-- item cmp-s4's abstentions: a bound prose unit and a fenced unit (14.3's slot steps are item cmp-s4ab)
#guard composed (doc (discourse := mention "u1")) == "error: NotImplemented: a bound prose unit on the chain"
#guard composed (doc (us := units (some r#"{"fence": "u2"}"#))) == "error: NotImplemented: fenced content on the chain"

/-! ## Identity cases (14.6): today's answer, byte for byte -/

def alpha (profiles : String) : String :=
  doc (profiles := profiles) (us := "[" ++ u1 ++ "]") (regulated := false)
    (body := src1)

-- S4-3: α with `norms@0`, no chain construct
#guard (composed (alpha r#""norms@0", "relational-fol@0", "ve.discourse@1""#)).startsWith "today "
#guard composed (alpha r#""norms@0", "relational-fol@0", "ve.discourse@1""#) ==
  today (alpha r#""norms@0", "relational-fol@0", "ve.discourse@1""#)
-- S4-2 (α): today's answer
#guard composed (alpha r#""relational-fol@0", "ve.discourse@1""#) == today (alpha r#""relational-fol@0", "ve.discourse@1""#)
-- S4-28: a `ve-document@1` text on `norms@0, relational-fol@0` with a norm unit is not the composed path
def s428 : String := doc (profiles := r#""norms@0", "relational-fol@0""#) (format := "ve-document@1") (discourse := "")
#guard !(composed s428).startsWith "chain "
#guard composed s428 == today s428
-- S4-25: no `norms@0`, a vocabulary `baseVocabulary` rejects: today's error
def s425 : String := doc (profiles := r#""relational-fol@0", "ve.discourse@1""#)
#guard (composed s425).startsWith "error: "
#guard composed s425 == today s425

/-! ## Chain constructs (14.2), cases (14.4) and the pre-order of `conditional_on` -/

def env (vocabulary : String) : Json := Json.mkObj [("vocabulary", (Json.parse vocabulary).toOption.getD .null)]
def payload (units : String) : Json :=
  Json.mkObj [("metadata", (Json.parse s!"\{\"units\": {units}}").toOption.getD .null)]
#guard chainConstructs (env "{\"soft\": {}}") .null
#guard chainConstructs (env "{\"rights\": {}}") .null
#guard chainConstructs (env "{\"predicates\": {\"p\": {\"regulated\": {}}}}") .null
#guard !chainConstructs (env "{\"predicates\": {\"p\": {}}}") .null
#guard chainConstructs .null (payload r#"[{"id": "u", "parts": [{"id": "p", "content": {"right": {}}}]}]"#)
#guard !chainConstructs .null (payload r#"[{"id": "u", "content": {"ast": ["top"]}}]"#)

-- `contentFree`: every unit's and part's content `null`, `fences` emptied, nothing else touched
#guard contentFree (Json.mkObj [("metadata", (Json.parse r#"{"units": [{"id": "u", "content": 1,
  "parts": [{"id": "p", "content": 2}]}], "format": "f"}"#).toOption.getD .null), ("fences", Json.mkObj [("u", "t")]),
  ("source", "s")]) == Json.mkObj [("metadata", (Json.parse r#"{"units": [{"id": "u", "content": null,
  "parts": [{"id": "p", "content": null}]}], "format": "f"}"#).toOption.getD .null), ("fences", Json.mkObj []),
  ("source", "s")]

-- S4-22 (without a fence): the case written out as a `ve-document@1` text, its shape kept; `checkCore` on it equals
-- `checkCore` on the hand-written `@1` document
def resolved : Json := (resolveCase (caseOf doc)).toOption.getD .null
def front (j : Json) : Json :=
  (((j.getObjValD "document").getStr?.toOption.bind fun t => (Loader.splitText t).toOption).map (·.front)).getD .null
#guard (front resolved).getObjValD "format" == .str "ve-document@1"
#guard ((front resolved).getObjVal? "discourse").toOption.isNone
#guard ((front resolved).getObjValD "environment").getObjValD "profiles" ==
  Json.arr #[.str "norms@0", .str "relational-fol@0"]
#guard (caseShape resolved).compress == (caseShape (caseOf doc)).compress
#guard (caseShape resolved).getObjValD "document" != .null
#guard ((VE.Service.Document.checkCore resolved).toOption.map Json.compress) ==
  ((VE.Service.Document.checkCore (caseOf (doc (profiles := r#""norms@0", "relational-fol@0""#)
    (format := "ve-document@1") (discourse := "")))).toOption.map Json.compress)
#guard ((VE.Service.Document.checkCore resolved).toOption.map (·.getObjValD "status")) == some (.str "ok")
-- S4-23: a case without `ve.discourse@1` is returned as it is
#guard (resolveCase (caseOf s428)).toOption.map Json.compress == some (caseOf s428).compress

-- `conditionalOnOf`: every `conditional_on` list, pre-order, keys in order, arrays in order
#guard conditionalOnOf ((Json.parse r#"{"a": {"conditional_on": ["x"]}, "b": [{"conditional_on": ["y"]},
  {"conditional_on": "z"}], "conditional_on": ["w", {"conditional_on": ["v"]}]}"#).toOption.getD .null) ==
  [Json.arr #[.str "x"], Json.arr #[.str "y"], (Json.parse r#"["w", {"conditional_on": ["v"]}]"#).toOption.getD .null,
   Json.arr #[.str "v"]]

end VE.Discourse.ComposeExamples
