import VE.Senses.Dictionary
import VE.Bridge
import VE.CertificateWire

/-! The pack decoder and the dictionary identity (docs/spec/senses.md 2.2 and 2.7, plan 2.7; batch B2's
Lean half).

A pack file is `{"format": "ve.sense-pack@1", "name", "sorts", "senses"}`; a sort has `name`, `noun`,
`plural`, `description` and `letter`; a sense has `word`, `index`, `gloss`, `description`, `kinds`,
`wording` and, optionally, `negative`. The text is read by the restricted JSON boundary
(`VE.JsonInput.parse`: no null, no duplicate key, no fraction, a bounded depth); a missing field, an
unknown field, a field of another type, or a `true` where a number stands is refused. The decoder decides
the shape only: W1 to W7 are `Dictionary.failures`, run by the reader.

`dictionaryId D` is the digest, under the domain `ve-senses-dictionary-v1`, of the canonical JSON of the
packs (name and content, re-encoded from the decoded values, so whitespace and key order do not count)
and of the own senses, in order.
-/

namespace VE.Senses
open Lean

def packFormat : String := "ve.sense-pack@1"

/-- The fields of an object are the `required` ones and some of the `optional` ones, nothing else. -/
def checkFields (j : Json) (required optional : List String) : Except String Unit := do
  let actual := (← VE.Bridge.fields j).map (·.1)
  for k in actual do
    unless required.contains k || optional.contains k do throw s!"unknown field {k}"
  for k in required do
    unless actual.contains k do throw s!"missing field {k}"

/-- A natural number: a JSON number, never a Boolean or a string. -/
def natOf (j : Json) : Except String Nat :=
  match j with
  | .num _ => j.getNat?
  | _ => throw "expected a natural number"

def decodeSense (j : Json) : Except String Sense := do
  checkFields j ["word", "index", "gloss", "description", "kinds", "wording"] ["negative"]
  let negative ← match j.getObjVal? "negative" with
    | .ok n => do pure (some (← n.getStr?))
    | .error _ => pure none
  pure { word := ← VE.Bridge.stringField j "word", index := ← natOf (← j.getObjVal? "index"),
         gloss := ← VE.Bridge.stringField j "gloss", description := ← VE.Bridge.stringField j "description",
         kinds := ← VE.Bridge.strings (← j.getObjVal? "kinds"), wording := ← VE.Bridge.stringField j "wording",
         negative }

def decodePackSort (j : Json) : Except String PackSort := do
  checkFields j ["name", "noun", "plural", "description", "letter"] []
  pure { name := ← VE.Bridge.stringField j "name", noun := ← VE.Bridge.stringField j "noun",
         plural := ← VE.Bridge.stringField j "plural", description := ← VE.Bridge.stringField j "description",
         letter := ← VE.Bridge.stringField j "letter" }

def decodePack (j : Json) : Except String Pack := do
  checkFields j ["format", "name", "sorts", "senses"] []
  unless (← VE.Bridge.stringField j "format") == packFormat do throw s!"the format is not {packFormat}"
  pure { name := ← VE.Bridge.stringField j "name",
         sorts := ← (← (← j.getObjVal? "sorts").getArr?).toList.mapM decodePackSort,
         senses := ← (← (← j.getObjVal? "senses").getArr?).toList.mapM decodeSense }

/-- A pack from the bytes of its file, as text. -/
def decodePackText (text : String) : Except String Pack := do
  decodePack (← VE.JsonInput.parse text)

def Sense.toJson (s : Sense) : Json :=
  Json.mkObj ([("word", .str s.word), ("index", Lean.toJson s.index), ("gloss", .str s.gloss),
    ("description", .str s.description), ("kinds", Lean.toJson s.kinds), ("wording", .str s.wording)] ++
    match s.negative with
    | some n => [("negative", .str n)]
    | none => [])

def PackSort.toJson (t : PackSort) : Json :=
  Json.mkObj [("name", .str t.name), ("noun", .str t.noun), ("plural", .str t.plural),
    ("description", .str t.description), ("letter", .str t.letter)]

def Pack.toJson (p : Pack) : Json :=
  Json.mkObj [("format", .str packFormat), ("name", .str p.name),
    ("sorts", .arr (p.sorts.map PackSort.toJson).toArray), ("senses", .arr (p.senses.map Sense.toJson).toArray)]

/-- The canonical JSON the dictionary identity digests: the packs (name and content) and the own senses. -/
def Dictionary.toJson (D : Dictionary) : Json :=
  Json.mkObj [("packs", .arr (D.packs.map fun p => Json.arr #[.str p.name, p.toJson]).toArray),
    ("own", .arr (D.own.map Sense.toJson).toArray)]

/-- The dictionary identity (plan 2.7). The canonical form of `Dictionary.toJson` has no null, no
fraction and a depth of five, so the digest has no error; the fallback is never taken. -/
def dictionaryId (D : Dictionary) : String :=
  match VE.CertificateWire.digest "ve-senses-dictionary-v1\n" D.toJson with
  | .ok d => d
  | .error _ => ""

end VE.Senses
