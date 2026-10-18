import VE.Closure.Syntax
import VE.RoundTrip

namespace VE.Closure.Surface
open VE.Surface

def kindText : Kind → String
  | .plus => "tc"
  | .star => "rtc"

def printAux (names : List String) (next : Nat) : Formula → List Char × Nat
  | .top => ("true".toList, next)
  | .bottom => ("false".toList, next)
  | .unary p t => (printTerm names t ++ " is ".toList ++ p.toList, next)
  | .binary p t u => (printTerm names t ++ [' '] ++ p.toList ++ [' '] ++ printTerm names u, next)
  | .eq t u => (printTerm names t ++ " equals ".toList ++ printTerm names u, next)
  | .not a =>
      let (text, n) := printAux names next a
      ("not (".toList ++ text ++ [')'], n)
  | .and a b =>
      let (left, n) := printAux names next a
      let (right, n') := printAux names n b
      (['('] ++ left ++ ") and (".toList ++ right ++ [')'], n')
  | .or a b =>
      let (left, n) := printAux names next a
      let (right, n') := printAux names n b
      (['('] ++ left ++ ") or (".toList ++ right ++ [')'], n')
  | .implies a b =>
      let (left, n) := printAux names next a
      let (right, n') := printAux names n b
      ("if (".toList ++ left ++ "), then (".toList ++ right ++ [')'], n')
  | .all s a =>
      let name := "x" ++ toString next
      let (body, n) := printAux (name :: names) (next + 1) a
      ("for every ".toList ++ s.toList ++ [' '] ++ name.toList ++ ", (".toList ++ body ++ [')'], n)
  | .ex s a =>
      let name := "x" ++ toString next
      let (body, n) := printAux (name :: names) (next + 1) a
      ("there exists ".toList ++ s.toList ++ [' '] ++ name.toList ++ ", (".toList ++ body ++ [')'], n)

  | .reachNamed k p t u =>
      ((kindText k).toList ++ ['['] ++ p.toList ++ "](".toList ++
        printTerm names t ++ ", ".toList ++ printTerm names u ++ [')'], next)
  | .reachBody k s a t u =>
      let src := "x" ++ toString next
      let dst := "x" ++ toString (next + 1)
      let (body, n) := printAux (dst :: src :: names) (next + 2) a
      ((kindText k).toList ++ ['['] ++ s.toList ++ [' '] ++ src.toList ++
        ", ".toList ++ dst.toList ++ " | (".toList ++ body ++ ")](".toList ++
        printTerm names t ++ ", ".toList ++ printTerm names u ++ [')'], n)

def statementChars (a : Formula) : List Char := (printAux [] 0 a).1 ++ ['.', '\n']

def print (formulas : List Formula) : String :=
  String.mk (formulas.flatMap statementChars)

def parseAtom (names : List String) (input : List Char) : Option (Formula × List Char) := do
  let (t, rest) ← parseTerm names input
  if let some rest := consume " equals ".toList rest then
    let (u, rest) ← parseTerm names rest
    some (.eq t u, rest)
  else if let some rest := consume " is ".toList rest then
    let (p, rest) ← readIdent rest
    some (.unary p t, rest)
  else
    let rest ← consume [' '] rest
    let (p, rest) ← readIdent rest
    let rest ← consume [' '] rest
    let (u, rest) ← parseTerm names rest
    some (.binary p t u, rest)

def parseReach (E : Environment)
    (bodyParser : List String → List Char → Option (Formula × List Char))
    (k : Kind) (names : List String) (input : List Char) : Option (Formula × List Char) := do
  let (id, rest) ← readIdent input
  if let some rest := consume "](".toList rest then
    let (t, rest) ← parseTerm names rest
    let rest ← consume ", ".toList rest
    let (u, rest) ← parseTerm names rest
    let rest ← consume [')'] rest
    some (.reachNamed k id t u, rest)
  else do
    let rest ← consume [' '] rest
    let (src, rest) ← readIdent rest
    if !binderAllowed E names src then none else do
      let rest ← consume ", ".toList rest
      let (dst, rest) ← readIdent rest
      if !binderAllowed E (src :: names) dst then none else do
        let rest ← consume " | (".toList rest
        let (a, rest) ← bodyParser (dst :: src :: names) rest
        let rest ← consume ")](".toList rest
        let (t, rest) ← parseTerm names rest
        let rest ← consume ", ".toList rest
        let (u, rest) ← parseTerm names rest
        let rest ← consume [')'] rest
        some (.reachBody k id a t u, rest)

/-- The definition premise of this family (Python `definitions.premise`): unary and binary heads. -/
def premiseOf (p : String) (sorts : List String) (body : Formula) : Option Formula :=
  let head : Option Formula := match sorts with
    | [_] => some (.unary p (.var 0))
    | [_, _] => some (.binary p (.var 1) (.var 0))
    | _ => none
  head.map fun h => definitionPremise .all .and .implies sorts h body

def parseRawWith (E : Environment) (sugar : Option (Sugar Formula)) :
    Nat → List String → List Char → Option (Formula × List Char)
  | 0, _, _ => none
  | fuel + 1, names, input =>
    match input with
    | 't' :: 'c' :: '[' :: rest => parseReach E (parseRawWith E sugar fuel) .plus names rest
    | 'r' :: 't' :: 'c' :: '[' :: rest => parseReach E (parseRawWith E sugar fuel) .star names rest
    | 't' :: 'r' :: 'u' :: 'e' :: rest =>
        if boundary rest then some (.top, rest) else parseAtom names input
    | 'f' :: 'a' :: 'l' :: 's' :: 'e' :: rest =>
        if boundary rest then some (.bottom, rest) else parseAtom names input
    | 'n' :: 'o' :: 't' :: ' ' :: '(' :: rest => do
        let (a, rest) ← parseRawWith E sugar fuel names rest
        let rest ← consume [')'] rest
        some (.not a, rest)
    | 'n' :: 'o' :: ' ' :: rest =>
        match sugar with
        | none => parseAtom names input
        | some _ => readNo (fun s p => .all s (.not (.unary p (.var 0)))) rest
    | 'e' :: 'v' :: 'e' :: 'r' :: 'y' :: ' ' :: rest =>
        match sugar with
        | none => parseAtom names input
        | some _ => readEvery (binderAllowed E) (parseRawWith E sugar fuel)
            (fun s p a => .all s (.implies (.unary p (.var 0)) a)) names rest
    | '(' :: rest => do
        let (a, rest) ← parseRawWith E sugar fuel names rest
        if let some rest := consume ") and (".toList rest then
          let (b, rest) ← parseRawWith E sugar fuel names rest
          let rest ← consume [')'] rest
          some (.and a b, rest)
        else
          match consume ") or (".toList rest, sugar with
          | some rest, _ => do
            let (b, rest) ← parseRawWith E sugar fuel names rest
            let rest ← consume [')'] rest
            some (.or a b, rest)
          | none, some _ => do
            let rest ← consume ") iff (".toList rest
            let (b, rest) ← parseRawWith E sugar fuel names rest
            let rest ← consume [')'] rest
            some (.and (.implies a b) (.implies b a), rest)
          | none, none => none
    | 'i' :: 'f' :: ' ' :: '(' :: rest => do
        let (a, rest) ← parseRawWith E sugar fuel names rest
        let rest ← consume "), then (".toList rest
        let (b, rest) ← parseRawWith E sugar fuel names rest
        let rest ← consume [')'] rest
        some (.implies a b, rest)
    | 'f' :: 'o' :: 'r' :: ' ' :: 'e' :: 'v' :: 'e' :: 'r' :: 'y' :: ' ' :: rest => do
        let (s, rest) ← readIdent rest
        let rest ← consume [' '] rest
        let (name, rest) ← readIdent rest
        if !binderAllowed E names name then none else do
          let rest ← consume ", (".toList rest
          let (a, rest) ← parseRawWith E sugar fuel (name :: names) rest
          let rest ← consume [')'] rest
          some (.all s a, rest)
    | 't' :: 'h' :: 'e' :: 'r' :: 'e' :: ' ' :: 'e' :: 'x' :: 'i' :: 's' :: 't' :: 's' :: ' ' :: rest => do
        let (s, rest) ← readIdent rest
        let rest ← consume [' '] rest
        let (name, rest) ← readIdent rest
        if !binderAllowed E names name then none else do
          let rest ← consume ", (".toList rest
          let (a, rest) ← parseRawWith E sugar fuel (name :: names) rest
          let rest ← consume [')'] rest
          some (.ex s a, rest)
    | _ => parseAtom names input

/-- The parser without sugar: every proved round trip is about this one. -/
abbrev parseRaw (E : Environment) : Nat → List String → List Char → Option (Formula × List Char) :=
  parseRawWith E none

def parseStatementsWith (E : Environment) (sugar : Option (Sugar Formula)) :
    Nat → List Char → Option (List Formula)
  | 0, _ => none
  | _ + 1, [] => some []
  | fuel + 1, input => do
      let (a, rest) ← readStatement sugar (parseRawWith E sugar (input.length + 1) [])
        (fun s => readDefine (binderAllowed E) s (fun names => parseRawWith E sugar (input.length + 1) names)
          premiseOf) input
      let rest ← consume ['.', '\n'] rest
      let tail ← parseStatementsWith E sugar fuel rest
      some (a :: tail)

abbrev parseStatements (E : Environment) : Nat → List Char → Option (List Formula) :=
  parseStatementsWith E none

def parseWith (E : Environment) (sugar : Option (Sugar Formula)) (text : String) : Option (List Formula) := do
  let fs ← parseStatementsWith E sugar (text.toList.length + 1) text.toList
  if !fs.isEmpty && fs.all (fun a => a.check E []) then some fs else none

def parse (E : Environment) (text : String) : Option (List Formula) :=
  parseWith E none text

def normalize (E : Environment) (text : String) : Option String :=
  (parse E text).map print

end VE.Closure.Surface
