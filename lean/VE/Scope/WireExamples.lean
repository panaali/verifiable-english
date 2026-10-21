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

end VE.Scope.WireExamples
