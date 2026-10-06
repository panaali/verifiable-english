import VE.Senses.Dictionary

/-! Assignments of defaults (docs/spec/senses.md 2.4 and 5.2; batch B4).

An assignment lists the defaults a document chooses, one sense per word, in the order of its preamble
lines. `defaultOf D A w` is the assigned sense, else the only sense when `w` has exactly one, else none.
`Assignment.lines` renders the assignment as preamble lines, which the preamble reader reads back.
-/

namespace VE.Senses
open VE.EnglishGrammar

structure Assignment where
  /-- Word and index, in line order. -/
  defaults : List (String × Nat)
  deriving DecidableEq, Repr

/-- No word is assigned twice, and every assigned index is a sense of its word. -/
def Assignment.wf (D : Dictionary) (A : Assignment) : Bool :=
  (A.defaults.map (·.1)).eraseDups.length == A.defaults.length &&
  A.defaults.all fun (w, i) => (D.sensesOf w).any (·.index == i)

def Assignment.extend (A : Assignment) (c : List (String × Nat)) : Assignment := ⟨A.defaults ++ c⟩

def defaultOf (D : Dictionary) (A : Assignment) (w : String) : Option Sense :=
  match A.defaults.lookup w with
  | some i => (D.sensesOf w).find? (·.index == i)
  | none =>
    match D.sensesOf w with
    | [s] => some s
    | _ => none

/-- The preamble line of one default. -/
def lineOf (w : String) (s : Sense) : String := "In this document, " ++ w ++ " means " ++ s.gloss ++ "."

/-- One line per default, in the assignment's order, joined by line breaks. -/
def Assignment.lines (D : Dictionary) (A : Assignment) : String :=
  "\n".intercalate (A.defaults.filterMap fun (w, i) => ((D.sensesOf w).find? (·.index == i)).map (lineOf w))

/-- The assigned words that have one sense: their lines change nothing and are reported, never refused. -/
def unneeded (D : Dictionary) (A : Assignment) : List String :=
  (A.defaults.map (·.1)).filter fun w => (D.sensesOf w).length == 1

end VE.Senses
