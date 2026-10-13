import VE.SearchBudget.Budget
import VE.Bridge
import VE.Route.Wire

/-! # Service mode `search-budget` (premise-scale)

A case is `{"id", "environment", "premises"}`: the environment the premise check searches
(Rust's model environment) and its premises as ASTs. The row is the premise check's budget
(`premiseBudget`) and the sorts it raises (`sortBounds`):

    {"id", "status": "ok", "max_proof_steps", "max_domain_size", "max_models", "max_evaluations",
     "sorts": [{"sort", "least", "most"}]}

The sorts are the environment's declared sorts (`vocabulary.sorts`, an object's keys) and the
constants its `vocabulary.constants` entries whose `sort` is a string. The facts are read
leniently: each premise's top-level conjuncts are decoded one at a time (`VE.Bridge.decodeFormula`),
and a conjunct outside the core first-order syntax (an order comparison, an n-ary atom, a
reachability atom) is left out, so it only forces nothing. The premises and the environment are
typed elsewhere (the search and the model check refuse what does not type); no row here is a
verdict, and a row only bounds an untrusted search. -/
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

/-- The declared sorts: the keys of `vocabulary.sorts`. -/
def decodeSorts (vocabulary : Json) : List String :=
  match vocabulary.getObjValD "sorts" with
  | .obj m => m.toList.map Prod.fst
  | _ => []

/-- The declared constants with a string sort. -/
def decodeConstants (vocabulary : Json) : List (String × String) :=
  match vocabulary.getObjValD "constants" with
  | .obj m => m.toList.filterMap fun (name, entry) =>
      match entry.getObjValD "sort" with
      | .str s => some (name, s)
      | _ => none
  | _ => []

def boundJson (r : String × Nat × Nat) : Json :=
  Json.mkObj [("sort", .str r.1), ("least", toJson r.2.1), ("most", toJson r.2.2)]

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let vocabulary ← environment.getObjVal? "vocabulary"
  let premises ← (← j.getObjVal? "premises").getArr?
  let b := premiseBudget
  let bounds := sortBounds b (decodeConstants vocabulary) (decodeFacts premises) (decodeSorts vocabulary)
  pure (VE.Route.Wire.ok id [("max_proof_steps", toJson b.maxProofSteps),
    ("max_domain_size", toJson b.domainSize), ("max_models", toJson b.maxModels),
    ("max_evaluations", toJson b.maxEvaluations),
    ("sorts", Json.arr (bounds.map boundJson).toArray)])

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
      ("error", .str s!"InvalidInput: search-budget case: {message}")]

end VE.SearchBudget.Run
