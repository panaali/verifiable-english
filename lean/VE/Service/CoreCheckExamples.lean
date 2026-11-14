import VE.Service.CoreCheck

/-! Examples of the document mode's core path (`VE.Service.CoreCheck`, kb-2a-b) on one small document and one-edit
variations of it: a heading (LABELLED), a fact (CHECKED), a soft default rule (CHECKED), a unit whose reading set has
one rule and one pending reading (OPEN: the set is open), and a rule reading the judgment term `t` (OPEN). Each
`#guard` runs the mode's entry, `runCaseReported`, as the service does. -/
namespace VE.Service.CoreCheckExamples
open Lean

def front : String := r#"{"format":"ve-document@1","environment":{"language":"ve.core@0.2","profiles":["documents@1","judgments@0","norms@0","readings@1","relational-fol@0","soft-norms@0"],"spec_revision":"ve-v0.2-expand2-2026-09-25","vocabulary":{"sorts":{"assistant":{"description":"assistant"},"user":{"description":"user"}},"predicates":{"x_required":{"arguments":["assistant"],"description":"obligation","regulated":{"role":"obligation","default":"deny","act":"{0} do x","permission":"x_permitted"}},"x_permitted":{"arguments":["assistant"],"description":"permission","regulated":{"role":"permission","default":"allow","act":"{0} do x"}},"v":{"arguments":["assistant"],"description":"v"},"w":{"arguments":["assistant"],"description":"w"},"q":{"arguments":["assistant"],"description":"q"},"t":{"arguments":["assistant"],"description":"a judgment"}},"constants":{}}},"units":[{"id":"u1","span":[0,7],"kind":"meta","meaning":"specified","support":"none"},{"id":"u2","span":[7,13],"kind":"asserted","meaning":"specified","support":"testimony","content":{"ast":["forall","assistant",["implies",["unary","v",["var",0]],["unary","q",["var",0]]]]}},{"id":"u3","span":[13,19],"kind":"norm","meaning":"specified","support":"testimony","content":{"norm":{"name":"h","predicate":"x_required","sign":true,"guard":["unary","v",["var",0]],"unless":[],"over":[],"mode":"default","exception":{"decided_by":"unstated","sufficient":[],"necessary":[],"factors":[]}}}},{"id":"u4","span":[19,24],"kind":"norm","meaning":"specified","support":"testimony"},{"id":"u5","span":[24,32],"kind":"norm","meaning":{"open":["t"]},"support":"testimony","content":{"norm":{"name":"g","predicate":"x_required","sign":true,"guard":["unary","t",["var",0]],"unless":[],"over":[]}}}],"open_terms":[{"name":"t","arguments":["assistant"],"decided_by":"unstated","necessary":[],"sufficient":[],"factors":[],"precedents":[],"jurisdiction":"document","version":1}],"reading_sets":[{"id":"s","unit":"u4","version":1,"status":"open","readings":[{"id":"r0","kind":"norm","content":{"norm":{"name":"k","predicate":"x_required","sign":false,"guard":["unary","w",["var",0]],"unless":[],"over":[]}},"meaning_id":"4ef8cd134059e2f9495881099123d3ccf16eed3f6556dbfe383e1448cf24e905","admission":{"who":"translator","why":"r0","distinguishing_models":{}}},{"id":"r1","kind":"norm","meaning_id":"pending","content":null,"admission":{"who":"translator","why":"r1","distinguishing_models":{}}}]}]}"#

