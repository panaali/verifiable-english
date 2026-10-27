import VE.Scope.Govern
import VE.Discourse.Wire
import VE.Attribution.Status

/-! Scope's front matter and statuses in the document mode (scope@0, docs/spec/scope.md 1.6, 3 and 5.2; SC-1b): the
    `scope` block decoded into governors, list names and anchors, with the layout read from the source bytes of
    exactly the document's units (`decodeBlock`), and the fold of a governor unit's status into the document mode's
    answer (`governorStatus`, `foldGovernors`). The document mode calls them (`VE/Service/Document.lean`). -/

namespace VE.Scope
open Lean
open VE.Reports (Status)

/-- A governor counts under the weakest status of what it governs, never a stronger one. -/
def governorStatus (st : String → Option Status) (us : List String) : Option Status :=
  if us.isEmpty then none else (us.mapM st).map VE.Reports.foldStatus

/-! The block (3): unknown members are refused and optional members are absent, never `null`. -/

def wireFault (path form : String) : String := s!"InvalidInput: scope@0 {path} must be {form}"

def membersIn (path : String) (known : List String) (j : Json) : Except String (List (String × Json)) := do
  let ms ← (VE.Bridge.fields j).mapError fun _ => wireFault path "an object"
  if let some (k, _) := ms.find? (!known.contains ·.1) then throw s!"InvalidInput: scope@0 unknown member {path}.{k}"
  if let some (k, _) := ms.find? (·.2 == .null) then throw (wireFault s!"{path}.{k}" "absent, not null")
  pure ms

def memberOf (path : String) (ms : List (String × Json)) (k : String) : Except String Json :=
  match ms.lookup k with
  | some v => pure v
  | none => throw (wireFault s!"{path}.{k}" "present")

def textOf (path : String) : Json → Except String String
  | .str s => pure s
  | _ => throw (wireFault path "a string")

def textsOf (path : String) (j : Json) : Except String (List String) :=
  (VE.Bridge.strings j).mapError fun _ => wireFault path "an array of strings"

def decodeReach (path : String) : Json → Except String Reach
  | .str "frontier" => pure .frontier
  | j => match members j with
    | [("list", .str u)] => pure (.list u)
    | [("list_name", .str n)] => pure (.listName n)
    | [("anchor", .str a)] => pure (.anchor a)
    | [("label", .str i)] => pure (.label i)
    | [("rules", ns)] => .rules <$> textsOf s!"{path}.rules" ns
    | _ => throw (wireFault path "a reach")

def decodeEffect (path : String) : Json → Except String Effect
  | .str "precedes" => pure .precedes
  | .str "yields" => pure .yields
  | .str "title" => pure .title
  | j => match members j with
    | [("frame", p)] => pure (.frame p)
    | [("reguard", c)] => pure (.reguard c)
    | [("carve_out", c)] => pure (.carveOut c)
    | _ => throw (wireFault path "an effect")

def decodeGovernor (j : Json) : Except String Governor := do
  let ms ← membersIn "governors" ["id", "unit", "reach", "effect", "units"] j
  let id ← textOf "governors.id" (← memberOf "governors" ms "id")
  let p := s!"governors.{id}"
  let reach ← decodeReach s!"{p}.reach" (← memberOf p ms "reach")
  let units ← match ms.lookup "units", reach with
    | some v, _ => textsOf s!"{p}.units" v
    | none, .frontier => pure []
    | none, _ => throw (wireFault s!"{p}.units" "present")
  pure { id, unit := ← textOf s!"{p}.unit" (← memberOf p ms "unit"), reach, units,
         effect := ← decodeEffect s!"{p}.effect" (← memberOf p ms "effect") }

/-- A list name: `lead` and `unit` are scope's; the rest is discourse's `ContentName`, decoded by discourse. -/
def decodeListName (j : Json) : Except String (VE.Discourse.ContentName × String × String) := do
  let ms ← membersIn "list_names" ["name", "units", "scope", "lead", "unit"] j
  let cn ← VE.Discourse.Wire.decodeContentName (Json.mkObj (ms.filter (!["lead", "unit"].contains ·.1)))
  let p := s!"list_names.{cn.name}"
  pure (cn, ← textOf s!"{p}.lead" (← memberOf p ms "lead"), ← textOf s!"{p}.unit" (← memberOf p ms "unit"))

def listMember (ms : List (String × Json)) (k : String) : Except String (List Json) :=
  match ms.lookup k with
  | some (.arr xs) => pure xs.toList
  | some _ => throw (wireFault k "an array")
  | none => pure []

