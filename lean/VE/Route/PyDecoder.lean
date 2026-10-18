import VE.Route.AstLimit

/-! Python's view of an AST on the wire: `repr` of a name and the walk of its `_Decoder`.

The reports preflight walk (`VE.Attribution.Preflight`) and the definitions layer of the
route (`VE.Route.Wire.bodyFault`) both name a formula a Lean decoder rejected as Python's
decoder names it, so this walk sits below both, under the preflight's namespace. -/
namespace VE.Reports.Preflight
open Lean

/-- Python `repr` of a string: its quotes, and escapes for `\\`, the quote, controls and the
Latin-1 non-printables. -/
def quote (s : String) : String :=
  let q := if s.contains '\'' && !s.contains '"' then '"' else '\''
  let hex := fun (n : Nat) => "\\x" ++ (if n < 16 then "0" else "") ++ String.mk (Nat.toDigits 16 n)
  let esc := fun (c : Char) =>
    if c == '\\' then "\\\\" else if c == q then "\\" ++ c.toString
    else if c == '\t' then "\\t" else if c == '\n' then "\\n" else if c == '\r' then "\\r"
    else if c.toNat < 0x20 || (0x7f ≤ c.toNat && c.toNat ≤ 0xa0) || c.toNat == 0xad then hex c.toNat
    else c.toString
  q.toString ++ String.join (s.toList.map esc) ++ q.toString

/-! ## Formulas: Python's AST decoder -/

abbrev Walk := StateT Nat (Except String)

def termArity : String → Option Nat
  | "var" | "const" | "num" => some 2
  | "add" | "scale" => some 3
  | _ => none

def formulaArity : String → Option Nat
  | "top" | "bottom" => some 1
  | "not" => some 2
  | "unary" | "eq" | "lt" | "le" | "and" | "or" | "implies" | "forall" | "exists" | "atom" => some 3
  | "binary" => some 4
  | "reach" => some 5
  | _ => none

/-- Python `decimal_from_wire`. -/
def decimal : Json → Walk _root_.Unit
  | .str s =>
    if s.length > 40 then throw "ResourceLimit: Integer literal exceeds 40 characters"
    else
      let ok := match s.toList with
        | '-' :: ds => VE.Route.AstLimit.digitsOk ds && ds != ['0']
        | ds => VE.Route.AstLimit.digitsOk ds
      if ok then pure () else throw s!"SyntaxError: Non-canonical integer literal {quote s}"
  | _ => throw "SyntaxError: Integer wire values must be canonical decimal strings"

def atomTerms : String := "SyntaxError: Atom terms must be an array of three to six terms"
def reachEdge : String := "SyntaxError: Reach edge must be a tagged array"

/-- Python `_Decoder.decode`: one node at `depth`, counted; terms when `term`. Fuel only
bounds recursion (the 64-level limit is reached first). -/
def decodeNode : Nat → Bool → Nat → Json → Walk _root_.Unit
  | 0, _, _, _ => pure ()
  | fuel + 1, term, depth, j => do
    let n := (← get) + 1
    set n
    if n > 10000 || depth > 64 then throw "ResourceLimit: AST exceeds depth or node budget"
    let (tag, args) ← match j with
      | .arr a => match a.toList with
        | .str t :: rest => pure (t, rest)
        | _ => throw "SyntaxError: AST nodes must be nonempty tagged JSON arrays"
      | _ => throw "SyntaxError: AST nodes must be nonempty tagged JSON arrays"
    let arity := if term then termArity tag else formulaArity tag
    unless arity == some (args.length + 1) do
      throw s!"SyntaxError: Unknown AST tag or incorrect arity: {quote tag}"
    let t := decodeNode fuel true
    let f := decodeNode fuel false
    match tag, args with
    | "var", [i] =>
      unless VE.Route.AstLimit.validIndex i do throw "UnboundVariable: Invalid variable index"
    | "num", [v] => decimal v
    | "add", [a, b] => do t (depth + 1) a; t (depth + 1) b
    | "scale", [k, x] => do decimal k; t (depth + 1) x
    | "lt", [a, b] | "le", [a, b] | "eq", [a, b] => do t 1 a; t 1 b
    | "unary", [_, a] => t 1 a
    | "binary", [_, a, b] => do t 1 a; t 1 b
    | "atom", [_, ts] =>
      match ts with
      | .arr xs =>
        unless 3 ≤ xs.size && xs.size ≤ 6 do throw atomTerms
        for x in xs.toList do t 1 x
      | _ => throw atomTerms
    | "reach", [_, edge, a, b] => do
      match edge with
      | .arr e => match e.toList with
        | [.str "named", _] => pure ()
        | [.str "body", _, body] => f (depth + 1) body
        | .str _ :: _ => throw "SyntaxError: Unknown Reach edge tag or incorrect arity"
        | _ => throw reachEdge
      | _ => throw reachEdge
      t 1 a
      t 1 b
    | "not", [a] => f (depth + 1) a
    | "and", [a, b] | "or", [a, b] | "implies", [a, b] => do f (depth + 1) a; f (depth + 1) b
    | "forall", [_, a] | "exists", [_, a] => f (depth + 1) a
    | _, _ => pure ()

def decoderFault (j : Json) : Option String :=
  match (decodeNode 300 false 1 j).run' 0 with
  | .error m => some m
  | .ok () => none

/-- Python `definitions._has_reach` on a body its `_Decoder` accepted (`decoderFault` is
`none`): a `reach` node under the connectives and quantifiers. Fuel bounds the 64 levels. -/
def hasReach : Nat → Json → Bool
  | 0, _ => false
  | fuel + 1, j => match j with
    | .arr a => match a.toList with
      | .str "reach" :: _ => true
      | [.str "not", b] | [.str "forall", _, b] | [.str "exists", _, b] => hasReach fuel b
      | [.str "and", b, c] | [.str "or", b, c] | [.str "implies", b, c] => hasReach fuel b || hasReach fuel c
      | _ => false
    | _ => false

#guard decoderFault (.arr #[.str "bogus"]) == some "SyntaxError: Unknown AST tag or incorrect arity: 'bogus'"
#guard decoderFault (.arr #[.str "atom", (7 : Nat), .arr #[]]) == some atomTerms
#guard hasReach 65 (.arr #[.str "not", .arr #[.str "reach", .str "plus", .arr #[.str "named", (7 : Nat)],
  .arr #[.str "var", (0 : Nat)], .arr #[.str "var", (0 : Nat)]]]) == true

end VE.Reports.Preflight
