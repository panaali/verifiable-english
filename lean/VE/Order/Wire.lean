import VE.Order.Tableau
import VE.Order.ModelCheck
import VE.CertificateWire

/-! The order@0 wire adapter, reached only through the separate `order`
subcommand. The existing certificate entry point and its profile gate are
unchanged: they still reject every envelope listing order@0.

Accepted envelope: language ve.core@0.1, profiles exactly
["order@0", "relational-fol@0"], revision ve-v0.1-order-2026-09-22. The
combined closure@0 x order@0 list is rejected by exact list comparison.
Integer values are canonical decimal strings. Serialization and hash identity
correspondence are tested boundary code, not premises of tableau soundness. -/
namespace VE.Order.Wire
open Lean
open VE.Bridge (exactFields stringField strings fields identifier reserved generatedName)

def orderLanguage : String := "ve.core@0.1"
def orderProfiles : List String := ["order@0", "relational-fol@0"]
def orderRevision : String := "ve-v0.1-order-2026-09-22"
def maxNumeralChars : Nat := 40

/-- Canonical decimal: optional minus, no leading zeros, no "-0", bounded length. -/
def decodeInt (s : String) : Except String Int := do
  if s.length > maxNumeralChars then throw "ResourceLimit: numeral length"
  match s.toInt? with
  | some z => if toString z == s then pure z else throw "non-canonical integer"
  | none => throw "invalid integer"

def decodeSortName (sorts : List String) (s : String) : Except String SortName :=
  if s == "$int" then pure .int
  else if sorts.contains s then pure (.user s)
  else throw s!"unknown sort: {s}"

def decodeEnvironment (j : Json) : Except String Vocabulary := do
  exactFields j ["language", "profiles", "spec_revision", "vocabulary"]
  unless (← stringField j "language") == orderLanguage &&
      (← strings (← j.getObjVal? "profiles")) == orderProfiles &&
      (← stringField j "spec_revision") == orderRevision do
    throw "unsupported order environment version/profiles"
  let v ← j.getObjVal? "vocabulary"
  exactFields v ["sorts", "predicates", "constants"]
  let sorts ← fields (← v.getObjVal? "sorts")
  let predicates ← fields (← v.getObjVal? "predicates")
  let constants ← fields (← v.getObjVal? "constants")
  let names := (sorts ++ predicates ++ constants).map Prod.fst
  unless names.eraseDups.length == names.length do throw "duplicate declaration"
  for name in names do
    unless identifier name && !reserved.contains name && !generatedName name do
      throw s!"invalid or reserved declaration: {name}"
  if sorts.length > 32 || predicates.length > 256 then
    throw "ResourceLimit: vocabulary size"
  let sortNames := sorts.map Prod.fst
  let ps ← predicates.mapM fun (p, entry) => do
    let ss ← strings (← entry.getObjVal? "arguments")
    unless ss.length == 1 || ss.length == 2 do throw s!"invalid signature: {p}"
    pure (p, ← ss.mapM (decodeSortName sortNames))
  let cs ← constants.mapM fun (c, entry) => do
    pure (c, ← decodeSortName sortNames (← stringField entry "sort"))
  pure ⟨sortNames, ps, cs⟩

def decodeTerm : Nat → Json → Except String Term
  | 0, _ => throw "ResourceLimit: term depth"
  | n + 1, j => do
    match (← j.getArr?).toList with
    | [.str "var", i] => return .var (← i.getNat?)
    | [.str "const", .str c] => return .const c
    | [.str "num", .str z] => return .num (← decodeInt z)
    | [.str "add", t, u] => return .add (← decodeTerm n t) (← decodeTerm n u)
    | [.str "scale", .str z, t] => return .scale (← decodeInt z) (← decodeTerm n t)
    | _ => throw "invalid indexed term"

def decodeFormula : Nat → Json → Except String Formula
  | 0, _ => throw "ResourceLimit: formula depth exceeds 64"
  | n + 1, j => do
    let term := decodeTerm 66
    match (← j.getArr?).toList with
    | [.str "top"] => return .top
    | [.str "bottom"] => return .bottom
    | [.str "unary", .str p, t] => return .unary p (← term t)
    | [.str "binary", .str p, t, u] => return .binary p (← term t) (← term u)
    | [.str "eq", t, u] => return .eq (← term t) (← term u)
    | [.str "lt", t, u] => return .lt (← term t) (← term u)
    | [.str "le", t, u] => return .le (← term t) (← term u)
    | [.str "not", a] => return .not (← decodeFormula n a)
    | [.str "and", a, b] => return .and (← decodeFormula n a) (← decodeFormula n b)
    | [.str "or", a, b] => return .or (← decodeFormula n a) (← decodeFormula n b)
    | [.str "implies", a, b] => return .implies (← decodeFormula n a) (← decodeFormula n b)
    | [.str "forall", .str s, a] => return .all s (← decodeFormula n a)
    | [.str "exists", .str s, a] => return .ex s (← decodeFormula n a)
    | _ => throw "invalid indexed formula"

