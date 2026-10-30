import VE.Service.Document

/-! scope@0 in the document mode (SC-1b; docs/spec/scope.md 1.6, 3, 5.2 and 7.2) on a small part document built as a
request carries it: a lead-in "Agents must not:" framing two items, and a closing sentence. F1-doc (the governor's
status is its items' weakest, and each item's row is byte for byte the row of the same rule written in full), F1-bad
and F1-none, the absent case, the profile gate, the block's wire faults and the layout. -/

namespace VE.Service.ScopeExamples
open Lean VE.Service.Document

def source : String := "Agents must not:\n\n* Act.\n* Rest.\n\nThat is all."
def lead : Json := Json.mkObj [("sign", .bool false), ("unless", Json.arr #[]), ("over", Json.arr #[])]
def item (n : String) : Json := Json.mkObj [("name", .str n), ("predicate", .str "p"), ("guard", toJson ["top"])]
def unit (id : String) (s e : Nat) (meaning kind : Json) (support : String) (content : Option Json) : Json :=
  Json.mkObj ([("id", .str id), ("span", toJson [s, e]), ("kind", kind), ("meaning", meaning),
    ("support", .str support)] ++ content.toList.map ("content", ·))
def unf : Json := Json.mkObj [("unformalised", .str "x")]
def unfKind : Json := toJson ["unformalised", "x"]
def sp : Json := .str "specified"
/-- The document's units: the lead-in, its items with the contents `c₁`, `c₂` (none: pending), the closing sentence. -/
def units (c₁ c₂ : Option Json) (leadMeaning : Json := sp) : List Json :=
  [unit "u1" 0 18 leadMeaning (if leadMeaning == sp then .str "norm" else unfKind) "none" none,
   unit "i1" 18 25 (if c₁.isSome then sp else unf) (if c₁.isSome then .str "norm" else unfKind)
     (if c₁.isSome then "assumption" else "none") c₁,
   unit "i2" 25 34 (if c₂.isSome then sp else unf) (if c₂.isSome then .str "norm" else unfKind)
     (if c₂.isSome then "assumption" else "none") c₂,
   unit "u3" 34 46 unf unfKind "none" none]
def env (profiles : List String) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("agent", Json.mkObj [("description", .str "agent")])]),
      ("predicates", Json.mkObj [("p", Json.mkObj [("arguments", toJson ["agent"]), ("description", .str "d"),
        ("regulated", Json.mkObj [("role", .str "permission"), ("default", .str "deny"), ("act", .str "{0} acts")])])]),
      ("constants", Json.mkObj [])])]
def listed : List String := ["norms@0", "relational-fol@0", "scope@0"]
def governor (units : List String := ["i1", "i2"]) : Json :=
  Json.mkObj [("id", .str "g1"), ("unit", .str "u1"), ("reach", Json.mkObj [("list", .str "u1")]),
    ("units", toJson units), ("effect", Json.mkObj [("frame", lead)])]
def block (governors : List Json := [governor]) : Json :=
  Json.mkObj [("version", .str "scope@0"), ("governors", toJson governors)]
def part (n : String) : Json := Json.mkObj [("part", item n)]
def front (us : List Json) (profiles : List String := listed) (scope : Option Json := some block) : Json :=
  Json.mkObj ([("format", .str "ve-document@1"), ("environment", env profiles), ("units", toJson us)] ++
    scope.toList.map ("scope", ·))
def case (f : Json) : Json := Json.mkObj [("id", .str "d"), ("document", .str ("---\n" ++ f.compress ++ "\n---\n" ++ source))]

def doc : Json := case (front (units (some (part "r1")) (some (part "r2"))))
/-- The same rules written in full, without scope (the document as it is checked today). -/
def full : Json := case (front (units (some (Json.mkObj [("norm", (item "r1").mergeObj lead)]))
  (some (Json.mkObj [("norm", (item "r2").mergeObj lead)])) unf) ["norms@0", "relational-fol@0"] none)
def statuses (a : Except String Json) : List (String × String) :=
  match a with
  | .ok r => match r.getObjValD "units" with
    | .arr xs => xs.toList.map fun u => ((u.getObjValD "id").getStr?.toOption.getD "",
        (u.getObjValD "status").getStr?.toOption.getD "")
    | _ => []
  | .error e => [("error", e)]
def row (a : Except String Json) (u : String) : Json :=
  match a with
  | .ok r => match r.getObjValD "units" with
    | .arr xs => (xs.toList.find? (·.getObjValD "id" == .str u)).getD .null
    | _ => .null
  | .error _ => .null
def member (a : Except String Json) (k : String) : Json := (a.toOption.map (·.getObjValD k)).getD .null
def errorOf (a : Except String Json) : String := match a with | .error e => e | .ok _ => "ok"

