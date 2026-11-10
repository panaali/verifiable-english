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
open VE.Purposes (decodeBlock decodeRef decodeSide idOf linkFieldsOk linksOf maxLinks shareOf wordOf)

/-- A value as the decoder's texts quote it (`idOf`, `wordOf`): a string as it is, anything else compressed. -/
def shown : Json → String
  | .str s => s
  | j => j.compress

/-- 7.1's row for a side `decodeSide` refuses, at its first ref `decodeRef` refuses: 1.1e for a part or mention whose
string is not a token, 1.1i for anything else; `none` for a side the decoder accepts. -/
def sideMember (lid : String) (side : Json) : Option (String × List (String × Json)) :=
  let other := some ("1.1i", [("link", .str lid)])
  match decodeSide lid side, side with
  | .ok _, _ => none
  | .error _, .arr rs => match rs.toList.find? (fun r => !(decodeRef lid r).isOk) with
    | some r => match VE.Bridge.fields r with
      | .ok [(k, .str i)] => if k == "part" || k == "mention" then some ("1.1e", [("id", .str i)]) else other
      | _ => other
    | none => other
  | .error _, _ => other

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
    else (sideMember lid (v "reason") <|> sideMember lid (v "target")).getD ("1.1i", [("link", .str lid)])

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

theorem decodeLinks_length {n : Nat} {js : List Json} {ls : List VE.Purposes.Link}
    (h : VE.Purposes.decodeLinks n js = .ok ls) : ls.length = js.length := by
  induction js generalizing n ls with
  | nil => simp [VE.Purposes.decodeLinks, pure, Except.pure] at h; subst h; rfl
  | cons j js ih =>
    simp only [VE.Purposes.decodeLinks] at h
    cases h1 : VE.Purposes.decodeLink n j with
    | error e => simp [h1, bind, Except.bind] at h
    | ok L =>
      cases h2 : VE.Purposes.decodeLinks (n + 1) js with
      | error e => simp [h1, h2, bind, Except.bind] at h
      | ok ls' => simp [h1, h2, bind, Except.bind, pure, Except.pure] at h; subst h; simp [ih h2]

theorem decodeBlock_length {j : Json} {B : VE.Purposes.Block} (h : decodeBlock j = .ok B) :
    B.links.length ≤ maxLinks := by
  unfold decodeBlock at h
  cases h1 : linksOf j with
  | error e => simp [h1, bind, Except.bind] at h
  | ok ls =>
    simp only [h1, bind, Except.bind] at h
    split at h
    · obtain ⟨ls', h2, h3⟩ := VE.Purposes.map_ok h
      subst h3
      simp [decodeLinks_length h2]
      omega
    · cases h

/-- 2.1b reads `VE.Purposes.check`: when `purposes_ids` names it, the block decodes and `check` refuses it with 7.2's
row 2 text, whatever the checked view. -/
theorem purposes_ids_reads_check (root : Json) (items : List Pointer) (U : VE.Purposes.Units)
    (h : classifier "purposes_ids" root items = .fail "2.1b" []) :
    ∃ B, decodeBlock (purposesOf root) = .ok B ∧
      VE.Purposes.check U B = .error "InvalidPurposes: two links have the same id" := by
  cases hB : decodeBlock (purposesOf root) with
  | error e => simp [classifier, hB] at h
  | ok B =>
    refine ⟨B, rfl, ?_⟩
    have hn : ¬ (B.links.map (·.id)).Nodup := by
      intro hn; simp [classifier, hB, hn] at h
    have hl := decodeBlock_length hB
    simp [VE.Purposes.check, VE.Route.Gate.require, hl, hn, bind, Except.bind]

def registered : List String := ["purposes_block", "purposes_ids"]

#guard Tables.Purposes.table.hookNames.all registered.contains
#guard Tables.Purposes.table.revision == 1  -- purposes@0.json's revision: a new revision updates this pin
-- every entry is a classifier check, so `hooks`' predicate and view (the engine's defaults) are never called
#guard Tables.Purposes.table.phases.all fun p => p.entries.all fun
  | .check c => match c.kind with | .classifier .. => true | _ => false
  | _ => false

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
    (block [link "l1" [("reason", Json.arr #[Json.mkObj [("unit", "p 1")]])]], "1.1i"),
    (block [link "l1" [("reason", Json.arr #[Json.mkObj [("part", 7)]])]], "1.1i"),
    (block [link "l1" [("reason", "x"), ("target", Json.arr #[Json.mkObj [("part", "a b")]])]], "1.1i"),
    (block [link "l1" [("reason", Json.arr #[Json.mkObj [("unit", "p1")], Json.mkObj [("part", "x y")]])]], "1.1i"),
    (block [link "l1" [("target", Json.arr #[Json.mkObj [("mention", "m 2")]])]], "1.1e"),
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