/-- The document with its rule reading made pending too, with no distinguishing ids: W2's refusal, before any lowering
(the lowering's `ReadingsCollapsed` is checked on the acceptance document, tests/test_kb2a_document.py). -/
def collapsed : String := r#"{"format":"ve-document@1","environment":{"language":"ve.core@0.2","profiles":["documents@1","judgments@0","norms@0","readings@1","relational-fol@0","soft-norms@0"],"spec_revision":"ve-v0.2-expand2-2026-09-25","vocabulary":{"sorts":{"assistant":{"description":"assistant"},"user":{"description":"user"}},"predicates":{"x_required":{"arguments":["assistant"],"description":"obligation","regulated":{"role":"obligation","default":"deny","act":"{0} do x","permission":"x_permitted"}},"x_permitted":{"arguments":["assistant"],"description":"permission","regulated":{"role":"permission","default":"allow","act":"{0} do x"}},"v":{"arguments":["assistant"],"description":"v"},"w":{"arguments":["assistant"],"description":"w"},"q":{"arguments":["assistant"],"description":"q"},"t":{"arguments":["assistant"],"description":"a judgment"}},"constants":{}}},"units":[{"id":"u1","span":[0,7],"kind":"meta","meaning":"specified","support":"none"},{"id":"u2","span":[7,13],"kind":"asserted","meaning":"specified","support":"testimony","content":{"ast":["forall","assistant",["implies",["unary","v",["var",0]],["unary","q",["var",0]]]]}},{"id":"u3","span":[13,19],"kind":"norm","meaning":"specified","support":"testimony","content":{"norm":{"name":"h","predicate":"x_required","sign":true,"guard":["unary","v",["var",0]],"unless":[],"over":[],"mode":"default","exception":{"decided_by":"unstated","sufficient":[],"necessary":[],"factors":[]}}}},{"id":"u4","span":[19,24],"kind":"norm","meaning":"specified","support":"testimony"},{"id":"u5","span":[24,32],"kind":"norm","meaning":{"open":["t"]},"support":"testimony","content":{"norm":{"name":"g","predicate":"x_required","sign":true,"guard":["unary","t",["var",0]],"unless":[],"over":[]}}}],"open_terms":[{"name":"t","arguments":["assistant"],"decided_by":"unstated","necessary":[],"sufficient":[],"factors":[],"precedents":[],"jurisdiction":"document","version":1}],"reading_sets":[{"id":"s","unit":"u4","version":1,"status":"open","readings":[{"id":"r0","kind":"norm","content":null,"meaning_id":"pending","admission":{"who":"translator","why":"r0","distinguishing_models":{}}},{"id":"r1","kind":"norm","meaning_id":"pending","content":null,"admission":{"who":"translator","why":"r1","distinguishing_models":{}}}]}]}"#

def body : String := "Title.\nFact.\nRule.\nSet.\nJudged.\n"

def run (f : String) : Json :=
  VE.Service.CoreCheck.runCaseReported (Json.mkObj [("id", .str "d"), ("document", .str ("---\n" ++ f ++ "\n---\n" ++ body)),
    ("admit", .bool true)])

def arr (j : Json) : List Json := (j.getArr?.toOption.map (·.toList)).getD []

/-- Each unit's id and status. -/
def statuses (a : Json) : List (String × String) :=
  (arr ((a.getObjValD "view").getObjValD "units")).map fun u =>
    ((u.getObjValD "id").getStr?.toOption.getD "", (u.getObjValD "status").getStr?.toOption.getD "")

/-- Each unit's statements, per choice, as feature and reading index. -/
def statements (a : Json) : List (String × List (List (String × Option Nat))) :=
  (arr ((a.getObjValD "view").getObjValD "statements")).map fun e =>
    ((e.getObjValD "id").getStr?.toOption.getD "", (arr (e.getObjValD "choices")).map fun c => (arr c).map fun s =>
      ((s.getObjValD "feature").getStr?.toOption.getD "", ((s.getObjValD "reading").getObjValD "index").getNat?.toOption))

/-- Each row's case id, kind and counts, and the kernel's answer. -/
def rows (a : Json) : List (String × Nat × Nat × Json) :=
  (arr (a.getObjValD "rows")).map fun r =>
    ((r.getObjValD "case").getObjValD "id" |>.getStr?.toOption.getD "", (arr ((r.getObjValD "case").getObjValD "norms")).length,
      (arr ((r.getObjValD "case").getObjValD "facts")).length, r.getObjValD "answer")

/-- A refusal and its `lowering` mark. -/
def refusal (a : Json) : String × Json := ((a.getObjValD "error").getStr?.toOption.getD "", a.getObjValD "lowering")

def edit (old new : String) : String := front.replace old new

-- The document: answered on the core path, statuses from the fold.
#guard statuses (run front) ==
  [("u1", "LABELLED"), ("u2", "CHECKED"), ("u3", "CHECKED"), ("u4", "OPEN"), ("u5", "OPEN")]
-- One kernel row per choice of the set (r0, then the pending r1), each the soft route's admission of its case.
#guard rows (run front) ==
  [("choice-0", 3, 1, Json.mkObj [("facts", toJson (1 : Nat)), ("id", .str "choice-0"), ("rules", toJson (3 : Nat)),
     ("status", .str "ok")]),
   ("choice-1", 2, 1, Json.mkObj [("facts", toJson (1 : Nat)), ("id", .str "choice-1"), ("rules", toJson (2 : Nat)),
     ("status", .str "ok")])]
-- Each unit's core statements per choice with their origins: u4's rule only under r0, u5's judgment declaration first.
#guard statements (run front) ==
  [("u2", [[("facts", none)], [("facts", none)]]),
   ("u3", [[("soft-norms@0", none)], [("soft-norms@0", none)]]),
   ("u4", [[("norms@0", some 0)], []]),
   ("u5", [[("judgments@0", none), ("soft-norms@0", none)], [("judgments@0", none), ("soft-norms@0", none)]])]
#guard (run front).getObjValD "status" == .str "ok" && (run front).getObjValD "lowering" == .null
-- A soft rule whose exception reads the judgment term reads it: u3 is OPEN.
#guard (statuses (run (edit "\"sufficient\":[],\"necessary\":[]" "\"sufficient\":[[\"unary\",\"t\",[\"var\",0]]],\"necessary\":[]"))).lookup "u3" == some "OPEN"
-- A refusal of the decoding before the lowering is Lean's, marked; a set naming a unit the document lacks is UnknownPart.
#guard refusal (run collapsed) == ("each other reading needs a distinguishing model id", .bool true)
#guard refusal (run (edit "\"unit\":\"u4\"" "\"unit\":\"u9\"")) ==
  ("UnknownPart: reading set s names unit u9, which the document does not have", .bool true)
-- An authored status that is not the fold's.
#guard refusal (run (edit "\"support\":\"testimony\",\"content\":{\"ast\"" "\"support\":\"testimony\",\"status\":\"OPEN\",\"content\":{\"ast\"")) ==
  ("unit status contradicts content, meaning, or active reading set", .bool true)
-- A soft source the soft route rejects: Lean's refusal, marked, whatever its code.
#guard (refusal (run (edit "\"name\":\"h\"" "\"name\":\"h\",\"rank\":\"nowhere\""))).2 == .bool true
-- A feature with no lowering row (couplings): today's refusal, unmarked.
#guard refusal (run (edit "\"format\":\"ve-document@1\"" "\"format\":\"ve-document@1\",\"couplings\":[]")) ==
  ("CheckerUnavailable: soft-norms with readings, alternatives or risk needs its composed Lean route", .null)
-- Not routed: a profile outside the lowering's rows (norm-defaults@0) keeps today's path and text.
#guard (refusal (run (edit "\"judgments@0\",\"norms@0\"" "\"judgments@0\",\"norm-defaults@0\",\"norms@0\""))).2 == .null
#guard !VE.Service.CoreCheck.routed (Json.mkObj [("id", .str "d"), ("document", .str ("---\n" ++
  (edit "\"judgments@0\",\"norms@0\"" "\"judgments@0\",\"norm-defaults@0\",\"norms@0\"") ++ "\n---\n" ++ body))])
