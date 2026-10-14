import VE.Calc.Decls

namespace VE.Calc.English
open VE.Calc VE.Numbers

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

private def printedWords (p : Printed) : String :=
  if p.places < 0 then
    toString p.digits ++ " times ten to the power " ++ toString (-p.places)
  else VE.Time.renderAmount p.places.toNat p.digits

private def exactWords (q : Rat) : Option String :=
  (List.range 41).findSome? fun k =>
    let scaled := q * (10 : Rat) ^ k
    if scaled.den = 1 then some (VE.Time.renderAmount k scaled.num) else none

private def exprDepth : Expr → Nat
  | .lit _ | .val _ => 0
  | .add a b | .sub a b | .mul a b | .div a b => 1 + max (exprDepth a) (exprDepth b)
  | .pow a _ => 1 + exprDepth a

private def exprAtom : Expr → Bool
  | .lit _ | .val _ => true
  | _ => false

private def renderExpr (words : String → Option String) (e : Expr) : Option String := do
  if exprDepth e > 2 then none else
  match e with
  | .lit q => exactWords q
  | .val n => words n
  | .add a b =>
      pure ("the sum of " ++ (← renderExpr words a) ++ " and " ++ (← renderExpr words b))
  | .sub a b =>
      if !exprAtom a then none else
      pure ((← renderExpr words a) ++ " minus " ++ (← renderExpr words b))
  | .mul a b =>
      pure ("the product of " ++ (← renderExpr words a) ++ " and " ++ (← renderExpr words b))
  | .div a b =>
      if !exprAtom a then none else
      pure ((← renderExpr words a) ++ " divided by " ++ (← renderExpr words b))
  | .pow a k =>
      let s ← renderExpr words a
      if k = 2 then pure ("the square of " ++ s)
      else if k = 3 then pure ("the cube of " ++ s)
      else pure (s ++ " to the power " ++ toString k)

private def fill2 (template a b : String) : String :=
  (template.replace "{0}" a).replace "{1}" b

def renderClaim (words : String → Option String) (c : Claim) : Option String := do
  match c with
  | .compare cmp a b =>
      let some phrase := (orderPhrases ++ [equalsPhrase]).find? (fun row => decide (row.2 = cmp))
        | none
      pure (fill2 phrase.1 (← renderExpr words a) (← renderExpr words b) ++ ".")
  | .within e lo hi =>
      let line := fill2 withinPhrase (← renderExpr words e) (← renderExpr words lo)
      pure ((line.replace "{2}" (← renderExpr words hi)) ++ ".")
  | .rounds rule e p =>
      let v ← renderExpr words e
      let printed := printedWords p
      let places := placesPhrase p.places
      let sentence := match rule with
        | .tiesUp => v ++ " is " ++ printed ++ " when rounded to " ++ places ++
            ", with exact ties going up."
        | .halfEven => v ++ " is " ++ printed ++ " when rounded to " ++ places ++
            ", with exact ties going to the even digit."
        | .down => v ++ " is " ++ printed ++ " when rounded down to " ++ places ++ "."
        | .up => v ++ " is " ++ printed ++ " when rounded up to " ++ places ++ "."
      pure sentence

end VE.Calc.English
