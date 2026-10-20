import VE.Semantics

/-! `scales@0` declarations (docs/spec/quantities.md 6.1): the `vocabulary.scales` block is a list of
dimensions. A dimension names a compared sort, a comparative predicate, optionally an equative one and
"any two can be compared" (only with an equative), graded words (W2 open terms, each with a direction)
and `above` pairs ("whatever is g is h"). Every predicate is ordinary declared vocabulary: the block
declares no symbol. -/
namespace VE.Scales

inductive Direction where
  | upper
  | lower
  deriving DecidableEq, Repr

/-- A graded word: a unary predicate that is a W2 open term (decider and factors stay in the W2 record). -/
structure Grade where
  name : String
  direction : Direction
  deriving DecidableEq, Repr

/-- One dimension along which objects of one sort are compared. -/
structure Dimension where
  name : String
  sort : String
  more : String
  same : Option String
  comparable : Bool
  grades : List Grade
  above : List (String × String)
  deriving DecidableEq, Repr

structure ScaleDoc where
  dims : List Dimension
  deriving DecidableEq, Repr

def Dimension.symbols (d : Dimension) : List String := d.more :: (d.same.toList ++ d.grades.map (·.name))
def ScaleDoc.symbols (D : ScaleDoc) : List String := D.dims.flatMap Dimension.symbols

def rel2 (p : String) (i j : Nat) : VE.Formula := .binary p (.var i) (.var j)
def rel1 (p : String) (i : Nat) : VE.Formula := .unary p (.var i)

end VE.Scales
