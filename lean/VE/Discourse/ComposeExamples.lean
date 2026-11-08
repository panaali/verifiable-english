import VE.Discourse.Run

/-! # Fixtures of the composed admission (docs/spec/discourse.md 14.8, item cmp-s4)

Synthetic documents over 10's α environment with the regulated `review_required : service` (14.8): `u1` asserts
`deployed(web_api)`, `u2` is the norm `review-it`. Each `#guard` names its fixture or the definition it pins. These
check each step on its own input; the end-to-end admissions are in `VE/Service/ComposedAdmissionExamples.lean`. -/
namespace VE.Discourse.ComposeExamples
open Lean VE.Discourse

def src1 : String := "Web API is deployed.\n"
def src2 : String := "Every deployed service must be reviewed.\n"

/-- 10's α vocabulary; `regulated` adds the regulated predicate. -/
def vocabulary (regulated : Bool := true) : String :=
  "{\"sorts\": {\"service\": {\"description\": \"Service\"}, \"person\": {\"description\": \"Person\"}},
  \"predicates\": {\"deployed\": {\"arguments\": [\"service\"], \"description\": \"Deployed\"},
    \"api\": {\"arguments\": [\"service\"], \"description\": \"API\"},
    \"owns\": {\"arguments\": [\"person\", \"service\"], \"description\": \"Owner\"}" ++
  (if regulated then ", \"review_required\": {\"arguments\": [\"service\"], \"description\": \"must be reviewed\",
    \"regulated\": {\"role\": \"obligation\", \"default\": \"allow\", \"act\": \"{0} be reviewed\"}}" else "") ++
  "}, \"constants\": {\"web_api\": {\"sort\": \"service\", \"description\": \"Web API\"},
    \"alice\": {\"sort\": \"person\", \"description\": \"Alice\"}}}"

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
  "\"graph\": {\"root\": \"n\", \"nodes\": [{\"name\": \"n\", \"ast\": [\"top\"], \"label\": \"open:t\"}]}, \"open_terms\": [{\"name\": \"t\",
  \"arguments\": [], \"decided_by\": \"reviewer\", \"necessary\": [], \"sufficient\": [], \"factors\": [], \"precedents\": [],
  \"jurisdiction\": \"policy\", \"version\": 1}]"

/-- A document text: format, profiles, units, the discourse block and the rest of the front matter. -/
def doc (profiles : String := "\"norms@0\", \"relational-fol@0\", \"ve.discourse@1\"") (format := "ve-document@2")
    (us : String := units) (discourse := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": []}")
    (rest := ", " ++ graph) (regulated := true) (body := src1 ++ src2) : String :=
  s!"---\n\{\"format\": \"{format}\", \"environment\": \{\"language\": \"ve.core@0.2\", " ++
  s!"\"spec_revision\": \"ve-v0.2-expand2-2026-09-25\", \"vocabulary\": {vocabulary regulated}, " ++
  s!"\"profiles\": [{profiles}]}, \"units\": {us}{discourse}{rest}}\n---\n{body}"

def caseOf (text : String) : Json :=
  Json.mkObj [("id", .str "s4"), ("kind", .str "admission"), ("document", .str text)]

def mention (unit : String) : String :=
  s!", \"discourse\": \{\"version\": \"ve.discourse@1\", \"anchors\": [], \"mentions\": [\{\"id\": \"m1\", " ++
  s!"\"unit\": \"{unit}\", \"span\": [0, 3], \"form\": \"pronoun\", \"target\": \{\"kind\": \"entity\", \"name\": \"web_api\"}}]}"

/-! ## The steps of the composed path, each on its own input -/

def ok? : Except String Unit → String
  | .ok () => "ok"
  | .error e => e
def parsed (s : String) : Json := (Json.parse s).toOption.getD .null
def mentionBlock (unit : String) : Json := parsed ((mention unit).drop 15)
def manifestOf (unit : String) : Manifest :=
  (Wire.decodeManifest [] [] "e" (mentionBlock unit)).toOption.getD emptyManifest