def termNodes : Term → Nat
  | .var _ | .const _ | .num _ => 1
  | .add t u => 1 + termNodes t + termNodes u
  | .scale _ t => 1 + termNodes t

def formulaNodes : Formula → Nat
  | .top | .bottom => 1
  | .unary _ t => 1 + termNodes t
  | .binary _ t u | .eq t u | .lt t u | .le t u => 1 + termNodes t + termNodes u
  | .not a | .all _ a | .ex _ a => 1 + formulaNodes a
  | .and a b | .or a b | .implies a b => 1 + formulaNodes a + formulaNodes b

def decodeFormulas (E : Environment) (j : Json) : Except String (List Formula) := do
  let fs ← (← j.getArr?).toList.mapM (decodeFormula 64)
  unless fs.all (fun a => a.check E []) do throw "ill-typed or unbound formula"
  if (fs.map formulaNodes).foldl (· + ·) 0 > 10000 then throw "ResourceLimit: AST node count"
  pure fs

/-! Finite presentations: user objects are (sort, local id); integers are Int. -/

abbrev Entity := String × String

def decodeValue (domains : List (String × List String)) (s : SortName) (j : Json) :
    Except String (Value Entity) := do
  let text ← j.getStr?
  match s with
  | .int => return .inr (← decodeInt text)
  | .user sort =>
    unless ((lookup domains sort).getD []).contains text do
      throw "dangling or wrong-sort value"
    return .inl (sort, text)

/-- Decode wire tables into `ModelData`; admissibility is then decided by the
proved `validModel?` gate (ModelCheck.validModel_iff), not by this decoder. -/
def decodeModel (v : Vocabulary) (j : Json) : Except String (ModelData Entity) := do
  exactFields j ["complete", "domains", "constants", "relations"]
  unless (← (← j.getObjVal? "complete").getBool?) do throw "complete must be true"
  let ds ← j.getObjVal? "domains"
  let cs ← j.getObjVal? "constants"
  let rs ← j.getObjVal? "relations"
  exactFields ds v.sorts
  exactFields cs (v.constants.map Prod.fst)
  exactFields rs (v.predicates.map Prod.fst)
  let domains ← v.sorts.mapM fun s => do
    let xs ← strings (← ds.getObjVal? s)
    unless xs.all identifier do throw "invalid local identifier"
    unless xs.eraseDups.length == xs.length do throw "duplicate domain entity"
    if xs.length > 1000 then throw "ResourceLimit: domain size"
    pure (s, xs)
  let constants ← v.constants.mapM fun (c, s) => do
    pure (c, ← decodeValue domains s (← cs.getObjVal? c))
  let relations ← v.predicates.mapM fun (p, ss) => do
    let rows ← (← (← rs.getObjVal? p).getArr?).toList.mapM fun row => do
      let cells := (← row.getArr?).toList
      unless cells.length == ss.length do throw "wrong relation arity"
      (ss.zip cells).mapM fun (s, cell) => decodeValue domains s cell
    unless rows.eraseDups.length == rows.length do throw "duplicate relation tuple"
    pure (p, rows)
  if (relations.map (fun p => p.2.length)).foldl (· + ·) 0 > 100000 then
    throw "ResourceLimit: tuple count"
  pure ⟨domains.map (fun (s, xs) => (s, xs.map (s, ·))), constants, relations⟩

/-- Decoded and admissible: every successful result passes `validModel?`. -/
def decodeValidModel (v : Vocabulary) (j : Json) : Except String (ModelData Entity) := do
  let d ← decodeModel v j
  unless validModel? v d do throw "model is not semantically admissible"
  pure d

/-! Certificates (checker ve-order-farkas-checker@1). -/

def decodePairs (j : Json) : Except String (List (Nat × Int)) := do
  (← j.getArr?).toList.mapM fun item => do
    match (← item.getArr?).toList with
    | [i, .str k] => pure (← i.getNat?, ← decodeInt k)
    | _ => throw "invalid multiplier pair"

def decodeCombo (j : Json) : Except String Tableau.Combo := do
  pure ⟨← decodePairs (← j.getObjVal? "literals"), ← decodePairs (← j.getObjVal? "cuts")⟩

def decodeCut (j : Json) : Except String Tableau.Cut := do
  exactFields j ["literals", "cuts", "divisor"]
  pure ⟨← decodeCombo j, ← decodeInt (← stringField j "divisor")⟩

