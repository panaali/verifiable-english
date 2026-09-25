import VE.Order.Wire
import VE.Surface

/-! Executable strict order surface. This is boundary parsing code; checked
formulas still pass through `Formula.check` before use by semantic routes. -/
namespace VE.Order.Surface
open VE.Surface (consume readIdent boundary)

def readNumeral (input : List Char) : Option (Int × List Char) := do
  let (sign, rest) := match input with
    | '-' :: cs => (['-'], cs)
    | _ => ([], input)
  let (digits, rest) := rest.span (fun c => c ≥ '0' && c ≤ '9')
  if digits.isEmpty then none else
    match Wire.decodeInt (String.mk (sign ++ digits)) with
    | .ok n => some (n, rest)
    | .error _ => none

def parseTerm (names : List String) : Nat → List Char → Option (Term × List Char)
  | 0, _ => none
  | fuel + 1, input => do
    match input with
    | '@' :: cs =>
        let (name, rest) ← readIdent cs
        some (.const name, rest)
    | '[' :: cs =>
        let (left, rest) ← parseTerm names fuel cs
        if let some rest := consume " * ".toList rest then
          let .num coefficient := left | none
          let (right, rest) ← parseTerm names fuel rest
          let rest ← consume [']'] rest
          some (.scale coefficient right, rest)
        else if let some rest := consume " + ".toList rest then
          let (right, rest) ← parseTerm names fuel rest
          let rest ← consume [']'] rest
          some (.add left right, rest)
        else
          let rest ← consume " - ".toList rest
          let (right, rest) ← parseTerm names fuel rest
          let rest ← consume [']'] rest
          some (left.sub right, rest)
    | '-' :: c :: _ =>
        if c ≥ '0' && c ≤ '9' then
          let (n, rest) ← readNumeral input
          some (.num n, rest)
        else do
          let (t, rest) ← parseTerm names fuel input.tail!
          some (t.neg, rest)
    | c :: _ =>
        if c ≥ '0' && c ≤ '9' then
          let (n, rest) ← readNumeral input
          some (.num n, rest)
        else
          let (name, rest) ← readIdent input
          if names.contains name then some (.var (names.idxOf name), rest) else none
    | [] => none

def parseAtom (names : List String) (input : List Char) : Option (Formula × List Char) := do
  let (t, rest) ← parseTerm names (input.length + 1) input
  if let some rest := consume " equals ".toList rest then
    let (u, rest) ← parseTerm names (rest.length + 1) rest
    some (.eq t u, rest)
  else if let some rest := consume " <= ".toList rest then
    let (u, rest) ← parseTerm names (rest.length + 1) rest
    some (.le t u, rest)
  else if let some rest := consume " < ".toList rest then
    let (u, rest) ← parseTerm names (rest.length + 1) rest
    some (.lt t u, rest)
  else if let some rest := consume " is ".toList rest then
    let (p, rest) ← readIdent rest
    some (.unary p t, rest)
  else
    let rest ← consume [' '] rest
    let (p, rest) ← readIdent rest
    let rest ← consume [' '] rest
    let (u, rest) ← parseTerm names (rest.length + 1) rest
    some (.binary p t u, rest)

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
        if names.contains name || VE.Surface.reserved.contains name || E.sorts.contains name ||
            (E.predicates name).isSome || (E.constants name).isSome then none else do
          let rest ← consume ", (".toList rest
          let (a, rest) ← parseRaw E fuel (name :: names) rest
          let rest ← consume [')'] rest
          some (.all s a, rest)
    | 't' :: 'h' :: 'e' :: 'r' :: 'e' :: ' ' :: 'e' :: 'x' :: 'i' :: 's' :: 't' :: 's' :: ' ' :: rest => do
        let (s, rest) ← readIdent rest
        let rest ← consume [' '] rest
        let (name, rest) ← readIdent rest
        if names.contains name || VE.Surface.reserved.contains name || E.sorts.contains name ||
            (E.predicates name).isSome || (E.constants name).isSome then none else do
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
  if !fs.isEmpty && fs.all (fun f => f.check E []) then some fs else none

open Lean

def termJson : Term → Json
  | .var i => toJson #[Json.str "var", toJson i]
  | .const c => toJson #[Json.str "const", toJson c]
  | .num n => toJson #[Json.str "num", toJson (toString n)]
  | .add t u => toJson #[Json.str "add", termJson t, termJson u]
  | .scale k t => toJson #[Json.str "scale", toJson (toString k), termJson t]

def formulaJson : Formula → Json
  | .top => toJson #[Json.str "top"]
  | .bottom => toJson #[Json.str "bottom"]
  | .unary p t => toJson #[Json.str "unary", toJson p, termJson t]
  | .binary p t u => toJson #[Json.str "binary", toJson p, termJson t, termJson u]
  | .eq t u => toJson #[Json.str "eq", termJson t, termJson u]
  | .lt t u => toJson #[Json.str "lt", termJson t, termJson u]
  | .le t u => toJson #[Json.str "le", termJson t, termJson u]
  | .not a => toJson #[Json.str "not", formulaJson a]
  | .and a b => toJson #[Json.str "and", formulaJson a, formulaJson b]
  | .or a b => toJson #[Json.str "or", formulaJson a, formulaJson b]
  | .implies a b => toJson #[Json.str "implies", formulaJson a, formulaJson b]
  | .all s a => toJson #[Json.str "forall", toJson s, formulaJson a]
  | .ex s a => toJson #[Json.str "exists", toJson s, formulaJson a]

def runCase (j : Json) : Except String Json := do
  if (← j.getObjValAs? String "kind") != "surface" then
    Wire.runCase j
  else
    let id ← j.getObjValAs? String "id"
    let vocabulary ← Wire.decodeEnvironment (← j.getObjVal? "environment")
    let source ← j.getObjValAs? String "source"
    if source.utf8ByteSize > 65536 then throw "ResourceLimit: source size"
    let some formulas := parse vocabulary.environment source | throw "invalid order surface"
    if (formulas.map Wire.formulaNodes).foldl (· + ·) 0 > 10000 then
      throw "ResourceLimit: AST node count"
    pure (Json.mkObj [("id", toJson id), ("status", toJson "ok"),
      ("ast", toJson (formulas.map formulaJson))])

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
      ("valid", .bool false), ("error", .str message)]

end VE.Order.Surface
