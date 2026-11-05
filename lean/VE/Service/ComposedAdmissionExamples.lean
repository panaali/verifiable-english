import VE.Discourse.ComposeExamples

/-! # The composed admission end to end (docs/spec/discourse.md 14.5, 14.6, 14.8; item cmp-s4)

The documents of `VE.Discourse.ComposeExamples` admitted through `admitComposed`, against today's admission
(`admitDiscourse`) and the document mode (`checkCore`). Each `#guard` names its fixture. -/
namespace VE.Service.ComposedAdmissionExamples
open Lean VE.Discourse VE.Discourse.ComposeExamples

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
-- the norm content reaches the chain route: a guard over a binary predicate is its rejection
#guard (composed (doc (us := units (some ("{\"norm\": {\"name\": \"bad\", \"predicate\": \"review_required\", " ++
  "\"sign\": true, \"guard\": [\"unary\", \"owns\", [\"var\", 0]], \"unless\": [], \"over\": []}}"))))).startsWith "error: "

-- S4-16 and S4-17 at `dispatchAdmission` itself (the list `dispatch` reads, base profiles)
#guard (match dispatchAdmission ["norms@0", "readings@1", "relational-fol@0"] .null .null with
  | .error e => e | .ok _ => "") == "UnsupportedProfile: ve.discourse@1 with readings@1"
#guard (match dispatchAdmission ["norms@0", "relational-fol@0", "speech-acts@0"] .null .null with
  | .error e => e | .ok _ => "") == "UnsupportedProfile: ve.discourse@1 with speech-acts@0"
-- `encodeComposed`: the wrapper with the case id
#guard match VE.Discourse.Run.loadCase (caseOf doc) with
  | .ok (d, env) => match admitComposed ["norms@0", "relational-fol@0", "ve.discourse@1"] env d with
    | .ok (.chain c) => (VE.Discourse.Run.encodeComposed "s4" c).compress ==
        ((composedJson c).setObjVal! "id" (.str "s4") |>.setObjVal! "status" (.str "ok")).compress &&
        (VE.Discourse.Run.encodeComposed "s4" c).getObjValD "id" == .str "s4"
    | _ => false
  | .error _ => false
-- S4-20: a `groups` entry (14.5 step 1, named abstention)
#guard composed (doc (discourse := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": [], \"groups\": [{}]}")) ==
  "error: NotImplemented: groups on the chain"
#guard composed (doc (rest := ", " ++ graph ++ ", \"reading_sets\": [{}]")) ==
  "error: NotImplemented: reading sets on the chain"
#guard composed (doc (discourse := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": [], \"constraints\": [{}]}")) ==
  "error: NotImplemented: constraints on the chain"
#guard composed (doc (discourse := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": [], \"validity\": [{}]}")) ==
  "error: NotImplemented: validity claims on the chain"
-- and empty lists are no abstention
#guard (composed (doc (discourse := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": [], \"groups\": [], \"constraints\": [],
  \"validity\": []}") (rest := ", " ++ graph ++ ", \"reading_sets\": []"))).startsWith "chain "
-- S4-21 (OPEN 2): no claim graph, as today
#guard composed (doc (rest := "")) == "error: NotImplemented: a document without a claim graph"
-- 14.5 step 3: `definitions_version` names the chain route's environment id
#guard composed (doc (discourse := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": [],
  \"definitions_version\": \"x\"}")) == "error: StaleTarget: definitions@x"
-- 14.3 step 6: a recorded formula-producing mention on a JSON content
#guard composed (doc (discourse := mention "u2")) == "error: MentionNotSlot: m1"
#guard composed (doc (us := units (some "{\"right\": {}}")) (discourse := mention "u2")) == "error: MentionNotSlot: m1"
-- item cmp-s4's abstentions: a bound prose unit and a fenced unit (14.3's slot steps are item cmp-s4ab)
#guard composed (doc (discourse := mention "u1")) == "error: NotImplemented: a bound prose unit on the chain"
#guard composed (doc (us := units (some "{\"fence\": \"u2\"}"))) == "error: NotImplemented: fenced content on the chain"
-- review cmp-s4 F7: a body fence no unit binds is never read on the chain, so every entry refuses it by name with
-- the loader's own refusal (`Loader.fencesOk`, `resolveWith`): the composed admission, `caseManifest`, `resolveCase`
def fenceBody : String := src1 ++ src2 ++ "```ve zz\nIt is safe.\n```\n"
#guard (composed (doc (body := fenceBody))).startsWith "error: "
#guard composed (doc (body := fenceBody)) == "error: NotImplemented: fenced English or strict content"
#guard (match caseManifest (caseOf (doc (body := fenceBody))) with | .ok _ => "" | .error e => e) ==
  "NotImplemented: fenced English or strict content"
