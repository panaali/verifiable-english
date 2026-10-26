import VE.Scope.Wire

/-! SC-1b's fixtures for the governor status (F1-doc, F1-bad, F1-none of docs/spec/scope.md 7.2), the block decoder
(wire 3: every reach and effect, and each fault) and the layout of the document's units. -/

namespace VE.Scope.WireExamples
open Lean VE.Scope
open VE.Reports (Status)

def st (xs : List (String × Status)) (u : String) : Option Status := xs.lookup u
def errorOf {α : Type} : Except String α → String
  | .error e => e
  | .ok _ => "ok"

-- F1-doc: seven OPEN items, OPEN; the weakest wins, whatever the order; all CHECKED is CHECKED.
#guard governorStatus (st ((List.range 7).map fun i => (s!"u{i}", .open))) ((List.range 7).map (s!"u{·}")) ==
  some .open
#guard governorStatus (st [("a", .checked), ("b", .labelled), ("c", .open)]) ["a", "b", "c"] == some .open
#guard governorStatus (st [("a", .labelled), ("b", .checked)]) ["b", "a"] == some .labelled
#guard governorStatus (st [("a", .checked)]) ["a"] == some .checked
-- F1-bad: one item not admitted (UNFORMALISED); F1-none: no item, or one with no status.
#guard governorStatus (st [("a", .open), ("b", .unformalised)]) ["a", "b"] == some .unformalised
#guard governorStatus (st []) [] == none
#guard governorStatus (st [("a", .open)]) ["a", "b"] == none
#guard ["UNFORMALISED", "OPEN", "UNKNOWN", "LABELLED", "CHECKED", "open"].map statusOf ==
  [some .unformalised, some .open, none, some .labelled, some .checked, none]

def gov (reach effect : Json) (units : Option Json := some (toJson ["b"])) : Json :=
  Json.mkObj ([("id", .str "g"), ("unit", .str "a"), ("reach", reach), ("effect", effect)] ++
    units.toList.map ("units", ·))
def blockWith (governors : List Json) (rest : List (String × Json) := []) : Json :=
  Json.mkObj ([("version", .str "scope@0"), ("governors", toJson governors)] ++ rest)
def effectTag : Effect → String
  | .frame p => "frame " ++ p.compress | .reguard c => "reguard " ++ c.compress
  | .carveOut c => "carve_out " ++ c.compress | .precedes => "precedes" | .yields => "yields" | .title => "title"
def decoded (b : Json) : Option (List (String × String × Reach × String × List String)) :=
  (decodeParts b).toOption.map fun (gs, _, _) => gs.map fun g => (g.id, g.unit, g.reach, effectTag g.effect, g.units)

-- Every reach and effect of the wire (3), and a frontier reach with no recorded units.
#guard decoded (blockWith [gov (Json.mkObj [("list", .str "a")]) (Json.mkObj [("frame", Json.mkObj [])]),
    gov (Json.mkObj [("list_name", .str "n")]) (Json.mkObj [("reguard", toJson ["top"])]),
    gov (Json.mkObj [("anchor", .str "s")]) (Json.mkObj [("carve_out", toJson ["top"])]),
    gov (Json.mkObj [("label", .str "a")]) (.str "title"),
    gov (Json.mkObj [("rules", toJson ["r1", "r2"])]) (.str "precedes"),
    gov (.str "frontier") (.str "yields") none]) ==
  some [("g", "a", .list "a", "frame {}", ["b"]), ("g", "a", .listName "n", "reguard [\"top\"]", ["b"]),
    ("g", "a", .anchor "s", "carve_out [\"top\"]", ["b"]), ("g", "a", .label "a", "title", ["b"]),
    ("g", "a", .rules ["r1", "r2"], "precedes", ["b"]), ("g", "a", .frontier, "yields", [])]
-- A list name: lead and unit are scope's, the rest is discourse's ContentName; anchors are discourse's.
#guard (decodeParts (blockWith [] [("list_names", toJson [Json.mkObj [("name", .str "the list"), ("units", toJson ["b"]),
    ("scope", .str "doc"), ("lead", .str "a"), ("unit", .str "z")]])])).toOption.map
    (fun (_, ls, _) => ls.map fun (cn, l, u) => (cn.name, cn.units, cn.scope, l, u)) ==
  some [("the list", ["b"], "doc", "a", "z")]