#guard VE.Service.CoreCheck.routed (Json.mkObj [("id", .str "d"), ("document", .str ("---\n" ++ front ++ "\n---\n" ++ body))])

/-! ## The shell's pieces, one by one -/

section pieces
open VE.Service.CoreCheck
open VE.Service.CoreDocument (CoreDoc Statement)

/-- An answer of `casesOf`, as text. -/
def casesText : Except String (List Json) → String
  | .ok l => (Json.arr l.toArray).compress
  | .error e => "error: " ++ e

/-- The cases' environment: the document's, without `judgments@0` and `readings@1`. -/
def env : Json := (((Json.parse front).toOption.getD .null).getObjValD "environment").setObjVal! "profiles"
  (toJson ["documents@1", "norms@0", "relational-fol@0", "soft-norms@0"])
def ruleH : Json := ((((((Json.parse front).toOption.getD .null).getObjValD "units").getArr?.toOption.getD #[]).toList.getD 2
  .null).getObjValD "content")

def x : VE.Term := .var 0
def fact : VE.Formula := .all "assistant" (.implies (.unary "v" x) (.unary "q" x))
def illTyped : VE.Formula := .all "assistant" (.unary "nosuch" x)
def deep : VE.Formula := (List.replicate 64 ()).foldl (fun f _ => .not f) .top
def decision : VE.Formula := .all "assistant" (.unary "soft__excepted__h" x)
def core (P : List VE.Formula) (norms : List Json := []) : CoreDoc := ⟨env, Json.arr norms.toArray, P, []⟩
def src (norms : List Json := []) : Option VE.SoftNorms.Wire.SoftSource :=
  (VE.SoftNorms.Wire.decodeSoftSource env (Json.arr norms.toArray)).toOption

-- The premises as the route's encoder writes them, and the case of a choice.
#guard factsJson [] == Json.arr #[] && factsJson [fact] == Json.arr #[VE.Route.Wire.encodeFormula fact]
#guard caseOf 3 (core [fact] [ruleH]) == Json.mkObj [("id", .str "choice-3"), ("kind", .str "slot-admission"),
  ("environment", env), ("norms", Json.arr #[ruleH]), ("facts", factsJson [fact])]
-- The round trip's gates: typing, depth (the decoder's bound exactly), and no soft decision predicate.
#guard (src).any fun s => roundTrips s [] && roundTrips s [fact] && !roundTrips s [illTyped] && !roundTrips s [deep] &&
  !roundTrips s [fact, illTyped]
#guard (src [ruleH]).any fun s => roundTrips s [fact] && !roundTrips s [decision]
#guard (src).any fun s => roundTrips s [(List.replicate 63 ()).foldl (fun f _ => .not f) .top]
-- A premise that would not read back is refused with the decoder's own diagnostic; a source the soft decoder refuses is
-- the kernel's to refuse.
#guard caseFault (core [fact]) == none && caseFault (core [illTyped]) == some "ill-typed or unbound formula"
#guard (caseFault (core [decision] [ruleH])).any (·.startsWith "InvalidInput: facts: soft__excepted__h")
#guard caseFault ⟨.null, Json.arr #[], [illTyped], []⟩ == none
#guard (src).any fun s => factsRefusal s [illTyped] == "ill-typed or unbound formula"
-- One case per core document, in order; the first refusal names its choice.
#guard casesText (casesOf [([], core [fact]), ([("s", 1)], core [] [ruleH])]) ==
  (Json.arr #[caseOf 0 (core [fact]), caseOf 1 (core [] [ruleH])]).compress
#guard casesText (casesOf [([], core [fact]), ([], core [illTyped])]) ==
  "error: ill-typed or unbound formula (core document of choice 1)"
#guard casesText (casesOf []) == "[]"
-- The first refused row and its choice.
#guard firstRefused [⟨.null, .ok .null⟩, ⟨.null, .error "e"⟩, ⟨.null, .error "f"⟩] 0 == some (1, "e")
#guard firstRefused [⟨.null, .ok .null⟩] 0 == none && firstRefused [⟨.null, .error "e"⟩] 4 == some (4, "e")
#guard VE.Service.CoreCheck.refusal [([("s", 1)], core [])] 0 "e" == "e (core document of choice 0: [s reading 1])"
#guard VE.Service.CoreCheck.refusal [] 2 "e" == "e (core document of choice 2: [])"
-- A refusal of the lowering's table, and nothing else, sends a document back to today's path.
#guard noRow "UnsupportedLowering: unit u feature couplings: the table has no row for it" && !noRow "UnknownPart: x" &&
  !noRow "UnsupportedLoweringx" && !noRow "CheckerUnavailable: UnsupportedLowering: x"
#guard routedRefusals == ["CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean route",
  "CheckerUnavailable: soft-norms with readings, alternatives or risk needs its composed Lean route"]
-- The fold's statuses as the answer names them.
#guard [VE.Kernel.DocumentFold.Status.checked, .opened, .labelled, .unformalised].map (fun s => (unitStatus s).name) ==
  ["CHECKED", "OPEN", "LABELLED", "UNFORMALISED"]
-- A statement as the view writes it: its feature, its reading, its body.
#guard statementJson ⟨.premise fact, ⟨"u", "facts", none⟩⟩ ==
  Json.mkObj [("feature", .str "facts"), ("premise", VE.Route.Wire.encodeFormula fact)]
#guard statementJson ⟨.soft ruleH, ⟨"u", "norms@0", some ("s", 2)⟩⟩ == Json.mkObj [("feature", .str "norms@0"),
  ("reading", Json.mkObj [("set", .str "s"), ("index", toJson (2 : Nat))]), ("rule", ruleH)]
