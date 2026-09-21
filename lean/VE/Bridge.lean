import VE.Consequence
import VE.Json

namespace VE.Bridge
open Lean

abbrev Entity := String × String
abbrev Fields := List (String × Json)

def fields (j : Json) : Except String Fields := do
  return (← j.getObj?).toList

def exactFields (j : Json) (expected : List String) : Except String Unit := do
  let actual := (← fields j).map Prod.fst
  unless actual.length == expected.length && expected.all actual.contains do
    throw s!"fields do not match: expected {expected}, got {actual}"

def stringField (j : Json) (name : String) : Except String String := do
  (← j.getObjVal? name).getStr?

def strings (j : Json) : Except String (List String) := do
  (← j.getArr?).toList.mapM Json.getStr?

def identifier (s : String) : Bool :=
  match s.toList with
  | [] => false
  | c :: cs => s.utf8ByteSize ≤ 64 && c ≥ 'a' && c ≤ 'z' &&
      cs.all (fun x => (x ≥ 'a' && x ≤ 'z') || (x ≥ '0' && x ≤ '9') || x == '_')

def reserved : List String := ["true", "false", "is", "equals", "not", "and", "or",
  "if", "then", "for", "every", "there", "exists", "believes", "must", "eventually"]

def generatedName (s : String) : Bool :=
  match s.toList with
  | 'x' :: cs => !cs.isEmpty && cs.all (fun c => c ≥ '0' && c ≤ '9')
  | _ => false

def lookup {α : Type} (xs : List (String × α)) (k : String) : Option α :=
  (xs.find? (fun x => x.1 == k)).map Prod.snd

structure Vocabulary where
  sorts : List String
  predicates : List (String × List String)
  constants : List (String × String)

def Vocabulary.environment (v : Vocabulary) : Environment :=
  ⟨v.sorts, lookup v.predicates, lookup v.constants⟩

private def description (j : Json) : Except String Unit := do
  if (← stringField j "description").isEmpty then throw "empty description"

def decodeEnvironment (j : Json) : Except String Vocabulary := do
  exactFields j ["language", "profile", "spec_revision", "vocabulary"]
  unless (← stringField j "language") == "ve.core@0" &&
      (← stringField j "profile") == "relational-fol@0" &&
      (← stringField j "spec_revision") == "ve-v0-draft-2026-09-20" do
    throw "unsupported environment version"
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
    exactFields entry ["description"]
    description entry
  let sortNames := sorts.map Prod.fst
  let ps ← predicates.mapM fun (p, entry) => do
    exactFields entry ["arguments", "description"]
    description entry
    let ss ← strings (← entry.getObjVal? "arguments")
    unless (ss.length == 1 || ss.length == 2) && ss.all sortNames.contains do
      throw s!"invalid signature: {p}"
    pure (p, ss)
  let cs ← constants.mapM fun (c, entry) => do
    exactFields entry ["sort", "description"]
    description entry
    let s ← stringField entry "sort"
    unless sortNames.contains s do throw s!"unknown constant sort: {c}"
    pure (c, s)
  pure ⟨sortNames, ps, cs⟩

private def localIds (j : Json) : Except String (List String) := do
  let xs ← strings j
  unless xs.all identifier do throw "invalid local identifier"
  pure xs

def decodeModel (v : Vocabulary) (j : Json) : Except String (FiniteModel Entity) := do
  exactFields j ["complete", "domains", "constants", "relations"]
  unless (← (← j.getObjVal? "complete").getBool?) do throw "complete must be true"
  let ds ← j.getObjVal? "domains"
  let cs ← j.getObjVal? "constants"
  let rs ← j.getObjVal? "relations"
  exactFields ds v.sorts
  exactFields cs (v.constants.map Prod.fst)
  exactFields rs (v.predicates.map Prod.fst)
  let domains ← v.sorts.mapM fun s => do
    let xs ← localIds (← ds.getObjVal? s)
    unless xs.eraseDups.length == xs.length do throw "duplicate domain entity"
    if xs.length > 1000 then throw "ResourceLimit: domain size"
    pure (s, xs)
  let constants ← v.constants.mapM fun (c, s) => do
    let x ← stringField cs c
    unless ((lookup domains s).getD []).contains x do throw "dangling constant"
    pure (c, (s, x))
  let relations ← v.predicates.mapM fun (p, ss) => do
    let rows ← (← (← rs.getObjVal? p).getArr?).toList.mapM localIds
    unless rows.eraseDups.length == rows.length do throw "duplicate relation tuple"
    let tuples ← rows.mapM fun row => do
      unless row.length == ss.length do throw "wrong relation arity"
      let tuple := ss.zip row
      for (s, x) in tuple do
        unless ((lookup domains s).getD []).contains x do throw "dangling or wrong-sort tuple"
      pure tuple
    pure (p, tuples)
  if (relations.map (fun p => p.2.length)).foldl (· + ·) 0 > 100000 then
    throw "ResourceLimit: tuple count"
  pure {
    domains := fun s => ((lookup domains s).getD []).map (s, ·)
    constants := lookup constants
    relations := fun p => (lookup relations p).getD [] }

def decodeTerm (j : Json) : Except String Term := do
  match (← j.getArr?).toList with
  | [.str "var", i] => return .var (← i.getNat?)
  | [.str "const", .str c] => return .const c
  | _ => throw "invalid indexed term"

/-- Depth fuel is an operational limit, not a logical false value. -/
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
    | _ => throw "invalid indexed formula"

def termNodes (_ : Term) : Nat := 1

def formulaNodes : Formula → Nat
  | .top | .bottom => 1
  | .unary _ t => 1 + termNodes t
  | .binary _ t u | .eq t u => 1 + termNodes t + termNodes u
  | .not a | .all _ a | .ex _ a => 1 + formulaNodes a
  | .and a b | .or a b | .implies a b => 1 + formulaNodes a + formulaNodes b

def decodeDocument (E : Environment) (j : Json) : Except String (Document E) := do
  let fs ← (← j.getArr?).toList.mapM (decodeFormula 64)
  if (fs.map formulaNodes).foldl (· + ·) 0 > 10000 then
    throw "ResourceLimit: AST node count"
  if hn : fs = [] then throw "empty document"
  else if hw : ∀ a ∈ fs, a.check E [] = true then
    pure ⟨fs, hn, fun a ha => (check_iff_wellFormed E [] a).mp (hw a ha)⟩
  else throw "ill-typed or unbound formula"

/-- Input envelope: id, environment, model, ast. Output is per-formula truth and
conjunction. The expected results in fixture files are never consulted here. -/
def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let v ← decodeEnvironment (← j.getObjVal? "environment")
  let m ← decodeModel v (← j.getObjVal? "model")
  let d ← decodeDocument v.environment (← j.getObjVal? "ast")
  let values := d.formulas.map (fun a => a.eval m [])
  pure (Json.mkObj [("id", .str id), ("values", toJson values),
    ("value", .bool (d.eval m)), ("status", .str "ok")])

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"),
      ("status", .str "error"), ("error", .str message)]

end VE.Bridge
