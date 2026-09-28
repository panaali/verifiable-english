import VE.Discourse.WellFormed
import VE.Route.Run

/-! # The discourse wire form (docs/spec/discourse.md 3.1, 3.3, 3.5)

A strict decoder for the `discourse` block of a `ve-document@2` document: unknown fields
are rejected and optional fields are absent, never `null`. Mention spans arrive as prose
byte ranges and are mapped to token ranges of their unit by the lexer (a named trust
boundary); a byte range that does not start and end on token boundaries of its unit is
`InvalidInput`. The Lean document object is W2's (`units`, `graph`, `lemmas`,
`open_terms`, `reading_sets`, `narrowings`) plus `format`, `prose` and `discourse`.

Lean wire conventions that differ from the Python front matter (recorded in
lean/DISCOURSE.md): a group's `reading` and a constraint's readings are `original_index`
numbers (the Python loader maps reading ids to indexes); an import's stored document is the
optional string `content` (the JSON text of a case `{"environment", "document"}`) instead of
a sibling file name; a predicate target's `version` pin is checked by W3 and not carried
into the Lean target. -/
namespace VE.Discourse.Wire
open Lean
open VE.Bridge (stringField strings fields displayFields)
open VE.English (Tok)

def nullError : String := "InvalidInput: null in discourse block"

/-- An optional field: absent is `none`; `null` is rejected. -/
def opt (j : Json) (k : String) : Except String (Option Json) :=
  match j.getObjVal? k with
  | .ok .null => .error nullError
  | .ok v => .ok (some v)
  | .error _ => .ok none

def optString (j : Json) (k : String) : Except String (Option String) := do
  match ← opt j k with
  | some v => some <$> v.getStr?
  | none => pure none

def optList (j : Json) (k : String) : Except String (List Json) := do
  match ← opt j k with
  | some v => pure (← v.getArr?).toList
  | none => pure []

def optStrings (j : Json) (k : String) : Except String (List String) := do
  match ← opt j k with
  | some v => strings v
  | none => pure []

def decodeSpan (j : Json) : Except String (Nat × Nat) := do
  match (← j.getArr?).toList with
  | [a, b] => pure (← a.getNat?, ← b.getNat?)
  | _ => throw "InvalidInput: span"

def decodeAnchor (j : Json) : Except String Anchor := do
  displayFields j ["id", "kind", "label", "span"] ["parent", "edition", "exports"]
  let kind ← stringField j "kind"
  unless ["document", "section", "clause", "item", "article"].contains kind do
    throw s!"InvalidInput: anchor kind {kind}"
  pure { id := ← stringField j "id", kind, parent := ← optString j "parent", label := ← stringField j "label",
         span := ← decodeSpan (← j.getObjVal? "span"), edition := ← optString j "edition",
         exports := ← optStrings j "exports" }

def decodeName (j : Json) : Except String Name := do
  displayFields j ["constant", "display", "scope"] ["aliases"]
  pure { constant := ← stringField j "constant", display := ← stringField j "display",
         scope := ← stringField j "scope", aliases := ← optStrings j "aliases" }

def decodeContentName (j : Json) : Except String ContentName := do
  displayFields j ["name", "units", "scope"] []
  pure { name := ← stringField j "name", units := ← strings (← j.getObjVal? "units"),
         scope := ← stringField j "scope" }

def decodeForm : String → Except String Form
  | "pronoun" => .ok .pronoun
  | "demonstrative" => .ok .demonstrative
  | "definite" => .ok .definite
  | "ordinal_pair" => .ok .ordinalPair
  | "such" => .ok .such
  | "possessive" => .ok .possessive
  | "plural" => .ok .plural
  | "section_ref" => .ok .sectionRef
  | "definition_ref" => .ok .definitionRef
  | "document_name" => .ok .documentName
  | "citation" => .ok .citation
  | "navigation" => .ok .navigation
  | f => .error s!"InvalidInput: form {f}"

def decodeTargetKind : String → Except String TargetKind
  | "entity" => .ok .entity
  | "predicate" => .ok .predicate
  | "unit" => .ok .unit
  | "anchor" => .ok .anchor
  | "rule" => .ok .rule
  | "claim" => .ok .claim
  | "document" => .ok .document
  | k => .error s!"InvalidInput: target kind {k}"

