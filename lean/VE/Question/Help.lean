import VE.Question.Basic
import VE.EnglishGrammar.Diagnose

namespace VE.Question
open Lean VE.EnglishGrammar

def diagnosisOf (E : Env) (L : Lexicon) (c : Candidate) : Option Diagnosis :=
  match lexSpans c.sentence with
  | .ok ss => (ss[0]?).bind (diagnose E L c.sentence)
  | .error _ => none

/-- The candidate whose diagnosis span starts furthest right, in its own bytes; ties go to the leftmost. Candidates
    without a diagnosis (the budget did not allow finding it) are skipped. -/
def closest (E : Env) (L : Lexicon) (cs : List Candidate) : Option Candidate :=
  (cs.foldl (fun (best : Option (Candidate × Nat)) c => match diagnosisOf E L c, best with
    | some d, some (_, k) => if d.span.1 > k then some (c, d.span.1) else best
    | some d, none => some (c, d.span.1)
    | none, _ => best) none).map (·.1)

/-- A candidate's byte offset on the question. F1: moved right by the frame. F2: before the gap, moved right by the
    auxiliary and its space; the put-back word maps to the question's first word, its following space to the
    question's first space, and the suffix stays at the same byte offsets. -/
def mapPoint (c : Candidate) (off x : Nat) : Nat :=
  match c.form with
  | .caseThat => x + off
  | .fronted a g =>
    let n := a.utf8ByteSize
    let k := n + 1
    if x < g then x + k else if x < g + n then x - g
    else if x < g + k then n + (x - (g + n)) else x

/-- The image of the intersection of `[start, stop)` with one candidate region `[lo, hi)`, whose image begins at
    `dst`. The four F2 regions are each order-preserving, though their concatenation is not. -/
def mappedPiece (start stop lo hi dst : Nat) : Option (Nat × Nat) :=
  let s := max start lo
  let t := min stop hi
  if s < t then some (dst + (s - lo), dst + (t - lo)) else none

/-- Split a diagnosis interval at the F2 movement boundaries, map each piece, and enclose all of their images.
    An empty interval maps its point. The candidate's final `.` occupies the question's final `?` position. -/
def mapSpan (c : Candidate) (off : Nat) (span : Nat × Nat) : Nat × Nat :=
  match c.form with
  | .caseThat => (span.1 + off, span.2 + off)
  | .fronted a g =>
    let n := a.utf8ByteSize
    let k := n + 1
    let pieces := ([mappedPiece span.1 span.2 0 g k,
      mappedPiece span.1 span.2 g (g + n) 0,
      mappedPiece span.1 span.2 (g + n) (g + k) n,
      mappedPiece span.1 span.2 (g + k) c.sentence.utf8ByteSize (g + k)] : List (Option (Nat × Nat)))
        |>.filterMap id
    match pieces with
    | [] => let x := mapPoint c off span.1; (x, x)
    | p :: ps => ps.foldl (fun acc v => (min acc.1 v.1, max acc.2 v.2)) p

/-- A lexer rejection's offset, moved from the body onto the question. -/
def shiftReject (k : Nat) : Reject → Reject
  | .badCharacter o => .badCharacter (o + k)
  | .openQuote o => .openQuote (o + k)
  | .badNumeral o => .badNumeral (o + k)
  | .badSpacing o => .badSpacing (o + k)
  | r => r

end VE.Question
