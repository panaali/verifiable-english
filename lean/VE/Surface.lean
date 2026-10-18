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

/-! The `definitions@0` surface sugar (lean-first batch 14a), read by every
family parser when the environment has the profile: `no S is P`, `every S x
that is P, (A)`, `(A) iff (B)` and the statement `define p(x, …) as (A)`. Each
reads as the core formula it abbreviates; the family's typing check then
decides it like any other statement. These readers are shared by the family
parsers, which pass their own formula builders. -/

/-- A `definitions@0` environment's sugar: `defined p` gives the argument sorts
of a defined predicate `p` and whether a body is `p`'s identity-bound body. -/
structure Sugar (F : Type) where
  defined : String → Option (List String × (F → Bool))

/-- `no S is P`, after `no `. -/
def readNo {F : Type} (build : String → String → F) (input : List Char) : Option (F × List Char) := do
  let (s, rest) ← readIdent input
  let rest ← consume " is ".toList rest
  let (p, rest) ← readIdent rest
  some (build s p, rest)

/-- `every S x that is P, (A)`, after `every `; `body` reads `A` in the scope of `x`. -/
def readEvery {F : Type} (allowed : List String → String → Bool)
    (body : List String → List Char → Option (F × List Char)) (build : String → String → F → F)
    (names : List String) (input : List Char) : Option (F × List Char) := do
  let (s, rest) ← readIdent input
  let rest ← consume [' '] rest
  let (name, rest) ← readIdent rest
  if !allowed names name then none else do
    let rest ← consume " that is ".toList rest
    let (p, rest) ← readIdent rest
    let rest ← consume ", (".toList rest
    let (a, rest) ← body (name :: names) rest
    let rest ← consume [')'] rest
    some (build s p a, rest)

/-- `n` definition arguments `x, y, …`; the names come back innermost first. -/
def readArguments (allowed : List String → String → Bool) :
    Nat → List String → List Char → Option (List String × List Char)
  | 0, names, input => some (names, input)
  | n + 1, names, input => do
    let input ← if names.isEmpty then some input else consume ", ".toList input
    let (name, rest) ← readIdent input
    if !allowed names name then none else readArguments allowed n (name :: names) rest

/-- The closed biconditional of a definition (Python `definitions.premise`):
`head` is the predicate applied to the bound arguments, binders in declared order. -/
def definitionPremise {F : Type} (all : String → F → F) (and implies : F → F → F)
    (sorts : List String) (head body : F) : F :=
  sorts.foldr all (and (implies head body) (implies body head))

/-- `define p(x, …) as (A)`, after `define `: `A` must be `p`'s identity-bound
body, read in the scope of the arguments. -/
def readDefine {F : Type} (allowed : List String → String → Bool) (sugar : Sugar F)
    (body : List String → List Char → Option (F × List Char))
    (premise : String → List String → F → Option F) (input : List Char) : Option (F × List Char) := do
  let (p, rest) ← readIdent input
  let (sorts, declared) ← sugar.defined p
  let rest ← consume ['('] rest
  let (names, rest) ← readArguments allowed sorts.length [] rest
  let rest ← consume ") as (".toList rest
  let (a, rest) ← body names rest
  let rest ← consume [')'] rest
  if !declared a then none else do
    let f ← premise p sorts a
    some (f, rest)

/-- One statement: under the sugar, a `define` statement or a formula. -/
def readStatement {F : Type} (sugar : Option (Sugar F)) (formula : List Char → Option (F × List Char))
    (define : Sugar F → List Char → Option (F × List Char)) (input : List Char) : Option (F × List Char) :=
  match sugar with
  | none => formula input
  | some s =>
    match consume "define ".toList input with
    | some rest => define s rest
    | none => formula input

/-- The definition premise of the FOL family: unary and binary heads. -/
def premiseOf (p : String) (sorts : List String) (body : Formula) : Option Formula :=
  let head : Option Formula := match sorts with
    | [_] => some (.unary p (.var 0))
    | [_, _] => some (.binary p (.var 1) (.var 0))
    | _ => none
  head.map fun h => definitionPremise .all .and .implies sorts h body

/-- Total prefix parser: recursive calls decrease explicit fuel. Public parsing
uses input length plus one, so the unbudgeted reference does not guess a depth.
The executable parser covers all v0 constructors and, with `sugar`, the
`definitions@0` sugar. The full round-trip proof (without sugar) is in `RoundTrip.lean`. -/
def parseRawWith (E : Environment) (sugar : Option (Sugar Formula)) :
    Nat → List String → List Char → Option (Formula × List Char)
  | 0, _, _ => none
  | fuel + 1, names, input =>
    match input with
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

end VE.Surface