/-- The block's governors, list names and anchors. -/
def decodeParts (block : Json) :
    Except String (List Governor × List (VE.Discourse.ContentName × String × String) × List VE.Discourse.Anchor) := do
  let ms ← membersIn "scope" ["version", "list_names", "anchors", "governors"] block
  unless ms.lookup "version" == some (.str "scope@0") do throw (wireFault "version" "\"scope@0\"")
  pure (← (← listMember ms "governors").mapM decodeGovernor, ← (← listMember ms "list_names").mapM decodeListName,
    ← (← listMember ms "anchors").mapM VE.Discourse.Wire.decodeAnchor)

/-- A unit's span as written, clamped to the source (a span the document mode refuses reads as empty). -/
def spanIn (size : Nat) (u : Json) : Nat × Nat :=
  match u.getObjValD "span" with
  | .arr #[a, b] => let e := min ((b.getNat?).toOption.getD 0) size; (min ((a.getNat?).toOption.getD 0) e, e)
  | _ => (0, 0)

/-- The layout of exactly the document's units, read from the source bytes (1.2). -/
def layoutOf (doc : Json) (source : String) : List VE.Layout.Unit :=
  VE.Layout.ofSource source ((unitsOf doc).map fun u => (idOf u, spanIn source.utf8ByteSize u))

/-- The scope block of a front matter `front` (the complete document) over its source, read by the chain's
    environment `re`. -/
def decodeBlock (front : Json) (source : String) (re : VE.Readings.Wire.ReadingsEnvironment) : Except String SDoc :=
  (decodeParts (front.getObjValD "scope")).map fun (governors, listNames, anchors) =>
    { layout := layoutOf front source, doc := front, block := front.getObjValD "scope", governors, listNames,
      anchors, re }

/-! The document mode's fold (1.6) -/

/-- A unit status of the document mode's answer: W2's four (`Discourse.Loader.statuses`); no unit is UNKNOWN. -/
def statusOf : String → Option Status
  | "UNFORMALISED" => some .unformalised
  | "OPEN" => some .open
  | "LABELLED" => some .labelled
  | "CHECKED" => some .checked
  | _ => none

/-- The content-changing governors a unit hosts. -/
def changers (D : SDoc) (u : String) : List Governor :=
  D.governors.filter fun g => g.unit == u && (isFrame g.effect || unary g.effect)

/-- The bytes of the answer's units by status, in order of first appearance. -/
def byStatus (units : List Json) : List (String × Json) :=
  (units.foldl (fun (acc : List (String × Nat)) x =>
    let k := (x.getObjValD "status").getStr?.toOption.getD ""
    let n := match x.getObjValD "span" with
      | .arr #[s, e] => (e.getNat?).toOption.getD 0 - (s.getNat?).toOption.getD 0
      | _ => 0
    if acc.any (·.1 == k) then acc.map fun (k', m) => (k', if k' == k then m + n else m) else acc ++ [(k, n)])
    []).map fun (k, n) => (k, toJson n)

/-- The document mode's answer row with the status of each governor unit without content, meaning `specified`,
    that hosts a content-changing governor folded by `governorStatus` over the statuses before the fold (none:
    UNFORMALISED), and the coverage's bytes by status counted again. -/
def foldGovernors (D : SDoc) (a : Json) : Json :=
  let units := match a.getObjValD "units" with
    | .arr xs => xs.toList
    | _ => []
  let st (u : String) : Option Status :=
    ((units.find? (idOf · == u)).bind fun x => (x.getObjValD "status").getStr?.toOption).bind statusOf
  let fold (x : Json) : Json :=
    let gs := changers D (idOf x)
    if gs.isEmpty || (x.getObjVal? "content").isOk || x.getObjValD "meaning" != .str "specified" then x
    else x.setObjVal! "status" (.str ((governorStatus st
      (gs.flatMap fun g => (covered D g.reach).toOption.getD [])).getD .unformalised).render)
  let folded := units.map fold
  Json.mkObj [("id", a.getObjValD "id"), ("status", a.getObjValD "status"),
    ("document_id", a.getObjValD "document_id"), ("source_id", a.getObjValD "source_id"),
    ("source", a.getObjValD "source"), ("units", .arr folded.toArray),
    ("coverage", (a.getObjValD "coverage").setObjVal! "bytes_by_status" (Json.mkObj (byStatus folded)))]

end VE.Scope
