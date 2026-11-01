import VE.Cardinality.Wire

/-! Lean's English line for a canonical cardinality statement: the `paraphrase` case (docs/spec/quantities.md 2.1,
4.1), display-only until QT-A6 adds the parse-back check.

Nouns, verb phrases and constants are the vocabulary's descriptions in the projection's target environment; a sort's
plural adds "s" (plural forms are QT-A6's catalogue). The counted object is "x". Every declared finite sort is shown
as the document's assumption; every proportion says its population has at least one member, every ratio that its
denominator is positive, and every rounding how a value exactly halfway rounds. A connective's operands are each in
parentheses, and a line's first letter after its opening parentheses is a capital. W6a parts are shown in W6a's
canonical encoding (Lean has no English line for W6a). The reply's text, every assumption and the line together, is
at most `maxBytes` UTF-8 bytes: each piece, a vocabulary text included, is charged before it is appended. -/
namespace VE.Cardinality.Render
open Lean

def maxBytes : Nat := 65536
def tooLong : String := s!"ResourceLimit: At most {maxBytes} bytes in a paraphrase"

/-- The bytes charged for the whole reply so far, and the piece being built. -/
abbrev M := StateT (Nat × String) (Except String)

/-- Append `s` to the piece, charged first. -/
def emit (s : String) : M Unit := fun (n, out) =>
  if n + s.utf8ByteSize > maxBytes then .error tooLong else .ok ((), (n + s.utf8ByteSize, out ++ s))

/-- A new piece of the reply, charged after the earlier pieces. -/
def piece (m : M Unit) : M String := fun (n, _) => do
  let ((), n', out) ← m (n, "")
  pure (out, (n', ""))

/-- A vocabulary entry's description, else its name. -/
def describe (w : CardEnv) (group name : String) : String :=
  ((((w.w6.target.getObjValD "vocabulary").getObjValD group).getObjValD name).getObjValD "description").getStr?
    |>.toOption.getD name

def inParens (m : M Unit) : M Unit := do emit "("; m; emit ")"

def body (w : CardEnv) : Body → M Unit
  | .atom p => do emit "x "; emit (describe w "predicates" p)
  | .any => emit "x is any object"
  | .not b => do emit "it is not the case that "; inParens (body w b)
  | .and a b => do inParens (body w a); emit " and "; inParens (body w b)
  | .or a b => do inParens (body w a); emit " or "; inParens (body w b)

/-- "the users x such that …"; every object of the sort is "the users". -/
def members (w : CardEnv) (s : String) : Body → M Unit
  | .any => do emit (describe w "sorts" s); emit "s"
  | b => do emit (describe w "sorts" s); emit "s x such that "; body w b

/-- "there is at least one user (x such that …)". -/
def atLeastOne (w : CardEnv) (s : String) : Body → M Unit
  | .any => do emit "there is at least one "; emit (describe w "sorts" s)
  | b => do emit "there is at least one "; emit (describe w "sorts" s); emit " x such that "; body w b

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
  | .quantity a => do emit "the W6a statement "; emit (VE.Time.Wire.encQ a).compress; emit " holds"
  | .count c => count w c
  | .proportion p => do
    atLeastOne w p.sort p.whole
    emit ", and of the "; emit (describe w "sorts" p.sort); emit "s x"
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

/-- A line's sentence-initial spelling: its first character after any opening parentheses ASCII-uppercased. -/
def initial (s : String) : String :=
  let (opens, rest) := s.toList.span (· == '(')
  String.mk (opens ++ (VE.Time.Wire.sentenceInitial (String.mk rest)).toList)

/-- The reply's text: each declared finite sort shown as the document's assumption, then the statement's line, one
sentence; at most `maxBytes` bytes together. -/
def paraphrase (w : CardEnv) (f : CFormula) : Except String (String × List String) :=
  Prod.fst <$> (do
    let assumptions ← w.env.finite.mapM fun s => piece do
      emit "The document assumes there are finitely many "; emit (describe w "sorts" s); emit "s."
    let line ← piece do formula w f; emit "."
    pure (initial line, assumptions) : M (String × List String)) (0, "")

end VE.Cardinality.Render
