import VE.Typing

namespace VE.Surface

/-- Canonical names are allocated in preorder and the counter is threaded across
siblings, resetting for each statement. Raw ill-scoped terms print a sentinel;
the public AST bridge checks typing before printing. -/
def printTerm (names : List String) : Term → List Char
  | .var i => ((names[i]?).getD "#unbound").toList
  | .const c => '@' :: c.toList

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

def statementChars (a : Formula) : List Char := (printAux [] 0 a).1 ++ ['.', '\n']

def print (formulas : List Formula) : String :=
  String.mk (formulas.flatMap statementChars)

/-- Literal consumption does no whitespace normalization. -/
def consume : List Char → List Char → Option (List Char)
  | [], input => some input
  | c :: cs, d :: ds => if c = d then consume cs ds else none
  | _ :: _, [] => none

def identChar (c : Char) : Bool :=
  (c ≥ 'a' && c ≤ 'z') || (c ≥ '0' && c ≤ '9') || c == '_'

def boundary : List Char → Bool
  | [] => true
  | c :: _ => !identChar c

def readIdent (input : List Char) : Option (String × List Char) := do
  let c ← input.head?
  if !(c ≥ 'a' && c ≤ 'z') then none
  else
    let (name, rest) := input.span identChar
    some (String.mk name, rest)

def reserved : List String := ["true", "false", "is", "equals", "not", "and", "or",
  "if", "then", "for", "every", "there", "exists", "believes", "must", "eventually", "no"]

/-- Unbudgeted ASCII identifier grammar. Runtime byte limits belong to the bridge. -/
def identifier (s : String) : Bool :=
  match s.toList with
  | [] => false
  | c :: cs => (c ≥ 'a' && c ≤ 'z') && cs.all identChar

def generatedName (s : String) : Bool :=
  match s.toList with
  | 'x' :: cs => !cs.isEmpty && cs.all (fun c => c ≥ '0' && c ≤ '9')
  | _ => false

def declarationName (s : String) : Bool :=
  identifier s && !reserved.contains s && !generatedName s

/-- Only lexical side conditions needed for P4. Each declaration is checked by
`declarationName`; finite wire vocabularies validate these conditions executably.
Semantic signature validity and cross-category distinctness are separate. -/
def NamesValid (E : Environment) : Prop :=
  (∀ s ∈ E.sorts, declarationName s = true) ∧
  (∀ p ss, E.predicates p = some ss → declarationName p = true) ∧
  (∀ c s, E.constants c = some s → declarationName c = true)

def binderAllowed (E : Environment) (names : List String) (name : String) : Bool :=
  !names.contains name && !reserved.contains name && !E.sorts.contains name &&
    (E.predicates name).isNone && (E.constants name).isNone

def parseTerm (names : List String) (input : List Char) : Option (Term × List Char) := do
  match input with
  | '@' :: rest =>
      let (c, rest) ← readIdent rest
      some (.const c, rest)
  | _ =>
      let (v, rest) ← readIdent input
      if names.contains v then some (.var (names.idxOf v), rest) else none

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

/-- Total prefix parser: recursive calls decrease explicit fuel. Public parsing
uses input length plus one, so the unbudgeted reference does not guess a depth.
The executable parser covers all v0 constructors. The full round-trip proof is in `RoundTrip.lean`. -/
def parseRaw (E : Environment) : Nat → List String → List Char → Option (Formula × List Char)
  | 0, _, _ => none
  | fuel + 1, names, input =>
    match input with
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

end VE.Surface