def unitJ (content : Option String) (id := "u2") : Json :=
  parsed (s!"\{\"id\": \"{id}\"" ++ (content.map (", \"content\": " ++ ·)).getD "" ++ "}")

-- 14.3 step 6 and this item's abstentions (`contentOk`), with the opposite direction
#guard (manifestOf "u2").mentions.length == 1
#guard ok? (contentOk (manifestOf "u2") (unitJ "{\"norm\": {}}")) == "MentionNotSlot: m1"
#guard ok? (contentOk (manifestOf "u2") (unitJ "{\"right\": {}}")) == "MentionNotSlot: m1"
def twoMentions : Manifest :=
  { manifestOf "u2" with mentions := (manifestOf "u2").mentions ++ (manifestOf "u2").mentions.map (fun m => { m with id := "m2" }) }
#guard ok? (contentOk twoMentions (unitJ "{\"norm\": {}}")) == "MentionNotSlot: m1"
#guard ok? (contentOk (manifestOf "u2") (unitJ "{\"fence\": \"u2\"}")) == "NotImplemented: fenced content on the chain"
#guard ok? (contentOk (manifestOf "u1") (unitJ "{\"fence\": \"u2\"}")) == "NotImplemented: fenced content on the chain"
#guard ok? (contentOk (manifestOf "u2") (unitJ "{\"ast\": [\"top\"]}")) == "NotImplemented: a bound prose unit on the chain"
#guard ok? (contentOk (manifestOf "u2") (unitJ none)) == "NotImplemented: a bound prose unit on the chain"
#guard ok? (contentOk (manifestOf "u1") (unitJ "{\"norm\": {}}")) == "ok"
#guard ok? (contentOk (manifestOf "u1") (unitJ "{\"ast\": [\"top\"]}")) == "ok"

-- 14.5 step 1's named abstentions (`chainAbstentions`), and empty or absent lists are none
#guard ok? (chainAbstentions (parsed "{\"discourse\": {\"groups\": [{}]}}")) == "NotImplemented: groups on the chain"
#guard ok? (chainAbstentions (parsed "{\"discourse\": {\"constraints\": [{}]}}")) ==
  "NotImplemented: constraints on the chain"
#guard ok? (chainAbstentions (parsed "{\"discourse\": {\"validity\": [{}]}}")) ==
  "NotImplemented: validity claims on the chain"
#guard ok? (chainAbstentions (parsed "{\"reading_sets\": [{}]}")) == "NotImplemented: reading sets on the chain"
#guard ok? (chainAbstentions (parsed "{\"discourse\": {\"groups\": [], \"constraints\": [], \"validity\": []},
  \"reading_sets\": []}")) == "ok"
#guard ok? (chainAbstentions (parsed "{}")) == "ok"

-- `chainUnit`: an `ast` content its formula, any other content as written, no content none
#guard (chainUnit (parsed "{\"id\": \"u\", \"span\": [0, 1], \"kind\": \"asserted\", \"content\": {\"ast\": [\"top\"]}}")).compress ==
  "{\"content\":[\"top\"],\"id\":\"u\",\"kind\":\"asserted\",\"span\":[0,1]}"
#guard (chainUnit (parsed "{\"id\": \"u\", \"span\": [0, 1], \"kind\": \"norm\", \"content\": {\"norm\": {}}}")).compress ==
  "{\"content\":{\"norm\":{}},\"id\":\"u\",\"kind\":\"norm\",\"span\":[0,1]}"
#guard (chainUnit (parsed "{\"id\": \"u\", \"span\": [0, 1], \"kind\": \"asserted\"}")).compress ==
  "{\"id\":\"u\",\"kind\":\"asserted\",\"span\":[0,1]}"

-- `caseShape`: the id, the source and the front matter without what resolution rewrites (profiles, format, the
-- discourse key, contents); anything else changed is another shape
def shape (text : String) : String := (caseShape (caseOf text)).compress
#guard shape doc == shape (doc (profiles := "\"norms@0\", \"relational-fol@0\"") (format := "ve-document@1")
  (discourse := "") (us := units (some "{\"norm\": {}}")))
