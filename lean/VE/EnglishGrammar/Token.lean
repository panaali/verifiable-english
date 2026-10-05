import VE.Grammar.Basic

/-! The English tokens, terminals and their matching (docs/spec/english-lean.md 2.2, 2.3 and 5.8).

Tier B of the specification: the English instance of the generic engine. An English grammar is a
`Grammar Terminal` and its trees are `Tree Tok`.

A punctuation token carries the `glued` flag of the DRI's ruling on O1 (2026-10-04), in two halves:
`gluedBefore` is true when no whitespace separates the mark from the character before it, and
`gluedAfter` when none separates it from the character after it. An `exact` terminal compares them,
so `deployed , it`, `deployed,it` and `non - compliant` do not match the rules that read
`deployed, it` and `non-compliant`: Lean accepts the spacing that Python accepts and no other.
-/

namespace VE.EnglishGrammar
open VE.Grammar

inductive Tok where
  | word (text : String) (initial : Bool)
  | quoted (name : String)
  | label (letter : String) (index : Nat)
  | numeral (value : Int)
  | punct (text : String) (gluedBefore gluedAfter : Bool)
  deriving DecidableEq, Repr, Inhabited

/-- The sentence terminator, with each spacing. The lexer never puts it inside a sentence. -/
def terminators : List Tok :=
  [.punct "." false false, .punct "." false true, .punct "." true false, .punct "." true true]

inductive TokClass where
  | numeral
  | label (letter : String)
  deriving DecidableEq, Repr

inductive Terminal where
  | kw (s : String)
  | content (s : String)
  | exact (t : Tok)
  | cls (c : TokClass)
  deriving DecidableEq, Repr

/-- ASCII letters to lower case; `İ` and `ı` to `i`, `ſ` to `s`, the Kelvin sign to `k`. The table of
`VE.Discourse.foldChar`, copied (R13); `EnglishGrammar/FoldAgree.lean` proves the two agree. -/
def foldChar (c : Char) : Char :=
  if c.isAlphanum then c.toLower
  else if c.val == 0x130 || c.val == 0x131 then 'i'
  else if c.val == 0x17F then 's'
  else if c.val == 0x212A then 'k'
  else c

def fold (s : String) : String := s.map foldChar

/-- The first character in ASCII upper case, the rest unchanged. -/
def capitalise (s : String) : String :=
  match s.toList with
  | [] => s
  | c :: cs => String.mk (c.toUpper :: cs)

def Tok.plain : Tok → Tok
  | .word text _ => .word text false
  | t => t

def TokClass.accepts : TokClass → Tok → Bool
  | .numeral, .numeral _ => true
  | .label l, .label l2 _ => l == l2
  | _, _ => false

def Terminal.accepts : Terminal → Tok → Bool
  | .kw s, .word text initial => text == s || (initial && text == capitalise s)
  | .content s, .word text _ => fold text == fold s
  | .exact t, tok => tok.plain == t.plain
  | .cls c, tok => c.accepts tok
  | _, _ => false

/-- The matching of the English instance. -/
instance : Accepts Terminal Tok := ⟨Terminal.accepts⟩

/-- W4 of the specification: no terminal of any rule accepts the terminator, with any spacing. -/
def terminatorFree (G : Grammar Terminal) : Bool :=
  G.rules.all fun R => R.rhs.all fun
    | .t a => terminators.all fun x => !a.accepts x
    | .n _ => true

end VE.EnglishGrammar
