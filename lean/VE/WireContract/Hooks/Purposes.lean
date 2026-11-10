import VE.Purposes.Wire
import VE.Purposes.WellFormed
import VE.WireContract.Engine
import VE.WireContract.Tables.Purposes

/-! The classifiers and adapter of the contract `purposes@0`, in shadow (sa-wire-purposes0; purpose-explanation.md
5.4 and 7): they report and refuse nothing.

`purposes_block` runs `VE.Purposes.decodeBlock`; when it refuses, `member` names the row of spec 7.1 by running the
decoder's own functions in `decodeLink`'s order, and returns the values the row's text quotes, so the table's text
renders to the decoder's (the round-trip guards below). `purposes_ids` names 7.2's row 2, the one fault of
`VE.Purposes.check` that reads no checked unit; every other row of 7.2 waits for PE-2's checked view. The limit is
`VE.Purposes.maxLinks`, read here and never copied. Diagnostic only: no verdict depends on this module. -/

namespace VE.WireContract.Hooks.Purposes
open Lean
open VE.WireContract
open VE.Purposes (decodeBlock decodeRef idOf linkFieldsOk linksOf maxLinks shareOf wordOf)

/-- A value as the decoder's texts quote it (`idOf`, `wordOf`): a string as it is, anything else compressed. -/
def shown : Json → String
  | .str s => s
  | j => j.compress

/-- The first id of a side that `decodeRef` refuses as not a token, when the side's refusal is one. -/
def sideId (lid : String) (side : Json) : Option String :=
  match side with
  | .arr rs => rs.toList.findSome? fun r => match decodeRef lid r, VE.Bridge.fields r with
    | .error _, .ok [(_, v)] => if (idOf v).isOk then none else some (shown v)
    | _, _ => none
  | _ => none

/-- 7.1's row for link `n`'s refusal, with its arguments, in `decodeLink`'s order. -/
def linkMember (n : Nat) (j : Json) : String × List (String × Json) :=
  let v := j.getObjValD
  let word {α : Type} (f : String → Option α) (k : String) : Bool := (wordOf f id (v k)).isOk
  if !(linkFieldsOk n j).isOk then ("1.1d", [("link", .str (toString n))])
  else if !(idOf (v "id")).isOk then ("1.1e", [("id", .str (shown (v "id")))])
  else if !(idOf (v "marker")).isOk then ("1.1e", [("id", .str (shown (v "marker")))])
  else
    let lid := shown (v "id")
    if !word VE.Purposes.Relation.ofWire? "relation" then ("1.1f", [("link", .str lid), ("relation", .str (shown (v "relation")))])
    else if !word VE.Purposes.Polarity.ofWire? "polarity" then
      ("1.1g", [("link", .str lid), ("polarity", .str (shown (v "polarity")))])
    else if !(shareOf lid j).isOk then ("1.1h", [("link", .str lid), ("share", .str (shown (v "share")))])
    else match sideId lid (v "reason") <|> sideId lid (v "target") with
      | some i => ("1.1e", [("id", .str i)])
      | none => ("1.1i", [("link", .str lid)])

/-- 7.1's row of a block the decoder refuses: the block's shape, its count, then the first link the decoder refuses. -/
def member (j : Json) : String × List (String × Json) :=
  match linksOf j with
  | .error _ => ("1.1b", [])
  | .ok ls =>
    if maxLinks < ls.size then ("1.1c", [("limit", .str (toString maxLinks))])
    else match (ls.toList.zip (List.range ls.size)).find? (fun (l, i) => !(VE.Purposes.decodeLink (i + 1) l).isOk) with
      | some (l, i) => linkMember (i + 1) l
      | none => ("1.1b", [])

def purposesOf (root : Json) : Json := root.getObjValD "purposes"

def classifier : String → Json → List Pointer → ClassifierResult
  | "purposes_block", root, _ => match decodeBlock (purposesOf root) with
    | .ok _ => .ok
    | .error _ => let (m, args) := member (purposesOf root); .fail m args
  | "purposes_ids", root, _ => match decodeBlock (purposesOf root) with
    | .ok B => if (B.links.map (·.id)).Nodup then .ok else .fail "2.1b" []
    | .error _ => .ok
  | _, _, _ => .ok

def hooks : Hooks := ⟨fun _ _ _ => .ok, classifier, fun _ v => v⟩

/-- The adapter `purposes_block`: the case's `purposes` member, `null` when absent. -/
def adapter (case : Json) : Except String Json := .ok (Json.mkObj [("purposes", case.getObjValD "purposes")])

