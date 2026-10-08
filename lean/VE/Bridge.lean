import VE.Consequence
import VE.Json
import VE.Surface

namespace VE.Bridge
open Lean

abbrev Entity := String × String
abbrev Fields := List (String × Json)

/-- The expected consequence type for JSON-backed certificates/countermodels. -/
abbrev JsonEntails := Entails.{0}

def fields (j : Json) : Except String Fields := do
  return (← j.getObj?).toList

def exactFields (j : Json) (expected : List String) : Except String Unit := do
  let actual := (← fields j).map Prod.fst
  unless actual.length == expected.length && expected.all actual.contains do
    throw s!"fields do not match: expected {expected}, got {actual}"

/-- The legacy and model diagnostics retain quoted field spellings, including
the extra or missing field that caused the rejection. Profile routes with
their own field-list wording continue to use `exactFields`. -/
def exactFieldsQuoted (j : Json) (expected : List String) : Except String Unit := do
  match exactFields j expected with
  | .ok () => pure ()
  | .error message =>
    let .ok actual := (fields j).map (·.map Prod.fst) | throw message
    let quoted := fun (names : List String) =>
      "[" ++ String.intercalate ", " (names.map fun name => "'" ++ name ++ "'") ++ "]"
    throw s!"fields do not match: expected {quoted expected}, got {quoted actual}"

def stringField (j : Json) (name : String) : Except String String := do
  (← j.getObjVal? name).getStr?

def strings (j : Json) : Except String (List String) := do
  (← j.getArr?).toList.mapM Json.getStr?

/-- Retain the offending sort spelling in the public diagnostic across every
family vocabulary decoder. -/
def checkArgumentSorts (arguments : List String) (allowed : String → Bool) : Except String Unit := do
  if let some unknown := arguments.find? (fun sort => !allowed sort) then
    throw s!"UnknownSymbol: Undeclared predicate argument sort: '{unknown}'"

/-- Reject a wrong-typed sort cell with the same code as an unknown sort.
The array's own shape remains the caller's arity/type check. -/
def argumentSorts (raw : Json) (allowed : String → Bool) : Except String (List String) := do
  let cells ← raw.getArr?
  cells.toList.mapM fun cell => do
    match cell with
    | .str sort => do
      checkArgumentSorts [sort] allowed
      pure sort
    | _ => throw s!"UnknownSymbol: Undeclared predicate argument sort: {cell.compress}"

def checkConstantSort (sort : String) (allowed : String → Bool) : Except String Unit := do
  unless allowed sort do
    throw s!"UnknownSymbol: Undeclared constant sort: '{sort}'"

def constantSort (entry : Json) (allowed : String → Bool) : Except String String := do
  let raw ← entry.getObjVal? "sort"
  match raw with
  | .str sort => do
    checkConstantSort sort allowed
    pure sort
  | _ => throw s!"UnknownSymbol: Undeclared constant sort: {raw.compress}"

/-- Runtime identifiers additionally obey the 64-byte wire budget. -/
def identifier (s : String) : Bool :=
  s.utf8ByteSize ≤ 64 && Surface.identifier s

/-- Runtime-only cap on identifier runs in source. The unbudgeted reference
parser remains independent of this wire-resource restriction. -/
def sourceIdentifierBudget (text : String) : Bool :=
  (text.toList.foldl (fun (state : Nat × Bool) c =>
    if Surface.identChar c then (state.1 + 1, state.2 && state.1 < 64)
    else (0, state.2)) (0, true)).2

abbrev reserved := Surface.reserved
abbrev generatedName := Surface.generatedName

