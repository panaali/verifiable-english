import VE.EnglishGrammar.Read

/-! The answer's sentences and their all-derivations gate (docs/spec/question-answering.md 3.3; W7; review B of the
Q1 reviews, Astra: the A0 line).

`answerFrames` registers every frame of spec 3.3, each as fixed text and slots. `frameReadings line` lists every
derivation of a line from every registered frame, a slot taking any non-empty text; an optional part of a frame
(`[...]` in 3.3) is a slot's text, so it needs no frame of its own. A line is shown as frame `f` only when it has
exactly one derivation and that derivation is `f`'s (`gated`). A0's one slot is then read back by E2's reader:
the line is shown only when `<asked sentence>.` reads exactly `[(φ, false)]` (`askedGate`, `askedGate_sound`). The
frames' leads are pairwise not prefixes of each other (`frames_leads`), which is why each frame gives one derivation.
-/

namespace VE.Question
open VE.EnglishGrammar

inductive Piece
  | lit (s : String)
  | slot
  /-- A number slot: one or more decimal digits (a sentence's display number, a count), a closed class (spec 3.3),
      so a line that names two sentences has one derivation. -/
  | num
  /-- A citation is made of decimal sentence numbers, joined with commas and `and`. -/
  | citation
  /-- The closed set of answer leads after an R1 reading name. -/
  | answerLead
  deriving DecidableEq, Repr

/-- The frames of spec 3.3 in its order, each `<...>` slot (with any optional part after it) one `slot`, a sentence
    number or a count a `num`. -/
def answerFrames : List (String × List Piece) :=
  [("A0", [.lit "You asked whether ", .slot, .lit "."]),
   ("A1", [.lit "Yes."]),
   ("A2", [.lit "No. The document rules this out."]),
   ("A3", [.lit "The text does not settle this."]),
   ("A4", [.lit "Not necessarily."]),
   ("A5", [.lit "VE could not decide this."]),
   ("C1", [.lit "Sentence ", .num, .lit " says: \"", .slot, .lit "\""]),
   ("C2", [.lit "Sentences ", .citation, .lit " say when ", .slot, .lit "."]),
   ("C3", [.lit "VE also used what the document's word list declares."]),
   ("C4", [.lit "VE also used its rule that whatever must be done may be done: ", .slot]),
   ("S1", [.lit "Here is a situation the document allows where it fails: ", .slot, .lit "."]),
   ("S2", [.lit "Here is a situation where the answer depends on what the text leaves unsaid: ", .slot, .lit "."]),
   ("S2p", [.lit "The text does not say whether ", .slot, .lit "."]),
   ("S3", [.lit "Here the text does not say whether ", .slot, .lit "; this situation answers 'no'."]),
   ("R1", [.lit "If sentence ", .num, .lit " means \"", .slot, .lit ", ", .answerLead, .lit "."]),
   ("R2", [.lit "Every way of reading the document gives this answer."]),
   ("U1", [.lit "VE did not use ", .num, .lit " sentences of this document that it could not read formally: ",
     .slot, .lit "."]),
   ("X1", [.lit "The document's rules or defaults conflict in this situation, so VE cannot answer: ", .slot,
     .lit "."]),
   ("X2", [.lit "VE could not check that the rules never contradict each other."]),
   ("X3", [.lit "The sentences of this document cannot all be true together, so VE does not answer questions about it."]),
   ("X4", [.lit "VE found neither a proof nor a situation where it fails, within its limits."]),
   ("X5", [.lit "There are more than 64 ways to read this document's open sentences. VE did not check them all."]),
   ("X6", [.lit "VE found a proof but could not check that the document's sentences can all be true together, so it does not answer."])]

def answerLeadPhrases : List String :=
  ["yes", "no: the document rules this out", "the text does not settle this", "not necessarily",
   "VE could not decide this"]

private def digits (s : String) : Bool := !s.isEmpty && s.toList.all Char.isDigit

/-- The citation text emitted between `Sentences ` and ` say when `. -/
def citationTextValid (s : String) : Bool :=
  let parts := s.splitOn " and "
  if parts.length > 2 then false
  else
    let before := (parts.headD "").splitOn ", "
    !before.isEmpty && before.all digits &&
      (parts.length == 1 || digits (parts[1]!))

/-- Every way the pieces read all of `cs`, as the slots' texts in order. -/
def pieceReadings : List Piece → List Char → List (List String)
  | [], [] => [[]]
  | [], _ :: _ => []
  | .lit s :: ps, cs => if s.toList.isPrefixOf cs then pieceReadings ps (cs.drop s.length) else []
  | .slot :: ps, cs =>
    (List.range cs.length).flatMap fun k =>
      (pieceReadings ps (cs.drop (k + 1))).map fun rest => String.mk (cs.take (k + 1)) :: rest
  | .num :: ps, cs =>
    (List.range cs.length).flatMap fun k =>
      if (cs.take (k + 1)).all Char.isDigit then
        (pieceReadings ps (cs.drop (k + 1))).map fun rest => String.mk (cs.take (k + 1)) :: rest
      else []
  | .citation :: ps, cs =>
    (List.range cs.length).flatMap fun k =>
      let s := String.mk (cs.take (k + 1))
      if citationTextValid s then (pieceReadings ps (cs.drop (k + 1))).map (s :: ·) else []
  | .answerLead :: ps, cs =>
    answerLeadPhrases.flatMap fun s =>
      if s.toList.isPrefixOf cs then (pieceReadings ps (cs.drop s.length)).map (s :: ·) else []

/-- Every derivation of a line from every registered frame. -/
def frameReadings (line : String) : List (String × List String) :=
  answerFrames.flatMap fun (name, ps) => (pieceReadings ps line.toList).map (name, ·)

/-- W7's all-derivations gate: the line has exactly one derivation, and it is frame `f`'s; its slots. -/
def gated (f line : String) : Option (List String) :=
  match frameReadings line with
  | [(g, slots)] => if g == f then some slots else none
  | _ => none

/-- A0 is shown only when it is gated and its asked sentence, with its final period, reads exactly `[(φ, false)]`. -/
def askedGate (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (φ : EFormula) (line : String) : Bool :=
  match gated "A0" line with
  | some [s] => checkRendering E O L b [(φ, false)] (s ++ ".")
  | _ => false

/-- The first literal of a frame. -/
def lead : List Piece → String
  | .lit s :: _ => s
  | _ => ""

theorem frames_leads : (answerFrames.map (lead ·.2)).Pairwise
    (fun a b => a ≠ "" ∧ b ≠ "" ∧ ¬ a.toList.isPrefixOf b.toList ∧ ¬ b.toList.isPrefixOf a.toList) := by
  decide

/-- A gated A0 line reads back: it has one derivation, A0's, whose slot with its final period is the sentence VE
    read, with exactly the formula `φ` and one derivation. -/
theorem askedGate_sound (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (φ : EFormula) (line : String)
    (h : askedGate E O L b φ line = true) :
    ∃ s, frameReadings line = [("A0", [s])] ∧ EnglishOneReading E O L (s ++ ".") [(φ, false)] := by
  unfold askedGate gated at h
  split at h
  · rename_i slots hg
    split at hg
    · rename_i g sl hf
      split at hg
      · rename_i heq
        cases hg
        refine ⟨_, ?_, checked_rendering E O L b [(φ, false)] _ h⟩
        rw [hf]
        simp at heq
        rw [heq]
      · cases hg
    · cases hg
  · cases h

end VE.Question