#guard shape doc != shape (doc (body := src2 ++ src1))
#guard shape doc != shape (doc (regulated := false))
#guard shape doc != shape (doc (us := "[" ++ u1 ++ "]"))
#guard (caseShape (caseOf doc)).getObjValD "id" == .str "s4"
#guard (caseShape (caseOf doc)).getObjValD "document" != .null

-- `chainBase` and `caseManifest`: the manifest decoded under the chain route's environment id (step 3's default)
def loaded (text : String) : Json × Json :=
  match Loader.splitText text with
  | .ok s => (s.front.getObjValD "environment", Loader.payload s (Json.mkObj []))
  | .error _ => (.null, .null)
#guard ((chainBase (loaded doc).1 (loaded doc).2).toOption.map fun (_, K, id) =>
  K.definitionsVersion == id && id.length == 64) == some true
-- `caseManifest`: the case's recorded mentions, under the base pair, after 14.5 step 4's checks (a navigation
-- mention passes them; `VE/Service/ComposedAdmissionExamples.lean` has the refusals)
#guard ((caseManifest (caseOf (doc (discourse := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": [], " ++
  "\"mentions\": [{\"id\": \"m1\", \"unit\": \"u1\", \"span\": [0, 3], \"form\": \"navigation\", " ++
  "\"target\": {\"kind\": \"unit\", \"units\": [\"u2\"]}}]}")))).toOption.map (·.2.mentions.map (·.id))) ==
  some ["m1"]

-- `formulaUnit`: W2's view of a unit on the composed path, an `ast` content its formula, any other content none
#guard (formulaUnit (parsed "{\"id\": \"u\", \"span\": [0, 1], \"kind\": \"asserted\", \"content\": {\"ast\": [\"top\"]}}")).compress ==
  "{\"content\":[\"top\"],\"id\":\"u\",\"kind\":\"asserted\",\"span\":[0,1]}"
#guard (formulaUnit (parsed "{\"id\": \"u\", \"span\": [0, 1], \"kind\": \"norm\", \"content\": {\"norm\": {}}}")).compress ==
  "{\"id\":\"u\",\"kind\":\"norm\",\"span\":[0,1]}"

-- `chainDDoc`, and `slotUnit` and `coveredOk` on it (14.3 step 6): a chain content's unit is a unit with meaning.
-- u1 asserts, u2 and u3 are norm units reading `It`, u4 has no content.
def itText : String := "It must be reviewed when deployed.\n"
def bareUnit (id : String) (a b : Nat) : String :=
  s!"\{\"id\": \"{id}\", \"span\": [{a}, {b}], \"kind\": \"exposition\", \"meaning\": \{\"unformalised\": \"commentary\"}, " ++
  "\"support\": \"none\"}"
def fourUnits : String :=
  doc (us := "[" ++ u1 ++ ", " ++ normUnit "u2" 21 56 ++ ", " ++ normUnit "u3" 56 91 ++ ", " ++ bareUnit "u4" 91 102 ++ "]")
    (body := src1 ++ itText ++ itText ++ "See above.\n")
def chainD : Option DDoc := do
  let (e, p) := loaded fourUnits
  let (rv, K, _) ← (chainBase e p).toOption
  (chainDDoc rv e p K).toOption
#guard chainD.map (·.chain) == some ["u2", "u3"]
#guard chainD.map (fun D => ["u1", "u2", "u3", "u4"].map (slotUnit D)) == some [true, true, true, false]
#guard chainD.map (fun D => ["u1", "u2", "u3", "u4"].map fun u => ok? (coveredOk D u)) ==
  some ["ok", "UnrecordedSlot: u2: [21, 23)", "UnrecordedSlot: u3: [56, 58)", "ok"]