#guard (decodeParts (blockWith [] [("anchors", toJson [Json.mkObj [("id", .str "doc"), ("kind", .str "document"),
    ("label", .str "Doc"), ("span", toJson [0, 5])]])])).toOption.map (fun (_, _, as) => as.map (·.span)) ==
  some [(0, 5)]
-- The block's faults, each with its path (3, 6.1).
#guard errorOf (decodeParts .null) == "InvalidInput: scope@0 scope must be an object"
#guard errorOf (decodeParts (blockWith [] [("forward", toJson ([] : List Json))])) ==
  "InvalidInput: scope@0 unknown member scope.forward"
#guard errorOf (decodeParts (blockWith [] [("anchors", .null)])) == "InvalidInput: scope@0 scope.anchors must be absent, not null"
#guard errorOf (decodeParts (Json.mkObj [("version", .str "scope@1")])) == "InvalidInput: scope@0 version must be \"scope@0\""
#guard errorOf (decodeParts (Json.mkObj [("governors", toJson ([] : List Json))])) ==
  "InvalidInput: scope@0 version must be \"scope@0\""
#guard errorOf (decodeParts (Json.mkObj [("version", .str "scope@0"), ("governors", .str "g")])) ==
  "InvalidInput: scope@0 governors must be an array"
#guard errorOf (decodeParts (blockWith [Json.mkObj [("unit", .str "a")]])) == "InvalidInput: scope@0 governors.id must be present"
#guard errorOf (decodeParts (blockWith [(gov (.str "frontier") (.str "title")).setObjVal! "x" (.bool true)])) ==
  "InvalidInput: scope@0 unknown member governors.x"
#guard errorOf (decodeParts (blockWith [gov (Json.mkObj [("list", toJson [1])]) (.str "title")])) ==
  "InvalidInput: scope@0 governors.g.reach must be a reach"
#guard errorOf (decodeParts (blockWith [gov (Json.mkObj [("list", .str "a"), ("label", .str "a")]) (.str "title")])) ==
  "InvalidInput: scope@0 governors.g.reach must be a reach"
#guard errorOf (decodeParts (blockWith [gov (.str "frontier") (.str "narrows")])) ==
  "InvalidInput: scope@0 governors.g.effect must be an effect"
#guard errorOf (decodeParts (blockWith [gov (Json.mkObj [("rules", toJson [1])]) (.str "title")])) ==
  "InvalidInput: scope@0 governors.g.reach.rules must be an array of strings"
#guard errorOf (decodeParts (blockWith [gov (Json.mkObj [("list", .str "a")]) (.str "title") none])) ==
  "InvalidInput: scope@0 governors.g.units must be present"
#guard errorOf (decodeParts (blockWith [gov (Json.mkObj [("list", .str "a")]) (.str "title") (some (.str "b"))])) ==
  "InvalidInput: scope@0 governors.g.units must be an array of strings"
#guard errorOf (decodeParts (blockWith [(gov (.str "frontier") (.str "title")).setObjVal! "unit" (toJson [1])])) ==
  "InvalidInput: scope@0 governors.g.unit must be a string"
#guard errorOf (decodeParts (blockWith [] [("list_names", toJson [Json.mkObj [("name", .str "n"),
    ("units", toJson ["b"]), ("scope", .str "doc"), ("unit", .str "z")]])])) ==
  "InvalidInput: scope@0 list_names.n.lead must be present"

-- The layout: exactly the document's units in order, each span clamped to the source.
#guard (layoutOf (Json.mkObj [("units", toJson [Json.mkObj [("id", .str "a"), ("span", toJson [0, 4])],
    Json.mkObj [("id", .str "b"), ("span", toJson [4, 99])], Json.mkObj [("id", .str "c")]])]) "x:\n\n* y").map
    (fun x => (x.id, x.span, x.lead, x.item)) ==
  [("a", (0, 4), true, none), ("b", (4, 7), false, some 0), ("c", (0, 0), false, none)]
#guard [Json.mkObj [("span", toJson [Json.str "x", toJson (5 : Nat)])],
  Json.mkObj [("span", toJson [toJson (3 : Nat), Json.str "y"])]].map (spanIn 9) == [(0, 5), (0, 0)]

