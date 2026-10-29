import Lean

/-! The one Lean-owned catalogue of source-word reading sets, refusals and profile-fixed wordings.
Rows are added by the owning English batches; this item establishes the checked shape with no rows. -/

namespace VE.EnglishGrammar
open Lean

/-- A candidate wording and a sentence describing a situation that distinguishes it. -/
structure SourceWordReading where
  wording : String
  situation : String
  deriving DecidableEq, Repr

inductive SourceWordKind where
  | readings (candidates : List SourceWordReading)
  | refuse (code advice rewrite : String)
  | fixed (wording : String)
  deriving DecidableEq, Repr

/-- The source phrase, context, profile and plan-item owner of one reading decision. -/
structure SourceWordRow where
  word : String
  frame : String
  profile : String
  owner : String
  kind : SourceWordKind
  deriving DecidableEq, Repr

/-- A refused word may not occur even as a substring of the suggested rewrite. -/
def SourceWordRow.validKind (row : SourceWordRow) : Bool :=
  match row.kind with
  | .readings candidates =>
      candidates.length ≥ 2 &&
      (candidates.map (·.wording)).Nodup &&
      candidates.all (fun c => !c.situation.isEmpty)
  | .refuse code advice rewrite =>
      !code.isEmpty && !advice.isEmpty && !rewrite.isEmpty &&
      (rewrite.splitOn row.word).length == 1
  | .fixed _ => true

/-- Every row has a lower-case source phrase and a plan-item owner. -/
def SourceWordRow.validIdentity (row : SourceWordRow) : Bool :=
  !row.word.isEmpty && row.word.toLower == row.word && !row.owner.isEmpty

def SourceWordRow.key (row : SourceWordRow) : String × String × String :=
  (row.word, row.frame, row.profile)

/-- All catalogue invariants are checked by Lean, including the contextual key. -/
def sourceWordsValid (rows : List SourceWordRow) : Bool :=
  (rows.map SourceWordRow.key).Nodup &&
  rows.all (fun row => row.validIdentity && row.validKind)

/-- No product rows until the consuming English batches add them. -/
def sourceWords : List SourceWordRow := []

#guard sourceWordsValid sourceWords

def SourceWordKind.toJson : SourceWordKind → Json
  | .readings candidates => Json.mkObj [
      ("type", "readings"),
      ("candidates", Json.arr ((candidates.map fun c =>
        Json.mkObj [("wording", .str c.wording), ("situation", .str c.situation)]).toArray))]
  | .refuse code advice rewrite => Json.mkObj [
      ("type", "refuse"), ("code", .str code), ("advice", .str advice),
      ("rewrite", .str rewrite)]
  | .fixed wording => Json.mkObj [("type", "fixed"), ("wording", .str wording)]

def SourceWordRow.toJson (row : SourceWordRow) : Json := Json.mkObj [
  ("word", .str row.word), ("frame", .str row.frame),
  ("profile", .str row.profile), ("owner", .str row.owner),
  ("kind", row.kind.toJson)]

/-- This is the sole source of the generated Python view. -/
def sourceWordsJson : Json := Json.mkObj [
  ("format", "ve.source-words@1"),
  ("rows", Json.arr ((sourceWords.map SourceWordRow.toJson).toArray))]

end VE.EnglishGrammar
