import VE.Calc.Decls

namespace VE.Calc.English
open VE.Calc VE.Numbers

/-- 11.2's reserved words: value words contain none of them (`ReservedWord`). -/
def reservedWords : List String :=
  ["and", "minus", "divided by", "to the power", "times ten to the power", "is", "be", "equals",
   "when rounded", "through"]

/-- 11.2's phrase words: value words do not begin with one (`ValueWordsForm`). -/
def phraseWords : List String :=
  ["the sum of", "the product of", "the square of", "the cube of", "twice", "half of"]

/-- 11.2's form of value words: single-spaced words beginning with "the", not beginning with a phrase
word and containing no reserved word, so that an atom never reads as a phrase. -/
def valueWordsOk (w : String) : Bool :=
  let padded := " " ++ w ++ " "
  w.startsWith "the " && (w.splitOn " ").all (fun t => !t.isEmpty) &&
    !(phraseWords.any fun p => padded.startsWith (" " ++ p ++ " ")) &&
    !(reservedWords.any fun r => (padded.splitOn (" " ++ r ++ " ")).length > 1)

private def natWords : Nat → String
  | 1 => "one" | 2 => "two" | 3 => "three" | 4 => "four" | 5 => "five"
  | 6 => "six" | 7 => "seven" | 8 => "eight" | 9 => "nine" | 10 => "ten"
  | 11 => "eleven" | 12 => "twelve" | 13 => "thirteen" | 14 => "fourteen"
  | 15 => "fifteen" | 16 => "sixteen" | 17 => "seventeen" | 18 => "eighteen"
  | 19 => "nineteen" | 20 => "twenty" | n => toString n

private def placesPhrase (k : Int) : String :=
  if k = 0 then "a whole number"
  else if k > 0 then
    let n := k.toNat
    if n = 1 then "one decimal place" else natWords n ++ " decimal places"
  else "a multiple of ten to the power " ++ toString (-k)

/-- A printed number in words; a negative one has no numeral in VE text (the sign is a symbol,
`SymbolInText`). -/
private def printedWords (p : Printed) : Option String :=
  if p.digits < 0 then none
  else if p.places < 0 then
    some (toString p.digits ++ " times ten to the power " ++ toString (-p.places))
  else some (VE.Time.renderAmount p.places.toNat p.digits)

private def exactWords (q : Rat) : Option String :=
  if q < 0 then none else
  (List.range 41).findSome? fun k =>
    let scaled := q * (10 : Rat) ^ k
    if scaled.den = 1 then some (VE.Time.renderAmount k scaled.num) else none

private def exprDepth : Expr → Nat
  | .lit _ | .val _ => 0
  | .add a b | .sub a b | .mul a b | .div a b => 1 + max (exprDepth a) (exprDepth b)
  | .pow a _ => 1 + exprDepth a

/-- 11.2 `atom`: a value's words or a numeral. -/
private def renderAtom (words : String → Option String) : Expr → Option String
  | .lit q => exactWords q
  | .val n => do
      let w ← words n
      if valueWordsOk w then pure w else none
  | _ => none

/-- 11.2 `term`: an atom or a prefix phrase whose operands are terms, so no infix phrase ("minus",
"divided by", "to the power") ever stands inside it. -/
private def renderTerm (words : String → Option String) : Expr → Option String
  | .add a b => return "the sum of " ++ (← renderTerm words a) ++ " and " ++ (← renderTerm words b)
  | .mul a b =>
      return "the product of " ++ (← renderTerm words a) ++ " and " ++ (← renderTerm words b)
  | .pow a 2 => return "the square of " ++ (← renderTerm words a)
  | .pow a 3 => return "the cube of " ++ (← renderTerm words a)
  | e => renderAtom words e

/-- 11.2 `expression`: a term, or one infix phrase at the top with an atom on its left, and at
most one phrase inside another (`NestedPhrase`). Anything else is `none`: the display then names
the intermediate values. -/
private def renderExpr (words : String → Option String) (e : Expr) : Option String :=
  if exprDepth e > 2 then none else
  match e with
  | .sub a b => return (← renderAtom words a) ++ " minus " ++ (← renderTerm words b)
  | .div a b => return (← renderAtom words a) ++ " divided by " ++ (← renderTerm words b)
  | .pow a k =>
      if k = 2 ∨ k = 3 then renderTerm words e
      else return (← renderAtom words a) ++ " to the power " ++ toString k
  | _ => renderTerm words e

/-- Fills a phrase template's `{i}` in one pass, so the text filled in is never read as a
placeholder. -/
private def fill (args : List String) : List Char → String
  | '{' :: d :: '}' :: rest =>
      match d.isDigit, args[d.toNat - '0'.toNat]? with
      | true, some a => a ++ fill args rest
      | _, _ => "{" ++ fill args (d :: '}' :: rest)
  | c :: rest => c.toString ++ fill args rest
  | [] => ""

def renderClaim (words : String → Option String) (c : Claim) : Option String := do
  let line ← match c with
    | .compare cmp a b => do
        let some phrase := (orderPhrases ++ [equalsPhrase]).find? (fun row => decide (row.2 = cmp))
          | none
        pure (fill [← renderExpr words a, ← renderExpr words b] phrase.1.toList)
    | .within e lo hi =>
        pure (fill [← renderExpr words e, ← renderExpr words lo, ← renderExpr words hi]
          withinPhrase.toList)
    | .rounds rule e p => do
        let v ← renderExpr words e
        let printed ← printedWords p
        let places := placesPhrase p.places
        pure <| match rule with
          | .tiesUp => v ++ " is " ++ printed ++ " when rounded to " ++ places ++
              ", with exact ties going up"
          | .halfEven => v ++ " is " ++ printed ++ " when rounded to " ++ places ++
              ", with exact ties going to the even digit"
          | .down => v ++ " is " ++ printed ++ " when rounded down to " ++ places
          | .up => v ++ " is " ++ printed ++ " when rounded up to " ++ places
  pure (line.capitalize ++ ".")

end VE.Calc.English