-- a group span is a slot position, wherever its group lists it
def grouped (spans : List String) : Option Bool :=
  chainD.map fun D => slotUnit { D with K := { D.K with groups := [⟨"s", 1, 0, spans⟩] } } "u4"
#guard grouped ["u4", "u9"] == some true
#guard grouped ["u9", "u4"] == some true
#guard grouped ["u9"] == some false

-- `documentSortOk` (shared with `admitCore`): every constant of the document sort is a document name
def docName (n : String) : DocName := ⟨n, [n], .self, 1, none, [], none, none, none⟩
def sortOk (sort : String) (names : List String) : String :=
  match VE.Norms.Wire.decodeNormsEnvironment (baseEnvironment (loaded doc).1) with
  | .ok ne => ok? (documentSortOk ne.rv { emptyManifest with documentSort := sort, documents := names.map docName })
  | .error e => e
#guard sortOk "service" [] == "InvalidInput: document sort service has other constants"
#guard sortOk "person" [] == "InvalidInput: document sort person has other constants"
#guard sortOk "service" ["x"] == "InvalidInput: document sort service has other constants"
#guard sortOk "service" ["web_api"] == "ok"
#guard sortOk "service" ["x", "web_api"] == "ok"
#guard sortOk "service" ["web_api", "x"] == "ok"
#guard sortOk "other" [] == "ok"

-- `encodeComposed` and `composedJson`: the wrapper fields, `inner` verbatim, the case id
def c0 : ChainAdmitted := ⟨.norms, .null, Json.mkObj [("report_id", "r"), ("conditional_on", Json.arr #["a"])], "d", "w",
  Json.arr #[]⟩
#guard (VE.Discourse.Run.encodeComposed "s4" c0).compress == "{\"document_id\":\"d\",\"id\":\"s4\"," ++
  "\"inner\":{\"conditional_on\":[\"a\"],\"report_id\":\"r\"},\"inner_report_id\":\"r\",\"references\":[]," ++
  "\"report_id\":\"w\",\"status\":\"ok\"}"
#guard conditionalOnOf (composedJson c0) == [Json.arr #["a"]]

/-! ## Chain constructs (14.2), cases (14.4) and the pre-order of `conditional_on` -/

def env (vocabulary : String) : Json := Json.mkObj [("vocabulary", (Json.parse vocabulary).toOption.getD .null)]
def payload (units : String) : Json :=
  Json.mkObj [("metadata", (Json.parse s!"\{\"units\": {units}}").toOption.getD .null)]
#guard chainConstructs (env "{\"soft\": {}}") .null
#guard chainConstructs (env "{\"rights\": {}}") .null
#guard chainConstructs (env "{\"predicates\": {\"a\": {}, \"p\": {\"regulated\": {}}}}") .null
#guard chainConstructs (env "{\"predicates\": {\"p\": {\"regulated\": {}}, \"z\": {}}}") .null
#guard !chainConstructs (env "{\"predicates\": {\"p\": {}}}") .null
#guard ["norm", "right", "right_lines", "limitation", "bar", "fence"].all fun k =>
  chainConstructs .null (payload s!"[\{\"id\": \"u\", \"content\": \{\"{k}\": \{}}}]")
#guard chainConstructs .null (payload "[{\"id\": \"u\", \"content\": {\"norm\": {}}}, {\"id\": \"v\"}]")
#guard chainConstructs .null (payload "[{\"id\": \"v\"}, {\"id\": \"u\", \"content\": {\"norm\": {}}}]")
#guard chainConstructs .null (payload "[{\"id\": \"u\", \"parts\": [{\"id\": \"p\", \"content\": {\"right\": {}}}]}]")
#guard !chainConstructs .null (payload "[{\"id\": \"u\", \"content\": {\"ast\": [\"top\"]}}]")
#guard !chainConstructs .null (payload "[{\"id\": \"u\", \"content\": {\"norm\": {}, \"ast\": 1}}]")

-- `contentFree`: every unit's and part's content `null`, `fences` emptied, nothing else touched
#guard contentFree (Json.mkObj [("metadata", (Json.parse "{\"units\": [{\"id\": \"u\", \"content\": 1,
  \"parts\": [{\"id\": \"p\", \"content\": 2}, {\"id\": \"q\", \"content\": 3}]}, {\"id\": \"v\", \"content\": 4}],
  \"format\": \"f\"}").toOption.getD .null), ("fences", Json.mkObj [("u", "t")]), ("source", "s")]) ==
  Json.mkObj [("metadata", (Json.parse "{\"units\": [{\"id\": \"u\", \"content\": null, \"parts\": [{\"id\": \"p\",
  \"content\": null}, {\"id\": \"q\", \"content\": null}]}, {\"id\": \"v\", \"content\": null}], \"format\": \"f\"}").toOption.getD
  .null), ("fences", Json.mkObj []), ("source", "s")]