#guard (match resolveCase (caseOf (doc (body := fenceBody))) with | .ok _ => "" | .error e => e) ==
  "NotImplemented: fenced English or strict content"
#guard (match Loader.fencesOk [("zz", "It is safe.\n")] with | .ok _ => "" | .error e => e) ==
  "NotImplemented: fenced English or strict content"
-- a fence a unit binds keeps that unit's abstention (`contentOk` runs first, as `compileUnits` does in `loadFront`)
#guard composed (doc (us := units (some "{\"fence\": \"zz\"}")) (body := fenceBody)) ==
  "error: NotImplemented: fenced content on the chain"

/-! ## 14.5 step 4: the manifest checks of 4.1 on the composed path (review cmp-s4 F1)

Each mutation is applied to the chain document and to its twin without a chain construct (`u2` an `ast` unit,
no regulated predicate, no `norms@0`), which today's admission reads. The composed path refuses each with today's
diagnostic: the `@1` part's load (4.1(1)), then `wellFormed` (4.1(2) to (8)), the same functions. -/

-- PROBE F1 (review cmp-s4): a gap in the unit spans, and an unrecorded `It` in a norm unit (S4-14's class)
#guard (composed (doc (us := "[" ++ u1 ++ ", " ++ normUnit "u2" 21 51 ++ "]"))).startsWith "error: "
#guard (composed (doc (us := "[" ++ u1 ++ ", " ++ normUnit "u2" 21 56 ++ "]") (body := src1 ++ "It must be reviewed when deployed.\n"))).startsWith "error: "

def astUnit (id : String) (a b : Nat) (support := "assumption") : String :=
  s!"\{\"id\": \"{id}\", \"span\": [{a}, {b}], \"kind\": \"asserted\", \"meaning\": \"specified\", \"support\": \"{support}\", " ++
  "\"content\": {\"ast\": [\"unary\", \"deployed\", [\"const\", \"web_api\"]]}}"

/-- A mutation of the parts both documents share. -/
structure Mutation where
  u1 : String := u1
  stop : Nat := (src1 ++ src2).utf8ByteSize
  body : String := src1 ++ src2
  discourse : String := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": []}"
  rest : String := ", " ++ graph

def chainOf (m : Mutation) : String :=
  doc (us := "[" ++ m.u1 ++ ", " ++ normUnit "u2" 21 m.stop ++ "]") (body := m.body) (discourse := m.discourse)
    (rest := m.rest)
def twinOf (m : Mutation) : String :=
  doc (profiles := "\"relational-fol@0\", \"ve.discourse@1\"") (regulated := false)
    (us := "[" ++ m.u1 ++ ", " ++ astUnit "u2" 21 m.stop ++ "]") (body := m.body) (discourse := m.discourse)
    (rest := m.rest)
def block (entries : String) : String := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": []" ++ entries ++ "}"
def navigations (n : Nat) : String :=
  ", \"mentions\": [" ++ ", ".intercalate ((List.range n).map fun i => s!"\{\"id\": \"m{i}\", \"unit\": \"u1\", " ++
    "\"span\": [0, 3], \"form\": \"navigation\", \"target\": {\"kind\": \"unit\", \"units\": [\"u2\"]}}") ++ "]"
def itBody : String := src1 ++ "It must be reviewed when deployed.\n"

/-- Each mutation and today's diagnostic of it. -/
def mutations : List (Mutation × String) := [
  ({ stop := 51 }, "unit spans do not partition all source bytes"),
  ({ u1 := astUnit "u1" 0 21 "bogus" }, "invalid support"),
  ({ u1 := "{\"id\": \"u1\", \"span\": [0, 21], \"kind\": \"asserted\", \"meaning\": \"specified\", \"support\": \"assumption\", " ++
      "\"meaning_id\": \"x\", \"content\": {\"ast\": [\"unary\", \"deployed\", [\"const\", \"web_api\"]]}}" },
    "unit meaning id does not match content"),
  ({ rest := ", " ++ graph ++ ", \"narrowings\": [{\"id\": \"n1\", \"set\": \"s\", \"version\": 1, \"keeps\": [\"a\"], " ++
      "\"by\": \"r\", \"reason_spans\": [\"u1\"]}]" }, "narrowing cites unknown reading set version"),
  ({ discourse := block (", \"mentions\": [{\"id\": \"m1\", \"unit\": \"u9\", \"span\": [0, 3], \"form\": \"pronoun\", " ++
      "\"target\": {\"kind\": \"entity\", \"name\": \"nobody\"}}]") }, "InvalidInput: mention m1 names an unknown unit"),
  ({ discourse := ", \"discourse\": {\"version\": \"ve.discourse@1\", \"anchors\": [{\"id\": \"a\", \"kind\": \"section\", " ++
      "\"label\": \"A\", \"span\": [0, 30]}, {\"id\": \"b\", \"kind\": \"section\", \"label\": \"B\", \"span\": [10, 50]}]}" },
    "InvalidInput: anchors must form one tree"),
  ({ discourse := block ", \"names\": [{\"constant\": \"nobody\", \"display\": \"Nobody\", \"scope\": \"root\"}]" },
    "InvalidInput: name nobody is not a declared constant"),
  ({ discourse := block (navigations 4097) }, "ResourceLimit: mentions"),
  ({ discourse := block (navigations 2) }, "InvalidInput: mentions m0, m1 overlap"),
  ({ stop := 56, body := itBody }, "UnrecordedSlot: u2: [21, 23)"),
  ({ body := "It is deployed here.\n" ++ src2 }, "UnrecordedSlot: u1: [0, 2)"),
  ({ stop := 56, body := itBody, discourse := block (", \"mentions\": [{\"id\": \"m1\", \"unit\": \"u2\", \"span\": [21, 23], " ++
      "\"form\": \"pronoun\", \"target\": {\"kind\": \"unit\", \"units\": [\"u1\"]}}]") }, "TargetKindMismatch: m1: pronoun, unit"),
  ({ discourse := block ", \"self_truth\": [\"u1\"]" }, "InvalidInput: self-truth unit u1"),
  ({ discourse := block ", \"document_sort\": \"service\"" }, "InvalidInput: document sort service has other constants")]

-- the unmutated pair is admitted on both paths, so each refusal below is the mutation's
#guard (composed (chainOf {})).startsWith "chain "
#guard (today (twinOf {})).startsWith "today "
-- each mutation: today's diagnostic on the twin, the same on the composed path
#guard mutations.all fun (m, e) => today (twinOf m) == "error: " ++ e
#guard mutations.all fun (m, e) => composed (chainOf m) == "error: " ++ e
-- one navigation mention is no fault: a recorded location binding passes the checks on both paths
#guard (composed (chainOf { discourse := block (navigations 1) })).startsWith "chain "
#guard (today (twinOf { discourse := block (navigations 1) })).startsWith "today "
-- `caseManifest` hands out a manifest only after the same checks
#guard ((caseManifest (caseOf (chainOf { discourse := block (navigations 1) }))).toOption.map (·.2.mentions.map (·.id))) ==
  some ["m0"]
#guard mutations.all fun (m, e) => match caseManifest (caseOf (chainOf m)) with
  | .error e' => e' == e
  | .ok _ => false
#guard (match caseManifest (caseOf (doc (discourse := mention "u2"))) with
  | .error e => e | .ok _ => "") == "MentionNotSlot: m1"