def decodeReading : String → Except String Reading
  | "assertive" => .ok .assertive
  | "presuppositional" => .ok .presuppositional
  | "distributive" => .ok .distributive
  | r => .error s!"InvalidInput: reading {r}"

def decodeTarget (j : Json) : Except String Target := do
  displayFields j ["kind"] ["name", "version", "members", "pair", "units", "content_name"]
  let kind ← decodeTargetKind (← stringField j "kind")
  let version ← match ← opt j "version" with
    | some v => some <$> v.getNat?
    | none => pure none
  let pair ← match ← opt j "pair" with
    | some v => match ← strings v with
      | [a, b] => pure (some (a, b))
      | _ => throw "InvalidInput: pair"
    | none => pure none
  pure { kind, name := ← optString j "name", version := if kind == .predicate then none else version,
         members := ← optStrings j "members", pair, units := ← optStrings j "units",
         contentName := ← optString j "content_name" }

/-- A mention with its prose byte span (mapped to tokens by `toTokenSpans`). -/
def decodeMention (j : Json) : Except String Mention := do
  displayFields j ["id", "unit", "span", "form", "target"] ["restriction", "reading", "presupposition_unit"]
  let restriction ← match ← opt j "restriction" with
    | some r => some <$> VE.Bridge.decodeFormula 64 r
    | none => pure none
  let reading ← match ← optString j "reading" with
    | some r => some <$> decodeReading r
    | none => pure none
  pure { id := ← stringField j "id", unit := ← stringField j "unit", span := ← decodeSpan (← j.getObjVal? "span"),
         form := ← decodeForm (← stringField j "form"), target := ← decodeTarget (← j.getObjVal? "target"),
         restriction, reading, presuppositionUnit := ← optString j "presupposition_unit" }

def decodeRefers (j : Json) : Except String DocRefers := do
  match j with
  | .str "self" => pure .self
  | _ =>
    match (← fields j) with
    | [("embedded", .str u)] => pure (.embedded u)
    | [("import", .str k)] => pure (.imported k)
    | [("part", .str a)] => pure (.part a)
    | _ => throw "InvalidInput: refers"

def decodeDocName (j : Json) : Except String DocName := do
  displayFields j ["name", "display", "refers", "version"] ["author", "supersedes", "scope", "source_id", "document_id"]
  pure { name := ← stringField j "name", display := ← strings (← j.getObjVal? "display"),
         refers := ← decodeRefers (← j.getObjVal? "refers"), version := ← (← j.getObjVal? "version").getNat?,
         author := ← optString j "author", supersedes := ← optStrings j "supersedes", scope := ← optString j "scope",
         sourceId := ← optString j "source_id", documentId := ← optString j "document_id" }

def decodeImport (key : String) (j : Json) : Except String Import := do
  displayFields j ["source_id", "document_id"] ["content"]
  pure { key, sourceId := ← stringField j "source_id", documentId := ← stringField j "document_id",
         bytes := (← optString j "content").map String.toUTF8 }

def decodeTriple (j : Json) : Except String (String × Nat × Nat) := do
  match (← j.getArr?).toList with
  | [.str s, v, i] => pure (s, ← v.getNat?, ← i.getNat?)
  | _ => throw "InvalidInput: reading triple"

def decodeGroup (j : Json) : Except String Group := do
  displayFields j ["set", "version", "reading", "spans"] []
  pure { set := ← stringField j "set", version := ← (← j.getObjVal? "version").getNat?,
         reading := ← (← j.getObjVal? "reading").getNat?, spans := ← strings (← j.getObjVal? "spans") }

def decodeConstraint (j : Json) : Except String Constraint := do
  displayFields j ["kind", "a", "b"] []
  let kind ← match ← stringField j "kind" with
    | "requires" => pure ConstraintKind.requires
    | "excludes" => pure ConstraintKind.excludes
    | k => throw s!"InvalidInput: constraint kind {k}"
  pure { kind, a := ← decodeTriple (← j.getObjVal? "a"), b := ← decodeTriple (← j.getObjVal? "b") }

def decodeValidity (j : Json) : Except String Validity := do
  displayFields j ["unit", "document", "holds"] []
  pure { unit := ← stringField j "unit", document := ← stringField j "document",
         holds := ← (← j.getObjVal? "holds").getBool? }