#guard choicesJson [([("s", 0), ("r", 1)], core [])] == Json.arr #[Json.arr #[
  Json.mkObj [("set", .str "s"), ("reading", toJson (0 : Nat))], Json.mkObj [("set", .str "r"), ("reading", toJson (1 : Nat))]]]
-- A soft rule's exception conditions, read for the fold's judgment condition; none for any other content.
#guard exceptionFormulas none (some (.soft ruleH)) == []
#guard exceptionFormulas none none == []

end pieces

-- The view's coverage counts each unit's bytes under the fold's status.
#guard ((run front).getObjValD "view" |>.getObjValD "coverage" |>.getObjValD "bytes_by_status") ==
  Json.mkObj [("CHECKED", toJson (12 : Nat)), ("LABELLED", toJson (7 : Nat)), ("OPEN", toJson (13 : Nat))]
-- An asserted unit with neither content nor a reading set: W2's refusal, Lean's, marked.
#guard refusal (run (edit "\"kind\":\"meta\"" "\"kind\":\"asserted\"")) ==
  ("asserted unit needs content or a reading set", .bool true)
-- Senses are no row of the lowering: not routed.
#guard !VE.Service.CoreCheck.routed (Json.mkObj [("id", .str "d"), ("document", .str ("---\n" ++
  (edit "\"format\":\"ve-document@1\"" "\"format\":\"ve-document@1\",\"senses\":{}") ++ "\n---\n" ++ body))])