-- `conditionalOnOf`: every `conditional_on` list, pre-order, keys in order, arrays in order
#guard conditionalOnOf ((Json.parse "{\"a\": {\"conditional_on\": [\"x\"]}, \"b\": [{\"conditional_on\": [\"y\"]},
  {\"conditional_on\": \"z\"}, {\"conditional_on\": [\"u\"]}, {\"conditional_on\": [\"t\"]}], \"conditional_on\": [\"w\", {\"conditional_on\": [\"v\"]}]}").toOption.getD .null) ==
  [Json.arr #[.str "x"], Json.arr #[.str "y"], Json.arr #[.str "u"], Json.arr #[.str "t"], (Json.parse "[\"w\", {\"conditional_on\": [\"v\"]}]").toOption.getD .null,
   Json.arr #[.str "v"]]

-- `usesDiscoursePath` (Run.lean; its lines border the moved `fuelBudget`)
def envCase (ps : List String) (kind : String := "admission") : Json :=
  Json.mkObj [("id", "c"), ("kind", .str kind), ("environment", Json.mkObj [("profiles", toJson ps)])]
#guard VE.Discourse.Run.usesDiscoursePath (envCase ["relational-fol@0", "ve.discourse@1"])
#guard VE.Discourse.Run.usesDiscoursePath (envCase ["ve.discourse@1", "z@0"])
#guard !VE.Discourse.Run.usesDiscoursePath (envCase ["relational-fol@0", "z@0"])
#guard VE.Discourse.Run.usesDiscoursePath (envCase ["relational-fol@0"] "discourse-joint")
#guard VE.Discourse.Run.usesDiscoursePath (caseOf doc)

/-! ## The route entry (14.6, item cmp-s4c) -/

/-- The discourse route's answer to a case of `kind` on `text`, as text. -/
def routeOf (kind text : String) : String :=
  match VE.Discourse.Run.runCase (Json.mkObj [("id", .str "s4"), ("kind", .str kind), ("document", .str text)]) with
  | .ok j => j.compress
  | .error e => "error: " ++ e
/-- Today's discourse admission of the case, as the route encodes it. -/
def todayOf (text : String) : String :=
  match VE.Discourse.Run.loadCase (caseOf text) >>= fun (d, env) => do
      admitDiscourse (← VE.Route.Gate.profilesOf env) env (← baseVocabulary env) d fuelBudget with
  | .ok r => ((VE.Discourse.Run.encodeAdmission "s4" r).toOption.getD .null).compress
  | .error e => "error: " ++ e
def innerOf (kind text : String) : Json := (parsed (routeOf kind text)).getObjValD "inner"
def listed (ps : List String) : String := ", ".intercalate (ps.map fun p => "\"" ++ p ++ "\"")

-- Two checks, each read once by the trust mutants' probe (a check that runs the route reaches every route).
-- `runCase`: S4-27, an `admission` case is `encodeComposed` of the composed admission, the other discourse kinds by
-- name, any other kind as today; off the composed path today's answer (S4-28: no `ve.discourse@1`; S4-3: no chain
-- construct); step 1's chain decoder (`chainEnvironment`), the route `dispatch` chooses, or `dispatchAdmission`'s
-- refusal of a list no chain route reads (S4-16, S4-17)
#guard [(parsed (routeOf "admission" doc)).getObjValD "status" == .str "ok" && innerOf "admission" doc != .null &&
    (parsed (routeOf "admission" doc)).getObjValD "inner_report_id" == (innerOf "admission" doc).getObjValD "report_id",
  ["discourse-joint", "discourse-validity", "discourse-resolve"].all fun k =>
    routeOf k doc == "error: NotImplemented: " ++ k ++ " on the chain",
  routeOf "no-such" doc == "error: UnsupportedProfile: case kind no-such is not available on the discourse route",
  routeOf "admission" (doc (format := "ve-document@1") (profiles := listed ["norms@0", "relational-fol@0"])
    (discourse := "")) ==
    "error: fields do not match: expected [arguments, description], got [arguments, description, regulated]",
  routeOf "admission" (doc (us := "[" ++ u1 ++ "]") (regulated := false) (body := src1)) ==
    todayOf (doc (us := "[" ++ u1 ++ "]") (regulated := false) (body := src1)),
  (innerOf "admission" (doc (profiles := listed ["norms@0", "relational-fol@0", "soft-norms@0", "ve.discourse@1"]))).getObjValD
    "conditional_on" == Json.arr #[],
  (innerOf "admission" (doc (profiles := listed ["norm-defaults@0", "norms@0", "relational-fol@0", "ve.discourse@1"]))).getObjValD
    "admitted" == .bool true,
  routeOf "admission" (doc (profiles := listed ["norms@0", "relational-fol@0", "rights@0", "soft-norms@0", "ve.discourse@1"])) ==
    "error: InvalidInput: invalid rights block",
  routeOf "admission" (doc (profiles := listed ["norms@0", "readings@1", "relational-fol@0", "ve.discourse@1"])) ==
    "error: UnsupportedProfile: ve.discourse@1 with readings@1",
  routeOf "admission" (doc (profiles := listed ["norms@0", "relational-fol@0", "speech-acts@0", "ve.discourse@1"])) ==
    "error: UnsupportedProfile: ve.discourse@1 with speech-acts@0"].all id