/-- Phase `decode` is clean exactly when the decoder accepts the block: the legacy validation of the examples. -/
theorem classifier_ok_iff (root : Json) (items : List Pointer) :
    (match classifier "purposes_block" root items with | .ok => true | .fail _ _ => false) =
      (decodeBlock (purposesOf root)).isOk := by
  cases h : decodeBlock (purposesOf root) <;> simp [classifier, h, Except.isOk, Except.toBool]

def registered : List String := ["purposes_block", "purposes_ids"]

#guard Tables.Purposes.table.hookNames.all registered.contains
#guard Tables.Purposes.table.revision == 1  -- purposes@0.json's revision: a new revision updates this pin

/-! The round trip: on each fixture the engine's record over the generated table names `row` and its text is the
decoder's (`check`'s for 2.1b); a clean block gives no record. -/

def recordOf (j : Json) : Option Json :=
  (run Tables.Purposes.table hooks (Json.mkObj [("purposes", j)])).map (record Tables.Purposes.table)

def roundTrips (j : Json) (row : String) : Bool :=
  let text := match decodeBlock j with
    | .error e => e
    | .ok B => match VE.Purposes.check ⟨"", [], []⟩ B with | .error e => e | .ok _ => ""
  match recordOf j with
  | some r => r.getObjValD "check" == .str row && r.getObjValD "text" == .str text && r.getObjValD "path" == "/purposes"
  | none => false

def link (id : String) (more : List (String × Json) := []) (drop : List String := []) : Json :=
  Json.mkObj ((([("id", Json.str id), ("relation", "because"), ("polarity", "affirmed"),
    ("reason", Json.arr #[Json.mkObj [("part", "p1")]]), ("target", Json.arr #[Json.mkObj [("mention", "m2")]]),
    ("marker", "m")].filter (!drop.contains ·.1)).filter (fun kv => !more.any (·.1 == kv.1))) ++ more)
def block (ls : List Json) : Json := Json.mkObj [("links", Json.arr ls.toArray)]
def links (n : Nat) : List Json := (List.range n).map (link s!"l{·}")

#guard [block [], block [link "l1", link "l2" [("share", "sole")]], block (links maxLinks)].all (recordOf · == none)
#guard [(Json.null, "1.1b"), (Json.mkObj [("links", Json.arr #[]), ("x", 1)], "1.1b"), ((block []).setObjVal! "links" 3, "1.1b"),
    (block (links (maxLinks + 1)), "1.1c"),
    (block [link "l1" [("x", 1)]], "1.1d"), (block [link "l1", link "l2" [] ["marker"]], "1.1d"),
    (block [link "l 1"], "1.1e"), (block [link "l1" [("id", 7)]], "1.1e"), (block [link "l1" [("marker", "a b")]], "1.1e"),
    (block [link "l1" [("reason", Json.arr #[Json.mkObj [("part", "p 1")]])]], "1.1e"),
    (block [link "l1" [("relation", "prevents")]], "1.1f"), (block [link "l1" [("relation", Json.arr #[])]], "1.1f"),
    (block [link "l1" [("polarity", "maybe")]], "1.1g"), (block [link "l1" [("share", "most")]], "1.1h"),
    (block [link "l1" [("target", "p2")]], "1.1i"), (block [link "l1" [("reason", Json.arr #[Json.mkObj [("unit", "p1")]])]], "1.1i"),
    (block [link "l1", link "l1"], "2.1b")].all fun (j, row) => roundTrips j row
-- the fault order: within a link, 7.1's rows in turn; an earlier link before a later one; decoding before 2.1b
#guard [(block [link "l1" [("relation", "x"), ("polarity", "x"), ("share", "x"), ("target", 1)]], "1.1f"),
    (block [link "l1" [("polarity", "x"), ("share", "x"), ("target", 1)]], "1.1g"),
    (block [link "l1" [("share", "x"), ("target", 1)]], "1.1h"), (block [link "l 1" [("relation", "x")]], "1.1e"),
    (block [link "l1" [("relation", "x"), ("y", 1)]], "1.1d"), (block [link "l1" [("polarity", "x")], link "l2" [("z", 1)]], "1.1g"),
    (block [link "l1", link "l1" [("polarity", "x")]], "1.1g"),
    (block (link "l1" :: links maxLinks), "1.1c")].all fun (j, row) => roundTrips j row
#guard (adapter (Json.mkObj [("purposes", 1), ("id", "c")])).toOption == some (Json.mkObj [("purposes", 1)]) &&
  (adapter (Json.mkObj [])).toOption == some (Json.mkObj [("purposes", Json.null)])

end VE.WireContract.Hooks.Purposes
