import VE.SearchBudget.Budget
import VE.Bridge
import VE.Route.Wire

/-! # Service mode `search-budget` (premise-scale)

A case is `{"id", "environment", "premises", "sorts"}`: the environment the premise check searches
(Rust's model environment), its premises as ASTs, and the sorts to budget. The row is the premise
check's budget (`premiseBudget`) and, for each requested sort in order, its raised bounds
(`sortBound`) or `null` where the shared bound stands:

    {"id", "status": "ok", "max_proof_steps", "max_domain_size", "max_models", "max_evaluations",
     "sorts": [{"least", "most"} | null, ...]}

The answer names no sort: its `sorts` is one entry per requested sort, so the client binds it by
position (`search-budget.json`, `x-zip`). The constants are the environment's `vocabulary.constants`
entries whose `sort` is a string. The facts are read leniently: each premise's top-level conjuncts
are decoded one at a time (`VE.Bridge.decodeFormula`), and a conjunct outside the core first-order
syntax (an order comparison, an n-ary atom, a reachability atom) is left out, so it only forces
nothing. The premises and the environment are typed elsewhere (the search and the model check
refuse what does not type); no row here is a verdict, and a row only bounds an untrusted search. -/
namespace VE.SearchBudget.Run
open Lean VE

/-- Most JSON nodes read when splitting the premises into conjuncts (`ve/limits.py` MAX_NODES). -/
def maxConjunctNodes : Nat := 10000

/-- The top-level conjuncts of a JSON AST, at most `fuel` deep. -/
def jsonConjuncts : Nat → Json → List Json
  | 0, j => [j]
  | n + 1, j => match j with
    | .arr #[.str "and", a, b] => jsonConjuncts n a ++ jsonConjuncts n b
    | j => [j]

/-- The facts of the premises the core decoder reads; any other conjunct is left out. -/
def decodeFacts (premises : Array Json) : List Formula :=
  (premises.toList.flatMap (jsonConjuncts maxConjunctNodes)).filterMap
    fun j => (VE.Bridge.decodeFormula 64 j).toOption

/-- The declared constants with a string sort. -/
def decodeConstants (vocabulary : Json) : List (String × String) :=
  match vocabulary.getObjValD "constants" with
  | .obj m => m.toList.filterMap fun (name, entry) =>
      match entry.getObjValD "sort" with
      | .str s => some (name, s)
      | _ => none
  | _ => []

/-- A requested sort's entry: its raised bounds, or `null` where the shared bound stands. -/
def boundJson : Option (String × Nat × Nat) → Json
  | some (_, least, most) => Json.mkObj [("least", toJson least), ("most", toJson most)]
  | none => .null

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let vocabulary ← environment.getObjVal? "vocabulary"
  let premises ← (← j.getObjVal? "premises").getArr?
  let sorts ← VE.Bridge.strings (← j.getObjVal? "sorts")
  let b := premiseBudget
  let cs := decodeConstants vocabulary
  let facts := decodeFacts premises
  pure (VE.Route.Wire.ok id [("max_proof_steps", toJson b.maxProofSteps),
    ("max_domain_size", toJson b.domainSize), ("max_models", toJson b.maxModels),
    ("max_evaluations", toJson b.maxEvaluations),
    ("sorts", Json.arr (sorts.map fun s => boundJson (sortBound b cs facts s)).toArray)])

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
      ("error", .str s!"InvalidInput: search-budget case: {message}")]

end VE.SearchBudget.Run
