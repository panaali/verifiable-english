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

def parseRaw (E : Environment) : Nat → List String → List Char → Option (Formula × List Char)
  | 0, _, _ => none
  | fuel + 1, names, input =>
    match input with
    | 't' :: 'c' :: '[' :: rest => parseReach E (parseRaw E fuel) .plus names rest
    | 'r' :: 't' :: 'c' :: '[' :: rest => parseReach E (parseRaw E fuel) .star names rest
    | 't' :: 'r' :: 'u' :: 'e' :: rest =>
        if boundary rest then some (.top, rest) else parseAtom names input
    | 'f' :: 'a' :: 'l' :: 's' :: 'e' :: rest =>
        if boundary rest then some (.bottom, rest) else parseAtom names input
    | 'n' :: 'o' :: 't' :: ' ' :: '(' :: rest => do
        let (a, rest) ← parseRaw E fuel names rest
        let rest ← consume [')'] rest
        some (.not a, rest)
    | '(' :: rest => do
        let (a, rest) ← parseRaw E fuel names rest
        if let some rest := consume ") and (".toList rest then
          let (b, rest) ← parseRaw E fuel names rest
          let rest ← consume [')'] rest
          some (.and a b, rest)
        else
          let rest ← consume ") or (".toList rest
          let (b, rest) ← parseRaw E fuel names rest
          let rest ← consume [')'] rest
          some (.or a b, rest)
    | 'i' :: 'f' :: ' ' :: '(' :: rest => do
        let (a, rest) ← parseRaw E fuel names rest
        let rest ← consume "), then (".toList rest
        let (b, rest) ← parseRaw E fuel names rest
        let rest ← consume [')'] rest
        some (.implies a b, rest)
    | 'f' :: 'o' :: 'r' :: ' ' :: 'e' :: 'v' :: 'e' :: 'r' :: 'y' :: ' ' :: rest => do
        let (s, rest) ← readIdent rest
        let rest ← consume [' '] rest
        let (name, rest) ← readIdent rest
        if !binderAllowed E names name then none else do
          let rest ← consume ", (".toList rest
          let (a, rest) ← parseRaw E fuel (name :: names) rest
          let rest ← consume [')'] rest
          some (.all s a, rest)
    | 't' :: 'h' :: 'e' :: 'r' :: 'e' :: ' ' :: 'e' :: 'x' :: 'i' :: 's' :: 't' :: 's' :: ' ' :: rest => do
        let (s, rest) ← readIdent rest
        let rest ← consume [' '] rest
        let (name, rest) ← readIdent rest
        if !binderAllowed E names name then none else do
          let rest ← consume ", (".toList rest
          let (a, rest) ← parseRaw E fuel (name :: names) rest
          let rest ← consume [')'] rest
          some (.ex s a, rest)
    | _ => parseAtom names input

def parseStatements (E : Environment) : Nat → List Char → Option (List Formula)
  | 0, _ => none
  | _ + 1, [] => some []
  | fuel + 1, input => do
      let (a, rest) ← parseRaw E (input.length + 1) [] input
      let rest ← consume ['.', '\n'] rest
      let tail ← parseStatements E fuel rest
      some (a :: tail)

def parse (E : Environment) (text : String) : Option (List Formula) := do
  let fs ← parseStatements E (text.toList.length + 1) text.toList
  if !fs.isEmpty && fs.all (fun a => a.check E []) then some fs else none

def normalize (E : Environment) (text : String) : Option String :=
  (parse E text).map print

end VE.Closure.Surface
