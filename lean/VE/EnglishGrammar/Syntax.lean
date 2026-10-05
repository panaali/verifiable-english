/-! The surface AST, the declared rejections, the state of the `it` rule and the semantic types of the
English instance (docs/spec/english-lean.md 2.7, 2.8, 4.2 and 5.8; tier B).

The lists here are the drafts of spec 5.8 as S0 closed them (docs/spec/english-lean-measured.md
section 8, on branch `english-lean/py`) and as the DRI ruled on 2026-10-04:

- `Reject` gains `coefficientNotNumeral`: a scaling coefficient that is not a numeral
  (`Api costs [budget * limit].`) has one derivation, and Python rejects it as a side condition.
- The `blockedWording` identifiers are `natural-negation` (`Every deployed service is not reviewed.`)
  and `risk-every-cannot`. Every other blocked wording of the hand parser fires only when no rule
  matches, so Lean's outcome is `noDerivation` with Python's advice as the diagnostic.
-/

namespace VE.EnglishGrammar

/-- Terms of the strict AST of formula-level English. `var` is a de Bruijn index, 0 the innermost
binder. -/
inductive ETerm where
  | var (index : Nat)
  | const (name : String)
  | num (value : Int)
  | add (left right : ETerm)
  | scale (coefficient : Int) (term : ETerm)
  deriving DecidableEq, Repr

/-- Formulas of the strict AST of formula-level English. -/
inductive EFormula where
  | top
  | bottom
  | pred (name : String) (args : List ETerm)
  | eq (left right : ETerm)
  | lt (left right : ETerm)
  | le (left right : ETerm)
  | not (body : EFormula)
  | and (left right : EFormula)
  | or (left right : EFormula)
  | implies (left right : EFormula)
  | all (sort : String) (body : EFormula)
  | ex (sort : String) (body : EFormula)
  | reachNamed (reflexive : Bool) (relation : String) (left right : ETerm)
  | reachBody (reflexive : Bool) (sort : String) (body : EFormula) (left right : ETerm)
  deriving DecidableEq, Repr

/-- The declared rejections. Each has one public code and one fixed text (spec 4.2). -/
inductive Reject where
  | sourceTooLong | textTooLong | badCharacter (offset : Nat) | openQuote (offset : Nat)
  | badNumeral (offset : Nat) | emptyDocument | emptySentence (index : Nat) | unterminated
  | unboundReference | shadowedName | sortMismatch | markerDepth | nestingLimit | numeralBound
  | coefficientNotNumeral
  | pronounUnresolved | blockedWording (id : String)
  | internal
  deriving DecidableEq, Repr

/-- The identifiers of the blocked wordings that are side conditions (S0, DRI ruling 3). -/
def blockedWordingIds : List String := ["natural-negation", "risk-every-cannot"]

/-- The public code of a rejection (spec 4.2). -/
def Reject.code : Reject → String
  | .sourceTooLong => "SourceTooLong"
  | .textTooLong => "TextTooLong"
  | .badCharacter _ => "BadCharacter"
  | .openQuote _ => "OpenQuote"
  | .badNumeral _ => "BadNumeral"
  | .emptyDocument => "EmptyDocument"
  | .emptySentence _ => "EmptySentence"
  | .unterminated => "Unterminated"
  | .unboundReference => "UnboundReference"
  | .shadowedName => "ShadowedName"
  | .sortMismatch => "SortMismatch"
  | .markerDepth => "MarkerDepth"
  | .nestingLimit => "NestingLimit"
  | .numeralBound => "NumeralBound"
  | .coefficientNotNumeral => "CoefficientNotNumeral"
  | .pronounUnresolved => "PronounUnresolved"
  | .blockedWording _ => "BlockedWording"
  | .internal => "Internal"

/-- The state of the `it` rule. `referents` is sorted and has no duplicate. -/
structure DState where
  referents : List String
  binderSeen : Bool
  deriving DecidableEq, Repr

def DState.init : DState := ⟨[], false⟩

/-- The semantic types. Tier B: S2 closes the list with the action library. -/
inductive Ty where
  | tok | sentence | formula | term | intTerm | declaration | guard | relative
  deriving DecidableEq, Repr

end VE.EnglishGrammar
