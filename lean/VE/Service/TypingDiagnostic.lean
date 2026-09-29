import VE.Bridge

/-! Python-compatible typing diagnostics for the standalone `check` mode.

The verdict of a typing request is always the proved family decoder's. When
that decoder rejects a formula as ill typed, this classifier walks the wire AST
in the order of Python's `_Checker` (`ve/ast.py`) and names the first error
with Python's code and message (`UnknownSymbol`, `TypeMismatch`,
`UnboundVariable`, `UnsupportedProfile`), so diagnostic codes agree at zero
tolerance (SEMANTICS-MIGRATION-PLAN.md 2a). It never accepts anything: if it
finds no error, the decoder's own message stands. Node and depth budgets are
the decoder's and are not re-checked here. -/
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

/-- Python `repr` of an identifier-like string. -/
def pyRepr (s : String) : String :=
  if s.contains '\'' && !s.contains '"' then "\"" ++ s ++ "\""
  else "'" ++ (s.replace "\\" "\\\\").replace "'" "\\'" ++ "'"

/-- Python `repr` of a tuple of strings: `('a',)`, `('a', 'b')`. -/
def pyTuple : List String → String
  | [s] => "(" ++ pyRepr s ++ ",)"
  | ss => "(" ++ ", ".intercalate (ss.map pyRepr) ++ ")"

def intSort : String := "$int"

/-- The diagnostic of the first error, as `Except` with the message on the left. -/
abbrev Check := Except String

def fail {α : Type} (code message : String) : Check α := .error s!"{code}: {message}"

def term (sig : Signature) (ctx : List String) : Nat → Json → Check String
  | 0, _ => fail "TypeMismatch" "Expected a variable or constant term"
  | fuel + 1, j => do
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
    | [.str "const", _] => fail "UnknownSymbol" "Unknown constant"
    | .str tag :: rest =>
      if tag == "num" || tag == "add" || tag == "scale" then do
        unless sig.profiles.contains "order@0" do
          fail "UnsupportedProfile" "Integer arithmetic requires order@0"
        let parts := if tag == "num" then [] else if tag == "scale" then rest.drop 1 else rest
        for part in parts do
          if (← term sig ctx fuel part) != intSort then
            fail "TypeMismatch" "Arithmetic requires integer operands"
        pure intSort
      else fail "TypeMismatch" "Expected a variable or constant term"
    | _ => fail "TypeMismatch" "Expected a variable or constant term"

/-- Walk a formula in `_Checker.formula` order. `none` in the error channel is
not used: an unrecognised construct ends the walk without a diagnostic. -/
def formula (sig : Signature) (ctx : List String) : Nat → Json → Check Bool
  | 0, _ => pure false
  | fuel + 1, j => do
    let items ← match j.getArr? with
      | .ok items => pure items.toList
      | .error _ => return false
    let t := term sig ctx 64
    match items with
    | [.str "top"] | [.str "bottom"] => pure true
    | .str tag :: .str p :: rest =>
      if tag == "unary" || tag == "binary" || tag == "atom" then do
        let some signature := VE.Bridge.lookup sig.predicates p
          | fail "UnknownSymbol" s!"Unknown predicate {pyRepr p}"
        let terms ← if tag == "atom" then match rest with
            | [ts] => match ts.getArr? with
              | .ok ts => pure ts.toList
              | .error _ => return false
            | _ => return false
          else pure rest
        if tag == "atom" && (!sig.profiles.contains "nary@0" || terms.length < 3 || terms.length > 6) then
          fail "UnsupportedProfile" "Atom requires nary@0 and arity from three to six"
        if signature.length != terms.length then
          fail "TypeMismatch" s!"Predicate {pyRepr p} has arity {signature.length}, not {terms.length}"
        let actual ← terms.mapM t
        if actual != signature then
          fail "TypeMismatch" s!"Predicate {pyRepr p} expects {pyTuple signature}, received {pyTuple actual}"
        pure true
      else if tag == "reach" then do
        unless sig.profiles.contains "closure@0" do fail "UnsupportedProfile" "Reach requires closure@0"
        unless p == "plus" || p == "star" do fail "TypeMismatch" "Reach kind must be plus or star"
        let [edge, left, right] := rest | return false
        let edgeSort : Check (Option String) := match edge.getArr?.toOption.map Array.toList with
          | some [.str "named", .str relation] =>
            match VE.Bridge.lookup sig.predicates relation with
            | none => fail "UnknownSymbol" s!"Unknown closure relation {pyRepr relation}"
            | some [a, b] => if a == b then pure (some a)
                else fail "TypeMismatch" "Named closure requires a homogeneous binary relation"
            | some _ => fail "TypeMismatch" "Named closure requires a homogeneous binary relation"
          | some [.str "body", .str sort, body] => do
            unless sig.sorts.contains sort do fail "UnknownSymbol" s!"Unknown closure sort {pyRepr sort}"
            if ← formula sig (sort :: sort :: ctx) fuel body then pure (some sort) else pure none
          | _ => pure none
        let some sort ← edgeSort | return false
        if (← t left) != sort then
          fail "TypeMismatch" "Closure endpoints must have the edge sort in the outer context"
        if (← t right) != sort then
          fail "TypeMismatch" "Closure endpoints must have the edge sort in the outer context"
        pure true
      else if tag == "forall" || tag == "exists" then do
        unless sig.sorts.contains p do
          if p == "$string" && sig.profiles.contains "data@0" then
            fail "UnsupportedProfile" "$string quantification requires data stage 2"
          fail "UnknownSymbol" s!"Unknown binder sort {pyRepr p}"
        let [body] := rest | return false
        formula sig (p :: ctx) fuel body
      else pure false
    | [.str "not", body] => formula sig ctx fuel body
    | [.str tag, left, right] =>
      if tag == "and" || tag == "or" || tag == "implies" then do
        unless ← formula sig ctx fuel left do return false
        formula sig ctx fuel right
      else if tag == "lt" || tag == "le" then do
        unless sig.profiles.contains "order@0" do fail "UnsupportedProfile" "Comparisons require order@0"
        if (← t left) != intSort then fail "TypeMismatch" "Comparisons require integer terms"
        if (← t right) != intSort then fail "TypeMismatch" "Comparisons require integer terms"
        pure true
      else if tag == "eq" then do
        let a ← t left
        let b ← t right
        if a != b then
          fail "TypeMismatch" s!"Equality requires one sort, received {pyRepr a} and {pyRepr b}"
        pure true
      else pure false
    | _ => pure false

/-- The Python diagnostic for the first ill-typed formula of `asts`, if the
walk finds one. -/
def diagnose (profiles : List String) (vocabulary : Json) (asts : List Json) : Option String :=
  match decodeSignature profiles vocabulary with
  | .error _ => none
  | .ok sig =>
    let rec go : List Json → Option String
      | [] => none
      | a :: rest => match formula sig [] 65 a with
        | .error message => some message
        | .ok true => go rest
        | .ok false => none
    go asts

end VE.Service.TypingDiagnostic
