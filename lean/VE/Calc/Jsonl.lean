import VE.Calc.Table
import Lean.Data.Json

/-! The JSON-lines subset of spec 4.1: one flat object per line, columns read by top-level key. A key appears once
(Lean's own JSON parser keeps the last of two equal keys, a second reading, so this reader refuses them). A line is a
flat object of scalars (a string, a number, `true`, `false` or `null`; an array or object fails). A missing key or
`null` is absent; a string is read as a CSV field; a JSON number or Boolean is that value in a column of its type and
is kept as text in any other. -/

namespace VE.Calc
open Lean Std.Internal.Parsec Std.Internal.Parsec.String

def jsonScalar : Parser Json := do
  let c ← peek!
  if c == '"' then skip; return .str (← Json.Parser.str)
  else if c == 't' then skipString "true"; return .bool true
  else if c == 'f' then skipString "false"; return .bool false
  else if c == 'n' then skipString "null"; return .null
  else return .num (← Json.Parser.num)

def jsonFlatObject : Parser (List (String × Json)) := do
  ws; skipChar '{'; ws
  if (← peek!) == '}' then skip; ws; eof; return []
  let pair : Parser (String × Json) := do
    skipChar '"'; let k ← Json.Parser.str; ws; skipChar ':'; ws; let v ← jsonScalar; ws; pure (k, v)
  let ps := (← pair) :: (← many (skipChar ',' *> ws *> pair)).toList
  skipChar '}'; ws; eof; pure ps

def jsonCell (t : ColType) : Option Json → Cell
  | some (.str s) => readCell t s
  | some (.num n) => if t = .number then .num (n.mantissa / (10 ^ n.exponent : Nat)) else .text n.toString
  | some (.bool b) => if t = .bool then .bool b else .text (toString b)
  | _ => .absent

def decodeJsonl (decl : List (String × ColType)) (bytes : ByteArray) : Except String Table := do
  let some text := String.fromUTF8? bytes | throw "TableFormat: the bytes are not UTF-8"
  let lines := (text.splitOn "\n").map fun l => if l.endsWith "\r" then l.dropRight 1 else l
  let lines := if lines.getLast? = some "" then lines.dropLast else lines
  let rows ← lines.mapM fun l => do
    let some pairs := (Parser.run jsonFlatObject l).toOption | throw "TableFormat: a line is not a flat JSON object"
    let keys := pairs.map Prod.fst
    unless keys.eraseDups.length = keys.length do throw "TableFormat: a repeated key"
    if let some k := keys.find? (fun k => (decl.lookup k).isNone) then throw s!"TableFormat: an undeclared column {k}"
    pure (decl.map fun (c, t) => jsonCell t (pairs.lookup c))
  pure ⟨decl.map Prod.fst, rows⟩

end VE.Calc
