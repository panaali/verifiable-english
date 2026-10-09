import VE.Bridge

/-! Python-compatible typing diagnostics for the standalone `check` mode.

The verdict of a typing request is always the proved family decoder's. When
that decoder rejects a formula as ill typed, this classifier walks the wire AST
in the order of Python's `_Checker` (`ve/ast.py`) and names the first error
with Python's code and message (`UnknownSymbol`, `TypeMismatch`,
`UnboundVariable`, `UnsupportedProfile`, `ResourceLimit`), so diagnostic codes
agree at zero tolerance (SEMANTICS-MIGRATION-PLAN.md 2a). It never accepts
anything: if it finds no error, the decoder's own message stands. The walk
keeps `_Checker`'s node counter (one per request, shared by a document's
formulas) and its formula and term depths, so a budget rejection is named where
and as Python names it. -/
namespace VE.Service.TypingDiagnostic
open Lean

/-- The vocabulary facts `_Checker` consults. -/
structure Signature where
  sorts : List String
  predicates : List (String × List String)
  constants : List (String × String)
  profiles : List String

def decodeSignature (profiles : List String) (vocabulary : Json) : Except String Signature := do
  let sorts := (← VE.Bridge.fields (← vocabulary.getObjVal? "sorts")).map Prod.fst
  let predicates ← (← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")).mapM fun (p, entry) => do
    pure (p, ← VE.Bridge.strings (← entry.getObjVal? "arguments"))
  let constants ← (← VE.Bridge.fields (← vocabulary.getObjVal? "constants")).mapM fun (c, entry) => do
    pure (c, ← VE.Bridge.stringField entry "sort")
  pure ⟨sorts, predicates, constants, profiles⟩

/-- Characters Python's `str.isprintable` refuses, which `repr` escapes: exact for Latin-1, and above it the
separator, format and private-use ranges a diagnostic can meet. An unassigned code point outside these ranges
(Python escapes it too) is shown as itself. -/
def nonPrintable (n : Nat) : Bool :=
  n < 0x20 || (0x7f ≤ n && n ≤ 0xa0) || n == 0xad || (0x600 ≤ n && n ≤ 0x605) || n == 0x61c ||
  n == 0x6dd || n == 0x70f || n == 0x180e || n == 0x1680 || (0x2000 ≤ n && n ≤ 0x200f) ||
  (0x2028 ≤ n && n ≤ 0x202f) || (0x205f ≤ n && n ≤ 0x206f) || n == 0x3000 || (0xd800 ≤ n && n ≤ 0xf8ff) ||
  n == 0xfeff || (0xfff9 ≤ n && n ≤ 0xfffb) || n ≥ 0xf0000

def hexDigits (width n : Nat) : String :=
  let digits := Nat.toDigits 16 n
  String.mk (List.replicate (width - digits.length) '0' ++ digits)

/-- Python `repr` of a string: single quotes unless it has a single quote and no double quote; the backslash,
that quote, tab, newline and carriage return escaped by name, and every other non-printable character as
`\xNN`, `\uNNNN` or `\UNNNNNNNN` (looprecheck1 of batch 16b: a name with a control character, a tab or a
no-break space was shown raw where Python shows its escape). -/
def pyRepr (s : String) : String :=
  let q := if s.contains '\'' && !s.contains '"' then '"' else '\''
  let esc := fun (c : Char) =>
    let n := c.toNat
    if c == '\\' then "\\\\" else if c == q then "\\" ++ c.toString
    else if c == '\t' then "\\t" else if c == '\n' then "\\n" else if c == '\r' then "\\r"
    else if !nonPrintable n then c.toString
    else if n ≤ 0xff then "\\x" ++ hexDigits 2 n
    else if n ≤ 0xffff then "\\u" ++ hexDigits 4 n
    else "\\U" ++ hexDigits 8 n
  q.toString ++ String.join (s.toList.map esc) ++ q.toString

#guard pyRepr "in_legal\r" == "'in_legal\\r'"
#guard pyRepr "i\tn" == "'i\\tn'"
#guard pyRepr "adopted\x1c" == "'adopted\\x1c'"
#guard pyRepr "g\u00a0uarantee" == "'g\\xa0uarantee'"
#guard pyRepr "a\u2028b" == "'a\\u2028b'"
#guard pyRepr "bob\u2019" == "'bob\u2019'"
#guard pyRepr "it's" == "\"it's\""
#guard pyRepr "a'b\"c" == "'a\\'b\"c'"
#guard pyRepr "a\\b" == "'a\\\\b'"

/-- Python `repr` of a tuple of strings: `('a',)`, `('a', 'b')`. -/
def pyTuple : List String → String
  | [s] => "(" ++ pyRepr s ++ ",)"
  | ss => "(" ++ ", ".intercalate (ss.map pyRepr) ++ ")"

def intSort : String := "$int"

/-- The diagnostic of the first error, as `Except` with the message on the
left; the state is `_Checker.nodes`. -/
abbrev Check := StateT Nat (Except String)

def fail {α : Type} (code message : String) : Check α := throw s!"{code}: {message}"

/-- Python `ve/limits.py` `MAX_NODES` and `MAX_DEPTH`. -/
def maxNodes : Nat := 10000
def maxDepth : Nat := 64

/-- `_Checker.tick`. -/
def tick : Check Unit := do
  let n ← get
  if n + 1 > maxNodes then fail "ResourceLimit" "AST exceeds 10,000 nodes"
  set (n + 1)

/-- Python `repr` of a JSON value the Python decoder accepts as a name. -/
def pyJson : Nat → Json → String
  | 0, _ => "..."
  | _ + 1, .str s => pyRepr s
  | _ + 1, .bool true => "True"
  | _ + 1, .bool false => "False"
  | _ + 1, .null => "None"
  | _ + 1, .num n => toString n
  | n + 1, .arr a => "[" ++ ", ".intercalate (a.toList.map (pyJson n)) ++ "]"
  | n + 1, .obj o => "{" ++ ", ".intercalate (o.toList.map fun (k, v) => pyRepr k ++ ": " ++ pyJson n v) ++ "}"

/-- Python `repr` of any decoded JSON value (a list or an object as Python shows it, not as JSON). -/
def pyValue (j : Json) : String := pyJson 64 j

#guard pyValue (Json.arr #[]) == "[]"
#guard pyValue (Json.mkObj []) == "{}"
#guard pyValue (Json.arr #[.str "a", .bool true, .null, toJson (7 : Nat)]) == "['a', True, None, 7]"

def term (sig : Signature) (ctx : List String) (depth : Nat) : Nat → Json → Check String
  | 0, _ => fail "TypeMismatch" "Expected a variable or constant term"
  | fuel + 1, j => do
    tick
    if depth > maxDepth then fail "ResourceLimit" "Arithmetic term exceeds 64 nesting levels"
    let items ← match j.getArr? with
      | .ok items => pure items.toList
      | .error _ => fail "TypeMismatch" "Expected a variable or constant term"
    match items with
    | [.str "var", index] =>
      let i ← match index.getNat? with
        | .ok i => pure i
        | .error _ => fail "UnboundVariable" "Variable index must be a bounded nonnegative integer (not Boolean)"
      match ctx[i]? with
      | some sort => pure sort
      | none => fail "UnboundVariable" s!"Variable index {i} is outside its scope"
    | [.str "const", .str name] =>
      match VE.Bridge.lookup sig.constants name with
      | some sort => pure sort
      | none => fail "UnknownSymbol" s!"Unknown constant {pyRepr name}"
    | [.str "const", other] => fail "UnknownSymbol" s!"Unknown constant {pyValue other}"
    | .str tag :: rest =>
      if tag == "num" || tag == "add" || tag == "scale" then do
        unless sig.profiles.contains "order@0" do
          fail "UnsupportedProfile" "Integer arithmetic requires order@0"
        let parts := if tag == "num" then [] else if tag == "scale" then rest.drop 1 else rest
        for part in parts do
          if (← term sig ctx (depth + 1) fuel part) != intSort then
            fail "TypeMismatch" "Arithmetic requires integer operands"
        pure intSort
      else fail "TypeMismatch" "Expected a variable or constant term"
    | _ => fail "TypeMismatch" "Expected a variable or constant term"

/-- Walk a formula in `_Checker.formula` order. The error channel carries the
first diagnostic; `false` is an unrecognised construct, which ends the walk
without one. -/
def formula (sig : Signature) (ctx : List String) (depth : Nat) : Nat → Json → Check Bool
  | 0, _ => pure false
  | fuel + 1, j => do
    tick
    if depth > maxDepth then fail "ResourceLimit" "Formula exceeds 64 nesting levels"
    let items ← match j.getArr? with
      | .ok items => pure items.toList
      | .error _ => return false
    let t := term sig ctx 1 (maxDepth + 1)
    let .str tag :: args := items | return false
    if tag == "top" || tag == "bottom" then return args.isEmpty
    if tag == "unary" || tag == "binary" || tag == "atom" then
      let p :: rest := args | return false
      let some signature := (match p with
          | .str name => VE.Bridge.lookup sig.predicates name
          | _ => none)
        | fail "UnknownSymbol" s!"Unknown predicate {pyValue p}"
      let terms ← if tag == "atom" then match rest with
          | [ts] => match ts.getArr? with
            | .ok ts => pure ts.toList
            | .error _ => return false
          | _ => return false
        else pure rest
      if tag == "atom" && (!sig.profiles.contains "nary@0" || terms.length < 3 || terms.length > 6) then
        fail "UnsupportedProfile" "Atom requires nary@0 and arity from three to six"
      let name := pyValue p
      if signature.length != terms.length then
        fail "TypeMismatch" s!"Predicate {name} has arity {signature.length}, not {terms.length}"
      let actual ← terms.mapM t
      if actual != signature then
        fail "TypeMismatch" s!"Predicate {name} expects {pyTuple signature}, received {pyTuple actual}"
      return true
    if tag == "reach" then
      let [kind, edge, left, right] := args | return false
      unless sig.profiles.contains "closure@0" do fail "UnsupportedProfile" "Reach requires closure@0"
      unless kind == .str "plus" || kind == .str "star" do
        fail "TypeMismatch" "Reach kind must be plus or star"
      let edgeSort : Check (Option String) := match edge.getArr?.toOption.map Array.toList with
        | some [.str "named", relation] =>
          match (match relation with
              | .str name => VE.Bridge.lookup sig.predicates name
              | _ => none) with
          | none => fail "UnknownSymbol" s!"Unknown closure relation {pyValue relation}"
          | some [a, b] => if a == b then pure (some a)
              else fail "TypeMismatch" "Named closure requires a homogeneous binary relation"
          | some _ => fail "TypeMismatch" "Named closure requires a homogeneous binary relation"
        | some [.str "body", sort, body] => do
          let .str s := sort | fail "UnknownSymbol" s!"Unknown closure sort {pyValue sort}"
          unless sig.sorts.contains s do fail "UnknownSymbol" s!"Unknown closure sort {pyRepr s}"
          if ← formula sig (s :: s :: ctx) (depth + 1) fuel body then pure (some s) else pure none
        | _ => pure none
      let some sort ← edgeSort | return false
      if (← t left) != sort then
        fail "TypeMismatch" "Closure endpoints must have the edge sort in the outer context"
      if (← t right) != sort then
        fail "TypeMismatch" "Closure endpoints must have the edge sort in the outer context"
      return true
    if tag == "forall" || tag == "exists" then
      let [sort, body] := args | return false
      let known := match sort with
        | .str s => sig.sorts.contains s
        | _ => false
      unless known do
        if sort == .str "$string" && sig.profiles.contains "data@0" then
          fail "UnsupportedProfile" "$string quantification requires data stage 2"
        fail "UnknownSymbol" s!"Unknown binder sort {pyValue sort}"
      let .str s := sort | return false
      return ← formula sig (s :: ctx) (depth + 1) fuel body
    if tag == "not" then
      let [body] := args | return false
      return ← formula sig ctx (depth + 1) fuel body
    let [left, right] := args | return false
    if tag == "and" || tag == "or" || tag == "implies" then
      unless ← formula sig ctx (depth + 1) fuel left do return false
      return ← formula sig ctx (depth + 1) fuel right
    if tag == "lt" || tag == "le" then
      unless sig.profiles.contains "order@0" do fail "UnsupportedProfile" "Comparisons require order@0"
      if (← t left) != intSort then fail "TypeMismatch" "Comparisons require integer terms"
      if (← t right) != intSort then fail "TypeMismatch" "Comparisons require integer terms"
      return true
    if tag == "eq" then
      let a ← t left
      let b ← t right
      if a != b then
        fail "TypeMismatch" s!"Equality requires one sort, received {pyRepr a} and {pyRepr b}"
      return true
    return false

/-- The Python diagnostic for the first ill-typed or over-budget formula of
`asts`, if the walk finds one; one node counter spans the list. -/
def diagnose (profiles : List String) (vocabulary : Json) (asts : List Json) : Option String :=
  match decodeSignature profiles vocabulary with
  | .error _ => none
  | .ok sig =>
    let rec go : List Json → Check Bool
      | [] => pure true
      | a :: rest => do
        unless ← formula sig [] 1 (maxDepth + 1) a do return false
        go rest
    match (go asts).run' 0 with
    | .error message => some message
    | .ok _ => none

end VE.Service.TypingDiagnostic
