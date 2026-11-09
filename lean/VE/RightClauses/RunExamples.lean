import VE.RightClauses.Run

/-! `clauses-elaborate` on spec 9.1's documents as `#guard`s (the service tests' fixtures, tests/test_right_clauses.py):
9.1's environment, right `r21` with the claim line `equal-access`, unit span [0, 100). -/
namespace VE.RightClauses.RunExamples
open Lean VE.RightClauses VE.RightClauses.Run

def parse (s : String) : Json := (Json.parse s).toOption.getD .null
def profiles (ps : String) : String :=
  "{\"language\":\"ve.core@0.2\",\"profiles\":[" ++ ps ++ "],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\"," ++
  "\"vocabulary\":{\"sorts\":{\"state\":{\"description\":\"state\"},\"person\":{\"description\":\"person\"}}," ++
  "\"predicates\":{\"public_service_access_required\":{\"arguments\":[\"state\",\"person\"],\"description\":\"obligation\"," ++
  "\"regulated\":{\"role\":\"obligation\",\"default\":\"deny\",\"act\":\"{0} give {1} equal access to public service\"}}," ++
  "\"country_of\":{\"arguments\":[\"state\",\"person\"],\"description\":\"base\"}," ++
  "\"charged\":{\"arguments\":[\"person\"],\"description\":\"base\"}},\"constants\":{\"texas\":{\"sort\":\"state\"," ++
  "\"description\":\"Texas\"},\"ann\":{\"sort\":\"person\",\"description\":\"Ann\"}},\"rights\":{\"holders\":[\"person\"]," ++
  "\"bearers\":[\"state\",\"person\"]}}}"
def on : String := "\"norms@0\",\"relational-fol@0\",\"right-clauses@0\",\"rights@0\",\"soft-norms@0\""
/-- The document whose one line has the head keys `keys` (a JSON member list), in a unit whose own members end `unit`. -/
def doc (keys : String) (unit : String := ",\"span\":[0,100]") : Json := parse <|
  "[{\"right\":{\"name\":\"r21\",\"holder\":\"person\",\"lines\":[{\"kind\":\"claim\",\"norm\":{\"name\":\"equal-access\"," ++
  "\"predicate\":\"public_service_access_required\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[],\"over\":[]}" ++ keys ++
  "}]}" ++ unit ++ "}]"
def ask (d : Json) (ps : String := on) : Except String Json :=
  (·.getObjValD "result") <$> elaborateCase (Json.mkObj [("id", "k"), ("environment", parse (profiles ps)), ("document", d)])
/-- The plained document's bytes, or the refusal. -/
def says (d : Json) (ps : String := on) : String :=
  match ask d ps with
  | .ok r => (r.getObjValD "plained").getStr?.toOption.getD ""
  | .error e => e
/-- The profile-off document with the line's guard `g`, as canonical bytes. -/
def off (g : String) : String :=
  (VE.CertificateWire.canonical 257 (parse ("[{\"right\":{\"name\":\"r21\",\"holder\":\"person\",\"lines\":[{\"kind\":" ++
    "\"claim\",\"norm\":{\"name\":\"equal-access\",\"predicate\":\"public_service_access_required\",\"sign\":true," ++
    "\"guard\":" ++ g ++ ",\"unless\":[],\"over\":[]}}]}}]"))).toOption.getD ""
def rel : String := "\"predicate\":\"country_of\",\"slots\":[0,1],\"cites\":[]"
def charged : String := "{\"role\":\"trigger\",\"formula\":[\"unary\",\"charged\",[\"var\",0]],\"span\":[10,20]}"
def countryOf : String := "[\"and\",[\"top\"],[\"binary\",\"country_of\",[\"var\",1],[\"var\",0]]]"

-- K1: the profile-off bytes, an empty slot
#guard says (doc ",\"elided\":[]") == off "[\"top\"]"
#guard ((ask (doc ",\"elided\":[]")).map (·.getObjValD "clause_slot")).toOption == some (Json.arr #[])
-- K2, K3: the relation atom in the guard; with total 1 its premise is the slot
#guard says (doc (",\"elided\":[],\"relation\":{" ++ rel ++ "}")) == off countryOf
#guard ((ask (doc (",\"elided\":[],\"relation\":{" ++ rel ++ ",\"total\":1}"))).map
  (·.getObjValD "clause_slot")).toOption == some (parse ("[{\"label\":\"rights:relation:equal-access:total\",\"ast\":" ++
  "[\"forall\",\"person\",[\"implies\",[\"top\"],[\"exists\",\"state\",[\"binary\",\"country_of\",[\"var\",0],[\"var\",1]]]]]}]"))