/-! ## Identity cases (14.6): today's answer, byte for byte -/

def alpha (profiles : String) : String :=
  doc (profiles := profiles) (us := "[" ++ u1 ++ "]") (regulated := false)
    (body := src1)

-- S4-3: α with `norms@0`, no chain construct
#guard (composed (alpha "\"norms@0\", \"relational-fol@0\", \"ve.discourse@1\"")).startsWith "today "
#guard composed (alpha "\"norms@0\", \"relational-fol@0\", \"ve.discourse@1\"") ==
  today (alpha "\"norms@0\", \"relational-fol@0\", \"ve.discourse@1\"")
-- S4-2 (α): today's answer
#guard composed (alpha "\"relational-fol@0\", \"ve.discourse@1\"") == today (alpha "\"relational-fol@0\", \"ve.discourse@1\"")
-- S4-28: a `ve-document@1` text on `norms@0, relational-fol@0` with a norm unit is not the composed path
def s428 : String := doc (profiles := "\"norms@0\", \"relational-fol@0\"") (format := "ve-document@1") (discourse := "")
#guard !(composed s428).startsWith "chain "
#guard composed s428 == today s428
-- S4-25: no `norms@0`, a vocabulary `baseVocabulary` rejects: today's error
def s425 : String := doc (profiles := "\"relational-fol@0\", \"ve.discourse@1\"")
#guard (composed s425).startsWith "error: "
#guard composed s425 == today s425

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
#guard (caseShape resolved).getObjValD "id" == .str "s4"
#guard ((VE.Service.Document.checkCore resolved).toOption.map Json.compress) ==
  ((VE.Service.Document.checkCore (caseOf (doc (profiles := "\"norms@0\", \"relational-fol@0\"")
    (format := "ve-document@1") (discourse := "")))).toOption.map Json.compress)
#guard ((VE.Service.Document.checkCore resolved).toOption.map (·.getObjValD "status")) == some (.str "ok")
-- S4-23: a case without `ve.discourse@1` is returned as it is
#guard (resolveCase (caseOf s428)).toOption.map Json.compress == some (caseOf s428).compress

end VE.Service.ComposedAdmissionExamples