-- The fold (1.6) on an answer: the lead-in u1 (specified, no content) hosts the frame g1 and takes the weakest of
-- its items; i1 has content and u3 hosts only a graph governor, so both keep their status; bytes counted again.
def foldEnv : Json := Json.mkObj [("language", .str "ve.core@0.2"),
  ("profiles", toJson ["norms@0", "readings@1", "relational-fol@0"]),
  ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
  ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("agent", Json.mkObj [("description", .str "agent")])]),
    ("predicates", Json.mkObj []), ("constants", Json.mkObj [])])]
def ansUnit (id : String) (s e : Nat) (status : String) (content : Option Json := none) : Json :=
  Json.mkObj ([("id", .str id), ("span", toJson [s, e]), ("meaning", .str "specified"), ("status", .str status)] ++
    content.toList.map ("content", ·))
def ansUnits : List Json := [ansUnit "u1" 0 18 "OPEN", ansUnit "i1" 18 25 "CHECKED" (some (Json.mkObj [])),
  ansUnit "i2" 25 34 "LABELLED", ansUnit "u3" 34 46 "OPEN"]
def foldGov (id unit : String) (reach effect : Json) : Json :=
  Json.mkObj [("id", .str id), ("unit", .str unit), ("reach", reach), ("units", toJson ["i1", "i2"]),
    ("effect", effect)]
def foldDoc : Option SDoc := do
  let re ← (VE.Readings.Wire.decodeEnvironment foldEnv).toOption
  (decodeBlock (Json.mkObj [("units", toJson ansUnits), ("scope", blockWith [
    foldGov "g1" "u1" (Json.mkObj [("list", .str "u1")]) (Json.mkObj [("frame", Json.mkObj [])]),
    foldGov "g2" "u3" (.str "frontier") (.str "precedes"),
    foldGov "g3" "i1" (Json.mkObj [("list", .str "u1")]) (Json.mkObj [("frame", Json.mkObj [])])])])
    "Agents must not:\n\n* Act.\n* Rest.\n\nThat is all." re).toOption
def answer : Json := Json.mkObj [("id", .str "d"), ("status", .str "OPEN"), ("units", toJson ansUnits),
  ("coverage", Json.mkObj [("units", toJson (4 : Nat)), ("bytes_by_status", Json.mkObj [])])]
#guard foldDoc.map (fun D => ((changers D "u1").map (·.id), (changers D "u3").map (·.id))) == some (["g1"], [])
#guard foldDoc.map (fun D => (foldGovernors D answer).compress) == some ("{\"coverage\":{\"bytes_by_status\":" ++
  "{\"CHECKED\":7,\"LABELLED\":27,\"OPEN\":12},\"units\":4},\"document_id\":null,\"id\":\"d\",\"source\":null," ++
  "\"source_id\":null,\"status\":\"OPEN\",\"units\":[{\"id\":\"u1\",\"meaning\":\"specified\",\"span\":[0,18]," ++
  "\"status\":\"LABELLED\"},{\"content\":{},\"id\":\"i1\",\"meaning\":\"specified\",\"span\":[18,25]," ++
  "\"status\":\"CHECKED\"},{\"id\":\"i2\",\"meaning\":\"specified\",\"span\":[25,34],\"status\":\"LABELLED\"}," ++
  "{\"id\":\"u3\",\"meaning\":\"specified\",\"span\":[34,46],\"status\":\"OPEN\"}]}")
-- The bytes by status, in order of first appearance; a unit without a span counts no bytes.
#guard byStatus [Json.mkObj [("status", .str "A"), ("span", toJson [0, 4])],
  Json.mkObj [("status", .str "B"), ("span", toJson [4, 10])],
  Json.mkObj [("status", .str "A"), ("span", toJson [10, 11])],
  Json.mkObj [("status", .str "B")]] == [("A", toJson (5 : Nat)), ("B", toJson (6 : Nat))]
#guard byStatus [Json.mkObj [("status", .str "A"), ("span", toJson [Json.str "x", toJson (4 : Nat)])],
  Json.mkObj [("status", .str "A"), ("span", toJson [toJson (0 : Nat), Json.str "y"])]] == [("A", toJson (4 : Nat))]

end VE.Scope.WireExamples
