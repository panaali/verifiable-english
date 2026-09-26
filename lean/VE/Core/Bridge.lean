import VE.Core.Consequence
import VE.Core.RoundTrip
import VE.ModelProofs

namespace VE.Core.Bridge
open Lean
open VE.Bridge

def decodeEnvironment (j : Json) : Except String Vocabulary := do
  exactFields j ["language", "profiles", "spec_revision", "vocabulary"]
  unless (← stringField j "language") == "ve.core@0.2" &&
      (← strings (← j.getObjVal? "profiles")) ==
        ["closure@0", "nary@0", "relational-fol@0"] &&
      (← stringField j "spec_revision") == "ve-v0.2-expand2-2026-09-25" do
    throw "unsupported closure+n-ary environment version/profiles"
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
  for (_, entry) in sorts do
    displayFields entry ["description"] ["verbalisation"]
    description entry
    if let .ok words := entry.getObjVal? "verbalisation" then
      exactFields words ["singular", "plural"]
      displayString (← words.getObjVal? "singular")
      displayString (← words.getObjVal? "plural")
  let sortNames := sorts.map Prod.fst
  let ps ← predicates.mapM fun (p, entry) => do
    displayFields entry ["arguments", "description"] ["verbalisation", "negative_verbalisation"]
    description entry
    for key in ["verbalisation", "negative_verbalisation"] do
      if let .ok words := entry.getObjVal? key then displayString words
    let ss ← strings (← entry.getObjVal? "arguments")
    unless ss.all sortNames.contains do
      throw "UnknownSymbol: unknown predicate argument sort"
    unless decide (1 ≤ ss.length) && decide (ss.length ≤ 6) do
      throw s!"invalid signature: {p}"
    pure (p, ss)
  let cs ← constants.mapM fun (c, entry) => do
    let literal := (← stringField entry "sort") == "$string"
    if literal then
      displayFields entry ["sort"] ["description"]
      if let .ok _ := entry.getObjVal? "description" then description entry
    else
      exactFields entry ["sort", "description"]
      description entry
    let s ← stringField entry "sort"
    unless sortNames.contains s || s == "$string" do throw s!"unknown constant sort: {c}"
    pure (c, s)
  if (cs.filter (fun c => c.2 == "$string")).length > 64 then
    throw "ResourceLimit: At most 64 declared $string literals"
  let result : Vocabulary := ⟨sortNames, ps, cs⟩
  unless result.namesValid do throw "invalid declaration names"
  pure result

def decodeKind (j : Json) : Except String Kind := do
  match (← j.getStr?) with
  | "plus" => pure .plus
  | "star" => pure .star
  | _ => throw "invalid reach kind"

def decodeFormula : Nat → Json → Except String Formula
  | 0, _ => throw "ResourceLimit: formula depth exceeds 64"
  | n + 1, j => do
    match (← j.getArr?).toList with
    | [.str "top"] => return .top
    | [.str "bottom"] => return .bottom
    | [.str "unary", .str p, t] => return .unary p (← decodeTerm t)
    | [.str "binary", .str p, t, u] => return .binary p (← decodeTerm t) (← decodeTerm u)
    | [.str "atom", .str p, ts] =>
      let termArray ← match ts.getArr? with
        | .ok array => pure array
        | .error _ => throw "Atom terms must be an array of three to six terms"
      let terms ← termArray.toList.mapM decodeTerm
      unless decide (3 ≤ terms.length) && decide (terms.length ≤ 6) do
        throw "Atom terms must be an array of three to six terms"
      return .atom p terms
    | [.str "eq", t, u] => return .eq (← decodeTerm t) (← decodeTerm u)
    | [.str "not", a] => return .not (← decodeFormula n a)
    | [.str "and", a, b] => return .and (← decodeFormula n a) (← decodeFormula n b)
    | [.str "or", a, b] => return .or (← decodeFormula n a) (← decodeFormula n b)
    | [.str "implies", a, b] => return .implies (← decodeFormula n a) (← decodeFormula n b)
    | [.str "forall", .str s, a] => return .all s (← decodeFormula n a)
    | [.str "exists", .str s, a] => return .ex s (← decodeFormula n a)
    | [.str "reach", k, e, t, u] =>
      let k ← decodeKind k
      let t ← decodeTerm t
      let u ← decodeTerm u
      match (← e.getArr?).toList with
      | [.str "named", .str r] => pure (.reachNamed k r t u)
      | [.str "body", .str s, a] => return .reachBody k s (← decodeFormula n a) t u
      | _ => throw "invalid reach edge"
    | _ => throw "invalid indexed formula"

def formulaNodes : Formula → Nat
  | .top | .bottom => 1
  | .unary _ t => 1 + termNodes t
  | .binary _ t u | .eq t u => 1 + termNodes t + termNodes u
  | .atom _ ts => 1 + (ts.map termNodes).foldl (· + ·) 0
  | .not a | .all _ a | .ex _ a => 1 + formulaNodes a
  | .and a b | .or a b | .implies a b => 1 + formulaNodes a + formulaNodes b

  | .reachNamed _ _ t u => 1 + termNodes t + termNodes u
  | .reachBody _ _ a t u => 1 + formulaNodes a + termNodes t + termNodes u

def checkFormula (E : Environment) (a : Formula) (label : String) : Except String Unit := do
  unless a.check E [] do
    match a with
    | .atom p ts =>
      if (E.predicates p).isNone || ts.any (fun t => (t.sortOf E []).isNone) then
        throw "UnknownSymbol: n-ary predicate or argument is undeclared"
      throw "TypeMismatch: predicate argument sort mismatch"
    | _ => throw s!"ill-typed or unbound {label}"

def decodeFormulas (E : Environment) (j : Json) : Except String (List Formula) := do
  let fs ← (← j.getArr?).toList.mapM (decodeFormula 64)
  for a in fs do checkFormula E a "formula"
  if (fs.map formulaNodes).foldl (· + ·) 0 > 10000 then throw "ResourceLimit: AST node count"
  pure fs

def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let v ← decodeEnvironment (← j.getObjVal? "environment")
  let m ← decodeModel v (← j.getObjVal? "model")
  if let .ok kind := j.getObjVal? "kind" then
    unless kind == .str "countermodel" do throw "unknown case kind"
    let ps ← decodeFormulas v.environment (← j.getObjVal? "premises")
    let c ← decodeFormula 64 (← j.getObjVal? "conclusion")
    checkFormula v.environment c "conclusion"
    if ((c :: ps).map formulaNodes).foldl (· + ·) 0 > 10000 then
      throw "ResourceLimit: AST node count"
    return Json.mkObj [("id", .str id), ("status", .str "ok"),
      ("refutes", .bool (countermodelCheck m ps c))]
  let fs ← decodeFormulas v.environment (← j.getObjVal? "ast")
  if fs.isEmpty then throw "empty document"
  let canonical := Surface.print fs
  unless Surface.parse v.environment canonical == some fs do
    throw "internal printer/parser disagreement"
  if let .ok source := j.getObjVal? "source" then
    let text ← source.getStr?
    unless sourceIdentifierBudget text do throw "ResourceLimit: source identifier exceeds 64 bytes"
    unless Surface.parse v.environment text == some fs do throw "source/AST mismatch"
  let values := fs.map (fun a => a.eval m [])
  pure (Json.mkObj [("id", .str id), ("values", toJson values),
    ("value", .bool (values.all (fun b => b))), ("canonical", .str canonical), ("status", .str "ok")])

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"),
      ("status", .str "error"), ("error", .str message)]

end VE.Core.Bridge