-- A document no refusal stops (no readings@1, no exception condition): not routed.
#guard !VE.Service.CoreCheck.routed (Json.mkObj [("id", .str "d"), ("document", .str ("---\n" ++
  (edit "\"readings@1\"," "") ++ "\n---\n" ++ body))])

/-! ## More units: a second reading set, authored sets, a last unit whose fold status is not its own -/

section more
open VE.Service.CoreCheck

def frontJ : Json := (Json.parse front).toOption.getD .null
def unitsJ : List Json := ((frontJ.getObjValD "units").getArr?.toOption.map (·.toList)).getD []
def setsJ : List Json := ((frontJ.getObjValD "reading_sets").getArr?.toOption.map (·.toList)).getD []

/-- The document mode's environment of `front` (the core path's decoding), for the identities the sets name. -/
def envE : Option VE.Service.Document.Env :=
  (VE.Service.Document.environmentOf (frontJ.getObjValD "environment") (frontJ.getObjValD "units") false none true).toOption
def ast (f : VE.Formula) : Json := VE.Route.Wire.encodeFormula f
def mid (f : VE.Formula) : String :=
  (envE.bind fun E => (VE.Route.Wire.meaningId E.profiles E.envId (ast f)).toOption).getD ""
def qAll : VE.Formula := .all "assistant" (.unary "q" (.var 0))
def notQ : VE.Formula := .all "assistant" (.not (.unary "q" (.var 0)))
def tAll : VE.Formula := .all "assistant" (.unary "t" (.var 0))
def modelData : Json := (Json.parse r#"{"complete": true, "domains": {"assistant": ["a"], "user": []}, "constants": {}, "relations": {"v": [], "w": [], "q": [["a"]], "t": [], "x_required": [], "x_permitted": []}}"#).toOption.getD .null
def modelName : String :=
  (envE.bind fun E => (VE.Discourse.Loader.modelId E.profiles E.envId modelData).toOption).getD ""
def admission (others : List String) : Json :=
  Json.mkObj [("who", .str "translator"), ("why", .str "r"),
    ("distinguishing_models", Json.mkObj (others.map fun o => (o, .str modelName)))]
def asserted (id : String) (f : VE.Formula) (others : List String) : Json :=
  Json.mkObj [("id", .str id), ("kind", .str "asserted"), ("meaning_id", .str (mid f)), ("content", ast f),
    ("admission", admission others)]
def unitJ (id : String) (a b : Nat) (kind meaning : Json) (content : Option Json) : Json :=
  Json.mkObj ([("id", .str id), ("span", toJson [a, b]), ("kind", kind), ("meaning", meaning),
    ("support", .str "testimony")] ++ (content.map ("content", ·)).toList)
def softM : Json := (Json.parse r#"{"norm": {"name": "m", "predicate": "x_required", "sign": true, "guard": ["unary", "w", ["var", 0]], "unless": [], "over": [], "mode": "default", "exception": {"decided_by": "unstated", "sufficient": [["unary", "v", ["var", 0]], ["unary", "t", ["var", 0]]], "necessary": [], "factors": []}}}"#).toOption.getD .null

/-- `front` with two units more: u6, asserted, its open set s2 of two asserted readings (q, not q) told apart by one
model; u7 last, a soft rule whose exception's second sufficient condition reads the judgment term. -/
def richBody : String := body ++ "Asserted.\nLast.\n"
def rich : String :=
  let n := body.utf8ByteSize
  let units := unitsJ ++ [unitJ "u6" n (n + 10) (.str "asserted") (.str "specified") none,
    unitJ "u7" (n + 10) (n + 16) (.str "norm") (.str "specified") (some softM)]
  let s2 := Json.mkObj [("id", .str "s2"), ("unit", .str "u6"), ("version", toJson (1 : Nat)), ("status", .str "open"),
    ("readings", Json.arr #[asserted "a" qAll ["b"], asserted "b" notQ ["a"]]),
    ("models", Json.mkObj [(modelName, modelData)])]
  ((frontJ.setObjVal! "units" (Json.arr units.toArray)).setObjVal! "reading_sets" (Json.arr (setsJ ++ [s2]).toArray)).compress
def runRich : Json := VE.Service.CoreCheck.runCaseReported (Json.mkObj [("id", .str "d"),
  ("document", .str ("---\n" ++ rich ++ "\n---\n" ++ richBody)), ("admit", .bool true)])

-- Two sets, four choices, one row each; u6 is OPEN (its set is open though both readings are asserted); u7, the last
-- unit, is OPEN by its exception's second condition though its own status is CHECKED.
#guard statuses runRich == [("u1", "LABELLED"), ("u2", "CHECKED"), ("u3", "CHECKED"), ("u4", "OPEN"), ("u5", "OPEN"),
  ("u6", "OPEN"), ("u7", "OPEN")]
#guard (rows runRich).map (·.1) == ["choice-0", "choice-1", "choice-2", "choice-3"]
#guard (rows runRich).map (fun r => (r.2.1, r.2.2.1)) == [(4, 2), (4, 2), (3, 2), (3, 2)]
#guard (statements runRich).lookup "u6" == some [[("facts", some 0)], [("facts", some 1)], [("facts", some 0)], [("facts", some 1)]]
-- The judgment lines name the term the document's units read.
#guard ((runRich.getObjValD "view").getObjValD "judgment_lines").getObjValD "legend" != Json.arr #[]

/-- `front` with u4's set authored: one signed reading. -/
def authoredWith (meaning : Json) (reading : Json) : String :=
  let units := unitsJ.map fun u => if u.getObjValD "id" == .str "u4" then u.setObjVal! "meaning" meaning else u
  let s := ((setsJ.head?.getD .null).setObjVal! "status" (.str "authored")).setObjVal! "signature" (.str "translator")
    |>.setObjVal! "readings" (Json.arr #[reading])
  ((frontJ.setObjVal! "units" (Json.arr units.toArray)).setObjVal! "reading_sets" (Json.arr #[s])).compress

-- An authored set of one rule reading (not asserted): OPEN.
#guard (statuses (run (authoredWith (.str "specified")
  ((((setsJ.head?.getD .null).getObjValD "readings").getArr?.toOption.getD #[]).toList.headD .null)))).lookup "u4" ==
  some "OPEN"
-- An authored set of one asserted reading decides its unit: CHECKED, or OPEN when the reading reads a judgment term.
#guard (statuses (run (authoredWith (.str "specified") (asserted "r0" qAll [])))).lookup "u4" == some "CHECKED"
#guard (statuses (run (authoredWith (Json.mkObj [("open", toJson ["t"])]) (asserted "r0" tAll [])))).lookup "u4" ==
  some "OPEN"

-- The shell's pieces at their boundaries: several facts, the base level, the node limit (each `top` one node).
#guard factsJson [qAll, notQ] == Json.arr #[ast qAll, ast notQ]
#guard VE.Bridge.formulaNodes .top == 1
#guard (src).any fun s => !roundTrips s [fact, deep] && !roundTrips s [fact, fact, illTyped] &&
  !roundTrips s [.all "assistant" (.unary "x_required" (.var 0))]
#guard (src).any fun s => roundTrips s (List.replicate 10000 .top) && !roundTrips s (List.replicate 10001 .top)
-- A soft rule's exception conditions, every one, sufficient then necessary.
def se : Option VE.SoftNorms.Wire.SoftEnvironment := (src).map (·.se)
def softN : Json := (Json.parse r#"{"norm": {"name": "n", "predicate": "x_required", "sign": true, "guard": ["top"], "unless": [], "over": [], "mode": "default", "exception": {"decided_by": "unstated", "sufficient": [["unary", "v", ["var", 0]], ["unary", "w", ["var", 0]]], "necessary": [["unary", "q", ["var", 0]]], "factors": []}}}"#).toOption.getD .null
#guard exceptionFormulas se (some (.soft softN)) ==
  [.unary "v" (.var 0), .unary "w" (.var 0), .unary "q" (.var 0)]
#guard exceptionFormulas se (some (.soft ruleH)) == [] && exceptionFormulas se (some (.formula fact)) == []
-- Every profile is read, the last one too: a profile with no row anywhere in the list is not routed.
#guard !routed (Json.mkObj [("id", .str "d"), ("document", .str ("---\n" ++ (frontJ.setObjVal! "environment"
  ((frontJ.getObjValD "environment").setObjVal! "profiles" (toJson ["documents@1", "judgments@0", "norms@0",
    "readings@1", "relational-fol@0", "soft-norms@0", "norm-defaults@0"]))).compress ++ "\n---\n" ++ body))])
-- environmentOf's two routed refusals, each only where it applies, read with every argument given.
def envWith (ps : List String) : Json := (frontJ.getObjValD "environment").setObjVal! "profiles" (toJson ps)
#guard (VE.Service.Document.environmentOf (envWith ["documents@1", "norms@0", "relational-fol@0", "soft-norms@0"])
  (frontJ.getObjValD "units") false none false).toOption.isSome
#guard (VE.Service.Document.environmentOf (envWith ["documents@1", "norms@0", "readings@1", "relational-fol@0",
  "soft-norms@0"]) (frontJ.getObjValD "units") false none false).toOption.isNone
