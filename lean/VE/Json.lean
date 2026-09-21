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

def parse (text : String) : Except String Json := do
  if text.utf8ByteSize > 16777216 then throw "ResourceLimit: package exceeds 16 MiB"
  Parser.run (do ws; let j ← value 256; eof; pure j) text

end VE.JsonInput
