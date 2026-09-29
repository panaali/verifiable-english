import Lean.Data.Json

/-! The static AST limits of wire formulas, in Python's decoder order.

Python's `_Decoder` (and Rust's `ast_limit`) counts each formula and term node
in preorder, and reports `ResourceLimit` at the 10,001st node or past 64 levels
before it looks at the node's shape; typing runs only on a decoded AST. The
frozen Lean decoders check depth as they decode but count nodes after decoding,
and several frozen `decodeFormulas` type the formulas before counting, so a
formula with an unbound variable ahead of 16,000 nodes was ill-typed in Lean and
`ResourceLimit` in Python and Rust.

`check` walks the raw JSON of a case's formulas as Python decodes them, counting
across the formulas as one shared decoder does: past a limit it reports
`ResourceLimit`; at the first node Python would reject for its shape it stops
silently, leaving that diagnostic to the frozen decoder. It runs before any
formula is decoded, typed or evaluated. -/
namespace VE.Route.AstLimit
open Lean

def maxNodes : Nat := 10000
def maxDepth : Nat := 64

def nodeLimit : String := "ResourceLimit: AST node count"
def depthLimit : String := "ResourceLimit: formula depth exceeds 64"
def numeralLimit : String := "ResourceLimit: Integer literal exceeds 40 characters"

/-- Why the walk ended early: a limit (the diagnostic), or a node Python's
decoder rejects (not a limit; the frozen decoder reports it). -/
inductive Halt
  | limit (message : String)
  | stop

def digitsOk : List Char → Bool
  | ['0'] => true
  | c :: cs => c != '0' && c.isDigit && cs.all Char.isDigit
  | [] => false

/-- Python `decimal_from_wire`: at most 40 characters, then canonical decimal. -/
def decimal : Json → Except Halt Unit
  | .str s =>
    if s.length > 40 then throw (.limit numeralLimit)
    else match s.toList with
      | '-' :: ds => if digitsOk ds && ds != ['0'] then pure () else throw .stop
      | ds => if digitsOk ds then pure () else throw .stop
  | _ => throw .stop

/-- A variable index: a JSON integer in `[0, 2^53 - 1]`. -/
def validIndex : Json → Bool
  | .num n => n.exponent == 0 && decide (0 ≤ n.mantissa) && decide (n.mantissa ≤ 2 ^ 53 - 1)
  | _ => false

/-- One node at `depth` (formula levels, or term levels under an atom), after
`n` nodes; the count after it and its subterms. Fuel only bounds recursion: the
depth limit is reached first. -/
def walk : Nat → Bool → Nat → Nat → Json → Except Halt Nat
  | 0, _, _, _, _ => throw .stop
  | fuel + 1, term, depth, n, j => do
    let n := n + 1
    if n > maxNodes then throw (.limit nodeLimit)
    if depth > maxDepth then throw (.limit depthLimit)
    let .arr xs := j | throw .stop
    match term, xs.toList with
    | true, [.str "var", i] => if validIndex i then pure n else throw .stop
    | true, [.str "const", _] => pure n
    | true, [.str "num", v] => do decimal v; pure n
    | true, [.str "add", a, b] => do
      let n ← walk fuel true (depth + 1) n a
      walk fuel true (depth + 1) n b
    | true, [.str "scale", k, t] => do decimal k; walk fuel true (depth + 1) n t
    | false, [.str "top"] | false, [.str "bottom"] => pure n
    | false, [.str "unary", _, t] => walk fuel true 1 n t
    | false, [.str "binary", _, t, u] | false, [.str "eq", t, u]
    | false, [.str "lt", t, u] | false, [.str "le", t, u] => do
      let n ← walk fuel true 1 n t
      walk fuel true 1 n u
    | false, [.str "atom", _, .arr ts] =>
      if 3 ≤ ts.size && ts.size ≤ 6 then ts.toList.foldlM (fun n t => walk fuel true 1 n t) n
      else throw .stop
    | false, [.str "reach", _, .arr edge, t, u] => do
      let n ← match edge.toList with
        | [.str "named", _] => pure n
        | [.str "body", _, a] => walk fuel false (depth + 1) n a
        | _ => throw .stop
      let n ← walk fuel true 1 n t
      walk fuel true 1 n u
    | false, [.str "not", a] => walk fuel false (depth + 1) n a
    | false, [.str "and", a, b] | false, [.str "or", a, b] | false, [.str "implies", a, b] => do
      let n ← walk fuel false (depth + 1) n a
      walk fuel false (depth + 1) n b
    | false, [.str "forall", _, a] | false, [.str "exists", _, a] => walk fuel false (depth + 1) n a
    | _, _ => throw .stop

/-- The limits of formulas decoded by one shared decoder (a document, or a
case's premises followed by its conclusion). -/
def check (fs : List Json) : Except String Unit :=
  match fs.foldlM (walk 256 false 1) 0 with
  | .error (.limit message) => .error message
  | _ => .ok ()

private def doubling : Nat → Json
  | 0 => .arr #[.str "top"]
  | n + 1 => .arr #[.str "and", doubling n, doubling n]

private def var0 : Json := .arr #[.str "var", (0 : Nat)]

private def diagnostic (r : Except String Unit) : Option String :=
  match r with
  | .error e => some e
  | .ok () => none

-- The loop-review reproducer: an unbound variable ahead of 16,383 nodes.
#guard diagnostic (check [.arr #[.str "and", .arr #[.str "eq", var0, var0], doubling 13]]) ==
  some nodeLimit
-- Counted across a case's formulas (8,191 + 8,191 nodes).
#guard diagnostic (check [doubling 12, doubling 12]) == some nodeLimit
#guard diagnostic (check [doubling 12, .arr #[.str "top"]]) == none
-- A node Python rejects before the limit is left to the frozen decoder.
#guard diagnostic (check [.arr #[.str "and", .arr #[.str "bad"], doubling 13]]) == none
-- A Reach body counts; its edge wrapper does not.
#guard diagnostic (check [.arr #[.str "reach", .str "plus", .arr #[.str "body", .str "s", doubling 13],
  var0, var0]]) == some nodeLimit

end VE.Route.AstLimit