#guard (VE.Service.Document.environmentOf (envWith ["documents@1", "norms@0", "readings@1", "relational-fol@0",
  "soft-norms@0"]) (frontJ.getObjValD "units") false none true).toOption.isSome
-- No front matter: not routed; today's answer.
#guard !routed (Json.mkObj [("id", .str "d"), ("document", .str "no front matter")])
-- `check` admits a claim graph unless asked not to (`withGraph`); a graph rooted nowhere is refused.
def plainGraph : String :=
  ((frontJ.setObjVal! "environment" ((frontJ.getObjValD "environment").setObjVal! "profiles"
    (toJson ["documents@1", "norms@0", "relational-fol@0", "soft-norms@0"]))).setObjVal! "units"
    (Json.arr (unitsJ.map fun u => if u.getObjValD "id" == .str "u5" then u.setObjVal! "meaning" (.str "specified") else u).toArray)
    |>.setObjVal! "reading_sets" (Json.arr #[]) |>.setObjVal! "open_terms" (Json.arr #[])
    |>.setObjVal! "graph" (Json.mkObj [("root", .str "nowhere"), ("nodes", Json.arr #[])])).compress
#guard (VE.Service.Document.check ("---\n" ++ plainGraph ++ "\n---\n" ++ body)).toOption.isNone &&
  (VE.Service.Document.check ("---\n" ++ plainGraph ++ "\n---\n" ++ body) (withGraph := false)).toOption.isSome

end more

end VE.Service.CoreCheckExamples
