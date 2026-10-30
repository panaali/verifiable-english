import VE.Cardinality.Wire

/-! Lean's English line for a canonical cardinality statement: the `paraphrase` case (docs/spec/quantities.md 2.1,
4.1), display-only until QT-A6 adds the parse-back check.

Nouns, verb phrases and constants are the vocabulary's descriptions in the projection's target environment; a sort's
plural adds "s" (grammar is QT-A6's catalogue). The counted object is "x". Every proportion says its population has at
least one member, every ratio that its denominator is positive, and every rounding how a value exactly halfway rounds.
A connective's operands are each in parentheses. W6a parts are shown in W6a's canonical encoding. Each piece is
charged before it is appended: the line and the assumptions are at most `maxBytes` UTF-8 bytes each. -/
namespace VE.Cardinality.Render
open Lean

def maxBytes : Nat := 65536
def tooLong : String := s!"ResourceLimit: At most {maxBytes} bytes in a paraphrase"

abbrev M := StateT String (Except String)

/-- Append `s`, charged first. -/
def emit (s : String) : M Unit := fun out =>
  if out.utf8ByteSize + s.utf8ByteSize > maxBytes then .error tooLong else .ok ((), out ++ s)

def run (m : M Unit) : Except String String := (m "").map (·.2)

/-- A vocabulary entry's description, else its name. -/
def describe (w : CardEnv) (group name : String) : String :=
  ((((w.w6.target.getObjValD "vocabulary").getObjValD group).getObjValD name).getObjValD "description").getStr?
    |>.toOption.getD name

def inParens (m : M Unit) : M Unit := do emit "("; m; emit ")"

def body (w : CardEnv) : Body → M Unit
  | .atom p => emit ("x " ++ describe w "predicates" p)
  | .any => emit "x is any object"
  | .not b => do emit "it is not the case that "; inParens (body w b)
  | .and a b => do inParens (body w a); emit " and "; inParens (body w b)
  | .or a b => do inParens (body w a); emit " or "; inParens (body w b)

/-- "the users x such that …"; every object of the sort is "the users". -/
def members (w : CardEnv) (s : String) : Body → M Unit
  | .any => emit (describe w "sorts" s ++ "s")
  | b => do emit (describe w "sorts" s ++ "s x such that "); body w b

/-- "at least one user (x such that …)". -/
def atLeastOne (w : CardEnv) (s : String) : Body → M Unit
  | .any => emit ("there is at least one " ++ describe w "sorts" s)
  | b => do emit ("there is at least one " ++ describe w "sorts" s ++ " x such that "); body w b

def term (w : CardEnv) : VE.Time.QTerm → M Unit
  | .const _ c => emit (describe w "constants" c)
  | t => emit (VE.Time.Wire.encTerm t).compress

def operand (w : CardEnv) : CTerm → M Unit
  | .quantity t => term w t
  | .count s b => do emit "the number of "; members w s b

/-- A denominator is positive: a count has at least one member. -/
def positive (w : CardEnv) : CTerm → M Unit
  | .quantity t => do term w t; emit " is more than zero"
  | .count s b => atLeastOne w s b

def tie : VE.Numbers.Rounding → String
  | .tiesUp => "a value exactly halfway rounds up, to the larger number"
  | .halfEven => "a value exactly halfway rounds to the even digit"
  | .down => "every value rounds down"
  | .up => "every value rounds up"

def place : Nat → String
  | 1 => "tenth"
  | 2 => "hundredth"
  | 3 => "thousandth"
  | k => s!"{k}th decimal place"

def relText : Rel → String
  | .lt => "is less than"
  | .le => "is at most"
  | .eq => "is exactly"

def cmpText : Cmp → String
  | .gt => "more than"
  | .ge => "at least"
  | .lt => "fewer than"
  | .le => "at most"
  | .eq => "exactly"

def countTerm (w : CardEnv) (s : String) (kb : Int × Body) : M Unit := do
  unless kb.1 == 1 do emit s!"{kb.1} times "
  emit "the number of "
  members w s kb.2

def count (w : CardEnv) (c : CountAtom) : M Unit := do
  match c.terms with
  | [] => emit "0"
  | t :: ts => do
    countTerm w c.sort t
    for x in ts do
      emit " plus "
      countTerm w c.sort x
  emit s!" {relText c.rel} {c.bound}"

def formula (w : CardEnv) : CFormula → M Unit
  | .quantity a => emit s!"the W6a statement {(VE.Time.Wire.encQ a).compress} holds"
  | .count c => count w c
  | .proportion p => do
    atLeastOne w p.sort p.whole
    emit (", and of the " ++ describe w "sorts" p.sort ++ "s x")
    unless p.whole == .any do emit " such that "; body w p.whole
    emit s!", {cmpText p.cmp} {p.num} in {p.den} are such that "
    body w p.part
  | .roundsTo r n d D k => do
    operand w n; emit ", divided by "; operand w d
    emit s!", rounds to {VE.Time.renderAmount k D}, rounded to the nearest "
    emit (if k == 0 then "whole number" else place k)
    emit "; "; positive w d; emit s!"; {tie r}"
  | .percentOf p wh D k => do
    operand w p; emit s!" is exactly {VE.Time.renderAmount k D} percent of "; operand w wh
    emit "; "; positive w wh
  | .percentRoundsTo r p wh D k => do
    operand w p; emit s!" is {VE.Time.renderAmount k D} percent of "; operand w wh
    emit (if k == 0 then ", to the nearest percent" else s!", to the nearest {place k} of a percent")
    emit "; "; positive w wh; emit s!"; {tie r}"
  | .not a => do emit "it is not the case that "; inParens (formula w a)
  | .and a b => do inParens (formula w a); emit " and "; inParens (formula w b)
  | .or a b => do inParens (formula w a); emit " or "; inParens (formula w b)
  | .implies a b => do emit "if "; inParens (formula w a); emit ", then "; inParens (formula w b)

/-- The statement's line: one sentence. -/
def line (w : CardEnv) (f : CFormula) : Except String String := do
  pure (VE.Time.Wire.sentenceInitial (← run do formula w f; emit "."))

/-- Each declared finite sort, shown as the document's assumption. -/
def assumptions (w : CardEnv) : Except String (List String) :=
  w.env.finite.mapM fun s => run (emit s!"The document assumes there are finitely many {describe w "sorts" s}s.")

end VE.Cardinality.Render