-- K4 and the three roles: clauses in order
#guard says (doc (",\"elided\":[[30,40]],\"clauses\":[" ++ charged ++ "]")) ==
  off "[\"and\",[\"top\"],[\"unary\",\"charged\",[\"var\",0]]]"
#guard says (doc (",\"elided\":[],\"clauses\":[{\"role\":\"scope\",\"formula\":[\"unary\",\"charged\",[\"var\",0]]," ++
  "\"span\":[10,20]},{\"role\":\"object\",\"formula\":[\"top\"],\"span\":[20,30]}]")) ==
  off "[\"and\",[\"and\",[\"top\"],[\"unary\",\"charged\",[\"var\",0]]],[\"top\"]]"
-- section 7's texts, in 4.1's order
#guard says (doc (",\"elided\":[[30,40]],\"clauses\":[{\"role\":\"trigger\",\"formula\":[\"top\"],\"span\":[90,110]}]")) ==
  "ClauseSpan: equal-access: [90, 110)"
#guard says (doc (",\"elided\":[[15,25]],\"clauses\":[" ++ charged ++ "]")) == "ClauseSpan: equal-access: [15, 25)"
#guard says (doc ",\"elided\":[],\"clauses\":[{\"role\":\"trigger\",\"formula\":[\"unary\",\"charged\",[\"var\",1]],\"span\":[10,20]}]") ==
  "InvalidInput: ill-typed clause 0 of rule equal-access"
#guard says (doc ",\"elided\":[],\"relation\":{\"predicate\":\"country_of\",\"slots\":[1,1],\"cites\":[]}") ==
  "RelationShape: equal-access"
#guard says (doc (",\"elided\":[],\"relation\":{" ++ rel ++ ",\"total\":0}")) == "RelationShape: equal-access"
#guard says (doc "") == "InvalidInput: elided missing on rule equal-access"
#guard says (doc ",\"clauses\":[]") == "InvalidInput: elided missing on rule equal-access"
#guard says (doc (",\"elided\":[],\"relation\":[{" ++ rel ++ "}]")) == "InvalidInput: invalid relation of rule equal-access"
#guard says (doc (",\"elided\":[],\"relation\":{" ++ rel ++ ",\"extra\":1}")) ==
  "InvalidInput: invalid relation of rule equal-access"
#guard says (doc ",\"elided\":[],\"relation\":{\"predicate\":\"country_of\",\"slots\":[0,1],\"cites\":[1]}") ==
  "InvalidInput: invalid relation of rule equal-access"
#guard says (doc ",\"elided\":[[1,2,3]]") == "InvalidInput: invalid elided of rule equal-access"
#guard says (doc ",\"elided\":5") == "InvalidInput: invalid elided of rule equal-access"
#guard says (doc ",\"elided\":[],\"clauses\":[]") == "InvalidInput: invalid clauses of rule equal-access"
#guard says (doc ",\"elided\":[],\"clauses\":5") == "InvalidInput: invalid clauses of rule equal-access"
#guard says (doc ",\"elided\":[],\"clauses\":[{\"role\":\"reason\",\"formula\":[\"top\"],\"span\":[10,20]}]") ==
  "InvalidInput: invalid clause 0 of rule equal-access"
#guard says (doc ",\"elided\":[]" ",\"span\":[0]") == "InvalidInput: invalid unit span"
#guard says (doc ",\"elided\":[],\"clauses\":[{\"role\":\"trigger\",\"span\":[10,20]}]") ==
  "InvalidInput: invalid clause 0 of rule equal-access"
#guard says (doc ",\"elided\":[[0,1]]" "") == "ClauseSpan: equal-access: [0, 1)"
#guard says (doc (",\"elided\":[],\"clauses\":[" ++ charged ++ "]") "") == "ClauseSpan: equal-access: [10, 20)"
#guard says (doc (",\"elided\":[],\"clauses\":[{\"role\":\"trigger\",\"span\":[10,20],\"formula\":" ++
  (List.range 65).foldl (fun f _ => "[\"not\"," ++ f ++ "]") "[\"top\"]" ++ "}]")) == "ResourceLimit: formula depth exceeds 64"