/-- The `discourse` block, strictly. -/
def decodeManifest (j : Json) : Except String Manifest := do
  displayFields j ["version", "definitions_version", "document_sort", "anchors", "names", "mentions"]
    ["content_names", "documents", "imports", "groups", "constraints", "validity", "self_truth", "choices"]
  unless (← stringField j "version") == "ve.discourse@1" do throw "InvalidInput: discourse version"
  let imports ← match ← opt j "imports" with
    | some v => (← fields v).mapM fun (k, x) => decodeImport k x
    | none => pure []
  pure { definitionsVersion := ← stringField j "definitions_version", documentSort := ← stringField j "document_sort",
         anchors := ← (← (← j.getObjVal? "anchors").getArr?).toList.mapM decodeAnchor,
         names := ← (← (← j.getObjVal? "names").getArr?).toList.mapM decodeName,
         contentNames := ← (← optList j "content_names").mapM decodeContentName,
         mentions := ← (← (← j.getObjVal? "mentions").getArr?).toList.mapM decodeMention,
         documents := ← (← optList j "documents").mapM decodeDocName,
         imports, groups := ← (← optList j "groups").mapM decodeGroup,
         constraints := ← (← optList j "constraints").mapM decodeConstraint,
         validity := ← (← optList j "validity").mapM decodeValidity,
         selfTruth := ← optStrings j "self_truth",
         choices := ← (← optList j "choices").mapM decodeTriple }

/-! ## Units, tokens and spans -/

/-- The tokens of the prose whose byte range lies in `[a, b)`. -/
def tokensIn (toks : List (String × Nat × Nat)) (a b : Nat) : List (String × Nat × Nat) :=
  toks.filter fun t => a ≤ t.2.1 && t.2.2 ≤ b

/-- Map a mention's prose byte range to the token range of its unit. -/
def tokenSpan (unitToks : List (String × Nat × Nat)) (m : Mention) : Except String (Nat × Nat) :=
  let starts := unitToks.zipIdx.filter fun (t, _) => t.2.1 == m.span.1
  let ends := unitToks.zipIdx.filter fun (t, _) => t.2.2 == m.span.2
  match starts, ends with
  | [(_, i)], [(_, j)] => if i ≤ j then .ok (i, j + 1) else .error s!"InvalidInput: mention {m.id} span"
  | _, _ => .error s!"InvalidInput: mention {m.id} span"

/-- The prose, its tokens and the per-unit token lists. -/
structure Source where
  prose : String
  toks : List (String × Nat × Nat)

def Source.unitToks (src : Source) (D : VE.Route.Admission.Doc) (u : String) : Option (List (String × Nat × Nat)) :=
  (unitOf D u).map fun x => tokensIn src.toks x.start x.stop

def Source.text (src : Source) (D : VE.Route.Admission.Doc) (u : String) : Option (List Tok) :=
  (src.unitToks D u).map (List.map fun t => .word t.1)

/-- Every mention's span as a token range of its unit. -/
def toTokenSpans (src : Source) (D : VE.Route.Admission.Doc) (K : Manifest) : Except String Manifest := do
  let ms ← K.mentions.mapM fun m => do
    match src.unitToks D m.unit with
    | some ts => pure { m with span := ← tokenSpan ts m }
    | none => throw s!"InvalidInput: mention {m.id} names an unknown unit"
  pure { K with mentions := ms }

/-! ## Identity -/

def identityVersion (profiles : List String) : String := VE.Route.Wire.identityVersion profiles

/-- `source_id`: the fingerprint of the prose bytes (profile-independent). -/
def sourceId (prose : String) : String :=
  VE.CertificateWire.sha256 (("ve-source-v0.2\n" ++ prose).toUTF8)

/-- The `@2` document identity: the `@1` payload under the new domain tag; the discourse
block is inside the metadata, so every manifest entry is identity-bound. -/
def documentId2 (front : Json) (prose : String) (fences : List (String × String)) : Except String String :=
  VE.CertificateWire.digest "ve-document@2\n" (Json.mkObj [("metadata", front), ("source", .str prose),
    ("fences", Json.arr (fences.map fun (a, b) => Json.arr #[.str a, .str b]).toArray)])

/-- The document object without its prose and removable weights. -/
def frontMatter (j : Json) : Json :=
  match j with
  | .obj kvs => Json.mkObj (kvs.toList.filter fun (k, _) => k != "prose" && k != "weights")
  | _ => j

def prose (j : Json) : String := (j.getObjValD "prose").getStr?.toOption.getD ""

def fences (_j : Json) : List (String × String) := []

end VE.Discourse.Wire