-- F1-doc: the lead-in takes its items' weakest status (both CHECKED); each item is the rule written in full.
#guard statuses (checkDoc doc) == [("u1", "CHECKED"), ("i1", "CHECKED"), ("i2", "CHECKED"), ("u3", "UNFORMALISED")]
#guard row (checkDoc doc) "i1" == row (checkCore full) "i1" && row (checkDoc doc) "i2" == row (checkCore full) "i2"
#guard (row (checkDoc doc) "i1").getObjValD "content" ==
  Json.mkObj [("norm", Json.mkObj [("guard", toJson ["top"]), ("name", .str "r1"), ("over", Json.arr #[]),
    ("predicate", .str "p"), ("sign", .bool false), ("unless", Json.arr #[])])]
#guard (member (checkDoc doc) "coverage").getObjValD "bytes_by_status" ==
  Json.mkObj [("CHECKED", toJson (34 : Nat)), ("UNFORMALISED", toJson (12 : Nat))]
-- The identities: the document as written (its block and parts), on the environment without scope@0.
#guard member (checkDoc doc) "source_id" == member (checkCore full) "source_id"
#guard some (member (checkDoc doc) "document_id") ==
  ((do documentId (← split ("---\n" ++ (front (units (some (part "r1")) (some (part "r2")))).compress ++ "\n---\n" ++
    source) (senses := true))).toOption.map Json.str)
#guard member (checkDoc doc) "document_id" != member (checkCore full) "document_id"
-- F1-bad: one item not admitted (pending): the lead-in is UNFORMALISED, and so are its bytes.
#guard statuses (checkDoc (case (front (units (some (part "r1")) none)))) ==
  [("u1", "UNFORMALISED"), ("i1", "CHECKED"), ("i2", "UNFORMALISED"), ("u3", "UNFORMALISED")]
#guard (member (checkDoc (case (front (units (some (part "r1")) none)))) "coverage").getObjValD "bytes_by_status" ==
  Json.mkObj [("CHECKED", toJson (7 : Nat)), ("UNFORMALISED", toJson (39 : Nat))]
-- A lead-in whose meaning is not `specified` keeps its own status.
#guard statuses (checkDoc (case (front (units (some (part "r1")) (some (part "r2")) unf)))) ==
  [("u1", "UNFORMALISED"), ("i1", "CHECKED"), ("i2", "CHECKED"), ("u3", "UNFORMALISED")]
-- Absent: the document without scope@0 is checkCore's, as before (F1-off: a part is no content it reads).
#guard (checkDoc full).toOption == (checkCore full).toOption && (checkCore full).isOk
#guard errorOf (checkDoc (case (front (units (some (part "r1")) (some (part "r2"))) ["norms@0", "relational-fol@0"]
  none))) == "unit fence must match its id"
#guard errorOf (checkDoc (case (front (units (some (part "r1")) (some (part "r2"))) ["norms@0", "relational-fol@0"])))
  == "unknown document metadata"
#guard profilesOf doc == listed && profilesOf full == ["norms@0", "relational-fol@0"]
-- sc-1af: the route's parsed documents pass the boundary's check, `false` and spans included
#guard [doc, case (front (units (some (part "r1")) none)),
    case (front (units (some (part "r1")) (some (part "r2")) unf))].map
  (fun c => (VE.Scope.decodeScope c).toOption.map (VE.Scope.jsonWF? ·.doc)) == [some true, some true, some true]
-- The profile gate (AR-10's row) and the block.
#guard errorOf (checkDoc (case (front (units none none) ["alternatives@0", "norms@0", "relational-fol@0", "scope@0"])))
  == "UnsupportedProfile: scope@0 with alternatives@0"
#guard errorOf (checkDoc (case (front (units none none) ["relational-fol@0", "scope@0"]))) ==
  "UnsupportedProfile: scope@0 requires norms@0"
#guard errorOf (checkDoc (case (front (units none none) listed none))) ==
  "InvalidInput: scope@0 scope must be an object"
#guard errorOf (checkDoc (case (front (units none none) listed (some (block [governor ["i1"]]))))) ==
  "ManifestMismatch: scope.governors.g1.units"
#guard errorOf (checkDoc (case (front (units (some (part "r1")) (some (part "r2"))) listed (some (block []))))) ==
  "ScopeOrphanPart: i1"
-- The block's environment is the chain's, `readings@1` listed in order, `scope@0` lowered; a document with senses is
-- decoded as the chain reads it.
#guard [listed, ["norms@0", "readings@1", "relational-fol@0", "scope@0"],
    ["norm-defaults@0", "norms@0", "relational-fol@0", "scope@0", "soft-norms@0"]].map
  (fun ps => (scopeReadings (env ps)).toOption.map (·.profiles)) ==
  [some ["norms@0", "readings@1", "relational-fol@0"], some ["norms@0", "readings@1", "relational-fol@0"],
   some ["norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]]
-- `split` and `check` read the whole list: scope@0 anywhere in it (here first; only the environment refuses an
-- unsorted list) admits the block, and `check` reads the governed units on the environment without scope@0.
def unsorted : String :=
  "---\n" ++ (front (units (some (part "r1")) (some (part "r2"))) ["scope@0", "norms@0", "relational-fol@0"]).compress ++
    "\n---\n" ++ source
def fullUnits : Json := toJson (units (some (Json.mkObj [("norm", (item "r1").mergeObj lead)]))
  (some (Json.mkObj [("norm", (item "r2").mergeObj lead)])) unf)
#guard (split unsorted (senses := true)).toOption.isSome
#guard (check unsorted (governed := some fullUnits)).toOption.map (·.units.length) == some 4
#guard (VE.Scope.decodeScope (case ((front (units (some (part "r1")) (some (part "r2")))).setObjVal! "senses"
  (Json.mkObj [])))).toOption.isSome
-- The layout is read from the source bytes of exactly the document's units.
#guard (VE.Scope.decodeScope doc).toOption.map (fun D => D.layout.map fun x => (x.id, x.lead, x.item)) ==
  some [("u1", true, none), ("i1", false, some 0), ("i2", false, some 0), ("u3", false, none)]

end VE.Service.ScopeExamples
