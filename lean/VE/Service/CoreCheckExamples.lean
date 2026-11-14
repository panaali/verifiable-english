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

end VE.Service.CoreCheckExamples