/-- The frozen schema counts identifier characters before ASCII validation
and checks each category in declaration order. -/
def checkVocabularyNames (sorts predicates constants : Fields) : Except String Unit := do
  let mut seen : List String := []
  for (name, _) in sorts ++ predicates ++ constants do
    if name.length > 64 then
      throw "ResourceLimit: Identifier exceeds 64 ASCII bytes"
    unless Surface.identifier name do
      throw s!"Invalid ASCII identifier: '{name}'"
    if seen.contains name then
      throw s!"DuplicateDeclaration: Symbol '{name}' is declared in multiple categories"
    if reserved.contains name || generatedName name then
      throw s!"DuplicateDeclaration: Schema identifier '{name}' is reserved"
    seen := name :: seen

def lookup {α : Type} (xs : List (String × α)) (k : String) : Option α :=
  (xs.find? (fun x => x.1 == k)).map Prod.snd

structure Vocabulary where
  sorts : List String
  predicates : List (String × List String)
  constants : List (String × String)

def Vocabulary.environment (v : Vocabulary) : Environment :=
  ⟨v.sorts, lookup v.predicates, lookup v.constants⟩

/-- Decidable lexical conditions on the complete finite declaration inventory. -/
def Vocabulary.namesValid (v : Vocabulary) : Bool :=
  v.sorts.all Surface.declarationName &&
  v.predicates.all (fun p => Surface.declarationName p.1) &&
  v.constants.all (fun c => Surface.declarationName c.1)

def description (j : Json) : Except String Unit := do
  if (← stringField j "description").isEmpty then throw "empty description"

-- Display metadata has no semantic interpretation here. Match Python's wire
-- validation while leaving lexical acceptance/fallback to the view renderer.
def displayString (j : Json) : Except String Unit := do
  let text ← j.getStr?
  if text.isEmpty then throw "empty verbalisation"
  if text.length > 256 then throw "ResourceLimit: verbalisation size"

def displayFields (j : Json) (required optional : List String) : Except String Unit := do
  let names := (← fields j).map Prod.fst
  exactFields j (required ++ optional.filter names.contains)

def decodeEnvironment (j : Json) : Except String Vocabulary := do
  exactFieldsQuoted j ["language", "profile", "spec_revision", "vocabulary"]
  unless (← stringField j "language") == "ve.core@0" &&
      (← stringField j "profile") == "relational-fol@0" &&
      (← stringField j "spec_revision") == "ve-v0-draft-2026-09-20" do
    throw "unsupported environment version"
  let v ← j.getObjVal? "vocabulary"
  exactFieldsQuoted v ["sorts", "predicates", "constants"]
  let sorts ← fields (← v.getObjVal? "sorts")
  let predicates ← fields (← v.getObjVal? "predicates")
  let constants ← fields (← v.getObjVal? "constants")
  if sorts.length > 32 || predicates.length > 256 then
    throw "ResourceLimit: vocabulary size"
  checkVocabularyNames sorts predicates constants
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
      if let .ok words := entry.getObjVal? key then
        displayString words
    let raw ← entry.getObjVal? "arguments"
    let cells ← raw.getArr?
    unless cells.size == 1 || cells.size == 2 do
      throw "Predicate arguments must be an array of one to 2 sort identifiers"
    let ss ← argumentSorts raw sortNames.contains
    pure (p, ss)
  let cs ← constants.mapM fun (c, entry) => do
    exactFields entry ["sort", "description"]
    description entry
    let s ← constantSort entry sortNames.contains
    pure (c, s)
  let result : Vocabulary := ⟨sortNames, ps, cs⟩
  unless result.namesValid do throw "invalid declaration names"
  pure result

private def localIds (j : Json) : Except String (List String) := do
  let xs ← strings j
  unless xs.all identifier do throw "invalid local identifier"
  pure xs

/-- Finite tables retained so semantic admissibility can be checked exhaustively. -/
structure ModelData where
  domains : List (String × List String)
  constants : List (String × Entity)
  relations : List (String × List (List Entity))

def ModelData.toModel (d : ModelData) : FiniteModel Entity where
  domains := fun s => ((lookup d.domains s).getD []).map (s, ·)
  constants := lookup d.constants
  relations := fun p => (lookup d.relations p).getD []

