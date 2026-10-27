/- AR-20 evidence, not part of the build: main's (f1943fab6) `canonical` and `documentCanonical`, copied
verbatim into `Old`, against this branch's over generated JSON values and fuels, including errors.
Run: cd lean && lake env lean ../docs/arch/AR-20/canonical_equiv.lean -/
import VE.CertificateWire
open Lean
namespace Old
def quoted (s : String) : String :=
  "\"" ++ s.foldl (fun acc c => acc ++ match c with
    | '"' => "\\\"" | '\\' => "\\\\" | '\x08' => "\\b" | '\x0c' => "\\f"
    | '\n' => "\\n" | '\r' => "\\r" | '\t' => "\\t"
    | _ => if c.toNat < 32 then "\\u00" ++ String.mk
        [Nat.digitChar (c.toNat / 16), Nat.digitChar (c.toNat % 16)]
      else String.singleton c) "" ++ "\""

def utf16 (s : String) : List Nat := s.toList.flatMap fun c =>
  let n := c.toNat
  if n < 65536 then [n] else [55296 + (n-65536)/1024, 56320 + (n-65536)%1024]

/-- Restricted canonical JSON, including UTF-16 object-key ordering. -/
def canonical : Nat → Json → Except String String
  | 0, _ => throw "ResourceLimit: canonical JSON depth"
  | fuel+1, j => match j with
    | .str s => pure (quoted s)
    | .bool b => pure (if b then "true" else "false")
    | .num _ => do pure (toString (← j.getNat?))
    | .null => throw "null is not in certificate wire format"
    | .arr xs => do
      let parts ← xs.toList.mapM (canonical fuel)
      pure ("[" ++ String.intercalate "," parts ++ "]")
    | .obj obj => do
      let pairs := obj.toList.mergeSort (fun a b => compare (utf16 a.1) (utf16 b.1) != .gt)
      let parts ← pairs.mapM fun (k,v) => do pure (quoted k ++ ":" ++ (← canonical fuel v))
      pure ("{" ++ String.intercalate "," parts ++ "}")

/-- Document front matter permits JSON null. Keep certificate canonicalisation unchanged;
this is the same Python-compatible encoding with one additional JSON constructor. -/
def documentCanonical : Nat → Json → Except String String
  | 0, _ => throw "ResourceLimit: canonical JSON depth"
  | fuel+1, j => match j with
    | .null => pure "null"
    | .arr xs => do
      let parts ← xs.toList.mapM (documentCanonical fuel)
      pure ("[" ++ String.intercalate "," parts ++ "]")
    | .obj obj => do
      let pairs := obj.toList.mergeSort (fun a b => compare (utf16 a.1) (utf16 b.1) != .gt)
      let parts ← pairs.mapM fun (k,v) => do pure (quoted k ++ ":" ++ (← documentCanonical fuel v))
      pure ("{" ++ String.intercalate "," parts ++ "}")
    | _ => canonical (fuel+1) j


end Old

def samples : List Json := Id.run do
  let atoms : List Json := [.null, .bool true, .bool false, (7 : Nat), (0 : Nat), Json.num (-3), Json.num ⟨15, 1⟩,
    "", "a\"b\\c\n\t\u0001\u001f é 𝔸", Json.arr #[], Json.mkObj []]
  let keys := ["a", "B", "é", "𝔸", "\u0000", "aa", "ﬀ"]
  let mut level := atoms
  let mut all := atoms
  for _ in [0:3] do
    let arrs := (level.take 6).map (fun x => Json.arr #[x, .null, x])
    let objs := (List.range 6).map (fun k => Json.mkObj ((keys.drop (k % 4)).zip (level.drop k)))
    level := arrs ++ objs ++ [Json.arr (level.toArray.extract 0 4)]
    all := all ++ level
  pure all

def agree (fuel : Nat) (j : Json) : Bool :=
  (Old.canonical fuel j).toBool == (VE.CertificateWire.canonical fuel j).toBool &&
  reprStr (Old.canonical fuel j) == reprStr (VE.CertificateWire.canonical fuel j) &&
  reprStr (Old.documentCanonical fuel j) == reprStr (VE.CertificateWire.documentCanonical fuel j)

#eval do
  let fuels := [0, 1, 2, 3, 4, 257]
  let results := samples.flatMap (fun j => fuels.map (fun f => agree f j))
  IO.println s!"{samples.length} inputs x {fuels.length} fuels: {results.filter id |>.length}/{results.length} agree"
