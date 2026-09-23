import VE.Bridge
import VE.TableauChecker
import VE.TableauExtendedChecker
import VE.Closure.Bridge

/-! The data-only wire adapter. Serialization and hash identity correspondence
are tested boundary code, not additional premises of tableau soundness. -/
namespace VE.CertificateWire
open Lean

private def roundConstants : Array UInt32 := #[
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]

private def rotate (x : UInt32) (n : UInt32) : UInt32 := (x >>> n) ||| (x <<< (32 - n))

private def shaBlock (state : Array UInt32) (bytes : ByteArray) (offset : Nat) : Array UInt32 := Id.run do
  let mut w : Array UInt32 := #[]
  for i in [0:16] do
    let j := offset + 4 * i
    let word := (bytes[j]!.toUInt32 <<< 24) ||| (bytes[j+1]!.toUInt32 <<< 16) |||
      (bytes[j+2]!.toUInt32 <<< 8) ||| bytes[j+3]!.toUInt32
    w := w.push word
  for i in [16:64] do
    let x := w[i-15]!
    let y := w[i-2]!
    let s0 := rotate x 7 ^^^ rotate x 18 ^^^ (x >>> 3)
    let s1 := rotate y 17 ^^^ rotate y 19 ^^^ (y >>> 10)
    w := w.push (w[i-16]! + s0 + w[i-7]! + s1)
  let mut a := state[0]!
  let mut b := state[1]!
  let mut c := state[2]!
  let mut d := state[3]!
  let mut e := state[4]!
  let mut f := state[5]!
  let mut g := state[6]!
  let mut h := state[7]!
  for i in [0:64] do
    let s1 := rotate e 6 ^^^ rotate e 11 ^^^ rotate e 25
    let ch := (e &&& f) ^^^ ((~~~e) &&& g)
    let t1 := h + s1 + ch + roundConstants[i]! + w[i]!
    let s0 := rotate a 2 ^^^ rotate a 13 ^^^ rotate a 22
    let maj := (a &&& b) ^^^ (a &&& c) ^^^ (b &&& c)
    let t2 := s0 + maj
    h := g; g := f; f := e; e := d + t1
    d := c; c := b; b := a; a := t1 + t2
  return (state.zip #[a,b,c,d,e,f,g,h]).map fun (x,y) => x+y

def sha256 (input : ByteArray) : String := Id.run do
  let bitLength := input.size * 8
  let mut bytes := input.push 128
  let padding := (64 - ((bytes.size + 8) % 64)) % 64
  for _ in [0:padding] do bytes := bytes.push 0
  for i in [0:8] do bytes := bytes.push ((bitLength / 2^(8*(7-i))) % 256).toUInt8
  let mut state : Array UInt32 := #[0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
  for block in [0:bytes.size / 64] do state := shaBlock state bytes (block*64)
  return String.mk (state.toList.flatMap fun word =>
    (List.range 8).map fun i => Nat.digitChar ((word.toNat / 16^(7-i)) % 16))

#guard sha256 "".toUTF8 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
#guard sha256 "abc".toUTF8 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
#guard sha256 "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq".toUTF8 ==
  "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"

private def quoted (s : String) : String :=
  "\"" ++ s.foldl (fun acc c => acc ++ match c with
    | '"' => "\\\"" | '\\' => "\\\\" | '\x08' => "\\b" | '\x0c' => "\\f"
    | '\n' => "\\n" | '\r' => "\\r" | '\t' => "\\t"
    | _ => if c.toNat < 32 then "\\u00" ++ String.mk
        [Nat.digitChar (c.toNat / 16), Nat.digitChar (c.toNat % 16)]
      else String.singleton c) "" ++ "\""

private def utf16 (s : String) : List Nat := s.toList.flatMap fun c =>
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

def digest (domain : String) (j : Json) : Except String String := do
  pure (sha256 (domain ++ (← canonical 257 j)).toUTF8)

def decodeTrace : Nat → Json → Except String Tableau.Trace
  | 0, _ => throw "ResourceLimit: certificate expansion depth exceeds 124"
  | fuel + 1, j => do
    let rule ← Bridge.stringField j "rule"
    if rule == "close" then
      Bridge.exactFields j ["rule"]
      pure .close
    else if rule == "expand" then
      let names := (← Bridge.fields j).map Prod.fst
      let optional := names.contains "parameter"
      Bridge.exactFields j (["rule", "at", "children"] ++ if optional then ["parameter"] else [])
      let index ← (← j.getObjVal? "at").getNat?
      let parameter ← if optional then do pure (some (← Bridge.stringField j "parameter")) else pure none
      let children ← (← (← j.getObjVal? "children").getArr?).toList.mapM (decodeTrace fuel)
      pure (.expand index parameter children)
    else throw "unknown tableau rule"

def decodeCertificate (j : Json) : Except String Tableau.Certificate := do
  Bridge.exactFields j ["checker_version", "environment_id", "premise_meaning_ids",
    "conclusion_meaning_id", "trace"]
  pure ⟨← Bridge.stringField j "checker_version", ← Bridge.stringField j "environment_id",
    ← Bridge.strings (← j.getObjVal? "premise_meaning_ids"),
    ← Bridge.stringField j "conclusion_meaning_id", ← decodeTrace 125 (← j.getObjVal? "trace")⟩

def decodeClosureTrace : Nat → Json → Except String Closure.Tableau.Trace
  | 0, _ => throw "ResourceLimit: certificate expansion depth exceeds 124"
  | fuel + 1, j => do
    let rule ← Bridge.stringField j "rule"
    if rule == "close" then
      Bridge.exactFields j ["rule"]
      pure .close
    else if rule == "closure-induct@1" then
      Bridge.exactFields j ["rule", "at", "sort", "invariant", "children"]
      let index ← (← j.getObjVal? "at").getNat?
      let sort ← Bridge.stringField j "sort"
      let invariant ← Closure.Bridge.decodeFormula 64 (← j.getObjVal? "invariant")
      if Closure.Bridge.formulaNodes invariant > 10000 then
        throw "ResourceLimit: invariant AST node count"
      let children ← (← (← j.getObjVal? "children").getArr?).toList.mapM (decodeClosureTrace fuel)
      pure (.induct index sort invariant children)
    else if rule == "expand" || rule == "closure-plus@0" || rule == "closure-star@0" ||
        Closure.Tableau.extraRule rule then
      let names := (← Bridge.fields j).map Prod.fst
      let optional := names.contains "parameter"
      Bridge.exactFields j (["rule", "at", "children"] ++ if optional then ["parameter"] else [])
      let index ← (← j.getObjVal? "at").getNat?
      let parameter ← if optional then do pure (some (← Bridge.stringField j "parameter")) else pure none
      let children ← (← (← j.getObjVal? "children").getArr?).toList.mapM (decodeClosureTrace fuel)
      pure (.expand rule index parameter children)
    else throw "unknown tableau rule"

def decodeClosureCertificate (j : Json) : Except String Closure.Tableau.Certificate := do
  Bridge.exactFields j ["checker_version", "environment_id", "premise_meaning_ids",
    "conclusion_meaning_id", "trace"]
  pure ⟨← Bridge.stringField j "checker_version", ← Bridge.stringField j "environment_id",
    ← Bridge.strings (← j.getObjVal? "premise_meaning_ids"),
    ← Bridge.stringField j "conclusion_meaning_id", ← decodeClosureTrace 125 (← j.getObjVal? "trace")⟩

def meaningId (environmentId : String) (ast : Json) : Except String String :=
  digest "ve-meaning-v0\n" (Json.mkObj [("environment_id", .str environmentId), ("ast", ast)])

structure Query (E : Environment) where
  formulas : Bridge.CountermodelQuery E
  certificate : Tableau.Certificate

def Query.accepts {E : Environment} (q : Query E) : Bool :=
  Tableau.checkCertificate E q.formulas.premises q.formulas.conclusion q.certificate

/-- JSON-facing P9 uses exactly Entails at universe zero, the same target as
countermodel refutation. The generic checker theorem holds at every universe. -/
theorem Query.accepts_sound {E : Environment} (q : Query E) (h : q.accepts = true) :
    Bridge.JsonEntails E q.formulas.premises q.formulas.conclusion :=
  Tableau.checkCertificate_sound E q.formulas.premises q.formulas.conclusion q.certificate h

def decodeQuery (environment : Json) (v : Bridge.Vocabulary) (j : Json) : Except String (Query v.environment) := do
  let formulas ← Bridge.decodeCountermodel v.environment j
  let certificate ← decodeCertificate (← j.getObjVal? "certificate")
  let environmentId ← digest "ve-environment-v0\n" environment
  let premises ← (← (← j.getObjVal? "premises").getArr?).toList.mapM (meaningId environmentId)
  let conclusion ← meaningId environmentId (← j.getObjVal? "conclusion")
  unless certificate.environment_id == environmentId && certificate.premise_meaning_ids == premises &&
      certificate.conclusion_meaning_id == conclusion do
    throw "certificate is stale or bound to different inputs"
  pure ⟨formulas, certificate⟩

structure ClosureQuery (E : Environment) where
  premises : List Closure.Formula
  conclusion : Closure.Formula
  certificate : Closure.Tableau.Certificate

def ClosureQuery.accepts {E : Environment} (q : ClosureQuery E) : Bool :=
  Closure.Tableau.checkCertificate E q.premises q.conclusion q.certificate

theorem ClosureQuery.accepts_sound {E : Environment} (q : ClosureQuery E)
    (h : q.accepts = true) : Closure.Entails.{0} E q.premises q.conclusion :=
  Closure.Tableau.checkCertificate_sound E q.premises q.conclusion q.certificate h

def runClosureCase (j : Json) : Except String Json := do
  let id ← Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let v ← Closure.Bridge.decodeEnvironment environment
  let ps ← Closure.Bridge.decodeFormulas v.environment (← j.getObjVal? "premises")
  let c ← Closure.Bridge.decodeFormula 64 (← j.getObjVal? "conclusion")
  unless c.check v.environment [] do throw "ill-typed or unbound conclusion"
  if ((c :: ps).map Closure.Bridge.formulaNodes).foldl (· + ·) 0 > 10000 then
    throw "ResourceLimit: AST node count"
  let certificate ← decodeClosureCertificate (← j.getObjVal? "certificate")
  let environmentId ← digest "ve-environment-v0.1\n" environment
  let mid := fun ast => digest "ve-meaning-v0.1\n"
    (Json.mkObj [("environment_id", .str environmentId), ("ast", ast)])
  let premises ← (← (← j.getObjVal? "premises").getArr?).toList.mapM mid
  let conclusion ← mid (← j.getObjVal? "conclusion")
  unless certificate.environment_id == environmentId && certificate.premise_meaning_ids == premises &&
      certificate.conclusion_meaning_id == conclusion do
    throw "certificate is stale or bound to different inputs"
  let q : ClosureQuery v.environment := ⟨ps,c,certificate⟩
  pure (Json.mkObj [("id", .str id), ("status", .str "ok"), ("valid", .bool q.accepts)])

def runCase (j : Json) : Except String Json := do
  let id ← Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  if environment.getObjValD "language" == .str "ve.core@0.1" then
    return ← runClosureCase j
  let v ← Bridge.decodeEnvironment environment
  let q ← decodeQuery environment v j
  pure (Json.mkObj [("id", .str id), ("status", .str "ok"), ("valid", .bool q.accepts)])

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
      ("valid", .bool false), ("error", .str message)]

end VE.CertificateWire