def tupleCheck (M : FiniteModel Entity) : List String → List Entity → Bool
  | [], [] => true
  | s :: ss, x :: xs => (M.domains s).contains x && tupleCheck M ss xs
  | _, _ => false

/-- This final semantic gate is independent of the JSON parser and earlier wire
checks. Its soundness is proved in ModelProofs for arbitrary finite tables. -/
def ModelData.valid (d : ModelData) (v : Vocabulary) : Bool :=
  v.constants.all (fun (c, s) => match d.toModel.constants c with
    | some x => (d.toModel.domains s).contains x
    | none => false) &&
  d.relations.all (fun (p, rows) => match v.environment.predicates p with
    | some ss => rows.all (tupleCheck d.toModel ss)
    | none => false)

def decodeModelData (v : Vocabulary) (j : Json) : Except String ModelData := do
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
  pure ⟨domains, constants, relations⟩

/-- Every successful result is admissible, by decodeModel_valid. -/
def decodeModel (v : Vocabulary) (j : Json) : Except String (FiniteModel Entity) := do
  let data ← decodeModelData v j
  if data.valid v then pure data.toModel
  else throw "model is not semantically admissible"

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

/-- A countermodel request has closed typed formulas; zero premises are allowed. -/
structure CountermodelQuery (E : Environment) where
  premises : List Formula
  conclusion : Formula
  premises_typed : ∀ a ∈ premises, a.WellFormed E []
  conclusion_typed : conclusion.WellFormed E []

def decodeCountermodel (E : Environment) (j : Json) : Except String (CountermodelQuery E) := do
  let ps ← (← (← j.getObjVal? "premises").getArr?).toList.mapM (decodeFormula 64)
  let c ← decodeFormula 64 (← j.getObjVal? "conclusion")
  if ((c :: ps).map formulaNodes).foldl (· + ·) 0 > 10000 then
    throw "ResourceLimit: countermodel AST node count"
  if hp : ∀ a ∈ ps, a.check E [] = true then
    if hc : c.check E [] = true then
      pure ⟨ps, c, fun a ha => (check_iff_wellFormed E [] a).mp (hp a ha),
        (check_iff_wellFormed E [] c).mp hc⟩
    else throw "ill-typed or unbound conclusion"
  else throw "ill-typed or unbound premise"

def CountermodelQuery.refutes {E : Environment} (q : CountermodelQuery E)
    (M : FiniteModel Entity) : Bool :=
  countermodelCheck M q.premises q.conclusion

/-- Legacy evaluation envelopes retain their format. The optional kind field
selects a countermodel request; fixture expected values are never consulted. -/
def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let v ← decodeEnvironment (← j.getObjVal? "environment")
  let m ← decodeModel v (← j.getObjVal? "model")
  if let .ok kind := j.getObjVal? "kind" then
    unless kind.getStr?.toOption == some "countermodel" do throw "unknown case kind"
    let q ← decodeCountermodel v.environment j
    return Json.mkObj [("id", .str id), ("status", .str "ok"), ("refutes", .bool (q.refutes m))]
  let d ← decodeDocument v.environment (← j.getObjVal? "ast")
  let canonical := Surface.print d.formulas
  unless Surface.parse v.environment canonical == some d.formulas do
    throw "internal printer/parser disagreement"
  if let .ok source := j.getObjVal? "source" then
    let text ← source.getStr?
    unless sourceIdentifierBudget text do throw "ResourceLimit: source identifier exceeds 64 bytes"
    unless Surface.parse v.environment text == some d.formulas do
      throw "source/AST mismatch"
  let values := d.formulas.map (fun a => a.eval m [])
  pure (Json.mkObj [("id", .str id), ("values", toJson values),
    ("value", .bool (d.eval m)), ("canonical", .str canonical), ("status", .str "ok")])

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"),
      ("status", .str "error"), ("error", .str message)]

end VE.Bridge
