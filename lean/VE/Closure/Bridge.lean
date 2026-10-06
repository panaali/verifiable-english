import VE.Closure.Consequence
import VE.Closure.RoundTrip
import VE.ModelProofs

namespace VE.Closure.Bridge
open Lean
open VE.Bridge

def decodeEnvironment (j : Json) : Except String Vocabulary := do
  exactFields j ["language", "profiles", "spec_revision", "vocabulary"]
  unless (← stringField j "language") == "ve.core@0.1" &&
      (← strings (← j.getObjVal? "profiles")) == ["closure@0", "relational-fol@0"] &&
      (← stringField j "spec_revision") == "ve-v0.1-closure-2026-09-21" do
    throw "unsupported closure environment version/profiles"
  VE.Bridge.decodeEnvironment (Json.mkObj [
    ("language", .str "ve.core@0"), ("profile", .str "relational-fol@0"),
    ("spec_revision", .str "ve-v0-draft-2026-09-20"),
    ("vocabulary", ← j.getObjVal? "vocabulary")])

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
  | .not a | .all _ a | .ex _ a => 1 + formulaNodes a
  | .and a b | .or a b | .implies a b => 1 + formulaNodes a + formulaNodes b

  | .reachNamed _ _ t u => 1 + termNodes t + termNodes u
  | .reachBody _ _ a t u => 1 + formulaNodes a + termNodes t + termNodes u

def decodeFormulas (E : Environment) (j : Json) : Except String (List Formula) := do
  let fs ← (← j.getArr?).toList.mapM (decodeFormula 64)
  unless fs.all (fun a => a.check E []) do throw "ill-typed or unbound formula"
  if (fs.map formulaNodes).foldl (· + ·) 0 > 10000 then throw "ResourceLimit: AST node count"
  pure fs

def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let v ← decodeEnvironment (← j.getObjVal? "environment")
  let m ← decodeModel v (← j.getObjVal? "model")
  if let .ok kind := j.getObjVal? "kind" then
    unless kind.getStr?.toOption == some "countermodel" do throw "unknown case kind"
    let ps ← decodeFormulas v.environment (← j.getObjVal? "premises")
    let c ← decodeFormula 64 (← j.getObjVal? "conclusion")
    unless c.check v.environment [] do throw "ill-typed or unbound conclusion"
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

end VE.Closure.Bridge