-- step 1: on the composed path the envelope checks come first, with today's texts (`admitChain`, the path's body);
-- off it, today's FOL-family check
#guard match VE.Discourse.Run.loadCase (caseOf doc) with
  | .ok (d, env) => (match admitChain ["norms@0", "relational-fol@0", "ve.discourse@1"] (env.setObjVal! "profiles"
      (toJson ["norms@0", "relational-fol@0", "ve.discourse@1", "zz@0"])) d with | .error e => e | .ok _ => "") ==
    "UnsupportedProfile: environment profiles differ from the declared list"
  | .error _ => false
#guard todayOf (doc (profiles := listed ["order@0", "relational-fol@0", "ve.discourse@1"]) (us := "[" ++ u1 ++ "]")
  (regulated := false) (body := src1)) == "error: UnsupportedProfile: discourse admission requires the FOL family"
-- `envelopeChecks` on its own: the environment's profile list must be the declared one
#guard (match runAll (envelopeChecks ["norms@0", "relational-fol@0", "ve.discourse@1"]
    (Json.mkObj [("profiles", toJson ["x@0"])]) .null) with | .error e => e | .ok _ => "") ==
  "UnsupportedProfile: environment profiles differ from the declared list"

-- 14.5 step 3: the chain route's environment id is the one over the base pair's profiles
#guard match VE.Discourse.Run.loadCase (caseOf doc) with
  | .ok (d, env) => (do
      let id ← VE.Route.Wire.environmentId ["norms@0", "relational-fol@0"]
        (← VE.Norms.Wire.canonicalEnvironmentJson (baseEnvironment env))
      pure ((← chainBase env d).2.2 == id)).toOption == some true
  | .error _ => false

end VE.Discourse.ComposeExamples