def decodeTrace : Nat → Json → Except String Tableau.Trace
  | 0, _ => throw "ResourceLimit: certificate expansion depth exceeds 124"
  | fuel + 1, j => do
    let rule ← stringField j "rule"
    let children := fun (_ : Unit) => do
      (← (← j.getObjVal? "children").getArr?).toList.mapM (decodeTrace fuel)
    if rule == "close" then
      exactFields j ["rule"]
      pure .close
    else if rule == "expand" then
      let names := (← fields j).map Prod.fst
      let optional := names.contains "parameter"
      exactFields j (["rule", "at", "children"] ++ if optional then ["parameter"] else [])
      let index ← (← j.getObjVal? "at").getNat?
      let parameter ← if optional then do pure (some (← stringField j "parameter")) else pure none
      pure (.expand index parameter (← children ()))
    else if rule == "order-split@1" then
      exactFields j ["rule", "formula", "children"]
      let f ← decodeFormula 64 (← j.getObjVal? "formula")
      pure (.split f (← children ()))
    else if rule == "order-neq@1" then
      exactFields j ["rule", "at", "children"]
      pure (.neq (← (← j.getObjVal? "at").getNat?) (← children ()))
    else if rule == "order-farkas@1" then
      exactFields j ["rule", "cuts", "literals", "final_cuts"]
      let cuts ← (← (← j.getObjVal? "cuts").getArr?).toList.mapM decodeCut
      let final : Tableau.Combo := ⟨← decodePairs (← j.getObjVal? "literals"),
        ← decodePairs (← j.getObjVal? "final_cuts")⟩
      pure (.farkas cuts final)
    else throw "unknown tableau rule"

def decodeCertificate (j : Json) : Except String Tableau.Certificate := do
  exactFields j ["checker_version", "environment_id", "premise_meaning_ids",
    "conclusion_meaning_id", "trace"]
  pure ⟨← stringField j "checker_version", ← stringField j "environment_id",
    ← strings (← j.getObjVal? "premise_meaning_ids"),
    ← stringField j "conclusion_meaning_id", ← decodeTrace 125 (← j.getObjVal? "trace")⟩

structure Query (E : Environment) where
  premises : List Formula
  conclusion : Formula
  certificate : Tableau.Certificate

def Query.accepts {E : Environment} (q : Query E) : Bool :=
  Tableau.checkCertificate E q.premises q.conclusion q.certificate

/-- JSON-facing soundness at universe zero, the countermodel target universe. -/
theorem Query.accepts_sound {E : Environment} (q : Query E) (h : q.accepts = true) :
    Entails.{0} E q.premises q.conclusion :=
  Tableau.checkCertificate_sound E q.premises q.conclusion q.certificate h

def environmentId (environment : Json) : Except String String :=
  VE.CertificateWire.digest "ve-environment-v0.1-order\n" environment

def meaningId (environmentId : String) (ast : Json) : Except String String :=
  VE.CertificateWire.digest "ve-meaning-v0.1-order\n"
    (Json.mkObj [("environment_id", .str environmentId), ("ast", ast)])

def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let environment ← j.getObjVal? "environment"
  let v ← decodeEnvironment environment
  let E := v.environment
  let kind ← stringField j "kind"
  if kind == "evaluate" then
    let d ← decodeValidModel v (← j.getObjVal? "model")
    let fs ← decodeFormulas E (← j.getObjVal? "ast")
    if fs.isEmpty then throw "empty document"
    let values := fs.map (fun a => a.eval d.toModel [])
    return Json.mkObj [("id", .str id), ("status", .str "ok"), ("values", toJson values)]
  let ps ← decodeFormulas E (← j.getObjVal? "premises")
  let c ← decodeFormula 64 (← j.getObjVal? "conclusion")
  unless c.check E [] do throw "ill-typed or unbound conclusion"
  if ((c :: ps).map formulaNodes).foldl (· + ·) 0 > 10000 then
    throw "ResourceLimit: AST node count"
  if kind == "countermodel" then
    let d ← decodeModel v (← j.getObjVal? "model")
    return Json.mkObj [("id", .str id), ("status", .str "ok"),
      ("refutes", .bool (checkCountermodel v d ps c))]
  unless kind == "certificate" do throw "unknown case kind"
  let certificate ← decodeCertificate (← j.getObjVal? "certificate")
  let environmentId ← environmentId environment
  let premises ← (← (← j.getObjVal? "premises").getArr?).toList.mapM (meaningId environmentId)
  let conclusion ← meaningId environmentId (← j.getObjVal? "conclusion")
  unless certificate.environment_id == environmentId && certificate.premise_meaning_ids == premises &&
      certificate.conclusion_meaning_id == conclusion do
    throw "certificate is stale or bound to different inputs"
  let q : Query E := ⟨ps, c, certificate⟩
  pure (Json.mkObj [("id", .str id), ("status", .str "ok"), ("valid", .bool q.accepts)])

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
      ("valid", .bool false), ("error", .str message)]

end VE.Order.Wire
