import VE.Service.DocumentView
import VE.Compose.ContractExamples

/-! sa-checked-view's build-time checks, the trust-mutant sweep's `--test` file (tests/test_sa_checked_view.py runs it
too): the view on `VE.Service.ScopeExamples`' `full` (plain) and `doc` (two items under a `frame` governor), and its
parts on literal values. A governed reading set's view is the Python test's (its route traces stages with
`dbgTrace`, which the sweep does not read as a check). -/

open Lean VE.Service.Document VE.Service.ScopeExamples VE.Discourse

def agrees (j : Json) : Bool := match checkDocSetsView j, checkDocSets j with
  | .ok (a, V), .ok b => a == b && a.getObjValD "units" == toJson (V.rows.map unitJson) &&
      a.getObjValD "source" == .str V.source && V.packSources.isEmpty
  | .error e, .error f => e == f
  | _, _ => false

def reading (id kind : String) : Json := Json.mkObj [("id", .str id), ("kind", .str kind), ("meaning_id", .str "m"),
  ("content", .null), ("admission", Json.mkObj [("who", .str "t"), ("why", .str "w"),
    ("distinguishing_models", Json.mkObj [])])]
def setJ (id u : String) (r : Json) : Json := Json.mkObj [("id", .str id), ("unit", .str u), ("version", toJson 1),
  ("status", .str "open"), ("readings", toJson [r])]
def plainFront : Json := front (units none none) ["norms@0", "relational-fol@0"] none
/-- Two reading sets, on `i1` and `i2`, each with one pending reading; and a claim graph the admission refuses. -/
def twoSets : Json :=
  case (plainFront.setObjVal! "reading_sets"
    (toJson [setJ "s" "i1" (reading "p" "asserted"), setJ "t" "i2" (reading "q" "norm")]))
def badGraph : Json := case (plainFront.setObjVal! "graph" (.str "bad"))

#guard [full, doc, twoSets, badGraph, full.setObjVal! "admit" (.str "x"),
  full.setObjVal! "document" (.num 1)].all agrees
#guard [full, doc].all fun j => (checkDocSetsView j).toOption.map (·.2.candidates.isEmpty) == some true
#guard (activeKinds twoSets).toOption == some [("i1", [.asserted]), ("i2", [.norm])]
#guard (checkDocSetsView twoSets).toOption.map (·.2.readings) == some [("i1", ["p"]), ("i2", ["q"])]
-- Scope's fold: the lead-in is LABELLED before it and takes its items' status after it.
#guard (checkDocSetsView doc).toOption.map (·.2.rows.map (·.status.name)) ==
  some ["CHECKED", "CHECKED", "CHECKED", "UNFORMALISED"]

def r : RowUnit := ⟨"u", (0, 1), .route .asserted, .specified, .assumption, .labelled, none, none, none⟩

#guard unitJson (readStatus r (Json.mkObj [("status", .str "CHECKED")])) == unitJson { r with status := .checked }
#guard unitJson (readStatus r (Json.mkObj [("status", .str "UNKNOWN")])) == unitJson r
#guard (foldedRows [r, r] (Json.mkObj [("units", toJson [unitJson { r with status := .opened }, unitJson r])])).map
  unitJson == [unitJson { r with status := .opened }, unitJson r]

/-- Set `s` on unit `a` in two versions, the second with two readings of two kinds, and set `t` on unit `b`. -/
def setsFront : Json :=
  let set (id : String) (v : Nat) (rs : List (String × String)) := Json.mkObj [("id", .str id), ("version", toJson v),
    ("readings", toJson (rs.map fun (i, k) => Json.mkObj [("id", .str i), ("kind", .str k)]))]
  Json.mkObj [("reading_sets", toJson [set "s" 1 [("p", "asserted")],
    set "s" 2 [("notp", "exposition"), ("p", "asserted")], set "t" 1 [("q", "norm")]])]

def s2 : FrontSet := ⟨"s", "a", 2, "open", [("notp", .top), ("p", .top)]⟩
def t1 : FrontSet := ⟨"t", "b", 1, "open", [("q", .top)]⟩
def checked : Checked :=
  { documentId := "", sourceId := "", source := "S", units := [], rows := [], front := setsFront, block := none,
    active := [(s2, []), (⟨"s", "a", 1, "open", [("p", .top)]⟩, []), (t1, [])] }

#guard candidatesOf setsFront s2 == [("notp", .exposition), ("p", .asserted)]
#guard candidatesOf setsFront ⟨"s", "a", 1, "open", [("p", .top)]⟩ == [("p", .asserted)]
#guard firstPerUnit [("a", 1), ("b", 2), ("a", 3)] == [("a", 1), ("b", 2)]
#guard firstPerUnit [("a", 1), ("b", 2), ("b", 3), ("c", 4)] == [("a", 1), ("b", 2), ("c", 4)]
/-- A kind `n` hedges deep: `decodeKind 16` reads 15, not 16. -/
def nest : Nat → Json
  | 0 => .str "asserted"
  | n + 1 => toJson [.str "hedged", .str "likely", nest n]
#guard (candidatesOf (Json.mkObj [("reading_sets", toJson [Json.mkObj [("id", .str "d"), ("version", toJson 1),
    ("readings", toJson [Json.mkObj [("id", .str "ok"), ("kind", nest 15)], Json.mkObj [("id", .str "deep"),
    ("kind", nest 16)]])]])]) ⟨"d", "a", 1, "open", [("ok", .top), ("deep", .top)]⟩).map (·.1) == ["ok"]
#guard unitSets checked == [("a", [("notp", .exposition), ("p", .asserted)]), ("b", [("q", .norm)])]
#guard let V := viewOf checked [r]
  V.candidates == [("a", [.exposition, .asserted]), ("b", [.norm])] &&
    V.readings == [("a", ["notp", "p"]), ("b", ["q"])] && V.packSources.isEmpty && V.source == "S" &&
    V.rows.map unitJson == [unitJson r]
