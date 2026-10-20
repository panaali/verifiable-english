import VE.Acts.Lexical
import VE.Grammar.Basic

/-! The act grammar's tokens, vocabulary and terminals (docs/spec/act-phrases.md 1.1, 1.2, 1.4, 5.1).

A document declares **frames** (a head and the markers that introduce its arguments and modifiers) and **adverbs**;
`framesOk` is the check of 1.4, run as `checkVocab`, which raises the first failing condition's text in the order of
D-31 (10). An act phrase is read as a list of tokens (`Lexical.Tok`, 1.1) by a grammar over the terminals `Term`.
The rule table, the act trees and the meaning (1.5, 5.2, 5.3) build on these.
-/

namespace VE.Acts
open Lexical (Tok)

/-- A head (a verb, or a noun after *has the right to*), its argument markers (`""`: the direct object, then
required), the markers whose joined fillers read as joined acts, and its modifier markers (1.4). -/
structure Frame where
  head : List String
  markers : List String
  split : List String
  mods : List String
  deriving DecidableEq, Repr

/-- The act grammar's vocabulary: the document's frames and adverbs (1.4). -/
structure Vocab where
  frames : List Frame
  adverbs : List String
  deriving DecidableEq, Repr

/-- The grammar's terminals over tokens (5.1); `never` accepts nothing. -/
inductive Term
  | subj | slot | fixed | comma | never
  | kw (w : String)
  | adv (ws : List String)
  | fill (excl : List String)
  deriving DecidableEq, Repr

def Term.accepts : Term → Tok → Bool
  | .subj, .slot 0 => true
  | .slot, .slot (_ + 1) => true
  | .fixed, .fixed _ => true
  | .comma, .comma => true
  | .kw w, .word v => v.toLower == w
  | .adv ws, .word v => ws.contains v.toLower
  | .fill ex, .word v => !ex.contains v.toLower
  | _, _ => false

instance : VE.Grammar.Accepts Term Tok := ⟨Term.accepts⟩

/-- A marker's words: split at spaces, empty pieces dropped (1.4). -/
def wordsOf (m : String) : List String := (m.splitOn " ").filter (· ≠ "")
/-- A lower-case word of letters, with inner `'` or `-`. -/
def wordOk (w : String) : Bool := VE.Norms.Wire.actWord w && w == w.toLower
/-- The first element that occurs again later in the list. -/
def firstDup : List String → Option String
  | [] => none
  | x :: xs => if xs.contains x then some x else firstDup xs

/-- The conditions of 1.4, checked in the order of D-31; the first failing one's text. -/
def checkVocab (V : Vocab) : Except String Unit := do
  let fs := V.frames
  let hd (f : Frame) : String := " ".intercalate f.head
  let resv := ["and", "or", "nor", "to", "be"] ++ Lexical.clauseWords
  let mresv := ["and", "or", "nor", "be"] ++ Lexical.clauseWords
  let ms (f : Frame) : List String := (f.markers ++ f.mods).filter (· ≠ "")
  let mwords := fs.flatMap (fun f => (ms f).flatMap wordsOf)
  if 128 < fs.length then throw "ResourceLimit: more than 128 frames"
  if fs.any (·.head.isEmpty) then throw "InvalidInput: a frame has an empty head"
  for f in fs do
    if let some w := f.head.find? (!wordOk ·) then
      throw s!"InvalidInput: frame '{hd f}' has the head word '{w}', which is not a lower-case word of letters"
  for f in fs do
    if let some w := f.head.find? resv.contains then throw s!"InvalidInput: frame '{hd f}' has the reserved head word '{w}'"
  if let some h := firstDup (fs.map hd) then throw s!"InvalidInput: frame '{h}' is declared twice"
  for f in fs do
    if let some g := fs.find? (fun g => g.head != f.head && f.head.isPrefixOf g.head) then
      throw s!"InvalidInput: frame heads '{hd f}' and '{hd g}' overlap: one begins the other"
  for f in fs do
    if let some m := firstDup f.markers then throw s!"InvalidInput: frame '{hd f}' lists the marker '{m}' twice"
  for f in fs do
    if let some m := firstDup f.mods then throw s!"InvalidInput: frame '{hd f}' lists the modifier marker '{m}' twice"
  for f in fs do
    if let some m := f.split.find? (!f.markers.contains ·) then
      throw s!"InvalidInput: frame '{hd f}' splits '{m}', which is not one of its markers"
  for f in fs do
    if f.mods.contains "" then throw s!"InvalidInput: frame '{hd f}' has an empty modifier marker"
  for f in fs do
    if let some m := f.mods.find? f.markers.contains then
      throw s!"InvalidInput: frame '{hd f}' lists '{m}' both as a marker and as a modifier marker"
  for f in fs do
    if let some m := (ms f).find? (fun m => m != " ".intercalate (wordsOf m) || wordsOf m == []) then
      throw s!"InvalidInput: frame '{hd f}' has the marker '{m}', which is not words separated by single spaces"
  for f in fs do
    if let some w := ((ms f).flatMap wordsOf).find? (!wordOk ·) then
      throw s!"InvalidInput: frame '{hd f}' has the marker word '{w}', which is not a lower-case word of letters"
  for f in fs do
    if let some w := ((ms f).flatMap wordsOf).find? mresv.contains then
      throw s!"InvalidInput: frame '{hd f}' has the reserved marker word '{w}'"
  for f in fs do
    for m in ms f do
      if let some n := (ms f).find? (fun n => n != m && (wordsOf m).isPrefixOf (wordsOf n)) then
        throw s!"InvalidInput: frame '{hd f}' has the markers '{m}' and '{n}', and one begins the other"
  if let some a := firstDup V.adverbs then throw s!"InvalidInput: the adverb '{a}' is declared twice"
  if let some a := V.adverbs.find? (fun a => !wordOk a || resv.contains a) then
    throw s!"InvalidInput: the adverb '{a}' is not a lower-case word of letters, or is reserved"
  if let some a := V.adverbs.find? (fun a => mwords.contains a || fs.any (·.head.contains a)) then
    throw s!"InvalidInput: the adverb '{a}' is also a marker or head word"
  for f in fs do
    if let some w := f.head.head? then
      if mwords.contains w then throw s!"InvalidInput: frame '{hd f}' begins with the marker word '{w}'"

/-- The vocabulary check of 1.4. -/
def framesOk (V : Vocab) : Bool := (checkVocab V).isOk

end VE.Acts