-- the profile off, and reading sets (cmp-s3-cfr-1c)
#guard says (doc ",\"elided\":[]") "\"norms@0\",\"relational-fol@0\",\"rights@0\",\"soft-norms@0\"" ==
  "UnsupportedProfile: clauses-elaborate requires right-clauses@0"
#guard says (doc ",\"elided\":[]")
  "\"norms@0\",\"readings@1\",\"relational-fol@0\",\"right-clauses@0\",\"rights@0\",\"soft-norms@0\"" ==
  "UnsupportedProfile: right-clauses@0 with readings@1 is not implemented"
-- the registration: an environment listing a wrapper is gated by the whole table, and the rights frame is read
-- without `right-clauses@0`
#guard (VE.Compose.environmentRows ["right-clauses@0"]).length == VE.Compose.profileTable.length &&
  (VE.Compose.environmentRows ["readings@1"]).length == VE.Compose.profileTable.length &&
  (VE.Compose.environmentRows ["norms@0"]).length == VE.Compose.baseRows.length &&
  (VE.Compose.environmentRows ["norms@0", "readings@1", "relational-fol@0"]).length ==
    VE.Compose.profileTable.length
#guard (VE.Compose.withoutClauses (parse (profiles on))).getObjValD "profiles" ==
  parse "[\"norms@0\",\"relational-fol@0\",\"rights@0\",\"soft-norms@0\"]"
-- the runner's row: the id echoed, the result typed
#guard (runCaseReported (Json.mkObj [("id", "k"), ("environment", parse (profiles on)), ("document", doc ",\"elided\":[]")])
  ).getObjValD "status" == "ok"
#guard runCaseReported (Json.mkObj [("id", "k")]) == Json.mkObj [("id", "k"), ("status", "error"),
  ("error", "fields do not match: expected [id, environment, document], got [id]")]
-- two units (a `right` and its `right_lines`), each line with a total relation: both units plained, two premises
def twoLines : Json := parse <|
  "[{\"right\":{\"name\":\"r21\",\"holder\":\"person\",\"lines\":[{\"kind\":\"claim\",\"norm\":{\"name\":" ++
  "\"equal-access\",\"predicate\":\"public_service_access_required\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[]," ++
  "\"over\":[]},\"elided\":[],\"relation\":{" ++ rel ++ ",\"total\":1}}]},\"span\":[0,100]}," ++
  "{\"right_lines\":{\"right\":\"r21\",\"lines\":[{\"kind\":\"claim\",\"norm\":{\"name\":\"equal-access-2\"," ++
  "\"predicate\":\"public_service_access_required\",\"sign\":true,\"guard\":[\"top\"],\"unless\":[],\"over\":[]}," ++
  "\"elided\":[],\"relation\":{" ++ rel ++ ",\"total\":1}}]},\"span\":[100,200]}]"
#guard ((ask twoLines).map fun r => ((r.getObjValD "clause_slot").getArr?.toOption.map (·.size),
  (parse ((r.getObjValD "plained").getStr?.toOption.getD "")).getArr?.toOption.map (·.size))).toOption ==
  some (some 2, some 2)
#guard says (doc ",\"elided\":[[30,40],[35,45]]") == "ClauseSpan: equal-access: [35, 45)"
-- an extra member that sorts first, then last
#guard says (doc (",\"elided\":[],\"relation\":{\"aaa\":1," ++ rel ++ "}")) ==
  "InvalidInput: invalid relation of rule equal-access"
#guard says (doc ",\"elided\":[],\"clauses\":[{\"aaa\":1,\"role\":\"trigger\",\"formula\":[\"top\"],\"span\":[10,20]}]") ==
  "InvalidInput: invalid clause 0 of rule equal-access"
#guard says (doc (",\"elided\":[],\"relation\":{" ++ rel ++ ",\"zzz\":1}")) ==
  "InvalidInput: invalid relation of rule equal-access"
#guard says (doc ",\"elided\":[],\"clauses\":[{\"role\":\"trigger\",\"formula\":[\"top\"],\"span\":[10,20],\"zzz\":1}]") ==
  "InvalidInput: invalid clause 0 of rule equal-access"

end VE.RightClauses.RunExamples
