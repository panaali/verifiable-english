import Lean.Data.Json
import Std.Internal.Parsec

/-! Restricted JSON input boundary. Unlike Lean.Json.parse, this rejects duplicate
keys, unpaired surrogate escapes, null, fractions and exponents. This decoder is
executable and tested, but has no refinement theorem against the wire spec. -/
namespace VE.JsonInput
open Lean Std.Internal.Parsec Std.Internal.Parsec.String

private def escaped : Parser Char := do
  match ← any with
  | '"' => pure '"'
  | '\\' => pure '\\'
  | '/' => pure '/'
  | 'b' => pure '\x08'
  | 'f' => pure '\x0c'
  | 'n' => pure '\n'
  | 'r' => pure '\r'
  | 't' => pure '\t'
  | 'u' =>
    let a ← Json.Parser.hexChar
    let b ← Json.Parser.hexChar
    let c ← Json.Parser.hexChar
    let d ← Json.Parser.hexChar
    let v := (a <<< 12) ||| (b <<< 8) ||| (c <<< 4) ||| d
    if v ≥ 0xD800 && v < 0xDC00 then
      Json.Parser.finishSurrogatePair v
    else if v ≥ 0xDC00 && v < 0xE000 then
      fail "unpaired surrogate"
    else
      pure (Char.ofNat v.toNat)
  | _ => fail "invalid string escape"

private def quoted : Parser String := do
  skipChar '"'
  let chars ← manyChars do
    let c ← peek!
    if c == '"' then fail "end of string"
    skip
    if c == '\\' then escaped
    else if c.toNat < 32 then fail "unescaped control character"
    else pure c
  skipChar '"'
  pure chars

private def values (p : Parser α) (closing : Char) : Parser (Array α) := do
  if (← peek!) == closing then
    skip; ws
    return #[]
  let first ← p
  let rest ← many (skipChar ',' *> ws *> p)
  skipChar closing; ws
  pure (#[first] ++ rest)

private def value : Nat → Parser Json
  | 0 => fail "ResourceLimit: JSON depth exceeds 256"
  | fuel + 1 => do
    let c ← peek!
    if c == '[' then
      skip; ws
      return .arr (← values (value fuel) ']')
    else if c == '{' then
      skip; ws
      let pairs ← values (do
        let key ← quoted
        ws; skipChar ':'; ws
        let val ← value fuel
        pure (key, val)) '}'
      let keys := pairs.toList.map Prod.fst
      if keys.eraseDups.length != keys.length then fail "duplicate object key"
      return Json.mkObj pairs.toList
    else if c == '"' then
      let s ← quoted
      ws
      return .str s
    else if c == 't' then
      skipString "true"; ws
      return .bool true
    else if c == 'f' then
      skipString "false"; ws
      return .bool false
    else if c ≥ '0' && c ≤ '9' then
      let n ← Json.Parser.nat
      if n > 9007199254740991 then fail "integer out of range"
      ws
      return toJson n
    else fail "expected restricted JSON value"

def parse (text : String) (depth : Nat := 256) : Except String Json := do
  if text.utf8ByteSize > 16777216 then throw "ResourceLimit: package exceeds 16 MiB"
  Parser.run (do ws; let j ← value depth; eof; pure j) text

/-- Split only the outer batch array, without recursively decoding its cases.
Each slice still goes through the restricted parser. This lets a depth error
stay local to one case without allocating a deeply nested Json value. -/
private def caseTexts (text : String) : Except String (Array String) := do
  let text := text.trim
  if !text.startsWith "[" then return #[text]
  unless text.endsWith "]" do throw "unterminated batch array"
  let body := (text.drop 1).dropRight 1
  if body.trim.isEmpty then return #[]
  let mut cases := #[]
  let mut chars : Array Char := #[]
  let mut depth := 0
  let mut quoted := false
  let mut escaped := false
  for c in body.toList do
    if !quoted && depth == 0 && c == ',' then
      cases := cases.push (String.mk chars.toList)
      chars := #[]
    else
      chars := chars.push c
      if quoted then
        if escaped then escaped := false
        else if c == '\\' then escaped := true
        else if c == '"' then quoted := false
      else if c == '"' then quoted := true
      else if c == '[' || c == '{' then depth := depth + 1
      else if c == ']' || c == '}' then
        if depth == 0 then throw "unexpected batch delimiter"
        depth := depth - 1
  if quoted || depth != 0 then throw "unterminated batch case"
  return cases.push (String.mk chars.toList)

def parseCases (text : String) : Except String (Array (Except String Json)) := do
  if text.utf8ByteSize > 16777216 then throw "ResourceLimit: package exceeds 16 MiB"
  let depth := if text.trim.startsWith "[" then 255 else 256
  (← caseTexts text).mapM fun raw => do
    match parse raw depth with
    | .ok j => pure (.ok j)
    | .error message =>
      if (message.splitOn "ResourceLimit: JSON depth").length > 1 then
        pure (.error "ResourceLimit: JSON depth exceeds 256")
      else throw message

end VE.JsonInput
